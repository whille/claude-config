---
name: intel
version: 1.2.0
description: 信息源适配层。AI预判源选择，扫描多源信息（B站/GitHub/RSS），自动去重、评分、筛选。加 --deep 深度提取字幕/代码分析。
user-invocable: true
argument-hint: "<主题> [--deep]"
triggers:
  - "情报收集"
  - "信息跟踪"
  - "intel"
  - "信息源监控"
  - "持续跟踪"
last_updated: 2026-04-20
---

# Intel

信息源适配层，负责从不同信息源获取内容并输出标准化格式。

---

## 架构定位

```
┌─────────────────────────────────────────────────┐
│                    intel                         │
│              （信息源适配层）                      │
├─────────────────────────────────────────────────┤
│  B站        │  GitHub      │  Web    │  PDF     │
│  ───        │  ──────      │  ───    │  ───     │
│  抓字幕     │  克隆仓库    │  提取   │  读取    │
│  (登录态)   │  代码分析    │  全文   │  内容    │
└─────────────────────────────────────────────────┘
                      ↓
            标准化输出（raw/）
                      ↓
┌─────────────────────────────────────────────────┐
│                  llm-wiki                        │
│              （内容处理层）                       │
├─────────────────────────────────────────────────┤
│  结构化整理 → 生成摘要 → 建立关联                │
└─────────────────────────────────────────────────┘
```

### 职责边界

| 层级 | 职责 | 不负责 |
|------|------|--------|
| **intel** | 信息源适配、获取手段、价值筛选 | 结构化、建立关联 |
| **llm-wiki** | 结构化整理、摘要生成、关联建立 | 从哪来的、怎么获取 |

---

## 使用方式

### 快速扫描

```bash
/intel 鱼菜共生
```

多源搜索，生成报告，筛选高价值内容。

### 深度扫描

```bash
/intel 鱼菜共生 --deep
```

扫描 + 深度提取（字幕/代码分析），一步到位。

### 参数说明

| 参数 | 说明 |
|------|------|
| `<主题>` | 快速扫描，生成报告筛选价值，Top 5 高价值内容 |
| `--deep` | 深度提取：B站抓字幕、GitHub克隆分析、Web提全文 |

---

## 执行流程

### 第一步：AI 预判（源路由）

每次执行前，AI 根据关键词轻量预判，决定搜哪些源、跳哪些源。

```
/intel 胜宏科技港股上市
         │
         ▼
    ┌──────────────────────────────┐
    │  AI 预判（轻量，少量token）   │
    │                              │
    │  1. 源选择（搜/跳）           │
    │     GitHub? ❌ 股市不相关     │
    │     B站?    ✅ 可能有财经UP   │
    │     Web?    ✅ 万能源，必搜   │
    │     PDF?    等用户指定路径     │
    │                              │
    │  2. RSS 匹配                 │
    │     现有 tags 含 stock?      │
    │       → 有: 用对应 feed      │
    │       → 无: WebSearch 找RSS  │
    │         → 找到 → 追加yaml    │
    │         → 本次使用            │
    └──────────────────────────────┘
         │
         ▼
    只搜: Web + B站 + 匹配的RSS
```

**预判规则**：

| 源 | 判断逻辑 | 示例 |
|----|---------|------|
| **Web** | 永远搜 | — |
| **B站** | 关键词是否可能有视频内容 | 股市→✅、编程→✅、纯代码bug→❌ |
| **GitHub** | 关键词是否涉及代码/项目/框架 | 代码→✅、股市→❌、鱼菜共生→❌ |
| **PDF** | 用户是否指定了文件路径 | 有路径→✅，否则→跳过 |
| **RSS** | 现有 feeds 的 tags 是否匹配关键词意图；不匹配则跳过该 feed；全部不匹配则尝试发现新 RSS 源 |

**RSS 动态发现流程**：

```
关键词意图: [stock, finance]
    │
    ├─ 扫描现有 feeds tags → 无匹配
    │
    ├─ WebSearch: "{领域} RSS feed"
    │   例: "财经 RSS feed 中国股市"
    │
    ├─ 验证 RSS 可用性（尝试 fetch）
    │
    └─ 追加到 intel.yaml:
       - name: "东方财富-要闻"
         url: "https://..."
         tags: [stock, finance, a-share]
         base_score: 30
       → 本次搜索使用
       → 后续同类查询直接命中
```

### 第二步：快速扫描（默认）

```
/intel 主题
    ↓
    [AI 预判: 确定搜索源]
    ↓
┌─────────────────────────────────┐
│ 仅搜预判通过的源：              │
│ B站：搜索 → 列表 → 可信度评分   │
│ GitHub：搜索 → Stars → 评分     │
│ Web：搜索 → 摘要 → 评分         │
│ RSS：匹配的feeds → 摘要 → 评分  │
└─────────────────────────────────┘
    ↓
reports/YYYY-MM-DD-主题.md
（供用户判断是否深入）
```

### 第三步：深度扫描（--deep）

```
/intel 主题 --deep
    ↓
    [AI 预判: 确定搜索源]
    ↓
┌─────────────────────────────────┐
│ 仅对预判通过的源深度提取：      │
│ B站：搜索 → 登录态API → 完整字幕 │
│ GitHub：搜索 → 克隆 → 代码分析   │
│ Web：搜索 → 全文提取            │
│ RSS：跳转原文 → 全文提取        │
└─────────────────────────────────┘
    ↓
wiki/raw/
（标准化输出，可直接进入 llm-wiki）
```

---

## 信息源适配器

| 源 | 快速扫描 | 深度提取 | 输出格式 |
|----|---------|---------|---------|
| **B站** | 标题/播放量/UP主 | 完整字幕（SRT） | `subtitles/*.srt` |
| **GitHub** | Stars/简介/评分 | 克隆+代码分析 | `articles/*.md` |
| **Web** | 标题/摘要 | 全文提取 | `articles/*.md` |
| **PDF** | 文件元信息 | OCR/文本提取 | `pdfs/*.md` |
| **RSS** | 标题/摘要 | 跳转原文提取 | `articles/*.md` |

---

## B站适配器

### 快速扫描

```python
# 搜索关键词，获取视频列表
videos = search_bilibili("鱼菜共生", limit=20)

# 对每个视频计算可信度
for v in videos:
    v.credibility = calculate_credibility(v)
    # 基于：播放量、UP主粉丝、官方认证、历史播放量
```

### 深度提取（字幕）

```python
# 需要登录态
credential = load_credential("~/.claude/bilibili-credential.json")

# 获取字幕
subtitle = await video.get_subtitle(cid, credential)

# 输出 SRT 格式
save_srt(subtitle, "subtitles/xxx.srt")
```

**凭证文件**：`~/.claude/bilibili-credential.json`

```json
{
  "SESSDATA": "xxx",
  "bili_jct": "xxx",
  "buvid3": "xxx"
}
```

---

## GitHub适配器

### 快速扫描

```python
# 搜索项目
repos = search_github("aquaponics", sort="stars", limit=20)

# 评分维度
for r in repos:
    r.score = (
        r.stars * 0.3 +
        r.forks * 0.2 +
        r.recent_activity * 0.2 +
        r.documentation_quality * 0.3
    )
```

### 深度提取（代码分析）

```python
# 克隆仓库（浅克隆）
clone_repo(url, depth=1)

# 分析核心模块
analysis = {
    "structure": analyze_structure(),      # 目录结构
    "core_modules": find_core_files(),     # 核心文件
    "patterns": extract_design_patterns(), # 设计模式
    "dependencies": parse_requirements(),  # 依赖
    "entry_points": find_entry_points()    # 入口点
}

# 生成代码洞察文档
generate_code_insight(analysis)
```

**分析维度**：

| 维度 | 说明 |
|------|------|
| 目录结构 | 模块划分、分层架构 |
| 核心文件 | 主控制器、配置、路由 |
| 设计模式 | 单例、工厂、观察者等 |
| 数据模型 | 表结构、字段含义 |
| 依赖版本 | requirements.txt 解析 |

---

## 输出规范

### 扫描报告格式

```markdown
# XXX信息扫描报告

> 扫描时间：YYYY-MM-DD
> 关键词：XXX
> 高价值内容：N 条

## 扫描统计

| 指标 | 数值 |
|------|------|
| B站视频 | N 个 |
| GitHub项目 | N 个 |

## 高价值内容

### 1. [标题](URL)

| 属性 | 值 |
|------|---|
| 来源 | xxx |
| 评分 | XX/100 |
```

### 深度提取格式

```markdown
---
url: https://xxx
source: GitHub/B站/Web
fetched: YYYY-MM-DD
---

# 标题

## 基本信息
...

## 核心内容
...

## 代码架构洞察（仅GitHub）
...
```

---

## 与 llm-wiki 集成

```
/intel 主题
      ↓
reports/（快速筛选）
      ↓ 用户决定是否深入

/intel 主题 --deep
      ↓
wiki/raw/（标准化内容）

/llm-wiki ingest
      ↓
wiki/sources/（摘要页）
```

---

## 配置

### 路径配置

**执行时解析顺序**：

```python
# 1. 环境变量优先
import os
INTEL_HOME = os.environ.get("INTEL_HOME")

# 2. 默认目录
if not INTEL_HOME:
    INTEL_HOME = os.path.expanduser("~/Documents/ai_intel")

# 3. 确保目录存在
os.makedirs(f"{INTEL_HOME}/reports", exist_ok=True)
os.makedirs(f"{INTEL_HOME}/cache", exist_ok=True)
```

**目录结构**：

```
$INTEL_HOME/
├── reports/     # 扫描报告
├── cache/       # 去重缓存
├── history.json # 扫描历史
└── wiki/        # llm-wiki 知识库（共享）
```

**报告命名规则**：

```
{INTEL_HOME}/reports/{topic}-{YYYY-MM-DD}.md
```

示例：`~/Documents/ai_intel/reports/ai-agent-refactoring-2026-04-20.md`

### B站登录凭证

从浏览器 Cookie 提取：

| 字段 | 说明 |
|------|------|
| SESSDATA | 登录会话 |
| bili_jct | CSRF token |
| buvid3 | 设备标识 |

保存至：`~/.claude/bilibili-credential.json`

---

## 详细设计

- 详细评分算法见项目文档
- 缓存去重机制见 `cache/` 目录结构
