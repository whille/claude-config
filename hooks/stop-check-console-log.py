#!/usr/bin/env python3
"""
stop-check-console-log.py - 检查遗留的 console.log/print 调试语句

触发：Stop（会话结束）
动作：扫描代码中的调试语句，提醒清理
"""

import subprocess
import sys
import os
import re

# 调试语句模式
DEBUG_PATTERNS = {
    "console.log": r"console\.log\s*\(",
    "console.debug": r"console\.debug\s*\(",
    "print(...)": r"print\s*\(['\"]debug|DEBUG|TODO:",
    "pdb": r"import pdb|pdb\.set_trace\(\)",
    "breakpoint()": r"breakpoint\s*\(\)",
}

# 排除的文件/目录
EXCLUDE_PATTERNS = [
    "node_modules/",
    ".venv/",
    "venv/",
    "__pycache__/",
    ".git/",
    "tests/",
    "test_",
    "_test.py",
]

def should_skip(file_path):
    """判断是否跳过该文件"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path:
            return True
    return False

def find_debug_statements():
    """查找代码中的调试语句"""
    issues = []

    try:
        # 获取最近修改的文件（git status + 最近1小时修改的文件）
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5"],
            capture_output=True, text=True, timeout=5
        )

        files = result.stdout.strip().split("\n") if result.stdout else []

        # 也检查当前目录下最近修改的文件
        for root, dirs, filenames in os.walk("."):
            # 排除目录
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "venv", "__pycache__"]]

            for filename in filenames:
                if filename.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
                    filepath = os.path.join(root, filename)
                    if os.path.getmtime(filepath) > os.path.getmtime(filepath) - 3600:  # 1小时内
                        files.append(filepath)

        files = list(set(files))

        for filepath in files:
            if should_skip(filepath):
                continue

            if not os.path.exists(filepath):
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                    for pattern_name, pattern in DEBUG_PATTERNS.items():
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                # 忽略注释中的
                                if line.strip().startswith("#") or line.strip().startswith("//"):
                                    continue
                                issues.append({
                                    "file": filepath,
                                    "line": i,
                                    "type": pattern_name,
                                    "content": line.strip()[:60]
                                })
            except Exception:
                pass

    except Exception as e:
        print(f"⚠️ Check error: {e}", file=sys.stderr)

    return issues

def main():
    issues = find_debug_statements()

    if issues:
        print("\n" + "=" * 60)
        print("🔍 发现调试语句（建议清理）")
        print("=" * 60)

        for issue in issues[:10]:  # 只显示前10个
            print(f"  {issue['file']}:{issue['line']}")
            print(f"    [{issue['type']}] {issue['content']}")

        if len(issues) > 10:
            print(f"  ... 共 {len(issues)} 个")

        print("\n💡 提示: 使用 /simplify 清理这些调试语句")
        print("=" * 60)

if __name__ == "__main__":
    main()
