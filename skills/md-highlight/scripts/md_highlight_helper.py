#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_highlight helper: 预处理、后处理、验证
确保原文内容不变，仅添加高亮标记
"""

import hashlib
import re
from pathlib import Path
from typing import List, Tuple

# 颜色映射
CLASS_TO_COLOR = {
    "hl-concept": "#d1ecf1",
    "hl-conclusion": "#fff3cd",
    "hl-data": "#d4edda",
    "hl-warning": "#fff2e6",
}

STYLE_BLOCK = """<style>
.hl-concept { background-color:#d1ecf1; padding:2px 4px; border-radius:3px; }
.hl-conclusion { background-color:#fff3cd; padding:2px 4px; border-radius:3px; }
.hl-data { background-color:#d4edda; padding:2px 4px; border-radius:3px; }
.hl-warning { background-color:#fff2e6; padding:2px 4px; border-radius:3px; }
</style>
"""

SPAN_CLASS_PATTERN = re.compile(
    r'<span class="hl-(?:concept|conclusion|data|warning)">([^<]+)</span>'
)
STYLE_BLOCK_PATTERN = re.compile(r'<style>[\s\S]*?</style>\s*', re.IGNORECASE)


def compute_hash(content: str) -> str:
    """计算内容 hash，用于验证"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def count_lines(content: str) -> int:
    """统计非空行数"""
    return len([l for l in content.split('\n') if l.strip()])


def strip_spans(content: str) -> str:
    """移除所有 span 标记，保留内部文字"""
    content = STYLE_BLOCK_PATTERN.sub('', content)
    content = SPAN_CLASS_PATTERN.sub(r'\1', content)
    return content


def normalize(content: str) -> str:
    """标准化内容用于比对（忽略空白差异、引号类型差异）"""
    # 统一所有引号类型为普通双引号（使用 Unicode 码点确保正确）
    content = content.replace('\u201c', '"').replace('\u201d', '"')  # " " -> "
    content = content.replace('\u2018', "'").replace('\u2019', "'")  # ' ' -> '
    return ''.join(content.split())


def split_by_headers(content: str, max_lines: int = 400) -> List[Tuple[int, int, str]]:
    """
    按标题分段，返回 (start_line, end_line, segment) 列表
    每段约 max_lines 行
    """
    lines = content.split('\n')
    segments = []
    current_start = 0
    current_lines = []

    for i, line in enumerate(lines):
        current_lines.append(line)

        # 遇到 ## 或 ### 标题，且当前段已够长
        if line.startswith('##') and len(current_lines) >= max_lines // 2:
            segments.append((current_start, i, '\n'.join(current_lines)))
            current_start = i
            current_lines = []

    # 最后一段
    if current_lines:
        segments.append((current_start, len(lines), '\n'.join(current_lines)))

    return segments


def preprocess(file_path: str) -> dict:
    """
    预处理：读取文件，返回元数据供 Claude 处理

    Returns:
        {
            'content': str,           # 原文内容
            'hash': str,              # 原文 hash
            'line_count': int,       # 行数
            'segments': list,         # 分段（大文件）
            'is_large': bool,        # 是否大文件
            'text_type': str,         # 推测的文本类型
        }
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    content = path.read_text(encoding='utf-8')
    line_count = count_lines(content)

    # 推测文本类型（简单启发式）
    text_type = infer_text_type(content)

    result = {
        'content': content,
        'hash': compute_hash(content),
        'line_count': line_count,
        'is_large': line_count > 500,
        'text_type': text_type,
    }

    # 大文件分段
    if line_count > 500:
        result['segments'] = split_by_headers(content)

    return result


def infer_text_type(content: str) -> str:
    """
    推测文本类型：narrative/pop_sci/technical/instruction
    """
    # 简单启发式规则
    has_chapter = bool(re.search(r'^第[一二三四五六七八九十]+章', content, re.MULTILINE))
    has_person = bool(re.search(r'说[道：]|问[道：]', content))
    has_warning = bool(re.search(r'注意|警告|必须|禁止|安全', content))
    has_numbers = bool(re.search(r'\d+%|\d+万|\d+亿|\d+年', content))
    has_tutorial = bool(re.search(r'步骤|方法|教程|如何', content))

    if has_chapter and has_person:
        return 'narrative'
    if has_tutorial and has_numbers:
        return 'technical'
    if has_warning:
        return 'instruction'
    if has_numbers:
        return 'pop_sci'
    return 'narrative'


def postprocess(original_content: str, highlighted_content: str, output_path: str) -> dict:
    """
    后处理：验证、写回文件

    Returns:
        {
            'success': bool,
            'error': str or None,
            'span_count': int,
            'output_path': str,
        }
    """
    # 1. 验证原文内容不变
    original_normalized = normalize(original_content)
    highlighted_stripped = strip_spans(highlighted_content)
    highlighted_normalized = normalize(highlighted_stripped)

    if original_normalized != highlighted_normalized:
        # 找出差异位置
        diff_start = find_diff_position(original_normalized, highlighted_normalized)
        return {
            'success': False,
            'error': f'原文内容被修改！差异位置: ...{diff_start}...',
            'span_count': 0,
            'output_path': None,
        }

    # 2. 验证标注格式
    spans = SPAN_CLASS_PATTERN.findall(highlighted_content)
    for text in spans:
        text_len = len(text.strip())
        if text_len < 2 or text_len > 10:
            return {
                'success': False,
                'error': f'标注长度 {text_len} 超出 2-10 字范围: {text}',
                'span_count': 0,
                'output_path': None,
            }

    # 3. 确保有 style 块
    if '<style>' not in highlighted_content:
        highlighted_content = STYLE_BLOCK + '\n' + highlighted_content

    # 4. 写回文件
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(highlighted_content, encoding='utf-8')

    return {
        'success': True,
        'error': None,
        'span_count': len(spans),
        'output_path': str(out_path.resolve()),
    }


def find_diff_position(s1: str, s2: str, context_len: int = 20) -> str:
    """找出两个字符串首次不同的位置，返回上下文"""
    min_len = min(len(s1), len(s2))
    for i in range(min_len):
        if s1[i] != s2[i]:
            start = max(0, i - context_len)
            end = min(len(s1), i + context_len)
            return s1[start:end]
    if len(s1) != len(s2):
        return s1[min_len:min_len + context_len]
    return "未知"


def validate_file(file_path: str) -> dict:
    """
    验证已标注文件是否符合规则

    Returns:
        {
            'valid': bool,
            'errors': list,
            'span_count': int,
            'density': float,  # 每多少行一个标注
        }
    """
    content = Path(file_path).read_text(encoding='utf-8')
    errors = []

    # 检查 span 格式
    spans = list(SPAN_CLASS_PATTERN.finditer(content))

    # 检查是否有非法 span
    remaining = SPAN_CLASS_PATTERN.sub('', content)
    remaining = STYLE_BLOCK_PATTERN.sub('', remaining)
    if '<span' in remaining:
        errors.append('存在非标准格式的 span 标记')

    # 检查标注长度
    for m in spans:
        text = m.group(1)
        text_len = len(text.strip())
        if text_len < 2 or text_len > 10:
            errors.append(f'标注长度 {text_len} 超出范围: {text[:20]}')

    # 检查密度
    lines = [l for l in content.split('\n') if l.strip()]
    total_spans = len(spans)
    density = len(lines) / total_spans if total_spans > 0 else float('inf')

    if density < 4:
        errors.append(f'标注过密: 约每 {density:.1f} 行 1 处（建议 4-6 行）')
    elif density > 25:
        errors.append(f'标注过疏: 约每 {density:.1f} 行 1 处')

    # 检查是否有 == 高亮（禁止）
    if re.search(r'==[^=]+==', content):
        errors.append('存在 == 高亮标记（应使用 span）')

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'span_count': total_spans,
        'density': round(density, 1),
    }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description='md_highlight 辅助工具')
    subparsers = parser.add_subparsers(dest='command')

    # preprocess
    prep_parser = subparsers.add_parser('preprocess', help='预处理文件')
    prep_parser.add_argument('file', help='Markdown 文件路径')

    # validate
    val_parser = subparsers.add_parser('validate', help='验证标注文件')
    val_parser.add_argument('file', help='已标注的 Markdown 文件')

    # strip
    strip_parser = subparsers.add_parser('strip', help='移除标注，还原原文')
    strip_parser.add_argument('file', help='已标注的 Markdown 文件')
    strip_parser.add_argument('-o', '--output', help='输出文件路径')

    args = parser.parse_args()

    if args.command == 'preprocess':
        result = preprocess(args.file)
        print(f"文件: {args.file}")
        print(f"行数: {result['line_count']}")
        print(f"Hash: {result['hash']}")
        print(f"文本类型: {result['text_type']}")
        print(f"大文件: {'是' if result['is_large'] else '否'}")
        if result['is_large']:
            print(f"分段数: {len(result['segments'])}")

    elif args.command == 'validate':
        result = validate_file(args.file)
        print(f"文件: {args.file}")
        print(f"有效: {'是' if result['valid'] else '否'}")
        print(f"标注数: {result['span_count']}")
        print(f"密度: 每 {result['density']} 行 1 处")
        if result['errors']:
            print("错误:")
            for e in result['errors']:
                print(f"  - {e}")

    elif args.command == 'strip':
        content = Path(args.file).read_text(encoding='utf-8')
        stripped = strip_spans(content)
        output = args.output or args.file.replace('.md', '_stripped.md')
        Path(output).write_text(stripped, encoding='utf-8')
        print(f"已还原原文到: {output}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
