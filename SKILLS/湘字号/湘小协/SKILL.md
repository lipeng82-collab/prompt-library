---
name: 湘小协
version: 1.2.0
description: "湘江研究院Harness工程协调器 v1.1。管理Generator-Evaluator对抗流水线，实现Agent间结构化质量对抗协议（QA Protocol），确保产出型Agent的输出经过独立评估后再提交。新增：IPC通信协议实现层（JSON→use_skill调用映射）、白板协作Step-by-Step流程、与ultraplan/ultrareview上下游衔接规范。Use when orchestrating multi-agent quality review workflows, setting up generator-evaluator pairs, or running QA protocols before submitting research deliverables. Trigger phrases: '质量对抗', 'Generator-Evaluator', '审校流水线', 'QA协议', '评估生成', '对抗检查', 'GE配对', '协调查看', '协调整合'."
compatibility: 需要能调用湘小法（Evaluator）及其他产出型Agent（Generator），依赖Agent间消息传递机制；与ultraplan（上游开题规划）、ultrareview（下游会审模式）形成完整链路
author: 湘江研究院
tags: [harness-engineering, generator-evaluator, quality-assurance, agent-coordination, ipc-protocol, whiteboard]
---

# 湘小协 · Harness工程协调器

## 基本信息

- **名称**：湘小协
- **类型**：协调器Skill（Agent间通信协议 + GE流水线管理）
- **触发关键词**：评估、审校、质量检查、Generator、Evaluator、对抗、对抗流水线、协调整合
- **版本**：1.2.0（2026-04-10）
- **创建日期**：2026-04-05
- **升级日期**：2026-04-10
- **参考来源**：Anthropic "Harness Design for Long-Running Application Development"（2026.3）

---

## 职能定位

湘江研究院Harness工程协调器，负责管理和执行Generator-Evaluator对抗流水线。

**核心理念**（来自Anthropic Harness Engineering）：
- AI独立完成复杂任务有两个致命问题：上下文焦虑和自我评估偏差
- 解法是借鉴GAN（生成对抗网络）：Generator（生成器）负责干活，Evaluator（评估器）独立挑刺
- Anthropic实测：普通模式9美元做出一个能看不能玩的游戏；Harness模式200美元做出真正的游戏（贵20倍，能力质变）

**湘小协的角色**：不直接生成或评估内容，而是设计和管理"谁生成→谁评估→怎么对抗→何时通过"的流程规则。

**在智库写作三件套中的定位**（v1.1新增）：

```
ultraplan（开题推演）
    ↓ 规划方案（Phase4）
湘小协（GE协调层）
    ↓ GE配对 + IPC调度
Generator Agent（执行）
    ↓ 产出文件
湘小协（质量门禁）
    ↓ 评估请求
Evaluator（湘小法）
    ↓ 评估报告
湘小协（汇总决策）
    ↓ 整改清单
ultrareview（会审增强）
    ↓ 最终报告
湘小法（合规终审）
    ↓ 通过
输出/提交
```

---

## 一、Generator-Evaluator配对关系表

### 核心GE配对表（v1.1扩展）

| 配对编号 | Generator | 产出类型 | Evaluator | 评估维度 | 触发条件 | 评估模式 |
|---------|-----------|---------|-----------|---------|---------|---------|
| GE-01 | 湘小研（产业分析） | 产业链/产业政策分析 | 湘小法（全维模式） | 合规+七律+数据+逻辑 | 提交前 | 强制 |
| GE-02 | 湘小写（专报撰写） | 智库专报/内参 | 湘小法（全维模式） | 合规+七律+数据+逻辑 | 提交批示前 | 强制 |
| GE-03 | deep-research | 深度研究报告 | 湘小法（研究模式） | 数据+逻辑+来源 | 终稿前 | 强制 |
| GE-04 | industry-chain-analysis | 产业分析报告 | 湘小数（数据核查）→湘小法 | 数据准确性+合规 | 终稿前 | 强制 |
| GE-05 | data-analysis-xt | 数据分析报告/图表 | 湘小数（数据核查） | 量化一致性+来源 | 终稿前 | 建议 |
| GE-06 | china-macro-analyst | 宏观研判报告 | 湘小报（政策对标）→湘小法 | 政策吻合+逻辑 | 终稿前 | 强制 |
| GE-07 | policy-report-writer | 智库专报 | 湘小法（全维模式） | 合规+七律+数据+逻辑 | 提交批示前 | 强制 |
| GE-08 | 湘小印（格式文档） | 格式化输出文档 | 湘小印（格式自检） | 格式+合规 | 输出前 | 可选 |
| GE-09 | 任意Generator | 任何对外产出 | 湘小法（通用模式） | 合规（最低标准） | 对外发送/用户要求 | 视情况 |

### 与ultraplan的接口（v1.1新增）

ultraplan Phase4输出的Agent分工方案，直接映射为GE配对执行计划：

```json
{
  "protocol": "ipc_v1.1",
  "role": "plan_to_ge_mapping",
  "source": "ultraplan",
  "output_file": "[Phase5报告中的Agent分工表]",
  "ge_pairs": [
    {
      "pair_id": "GE-04",
      "generator_agent": "industry-chain-analysis",
      "output_file": "[ultraplan指定的产业链分析文件]",
      "evaluator_agent": "湘小数",
      "trigger": "自动触发（Generator完成后立即）",
      "timeout_minutes": 15
    },
    {
      "pair_id": "GE-06",
      "generator_agent": "china-macro-analyst",
      "output_file": "[ultraplan指定的宏观研判文件]",
      "evaluator_agent": "湘小报",
      "trigger": "自动触发",
      "timeout_minutes": 15
    }
  ]
}
```

---

## 二、IPC通信协议实现层（v1.1核心新增）

### 2.1 协议概述

IPC（Inter-Process Communication）协议定义了Generator-Agent与Evaluator-Agent之间的标准消息格式，确保质量对抗流水线可追踪、可重复执行。

**消息流**：

```
Generator Agent
    │
    ├──→ [IPC请求消息] ──→ 湘小协（协调器）
    │                            │
    │                            ├──→ 湘小法（Evaluator）
    │                            │         │
    │                            │         └──→ [IPC评估消息] ──→ 湘小协
    │                            │                            │
    │                            │                            ├──→ 汇总报告
    │                            │                            │    │
    │                            │                            │    ├── 评分≥34 → 通过 → 提交
    │                            │                            │    ├── 评分30-33 → 修改→重评
    │                            │                            │    └── 评分<30 → 打回重写
    │                            │                            │
    │                            └──→ 白板协作（如需要诊断）
```

### 2.2 IPC消息格式规范（JSON Schema）

#### 2.2.1 评估请求消息（IPC-EVAL-REQ）

Generator向湘小协提交评估请求：

```json
{
  "protocol_version": "1.1",
  "message_type": "EVALUATION_REQUEST",
  "message_id": "IPC-REQ-2026-XXXXXX",
  "timestamp": "2026-04-10T13:30:00+08:00",
  "sender": {
    "agent": "Generator-Agent名称",
    "agent_skill_id": "Generator的SKILL.md名称",
    "session_id": "当前会话ID"
  },
  "payload": {
    "ge_pair_id": "GE-01",
    "task_description": "政策研究报告：湖南省低空经济政策分析",
    "output_type": "政策研究报告",
    "output_file": "d:/Work@湘江研究院/2026/0410课题/低空经济分析.md",
    "round": 1,
    "previous_evaluations": [],
    "quality_claims": {
      "data_verified": true,
      "source_cited": true,
      "logic_checked": false,
      "compliance_self_check": true
    }
  },
  "use_skill_instruction": "请调用 use_skill('湘小法') 对上述文件进行合规评估，评估模式：全维模式，参考维度：合规+七律+数据+逻辑"
}
```

#### 2.2.2 评估响应消息（IPC-EVAL-RES）

Evaluator（湘小法）返回评估结果：

```json
{
  "protocol_version": "1.1",
  "message_type": "EVALUATION_RESPONSE",
  "message_id": "IPC-RES-2026-XXXXXX",
  "timestamp": "2026-04-10T13:45:00+08:00",
  "sender": {
    "agent": "湘小法",
    "agent_skill_id": "湘小法"
  },
  "reference": {
    "request_id": "IPC-REQ-2026-XXXXXX",
    "ge_pair_id": "GE-01",
    "round": 1
  },
  "payload": {
    "overall_score": 31,
    "overall_verdict": "需修改",
    "max_score": 37,
    "pass_threshold": 34,
    "dimensions": {
      "legal_compliance": 9,
      "seven_laws": 5,
      "data_verification": 8,
      "logical_consistency": 9
    },
    "priority_issues": [
      {
        "priority": "P0",
        "category": "主体归位律",
        "location": "第3段",
        "original_text": "研究中心建议省国资委探索...",
        "issue": "主语无权，建议改为有权主体表述",
        "suggestion": "将'研究中心建议省国资委探索...'改为'省国资委可探索...'",
        "fix_action": "replace",
        "estimated_fix_time": "2分钟"
      }
    ],
    "passed_dimensions": ["数据边界", "程序合规"],
    "requires_reviewer_attention": ["主体归位律", "措辞合规"]
  },
  "recommendation": {
    "action": "MODIFY",
    "next_steps": ["Generator根据评估报告修改", "重新提交湘小法评估（round+1）"],
    "skip_possible": false
  }
}
```

#### 2.2.3 评估通过消息（IPC-EVAL-PASS）

当评分≥34分时，Evaluator发送通过消息：

```json
{
  "protocol_version": "1.1",
  "message_type": "EVALUATION_PASS",
  "message_id": "IPC-PASS-2026-XXXXXX",
  "reference": {
    "request_id": "IPC-REQ-2026-XXXXXX",
    "ge_pair_id": "GE-01",
    "total_rounds": 2
  },
  "payload": {
    "overall_score": 35,
    "pass_threshold": 34,
    "summary": "所有关键维度达标，可进入下一阶段",
    "final_issues": []
  },
  "recommendation": "提交ultrareview会审增强模式"
}
```

#### 2.2.4 顾问咨询请求消息（IPC-ADVISOR-REQ）(v1.2新增)

Generator在执行过程中向湘小策发起顾问咨询：

```json
{
  "protocol_version": "1.2",
  "message_type": "ADVISOR_REQUEST",
  "message_id": "IPC-ADV-REQ-2026-XXXXXX",
  "timestamp": "2026-04-10T13:30:00+08:00",
  "sender": {
    "agent": "deep-research",
    "agent_skill_id": "deep-research"
  },
  "payload": {
    "advisor_type": "strategy|methodology|soe_context|cost_control|auto",
    "query": "以低空经济产业链安全为主线的假设是否成立？",
    "context_summary": "正在撰写湖南省低空经济十五五规划研究，已完成产业全景分析，目前处于Issue Tree构建阶段，初始假设为'核心瓶颈是应用场景盈利模式不清晰'",
    "use_count": 1,
    "max_uses": 3
  },
  "use_skill_instruction": "请调用 use_skill('湘小策') 进行顾问咨询"
}
```

#### 2.2.5 顾问咨询响应消息（IPC-ADVISOR-RES）(v1.2新增)

湘小策返回结构化建议：

```json
{
  "protocol_version": "1.2",
  "message_type": "ADVISOR_RESPONSE",
  "message_id": "IPC-ADV-RES-2026-XXXXXX",
  "timestamp": "2026-04-10T13:30:30+08:00",
  "sender": {
    "agent": "湘小策",
    "agent_skill_id": "湘小策"
  },
  "reference": {
    "request_id": "IPC-ADV-REQ-2026-XXXXXX"
  },
  "payload": {
    "advisor_type": "strategy",
    "confidence": "high",
    "advice_items": [
      {"id": 1, "suggestion": "以产业链安全为主线而非规模增长", "rationale": "地缘环境下安全叙事更有政策穿透力", "priority": "high"},
      {"id": 2, "suggestion": "补充国际对标维度", "rationale": "韩国/日本对比可增强说服力", "priority": "medium"},
      {"id": 3, "suggestion": "历史回顾压缩至1段", "rationale": "读者更关心前瞻性判断", "priority": "low"}
    ],
    "warning_if_ignored": "若忽略建议1，报告可能被认为'缺乏战略高度'",
    "token_count": 280
  },
  "tracking": {
    "use_count": 1,
    "max_uses": 3,
    "remaining_uses": 2
  }
}
```

### 2.3 use_skill调用映射（v1.2增强）

湘小协作为协调器，负责将IPC消息翻译为具体的use_skill调用：

| IPC场景 | use_skill调用 | 参数 | 说明 |
|--------|-------------|------|------|
| Generator发起评估 | `use_skill('湘小法')` | mode='全维模式', file=[文件路径], round=[轮次] | 启动湘小法合规审查 |
| **Generator发起顾问咨询** (v1.2) | `use_skill('湘小策')` | advisor_type=[类型], query=[问题], context_summary=[摘要], generator_agent=[名称] | 启动湘小策顾问咨询 |
| 评估结果汇总 | 内部处理 | 汇总IPC-EVAL-RES | 不调用外部Skill |
| 白板协作诊断 | `use_skill('湘小协')` | mode='白板诊断', file=[问题文件] | 启动白板协作 |
| 批量评估汇总 | 并行调用多个use_skill | 并行执行GE配对 | 批量模式 |
| 终稿会审 | `use_skill('ultrareview')` | mode='加强版', file=[终稿] | 启动ultrareview |

---

## 三、执行模式（v1.1增强）

### 3.1 手动模式（默认·对外提交）

```
用户请求 → Generator生成 → 湘小协IPC请求消息
→ 湘小法评估（use_skill调用）→ 评估报告展示
→ 彭总决策：通过/修改/重写
→ 如修改：Generator修改 → 再次评估（最多3轮）
→ ultrareview会审 → 湘小法终审 → 提交
```

### 3.2 自动模式（内部产出·非关键文件）

```
Generator生成 → 湘小协自动评估请求
→ 评分≥34：自动通过
→ 评分30-33：Generator自动修改→再评估
→ 评分<30：Generator自动重写
→ 3轮未达34分：提交彭总人工决策
```

### 3.3 批量模式（大型项目·v1.1详细流程）

适用于十五五规划等大型项目，多个Agent并行产出后统一评估：

**Step 1：开题规划（ultraplan主持）**
- ultraplan Phase4输出Agent分工表，直接映射为GE配对计划
- 湘小协接收分工表，生成IPC批处理计划

**Step 2：并行生成**
```
Agent A（产业链分析）──→ IPC-REQ-01 ──┐
Agent B（数据分析）───→ IPC-REQ-02 ──┼──→ 湘小协（IPC路由）
Agent C（宏观研判）───→ IPC-REQ-03 ──┘
```

**Step 3：并行评估（IPC并发）**
```
湘小数（IPC-RES-01，数据核查）
湘小报（IPC-RES-02，政策对标）──→ 湘小协汇总评估报告
湘小法（IPC-RES-03，合规审查）
```

**Step 4：整改与二次评估**
- 湘小协向各Agent下发整改清单
- 各Agent并行修改（湘小协监控Token消耗）
- 湘小法二次评估

**Step 5：整合终稿**
```
ultraplan主持 → 整合通过文件 → ultrareview会审（7人加强配置）
→ 湘小法终审 → 最终报告
```

---

## 四、白板协作Step-by-Step（v1.1详细流程）

### 4.1 适用场景

白板协作在以下场景与GE流水线联动：

| 场景 | 触发时机 | 作用 | 参与者 |
|-----|---------|------|-------|
| 框架设计争议 | Generator初稿框架被Evaluator打回 | 诊断问题根源，重新设计框架 | Generator+Evaluator+湘小协 |
| 假设验证 | Generator假设被数据否定 | 修正假设，重新生成 | Generator+湘小协 |
| 结论冲突 | Evaluator结论与Generator结论矛盾 | 中立仲裁，达成共识 | Generator+Evaluator+专家 |
| 大型课题启动 | ultraplan Phase5后 | 验证Issue Tree，确定关键假设 | 全体Agent代表 |

### 4.2 白板协作标准流程（v1.1详细版）

```
┌─────────────────────────────────────────────────────────────┐
│              白板协作会议流程（麦肯锡标准·Step-by-Step）        │
├─────────────────────────────────────────────────────────────┤
│  ⏱  Step 1：开场与目标对齐（5分钟）                           │
│     ├── 主持人宣布议题和目标（湘小协担任默认主持人）             │
│     ├── 确认参与者角色：Generator（陈述方）/Evaluator（挑战方） │
│     ├── 记录人在白板顶部书写"核心问题"                          │
│     └── 主持人确认边界：本次白板只解决[具体问题]，不跑题        │
│                                                              │
│  ⏱  Step 2：Generator初始假设陈述（10分钟）                    │
│     ├── Generator用3分钟陈述初始假设（一句话结论）               │
│     ├── Generator用5分钟说明支撑证据                           │
│     ├── Evaluator用2分钟确认理解（复述Generator的假设）         │
│     └── 记录人将假设写在白板顶部                                │
│                                                              │
│  ⏱  Step 3：Evaluator挑战与Issue Tree构建（20分钟）             │
│     ├── Evaluator逐条挑战Generator的假设（用"所以？"追问）       │
│     ├── 记录人将每个质疑点记录在白板左侧                        │
│     ├── Generator逐条回应，记录回应结论                        │
│     ├── 主持人引导构建Issue Tree（用mckinsey-mece）             │
│     └── 识别关键驱动因素（80/20法则）                          │
│                                                              │
│  ⏱  Step 4：假设验证状态确认（5分钟）                          │
│     ├── 全体参与者对每个假设投票：✅ 已验证 / 🔄 待验证 / ❌ 被否定│
│     ├── 主持人宣布"被否定的假设"和"待验证假设"清单              │
│     └── Generator接受验证结论                                  │
│                                                              │
│  ⏱  Step 5：修正方案与任务分配（5分钟）                        │
│     ├── Generator提出修正方案                                 │
│     ├── Evaluator确认修正是否充分                               │
│     ├── 主持人分配后续验证任务（指定Agent+截止时间）            │
│     └── 约定下次白板复盘时间                                   │
│                                                              │
│  ⏱  输出物（会后5分钟内生成）                                  │
│     ├── 白板纪要：[日期]_[议题]_白板纪要.md                    │
│     ├── 假设验证状态表                                        │
│     ├── 后续任务清单（含Agent+截止时间）                       │
│     └── 修正后的Issue Tree（更新版）                           │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 白板纪要模板（v1.1新增）

```markdown
# [日期]_[议题]_白板纪要.md

> 会议时间：YYYY-MM-DD HH:MM ~ HH:MM
> 参与者：Generator（[Agent名称]）/ Evaluator（湘小法）/ 主持人（湘小协）
> 会议目的：[具体问题]

## 核心结论（初始假设）
[Generator的初始假设一句话总结]

## Evaluator挑战清单
| 挑战编号 | 挑战内容 | Generator回应 | 最终结论 |
|---------|---------|--------------|---------|
| 1 | [挑战1] | [回应] | ✅ 已解决 / 🔄 待验证 / ❌ 被否定 |

## 假设验证状态
| 假设编号 | 假设描述 | 验证状态 | 支撑/否定依据 |
|---------|---------|---------|-------------|
| H1 | [假设1] | ✅ 已验证 | [依据] |
| H2 | [假设2] | 🔄 待验证 | 需[具体验证方法] |

## 修正方案
[Generator承诺的修正方案]

## 后续任务
| 任务 | 负责人Agent | 截止时间 | 交付物 |
|-----|-----------|---------|-------|
| [任务1] | [Agent] | [日期] | [文件] |

## 下次白板复盘
时间：[日期+时间]
待解决问题：[清单]
```

### 4.4 假设验证会议（每项目关键节点）

| 项目节点 | 会议目的 | 输出物 | 必须参加 |
|---------|---------|-------|---------|
| 项目启动（ultraplan后） | 验证Issue Tree假设框架 | Issue Tree终稿+关键假设清单 | 是 |
| 中期汇报（完成30%） | 验证核心假设是否成立 | 假设验证状态表+结论修正方案 | 是 |
| 终稿前（ultrareview前） | 验证结论是否支撑假设 | 最终假设评级（A/B/C/D） | 是 |

**假设评级标准**：
- **A级**：假设有2个以上独立数据源强力支撑，可直接使用
- **B级**：假设有1个数据源支撑，需补充验证后可使用
- **C级**：假设支撑不足，需要调整结论或补充研究
- **D级**：假设被数据证伪，需重新构建假设框架

---

## 五、上下游接口规范（v1.1新增）

### 5.1 与ultraplan的衔接

**输入**：ultraplan Phase5输出的Agent分工方案

**转换规则**：
- ultraplan Phase4的Agent分工表 → 湘小协GE配对计划
- 每个Generator-Agent自动配置对应的Evaluator-Agent
- 评估触发条件继承ultraplan的风险矩阵（R类风险→强制评估）

```json
{
  "interface": "ultraplan_to_xie",
  "input_file": "[ultraplan Phase5报告路径]",
  "mapping_rule": {
    "Generator_Agent_N": "GE-0N",
    "风险矩阵R1-R5": "强制评估（必须GE配对）",
    "风险矩阵R6-R11": "建议评估（可选GE配对）"
  }
}
```

### 5.2 与ultrareview的衔接

**触发条件**：Generator经过GE流水线通过（评分≥34）后，进入ultrareview会审

**传递信息**：
- 最终通过版本的GE评分汇总
- P0/P1问题修复记录
- 湘小法终审意见摘要

```json
{
  "interface": "xie_to_ultrareview",
  "trigger": "GE流水线通过（评分≥34）",
  "input": {
    "final_score": 35,
    "ge_rounds": 2,
    "critical_issues_fixed": ["P0-1", "P0-2"],
    "remaining_warnings": ["P1-3（已标注，可选择修复）"]
  },
  "recommended_config": "ultrareview加强版（7人）"
}
```

### 5.3 完整链路：三件套协同全景

```
彭总：/开题 [课题名]
    │
    ▼
【ultraplan v1.1】
Phase1→2→3→4→5
    │
    ├──→ Phase4 Agent分工方案
    │
    ▼
【湘小协 v1.1】（IPC协调层）
    ├──→ GE配对计划生成
    ├──→ IPC消息路由
    └──→ 质量门禁决策
    │
    ▼
【Generator Agents】
（并行执行）
    │
    ▼
【湘小法 Evaluator】（IPC评估）
    │
    ▼
【湘小协 汇总决策】
    ├── 评分≥34 → ultrareview加强版会审
    ├── 评分30-33 → Generator修改 + 复评
    └── 评分<30 → 打回 + 白板协作诊断
    │
    ▼
【ultrareview v1.1】（7人会审）
    │
    ▼
【湘小法 终审】
    │
    ▼
【输出/提交】
```

---

## 六、湘小协快捷指令（v1.1新增）

| 指令 | 说明 | 适用场景 |
|------|------|---------|
| `/协调整合` | 启动GE流水线协调模式 | 复杂项目执行 |
| `/协调整合 --自动` | 启动自动GE流水线 | 内部非关键产出 |
| `/协调整合 --批量` | 启动批量GE流水线 | 十五五规划等多Agent项目 |
| `/白板诊断 [文件]` | 启动白板协作诊断 | Generator被打回时 |
| `/白板启动 [议题]` | 启动假设验证白板 | 大型课题启动 |
| `/GE状态` | 查看当前GE流水线执行状态 | 监控进度 |
| `/GE通过 [GE编号]` | 手动标记某GE配对通过 | 加速非关键环节 |
| `/GE跳过 [GE编号]` | 跳过某GE配对评估 | 内部中间产出 |

---

## 七、质量门禁规则

### 7.1 强制评估（不可跳过）

| 产出类型 | 评估模式 | 原因 |
|---------|---------|------|
| 向上级提交的方案/专报 | 全维GE + ultrareview加强 | 政治敏感+合规风险 |
| 对外发布的公众号内容 | 内容GE + ultrareview标准 | IP风险+传播影响 |
| 对外交付的咨询报告 | 全维GE + ultrareview加强 | 合同履约+客户信任 |
| 投资尽调报告 | 投研GE + ultrareview加强 | 投资决策+国有资产 |
| 对外合同/协议 | 法律GE（湘小法） | 法律风险 |

### 7.2 可选评估（建议但不强制）

- 内部工作文档（建议GE-10通用模式）
- 数据分析中间结果（建议湘小数数据核查）
- 个人备忘/笔记（跳过GE）
- Agent间中间数据传递（由ultraplan指定）

### 7.3 顾问层质量指标（v1.2新增）

顾问咨询情况纳入质量门禁的综合评估：

| 指标 | 计算方式 | 质量信号 |
|------|---------|---------|
| 顾问咨询次数 | 任务中湘小策被调用的次数 | 0次：可能未充分利用；≥3次：充分校准 |
| 建议采纳率 | 采纳/(采纳+部分采纳+忽略) | ≥70%：积极校准；<30%：可能抗拒校准 |
| 顾问类型分布 | strategy/methodology/soe_context/cost_control的使用比例 | 均衡使用：方法论全面；单一类型：可能存在盲区 |
| 顾问效能提升 | 有顾问校准 vs 无校准的湘小法评分差 | 差值≥3分：顾问效能显著 |

### 7.4 顾问增强的质量门禁（v1.2新增）

```
质量门禁五层流水线（v1.2完整版）：

Layer 1: Generator 生成初稿
    ↓
Layer 2: 湘小策 顾问咨询（事中校准，0-3次）
    ↓
Layer 3: MECE自检
    ↓
Layer 4: 湘小法 评估（事后质量门禁，37分制）
    ↓  ≥34分 → 通过
    ↓  30-33分 → 修改→再评估（最多3轮）
    ↓  <30分 → 打回重写
Layer 5: 白板协作（如需要诊断方向性问题）
    ↓
ultrareview 会审 → 终审 → 提交
```

---

## 九、任务复杂度评估模块（v1.2新增）

> 来源：借鉴Claude Advisor Strategy的模型路由理念，对任务进行复杂度分级，决定GE流水线强度和顾问咨询频次。

### 9.1 三层复杂度定义

| 复杂度 | 特征描述 | 代表任务类型 | GE强度 | 顾问次数 |
|-------|---------|------------|--------|---------|
| **simple（简单）** | 有明确答案；单一维度；数据完整；不需要战略判断 | 数据查询、快速简报、单一指标汇总 | 跳过GE或可选GE | 0次 |
| **complex（复杂）** | 多维度分析；部分数据缺失；需要战略判断；涉及合规 | 产业分析、专报撰写、政策研究报告 | 强制GE（湘小法） | 1-3次 |
| **highly_complex（极高）** | 框架不确定；多主体博弈；数据高度缺失；高政治敏感 | 十五五规划、国资改革顶层设计、省级课题 | 强制GE+ultrareview加强+白板协作 | 3-5次 |

### 9.2 复杂度评估维度

每个任务接收后，按以下5个维度进行快速评估（湘小协自动判断，也可人工指定）：

| 评估维度 | 评估问题 | 权重 |
|---------|---------|------|
| **框架清晰度** | 任务框架是否明确？有无先例可循？ | 20% |
| **数据完整性** | 所需数据是否可获取？数据质量如何？ | 20% |
| **利益相关者数量** | 涉及多少个独立主体？是否有冲突诉求？ | 20% |
| **政治敏感性** | 产出是否涉及上级汇报？是否含敏感领域？ | 25% |
| **时间紧迫度** | 截止时间是否紧张？是否有快速交付压力？ | 15% |

**评分规则**：每个维度1-5分，加权总分：
- 总分≥4.0 → **highly_complex**
- 总分2.5-4.0 → **complex**
- 总分<2.5 → **simple**

### 9.3 复杂度-路由规则对照表

| 规则项 | simple | complex | highly_complex |
|-------|--------|--------|---------------|
| Generator | 直接执行 | 标准Generator | Generator + 顾问（Layer2） |
| GE配对 | 可选（湘小法通用模式） | 强制（湘小法相关模式） | 强制（湘小法全维模式） |
| 顾问咨询 | 0次（不调用湘小策） | 1-3次（按需触发） | 3-5次（固定节点必调） |
| 白板协作 | 不需要 | 被打回时启动 | 必做（启动+中期各1次） |
| ultrareview | 不需要 | 建议（标准版） | 强制（加强版7人） |
| Token预算 | 基础 | 标准×1.5 | 标准×2.5 |
| max_uses | 0 | 3 | 5 |

### 9.4 快速判断口诀

在接收任务时，用以下口诀快速判断复杂度：

> **简单任务**：数据直接查，结论很明确，没有新观点
> **复杂任务**：框架要设计，多方要平衡，表述要斟酌
> **极高复杂**：没有先例，利益冲突，政治敏感，时间紧迫

---

## 八、版本历史

- v1.0.0（2026-04-05）：初始版本，基于Claude Code Harness Engineering设计，实现Generator-Evaluator配对协议
- v1.1.0（2026-04-10）：新增IPC通信协议实现层（JSON消息格式+use_skill调用映射）、白板协作Step-by-Step详细流程、白板纪要模板、假设验证会议规范、与ultraplan/ultrareview上下游接口、快捷指令扩展、批量模式详细流程
- v1.2.0（2026-04-10）：新增IPC-ADVISOR-REQ/RES消息类型（顾问咨询协议）、顾问层质量指标体系、五层质量门禁流水线（Generator→顾问→MECE→评估→白板）、use_skill调用映射表新增湘小策条目
- v1.2.1（2026-04-10）：新增第九节"任务复杂度评估模块"，三层复杂度（simple/complex/highly_complex）定义、评估维度、加权评分规则、路由对照表、快速判断口诀
