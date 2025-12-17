"""
交互式聊天功能。
"""

from langchain_core.messages import AIMessage, HumanMessage

from src.models import create_llm
from src.tools import create_tools
from src.graph import ChatState, build_graph
from src.utils import visualize_graph


def interactive_chat(show_flow: bool = False) -> None:
    """命令行下的对话循环。
    
    Args:
        show_flow: 是否显示每一步的执行流向
    """
    llm = create_llm()
    tools = create_tools()
    graph = build_graph(llm, tools)
    
    # 可视化图结构
    print("\n📊 正在生成图结构可视化...")
    visualize_graph(graph)
    
    print("\n聊天机器人已启动，输入消息并按回车发送。")
    print("特殊命令: exit/quit=退出, flow=切换流向显示, clear=清空历史\n")
    print("💡 提示：机器人现在可以使用 Tavily 搜索引擎查找最新信息！\n")
    
    # 维护完整的对话历史
    conversation_history = []
    
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
        
        # 清空对话历史
        if user_input.strip().lower() == "clear":
            conversation_history = []
            print("✓ 对话历史已清空")
            continue
            
        # 添加用户消息到历史
        conversation_history.append(HumanMessage(content=user_input))
        
        # 初始状态包含完整对话历史
        initial_state: ChatState = {
            "messages": conversation_history
        }
        
        # 调用 graph.stream 逐步获取模型输出
        if show_flow:
            print("\n🔄 执行流向:")
        
        final_response = None
        for step_num, event in enumerate(graph.stream(initial_state), 1):
            if show_flow:
                node_name = list(event.keys())[0]
                if node_name == "tools":
                    print(f"  步骤 {step_num}: [🔧 {node_name}] 正在调用搜索工具...")
                else:
                    print(f"  步骤 {step_num}: [💭 {node_name}] 正在思考...")
                
            for value in event.values():
                # 更新对话历史
                conversation_history = value["messages"]
                
                # 获取最后一条消息
                last_msg = value["messages"][-1]
                
                # 只显示 AI 的最终回复（非工具调用消息）
                if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                    final_response = last_msg.content
        
        # 显示最终回复
        if final_response:
            print(f"\n🤖 Assistant: {final_response}")
                    
    print("\n对话结束。")
