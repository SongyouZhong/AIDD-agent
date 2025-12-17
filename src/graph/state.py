"""
LangGraph 状态定义。
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """聊天状态。
    
    Attributes:
        messages: 会话消息列表，使用 add_messages 注解表示每次更新时自动追加
    """
    messages: Annotated[list, add_messages]
