#!/usr/bin/env python3
"""
session-start.py - 会话启动时加载上下文

触发：SessionStart
动作：
1. 加载项目上下文（如 .omc/notepad.md）
2. 检测包管理器
3. 显示项目状态
"""

import os
import subprocess
import sys

def detect_package_manager():
    """检测项目使用的包管理器"""
    indicators = {
        "bun": ["bun.lockb", "bunfig.toml"],
        "pnpm": ["pnpm-lock.yaml"],
        "yarn": ["yarn.lock"],
        "npm": ["package-lock.json"],
        "uv": ["uv.lock", "pyproject.toml"],
        "poetry": ["poetry.lock"],
        "pip": ["requirements.txt", "setup.py"],
    }

    for pm, files in indicators.items():
        for f in files:
            if os.path.exists(f):
                return pm
    return None

def load_context():
    """加载项目上下文"""
    context_files = [
        ".omc/notepad.md",
        ".claude/CLAUDE.md",
        "CLAUDE.md",
        "README.md",
    ]

    contexts = []
    for filepath in context_files:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()[:500]  # 只读取前500字符
                    contexts.append(f"📄 {filepath}:\n{content[:200]}...")
            except Exception:
                pass

    return contexts

def get_git_status():
    """获取 git 状态"""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            return len(lines)
        return 0
    except Exception:
        return 0

def main():
    print("\n" + "=" * 60)
    print("🚀 Session Context")
    print("=" * 60)

    # 包管理器
    pm = detect_package_manager()
    if pm:
        print(f"📦 Package Manager: {pm}")

    # Git 状态
    changes = get_git_status()
    if changes > 0:
        print(f"📝 Uncommitted changes: {changes} files")

    # 上下文
    contexts = load_context()
    if contexts:
        print("\n📚 Loaded contexts:")
        for ctx in contexts[:2]:
            print(f"  {ctx.split(chr(10))[0]}")

    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
