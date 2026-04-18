# -*- coding: utf-8 -*-
"""Canonical stock-analysis mainline orchestration helpers.

This module hosts the synchronous single-stock analysis flow that used to live
inside ``src.core.pipeline.StockAnalysisPipeline.analyze_stock``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Callable, Optional

from src.enums import ReportType

if TYPE_CHECKING:
    from src.stock_analysis_skill.contracts import AnalysisResult
    from src.stock_analysis_skill.analyzers.trend import TrendAnalysisResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LegacySingleStockRunRequest:
    """Canonical request used when the skill runtime delegates to the legacy executor."""

    config: Any
    stock_code: str
    report_type: ReportType
    query_id: str
    progress_callback: Optional[Callable[[int, str], None]] = None
    force_refresh: bool = False


def run_legacy_single_stock_mainline(runner: Any, request: LegacySingleStockRunRequest):
    """Execute one stock-analysis run through a legacy pipeline factory."""
    pipeline = runner.create_pipeline(
        config=request.config,
        query_id=request.query_id,
        progress_callback=request.progress_callback,
    )
    _ = request.force_refresh  # Reserved for parity until low-level fetch semantics move into canonical runtime.
    return pipeline.process_single_stock(
        code=request.stock_code,
        skip_analysis=False,
        report_type=request.report_type,
    )


def run_stock_analysis_mainline(
    pipeline,
    code: str,
    report_type: ReportType,
    *,
    query_id: str,
) -> Optional["AnalysisResult"]:
    """Run the synchronous single-stock mainline using the provided pipeline object."""
    from src.stock_analysis_skill.analysis.postprocess import fill_chip_structure_if_needed, fill_price_position_if_needed
    from src.core.trading_calendar import get_market_for_stock, get_market_now
    from src.stock_analysis_skill.providers.base import normalize_stock_code
    from src.stock_analysis_skill.providers.us_index_mapping import is_us_stock_code

    stock_name = code
    try:
        pipeline._emit_progress(18, f"{code}：正在获取行情与筹码数据")
        stock_name = pipeline.fetcher_manager.get_stock_name(code, allow_realtime=False)

        realtime_quote = None
        try:
            if pipeline.config.enable_realtime_quote:
                realtime_quote = pipeline.fetcher_manager.get_realtime_quote(code, log_final_failure=False)
                if realtime_quote:
                    if realtime_quote.name:
                        stock_name = realtime_quote.name
                    volume_ratio = getattr(realtime_quote, "volume_ratio", None)
                    turnover_rate = getattr(realtime_quote, "turnover_rate", None)
                    logger.info(
                        "%s(%s) 实时行情: 价格=%s, 量比=%s, 换手率=%s%% (来源: %s)",
                        stock_name,
                        code,
                        realtime_quote.price,
                        volume_ratio,
                        turnover_rate,
                        realtime_quote.source.value if hasattr(realtime_quote, "source") else "unknown",
                    )
                else:
                    logger.warning("%s(%s) 所有实时行情数据源均不可用，已降级为历史收盘价继续分析", stock_name, code)
            else:
                logger.info("%s(%s) 实时行情已禁用，使用历史收盘价继续分析", stock_name, code)
        except Exception as exc:
            logger.warning("%s(%s) 实时行情链路异常，已降级为历史收盘价继续分析: %s", stock_name, code, exc)

        if not stock_name:
            stock_name = f"股票{code}"

        chip_data = None
        try:
            chip_data = pipeline.fetcher_manager.get_chip_distribution(code)
            if chip_data:
                logger.info(
                    "%s(%s) 筹码分布: 获利比例=%.1f%%, 90%%集中度=%.2f%%",
                    stock_name,
                    code,
                    chip_data.profit_ratio * 100,
                    chip_data.concentration_90 * 100,
                )
            else:
                logger.debug("%s(%s) 筹码分布获取失败或已禁用", stock_name, code)
        except Exception as exc:
            logger.warning("%s(%s) 获取筹码分布失败: %s", stock_name, code, exc)

        use_agent = getattr(pipeline.config, "agent_mode", False)
        if not use_agent:
            configured_skills = getattr(pipeline.config, "agent_skills", [])
            if configured_skills and configured_skills != ["all"]:
                use_agent = True
                logger.info("%s(%s) Auto-enabled agent mode due to configured skills: %s", stock_name, code, configured_skills)

        pipeline._emit_progress(32, f"{stock_name}：正在聚合基本面与趋势数据")

        fundamental_context = None
        try:
            fundamental_context = pipeline.fetcher_manager.get_fundamental_context(
                code,
                budget_seconds=getattr(pipeline.config, "fundamental_stage_timeout_seconds", 1.5),
            )
        except Exception as exc:
            logger.warning("%s(%s) 基本面聚合失败: %s", stock_name, code, exc)
            fundamental_context = pipeline.fetcher_manager.build_failed_fundamental_context(code, str(exc))

        fundamental_context = pipeline._attach_belong_boards_to_fundamental_context(
            code,
            fundamental_context,
        )

        try:
            pipeline.db.save_fundamental_snapshot(
                query_id=query_id,
                code=code,
                payload=fundamental_context,
                source_chain=fundamental_context.get("source_chain", []),
                coverage=fundamental_context.get("coverage", {}),
            )
        except Exception as exc:
            logger.debug("%s(%s) 基本面快照写入失败: %s", stock_name, code, exc)

        trend_result: Optional["TrendAnalysisResult"] = None
        try:
            market = get_market_for_stock(normalize_stock_code(code))
            end_date = get_market_now(market).date()
            start_date = end_date - timedelta(days=89)
            historical_bars = pipeline.db.get_data_range(code, start_date, end_date)
            if historical_bars:
                import pandas as pd

                df = pd.DataFrame([bar.to_dict() for bar in historical_bars])
                if pipeline.config.enable_realtime_quote and realtime_quote:
                    df = pipeline._augment_historical_with_realtime(df, realtime_quote, code)
                trend_result = pipeline.trend_analyzer.analyze(df, code)
                logger.info(
                    "%s(%s) 趋势分析: %s, 买入信号=%s, 评分=%s",
                    stock_name,
                    code,
                    trend_result.trend_status.value,
                    trend_result.buy_signal.value,
                    trend_result.signal_score,
                )
        except Exception as exc:
            logger.warning("%s(%s) 趋势分析失败: %s", stock_name, code, exc, exc_info=True)

        if use_agent:
            logger.info("%s(%s) 启用 Agent 模式进行分析", stock_name, code)
            pipeline._emit_progress(58, f"{stock_name}：正在切换 Agent 分析链路")
            return pipeline._analyze_with_agent(
                code,
                report_type,
                query_id,
                stock_name,
                realtime_quote,
                chip_data,
                fundamental_context,
                trend_result,
            )

        news_context = None
        pipeline._emit_progress(46, f"{stock_name}：正在检索新闻与舆情")
        if pipeline.search_service is not None and pipeline.search_service.is_available:
            logger.info("%s(%s) 开始多维度情报搜索...", stock_name, code)

            intel_results = pipeline.search_service.search_comprehensive_intel(
                stock_code=code,
                stock_name=stock_name,
                max_searches=5,
            )

            if intel_results:
                news_context = pipeline.search_service.format_intel_report(intel_results, stock_name)
                total_results = sum(len(response.results) for response in intel_results.values() if response.success)
                logger.info("%s(%s) 情报搜索完成: 共 %s 条结果", stock_name, code, total_results)
                logger.debug("%s(%s) 情报搜索结果:\n%s", stock_name, code, news_context)

                try:
                    query_context = pipeline._build_query_context(query_id=query_id)
                    for dimension_name, response in intel_results.items():
                        if response and response.success and response.results:
                            pipeline.db.save_news_intel(
                                code=code,
                                name=stock_name,
                                dimension=dimension_name,
                                query=response.query,
                                response=response,
                                query_context=query_context,
                            )
                except Exception as exc:
                    logger.warning("%s(%s) 保存新闻情报失败: %s", stock_name, code, exc)
        else:
            logger.info("%s(%s) 搜索服务不可用，跳过情报搜索", stock_name, code)

        if (
            pipeline.social_sentiment_service is not None
            and pipeline.social_sentiment_service.is_available
            and is_us_stock_code(code)
        ):
            try:
                social_context = pipeline.social_sentiment_service.get_social_context(code)
                if social_context:
                    logger.info("%s(%s) Social sentiment data retrieved", stock_name, code)
                    if news_context:
                        news_context = news_context + "\n\n" + social_context
                    else:
                        news_context = social_context
            except Exception as exc:
                logger.warning("%s(%s) Social sentiment fetch failed: %s", stock_name, code, exc)

        pipeline._emit_progress(58, f"{stock_name}：正在整理分析上下文")
        context = pipeline.db.get_analysis_context(code)

        if context is None:
            logger.warning("%s(%s) 无法获取历史行情数据，将仅基于新闻和实时行情分析", stock_name, code)
            market_date = get_market_now(get_market_for_stock(normalize_stock_code(code))).date()
            context = {
                "code": code,
                "stock_name": stock_name,
                "date": market_date.isoformat(),
                "data_missing": True,
                "today": {},
                "yesterday": {},
            }

        enhanced_context = pipeline._enhance_context(
            context,
            realtime_quote,
            chip_data,
            trend_result,
            stock_name,
            fundamental_context,
        )

        llm_progress_state = {"last_progress": 64}

        def _on_llm_stream(chars_received: int) -> None:
            dynamic_progress = min(92, 64 + min(chars_received // 80, 28))
            if dynamic_progress <= llm_progress_state["last_progress"]:
                return
            llm_progress_state["last_progress"] = dynamic_progress
            pipeline._emit_progress(
                dynamic_progress,
                f"{stock_name}：LLM 正在生成分析结果（已接收 {chars_received} 字符）",
            )

        pipeline._emit_progress(64, f"{stock_name}：正在请求 LLM 生成报告")
        result = pipeline.analyzer.analyze(
            enhanced_context,
            news_context=news_context,
            progress_callback=pipeline._emit_progress,
            stream_progress_callback=_on_llm_stream,
        )

        if result:
            pipeline._emit_progress(94, f"{stock_name}：正在校验并整理分析结果")
            result.query_id = query_id
            realtime_data = enhanced_context.get("realtime", {})
            result.current_price = realtime_data.get("price")
            result.change_pct = realtime_data.get("change_pct")

        if result and chip_data:
            fill_chip_structure_if_needed(result, chip_data)

        if result:
            fill_price_position_if_needed(result, trend_result, realtime_quote)

        if result and result.success:
            try:
                pipeline._emit_progress(97, f"{stock_name}：正在保存分析报告")
                context_snapshot = pipeline._build_context_snapshot(
                    enhanced_context=enhanced_context,
                    news_content=news_context,
                    realtime_quote=realtime_quote,
                    chip_data=chip_data,
                )
                pipeline.db.save_analysis_history(
                    result=result,
                    query_id=query_id,
                    report_type=report_type.value,
                    news_content=news_context,
                    context_snapshot=context_snapshot,
                    save_snapshot=pipeline.save_context_snapshot,
                )
            except Exception as exc:
                logger.warning("%s(%s) 保存分析历史失败: %s", stock_name, code, exc)

        return result
    except Exception as exc:
        logger.error("%s(%s) 分析失败: %s", stock_name, code, exc)
        logger.exception("%s(%s) 详细错误信息:", stock_name, code)
        return None


__all__ = [
    "LegacySingleStockRunRequest",
    "run_legacy_single_stock_mainline",
    "run_stock_analysis_mainline",
]
