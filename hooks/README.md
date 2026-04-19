# Review Trigger Hook 示例配置

## 1. 手动使用

```bash
# 直接执行脚本
python ~/.claude/hooks/review-trigger.py
```

## 2. 配置为 PreToolUse Hook

在项目根目录的 `.claude/settings.json` 中添加：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "toolName": "Bash"
        },
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/review-trigger.py",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

## 3.Git Hook 集成（可选）

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# 执行 review trigger
python3 ~/.claude/hooks/review-trigger.py

# 如果发现问题，询问是否继续
read -p "发现潜在问题，是否继续提交？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi
```

然后执行：
```bash
chmod +x .git/hooks/pre-commit
```

---

## 测试

```bash
# 模拟代码变更
echo "password = 'hardcoded_secret'" > test_secret.py
git add test_secret.py

# 执行 hook
python ~/.claude/hooks/review-trigger.py
```

---

## 注意事项

1. Hook 仅提示，不阻断操作
2. 发现问题后建议执行 `/code-reviewer` 进行详细分析
3. 可根据项目调整 `HIGH_RISK_PATTERNS` 和 `SECURITY_PATTERNS`
