import subprocess
from datetime import datetime
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a git command and print it for visibility."""
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=False, text=True)


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
    print(f"推送到远程 origin/{branch} ...")
    push_result = run(["git", "-C", str(repo_root), "push", "origin", branch])
    if push_result.returncode != 0:
        print("git push 失败，请检查上面的错误信息（可能是未登录、无权限或网络问题）。")
        return

    print("✅ 已自动提交并推送 QuestionUpdates 仓库。")


if __name__ == "__main__":
    main()


