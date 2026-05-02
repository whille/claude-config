# Call Chain Tracing Rules

## 追踪调用链的正确方法

### 核心原则

**从目标函数向上追踪，而不是从关键字猜测。**

---

## 场景对照表

| 场景 | 错误做法 | 正确做法 |
|------|----------|----------|
| 找"谁生成了这个文件" | grep `vnode.*csv` | LSP `incomingCalls` 从写入函数向上追踪 |
| 找"谁调用了这个函数" | grep `func_name(` | LSP `incomingCalls` |
| 找"这个函数调用了谁" | grep 搜内部调用 | LSP `outgoingCalls` |
| 找函数定义 | grep `def func` | LSP `goToDefinition` |
| 找所有引用 | grep 变量名 | LSP `findReferences` |

---

## 标准流程

### 找"谁生成了某文件"

```
1. grep 找写入函数：to_csv|open\(.*w|write\(
2. 定位具体函数（如 write_day_node）
3. LSP incomingCalls 向上追踪：
   write_day_node
     ← prepare_csv
       ← read_next_month_data_main
         ← next_month_main
           ← __main__
4. 输出完整调用栈
```

### 找"谁调用了某函数"

```
LSP incomingCalls 从目标函数开始
递归追踪直到入口点
```

### 找"某函数调用了谁"

```
LSP outgoingCalls 从目标函数开始
```

---

## 禁止的做法

| 禁止 | 原因 |
|------|------|
| grep 搜关键字 → 猜测调用链 | 会命中无关函数（如读取函数），误导分析 |
| 看到"读取"函数就以为是入口 | 读取和写入函数名可能相似，需要区分 |
| 只看一层调用就下结论 | 调用链可能有多层，需要完整追踪 |

---

## LSP 工具速查

| LSP 操作 | 用途 | 示例 |
|----------|------|------|
| `incomingCalls` | 找调用者（向上） | 谁调用了 `write_day_node` |
| `outgoingCalls` | 找被调用者（向下） | `write_day_node` 调用了谁 |
| `goToDefinition` | 跳转定义 | 跳到函数定义处 |
| `findReferences` | 找所有引用 | 找某变量的所有使用位置 |
| `hover` | 查看类型/文档 | 查看函数签名和类型 |

---

## 案例：生成 vnode CSV 的调用栈

### 错误分析过程

```
grep "vnode.*csv"
  → 命中 read_xihe_data.get_nodes_base_info（读取函数）
  → 错误结论：cluster_alg_with_improve_bw.py 只读取 vnode CSV
```

### 正确分析过程

```
1. 找写入函数：
   grep "vnode.*to_csv|write.*vnode" → write_day_node

2. LSP incomingCalls 追踪：
   write_day_node (read_data.py:324)
     ← prepare_csv (read_data.py:220)
       ← read_next_month_data_main (read_data.py:363)
         ← next_month_main (cluster_alg_with_improve_bw.py:1674)
           ← __main__ (alg_version=1 分支)

3. 正确结论：cluster_alg_with_improve_bw.py 1 华东移动 会生成 vnode CSV
```

---

## 检查清单

追踪调用链前，确认：

- [ ] 已定位目标函数（写入/核心函数）
- [ ] 使用 LSP incomingCalls 向上追踪
- [ ] 递归追踪直到入口点
- [ ] 输出完整调用栈，标明文件名和行号
