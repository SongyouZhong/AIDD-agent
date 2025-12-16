from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 加载 .env 文件中的环境变量
load_dotenv()

# 验证环境变量是否加载成功
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))


# ============ LangGraph 示例 ============

# 1. 定义状态 (State) - 图中所有节点共享的数据结构
class State(TypedDict):
    messages: Annotated[list, add_messages]  # 消息列表，使用 add_messages 自动合并
    count: int  # 自定义状态字段


# 2. 定义节点函数 (Nodes) - 每个节点是一个处理函数
def node_a(state: State) -> dict:
    """节点 A: 处理输入并增加计数"""
    print("执行节点 A")
    return {
        "messages": [{"role": "assistant", "content": "节点 A 处理完成"}],
        "count": state.get("count", 0) + 1
    }


def node_b(state: State) -> dict:
    """节点 B: 继续处理"""
    print("执行节点 B")
    return {
        "messages": [{"role": "assistant", "content": "节点 B 处理完成"}],
        "count": state["count"] + 1
    }


def node_c(state: State) -> dict:
    """节点 C: 最终处理"""
    print("执行节点 C")
    return {
        "messages": [{"role": "assistant", "content": f"最终结果，总计数: {state['count'] + 1}"}],
        "count": state["count"] + 1
    }


# 3. 定义条件边函数 (用于条件路由)
def should_go_to_c(state: State) -> str:
    """根据条件决定下一步走向"""
    if state["count"] >= 2:
        return "node_c"  # 如果计数 >= 2，去节点 C
    else:
        return "node_b"  # 否则继续去节点 B


# 4. 创建图 (Graph)
def create_graph():
    # 初始化 StateGraph，传入状态类型
    graph = StateGraph(State)
    
    # 5. 添加节点 (add_node)
    graph.add_node("node_a", node_a)
    graph.add_node("node_b", node_b)
    graph.add_node("node_c", node_c)
    
    # 6. 添加边 (add_edge) - 定义节点之间的连接
    
    # 从 START 到 node_a (入口边)
    graph.add_edge(START, "node_a")
    
    # 条件边: 从 node_a 根据条件选择下一个节点
    graph.add_conditional_edges(
        "node_a",           # 源节点
        should_go_to_c,     # 条件函数
        {                   # 路由映射
            "node_b": "node_b",
            "node_c": "node_c"
        }
    )
    
    # 普通边: node_b -> node_c
    graph.add_edge("node_b", "node_c")
    
    # 从 node_c 到 END (出口边)
    graph.add_edge("node_c", END)
    
    # 7. 编译图
    return graph.compile()


# 8. 可视化图
def visualize_graph(app):
    """可视化图结构"""
    # 方法1: 生成 Mermaid 图 (文本格式)
    print("\n--- Mermaid 图 (可复制到 mermaid.live 查看) ---\n")
    mermaid_code = app.get_graph().draw_mermaid()
    print(mermaid_code)
    
    # 保存 Mermaid 到文件
    with open("graph.mmd", "w") as f:
        f.write(mermaid_code)
    print("\n✅ Mermaid 图已保存到 graph.mmd")
    
    # 方法2: 生成 PNG 图片 (需要安装额外依赖)
    try:
        png_data = app.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_data)
        print("✅ PNG 图片已保存到 graph.png")
    except Exception as e:
        print(f"⚠️ 无法生成 PNG (可能需要安装依赖): {e}")
        print("   可以运行: pip install pyppeteer 或使用在线工具查看 Mermaid")


# 9. 运行图
if __name__ == "__main__":
    # 创建并编译图
    app = create_graph()
    
    # 可视化图结构
    visualize_graph(app)
    
    # 初始状态
    initial_state = {
        "messages": [{"role": "user", "content": "开始执行"}],
        "count": 0
    }
    
    # 执行图 - 使用 stream 模式可以看到每一步的执行过程
    print("\n--- 开始执行 LangGraph (流式追踪) ---\n")
    
    for step, state in enumerate(app.stream(initial_state)):
        print(f"📍 步骤 {step + 1}: {list(state.keys())[0]}")
        print(f"   状态: {state}")
        print()
    
    # 也可以用 invoke 获取最终结果
    print("--- 最终执行结果 ---")
    final_result = app.invoke(initial_state)
    print(f"最终计数: {final_result['count']}")
    print(f"消息数量: {len(final_result['messages'])}")
