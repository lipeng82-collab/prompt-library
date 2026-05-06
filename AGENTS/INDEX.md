# 专业 Agent 矩阵

> 6个专项研究 Agent，支撑深度研究工作流
> 最后更新：2026-05-06

---

## Agent 清单

| Agent | 目录名 | 功能 | 触发词 |
|-------|--------|------|--------|
| 产业分析Agent | industry-chain-analysis | 产业链与产业政策分析 | 产业链、产业分析、竞争格局 |
| 数据分析Agent | data-analysis-xt | 数据量化与可视化 | 数据分析、数据采集、可视化 |
| 宏观经济Agent | china-macro-analyst | 宏观政策研判 | 宏观经济、政策研判、趋势分析 |
| 深度研究Agent | deep-research | 系统框架与专题研究 | 深度研究、研究报告、系统分析 |
| 学术研究Agent | academic-research | 文献综述与CSSCI | 学术论文、文献综述、期刊投稿 |
| 专报撰写Agent | policy-report-writer | 专报撰写与优化 | 专报撰写、智库专报、政策建议 |

---

## Agent 协作流程

### 典型研究项目流程

```
1. 大总管接收任务
   │
2. deep-research（深度研究Agent）
   │  → 输出：研究框架 + 关键问题清单
   │
3. 并行执行
   ├── industry-chain-analysis → 产业链图谱
   ├── china-macro-analyst → 宏观政策研判
   ├── academic-research → 文献综述
   └── data-analysis-xt → 数据支撑
   │
4. policy-report-writer（专报撰写Agent）
   │  → 输出：专报初稿
   │
5. 湘小协（GE对抗协调）
   │  → Generator产出 + Evaluator审校
   │
6. 湘小法（七律审核）+ 湘小印（文档出品）
   → 最终交付
```

---

## Agent 与 Skill 依赖

| Agent | 依赖的湘字号 Skill |
|-------|-------------------|
| industry-chain-analysis | 湘小研（政策检索）、湘小数（数据分析） |
| data-analysis-xt | 湘小数（数据分析）、湘小印（文档出品） |
| china-macro-analyst | 湘小研（政策检索）、湘小策（顾问） |
| deep-research | 湘小研（政策检索）、湘小档（决策记忆） |
| academic-research | 湘小研（政策检索）、湘小策（顾问） |
| policy-report-writer | 湘小印（文档出品）、湘小法（七律审核） |

---

## Agent 使用场景

| 场景 | 推荐 Agent | 配合 Skill |
|------|-----------|-----------|
| 课题申报 | deep-research + academic-research | 湘小研、湘小印 |
| 产业分析报告 | industry-chain-analysis + data-analysis-xt | 湘小数、湘小印 |
| 政策专报 | policy-report-writer + china-macro-analyst | 湘小法、湘小印 |
| 资信评估 | data-analysis-xt + deep-research | 湘小查、湘小法 |
| 学术论文 | academic-research | 湘小研、湘小策 |
