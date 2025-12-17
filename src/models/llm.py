"""
LLM 模型初始化。
"""

from langchain_community.chat_models import ChatTongyi

from src.config import settings


def create_llm() -> ChatTongyi:
    """初始化通义千问聊天模型。
    
    Returns:
        ChatTongyi: 配置好的聊天模型实例
    """
    settings.validate()
    
    return ChatTongyi(
        model=settings.model_name,
        streaming=settings.streaming,
        temperature=settings.temperature,
        top_p=settings.top_p,
        api_key=settings.dashscope_api_key,
    )
