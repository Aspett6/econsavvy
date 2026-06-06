"""
知识图谱 — 8 门财经课程的知识点关系网络
"""
import json
import datetime
import streamlit as st
from core.persistence import load_study_stats

# ============================================================
# 知识点关系定义
# ============================================================
KNOWLEDGE_GRAPH = {
    "微观经济学": {
        "parent": None,
        "children": ["需求与供给", "消费者选择", "企业生产与成本", "完全竞争市场", "不完全竞争市场", "要素市场", "一般均衡", "市场失灵"],
    },
    "需求与供给": {"parent": "微观经济学", "children": ["均衡价格", "弹性理论"]},
    "消费者选择": {"parent": "微观经济学", "children": ["效用论", "预算约束", "无差异曲线"]},
    "企业生产与成本": {"parent": "微观经济学", "children": ["短期成本", "长期成本", "生产函数"]},
    "完全竞争市场": {"parent": "微观经济学", "children": ["利润最大化"]},
    "不完全竞争市场": {"parent": "微观经济学", "children": ["垄断", "寡头", "垄断竞争"]},
    "要素市场": {"parent": "微观经济学", "children": ["劳动市场", "资本市场"]},
    "一般均衡": {"parent": "微观经济学", "children": ["帕累托效率", "福利经济学"]},
    "市场失灵": {"parent": "微观经济学", "children": ["外部性", "公共物品", "信息不对称"]},

    "宏观经济学": {
        "parent": None,
        "children": ["GDP与国民收入", "IS-LM模型", "AD-AS模型", "失业与通胀", "货币政策", "财政政策", "经济增长"],
    },
    "GDP与国民收入": {"parent": "宏观经济学", "children": ["核算方法", "收入决定"]},
    "IS-LM模型": {"parent": "宏观经济学", "children": ["IS曲线", "LM曲线"]},
    "AD-AS模型": {"parent": "宏观经济学", "children": ["总需求", "总供给"]},
    "货币政策": {"parent": "宏观经济学", "children": ["利率", "准备金", "公开市场操作"]},
    "财政政策": {"parent": "宏观经济学", "children": ["税收", "政府支出"]},

    "金融学": {
        "parent": None,
        "children": ["货币银行", "金融市场", "中央银行", "投资学基础", "风险管理"],
    },
    "货币银行": {"parent": "金融学", "children": ["货币供给", "信用创造"]},
    "金融市场": {"parent": "金融学", "children": ["股票市场", "债券市场", "衍生品"]},
    "中央银行": {"parent": "金融学", "children": ["货币政策工具"]},
    "投资学基础": {"parent": "金融学", "children": ["CAPM", "资产配置"]},

    "会计学": {
        "parent": None,
        "children": ["六大会计要素", "借贷记账法", "财务报表", "业务核算"],
    },
    "借贷记账法": {"parent": "会计学", "children": ["会计分录", "试算平衡"]},
    "财务报表": {"parent": "会计学", "children": ["资产负债表", "利润表", "现金流量表"]},

    "税收学": {
        "parent": None,
        "children": ["增值税", "消费税", "企业所得税", "个人所得税", "国际税收"],
    },
    "增值税": {"parent": "税收学", "children": ["进项税额", "销项税额", "简易计税"]},
    "企业所得税": {"parent": "税收学", "children": ["应纳税所得额", "税前扣除", "汇算清缴"]},

    "商法": {
        "parent": None,
        "children": ["公司法", "合同法", "票据法", "保险法", "破产法", "反垄断法"],
    },
    "公司法": {"parent": "商法", "children": ["公司设立", "股东权利", "董事会"]},
    "合同法": {"parent": "商法", "children": ["合同订立", "合同效力", "违约责任"]},

    "统计学": {"parent": None, "children": ["描述统计", "推断统计", "回归分析"]},
    "财政学": {"parent": None, "children": ["公共产品", "财政支出", "税收原理", "政府预算"]},
    "管理学": {"parent": None, "children": ["计划", "组织", "领导", "控制", "组织行为学"]},
}


def get_mastery_color(kp_name: str, stats: dict) -> str:
    """根据掌握度返回颜色"""
    kp_data = stats.get("knowledge_points", {}).get(kp_name)
    if not kp_data:
        return "#d1d5db"  # gray: not tested
    correct = kp_data.get("correct", 0)
    wrong = kp_data.get("wrong", 0)
    total = correct + wrong
    if total == 0:
        return "#d1d5db"
    rate = correct / total
    if rate >= 0.8:
        return "#16a34a"  # green: strong
    elif rate >= 0.6:
        return "#d97706"  # orange: moderate
    else:
        return "#dc2626"  # red: weak


def render_knowledge_graph():
    """在 Streamlit 中渲染知识图谱"""
    stats = load_study_stats()
    kp_stats = stats.get("knowledge_points", {})

    st.markdown("### 🗺️ 知识图谱")
    st.caption("绿色=扎实  红色=薄弱  灰色=未测试  |  点击科目展开章节")

    # 按课程展示
    root_subjects = [k for k, v in KNOWLEDGE_GRAPH.items() if v.get("parent") is None]

    for subject in sorted(root_subjects):
        info = KNOWLEDGE_GRAPH[subject]
        children = info.get("children", [])

        # 计算科目整体掌握度
        total_q = 0
        total_c = 0
        for child in children:
            cd = kp_stats.get(child, {})
            total_c += cd.get("correct", 0)
            total_q += cd.get("correct", 0) + cd.get("wrong", 0)

        subj_color = "#16a34a" if (total_q > 0 and total_c / total_q >= 0.7) else \
                     "#d97706" if total_q > 0 else "#6b7280"

        with st.expander(f"📘 {subject}" + (f" · 正确率 {total_c/total_q*100:.0f}%" if total_q > 0 else "")):
            # 子节点横排
            cols = st.columns(min(len(children), 4))
            for i, child in enumerate(children):
                color = get_mastery_color(child, stats)
                child_data = kp_stats.get(child, {})
                c = child_data.get("correct", 0)
                w = child_data.get("wrong", 0)

                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="border-left: 3px solid {color}; padding: 0.3rem 0.5rem;
                                margin: 0.2rem 0; font-size: 0.8rem; background: #f9fafb;
                                border-radius: 4px;">
                        <b>{child}</b><br>
                        <span style="font-size: 0.7rem; color: #6b7280;">
                            {'[OK] ' + str(c) + '/' + str(c+w) if c+w > 0 else '[未测试]'}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # 三级节点
                    grand_info = KNOWLEDGE_GRAPH.get(child, {})
                    grand_children = grand_info.get("children", [])
                    for gc in grand_children:
                        gc_color = get_mastery_color(gc, stats)
                        gc_data = kp_stats.get(gc, {})
                        gc_c = gc_data.get("correct", 0)
                        gc_w = gc_data.get("wrong", 0)
                        st.markdown(f"""
                        <div style="border-left: 2px solid {gc_color}; padding: 0.15rem 0.4rem;
                                    margin: 0.1rem 0 0.1rem 0.5rem; font-size: 0.7rem;">
                            {gc} {'· ' + str(gc_c) + '/' + str(gc_c+gc_w) if gc_c+gc_w > 0 else ''}
                        </div>
                        """, unsafe_allow_html=True)

    # 底部图例
    st.markdown("""
    <div style="display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.75rem; color: #6b7280;">
        <span>🟢 正确率>=80%</span>
        <span>🟠 60-80%</span>
        <span>🔴 <60%</span>
        <span>⬜ 未测试</span>
    </div>
    """, unsafe_allow_html=True)
