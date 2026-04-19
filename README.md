# Claude Code Configuration

> 个人 Claude Code 配置：Skills + Rules + Hooks

---

## 组件概览

| 组件 | 数量 | 说明 |
|------|------|------|
| **Skills** | 6 个 | 自定义工作流 |
| **Rules** | 7 个 | 开发规范 |
| **Hooks** | 5 个 | 自动化脚本 |

---

## Skills 自定义工作流

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `intel` | 信息源适配层（B站/GitHub/RSS），自动去重、评分、筛选 | `/intel 主题 [--deep]` |
| `deep-review` | 4维度并行代码审查（安全/质量/性能/架构） | `/deep-review [files]` |
| `refactor` | 架构级重构 Playbook，小步验证 | `/refactor <path> [--plan\|--execute]` |
| `log-analyzer` | 日志分析 & 根因定位 | `/log-analyzer <path>` |
| `bilibili-analyzer` | B站视频分析，提取关键信息 | `/bilibili-analyzer <url>` |
| `test-case-generator` | 测试用例生成，边界条件覆盖 | `/test-case-generator` |

### intel 信息源适配层

```bash
# 快速扫描
/intel 鱼菜共生

# 深度提取（字幕/代码分析）
/intel 鱼菜共生 --deep
```

### deep-review 四维度审查

```bash
# 审查当前变更
/deep-review

# 审查指定文件
/deep-review src/main.py

# 审查目录
/deep-review src/
```

输出：
```
| 维度 | 问题数 | 严重 | 高 | 中 | 低 |
|------|--------|------|----|----|----|
| 安全 | 2 | 1 | 1 | 0 | 0 |
| 质量 | 3 | 0 | 1 | 2 | 0 |
| 性能 | 1 | 0 | 0 | 1 | 0 |
| 架构 | 0 | 0 | 0 | 0 | 0 |
```

### refactor 架构重构

```bash
# 仅规划
/refactor src/user_manager.py --plan

# 交互执行（推荐）
/refactor src/user_manager.py

# 自动执行（跳过确认）
/refactor src/user_manager.py --execute
```

---

## Rules 开发规范

| Rule | 内容 |
|------|------|
| `bug-prevention.md` | Bug 预防（Falsy陷阱、日期切片、空字典默认） |
| `security.md` | 安全规范（硬编码密钥、SQL注入、XSS） |
| `testing.md` | 测试规范（覆盖率 ≥80%、pytest 最佳实践） |
| `refactoring.md` | 重构原则（Martin Fowler 核心原则） |
| `refactoring-suggestions.md` | 重构建议检测规则 |
| `dev-guide.md` | 开发规范精简版 |
| `deep-review-trigger.md` | Deep Review 自动触发规则 |

### 核心规范速查

```markdown
## 代码质量
- 函数 < 50 行
- 文件 < 800 行
- 嵌套 ≤ 4 层
- 测试覆盖率 ≥ 80%

## 提交前检查
- [ ] 无硬编码密钥
- [ ] 无 console.log/print
- [ ] 测试通过
- [ ] pytest --cov ≥ 80%

## 常见陷阱
- Falsy 陷阱：`if config:` → `if config is not None:`
- 日期切片：`arr[-N:]` → `filter(d >= cutoff)`
- 空字典默认：`func(x={})` → `func(x=None)`
```

---

## Hooks 自动化脚本

| Hook | 触发 | 功能 |
|------|------|------|
| `session-start.py` | 会话启动 | 加载上下文、检测包管理器 |
| `review-trigger.py` | Bash 前 | 安全扫描（硬编码密钥、SQL注入） |
| `post-edit-python-format.py` | Edit .py 后 | 自动 `ruff format` |
| `post-edit-python-lint.py` | Edit .py 后 | 自动 `ruff check --fix` |
| `stop-check-console-log.py` | 会话结束 | 检查遗留的调试语句 |

### 效果示例

```
会话启动：
============================================================
🚀 Session Context
============================================================
📦 Package Manager: uv
📝 Uncommitted changes: 3 files
============================================================

编辑 .py 文件后：
✓ Formatted: src/main.py
⚠️ Lint issues in src/main.py:
  F401 [*] `os` imported but unused

会话结束：
============================================================
🔍 发现调试语句（建议清理）
============================================================
  src/debug.py:15
    [console.log] console.log("debug info")
💡 提示: 使用 /simplify 清理
============================================================
```

---

## 安装

### 方式一：克隆 + 软链接（推荐）

```bash
# 克隆仓库
git clone https://github.com/你的用户名/claude-config.git
cd claude-config

# 链接 Skills
ln -s $(pwd)/skills/* ~/.claude/skills/

# 复制 Rules
cp -r rules/* ~/.claude/rules/

# 复制 Hooks
cp -r hooks/* ~/.claude/hooks/

# 合并 settings.json 的 hooks 配置到 ~/.claude/settings.json
```

### 方式二：手动复制

```bash
# 复制全部
cp -r skills/* ~/.claude/skills/
cp -r rules/* ~/.claude/rules/
cp -r hooks/* ~/.claude/hooks/

# 编辑 ~/.claude/settings.json，添加 hooks 配置
```

### settings.json Hooks 配置

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/session-start.py",
            "description": "加载项目上下文"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/review-trigger.py",
            "description": "安全扫描",
            "timeout": 30000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/post-edit-python-format.py \"$CLAUDE_FILE_PATH\"",
            "description": "Python 自动格式化",
            "timeout": 10000
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/post-edit-python-lint.py \"$CLAUDE_FILE_PATH\"",
            "description": "Python 自动 Lint",
            "timeout": 10000
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/stop-check-console-log.py",
            "description": "检查调试语句"
          }
        ]
      }
    ]
  }
}
```

---

## 依赖

### 必需

- Python 3.10+
- ruff（Python 格式化/Lint）
- pytest（测试）

### 可选

- bun/npm/pnpm（包管理器检测）
- git（版本控制）

```bash
# 安装依赖
pip install ruff pytest pytest-cov
```

---

## 与 OMC/ECC 的关系

本项目是**独立配置**，可与以下框架共存：

| 框架 | 关系 |
|------|------|
| **OMC (oh-my-claudecode)** | 共存，复用其 workflow skills |
| **ECC (everything-claude-code)** | 共存，补充其 rules/hooks |

### 本项目特色

- 垂直领域 Skills（信息收集、代码审查）
- 完整开发规范 Rules
- 实用自动化 Hooks

---

## 目录结构

```
claude-config/
├── skills/
│   ├── intel/SKILL.md
│   ├── deep-review/SKILL.md
│   ├── refactor/SKILL.md
│   ├── log-analyzer/SKILL.md
│   ├── bilibili-analyzer/SKILL.md
│   └── test-case-generator/SKILL.md
├── rules/
│   ├── bug-prevention.md
│   ├── security.md
│   ├── testing.md
│   ├── refactoring.md
│   ├── refactoring-suggestions.md
│   ├── dev-guide.md
│   └── deep-review-trigger.md
├── hooks/
│   ├── session-start.py
│   ├── review-trigger.py
│   ├── post-edit-python-format.py
│   ├── post-edit-python-lint.py
│   └── stop-check-console-log.py
├── settings.json              # Hooks 配置示例
└── README.md
```

---

## 许可证

MIT
