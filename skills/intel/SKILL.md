---
name: intel
version: 1.3.0
description: 信息源适配层。AI预判源选择，扫描多源信息（B站/GitHub/RSS），自动去重、评分、筛选。加 --deep 深度提取字幕/代码分析，B站自动获取AI字幕。
user-invocable: true
argument-hint: "<主题> [--deep]"
triggers:
  - "情报收集"
  - "信息跟踪"
  - "intel"
  - "信息源监控"
  - "持续跟踪"
last_updated: 2026-05-04
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
| `--deep` | 深度提取：B站自动获取字幕（普通/AI）、GitHub克隆分析、Web提全文 |

### --deep 对 B站的处理

1. 搜索关键词，计算可信度，筛选 Top N 视频
2. 对每个视频尝试获取字幕：
   - 优先：UP主上传的普通字幕
   - 其次：B站 AI 自动生成的字幕
   - 最后：使用视频简介
3. 基于字幕内容生成洞察摘要
4. 汇总生成深度报告

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

### B站深度扫描流程

```
/intel 主题 --deep
    │
    ├─ 调用 bilibili-analyzer 搜索
    │     ↓
    │   计算可信度，筛选 top N 视频
    │     ↓
    ├─ 对每个 top N 视频：
    │     │
    │     ├─ 尝试获取普通字幕（UP主上传）
    │     │     ↓
    │     ├─ 无字幕？尝试获取 AI 字幕
    │     │     ↓
    │     │   调用 subtitle/web/view API
    │     │     ↓
    │     │   解析 Protobuf 提取 auth_key
    │     │     ↓
    │     │   构造字幕 URL 下载
    │     │     ↓
    │     ├─ 保存字幕到 reports/subtitles/
    │     │
    │     └─ 生成单视频洞察摘要
    │           ↓
    └─ 汇总生成深度报告
          ↓
      reports/{主题}-{日期}-deep.md
```

**字幕获取优先级**：

| 优先级 | 类型 | 来源 | 说明 |
|--------|------|------|------|
| 1 | 普通字幕 | UP主上传 | `video.get_subtitle()` |
| 2 | AI 字幕 | B站自动生成 | `aisubtitle.hdslb.com` |
| 3 | 简介 | 视频描述 | 字幕都无时使用 |

**AI 字幕获取代码**：

```python
# 使用 bilibili-analyzer 提供的脚本
import sys
sys.path.insert(0, f"{CLAUDE_SKILL_DIR}/bilibili-analyzer/scripts")
from bilibili_ai_subtitle import fetch_bilibili_ai_subtitle, BilibiliCredential

async def get_bilibili_subtitle(bvid: str) -> str:
    """获取 B站视频字幕（普通字幕或 AI 字幕）"""

    credential = BilibiliCredential(
        sessdata=os.environ.get("BILIBILI_SESSDATA"),
        bili_jct=os.environ.get("BILIBILI_BILI_JCT"),
        buvid3=os.environ.get("BILIBILI_BUVID3")
    )

    # 方法1: 尝试普通字幕
    subtitle = await get_normal_subtitle(bvid)
    if subtitle:
        return subtitle

    # 方法2: 尝试 AI 字幕
    try:
        subtitles = await fetch_bilibili_ai_subtitle(bvid, credential, verbose=False)
        return "\n".join([f"[{s.time:.1f}s] {s.content}" for s in subtitles])
    except:
        pass

    # 方法3: 返回简介
    return await get_video_description(bvid)
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

# 优先级：普通字幕 > AI字幕 > 简介
subtitle = await get_subtitle_with_fallback(bvid, credential)

# 输出 SRT 格式
save_srt(subtitle, "subtitles/xxx.srt")
```

### AI 字幕获取

**原理**：B站部分视频有 AI 自动生成的字幕，存储在 CDN 上。

**获取流程**：

```
1. 调用 subtitle/web/view API
   https://api.bilibili.com/x/v2/subtitle/web/view?oid={cid}&pid={aid}&...
   返回 Protobuf 格式
     ↓
2. 解析 Protobuf 提取 auth_key
   auth_key 格式: timestamp-{hash1}-0-{hash2}
     ↓
3. 构造字幕 URL
   https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/{aid}{cid}{hash}?auth_key={auth_key}
     ↓
4. 下载 JSON 字幕
   {"body": [{"from": 0.0, "content": "..."}, ...]}
```

**代码示例**：

```python
# 使用 bilibili-analyzer 的脚本
from bilibili_ai_subtitle import fetch_bilibili_ai_subtitle, load_credential_from_file

async def get_ai_subtitle(bvid: str) -> str:
    credential = load_credential_from_file()
    subtitles = await fetch_bilibili_ai_subtitle(bvid, credential)

    # 转换为带时间戳的文本
    lines = [f"[{s.time:.1f}s] {s.content}" for s in subtitles]
    return "\n".join(lines)
```

**注意事项**：
- auth_key 有效期约 60 秒
- 并非所有视频都有 AI 字幕
- 需要有效的 SESSDATA 登录态

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

### B站视频深度报告格式

```markdown
# {主题} B站深度扫描报告

> 扫描时间：YYYY-MM-DD
> 关键词：XXX
> Top N 视频：N 个
> 字幕获取成功率：N/N

## 视频洞察

### 1. [视频标题](URL)

| 属性 | 值 |
|------|---|
| UP主 | xxx |
| 可信度 | XX (A级) |
| 播放量 | xxx |
| 时长 | xx分钟 |
| 字幕来源 | AI字幕/普通字幕/简介 |

**核心观点**：
- 观点1
- 观点2

**技术要点**：
- 要点1
- 要点2

**字幕摘要**（前500字）：
> 字幕内容摘要...

---

### 2. [视频标题](URL)
...

## 综合洞察

### 主要发现
- 发现1
- 发现2

### 共性观点
- 观点1
- 观点2

### 推荐深入
- 视频1：理由
- 视频2：理由

## 附录：完整字幕

字幕文件保存在：`reports/subtitles/{主题}-{日期}/`
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
