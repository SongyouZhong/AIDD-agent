#!/usr/bin/env python
"""
LangGraph 聊天机器人主入口。

使用阿里云百炼的通义千问构建聊天机器人，支持 Tavily 搜索。

运行前请确认：
1. 已安装 langgraph、langchain-community、dashscope、langchain-tavily 等依赖。
2. 在 .env 文件中设置 DASHSCOPE_API_KEY 和 TAVILY_API_KEY。

使用方法：
    python main.py
"""

import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.chat import interactive_chat


def main():
    """主入口函数。"""
    interactive_chat()


if __name__ == "__main__":
    main()
