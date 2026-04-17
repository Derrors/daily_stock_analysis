# -*- coding: utf-8 -*-
"""Batch/synchronous orchestration mixin for the stock-analysis runtime.

This mixin hosts the synchronous orchestration entrypoints that used to live
inside `src.core.pipeline.StockAnalysisPipeline`. The concrete low-level engine
still provides data-fetch, analysis, and storage helpers; the mixin keeps the
canonical orchestration logic under `src.stock_analysis_skill.runtime`.
"""

from __future__ import annotations

import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import List, Optional

from src.analyzer import AnalysisResult
from src.enums import ReportType

logger = logging.getLogger(__name__)


class StockAnalysisBatchRuntimeMixin:
    """Synchronous stock-analysis batch/runtime entrypoints."""

    def process_single_stock(
        self,
        code: str,
        skip_analysis: bool = False,
        report_type: ReportType = ReportType.SIMPLE,
        analysis_query_id: Optional[str] = None,
        current_time: Optional[datetime] = None,
    ) -> Optional[AnalysisResult]:
        """处理单只股票的完整流程。"""
        logger.info(f"========== 开始处理 {code} ==========")

        try:
            self._emit_progress(12, f"{code}：正在准备分析任务")
            success, error = self.fetch_and_save_stock_data(
                code, current_time=current_time
            )

            if not success:
                logger.warning(f"[{code}] 数据获取失败: {error}")
            else:
                self._emit_progress(16, f"{code}：行情数据准备完成")

            if skip_analysis:
                logger.info(f"[{code}] 跳过 AI 分析（dry-run 模式）")
                return None

            effective_query_id = analysis_query_id or self.query_id or uuid.uuid4().hex
            result = self.analyze_stock(code, report_type, query_id=effective_query_id)

            if result and result.success:
                logger.info(
                    f"[{code}] 分析完成: {result.operation_advice}, 评分 {result.sentiment_score}"
                )
            elif result:
                logger.warning(
                    f"[{code}] 分析未成功: {result.error_message or '未知错误'}"
                )

            return result
        except Exception as e:
            logger.exception(f"[{code}] 处理过程发生未知异常: {e}")
            return None

    def run(
        self,
        stock_codes: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> List[AnalysisResult]:
        """运行完整的同步股票分析流程。"""
        start_time = time.time()

        if stock_codes is None:
            self.config.refresh_stock_list()
            stock_codes = self.config.stock_list

        if not stock_codes:
            logger.error("未配置自选股列表，请在 .env 文件中设置 STOCK_LIST")
            return []

        logger.info(f"===== 开始分析 {len(stock_codes)} 只股票 =====")
        logger.info(f"股票列表: {', '.join(stock_codes)}")
        logger.info(f"并发数: {self.max_workers}, 模式: {'仅获取数据' if dry_run else '完整分析'}")

        resume_reference_time = datetime.now(timezone.utc)

        if len(stock_codes) >= 5:
            prefetch_count = self.fetcher_manager.prefetch_realtime_quotes(stock_codes)
            if prefetch_count > 0:
                logger.info(f"已启用批量预取架构：一次拉取全市场数据，{len(stock_codes)} 只股票共享缓存")

        if not dry_run:
            self.fetcher_manager.prefetch_stock_names(stock_codes, use_bulk=False)

        report_type_str = getattr(self.config, 'report_type', 'simple').lower()
        if report_type_str == 'brief':
            report_type = ReportType.BRIEF
        elif report_type_str == 'full':
            report_type = ReportType.FULL
        else:
            report_type = ReportType.SIMPLE
        analysis_delay = getattr(self.config, 'analysis_delay', 0)

        results: List[AnalysisResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_code = {
                executor.submit(
                    self.process_single_stock,
                    code,
                    skip_analysis=dry_run,
                    report_type=report_type,
                    analysis_query_id=uuid.uuid4().hex,
                    current_time=resume_reference_time,
                ): code
                for code in stock_codes
            }

            for idx, future in enumerate(as_completed(future_to_code)):
                code = future_to_code[future]
                try:
                    result = future.result()
                    if result and result.success:
                        results.append(result)
                    elif result and not result.success:
                        logger.warning(
                            f"[{code}] 分析结果标记为失败，不计入汇总: {result.error_message or '未知原因'}"
                        )

                    if idx < len(stock_codes) - 1 and analysis_delay > 0:
                        logger.debug(f"等待 {analysis_delay} 秒后继续下一只股票...")
                        time.sleep(analysis_delay)
                except Exception as e:
                    logger.error(f"[{code}] 任务执行失败: {e}")

        elapsed_time = time.time() - start_time

        if dry_run:
            success_count = sum(
                1
                for code in stock_codes
                if self.db.has_today_data(
                    code,
                    self._resolve_resume_target_date(code, current_time=resume_reference_time),
                )
            )
            fail_count = len(stock_codes) - success_count
        else:
            success_count = len(results)
            fail_count = len(stock_codes) - success_count

        logger.info("===== 分析完成 =====")
        logger.info(f"成功: {success_count}, 失败: {fail_count}, 耗时: {elapsed_time:.2f} 秒")

        if results and not dry_run:
            self._save_local_report(results, report_type)

        return results

    def _get_report_output_service(self):
        return self.report_output_service

    def _save_local_report(
        self,
        results: List[AnalysisResult],
        report_type: ReportType = ReportType.SIMPLE,
    ) -> None:
        """保存分析报告到本地文件（与外部消息投递解耦）"""
        try:
            report_output_service = self._get_report_output_service()
            report = self._generate_aggregate_report(results, report_type)
            filepath = report_output_service.save_report_to_file(report)
            logger.info(f"决策仪表盘日报已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存本地报告失败: {e}")

    def _generate_aggregate_report(
        self,
        results: List[AnalysisResult],
        report_type: ReportType,
    ) -> str:
        """Generate aggregate report via the report-output service, with compatibility fallbacks."""
        report_output_service = self._get_report_output_service()
        generator = getattr(report_output_service, "generate_aggregate_report", None)
        if callable(generator):
            return generator(results, report_type)
        if report_type == ReportType.BRIEF and hasattr(report_output_service, "generate_brief_report"):
            return report_output_service.generate_brief_report(results)
        return report_output_service.generate_dashboard_report(results)
