import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

GITEE_REMOTE_NAME = "gitee"
GITEE_REMOTE_URL = "https://gitee.com/langzhikeji/QuestionUpdates.git"


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    """Run a git command and print it for visibility."""
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=capture,
        encoding="utf-8" if capture else None,
    )


def ensure_gitee_remote(repo_root: Path) -> bool:
    """Ensure the gitee remote exists; add it if missing."""
    remotes_proc = run(
        ["git", "-C", str(repo_root), "remote"],
        capture=True,
    )
    if remotes_proc.returncode != 0:
        print("无法获取远程列表，稍后推送可能失败。")
        return False
    remotes = remotes_proc.stdout.split()
    if GITEE_REMOTE_NAME in remotes:
        return True

    print(f"未检测到 {GITEE_REMOTE_NAME} 远程，正在添加...")
    add_proc = run(
        [
            "git",
            "-C",
            str(repo_root),
            "remote",
            "add",
            GITEE_REMOTE_NAME,
            GITEE_REMOTE_URL,
        ]
    )
    return add_proc.returncode == 0


def main() -> None:
    repo_root = Path(__file__).resolve().parent

    # Ensure we are in the QuestionUpdates repo
    if not (repo_root / ".git").exists():
        print("错误：当前目录不是 Git 仓库（未找到 .git 目录）")
        return

    # Show current status
    print("检查 Git 状态...")
    run(["git", "-C", str(repo_root), "status"])

    # Stage changes under this repo (新增的 APK、version.json 等)
    print("添加所有改动到暂存区（git add）...")
    add_result = run(["git", "-C", str(repo_root), "add", "."])
    if add_result.returncode != 0:
        print("git add 失败，请检查上面的错误信息。")
        return

    # 检查是否真的有改动
    diff_result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--quiet"],
        check=False,
    )
    if diff_result.returncode == 0:
        print("没有需要提交的改动，已退出。")
        return

    # 自动生成提交信息，包含时间戳
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"更新 Question APK 与版本配置 ({ts})"
    print(f"创建提交：{commit_msg}")
    commit_result = run(
        ["git", "-C", str(repo_root), "commit", "-m", commit_msg]
    )
    if commit_result.returncode != 0:
        print("git commit 失败，请检查上面的错误信息。")
        return

    # 获取当前分支名
    print("检测当前分支名...")
    branch_proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
        check=False,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    if branch_proc.returncode != 0:
        print("无法获取当前分支名，请检查 Git 配置。")
        return
    branch = branch_proc.stdout.strip()
    if not branch:
        print("当前分支名为空，请检查 Git 配置。")
        return

    # 推送到远程 origin
    # 推送到 origin
    print(f"推送到远程 origin/{branch} ...")
    push_result = run(["git", "-C", str(repo_root), "push", "origin", branch])
    if push_result.returncode != 0:
        print("⚠️ 推送到 origin 失败，请检查上面的错误信息。")
        return

    # 推送到 gitee
    if ensure_gitee_remote(repo_root):
        print(f"推送到远程 {GITEE_REMOTE_NAME}/{branch} ...")
        push_gitee = run(
            ["git", "-C", str(repo_root), "push", GITEE_REMOTE_NAME, branch]
        )
        if push_gitee.returncode != 0:
            print("⚠️ 推送到 gitee 失败，请检查凭证或网络。")
            return

    print("[OK] 已自动提交并推送 QuestionUpdates 到 GitHub 与 Gitee。")


if __name__ == "__main__":
    main()


