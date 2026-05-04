---
name: refactor
version: 1.0.0
description: Execute architecture-level refactoring with safe, incremental steps. Use when restructuring modules, splitting large classes, or reorganizing directory structure.
user-invocable: true
argument-hint: "<file-or-directory> [--plan | --execute]"
triggers:
  - "架构重构"
  - "重构架构"
  - "refactor architecture"
  - "重构目录"
  - "拆分模块"
  - "reorganize code"
last_updated: 2026-05-04
---

# Architecture Refactoring Playbook

> 给复杂重构提供可执行的操作手册

---

## 核心原则（必须遵守）

```
1. 小步前进 — 每步都能测试
2. 保持可运行 — 永不留 broken 状态
3. 先创建后删除 — 新模块就绪再删旧代码
4. 验证每一步 — 测试通过再继续
5. 有回滚点 — 关键步骤提交
```

---

## 执行前检查

### 必要条件

| 条件 | 检查方法 | 不满足时 |
|------|----------|----------|
| **有测试** | `pytest --collect-only` | 先补测试 |
| **测试通过** | `pytest` | 先修复 |
| **Git 干净** | `git status` | 先提交当前改动 |
| **有分支** | `git branch` | 创建 feature 分支 |

```bash
# 快速检查
pytest && git status
```

---

## 标准流程四阶段

### Phase 1: 分析与设计

```
输入：目标文件/目录

Step 1: 识别职责
- 列出所有公开方法
- 按功能分组
- 标记依赖关系

Step 2: 设计新结构
- 确定目录划分
- 定义模块边界
- 绘制依赖图

Step 3: 输出方案
- 旧结构 → 新结构
- 迁移顺序（依赖低的先迁移）
- 预估步骤数
```

**输出示例**：

```markdown
## 重构方案：UserManager (2100行)

### 职责分析
| 职责 | 方法数 | 依赖 |
|------|--------|------|
| 认证 | 8 | 无 |
| 用户资料 | 12 | 认证 |
| 权限 | 6 | 认证 |

### 迁移顺序
1. 认证（无依赖，先迁移）
2. 权限（依赖认证）
3. 用户资料（依赖认证+权限）

### 目标结构
src/
├── auth/
│   └── manager.py
├── permission/
│   └── manager.py
└── profile/
    └── manager.py
```

---

### Phase 2: 逐步迁移

```
核心思想：逐个职责迁移，每步可验证
```

#### 标准迁移模板

```python
# === 迁移一个方法的完整循环 ===

# Step 1: 创建目标文件（空壳）
# src/auth/manager.py
class AuthManager:
    """认证管理器"""

    def __init__(self, db):
        self.db = db

# Step 2: 复制方法（不改逻辑）
# 从源文件复制，保持代码不变
class AuthManager:
    def login(self, username, password):
        # 原逻辑不变
        ...

# Step 3: 添加导入兼容层（渐进式）
# src/user_manager.py（旧文件）
from auth.manager import AuthManager

class UserManager:
    # 兼容层：转发调用
    def login(self, *args):
        return self._auth.login(*args)

# Step 4: 更新外部导入
# 找到所有使用 UserManager.login 的地方
# 更新为 AuthManager.login

# Step 5: 运行测试
pytest tests/

# Step 6: 提交检查点
git add . && git commit -m "refactor: migrate login to AuthManager"

# Step 7: 清理
# 删除 UserManager 中的 login 方法
# 删除兼容层（如果已全部迁移）
```

#### 批量迁移脚本

```bash
# 每迁移一个模块，执行一次
make refactor-migrate MODULE=auth

# 等价于：
# 1. pytest tests/
# 2. git commit -m "refactor: migrate auth module"
```

---

### Phase 3: 验证与修复

```
全量检查清单

□ pytest tests/          # 单元测试
□ pytest tests/e2e/     # 集成测试（如有）
□ mypy src/             # 类型检查（如有）
□ ruff check src/       # Lint（如有）
□ python -m src.main    # 启动测试
```

**失败处理**：

```python
# 测试失败时的诊断流程
1. 运行 pytest --tb=short
2. 检查导入路径是否正确
3. 检查是否有遗漏的方法
4. 检查依赖注入是否完整
```

---

### Phase 4: 收尾清理

```
完成迁移后的清理工作
```

```bash
# 1. 删除废弃文件（确认无引用）
# 先搜索引用
grep -r "UserManager" src/
# 确认无引用后再删除
rm src/user_manager.py

# 2. 更新文档
# README.md
# CHANGELOG.md

# 3. 最终提交
git add .
git commit -m "refactor: complete UserManager split into auth/profile/permission"
```

---

## 安全检查点

### 🛑 必须停止

| 触发条件 | 动作 |
|----------|------|
| 测试失败 | 立即修复，不继续 |
| 导入错误 | 检查路径，修复后继续 |
| 循环导入 | 重新设计依赖关系 |
| 类型错误 | 修复后再继续 |

### ⚠️ 需要确认

| 触发条件 | 确认内容 |
|----------|----------|
| 删除文件 | "确认删除 user_manager.py？[y/N]" |
| 重命名 | "确认重命名？可能影响外部代码" |
| 改接口 | "接口变更，确认向后兼容？" |

---

## 目录组织最佳实践

### 推荐结构

```
src/
├── auth/               # 按领域分目录
│   ├── __init__.py
│   ├── manager.py      # 核心类
│   ├── tokens.py       # 子模块
│   └── models.py       # 数据模型
├── profile/
├── permission/
└── shared/             # 真正共享的代码
    ├── exceptions.py
    └── types.py
```

### 禁止的反模式

```
❌ utils/       → 变成垃圾桶
❌ helpers/     → 职责不清
❌ common/      → 太泛
❌ core/        → 什么都往里放

✅ 如果不确定 → 按 domain/feature 组织
```

---

## 常见重构模式

### 1. Extract Class

```
Before:
class User:
    def login()
    def update_profile()
    def check_permission()

After:
class User:
    def login()          # → AuthManager
    def update_profile() # → ProfileManager
    def check_permission() # → PermissionManager
```

### 2. Extract Module

```
Before:
src/
└── big_module.py (1500行)

After:
src/
└── big_module/
    ├── __init__.py
    ├── core.py
    ├── helpers.py
    └── types.py
```

### 3. Fix Circular Dependency

```
Before: A → B → C → A

After:  A → B
        A → C
        (引入中间层 D)
```

---

## 执行模式

### 默认：交互模式

```bash
/refactor src/user_manager.py

# 输出方案，等待确认
# 逐步执行，每步检查
```

### 自动模式（跳过确认）

```bash
/refactor src/user_manager.py --execute

# 自动执行，失败会停止
```

### 仅规划

```bash
/refactor src/user_manager.py --plan

# 只输出方案，不执行
# 适合 review 方案
```

---

## 回滚策略

```bash
# 每个阶段结束时打 tag
git tag refactor-auth-phase1
git tag refactor-auth-phase2
...

# 出问题回滚
git reset --hard refactor-auth-phase1
```

---

## 示例：完整重构流程

```bash
# 用户执行
/refactor src/user_manager.py

# Claude 输出
分析中...

## 重构方案

### 现状
- 文件：src/user_manager.py (2100行)
- 职责：认证、资料、权限

### 目标结构
src/
├── auth/manager.py (200行)
├── profile/manager.py (300行)
└── permission/manager.py (150行)

### 迁移步骤 (预估 15 步)
1. 创建目录结构
2. 迁移认证模块 (5步)
3. 迁移权限模块 (4步)
4. 迁移资料模块 (4步)
5. 清理与验证 (2步)

是否开始执行？[Y/n]

# 用户确认后
开始执行 Phase 1: 创建目录...

✓ mkdir -p src/auth src/profile src/permission
✓ 创建空壳文件

Step 1/15 完成 ✓

开始 Phase 2: 迁移认证模块...

Step 2: 创建 AuthManager.login...
✓ 复制方法到 src/auth/manager.py
✓ pytest tests/auth/ ... 通过

是否继续下一步？[Y/n]
...
```

---

## AST 精确重构（Python Only）

### 优势对比

| 场景 | 文本级重构 | AST 精确重构 |
|------|------------|--------------|
| 重命名变量 | ❌ 误改字符串/注释 | ✅ 精确匹配语法节点 |
| 重命名函数 | ⚠️ 可能漏改调用点 | ✅ 同步更新所有引用 |
| 重命名类 | ⚠️ import 可能漏改 | ✅ 完整更新 |

### 使用方式

```bash
# 重命名变量（精确，不误改字符串）
python ${CLAUDE_SKILL_DIR}/scripts/ast_refactor.py rename-variable old_name new_name src/*.py

# 重命名函数（同步更新定义和调用）
python ${CLAUDE_SKILL_DIR}/scripts/ast_refactor.py rename-function old_func new_func src/*.py

# 重命名类（同步更新定义、继承、实例化）
python ${CLAUDE_SKILL_DIR}/scripts/ast_refactor.py rename-class OldClass NewClass src/*.py

# 应用变更（默认 dry-run 模式）
python ${CLAUDE_SKILL_DIR}/scripts/ast_refactor.py rename-variable user_id uid src/*.py --apply
```

### 示例：重命名变量

```python
# 原代码
def process(user_id):
    print(f"User ID: {user_id}")
    msg = "Please provide user_id parameter"  # 字符串中的 user_id
    user_ids = [1, 2, 3]  # 复数形式
    return fetch(user_id)

# 执行：rename-variable user_id uid

# 结果（精确匹配）
def process(uid):
    print(f"User ID: {uid}")           # ✅ 改
    msg = "Please provide user_id parameter"  # ❌ 不改（字符串）
    user_ids = [1, 2, 3]               # ❌ 不改（复数形式）
    return fetch(uid)                   # ✅ 改
```

### 限制

- **仅支持 Python**（基于 `ast` 模块）
- **可能丢失注释**（`ast.unparse()` 的已知限制）
- **格式可能变化**（缩进、空行）

---

## 与其他工具协作

| 工具 | 用途 |
|------|------|
| **`/simplify`** | 细粒度代码清理（内置） |
| **`/deep-review`** | 重构后质量审查 |
| **`planner` agent** | 复杂场景的方案设计 |
| **`architect` agent** | 架构评估 |
| **`/refactor`** | 执行架构级重构（本 skill） |
| **`scripts/ast_refactor.py`** | AST 精确重构（Python only） |

---

## 输出契约

每个阶段必须输出：

1. **当前进度**：`Step X/Y`
2. **已做操作**：具体改动
3. **验证结果**：测试状态
4. **下一步预览**：即将做什么
5. **回滚点**：给用户选择

---

**记住**：重构是整理代码，不是重写代码。小步前进，每步可证。
