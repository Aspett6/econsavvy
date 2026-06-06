"""
配置管理 — 从 .env 文件加载，解决 API Key 硬编码问题
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
_project_root = Path(__file__).parent
_env_path = _project_root / ".env"
load_dotenv(_env_path)

# API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096"))

# 数据目录
DATA_DIR = _project_root / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 知识库目录
KB_DIR = _project_root / "知识库"
