#!/usr/bin/env python3
"""
学习对话历史，提取模式并建议规则/hooks
支持 --all 参数分析所有项目
需要用户确认后才保存文件
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
import re
import argparse


def get_all_projects():
    """获取所有项目目录"""
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return []

    projects = []
    for project_path in projects_dir.iterdir():
        if project_path.is_dir() and project_path.name.startswith("-Users-"):
            # 提取项目名（去掉前缀）
            name = project_path.name.replace("-Users-wangzhiguo-github-com-", "")
            projects.append({
                "name": name,
                "path": project_path,
                "full_name": project_path.name
            })
    return projects


def load_conversations(project_path: str | Path, days: int = 7):
    """加载指定项目最近N天的对话"""
    project_dir = Path(project_path) if isinstance(project_path, str) else project_path

    if not project_dir.exists():
        return []

    conversations = []
    cutoff = datetime.now() - timedelta(days=days)

    for jsonl_file in project_dir.glob("*.jsonl"):
        # 跳过子目录中的文件
        if jsonl_file.parent != project_dir:
            continue

        try:
            file_mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            if file_mtime < cutoff:
                continue
        except:
            pass

        with open(jsonl_file) as f:
            for line in f:
                try:
                    data = json.loads(line)
                except:
                    continue

                if data.get('type') in ['user', 'assistant']:
                    msg = data.get('message', {})
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')

                    # 提取文本
                    text = ''
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text = item.get('text', '')
                                break

                    if text and len(text) > 20:
                        conversations.append({
                            'role': role,
                            'text': text,
                            'file': jsonl_file.name,
                            'project': project_dir.name
                        })

    return conversations


def analyze_patterns(conversations: list):
    """分析对话模式"""
    patterns = {
        'clarifications': [],      # 用户澄清问题
        'corrections': [],        # 用户纠正
        'repetitions': [],        # 重复问题
        'preferences': [],        # 用户偏好
    }

    # 追踪问题用于检测重复
    user_questions = []

    for i, conv in enumerate(conversations):
        if conv['role'] == 'user':
            text = conv['text']

            # 检测澄清
            clarification_signals = [
                (r"你指的是", "指代不明"),
                (r"我问的是", "话题偏离"),
                (r"不是这个", "理解错误"),
                (r"我是说", "表达不清"),
                (r"我的意思是", "表达不清"),
                (r"不要.*改", "操作被拒"),
                (r"不需要", "需求误判"),
            ]
            for sig, reason in clarification_signals:
                if re.search(sig, text):
                    patterns['clarifications'].append({
                        'signal': sig,
                        'reason': reason,
                        'user_text': text[:150],
                        'project': conv.get('project', 'unknown')
                    })
                    break

            # 检测纠正
            correction_signals = [
                (r"不对", "事实错误"),
                (r"错了", "事实错误"),
                (r"不是", "理解错误"),
                (r"应该", "方法纠正"),
                (r"重新", "结果不满意"),
            ]
            for sig, reason in correction_signals:
                if re.search(sig, text):
                    patterns['corrections'].append({
                        'signal': sig,
                        'reason': reason,
                        'user_text': text[:150],
                        'project': conv.get('project', 'unknown')
                    })
                    break

            # 检测偏好
            preference_signals = [
                (r"我喜欢", "偏好表达"),
                (r"用.*格式", "格式偏好"),
                (r"不要.*格式", "格式偏好"),
                (r"简单.*说", "风格偏好"),
                (r"详细", "风格偏好"),
            ]
            for sig, reason in preference_signals:
                if re.search(sig, text):
                    patterns['preferences'].append({
                        'signal': sig,
                        'reason': reason,
                        'user_text': text[:150],
                        'project': conv.get('project', 'unknown')
                    })
                    break

            # 追踪问题（简化版）
            simple_question = re.sub(r'[^\w]', '', text[:50]).lower()
            if simple_question:
                user_questions.append(simple_question)

    # 检测重复问题
    question_counts = Counter(user_questions)
    for question, count in question_counts.items():
        if count >= 3:
            patterns['repetitions'].append({
                'question': question[:50],
                'count': count
            })

    return patterns


def generate_rule_suggestion(pattern_type: str, pattern_data: list, all_patterns: dict) -> list:
    """根据模式生成规则建议"""

    suggestions = []

    if pattern_type == 'clarifications' and pattern_data:
        # 分析常见的澄清类型
        reasons = Counter(p.get('reason', '') for p in pattern_data)

        if reasons.get('指代不明', 0) >= 3:
            suggestions.append({
                'type': 'rule',
                'name': 'scope-clarification.md',
                'title': '范围澄清规则',
                'problem': f'用户澄清了 {len(pattern_data)} 次，常见于"当前"、"改动"等指代不明',
                'content': '''# Scope Clarification Rule

## Trigger
- User asks about "当前"、"改动"、"现在的"、"配置"

## Guideline
Before answering, clarify scope:
- 本地改动还是服务器配置？
- 当前会话还是全局？
- 未提交还是已提交？

## Example
用户: 当前的配置是什么？
AI: 你指的是本地未提交的改动，还是服务器上的配置？
''',
                'save_path': str(Path.home() / ".claude" / "rules" / "scope-clarification.md")
            })

        if reasons.get('操作被拒', 0) >= 3:
            suggestions.append({
                'type': 'rule',
                'name': 'confirm-before-action.md',
                'title': '操作确认规则',
                'problem': f'用户拒绝了 {reasons.get("操作被拒", 0)} 次操作',
                'content': '''# Confirm Before Action Rule

## Trigger
- Modifying files (Edit, Write)
- Running destructive commands
- Git operations (commit, push, reset)

## Guideline
Before executing:
1. Preview the change
2. Ask for confirmation
3. Execute only after approval

## Example
用户: 删除这个文件
AI: 确认删除 /path/to/file.py？(y/n)
''',
                'save_path': str(Path.home() / ".claude" / "rules" / "confirm-before-action.md")
            })

    elif pattern_type == 'corrections' and pattern_data:
        reasons = Counter(p.get('reason', '') for p in pattern_data)

        if reasons.get('事实错误', 0) >= 3:
            suggestions.append({
                'type': 'rule',
                'name': 'verify-before-claim.md',
                'title': '声明验证规则',
                'problem': f'用户纠正了 {reasons.get("事实错误", 0)} 次事实错误',
                'content': '''# Verify Before Claim Rule

## Trigger
- Making claims about code state
- Describing file contents
- Answering "what is" questions

## Guideline
Before making claims:
1. Read the file first
2. Verify the statement
3. Cite the source (file:line)

## Example
用户: 这个函数做什么的？
AI: 让我先读取这个文件...
[Read file]
这个函数 at src/module.py:45 用于...
''',
                'save_path': str(Path.home() / ".claude" / "rules" / "verify-before-claim.md")
            })

    elif pattern_type == 'preferences' and pattern_data:
        # 检测常见的偏好模式
        pref_texts = [p.get('user_text', '') for p in pattern_data]

        if any('简单' in t for t in pref_texts) >= 3:
            suggestions.append({
                'type': 'memory',
                'name': 'MEMORY.md 更新',
                'title': '简洁风格偏好',
                'problem': '用户偏好简洁的回答风格',
                'content': '在 MEMORY.md 中添加:\n- 回答风格: 简洁，避免冗余',
                'save_path': 'MEMORY.md'
            })

    elif pattern_type == 'repetitions' and pattern_data:
        if len(pattern_data) >= 2:
            suggestions.append({
                'type': 'hook',
                'name': 'faq-reminder',
                'title': 'FAQ 提醒 Hook',
                'problem': f'发现 {len(pattern_data)} 个重复问题',
                'content': '''// PreToolUse hook for FAQ detection
// Check if user question matches known patterns
''',
                'save_path': str(Path.home() / ".claude" / "hooks" / "faq-reminder.mjs")
            })

    return suggestions


def print_suggestion(idx: int, total: int, suggestion: dict):
    """打印单个建议"""
    print(f"\n{'='*60}")
    print(f"## [{idx}/{total}] {suggestion['title']}")
    print(f"\n**类型**: {suggestion['type']}")
    print(f"**问题**: {suggestion['problem']}")
    print(f"**保存位置**: {suggestion['save_path']}")

    print(f"\n--- 预览 ---")
    print(suggestion['content'][:500])
    if len(suggestion['content']) > 500:
        print("... (内容已截断)")
    print("--- 预览结束 ---")


def save_suggestion(suggestion: dict) -> bool:
    """保存建议（需要用户确认）"""
    save_path = Path(suggestion['save_path'])

    if suggestion['type'] == 'memory':
        print(f"\n💡 请手动更新 {suggestion['save_path']}:")
        print(suggestion['content'])
        return False

    # 创建目录
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存文件
    save_path.write_text(suggestion['content'])
    print(f"✅ 已保存到 {save_path}")
    return True


def interactive_confirm(suggestions: list, dry_run: bool = False):
    """交互式确认"""
    if not suggestions:
        print("\n没有发现需要建议的改进")
        return

    print(f"\n📋 建议采纳的改进 (共 {len(suggestions)} 项)")

    adopted = []
    skipped = []

    for i, suggestion in enumerate(suggestions, 1):
        print_suggestion(i, len(suggestions), suggestion)

        if dry_run:
            print("\n[Dry run] 不会保存文件")
            continue

        while True:
            try:
                answer = input("\n是否采纳？ (y/n/preview/skip-all): ").strip().lower()
            except EOFError:
                answer = 'n'

            if answer == 'y':
                if save_suggestion(suggestion):
                    adopted.append(suggestion)
                break
            elif answer == 'n':
                print("⏭️ 跳过")
                skipped.append(suggestion)
                break
            elif answer == 'preview':
                print(f"\n--- 完整内容 ---")
                print(suggestion['content'])
                print("--- 完整内容结束 ---")
                continue
            elif answer == 'skip-all':
                skipped.extend(suggestions[i-1:])
                print("⏭️ 跳过剩余所有建议")
                break
            else:
                print("请输入 y/n/preview/skip-all")
                continue

        if answer == 'skip-all':
            break

    # 汇总
    print(f"\n{'='*60}")
    print("📊 学习完成!")
    print(f"   ├─ 采纳: {len(adopted)} 项")
    print(f"   ├─ 跳过: {len(skipped)} 项")
    print(f"   └─ 感谢反馈，将持续学习")


def main():
    parser = argparse.ArgumentParser(
        description='学习对话历史，建议规则和 hooks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 分析当前项目（最近 7 天）
  python3 analyze_conversations.py -p stockq

  # 分析所有项目
  python3 analyze_conversations.py --all

  # 分析所有项目（最近 30 天）
  python3 analyze_conversations.py --all --days 30

  # 仅输出建议，不保存
  python3 analyze_conversations.py --all --dry-run

  # 保存报告到文件
  python3 analyze_conversations.py --all --output /tmp/report.md
'''
    )

    parser.add_argument('--project', '-p', default=None,
                        help='项目名称（不含 -Users- 前缀）')
    parser.add_argument('--all', action='store_true',
                        help='分析所有项目')
    parser.add_argument('--days', '-d', type=int, default=7,
                        help='分析最近 N 天（默认 7）')
    parser.add_argument('--dry-run', action='store_true',
                        help='仅显示建议，不保存文件')
    parser.add_argument('--output', '-o', default=None,
                        help='保存报告到文件')
    parser.add_argument('--non-interactive', action='store_true',
                        help='非交互模式，仅输出建议')

    args = parser.parse_args()

    # 收集对话
    all_conversations = []

    if args.all:
        print("📊 正在分析所有项目...")
        projects = get_all_projects()

        if not projects:
            print("❌ 没有找到项目目录")
            return 1

        for project in projects:
            convs = load_conversations(project['path'], args.days)
            all_conversations.extend(convs)
            print(f"   ├─ {project['name']}: {len(convs)} 条对话")

        print(f"   └─ 共计: {len(all_conversations)} 条对话")

    elif args.project:
        # 自动添加前缀
        project_name = args.project
        if not project_name.startswith("-Users-"):
            project_name = f"-Users-wangzhiguo-github-com-{project_name}"

        project_dir = Path.home() / ".claude" / "projects" / project_name

        if not project_dir.exists():
            print(f"❌ 项目目录不存在: {project_dir}")
            return 1

        print(f"📊 分析项目 {args.project}...")
        all_conversations = load_conversations(project_dir, args.days)
        print(f"   └─ 找到 {len(all_conversations)} 条对话")

    else:
        # 默认分析当前项目（从环境变量推断）
        cwd = Path.cwd()
        project_name = f"-Users-{Path.home().name}-github-com-{cwd.name}"

        project_dir = Path.home() / ".claude" / "projects" / project_name

        if project_dir.exists():
            print(f"📊 分析当前项目 {cwd.name}...")
            all_conversations = load_conversations(project_dir, args.days)
            print(f"   └─ 找到 {len(all_conversations)} 条对话")
        else:
            print("❌ 无法确定当前项目，请使用 -p 指定项目名或使用 --all")
            return 1

    if not all_conversations:
        print("❌ 没有找到对话记录")
        return 1

    # 分析模式
    patterns = analyze_patterns(all_conversations)

    # 打印摘要
    total_patterns = sum(len(v) for v in patterns.values())
    print(f"\n📊 发现 {total_patterns} 个模式:")
    for pattern_type, items in patterns.items():
        if items:
            print(f"   ├─ {pattern_type}: {len(items)} 次")

    # 生成建议
    all_suggestions = []
    for pattern_type, items in patterns.items():
        suggestions = generate_rule_suggestion(pattern_type, items, patterns)
        all_suggestions.extend(suggestions)

    # 去重（基于 name）
    seen = set()
    unique_suggestions = []
    for s in all_suggestions:
        if s['name'] not in seen:
            seen.add(s['name'])
            unique_suggestions.append(s)

    # 保存报告或交互确认
    if args.output:
        output_path = Path(args.output)
        report_lines = [
            "# 学习报告",
            "",
            f"**时间范围**: 最近 {args.days} 天",
            f"**对话数**: {len(all_conversations)}",
            "",
            "## 发现的模式",
            "",
        ]
        for pattern_type, items in patterns.items():
            if items:
                report_lines.append(f"### {pattern_type} ({len(items)} 次)")
                for item in items[:10]:
                    report_lines.append(f"- {item}")
                report_lines.append("")

        report_lines.append("## 建议的改进")
        report_lines.append("")
        for s in unique_suggestions:
            report_lines.append(f"### {s['title']}")
            report_lines.append(f"**问题**: {s['problem']}")
            report_lines.append(f"**保存位置**: {s['save_path']}")
            report_lines.append("")
            report_lines.append("```")
            report_lines.append(s['content'])
            report_lines.append("```")
            report_lines.append("")

        output_path.write_text('\n'.join(report_lines))
        print(f"\n✅ 报告已保存到: {output_path}")

    elif args.non_interactive or args.dry_run:
        # 非交互模式
        print(f"\n📋 建议的改进 (共 {len(unique_suggestions)} 项):")
        for i, s in enumerate(unique_suggestions, 1):
            print(f"\n[{i}] {s['title']}")
            print(f"    问题: {s['problem']}")
            print(f"    位置: {s['save_path']}")

        if args.dry_run:
            print("\n[Dry run] 未保存任何文件")

    else:
        # 交互式确认
        interactive_confirm(unique_suggestions, args.dry_run)

    return 0


if __name__ == '__main__':
    sys.exit(main())
