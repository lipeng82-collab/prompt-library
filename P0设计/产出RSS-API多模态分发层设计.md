# 产出RSS/API多模态分发层设计（Layer 6）

> 为现有研究报告/专报增加RSS摘要和API JSON输出能力
> 版本：v1.0.0 | 设计日期：2026-05-08

---

## 一、设计背景

### 现状问题
当前研究院的产出形态单一：**Word正式版 + Markdown内部版**。所有产出都是"单点交付"——生成一份文件，发给特定人，结束。

### AIHOT启示
AIHOT的Skill/RSS/API三模态分发覆盖了三种不同用户：
- **Skill用户**：Agent生态使用者
- **RSS用户**：传统RSS阅读器用户
- **API用户**：系统集成开发者

### 目标
在现有五层Harness质量门禁（Generator→顾问→MECE→评估→白板）之后，增加**Layer 6：分发层**，让一份产出的价值在多个渠道同时释放。

---

## 二、架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                  Layer 6：分发层（新增）                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：通过湘小法终审的完整产出                               │
│       （Word正式版 / Markdown全文 / 结构化数据）              │
│                                                             │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              分发路由决策器                            │   │
│  │  根据产出类型、敏感级别、目标受众，决定分发渠道组合      │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ├──→ Word正式版（原有）→ 上级提交/合同交付            │
│       │                                                     │
│       ├──→ Markdown精简版（原有）→ 内部传阅                 │
│       │                                                     │
│       ├──→ RSS摘要（新增）→ 订阅用户/外部传播               │
│       │                                                     │
│       ├──→ API JSON（新增）→ 系统对接/数据服务              │
│       │                                                     │
│       └──→ Skill数据包（新增）→ Agent生态                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、四种分发形态详细设计

### 3.1 Word正式版（保留）
- **用途**：向上级提交、合同交付、正式归档
- **格式**：符合国企公文规范（湘小印出品）
- **敏感级别**：内部机密以上
- **分发方式**：邮件/纸质/腾讯文档

### 3.2 Markdown精简版（保留）
- **用途**：内部Agent间传递、快速传阅
- **格式**：标准Markdown，含目录
- **敏感级别**：内部公开
- **分发方式**：WorkBuddy文件系统/IMA知识库

### 3.3 RSS摘要（新增）⭐

#### 3.3.1 RSS Feed设计

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>湘智库·政策研究</title>
    <link>https://research.xiangjiang.com</link>
    <description>湘江研究院政策研究成果RSS订阅</description>
    <language>zh-cn</language>
    
    <item>
      <title>湖南省低空经济产业布局研究报告</title>
      <link>https://research.xiangjiang.com/reports/2026/low-altitude-economy</link>
      <description>本报告系统分析了湖南省低空经济产业链现状、政策机遇与挑战，提出省属国企布局建议。核心结论：湖南应优先发展低空物流与应急救援两大应用场景...</description>
      <category>战新产业</category>
      <category>低空经济</category>
      <pubDate>Fri, 08 May 2026 08:00:00 +0800</pubDate>
      <guid>xiangjiang-report-2026-0508-001</guid>
      <author>湘江研究院研究中心</author>
    </item>
    
  </channel>
</rss>
```

#### 3.3.2 RSS订阅分类

| Feed名称 | 内容 | 目标用户 |
|---------|------|---------|
| 湘智库·全部研究 | 所有公开发布的研究报告摘要 | 综合关注者 |
| 湘智库·国资改革 | 国企改革/考核/混改类研究 | 国企改革关注者 |
| 湘智库·战新产业 | 低空经济/算力/新材料类 | 产业投资人 |
| 湘智库·湖南专题 | 仅湖南相关研究 | 湖南本地用户 |
| 湘智库·政策早报 | 每日政策动态（湘小报产出） | 政策追踪者 |

#### 3.3.3 摘要生成规则

```python
# 伪代码：从完整报告生成RSS摘要
def generate_rss_summary(full_report_md: str) -> str:
    # Step 1: 提取核心结论（报告最后的"结论与建议"部分）
    conclusion = extract_section(full_report_md, "结论")
    
    # Step 2: 压缩至200字以内
    summary = truncate(conclusion, max_chars=200)
    
    # Step 3: 添加报告元信息
    final_summary = f"{summary}...（完整报告含{count_words(full_report_md)}字，{count_charts(full_report_md)}张图表）"
    
    return final_summary
```

### 3.4 API JSON（新增）⭐

#### 3.4.1 API设计

```yaml
openapi: 3.0.0
info:
  title: 湘智库API
  version: 1.0.0
  description: 湘江研究院研究成果与政策数据API

servers:
  - url: https://api.xiangjiang.com/v1

paths:
  /reports:
    get:
      summary: 获取研究报告列表
      parameters:
        - name: category
          in: query
          schema:
            type: string
            enum: [国资改革, 战新产业, 三资盘活, 资本运作, 区域经济]
        - name: date_from
          in: query
          schema:
            type: string
            format: date
        - name: date_to
          in: query
          schema:
            type: string
            format: date
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
            maximum: 100
      responses:
        '200':
          description: 报告列表
          content:
            application/json:
              schema:
                type: object
                properties:
                  total:
                    type: integer
                  reports:
                    type: array
                    items:
                      $ref: '#/components/schemas/ReportSummary'

  /reports/{id}:
    get:
      summary: 获取单篇报告详情
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 报告详情
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReportDetail'

  /policies:
    get:
      summary: 获取政策动态列表（湘小报数据）
      parameters:
        - name: date_range
          in: query
          schema:
            type: string
            enum: [today, week, month]
        - name: importance
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 5
      responses:
        '200':
          description: 政策动态列表

components:
  schemas:
    ReportSummary:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        category:
          type: string
        summary:
          type: string
        publish_date:
          type: string
          format: date
        word_count:
          type: integer
        chart_count:
          type: integer
        source_url:
          type: string

    ReportDetail:
      allOf:
        - $ref: '#/components/schemas/ReportSummary'
        - type: object
          properties:
            content_md:
              type: string
              description: Markdown格式全文（需授权）
            key_findings:
              type: array
              items:
                type: string
            recommendations:
              type: array
              items:
                type: string
            data_sources:
              type: array
              items:
                type: string
```

#### 3.4.2 数据开放分级

| 级别 | 内容 | 访问方式 | 鉴权 |
|------|------|---------|------|
| L1 公开 | 报告标题+摘要+元信息 | 无需鉴权 | 免费 |
| L2 注册 | 报告全文（Markdown） | API Key | 注册即可 |
| L3 授权 | 结构化数据/图表/原始素材 | API Key + 合同 | 付费/合作 |
| L4 内部 | 敏感分析/未公开数据 | 内部网络 | 仅限内部 |

### 3.5 Skill数据包（新增）

当其他机构的Agent安装"湘智库Skill"后，可通过Skill接口查询：

```json
{
  "skill_name": "xiangjiang-thinktank",
  "version": "1.0.0",
  "endpoints": {
    "query_reports": {
      "description": "查询湘江研究院研究报告",
      "input": "关键词+分类+时间范围",
      "output": "报告摘要列表"
    },
    "query_policies": {
      "description": "查询国资政策动态",
      "input": "政策领域+时间范围",
      "output": "政策条目列表（含摘要和原文链接）"
    },
    "get_daily_brief": {
      "description": "获取今日国资政策早报",
      "input": "日期（可选，默认今日）",
      "output": "结构化早报数据"
    }
  }
}
```

---

## 四、分发路由决策规则

### 4.1 路由矩阵

| 产出类型 | Word | Markdown | RSS | API | Skill |
|---------|------|----------|-----|-----|-------|
| 向上提交的方案/专报 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 对外交付的咨询报告 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 公开发布的产业研究 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 政策早报 | ❌ | ✅ | ✅ | ✅ | ✅ |
| 内部工作文档 | ❌ | ✅ | ❌ | ❌ | ❌ |
| 数据包/素材包 | ❌ | ❌ | ❌ | ✅ | ✅ |

### 4.2 敏感级别自动判定

```python
def determine_distribution_channels(report_content: str, metadata: dict) -> list:
    sensitivity_score = 0
    
    # 敏感词检测
    sensitive_keywords = ["尚未公开", "内部数据", "保密", "不宜外传"]
    for kw in sensitive_keywords:
        if kw in report_content:
            sensitivity_score += 2
    
    # 受众检测
    if metadata.get("target") in ["省国资委", "省委", "省政府"]:
        sensitivity_score += 3
    
    # 金额检测
    if extract_large_amounts(report_content) > 1000000000:  # 10亿以上
        sensitivity_score += 1
    
    # 路由决策
    if sensitivity_score >= 5:
        return ["Word", "Markdown"]
    elif sensitivity_score >= 2:
        return ["Word", "Markdown", "RSS摘要"]
    else:
        return ["Word", "Markdown", "RSS摘要", "API", "Skill"]
```

---

## 五、与现有体系的集成

### 5.1 在Harness流水线中的位置

```
Layer 1: Generator 生成初稿
    ↓
Layer 2: 湘小策 顾问咨询
    ↓
Layer 3: MECE自检
    ↓
Layer 4: 湘小法 评估
    ↓
Layer 5: ultrareview 会审 → 湘小法 终审
    ↓
【Layer 6: 分发层（新增）】
    ├──→ 敏感级别判定（自动）
    ├──→ 多模态生成（Word/Markdown/RSS/API/Skill）
    ├──→ 质量检查（各模态格式校验）
    └──→ 分发执行（推送/发布/归档）
```

### 5.2 湘小协的协调职责扩展

湘小协v1.3新增"分发协调"职责：
- 接收终审通过的产出
- 调用分发路由决策器
- 并行生成各模态版本
- 调度各渠道的推送任务
- 记录分发日志到湘小档

---

## 六、实施路径

### Phase 1（2周）：RSS Feed
- [ ] 确定RSS生成工具（Python feedgen库）
- [ ] 设计5个RSS Feed分类
- [ ] 实现从Markdown报告自动生成RSS摘要
- [ ] 部署RSS Feed静态文件服务
- [ ] 内部测试（3个报告）

### Phase 2（4周）：API服务
- [ ] 设计OpenAPI规范（本文档3.4.1）
- [ ] 实现基础API（/reports列表+详情）
- [ ] 实现鉴权（API Key分级）
- [ ] 部署测试环境
- [ ] 向财信金控/数据宝提供试用

### Phase 3（6周）：Skill封装
- [ ] 设计Skill接口规范
- [ ] 实现3个核心endpoint
- [ ] GitHub发布（开源引流）
- [ ] 编写Skill使用文档

---

## 七、成功指标

| 指标 | 目标值 | 测量方式 |
|------|--------|---------|
| RSS订阅数 | ≥50个（3个月内） | Feedly/Inoreader等统计 |
| API调用量 | ≥1000次/月（内部POC） | API网关日志 |
| Skill安装数 | ≥100次（GitHub Star） | GitHub统计 |
| 多模态生成自动化率 | ≥80% | 自动生成比例 |

---

*设计完成日期：2026-05-08*
