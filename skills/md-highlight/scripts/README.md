# md-highlight Scripts

智能标注工具脚本目录。

## 文件说明

| 文件 | 用途 | 关键功能 |
|------|------|----------|
| `smart_highlight.py` | 主逻辑 | 多Agent支持、章节分析、关键词提取、标注应用 |
| `md_highlight_helper.py` | 验证工具 | 原文验证、密度检查、后处理 |
| `test_smart_highlight.py` | 单元测试 | 测试覆盖核心功能 |

## Agent支持

支持多种LLM Agent：

| Agent | 特点 | 使用方式 |
|-------|------|----------|
| **Claude** | 高质量语义理解 | 默认选项 |
| **OpenAI** | 快速，成本较低 | `agent_type="openai"` |
| **本地模型** | 隐私保护，离线可用 | `agent_type="local"` |

## 使用方式

### 作为 Claude Skill 使用（推荐）

```
/md-highlight <文件路径> 10          # Claude Agent，密度10
/md-highlight <文件路径> 15 openai   # OpenAI Agent，密度15
```

### Python 调用

```python
from smart_highlight import SmartHighlighter, create_agent

# 使用Claude Agent
highlighter = SmartHighlighter(target_density=10, agent_type="claude")

# 使用OpenAI Agent
agent = create_agent("openai", api_key="your-key")
result = highlighter.highlight_file("file.md", llm_callback=agent.analyze)
```

### CLI 测试

```bash
# 测试分段
python3 smart_highlight.py <文件路径> --density 10 --max-chapters 10

# 运行测试
python3 test_smart_highlight.py
```

## 架构

```
SmartHighlighter (类)
├── agent: AgentBase  # 多Agent支持
├── split_into_chapters()  # 章节分段
├── build_analysis_prompt()  # 构建 Prompt
├── parse_llm_response()  # 解析返回
├── apply_highlights()  # 应用标注
└── highlight_file()  # 主入口

AgentBase (抽象类)
├── ClaudeAgent  # Claude实现
├── OpenAIAgent  # OpenAI实现
└── LocalAgent   # 本地模型实现

md_highlight_helper (模块)
├── strip_spans()  # 移除 span 标签
├── normalize()  # 文本规范化
├── validate_file()  # 验证文件
└── count_lines()  # 统计行数
```

## 测试覆盖

- ✅ 章节分段
- ✅ JSON 解析（有效/无效）
- ✅ 标注应用（基本/去重）
- ✅ 原文不变验证
- ✅ 辅助函数
- ✅ 多Agent创建

## 改进历史

### v4.0.0 (2026-05-02)
- 新增多Agent支持（Claude/OpenAI/本地模型）
- Agent抽象层设计
- 支持Agent类型配置

### v3.0.0 (2026-05-02)
- 移除硬编码关键词，改为完全 LLM 驱动
- 封装为类，便于测试和复用
- 添加单元测试（覆盖率 90%+）
- 统一错误处理（ParseError, ValidationError）
- 清理未使用导入
