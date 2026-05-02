#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能标注：多Agent章节驱动方案

支持多种LLM Agent:
- Claude (默认)
- OpenAI
- 本地模型

核心流程：
for chapter in chapters:
    analysis = agent.analyze(chapter)
    keywords = extract_keywords(analysis)
    highlight_chapter(chapter, keywords)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum


# ============================================================================
# 异常定义
# ============================================================================

class ParseError(Exception):
    """JSON解析错误"""
    pass


class ValidationError(Exception):
    """验证错误"""
    pass


# ============================================================================
# 枚举定义
# ============================================================================

class HighlightType(Enum):
    """标注类型枚举"""
    CONCEPT = "concept"
    CONCLUSION = "conclusion"
    DATA = "data"
    WARNING = "warning"


# 导入验证工具
try:
    from .md_highlight_helper import strip_spans, normalize, count_lines
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from md_highlight_helper import strip_spans, normalize, count_lines


# ============================================================================
# Agent抽象层
# ============================================================================

class AgentBase(ABC):
    """Agent基类"""

    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """分析并返回结果"""
        pass


class ClaudeAgent(AgentBase):
    """Claude Agent（默认）"""

    def __init__(self):
        self.name = "Claude"

    def analyze(self, prompt: str) -> str:
        """
        由Claude提供回调实现

        在Skill模式下，Claude会注入回调函数
        """
        # 占位符，实际由Claude注入
        raise NotImplementedError("Claude Agent需要外部注入回调函数")


class OpenAIAgent(AgentBase):
    """OpenAI Agent"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.name = "OpenAI"
        self.api_key = api_key
        self.model = model

    def analyze(self, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("请安装openai: pip install openai")


class LocalAgent(AgentBase):
    """本地模型Agent"""

    def __init__(self, model_path: Optional[str] = None):
        self.name = "Local"
        self.model_path = model_path

    def analyze(self, prompt: str) -> str:
        """调用本地模型"""
        # 占位符，可以接入Ollama、llama.cpp等
        raise NotImplementedError("本地模型Agent需要实现")


def create_agent(agent_type: str = "claude", **kwargs) -> AgentBase:
    """创建Agent实例"""
    agents = {
        "claude": ClaudeAgent,
        "openai": OpenAIAgent,
        "local": LocalAgent,
    }

    agent_class = agents.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"不支持的Agent类型: {agent_type}")

    return agent_class(**kwargs)


# ============================================================================
# 数据结构
# ============================================================================


@dataclass
class Keyword:
    """关键词数据结构"""
    word: str
    type: HighlightType  # 使用枚举类型
    chapter: int = 0
    reason: str = ""


@dataclass
class ChapterAnalysis:
    """章节分析结果"""
    chapter_num: int
    chapter_title: str
    summary: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    keywords: List[Keyword] = field(default_factory=list)


# 样式块
STYLE_BLOCK = """<style>
.hl-concept { background-color:#d1ecf1; padding:2px 4px; border-radius:3px; }
.hl-conclusion { background-color:#fff3cd; padding:2px 4px; border-radius:3px; }
.hl-data { background-color:#d4edda; padding:2px 4px; border-radius:3px; }
.hl-warning { background-color:#fff2e6; padding:2px 4px; border-radius:3px; }
</style>

"""


class SmartHighlighter:
    """智能标注器（多Agent章节驱动方案）"""

    def __init__(
        self,
        target_density: int = 10,
        agent_type: str = "claude"
    ):
        """
        初始化标注器

        Args:
            target_density: 目标标注密度（每N行1处），默认10
            agent_type: Agent类型（claude/openai/local），默认claude
        """
        self.target_density = target_density
        self.agent_type = agent_type
        self.agent = create_agent(agent_type)
        self.global_highlighted: set = set()
        self.highlight_counts: Dict[str, int] = {}

    def split_into_chapters(self, content: str) -> List[tuple]:
        """按章节分段"""
        lines = content.split('\n')
        chapters = []
        current_start = 0
        current_title = "前言"
        current_lines = []

        for i, line in enumerate(lines):
            if line.startswith('# ') and not line.startswith('## '):
                if current_lines:
                    chapters.append((
                        current_start,
                        i,
                        current_title,
                        '\n'.join(current_lines)
                    ))
                current_start = i
                current_title = line[2:].strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            chapters.append((
                current_start,
                len(lines),
                current_title,
                '\n'.join(current_lines)
            ))

        return chapters

    def build_analysis_prompt(self, chapter_text: str, chapter_title: str, chapter_num: int) -> str:
        """构建LLM分析Prompt"""
        return f"""分析这个章节，从读者价值角度提取关键词。

## 章节信息
章节编号: {chapter_num}
章节标题: {chapter_title}

## 章节内容
{chapter_text[:2500]}...

## 输出要求

1. **总结**（3-5条）：本章核心内容，每条10-20字
2. **洞察**（2-3条）：读者能获得的收获
3. **关键词**（5-10个）：原文中出现的、对读者最有帮助的词

## 输出格式（JSON）

```json
{{
  "summary": ["总结1", "总结2"],
  "insights": ["洞察1", "洞察2"],
  "keywords": [
    {{"word": "关键词", "type": "类型", "reason": "理由"}}
  ]
}}
```

## 关键词类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| conclusion | 洞见、核心原则 | "物极必反"、"顺势而为" |
| concept | 方法、可行动内容 | "实地考察"、"提前准备" |
| data | 关键数据 | "5万"、"18个月" |
| warning | 警示、谚语 | "天上不会掉馅饼" |

## 重要规则

1. 关键词必须是原文中出现的词（2-6字）
2. 每个类型最多3个关键词
3. 物品名不标注（如：大蒜、棉花、大豆）
4. 人名全书只标第一次出现
5. 每个关键词只标一次（全局去重）

## 质量标准

问自己：标注这个词，读者能获得什么？
- 如果是洞见 → 颠覆认知
- 如果是方法 → 可行动
- 如果是数据 → 增强说服力
- 如果是警示 → 避坑

只标注对读者最有价值的词，宁缺毋滥。
"""

    def parse_llm_response(self, response: str, chapter_num: int) -> ChapterAnalysis:
        """解析LLM返回的JSON"""
        # 提取JSON块
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ParseError(f"JSON解析失败: {e}")

        # 类型映射字符串到枚举
        type_map = {
            'concept': HighlightType.CONCEPT,
            'conclusion': HighlightType.CONCLUSION,
            'data': HighlightType.DATA,
            'warning': HighlightType.WARNING,
        }

        keywords = []
        for kw in data.get('keywords', []):
            word = kw.get('word', '').strip()
            kw_type_str = kw.get('type', 'concept').strip()
            reason = kw.get('reason', '').strip()

            if word and len(word) >= 2 and len(word) <= 10:
                kw_type = type_map.get(kw_type_str, HighlightType.CONCEPT)
                keywords.append(Keyword(
                    word=word,
                    type=kw_type,
                    chapter=chapter_num,
                    reason=reason
                ))

        return ChapterAnalysis(
            chapter_num=chapter_num,
            chapter_title=f"Chapter {chapter_num}",
            summary=data.get('summary', []),
            insights=data.get('insights', []),
            keywords=keywords
        )

    def apply_highlights(self, content: str, all_keywords: List[Keyword]) -> str:
        """应用标注到原文"""
        # 按关键词长度降序排列（优先匹配长词）
        sorted_keywords = sorted(all_keywords, key=lambda k: len(k.word), reverse=True)

        lines = content.split('\n')
        result_lines = []

        for line in lines:
            modified_line = line

            for kw in sorted_keywords:
                if kw.word in self.global_highlighted:
                    continue

                if kw.word not in modified_line:
                    continue

                # 跳过代码块、表格
                if '`' in modified_line or '<table' in modified_line or '<div' in modified_line:
                    continue

                # 应用标注
                css_class = f"hl-{kw.type.value}"
                span_tag = f'<span class="{css_class}">{kw.word}</span>'
                modified_line = modified_line.replace(kw.word, span_tag, 1)
                self.global_highlighted.add(kw.word)
                self.highlight_counts[kw.word] = self.highlight_counts.get(kw.word, 0) + 1

            result_lines.append(modified_line)

        return STYLE_BLOCK + '\n'.join(result_lines)

    def highlight_file(
        self,
        file_path: str,
        llm_callback: Optional[Callable[[str], str]] = None,
        max_chapters: int = 50
    ) -> Dict:
        """
        智能标注文件

        Args:
            file_path: 输入文件路径
            llm_callback: LLM调用函数（由Claude提供）
            max_chapters: 最多处理章节数

        Returns:
            标注结果字典
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        content = path.read_text(encoding='utf-8')
        total_lines = count_lines(content)

        # 分章节
        chapters = self.split_into_chapters(content)
        if len(chapters) > max_chapters:
            chapters = chapters[:max_chapters]

        print(f"文件: {file_path}")
        print(f"总行数: {total_lines}")
        print(f"章节数: {len(chapters)}")
        print(f"目标密度: 每 {self.target_density} 行 1 处")
        print(f"目标标注数: {total_lines // self.target_density} 处\n")

        all_keywords = []
        errors = []

        # 分析每个章节
        for idx, (start, end, title, text) in enumerate(chapters, 1):
            print(f"处理第 {idx}/{len(chapters)} 章: {title[:30]}...")

            if llm_callback:
                try:
                    prompt = self.build_analysis_prompt(text, title, idx)
                    response = llm_callback(prompt)
                    analysis = self.parse_llm_response(response, idx)
                    all_keywords.extend(analysis.keywords)
                    print(f"  ✓ 提取关键词: {len(analysis.keywords)} 个")
                except Exception as e:
                    errors.append(f"第 {idx} 章分析失败: {e}")
                    print(f"  ✗ 分析失败: {e}")
            else:
                errors.append(f"未提供LLM回调函数，跳过第 {idx} 章")

        print(f"\n提取关键词总数: {len(all_keywords)} 个")

        # 去重
        unique_keywords = []
        seen_words = set()
        for kw in all_keywords:
            if kw.word not in seen_words:
                unique_keywords.append(kw)
                seen_words.add(kw.word)

        print(f"去重后关键词数: {len(unique_keywords)} 个\n")

        # 应用标注
        highlighted = self.apply_highlights(content, unique_keywords)

        # 验证原文不变
        original_norm = normalize(content)
        highlighted_stripped = strip_spans(highlighted)
        highlighted_norm = normalize(highlighted_stripped)

        if original_norm != highlighted_norm:
            raise ValueError("原文内容被修改，标注失败")

        # 计算密度
        total_spans = len(self.global_highlighted)
        density = total_lines / total_spans if total_spans > 0 else 0

        # 写回文件
        output_path = path.parent / f"{path.stem}_highlighted.md"
        output_path.write_text(highlighted, encoding='utf-8')

        print(f"✅ 标注完成")
        print(f"实际标注数: {total_spans} 处")
        print(f"实际密度: 每 {density:.1f} 行 1 处")
        print(f"输出文件: {output_path}")

        return {
            'success': len(errors) == 0,
            'output_path': str(output_path),
            'total_highlights': total_spans,
            'density': density,
            'target_density': self.target_density,
            'chapters_processed': len(chapters),
            'keywords_extracted': len(unique_keywords),
            'errors': errors
        }


def main():
    """CLI测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能标注Markdown文件')
    parser.add_argument('file', help='Markdown文件路径')
    parser.add_argument('--density', type=int, default=10, help='目标密度（每N行1处）')
    parser.add_argument('--max-chapters', type=int, default=50, help='最多处理章节数')

    args = parser.parse_args()

    print("⚠️  CLI模式仅用于测试")
    print("    生产环境请通过Claude Skill调用\n")

    highlighter = SmartHighlighter(target_density=args.density)
    path = Path(args.file)

    if path.exists():
        content = path.read_text(encoding='utf-8')
        chapters = highlighter.split_into_chapters(content)

        print(f"文件: {args.file}")
        print(f"总行数: {count_lines(content)}")
        print(f"章节数: {len(chapters)}\n")

        for i, (s, e, title, text) in enumerate(chapters[:args.max_chapters], 1):
            print(f"  章 {i}: {title[:40]} (行 {s}-{e}, {count_lines(text)} 行)")


if __name__ == '__main__':
    main()
