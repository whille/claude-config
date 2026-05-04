---
name: learn-history
version: 1.0.0
description: Analyze conversation history across projects to extract patterns and suggest rules/hooks.
user-invocable: true
argument-hint: "[--all] [--days N] [--dry-run]"
triggers:
  - "learn history"
  - "分析历史"
  - "学习模式"
last_updated: 2026-05-04
---

# Learn History Skill

Analyze historical conversations across projects and suggest improvements.

**Key Difference from `/learner`**: This analyzes **all historical conversations**, not just current session.

---

## Features

| Feature | Description |
|---------|-------------|
| **Cross-project analysis** | `--all` flag analyzes all projects |
| **Suggestion mode** | Outputs recommendations, requires user confirmation |
| **Pattern detection** | Clarifications, corrections, repetitions, preferences |
| **Rule/Hook generation** | Auto-generates rule and hook templates |

---

## Usage

```bash
# Analyze current project (last 7 days)
/learn-history

# Analyze current project (last 30 days)
/learn-history --days 30

# Analyze ALL projects
/learn-history --all

# Analyze ALL projects (last 30 days)
/learn-history --all --days 30

# Dry run (show suggestions only, no files created)
/learn-history --all --dry-run
```

---

## Output

### 1. Analysis Report

```
📊 学习报告
├─ 项目数: 5
├─ 对话数: 1234
├─ 时间范围: 2026-04-01 ~ 2026-05-01
│
├─ 发现的模式:
│  ├─ 澄清请求: 23 次
│  ├─ 纠正: 15 次
│  ├─ 重复问题: 8 次
│  └─ 偏好表达: 12 次
│
└─ 建议改进:
   ├─ 规则: 3 个
   └─ Hook: 1 个
```

### 2. Suggested Rules

```markdown
## 建议: Scope Clarification Rule

**触发条件**: 用户问"当前"、"改动"、"配置"

**问题示例**:
- "当前的配置是什么？" → AI 回答了服务器配置，用户指的是本地
- "刚才的改动呢？" → AI 列出了 git diff，用户指的是回测参数

**建议规则**:
在回答涉及"当前"、"改动"等问题时，先确认范围。

**是否采纳此规则？**
[ ] 采纳 → 保存到 ~/.claude/rules/scope-clarification.md
[ ] 跳过
```

### 3. Suggested Hooks

```markdown
## 建议: Pre-Commit Test Hook

**触发条件**: git commit 时修改了 backtest/*.py

**问题示例**:
- 多次提交后发现测试失败，需要回滚

**建议 Hook**:
提交前自动运行 pytest tests/unit/test_backtest.py

**是否采纳此 Hook？**
[ ] 采纳 → 添加到 settings.json hooks
[ ] 跳过
```

---

## Workflow

### Step 1: Collect Conversations

```bash
# Single project
~/.claude/projects/-Users-wangzhiguo-github-com-stockq/*.jsonl

# All projects (--all)
~/.claude/projects/*/*.jsonl
```

### Step 2: Extract Patterns

| Pattern | Signals | Suggested Action |
|---------|---------|------------------|
| **Clarification** | "你指的是"、"我问的是" | Create clarification rule |
| **Correction** | "不对"、"错了"、"不是" | Create prevention rule |
| **Repetition** | Same question 3+ times | Create automation hook |
| **Preference** | "我喜欢"、"用xxx格式" | Update MEMORY.md |

### Step 3: Generate Suggestions

Output suggestions in a structured format:

```
📋 建议采纳的改进 (共 4 项)

## [1/4] 规则: scope-clarification.md
**问题**: 用户澄清了 23 次
**建议**: 在回答"当前"、"改动"前先确认范围
**保存位置**: ~/.claude/rules/scope-clarification.md

--- 预览 ---
[规则内容]
--- 预览结束 ---

是否采纳？ (y/n/skip-all)
```

### Step 4: User Confirmation

After each suggestion, prompt user:
- `y` → Save the rule/hook
- `n` → Skip this suggestion
- `skip-all` → Skip remaining suggestions
- `preview` → Show full content before deciding

---

## Command-Line Script

```bash
# Analyze all projects
python3 ~/.claude/skills/learn-history/scripts/analyze_conversations.py --all

# Analyze specific project
python3 ~/.claude/skills/learn-history/scripts/analyze_conversations.py -p stockq -d 30

# Dry run (no files created)
python3 ~/.claude/skills/learn-history/scripts/analyze_conversations.py --all --dry-run

# Save suggestions to file for review
python3 ~/.claude/skills/learn-history/scripts/analyze_conversations.py --all --output /tmp/suggestions.md
```

---

## Output Locations

| Output | Location | Note |
|--------|----------|------|
| Global rules | `~/.claude/rules/*.md` | Cross-project patterns |
| Project rules | `<project>/.claude/rules/*.md` | Project-specific |
| Hooks | `~/.claude/settings.json` | Requires confirmation |
| Memory | `<project>/memory/MEMORY.md` | User preferences |

---

## Comparison

| Feature | `/learner` | `/learn-history` |
|---------|-----------|------------------|
| **Scope** | Current session | All historical sessions |
| **Trigger** | Manual | Manual or auto |
| **Cross-project** | ❌ | ✅ (`--all`) |
| **Confirmation** | Auto-save | Require confirmation |
| **Output** | Single skill | Rules + Hooks + Memory |

---

## Example Session

```
用户: /learn-history --all

📊 正在分析所有项目...
   ├─ stockq: 456 条对话
   ├─ claude-config: 234 条对话
   ├─ other-project: 123 条对话
   └─ 共计: 813 条对话

📊 发现 58 个模式:
   ├─ 澄清请求: 23 次
   ├─ 纠正: 15 次
   ├─ 重复问题: 8 次
   └─ 偏好表达: 12 次

📋 建议采纳的改进 (共 4 项)

═══════════════════════════════════════════════════════
## [1/4] 规则: scope-clarification.md

**问题**: 用户澄清了 23 次，常见于"当前"、"改动"等词

**建议规则**:
在回答涉及"当前"、"改动"、"配置"等问题时，先确认范围：
- 本地还是服务器？
- 当前会话还是全局？
- 未提交还是已提交？

--- 预览 ---
# Scope Clarification Rule

## Trigger
- User asks about "当前"、"改动"、"现在的"

## Guideline
Before answering, clarify scope:
- Local changes or server config?
- Current session or global?
- Uncommitted or committed?

## Example
用户: 当前的配置是什么？
AI: 你指的是本地未提交的改动，还是服务器上的配置？
--- 预览结束 --@

是否采纳？ (y/n/preview/skip-all): y

✅ 已保存到 ~/.claude/rules/scope-clarification.md

═══════════════════════════════════════════════════════
## [2/4] Hook: pre-commit-test

...

是否采纳？ (y/n/preview/skip-all): n

⏭️ 跳过

═══════════════════════════════════════════════════════
📊 学习完成!
   ├─ 采纳: 1 规则, 0 Hook
   ├─ 跳过: 3 项
   └─ 感谢反馈，将持续学习
```
