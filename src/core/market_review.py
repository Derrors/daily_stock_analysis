# -*- coding: utf-8 -*-
"""
===================================
股票智能分析系统 - 大盘复盘模块（支持 A 股 / 美股）
===================================

职责：
1. 根据 MARKET_REVIEW_REGION 配置选择市场区域（cn / us / both）
2. 执行大盘复盘分析并生成复盘报告
3. 通过报告输出服务保存复盘报告
"""

import logging
from datetime import datetime
from typing import Optional

from src.config import get_config
from src.report_output import ReportOutputService
from src.market_analyzer import MarketAnalyzer
from src.report_language import normalize_report_language
from src.search_service import SearchService
from src.analyzer import GeminiAnalyzer


logger = logging.getLogger(__name__)


def _get_market_review_text(language: str) -> dict[str, str]:
    normalized = normalize_report_language(language)
    if normalized == "en":
        return {
            "root_title": "# 🎯 Market Review",
            "push_title": "🎯 Market Review",
            "cn_title": "# A-share Market Recap",
            "us_title": "# US Market Recap",
            "separator": "> US market recap follows",
        }
    return {
        "root_title": "# 🎯 大盘复盘",
        "push_title": "🎯 大盘复盘",
        "cn_title": "# A股大盘复盘",
        "us_title": "# 美股大盘复盘",
        "separator": "> 以下为美股大盘复盘",
    }


def run_market_review(
    report_output_service: ReportOutputService,
    analyzer: Optional[GeminiAnalyzer] = None,
    search_service: Optional[SearchService] = None,
    override_region: Optional[str] = None,
) -> Optional[str]:
    """
    执行大盘复盘分析

    Args:
        report_output_service: 报告输出服务（旧调用方传入的 notifier 对象也可兼容工作）
        analyzer: AI分析器（可选）
        search_service: 搜索服务（可选）
        override_region: 覆盖 config 的 market_review_region（Issue #373 交易日过滤后有效子集）

    Returns:
        复盘报告文本
    """
    logger.info("开始执行大盘复盘分析...")
    config = get_config()
    review_text = _get_market_review_text(getattr(config, "report_language", "zh"))
    region = (
        override_region
        if override_region is not None
        else (getattr(config, 'market_review_region', 'cn') or 'cn')
    )
    if region not in ('cn', 'us', 'both'):
        region = 'cn'

    try:
        if region == 'both':
            # 顺序执行 A 股 + 美股，合并报告
            cn_analyzer = MarketAnalyzer(
                search_service=search_service, analyzer=analyzer, region='cn'
            )
            us_analyzer = MarketAnalyzer(
                search_service=search_service, analyzer=analyzer, region='us'
            )
            logger.info("生成 A 股大盘复盘报告...")
            cn_report = cn_analyzer.run_daily_review()
            logger.info("生成美股大盘复盘报告...")
            us_report = us_analyzer.run_daily_review()
            review_report = ''
            if cn_report:
                review_report = f"{review_text['cn_title']}\n\n{cn_report}"
            if us_report:
                if review_report:
                    review_report += f"\n\n---\n\n{review_text['separator']}\n\n"
                review_report += f"{review_text['us_title']}\n\n{us_report}"
            if not review_report:
                review_report = None
        else:
            market_analyzer = MarketAnalyzer(
                search_service=search_service,
                analyzer=analyzer,
                region=region,
            )
            review_report = market_analyzer.run_daily_review()
        
        if review_report:
            # 保存报告到文件
            date_str = datetime.now().strftime('%Y%m%d')
            report_filename = f"market_review_{date_str}.md"
            filepath = report_output_service.save_report_to_file(
                f"{review_text['root_title']}\n\n{review_report}",
                report_filename
            )
            logger.info(f"大盘复盘报告已保存: {filepath}")
            
            return review_report
        
    except Exception as e:
        logger.error(f"大盘复盘分析失败: {e}")
    
    return None
