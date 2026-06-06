"""
知识清单浏览器 — exampass 知识清单 + 章节测试（暗色适配）
"""
import os
import streamlit as st
from config import KB_DIR

# 注入到 exampass HTML 中的暗色模式 CSS
DARK_CSS_INJECT = """
<style>
  body { background: #1a1a2e !important; color: #e5e7eb !important; }
  .container, main, article, section { background: #1a1a2e !important; }
  h1, h2, h3, h4, h5, h6 { color: #f3f4f6 !important; }
  p, li, td, th, span, div { color: #d1d5db !important; }
  .kp { color: #f3f4f6 !important; font-weight: 700; }
  .exp { color: #9ca3af !important; }
  .tag-must { background: #7f1d1d !important; color: #fca5a5 !important; }
  .tag-key { background: #1e3a5f !important; color: #93c5fd !important; }
  .tag-freq { background: #1e3a1e !important; color: #86efac !important; }
  .tag-info { background: #2a2a3a !important; color: #a5b4fc !important; }
  table { background: #16213e !important; border-color: #2a2a4a !important; }
  th { background: #2a2a4a !important; color: #e5e7eb !important; border-color: #3a3a5a !important; }
  td { background: #16213e !important; color: #d1d5db !important; border-color: #2a2a4a !important; }
  blockquote { background: #2a2a1a !important; border-left-color: #f59e0b !important; color: #fbbf24 !important; }
  code, pre { background: #2a2a4a !important; color: #e5e7eb !important; }
  a { color: #60a5fa !important; }
  input, textarea, select, button { background: #2a2a4a !important; color: #e5e7eb !important; border-color: #3a3a5a !important; }
  .quiz-option:hover { background: #2a2a4a !important; }
  .correct { background: #0a3622 !important; }
  .incorrect { background: #3b0a0a !important; }
  hr { border-color: #2a2a4a !important; }
</style>"""


def _get_subjects() -> list:
    """扫描知识库中有 HTML 或 txt 内容的科目"""
    subjects = []
    if not os.path.isdir(KB_DIR):
        return subjects
    for name in sorted(os.listdir(KB_DIR)):
        path = os.path.join(KB_DIR, name)
        if not os.path.isdir(path):
            continue
        has_knowledge = os.path.exists(os.path.join(path, "知识清单.html"))
        has_test = os.path.exists(os.path.join(path, "章节测试.html"))
        has_txt = any(f.endswith('.txt') for f in os.listdir(path))
        if has_knowledge or has_test or has_txt:
            subjects.append({
                "name": name,
                "has_knowledge": has_knowledge,
                "has_test": has_test,
            })
    return subjects


def _read_html(filepath: str, dark: bool = False) -> str:
    """读取 HTML 文件，可选注入暗色模式 CSS"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        if dark:
            html = html.replace('</head>', DARK_CSS_INJECT + '\n</head>')
        return html
    except Exception:
        return "<p>无法加载文件</p>"


def render_knowledge_browser():
    """知识清单浏览器"""
    st.markdown("## 📚 知识清单与章节测试")

    subjects = _get_subjects()

    if not subjects:
        st.info("知识库中暂无内容。运行 exampass 生成知识清单后将自动显示。")
        st.markdown("已有内容：会计学、税收学")
        return

    # 科目选择
    st.markdown("### 选择科目")
    cols = st.columns(min(len(subjects), 4))

    if "kb_selected" not in st.session_state:
        st.session_state.kb_selected = subjects[0]["name"] if subjects else None

    for i, subj in enumerate(subjects):
        with cols[i % 4]:
            status = []
            if subj["has_knowledge"]:
                status.append("K")
            if subj["has_test"]:
                status.append("T")
            tag = "+".join(status) if status else "?"

            is_current = st.session_state.kb_selected == subj["name"]
            btn_type = "primary" if is_current else "secondary"
            if st.button(
                f"[{tag}] {subj['name']}",
                key=f"kb_{subj['name']}",
                use_container_width=True,
                type=btn_type,
            ):
                st.session_state.kb_selected = subj["name"]
                st.rerun()

    selected_name = st.session_state.kb_selected
    if not selected_name or selected_name not in [s["name"] for s in subjects]:
        selected_name = subjects[0]["name"]

    st.divider()
    st.markdown(f"## {selected_name}")

    subj_path = os.path.join(str(KB_DIR), selected_name)
    dark = st.session_state.get("dark_mode", False)

    tab1, tab2 = st.tabs(["📖 知识清单", "📝 章节测试"])

    with tab1:
        knowledge_path = os.path.join(subj_path, "知识清单.html")
        if os.path.exists(knowledge_path):
            html = _read_html(knowledge_path, dark=dark)
            st.components.v1.html(html, height=800, scrolling=True)
        else:
            st.warning("该科目尚未生成知识清单。")

    with tab2:
        test_path = os.path.join(subj_path, "章节测试.html")
        if os.path.exists(test_path):
            html = _read_html(test_path, dark=dark)
            st.components.v1.html(html, height=900, scrolling=True)
        else:
            st.warning("该科目尚未生成章节测试。")
