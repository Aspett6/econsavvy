"""
导出成绩单为 PDF — 优化版（跨平台兼容）
"""
import os
import sys
import datetime
from fpdf import FPDF

# 跨平台字体探测
def _find_cjk_font() -> dict:
    if sys.platform == 'win32':
        candidates = [
            (r'C:\Windows\Fonts\simhei.ttf', 'hei'),
            (r'C:\Windows\Fonts\simsun.ttc', 'sun'),
            (r'C:\Windows\Fonts\simkai.ttf', 'kai'),
            (r'C:\Windows\Fonts\msyh.ttc', 'hei'),
        ]
    elif sys.platform == 'darwin':
        candidates = [
            ('/System/Library/Fonts/PingFang.ttc', 'hei'),
            ('/System/Library/Fonts/STHeiti Light.ttc', 'hei'),
            ('/Library/Fonts/Arial Unicode.ttf', 'sun'),
        ]
    else:
        candidates = [
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'hei'),
            ('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc', 'hei'),
            ('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc', 'sun'),
            ('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', 'sun'),
            ('/usr/share/fonts/truetype/arphic/uming.ttc', 'kai'),
        ]
    found = {}
    for path, role in candidates:
        if role not in found and os.path.exists(path):
            found[role] = path
    for tag in ('hei', 'sun', 'kai'):
        if tag not in found and found:
            found[tag] = list(found.values())[0]
    return found


def generate_score_pdf(report: dict, subject: str = "", total_time_min: int = 0) -> str:
    """生成优化版考试成绩单 PDF"""
    fonts = _find_cjk_font()
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(True, 18)

    has_hei = 'hei' in fonts
    has_sun = 'sun' in fonts
    if has_hei:
        pdf.add_font('Hei', '', fonts['hei'])
    if has_sun:
        pdf.add_font('Sun', '', fonts['sun'])
    if 'kai' in fonts:
        pdf.add_font('Kai', '', fonts['kai'])
    # 兼容 fallback
    font_title = 'Hei' if has_hei else 'Helvetica'
    font_body = 'Sun' if has_sun else (font_title)

    accuracy = report.get('accuracy', 0)
    grade = report.get('grade', '?')
    correct = report.get('correct', 0)
    total = report.get('total', 0)
    wrong = total - correct

    # ── 颜色常量 ──
    BLUE_DARK = (30, 58, 138)
    BLUE_MID = (37, 99, 235)
    BLUE_LIGHT = (219, 234, 254)
    BG_CARD = (249, 250, 251)
    TEXT_DARK = (15, 23, 42)
    TEXT_MID = (71, 85, 105)
    TEXT_LIGHT = (148, 163, 184)
    GREEN = (22, 163, 74)
    RED = (239, 68, 68)
    WHITE = (255, 255, 255)

    # ═══════════ 页眉 ═══════════
    pdf.add_page()
    # 深蓝顶条
    pdf.set_fill_color(*BLUE_DARK)
    pdf.rect(0, 0, 210, 8, 'F')
    # 蓝底 header 区域
    pdf.set_fill_color(*BLUE_MID)
    pdf.rect(0, 8, 210, 48, 'F')

    # Logo 文字
    pdf.set_font(font_title, '', 20)
    pdf.set_text_color(*WHITE)
    pdf.set_y(18)
    pdf.cell(0, 10, 'EconSavvy', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_body, '', 9)
    pdf.cell(0, 6, '经世智用 · 模拟考试成绩单', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ═══════════ 分数大卡片 ═══════════
    pdf.set_fill_color(*WHITE)
    pdf.set_draw_color(*BLUE_MID)
    pdf.set_line_width(0.6)
    card_y = pdf.get_y() - 4
    pdf.rect(18, card_y, 174, 44, 'DF')

    pdf.set_fill_color(*BLUE_LIGHT)
    pdf.set_draw_color(*BLUE_MID)
    pdf.set_line_width(0.3)
    pdf.rect(22, card_y + 3, 166, 38, 'DF')

    # 分数
    pdf.set_font(font_title, '', 42)
    pdf.set_text_color(*BLUE_MID)
    pdf.set_y(card_y + 6)
    pdf.cell(0, 16, f'{correct}/{total}', align='C', new_x="LMARGIN", new_y="NEXT")

    # 正确率 + 等级
    pdf.set_font(font_body, '', 11)
    pdf.set_text_color(*TEXT_MID)
    pdf.cell(0, 7, f'正确率 {accuracy:.0f}%    等级 {grade}', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ═══════════ 考试信息 ═══════════
    pdf.ln(4)
    pdf.set_font(font_title, '', 11)
    pdf.set_text_color(*BLUE_DARK)
    pdf.set_x(20)
    pdf.cell(0, 8, '考试信息', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    info_items = [
        ('科目', subject or '综合'),
        ('日期', datetime.date.today().isoformat()),
        ('题量', f'{total} 题'),
        ('答对', f'{correct} 题'),
        ('答错', f'{wrong} 题'),
    ]
    if total_time_min > 0:
        info_items.insert(2, ('用时', f'{total_time_min} 分钟'))

    pdf.set_font(font_body, '', 9)
    col_width = 34
    pdf.set_x(20)
    for label, value in info_items:
        pdf.set_text_color(*TEXT_LIGHT)
        pdf.cell(col_width, 7, label, align='R')
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(4, 7, '')
        pdf.cell(col_width + 10, 7, value, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(20)

    pdf.ln(6)

    # ═══════════ 得分分布条 ═══════════
    pdf.set_font(font_title, '', 11)
    pdf.set_text_color(*BLUE_DARK)
    pdf.set_x(20)
    pdf.cell(0, 8, '得分分布', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    if total > 0:
        green_w = (correct / total) * 160
        red_w = (wrong / total) * 160
        bar_y = pdf.get_y()
        pdf.set_fill_color(*GREEN)
        pdf.rect(25, bar_y, green_w, 6, 'F')
        pdf.set_fill_color(*RED)
        pdf.rect(25 + green_w, bar_y, red_w, 6, 'F')
        pdf.set_font(font_body, '', 8)
        pdf.set_text_color(*TEXT_MID)
        pdf.set_y(bar_y + 7)
        pdf.set_x(25)
        pdf.cell(green_w, 5, f'正确 {correct}（{accuracy:.0f}%）', align='C')
        pdf.set_text_color(*WHITE)
        pdf.cell(red_w, 5, f'错误 {wrong}', align='C')
        pdf.ln(12)

    # ═══════════ 逐题详情 ═══════════
    pdf.set_font(font_title, '', 11)
    pdf.set_text_color(*BLUE_DARK)
    pdf.set_x(20)
    pdf.cell(0, 8, '逐题详情', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    for d in report.get('details', []):
        is_correct = d.get('is_correct', False)
        q_num = d.get('num', '?')
        kp = d.get('knowledge_point', '')
        q_text = d.get('question_text', '')[:80]
        user_ans = d.get('user_answer', '')
        correct_ans = d.get('correct_answer', '')

        pdf.set_fill_color(*BG_CARD)
        pdf.set_draw_color(229, 231, 235)
        pdf.set_line_width(0.2)
        row_y = pdf.get_y()
        pdf.rect(20, row_y, 170, 9, 'DF')

        # 状态图标
        pdf.set_font(font_title, '', 9)
        if is_correct:
            pdf.set_text_color(*GREEN)
            pdf.set_xy(24, row_y + 1.5)
            pdf.cell(10, 6, '✓', align='C')
        else:
            pdf.set_text_color(*RED)
            pdf.set_xy(24, row_y + 1.5)
            pdf.cell(10, 6, '✗', align='C')

        # 题号 + 知识点
        pdf.set_font(font_body, '', 8)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_xy(36, row_y + 1.5)
        pdf.cell(0, 6, f'第{q_num}题（{kp}）  你的答案：{user_ans}  →  正确答案：{correct_ans}',
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

    # ═══════════ 页脚 ═══════════
    pdf.ln(6)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.3)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    pdf.set_font(font_body, '', 7)
    pdf.set_text_color(*TEXT_LIGHT)
    pdf.cell(0, 4, 'EconSavvy · 经世智用 — 把任何财经概念，讲到你彻底懂', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.cell(0, 4, f'生成于 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C')

    # 保存
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"score_report_{datetime.date.today().isoformat()}.pdf")
    pdf.output(out_path)
    return out_path
