#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
湘小研 Agent 后台执行器
由 xiang_research.py 的 create 命令启动，以独立进程运行
负责：读取任务上下文 → 调用 deep-research Agent → 写入成果 → 更新状态
"""
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 参数：task_id, skill_dir
# ---------------------------------------------------------------------------
if len(sys.argv) < 3:
    print("Usage: _agent_runner.py <task_id> <skill_dir>")
    sys.exit(1)

task_id  = sys.argv[1]
skill_dir = Path(sys.argv[2])
db_path  = skill_dir / "tasks.db"
out_dir  = skill_dir / "outputs" / task_id

# ---------------------------------------------------------------------------
# 数据库
# ---------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(str(db_path))
    return conn

def mark_status(conn, status, error=""):
    now = datetime.now().isoformat()
    extra = f", finished_at = '{now}'" if status in ("finished", "error", "aborted") else ""
    if error:
        conn.execute(
            f"UPDATE tasks SET status = ?, updated_at = ?, error_msg = ? {extra} WHERE id = ?",
            [status, now, error, task_id]
        )
    else:
        conn.execute(
            f"UPDATE tasks SET status = ?, updated_at = ? {extra} WHERE id = ?",
            [status, now, task_id]
        )
    conn.commit()

# ---------------------------------------------------------------------------
# 主执行流程
# ---------------------------------------------------------------------------
def run():
    conn = get_conn()
    ctx_file = out_dir / "_context.json"

    if not ctx_file.exists():
        mark_status(conn, "error", f"任务上下文文件不存在：{ctx_file}")
        return

    ctx = json.loads(ctx_file.read_text(encoding="utf-8"))
    query  = ctx["query"]
    domain = ctx.get("domain", "通用")

    mark_status(conn, "running")
    print(f"[{task_id}] Agent 启动，研究主题：{query[:40]}...")

    try:
        # ── 阶段一占位：写成果占位文件 ─────────────────────────────────
        # 阶段二替换为真实 deep-research Agent 调用
        # 阶段三集成湘小协 GE 流水线 + 湘小法质量审核
        # ──────────────────────────────────────────────────────────────

        result_dir = out_dir / "成果"
        result_dir.mkdir(parents=True, exist_ok=True)

        output_file = result_dir / f"深度研究报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_file.write_text(
            f"""# 【占位成果】{query[:60]}

> Task ID：{task_id}
> 领域：{domain}
> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 研究概要

本报告由湘小研 Agentic 智能体生成。

**研究主题**：{query}

**执行状态**：阶段一框架就绪

## 说明

当前为湘小研 Agentic CLI 阶段一框架，Agent 执行引擎已就位：
- ✅ 任务创建（create）
- ✅ 状态管理（status/poll/list）
- ✅ SQLite 持久化
- ✅ 成果目录管理

**阶段二**将接入 deep-research Agent 执行真实研究任务。
**阶段三**将集成湘小协 GE 流水线 + 湘小法三维质量审核。

---
*湘江研究院研究中心 · 湘小研 Agentic 智能体 · {datetime.now().strftime('%Y-%m-%d')}*
""",
            encoding="utf-8"
        )

        mark_status(conn, "finished")
        print(f"[{task_id}] 完成！成果已写入：{output_file}")

    except Exception as e:
        mark_status(conn, "error", str(e))
        print(f"[{task_id}] 执行出错：{e}")

if __name__ == "__main__":
    run()
