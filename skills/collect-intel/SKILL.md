---
name: collect-intel
version: 1.0.0
description: |
  集智决策系统：自动识别问题领域，选择最合适的专家视角，并行调用，按权重汇总决策答案。

  触发词：「集智」「多位专家」「综合视角」「collect intel」「collect_intel」「wisdom of crowds」。

  当用户需要多角度分析、不确定该问哪个专家、或想要综合性决策参考时使用。
user-invocable: true
argument-hint: "<问题>"
triggers:
  - "集智"
  - "多位专家"
  - "综合视角"
  - "collect intel"
  - "wisdom of crowds"
last_updated: 2026-05-04
---

# 集智决策 · Collective Intelligence System

> "The wisdom of crowds works when the crowd is diverse, decentralized, and aggregated properly."
> —— James Surowiecki

## 核心理念

单一视角有盲区。多视角并行，权重汇总，能逼近更全面的决策。

**与单 Skill 的区别**：
| 单 Skill | collect_intel |
|----------|---------------|
| 一个视角 | 多视角并行 |
| 手动选择 | 自动路由 |
| 单一结论 | 权重汇总 |
| 深度优先 | 广度优先 |

---

## 执行流程

### Phase 1: 问题分类

**自动识别问题所属领域**：

| 领域代码 | 领域名称 | 典型关键词 |
|---------|---------|-----------|
| `INVEST` | 投资决策 | 投资、股票、估值、回报、风险、组合、资产 |
| `STARTUP` | 创业/商业 | 创业、产品、PMF、商业模式、融资、增长 |
| `PRODUCT` | 产品决策 | 产品、功能、用户体验、设计、迭代 |
| `RISK` | 风险管理 | 风险、黑天鹅、不确定性、尾部、脆弱 |
| `LEARN` | 学习/理解 | 理解、学习、解释、概念、教学 |
| `CAREER` | 职业人生 | 职业、选择、方向、人生、时间 |
| `TECH` | 技术/AI | 技术、AI、编程、模型、架构 |
| `STRATEGY` | 战略决策 | 战略、竞争、护城河、长期、决策 |

**分类方法**：
1. 关键词匹配（快速）
2. LLM 语义理解（精确）
3. 用户手动指定（兜底）

**输出**：`primary_domain` + `secondary_domains[]`

---

### Phase 2: 专家选择

**根据领域选择专家，按权重分配**：

#### 权重矩阵（训练样本）

```yaml
# 专家权重配置
weights:
  # 投资决策
  INVEST:
    munger-perspective: 0.30      # 主导：逆向思考、激励分析
    duan-yongping-perspective: 0.25 # 辅助：中国价值投资、企业文化
    taleb-perspective: 0.20       # 辅助：尾部风险、反脆弱
    naval-perspective: 0.15       # 辅助：杠杆、长期主义
    ma-yun-perspective: 0.10      # 补充：战略视角、中国经验

  # 创业/商业
  STARTUP:
    paul-graham-perspective: 0.35 # 主导：创业方法论、PMF
    zhang-yiming-perspective: 0.30 # 辅助：组织、产品克制
    naval-perspective: 0.20       # 辅助：杠杆、复利
    elon-musk-perspective: 0.15   # 辅助：第一性原理

  # 产品决策
  PRODUCT:
    steve-jobs-perspective: 0.40  # 主导：极简、用户心理
    feynman-perspective: 0.25    # 辅助：货物崇拜检测
    paul-graham-perspective: 0.20 # 辅助：用户需求验证
    zhang-yiming-perspective: 0.15 # 辅助：产品克制

  # 风险管理
  RISK:
    taleb-perspective: 0.45       # 主导：反脆弱、尾部风险
    munger-perspective: 0.25      # 辅助：逆向思考、Lollapalooza
    naval-perspective: 0.15       # 辅助：长期视角
    feynman-perspective: 0.15     # 辅助：反自欺

  # 学习/理解
  LEARN:
    feynman-perspective: 0.45     # 主导：命名≠理解、类比
    karpathy-perspective: 0.25    # 辅助：技术理解
    naval-perspective: 0.15       # 辅助：学习杠杆
    munger-perspective: 0.15      # 辅助：多元思维

  # 职业人生
  CAREER:
    naval-perspective: 0.40       # 主导：杠杆、复利、人生策略
    paul-graham-perspective: 0.25 # 辅助：独立思考
    feynman-perspective: 0.20     # 辅助：深度游戏、好奇心
    munger-perspective: 0.15      # 辅助：逆向思考、避免愚蠢

  # 技术/AI
  TECH:
    karpathy-perspective: 0.35    # 主导：AI、工程
    ilya-sutskever-perspective: 0.30 # 辅助：AI安全、scaling
    elon-musk-perspective: 0.20   # 辅助：第一性原理、工程
    feynman-perspective: 0.15     # 辅助：理解验证

  # 战略决策
  STRATEGY:
    munger-perspective: 0.25      # 主导：逆向思考、多元思维
    elon-musk-perspective: 0.25   # 主导：第一性原理
    steve-jobs-perspective: 0.20  # 辅助：聚焦、极简
    naval-perspective: 0.15       # 辅助：杠杆思维
    zhang-yiming-perspective: 0.15 # 辅助：组织进化
```

**权重解释**：
- **0.35-0.45**：主导专家，该领域最强视角
- **0.20-0.30**：辅助专家，补充关键维度
- **0.10-0.20**：补充专家，提供边界检查

---

### Phase 3: 并行调用

**同时调用选中的 Skills（通常 3-5 个）**：

```
问题: [用户问题]
├── Skill A → 回答 A
├── Skill B → 回答 B
├── Skill C → 回答 C
└── Skill D → 回答 D
```

**调用规则**：
1. 每个 Skill 独立调用，互不干扰
2. 每个 Skill 都收到完整的原始问题
3. 每个 Skill 都按自己的风格回答
4. 如果某个 Skill 缺失，跳过并重新分配权重

---

### Phase 4: 权重汇总

**整合多个回答，按权重输出**：

#### 汇总格式

```markdown
# 集智决策报告

## 问题
[用户原始问题]

## 领域识别
- 主领域：[领域名称]
- 相关领域：[次要领域列表]

## 专家观点

### [专家1名] (权重: XX%)
[回答内容摘要]

### [专家2名] (权重: XX%)
[回答内容摘要]

### [专家3名] (权重: XX%)
[回答内容摘要]

## 综合决策

### 共识点
- [所有专家都同意的观点]

### 分歧点
- [专家之间的不同意见]

### 权重加权建议
[按权重汇总的核心建议]

### 风险提示
- [最高权重专家的风险提示]
- [其他专家补充的风险]

---

**置信度**：[基于权重集中度的置信度]
**建议**：[是否需要更多专家、是否需要深入研究]
```

---

## 训练样本

> 以下样本用于校准权重矩阵

### 样本1：投资决策

```yaml
question: "泡泡玛特现在值得投资吗？"
domain: INVEST
experts:
  - skill: munger-perspective
    weight: 0.35
    expected_focus: "护城河、管理层激励、逆向思考（什么会亏钱）、Too Hard分类"
  - skill: taleb-perspective
    weight: 0.25
    expected_focus: "尾部风险、反脆弱性检验、凸性分析"
  - skill: naval-perspective
    weight: 0.20
    expected_focus: "长期价值、杠杆思维"
  - skill: zhang-yiming-perspective
    weight: 0.20
    expected_focus: "组织能力、IP战略（中国视角）"

validation:
  consensus_check: "估值是否合理、风险是否可控"
  divergence_check: "芒格可能放Too Hard，Taleb可能强调尾部风险"
  weight_adjustment: "如果决策明确，可提高主导专家权重"
```

### 样本2：创业方向

```yaml
question: "我有技术背景，想做一个AI工具，但不确定方向，怎么选？"
domain: STARTUP
experts:
  - skill: paul-graham-perspective
    weight: 0.35
    expected_focus: "问题是真实的吗？用户是谁？能独立启动吗？PMF检验"
  - skill: zhang-yiming-perspective
    weight: 0.30
    expected_focus: "组织进化、产品克制、全球化视角"
  - skill: naval-perspective
    weight: 0.20
    expected_focus: "杠杆思维、复利、产品化自己"
  - skill: elon-musk-perspective
    weight: 0.15
    expected_focus: "第一性原理：AI工具的本质是什么？"

validation:
  consensus_check: "用户需求验证、MVP方向"
  divergence_check: "PG强调独立开发，Yiming强调组织能力"
```

### 样本3：概念理解

```yaml
question: "什么是强化学习？用最简单的话解释。"
domain: LEARN
experts:
  - skill: feynman-perspective
    weight: 0.45
    expected_focus: "不用术语、具体例子、命名≠理解检验"
  - skill: karpathy-perspective
    weight: 0.25
    expected_focus: "技术直觉、代码视角、实现细节"
  - skill: naval-perspective
    weight: 0.15
    expected_focus: "学习杠杆、复利学习"
  - skill: munger-perspective
    weight: 0.15
    expected_focus: "多元思维、跨学科类比"

validation:
  consensus_check: "核心机制解释、具体例子"
  divergence_check: "Feynman用日常类比，Karpathy用代码类比"
```

### 样本4：风险决策

```yaml
question: "我的投资组合年化15%，但最大回撤40%，这样合理吗？"
domain: RISK
experts:
  - skill: taleb-perspective
    weight: 0.45
    expected_focus: "尾部风险、反脆弱检验、脆弱性分析"
  - skill: munger-perspective
    weight: 0.25
    expected_focus: "逆向思考、Lollapalooza效应检测"
  - skill: naval-perspective
    weight: 0.15
    expected_focus: "长期视角、时间复利"
  - skill: feynman-perspective
    weight: 0.15
    expected_focus: "数据验证、自欺检测"

validation:
  consensus_check: "40%回撤是否可接受、风险调整收益"
  divergence_check: "Taleb强调尾部风险，Munger强调激励机制"
```

### 样本5：产品决策

```yaml
question: "我们的产品功能越来越多，用户反馈复杂，怎么办？"
domain: PRODUCT
experts:
  - skill: steve-jobs-perspective
    weight: 0.40
    expected_focus: "极简主义、砍什么、用户真正需要什么"
  - skill: feynman-perspective
    weight: 0.25
    expected_focus: "货物崇拜检测：功能是形式还是实质？"
  - skill: paul-graham-perspective
    weight: 0.20
    expected_focus: "用户需求验证、MVP思维"
  - skill: zhang-yiming-perspective
    weight: 0.15
    expected_focus: "产品克制、延迟满足"

validation:
  consensus_check: "简化方向、用户价值"
  divergence_check: "Jobs直接砍，Feynman检验货物崇拜"
```

### 样本6：技术选择

```yaml
question: "我们应该用微服务架构吗？团队只有5个人。"
domain: TECH
experts:
  - skill: karpathy-perspective
    weight: 0.35
    expected_focus: "工程实践、复杂度成本、团队规模匹配"
  - skill: elon-musk-perspective
    weight: 0.25
    expected_focus: "第一性原理：问题本质是什么？"
  - skill: feynman-perspective
    weight: 0.20
    expected_focus: "货物崇拜检测：微服务是形式还是需要？"
  - skill: paul-graham-perspective
    weight: 0.20
    expected_focus: "创业团队应该怎么做？过早优化？"

validation:
  consensus_check: "团队规模不匹配微服务"
  divergence_check: "Karpathy强调工程成本，Elon强调本质问题"
```

---

## 权重调优方法

### 自动调优（推荐）

```python
# 伪代码
def adjust_weights(question, domain, expert_answers, user_feedback):
    """
    根据用户反馈调整权重

    用户反馈：
    - 哪个专家最有用？
    - 整体决策是否有帮助？
    - 是否遗漏关键视角？
    """
    for expert in experts:
        if user_feedback[f"{expert}_useful"]:
            weights[domain][expert] += 0.05
        else:
            weights[domain][expert] -= 0.05

    # 归一化
    normalize(weights[domain])
```

### 手动调优

用户可以直接编辑 `weights.yaml` 文件，调整各专家权重。

---

## 输出选项

### 标准输出（推荐）

```
集智决策报告（见上方格式）
```

### 精简输出

```
核心建议：[一句话]
共识点：[2-3条]
分歧点：[1-2条]
风险提示：[1-2条]
```

### 详细输出

```
完整报告 + 各专家完整回答原文
```

---

## 已安装专家清单

| Skill 名称 | 状态 | 主要领域 |
|-----------|------|---------|
| munger-perspective | ✅ 已安装 | 投资、决策、风险 |
| duan-yongping-perspective | ✅ 已安装 | 投资、企业经营、人生选择 |
| feynman-perspective | ✅ 已安装 | 学习、理解、科学 |
| paul-graham-perspective | ✅ 已安装 | 创业、写作、产品 |
| zhang-yiming-perspective | ✅ 已安装 | 产品、组织、全球化 |
| karpathy-perspective | ✅ 已安装 | AI、工程、教育 |
| ilya-sutskever-perspective | ✅ 已安装 | AI安全、scaling |
| steve-jobs-perspective | ✅ 已安装 | 产品、设计、战略 |
| elon-musk-perspective | ✅ 已安装 | 工程、第一性原理 |
| naval-perspective | ✅ 已安装 | 财富、杠杆、人生 |
| taleb-perspective | ✅ 已安装 | 风险、反脆弱 |
| ma-yun-perspective | ✅ 已安装 | 创业、管理、战略 |

---

## 限制与边界

1. **不替代决策**：这是辅助系统，最终决策权在用户
2. **专家有限**：当前只覆盖已安装的专家视角
3. **权重是估算**：权重基于训练样本，可能需要调优
4. **并行调用成本**：同时调用多个 Skills 会消耗更多 token
5. **汇总有损失**：多视角整合必然丢失细节

---

## 示例

**用户**：`/collect-intel 我该不该辞职创业？`

**系统输出**：
```
# 集智决策报告

## 问题
我该不该辞职创业？

## 领域识别
- 主领域：CAREER（职业人生）
- 相关领域：STARTUP（创业）

## 专家观点

### Naval (权重: 40%)
辞职创业不是目的，目的是获得杠杆。你现在有杠杆吗？
- 产品化自己：你的技能能产品化吗？
- 复利：创业能让你积累复利吗？
- 杠杆类型：资金杠杆（VC）还是产品杠杆（代码/媒体）？

### Paul Graham (权重: 25%)
不要为了创业而创业。你有忍不住想解决的问题吗？
- 独立思考：你看到的别人没看到的是什么？
- 现实检验：你能不辞职先试水吗？

### Feynman (权重: 20%)
你确定你是"想创业"还是"不想上班"？
- 货物崇拜：你是在模仿创业者，还是真有东西要做？
- 深度游戏：创业这事对你有内在吸引力吗？

### Munger (权重: 15%)
逆向思考：什么情况下辞职创业一定失败？
- 没有积蓄、没有明确方向、只有"想创业"的冲动
- 把辞职当成解决方案，而不是成本

## 综合决策

### 共识点
- 不要为了创业而创业
- 需要验证真实需求/问题
- 可以先不辞职试水

### 分歧点
- Naval强调杠杆思维，PG强调独立思考
- Munger逆向切入，Feynman反自欺检测

### 权重加权建议
1. 先检验动机：是"想创业"还是"不想上班"
2. 找到真实问题：有没有忍不住想解决的
3. 不辞职试水：用最小成本验证
4. 积累杠杆：产品化自己、复利积累

### 风险提示
- 辞职是不可逆决策，需要高确信度
- 创业成功率低，需要风险承受能力

---

**置信度**：中等（专家意见有分歧）
**建议**：可以补充 STARTUP 领域专家（张一鸣）获取组织视角
```

---

## 后续扩展

1. **动态权重学习**：根据用户反馈自动调优
2. **专家推荐**：识别缺失的专家视角，推荐安装
3. **冲突仲裁**：当专家意见强烈分歧时，提供仲裁机制
4. **历史记忆**：记住用户偏好，个性化权重
5. **导出配置**：导出权重配置，供其他平台使用
