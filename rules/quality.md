# Quality Rules

> 测试与质量规范

---

## 用户偏好

- **核心逻辑必测**：关键功能必须有测试覆盖
- **追求全覆盖**：目标 80%+ 覆盖率
- **遵循项目现有**：用项目已有的测试框架

---

## 测试覆盖率标准

| 指标 | 要求 |
|------|------|
| 全局覆盖率 | ≥ 80% |
| 新增代码覆盖率 | 100% |
| 核心模块覆盖率 | ≥ 90% |

---

## 测试命名

```python
# 模板：test_{method}_{condition}_{expected}
def test_login_valid_credentials_returns_token():
    ...

def test_login_invalid_password_raises_error():
    ...
```

---

## AAA 模式

```python
def test_user_creation():
    # Arrange（准备）
    user_data = {"name": "张三"}

    # Act（执行）
    user = create_user(user_data)

    # Assert（断言）
    assert user.id is not None
```

---

## pytest 要点

```python
# 参数化
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, -2, -3),
])
def test_add(a, b, expected):
    assert add(a, b) == expected

# 异常测试
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

# Mock
@patch("requests.get")
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {"id": 1}
    result = fetch_user(1)
    assert result["id"] == 1
```

---

## 运行测试

```bash
pytest --cov=src --cov-report=term-missing  # 带覆盖率
pytest --lf                                  # 只运行失败
pytest -n auto                               # 并行
```

---

## 测试清单

提交前：
- [ ] `pytest tests/` 通过
- [ ] 覆盖率 ≥ 80%
- [ ] 无跳过的测试

---

## 边界条件必测

- 空值、None
- 极值（最大、最小）
- 异常格式

---

## 重构红线

| 红线 | 触发条件 | 行动 |
|------|----------|------|
| 行为变更 | 输入输出改变 | 立即停止 |
| 代码膨胀 | 新增 > 10% | 方向错误 |
| 批量改动 | > 1 个文件 | 步子太大 |

---

## 精准修改

**只改必须改的。只清理自己的烂摊子。**

- 不"改进"相邻代码、注释、格式
- 不重构没坏的东西
- 匹配现有风格
- 发现无关死代码 → 提及，不删除

**检验标准**：每行改动都能追溯到用户请求。

---

## 坏味道检测

| 坏味道 | 解决方案 |
|--------|----------|
| 重复代码 | 提取共用函数 |
| 过长函数 | 拆分子函数 |
| 过大类 | 拆分职责 |

---

## 重构前检查

- [ ] 有测试吗？没测试 = 不能重构
- [ ] 行为明确吗？不清楚 = 停止
- [ ] 能 import 吗？能 = 不要复制

---

## 代码异味判断

```
需要复制粘贴？→ 错了，应该 import
新增文件 > 1？→ 步子太大
原有代码"不好"想重写？→ 先复用，后续优化
```
