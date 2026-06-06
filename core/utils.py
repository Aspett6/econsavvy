"""
工具函数 — 答案解析、HTML 过滤、标准化等
"""
import re

# True/False 标准化映射
TF_TRUE  = {"对", "√", "✓", "✔", "☑", "T", "TRUE",  "Y", "YES", "正确", "是"}
TF_FALSE = {"错", "×", "✗", "✘", "☒", "F", "FALSE", "N", "NO",  "错误", "否"}


def normalize_tf(value: str) -> str:
    """将各种对/错写法标准化为 √ 或 ×，非判断题答案原样返回"""
    v = value.strip().upper()
    if v in TF_TRUE:
        return "√"
    if v in TF_FALSE:
        return "×"
    raw = value.strip()
    if raw in TF_TRUE:
        return "√"
    if raw in TF_FALSE:
        return "×"
    return v


def strip_answers_comment(text: str) -> str:
    """移除 AI 回复中的 ANSWERS 注释，防止学生看到正确答案"""
    return re.sub(
        r'<!--\s*ANSWERS?\s*:\s*[^>]+-->',
        '', text, flags=re.IGNORECASE
    ).strip()


def extract_hidden_answers(ai_text: str) -> dict | None:
    """从 AI 出题回复中提取隐藏的正确答案"""
    ans_match = re.search(
        r'<!--\s*ANSWERS?\s*:\s*([^>]+)-->',
        ai_text, re.IGNORECASE
    )
    if not ans_match:
        return None

    ans_str = ans_match.group(1).strip()
    answers = {}
    for pair in ans_str.split(','):
        pair = pair.strip()
        if ':' in pair:
            num, letter = pair.split(':', 1)
            answers[num.strip()] = letter.strip().upper()
    return answers if answers else None


def parse_user_answers(user_text: str) -> dict:
    """从学生的提交中解析答案，支持多种格式：
    A-D 选择题: '1B 2C 3D' / '1:B 2:C' / '第1题B' / 'B A B' / 'BAB'
    判断题: '1对 2错' / '第1题√ 第2题×' / '对错对' / 'T F T'
    """
    answers = {}

    # 模式1: 题号 + 分隔符 + 答案字母或判断符
    pat1 = re.findall(r'(\d+)\s*[：:.)、\s]*\s*([A-Da-d√×✓✗✔✘TF对错])', user_text)
    for num, letter in pat1:
        answers[num] = letter.upper()

    # 模式2: 第N题 + 答案
    pat2 = re.findall(r'第\s*(\d+)\s*题\s*[：:.]?\s*([A-Da-d√×✓✗✔✘TF对错])', user_text)
    for num, letter in pat2:
        if num not in answers:
            answers[num] = letter.upper()

    if not answers:
        # 判断题符号序列: √×✓✗✔✘
        tf_chars = re.findall(r'[√×✓✗✔✘]', user_text)
        if tf_chars:
            for i, ch in enumerate(tf_chars, 1):
                answers[str(i)] = normalize_tf(ch)

    if not answers:
        # 中文字序列: 对/错
        tf_words = re.findall(r'[对错]', user_text)
        if tf_words:
            for i, w in enumerate(tf_words, 1):
                answers[str(i)] = normalize_tf(w)

    if not answers:
        # 英文字序列: T/F
        tf_letters = re.findall(r'[TtFf]', user_text)
        if tf_letters:
            for i, letter in enumerate(tf_letters, 1):
                answers[str(i)] = normalize_tf(letter)

    if not answers:
        # 选择题字母序列: A/B/C/D
        letters = re.findall(r'[A-Da-d]', user_text)
        if letters:
            for i, letter in enumerate(letters, 1):
                answers[str(i)] = letter.upper()

    return answers


def parse_exam_questions(raw_text: str) -> list:
    """解析 AI 生成的试题文本，返回题目列表"""
    parts = re.split(r'\*\*第\s*\d+\s*题\*\*', raw_text)
    questions = []

    for i, part in enumerate(parts[1:], 1):
        q = {"num": i, "text": "", "options": {}, "knowledge_point": ""}

        kp_match = re.match(r'[（(]([^)）]+)[)）]\s*\n?(.*)', part, re.DOTALL)
        if kp_match:
            q["knowledge_point"] = kp_match.group(1).strip()
            part = kp_match.group(2)

        option_pattern = r'([A-D])[.、:：]\s*(.+?)(?=\n[A-D][.、:：]|\n\n|$)'
        opt_matches = re.findall(option_pattern, part, re.DOTALL)
        for opt_letter, opt_text in opt_matches:
            q["options"][opt_letter] = opt_text.strip()

        first_opt_pos = len(part)
        for opt_letter in ['A', 'B', 'C', 'D']:
            m = re.search(rf'\n{opt_letter}[.、:：]', part)
            if m:
                first_opt_pos = min(first_opt_pos, m.start())
        q["text"] = part[:first_opt_pos].strip()

        if q["text"]:
            questions.append(q)

    return questions


def extract_exam_answers(raw_text: str) -> dict:
    """从 AI 生成的试卷中提取正确答案"""
    ans_match = re.search(
        r'<!--\s*ANSWERS?\s*:\s*([^>]+)-->',
        raw_text, re.IGNORECASE
    )
    if ans_match:
        ans_str = ans_match.group(1).strip()
        answers = {}
        for pair in ans_str.split(','):
            pair = pair.strip()
            if ':' in pair:
                num, letter = pair.split(':', 1)
                answers[num.strip()] = letter.strip().upper()
        return answers
    return {}
