#!/usr/bin/env python3
"""
导出 Claude Code 对话历史（过滤代码，保留摘要）
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def extract_conversations(jsonl_file: str, output_format: str = "markdown"):
    """从 .jsonl 文件提取对话记录"""

    conversations = []
    stats = {"user": 0, "assistant": 0, "tool_calls": 0}

    with open(jsonl_file) as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
            except:
                continue

            if data.get('type') not in ['user', 'assistant']:
                continue

            msg = data.get('message', {})
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')

            # 提取文本
            text = ''
            has_tool_use = False

            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                texts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            texts.append(item.get('text', ''))
                        elif item.get('type') == 'tool_use':
                            has_tool_use = True
                            stats['tool_calls'] += 1
                text = '\n'.join(texts)

            # 过滤系统提示
            if text.startswith('You are') or len(text) < 10:
                continue

            # 统计
            if role == 'user':
                stats['user'] += 1
            else:
                stats['assistant'] += 1

            # 提取摘要（前150字符）
            summary = text.replace('\n', ' ')[:150].strip()
            if summary:
                conversations.append({
                    'role': role,
                    'text': summary,
                    'has_tool': has_tool_use
                })

    return conversations, stats

def format_markdown(conversations: list, stats: dict) -> str:
    """格式式为 Markdown"""
    lines = [
        "# 📋 对话记录摘要",
        "",
        f"**统计**: 用户 {stats['user']} 条 | AI {stats['assistant']} 条 | 工具调用 {stats['tool_calls']} 次",
        "",
        "---",
        ""
    ]

    for c in conversations:
        icon = "👤" if c['role'] == 'user' else "🤖"
        tool_marker = " [🔧]" if c.get('has_tool') else ""
        lines.append(f"{icon}{tool_marker} {c['text']}")
        lines.append("")

    return '\n'.join(lines)

def format_json(conversations: list, stats: dict) -> str:
    """格式为 JSON"""
    return json.dumps({
        'stats': stats,
        'conversations': conversations
    }, ensure_ascii=False, indent=2)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='导出 Claude Code 对话历史')
    parser.add_argument('session_file', help='.jsonl 会话文件路径')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--output', '-o', help='输出文件路径')

    args = parser.parse_args()

    conversations, stats = extract_conversations(args.session_file)

    if args.format == 'markdown':
        output = format_markdown(conversations, stats)
    else:
        output = format_json(conversations, stats)

    if args.output:
        Path(args.output).write_text(output)
        print(f"✅ 已导出到: {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
