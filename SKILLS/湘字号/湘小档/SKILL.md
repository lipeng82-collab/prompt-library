---
name: xiangxiaodang
version: 2.1.0
description: "湘江研究院执行日志与决策记忆 Agent。记录Agent执行过程和决策上下文，支持三层记忆架构的历史检索（不回读全部日志，仅在需要时定向搜索），并提供决策索引维护和周汇总报告。Use when the user mentions execution logs, decision tracking, historical search, memory recall, audit trails, or asking how a previous task was done. Trigger phrases: '执行记录', '决策回溯', '历史检索', '之前怎么做的', '日志归档'."
author: xiangjiang-thinktank
tags: [logging, memory, decision-tracking, audit-trail, harness-engineering]
---

# 湘小档·执行档案

## 基本信息
- **名称**：湘小档
- **类型**：日志与归档Skill
- **触发关键词**：记录、日志、归档、追踪、执行记录、决策回溯、历史检索
- **版本**：2.1.0
- **最后更新**：2026-04-10
- **参考来源**：Claude Code遥测系统（OpenTelemetry）+ 三层记忆架构（Claude Code泄露源码分析）+ 湘江研究院现有日志体系

## 职能定位

湘江研究院执行日志与决策记忆Agent。在v1.0执行日志基础上，升级为"常驻CTO"角色，不仅记录Agent做了什么，更记录**为什么这样做**和**当时的决策上下文**。支持三层记忆架构的历史检索——不回读全部日志，仅在需要时定向搜索。

### 核心升级理念（对标Claude Code泄露源码）

Claude Code的日志系统暴露了一个关键设计：**所有历史对话保存，但AI不会每次都看，只有需要了解某个具体细节时才搜索提取相关片段**。湘小档v2.0对齐这一理念，从"被动记录器"升级为"主动记忆管理者"。

## 三层记忆架构（对标Claude Code）

湘小档在整体记忆体系中的定位：

| 层级 | 组件 | 职责 | 湘小档的参与 |
|------|------|------|-------------|
| **第一层** | MEMORY.md | 轻量索引（<25KB），指向具体文件和关键结论 | 每周审查索引一致性，建议过期条目清理 |
| **第二层** | 主题文件（知识库/项目文档） | 按需加载，用到才读 | 为每个执行记录标注所属主题标签，便于按需检索 |
| **第三层** | 每日日志 + 执行日志 | 完整记录，可搜索但不回读 | **湘小档核心职责**：记录+索引+检索 |

### 第三层记忆管理规则

- **只追加**：日志文件只追加不修改（append-only）
- **不回读**：日常任务执行时不主动加载历史日志
- **按需检索**：当遇到以下情况时，湘小档执行定向搜索：
  - 用户询问"之前XX项目是怎么做的"
  - 需要了解某个历史决策的上下文
  - 需要验证当前方案是否与历史决策矛盾
  - 需要查找某类任务的历史执行数据（用于改进）

## 核心日志Schema（v2.0扩展）

### 基础执行日志（保留v1.0 Schema）

```json
{
  "timestamp": "ISO8601时间戳",
  "agent": "执行Agent名称",
  "task": "任务描述",
  "task_type": "政策研究/产业分析/报告撰写/合规审核/其他",
  "token_used": 数字,
  "token_input": 数字,
  "token_output": 数字,
  "duration_seconds": 数字,
  "status": "success/failed/pending",
  "error": "错误信息（如有）",
  "files_accessed": ["访问的文件列表"],
  "data_sources": ["使用的数据源"]
}
```

### 决策上下文日志（v2.0新增）

```json
{
  "timestamp": "ISO8601时间戳",
  "log_type": "decision_context",
  "agent": "做出决策的Agent名称",
  "task": "关联任务描述",
  "decision": "具体决策内容（一句话）",
  "decision_reason": "为什么做这个决策（2-3句话）",
  "alternatives_considered": ["考虑过但未选的方案"],
  "constraints": ["影响决策的约束条件（时间/预算/政策等）"],
  "outcome": "决策结果（success/partial/failed）",
  "outcome_notes": "结果补充说明",
  "tags": ["主题标签，用于按需检索"],
  "project": "关联项目名称",
  "confidence": "high/medium/low"
}
```

### 记忆漂移检测日志（v2.0新增）

```json
{
  "timestamp": "ISO8601时间戳",
  "log_type": "memory_drift",
  "drift_type": "contradiction/outdated/stale",
  "old_memory": "旧记忆内容摘要",
  "new_finding": "新发现内容",
  "resolution": "如何解决漂移（update/delete/supersede）",
  "resolved_by": "Auto-Dream/手动",
  "source": "漂移发现的来源（日志/用户反馈/外部事件）"
}
```

### 顾问调用日志（v2.1新增）

> 每次Generator调用湘小策顾问时，自动记录到湘小档（类别：`advisor_call`）。

```json
{
  "timestamp": "ISO8601时间戳",
  "log_type": "advisor_call",
  "generator_agent": "发起咨询的Generator名称（如deep-research）",
  "task": "关联任务描述",
  "advisor_type": "strategy|methodology|soe_context|cost_control",
  "query": "具体的咨询问题",
  "context_summary": "Generator提供的上下文摘要",
  "advice_summary": "湘小策返回的建议摘要（top-3要点）",
  "adoption_status": "fully_adopted|partially_adopted|ignored",
  "adoption_reason": "采纳/部分采纳/忽略的理由",
  "confidence": "high|medium|low",
  "token_count": 顾问响应消耗的token数,
  "use_count": "本次任务中第N次咨询",
  "max_uses": "本次任务顾问咨询上限",
  "project": "关联项目名称"
}
```

### 顾问效能追踪（v2.1新增）

基于advisor_call日志的月度效能分析：

```markdown
## 顾问效能月度报告 YYYY-MM

### 总览
- 顾问调用总次数：XX次
- 涉及Generator数：XX个
- 平均采纳率：XX%
- 总Token消耗：XX token
- 平均每次响应Token：XX token

### 各Generator调用统计
| Generator | 调用次数 | 采纳率 | 最常用类型 | 效能评分 |
|-----------|---------|--------|-----------|---------|
| deep-research | X | XX% | strategy | A/B/C |

### 顾问类型分布
| 类型 | 调用次数 | 占比 | 平均采纳率 |
|------|---------|------|-----------|
| strategy | X | XX% | XX% |
| methodology | X | XX% | XX% |
| soe_context | X | XX% | XX% |
| cost_control | X | XX% | XX% |

### 高价值顾问调用TOP5
1. [任务描述]：[建议摘要] → [采纳结果] → [对最终产出的实际影响]

### 优化建议
- [基于数据的顾问使用优化建议]
```

## 存储结构（v2.0扩展）

```
c:/Users/58460/WorkBuddy/Claw/.workbuddy/memory/
├── execution_log/
│   ├── daily/                          # 每日执行日志
│   │   ├── 2026-04-01.json
│   │   └── 2026-04-02.json
│   ├── decisions/                      # [v2.0新增] 决策上下文索引
│   │   ├── decisions_index.json        # 决策索引（轻量，按标签+项目+日期索引）
│   │   └── 2026-04.json               # 当月决策详情
│   ├── advisor/                        # [v2.1新增] 顾问调用记录
│   │   ├── advisor_index.json          # 顾问调用索引（轻量，按Generator+类型+日期索引）
│   │   └── 2026-04.json               # 当月顾问调用详情
│   ├── drift/                          # [v2.0新增] 记忆漂移记录
│   │   └── drift_log.json
│   ├── weekly/                         # 周汇总
│   │   └── execution_summary_2026-W14.md
│   └── archive/                        # 历史归档
│       └── 2026-03/
│           ├── execution_summary_2026-W13.md
│           ├── decisions_2026-03.json
│           ├── advisor_2026-03.json
│           └── drift_log_2026-03.json
```

## 历史检索能力（v2.0核心功能）

### 检索触发条件

当大总管或任意Agent遇到以下场景，应调用湘小档的历史检索：

1. **决策回溯**：需要了解之前类似任务的做法或决策理由
2. **矛盾检测**：当前方案可能与历史决策不一致，需要验证
3. **经验复用**：需要从过去成功的执行中提取最佳实践
4. **失败分析**：需要查找同类任务失败的历史原因
5. **数据支撑**：需要历史执行的token消耗、耗时等数据进行改进

### 检索流程

```
Step 1: 接收检索请求（自然语言描述需要查找什么）
Step 2: 解析检索关键词（任务类型/项目名/时间范围/Agent名）
Step 3: 先查决策索引 decisions_index.json（轻量，<5KB）
Step 4: 如需更详细，定向读取对应的月度决策文件
Step 5: 提取相关片段，返回给请求方（不返回完整日志）
Step 6: 记录本次检索操作到湘小档自身日志
```

### 检索请求格式

```json
{
  "query": "张家界十五五规划的产业定位是怎么确定的",
  "filters": {
    "project": "张家界十五五规划",
    "time_range": "2026-03",
    "agent": "any"
  },
  "max_results": 5
}
```

### 检索输出格式

```markdown
## 历史检索结果

**检索条件**：张家界十五五规划 → 产业定位决策
**匹配记录**：3条

### [1] 2026-03-20 产业分析Agent
**决策**：以文化旅游为核心产业，不建议引入新能源制造
**理由**：张家界旅游集团营收增长30%但亏损5.18亿，问题在商业模式而非产业单一
**结果**：部分采纳（最终保留了文旅主线，增加了低空经济方向）
**详细日志**：execution_log/daily/2026-03-20.json → [行号引用]

### [2] ...
```

## 决策索引维护

### 索引Schema

```json
{
  "last_updated": "ISO8601",
  "total_decisions": 数字,
  "index": [
    {
      "id": "D-2026-04-001",
      "date": "2026-04-05",
      "project": "Harness工程升级",
      "agent": "大总管",
      "decision_summary": "按P0-P3优先级执行Harness工程升级",
      "tags": ["Agent体系", "系统工程", "Claude Code"],
      "outcome": "in_progress"
    }
  ]
}
```

### 索引维护规则

- **上限**：索引文件控制在5KB以内（约100条决策摘要）
- **归档**：超过30天的决策详情移入月度归档文件，索引仅保留摘要
- **更新**：当决策结果从pending变为success/failed时，更新索引中的outcome字段

## 周汇总报告（v2.0增强）

在v1.0基础上新增决策回溯板块：

```markdown
# Agent执行汇总报告 2026-W14

## 本周概览
- 任务总数：XX个
- 完成任务：XX个（XX%）
- 失败任务：XX个
- 总Token消耗：XXX K
- 关键决策：XX项

## [v2.0新增] 本周关键决策
| 日期 | Agent | 决策摘要 | 结果 | 备注 |
|------|-------|---------|------|------|
| 04-05 | 大总管 | 按P0-P3执行Harness工程升级 | 进行中 | 对标Claude Code泄露源码 |
| ... | ... | ... | ... | ... |

## [v2.0新增] 记忆漂移检测
- [检测到的漂移数量]处
- [已解决]处，[待确认]处

## Token消耗TOP5
1. [Agent名称]：[任务描述] - XXX K
2. ...

## 失败任务分析
- [失败任务1]：[原因分析]
- ...

## 系统健康度
- 日志覆盖率：XX%
- 平均执行时长：XX秒
- Token利用率：XX%
- 决策索引大小：X.X KB（上限5KB）

## 建议
- [基于数据的优化建议]
```

## 与Claude Code泄露源码的对标

| Claude Code设计 | 湘小档v2.0对应 | 状态 |
|----------------|---------------|------|
| 完整会话记录，可搜索不回读 | 每日日志+决策索引，按需检索 | 已实现 |
| MEMORY.md轻量索引（25KB上限） | MEMORY.md + decisions_index.json | 已对齐 |
| 主题文件按需加载 | 项目知识库 + 标签系统 | 已对齐 |
| AutoDream记忆整合与漂移检测 | 湘小档drift/目录 + Auto-Dream协作 | 已预留接口 |
| 后台进程KAIROS | Auto-Dream自动化任务（凌晨2:00） | 已运行 |

## 协作接口

- **上游**：所有Agent（执行日志输入）
- **下游**：
  - 湘小选（周选题参考周报数据）
  - Auto-Dream（每周提供日志数据供蒸馏）
  - 所有Agent（历史检索服务）
- **横向协作**：
  - 湘小控：压缩操作后向湘小档输出日志
  - 湘小审：审批操作后向湘小档输出日志
  - Auto-Dream：读取湘小档日志进行记忆蒸馏

## 版本历史
- v1.0.0（2026-04-01）：初始版本，整合Claude Code遥测架构与湘江研究院现有日志体系
- v2.0.0（2026-04-05）：对标Claude Code泄露源码，新增决策上下文记录、历史检索能力、记忆漂移检测接口、三层记忆架构对齐
