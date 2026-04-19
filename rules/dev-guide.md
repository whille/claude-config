# Dev Guide

> 开发规范精简版

---

## 代码质量标准

| 指标 | 限制 |
|------|------|
| 函数长度 | < 50 行 |
| 文件长度 | < 800 行 |
| 嵌套层级 | ≤ 4 层 |
| 测试覆盖率 | ≥ 80% |

---

## 核心原则

### 不可变性

创建新对象，不修改现有对象：
- 防止隐藏副作用
- 简化调试
- 支持安全并发

### 错误处理

- 每层显式处理
- UI 层用户友好
- 服务端记录上下文
- 绝不静默吞掉错误

### 输入验证

- 系统边界验证
- Schema-based 校验
- 快速失败
- 不信任外部数据

---

## 工作流

1. **研究先行**：GitHub → 官方文档 → Exa
2. **规划**：复杂功能用 planner agent
3. **TDD**：先写测试 → 实现 → 重构
4. **审查**：写完代码立即 code-reviewer agent
5. **提交**：Conventional Commits 格式

---

## Git 规范

```
<type>: <description>

Types: feat | fix | refactor | docs | test | chore | perf
```

---

## Python 规范

| 工具 | 用途 |
|------|------|
| black | 格式化 |
| ruff | Linting |
| pytest | 测试 |
| mypy | 类型检查 |
| bandit | 安全扫描 |

```bash
# 运行测试与覆盖率
pytest --cov=src --cov-report=term-missing

# 安全扫描
bandit -r src/
```

---

## Agent 使用

| 场景 | Agent |
|------|-------|
| 复杂功能规划 | planner |
| 写完代码后 | code-reviewer |
| Bug 修复/新功能 | tdd-guide |
| 架构决策 | architect |
| 安全敏感代码 | security-reviewer |

**并行执行**独立任务。

---

## 安全审查触发点

以下场景**立即**使用 security-reviewer：

- 认证/授权代码
- 用户输入处理
- 数据库查询
- 文件系统操作
- 外部 API 调用
- 加密/支付代码

**常见问题**：硬编码凭证、SQL 注入、XSS、路径遍历

---

## 代码审查清单

- [ ] 命名清晰
- [ ] 函数 <50 行
- [ ] 文件 <800 行
- [ ] 嵌套 ≤4 层
- [ ] 错误显式处理
- [ ] 无硬编码秘密
- [ ] 无 console.log/print
- [ ] 有测试覆盖
- [ ] **无 Falsy 陷阱**（空集合检查）
- [ ] **日期范围验证**（打印实际范围）

---

## Bug 预防

> 详见 [bug-prevention.md](./bug-prevention.md)

### 常见陷阱

| 陷阱 | 错误示例 | 正确做法 |
|------|----------|----------|
| Falsy 陷阱 | `if config:` | `if config is not None:` |
| 日期切片 | `arr[-N:]` | `filter(d >= cutoff)` |
| 空字典默认 | `func(x={})` | `func(x=None)` |

### 提交前必打印

```python
print(f"日期范围: {start} - {end}")  # 验证实际范围
print(f"数据量: {len(data)} 条")     # 验证数据量
```

---

## 重构规范

> 详见 [refactoring.md](./refactoring.md)

### 核心原则

**重构是整理代码，不是重写代码。**

```
错误：创建新文件 → 复制粘贴 → 修改
正确：分析原有代码 → import 复用 → 只写入口
```

### 红线

| 问题 | 阈值 | 说明 |
|------|------|------|
| 代码量增加 | > 10% | 方向错误 |
| 新增文件 | > 1 | 步子太大 |
| 重复函数 | 多文件存在 | 应该 import |

### 增量修改

1. 每次只改一个文件
2. 改完立即测试
3. 新增代码 < 原代码 10%