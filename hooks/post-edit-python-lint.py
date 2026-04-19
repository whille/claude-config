#!/usr/bin/env python3
"""
post-edit-python-lint.py - 自动 lint Python 文件

触发：Edit 或 Write .py 文件后
动作：运行 ruff check --fix
"""

import subprocess
import sys
import os

def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLAUDE_FILE_PATH", "")

    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    try:
        result = subprocess.run(
            ["ruff", "check", "--fix", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout and "fixed" in result.stdout.lower():
            print(f"✓ Linted: {file_path}")
        elif result.returncode != 0 and result.stdout:
            # 有未修复的问题
            lines = result.stdout.strip().split("\n")
            issues = [l for l in lines if l.startswith(file_path) or l.strip().startswith("F:") or l.strip().startswith("E:")]
            if issues:
                print(f"⚠️ Lint issues in {file_path}:")
                for issue in issues[:5]:  # 只显示前5个
                    print(f"  {issue}")

    except FileNotFoundError:
        print("⚠️ ruff not found, skipping lint", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️ Lint timeout", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Lint error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
