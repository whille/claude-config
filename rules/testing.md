# Testing Guidelines

> 测试规范与覆盖率要求

---

## 测试覆盖率标准

| 指标 | 要求 | 说明 |
|------|------|------|
| **全局覆盖率** | ≥ 80% | 核心代码必须达标 |
| **新增代码覆盖率** | 100% | 新功能必须有测试 |
| **核心模块覆盖率** | ≥ 90% | 业务逻辑、API 端点 |
| **工具函数覆盖率** | ≥ 70% | 可适当放宽 |

---

## 测试分层

```
tests/
├── unit/           # 单元测试（快）
├── integration/    # 集成测试（中）
└── e2e/            # 端到端测试（慢）
```

| 类型 | 速度 | 隔离性 | 数量占比 |
|------|------|--------|----------|
| 单元测试 | 毫秒级 | 完全隔离 | 70% |
| 集成测试 | 秒级 | 部分隔离 | 20% |
| E2E 测试 | 分钟级 | 无隔离 | 10% |

---

## 测试命名规范

### 文件命名

```
tests/
├── test_{module}.py        # 单元测试
├── test_{module}_integration.py  # 集成测试
└── test_{feature}_e2e.py   # E2E 测试
```

### 函数命名

```python
# ❌ 错误：命名不清
def test_function():
    assert add(1, 2) == 3

# ✅ 正确：描述行为
def test_add_two_positive_numbers():
    assert add(1, 2) == 3

def test_add_negative_number_raises_error():
    with pytest.raises(ValueError):
        add(-1, 2)

def test_add_zero_returns_same():
    assert add(0, 5) == 5
```

### 模板：`test_{method}_{condition}_{expected}`

```python
def test_login_valid_credentials_returns_token():
    ...

def test_login_invalid_password_raises_auth_error():
    ...

def test_login_empty_username_returns_400():
    ...
```

---

## 测试结构：AAA 模式

```python
def test_user_creation():
    # Arrange（准备）
    user_data = {"name": "张三", "email": "test@example.com"}

    # Act（执行）
    user = create_user(user_data)

    # Assert（断言）
    assert user.id is not None
    assert user.name == "张三"
    assert user.email == "test@example.com"
```

---

## pytest 最佳实践

### pytest.fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def db_session():
    """每个测试独立的数据库会话"""
    session = create_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user():
    """示例用户数据"""
    return {"name": "测试用户", "email": "test@example.com"}
```

### pytest.parametrize

```python
# ❌ 错误：重复代码
def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, -2) == -3

def test_add_zero():
    assert add(0, 5) == 5

# ✅ 正确：参数化
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, -2, -3),
    (0, 5, 5),
    (1, -1, 0),  # 边界
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### pytest.raises

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email("not-an-email")
```

---

## Mock 使用

```python
from unittest.mock import patch, MagicMock

# Mock 外部 API
@patch("requests.get")
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {"id": 1, "name": "Test"}

    result = fetch_user(1)

    assert result["name"] == "Test"
    mock_get.assert_called_once_with("https://api.example.com/users/1")

# Mock 数据库
def test_save_user():
    mock_db = MagicMock()
    save_user(mock_db, {"name": "Test"})

    mock_db.insert.assert_called_once()
```

---

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/unit/test_user.py

# 运行特定测试
pytest tests/unit/test_user.py::test_login_valid

# 带覆盖率
pytest --cov=src --cov-report=term-missing

# 只运行失败的测试
pytest --lf

# 并行运行
pytest -n auto

# 输出 print
pytest -s
```

---

## 测试清单

### 提交前检查

- [ ] `pytest tests/` 通过
- [ ] 覆盖率 ≥ 80%
- [ ] 无跳过的测试（`@pytest.mark.skip`）
- [ ] 无待修复的测试（`@pytest.mark.xfail`）

### 代码审查检查

- [ ] 测试命名清晰（`test_xxx_yyy_zzz`）
- [ ] 测试覆盖边界条件
- [ ] 测试覆盖错误路径
- [ ] Mock 使用正确
- [ ] 无硬编码数据（用 fixtures）
- [ ] 无测试间依赖

---

## 边界条件测试

```python
@pytest.mark.parametrize("input,expected", [
    # 正常值
    ("normal@example.com", True),

    # 边界值
    ("", False),                    # 空字符串
    ("a@b.c", True),                # 最短合法
    ("a" * 100 + "@example.com", False),  # 过长

    # 异常值
    ("no-at-sign", False),
    ("@no-local.com", False),
    ("spaces in@local.com", False),
    (None, False),                  # None
])
def test_validate_email(input, expected):
    assert validate_email(input) == expected
```

---

## 与其他 Rules 协作

| Rule | 关联 | 说明 |
|------|------|------|
| `dev-guide.md` | TDD 流程 | 先写测试再实现 |
| `bug-prevention.md` | 失败测试 | Bug 修复需加测试 |
| `refactoring.md` | 测试保护 | 重构前必须有测试 |

---

## 工具推荐

| 工具 | 用途 |
|------|------|
| `pytest` | 测试框架 |
| `pytest-cov` | 覆盖率 |
| `pytest-xdist` | 并行测试 |
| `pytest-mock` | Mock 工具 |
| `hypothesis` | 属性测试 |
| `faker` | 测试数据生成 |

---

## CI/CD 集成

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=src --cov-fail-under=80 \
           --cov-report=xml --cov-report=term-missing
```

**强制覆盖率**：低于 80% CI 失败。

---

## 常见陷阱

| 陷阱 | 问题 | 解决 |
|------|------|------|
| **测试间依赖** | 改一个影响其他 | 用 fixtures 隔离 |
| **硬编码数据** | 难以维护 | 用工厂/faker |
| **测试实现细节** | 重构会断 | 测试行为而非实现 |
| **跳断言** | 假通过 | 用 `pytest.raises` |
| **测试慢** | 开发体验差 | Mock 外部依赖 |
