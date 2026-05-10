# 湘小策·顾问输出模板库

> **用途**：湘小策Skill的标准化输出模板，供顾问响应时直接调用或参考
> **版本**：1.0.0（2026-04-10）
> **路径**：`C:\Users\58460\.workbuddy\skills\湘小策\references\advisor_templates.md`

---

## 模板一：战略方向顾问 (strategy)

### 适用场景清单
- 研究框架/Issue Tree搭建与验证
- 核心论点/结论方向确定
- 分析视角选择（如：产业视角 vs 区域视角 vs 企业视角）
- 报告结构主线确定
- 优先级排序

### 输出模板

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_RESPONSE",
  "advisor_type": "strategy",
  "query_ref": "[引用原始咨询问题]",
  "confidence": "high|medium|low",
  "advice_items": [
    {
      "id": 1,
      "suggestion": "①以[核心主线]为主线",
      "rationale": "[理由，≤30字]",
      "priority": "high"
    },
    {
      "id": 2,
      "suggestion": "②补充[缺失维度]",
      "rationale": "[理由]",
      "priority": "medium"
    },
    {
      "id": 3,
      "suggestion": "③[可弱化部分]可以压缩",
      "rationale": "[理由]",
      "priority": "low"
    }
  ],
  "warning_if_ignored": "若忽略第①项，可能导致[具体风险]",
  "token_count_estimate": "~450",
  "timestamp": "ISO8601"
}
```

### 典型示例

**示例A — 研究框架咨询**
```
Query: "张家界十五五规划应该以什么为主线？文旅融合还是产业多元化？"
Context: 张家界旅游集团2024年亏损5.18亿但营收增30%，门票经济模式难以为继
```

**建议输出**：
```json
{
  "advisor_type": "strategy",
  "confidence": "high",
  "advice_items": [
    {"id":1, "suggestion":"①以'文旅深度融合+数字化转型'双主线", "rationale":"单一文旅已见顶，数字化是新增长极", "priority":"high"},
    {"id":2, "suggestion":"②增加低空经济赛道作为第三曲线", "rationale":"湖南全省战略+张家界地形优势匹配", "priority":"medium"},
    {"id":3, "suggestion":"③'产业多元化'概念过宽需收窄", "rationale":"资源有限应聚焦而非铺开", "priority":"medium"},
    {"id":4, "suggestion":"④历史回顾压缩至0.5页内", "rationale":"决策者更关心未来5年", "priority":"low"}
  ],
  "warning_if_ignored": "若忽略①②，报告可能被认为缺乏前瞻性和省级站位"
}
```

---

## 模板二：方法论顾问 (methodology)

### 适用场景清单
- 分析方法/框架选择
- 数据源充分性判断与取舍
- 论证逻辑链条设计
- 定量vs定性方法配比
- 对标对象选择

### 输出模板

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_RESPONSE",
  "advisor_type": "methodology",
  "query_ref": "[引用原始咨询问题]",
  "confidence": "high|medium|low",
  "advice_items": [
    {"id": 1, "suggestion": "推荐[方法A]+[方法B]交叉验证", "rationale": "[理由]", "priority": "high"},
    {"id": 2, "suggestion": "数据源优先级: [排序]", "rationale": "[理由]", "priority": "medium"},
    {"id": 3, "suggestion": "量化指标至少保留[N]个关键项", "rationale": "[理由]", "priority": "medium"}
  ],
  "warning_if_ignored": "若忽略，可能影响论证力度或数据可信度",
  "token_count_estimate": "~400"
}
```

### 典型示例

**示例B — 方法选择咨询**
```
Query: "分析湖南省算力产业的竞争格局，用波特五力还是SWOT？"
Context: 需要为省发改委提交一份产业研究报告，关注湖南在全国的定位
```

**建议输出**：
```json
{
  "advisor_type": "methodology",
  "confidence": "high",
  "advice_items": [
    {"id":1, "suggestion":"①主框架用PEST(宏观)+产业链图谱(中观)", "rationale":"五力和SWOT偏静态，政策研究需要动态视角", "priority":"high"},
    {"id":2, "suggestion":"②对标省市选长三角(浙江/安徽)和西部(贵州)", "rationale":"前者领先有借鉴价值后者同属后发有参照", "priority":"high"},
    {"id":3, "suggestion":"③量化部分必须含:机架规模/PUE/利用率/电价", "rationale":"四项是算力核心竞争力硬指标", "priority":"medium"}
  ],
  "warning_if_ignored": "若只用SWOT/五力，可能被评审认为方法论陈旧"
}
```

---

## 模板三：国资语境顾问 (soe_context)

### 适用场景清单
- 措辞合规检查（七律预检）
- 汇报语气/语体适配
- 敏感表述识别
- 责任主体确认
- 政策引用规范性

### 内置知识：陈满七律速查表

| 七律 | 关键规则 | 违规典型 | 正确写法 |
|------|---------|---------|---------|
| ①主体归位律 | 主语=上级机构 | "我们建议" | "可探索"/"宜" |
| ②降调去锋律 | "必须"→"探索" | "必须加大投入" | "宜持续加大投入" |
| ③数字克制律 | 数字加限定词 | "增长50%" | "预计增长约50%" |
| ④合规前置律 | 敏感措施附说明 | 直接提跟投 | 提及后附三重一大程序 |
| ⑤政策品牌律 | 引用已有品牌 | 自创"湘江模式" | 引用已有"芙蓉计划"等 |
| ⑥四要素律 | 措施四要素完整 | "加强人才培养" | "依托XX载体每年培养XX人(资金来源)" |
| ⑦系统导向律 | 现状分析前置 | 直接给举措 | 先分析现状再提措施 |

### 输出模板

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_RESPONSE",
  "advisor_type": "soe_context",
  "query_ref": "[引用原始咨询问题]",
  "confidence": "high|medium|low",
  "seven_laws_check": {
    "violations_found": N,
    "details": [
      {"law_id": "②", "original": "违规原文", "correction": "修改建议", "severity": "high|medium|low"}
    ]
  },
  "advice_items": [
    {"id": 1, "suggestion": "措辞修正", "rationale": "违反X律", "priority": "high"},
    {"id": 2, "suggestion": "结构调整", "rationale": "原因", "priority": "medium"}
  ],
  "warning_if_ignored": "若不修改，湘小法评估预计扣N分以上",
  "token_count_estimate": "~500"
}
```

### 典型示例

**示例C — 措辞检查咨询**
```
Query: "这段话对外汇报是否合适：'研究中心经过深入研究，认为我省必须大力发展低空经济，建议省政府设立专项基金支持。'"
Context: 以湘江研究院名义向省政府提交的建议方案
```

**建议输出**：
```json
{
  "advisor_type": "soe_context",
  "confidence": "high",
  "seven_laws_check": {
    "violations_found": 4,
    "details": [
      {"law_id":"①", "original":"'研究中心经过深入研究'", "correction":"删除，直接陈述观点", "severity":"high"},
      {"law_id":"②", "original":"'必须大力发展'", "correction":"'宜加快发展'或'可积极探索'", "severity":"high"},
      {"law_id":"①", "original":"'建议省政府'", "correction":"改为被动语态'可推动设立'", "severity":"medium"},
      {"law_id":"⑥", "original":"'设立专项基金支持'(缺四要素)", "correction":"补充金额、来源、频次", "severity":"medium"}
    ]
  },
  "advice_items": [
    {"id":1, "suggestion":"①删除'研究中心经过深入研究'——自我吹捧", "rationale":"违反主体归位律","priority":"high"},
    {"id":2, "suggestion":"②'必须'→'宜加快发展'", "rationale":"违反降调去锋律","priority":"high"},
    {"id":3, "suggestion":"③开篇加'在省国资委指导、兴湘集团支持下'", "rationale":"符合向上汇报格式","priority":"medium"},
    {"id":4, "suggestion":"④基金部分补齐四要素：规模/来源/年度/用途", "rationale":"违反四要素律","priority":"medium"}
  ],
  "warning_if_ignored": "4项违规中2项高优，湘小法评估预计评分≤28分"
}
```

---

## 模板四：成本控制顾问 (cost_control)

### 适用场景清单
- 研究范围边界判断（"不煮海"）
- 80/20关键驱动识别
- 边际收益递减判断
- 篇幅/深度控制
- 资源聚焦决策

### 内置原则速查

**麦肯锡"不要煮海"原则**：
- 80%的价值来自20%的分析——找到那20%
- 当新增分析的边际收益明显递减时止步
- 完美是优秀的敌人

**80/20法则应用**：
- 数据：TOP3关键指标 > 全量数据罗列
- 案例：1个深度案例 > 5个浅层案例
- 对标：2-3个精选对标 > 全面扫描

### 输出模板

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_RESPONSE",
  "advisor_type": "cost_control",
  "query_ref": "[引用原始咨询问题]",
  "confidence": "high|medium|low",
  "scope_assessment": {
    "current_scope": "当前范围描述",
    "recommended_scope": "建议范围描述",
    "reduction_pct": "建议缩减比例"
  },
  "advice_items": [
    {"id": 1, "suggestion": "范围裁剪建议", "rationale": "边际收益判断", "priority": "high"},
    {"id": 2, "suggestion": "聚焦重点建议", "rationale": "80/20分析", "priority": "medium"},
    {"id": 3, "suggestion": "止步信号", "rationale": "递减拐点", "priority": "medium"}
  ],
  "warning_if_ignored": "若不加控制，预计超出预算/时间约X%",
  "token_count_estimate": "~350"
}
```

### 典型示例

**示例D — 范围控制咨询**
```
Query: "这个低空经济课题要不要把无人机、eVTOL、起降场、通信导航、空域管理、适航认证全覆盖？"
Context: 为兴湘集团撰写低空经济产业分析报告，时间预算3天
```

**建议输出**：
```json
{
  "advisor_type": "cost_control",
  "confidence": "high",
  "scope_assessment": {
    "current_scope": "6个子领域全覆盖",
    "recommended_scope": "聚焦3个：eVTOL制造+运营服务+起降场基础设施",
    "reduction_pct": "50%"
  },
  "advice_items": [
    {"id":1, "suggestion":"①聚焦eVTOL+运营+起降场三个子领域", "rationale":"与兴湘业务直接相关度最高","priority":"high"},
    {"id":2, "suggestion":"②通信导航/空域管理合并为一节背景介绍", "rationale":"非核心但不可完全略过","priority":"medium"},
    {"id":3, "suggestion":"③适航认证仅提及不展开", "rationale":"专业度过深且变化快","priority":"low"},
    {"id":4, "suggestion":"④每个子领域控制在1.5页以内", "rationale":"总篇幅控制在15页以内","priority":"medium"}
  ],
  "warning_if_ignored": "6个全覆盖预计需要5天以上，超时67%且边际收益递减明显"
}
```

---

## 错误处理模板

### E1: 超出能力范围

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_OUT_OF_SCOPE",
  "query_ref": "[原问题]",
  "reason": "此问题属于[具体领域]，超出四类顾问能力范围",
  "suggested_alternative": "建议咨询[替代Agent/Skill]或自行处理",
  "not_counted_toward_max_uses": true
}
```

### E2: 问题过于模糊

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_QUERY_CLARIFICATION_NEEDED",
  "query_ref": "[原问题]",
  "issue": "问题描述不够具体，无法给出针对性建议",
  "clarification_questions": ["您想从哪个角度分析？", "目标读者是谁？"],
  "example_of_good_query": "更具体的问法示例"
}
```

### E3: 达到max_uses上限

```json
{
  "protocol_version": "1.0",
  "message_type": "ADVISOR_LIMIT_REACHED",
  "current_use_count": N,
  "max_uses_limit": N,
  "message": "本次任务顾问咨询次数已达上限，请Generator自行决策或申请提升上限",
  "last_advice_summary": "前N次咨询的核心建议回顾"
}
```

---

*模板库 v1.0 · 湘江研究院研究中心 · 2026年4月10日*
