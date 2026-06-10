"""
配置管理 — 支持 .env 文件（本地）+ Streamlit Cloud Secrets（线上部署）
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件（本地开发用）
_project_root = Path(__file__).parent
_env_path = _project_root / ".env"
load_dotenv(_env_path)

# 辅助函数：先从 .env 拿默认值
def _env(key, default=""):
    return os.getenv(key, default)

# API 配置：优先从 Streamlit Secrets 读取（线上部署），没有则 fallback 到 .env
def _get_secret(key, default=""):
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    return default

DEEPSEEK_API_KEY = _get_secret("DEEPSEEK_API_KEY") or _env("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = _get_secret("DEEPSEEK_BASE_URL") or _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = _get_secret("DEEPSEEK_MODEL") or _env("DEEPSEEK_MODEL", "deepseek-chat")
_max_tokens_raw = _get_secret("DEEPSEEK_MAX_TOKENS") or _env("DEEPSEEK_MAX_TOKENS", "4096")
DEEPSEEK_MAX_TOKENS = int(_max_tokens_raw)

# 数据目录
DATA_DIR = _project_root / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 知识库目录
KB_DIR = _project_root / "知识库"
