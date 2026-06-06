"""
Generate ExamPass knowledge HTML and interactive tests
for all four exams from knowledge base TXT files.
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
from template_engine import save_knowledge_html, save_test

OUT = os.path.join(r'D:\Desktop\智学财经_v5', 'exampass_output')
os.makedirs(OUT, exist_ok=True)

def gen_exam(name, knowledge, questions, duration=45):
    kf = os.path.join(OUT, f'{name}_知识清单.html')
    tf = os.path.join(OUT, f'{name}_章节测试.html')
    save_knowledge_html(knowledge.replace('---', ''), kf, f'{name} · 知识清单')
    save_test(questions, tf, f'{name} · 章节测试',
              f'2025考纲 · 28题100分 · {duration}分钟', duration)
    print(f'  {name} done')

# ══════════════════════════════════════════════════════
# FRM
# ══════════════════════════════════════════════════════
FRM_KNOWLEDGE = """
<h2>Part I：风险管理基础 <span class="tag-must">必考</span></h2>
<p><strong>核心问题</strong>：金融风险有哪些类型？如何度量？企业如何建立有效的风险管理框架？</p>

<h3>风险类型</h3>
<p><span class="kp">市场风险</span><span class="exp">——利率、汇率、股价、商品价格波动导致的损失</span></p>
<p><span class="kp">信用风险</span><span class="exp">——交易对手违约或信用质量下降。预期损失 EL = PD × LGD × EAD</span></p>
<p><span class="kp">操作风险</span><span class="exp">——内部流程失败、人员、系统或外部事件</span></p>
<p><span class="kp">流动性风险</span><span class="exp">——市场流动性（无法以合理价格交易）和资金流动性（无法满足现金流需求）</span></p>

<h3>三道防线模型</h3>
<p>第一道：业务部门（承担并管理风险）。第二道：风险管理部门（独立监督）。第三道：内部审计（独立保证）。</p>

<h3>CAPM 与多因子模型 <span class="tag-key">重点</span></h3>
<p>$$E(R_i) = R_f + \\beta_i \\times [E(R_m) - R_f]$$</p>
<p><span class="kp">夏普比率</span> = (Rp - Rf) / σp</p>
<p><span class="kp">詹森 α</span> = Rp - [Rf + β(Rm-Rf)]。正值表示战胜了 CAPM 基准。</p>

<h3>金融灾难案例 <span class="tag-freq">高频</span></h3>
<table>
<tr><th>事件</th><th>年份</th><th>核心教训</th></tr>
<tr><td>巴林银行</td><td>1995</td><td>交易员权限失控、缺乏职责分离</td></tr>
<tr><td>LTCM</td><td>1998</td><td>高杠杆+流动性冻结=模型失效</td></tr>
<tr><td>次贷危机</td><td>2007-09</td><td>证券化链条过长、评级失误、系统性风险</td></tr>
<tr><td>伦敦鲸</td><td>2012</td><td>CIO对冲变投机、VaR模型操纵</td></tr>
</table>

---

<h2>Part I：定量分析 <span class="tag-must">必考</span></h2>

<h3>概率分布速查 <span class="tag-key">重点</span></h3>
<table>
<tr><th>分布</th><th>FRM 应用</th></tr>
<tr><td>正态</td><td>收益率近似、参数法 VaR</td></tr>
<tr><td>对数正态</td><td>资产价格（非负）</td></tr>
<tr><td>二项</td><td>违约次数建模</td></tr>
<tr><td>泊松</td><td>操作风险损失频率</td></tr>
<tr><td>贝塔</td><td>回收率 LGD 建模（0~1）</td></tr>
</table>

<h3>时间序列 <span class="tag-freq">高频</span></h3>
<p><span class="kp">GARCH(1,1)</span>：$$\\sigma_t^2 = \\omega + \\alpha \\varepsilon_{t-1}^2 + \\beta \\sigma_{t-1}^2$$</p>
<p>α 反应冲击的短期影响，β 反应波动率的持续性。α+β < 1 保证方差平稳。</p>

---

<h2>Part I：金融市场与产品 <span class="tag-must">必考（30%）</span></h2>
<h3>远期与期货定价</h3>
<p>无套利定价：$$F = S_0 \\cdot e^{rT}$$（无收入资产）</p>
<h3>期权 <span class="tag-key">重点</span></h3>
<p>买卖权平价：$$C + Ke^{-rT} = P + S$$</p>
<h3>债券与久期 <span class="tag-key">重点</span></h3>
<p>修正久期 MD = MacD/(1+y)。DV01：收益率变动 1bp 的价格变动。</p>
<p>凸性调整：$$\\frac{\\Delta P}{P} \\approx -MD \\times \\Delta y + \\frac{1}{2} \\times C \\times (\\Delta y)^2$$</p>

---

<h2>Part I：估值与风险模型 <span class="tag-must">必考（30%）</span></h2>
<h3>VaR 在险价值 <span class="tag-key">重点</span></h3>
<p>参数法：VaRα = -[μ + σ·zα]×√T。历史模拟法。蒙特卡洛法。</p>
<p><span class="kp">预期短缺 ES</span> = E[L | L > VaR]。ES 满足次可加性（一致风险度量），VaR 不满足。</p>
<blockquote>易错：VaR 不满足次可加性，ES 满足。巴塞尔 FRTB 因此用 ES 替代 VaR。</blockquote>

<h3>信用风险模型 <span class="tag-key">重点</span></h3>
<p>莫顿模型：股权=公司资产的看涨期权。违约距离 DD。</p>
<p>CVA = (1-R) × ΣPV(Expected Exposure) × PD</p>
<p>高斯 Copula：连接违约相关性——CDO 定价核心，2008 危机中被滥用的模型。</p>

<h3>期权估值</h3>
<p>B-S-M：$$C = S \\cdot N(d_1) - K \\cdot e^{-rT} \\cdot N(d_2)$$</p>
<p>希腊字母：Delta、Gamma、Theta（时间衰减）、Vega（Call/Put 都为正）、Rho。</p>

---

<h2>Part II：市场风险 & 信用风险</h2>
<p>VaR 回测：Kupiec 检验。巴塞尔回测：绿区 0-4、黄区 5-9、红区 ≥10。</p>
<p>FRTB：ES 替代 VaR（97.5%），引入不同流动性期限。</p>
<p>Vasicek 利率模型：$$dr = a(b-r)dt + \\sigma dW$$</p>

<h2>Part II：操作风险 & 流动性</h2>
<p>SMA 标准计量法。操作风险七类事件。</p>
<p>LCR = HQLA / 30天净流出 ≥ 100%。NSFR = ASF/RSF ≥ 100%。</p>

<h2>Part II：前沿话题（2025）</h2>
<p>生成式 AI 风控、加密资产监管 MiCA、气候风险压力测试、SVB 银行倒闭教训。</p>
"""

FRM_QUESTIONS = [
    {"type":"choice","points":2,"question":"预期损失 EL 的正确计算公式是什么？","options":["EL = PD × LGD","EL = PD × EAD","EL = PD × LGD × EAD","EL = LGD × EAD"],"answer":"EL = PD × LGD × EAD","explanation":"信用风险预期损失的三要素：违约概率 × 违约损失率 × 违约风险敞口。各要素缺一不可。"},
    {"type":"choice","points":2,"question":"以下哪项风险度量满足次可加性？","options":["VaR","预期短缺 ES","标准差","以上都满足"],"answer":"预期短缺 ES","explanation":"ES 满足一致风险度量的四个条件（含次可加性）。VaR 不满足次可加性——两个组合的 VaR 可能大于各自 VaR 之和。"},
    {"type":"choice","points":2,"question":"GARCH(1,1) 模型中 α+β 的经济含义是什么？","options":["波动率的短期冲击程度","波动率的持续性","无条件方差","长期平均波动率"],"answer":"波动率的持续性","explanation":"α+β 越接近 1，冲击对波动率的影响越持久。α+β<1 是方差平稳条件。"},
    {"type":"choice","points":2,"question":"根据买卖权平价公式，哪个等式正确（欧式、无股利、连续复利）？","options":["C + S = P + Ke^(-rT)","C + Ke^(-rT) = P + S","C = P + S - Ke^(-rT)","P + Ke^(-rT) = C - S"],"answer":"C + Ke^(-rT) = P + S","explanation":"买卖权平价是衍生品定价基石。组合A（Call+行权价折现）=组合B（Put+股票）。"},
    {"type":"choice","points":2,"question":"巴塞尔 III 规定的 LCR 最低要求是多少？","options":["≥80%","≥90%","≥100%","≥120%"],"answer":"≥100%","explanation":"LCR=HQLA/30天净现金流出≥100%，银行必须有足够优质流动性资产覆盖30天压力期的现金流出。"},
    {"type":"choice","points":2,"question":"莫顿模型将股权价值视为公司资产的什么？","options":["远期合约","看涨期权","看跌期权","互换合约"],"answer":"看涨期权","explanation":"股权=max(VT-F,0)，即公司资产价值的看涨期权（行权价=债务面值）。这是信用风险结构模型的核心洞察。"},
    {"type":"choice","points":2,"question":"以下哪项不属于操作风险的范畴？","options":["内部欺诈导致的损失","系统宕机导致的交易中断","利率变动导致的交易损失","合规违规导致的罚款"],"answer":"利率变动导致的交易损失","explanation":"利率变动是市场风险，不是操作风险。巴塞尔明确将市场风险和信用风险排除在操作风险之外。"},
    {"type":"choice","points":2,"question":"巴塞尔回测框架中，99% VaR 过去250天出现多少次例外属于「黄灯区」？","options":["0-4次","5-9次","10-19次","20次以上"],"answer":"5-9次","explanation":"绿区0-4，黄区5-9（资本乘数递增），红区≥10（重新审查模型）。预期例外=250×1%=2.5次。"},
    {"type":"choice","points":2,"question":"关于 CVA 的正确说法是？","options":["交易对手信用越好 CVA 越大","CVA 代表交易对手违约风险的预期成本","CVA 不影响衍生品公允价值","CVA 只适用于场内交易产品"],"answer":"CVA 代表交易对手违约风险的预期成本","explanation":"CVA=无风险价值-考虑交易对手风险价值。交易对手信用越差→CVA越大。OTC衍生品最需要CVA调整。"},
    {"type":"choice","points":2,"question":"在 GARCH 模型中，如果 α 大而 β 小，说明什么？","options":["波动率对冲击反应强烈但持续性低","波动率非常稳定","长期波动率水平很高","模型不适用"],"answer":"波动率对冲击反应强烈但持续性低","explanation":"α大=昨天冲击对今天方差影响大（尖峰反应快），β小=冲击消退快（波动率记忆短）。"},
    {"type":"tf","points":1,"question":"VaR 满足次可加性。","options":[],"answer":"错误","explanation":"VaR不一定满足次可加性，这正是VaR不是一致风险度量的原因。ES满足次可加性。"},
    {"type":"tf","points":1,"question":"看涨和看跌期权的 Vega 都是正数。","options":[],"answer":"正确","explanation":"波动率上升对期权买方有利（无论Call/Put），所以Vega都为正。"},
    {"type":"tf","points":1,"question":"压力测试是用来替代 VaR 的日常风险度量工具。","options":[],"answer":"错误","explanation":"压力测试是VaR的补充不是替代。VaR度量正常条件，压力测试考虑极端情景。两者互补。"},
    {"type":"tf","points":1,"question":"莫顿模型中的违约距离 DD 越大，违约概率越低。","options":[],"answer":"正确","explanation":"DD衡量资产价值离违约点的标准化距离。DD越大→资产越远离债务→违约越不可能。"},
    {"type":"tf","points":1,"question":"CDS买方承担参考实体的信用风险。","options":[],"answer":"错误","explanation":"CDS买方（保护买方）转移信用风险出去，卖方（保护卖方）承担信用风险。"},
    {"type":"tf","points":1,"question":"预期短缺 ES 总是大于或等于同置信水平的 VaR。","options":[],"answer":"正确","explanation":"ES=E[L|L>VaR]，是超过VaR的损失的条件期望，因此ES≥VaR。"},
    {"type":"tf","points":1,"question":"EWMA 对历史数据给予等权重的处理。","options":[],"answer":"错误","explanation":"EWMA对近期数据赋予更高权重（λ），对远期数据权重指数衰减。λ越接近1权重衰减越慢。"},
    {"type":"tf","points":1,"question":"巴塞尔 III 引入了 NSFR，要求银行中长期资金来源足以覆盖中长期资金运用。","options":[],"answer":"正确","explanation":"NSFR=ASF/RSF≥100%，关注1年期资金来源和运用的匹配。LCR关注30天短期流动性。"},
    {"type":"tf","points":1,"question":"参数法 VaR 假设收益率服从 t 分布。","options":[],"answer":"错误","explanation":"参数法（方差-协方差法）VaR 的核心假设是收益率服从正态分布，使用正态分位数 zα。"},
    {"type":"tf","points":1,"question":"操作风险 AMA 在巴塞尔 III 中被保留为主要方法。","options":[],"answer":"错误","explanation":"巴塞尔 III 已用 SMA 替代了 AMA。因为 AMA 过于复杂且银行间不可比。"},
    {"type":"short","points":6,"question":"简述 VaR 和 ES 的区别，以及为什么 FRTB 用 ES 替代 VaR。","answer":"VaR是在给定置信水平和持有期内最大可能损失的阈值。ES是超过VaR的损失的条件期望。核心区别：ES满足次可加性（VaR不满足），ES捕捉尾部严重程度（VaR只看阈值），ES更不易被操纵。FRTB替换原因：VaR低估尾部风险且不满足次可加性，97.5% ES的稳定性约等于99% VaR但更稳健。"},
    {"type":"short","points":6,"question":"简述 GARCH(1,1) 模型公式、各参数含义及为什么优于历史波动率。","answer":"GARCH(1,1)：σ²t=ω+α·ε²t-1+β·σ²t-1。ω=长期基础方差，α=「新闻」影响（尖峰反应），β=波动率惯性。优于历史波动率：波动率聚集（高波动期后仍预测高波动）、均值回归（预测回ω/(1-α-β)）、对冲击动态响应、适合短期预测。历史波动率假设波动恒定是最大问题。"},
    {"type":"short","points":6,"question":"解释莫顿模型的逻辑：股权如何视为期权？DD 如何计算？主要局限？","answer":"莫顿模型：股权=max(VT-F,0)——公司资产的看涨期权。VT>F时股东还债留剩余；VT<F时股东「不行权」将公司给债权人。DD=[ln(V/F)+(μ-σ²/2)T]/(σ√T)。局限：假设资产服从连续路径（无跳跃）、仅到期日可能违约、资产价值不可观测、单一债务面值简化。"},
    {"type":"short","points":6,"question":"什么是「三道防线」模型？每道防线职责是什么？","answer":"第一道：业务部门（风险的「所有者」，日常管理识别报告风险）。第二道：风险管理和合规部门（独立监督，制定政策限额，监控全公司风险）。第三道：内部审计（独立评估前两道有效性，直接向董事会/审计委员会保证）。核心是责任分离和独立监督。金融灾难案例根源往往是防线失效。"},
    {"type":"essay","points":8,"question":"比较历史模拟法和蒙特卡洛模拟法在 VaR 计算中的优缺点。","answer":"历史模拟法：不需假设分布（非参数）、自动捕获相关性/厚尾/非线性、简单直观。但假设「过去=未来」、无法模拟历史上未发生的情景、对数据长度敏感。蒙特卡洛：可模拟任何假设分布、可模拟未发生情景、灵活处理复杂产品和多因子模型。但有模型风险、计算量大、依赖随机数质量。选择：历史模拟法适用于数据丰富且市场稳定的情况（如流动性股票组合）；蒙特卡洛适用于新产品或需要压力情景分析的情况。"},
    {"type":"essay","points":8,"question":"解释 CDS 定价逻辑。CDS 利差与债券信用利差的关系是什么？","answer":"CDS定价：保护买方定期支付保费S，卖方在信用事件发生时赔付(1-RR)。CDS利差≈PD×(1-RR)。与债券利差应大致相等（否则存在基差套利）。基差=CDS利差-债券利差。正基差（CDS贵）：买债券+买CDS套利。负基差（CDS便宜）：买债券+卖CDS套利。实际基差不为零原因：融资成本差异、交易对手风险、流动性差异、交割期权。2008年后负基差因银行融资成本上升成为常态。"},
    {"type":"essay","points":10,"question":"从市场风险、流动性风险和利率风险三维度分析 SVB 倒闭原因及教训。","answer":"利率风险：资产端是长期固定利率债券（久期长），负债端是短期活期存款——严重久期错配。利率上升500+bp→债券市值暴跌~150亿美元超过权益资本。市场风险：HTM会计掩盖了未实现亏损（摊余成本计量，市价变动不反映）。流动性风险：存款集中于科技初创企业→加息时大量消耗现金→存款快速流出→被迫卖债确认亏损→恐慌→挤兑→48小时倒闭。教训：资产负债久期匹配是最基本的风险管理；HTM会计掩盖真实利率风险；存款集中度是流动性重要维度；压力测试须含利率大幅上升情景；社交媒体时代挤兑可在数小时内发生。"},
    {"type":"comprehensive","points":20,"question":"综合题：假设你是银行风险管理总监。(1)描述整体风险管理框架(6分)。(2)银行持有大量固收债券(久期8年)而负债端是短期存款。分析利率风险并推荐三种对冲策略(7分)。(3)解释LCR和NSFR，设计压力测试评估利率上升+存款流失时的流动性缓冲(7分)。","answer":"(1)治理：董事会下风险管理委员会→CRO→三道防线。RAS由董事会批准。度量：市场风险用VaR+ES+压力测试，信用风险用PD/LGD/EAD+RWA，操作风险用损失数据+KRI。限额：VaR限额、DV01限额、集中度限额、流动性比率。每月风险委员会审议。(2)DA=8年，DL≈0，正久期缺口。利率上升100bp→资产价值跌~8%，杠杆10倍下权益接近清零。对冲：①卖出国债期货缩短久期。②支付固定/收浮动利率互换。③购买利率上限期权。(3)LCR=HQLA/30天净流出，NSFR=ASF/RSF。压力测试：利率再升200bp+存款30%流失+银行间市场冻结。计算HQLA在扣除抵押品折扣后是否仍≥30天净流出，NSFR是否≥100%。不达标→启动应急融资计划CFP。"},
]

# ══════════════════════════════════════════════════════
# CPA
# ══════════════════════════════════════════════════════
CPA_KNOWLEDGE = """
<h2>科目一：会计 <span class="tag-must">必考（CPA 最核心）</span></h2>
<h3>收入确认五步法 <span class="tag-key">重点</span></h3>
<p>1.识别合同。2.识别履约义务。3.确定交易价格。4.分摊价格。5.确认收入（时点vs时段）。</p>
<h3>长期股权投资 <span class="tag-must">必考</span></h3>
<table><tr><th>持股</th><th>方法</th><th>要点</th></tr>
<tr><td>&gt;50%（控制）</td><td>成本法</td><td>编制合并报表</td></tr>
<tr><td>20-50%（重大影响）</td><td>权益法</td><td>按份额确认净利润</td></tr>
<tr><td>&lt;20%</td><td>金融资产</td><td>按 IFRS9/CAS22</td></tr></table>
<p>同一控制合并→账面价值法（无商誉）。非同一控制→购买法（产生商誉）。</p>
<h3>存货与固定资产</h3>
<p>中国准则：FIFO、加权平均、个别计价法。<strong>LIFO 已禁止。</strong>存货减值可转回（固定资产不能转回）。研发：研究阶段全费用化，开发阶段符合条件资本化。</p>
<h3>递延所得税 <span class="tag-key">重点</span></h3>
<p>DTA（可抵扣暂时性差异）、DTL（应纳税暂时性差异）。税率变化在当期确认。</p>

<h2>科目二：审计 <span class="tag-key">重点</span></h2>
<p>AR = IR × CR × DR。RMM = IR × CR。重要性：整体=利润5-10%，实际执行=整体50-75%。</p>
<p>意见类型：无保留、保留（重大不广泛）、否定（重大且广泛）、无法表示（范围受限且广泛）。</p>

<h2>科目三：财务成本管理 <span class="tag-key">重点</span></h2>
<p>WACC、NPV、IRR。DOL=边际贡献/EBIT。DFL=EBIT/(EBIT-利息)。杜邦：ROE=净利率×周转率×权益乘数。</p>
<p>EOQ=√(2KD/Kc)。CAPM：Re=Rf+β(Rm-Rf)。</p>

<h2>科目四：税法 <span class="tag-freq">高频</span></h2>
<p>增值税：13%/9%/6%/0%。一般计税=销项-进项。企业所得税：25%/15%/20%。研发加计100%。个税：综合所得3-45%七级，基本减除6万/年+7项专项附加扣除。</p>

<h2>科目五-六：经济法 & 战略</h2>
<p>公司法2024新修订：注册资本5年内缴足。合同法：要约+承诺=成立。波特五力。三大通用战略：成本领先/差异化/集中化。风险应对：回避/降低/转移/承担。</p>
"""

CPA_QUESTIONS = [
    {"type":"choice","points":2,"question":"CPA 会计中同一控制下企业合并使用什么方法？","options":["购买法（公允价值）","账面价值法","权益法","成本法"],"answer":"账面价值法","explanation":"同一控制下视为「内部资源整合」，按被合并方净资产账面价值入账，不产生商誉。"},
    {"type":"choice","points":2,"question":"审计风险模型中审计师唯一可控的因子是？","options":["固有风险 IR","控制风险 CR","检查风险 DR","重大错报风险 RMM"],"answer":"检查风险 DR","explanation":"IR和CR是被审计单位自身的，审计师只能评估不能改变。DR通过增大样本量、改善审计程序来降低。"},
    {"type":"choice","points":2,"question":"以下哪种审计意见表示「存在重大错报但影响不广泛」？","options":["无保留意见","保留意见","否定意见","无法表示意见"],"answer":"保留意见","explanation":"「重大但不广泛」→保留；「重大且广泛」→否定。范围受限同理。「可能但不广泛」→保留；「可能且广泛」→无法表示。"},
    {"type":"choice","points":2,"question":"研发支出中研究阶段的支出应如何处理？","options":["资本化","全部费用化","符合条件时资本化","成功时一次性资本化"],"answer":"全部费用化","explanation":"研究阶段探索性工作全部费用化。开发阶段符合条件的可资本化（五条件：技术可行+意图+经济利益+资源+可靠计量）。"},
    {"type":"choice","points":2,"question":"关于存货跌价准备的说法正确的是？","options":["一经计提不得转回","可以转回但不超过已计提金额","只能转回50%","中国准则不允许计提"],"answer":"可以转回但不超过已计提金额","explanation":"存货减值可转回（与长期资产不同）。固定资产、无形资产、商誉减值不可转回。"},
    {"type":"choice","points":2,"question":"杜邦分析中 ROE 从12%升到18%但净利���从8%降到6%，最可能的原因是？","options":["盈利能力提升","财务杠杆大幅增加","资产周转率大幅提升","股票回购"],"answer":"财务杠杆大幅增加","explanation":"净利率下降排除了盈利能力提升。ROE=净利率×周转率×权益乘数，净利率↓但ROE↑→权益乘数必大幅↑→「危险的高ROE」。"},
    {"type":"choice","points":2,"question":"增值税一般计税方法应纳税额公式是？","options":["销售额×税率","销项税额-进项税额","(销售额-成本)×税率","含税销售额/(1+税率)×税率"],"answer":"销项税额-进项税额","explanation":"一般计税=销项-进项（抵扣制）。简易计税=含税销售额/(1+征收率)×征收率（不能抵扣进项）。"},
    {"type":"choice","points":2,"question":"企业所得税研发费用加计扣除比例是多少？","options":["加计50%","加计75%","加计100%","加计200%"],"answer":"加计100%","explanation":"一般企业研发费用在据实扣除基础上再按100%加计扣除（总共200%）。自2023年起长期实施。"},
    {"type":"choice","points":2,"question":"波特五力中不属于五力之一的是？","options":["新进入者威胁","供应商议价能力","政府监管力度","替代品威胁"],"answer":"政府监管力度","explanation":"政府监管属于PESTEL分析中的政治/法律因素，不在波特五力中。五力是行业层面的竞争分析。"},
    {"type":"choice","points":2,"question":"关于合同法要约与承诺正确的是？","options":["要约一旦发出就不可撤销","承诺可对要约进行实质性修改","承诺到达要约人时合同成立","要约邀请等同于要约"],"answer":"承诺到达要约人时合同成立","explanation":"合同成立=要约+承诺。承诺必须完全接受要约（不得实质性修改，否则构成新要约）。要约邀请（如广告）不是要约。"},
    {"type":"tf","points":1,"question":"同一控制下企业合并会产生商誉。","options":[],"answer":"错误","explanation":"同一控制使用账面价值法，不产生商誉。只有非同一控制购买法才可能产生商誉。"},
    {"type":"tf","points":1,"question":"固定资产减值损失一经确认不得转回。","options":[],"answer":"正确","explanation":"中国准则规定长期资产（固定资产/无形资产/商誉）减值不可转回。但存货、应收款减值可转回。"},
    {"type":"tf","points":1,"question":"DOL 越大说明固定成本占比越小。","options":[],"answer":"错误","explanation":"DOL越大说明固定成本占比越大。DOL=边际贡献/EBIT，固定成本大→EBIT小→DOL大。"},
    {"type":"tf","points":1,"question":"中国个税综合所得适用3%-45%七级超额累进税率。","options":[],"answer":"正确","explanation":"综合所得（工资+劳务+稿酬×70%+特许权）适用七级。经营所得五级（5%-35%）。"},
    {"type":"tf","points":1,"question":"NPV>0 时 IRR 一定大于必要报酬率。","options":[],"answer":"正确","explanation":"NPV曲线单调递减。NPV=0时r=IRR，NPV>0时r<IRR。两者在常规现金流下一致。"},
    {"type":"tf","points":1,"question":"现金流量表间接法以净利润为起点调整。","options":[],"answer":"正确","explanation":"间接法：CFO=净利润+折旧摊销±营运资本变动±其他非现金项目。"},
    {"type":"tf","points":1,"question":"开发阶段所有支出都可以资本化。","options":[],"answer":"错误","explanation":"只有同时满足五个条件的开发支出才可资本化。不满足的仍需费用化。"},
    {"type":"tf","points":1,"question":"公司制企业中股东对公司债务承担有限��任。","options":[],"answer":"正确","explanation":"有限责任是公司区别于合伙企业的核心特征。股东限于出资额，不对公司债务承担连带责任。"},
    {"type":"tf","points":1,"question":"成本领先战略意味着产品品质也会降低。","options":[],"answer":"错误","explanation":"成本领先≠低质量。通过规模经济、高效运营降低成本的同时保持可接受质量水平。"},
    {"type":"tf","points":1,"question":"审计师出具的否定意见意味着报表完全不真实。","options":[],"answer":"错误","explanation":"否定意见表示存在重大且广泛的错报，但不意味着报表「完全」不真实。审计师不会做如此绝对的表述。"},
    {"type":"short","points":6,"question":"简述长期股权投资中成本法和权益法的适用条件及核算差异。","answer":"成本法（控制>50%）：按成本入账，被投资方宣告股利时确认投资收益，净利润不调投资账面。权益法（重大影响20-50%）：按成本入账，按持股比例确认净利润/亏损（调投资账面），收到股利冲减投资账面。成本法更简单，权益法更真实反映经济实质（「按比例分享经营成果」）。"},
    {"type":"short","points":6,"question":"什么是审计中的重要性水平？如何确定？","answer":"重要性是审计师判断错报是否重大的阈值。整体重要性通常为利润5-10%或收入1-3%。实际执行重要性=整体50-75%（用于设计程序）。明显微小错报=整体3-5%（可不累计）。定性判断同样重要——涉及舞弊或影响盈亏趋势的错报即使金额小也可能重大。"},
    {"type":"short","points":6,"question":"简述 WACC 各参数确定方法及为何用目标资本结构。","answer":"Re：CAPM（Rf+β×(Rm-Rf)）、股利增长模型、债券收益+溢价法。Rd：YTM或贷款利率，需税后Rd×(1-t)。权重：用市值权重非账面价值。用目标资本结构原因：估值面向未来（不是过去），当前结构可能临时偏离最优，使用目标结构使WACC稳定可预测。"},
    {"type":"short","points":6,"question":"简述增值税「视同销售」的情形及其税务处理目的。","answer":"主要情形：代销、跨县市移送（用于销售）、自产/委托加工货物用于非应税项目/集体福利/个人消费、投资/分配/赠送、无偿提供服务/转让无形资产。目的：保持增值税抵扣链条完整（货物离开增值税链条需补税）、确保税收中性（自产和外购在税务待遇上一致）。"},
    {"type":"essay","points":8,"question":"比较同一控制和非同一控制下企业合并的会计处理差异。","answer":"同一控制：按被合并方净资产账面价值入账，合并对价与账面价值的差额调资本公积（不足冲减调留存收益），不产生商誉。合并日视同报告主体自最终控制方开始控制时已存在→追溯调整比较报表。非同一控制（购买法）：按公允价值计量，产生商誉=合并成本-可辨认净资产公允价值份额。仅从购买日起纳入合并→不追溯调整。理由：同一控制=内部资源整合不应产生新商誉；非同一控制=市场交易应反映公允价值。"},
    {"type":"essay","points":8,"question":"解释审计意见类型的决策框架。","answer":"两维度决定：重大性+广泛性。存在错报+不重大→无保留；重大不广泛→保留；重大且广泛→否定。范围受限+不重大→无保留；重大不广泛→保留；重大且广泛→无法表示意见。举例：应收款减值未计提（重大但不广泛）→保留。持续经营不确定+未披露+多科目受影响→否定。审计师被拒绝接触子公司账簿（范围受限且广泛）→无法表示意见。"},
    {"type":"essay","points":10,"question":"比较企业所得税和个人所得税在税基、税率、扣除上的差异。为什么需要「综合与分类相结合」的个税改革？","answer":"企业所得税：税基=收入-不征税-免税-扣除-补亏。税率25%/15%/20%。扣除有限额（业务招待60%/5‰，广宣15%）。个税：综合所得=年收入-6万-专项扣除-附加扣除。税率3-45%七级。7项专项附加扣除。改革理由：公平性（综合计税使同收入同税负，防止高收入者通过分散收入来源避税），反避税（堵住劳务与工资分开计税漏洞），国际趋势（OECD国家普遍综合制），附加扣除（按家庭负担差异化）。但保留分类征收（利息/股息/财产转让），体现鼓励投资导向。"},
    {"type":"comprehensive","points":20,"question":"综合题：甲公司拟收购乙公司80%股权。(1)此前持有10%股权(权益法)，收购后达90%(控制)。描述权益法转成本法的处理。合并成本900万，乙公司可辨认净资产公允价值1000万，计算商誉(6分)。(2)乙公司当年净利润200万，宣告股利80万。甲个别报表和合并报表各如何处理(7分)。(3)年末乙公司(资产组)可收回金额900万，账面1050万(含商誉120万)。计算商誉减值损失(7分)。","answer":"(1)分步交易实现非同一控制合并。合并成本=原10%股权公允+新增80%对价公允=900万。可辨认净资产份额=1000×90%=900万。商誉=900-900=0。原10%股权账面与公允之差计入投资收益。(2)个别报表(成本法)：不确认乙净利润200万。宣告股利：借应收股利72万(80×90%)，贷投资收益72万。合并报表：全额合并乙净利润200万，少数股东损益=20万(200×10%)。股利抵销：借投资收益72万+借少数股东权益8万，贷股利分配80万。(3)减值=1050-900=150万。先冲商誉：商誉120万→0。剩余30万按比例分摊到资产组其他资产。合并报表确认减值损失150万。"},
]

# ══════════════════════════════════════════════════════
# ACCA
# ══════════════════════════════════════════════════════
ACCA_KNOWLEDGE = """
<h2>应用知识阶段 Applied Knowledge</h2>
<h3>BT 商业与技术</h3>
<p>PESTEL、波特五力、组织架构、激励理论（马斯洛/赫茨伯格）、团队发展（Tuckman）、职业道德五项原则（诚信/客观/专业胜任/保密/职业行为）。</p>
<h3>MA 管理会计 <span class="tag-key">重点</span></h3>
<p>成本分类（固定/变动/半变动）。吸收成本法vs边际成本法。盈亏平衡：BEP=固定成本/(单价-单位变动成本)。ABC作业成本法。差异分析。ROI和剩余收益RI。</p>
<h3>FA 财务会计 <span class="tag-key">重点</span></h3>
<p>会计恒等式、复式记账（DEAD CLIC）、三大报表、财务比率（盈利/流动/效率/投资）。</p>

<h2>应用技能阶段 Applied Skills</h2>
<h3>FR 财务报告 <span class="tag-must">必考</span></h3>
<p>IFRS核心准则：IAS16 PPE、IAS36减值、IAS37准备、IAS38无形资产、IFRS9金融工具（AC/FVOCI/FVTPL+ECL）、IFRS15收入五步法、IFRS16租赁（单一模型入表）、IFRS3合并（购买法+商誉）、IFRS10控制三要素、IAS28联营（权益法）。</p>
<h3>FM 财务管理 <span class="tag-key">重点</span></h3>
<p>NPV、IRR、WACC、CAPM、GGM（P₀=D₁/(r-g)）、EOQ、资本结构理论（MM/权衡/优序）、外汇风险（交易/折算/经济）。</p>
<h3>AA 审计与鉴证</h3>
<p>审计风险模型、重要性水平、内控五要素、审计证据充分性和适当性、审计意见类型。</p>

<h2>战略专业阶段 Strategic Professional</h2>
<h3>SBL & SBR</h3>
<p>SBL：综合案例（治理/战略/风险/科技/财务/变革）。SBR：复杂IFRS应用（合并/金融工具/外币折算/ESG/综合报告）。IFRS 18（替代IAS1）2027生效。</p>
"""

ACCA_QUESTIONS = [
    {"type":"choice","points":2,"question":"根据 IFRS 16 承租人对大多数租赁的会计处理是什么？","options":["全部费用化","确认使用权资产和租赁负债入表","仅在附注披露","与 IAS 17 处理一致"],"answer":"确认使用权资产和租赁负债入表","explanation":"IFRS16取消承租人经营租赁分类（单一会计模型）。除低值(<$5,000)和短期(≤12月)外全部入表。"},
    {"type":"choice","points":2,"question":"Tuckman 团队发展模型的正确顺序是？","options":["执行→规范→震荡→形成","形成→震荡→规范→执行→解散","形成→规范→震荡→执行","规范→形成→执行→解散"],"answer":"形成→震荡→规范→执行→解散","explanation":"Forming→Storming→Norming→Performing→Adjourning。震荡阶段不可跳过。"},
    {"type":"choice","points":2,"question":"吸收成本法与边际成本法利润差异的根本原因？","options":["销售数量变化","固定制造费用在存货中的处理差异","直接材料核算差异","管理费用分配差异"],"answer":"固定制造费用在存货中的处理差异","explanation":"吸收成本法将固定制造费用分摊入存货成本，边际成本法当期全费用化。利润差=存货变动×单位固定制造费用。"},
    {"type":"choice","points":2,"question":"IFRS 9 下债务工具按 AC 计量的条件是？","options":["管理层随意选择","通过SPPI测试且业务模式为收取合同现金流","活跃市场有报价","持有期限超过一年"],"answer":"通过SPPI测试且业务模式为收取合同现金流","explanation":"AC需两条件：①SPPI测试（仅本金+利息）；②业务模式=持有以收取（不打算出售）。"},

    {"type":"choice","points":2,"question":"优序融资理论下融资优先顺序是？","options":["债务→内源→股权","股权→内源→债务","内源→债务→股权","债务→股权→内源"],"answer":"内源→债务→股权","explanation":"基于信息不对称：内部资金→债务→外部股权。发行股票被认为是最差的信号（股价被高估）。"},
    {"type":"choice","points":2,"question":"职业道德五项原则中哪项要求「保持知识和技能在要求水平」？","options":["诚信","客观性","专业胜任与应有谨慎","保密"],"answer":"专业胜任与应有谨慎","explanation":"Competence and Due Care要求持续学习CPD，保持专业知识跟上发展，勤勉尽责。"},
    {"type":"choice","points":2,"question":"以下哪个不是 IFRS 15 五步法的步骤？","options":["识别与客户的合同","确定交易价格","评估客户信用风险","在履约义务完成时确认收入"],"answer":"评估客户信用风险","explanation":"信用风险评估属于IFRS9应收款减值范畴，不在IFRS15五步法内。"},
    {"type":"choice","points":2,"question":"平衡计分卡四个维度不包括？","options":["财务维度","客户维度","供应商维度","学习与成长维度"],"answer":"供应商维度","explanation":"BSC四维度：财务→客户→内部流程→学习与成长。供应商属于价值链分析范畴。"},
    {"type":"choice","points":2,"question":"可赎回债券 YTM 与不可赎回债券 YTM 的关系？","options":["可赎回YTM更高（补偿赎回风险）","不可赎回YTM更高","总是相等","与赎回条款无关"],"answer":"可赎回YTM更高（补偿赎回风险）","explanation":"赎回条款对发行人有利→投资者承担再投资风险→要求更高收益补偿→YTM更高。"},
    {"type":"choice","points":2,"question":"根据 IAS 37 哪项符合准备的确认条件？","options":["下年度预算维修费","很可能发生且金额可靠的质保赔偿","未来不确定的法律诉讼","尚未实施的未来重组计划"],"answer":"很可能发生且金额可靠的质保赔偿","explanation":"IAS37三条件：现时义务+很可能流出（>50%）+金额能可靠估计。质保赔偿同时满足。"},
    {"type":"tf","points":1,"question":"IFRS 16 允许承租人继续将大部分租赁分类为经营租赁。","options":[],"answer":"错误","explanation":"IFRS16取消了承租人经营租赁分类，除豁免外全部入表。"},
    {"type":"tf","points":1,"question":"吸收成本法下产量超过销量时利润高于边际成本法。","options":[],"answer":"正确","explanation":"产量>销量→存货增加→吸收成本法将固定制造费用「锁定」在存货中→利润更高。"},
    {"type":"tf","points":1,"question":"CAPM 中的 β 衡量的是非系统性风险。","options":[],"answer":"错误","explanation":"β衡量系统性风险（市场风险），不可通过分散化消除。非系统性风险不被CAPM定价。"},
    {"type":"tf","points":1,"question":"MM 有税模型下公司价值随债务增加而增加。","options":[],"answer":"正确","explanation":"MM有税：VL=VU+t×D。每增1元债务→公司价值增t元（税盾现值）。极端：100%债务最优。"},
    {"type":"tf","points":1,"question":"外部审计师的主要职责是防止公司舞弊。","options":[],"answer":"错误","explanation":"防止舞弊是管理层的责任。审计师只对因舞弊导致的重大错报进行检查（合理保证非绝对保证）。"},
    {"type":"tf","points":1,"question":"IFRS 禁止 LIFO，但允许 FIFO 和加权平均法。","options":[],"answer":"正确","explanation":"IAS2禁止LIFO。US GAAP仍允许。这是IFRS和US GAAP间的重要差异。"},
    {"type":"tf","points":1,"question":"替代品的可获得性降低了行业的整体利润率。","options":[],"answer":"正确","explanation":"替代品限制了行业定价能力。替代品威胁越高→行业利润率越低。"},
    {"type":"tf","points":1,"question":"ACCA 职业道德准则仅适用于审计师。","options":[],"answer":"错误","explanation":"五项原则适用所有专业会计师——无论公共执业（审计/咨询）还是企业（财务/管理会计）。"},
    {"type":"tf","points":1,"question":"短期决策中固定成本总是相关的。","options":[],"answer":"错误","explanation":"只有增量（相关）成本才需考虑。沉没成本和不受决策影响的固定成本是不相关的。"},
    {"type":"tf","points":1,"question":"IFRS 15 要求收入金额必须固定不可变。","options":[],"answer":"错误","explanation":"IFRS15包含可变对价处理——采用期望值法或最可能金额法估计，受「极可能不会重大转回」限制。"},
    {"type":"short","points":6,"question":"简述 IFRS 16 核心变化及对承租人财务报表的影响。","answer":"核心变化：取消承租人经营租赁与融资租赁区分→单一会计模型。除低值(<$5,000)和短期(≤12月)外全部入表确认使用权资产和租赁负债。旧IAS17问题：经营租赁表外融资。报表影响：资产负债表膨胀（D+E都增）、前期利润降低（折旧+利息>旧租金）、经营现金流改善、杠杆率上升、EBITDA改善。"},
    {"type":"short","points":6,"question":"解释 NPV vs IRR 的优缺点及为什么互斥项目下 NPV 优于 IRR。","answer":"NPV：直接量价值创造绝对值($)，正确再投资假设（以资本成本），互斥下选最大。需事先确定折现率。IRR：直觉好理解（%），不需事先折现率。但可能有多个IRR（非传统现金流）、互斥下可能排序错误（规模/期限差异）、再投资假设（IRR本身）不现实。互斥项目NPV优于IRR：NPV最大化股东财富（选最大绝对价值），IRR偏好高回报率小规模项目可能拒绝大规模略低回报但创更多价值项目。"},
    {"type":"short","points":6,"question":"解释 ACCA 审计中的重要性概念及应用。","answer":"重要性=可能影响使用者决策的错报阈值。计划阶段：确定整体重要性（利润5-10%或收入1-3%）和实际执行（整体50-75%）。执行阶段：分配到各账���（可容忍错报）、识别>明显微小阈值错报并汇总。报告阶段：汇总全部未更正错报评估整体是否重大→决定意见类型。定性因素：舞弊/影响盈亏趋势/违反监管/影响债务契约可能使金额不重要错报变重大。"},
    {"type":"short","points":6,"question":"比较 ACCA 和 CPA 知识体系的主要异同。","answer":"相同：精通财务报告、审计、财管、税法、职业道德。核心知识60-70%共通。不同：准则框架（ACCA=IFRS全球，CPA=中国准则）、税法差异（ACCA可选多国变体，CPA固定中国）、深度vs广度（CPA单科极深，ACCA面更广13门含战略/全球视野）、语言（ACCA全英文）、培训定位（ACCA面向全球商业会计，CPA是中国法定执业资格）。CPA转ACCA：补充IFRS差异、英文术语、国际法律框架、SBL战略综合分析能力。"},
    {"type":"essay","points":8,"question":"详细解释 ACCA 职业道德五项基本原则及实际工作中面临的威胁和防护措施。","answer":"五项原则：①诚信（坦诚诚实）。②客观性（不因偏见/利益冲突影响判断）。③专业胜任与应有谨慎（持续学习CPD、勤勉尽责）。④保密（不泄露未经授权信息、不用机密谋私利）。⑤职业行为（遵守法规、不损害职业声誉）。威胁类别：自身利益威胁、自我复核威胁、倡导威胁、密切关系威胁、胁迫威胁。防护：职业/法律/监管要求（外部）→事务所质量控制制度（内部）→个人拒绝/报告。"},
    {"type":"essay","points":8,"question":"IFRS 9 ECL 预期信用损失三阶段模型解释及为什么替代 IAS 39 已发生损失模型。","answer":"阶段1（信用良好）：确认12个月ECL，利息按总额计提。阶段2（显著恶化SICR）：确认整个存续期ECL，利息仍按总额。触发：逾期30+天、评级下调多档。阶段3（信用减值/违约）：确认整个存续期ECL，利息按净额计提。触发：逾期90+天、破产。改革原因：旧IAS39「已发生损失」需减值触发事件→2008危机中「太少、太晚」→银行在贷款已恶化时才计提→利润/资本被击穿。ECL是前瞻性的→持续评估信用变化→提前确认预期损失→避免悬崖效应。巴塞尔和IASB的共同改革方向。"},
    {"type":"essay","points":10,"question":"从战略管理角度分析传统零售企业在电商冲击下的战略选择。使用波特五力、SWOT和Ansoff矩阵。","answer":"五力：新进入者威胁高（电商低门槛）、替代品极高（线上替代线下）、买方议价上升（比价容易）、供应商议价（传统零售商规模仍占优）、竞争强度极高（价格战+体验战）。SWOT：S=品牌/门店网/供应链，W=高租金人工/数字化弱，O=O2O全渠道/社交电商/私域流量，T=电商价格压制/消费者习惯改变/新技术。Ansoff：市场渗透（优化门店体验+会员保持存量）、市场开发（低线城市）、产品开发（自有品牌+O2O服务）、多元化（社区团购+即时零售）。平衡：不能全关门（品牌展示+最后一公里物流节点），用线下利润养线上转型，设置数字化KPI而非仅短期利润考核，CEO亲自推动数字化。"},
    {"type":"comprehensive","points":20,"question":"综合题：XYZ是伦敦上市的跨国制造企业。(1)根据IFRS10阐述控制三要素并举例说明持股超50%也不能合并的情况(6分)。(2)欧元子公司折算为英镑遵循IAS21的哪些规则？区分货币/非货币、利润表/资产负债表项目的折算汇率及差额处理(7分)。(3)美元子公司2025/1/1签5年设备租赁(年租金$50万，借款利率6%)。PVIFA(6%,5)=4.2124。计算初始确认及对合并报表的影响(7分)。","answer":"(1)控制三要素：权力（指挥相关活动）、可变回报（回报随业绩变化）、权力影响回报的能力。三要素缺一不可。不能合并例子：深度价外期权（非实质性权利）、其他方拥有罢免权、仅有保护性权利（如否决清算）→需实质性权利。(2)IAS21：资产/负债=期末汇率（收盘汇率）。利润表=交易日/平均汇率。权益=历史汇率。折算差额→OCI→累积折算调整CTA（处置时回收至损益）。(3)租赁负债=500,000×4.2124=2,106,200。使用权资产同。第一年：利息126,372（进利润表），折旧421,240（进利润表）。资产/负债各增~2.1M→杠杆率上升，前期利润<旧租金，EBITDA改善，经营现金流改善。"},
]


# ══════════════════════════════════════════════════════
# CFA (already defined in existing script)
# ══════════════════════════════════════════════════════
# CFA knowledge and questions are already in CFA_KNOWLEDGE / CFA_QUESTIONS
# from the first run. We reuse them here.

# Import from the first generation
exec(open(os.path.join(os.path.dirname(__file__), 'generate_exampass.py'), encoding='utf-8').read().split("# ═══════════════════")[0])

print("Generating FRM...")
gen_exam('FRM', FRM_KNOWLEDGE, FRM_QUESTIONS, 50)

print("Generating CPA...")
gen_exam('CPA', CPA_KNOWLEDGE, CPA_QUESTIONS, 50)

print("Generating ACCA...")
gen_exam('ACCA', ACCA_KNOWLEDGE, ACCA_QUESTIONS, 45)

print('\n=== All exams generated ===')
print(f'Output: {OUT}')
for f in sorted(os.listdir(OUT)):
    size = os.path.getsize(os.path.join(OUT, f))
    print(f'  {f} ({size:,} bytes)')
