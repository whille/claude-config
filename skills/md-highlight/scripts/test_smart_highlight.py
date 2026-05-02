#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：智能标注工具

测试覆盖：
1. 章节分段
2. JSON 解析
3. 标注应用
4. 验证机制
"""

import unittest
from pathlib import Path
import sys
import os

# 添加路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 切换到脚本目录（确保相对导入正常）
os.chdir(script_dir)

from smart_highlight import (
    SmartHighlighter, Keyword, HighlightType,
    ParseError, ValidationError
)
from md_highlight_helper import strip_spans, normalize


class TestSmartHighlighter(unittest.TestCase):
    """测试 SmartHighlighter 类"""

    def setUp(self):
        """测试前准备"""
        self.highlighter = SmartHighlighter()

    def test_split_into_chapters(self):
        """测试章节分段"""
        content = """# 前言
前言内容

# 第一章 标题
第一章内容

# 第二章 标题
第二章内容
"""
        chapters = self.highlighter.split_into_chapters(content)

        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0][2], "前言")
        self.assertEqual(chapters[1][2], "第一章 标题")
        self.assertEqual(chapters[2][2], "第二章 标题")

    def test_parse_llm_response_valid(self):
        """测试有效 JSON 解析"""
        response = '''```json
{
  "summary": ["总结1", "总结2"],
  "insights": ["洞察1"],
  "keywords": [
    {"word": "傅海棠", "type": "concept"},
    {"word": "物极必反", "type": "conclusion"}
  ]
}
```'''
        analysis = self.highlighter.parse_llm_response(response, 1)

        self.assertEqual(len(analysis.keywords), 2)
        self.assertEqual(analysis.keywords[0].word, "傅海棠")
        self.assertEqual(analysis.keywords[0].type, HighlightType.CONCEPT)

    def test_parse_llm_response_invalid_json(self):
        """测试无效 JSON 解析"""
        response = "这不是 JSON"

        with self.assertRaises(ParseError):
            self.highlighter.parse_llm_response(response, 1)

    def test_apply_highlights_basic(self):
        """测试基本标注应用"""
        content = "傅海棠是期货投资传奇人物。"
        keywords = [
            Keyword(word="傅海棠", type=HighlightType.CONCEPT),
            Keyword(word="期货", type=HighlightType.CONCEPT),
        ]

        result = self.highlighter.apply_highlights(content, keywords)

        self.assertIn('<span class="hl-concept">傅海棠</span>', result)
        self.assertIn('<span class="hl-concept">期货</span>', result)

    def test_apply_highlights_dedup(self):
        """测试全局去重"""
        content = "傅海棠是期货传奇。傅海棠的故事很多。"
        keywords = [
            Keyword(word="傅海棠", type=HighlightType.CONCEPT),
        ]

        result = self.highlighter.apply_highlights(content, keywords)

        # 只标注第一次出现
        self.assertEqual(result.count('<span class="hl-concept">傅海棠</span>'), 1)

    def test_content_unchanged(self):
        """测试原文内容不变"""
        content = "傅海棠是期货投资传奇人物，被誉为北丐。"
        keywords = [
            Keyword(word="傅海棠", type=HighlightType.CONCEPT),
            Keyword(word="期货", type=HighlightType.CONCEPT),
        ]

        result = self.highlighter.apply_highlights(content, keywords)

        # 验证原文不变
        original_norm = normalize(content)
        result_stripped = strip_spans(result)
        result_norm = normalize(result_stripped)

        self.assertEqual(original_norm, result_norm)


class TestKeyword(unittest.TestCase):
    """测试 Keyword 数据类"""

    def test_keyword_creation(self):
        """测试关键词创建"""
        kw = Keyword(word="傅海棠", type=HighlightType.CONCEPT, chapter=1)

        self.assertEqual(kw.word, "傅海棠")
        self.assertEqual(kw.type, HighlightType.CONCEPT)
        self.assertEqual(kw.chapter, 1)


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""

    def test_strip_spans(self):
        """测试移除 span 标签"""
        text = '你好<span class="hl-concept">傅海棠</span>是世界'

        result = strip_spans(text)

        self.assertEqual(result, '你好傅海棠是世界')

    def test_normalize(self):
        """测试文本规范化"""
        text = "你好  世界\n\n傅海棠"

        result = normalize(text)

        # 移除多余空格和换行
        self.assertEqual(result, "你好世界傅海棠")


class TestHighlightTypes(unittest.TestCase):
    """测试标注类型"""

    def test_highlight_types(self):
        """测试所有标注类型"""
        types = [
            (HighlightType.CONCEPT, "concept"),
            (HighlightType.CONCLUSION, "conclusion"),
            (HighlightType.DATA, "data"),
            (HighlightType.WARNING, "warning"),
        ]

        for ht, expected in types:
            self.assertEqual(ht.value, expected)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
