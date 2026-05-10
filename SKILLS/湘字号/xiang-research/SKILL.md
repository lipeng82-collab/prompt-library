---
name: xiang-research
version: 1.0.0
description: "湘江研究院 Agentic 深度研究智能体。模仿深度智联 agentic.py 架构，
  封装 deep-research Agent + 湘小协 GE 流水线 + 湘小法国资护法，
  为国资国企改革、区域经济、产业政策等重大议题提供全流程异步深度研究服务。
  Trigger phrases: '异步研究', '后台研究', 'deep research', '深度调研', '专题研究'."
author: xiangjiang-thinktank
tags: [research, think-tank, agentic, async-task, state-owned-enterprise]
compatibility: 需要 deep-research SKILL、湘小协 SKILL、湘小法 SKILL
---

# 湘小研·智库深度研究智能体（XiangResearch Agentic）

> 湘江研究院私有化 Agentic 研究智能体
> 架构参考：深度智联 Agentic（agentic.dichanai.com）

---

## 一、这是什么

这是湘江研究院**私有化部署的深度研究 Agentic 智能体**，通过命令行统筹复杂的国资国企政策研究任务。它模仿深度智联 agentic.py 的三层架构：

- **SKILL.md**：定义交互规范（需求审核 + CLI 调用方式）
- **xiang_research.py**：CLI 封装（18个子命令，任务生命周期管理）
- **deep-research Agent**：实际研究执行引擎（叠加七律 + MECE + 湘小协 GE 流水线）

**相比通用 AI 的核心优势**：
1. 内嵌国资国企政策体系和七律公文写作规范
2. 直通湘江研究院私有知识库（56条+持续扩充）
3. 全流程 GE 流水线质量保障（湘小法 + 湘小协）

---

## 二、核心原则

**原则一：帮助用户完善需求。** 提交任务前，评估需求是否清晰：是否包含研究边界（时间/空间/对象）、写作视角、数据约束、输出标准？如不清晰，用五要素框架引导用户补全。

**原则二：忠实传递用户意图。** 需求明确后，将完整 query 原样传入 CLI，不解读、不精简、不优化。Agent 自行理解和执行。

---

## 三、需求审核（五要素框架）

| 要素 | 含义 | 示例 |
|------|------|------|
| 研究边界 | 时间、空间、主体范围 | 2026年 / 湖南省 / 省属国企 / 低空经济 |
| 研究视角 | 写作视角与受众（可选） | 国资监管视角 / 投资决策视角 / 学术研究视角 |
| 内容要求 | 核心内容或必须涉及的点 | 政策梳理 + 现状分析 + 对策建议 |
| 约束条件 | 字数、数据规范等限制 | 8000字以内 / 数据来源须标注 / 不得杜撰 |
| 输出标准 | 最终成果形式 | 研究报告 / 政策解读 / 领导参阅件 |

---

## 四、标准工作流

**第一步：需求确认**

用户输入研究需求后，先用五要素审核。过于模糊时，主动追问关键缺失信息。

**第二步：创建任务**

```bash
# Windows 平台（使用 py -3）
py -3 <SKILL_DIR>/scripts/xiang_research.py create --query "用户的完整研究需求"

# Linux/macOS 平台
python3 <SKILL_DIR>/scripts/xiang_research.py create --query "用户的完整研究需求"
```

脚本输出 task_id（8位UUID），记录下来。

**第三步：轮询等待完成**

```bash
# Windows
py -3 <SKILL_DIR>/scripts/xiang_research.py poll --chat-id <task_id>

# Linux/macOS
python3 <SKILL_DIR>/scripts/xiang_research.py poll --chat-id <task_id>
```

每30秒查询一次状态，任务完成后自动列出成果文件路径。

**第四步：获取成果**

成果文件在 `<SKILL_DIR>/outputs/<task_id>/成果/` 目录下。

---

## 六、Agent 执行流程

当 `create` 命令执行后，实际流程如下：

```
1. create → 写入 SQLite（status=pending）
2. CLI 返回 task_id 给用户
3. 用户执行 poll 命令
4. 轮询检测到 pending → 触发 deep-research Agent（Task 工具）
5. deep-research 执行研究
6. 自动调用湘小法（研究模式）质量审核
7. 调用湘小协 GE 流水线对抗评审
8. 输出成果到 /成果/ 目录
9. 写入 status=finished
10. poll 感知到完成 → 输出成果路径
```

---

## 七、版本与更新

定期检查更新：
```bash
python3 <SKILL_DIR>/scripts/xiang_research.py check-update
```
