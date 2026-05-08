# 湘江研究院AI体系迁移包

> 版本：v1.0 | 日期：2026年4月16日 | 适用：研究中心全体同事

## 包内容说明

本迁移包包含湘江研究院5层级AI体系的完整组件，支持一键迁移到同事的WorkBuddy环境。

### 目录结构

```
AI体系迁移包/
├── README.md                 # 本文件
├── skills/                   # 13个湘字号Skill + 6个专业Agent
│   ├── 湘小历/              # 工作记录与周报
│   ├── 湘小报/              # 政策简报
│   ├── 湘小研/              # 政策RAG检索
│   ├── 湘小数/              # 产业数据分析
│   ├── 湘小法/              # 合规风控
│   ├── 湘小印/              # 文档出品
│   ├── 湘小查/              # 背景调查
│   ├── 湘小审/              # 权限审批
│   ├── 湘小控/              # Token控制
│   ├── 湘小档/              # 执行日志
│   ├── 湘小协/              # GE协调
│   ├── 湘小策/              # 智能顾问
│   ├── 湘小镜/              # 对标分析
│   ├── industry-chain-analysis/      # 产业分析Agent
│   ├── data-analysis-xt/             # 数据分析Agent
│   ├── china-macro-analyst/          # 宏观经济Agent
│   ├── deep-research/                # 深度研究Agent
│   ├── academic-research/            # 学术研究Agent
│   └── policy-report-writer/         # 专报撰写Agent
├── automations/              # 自动化任务配置模板
│   ├── 周报生成.toml
│   └── 智库抓取.toml
├── knowledge-base/           # 知识库初始化模板
│   ├── init.bat             # Windows初始化脚本
│   ├── init.sh              # Mac/Linux初始化脚本
│   └── templates/           # 目录结构模板
├── scripts/                  # 安装脚本
│   ├── install.bat          # Windows一键安装
│   ├── install.sh           # Mac/Linux一键安装
│   └── verify.py            # 安装验证工具
└── docs/                     # 使用文档
    ├── 快速上手指南.md
    ├── Skill使用手册.md
    └── 常见问题FAQ.md
```

## 快速开始

### 方式一：一键安装（推荐）

**Windows用户：**
```bash
cd "AI体系迁移包"
scripts\install.bat
```

**Mac/Linux用户：**
```bash
cd AI体系迁移包
bash scripts/install.sh
```

### 方式二：手动安装

1. 复制 `skills/` 目录下所有文件夹到 `~/.workbuddy/skills/`
2. 复制 `automations/` 目录下的配置到 `~/.workbuddy/automations/`
3. 运行 `knowledge-base/init.bat` (Windows) 或 `knowledge-base/init.sh` (Mac/Linux)
4. 重启WorkBuddy

## 安装后验证

运行验证工具检查安装是否成功：

```bash
python scripts/verify.py
```

## 使用指南

详见 `docs/快速上手指南.md`

## 技术支持

如有问题，请联系：研究中心AI体系建设负责人
