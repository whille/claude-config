---
name: scene-img
version: 3.0.0
description: 场景文生图工作流 - 将文本中的场景描述转换为配有 AI 生成图片的 Markdown 文档
user-invocable: true
argument-hint: "<URL或本地路径或文本>"
triggers:
  - "场景配图"
  - "生成场景图"
  - "文生图"
  - "配图"
last_updated: 2026-04-26
---

# scene-img: 场景文生图工作流

将文本中的场景描述提取，并生成 AI 配图，输出为 Markdown 文档。

适用于：小说章节、散文描写、剧本场景、游记、说明文字等任何包含场景描写的文本。

---

## 触发条件

用户提到：`场景配图`、`生成场景图`、`文生图`、`/scene-img`，或提供文本 URL/路径要求配图。

---

## 支持的文本类型

| 类型 | 示例 |
|------|------|
| 古典小说 | 水浒传、红楼梦、西游记 |
| 现代小说 | 任意小说章节 |
| 散文游记 | 游记、山水散文 |
| 剧本脚本 | 影视剧本场景 |
| 说明文字 | 建筑、园林、场景描述 |
| 新闻报道 | 场景描写段落 |

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

自动分析并提取：

1. **识别文本类型**
   - 古典文学：添加古典评语风格
   - 现代文学：添加现代评论风格
   - 说明文字：提取关键信息点
   - 剧本：提取场景和动作描述

2. **标记场景描写**（加粗 `**文字**`）
   - 环境描写：建筑、自然景观、室内陈设
   - 人物动作：与场景相关的活动
   - 氛围词：时间、天气、光影

3. **选取关键场景**
   - 最具画面感的段落
   - 场景描写完整
   - 适合文生图渲染
   - 数量：默认 2-3 个，可由用户指定

4. **添加注释/评语**（可选）
   - 古典文本：可添加古雅评语
   - 现代文本：可添加赏析注释
   - 说明文字：可添加解释说明

---

### Step 2.5: 场景视觉考据（必需）

生成图片前，必须确认视觉元素的正确性。

#### 缓存机制

**优先读取缓存，避免重复查证**：

```
~/.claude/skills/scene-img/
├── references/           # 通用历史资料
│   ├── dynasty-costume.md
│   └── dynasty-architecture.md
└── cache/                # 项目专项缓存
    └── {项目名}/
        └── visual-reference.md
```

**执行流程**：

1. **检查缓存**：`Read cache/{项目名}/visual-reference.md`
   - 存在 → 直接使用缓存内容
   - 不存在 → 执行查证流程 → 保存到缓存

2. **通用资料**：`Read references/dynasty-costume.md`（唐宋元明清速查）

3. **首次查证后保存**：
   ```markdown
   # {项目名} - 视觉参考缓存
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
mmx image generate --out-prefix {作品名}_ch{章节}_scene01 &
mmx image generate --out-prefix {作品名}_ch{章节}_scene02 &
mmx image generate --out-prefix {作品名}_ch{章节}_scene03 &

然后并行下载图片
```

**注意**：使用 `--out-prefix` 指定不同前缀避免冲突

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

**内容规则**：
1. **用原文翻译成现代文字，不要缩写**
   - ❌ "镜面白石题刻"（原文无"题刻"）
   - ✅ "一块镜面般的白色石头"
2. **数量精确，沿用原文数量**
   - 原文"一块" → 提示词"one piece", "single"
   - 原文"两行" → 提示词"two rows"
3. **不添加原图没有的内容**
   - 原文只说"白石" → 只写"white stone"，不加"题刻"、"刻字"
4. **不省略原文内容**
   - ❌ 省略"或垂山巅，或穿石隙"等原文细节
   - ✅ 完整翻译原文所有描述
   - 原文的排比、递进等修辞应保留

```
[时代背景 - 明确历史时期],
[景物描述 - 原文翻译成现代文字，保留数量],
[环境规模 - 指明是园林/院落/建筑内部],
[POV 视角 - 根据场景规模选择],
traditional Chinese ink painting aesthetic,
negative space, atmospheric perspective,
[背景控制 - 避免不符合原文的远景],
aspect ratio 16:9
```

**时代背景（必须）**：

| 文本类型 | 时代标注 |
|---------|---------|
| 古典小说（红楼梦） | `Qing dynasty`, `清代园林` |
| 古典小说（水浒传） | `Northern Song dynasty`, `北宋` |
| 古典小说（西游记） | `Tang dynasty`, `唐代` |
| 现代文本 | `modern era`, `当代` |
| 不确定 | 根据文本线索推断，或询问用户 |

**时代背景示例**：
```
清代园林建筑，单层房舍，传统木结构窗棂，
Qing dynasty Chinese architecture,
single-story building not multi-story,
traditional wooden lattice windows not modern glass
```

**环境规模描述（必须）**：

| 场景类型 | 必须添加 |
|---------|---------|
| 园林建筑 | `within garden walls`, `enclosed courtyard` |
| 院落 | `small courtyard`, `walled garden` |
| 建筑内部 | `interior view`, `inside building` |
| 室外街景 | `city street`, `market scene` |

**POV 视角选择**：

| 场景规模 | POV | 英文术语 |
|---------|-----|---------|
| 小场景（院落、建筑局部） | 平视/仰视 | `eye-level view`, `low angle view` |
| 中场景（园林、建筑群） | 平视/略俯 | `medium shot`, `slightly elevated` |
| 大场景（全景、山水） | 俯瞰 | `aerial view`, `bird's eye view` |

**背景控制（必须）**：

| 原文环境 | 背景处理 |
|---------|---------|
| 园林/院落内部 | `no distant mountains`, `walled enclosure` |
| 建筑群 | `fill frame`, `background blurred` |
| 室内 | `interior setting`, `no outdoor view` |

**尺度参照（避免歧义）**：

| 中文 | 易误解 | 修正 |
|------|--------|------|
| 假山 | 真山/微缩模型 | `life-sized rockery not miniature`, `rocks as tall as human` |
| 楼 | 高楼 | `two-story pavilion`, `low building` |
| 池 | 湖泊 | `small pond`, `courtyard pool` |

**尺度参照技巧**：
- 添加人物作为参照：`small figure for scale`
- 明确实际大小：`life-sized not miniature`, `human-scale`
- 具体尺寸：`高度约三米`, `two meters tall`

**示例（中文小说）**：
```
武僧背影，戴圆锥形竹斗笠，手持禅杖，
雪景古道（人行尺度），天色阴沉，
eye-level view, no distant mountains,
traditional Chinese ink painting style,
vast negative space
```

**英文术语速查**：
| 类别 | 英文术语 |
|------|---------|
| 构图 | `wide shot`, `medium shot`, `aerial view` |
| 光影 | `rim lighting`, `soft lighting`, `dramatic lighting` |
| 氛围 | `atmospheric`, `misty`, `ethereal` |
| 风格 | `ink painting style`, `negative space`, `monochrome` |
| 视角 | `back view`, `silhouette`, `figure in distance` |

#### 提示词技巧

**提示词公式**：
```
提示词 = 主体(主体描述) + 场景(场景描述) + 风格 + 镜头语言 + 质量修饰
```

**核心技巧表**：

| 技巧 | 说明 | 错误示例 | 正确示例 |
|------|------|----------|----------|
| **具体化** | 避免模糊词 | ❌ "大房子" | ✅ "两层木结构房屋" |
| **数量精确** | 用数字限定 | ❌ "白石" | ✅ "一块镜面白石" |
| **尺度参照** | 添加对比物 | ❌ "假山" | ✅ "life-sized rockery, figure for scale" |
| **环境限定** | 防止场景溢出 | ❌ "园林" | ✅ "within garden walls, enclosed courtyard" |
| **背景控制** | 避免不符合远景 | ❌ "亭子" | ✅ "no distant mountains, fill frame" |
| **POV 明确** | 根据场景选择 | ❌ 默认鸟瞰 | ✅ "eye-level view"（小场景） |

**负向提示词（避免生成）**：
```
no text, no watermark, no signature, no frame,
no distant mountains (园林内场景),
not miniature (假山/建筑)
```

**常见问题与解决**：

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 像微缩模型 | 缺少尺度参照 | + `life-sized`, `figure for scale` |
| 背景太宏大 | 未限制环境 | + `within garden walls`, `no distant mountains` |
| 数量错误 | 未指定数量 | + `one`, `single`, `two rows` |
| 添加了原文没有的内容 | 过度推演 | 只写原文明确提及的内容 |

**命令**：
```bash
mmx image generate --prompt "..." --aspect-ratio 16:9 --out-dir ./assets --out-prefix honglou_ch17_scene08
```

#### 音乐生成（默认不生成）

音乐生成默认跳过，仅当用户明确要求时执行。

**触发条件**：用户提及"配乐"、"背景音乐"、"BGM"

**Prompt 模板**：

**核心原则：内容语言与输入文件一致 + 细节术语用英文**

```
Traditional Chinese instrumental,
[场景氛围描述 - 与输入语言相同],
[乐器名称], brief atmospheric, cinematic ambient
```

**示例（中文场景）**：
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
mmx music generate --model music-2.6 --prompt "..." --instrumental --out ./assets/honglou_ch17_scene01_bgm.mp3
```

**注意**：音乐生成仅当用户明确要求时执行。

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

<img src="assets/honglou_ch17_scene01.jpg" ...>

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

**文件命名规范**：

```
图片：{作品名}_ch{章节}_scene{场景号}.jpg
提示词：{作品名}_ch{章节}_prompts.md
音乐（可选）：{作品名}_ch{章节}_scene{场景号}_bgm.mp3

示例：
- honglou_ch17_scene01.jpg
- honglou_ch17_prompts.md
- honglou_ch17_scene01_bgm.mp3（仅当用户要求配乐时生成）
```

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
缓存文件：`~/.claude/skills/scene-img/cache/{项目名}/visual-reference.md`
```

---

## 注释/评语模板（可选）

根据文本类型选择：

### 古典文学（金圣叹风格）

| 特征 | 示例 |
|------|------|
| 一字评 | "\"紧\"字第一见。有势将来之意。" |
| 对照法 | "\"抬举\"二字，对照前文。" |

### 现代文学

| 特征 | 示例 |
|------|------|
| 氛围描写 | "这段通过光影变化渲染氛围" |
| 细节点睛 | "\"转身\"一词写出心理转变" |

### 说明文字

| 特征 | 示例 |
|------|------|
| 结构说明 | "此处为建筑入口，采用..." |
| 特色标注 | "核心特征：对称布局" |

---

## 执行检查清单

生成前：
- [ ] 内容获取成功
- [ ] 标题正确提取
- [ ] 结构清晰

生成中：
- [ ] 场景描写识别完成
- [ ] 视觉元素考据（时代/环境/器物）
- [ ] 关键场景选取
- [ ] 图片 prompt 使用正确关键词
- [ ] 图片 prompt 遵守规则（数量精确、尺度参照、环境限定）

生成后：
- [ ] Markdown 格式正确
- [ ] 图片路径正确
- [ ] 音频路径正确

---

## 示例调用

### 示例一：古典小说
```
用户: /scene-img https://www.guwendao.net/guwen/shuihu_10.aspx

Claude 执行:
1. WebFetch 获取内容
2. 分析：提取标题"林教头风雪山神庙"
3. 识别关键场景：沽酒雪行、山神庙夜宿
4. Step 2.5 视觉考据：
   - 时代：北宋
   - 服饰：原文"毡笠"→ "cone-shaped douli"
   - 器物：原文"花枪"、"酒葫芦"
5. 生成图片 x2
6. 构建 Markdown → 输出：shuihu_chapter10.md
```

### 示例二：现代散文
```
用户: /scene-img "./游记.md"

Claude 执行:
1. Read 读取本地文件
2. 分析：识别场景描写段落
3. 提取关键场景：山间小路、湖畔黄昏
4. 生成图片 x2
5. 构建 Markdown → 输出：游记_配图版.md
```

### 示例三：剧本场景
```
用户: /scene-img "剧本第5场：咖啡馆内景，落地窗外下着雨..."

Claude 执行:
1. 直接分析用户提供的文本
2. 识别场景：咖啡馆、雨天、落地窗
3. 生成图片 x1
4. 输出 Markdown片段
```

---

## 依赖

- mmx CLI (MiniMax API)
- WebFetch / Read / MCP 工具
- `.claude/rules/novel-illustration.md`（文生图规则）

---

## 缓存目录

```
~/.claude/skills/scene-img/
├── SKILL.md
├── references/           # 通用历史资料
│   ├── dynasty-costume.md
│   └── dynasty-architecture.md
└── cache/                # 项目专项缓存
    └── {项目名}/
        └── visual-reference.md
```
