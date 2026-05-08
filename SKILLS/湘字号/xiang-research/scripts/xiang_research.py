#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
湘小研·智库深度研究智能体 CLI
对标深度智联 agentic.py，提供完整异步研究任务管理能力

用法示例：
  python xiang_research.py create --query "研究湖南省低空经济发展路径"
  python xiang_research.py poll --chat-id a1b2c3d4
  python xiang_research.py status --chat-id a1b2c3d4
  python xiang_research.py list
  python xiang_research.py abort --chat-id a1b2c3d4
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from threading import Thread

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
SKILL_DIR = Path(__file__).parent.parent
DB_PATH   = SKILL_DIR / "tasks.db"
OUT_DIR   = SKILL_DIR / "outputs"
SKILL_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

POLL_INTERVAL = 30   # 轮询间隔（秒）
POLL_TIMEOUT  = 7200 # 默认超时2小时

# ---------------------------------------------------------------------------
# 数据库初始化
# ---------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id           TEXT PRIMARY KEY,
            title        TEXT,
            query        TEXT,
            domain       TEXT DEFAULT '通用',
            status       TEXT DEFAULT 'pending',
            agent_name   TEXT DEFAULT 'deep-research',
            output_dir   TEXT,
            created_at   TEXT,
            updated_at   TEXT,
            finished_at  TEXT,
            error_msg    TEXT
        )
    """)
    conn.commit()
    return conn

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def task_dir(task_id: str) -> Path:
    return OUT_DIR / task_id

def mark_status(conn, task_id: str, status: str, error: str = ""):
    now = datetime.now().isoformat()
    extra = f", finished_at = '{now}'" if status in ("finished", "error", "aborted") else ""
    extra2 = f", error_msg = ? " if error else ""
    vals = [task_id]
    if error:
        vals.append(error)
    conn.execute(
        f"UPDATE tasks SET status = ?, updated_at = ? {extra2} {extra} WHERE id = ?",
        [status, now] + ([error] if error else []) + [task_id]
    )
    conn.commit()

# ---------------------------------------------------------------------------
# Agent 执行器（被 poll 触发）
# ---------------------------------------------------------------------------
def run_agent_async(task_id: str, query: str, domain: str):
    """
    后台线程：调用 deep-research Agent 执行研究任务
    完成后写入成果文件并更新状态
    """
    conn = get_conn()
    td = task_dir(task_id)

    try:
        mark_status(conn, task_id, "running")

        # 写入研究上下文文件（供 Agent 读取）
        ctx_file = td / "_context.json"
        ctx_file.write_text(json.dumps({
            "task_id": task_id,
            "query": query,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "instructions": (
                "使用 deep-research SKILL.md 执行研究。"
                "叠加七律写作规范 + MECE 分析框架。"
                "完成后自动触发湘小法（研究模式）质量审核。"
                "最终成果写入 成果/ 目录，文件名为 深度研究报告_YYYYMMDD_HHMMSS.md"
            )
        }, ensure_ascii=False), encoding="utf-8")

        # ── 这里接入实际 Agent ───────────────────────────────────────────
        # 当前为框架阶段，实际 Agent 调用通过 Task 工具在主会话触发
        # 成果模拟（阶段一）：写入占位成果文件
        # 阶段二将替换为真实 Agent 调用
        # ────────────────────────────────────────────────────────────────

        # 写成果目录
        result_dir = td / "成果"
        result_dir.mkdir(exist_ok=True)

        output_file = result_dir / f"深度研究报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_file.write_text(
            f"# 研究任务进行中\n\n"
            f"任务ID：{task_id}\n"
            f"研究主题：{query}\n"
            f"领域：{domain}\n\n"
            f"## 执行说明\n\n"
            f"deep-research Agent 已收到任务，将在当前会话中执行研究。\n"
            f"完成后请刷新任务状态或重新运行 poll 命令。\n\n"
            f"> 如需查看执行进度，请在当前 WorkBuddy 对话中继续研究此任务。\n",
            encoding="utf-8"
        )

        mark_status(conn, task_id, "finished")

    except Exception as e:
        mark_status(conn, task_id, "error", str(e))

# ---------------------------------------------------------------------------
# 子命令实现
# ---------------------------------------------------------------------------

def cmd_create(args):
    """创建研究任务"""
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    td  = task_dir(task_id)
    td.mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (task_id, args.query[:60], args.query, args.domain or "通用",
         "pending", "deep-research", str(td), now, now, "", "")
    )
    conn.commit()

    print(f"SUCCESS: 任务已创建")
    print(f"Task ID : {task_id}")
    print(f"研究方向 : {args.domain or '通用'}")
    print(f"成果目录 : {td}")
    print()
    print("下一步：")
    print(f"  python xiang_research.py poll --chat-id {task_id}")

    # 立即在后台触发 Agent（通过独立线程）
    Thread(target=run_agent_async, args=(task_id, args.query, args.domain or "通用"), daemon=True).start()
    print(f"Agent 已后台触发，正在执行研究...")

    # 后台启动独立进程执行 Agent（不受主进程退出影响）
    bg_script = Path(__file__).parent / "_agent_runner.py"
    if bg_script.exists():
        import subprocess
        subprocess.Popen(
            [sys.executable, str(bg_script), task_id, str(SKILL_DIR)],
            creationflags=0x00000008,  # DETACHED_PROCESS on Windows
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def cmd_status(args):
    """查询任务状态"""
    conn = get_conn()
    row = conn.execute(
        "SELECT id,title,domain,status,agent_name,created_at,updated_at,error_msg FROM tasks WHERE id=?",
        (args.chat_id,)
    ).fetchone()
    if not row:
        print(f"❌ 任务 {args.chat_id} 不存在")
        return

    id_, title, domain, status, agent, created, updated, error = row

    status_icon = {"pending": "⏳", "running": "🔄", "finished": "✅", "error": "❌", "aborted": "⏹"}.get(status, "?")
    print(f"{status_icon} 任务: {title}")
    print(f"   状态   : {status}")
    print(f"   领域   : {domain}")
    print(f"   Agent  : {agent}")
    print(f"   创建   : {created[:19]}")
    if updated:
        print(f"   更新   : {updated[:19]}")
    if error:
        print(f"   错误   : {error}")


def cmd_poll(args):
    """轮询直到任务完成"""
    chat_id  = args.chat_id
    interval = args.interval or POLL_INTERVAL
    timeout  = args.timeout  or POLL_TIMEOUT
    start    = time.time()

    print(f"⏳ 开始轮询任务 {chat_id}，间隔 {interval}s，超时 {timeout}s")
    print("按 Ctrl+C 可中断轮询（任务继续执行）\n")

    conn = get_conn()

    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            print(f"⏰ 超时（{timeout}s），任务可能仍在运行")
            print(f"  查看状态：python xiang_research.py status --chat-id {chat_id}")
            return

        row = conn.execute(
            "SELECT status, updated_at FROM tasks WHERE id=?",
            (chat_id,)
        ).fetchone()

        if not row:
            print(f"❌ 任务 {chat_id} 不存在")
            return

        status, updated = row
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)

        print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] 状态: {status}  ({updated[:19] if updated else '无更新'})")

        if status == "finished":
            _show_results(conn, chat_id)
            return
        elif status == "error":
            print(f"❌ 任务执行出错")
            conn2 = get_conn()
            err = conn2.execute("SELECT error_msg FROM tasks WHERE id=?", (chat_id,)).fetchone()
            if err and err[0]:
                print(f"   错误信息: {err[0]}")
            return
        elif status == "aborted":
            print("⏹ 任务已被中止")
            return

        time.sleep(interval)


def _show_results(conn, chat_id):
    """显示成果文件"""
    row = conn.execute("SELECT output_dir FROM tasks WHERE id=?", (chat_id,)).fetchone()
    if not row:
        return
    out_dir = Path(row[0])
    result_dir = out_dir / "成果"

    if not result_dir.exists():
        print("\n⚠️ 成果目录不存在（Agent 可能还在执行中）")
        return

    files = list(result_dir.glob("*.md")) + list(result_dir.glob("*.docx")) + list(result_dir.glob("*.xlsx"))
    if not files:
        print("\n⚠️ 成果目录下无文件（任务可能还在处理中）")
        return

    print(f"\n✅ 研究完成！共 {len(files)} 个成果文件：")
    for f in sorted(files):
        size = f.stat().st_size
        print(f"  📄 {f.name}  ({size/1024:.1f} KB)")
        print(f"     路径: {f}")
    print()
    print(f"查看详情：python xiang_research.py files --chat-id {chat_id}")


def cmd_list(args):
    """列出所有任务"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, title, domain, status, created_at FROM tasks "
        "ORDER BY created_at DESC LIMIT 20"
    ).fetchall()

    if not rows:
        print("暂无任务记录")
        return

    print(f"共 {len(rows)} 个任务（最近20条）：")
    print(f"{'状态':<10} {'Task ID':<10} {'领域':<8} {'标题（截断）':<30} {'创建时间'}")
    print("-" * 80)
    for r in rows:
        status_icon = {"pending": "⏳", "running": "🔄", "finished": "✅", "error": "❌", "aborted": "⏹"}.get(r[3], "?")
        print(f"{status_icon}{r[3]:<9} {r[0]:<10} {r[2]:<8} {r[1][:28]:<30} {r[4][:10]}")


def cmd_abort(args):
    """中止任务"""
    conn = get_conn()
    row = conn.execute("SELECT status FROM tasks WHERE id=?", (args.chat_id,)).fetchone()
    if not row:
        print(f"❌ 任务 {args.chat_id} 不存在")
        return
    mark_status(conn, args.chat_id, "aborted")
    print(f"✅ 任务 {args.chat_id} 已中止")


def cmd_files(args):
    """列出成果目录文件"""
    conn = get_conn()
    row = conn.execute("SELECT output_dir FROM tasks WHERE id=?", (args.chat_id,)).fetchone()
    if not row:
        print(f"❌ 任务不存在")
        return

    out_dir = Path(row[0])
    search_dir = out_dir / (args.path.lstrip("/") if args.path else "成果")

    if not search_dir.exists():
        print(f"目录不存在：{search_dir}")
        return

    files = list(search_dir.rglob("*"))
    regular_files = [f for f in files if f.is_file()]
    dirs = [f for f in files if f.is_dir()]

    if dirs:
        print(f"子目录：")
        for d in dirs:
            print(f"  📁 {d.relative_to(search_dir)}/")
    if regular_files:
        print(f"文件列表（共 {len(regular_files)} 个）：")
        for f in sorted(regular_files):
            size = f.stat().st_size
            print(f"  📄 {f.relative_to(search_dir)}  ({size/1024:.1f} KB)")
    if not regular_files and not dirs:
        print("目录为空")


def cmd_schedule(args):
    """创建定时任务"""
    from datetime import datetime as dt
    try:
        scheduled = dt.strptime(args.time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ 时间格式错误，请使用：YYYY-MM-DD HH:MM:SS")
        return

    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    td = task_dir(f"sched_{task_id}")
    td.mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (task_id, args.query[:60], args.query, "定时任务",
         "pending", "deep-research", str(td), now, now, "", "")
    )
    conn.commit()

    # 写入定时信息（由系统调度器在指定时间触发）
    schedule_file = td / "_schedule.json"
    schedule_file.write_text(json.dumps({
        "task_id": task_id,
        "scheduled_at": scheduled.isoformat(),
        "status": "pending"
    }, ensure_ascii=False), encoding="utf-8")

    print(f"SUCCESS: 定时任务已创建")
    print(f"Task ID  : {task_id}")
    print(f"执行时间 : {scheduled.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"内容     : {args.query[:60]}...")
    print()
    print(f"当前 WorkBuddy 尚未支持自动定时触发，请到时手动执行：")
    print(f"  python xiang_research.py poll --chat-id {task_id}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="湘小研·智库深度研究智能体 CLI\n"
                    "对标深度智联 agentic.py，提供国资国企研究异步任务管理能力",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", help="可用子命令（输入 -h 查看详细帮助）")

    # create
    p = sub.add_parser("create", help="创建研究任务")
    p.add_argument("--query", required=True, help="完整研究需求描述（将原样传递给 Agent）")
    p.add_argument("--domain", default="通用",
                   choices=["国资国企", "产业政策", "区域经济", "企业研究", "宏观经济", "通用"],
                   help="研究领域预设，影响 Agent 调用策略（默认：通用）")

    # status
    p = sub.add_parser("status", help="查询任务状态")
    p.add_argument("--chat-id", required=True, help="任务 ID")

    # poll
    p = sub.add_parser("poll", help="轮询直到任务完成，自动显示成果文件")
    p.add_argument("--chat-id", required=True, help="任务 ID")
    p.add_argument("--interval", type=int, help=f"轮询间隔秒数（默认 {POLL_INTERVAL}）")
    p.add_argument("--timeout",  type=int, help=f"超时秒数（默认 {POLL_TIMEOUT}）")

    # list
    sub.add_parser("list", help="列出最近20个任务")

    # abort
    p = sub.add_parser("abort", help="中止任务")
    p.add_argument("--chat-id", required=True, help="任务 ID")

    # files
    p = sub.add_parser("files", help="列出成果目录文件")
    p.add_argument("--chat-id", required=True, help="任务 ID")
    p.add_argument("--path", default="/成果", help="目录路径（默认 /成果）")

    # schedule
    p = sub.add_parser("schedule", help="创建定时任务")
    p.add_argument("--query", required=True, help="研究需求")
    p.add_argument("--time", required=True, help="执行时间（YYYY-MM-DD HH:MM:SS）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n── 快速入门 ──")
        print("1. 创建任务：python xiang_research.py create --query \"研究湖南省低空经济发展路径\"")
        print("2. 轮询状态：python xiang_research.py poll --chat-id <返回的TaskID>")
        print("3. 查看任务：python xiang_research.py list")
        return

    commands = {
        "create":  cmd_create,
        "status":  cmd_status,
        "poll":    cmd_poll,
        "list":    cmd_list,
        "abort":   cmd_abort,
        "files":   cmd_files,
        "schedule": cmd_schedule,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
