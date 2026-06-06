"""
Generate v5 design document PDF - Expanded 14-page edition
"""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from core.export import _find_cjk_font
from fpdf import FPDF

OUT = os.path.join(os.path.dirname(__file__), '设计书_v5.pdf')

fonts = _find_cjk_font()
pdf = FPDF('P', 'mm', 'A4')
has_hei = 'hei' in fonts
has_sun = 'sun' in fonts
if has_hei: pdf.add_font('Hei', '', fonts['hei'])
if has_sun: pdf.add_font('Sun', '', fonts['sun'])
ft = 'Hei' if has_hei else 'Helvetica'
fb = 'Sun' if has_sun else ft

BLUE_D = (30, 58, 138)
BLUE_M = (37, 99, 235)
BLUE_L = (219, 234, 254)
GRAY_50 = (249, 250, 251)
GRAY_100 = (243, 244, 246)
GRAY_200 = (229, 231, 235)
GRAY_400 = (148, 163, 184)
GRAY_600 = (71, 85, 105)
GRAY_800 = (15, 23, 42)
GREEN = (22, 163, 74)
WHITE = (255, 255, 255)
AUTHORS = '王馨  李昂  雷子亿'
PAGE_W = 210

def check_page_break(needed_mm):
    if pdf.get_y() + needed_mm > 272:
        pdf.add_page()

def section_title(title, num=''):
    check_page_break(20)
    pdf.ln(4)
    pdf.set_fill_color(*BLUE_L)
    pdf.set_draw_color(*BLUE_M)
    pdf.set_line_width(0.5)
    pdf.rect(20, pdf.get_y(), 170, 10, 'DF')
    label = f'{num}  {title}' if num else title
    pdf.set_font(ft, '', 11)
    pdf.set_text_color(*BLUE_D)
    pdf.set_y(pdf.get_y() + 2)
    pdf.cell(0, 6, label, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

def sub_title(title, indent=22):
    check_page_break(12)
    pdf.ln(2)
    pdf.set_font(ft, '', 10)
    pdf.set_text_color(*BLUE_D)
    pdf.set_x(indent)
    pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

def body(text, indent=22, size=9):
    check_page_break(15)
    pdf.set_font(fb, '', size)
    pdf.set_text_color(*GRAY_600)
    pdf.set_x(indent)
    pdf.multi_cell(210 - indent * 2, 5.2, text, align='L')

def bullet(items, indent=24):
    for item in items:
        check_page_break(8)
        pdf.set_x(indent)
        pdf.set_font(ft, '', 9)
        pdf.set_text_color(*BLUE_M)
        pdf.cell(5, 5, '-')
        pdf.set_font(fb, '', 9)
        pdf.set_text_color(*GRAY_600)
        pdf.multi_cell(210 - indent - 10, 5.2, item, align='L')
        pdf.ln(0.5)

def code_block(code, indent=25):
    lines = code.strip().split('\n')
    h = len(lines) * 4.5 + 10
    check_page_break(h + 5)
    pdf.set_fill_color(*GRAY_50)
    pdf.set_draw_color(*GRAY_200)
    pdf.set_line_width(0.2)
    pdf.rect(indent, pdf.get_y(), 210 - indent * 2, h, 'DF')
    pdf.set_font(fb, '', 7.5)
    pdf.set_text_color(*GRAY_600)
    pdf.set_y(pdf.get_y() + 5)
    for line in lines:
        pdf.set_x(indent + 5)
        pdf.cell(0, 4.5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

def mod_card(title, desc, indent=22):
    pdf.set_font(fb, '', 8.5)
    chars_per_line = int((170 - 10) / 2.3)
    lines = max(1, (len(desc) + chars_per_line - 1) // chars_per_line)
    card_h = 7 + lines * 4.8 + 4
    check_page_break(card_h + 3)
    y0 = pdf.get_y()
    pdf.set_fill_color(*GRAY_50)
    pdf.set_draw_color(*GRAY_200)
    pdf.set_line_width(0.2)
    pdf.rect(indent, y0, 168, card_h, 'DF')
    pdf.set_font(ft, '', 9)
    pdf.set_text_color(*BLUE_D)
    pdf.set_xy(indent + 5, y0 + 2.5)
    pdf.cell(0, 5, title)
    pdf.set_font(fb, '', 8.5)
    pdf.set_text_color(*GRAY_600)
    pdf.set_xy(indent + 5, y0 + 8)
    pdf.multi_cell(156, 4.8, desc, align='L')
    pdf.set_y(y0 + card_h + 2)

def info_box(text, indent=22):
    check_page_break(16)
    y0 = pdf.get_y()
    pdf.set_fill_color(239, 246, 255)
    pdf.set_draw_color(*BLUE_M)
    pdf.set_line_width(0.3)
    pdf.set_font(fb, '', 8.5)
    chars_per_line = int((170 - 10) / 2.3)
    lines = max(1, (len(text) + chars_per_line - 1) // chars_per_line)
    h = lines * 4.8 + 8
    pdf.rect(indent, y0, 168, h, 'DF')
    pdf.set_xy(indent + 4, y0 + 3)
    pdf.set_text_color(*BLUE_D)
    pdf.set_font(ft, '', 8)
    pdf.cell(0, 4, '关键设计决策')
    pdf.set_xy(indent + 4, y0 + 8)
    pdf.set_font(fb, '', 8.5)
    pdf.set_text_color(*GRAY_600)
    pdf.multi_cell(160, 4.8, text, align='L')
    pdf.set_y(y0 + h + 4)

def ver_table(rows, indent=22):
    col_w = [28, 26, 110]
    header = ['版本', '阶段', '核心变化']
    row_heights = []
    for row in rows:
        pdf.set_font(fb, '', 8)
        desc = row[2]
        chars_per_line = int((col_w[2] - 4) / 2.1)
        lines = max(1, (len(desc) + chars_per_line - 1) // chars_per_line)
        row_heights.append(max(6.5, lines * 4.2 + 2))
    total_h = sum(row_heights) + 7
    check_page_break(total_h + 10)
    y0 = pdf.get_y()
    pdf.set_fill_color(*BLUE_M)
    pdf.set_text_color(*WHITE)
    pdf.set_font(ft, '', 8)
    x = indent
    for h, w in zip(header, col_w):
        pdf.set_xy(x, y0)
        pdf.cell(w, 7, h, align='C', fill=True)
        x += w
    for ri, row in enumerate(rows):
        y = y0 + 7 + sum(row_heights[:ri])
        bg = GRAY_50 if ri % 2 == 0 else WHITE
        pdf.set_fill_color(*bg)
        for ci in [0, 1]:
            pdf.set_xy(indent + sum(col_w[:ci]), y)
            pdf.set_font(ft, '', 8)
            pdf.set_text_color(*GRAY_800)
            pdf.cell(col_w[ci], row_heights[ri], row[ci], align='C', fill=True)
        desc_x = indent + col_w[0] + col_w[1] + 2
        pdf.set_fill_color(*bg)
        pdf.rect(desc_x - 2, y, col_w[2] + 2, row_heights[ri], 'F')
        pdf.set_xy(desc_x, y + 1.5)
        pdf.set_font(fb, '', 8)
        pdf.set_text_color(*GRAY_600)
        pdf.multi_cell(col_w[2] - 4, 4.2, row[2], align='L')
    pdf.set_y(y0 + total_h + 4)


# ═══════════════════ PAGE 1: COVER ═══════════════════
pdf.add_page()
pdf.set_fill_color(*BLUE_D)
pdf.rect(0, 0, 210, 8, 'F')
pdf.set_fill_color(*BLUE_M)
pdf.rect(0, 8, 210, 118, 'F')

pdf.set_y(36)
pdf.set_font(ft, '', 34)
pdf.set_text_color(*WHITE)
pdf.cell(0, 15, 'EconSavvy', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font(fb, '', 15)
pdf.cell(0, 9, '经世智用', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font(fb, '', 10)
pdf.set_text_color(191, 219, 254)
pdf.cell(0, 7, 'AI 智能学习助手 · 技术设计书', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_text_color(147, 197, 253)
pdf.set_font(fb, '', 9)
pdf.cell(0, 6, 'v5 · Blue Glass Edition', align='C', new_x="LMARGIN", new_y="NEXT")

pdf.set_fill_color(*WHITE)
pdf.set_draw_color(*GRAY_200)
pdf.set_line_width(0.3)
card_y = pdf.get_y() + 10
pdf.rect(22, card_y, 166, 68, 'DF')
info = [
    ('项目名称', 'EconSavvy · 经世智用'),
    ('版本', 'v5 · Blue Glass Edition'),
    ('技术栈', 'Python / Streamlit / DeepSeek / Jieba+TF-IDF / fpdf2'),
    ('作者', AUTHORS),
]
pdf.set_y(card_y + 8)
for label, value in info:
    pdf.set_x(40)
    pdf.set_font(ft, '', 10)
    pdf.set_text_color(*GRAY_400)
    pdf.cell(30, 8, label, align='R')
    pdf.set_text_color(*GRAY_800)
    pdf.cell(4, 8, '')
    pdf.set_font(fb, '', 10)
    pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

pdf.set_y(240)
pdf.set_font(fb, '', 8)
pdf.set_text_color(*GRAY_400)
pdf.cell(0, 5, 'EconSavvy · 经世智用 — 把任何财经概念，讲到你彻底懂', align='C')

# ═══════════════════ PAGE 2: TOC ═══════════════════
pdf.add_page()
section_title('目  录')
pdf.ln(2)
toc = [
    ('一', '项目背景与定位'),
    ('二', '用户研究与需求分析'),
    ('三', '产品设计'),
    ('四', '系统架构'),
    ('五', '核心功能模块详解'),
    ('六', '知识库与检索系统'),
    ('七', 'AI 智能批改引擎'),
    ('八', '关键技术实现'),
    ('九', '版本演进'),
    ('十', '部署与运维'),
    ('十一', '未来规划'),
]
for num, title in toc:
    pdf.set_x(45)
    pdf.set_font(ft, '', 11)
    pdf.set_text_color(*GRAY_800)
    pdf.cell(0, 9, f'{num}、{title}', new_x="LMARGIN", new_y="NEXT")

# ═══════════════════ PAGE 3: 项目背景与定位 ═══════════════════
pdf.add_page()
section_title('项目背景与定位', '一')

body('1. 财经学习的三大痛点')
pdf.ln(2)
body('痛点一：知识碎片化。财经专业课程横跨会计学、金融学、经济学、税收学、商法等多个学科，教材厚重、知识点分散。学生在期末复习或备考证书时，难以快速检索和串联跨学科的概念。')
pdf.ln(2)
body('痛点二：刷题反馈缺失。传统刷题方式依赖纸质答案册，做完题翻答案、对答案、看解析三个环节割裂。学生不知道自己哪里薄弱、为什么错、下次如何避免。通用 AI 聊天工具在财经领域深度不足，出题和批改经常出现判断矛盾。')
pdf.ln(2)
body('痛点三：学习进度黑箱。学生无法量化自己的掌握程度——哪些知识点已经扎实、哪些需要回炉、哪些是考试必考但还没碰过的。缺乏一个自动追踪学习数据并给出可视化反馈的工具。')
pdf.ln(5)

body('2. 产品定位')
pdf.ln(2)
body('EconSavvy（经世智用）定位为「一站式 AI 财经学习平台」。不是题库 APP，不是网课平台，而是一个用自然语言驱动的智能学习助手——学生用日常对话的方式获取知识、练习题目、模拟考试、规划学习路径。')
pdf.ln(2)
body('核心理念：把任何财经概念，讲到你彻底懂。从直觉理解 -> 数学公式 -> 实战案例 -> 易错陷阱 -> 概念对比，结构化地层层剥开，不跳步骤、不扔结论。')
pdf.ln(5)

body('3. 目标用户画像')
pdf.ln(2)
bullet([
    '财经专业本科生：日常概念学习、期末复习、知识点串联',
    'CFA / FRM / CPA / ACCA 备考学生：考纲知识点速查、章节测试、全真模拟',
    '有论文需求的财经学生：选题推荐、大纲生成、文献格式整理',
    '非计算机背景的财经学习者：无需学习任何命令行或编程，浏览器打开即用',
])

# ═══════════════════ PAGE 4: 用户研究 ═══════════════════
pdf.add_page()
section_title('用户研究与需求分析', '二')

body('1. 典型学习场景')
pdf.ln(2)
bullet([
    '场景 A：周二晚上 9 点，大三学生复习《金融学》WACC 章节。课本看了两遍没完全懂——公式记住了但不知道直觉含义。打开 EconSavvy，在概念讲解中输入「WACC 加权平均资本成本」。AI 从「为什么公司融资不是免费的」讲起，给出 DCF 估值案例，对比股权成本和债务成本的区别。10 分钟后，学生不仅懂了公式，还理解了 WACC 在企业估值中的「灵魂折现率」角色。',
    '场景 B：考前两周，CFA 一级考生需要系统刷题。打开「考试备考」->「CFA 章节测试」，做完 28 题交互式测试，秒出成绩：正确率 71%。系统自动标注薄弱知识点（固定收益久期计算、财报存货计价差异），错题进入间隔重复队列。点击「智能刷题」，AI 针对薄弱点出了 10 道巩固练习。',
    '场景 C：期末论文选题。大四学生在「论文辅助」中输入研究方向「金融科技」，AI 生成 5 个选题推荐（含研究价值、数据来源、难度评估），选好后自动生成三级大纲。',
])
pdf.ln(4)

body('2. 用户旅程地图')
pdf.ln(2)
body('首次使用：打开浏览器 -> 首页仪表盘 -> 浏览功能介绍 -> 在概念讲解中试问一个问题 -> AI 流式回复 -> 体验完整学习闭环 -> 注册/收藏。')
pdf.ln(2)
body('日常使用：打开 -> 查看学习概览（今日待复习提醒）-> 进入对应功能 -> 学习/刷题 -> 查看统计数据更新 -> 关闭。')
pdf.ln(2)
body('考前冲刺：打开 -> 模拟考试 -> 配置科目和题量 -> 计时答题 -> 交卷 -> 查看成绩单 + PDF 导出 -> 错题自动进入复习队列。')
pdf.ln(5)

body('3. 核心需求矩阵')
pdf.ln(2)
bullet([
    '概念理解：需要从多个角度（直觉/公式/案例/对比）讲透一个概念，而非给定义',
    '即时反馈：做题后秒出批改结果 + 解析，不需要翻答案册',
    '知识串联：看到知识图谱，知道自己学了什么、哪里薄弱',
    '持久记忆：错题自动安排复习时间，到期提醒',
    '考据权威：AI 回答优先基于知识库教材内容，而非通用网络知识',
    '零门槛：浏览器打开即用，不安装、不配置、不写代码',
])

# ═══════════════════ PAGE 5: 产品设计 ═══════════════════
pdf.add_page()
section_title('产品设计', '三')

body('1. UI 设计语言：蓝色玻璃拟态 (Blue Glass Morphism)')
pdf.ln(2)
body('v5 采用现代玻璃拟态设计风格。核心 CSS 技术：backdrop-filter: blur(24px) saturate(160%) 实现毛玻璃效果；半透明背景 rgba(255,255,255,0.78) + 微蓝边框 rgba(37,99,235,0.07) 营造通透感；三层径向渐变光斑 + shimmer-glow 动画提供灵动的背景氛围。蓝色主色调取自 DeepSeek 品牌蓝（#2563eb），辅以靛蓝（#6366f1）和青色（#06b6d4）构成三色渐变体系。')
pdf.ln(2)
body('CSS 动画系统：cardEnter（卡片依次淡入，staggered 延迟）、shimmerGlow（三层光斑不同节奏呼吸）、floatSlow（悬浮卡片微浮动）、glowPulse（主按钮发光呼吸）、flamePulse（连胜火焰旋转 + 色相偏移）。')
pdf.ln(5)

body('2. 导航架构')
pdf.ln(2)
body('v5 采用侧边栏主导航架构，所有功能入口集中在一处，用户无需记忆「哪个功能在哪个标签页」。侧边栏结构（自上而下）：')
bullet([
    'Logo 区：EconSavvy + 经世智用 · AI Finance Tutor',
    '新建对话按钮（渐变主按钮，最常用操作置顶）',
    '主导航：首页 | 概念讲解 | 智能刷题 | 学习规划 | 论文辅助 | 考试备考 | 模拟考试',
    '知识图谱入口（独立页面）',
    '分隔线',
    '错题复习快捷入口（红色角标提示待复习数量）',
    '最近对话列表（hover 显示删除按钮，点击切换对话）',
    '学习概览卡片（总答题数 + 正确率）',
    '系统状态折叠区（缓存命中率 / 知识库段落数）',
])
pdf.ln(3)
body('桌面端侧边栏永久展开（280px 固定宽度，多重 JS/CSS 防御防止折叠），移动端 768px 以下允许原生折叠 + 全屏覆盖式展开。')

# ═══════════════════ PAGE 6: 产品设计（续） ═══════════════════
pdf.add_page()
section_title('产品设计（续）', '三')

body('3. 首页仪表盘')
pdf.ln(2)
body('v5 新增首页仪表盘，作为用户每次打开应用的默认着陆页。设计目标：3 秒内让用户知道「我学到了哪里」「接下来该做什么」。')
pdf.ln(2)
body('仪表盘布局（自上而下）：')
bullet([
    '顶部欢迎区：时段自适应问候语（清晨好 / 上午好 / 晚上好）+ 渐变色标题「今天想攻克哪个知识点？」+ Classic 品牌 tagline',
    '快捷提问区：4 个可点击按钮（如「杜邦分析法怎么拆解 ROE」），点击直接跳转概念讲解并发起提问',
    '数据看板：4 卡片行（总答题数 / 正确率 / 待复习数 / 学习天数），每张卡片玻璃拟态 + 入场动画',
    '学习路径推荐：3 张横排卡片（概念讲解 / 智能刷题 / 考试备考），带图标 + 功能描述，点击直达',
    '考试备考区：4 个紧凑入口（CFA / FRM / CPA / ACCA），点击进入考试 Hub 页',
    '底部状态栏：知识库段落数 + AI 缓存命中率 + 已覆盖考试范围',
])
pdf.ln(5)

body('4. 各功能页面统一的横幅系统')
pdf.ln(2)
body('每个功能页面顶部都有一个专属横幅（Page Banner），包含：图标 + 英文标题 + 中文副标题 + 一行功能描述。17 个页面各有不同的横幅文案，不重复。例如概念讲解页横幅：「Concept Deep Dive - 从直觉到对比表，结构化讲透每一个概念」，智能刷题页横幅：「Practice Makes Permanent - 做题 + 批改 + 解析 + 收录错题，一条龙」。')
pdf.ln(5)

body('5. 移动端响应式适配')
pdf.ln(2)
body('768px 断点以下：侧边栏从永久展开变为 Streamlit 原生折叠模式（全屏覆盖式），JS 强制守卫仅在桌面端生效。首页和功能页的卡片从横排变为竖排堆叠，字体缩小 10-15%，按钮和触摸目标增大以确保手指点击友好。聊天输入框高度和气泡最大宽度自动调整。')

# ═══════════════════ PAGE 7: 系统架构 ═══════════════════
pdf.add_page()
section_title('系统架构', '四')

body('1. 六层架构总览')
pdf.ln(2)

layers = [
    ('表现层', 'Streamlit Web UI · 蓝色玻璃拟态 CSS 体系（600+ 行） · JavaScript 前端逻辑（侧边栏守卫 + 考试计时器 + 自动滚动 + 主题响应）'),
    ('应用层', '8 大功能模块（首页/概念讲解/智能刷题/学习规划/论文辅助/考试备考/模拟考试/知识图谱）· 系统自动批改引擎 · 5 阶段考试状态机 · 对话路由'),
    ('AI 服务层', 'DeepSeek API (deepseek-chat) · OpenAI SDK 兼容接口 · 流式响应处理 · LRU + TTL 双层缓存（200 条/1h TTL） · 8 角色 System Prompts · 异常分类处理（401/429/网络）'),
    ('知识检索层', 'Jieba 中文分词（精确模式） · TF-IDF 向量化 · 余弦相似度 Top-K 检索 · 78 段落知识库（9 学科 + 4 证书考试） · 50+ 节点知识图谱关系网络 · 回退关键词匹配'),
    ('持久化层', '5 个 JSON 文件：conversations.json（对话历史）/ wrong_answer_book.json（错题本）/ study_stats.json（学习统计）/ ai_cache.json（AI 缓存）/ _exam_cache.json（考试缓存）'),
    ('基础设施层', 'Python 3.11 · Streamlit 1.28+ · Nginx 反向代理（80->8501） · Docker 容器 · 阿里云 ECS Windows Server · nssm 服务注册（开机自启）'),
]
for name, desc in layers:
    pdf.ln(1.5)
    pdf.set_x(24)
    pdf.set_font(ft, '', 10)
    pdf.set_text_color(*BLUE_M)
    pdf.set_x(24)
    pdf.cell(0, 7, f'▎{name}')
    pdf.ln(7)
    pdf.set_x(32)
    pdf.set_font(fb, '', 8.5)
    pdf.set_text_color(*GRAY_600)
    pdf.multi_cell(0, 5.5, desc)
    pdf.ln(0.5)

pdf.ln(5)
body('2. 核心数据流')
pdf.ln(2)
code_block("""用户输入 (prompt)
    |
app.py: render_conversation()
    |
    |-- build_kb_context(query)
    |       +-- kb.search(query, top_k=5)
    |       +-- Jieba 分词 -> TF-IDF 余弦相似度 -> Top-5 最相关段落
    |       +-- 封装为「参考资料」注入 prompt
    |
    |-- stream_ai(messages, feature)
    |       +-- cache.get(SHA256(messages+feature))
    |       |       +-- hit: 直接返回缓存内容（&& TTL 未过期）
    |       |       +-- miss: DeepSeek API 流式调用
    |       +-- 流式 tokens 写入 placeholder（渐进渲染）
    |       +-- 完整响应存入 cache
    |
    +-- (智能刷题模式) 学生提交答案后:
            +-- extract_hidden_answers(full_response) -> {1:'B', 2:'A', ...}
            +-- parse_user_answers(user_prompt) -> {1:'B', 2:'A', ...}
            +-- 系统比对 -> 生成批改报告（系统判断，不可更改）
            +-- 第 2 次 stream_ai() -> AI 根据系统判定补写每道题解析
            +-- 错题 -> add_wrong_answer_with_sr() -> 间隔重复队列
            +-- update_stats_after_grading() -> 学习统计更新

持久化（每次对话后自动执行）:
save_conversations() + save_wrong_answer_book() + save_study_stats() + cache.save()""")

# ═══════════════════ PAGE 8: 核心功能详解 ═══════════════════
pdf.add_page()
section_title('核心功能模块详解', '五')

body('v5 共实现 8 大核心功能模块，外加首页仪表盘和知识图谱两个独立页面。')
pdf.ln(4)

sub_title('5.1 概念讲解 (Concept Deep Dive)')
body('三段深度自适应机制：根据学生输入的关键词（「简单讲」「深入讲」或默认），自动切换小白版（生活化比喻、避免术语、200 字）、进阶版（公式 + 案例 + 应用场景、300 字）和专业版（理论争议 + 前沿研究 + 推导、400+ 字）。')
pdf.ln(2)
body('结构化输出框架：直觉理解（一句话说清解决什么问题）-> 核心定义（准确专业定义）-> 数学公式（公式 + 每个符号含义 + 直觉解释）-> 实战案例（具体数字案例，代入公式算一遍）-> 易错陷阱（考试/实践中最容易出错的地方）-> 对比表格（与易混淆概念的对比）-> 一句话总结。')
pdf.ln(2)
body('知识库优先：每次提问前自动调用 TF-IDF 检索，将 Top-5 最相关教材段落注入 System Prompt 的「参考资料」区域。AI 被要求优先基于这些内容回答，仅在参考资料不够时使用通用知识补充。')
pdf.ln(5)

sub_title('5.2 智能刷题 (Practice Makes Permanent)')
body('两步式出题-批改协议：第一步（出题）：学生说「出 5 道微观经济学选择题」，AI 生成题目和选项，末尾附加 HTML 注释 <!-- ANSWERS:1:B,2:A,... --> 隐藏正确答案。学生看到的是干净的题目，看不到答案。第二步（批改）：学生提交答案后，系统独立完成答案比对，然后调用第二次 AI 请求——这次 AI 只根据系统给定的对错结果写解析，不具备修改判定结果的权限。')
pdf.ln(2)
body('HTML 注释隐藏机制：Streamlit 的 st.markdown() 默认不渲染 HTML 注释。这是一个「零依赖、零开销」的方案——不需要额外的加密、不需要分离出题和批改的 API 调用、不需要数据库存储答案。strip_answers_comment() 在展示 AI 回复时还会再过滤一次，双重保险。')
pdf.ln(2)
body('出题来源灵活：可以指定数量（「5 道」）、科目（「微观经济学」）、知识点（「弹性的题」）、难度（「难题」）或直接基于错题本生成针对性练习。')

# ═══════════════════ PAGE 9: 核心功能详解（续） ═══════════════════
pdf.add_page()
section_title('核心功能模块详解（续）', '五')

sub_title('5.3 模拟考试')
body('5 阶段全真模拟流程：Phase 1 - 考试配置（选择科目、设定题量 5-50 题、设定时间 10-120 分钟）；Phase 2 - AI 生成试卷（按配置生成题目，40% 基础 + 40% 中等 + 20% 难题）；Phase 3 - 全屏答题（JavaScript 倒计时器实时显示剩余时间，最后 5 分钟红色闪烁警告）；Phase 4 - 自动阅卷（系统比对答案，生成成绩单：总分/正确率/等级 + 逐题对错）；Phase 5 - PDF 导出（一键生成 A4 成绩单 PDF，含分数卡片、分布条、逐题详情，可打印或提交给老师）。')
pdf.ln(2)
body('倒计时自动提交：时间归零时 JavaScript 自动触发提交按钮，防止学生超时作答。倒计时器同时运行在页面 iframe 内外，确保在任何渲染模式下都能正常工作。')
pdf.ln(5)

sub_title('5.4 考试备考 (Exam Preparation Hub)')
body('考试备考 Hub 页是 v5 新增的集中入口，整合了两类学习资源：大学课程科目（会计学、金融学、税收学、商法、经济学等，自动扫描知识库目录展示）+ 证书考试（CFA / FRM / CPA / ACCA 四大考试的知识清单和章节测试）。')
pdf.ln(2)
body('知识库规模：78 个 TF-IDF 索引段落，覆盖 9 大学科 + 4 证书考试。具体分布：CFA Level I（10 大模块，11 页大纲 + 28 题交互测试）、FRM Part I & II（10 模块，11 页大纲 + 28 题测试）、CPA 专业阶段（6 科，8 页大纲 + 28 题测试）、ACCA 全阶段（13 门，8 页大纲 + 28 题测试）、5 门大学基础学科（会计学/金融学/税收学/商法/经济学，20 段教材原文）。')
pdf.ln(2)
body('考试大纲来源：基于 2025 年官方 Candidate Body of Knowledge（CBOK）和考试机构公开的 Learning Outcome Statements（LOS），通过网络搜索 + exampass 结构化处理生成。')
pdf.ln(5)

sub_title('5.5 其他功能模块')
mod_card('学习规划', 'AI 根据学生的目标（期末/考研/考证）、科目、可用时间和考试日期，生成包含总体策略、阶段划分、每周计划、每日流程、重点知识点、检测节点和打卡表的完整学习计划。')
mod_card('论文辅助', '覆盖论文全流程：选题推荐（含研究价值、难度、数据来源）-> 大纲生成（章-节-小节 + 建议字数）-> 段落写作（学术规范）-> 文献格式整理（GB/T 7714 标准）。')
mod_card('知识图谱', '8 大学科 50+ 知识点节点，按父子关系组织。学习数据实时驱动 4 色掌握度标注：绿 >=80%（扎实）/ 橙 60-80%（需巩固）/ 红 <60%（薄弱）/ 灰（未测试）。点击科目展开章节子节点。')

# ═══════════════════ PAGE 10: 知识库与检索 ═══════════════════
pdf.add_page()
section_title('知识库与检索系统', '六')

body('1. 知识库演进历程')
pdf.ln(2)
body('v1-v2（关键词匹配）：使用 1-4 字 n-gram 切分 + 英文单词正则提取，简单集合交集打分。优点是零依赖，缺点是无法区分「银行利率」和「银行抢劫」——纯粹字符串匹配。')
pdf.ln(2)
body('v3（Jieba + TF-IDF）：引入 Jieba 中文分词（精确模式），构建 TF-IDF 向量索引。用余弦相似度替代集合交集，显著提升语义区分能力。同时引入模块级 @st.cache_resource 单例，索引仅构建一次。')
pdf.ln(2)
body('v4（exampass 结构化知识）：知识库从纯文本升级为结构化 HTML 知识清单 + 互动测试。5 门核心科目（微观/宏观经济学、金融学、会计学、税收学）各自拥有知识清单和章节测试。')
pdf.ln(2)
body('v5（规模扩展 + 证书覆盖）：知识段落从 20 段扩展至 78 段。新增 CFA/FRM/CPA/ACCA 四大证书考试的独立知识目录，每门考试配有完整的大纲文件和交互式测试 HTML。')
pdf.ln(5)

body('2. TF-IDF 检索技术细节')
pdf.ln(2)
body('分词层：Jieba 精确模式 lcut，过滤长度 <2 的单词和纯空白。Jieba 不可用时自动回退到 1-4 字 n-gram + 英文单词正则提取。')
body('索引层：遍历知识库目录所有 .txt 文件，按「--- 第 X 页 ---」标记分割页面。对每个页面（文档）计算词频 TF 和逆文档频率 IDF。IDF 平滑公式：log((N+1)/(df+1)) + 1。')
body('查询层：对用户 query 同样分词，计算 query TF 向量。与所有文档 TF 向量计算余弦相似度（IDF 加权）：sim = dot(q_tf * idf, d_tf * idf) / (|q| * |d|)。返回 Top-K（默认 5）最相关段落，每段截取前 800 字符。')
body('上下文注入：将检索到的段落封装为【参考资料】格式，注入 System Prompt。AI 被指令优先基于这些内容回答。')
pdf.ln(5)

body('3. 知识图谱关系网络')
pdf.ln(2)
body('静态定义 50+ 节点组成 8 棵学科树：微观经济学（9 子节点 + 14 孙节点）、宏观经济学（7+8）、金融学（5+6）、会计学（4+5）、税收学（5+3）、商法（6+3）、统计学（2）、财政学（3）、管理学（4）。每个节点标注 parent/children 关系。')
body('动态着色：根据 study_stats.json 中记录的答题数据，计算每个知识点的正确率，映射为 4 色（绿/橙/红/灰）实时渲染。学生一眼看到自己的薄弱环节。')

# ═══════════════════ PAGE 11: AI 智能批改引擎 ═══════════════════
pdf.add_page()
section_title('AI 智能批改引擎', '七')

body('1. 设计动机：解决「AI 出题又判题」的矛盾')
pdf.ln(2)
body('传统 AI 刷题方案中，同一个模型负责出题、判断对错、写解析。经验表明，大模型在判断自己出的题目时有不低的错误率——它可能先说 B 是对的，当学生追问时又说「抱歉，重新检查后应该是 C」。这严重破坏学习体验。')
pdf.ln(2)
body('v4 提出的解决方案：将「判断对错」和「写解析」分离为两个独立环节——系统负责绝对正确的答案比对（机械操作，零错误），AI 负责在这个正确判定基础上写解析（发挥语言能力）。')
pdf.ln(5)

body('2. 批改流程详解')
pdf.ln(2)
code_block("""Step 1: AI 出题（隐藏答案在 HTML 注释中）
  **第 1 题**（知识点：需求弹性）
  当某商品的需求价格弹性为 0.8 时...
  A. xxx  B. xxx  C. xxx  D. xxx
  <!-- ANSWERS:1:B -->

Step 2: 学生作答（自然语言格式）
  "B A D C B"  或  "1B 2A 3D 4C 5B"  或  "对错对错对"

Step 3: 系统自动比对
  extract_hidden_answers() -> {1: 'B', 2: 'A', 3: 'D', 4: 'C', 5: 'B'}
  parse_user_answers("B A D C B") -> {1: 'B', 2: 'A', 3: 'D', 4: 'C', 5: 'B'}
  逐题比对 -> 第1题正确, 第2题正确, ...

Step 4: AI 补写解析（仅根据系统判定结果）
  第 1 题：V 正确
  你的答案：B  |  正确答案：B
  解析：需求价格弹性 0.8 意味着价格变动 1%...""")
pdf.ln(3)

body('3. 7+ 格式答题解析器（parse_user_answers）')
pdf.ln(2)
body('支持的自然答题格式：空格分隔字母（B A D C B）、冒号分隔（1:B 2:A 3:D）、题号前缀（第1题B）、连续字母（BAB）、对错中文（对错对）、T/F 英文（T F T）、对叉符号。normalize_tf() 将 15+ 种对错表示（对/错/真/假/T/F/True/False/Yes/No/...) 统一为标准化判定值。')
pdf.ln(5)

body('4. 安全措施')
bullet([
    'HTML 注释双重过滤：Streamlit markdown() 默认不渲染 HTML 注释 + strip_answers_comment() 在展示 AI 回复时正则过滤 <!-- ANSWERS:... -->',
    '系统批改结果不可覆盖：AI 收到的 prompt 明确指令「系统已判定，你不可更改」，且 grading.py 中的报告格式将系统判定和 AI 解析分块输出',
    '答案解析位于出题者的文本末尾，不显示在 UI 中——即使学生打开浏览器开发者工具查看源代码才能看到，正常使用中完全不可见',
])

# ═══════════════════ PAGE 12: 关键技术实现 ═══════════════════
pdf.add_page()
section_title('关键技术实现', '八')

body('1. 间隔重复算法 (Spaced Repetition)')
pdf.ln(2)
body('基于艾宾浩斯遗忘曲线实现 4 阶段复习模型。每道错题自动附带 review_stage 和 next_review_date 字段：Stage 0（待复习，次日）-> Stage 1（1 天后）-> Stage 2（3 天后）-> Stage 3（7 天后）-> Stage 4（已掌握，手动确认）。每次打开应用时 count_due_reviews() 扫描错题本，统计哪些题目到期需要复习，侧边栏角标提醒。mark_reviewed() 将题目逐级推进直到掌握。')
pdf.ln(5)

body('2. AI 响应缓存')
pdf.ln(2)
body('LRU + TTL 双层策略。缓存键 = SHA256(json.dumps(messages) + feature)，确保相同问题+相同功能模块的缓存精确命中。TTL 1 小时，最多 200 条。v5 新增持久化：cache.save() 将 OrderedDict 序列化为 data/ai_cache.json，应用启动时 _load() 自动恢复，过滤掉已过期的条目。')
pdf.ln(5)

body('3. 跨平台字体探测')
pdf.ln(2)
body('_find_cjk_font() 根据 sys.platform 分三路探测：Windows（SimHei/SimSun/SimKai/MSYH）、macOS（PingFang/STHeiti/Arial Unicode）、Linux（Noto Sans/Serif CJK/DroidSansFallback/AR PL UMing）。按角色（hei/sun/kai）分别匹配，缺省时复用第一个找到的字体。解决了 v4 中 FONT_DIR = r\'C:\\\\Windows\\\\Fonts\' 在 Linux/Docker 上直接崩溃的问题。')
pdf.ln(5)

body('4. 对话持久化')
pdf.ln(2)
body('v5 新增。load_conversations()/save_conversations() 操作 data/conversations.json。每次消息交换后、删除对话时、新建对话时自动保存。应用重启后 st.session_state.conversations 从 JSON 恢复，对话历史完整保留。')
pdf.ln(5)

body('5. Streamlit 侧边栏守卫（多重防御）')
pdf.ln(2)
body('Streamlit 默认允许用户折叠侧边栏，v5 需要侧边栏始终可见（作为主导航）。实现方案：CSS 层固定 width/display/transform + 隐藏 collapsedControl 按钮 + 删除关闭按钮；JS 层清除 localStorage/sessionStorage 中的 sidebar 状态 + 150ms 定时暴力重置 + MutationObserver 监听属性变化 + 捕获阶段拦截折叠按钮的 click 事件。桌面端六层防御，移动端自动放行允许原生折叠。')

# ═══════════════════ PAGE 13: 版本演进 ═══════════════════
pdf.add_page()
section_title('版本演进', '九')

body('从 v1 到 v5，EconSavvy 经历了完整的「概念验证 -> 架构升级 -> 功能深化 -> 产品化」的演进路径。每个版本都在上一版本的基础上解决了明确的痛点。')
pdf.ln(4)

ver_table([
    ['v1-v2', '概念验证', '基础 AI 对话模块，学生可以提问财经问题并获得流式回复。8 科财经 txt 知识库作为 AI 回答的参考来源。系统自动批改 + AI 解析双引擎首次实现：系统比对答案保证正确，AI 只写解析。Streamlit 纯 Python 全栈，30 分钟可完成本地部署。'],
    ['v3',    '架构升级', '单文件 app.py 从 1500 行重构为 11 模块分层架构（core/ 目录下 10 个独立模块 + config.py），每个模块职责单一、不超过 300 行。知识检索从 n-gram 关键词匹配升级为 Jieba + TF-IDF 余弦相似度语义检索。数据存储从 Streamlit Session State（刷新即丢失）升级为 JSON 文件持久化（wrong_answer_book.json + study_stats.json）。API Key 改用 python-dotenv 管理，.env 文件加入 .gitignore，提供 .env.example 模板。'],
    ['v4',    '功能深化', '新增 LRU + TTL AI 响应缓存（SHA256 键 + 1h TTL + 200 条容量），大幅减少重复 API 调用。引入艾宾浩斯间隔重复算法（4 阶段：1 天 -> 3 天 -> 7 天 -> 已掌握），错题自动纳入复习队列。exampass 结构化知识殿堂上线：5 学科知识清单 HTML + 章节测试 HTML，支持双标签页（知识清单/章节测试）浏览。50+ 节点知识图谱实现 4 色掌握度可视化。A4 PDF 成绩单导出（fpdf2 + SimHei/SimSun/SimKai 中文字体）。学习数据看板（侧边栏统计卡片 + 每日刷题趋势图 + 知识点掌握标签）。'],
    ['v5',    '产品化',   'UI 全面重构为蓝色玻璃拟态 (Blue Glass Morphism)：600+ 行 CSS + 12 个关键帧动画 + 10 个渐变/阴影变量。导航架构从顶部标签栏改为侧边栏主导航 + 首页仪表盘。新增 CFA/FRM/CPA/ACCA 四大证书考试知识库（+58 个 TF-IDF 段落 + 8 套知识清单 HTML + 8 套章节测试 HTML）。对话持久化（conversations.json）+ AI 缓存持久化（ai_cache.json）。10 项生产环境修复（PDF 跨平台字体、模型名可配置、硬编码路径消除等）。响应式移动端适配。Docker 容器化 + 阿里云 ECS 部署 + Nginx 反向代理。'],
])

pdf.ln(6)
body('v5 生产环境修复清单（10 项）：')
bullet([
    'PDF 字体跨平台自动探测（Win / Mac / Linux），不再硬编码 C:\\\\Windows\\\\Fonts',
    '对话自动持久化到 conversations.json，重启后完整恢复',
    'AI 缓存持久化到 ai_cache.json，重启后有效缓存仍命中',
    'AI 模型名改为可配置（DEEPSEEK_MODEL 环境变量），不再硬编码 "deepseek-chat"',
    'exampass template_engine 本地化到 core/ 目录，消除外部 Claude 安装路径依赖',
    '移除 generate_exampass.py 中的递归 exec() 调用',
    'UI 文案修正：知识库支持格式如实标注（TXT），不再虚假声称支持 PDF/Word',
    'System Prompts 完善：新增考试备考 + 知识图谱两个独立 prompt，概念讲解 prompt 增强为 7 步结构化框架',
    '版本号全局统一：core/__init__.py(v3->v5)、PDF 页脚(v4->v5)、export.py 页眉同步更新',
    'Dockerfile + .dockerignore + .env.example 三件套，一键构建 + 安全部署',
])

# ═══════════════════ PAGE 14: 部署 + 未来 ═══════════════════
pdf.add_page()
section_title('部署与运维', '十')

body('1. Docker 容器化部署')
pdf.ln(2)
code_block("""FROM python:3.11-slim
RUN apt-get update && apt-get install -y fonts-noto-cjk
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
CMD ["streamlit", "run", "app.py"]""")
pdf.ln(2)
body('构建与运行：docker build -t econsavvy . && docker run -p 8501:8501 -e DEEPSEEK_API_KEY=sk-xxx econsavvy')
pdf.ln(5)

body('2. Nginx 反向代理')
pdf.ln(2)
body('Nginx 监听 80 端口，反向代理到本地 Streamlit 8501 端口。同时处理 WebSocket 升级（Streamlit 的实时通信依赖 WebSocket），配置了 proxy_read_timeout 86400 秒以支持长时间的 AI 流式响应。')
pdf.ln(2)
code_block("""server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}""")
pdf.ln(5)

body('3. 当前生产环境')
bullet([
    '服务器：阿里云 ECS（Windows Server），北京机房',
    '进程管理：nssm 将 Streamlit + Nginx 注册为 Windows 服务，开机自启',
    '访问地址：http://39.97.244.228（Nginx 80 端口，已免去 :8501）',
    '部署方式：本地编辑 -> 通过 VNC/RDP 上传文件到服务器 -> nssm restart JingshiApp',
])
pdf.ln(2)
body('4. 推荐部署路线（国际免备案）')
bullet([
    'Hugging Face Spaces：永久免费 16GB RAM，Streamlit 原生支持，适合 MVP 验证',
    'Railway：$5/月起，自动 HTTPS + 自定义域名',
    'Vercel + Supabase（需前端重写为 Next.js）：最完整方案',
])

pdf.ln(6)
section_title('未来规划', '十一')

future = [
    'PDF/Word 教材自动解析：PyMuPDF（MIT 协议）解析 PDF -> 纯文本 -> 自动分页 -> Jieba 分词 -> 纳入 TF-IDF 索引。python-docx 解析 Word。实现真正的「拖拽上传即纳入知识库」。',
    '知识检索升级：TF-IDF -> BM25（零额外依赖，检索效果提升 20-30%）-> ChromaDB 向量检索（sentence-transformers 做 embedding，语义匹配能力质的飞跃）。',
    '多用户系统：Phase 1 URL 参数区分用户（?user=wx，各自独立的 JSON 数据文件）；Phase 2 Supabase Auth（免费 5 万月活）+ Row Level Security。',
    'SM-2 增强间隔重复：引入难度因子 (Ease Factor) + 失败自动重置到 Stage 0，替代当前固定 1-3-7 间隔。更贴合个体差异。',
    '移动端 PWA 支持 + 微信小程序：离线可用、推送通知、添加到桌面。',
    '学习数据分析看板：Plotly 交互图表替代原生 st.bar_chart，支持自定义时间范围、知识点交叉筛选。',
    '团队协作 / 教师端：班级管理、学情概览、布置作业、查看全班掌握度分布。',
]
bullet(future)

# -- Footer --
pdf.ln(4)
pdf.set_draw_color(*GRAY_200)
pdf.set_line_width(0.3)
pdf.line(20, pdf.get_y(), 190, pdf.get_y())
pdf.ln(4)
pdf.set_font(fb, '', 7)
pdf.set_text_color(*GRAY_400)
pdf.cell(0, 4, 'EconSavvy · 经世智用 v5 — AI 智能学习助手 · 技术设计书', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 4, f'{AUTHORS}  |  {datetime.datetime.now().strftime("%Y-%m-%d")}', align='C')

pdf.output(OUT)
print(f'Generated: {OUT}')
print(f'Size: {os.path.getsize(OUT):,} bytes')
