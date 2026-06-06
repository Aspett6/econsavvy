"""
模拟考试逻辑 — 5 阶段流程管理
"""
import time
import datetime
import streamlit as st
from core.utils import (
    parse_exam_questions,
    extract_exam_answers,
    normalize_tf,
)
from core.persistence import update_stats_after_grading
from core.spaced_repetition import add_wrong_answer_with_sr


def grade_exam(exam_state: dict, user_answers: dict) -> dict:
    """批改考试试卷，返回成绩报告"""
    correct_answers = exam_state.get("correct_answers", {})
    questions = exam_state.get("questions", [])
    total = len(correct_answers)
    correct_count = 0

    details = []
    kp_results = {}

    for q in questions:
        qnum = str(q["num"])
        correct = correct_answers.get(qnum, "")
        user = user_answers.get(qnum, "未作答")
        is_correct = (normalize_tf(user) == normalize_tf(correct))
        kp = q.get("knowledge_point", "综合")

        if is_correct:
            correct_count += 1

        details.append({
            "num": q["num"],
            "knowledge_point": kp,
            "question_text": q["text"][:120],
            "user_answer": user,
            "correct_answer": correct,
            "is_correct": is_correct,
        })
        kp_results[kp] = {"is_correct": is_correct}

    accuracy = correct_count / total * 100 if total > 0 else 0

    # 等级评定
    if accuracy >= 90:
        grade = "优秀"
        grade_color = "#16a34a"
    elif accuracy >= 75:
        grade = "良好"
        grade_color = "#2563eb"
    elif accuracy >= 60:
        grade = "及格"
        grade_color = "#d97706"
    else:
        grade = "需努力"
        grade_color = "#dc2626"

    # 更新错题本
    for d in details:
        if not d["is_correct"]:
            add_wrong_answer_with_sr({
                "question_ref": f"考试第{d['num']}题",
                "user_answer": d["user_answer"],
                "correct_answer": d["correct_answer"],
                "knowledge_point": d["knowledge_point"],
                "analysis": "",
                "source_conv_id": "exam",
            })

    # 更新统计
    update_stats_after_grading(correct_count, total, kp_results)

    return {
        "total": total,
        "correct": correct_count,
        "accuracy": accuracy,
        "grade": grade,
        "grade_color": grade_color,
        "details": details,
    }


def render_exam_ui():
    """渲染模拟考试 5 阶段 UI"""
    exam = st.session_state.get("exam_state")

    # ---- 阶段1：配置 ----
    if exam is None:
        st.markdown("## 模拟考试")

        col1, col2, col3 = st.columns(3)
        with col1:
            subject = st.selectbox(
                "考试科目",
                ["微观经济学", "宏观经济学", "金融学", "会计学",
                 "税收学", "商法", "西方经济学（微观宏观综合）", "综合"]
            )
        with col2:
            q_count = st.selectbox("题目数量", [5, 10, 15, 20], index=1)
        with col3:
            duration = st.selectbox("考试时间（分钟）", [10, 15, 20, 30], index=1)

        st.markdown("---")
        st.markdown("""
        **考试须知：**
        - 开始后计时器立即启动，时间到自动交卷
        - 每题 4 个选项，单选
        - 全部答完后点击"提交试卷"查看成绩
        - 成绩会自动记录到学习数据看板
        """)

        if st.button("开始考试", type="primary", use_container_width=True):
            st.session_state.exam_state = {
                "phase": "generating",
                "subject": subject,
                "count": q_count,
                "duration_min": duration,
                "questions": [],
                "correct_answers": {},
                "answers": {},
                "start_time": None,
                "score_report": None,
                "raw_text": "",
            }
            st.rerun()

    # ---- 阶段2：AI 生成试题（由 app.py 处理）----

    # ---- 阶段3：答题中 ----
    elif exam.get("phase") == "in_progress":
        questions = exam.get("questions", [])
        elapsed = time.time() - exam.get("start_time", time.time())
        duration_sec = exam.get("duration_min", 15) * 60
        remaining_sec = max(0, duration_sec - elapsed)
        end_time_ms = int((time.time() + remaining_sec) * 1000)

        st.markdown(
            f'<div id="exam-end-time" style="display:none;">{end_time_ms}</div>',
            unsafe_allow_html=True
        )

        mins = int(remaining_sec // 60)
        secs = int(remaining_sec % 60)
        timer_class = "exam-timer warning" if remaining_sec < 300 else "exam-timer"
        st.markdown(
            f'<div id="exam-timer-display" class="{timer_class}">{mins}:{secs:02d}</div>',
            unsafe_allow_html=True
        )

        # 超时自动交卷
        if remaining_sec <= 0:
            report = grade_exam(exam, exam.get("answers", {}))
            st.session_state.exam_state["phase"] = "graded"
            st.session_state.exam_state["score_report"] = report
            st.rerun()

        # 进度条
        answered = len(exam.get("answers", {}))
        st.progress(answered / max(len(questions), 1))
        st.caption(f"已答：{answered} / {len(questions)}")

        # 答题区域
        user_answers = {}
        for q in questions:
            st.markdown(f"""
            <div class="exam-question">
                <div class="q-num">第 {q['num']} 题（{q.get('knowledge_point', '')}）</div>
                <div class="q-text">{q['text']}</div>
            </div>
            """, unsafe_allow_html=True)
            options = q.get("options", {})
            option_labels = [f"{k}. {v}" for k, v in options.items()]
            choice = st.radio(
                f"选择答案（第{q['num']}题）",
                option_labels,
                key=f"exam_q_{q['num']}",
                index=None,
            )
            if choice:
                user_answers[str(q["num"])] = choice[0]
            st.markdown("---")

        st.session_state.exam_state["answers"] = user_answers

        if st.button("提交试卷", type="primary", use_container_width=True):
            report = grade_exam(exam, user_answers)
            st.session_state.exam_state["phase"] = "graded"
            st.session_state.exam_state["score_report"] = report
            st.rerun()

    # ---- 阶段4：成绩单 ----
    elif exam.get("phase") == "graded":
        report = exam.get("score_report", {})
        st.markdown("## 考试成绩单")

        st.markdown(f"""
        <div class="score-card">
            <div class="label">最终得分</div>
            <div class="score">{report['correct']} / {report['total']}</div>
            <div class="label">正确率 {report['accuracy']:.0f}% · 等级：{report['grade']}</div>
        </div>
        """, unsafe_allow_html=True)

        # 逐题详情
        for d in report.get("details", []):
            icon = "✅" if d["is_correct"] else "❌"
            st.markdown(
                f"**第 {d['num']} 题**（{d['knowledge_point']}）：{icon} "
                f"你的答案：{d['user_answer']} | 正确答案：{d['correct_answer']}"
            )

        # PDF 导出
        if st.button("下载成绩单 PDF", use_container_width=True):
            try:
                from core.export import generate_score_pdf
                pdf_path = generate_score_pdf(report, exam.get("subject", ""))
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "点击下载 PDF",
                        data=f,
                        file_name=f"成绩单_{datetime.date.today().isoformat()}.pdf",
                        mime="application/pdf",
                    )
                st.success(f"PDF 已生成")
            except Exception as e:
                st.warning(f"PDF 生成失败：{e}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("重新考试", use_container_width=True):
                st.session_state.exam_state = None
                st.rerun()
        with col2:
            if st.button("返回首页", use_container_width=True):
                st.session_state.exam_state = None
                st.session_state.current_feature = "📖 概念讲解"
                st.rerun()
