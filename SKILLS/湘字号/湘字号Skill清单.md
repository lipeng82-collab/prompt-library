# 湘字号Skill清单

> 共13个Skill，分为4个类别

## 一、运营枢纽层（3个）

| Skill名称 | 目录名 | 功能定位 | 触发关键词 |
|-----------|--------|----------|------------|
| 湘小历 | xiangxiaoli | 工作记录与周报生成 | 记一下、工作记录、周报、日记 |
| 湘小报 | xiangxiaobao | 每日政策简报 | 政策简报、每日政策、政策追踪 |
| 湘小纪 | xiangxiaoji | 会议纪要标准化 | 会议纪要、会议记录、纪要整理 |

## 二、研究支撑层（5个）

| Skill名称 | 目录名 | 功能定位 | 触发关键词 |
|-----------|--------|----------|------------|
| 湘小研 | xiangxiaoyan | 政策RAG检索 | 政策检索、知识库查询、RAG检索 |
| 湘小数 | xiangxiaoshu | 产业数据分析 | 数据分析、产业数据、可视化 |
| 湘小法 | xiangxiaofa | 合规风控法务 | 合规审核、法律意见、风险评估 |
| 湘小印 | xiangxiaoyin | 文档标准化出品 | 转成Word、公文格式、文档出品 |
| 湘小查 | xiangxiaocha | 背景调查 | 背景调查、企业查询、尽职调查 |

## 三、Harness治理层（5个）

| Skill名称 | 目录名 | 功能定位 | 触发关键词 |
|-----------|--------|----------|------------|
| 湘小审 | xiangxiaoshen | 权限审批与安全 | 权限审批、风险评估、操作安全 |
| 湘小控 | xiangxiaokong | Token预算控制 | 上下文、token、压缩、加载 |
| 湘小档 | xiangxiaodang | 执行日志与决策记忆 | 执行记录、决策回溯、历史检索 |
| 湘小协 | xiangxiaoxie | GE对抗协调 | 质量对抗、Generator-Evaluator、审校流水线 |
| 湘小策 | xiangxiaoce | 智能顾问 | 顾问咨询、方向对吗、框架是否合理 |
| 湘小镜 | xiangxiaojing | AI成果对标分析 | 对标分析、成果对比、Benchmark |

## 四、专业Agent矩阵（6个）

| Agent名称 | 目录名 | 功能定位 | 触发关键词 |
|-----------|--------|----------|------------|
| 产业分析Agent | industry-chain-analysis | 产业链与产业政策分析 | 产业链、产业分析、竞争格局 |
| 数据分析Agent | data-analysis-xt | 数据量化与可视化 | 数据分析、数据采集、可视化 |
| 宏观经济Agent | china-macro-analyst | 宏观政策研判 | 宏观经济、政策研判、趋势分析 |
| 深度研究Agent | deep-research | 系统框架与专题研究 | 深度研究、研究报告、系统分析 |
| 学术研究Agent | academic-research | 文献综述与CSSCI | 学术论文、文献综述、期刊投稿 |
| 专报撰写Agent | policy-report-writer | 专报撰写与优化 | 专报撰写、智库专报、政策建议 |

## 安装说明

### 方式一：自动安装（推荐）

运行 `scripts/install.bat` (Windows) 或 `scripts/install.sh` (Mac/Linux)

### 方式二：手动安装

1. 从源地址复制以下Skill目录到 `~/.workbuddy/skills/`：
   - `xiangxiaoli/` → `~/.workbuddy/skills/xiangxiaoli/`
   - `xiangxiaobao/` → `~/.workbuddy/skills/xiangxiaobao/`
   - ...（以此类推）

2. 重启WorkBuddy即可使用

### 源地址

源Skill位于：`C:\Users\58460\.workbuddy\skills\`

## 依赖关系

```
湘小协 (协调器)
  ├── 依赖：湘小法 (Evaluator)
  ├── 依赖：湘小档 (日志)
  └── 依赖：湘小策 (顾问)

湘小历 (工作记录)
  ├── 依赖：湘小档 (日志归档)
  └── 依赖：湘小印 (文档出品)

专业Agent矩阵
  ├── 产业分析Agent
  ├── 数据分析Agent
  ├── 宏观经济Agent
  ├── 深度研究Agent
  ├── 学术研究Agent
  └── 专报撰写Agent
```

## 使用优先级建议

**新手入门（第1周）**：
1. 湘小历 - 记录日常工作
2. 湘小报 - 获取政策简报

**日常使用（第2-4周）**：
3. 湘小研 - 政策检索
4. 湘小印 - 文档出品
5. 湘小法 - 合规审核

**进阶应用（第1个月后）**：
6. 专业Agent矩阵 - 深度研究
7. Harness治理层 - 质量管控
