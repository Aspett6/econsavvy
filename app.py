"""EconSavvy · 经世智用 v5 — AI 智能学习助手"""
import re
import os
import time
import datetime
import uuid
import streamlit as st

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, KB_DIR
from core.ai_client import stream_ai
from core.cache import get_cache
from core.prompts import SYSTEM_PROMPTS
from core.utils import (
    strip_answers_comment,
    extract_hidden_answers,
    parse_user_answers,
)
from core.grading import grade_answers_and_build_prompt
from core.exam import render_exam_ui
from core.knowledge_base import get_kb
from core.knowledge_graph import render_knowledge_graph
from core.knowledge_browser import render_knowledge_browser
from core.spaced_repetition import count_due_reviews, advance_review_stage
from core.persistence import (
    load_wrong_answer_book,
    load_study_stats,
    save_wrong_answer_book,
    save_study_stats,
    clear_wrong_answer_book,
    mark_reviewed,
    load_conversations,
    save_conversations,
)

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="EconSavvy · 经世智用",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto",
)

# ============================================================
# 全局 CSS + JS — v5 蓝色玻璃拟态 · 侧边栏导航
# ============================================================
st.markdown("""
<style>
    /* ========================================
       CSS 变量 — 蓝色主题
       ======================================== */
    :root {
        --blue-50: #eff6ff;
        --blue-100: #dbeafe;
        --blue-200: #bfdbfe;
        --blue-300: #93c5fd;
        --blue-400: #60a5fa;
        --blue-500: #3b82f6;
        --blue-600: #2563eb;
        --blue-700: #1d4ed8;
        --blue-800: #1e40af;
        --indigo-400: #818cf8;
        --indigo-500: #6366f1;
        --cyan-400: #22d3ee;
        --cyan-500: #06b6d4;
        --slate-50: #f8fafc;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-300: #cbd5e1;
        --slate-400: #94a3b8;
        --slate-500: #64748b;
        --slate-600: #475569;
        --slate-700: #334155;
        --slate-800: #1e293b;
        --slate-900: #0f172a;
        --white: #ffffff;

        --gradient-primary: linear-gradient(135deg, #2563eb 0%, #6366f1 50%, #06b6d4 100%);
        --gradient-blue: linear-gradient(135deg, #3b82f6, #2563eb);
        --gradient-card: linear-gradient(135deg, rgba(37,99,235,0.03) 0%, rgba(99,102,241,0.06) 100%);
        --shadow-xs: 0 1px 2px rgba(0,0,0,0.03);
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 8px 24px rgba(37,99,235,0.07), 0 2px 6px rgba(0,0,0,0.04);
        --shadow-lg: 0 16px 40px rgba(37,99,235,0.10), 0 4px 12px rgba(0,0,0,0.04);
        --shadow-glow: 0 0 0 1px rgba(37,99,235,0.12), 0 8px 32px -6px rgba(37,99,235,0.20);
    }

    /* ========================================
       全局
       ======================================== */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: linear-gradient(170deg, #f8faff 0%, #f0f4ff 25%, #f6f8fc 60%, #f8fafc 100%);
    }

    /* 背景光斑 — shimmer-glow 动画 */
    .stApp::before {
        content: '';
        position: fixed; top: -20%; left: -10%;
        width: 60%; height: 60%;
        background: radial-gradient(ellipse at 25% 20%, rgba(37,99,235,0.07) 0%, transparent 70%);
        pointer-events: none; z-index: -1;
        animation: shimmerGlow1 8s ease-in-out infinite;
    }
    .stApp::after {
        content: '';
        position: fixed; bottom: -15%; right: -10%;
        width: 55%; height: 55%;
        background: radial-gradient(ellipse at 75% 80%, rgba(99,102,241,0.06) 0%, transparent 70%);
        pointer-events: none; z-index: -1;
        animation: shimmerGlow2 10s ease-in-out infinite;
    }
    /* 第三个光斑 */
    .main::before {
        content: '';
        position: fixed; top: 40%; left: 50%;
        width: 40%; height: 40%;
        background: radial-gradient(ellipse at 50% 50%, rgba(6,182,212,0.04) 0%, transparent 70%);
        pointer-events: none; z-index: -1;
        animation: shimmerGlow3 12s ease-in-out infinite;
    }

    @keyframes shimmerGlow1 {
        0%, 100% { opacity: 0.6; transform: translate(0, 0) scale(1); }
        25% { opacity: 1; transform: translate(3%, 2%) scale(1.06); }
        50% { opacity: 0.5; transform: translate(-1%, -1%) scale(0.96); }
        75% { opacity: 0.9; transform: translate(1%, 3%) scale(1.03); }
    }
    @keyframes shimmerGlow2 {
        0%, 100% { opacity: 0.5; transform: translate(0, 0) scale(1); }
        33% { opacity: 1; transform: translate(-3%, -2%) scale(1.05); }
        66% { opacity: 0.4; transform: translate(2%, 3%) scale(0.95); }
    }
    @keyframes shimmerGlow3 {
        0%, 100% { opacity: 0.3; transform: translate(0, 0) scale(1); }
        50% { opacity: 0.7; transform: translate(-2%, 2%) scale(1.08); }
    }

    /* ========================================
       侧边栏 — 桌面端 (>=769px) 永久展开
       ======================================== */
    @media (min-width: 769px) {
        section[data-testid="stSidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 280px !important;
            min-width: 280px !important;
            max-width: 280px !important;
            flex-shrink: 0 !important;
            transform: none !important;
            position: relative !important;
            left: 0 !important;
            background: rgba(255,255,255,0.78) !important;
            backdrop-filter: blur(24px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
            border-right: 1px solid rgba(37,99,235,0.07) !important;
            box-shadow: 2px 0 24px rgba(0,0,0,0.03) !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            display: flex !important;
            visibility: visible !important;
            width: 280px !important;
            min-width: 280px !important;
            transform: none !important;
        }
        button[data-testid="collapsedControl"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            pointer-events: none !important;
            position: absolute !important;
            z-index: -9999 !important;
        }
    }

    /* 主内容区 */

    /* 侧边栏内所有按钮 */
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 13px !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        color: var(--slate-600) !important;
        font-size: 0.87rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.85rem !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(37,99,235,0.05) !important;
        color: var(--blue-600) !important;
        border-color: rgba(37,99,235,0.12) !important;
        transform: translateX(2px);
    }
    /* 侧边栏主要按钮（新建对话） */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: var(--gradient-blue) !important;
        border: none !important;
        color: #fff !important;
        font-weight: 600 !important;
        justify-content: center !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.28) !important;
        text-align: center !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(37,99,235,0.38) !important;
    }
    /* 活跃导航项 */
    .nav-active {
        background: rgba(37,99,235,0.07) !important;
        color: var(--blue-600) !important;
        font-weight: 600 !important;
        border-color: rgba(37,99,235,0.15) !important;
    }

    /* 侧边栏 expander */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        border-radius: 11px !important;
        font-size: 0.83rem !important;
        font-weight: 500 !important;
        color: var(--slate-500) !important;
        background: transparent !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(37,99,235,0.03) !important;
        color: var(--slate-700) !important;
    }

    /* 侧边栏对话列表 — 单行卡片 */
    .conv-card .stButton > button {
        border-radius: 10px 0 0 10px !important;
        background: transparent !important;
        border: none !important;
        color: var(--slate-600) !important;
        font-size: 0.79rem !important;
        font-weight: 400 !important;
        padding: 0.4rem 0.5rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        height: 34px !important;
        min-height: 34px !important;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .conv-card .stButton > button:hover {
        background: rgba(37,99,235,0.05) !important;
        color: var(--blue-600) !important;
    }
    /* 删除按钮 */
    .conv-card .stButton:last-child > button {
        border-radius: 0 10px 10px 0 !important;
        width: 32px !important; min-width: 32px !important; height: 34px !important;
        min-height: 34px !important;
        font-size: 0.8rem !important; color: var(--slate-400) !important;
        padding: 0 !important; justify-content: center !important;
        background: transparent !important; border: none !important;
    }
    .conv-card .stButton:last-child > button:hover {
        color: #ef4444 !important;
        background: rgba(239,68,68,0.08) !important;
    }

    /* ========================================
       聊天气泡 — 玻璃拟态
       ======================================== */
    .user-bubble {
        display: flex; justify-content: flex-end;
        margin: 0.6rem 0;
        animation: fadeSlideIn 0.35s ease-out;
    }
    .user-bubble .content {
        max-width: 70%;
        background: var(--gradient-blue);
        color: #fff;
        padding: 12px 18px;
        border-radius: 20px 20px 6px 20px;
        font-size: 0.925rem; line-height: 1.55;
        box-shadow: 0 4px 16px rgba(37,99,235,0.22);
    }
    .ai-bubble {
        display: flex; justify-content: flex-start;
        margin: 0.6rem 0;
        animation: fadeSlideIn 0.35s ease-out;
    }
    .ai-bubble .content {
        max-width: 85%;
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(37,99,235,0.07);
        padding: 1rem 1.4rem;
        border-radius: 8px 20px 20px 20px;
        font-size: 0.925rem; line-height: 1.65;
        box-shadow: var(--shadow-xs);
    }
    .ai-bubble .content h1, .ai-bubble .content h2, .ai-bubble .content h3 {
        color: var(--blue-600); margin-top: 1rem; margin-bottom: 0.5rem;
    }
    .ai-bubble .content h2 {
        font-size: 1.2rem;
        border-bottom: 2px solid rgba(37,99,235,0.12);
        padding-bottom: 0.3rem;
    }
    .ai-bubble .content ul, .ai-bubble .content ol { padding-left: 1.5rem; }
    .ai-bubble .content li { margin: 0.3rem 0; }
    .ai-bubble .content strong { color: var(--blue-700); }
    .ai-bubble .content code {
        background: var(--blue-50); color: var(--blue-700);
        padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.85em;
    }
    .ai-bubble .content blockquote {
        border-left: 3px solid var(--blue-400);
        padding-left: 1rem; margin-left: 0; color: var(--slate-600);
    }
    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ========================================
       参考 lovable 的 staggered entrance
       ======================================== */
    @keyframes cardEnter {
        0% { opacity: 0; transform: translateY(16px) scale(0.98); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes floatSlow {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    @keyframes shimmerGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 8px rgba(37,99,235,0.15), 0 4px 16px rgba(37,99,235,0.2); }
        50% { box-shadow: 0 0 20px rgba(37,99,235,0.35), 0 8px 32px rgba(37,99,235,0.4); }
    }
    @keyframes borderShimmer {
        0% { border-color: rgba(37,99,235,0.08); }
        50% { border-color: rgba(37,99,235,0.3); }
        100% { border-color: rgba(37,99,235,0.08); }
    }
    @keyframes dotFloat {
        0%, 100% { background-position: 0 0; }
        50% { background-position: 4px 4px; }
    }
    @keyframes scaleIn {
        0% { transform: scale(0); opacity: 0; }
        80% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* 应用动画 */
    .dash-card {
        animation: cardEnter 0.5s ease-out both;
    }
    .dash-card:nth-child(1) { animation-delay: 0.05s; }
    .dash-card:nth-child(2) { animation-delay: 0.1s; }
    .dash-card:nth-child(3) { animation-delay: 0.15s; }
    .dash-card:nth-child(4) { animation-delay: 0.2s; }

    .featured-card {
        animation: cardEnter 0.5s ease-out both;
        animation-delay: 0.25s;
    }

    /* 按钮 hover 发光 */
    .stButton > button[kind="primary"]:hover {
        animation: glowPulse 2s ease-in-out infinite !important;
    }

    /* 大卡片 hover 浮起 */
    .hero-input-card:hover {
        animation: floatSlow 3s ease-in-out infinite;
    }

    /* 渐变文字闪烁 */
    h1 span[style*="gradient"] {
        background-size: 200% 200% !important;
        animation: shimmerGradient 4s ease-in-out infinite;
    }

    /* 点阵背景微动 */
    .main::before {
        animation: dotFloat 20s linear infinite;
    }

    /* 侧边栏活跃项左侧指示条 */
    .stButton > button[kind="primary"]::before {
        content: '';
        position: absolute; left: 0; top: 50%; transform: translateY(-50%);
        width: 3px; height: 20px; border-radius: 0 3px 3px 0;
        background: linear-gradient(180deg,#2563eb,#6366f1,#06b6d4);
        animation: scaleIn 0.3s ease-out;
    }

    /* 连胜火焰增强 */
    .streak-flame {
        animation: flamePulse 1.6s ease-in-out infinite;
        filter: drop-shadow(0 4px 20px rgba(251,146,60,0.5));
    }
    @keyframes flamePulse {
        0%, 100% { transform: scale(1) rotate(-2deg); filter: hue-rotate(0deg) drop-shadow(0 4px 20px rgba(251,146,60,0.5)); }
        33% { transform: scale(1.1) rotate(2deg); filter: hue-rotate(10deg) drop-shadow(0 8px 30px rgba(251,146,60,0.7)); }
        66% { transform: scale(0.95) rotate(-1deg); filter: hue-rotate(-5deg) drop-shadow(0 4px 16px rgba(251,146,60,0.4)); }
    }

    /* ========================================
       聊天输入框
       ======================================== */
    [data-testid="stChatInput"] textarea {
        border-radius: 18px !important;
        border: 1px solid rgba(37,99,235,0.13) !important;
        padding: 0.7rem 1.2rem !important;
        font-size: 0.925rem !important;
        background: rgba(255,255,255,0.8) !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--blue-500) !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.10) !important;
        background: rgba(255,255,255,0.95) !important;
    }

    /* ========================================
       首页仪表盘组件
       ======================================== */
    /* 大输入框卡片 */
    .hero-input-card {
        background: rgba(255,255,255,0.78);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(37,99,235,0.08);
        border-radius: 24px;
        padding: 1rem;
        box-shadow: var(--shadow-md);
        transition: box-shadow 0.3s ease;
    }
    .hero-input-card:focus-within {
        box-shadow: var(--shadow-glow);
    }

    /* 仪表盘卡片 */
    .dash-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(37,99,235,0.06);
        border-radius: 20px;
        padding: 1.3rem 1.2rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.25s ease;
        height: 100%;
    }
    .dash-card:hover {
        box-shadow: var(--shadow-md);
        border-color: rgba(37,99,235,0.14);
        transform: translateY(-1px);
    }
    .dash-card .card-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--slate-400);
        margin-bottom: 0.3rem;
    }
    .dash-card .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--slate-800);
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .dash-card .card-value.gradient {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .dash-card .card-sub {
        font-size: 0.75rem;
        color: var(--slate-500);
        margin-top: 0.2rem;
    }

    /* 任务进度条（首页） */
    .task-item {
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.55rem 0.8rem;
        border-radius: 12px;
        background: rgba(37,99,235,0.025);
        margin: 0.35rem 0;
        font-size: 0.85rem;
    }
    .task-bar-bg {
        flex: 1; height: 6px;
        background: rgba(37,99,235,0.08);
        border-radius: 10px; overflow: hidden;
    }
    .task-bar-fill {
        height: 100%; border-radius: 10px;
        background: var(--gradient-primary);
        transition: width 0.8s ease;
    }

    /* 精选卡片 */
    .featured-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(37,99,235,0.06);
        border-radius: 20px;
        padding: 1.2rem;
        cursor: pointer;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .featured-card::before {
        content: '';
        position: absolute; top: -40px; right: -40px;
        width: 100px; height: 100px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(37,99,235,0.08) 0%, transparent 70%);
        transition: opacity 0.3s ease; opacity: 0.5;
    }
    .featured-card:hover {
        box-shadow: var(--shadow-lg);
        border-color: rgba(37,99,235,0.2);
    }
    .featured-card:hover::before { opacity: 1; }
    .featured-card .feat-icon {
        width: 40px; height: 40px;
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-size: 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: var(--shadow-sm);
    }
    .featured-card .feat-tag {
        font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.08em;
        color: var(--slate-400); margin-bottom: 0.3rem;
    }
    .featured-card .feat-title {
        font-size: 1rem; font-weight: 600;
        color: var(--slate-800); margin-bottom: 0.3rem;
    }
    .featured-card .feat-desc {
        font-size: 0.78rem; color: var(--slate-500);
        line-height: 1.5; margin-bottom: 0.8rem;
    }
    .featured-card .feat-link {
        font-size: 0.8rem; font-weight: 600;
        color: var(--blue-600);
        display: flex; align-items: center; gap: 0.25rem;
    }

    /* 连胜火焰 */
    /* .streak-flame 样式已在下方动画区定义 */

    /* ========================================
       Source / 错题 / 考试 / 统计（保留）
       ======================================== */
    .source-tag {
        display: inline-block; font-size: 0.75rem;
        background: var(--blue-50); color: var(--blue-600);
        padding: 0.2rem 0.6rem; border-radius: 10px;
        margin: 0.15rem; border: 1px solid rgba(37,99,235,0.1);
    }
    .wrong-item {
        background: rgba(255,255,255,0.7); backdrop-filter: blur(8px);
        border-left: 3px solid #ef4444;
        padding: 0.7rem 0.9rem; border-radius: 8px;
        margin: 0.5rem 0; font-size: 0.82rem; box-shadow: var(--shadow-xs);
    }
    .wrong-item .q { font-weight: 600; color: var(--slate-800); }
    .wrong-item .a { color: var(--slate-500); margin-top: 0.2rem; }
    .exam-timer {
        font-size: 2.5rem; font-weight: 700; text-align: center;
        color: var(--blue-600); padding: 0.5rem;
        font-variant-numeric: tabular-nums;
        background: rgba(255,255,255,0.7); border-radius: 16px;
        box-shadow: var(--shadow-sm);
    }
    .exam-timer.warning { color: #ef4444; animation: pulse 1s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
    .exam-question {
        background: rgba(255,255,255,0.8); backdrop-filter: blur(8px);
        border: 1px solid rgba(37,99,235,0.08); border-radius: 16px;
        padding: 1.4rem; margin: 0.8rem 0; box-shadow: var(--shadow-xs);
    }
    .exam-question .q-num { font-weight: 700; color: var(--blue-600); font-size: 1rem; }
    .exam-question .q-text { font-size: 0.95rem; color: var(--slate-700); line-height: 1.5; }
    .score-card {
        background: var(--gradient-primary);
        color: #fff; border-radius: 20px;
        padding: 2.5rem 2rem; text-align: center; margin: 1rem 0;
        box-shadow: var(--shadow-glow);
    }
    .score-card .score { font-size: 5rem; font-weight: 800; letter-spacing: -0.02em; }
    .score-card .label { font-size: 1.05rem; opacity: 0.9; }
    .stat-card {
        background: rgba(255,255,255,0.75); backdrop-filter: blur(10px);
        border: 1px solid rgba(37,99,235,0.06); border-radius: 14px;
        padding: 0.9rem 0.6rem; text-align: center; margin: 0.3rem 0;
        box-shadow: var(--shadow-xs);
    }
    .stat-card .num { font-size: 1.8rem; font-weight: 700; color: var(--blue-600); }
    .stat-card .lbl { font-size: 0.75rem; color: var(--slate-400); margin-top: 0.15rem; }
    .weak-tag {
        display: inline-block; background: #fef2f2; color: #dc2626;
        padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.8rem; margin: 0.2rem;
    }
    .strong-tag {
        display: inline-block; background: #f0fdf4; color: #16a34a;
        padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.8rem; margin: 0.2rem;
    }

    /* ========================================
       其他全局元素
       ======================================== */
    hr, [data-testid="stDivider"] {
        border-color: rgba(37,99,235,0.05) !important;
        margin: 0.6rem 0 !important;
    }
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(255,255,255,0.5) !important;
        border: 1px solid rgba(37,99,235,0.06) !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(37,99,235,0.04) !important;
    }
    [data-testid="stAlert"] {
        border-radius: 14px !important; border: none !important;
        backdrop-filter: blur(8px) !important;
    }
    [data-testid="stAlert"][kind="warning"] {
        background: rgba(251,191,36,0.06) !important;
        border-left: 3px solid #f59e0b !important;
    }
    [data-testid="stAlert"][kind="success"] {
        background: rgba(34,197,94,0.05) !important;
        border-left: 3px solid #22c55e !important;
    }
    [data-testid="stAlert"][kind="info"] {
        background: rgba(37,99,235,0.04) !important;
        border-left: 3px solid var(--blue-500) !important;
    }
    .stButton > button[kind="primary"] {
        border-radius: 14px !important;
        background: var(--gradient-blue) !important;
        border: none !important; color: #fff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.28) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(37,99,235,0.38) !important;
    }
    .stButton > button[kind="secondary"] {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.7) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid var(--slate-200) !important;
        color: var(--slate-600) !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(37,99,235,0.04) !important;
        border-color: rgba(37,99,235,0.25) !important;
        color: var(--blue-600) !important;
        transform: translateY(-1px) !important;
    }

    @media (max-width: 768px) {
        /* 移动端：Streamlit 原生侧边栏（默认隐藏，汉堡打开） */
        /* 底部导航栏样式在 render_mobile_nav() 中内联定义 */
        /* ========================================
           基础重置
           ======================================== */
        *, *::before, *::after { box-sizing: border-box !important; }
        body {
            font-size: 15px !important;
            -webkit-tap-highlight-color: transparent !important;
            -webkit-text-size-adjust: 100% !important;
        }

        /* 禁用桌面大背景光斑（省性能） */
        .stApp::before, .stApp::after { opacity: 0.25 !important; }

        /* ========================================
           侧边栏 — 移动端：Streamlit 原生行为 + 样式增强
           ======================================== */
        button[data-testid="collapsedControl"] {
            width: 40px !important; height: 40px !important;
            min-width: 40px !important; min-height: 40px !important;
            border-radius: 12px !important;
            background: rgba(255,255,255,0.85) !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
        }

        /* ========================================
           容器适配
           ======================================== */
        .main, section[data-testid="stMain"] { padding: 0.4rem !important; }
        [data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
        [data-testid="column"] { width: 100% !important; flex: 1 0 100% !important; max-width: 100% !important; }

        /* ========================================
           图片与媒体
           ======================================== */
        img, video, iframe, svg { max-width: 100% !important; height: auto !important; }
        iframe { max-height: 600px !important; }

        /* ========================================
           字体适配
           ======================================== */
        html { font-size: 15px !important; }
        h1 { font-size: 1.5rem !important; line-height: 1.25 !important; margin: 0.3rem 0 !important; }
        h2 { font-size: 1.2rem !important; line-height: 1.3 !important; }
        h3 { font-size: 1rem !important; }
        p, li, td, th { font-size: 0.9rem !important; }

        /* ========================================
           触摸优化 — 最小 44x44 可点击区域
           ======================================== */
        .stButton > button, button {
            min-height: 44px !important; min-width: 44px !important;
            font-size: 0.88rem !important; padding: 0.55rem 0.9rem !important;
            touch-action: manipulation !important;
        }
        a, [role="button"] { min-height: 44px; display: inline-flex; align-items: center; }

        /* ========================================
           表单适配 — 防止 iOS 自动缩放
           ======================================== */
        input, textarea, select {
            width: 100% !important; max-width: 100% !important;
            font-size: 16px !important; padding: 0.6rem 0.8rem !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 16px !important; padding: 0.6rem 0.9rem !important;
            border-radius: 14px !important; min-height: 48px !important;
        }

        /* ========================================
           表格 — 横向滚动
           ======================================== */
        table, [data-testid="stTable"] {
            display: block !important; overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important; max-width: 100% !important;
        }
        th, td { white-space: nowrap; font-size: 0.8rem !important; padding: 0.4rem 0.5rem !important; }

        /* ========================================
           多列布局 → 单列堆叠
           ======================================== */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important; width: 100% !important; max-width: 100% !important;
        }

        /* ========================================
           长内容处理
           ======================================== */
        pre, code { overflow-x: auto !important; white-space: pre-wrap !important; word-break: break-all !important; font-size: 0.78rem !important; }
        a { word-break: break-all !important; }

        /* ========================================
           统计卡片
           ======================================== */
        .dash-card { padding: 0.8rem 0.7rem !important; margin: 0.2rem 0 !important; }
        .dash-card .card-value { font-size: 1.4rem !important; }
        .dash-card .card-label { font-size: 0.62rem !important; }

        /* ========================================
           聊天气泡
           ======================================== */
        .user-bubble .content {
            max-width: 88% !important; padding: 10px 15px !important;
            font-size: 0.9rem !important; border-radius: 18px 18px 4px 18px !important;
        }
        .ai-bubble .content {
            max-width: 94% !important; padding: 0.8rem 1rem !important;
            font-size: 0.9rem !important; border-radius: 6px 16px 16px 16px !important;
        }
        .ai-bubble .content h2 { font-size: 1.05rem !important; }
        .ai-bubble .content h3 { font-size: 0.95rem !important; }
        .ai-bubble .content table { font-size: 0.75rem !important; }
        .ai-bubble .content th, .ai-bubble .content td { padding: 0.3rem 0.4rem !important; }

        /* ========================================
           功能标签页
           ======================================== */
        [data-testid="stTabs"] button { font-size: 0.82rem !important; padding: 0.4rem 0.6rem !important; }

        /* ========================================
           考试页面 iframe（知识清单/测试）
           ======================================== */
        iframe[title="components.html"], .stIFrame {
            height: 700px !important; max-height: 80vh !important; width: 100% !important;
        }

        /* ========================================
           分数卡片
           ======================================== */
        .score-card { padding: 1.5rem 1rem !important; }
        .score-card .score { font-size: 3rem !important; }
        .score-card .label { font-size: 0.9rem !important; }

        /* ========================================
           考试题目卡片
           ======================================== */
        .exam-question { padding: 1rem !important; margin: 0.5rem 0 !important; }
        .exam-question .q-text { font-size: 0.88rem !important; }

        /* ========================================
           横幅
           ======================================== */
        [style*="margin-bottom:1rem;padding:0.7rem 1rem"] {
            padding: 0.5rem 0.7rem !important; gap: 0.5rem !important;
        }

        /* ========================================
           错题卡片
           ======================================== */
        .wrong-item { padding: 0.5rem 0.7rem !important; font-size: 0.8rem !important; }

        /* ========================================
           Expander 折叠面板
           ======================================== */
        .streamlit-expanderHeader { font-size: 0.82rem !important; padding: 0.5rem 0.7rem !important; }

        /* ========================================
           Alert 提示框
           ======================================== */
        [data-testid="stAlert"] { padding: 0.6rem 0.8rem !important; font-size: 0.85rem !important; }

        /* ========================================
           Metric 指标
           ======================================== */
        [data-testid="stMetric"] { padding: 0.6rem !important; }
        [data-testid="stMetric"] label { font-size: 0.75rem !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.5rem !important; }

        /* ========================================
           计时器
           ======================================== */
        .exam-timer { font-size: 1.8rem !important; }

        /* ========================================
           streamlit 列间距归零
           ======================================== */
        [data-testid="stHorizontalBlock"] { gap: 0.3rem !important; }

        /* ========================================
           知识库状态栏
           ======================================== */
        [style*="display:flex;align-items:center;justify-content:center;gap:2rem"] {
            flex-direction: column !important; gap: 0.3rem !important; text-align: center !important;
        }
    }
</style>

<script>
(function() {
    // =====================================================
    // 侧边栏 — 桌面端默认展开，支持折叠（带过渡动画）
    // Streamlit 原生管理折叠状态，CSS transition 提供动画
    // =====================================================

    // =====================================================
    // 侧边栏守卫 — 桌面端保持展开
    // =====================================================
    (function() {
        function getDoc() { try { return window.parent.document; } catch(e) { return document; } }
        function forceSidebar() {
            if (window.innerWidth < 769) return;
            var doc = getDoc();
            var sb = doc.querySelector('section[data-testid="stSidebar"]');
            if (sb) {
                sb.style.setProperty('display', 'flex', 'important');
                sb.style.setProperty('visibility', 'visible', 'important');
                sb.style.setProperty('width', '280px', 'important');
                sb.style.setProperty('min-width', '280px', 'important');
                sb.style.setProperty('max-width', '280px', 'important');
                sb.style.setProperty('transform', 'none', 'important');
                sb.setAttribute('aria-expanded', 'true');
            }
            var btn = doc.querySelector('button[data-testid="collapsedControl"]');
            if (btn) btn.style.setProperty('display', 'none', 'important');
        }
        forceSidebar();
        setInterval(forceSidebar, 500);
    })();

    // =====================================================
    // 自动滚到底部
    // =====================================================
    function scrollToBottom() {
        var el = window.parent.document.querySelector('section.main');
        if(el) el.scrollTop = el.scrollHeight;
    }
    scrollToBottom();
    var scrollObserver = new MutationObserver(scrollToBottom);
    var mainTarget = window.parent.document.querySelector('section.main');
    if(mainTarget) scrollObserver.observe(mainTarget, { childList: true, subtree: true, characterData: true });

    // =====================================================
    // 考试倒计时
    // =====================================================
    var examEndTime = document.getElementById('exam-end-time');
    if(examEndTime) {
        var endMs = parseInt(examEndTime.textContent);
        var display = document.getElementById('exam-timer-display');
        var submitBtn = window.parent.document.querySelector('button[kind="examSubmit"]');
        function tick() {
            var now = Date.now();
            var remaining = Math.max(0, Math.floor((endMs - now) / 1000));
            var m = Math.floor(remaining / 60);
            var s = remaining % 60;
            if(display) {
                display.textContent = m + ':' + (s < 10 ? '0' : '') + s;
                if(remaining < 300) display.classList.add('warning');
            }
            if(remaining <= 0 && submitBtn) { submitBtn.click(); return; }
            if(remaining > 0) setTimeout(tick, 1000);
        }
        tick();
    }
})();
</script>
""", unsafe_allow_html=True)

# ============================================================
# 会话状态初始化
# ============================================================
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = bool(
        DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "your-api-key-here"
    )
if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None
if "current_feature" not in st.session_state:
    st.session_state.current_feature = "🏠 首页"
if "pending_stream" not in st.session_state:
    st.session_state.pending_stream = False
if "wrong_answer_book" not in st.session_state:
    st.session_state.wrong_answer_book = load_wrong_answer_book()
if "exam_state" not in st.session_state:
    st.session_state.exam_state = None
if "study_stats" not in st.session_state:
    st.session_state.study_stats = load_study_stats()

# ============================================================
# 知识库
# ============================================================
@st.cache_resource
def load_kb():
    return get_kb(str(KB_DIR))
kb = load_kb()

# ============================================================
# 工具函数
# ============================================================
def build_kb_context(query: str) -> tuple:
    kb_context, kb_sources = kb.get_context_for_query(query, top_k=5)
    if kb_context:
        enhanced = f"""

【重要：以下是来自课程教材的参考资料，请优先基于这些内容回答。如果参考资料不够，可以用你的知识补充。】

参考资料：
{kb_context}"""
    else:
        enhanced = ""
    return enhanced, kb_sources

def new_conversation(feature: str):
    conv_id = str(uuid.uuid4())[:8]
    title = f"新对话 {datetime.datetime.now().strftime('%m/%d %H:%M')}"
    st.session_state.conversations[conv_id] = {
        "title": title, "feature": feature,
        "messages": [], "created_at": datetime.datetime.now().isoformat(),
    }
    st.session_state.current_conv_id = conv_id

def get_current_messages() -> list:
    cid = st.session_state.current_conv_id
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]["messages"]
    return []

def update_conv_title(conv_id: str, first_msg: str):
    msg = first_msg.strip().replace("\n", " ")
    prefixes = [
        r"^帮我[想出做]?[一道些个]?", r"^请问[一下]?", r"^我想[问了解知道]?",
        r"^能不能", r"^可以[帮我]?", r"^麻烦[你您]?", r"^请[你您]?",
        r"^来[一道些个]?", r"^给我[出]?",
    ]
    for pat in prefixes:
        msg = re.sub(pat, "", msg).strip()
    msg = re.sub(r"[？?。！!]+$", "", msg).strip()
    book_match = re.findall(r"《([^》]+)》", msg)
    if book_match:
        key = "、".join(book_match[:3])
    else:
        key = msg
    if len(key) > 18:
        cut = key[:18]
        for sep in ["，", "。", "、", " ", "；", "："]:
            idx = cut.rfind(sep)
            if idx > 8:
                cut = cut[:idx]
                break
        title = cut + "…"
    else:
        title = key
    if not title:
        title = "新对话"
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["title"] = title

# ============================================================
# 侧边栏 — 主导航（参考 lovable 设计）
# ============================================================
NAV_ITEMS = [
    {"icon": "🏠",  "label": "首页",     "key": "🏠 首页"},
    {"icon": "📖",  "label": "概念讲解", "key": "📖 概念讲解"},
    {"icon": "📝",  "label": "智能刷题", "key": "📝 智能刷题"},
    {"icon": "📅",  "label": "学习规划", "key": "📅 学习规划"},
    {"icon": "✍️",  "label": "论文辅助", "key": "✍️ 论文辅助"},
    {"icon": "🎯",  "label": "考试备考", "key": "🎯 考试备考"},
    {"icon": "⏱️",  "label": "模拟考试", "key": "⏱️ 模拟考试"},
]
EXAM_PAGE_KEYS = [
    "📋 CFA知识清单", "📝 CFA章节测试",
    "📋 FRM知识清单", "📝 FRM章节测试",
    "📋 CPA知识清单", "📝 CPA章节测试",
    "📋 ACCA知识清单", "📝 ACCA章节测试",
]

def navigate_to(feature_key: str):
    """切换页面"""
    st.session_state.current_feature = feature_key
    st.session_state.exam_state = None
    # 如果切到对话类功能且当前没有该功能的对话，创建新的
    conv_features = ["📖 概念讲解", "📝 智能刷题", "📅 学习规划", "✍️ 论文辅助"]
    if feature_key in conv_features:
        cid = st.session_state.current_conv_id
        if cid and cid in st.session_state.conversations:
            if st.session_state.conversations[cid]["feature"] != feature_key:
                found = False
                for fc_id, fc_data in sorted(
                    st.session_state.conversations.items(),
                    key=lambda x: x[1].get("created_at", ""), reverse=True
                ):
                    if fc_data["feature"] == feature_key:
                        st.session_state.current_conv_id = fc_id
                        found = True
                        break
                if not found:
                    new_conversation(feature_key)
        else:
            new_conversation(feature_key)

def render_sidebar():
    with st.sidebar:
        # ---- Logo ----
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 4px 16px 4px;">
            <div style="width:40px;height:40px;border-radius:15px;
                background:linear-gradient(135deg,#2563eb,#6366f1,#06b6d4);
                display:flex;align-items:center;justify-content:center;
                font-size:1.4rem;box-shadow:0 6px 20px rgba(37,99,235,0.38);">
                🎓
            </div>
            <div style="line-height:1.2;">
                <div style="font-weight:700;font-size:1rem;color:#1e293b;letter-spacing:-0.01em;">
                EconSavvy</div>
                <div style="font-size:0.65rem;color:#94a3b8;">
                经世智用 · AI Finance Tutor</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- 新建对话 ----
        st.button(
            "＋ 开始新对话", use_container_width=True,
            type="primary",
            on_click=new_conversation,
            args=(st.session_state.current_feature,)
        )

        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

        # ---- 主导航 ----
        for item in NAV_ITEMS:
            is_active = st.session_state.current_feature == item["key"]
            label = f"{item['icon']}  {item['label']}"
            if st.button(
                label, key=f"nav_{item['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                navigate_to(item["key"])
                st.rerun()

        # 知识图谱按钮
        is_kg_active = st.session_state.current_feature == "🕸️ 知识图谱"
        if st.button(
            "🕸️  知识图谱", key="nav_knowledge_graph",
            use_container_width=True,
            type="primary" if is_kg_active else "secondary",
        ):
            st.session_state.current_feature = "🕸️ 知识图谱"
            st.rerun()

        st.divider()

        # ---- 错题复习快捷入口 ----
        wrong_count = len(st.session_state.wrong_answer_book)
        due_count = count_due_reviews()
        if due_count > 0:
            btn_label = f"📝 错题复习 · {wrong_count}题（{due_count}待复习）"
            btn_type = "primary"
        else:
            btn_label = f"📝 错题本（{wrong_count}题）"
            btn_type = "secondary"
        if st.button(btn_label, use_container_width=True,
                      disabled=(wrong_count == 0), type=btn_type):
            st.session_state.current_feature = "📝 智能刷题"
            wrong_qs = st.session_state.wrong_answer_book
            kp_list = list(set(w["knowledge_point"] for w in wrong_qs))
            kp_str = "、".join(kp_list[:5])
            prompt = (
                f"我之前在以下知识点上做错了{wrong_count}道题，"
                f"请针对这些薄弱知识点出{wrong_count}道练习题帮我巩固：{kp_str}"
            )
            new_conversation("📝 智能刷题")
            st.session_state.conversations[
                st.session_state.current_conv_id
            ]["messages"].append({"role": "user", "content": prompt})
            st.rerun()

        st.divider()

        # ---- 最近对话 ----
        active_convs = {
            cid: cdata for cid, cdata in st.session_state.conversations.items()
            if len(cdata.get("messages", [])) > 0
        }
        if active_convs:
            st.markdown("""
            <div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;
            letter-spacing:0.06em;color:#94a3b8;margin-bottom:0.4rem;">
            最近对话
            </div>
            """, unsafe_allow_html=True)
            sorted_convs = sorted(
                active_convs.items(),
                key=lambda x: x[1].get("created_at", ""), reverse=True
            )[:8]
            for cid, cdata in sorted_convs:
                is_current = cid == st.session_state.current_conv_id
                feat_icon = cdata.get("feature", "📖")[:2]
                title = cdata.get("title", "对话")
                if len(title) > 16:
                    title = title[:16] + "..."
                prefix = "●" if is_current else "○"
                label = f"{prefix}  {feat_icon}  {title}"

                # 单行设计：按钮主体 + 删除 × 在同一个视觉框内
                st.markdown(f"""
                <div class="conv-card" style="display:flex;align-items:center;
                background:{'rgba(37,99,235,0.06)' if is_current else 'rgba(255,255,255,0.5)'};
                backdrop-filter:blur(8px);border-radius:12px;margin:2px 0;
                border:1px solid {'rgba(37,99,235,0.18)' if is_current else 'rgba(37,99,235,0.05)'};
                transition:all 0.2s ease;">
                """, unsafe_allow_html=True)

                c1, c2 = st.columns([22, 3])
                with c1:
                    if st.button(label, key=f"conv_{cid}", use_container_width=True):
                        navigate_to(cdata["feature"])
                        st.session_state.current_conv_id = cid
                        st.rerun()
                with c2:
                    if st.button("×", key=f"del_{cid}", help="删除此对话"):
                        del st.session_state.conversations[cid]
                        if st.session_state.current_conv_id == cid:
                            st.session_state.current_conv_id = None
                        save_conversations(st.session_state.conversations)
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # ---- 底部状态卡（类似 lovable 的 streak card） ----
        stats = st.session_state.study_stats
        total_q = stats["total_questions_answered"]
        correct_q = stats["correct_count"]
        rate = f"{correct_q / total_q * 100:.0f}%" if total_q > 0 else "-"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.6);backdrop-filter:blur(12px);
        border:1px solid rgba(37,99,235,0.07);border-radius:16px;padding:0.8rem 1rem;
        margin-top:0.5rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:0.7rem;font-weight:600;color:#94a3b8;">
                    📊 学习概览</div>
                    <div style="font-size:1.5rem;font-weight:700;color:#1e293b;margin-top:0.2rem;">
                    {total_q}<span style="font-size:0.85rem;font-weight:400;color:#94a3b8;"> 题</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:2rem;font-weight:800;
                    background:linear-gradient(135deg,#2563eb,#6366f1,#06b6d4);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">{rate}</div>
                    <div style="font-size:0.65rem;color:#94a3b8;">正确率</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 系统状态折叠
        with st.expander("⚙️ 系统状态"):
            cs = get_cache().stats
            st.caption(f"💾 缓存: {cs['entries']} 条 · 命中率 {cs['hit_rate']}")
            chunk_count = len(kb.chunks) if kb else 0
            if chunk_count > 0:
                st.caption(f"📚 知识库: {chunk_count} 段")
        st.caption("EconSavvy · 经世智用 v5")

# ============================================================
# 首页仪表盘
# ============================================================
def render_homepage():
    stats = st.session_state.study_stats
    total_q = stats["total_questions_answered"]
    correct_q = stats["correct_count"]
    wrong_q = stats["wrong_count"]
    wrong_book = st.session_state.wrong_answer_book
    due_count = count_due_reviews()
    daily = stats.get("daily_activity", {})
    streak = len(daily) if daily else 0

    # ---- 欢迎区 ----
    hour = datetime.datetime.now().hour
    greeting = "清晨好" if hour < 8 else "上午好" if hour < 12 else "中午好" if hour < 14 else "下午好" if hour < 18 else "晚上好"

    # 移动端 EconSavvy 品牌标志（仅手机端可见）
    st.markdown("""<div class="mobile-brand-header" style="display:none;align-items:center;gap:10px;margin-bottom:1rem;padding-bottom:0.8rem;border-bottom:1px solid rgba(37,99,235,0.06);"><div style="width:36px;height:36px;border-radius:13px;background:linear-gradient(135deg,#2563eb,#6366f1,#06b6d4);display:flex;align-items:center;justify-content:center;font-size:1.2rem;box-shadow:0 4px 14px rgba(37,99,235,0.35);color:#fff;">ES</div><div style="line-height:1.2;"><div style="font-weight:700;font-size:1rem;color:#1e293b;letter-spacing:-0.01em;">EconSavvy</div><div style="font-size:0.65rem;color:#94a3b8;">AI Finance Tutor</div></div></div><style>@media(max-width:768px){.mobile-brand-header{display:flex!important}}</style>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;">
            <span style="background:linear-gradient(135deg,#2563eb,#6366f1);color:#fff;
            font-size:0.7rem;font-weight:600;padding:0.2rem 0.7rem;border-radius:20px;">
            AI 财经导师
            </span>
            <span style="font-size:0.75rem;color:#94a3b8;">
            随时在线，随问随答
            </span>
        </div>
        <h1 style="font-size:2.2rem;font-weight:700;color:#0f172a;margin:0;letter-spacing:-0.02em;line-height:1.2;">
            {greeting}，今天想
            <span style="background:linear-gradient(135deg,#2563eb,#6366f1,#06b6d4);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">攻克哪个知识点</span>？
        </h1>
        <p style="color:#64748b;font-size:0.9rem;margin-top:0.5rem;line-height:1.6;max-width:560px;">
            不讲表面定义。从 <strong>直觉理解</strong> → <strong>数学公式</strong> → <strong>实战案例</strong> → <strong>常见陷阱</strong> → <strong>概念对比</strong>，<br/>
            一层层剥开，直到你彻底明白为止。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- 快捷提问 chips ----
    suggestions = [
        ("📖", "杜邦分析法怎么拆解 ROE"),
        ("🧮", "戈登增长模型 GGM 的推导和应用"),
        ("📊", "帮我做一份 CFA 一级 30 天冲刺计划"),
        ("✍️", "毕业论文选题：金融科技方向"),
    ]
    cols = st.columns(4)
    for i, (icon, text) in enumerate(suggestions):
        with cols[i]:
            if st.button(f"{icon}  {text}", key=f"home_q_{i}", use_container_width=True):
                navigate_to("📖 概念讲解")
                cid = st.session_state.current_conv_id
                if cid and cid in st.session_state.conversations:
                    st.session_state.conversations[cid]["messages"].append(
                        {"role": "user", "content": text}
                    )
                st.rerun()

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    # ---- 数据看板 ----
    rate_str = f"{correct_q / total_q * 100:.0f}%" if total_q > 0 else "—"
    col_a, col_b, col_c, col_d = st.columns(4)
    cards = [
        ("总答题数", f"{total_q}", "道题目已解答", "📝"),
        ("正确率", rate_str, f"✅ {correct_q} · ❌ {wrong_q}", "🎯"),
        ("待复习", f"{due_count}", f"共 {len(wrong_book)} 道错题" if wrong_book else "暂无错题", "📌"),
        ("学习天数", f"{streak}", "累计打卡记录", "🔥"),
    ]
    for col, (label, value, sub, icon) in zip([col_a, col_b, col_c, col_d], cards):
        with col:
            st.markdown(f"""
            <div class="dash-card" style="text-align:left;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div class="card-label">{label}</div>
                    <div style="font-size:1.3rem;">{icon}</div>
                </div>
                <div class="card-value gradient">{value}</div>
                <div class="card-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    # ---- 学习路径 + 考试入口 ----
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
        <div style="font-size:0.85rem;font-weight:600;color:#334155;margin-bottom:0.6rem;">
        你今天可以做什么
        </div>
        """, unsafe_allow_html=True)

        actions = [
            ("📖", "概念讲解", "选一个财经概念，AI 从直觉讲到对比表，结构化讲透", "📖 概念讲解"),
            ("📝", "智能刷题", "自动出题 + 实时批改 + 错题收录，查漏补缺", "📝 智能刷题"),
            ("📚", "考试备考", "CFA / FRM / CPA / ACCA 知识清单与章节测试", "🎯 考试备考"),
        ]
        for icon, title, desc, target in actions:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.7);backdrop-filter:blur(10px);
            border:1px solid rgba(37,99,235,0.06);border-radius:16px;
            padding:1rem 1.2rem;margin:0.5rem 0;
            display:flex;align-items:center;gap:1rem;
            transition:all 0.2s ease;cursor:pointer;"
            onmouseover="this.style.boxShadow='0 8px 24px rgba(37,99,235,0.08)';this.style.borderColor='rgba(37,99,235,0.18)';"
            onmouseout="this.style.boxShadow='';this.style.borderColor='rgba(37,99,235,0.06)';">
                <div style="width:42px;height:42px;border-radius:14px;
                background:linear-gradient(135deg,#2563eb,#6366f1);
                display:flex;align-items:center;justify-content:center;
                font-size:1.3rem;flex-shrink:0;box-shadow:0 4px 14px rgba(37,99,235,0.2);">
                {icon}
                </div>
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:0.92rem;color:#1e293b;">{title}</div>
                    <div style="font-size:0.78rem;color:#94a3b8;line-height:1.4;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"进入 {title} →", key=f"home_action_{target}"):
                if target in ["📖 概念讲解", "📝 智能刷题"]:
                    navigate_to(target)
                else:
                    st.session_state.current_feature = target
                st.rerun()

    with col_right:
        st.markdown("""
        <div style="font-size:0.85rem;font-weight:600;color:#334155;margin-bottom:0.6rem;">
        考试备考
        </div>
        """, unsafe_allow_html=True)

        exams = [
            ("📋", "CFA Level I", "10 大模块 · 知识清单 + 章节测试", "🎯 考试备考"),
            ("📋", "FRM Part I & II", "风险管理 · 知识清单 + 章节测试", "🎯 考试备考"),
            ("📋", "CPA 专业阶段", "6 科知识框架 + 章节测试", "🎯 考试备考"),
            ("📋", "ACCA 全阶段", "13 门课程框架 + 章节测试", "🎯 考试备考"),
        ]
        for i, (icon, name, desc, target) in enumerate(exams):
            label = f"{icon}  {name}"
            if st.button(label, key=f"home_exam_{i}", use_container_width=True):
                st.session_state.current_feature = target
                st.rerun()
            st.caption(desc)

    # ---- 知识库统计 ----
    chunk_count = len(kb.chunks) if kb else 0
    st.markdown(f"""
    <div style="margin-top:1.2rem;padding:0.8rem 1rem;
    background:rgba(255,255,255,0.5);backdrop-filter:blur(8px);
    border:1px solid rgba(37,99,235,0.05);border-radius:14px;
    display:flex;align-items:center;justify-content:center;gap:2rem;
    font-size:0.78rem;color:#94a3b8;">
        <span>📚 知识库：<strong style="color:#475569;">{chunk_count}</strong> 个知识段落</span>
        <span>💾 AI 缓存命中率：<strong style="color:#475569;">{get_cache().stats['hit_rate']}</strong></span>
        <span>🧠 已覆盖 <strong style="color:#475569;">CFA/FRM/CPA/ACCA</strong> 四大考试大纲</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 对话区域
# ============================================================
PAGE_BANNERS = {
    "🕸️ 知识图谱": {
        "icon": "🗺️", "title": "Knowledge Graph",
        "subtitle": "— 8 门财经课程的知识点关系网络",
        "desc": "绿色=已掌握 · 橙色=需巩固 · 红色=薄弱点 · 灰色=待探索。点击科目展开章节。",
    },
    "🎯 考试备考": {
        "icon": "🏆", "title": "Exam Preparation Hub",
        "subtitle": "— 大学课程 + 证书考试，知识清单 + 章节测试一站配齐",
        "desc": "会计学、金融学、税收学等大学教材知识点，CFA / FRM / CPA / ACCA 考纲全覆盖。",
    },
    "📖 概念讲解": {
        "icon": "🎓", "title": "Concept Deep Dive",
        "subtitle": "— 从直觉到对比表，结构化讲透每一个概念",
        "desc": "不是「这是什么」，而是「为什么需要它 → 怎么理解它 → 怎么用它 → 哪里容易错」。",
    },
    "📝 智能刷题": {
        "icon": "🎯", "title": "Practice Makes Permanent",
        "subtitle": "— 做题 + 批改 + 解析 + 收录错题，一条龙",
        "desc": "AI 出题，你作答，秒出批改报告。错题自动归档，薄弱点一目了然，针对性巩固。",
    },
    "📅 学习规划": {
        "icon": "🗓️", "title": "Your Study Roadmap",
        "subtitle": "— 不是泛泛的「每天学 2 小时」，而是精确到知识点的路线图",
        "desc": "告诉 AI 你的考试、可用时间和基础，它会帮你排出优先级和每周里程碑。",
    },
    "✍️ 论文辅助": {
        "icon": "📄", "title": "Academic Writing Wingman",
        "subtitle": "— 从选题到文献综述到润色，每一步都有帮手",
        "desc": "卡在开题？不知道框架怎么搭？AI 帮你理思路、找角度、顺逻辑，但不动笔替你写。",
    },
    "📋 CFA知识清单": {
        "icon": "📋", "title": "CFA Level I · 知识速查",
        "subtitle": "— 10 大模块精华梳理，2025 最新考纲",
        "desc": "道德、定量、财报、权益、固收……每个模块的核心公式和易错陷阱都在这。",
    },
    "📝 CFA章节测试": {
        "icon": "📝", "title": "CFA Level I · 章节测验",
        "subtitle": "— 28 题 100 分，仿真难度，逐题解析",
        "desc": "做完立刻出分，每道题都有「为什么对、为什么错、哪里容易踩坑」。",
    },
    "📋 FRM知识清单": {
        "icon": "📋", "title": "FRM Part I & II · 知识速查",
        "subtitle": "— 从风险基础到前沿话题，2025 考纲全覆盖",
        "desc": "市场风险、信用风险、操作风险、流动性风险……从 VaR 到 SVB，一网打尽。",
    },
    "📝 FRM章节测试": {
        "icon": "📝", "title": "FRM · 章节测验",
        "subtitle": "— 28 题 100 分，覆盖两级核心考点",
        "desc": "做完立刻出分，逐题解析 + 干扰项分析 + 常见错误提醒。",
    },
    "📋 CPA知识清单": {
        "icon": "📋", "title": "CPA · 知识速查",
        "subtitle": "— 6 科框架一页通，2025 最新考纲",
        "desc": "会计、审计、财管、税法、经济法、战略——每科核心考点和易混概念梳理。",
    },
    "📝 CPA章节测试": {
        "icon": "📝", "title": "CPA · 章节测验",
        "subtitle": "— 28 题 100 分，覆盖六科核心知识点",
        "desc": "做完立刻出分，逐题解析 + 常见陷阱提示。",
    },
    "📋 ACCA知识清单": {
        "icon": "📋", "title": "ACCA · 知识速查",
        "subtitle": "— 13 门课程框架，从 Applied Knowledge 到 Strategic Professional",
        "desc": "BT/MA/FA → LW/PM/TX/FR/AA/FM → SBL/SBR + 选修。IFRS 核心准则速查。",
    },
    "📝 ACCA章节测试": {
        "icon": "📝", "title": "ACCA · 章节测验",
        "subtitle": "— 28 题 100 分，覆盖核心科目关键概念",
        "desc": "做完立刻出分，逐题解析 + 易错点提醒。",
    },
}

def get_page_banner(feature_key: str) -> str:
    """为每个页面生成独特的横幅"""
    info = PAGE_BANNERS.get(feature_key)
    if not info:
        # 默认横幅
        info = {
            "icon": "🎓", "title": "Concept Deep Dive",
            "subtitle": "— 把任何财经概念，讲到你彻底懂",
            "desc": "不仅给定义。AI 会从直觉 → 公式 → 案例 → 易错点 → 对比表，结构化地讲透。",
        }
    return f"""
    <div style="margin-bottom:1rem;padding:0.7rem 1rem;
    background:rgba(255,255,255,0.6);backdrop-filter:blur(8px);
    border:1px solid rgba(37,99,235,0.07);border-radius:14px;
    display:flex;align-items:center;gap:0.8rem;">
        <div style="width:36px;height:36px;border-radius:12px;
        background:linear-gradient(135deg,#2563eb,#6366f1);
        display:flex;align-items:center;justify-content:center;
        font-size:1rem;flex-shrink:0;box-shadow:0 4px 12px rgba(37,99,235,0.25);">
        {info['icon']}
        </div>
        <div style="flex:1;min-width:0;">
            <div style="font-weight:600;font-size:0.85rem;color:#1e293b;">
            {info['title']}
            <span style="font-weight:400;color:#64748b;font-size:0.8rem;">
            {info['subtitle']}
            </span>
            </div>
            <div style="font-size:0.72rem;color:#94a3b8;line-height:1.4;">
            {info['desc']}
            </div>
        </div>
    </div>
    """

def render_conversation():
    current_feature = st.session_state.current_feature

    if not st.session_state.current_conv_id:
        new_conversation(current_feature)

    messages = get_current_messages()

    # 每个功能页各自的横幅
    st.markdown(get_page_banner(current_feature), unsafe_allow_html=True)

    # 历史消息
    for msg in messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-bubble"><div class="content">{msg["content"]}</div></div>',
                unsafe_allow_html=True
            )
        else:
            display_content = strip_answers_comment(msg.get("content", ""))
            st.markdown(
                f'<div class="ai-bubble"><div class="content">{display_content}</div></div>',
                unsafe_allow_html=True
            )

    # 聊天输入
    prompt = st.chat_input(f"在「{current_feature}」中输入你的问题…", key="main_chat_input")

    if prompt:
        conv_id = st.session_state.current_conv_id
        conv = st.session_state.conversations[conv_id]
        is_first_user_msg = (
            len([m for m in conv["messages"] if m["role"] == "user"]) == 0
        )

        kb_context, kb_sources = build_kb_context(prompt)
        enhanced_prompt = prompt + kb_context

        conv["messages"].append({"role": "user", "content": prompt})
        if is_first_user_msg:
            update_conv_title(conv_id, prompt)

        st.markdown(
            f'<div class="user-bubble"><div class="content">{prompt}</div></div>',
            unsafe_allow_html=True
        )

        # 调用 AI
        system_prompt = SYSTEM_PROMPTS[current_feature]
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(conv["messages"])

        placeholder = st.empty()
        full_response = ""
        for token in stream_ai(api_messages, feature=current_feature):
            full_response += token
            placeholder.markdown(
                f'<div class="ai-bubble"><div class="content">{full_response}▌</div></div>',
                unsafe_allow_html=True
            )

        display_response = strip_answers_comment(full_response)
        placeholder.markdown(
            f'<div class="ai-bubble"><div class="content">{display_response}</div></div>',
            unsafe_allow_html=True
        )

        # 智能刷题自动批改
        if current_feature == "📝 智能刷题":
            hidden_answers = extract_hidden_answers(full_response)
            user_answers = parse_user_answers(prompt)
            if (
                hidden_answers
                and user_answers
                and len(user_answers) >= len(hidden_answers) * 0.5
            ):
                questions_text = ""
                for m in conv["messages"]:
                    content = m.get("content", "")
                    if m["role"] == "assistant" and "第" in content and "题" in content:
                        questions_text = content
                        break
                if not questions_text:
                    questions_text = full_response

                ai_prompt, grading_report = grade_answers_and_build_prompt(
                    hidden_answers, user_answers, questions_text, prompt, conv_id
                )
                st.markdown("---")
                st.markdown(grading_report)

                api_messages2 = [
                    {"role": "system", "content": SYSTEM_PROMPTS["📝 智能刷题"]},
                    {"role": "user", "content": ai_prompt},
                ]
                placeholder2 = st.empty()
                full_analysis = ""
                for token in stream_ai(api_messages2, feature="📝 智能刷题"):
                    full_analysis += token
                    placeholder2.markdown(
                        f'<div class="ai-bubble"><div class="content">{full_analysis}▌</div></div>',
                        unsafe_allow_html=True
                    )
                final_analysis = strip_answers_comment(full_analysis)
                placeholder2.markdown(
                    f'<div class="ai-bubble"><div class="content">{final_analysis}</div></div>',
                    unsafe_allow_html=True
                )
                conv["messages"].append({
                    "role": "assistant",
                    "content": grading_report + "\n\n---\n\n" + final_analysis
                })
            else:
                conv["messages"].append({"role": "assistant", "content": full_response})
        else:
            conv["messages"].append({"role": "assistant", "content": full_response})

        save_wrong_answer_book(st.session_state.wrong_answer_book)
        save_study_stats(st.session_state.study_stats)
        save_conversations(st.session_state.conversations)
        get_cache().save()
        st.rerun()

# ============================================================
# 考试备考 Hub 页面
# ============================================================
def render_exam_hub():
    """考试备考中心：大学科目 + CFA/FRM/CPA/ACCA 知识清单与章节测试"""
    st.markdown(get_page_banner("🎯 考试备考"), unsafe_allow_html=True)

    # ── 大学课程科目 ──
    st.markdown("### 📖 大学课程科目")
    subjects = []
    if os.path.isdir(str(KB_DIR)):
        for name in sorted(os.listdir(str(KB_DIR))):
            subj_path = os.path.join(str(KB_DIR), name)
            if os.path.isdir(subj_path) and not name.startswith(('.', '_')):
                # Count txt/html files
                txt_count = len([f for f in os.listdir(subj_path) if f.endswith('.txt')])
                html_count = len([f for f in os.listdir(subj_path) if f.endswith('.html')])
                if txt_count > 0 or html_count > 0:
                    subjects.append({"name": name, "txt": txt_count, "html": html_count})

    if subjects:
        cols = st.columns(min(len(subjects), 4))
        for i, subj in enumerate(subjects):
            with cols[i % 4]:
                txt_label = f"{subj['txt']} 段教材" if subj['txt'] else ""
                html_label = f"{subj['html']} 个资料" if subj['html'] else ""
                label_parts = [p for p in [txt_label, html_label] if p]
                st.markdown(f"""
                <div class="dash-card" style="text-align:center;margin-bottom:0.4rem;">
                    <div style="font-size:2rem;margin-bottom:0.3rem;">📚</div>
                    <div style="font-weight:600;font-size:0.9rem;color:#1e293b;">{subj['name']}</div>
                    <div class="card-sub">{' · '.join(label_parts) if label_parts else '教材资料'}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("知识库中暂无大学课程教材。将 TXT 文件放入知识库文件夹即可自动识别。（PDF/Word 解析即将上线）")

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    # ── 证书考试 ──
    st.markdown("### 🏆 证书考试备考")
    st.caption("点击进入各考试的知识清单或章节测试")

    exam_sections = [
        ("CFA", "特许金融分析师", [
            ("📋 CFA 知识清单", "10 大模块知识点速查", "📋 CFA知识清单"),
            ("📝 CFA 章节测试", "28 题 100 分 · 仿真难度", "📝 CFA章节测试"),
        ]),
        ("FRM", "金融风险管理师", [
            ("📋 FRM 知识清单", "Part I & II 核心考点", "📋 FRM知识清单"),
            ("📝 FRM 章节测试", "28 题 100 分 · 覆盖两级", "📝 FRM章节测试"),
        ]),
        ("CPA", "注册会计师", [
            ("📋 CPA 知识清单", "6 科知识框架速查", "📋 CPA知识清单"),
            ("📝 CPA 章节测试", "28 题 100 分 · 六科覆盖", "📝 CPA章节测试"),
        ]),
        ("ACCA", "特许公认会计师", [
            ("📋 ACCA 知识清单", "13 门课程框架速查", "📋 ACCA知识清单"),
            ("📝 ACCA 章节测试", "28 题 100 分 · 核心科目", "📝 ACCA章节测试"),
        ]),
    ]

    for exam_name, exam_desc, links in exam_sections:
        st.markdown(f"""
        <div style="margin-top:0.8rem;font-weight:600;font-size:0.9rem;color:#334155;">
        {exam_name} <span style="font-weight:400;color:#94a3b8;font-size:0.78rem;">— {exam_desc}</span>
        </div>
        """, unsafe_allow_html=True)
        ecols = st.columns(len(links))
        for j, (label, desc, target) in enumerate(links):
            with ecols[j]:
                if st.button(f"{label}", key=f"exam_hub_{target}", use_container_width=True):
                    st.session_state.current_feature = target
                    st.session_state.exam_state = None
                    st.rerun()
                st.caption(desc)

# ============================================================
# 考试备考页面渲染
# ============================================================
EXAMPASS_DIR = os.path.join(os.path.dirname(__file__), "exampass_output")

EXAM_META = {
    "📋 CFA知识清单":  ("CFA一级_知识清单.html", "CFA Level I · 知识清单", False),
    "📝 CFA章节测试":  ("CFA一级_章节测试.html", "CFA Level I · 章节测试", True),
    "📋 FRM知识清单":  ("FRM_知识清单.html",     "FRM · 知识清单",           False),
    "📝 FRM章节测试":  ("FRM_章节测试.html",     "FRM · 章节测试",           True),
    "📋 CPA知识清单":  ("CPA_知识清单.html",     "CPA · 知识清单",           False),
    "📝 CPA章节测试":  ("CPA_章节测试.html",     "CPA · 章节测试",           True),
    "📋 ACCA知识清单": ("ACCA_知识清单.html",    "ACCA · 知识清单",          False),
    "📝 ACCA章节测试": ("ACCA_章节测试.html",    "ACCA · 章节测试",          True),
}

def render_exam_page(feature_key: str):
    """渲染考试知识清单或章节测试页面"""
    if feature_key not in EXAM_META:
        st.error("页面未找到")
        return

    filename, title, is_test = EXAM_META[feature_key]
    filepath = os.path.join(EXAMPASS_DIR, filename)

    if not os.path.exists(filepath):
        st.warning(f"⚠️ 文件尚未生成：{filename}")
        st.caption("请先运行 generate_exampass.py 生成考试资料。")
        return

    # 返回按钮
    if st.button("← 返回首页", key=f"back_{feature_key}"):
        st.session_state.current_feature = "🏠 首页"
        st.rerun()

    # 每个考试页各自的横幅
    st.markdown(get_page_banner(feature_key), unsafe_allow_html=True)

    # 标题
    emoji = "📝" if is_test else "📋"
    st.markdown(f"""
    <h2 style="margin-bottom:0.3rem;">{emoji} {title}</h2>
    <p style="color:#94a3b8;font-size:0.85rem;margin-bottom:1rem;">
        2025考纲 · {'交互式章节测试 · 28题100分' if is_test else '知识点速查'}
    </p>
    """, unsafe_allow_html=True)

    # 读取 HTML
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    if is_test:
        # 测试页面：全高 iframe 嵌入（保留 JS 交互）
        st.components.v1.html(html_content, height=1200, scrolling=True)
    else:
        # 知识清单：提取 body 内容直接渲染
        import re
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
        if body_match:
            # 只取内容区，不取完整 HTML shell
            content = body_match.group(1)
            # 移除 script 标签
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            st.markdown(content, unsafe_allow_html=True)
        else:
            st.components.v1.html(html_content, height=800, scrolling=True)

# ============================================================
# 主入口
# ============================================================
# ============================================================
# 移动端底部导航栏（仿 lovable）
# ============================================================
def render_mobile_nav():
    current = st.session_state.current_feature
    nav_items = [
        {"icon": "🏠", "label": "首页", "key": "🏠 首页"},
        {"icon": "📖", "label": "概念", "key": "📖 概念讲解"},
        {"icon": "📝", "label": "刷题", "key": "📝 智能刷题"},
        {"icon": "🎯", "label": "备考", "key": "🎯 考试备考"},
        {"icon": "⏱️", "label": "模考", "key": "⏱️ 模拟考试"},
    ]

    # 纯 HTML 底部导航栏
    items_html = ""
    for item in nav_items:
        is_active = current == item["key"]
        active_class = "mnav-active" if is_active else ""
        items_html += f"""
        <a href="?nav={item['key']}" class="mnav-item {active_class}">
            <span class="mnav-icon">{item['icon']}</span>
            <span class="mnav-label">{item['label']}</span>
        </a>"""

    st.markdown(f"""
    <nav class="mobile-nav">{items_html}</nav>
    <style>
        .mobile-nav {{
            display: none;
            position: fixed; bottom: 0; left: 0; right: 0; z-index: 999;
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(20px) saturate(160%);
            -webkit-backdrop-filter: blur(20px) saturate(160%);
            border-top: 1px solid rgba(37,99,235,0.08);
            box-shadow: 0 -2px 20px rgba(0,0,0,0.06);
            justify-content: space-around; align-items: center;
            padding: 4px 0; padding-bottom: max(4px, env(safe-area-inset-bottom));
        }}
        .mnav-item {{
            display: flex; flex-direction: column; align-items: center; gap: 1px;
            padding: 4px 12px; min-width: 56px;
            text-decoration: none !important; color: #94a3b8 !important;
            font-size: 0.65rem; font-weight: 500;
            border-radius: 12px; transition: all 0.2s ease;
            -webkit-tap-highlight-color: transparent;
        }}
        .mnav-active {{
            color: #2563eb !important; font-weight: 700;
            background: rgba(37,99,235,0.06);
        }}
        .mnav-icon {{ font-size: 1.3rem; line-height: 1; }}
        .mnav-label {{ margin-top: 1px; }}
        @media (max-width: 768px) {{
            .mobile-nav {{ display: flex !important; }}
            section[data-testid="stMain"] {{ padding-bottom: 70px !important; }}
        }}
    </style>
    """, unsafe_allow_html=True)


def main():
    # 移动端底部导航 URL 参数处理
    qp = st.query_params
    if "nav" in qp:
        st.session_state.current_feature = str(qp["nav"])
        st.session_state.exam_state = None

    if not st.session_state.api_key_configured:
        st.warning("""
        **⚡ API Key 未配置**

        请复制 `.env.example` 为 `.env`，填入 DeepSeek API Key。

        获取地址：[https://platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)
        """)
        with st.sidebar:
            manual_key = st.text_input("或手动输入 API Key", type="password")
            if manual_key:
                import config
                config.DEEPSEEK_API_KEY = manual_key
                st.session_state.api_key_configured = True
                st.rerun()
        if not st.session_state.api_key_configured:
            return

    render_sidebar()

    feature = st.session_state.current_feature

    if feature == "🏠 首页":
        render_homepage()
    elif feature == "⏱️ 模拟考试":
        render_exam_ui()
    elif feature == "🕸️ 知识图谱":
        st.markdown(get_page_banner("🕸️ 知识图谱"), unsafe_allow_html=True)
        render_knowledge_graph()
    elif feature == "🎯 考试备考":
        render_exam_hub()
    elif feature in EXAM_META:
        render_exam_page(feature)
    else:
        render_conversation()

    # 移动端底部导航栏
    render_mobile_nav()

if __name__ == "__main__":
    main()
