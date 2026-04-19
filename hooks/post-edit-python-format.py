#!/usr/bin/env python3
"""
post-edit-python-format.py - 自动格式化 Python 文件

触发：Edit 或 Write .py 文件后
动作：运行 ruff format
"""

import subprocess
import sys
import os

def main():
    # 从环境变量或参数获取文件路径
    file_path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLAUDE_FILE_PATH", "")

    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    # 运行 ruff format
    try:
        result = subprocess.run(
            ["ruff", "format", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout:
            print(f"✓ Formatted: {file_path}")
        elif result.returncode != 0:
            print(f"⚠️ Format failed: {result.stderr}", file=sys.stderr)

    except FileNotFoundError:
        print("⚠️ ruff not found, skipping format", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️ Format timeout", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Format error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
