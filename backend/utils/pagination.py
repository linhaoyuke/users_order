# backend/utils/pagination.py

"""
分页参数安全解析与防护模块
提供安全的分页参数提取函数，防止因过大分页参数（如 per_page=1000000）导致内存耗尽（DoS），
以及因负数或非整数参数引发的数据库异常。
"""

from typing import Tuple
from flask import request

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


def get_pagination_params(
    default_page: int = DEFAULT_PAGE,
    default_per_page: int = DEFAULT_PER_PAGE,
    max_per_page: int = MAX_PER_PAGE,
    page_param: str = 'page',
    per_page_param: str = 'per_page'
) -> Tuple[int, int]:
    """
    安全提取并限制分页参数。
    
    规则：
    1. page: 必须 >= 1。若未传、传非整数或 <= 0，自动回退到 default_page。
    2. per_page / page_size: 必须在 [1, max_per_page] 范围内。
       - 若未传、传非整数或 <= 0，自动回退到 default_per_page。
       - 若 > max_per_page，强制限制为 max_per_page（默认100）。
    3. 参数兼容性：优先读取 per_page_param，若无则尝试读取备用别名（per_page <=> page_size）。
    
    :param default_page: 默认页码，默认为 1
    :param default_per_page: 默认每页条数，默认为 10
    :param max_per_page: 每页最大允许条数，默认为 100（防 DoS 攻击）
    :param page_param: 页码参数名，默认为 'page'
    :param per_page_param: 每页条数参数名，默认为 'per_page'
    :return: (page, per_page) 元组
    """
    # 1. 解析 page
    try:
        raw_page = request.args.get(page_param, type=int)
        if raw_page is None or raw_page < 1:
            page = default_page
        else:
            page = raw_page
    except (ValueError, TypeError):
        page = default_page

    # 2. 解析每页条数（支持 per_page / page_size 互相兼容）
    raw_per_page = request.args.get(per_page_param, type=int)
    if raw_per_page is None:
        alt_param = 'page_size' if per_page_param == 'per_page' else 'per_page'
        raw_per_page = request.args.get(alt_param, type=int)

    try:
        if raw_per_page is None or raw_per_page < 1:
            per_page = default_per_page
        elif raw_per_page > max_per_page:
            per_page = max_per_page
        else:
            per_page = raw_per_page
    except (ValueError, TypeError):
        per_page = default_per_page

    return page, per_page
