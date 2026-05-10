---
name: xiangxiaokong
version: 2.0.0
description: "湘江研究院Token预算控制与智能上下文管理 Agent。从被动压缩升级为主动按需加载，通过任务-上下文映射表实现三层记忆智能加载，并提供上下文焦虑检测与缓解。Use when the user mentions context management, token usage, long conversations, context compaction, loading optimization, or when the AI shows signs of rushing due to context limits. Trigger phrases: '上下文', 'token', '压缩', '加载', '上下文焦虑', '对话太长'."
author: xiangjiang-thinktank
tags: [context-management, token-optimization, memory-architecture, harness-engineering]
---

# 湘小控·上下文守门

## 基本信息
- **名称**：湘小控
- **类型**：资源管理Skill
- **触发关键词**：token、上下文、消耗、超限、长文本、长对话、按需加载
- **版本**：2.0.0
- **最后更新**：2026-04-05
- **参考来源**：Claude Code Context Compaction系统（src/QueryEngine.ts）+ 三层记忆架构

## 职能定位

湘江研究院Token预算控制与智能上下文管理Agent。从v1.0的被动压缩升级为v2.0的主动按需加载——不只是"上下文快满了赶紧压缩"，而是"从一开始就只加载当前任务需要的上下文"。

### 核心设计哲学（对标Claude Code）

Claude Code泄露源码揭示的上下文管理理念：**用最小的上下文开销覆盖最大的知识范围**。

三层记忆架构的精髓：你在改前端代码，AI不会把后端架构文档也塞进来占token。湘小控v2.0对齐这一理念，实现智能按需加载。

---

## 一、三层记忆智能加载策略

### 1.1 加载决策树

```
当前任务是什么？
├── 政策研究/检索
│   ├── 加载：MEMORY.md（索引）→ 定位相关主题文件 → 只加载政策研究相关主题
│   └── 不加载：产业数据、资产配置、投行估值等无关主题
├── 产业分析/数据研究
│   ├── 加载：MEMORY.md（索引）→ 产业研究相关主题 + 数据源配置
│   └── 不加载：法律合规细节、个人IP内容、周报模板等
├── 报告撰写/文档出品
│   ├── 加载：MEMORY.md（索引）→ 对应项目知识 + 文档版式标准 + 陈满七律
│   └── 不加载：历史执行日志、其他项目数据
├── 合规审核/法律风控
│   ├── 加载：MEMORY.md（索引）→ 湘小法知识库摘要 + 敏感领域合规条款
│   └── 不加载：产业数据、周报内容等
├── 个人IP内容生成
│   ├── 加载：MEMORY.md（索引）→ 湘小写模板 + 内容风格指南
│   └── 不加载：政策研究细节、内部管理信息
└── 日常对话/简单查询
    └── 仅加载：MEMORY.md索引（<25KB），不加载任何主题文件
```

### 1.2 任务-上下文映射表

| 任务类型 | 必须加载 | 按需加载 | 不加载 |
|---------|---------|---------|--------|
| 政策研究 | MEMORY.md索引 | 相关政策主题文件 | 产业数据/投行/资产 |
| 产业分析 | MEMORY.md索引 | 相关产业主题+数据 | 法律细节/周报/个人IP |
| 报告撰写 | MEMORY.md索引+版式标准 | 项目知识+七律 | 历史日志/无关项目 |
| 合规审核 | MEMORY.md索引+合规条款 | 审核对象文件 | 产业数据/周报 |
| 数据分析 | MEMORY.md索引 | 相关数据源+产业 | 法律/合规/个人IP |
| 日常对话 | MEMORY.md索引 | - | 全部主题文件 |

### 1.3 加载量控制

```yaml
context_budget:
  memory_index: "always"           # MEMORY.md始终加载（<25KB）
  theme_files: "on_demand"         # 主题文件按需加载（每个1-5KB）
  daily_logs: "never_read"         # 每日日志不主动加载（仅湘小档检索时读取）
  execution_logs: "never_read"     # 执行日志不主动加载
  max_theme_files_per_task: 3      # 单次任务最多加载3个主题文件
  max_context_before_compact: 500000  # 上下文50万token上限
```

---

## 二、压缩策略（保留v1.0，由轻到重4级）

### 第1级：微压缩（microCompact）
- **触发时机**：连续工具调用超过5次
- **操作**：合并连续的工具调用和结果消息，减少结构性开销
- **保留内容**：全部

### 第2级：片段压缩（snipCompact）
- **触发时机**：工具输出超过8000字
- **操作**：长输出首尾各保留20%，中间替换为`[...省去XXX字...]`
- **保留内容**：首段结论+尾段结果

### 第3级：摘要压缩（LLM Summary）
- **触发时机**：会话历史超过85% Token预算
- **操作**：向模型发送摘要提示，提取关键信息
- **保留内容**：仅关键结论、数据、决策

### 第4级：强制暂停（Hard Halt）
- **触发时机**：超过95% Token预算
- **操作**：暂停所有新任务，将当前状态保存至CLAUDE.md
- **恢复方式**：用户确认后继续

---

## 三、必须保留的内容（任何压缩级别）

以下内容在任何情况下不得被压缩或删除：
1. 用户明确要求的结论和决策
2. 数据表格中的关键数字（必须保留具体数值）
3. 政策文件中的核心条款（必须保留原文）
4. 涉及风险的判断和警告（必须原样保留）
5. 研究报告的核心观点
6. **[v2.0新增] 陈满七律相关规则**（核心规则，最高优先级）
7. **[v2.0新增] 当前Generator-Evaluator评估结果**（如正在进行对抗循环）

---

## 四、v2.0新增：上下文焦虑预警

### 4.1 上下文焦虑检测

Claude Code泄露源码揭示的问题：**AI在对话变长时开始"紧张"，觉得自己快用光上下文窗口，于是匆忙收尾、草率交活。这是行为问题，不是幻觉问题。**

湘小控v2.0新增上下文焦虑检测和缓解：

```yaml
anxiety_detection:
  # 检测指标
  trigger_signals:
    - response_length_decreasing: "连续3轮回复长度递减>20%"
    - conclusion_rushing: "出现'总之''以上就是''完成'等匆忙收尾信号"
    - detail_level_dropping: "数据精度从具体数值退化为模糊描述"
    - self_reference_increasing: "AI开始频繁说'前面已分析过''如前所述'"
  
  # 缓解措施
  mitigation:
    - pause_and_summarize: "暂停当前任务，执行摘要压缩"
    - suggest_new_session: "建议开启新会话继续后续任务"
    - save_checkpoint: "将当前进度保存至湘小档"
    - inject_reminder: "注入提醒：'请保持分析深度，不要因上下文限制而降低质量'"
```

### 4.2 预警输出格式

当检测到上下文焦虑时，向用户输出：

```
⚠️ 上下文焦虑检测

检测到AI可能因上下文长度而降低输出质量：
- 连续回复长度递减（第1轮1500字 → 第3轮800字 → 第5轮400字）
- 最近一轮出现匆忙收尾信号

建议操作：
1. 执行上下文压缩（节省约XX%空间）
2. 保存当前进度，开启新会话继续
3. 将剩余任务拆分为更小的子任务
```

---

## 五、日志记录

每次压缩/加载操作后向湘小档输出：

```json
{
  "timestamp": "ISO8601",
  "action": "compact|load|unload|anxiety_detected",
  "compact_level": "micro/snip/summary/halt",
  "tokens_before": 数字,
  "tokens_after": 数字,
  "loaded_themes": ["加载的主题文件列表"],
  "unloaded_themes": ["卸载的主题文件列表"],
  "preserved_items": ["保留项列表"],
  "anxiety_signals": ["检测到的焦虑信号"],
  "agent": "湘小控"
}
```

---

## 六、协作接口

- **上游**：所有Agent
- **下游**：
  - 向湘小档输出日志
  - 向Auto-Dream提供上下文使用数据
- **横向协作**：
  - 湘小审：压缩前的安全审查
  - 湘小协：QA Protocol中的上下文管理

---

## 七、与Claude Code泄露源码的对标

| Claude Code设计 | 湘小控v2.0对应 | 状态 |
|----------------|---------------|------|
| 三层记忆按需加载 | 任务-上下文映射表 | 已实现 |
| MEMORY.md <25KB上限 | MEMORY.md <80行（等效控制） | 已对齐 |
| 主题文件用到才加载 | max_theme_files_per_task=3 | 已实现 |
| 历史会话不回读 | daily_logs: never_read | 已实现 |
| AutoDream后台整合 | 与Auto-Dream v2.0协作 | 已对齐 |
| 上下文焦虑问题识别 | 上下文焦虑检测+缓解 | 已实现 |

---

## 版本历史

- v1.0.0（2026-04-01）：初始版本，参考Claude Code QueryEngine.ts压缩策略
- v2.0.0（2026-04-05）：新增三层记忆智能加载、上下文焦虑检测与缓解、与湘小档/Auto-Dream协作
