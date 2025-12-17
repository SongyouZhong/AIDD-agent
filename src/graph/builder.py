"""
LangGraph 图构建器。
"""

from typing import List
from langchain_community.chat_models import ChatTongyi
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .state import ChatState
from .nodes import chatbot_node


def build_graph(llm: ChatTongyi, tools: List[BaseTool]):
    """构建 LangGraph 状态机。
    
    支持聊天节点和工具调用节点。
    
    流程:
        chatbot -> [tools_condition] -> tools -> chatbot -> END
                                    -> END
    
    Args:
        llm: 聊天模型实例
        tools: 工具列表
        
    Returns:
        编译后的图
    """
    # 将工具绑定到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 创建状态图
    graph_builder = StateGraph(ChatState)
    
    # 添加聊天节点
    graph_builder.add_node("chatbot", lambda state: chatbot_node(state, llm_with_tools))
    
    # 添加工具节点
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    
    # 添加条件边：根据模型输出决定是调用工具还是结束
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,  # 自动判断是否需要调用工具
    )
    
    # 工具执行完后返回到 chatbot 继续处理
    graph_builder.add_edge("tools", "chatbot")
    
    # 设置入口点
    graph_builder.set_entry_point("chatbot")
    
    return graph_builder.compile()
