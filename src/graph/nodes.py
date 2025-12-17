"""
LangGraph 节点函数定义。
"""

from typing import Dict, List
from langchain_core.messages import AIMessage

from .state import ChatState


def chatbot_node(state: ChatState, llm_with_tools) -> Dict[str, List]:
    """聊天机器人节点。
    
    读取当前状态的消息历史，调用模型生成新消息。
    支持工具调用：模型可以决定是否需要使用搜索等工具。
    
    Args:
        state: 当前聊天状态
        llm_with_tools: 绑定了工具的 LLM 实例
        
    Returns:
        包含新消息的字典
    """
    # 直接传递完整的消息历史给模型
    # llm_with_tools.invoke() 会返回 AIMessage 对象（可能包含工具调用）
    response = llm_with_tools.invoke(state["messages"])
    
    # 返回包含 AIMessage 的字典
    return {"messages": [response]}
