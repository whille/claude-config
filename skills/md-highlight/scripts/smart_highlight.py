#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能标注：基于 LLM 总结洞察，提取关键词，标注原文

核心流程：
原文 → LLM总结+洞察+关键词 → 在原文定位关键词 → 应用标注
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 导入现有 helper
try:
    from .md_highlight_helper import (
        STYLE_BLOCK, SPAN_CLASS_PATTERN, STYLE_BLOCK_PATTERN,
        strip_spans, normalize, compute_hash, count_lines
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from md_highlight_helper import (
        STYLE_BLOCK, SPAN_CLASS_PATTERN, STYLE_BLOCK_PATTERN,
        strip_spans, normalize, compute_hash, count_lines
    )


@dataclass
class Keyword:
    """关键词数据结构"""
    word: str
    type: str  # concept, conclusion, data, warning
    context: str = ""  # 原文中包含该词的句子片段（用于验证）


@dataclass
class SegmentAnalysis:
    """段落分析结果"""
    summary: List[str]
    insights: List[str]
    keywords: List[Keyword]


# 关键词类型映射（LLM 输出 → CSS class）
TYPE_TO_CLASS = {
    "concept": "hl-concept",
    "conclusion": "hl-conclusion",
    "data": "hl-data",
    "warning": "hl-warning",
}


def split_into_segments(content: str, max_lines: int = 400) -> List[Tuple[int, int, str]]:
    """
    智能分段：优先按标题，无标题时按固定长度

    Args:
        content: 原文内容
        max_lines: 每段最大行数

    Returns:
        [(start_line, end_line, segment_text), ...]
    """
    lines = content.split('\n')
    segments = []
    current_start = 0
    current_lines = []

    for i, line in enumerate(lines):
        current_lines.append(line)

        # 遇到 ## 标题，且当前段已够长
        is_header = line.startswith('##') and not line.startswith('###')
        should_split = is_header and len(current_lines) >= max_lines // 3

        # 或达到最大长度
        if should_split or len(current_lines) >= max_lines:
            segments.append((current_start, i, '\n'.join(current_lines)))
            current_start = i + 1
            current_lines = []

    # 最后一段
    if current_lines:
        segments.append((current_start, len(lines), '\n'.join(current_lines)))

    return segments


def build_analysis_prompt(segment: str) -> str:
    """
    构建 LLM 分析 Prompt

    Prompt 策略：
    1. 明确任务：从读者价值角度分析
    2. 给出类型定义和示例
    3. 强调关键词必须在原文中存在
    4. 控制数量（避免过度标注）
    """
    return f"""你是阅读顾问，帮助读者从文章中提取最有价值的内容。

分析下面这段文字，从读者收获角度输出：

## 文字内容
{segment}

## 输出要求

1. **总结**（3-5条）：本章核心内容，每条10-20字
2. **洞察**（2-3条）：读者能获得的收获
3. **关键词**（5-10个）：原文中出现的、对读者最有帮助的词

## 输出格式（JSON）

```json
{{
  "summary": ["总结1", "总结2", ...],
  "insights": ["洞察1", "洞察2", ...],
  "keywords": [
    {{"word": "关键词", "type": "类型"}},
    ...
  ]
}}
```

## 关键词类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| concept | 方法、概念、可行动的内容 | "生存技能"、"提前准备" |
| conclusion | 洞见、核心原则 | "顺势而为"、"有心人" |
| data | 关键数据（不含年份） | "5万"、"18个月" |
| warning | 警示、谚语、风险提示 | "天上不会掉馅饼" |

## 注意事项

- 关键词必须是原文中出现的词（2-6字）
- 每个类型最多3个关键词
- 全文同类词只标注最重要的
- 年份一般不标注（除非是关键时间节点）
- 人名、机构名全文只标注第一次出现

## 质量标准

问自己：标注这个词，读者能获得什么？
- 如果是方法 → 可行动
- 如果是洞见 → 颠覆认知
- 如果是数据 → 增强说服力
- 如果是警示 → 避坑

只标注对读者最有价值的词，宁缺毋滥。
"""


def parse_llm_response(response: str) -> Optional[SegmentAnalysis]:
    """
    解析 LLM 返回的 JSON

    Args:
        response: LLM 返回的文本（可能包含 markdown 代码块）

    Returns:
        SegmentAnalysis 对象，解析失败返回 None
    """
    # 尝试提取 JSON 块
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 尝试直接解析
        json_str = response.strip()

    try:
        data = json.loads(json_str)

        keywords = []
        for kw in data.get('keywords', []):
            word = kw.get('word', '').strip()
            kw_type = kw.get('type', '').strip()

            # 验证类型
            if kw_type not in TYPE_TO_CLASS:
                kw_type = 'concept'  # 默认类型

            if word and len(word) >= 2:
                keywords.append(Keyword(word=word, type=kw_type))

        return SegmentAnalysis(
            summary=data.get('summary', []),
            insights=data.get('insights', []),
            keywords=keywords
        )
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        return None


def find_keyword_in_text(keyword: str, text: str) -> Optional[Tuple[int, int]]:
    """
    在原文中查找关键词位置

    Args:
        keyword: 关键词
        text: 原文

    Returns:
        (start, end) 位置，未找到返回 None
    """
    # 直接查找
    pos = text.find(keyword)
    if pos != -1:
        return (pos, pos + len(keyword))

    return None


def apply_highlights(content: str, all_keywords: List[Keyword]) -> str:
    """
    应用标注到原文

    Args:
        content: 原文内容
        all_keywords: 所有段落的聚合关键词（已去重）

    Returns:
        标注后的内容
    """
    # 全局去重：记录已标注的词
    highlighted_words = set()

    # 按关键词长度降序排列（优先匹配长词）
    sorted_keywords = sorted(all_keywords, key=lambda k: len(k.word), reverse=True)

    # 分行处理，避免跨行匹配
    lines = content.split('\n')
    result_lines = []

    for line in lines:
        modified_line = line

        for kw in sorted_keywords:
            if kw.word in highlighted_words:
                continue  # 已标注过

            if kw.word not in modified_line:
                continue  # 原文中不存在

            # 查找位置
            pos = modified_line.find(kw.word)
            if pos == -1:
                continue

            # 检查是否在代码块、链接等特殊位置
            # 简单检查：前面是否有 ` 或 [
            before = modified_line[:pos]
            if '`' in before and before.rfind('`') > before.rfind('`', 0, before.rfind('`')):
                continue  # 在代码块内
            if '[' in before and ']' not in before[before.rfind('['):]:
                # 可能是链接文本，跳过
                pass

            # 应用标注
            css_class = TYPE_TO_CLASS[kw.type]
            span_tag = f'<span class="{css_class}">{kw.word}</span>'

            # 只替换第一次出现（避免全文替换导致混乱）
            modified_line = modified_line.replace(kw.word, span_tag, 1)
            highlighted_words.add(kw.word)

        result_lines.append(modified_line)

    # 添加 style 块
    result = '\n'.join(result_lines)
    if '<style>' not in result:
        result = STYLE_BLOCK + '\n' + result

    return result


def validate_highlighted_content(original: str, highlighted: str) -> Tuple[bool, str]:
    """
    验证标注后内容不变

    Returns:
        (success, error_message)
    """
    original_norm = normalize(original)
    highlighted_stripped = strip_spans(highlighted)
    highlighted_norm = normalize(highlighted_stripped)

    if original_norm != highlighted_norm:
        # 找出差异位置
        diff_pos = find_diff_position(original_norm, highlighted_norm)
        return False, f"原文内容被修改！差异位置: ...{diff_pos}..."

    # 检查标注数量
    spans = SPAN_CLASS_PATTERN.findall(highlighted)
    if len(spans) == 0:
        return False, "没有任何标注"

    # 检查密度
    lines = count_lines(highlighted)
    density = lines / len(spans)
    if density < 4:
        return False, f"标注过密: 每 {density:.1f} 行 1 处"

    return True, ""


def find_diff_position(s1: str, s2: str, context_len: int = 30) -> str:
    """找出差异位置，返回上下文"""
    min_len = min(len(s1), len(s2))
    for i in range(min_len):
        if s1[i] != s2[i]:
            start = max(0, i - context_len)
            end = min(len(s1), i + context_len)
            return s1[start:end]
    return "未知"


def smart_highlight_file(
    file_path: str,
    output_path: Optional[str] = None,
    llm_callback=None
) -> Dict:
    """
    智能标注文件

    Args:
        file_path: 输入文件路径
        output_path: 输出文件路径（默认：原文件名_highlighted.md）
        llm_callback: LLM 调用函数（用于外部注入，避免硬编码 API）

    Returns:
        {
            'success': bool,
            'output_path': str,
            'span_count': int,
            'segments_processed': int,
            'errors': list
        }
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    content = path.read_text(encoding='utf-8')
    original_hash = compute_hash(content)

    # 分段
    segments = split_into_segments(content)
    print(f"文件分段: {len(segments)} 段")

    # 收集所有关键词
    all_keywords = []

    for idx, (start, end, segment) in enumerate(segments):
        print(f"处理第 {idx + 1}/{len(segments)} 段...")

        # 调用 LLM 分析
        if llm_callback:
            prompt = build_analysis_prompt(segment)
            response = llm_callback(prompt)
        else:
            # 如果没有提供 LLM 回调，返回错误
            return {
                'success': False,
                'output_path': None,
                'span_count': 0,
                'segments_processed': idx,
                'errors': ['未提供 LLM 回调函数']
            }

        # 解析结果
        analysis = parse_llm_response(response)
        if analysis:
            all_keywords.extend(analysis.keywords)
            print(f"  - 提取关键词: {len(analysis.keywords)} 个")

    # 去重
    unique_keywords = []
    seen_words = set()
    for kw in all_keywords:
        if kw.word not in seen_words:
            unique_keywords.append(kw)
            seen_words.add(kw.word)

    print(f"去重后关键词: {len(unique_keywords)} 个")

    # 应用标注
    highlighted = apply_highlights(content, unique_keywords)

    # 验证
    success, error = validate_highlighted_content(content, highlighted)
    if not success:
        return {
            'success': False,
            'output_path': None,
            'span_count': 0,
            'segments_processed': len(segments),
            'errors': [error]
        }

    # 写回文件
    out_path = Path(output_path) if output_path else path.parent / f"{path.stem}_highlighted.md"
    out_path.write_text(highlighted, encoding='utf-8')

    return {
        'success': True,
        'output_path': str(out_path),
        'span_count': len(unique_keywords),
        'segments_processed': len(segments),
        'errors': []
    }


# Claude Skill 入口
# 当作为 Skill 被调用时，由 Claude 提供 llm_callback


def main():
    """CLI 测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能标注 Markdown 文件')
    parser.add_argument('file', help='Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')

    args = parser.parse_args()

    print("⚠️  CLI 模式仅用于测试，生产环境请通过 Claude Skill 调用")
    print("    需要 LLM 回调函数才能正常工作")

    # 测试分段
    path = Path(args.file)
    if path.exists():
        content = path.read_text(encoding='utf-8')
        segments = split_into_segments(content)
        print(f"\n文件: {args.file}")
        print(f"总行数: {count_lines(content)}")
        print(f"分段数: {len(segments)}")
        for i, (s, e, seg) in enumerate(segments):
            print(f"  段 {i+1}: 行 {s}-{e} ({count_lines(seg)} 行)")


if __name__ == '__main__':
    main()
