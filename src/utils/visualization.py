"""
图可视化工具。
"""

from pathlib import Path


def visualize_graph(graph, output_dir: Path = None) -> None:
    """可视化图结构并保存到文件。
    
    Args:
        graph: 编译后的 LangGraph 图
        output_dir: 输出目录，默认为当前目录
    """
    if output_dir is None:
        output_dir = Path(".")
    
    try:
        # 生成 Mermaid 图
        mermaid_code = graph.get_graph().draw_mermaid()
        mermaid_path = output_dir / "chat_graph.mmd"
        with open(mermaid_path, "w") as f:
            f.write(mermaid_code)
        print(f"✅ 图结构已保存到 {mermaid_path}")
        
        # 生成 PNG 图片
        try:
            png_data = graph.get_graph().draw_mermaid_png()
            png_path = output_dir / "chat_graph.png"
            with open(png_path, "wb") as f:
                f.write(png_data)
            print(f"✅ 图结构已保存到 {png_path}")
        except Exception as e:
            print(f"⚠️ PNG 生成失败: {e}")
    except Exception as e:
        print(f"⚠️ 可视化失败: {e}")
