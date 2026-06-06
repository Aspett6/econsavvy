"""
自动批改引擎 — 系统判题 + 错题记录 + 统计更新
"""
import re
import datetime
from core.utils import normalize_tf
from core.persistence import update_stats_after_grading
from core.spaced_repetition import add_wrong_answer_with_sr


def grade_answers_and_build_prompt(
    correct_answers: dict,
    user_answers: dict,
    questions_text: str,
    user_text: str,
    conv_id: str,
) -> tuple:
    """自动批改并构建发送给 AI 的解析请求。

    Returns:
        (ai_prompt, grading_report_markdown)
    """
    total = len(correct_answers)
    correct_count = 0
    q_kp_map = {}

    # 从试题文本中提取每道题的知识点
    for m in re.finditer(r'\*\*第\s*(\d+)\s*题\*\*[（(]([^)）]+)[)）]', questions_text):
        q_kp_map[m.group(1)] = m.group(2).strip()

    # 逐题比对
    grading_lines = []
    kp_results = {}

    for qnum in sorted(correct_answers.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        correct = correct_answers[qnum]
        user = user_answers.get(qnum, "未作答")
        is_correct = (normalize_tf(user) == normalize_tf(correct))
        icon = "✅" if is_correct else "❌"
        status = "正确" if is_correct else "错误"
        kp = q_kp_map.get(qnum, "综合")

        grading_lines.append(
            f"**第 {qnum} 题**（{kp}）：{icon} {status}\n"
            f"你的答案：{user}  |  正确答案：{correct}"
        )
        kp_results[kp] = {"is_correct": is_correct}

        if is_correct:
            correct_count += 1

    grading_report = "\n\n".join(grading_lines)
    accuracy = correct_count / total * 100 if total > 0 else 0
    grading_report += f"\n\n**总分：{correct_count} / {total}（正确率 {accuracy:.0f}%）**"

    # ---- 更新错题本 ----
    for qnum in correct_answers:
        correct = correct_answers[qnum]
        user = user_answers.get(qnum, "未作答")
        if normalize_tf(user) != normalize_tf(correct):
            add_wrong_answer_with_sr({
                "question_ref": f"第{qnum}题",
                "user_answer": user,
                "correct_answer": correct,
                "knowledge_point": q_kp_map.get(qnum, f"题目{qnum}"),
                "analysis": "",
                "source_conv_id": conv_id,
            })

    # ---- 更新统计数据 ----
    update_stats_after_grading(correct_count, total, kp_results)

    # ---- 构建 AI 解析请求 ----
    ai_prompt = f"""系统已完成自动批改，结果如下（你不可推翻）：

{grading_report}

请为每道题写一段详细解析：
- 正确题：一句话确认正确，并补充该知识点的要点
- 错误题：详细解释为什么正确选项是对的，学生选的答案为什么错
- 禁止写"抱歉""更正""重新批改""实际上答案是"等语句
- 禁止质疑或修改系统判定结果"""

    return ai_prompt, grading_report
