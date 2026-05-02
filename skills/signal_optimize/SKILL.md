---
name: signal_optimize
version: 1.1.0
description: StockQ 参数优化工作流 - 回测优化参数、更新配置、推送部署
user-invocable: true
argument-hint: "[optimizer] [days] 或留空使用默认值"
triggers:
  - "参数优化"
  - "signal optimize"
  - "优化参数"
  - "optuna优化"
last_updated: 2026-04-22
project: stockq
---

# 参数优化工作流

运行参数优化、推送配置、远程部署。

**仅对 stockq 项目有效。**

## 执行步骤

1. 并发运行 leaders + fusion 权重优化
2. 顺序执行 stage_top 卖出参数优化
3. Git commit & push
4. 远程服务器 pull & 测试

## 用法

```bash
# 完整工作流（默认，并发执行）
/signal_optimize

# 指定优化器
/signal_optimize leaders

# 指定优化器和天数
/signal_optimize leaders 730
```

## 可用优化器

| 优化器 | 说明 | 并发 |
|--------|------|------|
| `leaders` | 龙头策略权重 | ✅ 可并发 |
| `fusion` | 融合策略权重 | ✅ 可并发 |
| `stage_top` | 阶段顶部卖出参数 | ❌ 需单独执行 |

## stage_top 说明

**阶段性顶部参数优化** - 识别股票局部高点，优化卖出信号：

- `return_threshold`: 累积涨幅阈值（涨多少才算"高位"）
- `turnover_ratio_threshold`: 换手率比值（当天换手率/过去20日均值）

触发条件：累积涨幅 >= 阈值 且 换手率比值 >= 阈值 → 发出卖出信号

## 执行命令

根据参数执行：

```bash
# 默认完整工作流（leaders/fusion 并发）
python scripts/auto_optimize.py --days 365 --n-trials 50 --push --remote-test

# 指定优化器
python scripts/auto_optimize.py --optimizer {optimizer} --days {days} --push --remote-test
```

## 预检查

执行前确认：
1. 当前在 stockq 项目目录
2. Git 工作目录干净或愿意提交
3. 远程服务器可访问
