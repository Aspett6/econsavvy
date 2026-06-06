"""
数据持久化 — JSON 文件存储
解决 v2 中 Session State 数据刷新即丢失的问题
"""
import json
import datetime
from pathlib import Path
from config import DATA_DIR


# 文件路径
WRONG_BOOK_FILE = DATA_DIR / "wrong_answer_book.json"
STUDY_STATS_FILE = DATA_DIR / "study_stats.json"


# ---- 默认数据结构 ----
def _default_stats() -> dict:
    return {
        "total_questions_answered": 0,
        "correct_count": 0,
        "wrong_count": 0,
        "total_study_time_min": 0,
        "daily_activity": {},
        "knowledge_points": {},
        "sessions_started": 0,
    }


# ---- 错题本 ----
def load_wrong_answer_book() -> list:
    """从 JSON 文件加载错题本"""
    if not WRONG_BOOK_FILE.exists():
        return []
    try:
        with open(WRONG_BOOK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_wrong_answer_book(data: list):
    """保存错题本到 JSON 文件"""
    try:
        with open(WRONG_BOOK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except OSError:
        pass


def add_wrong_answer(entry: dict):
    """添加一条错题记录（自动去重并持久化）"""
    book = load_wrong_answer_book()
    # 去重
    already = any(
        w.get("source_conv_id") == entry.get("source_conv_id")
        and w.get("question_ref") == entry.get("question_ref")
        for w in book
    )
    if not already:
        entry["timestamp"] = datetime.datetime.now().isoformat()
        entry["reviewed"] = False
        book.append(entry)
        save_wrong_answer_book(book)


def mark_reviewed(index: int):
    """标记错题为已掌握"""
    book = load_wrong_answer_book()
    if 0 <= index < len(book):
        book[index]["reviewed"] = True
        save_wrong_answer_book(book)


def clear_wrong_answer_book():
    """清空错题本"""
    save_wrong_answer_book([])


# ---- 学习统计 ----
def load_study_stats() -> dict:
    """从 JSON 文件加载学习统计"""
    if not STUDY_STATS_FILE.exists():
        return _default_stats()
    try:
        with open(STUDY_STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 确保所有字段存在
        default = _default_stats()
        for k in default:
            if k not in data:
                data[k] = default[k]
        return data
    except (json.JSONDecodeError, OSError):
        return _default_stats()


def save_study_stats(stats: dict):
    """保存学习统计到 JSON 文件"""
    try:
        with open(STUDY_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
    except OSError:
        pass


# ---- 对话持久化 ----
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"


def load_conversations() -> dict:
    """从 JSON 文件加载所有对话"""
    if not CONVERSATIONS_FILE.exists():
        return {}
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_conversations(conversations: dict):
    """保存所有对话到 JSON 文件"""
    try:
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2, default=str)
    except OSError:
        pass


# ---- 学习统计 ----
def update_stats_after_grading(correct_count: int, total: int, knowledge_points: dict):
    """批改后更新统计数据"""
    stats = load_study_stats()
    stats["total_questions_answered"] += total
    stats["correct_count"] += correct_count
    stats["wrong_count"] += (total - correct_count)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    stats["daily_activity"][today] = stats["daily_activity"].get(today, 0) + total

    for kp, result in knowledge_points.items():
        if kp not in stats["knowledge_points"]:
            stats["knowledge_points"][kp] = {"correct": 0, "wrong": 0}
        if result["is_correct"]:
            stats["knowledge_points"][kp]["correct"] += 1
        else:
            stats["knowledge_points"][kp]["wrong"] += 1

    save_study_stats(stats)
