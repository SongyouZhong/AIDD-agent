"""
Tavily 搜索工具。
"""

from langchain_tavily import TavilySearch

from src.config import settings


def create_search_tool() -> TavilySearch:
    """创建 Tavily 搜索工具实例。
    
    Returns:
        TavilySearch: 配置好的搜索工具
    """
    return TavilySearch(
        max_results=settings.tavily_max_results,
        api_key=settings.tavily_api_key,
    )
