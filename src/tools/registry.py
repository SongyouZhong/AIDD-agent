"""
工具注册中心。

集中管理所有可用工具的创建。
"""

from typing import List
from langchain_core.tools import BaseTool

from .search import create_search_tool


def create_tools() -> List[BaseTool]:
    """创建并返回所有可用工具的列表。
    
    Returns:
        List[BaseTool]: 工具列表
    """
    tools = [
        create_search_tool(),
    ]
    return tools
