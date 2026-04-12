# -*- coding: utf-8 -*-
"""
===================================
数据源策略层 - 包初始化
===================================

当前运行时数据源策略：
1. TushareFetcher - 唯一保留的运行时行情数据源

说明：
- 旧数据源实现文件可能暂时仍留在仓库历史中，但主链已不再从这里导出它们
- 港股 / 美股代码识别辅助函数仍保留，供服务层判断市场使用
"""

from __future__ import annotations

import re

from .base import BaseFetcher, DataFetcherManager
from .tushare_fetcher import TushareFetcher
from .us_index_mapping import is_us_index_code, is_us_stock_code, get_us_index_yf_symbol, US_INDEX_MAPPING

_HK_CODE_PATTERN = re.compile(r'^(HK)?\d{5}$', re.IGNORECASE)


def is_hk_stock_code(stock_code: str) -> bool:
    """Return True when the input looks like a Hong Kong stock code."""
    normalized = (stock_code or '').strip().upper()
    if not normalized:
        return False
    if normalized.endswith('.HK'):
        return True
    return bool(_HK_CODE_PATTERN.match(normalized))


__all__ = [
    'BaseFetcher',
    'DataFetcherManager',
    'TushareFetcher',
    'is_us_index_code',
    'is_us_stock_code',
    'is_hk_stock_code',
    'get_us_index_yf_symbol',
    'US_INDEX_MAPPING',
]
