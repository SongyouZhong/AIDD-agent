"""
应用配置管理。

从环境变量和 .env 文件加载配置。
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Settings:
    """应用配置类。"""
    
    # DashScope API 配置
    dashscope_api_key: str = ""
    
    # Tavily API 配置
    tavily_api_key: str = ""
    
    # 模型配置
    model_name: str = "qwen-max"
    temperature: float = 0.7
    top_p: float = 0.8
    streaming: bool = True
    
    # Tavily 搜索配置
    tavily_max_results: int = 2
    
    def __post_init__(self):
        """从环境变量加载配置。"""
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
    
    def validate(self) -> None:
        """验证必要的配置项。"""
        if not self.dashscope_api_key or self.dashscope_api_key == "your_dashscope_api_key":
            raise ValueError(
                "请设置 DASHSCOPE_API_KEY！\n"
                "方式1: 在 .env 文件中添加: DASHSCOPE_API_KEY=sk-xxx\n"
                "方式2: 运行前设置环境变量: export DASHSCOPE_API_KEY=sk-xxx"
            )
        
        if not self.tavily_api_key:
            raise ValueError(
                "请设置 TAVILY_API_KEY！\n"
                "在 .env 文件中添加: TAVILY_API_KEY=tvly-xxx"
            )


# 全局配置实例
settings = Settings()
