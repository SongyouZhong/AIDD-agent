"""
使用 LangGraph 与阿里云百炼的通义千问构建聊天机器人。

运行前请确认：
1. 已安装 langgraph、langchain-community、dashscope 等依赖。
2. 在 .env 文件中设置 DASHSCOPE_API_KEY 为有效的 API 密钥。
"""

import os
from typing import Annotated, Dict, Iterable
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_community.llms import Tongyi
from langchain_core.messages import AIMessage, HumanMessage

# 加载 .env 文件中的环境变量
load_dotenv()

class ChatState(TypedDict):
    # 会话状态保存所有消息；add_messages 表示每次更新时会自动追加
    messages: Annotated[list, add_messages]

def create_llm() -> Tongyi:
    """初始化通义千问模型包装器。"""
    # 从环境变量或 .env 文件读取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key or api_key == "your_dashscope_api_key":
        raise ValueError(
            "请设置 DASHSCOPE_API_KEY！\n"
            "方式1: 在 .env 文件中添加: DASHSCOPE_API_KEY=sk-xxx\n"
            "方式2: 运行前设置环境变量: export DASHSCOPE_API_KEY=sk-xxx"
        )
    return Tongyi(
        model="qwen-max",
        streaming=True,
        temperature=0.7,
        top_p=0.8,
        api_key=api_key,
    )

def chatbot_node(state: ChatState, llm: Tongyi) -> Dict[str, Iterable]:
    """
    用于 LangGraph 的节点函数。
    读取当前状态的消息历史，调用模型生成新消息，并返回一个字典。
    """
    # 将消息列表转换为字符串格式供 LLM 使用
    messages = state["messages"]
    
    # 获取最后一条用户消息作为 prompt
    # 如果需要多轮对话，可以构建完整的对话历史
    user_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    if not user_messages:
        return {"messages": [AIMessage(content="请输入消息。")]}
    
    # 使用最后一条用户消息
    prompt = user_messages[-1].content
    
    # 验证 prompt 不为空
    if not prompt or not prompt.strip():
        return {"messages": [AIMessage(content="请输入有效的消息。")]}
    
    # 调用 LLM 获取响应（返回字符串）
    response_text = llm.invoke(prompt)
    
    # 将响应包装成 AIMessage
    return {"messages": [AIMessage(content=response_text)]}

def build_graph(llm: Tongyi):
    """构建 LangGraph 状态机。这里只包含一个聊天节点。"""
    graph_builder = StateGraph(ChatState)
    # 使用 lambda 将 llm 绑定进节点
    graph_builder.add_node("chatbot", lambda state: chatbot_node(state, llm))
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    return graph_builder.compile()

def visualize_graph(graph) -> None:
    """可视化图结构并保存到文件。"""
    try:
        # 生成 Mermaid 图
        mermaid_code = graph.get_graph().draw_mermaid()
        with open("chat_graph.mmd", "w") as f:
            f.write(mermaid_code)
        print("✅ 图结构已保存到 chat_graph.mmd")
        
        # 生成 PNG 图片
        try:
            png_data = graph.get_graph().draw_mermaid_png()
            with open("chat_graph.png", "wb") as f:
                f.write(png_data)
            print("✅ 图结构已保存到 chat_graph.png")
        except Exception as e:
            print(f"⚠️ PNG 生成失败: {e}")
    except Exception as e:
        print(f"⚠️ 可视化失败: {e}")

def interactive_chat(show_flow: bool = False) -> None:
    """命令行下的对话循环。
    
    Args:
        show_flow: 是否显示每一步的执行流向
    """
    llm = create_llm()
    graph = build_graph(llm)
    
    # 可视化图结构
    print("\n📊 正在生成图结构可视化...")
    visualize_graph(graph)
    
    print("\n聊天机器人已启动，输入消息并按回车发送。")
    print("特殊命令: exit/quit=退出, flow=切换流向显示\n")
    
    while True:
        try:
            user_input = input("\n👤 User: ")
        except EOFError:
            break
            
        # 检查是否为空输入
        if not user_input.strip():
            continue
            
        if user_input.strip().lower() in {"exit", "quit"}:
            print("🤖 Assistant: Goodbye!")
            break
        
        # 切换流向显示
        if user_input.strip().lower() == "flow":
            show_flow = not show_flow
            status = "开启" if show_flow else "关闭"
            print(f"✓ 流向追踪已{status}")
            continue
            
        # 初始状态包含用户消息（使用 HumanMessage）
        initial_state: ChatState = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        # 调用 graph.stream 逐步获取模型输出
        if show_flow:
            print("\n🔄 执行流向:")
            
        for step_num, event in enumerate(graph.stream(initial_state), 1):
            if show_flow:
                node_name = list(event.keys())[0]
                print(f"  步骤 {step_num}: [{node_name}] 正在处理...")
                
            for value in event.values():
                last_msg = value["messages"][-1]
                # 检查是否为 AIMessage
                if isinstance(last_msg, AIMessage):
                    print(f"\n🤖 Assistant: {last_msg.content}")
                    
    print("\n对话结束。")

if __name__ == "__main__":
    interactive_chat()
