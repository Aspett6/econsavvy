import sys, os, json
sys.path.insert(0, r'C:\Users\wx\.claude\skills\exampass-assistant\scripts')
from template_engine import save_knowledge_html, save_test

OUT = r'D:\Desktop\智学财经_v5\exampass_output'
os.makedirs(OUT, exist_ok=True)

# ======================= FRM =======================
FRM_BODY = """
<h2>Part I：风险管理基础 <span class="tag-must">必考20%</span></h2>
<p><strong>核心问题</strong>：金融风险有哪些类型？如何度量？企业如何建立有效的风险管理框架？</p>
<h3>风险类型与度量</h3>
<p><span class="kp">市场风险</span><span class="exp">——利率、汇率、股价、商品价格波动导致的损失</span></p>
<p><span class="kp">信用风险</span><span class="exp">——交易对手违约或信用质量下降。预期损失 EL = PD x LGD x EAD</span></p>
<p><span class="kp">操作风险</span><span class="exp">——内部流程失败、人员、系统或外部事件。七类事件</span></p>
<p><span class="kp">流动性风险</span><span class="exp">——市场流动性（无法合理价格交易）和资金流动性（无法满足现金流）</span></p>
<h3>三道防线模型</h3>
<p>第一道：业务部门。第二道：风险管理和合规。第三道：内部审计。核心：责任分离和独立监督。</p>
<h3>CAPM与风险度量 <span class="tag-key">重点</span></h3>
<p>E(Ri) = Rf + beta_i x [E(Rm) - Rf]</p>
<p>夏普比率 = (Rp - Rf) / sigma_p。特雷诺比率 = (Rp - Rf) / beta_p。詹森alpha = Rp - [Rf+beta(Rm-Rf)]</p>
<h3>金融灾难案例 <span class="tag-freq">高频</span></h3>
<table><tr><th>事件</th><th>教训</th></tr>
<tr><td>巴林银行 1995</td><td>交易员权限失控、缺乏职责分离</td></tr>
<tr><td>LTCM 1998</td><td>高杠杆+流动性冻结=模型失效</td></tr>
<tr><td>次贷危机 2007-09</td><td>证券化链条过长、评级失误、系统性风险</td></tr></table>
<h2>Part I：定量分析 <span class="tag-must">必考20%</span></h2>
<p>GARCH(1,1)：sigma^2_t = omega + alpha.epsilon^2_{t-1} + beta.sigma^2_{t-1}。alpha+beta < 1 保证平稳。</p>
<h2>Part I：金融市场与产品 <span class="tag-must">必考30%</span></h2>
<p>无套利定价：F = S0 x e^(rT)。买卖权平价：C + Ke^(-rT) = P + S。</p>
<p>修正久期MD = MacD/(1+y)。凸性调整：DeltaP/P = -MD x Delta_y + 0.5 x C x (Delta_y)^2。</p>
<h2>Part I：估值与风险模型 <span class="tag-must">必考30%</span></h2>
<p>VaR：参数法 VaRa = -(mu + sigma.za)x sqrt(T)。ES = E[L | L > VaR]（满足次可加性，VaR不满足）。</p>
<p>莫顿模型：股权 = max(VT-F, 0)——公司资产的看涨期权。DD = [ln(V/F)+(mu-sigma^2/2)T]/(sigma.sqrt(T))。</p>
<p>B-S-M：C = S.N(d1) - K.e^(-rT).N(d2)。希腊字母：Delta/Gamma/Theta/Vega(Call和Put都为正)/Rho。</p>
<h2>Part II：市场/信用/操作/流动性风险</h2>
<p>VaR回测：绿区0-4，黄区5-9（资本乘数递增），红区>=10。</p>
<p>FRTB：ES替代VaR（97.5%），引入流动性期限。</p>
<p>CVA = (1-R) x sum(PV(EE) x PD)。DVA：自身违约风险调整。</p>
<p>SMA标准计量法替代AMA。操作风险七类事件。</p>
<p>LCR = HQLA/30天净流出 >= 100%。NSFR = ASF/RSF >= 100%。</p>
<h2>Part II：前沿话题（2025）</h2>
<p>生成式AI风控与伦理、加密资产MiCA监管、气候风险压力测试、SVB倒闭教训（利率风险->市场风险->流动性风险->48小时倒闭）。</p>
"""

FRM_Q = [
    {"type":"choice","points":2,"question":"预期损失 EL 的计算公式？","options":["EL = PD x LGD","EL = PD x EAD","EL = PD x LGD x EAD","EL = LGD x EAD"],"answer":"EL = PD x LGD x EAD","explanation":"三要素缺一不可：违约概率x违约损失率x违约敞口。"},
    {"type":"choice","points":2,"question":"以下哪项满足次可加性（一致风险度量）？","options":["VaR","预期短缺 ES","标准差","都满足"],"answer":"预期短缺 ES","explanation":"ES满足次可加性，VaR不满足。这是FRTB用ES替代VaR的核心原因。"},
    {"type":"choice","points":2,"question":"GARCH(1,1)中alpha+beta的经济含义？","options":["短期冲击程度","波动率的持续性","无条件方差","长期均值"],"answer":"波动率的持续性","explanation":"alpha+beta越接近1冲击越持久。alpha+beta<1保证方差平稳。"},
    {"type":"choice","points":2,"question":"买卖权平价公式（欧式无股利）？","options":["C+S=P+Ke^(-rT)","C+Ke^(-rT)=P+S","C=P+S-Ke^(-rT)","P+Ke^(-rT)=C-S"],"answer":"C+Ke^(-rT)=P+S","explanation":"组合A(Call+行权价折现)=组合B(Put+股票)。衍生品定价的基石等式。"},
    {"type":"choice","points":2,"question":"巴塞尔III的LCR最低要求？","options":["80%","90%","100%","120%"],"answer":"100%","explanation":"LCR=HQLA/30天净流出>=100%。银行须有足够优质流动性资产覆盖30天压力现金流。"},
    {"type":"choice","points":2,"question":"莫顿模型将股权视为公司资产的什么？","options":["远期合约","看涨期权","看跌期权","互换合约"],"answer":"看涨期权","explanation":"股权=max(VT-F,0)，行权价=债务面值。这是信用风险结构模型的核心洞察。"},
    {"type":"choice","points":2,"question":"以下哪项不属于操作风险？","options":["内部欺诈","系统宕机","利率变动导致交易损失","合规罚款"],"answer":"利率变动导致交易损失","explanation":"利率变动是市场风险。巴塞尔明确将市场风险和信用风险排除在操作风险之外。"},
    {"type":"choice","points":2,"question":"巴塞尔回测99%VaR 250天中多少次例外属黄灯区？","options":["0-4次","5-9次","10-19次","20次以上"],"answer":"5-9次","explanation":"绿区0-4(正常)，黄区5-9(乘数从3增至4)，红区>=10(重新审查)。预期=250x1%=2.5次。"},
    {"type":"choice","points":2,"question":"关于CVA正确的是？","options":["对手信用越好CVA越大","CVA代表对手违约风险的预期成本","CVA不影响公允价值","只适用场内产品"],"answer":"CVA代表对手违约风险的预期成本","explanation":"CVA=无风险价值-考虑对手风险价值。对手越差CVA越大。OTC衍生品最需要CVA。"},
    {"type":"choice","points":2,"question":"GARCH中alpha大而beta小说明什么？","options":["对冲击反应强但持续性低","波动率非常稳定","长期波动率高","模型不适用"],"answer":"对冲击反应强但持续性低","explanation":"alpha=新闻影响(大=反应快且剧烈)，beta=惯性(小=消退快)。"},
    {"type":"tf","points":1,"question":"VaR满足次可加性。","options":[],"answer":"错误","explanation":"VaR不一定满足次可加性。两个组合VaR之和可能小于合并VaR。ES满足。"},
    {"type":"tf","points":1,"question":"看涨和看跌期权的Vega都为正。","options":[],"answer":"正确","explanation":"波动率上升对期权买方有利(Call和Put都一样)。Vega衡量波动率敏感度。"},
    {"type":"tf","points":1,"question":"压力测试是替代VaR的日常风险度量工具。","options":[],"answer":"错误","explanation":"压力测试补充VaR非替代。VaR管正常条件，压力测试管极端情景。两者互补。"},
    {"type":"tf","points":1,"question":"莫顿模型DD越大违约概率越低。","options":[],"answer":"正确","explanation":"DD衡量资产距离违约点的标准化距离。DD越大资产越远离债务->违约越不可能。"},
    {"type":"tf","points":1,"question":"CDS买方承担参考实体的信用风险。","options":[],"answer":"错误","explanation":"买方转移风险出去！卖方（保护卖方）承担信用风险。买方定期付保费。"},
    {"type":"tf","points":1,"question":"ES总是大于或等于同置信水平的VaR。","options":[],"answer":"正确","explanation":"ES=E[L|L>VaR]是超过VaR的平均损失，自然>=VaR(阈值)。"},
    {"type":"tf","points":1,"question":"EWMA对历史数据给等权处理。","options":[],"answer":"错误","explanation":"EWMA对近期数据权重更高(指数衰减)。lambda越接近1权重衰减越慢(越接近等权)。"},
    {"type":"tf","points":1,"question":"巴塞尔III引入了净稳定资金比率NSFR。","options":[],"answer":"正确","explanation":"NSFR=ASF/RSF>=100%，关注1年期资金来源和运用的结构匹配。"},
    {"type":"tf","points":1,"question":"参数法VaR假设收益率服从正态分布。","options":[],"answer":"正确","explanation":"参数法(方差-协方差法)核心假设。使用正态分位数za计算VaR。"},
    {"type":"tf","points":1,"question":"AMA在巴塞尔III中被保留为操作风险主要方法。","options":[],"answer":"错误","explanation":"SMA已替代AMA。因AMA太复杂且各银行不可比。"},
    {"type":"short","points":6,"question":"简述VaR和ES的区别及FRTB为什么用ES替代VaR。","answer":"VaR是给定置信水平和持有期内最大可能损失的阈值。ES是超过VaR的损失的条件期望。ES满足次可加性(VaR不满足)、ES捕捉尾部严重程度、ES更不易被操纵。FRTB替换原因：VaR低估尾部风险，97.5%ES的稳定性约等于99%VaR但更稳健。"},
    {"type":"short","points":6,"question":"简述GARCH(1,1)公式及为何优于历史波动率。","answer":"sigma^2_t=omega+alpha.epsilon^2_{t-1}+beta.sigma^2_{t-1}。omega=长期方差，alpha=新闻影响，beta=惯性。优于历史波动率：波动率聚集(高波动后仍预测高)、均值回归、对冲击动态响应、适合短期预测。历史波动率假设波动恒定是最大问题。"},
    {"type":"short","points":6,"question":"解释莫顿模型逻辑及主要局限。","answer":"股权=max(VT-F,0)——看涨期权。VT>F股东还债留剩余；VT<F不行权给债权人。DD=[ln(V/F)+(mu-sigma^2/2)T]/(sigma.sqrt(T))。局限：假设连续路径(无跳跃)、仅到期日违约、资产价值不可观测、单一债务简化。"},
    {"type":"short","points":6,"question":"什么是三道防线模型？每道防线职责？","answer":"第一道：业务部门(风险「所有者」，日常管理识别报告)。第二道：风控和合规(独立监督，制定政策限额，监控全公司风险)。第三道：内部审计(独立评估前两道，向董事会保证)。核心：责任分离和独立监督。金融灾难源于防线失效。"},
    {"type":"essay","points":8,"question":"比较历史模拟法和蒙特卡洛法在VaR计算中的优缺点。","answer":"历史模拟：无需假设分布(非参数)、自动捕获相关性/厚尾/非线性、简单直观。局限：假设过去=未来、无法模拟未发生情景、对数据长度敏感。蒙特卡洛：可模拟任何分布(含跳跃/厚尾)、可模拟未发生情景、灵活处理复杂产品。局限：有模型风险、计算量大、依赖随机数质量。选择：历史模拟适用数据丰富市场稳定；蒙特卡洛适用新产品或需压力情景。"},
    {"type":"essay","points":8,"question":"解释CDS定价逻辑及CDS利差与债券利差的关系。","answer":"CDS买方定期付保费S，卖方在信用事件时赔付(1-RR)。CDS利差约=PDx(1-RR)。与债券利差应大致相等(否则基差套利)。基差=CDS利差-债券利差。正基差(CDS贵)：买债券+买CDS。负基差(CDS便宜)：买债券+卖CDS。实际基差不为零：融资成本、对手风险、流动性、交割期权。2008后负基差因银行融资成本上升成常态。"},
    {"type":"essay","points":10,"question":"从市场/流动性/利率风险三维度分析SVB倒闭原因及教训。","answer":"利率风险：资产端长期固收(久期长)，负债端短期活期——严重久期错配。利率升500+bp->债券市值跌约150亿超权益。市场风险：HTM会计掩盖未实现亏损(摊余成本不反映市价)。流动性风险：存款集中科技初创(几乎全超FDIC保额)->加息消耗现金->存款流出->被迫卖债确认亏损->恐慌->挤兑->48小时倒闭。教训：久期匹配是基本风控；HTM掩盖真实利率风险；存款集中度是流动性重要维度；压力测试须含利率大幅上升；社交媒体时代挤兑可在数小时内发生。"},
    {"type":"comprehensive","points":20,"question":"综合题：(1)描述银行整体风险管理框架(6分)。(2)银行持大量固收(久期8年)+短期存款，分析利率风险并推荐三种对冲(7分)。(3)解释LCR和NSFR，设计压力测试评估利率上升+存款流失时的流动性缓冲(7分)。","answer":"(1)治理：董事会->风险管理委员会->CRO->三道防线。RAS董事会批准。度量：市场=VaR+ES+压力，信用=PD/LGD/EAD+RWA，操作=损失数据+KRI。限额：VaR/DV01/集中度/流动性。月风险委员会审议。(2)DA=8,DL约0，正久期缺口。利率升100bp->资产跌约8%。对冲：卖国债期货缩短久期/付固定收浮动IRS/买利率cap。(3)LCR=HQLA/30天净流出>=100%。NSFR=ASF/RSF>=100%。压力测试：利率再升200bp+存款30%流失+银行间冻结。测算HQLA和NSFR是否仍达标。不达标->启动CFP应急融资。"},
]

save_knowledge_html(FRM_BODY, os.path.join(OUT, 'FRM_知识清单.html'), 'FRM · 知识清单')
save_test(FRM_Q, os.path.join(OUT, 'FRM_章节测试.html'), 'FRM · 章节测试', '2025考纲 · 28题100分 · 50分钟', 50)
print('FRM done')

# ======================= CPA =======================
CPA_BODY = """
<h2>科目一：会计 <span class="tag-must">必考（CPA最核心）</span></h2>
<h3>收入确认五步法 <span class="tag-key">重点</span></h3>
<p>1.识别合同 2.识别履约义务 3.确定交易价格 4.分摊价格 5.确认收入（时点vs时段）</p>
<h3>长期股权投资 <span class="tag-must">必考</span></h3>
<table><tr><th>持股</th><th>方法</th><th>要点</th></tr>
<tr><td>>50%（控制）</td><td>成本法</td><td>需编合并报表。宣告股利确认收益</td></tr>
<tr><td>20-50%（重大影响）</td><td>权益法</td><td>按份额确认净利润，股利冲减账面</td></tr>
<tr><td><20%</td><td>金融资产</td><td>按CAS22分类</td></tr></table>
<p>同一控制合并->账面价值法（无商誉，差额调资本公积）。非同一控制->购买法（产生商誉=合并成本-可辨认净资产公允份额）。</p>
<h3>存货与固定资产</h3>
<p>FIFO、移动加权平均、月末一次加权平均、个别计价。LIFO已被禁止。存货减值可转回，固定资产/无形资产/商誉减值不可转回。</p>
<h3>研发支出</h3>
<p>研究阶段全费用化。开发阶段符合五条件可资本化：技术可行、意图完成、预期经济利益、资源充足、支出可靠计量。</p>
<h3>递延所得税 <span class="tag-key">重点</span></h3>
<p>DTA可抵扣暂时性差异（预付税款），DTL应纳税暂时性差异（未来多缴）。税率变化在变化当期确认。</p>
<h2>科目二：审计 <span class="tag-key">重点</span></h2>
<p>AR=IRxCRxDR。RMM=IRxCR（审计师不可控）。重要性：整体=利润5-10%，实际执行=整体50-75%。意见类型：保留（重大不广泛）、否定（重大且广泛）、无法表示（范围受限且广泛）。</p>
<h2>科目三：财务成本管理</h2>
<p>WACC=E/(D+E)Re + D/(D+E)Rd(1-t)。CAPM：Re=Rf+beta(Rm-Rf)。NPV=sum(CFt/(1+r)^t)-I0。</p>
<p>DOL=边际贡献/EBIT。DFL=EBIT/(EBIT-利息)。DTL=DOLxDFL。</p>
<p>杜邦：ROE=净利率x资产周转率x权益乘数。EOQ=sqrt(2KD/Kc)。</p>
<h2>科目四：税法 <span class="tag-freq">高频</span></h2>
<p>增值税：13%/9%/6%/0%。一般计税=销项-进项。简易计税=含税销售额/(1+征收率)x征收率。</p>
<p>企业所得税：25%/15%/20%。研发加计100%（形成无形资产200%摊销）。业务招待费min(发生额60%,收入5permil)。广宣费收入15%。</p>
<p>个税：综合所得3-45%七级。基本减除6万/年+7项专项附加扣除。</p>
<h2>科目五：经济法</h2>
<p>公司法2024新修订：注册资本5年内缴足。合同法：要约+承诺=成立。保证：一般vs连带。</p>
<h2>科目六：公司战略</h2>
<p>波特五力。三大通用战略：成本领先/差异化/集中化。SWOT。风险应对：回避/降低/转移/承担。</p>
"""

CPA_Q = [
    {"type":"choice","points":2,"question":"同一控制下企业合并使用什么方法？","options":["购买法（公允价值）","账面价值法","权益法","成本法"],"answer":"账面价值法","explanation":"同一控制视为内部资源整合，按账面价值入账，不产生商誉。差额调资本公积。"},
    {"type":"choice","points":2,"question":"审计师唯一可控的风险因子是？","options":["固有风险IR","控制风险CR","检查风险DR","重大错报风险RMM"],"answer":"检查风险DR","explanation":"IR和CR是被审计单位自身的，只能评估不能改变。DR可通过改进审计程序降低。"},
    {"type":"choice","points":2,"question":"「重大但不广泛」错报对应什么审计意见？","options":["无保留意见","保留意见","否定意见","无法表示意见"],"answer":"保留意见","explanation":"重大+不广泛=保留。重大+广泛=否定。范围受限同理。"},
    {"type":"choice","points":2,"question":"研究阶段支出应如何处理？","options":["资本化","全部费用化","符合条件的资本化","成功时一次性资本化"],"answer":"全部费用化","explanation":"研究阶段探索性工作全费用化。开发阶段符合五条件才可资本化。"},
    {"type":"choice","points":2,"question":"存货跌价准备的处理正确的是？","options":["不得转回","可以转回但不超过已计提金额","只能转回50%","不允许计提"],"answer":"可以转回但不超过已计提金额","explanation":"存货减值可转回(与固定资产不同)。长期资产减值不可转回。"},
    {"type":"choice","points":2,"question":"杜邦分析中ROE从12%升到18%但净利率从8%降到6%，最可能的解释？","options":["盈利提升","财务杠杆大增","周转率大升","股票回购"],"answer":"财务杠杆大增","explanation":"净利率降排除盈利提升。ROE=净利率x周转率x权益乘数，净利率降但ROE升->权益乘数必增。"},
    {"type":"choice","points":2,"question":"增值税一般计税应纳税额公式？","options":["销售额x税率","销项税额-进项税额","(销售额-成本)x税率","含税销售额/(1+税率)x税率"],"answer":"销项税额-进项税额","explanation":"一般计税=销项-进项(抵扣制)。简易计税不能抵扣进项。"},
    {"type":"choice","points":2,"question":"研发费用加计扣除的比例？","options":["50%","75%","100%","200%"],"answer":"100%","explanation":"2023年起一般企业研发费用据实扣除基础上加计100%(总共200%)。形成无形资产200%摊销。"},
    {"type":"choice","points":2,"question":"波特五力中不属于五力之一的是？","options":["新进入者威胁","供应商议价能力","政府监管力度","替代品威胁"],"answer":"政府监管力度","explanation":"政府监管属PESTEL政治/法律因素，不在五力范畴。五力是行业竞争层面的分析。"},
    {"type":"choice","points":2,"question":"合同法中正确的是？","options":["要约一旦发出就不可撤销","承诺可进行实质性修改","承诺到达要约人时合同成立","要约邀请等同要约"],"answer":"承诺到达要约人时合同成立","explanation":"合同成立=要约+承诺。承诺须完全接受要约(不得实质性修改)。要约邀请(广告)非要约。"},
    {"type":"tf","points":1,"question":"同一控制下企业合并产生商誉。","options":[],"answer":"错误","explanation":"同一控制使用账面价值法不产生商誉。只有非同一控制购买法才可能产生商誉。"},
    {"type":"tf","points":1,"question":"固定资产减值损失一经确认不得转回。","options":[],"answer":"正确","explanation":"长期资产(固定资产/无形资产/商誉)减值不可转回。但存货、应收款减值可转回。"},
    {"type":"tf","points":1,"question":"DOL越大说明固定成本占比越小。","options":[],"answer":"错误","explanation":"DOL越大固定成本占比越大。DOL=边际贡献/EBIT，固定成本大->EBIT小->DOL大。"},
    {"type":"tf","points":1,"question":"中国个税综合所得适用3%-45%七级超额累进税率。","options":[],"answer":"正确","explanation":"综合所得(工资+劳务+稿酬x70%+特许权)七级。经营所得五级5-35%。"},
    {"type":"tf","points":1,"question":"NPV>0时IRR一定大于必要报酬率。","options":[],"answer":"正确","explanation":"常规现金流下NPV和IRR一致。NPV>0等价于IRR>r。"},
    {"type":"tf","points":1,"question":"现金流量表间接法以净利润为起点调整。","options":[],"answer":"正确","explanation":"间接法：CFO=净利润+折旧摊销±营运资本变动±其他非现金项目。"},
    {"type":"tf","points":1,"question":"开发阶段所有支出都可以资本化。","options":[],"answer":"错误","explanation":"只有同时满足五个条件的开发支出才可资本化。不满足的仍需费用化。"},
    {"type":"tf","points":1,"question":"公司股东对公司债务承担有限责任。","options":[],"answer":"正确","explanation":"有限责任是公司区别于合伙企业的核心特征。股东限于出资额。"},
    {"type":"tf","points":1,"question":"成本领先战略等同于低质量。","options":[],"answer":"错误","explanation":"成本领先≠低质量。通过规模经济/高效运营降成本同时保持可接受质量(如宜家/沃尔玛)。"},
    {"type":"tf","points":1,"question":"否定意见意味着财务报表完全不真实。","options":[],"answer":"错误","explanation":"否定意见表示存在重大且广泛错报但不意味完全错误。审计师不做如此绝对表述。"},
    {"type":"short","points":6,"question":"简述成本法和权益法的适用及核算差异。","answer":"成本法(控制>50%)：按成本入账，被投资方宣告股利时确认投资收益，净利润不调投资账面。权益法(重大影响20-50%)：按成本入账，按份额确认被投资方净利润/亏损(调投资账面)，收到股利冲减投资账面。权益法更真实反映经济实质。"},
    {"type":"short","points":6,"question":"什么是审计重要性？如何确定？","answer":"重要性=可能影响财务报表使用者决策的错报阈值。整体重要性通常为利润5-10%或收入1-3%。实际执行=整体50-75%(用于设计程序)。明显微小=整体3-5%(可不累计)。定性因素：舞弊/影响盈亏趋势/违反监管的错报即使金额小也可能重大。"},
    {"type":"short","points":6,"question":"WACC各参数如何确定？为何用目标资本结构？","answer":"Re：CAPM(Rf+beta(Rm-Rf))、股利增长模型(D1/P0+g)。Rd：债券YTM或贷款利率，需税后Rdx(1-t)。权重：用市值(非账面)。用目标资本结构因：估值面向未来、当前结构可能临时偏离、目标结构使WACC稳定可预测。"},
    {"type":"short","points":6,"question":"简述增值税「视同销售」情形及税务处理目的。","answer":"情形：代销、跨县市移送、自产/委托加工用于非应税/集体福利/个人消费、投资/分配/赠送、无偿提供服务/转让无形资产。目的：保持增值税抵扣链条完整(货物离开链条需补税)、确保税收中性(自产和外购税务待遇一致)。"},
    {"type":"essay","points":8,"question":"比较同一控制和非同一控制企业合并的会计处理差异。","answer":"同一控制：按被合并方净资产账面价值入账，合并对价与账面差额调资本公积(不足冲减调留存收益)，不产生商誉。非同一控制(购买法)：按公允价值计量，产生商誉=合并成本-可辨认净资产公允份额。同一控制=内部资源整合不应产生新商誉；非同一控制=市场交易反映公允价值。"},
    {"type":"essay","points":8,"question":"解释审计意见类型的决策框架并举例。","answer":"两维度：重大性+广泛性。存在错报且不重大->无保留；重大但不广泛->保留；重大且广泛->否定。范围受限且不重大->无保留；可能但不广泛->保留；可能且广泛->无法表示。举例：应收款减值未计提(重大但不广泛)->保留意见。持续经营不确定性未披露且多科目影响->否定意见。"},
    {"type":"essay","points":10,"question":"比较企业所得税和个人所得税差异及个税改革理由。","answer":"企税：税基=收入-不征税-免税-扣除-补亏。税率25%/15%/20%。扣除有限额(招待费60%/5permil)。个税：综合所得=年收入-6万-专项扣除-7项附加扣除。税率3-45%七级。改革理由：公平性(同收入同税负)、反避税(堵劳务工资分开漏洞)、国际趋势(OECD综合制)、附加扣除(按家庭负担差异化)。保留分类征收(利息/股息)体现鼓励投资导向。"},
    {"type":"comprehensive","points":20,"question":"综合题：甲公司拟收购乙公司。(1)此前持10%(权益法)，收购后达90%(控制)。描述处理。合并成本900万，可辨认净资产公允1000万，计算商誉(6分)。(2)乙公司净利润200万，股利80万。个别和合并处理(7分)。(3)年末乙可收回金额900万，账面1050万(含商誉120万)。计算商誉减值(7分)。","answer":"(1)分步交易非同一控制合并。合并成本=原10%公允+新增80%对价=900万。可辨认份额=1000x90%=900万。商誉=0。原10%账面与公允之差计投资收益。(2)个别(成本法)：不确认乙净利润200万。股利：借应收72万(80x90%)贷投资收益72万。合并：全额合并净利润200万，少数股东损益20万(10%)。股利抵销。(3)减值=1050-900=150万。先冲商誉120万->0。剩下30万分摊到资产组其他资产。合并确认减值损失150万。"},
]

save_knowledge_html(CPA_BODY, os.path.join(OUT, 'CPA_知识清单.html'), 'CPA · 知识清单')
save_test(CPA_Q, os.path.join(OUT, 'CPA_章节测试.html'), 'CPA · 章节测试', '2025考纲 · 28题100分 · 50分钟', 50)
print('CPA done')

# ======================= ACCA =======================
ACCA_BODY = """
<h2>应用知识阶段 Applied Knowledge</h2>
<h3>BT 商业与技术</h3>
<p>PESTEL、波特五力、组织架构（职能/事业部/矩阵/扁平）、激励理论（马斯洛需求层次/赫茨伯格双因素）、团队发展（Tuckman形成->震荡->规范->执行->解散）、职业道德五项原则（诚信/客观/专业胜任与应有谨慎/保密/职业行为）。</p>
<h3>MA 管理会计 <span class="tag-key">重点</span></h3>
<p>成本分类（固定/变动/半变动）。吸收成本法vs边际成本法（利润差异=存货变动x单位固定OH）。盈亏平衡BEP=FC/(P-VC)。CVP分析。ABC作业成本法。差异分析。ROI和剩余收益RI。</p>
<h3>FA 财务会计</h3>
<p>会计恒等式、复式记账DEAD CLIC(Debit增加Expenses/Assets/Drawings，Credit增加Liabilities/Income/Capital)、三大报表、财务比率分析。</p>
<h2>应用技能阶段 Applied Skills</h2>
<h3>FR 财务报告 <span class="tag-must">必考</span></h3>
<p>IFRS核心准则：IAS16 PPE、IAS36减值（可收回金额=max(公允-处置,使用价值)）、IAS37准备（现时义务+很可能>50%+可靠估计）、IAS38无形资产、IFRS9金融工具（AC/FVOCI/FVTPL+ECL三阶段模型）、IFRS15收入五步法、IFRS16租赁（单一模型全入表，豁免低值<5000和短期<=12月）、IFRS3合并（购买法+商誉）、IFRS10控制三要素、IAS28联营权益法。</p>
<h3>FM 财务管理 <span class="tag-key">重点</span></h3>
<p>NPV=sum(CFt/(1+r)^t)-I0。WACC=E/(D+E)Re+D/(D+E)Rd(1-t)。CAPM：Re=Rf+beta(Rm-Rf)。GGM：P0=D1/(r-g)。EOQ=sqrt(2C0D/Ch)。资本结构（MM/权衡/优序：内源->债务->股权）。外汇风险（交易/折算/经济）。</p>
<h3>AA 审计</h3>
<p>AR=IRxCRxDR。重要性（利润5-10%）。内控五要素。审计证据充分性和适当性。审计意见类型。</p>
<h2>战略专业阶段 Strategic Professional</h2>
<h3>SBL & SBR</h3>
<p>SBL：综合案例（治理/战略/风险/科技/财务/变革管理）。SBR：复杂IFRS应用（合并/金融工具/外币折算/ESG可持续发展报告/IFRS18新准则）。2025考纲变化：IFRS18替代IAS1、SBR新增ESG披露、LW新增公司欺诈犯罪行为。</p>
"""

ACCA_Q = [
    {"type":"choice","points":2,"question":"IFRS16承租人对大多数租赁的处理？","options":["全部费用化","确认使用权资产和租赁负债入表","仅附注披露","与IAS17处理一致"],"answer":"确认使用权资产和租赁负债入表","explanation":"IFRS16取消经营租赁分类->单一模型。除低值(<5000)和短期(<=12月)外全部入表。"},
    {"type":"choice","points":2,"question":"Tuckman团队发展模型的正确顺序？","options":["执行->规范->震荡->形成","形成->震荡->规范->执行->解散","形成->规范->震荡->执行","规范->形成->执行->解散"],"answer":"形成->震荡->规范->执行->解散","explanation":"Forming->Storming->Norming->Performing->Adjourning。震荡不可跳过。"},
    {"type":"choice","points":2,"question":"吸收成本法与边际成本法利润差异的根本原因？","options":["销售数量变化","固定制造费用在存货中处理差异","直接材料核算差异","管理费用分配差异"],"answer":"固定制造费用在存货中处理差异","explanation":"吸收法将固定OH分摊入存货(存货含固定成本)，边际法全费用化。利润差=存货变动x单位固定OH。"},
    {"type":"choice","points":2,"question":"IFRS9债务工具按AC计量的条件是？","options":["管理层随意选择","通过SPPI测试且业务模式为收取现金流","活跃市场有报价","持有超过一年"],"answer":"通过SPPI测试且业务模式为收取现金流","explanation":"AC需两条件：1)SPPI测试(仅本金+利息)；2)业务模式=持有以收取(不打算出售)。"},  {"type":"choice","points":2,"question":"优序融资理论的融资优先顺序？","options":["债务->内源->股权","股权->内源->债务","内源->债务->股权","债务->股权->内源"],"answer":"内源->债务->股权","explanation":"基于信息不对称：内部资金->债务->外部股权。发行股票被认最差信号(传递股价被高估)。"},
    {"type":"choice","points":2,"question":"职业道德中要求保持知识和技能的是？","options":["诚信","客观性","专业胜任与应有谨慎","保密"],"answer":"专业胜任与应有谨慎","explanation":"Competence and Due Care要求持续CPD，保持专业知识跟上发展，勤勉尽责。"},
    {"type":"choice","points":2,"question":"以下哪个不是IFRS15五步法的步骤？","options":["识别合同","确定交易价格","评估客户信用风险","在履约义务完成时确认收入"],"answer":"评估客户信用风险","explanation":"信用风险评估属IFRS9应收款减值范畴，不在IFRS15五步法内。"},
    {"type":"choice","points":2,"question":"BSC四个维度不包括？","options":["财务维度","客户维度","供应商维度","学习与成长维度"],"answer":"供应商维度","explanation":"BSC四维：财务->客户->内部流程->学习与成长。供应商属价值链分析范畴。"},
    {"type":"choice","points":2,"question":"可赎回债券vs不可赎回债券的YTM？","options":["可赎回更高","不可赎回更高","总是相等","无关"],"answer":"可赎回更高","explanation":"赎回条款对发行人有利->投资者承担再投资风险->要求更高收益补偿。"},
    {"type":"choice","points":2,"question":"根据IAS37哪项符合准备确认条件？","options":["下年度预算维修费","很可能且金额可靠的质保赔偿","不确定的法律诉讼","未实施的未来重组"],"answer":"很可能且金额可靠的质保赔偿","explanation":"IAS37三条件：现时义务+很可能流出(>50%)+金额能可靠估计。质保赔偿同时满足。"},
    {"type":"tf","points":1,"question":"IFRS16允许承租人继续将大部分租赁分类为经营租赁。","options":[],"answer":"错误","explanation":"IFRS16取消经营租赁分类。除豁免外全部入表。"},
    {"type":"tf","points":1,"question":"产量超过销量时吸收成本法利润高于边际成本法。","options":[],"answer":"正确","explanation":"存货增加->吸收法将固定OH锁在存货中->当期费用少->利润高。"},
    {"type":"tf","points":1,"question":"CAPM中的beta衡量非系统性风险。","options":[],"answer":"错误","explanation":"beta衡量系统性风险(市场风险)。非系统性风险在CAPM中不获补偿。"},
    {"type":"tf","points":1,"question":"MM有税模型下公司价值随债务增加而增加。","options":[],"answer":"正确","explanation":"VL=VU+txD。每增1元债务公司价值增t元(税盾现值)。"},
    {"type":"tf","points":1,"question":"外部审计师的主要职责是防止公司舞弊。","options":[],"answer":"错误","explanation":"防止舞弊是管理层责任。审计师只对因舞弊导致重大错报做合理保证检查。"},
    {"type":"tf","points":1,"question":"IFRS禁止LIFO，允许FIFO和加权平均法。","options":[],"answer":"正确","explanation":"IAS2禁止LIFO。US GAAP仍允许。这是IFRS与US GAAP重要差异。"},
    {"type":"tf","points":1,"question":"替代品的可获得性降低了行业利润率。","options":[],"answer":"正确","explanation":"替代品限制行业定价能力。替代品威胁越高利润率越低。"},
    {"type":"tf","points":1,"question":"ACCA职业道德准则仅适用审计师。","options":[],"answer":"错误","explanation":"五项原则适用所有专业会计师——无论公共执业还是企业。"},
    {"type":"tf","points":1,"question":"短期决策中固定成本总是相关的。","options":[],"answer":"错误","explanation":"只有增量(相关)成本才需考虑。沉没成本总是不相关。"},
    {"type":"tf","points":1,"question":"IFRS15要求收入金额必须固定不可变。","options":[],"answer":"错误","explanation":"IFRS15包含可变对价——用期望值法或最可能金额法估计，受不会重大转回限制。"},
    {"type":"short","points":6,"question":"简述IFRS16核心变化及对承租人财务报表影响。","answer":"核心变化：取消经营租赁->单一模型。除低值(<5000)和短期(<=12月)外全部入表确认使用权资产+租赁负债。影响：资产负债膨胀(D+E均增)、前期利润降低(折旧+利息>旧租金)、经营现金流改善(租金从经营转筹资)、杠杆率上升、EBITDA改善。"},
    {"type":"short","points":6,"question":"解释NPV vs IRR的优缺点及互斥下NPV为何优于IRR。","answer":"NPV：直接量价值创造绝对值($)，正确再投资假设(资本成本)。需事先确定r。IRR：直觉好(%)，不需事先r。但可能多IRR(非传统现金流)、互斥下可能排错序(规模/期限差异)、再投资假设不现实(假设=IRR本身)。互斥：NPV最大化股东财富(选最大$)，IRR偏好高%小规模可能拒大规模略低%但创更多$项目。"},
    {"type":"short","points":6,"question":"解释审计重要性概念及应用。","answer":"重要性=可能影响使用者决策的错报阈值。计划阶段：整体=利润5-10%或收入1-3%，实际执行=整体50-75%。执行阶段：分配至账户、识别>明显微小错报并汇总。报告阶段：汇总未更正错报评估是否重大->决定意见类型。定性因素：舞弊/影响盈亏趋势/违反监管。"},
    {"type":"short","points":6,"question":"比较ACCA和CPA知识体系异同。","answer":"相同：财务报告、审计、财管、税法、职业道德，核心60-70%共通。不同：准则(ACCA=IFRS全球，CPA=中国CAS)、税法(ACCA可选多国，CPA固定中国)、深vs广(CPA单科极深，ACCA面广13门含战略/全球视野)、语言(ACCA英文)、定位(ACCA全球商业会计，CPA中国法定执业)。CPA转ACCA：补IFRS差异+英文术语+国际法+SBL综合分析。"},
    {"type":"essay","points":8,"question":"解释ACCA职业道德五项原则及威胁防护。","answer":"五项：①诚信(坦诚诚实)。②客观性(不因偏见/利益冲突影响判断)。③专业胜任与应有谨慎(持续CPD、勤勉尽责)。④保密(不泄露机密信息、不用机密谋私利)。⑤职业行为(遵守法规、不损职业声誉)。威胁类别：自身利益、自我复核、倡导、密切关系、胁迫。防护：职业/法律/监管->事务所质量控制->个人拒绝/报告。层层递进。"},
    {"type":"essay","points":8,"question":"解释IFRS9 ECL预期信用损失三阶段模型及改革原因。","answer":"阶段1(信用良好)：12个月ECL，利息按总额。阶段2(显著恶化SICR)：整个存续期ECL，利息仍按总额。触发：逾期30+天/评级下调。阶段3(信用减值/违约)：整个存续期ECL，利息按净额。触发：逾期90+天/破产。改革：旧IAS39已发生损失需触发事件->2008危机中太少太晚->银行在贷款已恶化时才计提。ECL前瞻性->持续评估信用变化->提前确认预期损失->避免悬崖效应。巴塞尔和IASB共同改革方向。"},
    {"type":"essay","points":10,"question":"从战略管理角度分析传统零售企业在电商冲击下的战略选择。使用五力+SWOT+Ansoff。","answer":"五力：新进入者威胁高(电商低门槛)、替代品极高(线上替代线下)、买方议价升(比价容易转换成本低)、竞争强度极高。SWOT：S=品牌/门店/供应链，W=高租金人工/数字化弱，O=O2O全渠道/社交电商/私域流量，T=电商价格压制/消费者习惯变/新技术。Ansoff：市场渗透(优化门店+会员)、市场开发(低线城市)、产品开发(自有品牌+O2O)、多元化(社区团购+即时零售)。平衡：不能全关店(品牌展示+最后一公里物流)+线下利润养线上转型+设数字化KPI+CEO亲自推数字化。"},
    {"type":"comprehensive","points":20,"question":"XYZ是伦敦上市跨国制造企业。(1)根据IFRS10阐述控制三要素并举例持股超50%也不能合并的情况(6分)。(2)欧元子公司折算为英镑遵循IAS21哪些规则(7分)。(3)美元子公司签5年设备租赁(年租$50万利率6%)，PVIFA(6%,5)=4.2124。计算初始确认及对合并影响(7分)。","answer":"(1)控制三要素：权力(指挥相关活动)、可变回报(回报随业绩变)、权力影响回报能力。三缺一不可。不能合并：深度价外期权(非实质性)、其他方有罢免权、仅有保护性权利(如否决清算)->需实质性权利才能控制。(2)IAS21：资产/负债=期末汇率。利润表=交易日或平均汇率。权益=历史汇率。折算差额->OCI->累积折算调整CTA(处置子公司时回收至损益)。(3)租赁负债=500000x4.2124=2106200。使用权资产同。第一年：利息126372(进利润)，折旧421240(进利润)。资产+负债各增约2.1M->杠杆率上升+前期利润<旧租金+EBITDA改善+经营现金流改善。"},
]

save_knowledge_html(ACCA_BODY, os.path.join(OUT, 'ACCA_知识清单.html'), 'ACCA · 知识清单')
save_test(ACCA_Q, os.path.join(OUT, 'ACCA_章节测试.html'), 'ACCA · 章节测试', '2025考纲 · 28题100分 · 45分钟', 45)
print('ACCA done')

print()
print('=== All 3 exams generated ===')
for f in sorted(os.listdir(OUT)):
    size = os.path.getsize(os.path.join(OUT, f))
    print(f'  {f} ({size:,} bytes)')
