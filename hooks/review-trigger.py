#!/usr/bin/env python3
"""
review-trigger.py - 代码提交前自动 review 触发器

触发条件：
1. git commit 命令
2. 存在代码变更
3. 变更涉及核心文件或高风险文件

动作：
1. 分析变更内容
2. 快速安全扫描
3. 如需要，提示执行 code-reviewer

使用方式：
1. 配置到 ~/.claude/settings.json 的 PreToolUse hook
2. 或手动执行
"""

import subprocess
import os
import re
import sys

# 高风险文件模式
HIGH_RISK_PATTERNS = [
    r"auth", r"security", r"password", r"token", r"api_key",
    r"payment", r"user", r"permission", r"role", r"secret"
]

# 快速安全扫描模式
SECURITY_PATTERNS = {
    "hardcoded_password": r"password\s*=\s*['\"].+['\"]",
    "hardcoded_key": r"api_key\s*=\s*['\"].+['\"]|secret\s*=\s*['\"].+['\"]",
    # SQL injection: f-string with SQL keywords and variable interpolation
    "sql_injection": r'f["\'][^"\']*(?:SELECT|INSERT|UPDATE|DELETE|DROP|FROM|WHERE)[^"\']*\{[^}]+\}',
    "eval_usage": r"eval\s*\(",
    "shell_true": r"shell\s*=\s*True",
    "xss_risk": r"\.format\s*\(|%s.*?(?:SELECT|INSERT|UPDATE|DELETE)",
}

def get_staged_files():
    """获取暂存文件列表"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f]

def get_changed_files():
    """获取变更文件列表"""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f]

def is_code_file(filepath):
    """判断是否为代码文件"""
    code_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java"]
    return any(filepath.endswith(ext) for ext in code_extensions)

def is_high_risk_file(filepath):
    """判断是否为高风险文件"""
    filepath_lower = filepath.lower()
    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, filepath_lower):
            return True
    return False

def quick_security_scan(filepath):
    """快速安全扫描"""
    issues = []

    if not os.path.exists(filepath):
        return issues

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️ 无法读取文件 {filepath}: {e}", file=sys.stderr)
        return issues

    for issue_type, pattern in SECURITY_PATTERNS.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count("\n") + 1
            issues.append({
                "type": issue_type,
                "line": line_num,
                "match": match.group()[:50]
            })

    return issues

def should_trigger_review(files):
    """
    判断是否需要触发 review

    Returns:
        (should_trigger, reason, issues)
    """
    if not files:
        return False, "无文件变更", []

    # 筛选代码文件
    code_files = [f for f in files if is_code_file(f)]

    if not code_files:
        return False, "仅非代码文件变更", []

    # 检查高风险文件
    high_risk_files = [f for f in code_files if is_high_risk_file(f)]
    if high_risk_files:
        return True, f"高风险文件: {len(high_risk_files)} 个", []

    # 快速安全扫描
    all_issues = []
    for f in code_files:
        issues = quick_security_scan(f)
        all_issues.extend(issues)

    if all_issues:
        return True, f"发现 {len(all_issues)} 个潜在安全问题", all_issues

    # 检查变更大小
    total_lines = 0
    for f in code_files:
        result = subprocess.run(
            ["git", "diff", "--cached", "--stat", f],
            capture_output=True, text=True
        )
        if result.stdout:
            # 解析变更行数
            stats = result.stdout.strip().split()[-1] if result.stdout.strip() else "0"
            try:
                total_lines += int(stats)
            except ValueError:
                pass  # stats 格式无法解析时忽略

    if len(code_files) > 10 or total_lines > 500:
        return True, f"大变更: {len(code_files)} 文件, {total_lines} 行", []

    # 默认：有代码变更则建议 review
    return True, f"代码变更: {len(code_files)} 个文件", []

def main():
    # 获取文件变更
    staged_files = get_staged_files()
    changed_files = get_changed_files()
    all_files = list(set(staged_files + changed_files))

    # 判断是否需要 review
    should_review, reason, issues = should_trigger_review(all_files)

    print("\n" + "=" * 60)
    print("Review Trigger Check")
    print("=" * 60)

    if should_review:
        print(f"\n⚠️  {reason}")

        if issues:
            print(f"\n发现安全问题:")
            for issue in issues[:5]:  # 只显示前5个
                print(f"  📋 {issue['type']}: line {issue['line']}")
                print(f"     → {issue['match']}")

        print(f"\n💡 建议执行:")
        print(f"   /code-reviewer")
        print(f"   或使用 Agent subagent_type='code-reviewer'")

        print(f"\n📋 待审查文件:")
        for f in all_files[:10]:
            print(f"   - {f}")
        if len(all_files) > 10:
            print(f"   ... 共 {len(all_files)} 个文件")

    else:
        print(f"\n✅ {reason}")
        print("   无需自动触发 review")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
