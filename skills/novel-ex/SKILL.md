---
name: novel-ex
version: 1.0.0
description: 古典小说配图文生图工作流 - 将小说文本转换为配有 AI 生成图片和音乐的 Markdown 文档
user-invocable: true
argument-hint: "<URL或本地路径>"
triggers:
  - "小说配图"
  - "古文转换"
  - "novel_ex"
  - "/novel-ex"
  - "配图配乐"
last_updated: 2026-04-25
---

# novel-ex: 古典小说配图文生图工作流

将古典小说文本转换为配有 AI 生成图片和音乐的 Markdown 文档。

---

## 触发条件

用户提到：`小说配图`、`古文转换`、`novel_ex`、`/novel-ex`，或提供小说文本 URL/路径要求配图配乐。

---

## 工作流程

### Step 1: 获取内容

根据用户输入类型选择工具：

| 输入类型 | 工具 |
|----------|------|
| URL (http/https) | WebFetch 抓取 |
| WPS 文档 (365.kdocs.cn) | mcp__ksc-local-mcp__get_wps_content |
| 本地路径 (.md/.txt) | Read 读取 |

**清理规则**：
- 移除 HTML 标签，保留纯文本
- 清理全角空格缩进（替换为标准格式）
- 提取标题（h1/h2 或首行）

---

### Step 2: 分析内容

自动分析并生成：

1. **标记重点段落**（加粗 `**文字**`）
   - 关键词：转折点、金句、伏笔、照应
   - 动词形容词精妙之处

2. **生成金圣叹式评语**
   - 简短精炼（10-40 字）
   - 指出文字妙处
   - 用词古雅
   - 常用句式：
     - "\"X字\"妙"
     - "...写出..."
     - "...伏笔"
     - "对照前文"
     - "一字之妙"

3. **选取 top2 关键场景**
   - 最具画面感
   - 情节高潮或氛围典型
   - 适合文生图渲染

---

### Step 2.5: 场景视觉考据（必需）

生成图片前，必须确认视觉元素的正确性。

#### 缓存机制

**优先读取缓存，避免重复查证**：

```
~/.claude/skills/novel-ex/
├── references/           # 通用历史资料
│   ├── dynasty-costume.md
│   └── dynasty-architecture.md
└── cache/                # 小说专项缓存
    └── {小说名}/
        └── visual-reference.md
```

**执行流程**：

1. **检查缓存**：`Read cache/{小说名}/visual-reference.md`
   - 存在 → 直接使用缓存内容
   - 不存在 → 执行查证流程 → 保存到缓存

2. **通用资料**：`Read references/dynasty-costume.md`（唐宋元明清速查）

3. **首次查证后保存**：
   ```markdown
   # {小说名} - 视觉参考缓存
   > {朝代} 服饰、器物、建筑参考
   **缓存创建时间**：{日期}
   ```

#### 时代识别（从文本推断）

| 时代特征 | 关键词示例 |
|----------|-----------|
| 古代 | 年号（嘉靖、万历）、帝号、古地名、科举术语 |
| 近代 | 民国、抗战、租界、洋行 |
| 现代 | 汽车、手机、高楼、互联网 |
| 不确定 | 标记为"待确认"，执行下一步 |

#### 关键视觉元素确认

| 类别 | 确认项 | 常见错误示例 |
|------|--------|-------------|
| **服饰** | 帽饰、衣着、鞋履 | 宋代帽式 ≠ 清代帽式 |
| **器物** | 武器、工具、日常用品 | 明代刀剑 ≠ 唐代刀剑 |
| **建筑** | 房屋、城门、街道风格 | 宋代建筑 ≠ 明清建筑 |
| **环境** | 季节、天气、时间 | 正确即可 |

#### 不确定时处理流程

**优先级 1：原文查找**
```
在原文中搜索具体描述，如"毡笠"、"花枪"、"酒葫芦"
```

**优先级 2：WebSearch 查证**
```bash
WebSearch: "{朝代} {物品} 服饰特点"
WebSearch: "宋代 禁军教头 帽子"
```

**优先级 3：询问用户**
```
无法确定 {场景} 的 {元素}，请提供参考或选择：
A) {选项1}  B) {选项2}
```

#### Prompt 构建原则

1. **使用考据后的正确关键词**
   - ✅ `cone-shaped douli (Song dynasty bamboo hat)`
   - ❌ `felt hat`（不准确）

2. **原文有明确描述时优先使用**
   - 原文："把花枪挑了酒葫芦"
   - Prompt: `carrying a spear with a gourd wine container`

3. **不确定元素用模糊描述（避免出错）**
   - ❌ `three-story building with exactly 12 windows`
   - ✅ `distant building silhouette, architectural details soft`

4. **原文未提及的元素不应出现**
   - 原文没提"塔楼" → 不应出现高大塔楼
   - 原文只提"古庙" → 用 `small humble shrine`, `simple village temple`
   - ❌ 自行添加原文没有的元素

5. **历史常识约束（古代建筑）**
   | 元素 | 限制 | Prompt 关键词 |
   |------|------|--------------|
   | 楼层数 | 民用 1-2 层 | `single-story`, `low`, `modest` |
   | 塔楼 | 罕见，原文未提则不出现 | 避免 `tower`, `pagoda` |
   | 庙宇 | 小型土地庙/山神庙 | `small shrine`, `humble temple` |

#### 朝代服饰速查（常见）

| 朝代 | 男子帽饰关键词 | 武器关键词 |
|------|---------------|-----------|
| 唐 (618-907) | `futou`, `soft cap with flaps` | `Tang saber`, `lance` |
| 宋 (960-1279) | `douli`, `cone-shaped bamboo hat` | `Song spear`, `straight blade` |
| 明 (1368-1644) | `wusa hat`, `round cap` | `Ming saber`, `liuyedao` |
| 清 (1644-1912) | `queue`, `Manchu hat` | `qing saber`, `dao` |
| 民国 | `western hat`, `cap` | `rifle`, `pistol` |

---

### Step 3: 生成多媒体

#### 并行执行（推荐）

MiniMax API 支持并行调用，可显著提升效率：

```
单次响应中同时调用：
- mmx image generate (场景1) & mmx image generate (场景2) &
- mmx music generate (场景1) & mmx music generate (场景2)

然后并行下载图片，等待音乐完成
```

**效率对比**：
| 执行方式 | 耗时 |
|----------|------|
| 串行 | ~100+ 秒 |
| 并行 | ~60 秒 |

#### 图片生成规则

遵循 `.claude/rules/novel-illustration.md` 规则：

**核心规则**：
- 人物不正面（背影/侧影/剪影/远景小人物）
- 不确定场景模糊处理（建筑楼层数、具体数量）
- 视角远近分开（远景 > 中景 > 近景）
- 东方美学留白

**Prompt 模板**：

**核心原则：内容语言与输入文件一致 + 细节术语用英文**

```
[人物/场景描述 - 与输入语言相同],
[环境/氛围 - 与输入语言相同],
traditional Chinese ink painting aesthetic,
vast negative space, atmospheric perspective,
cinematic composition, soft brushwork,
aspect ratio 16:9
```

**示例（中文小说）**：
```
武僧背影，戴圆锥形竹斗笠，手持禅杖，
雪景古道，天色阴沉，
traditional Chinese ink painting style,
vast negative space, cinematic wide shot
```

**示例（英文小说）**：
```
Back view of a monk with bamboo hat, holding a staff,
snowy ancient path, gloomy sky,
traditional Chinese ink painting style,
vast negative space, cinematic wide shot
```

**英文术语速查**：
| 类别 | 英文术语 |
|------|---------|
| 构图 | `wide shot`, `medium shot`, `aerial view` |
| 光影 | `rim lighting`, `soft lighting`, `dramatic lighting` |
| 氛围 | `atmospheric`, `misty`, `ethereal` |
| 风格 | `ink painting style`, `negative space`, `monochrome` |
| 视角 | `back view`, `silhouette`, `figure in distance` |

**命令**：
```bash
mmx image generate --prompt "..." --aspect-ratio 16:9 --out-dir ./assets --out-prefix scene_01
```

#### 音乐生成规则

**Prompt 模板**：

**核心原则：内容语言与输入文件一致 + 细节术语用英文**

```
Traditional Chinese instrumental,
[场景氛围描述 - 与输入语言相同],
[乐器名称], brief atmospheric, cinematic ambient
```

**示例（中文小说）**：
```
Traditional Chinese instrumental,
雪夜孤独氛围，古琴独奏，
guqin, brief atmospheric
```

**英文术语速查**：
| 类别 | 英文术语 |
|------|---------|
| 氛围 | `mysterious`, `tense`, `sorrowful`, `triumphant` |
| 时长 | `brief`, `short`, `ambient` |
| 乐器 | `guqin`, `pipa`, `erhu`, `flute`, `drum` |

**命令**：
```bash
mmx music generate --model music-2.6 --prompt "..." --instrumental --out ./assets/scene_01_bgm.mp3
```

**注意**：实际时长取决于模型输出，在 prompt 中明确 "10 seconds"、"short"、"brief"。

---

### Step 4: 构建 Markdown

#### 格式规范

**原文段落**：正常显示，重点加粗

**评语样式**：
```html
<div style="color:#888;font-size:0.85em;margin-left:1em;border-left:2px solid #ccc;padding-left:0.5em;">【评】...</div>
```

**图片样式**：
```html
<img src="assets/xxx.jpg" width="100%" style="max-width:800px;border-radius:8px;margin:1em 0;">
```

**音频样式**：
```html
<audio controls style="width:100%;max-width:400px;margin:1em 0;">
  <source src="assets/xxx.mp3" type="audio/mpeg">
  您的浏览器不支持音频播放
</audio>
```

#### 文件结构

```markdown
# [标题]

---

## [章节名]

[原文段落]

<div style="...">【评】[评语]</div>

[下一段落...]

---

## [关键场景标题]

<img src="assets/scene_01.jpg" ...>

<audio controls ...>...</audio>

[继续原文...]

---

## 【回后总评】

[整体评价：主题、人物、技法总结]
```

---

### Step 5: 输出文件

**保存 Markdown**：`{作品名}_{章节}.md`（Chrome 可直接打开，支持音频播放）

**保存提示词**：`assets/{作品名}_{章节}_prompts.md`（便于回测和复用，与正文同名）

```markdown
# 生成提示词记录

> 日期：{日期}
> 章节：{章节名}

---

## 场景一：{场景名}

### 图片 Prompt
```
{完整 prompt}
```

### 音乐 Prompt
```
{完整 prompt}
```

---

## 视觉考据来源
缓存文件：`~/.claude/skills/novel-ex/cache/{小说名}/visual-reference.md`
```

---

## 评语生成模板

### 金圣叹风格要点

| 特征 | 示例 |
|------|------|
| 一字评 | "\"紧\"字第一见。有势将来之意。" |
| 对照法 | "\"抬举\"二字，对照前文管营\"抬举\"林冲。" |
| 伏笔法 | "\"神明庇佑\"四字，是伏笔。后文果赖神明庇佑。" |
| 写出法 | "\"把花枪挑了酒葫芦\"九字，写林冲何等从容。" |
| 妙字法 | "妙绝！此乃天意，非人力也。" |
| 人物法 | "不是林冲狠，是林冲定。" |

### 评语位置

- 关键动词/形容词后
- 转折点后
- 伏笔处
- 照应处
- 场景描写精彩处

---

## 执行检查清单

生成前：
- [ ] 内容获取成功
- [ ] 标题正确提取
- [ ] 章节结构清晰

生成中：
- [ ] 时代识别完成
- [ ] 视觉元素考据（服饰/器物/建筑）
- [ ] 重点段落标记
- [ ] 评语符合金圣叹风格
- [ ] 图片 prompt 使用正确历史关键词
- [ ] 图片 prompt 遵守规则（无正面人脸、模糊建筑）
- [ ] 音乐 prompt 含时长限定

生成后：
- [ ] Markdown 格式正确
- [ ] 图片路径正确
- [ ] 音频路径正确

---

## 示例调用

```
用户: /novel-ex https://www.guwendao.net/guwen/shuihu_10.aspx

Claude 执行:
1. WebFetch 获取内容
2. 分析：提取标题"林教头风雪山神庙"
3. 识别关键场景：沽酒雪行、山神庙夜宿
4. Step 2.5 视觉考据：
   - 时代：北宋（从"沧州"、"高太尉"推断）
   - 服饰：原文"毡笠"→ WebSearch 查证 → "cone-shaped douli"
   - 器物：原文"花枪"、"酒葫芦" → 使用原文关键词
5. 生成图片 x2（使用正确关键词）
6. 生成音乐 x2
7. 构建 Markdown
8. 输出：水浒传第十回.md
```

---

## 依赖

- mmx CLI (MiniMax API)
- WebFetch / Read / MCP 工具
- .claude/rules/novel-illustration.md（文生图规则）
