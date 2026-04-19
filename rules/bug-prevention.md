# Bug Prevention Rules

> 常见 Bug 根因与预防清单

---

## 日期/时间处理

### 问题：数组切片 vs 日期筛选

```python
# ❌ 错误：取数组最后 N 条，不是最近 N 天
trade_dates = trade_dates[-days:]

# ✅ 正确：按日期范围筛选
cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
trade_dates = [d for d in trade_dates if d >= cutoff_date]
```

### 检查清单

- [ ] 明确语义：是"数组位置"还是"日期范围"
- [ ] 打印验证：输出实际日期范围 `print(f"范围: {start} - {end}")`
- [ ] 边界测试：空数据、单日数据、跨年数据

---

## Falsy 陷阱

### 问题：空集合/字典是 falsy

```python
# ❌ 错误：空字典 {} 不会进入分支
config = {}
if config:
    render_config(config)  # 永远不执行

# ✅ 正确：使用 is not None
if config is not None:
    render_config(config)

# ✅ 正确：传入有意义的值
config = {"name": strategy_name}  # 非空字典
```

### Python Falsy 值大全

| 值 | bool() | 常见错误 |
|---|--------|----------|
| `None` | False | 正确 |
| `False` | False | 正确 |
| `0` | False | ⚠️ 数字零 |
| `0.0` | False | ⚠️ 浮点零 |
| `""` | False | ⚠️ 空字符串 |
| `[]` | False | ⚠️ 空列表 |
| `{}` | False | ⚠️ 空字典 |
| `set()` | False | ⚠️ 空集合 |

### 检查清单

- [ ] 使用 `if x is not None` 而非 `if x`
- [ ] 检查默认参数：`func(x={})` → `func(x=None)`
- [ ] 类型注解：`Optional[Dict]` 明确可选

---

## 重复代码检测

### 问题：新建文件而非复用

```python
# ❌ 错误：创建新文件，复制粘贴重写
new_file.py:
    def new_func():
        # 复制 old_func 的代码
        ...

# ✅ 正确：导入复用
from old_module import old_func

def new_func():
    old_func()  # 调用
```

### 检查清单

- [ ] 新增代码 < 原代码 10%
- [ ] 新增文件 ≤ 1
- [ ] 无相同逻辑的多份实现
- [ ] 能 import 就不复制

---

## 提交前验证

### 功能正确性

| 检查项 | 方法 |
|--------|------|
| 关键值打印 | `print(f"日期范围: {start} - {end}")` |
| 边界条件 | 空数据、极值、异常输入 |
| 端到端验证 | 运行完整流程 |

### 代码质量

| 检查项 | 方法 |
|--------|------|
| Falsy 陷阱 | 检查 if 语句中的空集合 |
| 命名语义 | 变量名表达意图 |
| 重复代码 | `git diff --stat` 检查规模 |

### 测试覆盖

```bash
# 核心逻辑有测试
pytest tests/ -v

# 检查测试覆盖率
pytest --cov=src --cov-report=term-missing
```

---

## 典型 Bug 案例

### 案例 1: 日期范围错误

**现象**: 预期最近1年，实际覆盖18个月

**根因**: `array[-N:]` 取数组位置，不是日期范围

**修复**:
```python
cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
trade_dates = [d for d in trade_dates if d >= cutoff_date]
print(f"回测区间: {trade_dates[0]} - {trade_dates[-1]}")
```

### 案例 2: 配置丢失

**现象**: YAML 配置不渲染

**根因**: `config = {}` 空字典是 falsy，`if config:` 不进入

**修复**:
```python
config = {"name": strategy_name}  # 非空字典
# 或模板中用：if config is not None
```

### 案例 3: 重复代码

**现象**: 创建 `topn_strategy.py`（487行），与 `signal_strategy.py` 重复

**根因**: 倾向于"新建"而非"复用"

**修复**: 删除重复文件，扩展现有入口

---

## 预防 Checklist

```markdown
## 提交前检查

### 功能验证
- [ ] 打印关键日期范围
- [ ] 测试边界条件（空值、极值）
- [ ] 运行完整流程验证

### 代码质量
- [ ] 无 falsy 陷阱（检查 if config:）
- [ ] 变量命名语义明确
- [ ] 无重复代码

### 测试
- [ ] pytest tests/ 通过
- [ ] 核心逻辑有覆盖

### 规模控制
- [ ] 新增代码 < 10%
- [ ] 新增文件 ≤ 1
```
