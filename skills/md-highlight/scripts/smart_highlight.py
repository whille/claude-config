#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能标注：章节驱动模式

核心流程：
for chapter in chapters:
    analysis = llm_analyze(chapter)  # 总结+洞察+关键词
    keywords = extract_keywords(analysis)
    highlight_chapter(chapter, keywords)

改进点：
1. 按章节分段（# 标题）
2. 每个章节独立LLM分析
3. 提取该章节的关键词
4. 标注该章节
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 导入现有 helper
try:
    from .md_highlight_helper import (
        STYLE_BLOCK, strip_spans, normalize, compute_hash, count_lines
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from md_highlight_helper import (
        STYLE_BLOCK, strip_spans, normalize, compute_hash, count_lines
    )


@dataclass
class Keyword:
    """关键词数据结构"""
    word: str
    type: str  # concept, conclusion, data, warning
    chapter: int = 0  # 所在章节编号


@dataclass
class ChapterAnalysis:
    """章节分析结果"""
    chapter_num: int
    chapter_title: str
    summary: List[str]
    insights: List[str]
    keywords: List[Keyword]


# 关键词类型映射
TYPE_TO_CLASS = {
    "concept": "hl-concept",
    "conclusion": "hl-conclusion",
    "data": "hl-data",
    "warning": "hl-warning",
}


def split_into_chapters(content: str) -> List[Tuple[int, int, str, str]]:
    """
    按章节分段（# 标题）

    Returns:
        [(start_line, end_line, chapter_title, chapter_text), ...]
    """
    lines = content.split('\n')
    chapters = []
    current_start = 0
    current_title = "前言"
    current_lines = []

    for i, line in enumerate(lines):
        # 检测章节标题（# 开头）
        if line.startswith('# ') and not line.startswith('## '):
            # 保存上一章
            if current_lines:
                chapters.append((
                    current_start,
                    i,
                    current_title,
                    '\n'.join(current_lines)
                ))
            # 开始新章节
            current_start = i
            current_title = line[2:].strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    # 最后一章
    if current_lines:
        chapters.append((
            current_start,
            len(lines),
            current_title,
            '\n'.join(current_lines)
        ))

    return chapters


def build_chapter_prompt(chapter_text: str, chapter_title: str) -> str:
    """
    构建章节分析 Prompt
    """
    return f"""你是阅读顾问，帮助读者从章节中提取最有价值的内容。

## 章节标题
{chapter_title}

## 章节内容
{chapter_text[:3000]}...

## 输出要求

从读者收获角度分析这个章节：

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


def parse_llm_response(response: str) -> Optional[Dict]:
    """
    解析 LLM 返回的 JSON
    """
    # 尝试提取 JSON 块
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 尝试直接解析
        json_str = response.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        return None


def apply_highlights_to_chapter(
    chapter_text: str,
    keywords: List[Keyword],
    global_highlighted: set
) -> Tuple[str, int]:
    """
    应用标注到章节

    Args:
        chapter_text: 章节文本
        keywords: 该章节的关键词列表
        global_highlighted: 全局已标注的词集合

    Returns:
        (标注后的文本, 新增标注数)
    """
    lines = chapter_text.split('\n')
    result_lines = []
    new_highlights = 0

    for line in lines:
        modified_line = line

        for kw in keywords:
            if kw.word in global_highlighted:
                continue  # 已标注过

            if kw.word not in modified_line:
                continue

            # 检查是否在代码块
            if '`' in modified_line:
                continue

            # 应用标注
            css_class = TYPE_TO_CLASS[kw.type]
            span_tag = f'<span class="{css_class}">{kw.word}</span>'
            modified_line = modified_line.replace(kw.word, span_tag, 1)
            global_highlighted.add(kw.word)
            new_highlights += 1

        result_lines.append(modified_line)

    return '\n'.join(result_lines), new_highlights


def smart_highlight_chapters(
    content: str,
    llm_callback=None,
    max_chapters: int = 10
) -> Dict:
    """
    章节驱动的智能标注

    Args:
        content: 原文内容
        llm_callback: LLM 调用函数
        max_chapters: 最多处理章节数（避免处理过长文件）

    Returns:
        {
            'success': bool,
            'highlighted_content': str,
            'total_highlights': int,
            'chapters_processed': int,
            'errors': list
        }
    """
    # 分章节
    chapters = split_into_chapters(content)
    print(f"文件分段: {len(chapters)} 章")

    # 限制处理章节数
    if len(chapters) > max_chapters:
        print(f"章节数过多，仅处理前 {max_chapters} 章")
        chapters = chapters[:max_chapters]

    # 全局已标注集合
    global_highlighted = set()
    total_highlights = 0
    processed_chapters = []
    errors = []

    for idx, (start, end, title, text) in enumerate(chapters, 1):
        print(f"\n处理第 {idx}/{len(chapters)} 章: {title}")
        print(f"  行数: {count_lines(text)}")

        # LLM 分析
        if llm_callback:
            prompt = build_chapter_prompt(text, title)
            response = llm_callback(prompt)

            # 解析结果
            analysis = parse_llm_response(response)
            if analysis:
                # 提取关键词
                keywords = []
                for kw in analysis.get('keywords', []):
                    word = kw.get('word', '').strip()
                    kw_type = kw.get('type', 'concept').strip()

                    if word and len(word) >= 2:
                        keywords.append(Keyword(
                            word=word,
                            type=kw_type,
                            chapter=idx
                        ))

                print(f"  提取关键词: {len(keywords)} 个")

                # 应用标注
                highlighted_text, new_highlights = apply_highlights_to_chapter(
                    text, keywords, global_highlighted
                )
                total_highlights += new_highlights
                print(f"  新增标注: {new_highlights} 处")

                processed_chapters.append((start, end, highlighted_text))
            else:
                errors.append(f"第 {idx} 章解析失败")
                processed_chapters.append((start, end, text))
        else:
            # 无 LLM 回调，保持原样
            processed_chapters.append((start, end, text))

    # 重组文件
    lines = content.split('\n')
    result_lines = []

    # 找出未处理的章节部分
    current_pos = 0
    for start, end, text in processed_chapters:
        # 添加未处理的部分
        if start > current_pos:
            result_lines.extend(lines[current_pos:start])

        # 添加处理后的章节
        result_lines.extend(text.split('\n'))
        current_pos = end

    # 添加剩余部分
    if current_pos < len(lines):
        result_lines.extend(lines[current_pos:])

    # 添加 style 块
    result = STYLE_BLOCK + '\n'.join(result_lines)

    return {
        'success': True,
        'highlighted_content': result,
        'total_highlights': total_highlights,
        'chapters_processed': len(processed_chapters),
        'errors': errors
    }


def main():
    """CLI 测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能标注 Markdown 文件（章节驱动）')
    parser.add_argument('file', help='Markdown 文件路径')
    parser.add_argument('--max-chapters', type=int, default=10, help='最多处理章节数')

    args = parser.parse_args()

    print("⚠️  CLI 模式仅用于测试")
    print("    生产环境请通过 Claude Skill 调用\n")

    path = Path(args.file)
    if path.exists():
        content = path.read_text(encoding='utf-8')
        chapters = split_into_chapters(content)

        print(f"文件: {args.file}")
        print(f"总行数: {count_lines(content)}")
        print(f"章节数: {len(chapters)}\n")

        for i, (s, e, title, text) in enumerate(chapters[:args.max_chapters], 1):
            print(f"  章 {i}: {title} (行 {s}-{e}, {count_lines(text)} 行)")


if __name__ == '__main__':
    main()
