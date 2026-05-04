---
version: 1.0.0
name: test-case-generator
description: Generate comprehensive test cases for your code. Use this skill when writing tests, designing test coverage, creating test data, or identifying edge cases. Triggers when user mentions "test case", "测试用例", "boundary", "边界条件", "test coverage", "测试覆盖", or explicitly requests help generating test inputs and scenarios.
user-invocable: true
argument-hint: "<文件或函数> [--coverage]"
triggers:
  - "test case"
  - "测试用例"
  - "边界条件"
  - "test coverage"
  - "测试覆盖"
last_updated: 2026-05-04
---

# Test Case Generator

Systematic test case generation for comprehensive code coverage.

## When to Activate

- Writing or reviewing test code
- Designing test coverage strategy
- Generating test input data
- Identifying edge cases and boundary conditions
- Creating test scenarios for APIs or functions

## Claude Native Capabilities

### What Claude Can Do Well

| Capability | Description |
|------------|-------------|
| Basic test generation | Generate standard unit tests |
| Boundary identification | Identify common edge cases |
| Logic coverage | Cover main code paths |
| Exception testing | Test error handling paths |
| Mock suggestions | Recommend mock strategies |

### Where Claude Needs Guidance

| Limitation | Mitigation |
|------------|------------|
| Domain-specific rules | User provides business rules |
| Performance testing data | Requires specialized tools |
| Fuzz testing synthesis | Manual intervention needed |
| Integration complexity | Start simpler, iterate |

---

## Test Case Generation Framework

### Step 1: Analyze the Function Under Test

Before generating test cases, analyze:

```markdown
## Function Analysis

**Function Name**: [name]
**Purpose**: [what it does]
**Parameters**:
  - param1: [type, constraints]
  - param2: [type, constraints]
**Return Value**: [type, meaning]
**Exceptions**: [what errors can occur]
**Side Effects**: [state changes, I/O]
**Dependencies**: [external services, databases]
```

### Step 2: Identify Test Categories

For each function, generate test cases across these categories:

#### Category 1: Happy Path Tests

```python
# Example: Normal operation
def test_username_validation_success():
    """Valid usernames should pass validation."""
    assert validate_username("john_doe") is True
    assert validate_username("alice123") is True
    assert validate_username("bob") is True  # minimum length
```

**Generate happy path tests first** - these verify core functionality.

#### Category 2: Boundary Value Tests

```python
# Example: Boundary testing
def test_username_length_boundaries():
    """Test username length at and around boundaries."""
    # At boundary
    assert validate_username("abc") is True    # min = 3
    assert validate_username("a" * 50) is True # max = 50

    # Just below
    assert validate_username("ab") is False    # 2 chars

    # Just above
    assert validate_username("a" * 51) is False # 51 chars
```

**Boundary Value Analysis Template**:

| Type | Test Value | Expected |
|------|-----------|----------|
| Minimum valid | min_value | Pass |
| Minimum - 1 | min_value - 1 | Fail |
| Minimum + 1 | min_value + 1 | Pass |
| Maximum valid | max_value | Pass |
| Maximum + 1 | max_value + 1 | Fail |
| Maximum - 1 | max_value - 1 | Pass |

#### Category 3: Negative Tests

```python
# Example: Invalid inputs
def test_username_invalid_characters():
    """Usernames with invalid characters should fail."""
    assert validate_username("user@name") is False
    assert validate_username("user name") is False
    assert validate_username("") is False
    assert validate_username(None) is False
```

#### Category 4: Special Value Tests

```python
# Example: Special values
def test_special_values():
    """Test special input values."""
    assert validate_username("") is False      # empty string
    assert validate_username(None) is False     # None
    assert validate_username("  ") is False    # whitespace only
    assert validate_username("\t") is False    # control chars
```

**Special Values Checklist**:

| Type | Python | JavaScript/TS |
|------|--------|---------------|
| Empty | `""`, `[]`, `{}` | `""`, `[]`, `{}` |
| Null | `None` | `null`, `undefined` |
| Zero | `0`, `0.0` | `0`, `0.0` |
| Negative | `-1`, `-0.1` | `-1`, `-0.1` |
| Large | `float('inf')` | `Infinity` |
| NaN | `float('nan')` | `NaN` |

#### Category 5: Exception Tests

```python
# Example: Exception testing
import pytest

def test_divide_by_zero_raises():
    """Division by zero should raise exception."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_parse_invalid_json():
    """Invalid JSON should raise JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        parse_json("{invalid}")
```

---

## Test Case Templates by Type

### API Endpoint Tests

```python
import pytest
from fastapi.testclient import TestClient

class TestUserAPI:
    """Test cases for User API endpoints."""

    def test_create_user_success(self, client: TestClient):
        """Create user with valid data."""
        response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        assert response.status_code == 201
        assert response.json()["username"] == "testuser"

    def test_create_user_missing_field(self, client: TestClient):
        """Create user without required field."""
        response = client.post("/users", json={
            "username": "testuser"
            # missing email
        })
        assert response.status_code == 422

    def test_create_user_duplicate(self, client: TestClient):
        """Create duplicate user should fail."""
        # First create
        client.post("/users", json={"username": "dup", "email": "dup@test.com"})
        # Duplicate attempt
        response = client.post("/users", json={
            "username": "dup",
            "email": "dup@test.com"
        })
        assert response.status_code == 409

    @pytest.mark.parametrize("invalid_email", [
        "invalid",
        "@no-local",
        "no-domain@",
        "spaces in@email.com",
    ])
    def test_create_user_invalid_email(self, client: TestClient, invalid_email):
        """Create user with invalid email format."""
        response = client.post("/users", json={
            "username": "test",
            "email": invalid_email
        })
        assert response.status_code == 422
```

### Database Operation Tests

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestDatabase:
    """Test cases for database operations."""

    @pytest.fixture
    def session(self):
        """Create isolated test database session."""
        engine = create_engine("sqlite:///:memory:")
        Session = sessionmaker(engine)
        session = Session()
        yield session
        session.rollback()
        session.close()

    def test_insert_user_success(self, session):
        """Insert valid user record."""
        user = User(username="test", email="test@test.com")
        session.add(user)
        session.commit()
        assert user.id is not None

    def test_insert_duplicate_username(self, session):
        """Insert duplicate username should fail."""
        user1 = User(username="test", email="test1@test.com")
        session.add(user1)
        session.commit()

        user2 = User(username="test", email="test2@test.com")
        session.add(user2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_cascade_delete(self, session):
        """Deleting user should cascade to related records."""
        user = User(username="test", email="test@test.com")
        user.posts = [Post(title="p1"), Post(title="p2")]
        session.add(user)
        session.commit()

        session.delete(user)
        session.commit()

        assert session.query(Post).count() == 0
```

### Business Logic Tests

```python
class TestPriceCalculator:
    """Test cases for price calculation logic."""

    @pytest.fixture
    def calculator(self):
        return PriceCalculator()

    # Happy path
    def test_calculate_basic_price(self, calculator):
        """Basic price calculation."""
        price = calculator.calculate(base_price=100, quantity=5)
        assert price == 500

    # Boundary tests
    def test_calculate_zero_quantity(self, calculator):
        """Zero quantity should return zero."""
        price = calculator.calculate(base_price=100, quantity=0)
        assert price == 0

    def test_calculate_negative_quantity(self, calculator):
        """Negative quantity should raise error."""
        with pytest.raises(ValueError):
            calculator.calculate(base_price=100, quantity=-1)

    # Discount tests
    @pytest.mark.parametrize("quantity,discount", [
        (10, 0.95),    # 5% discount
        (50, 0.90),    # 10% discount
        (100, 0.85),   # 15% discount
    ])
    def test_calculate_bulk_discount(self, calculator, quantity, discount):
        """Bulk orders should get appropriate discount."""
        price = calculator.calculate(base_price=100, quantity=quantity)
        assert price == 100 * quantity * discount

    # Edge cases
    def test_calculate_quantity_at_discount_boundary(self, calculator):
        """Test at exact discount threshold."""
        # 9 items: no discount
        assert calculator.calculate(100, 9) == 900
        # 10 items: 5% discount
        assert calculator.calculate(100, 10) == 950
```

---

## Test Input Generation Strategies

### Strategy 1: Equivalence Partitioning

Divide input domain into equivalence classes:

```python
# Input domain: age (0-120)
# Partitions:
#   - Invalid: age < 0
#   - Valid child: 0 <= age < 18
#   - Valid adult: 18 <= age < 65
#   - Valid senior: 65 <= age <= 120
#   - Invalid: age > 120

@pytest.mark.parametrize("age,expected", [
    (-1, "invalid"),     # invalid partition 1
    (0, "child"),        # boundary + valid child
    (10, "child"),       # valid child
    (17, "child"),       # boundary - valid child
    (18, "adult"),       # boundary + valid adult
    (30, "adult"),       # valid adult
    (64, "adult"),       # boundary - valid adult
    (65, "senior"),      # boundary + valid senior
    (100, "senior"),     # valid senior
    (120, "senior"),     # boundary - valid senior
    (121, "invalid"),    # invalid partition 2
])
def test_age_classification(age, expected):
    assert classify_age(age) == expected
```

### Strategy 2: Boundary Value Analysis

For numeric ranges `[a, b]`:
- `a - 1` (just below)
- `a` (minimum)
- `a + 1` (just above minimum)
- `(a + b) / 2` (nominal)
- `b - 1` (just below maximum)
- `b` (maximum)
- `b + 1` (just above)

### Strategy 3: Decision Table Testing

```python
# Decision table for login validation
# Conditions:
#   - Username provided
#   - Password provided
#   - Username exists
#   - Password matches

@pytest.mark.parametrize("username,password,exists,matches,expected", [
    # Rule 1: All conditions met
    ("user", "pass", True, True, "success"),
    # Rule 2: Wrong password
    ("user", "wrong", True, False, "invalid_credentials"),
    # Rule 3: User not found
    ("nobody", "pass", False, False, "user_not_found"),
    # Rule 4: Empty username
    ("", "pass", False, False, "username_required"),
    # Rule 5: Empty password
    ("user", "", True, False, "password_required"),
])
def test_login_decision_table(username, password, exists, matches, expected):
    # Setup mock based on exists/matches
    ...
    assert login(username, password) == expected
```

### Strategy 4: State Transition Testing

```python
class TestOrderStateMachine:
    """Test order state transitions."""

    def test_valid_transitions(self):
        """Test all valid state transitions."""
        order = Order(status="pending")

        # pending -> confirmed
        order.confirm()
        assert order.status == "confirmed"

        # confirmed -> shipped
        order.ship()
        assert order.status == "shipped"

        # shipped -> delivered
        order.deliver()
        assert order.status == "delivered"

    def test_invalid_transition(self):
        """Test invalid state transition."""
        order = Order(status="pending")

        # Cannot ship pending order
        with pytest.raises(InvalidStateTransition):
            order.ship()

    def test_cancellation_from_any_state(self):
        """Test cancellation from different states."""
        for status in ["pending", "confirmed"]:
            order = Order(status=status)
            order.cancel()
            assert order.status == "cancelled"
```

---

## Test Data Generation

### Simple Test Data Generators

```python
def generate_test_emails(valid=True):
    """Generate test email addresses."""
    if valid:
        return [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
        ]
    else:
        return [
            "",                     # empty
            "invalid",              # no @
            "@no-local.com",        # no local part
            "user@",                # no domain
            "user@.com",            # empty domain
            "user@example",         # no TLD
            "user name@example.com" # space in local
        ]
```

### Using Faker for Realistic Data

```python
from faker import Faker

fake = Faker()

class TestUserRegistration:
    """Test with realistic random data."""

    @pytest.fixture
    def user_data(self):
        return {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(length=12),
            "age": fake.random_int(min=18, max=80),
        }

    def test_register_random_user(self, user_data):
        """Test registration with realistic random data."""
        response = register_user(user_data)
        assert response.success
```

---

## Checklist for Comprehensive Coverage

### Per-Function Checklist

```markdown
## Test Coverage Checklist

### Happy Path
- [ ] Normal input produces expected output
- [ ] Return value type and structure
- [ ] Side effects (if any)

### Boundaries
- [ ] Minimum valid input
- [ ] Maximum valid input
- [ ] Just below minimum (invalid)
- [ ] Just above maximum (invalid)

### Special Values
- [ ] Empty input ( "", [], {} )
- [ ] None/null
- [ ] Zero (0, 0.0)
- [ ] Negative values
- [ ] Very large values

### Error Handling
- [ ] Invalid input type
- [ ] Missing required parameters
- [ ] Invalid format
- [ ] Resource not found
- [ ] Permission denied
- [ ] Rate limiting

### Edge Cases
- [ ] Unicode characters
- [ ] Long strings (>1000 chars)
- [ ] Concurrent access (if applicable)
- [ ] Timeout scenarios
```

---

## Best Practices

### DO

1. **Name tests descriptively**: `test_username_empty_raises_validation_error`
2. **One assertion per test**: Each test validates one behavior
3. **Use Arrange-Act-Assert pattern**: Clear structure
4. **Generate tests for all boundaries**: Min, max, min±1, max±1
5. **Test error paths**: Not just happy paths
6. **Use parametrization**: Reduce duplication
7. **Include fixture data**: Isolated, reproducible

### DON'T

1. **Don't test implementation details**: Test behavior, not internals
2. **Don't share state between tests**: Each test is independent
3. **Don't skip failure cases**: Errors need tests too
4. **Don't use magic numbers**: Named constants instead
5. **Don't ignore flaky tests**: Fix immediately

---

## Quick Reference

```bash
# Common test commands
pytest -v                    # Verbose output
pytest -k "test_username"    # Run specific tests
pytest --cov=src             # Coverage report
pytest -x                    # Stop on first failure
pytest --lf                  # Run last failed tests
pytest -m "slow"             # Run tests with marker
```

---

**Remember**: Good tests are your safety net. Generate comprehensive test cases systematically to catch bugs before production.
