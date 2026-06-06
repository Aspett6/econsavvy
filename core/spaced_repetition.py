"""
错题间隔重复算法 (Spaced Repetition)
  待复习(0) → 1天后(1) → 3天后(2) → 7天后(3) → 已掌握(4)
"""
import datetime
from core.persistence import load_wrong_answer_book, save_wrong_answer_book


# 间隔天数映射
INTERVALS = {0: 1, 1: 3, 2: 7, 3: 7}   # stage 3→4 需手动确认


def init_sr_fields(entry: dict):
    """为新错题初始化 SR 字段"""
    if "review_stage" not in entry:
        entry["review_stage"] = 0
    if "next_review_date" not in entry:
        # 首次复习：第二天
        entry["next_review_date"] = (
            datetime.date.today() + datetime.timedelta(days=1)
        ).isoformat()


def get_due_reviews() -> list:
    """获取今天需要复习的错题"""
    book = load_wrong_answer_book()
    today = datetime.date.today().isoformat()
    due = [
        w for w in book
        if w.get("review_stage", 0) < 4          # 未掌握
        and w.get("next_review_date", "") <= today  # 已经到期
    ]
    return due


def count_due_reviews() -> int:
    """今天需要复习的数量"""
    return len(get_due_reviews())


def advance_review_stage(index: int) -> bool:
    """将指定错题推进到下一复习阶段，返回是否已掌握"""
    book = load_wrong_answer_book()
    if index < 0 or index >= len(book):
        return False

    entry = book[index]
    init_sr_fields(entry)
    stage = entry["review_stage"]

    if stage >= 4:
        return True  # 已经掌握了

    new_stage = stage + 1
    entry["review_stage"] = new_stage

    if new_stage >= 4:
        entry["reviewed"] = True
        entry["next_review_date"] = "mastered"
        save_wrong_answer_book(book)
        return True  # 已掌握
    else:
        days = INTERVALS.get(new_stage, 7)
        entry["next_review_date"] = (
            datetime.date.today() + datetime.timedelta(days=days)
        ).isoformat()
        save_wrong_answer_book(book)
        return False


def add_wrong_answer_with_sr(entry: dict):
    """添加错题并初始化 SR 字段"""
    from core.persistence import add_wrong_answer as _base_add
    init_sr_fields(entry)
    _base_add(entry)
