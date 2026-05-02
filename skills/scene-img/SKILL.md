---
name: scene-img
version: 3.1.0
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

3. **【新增】元素约束表**

   对每个关键场景，生成约束清单：

   | 类别 | 说明 | 示例 |
   |------|------|------|
   | ✅ 必须有 | 原文明确提及，不可省略 | "千百竿翠竹" |
   | ⚠️ 模糊处理 | 原文未细述，用通称 | "游廊" → "传统游廊" |
   | ❌ 禁止有 | 原文未提及，不应出现 | "紫色花（原文无）" |

   **生成规则**：
   - 原文明确描述的元素 → 标记 ✅ 必须有
   - 原文模糊描述 → 标记 ⚠️ 模糊处理
   - 原文未提及 → 标记 ❌ 禁止有

4. **【新增】核心视觉符号**

   每个场景提取 1-3 个标志性符号：

   | 场景 | 核心符号 | 来源依据 |
   |------|----------|----------|
   | 潇湘馆 | 翠竹千百竿 | 人物性格象征 |
   | 蘅芜苑 | 假山遮屋、异草 | 冷雅氛围关键 |
   | 稻香村 | 杏花如霞、茅屋 | 田园反差感 |

   **提取原则**：
   - 选择读者印象最深的元素
   - 与人物/主题相关联
   - 具有视觉辨识度

5. **选取关键场景**
   - 最具画面感的段落
   - 场景描写完整
   - 适合文生图渲染
   - 数量：默认 2-3 个，可由用户指定

6. **添加注释/评语**（可选）
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
│   ├── dynasty-architecture.md
│   ├── imagery-mapping.md    # 【新增】古文意象映射
│   └── scene-templates.md     # 【新增】场景类型模板
└── cache/                # 项目专项缓存
    └── {项目名}/
        └── visual-reference.md
```

**执行流程**：

1. **检查缓存**：`Read cache/{项目名}/visual-reference.md`
   - 存在 → 直接使用缓存内容
   - 不存在 → 执行查证流程 → 保存到缓存

2. **通用资料**：
   - `Read references/dynasty-costume.md`（朝代服饰）
   - `Read references/dynasty-architecture.md`（朝代建筑）
   - `Read references/imagery-mapping.md`（古文意象映射）
   - `Read references/scene-templates.md`（场景类型模板）

3. **首次查证后保存**：
   ```markdown
   # {项目名} - 视觉参考缓存
   > {朝代} 服饰、器物、建筑参考
   **缓存创建时间**：{日期}
   ```

#### 【新增】古文意象→视觉映射

阅读 `references/imagery-mapping.md`，查找对应意象：

| 古文意象 | 视觉关键词 | 常见误解 |
|----------|-----------|----------|
| 白石崚嶒 | gray-white limestone rocks, jagged texture | ❌ 洞穴入口 |
| 翠竹千百竿 | thousands of emerald bamboo, bamboo grove focus | ❌ 普通植物 |
| 异草藤蔓 | exotic vines and herbs, no flowers | ❌ 花园花卉 |

**使用原则**：
- 古文意象优先转换为英文视觉术语
- 避免常见误解
- 保持原文修辞意境

#### 【新增】场景类型模板

阅读 `references/scene-templates.md`，匹配场景类型：

| 场景类型 | 氛围关键词 | 必须元素 | 禁止元素 |
|----------|-----------|----------|----------|
| 文人宅院 | serene, scholarly | 书卷气、简洁陈设 | 金碧辉煌 |
| 贵族园林 | ornate, traditional | 精致、对称 | 现代玻璃窗 |
| 田园茅舍 | rustic, pastoral | 朴素、自然 | 精雕细琢 |

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

   **建筑规模约束（关键）**：

   | 建筑类型 | 规模限制 | Prompt 关键词 |
   |----------|----------|--------------|
   | 民居 | 单层，三五开间 | `humble`, `modest`, `simple dwelling` |
   | 官员宅第 | 单层，三五开间 | `official residence`, `single-story` |
   | 贵族园林 | 单层为主，偶有阁楼 | `noble garden`, `elegant not grandiose` |
   | 王府 | 单层为主，七开间 | `prince mansion`, `grand but not palace` |
   | 皇家宫殿 | 多层，宏大 | `imperial palace`, `grand palace` |

   **常见误解与修正**：

   | 误解 | 原因 | 修正 |
   |------|------|------|
   | 贵族园林 → 皇宫 | 过度渲染宏大 | `private garden`, `not imperial scale`, `noble family estate` |
   | 正殿 → 大殿 | 理解偏差 | `main hall of garden`, `reception pavilion`, `not throne hall` |
   | 园林 → 皇家御苑 | 园林无明确规模 | `private noble garden`, `family estate`, `not public park` |

   **建筑规模判定原则**：

   | 原文线索 | 判定 | Prompt 关键词 |
   |----------|------|--------------|
   | "省亲别墅"/"贵妃" | 贵族园林（非皇宫） | `noble family villa`, `garden for family visit` |
   | "府"/"宅"/"园" | 私人宅邸 | `private residence`, `family compound` |
   | "宫"/"殿"（皇家用词） | 可能是皇家 | 需结合上下文 |
   | 原文无"皇家"/"御" | 默认私人规模 | `private scale`, `not imperial` |

   **大观园规模参考**：
   - 贾府为侯爵府（贵族，非皇族）
   - 大观园是为"贵妃省亲"建的私人园林
   - "正殿"是园内主体建筑，非皇宫大殿
   - Prompt 用：`main hall within private garden`, `reception pavilion`, `grand but not imperial`

   **建筑规模约束模板**：

   ```
   【规模约束模块】（贵族园林）
   private noble garden,
   not imperial palace,
   family estate scale,
   grand but not royal scale,
   elegant architecture not overwhelming,
   ```

   | 元素 | 限制 | Prompt 关键词 |
   |------|------|--------------|
   | 楼层数 | 民用 1-2 层 | `single-story`, `low`, `modest` |
   | 塔楼 | 罕见，原文未提则不出现 | 避免 `tower`, `pagoda` |
   | 庙宇 | 小型土地庙/山神庙 | `small shrine`, `humble temple` |

6. **【新增】背景约束规则（关键）**

   **问题根源**：AI 易混淆"封闭空间"与"开放空间"，导致背景溢出。

   **场景类型与背景处理**：

   | 场景类型 | 空间性质 | 背景处理 | Prompt 关键词 |
   |----------|----------|----------|--------------|
   | **庭院/院落** | 封闭 | 围墙边界，无远景 | `enclosed courtyard`, `within walls`, `no distant view` |
   | **园林内部** | 封闭 | 园墙边界，无远山 | `within garden walls`, `no distant mountains` |
   | **室内** | 封闭 | 墙壁边界 | `interior`, `no outdoor view` |
   | **城市街巷** | 半封闭 | 建筑边界 | `city street`, `buildings on both sides` |
   | **自然山水** | 开放 | 允许远山 | `distant mountains`, `natural landscape` |
   | **田野乡村** | 开放 | 允许远景 | `open countryside`, `distant hills` |

   **"山"类元素区分（关键）**：

   | 原文用词类型 | 实指 | Prompt 关键词 |
   |----------|------|--------------|
   | 假山、怪石、山石 | 人造假山（园林内） | `artificial rockery`, `garden rocks`, `within enclosed space` |
   | 坡、丘、阜 | 土坡/小丘（可能是园林内） | `earthen slope`, `small hill`，需判断空间 |
   | 远山、群山 | 自然远山（开放空间） | `distant mountains`, `natural hills` |
   | 岳、峰 | 大山（自然场景） | `mountain peak`, `natural mountain` |

   **判断原则**：
   - 看原文是否提及"墙"、"院"、"园"、"门"等边界词
   - 园林/庭院内的"山"多为假山
   - 原文有"出园"、"远望"、"登高"等词才可能有真山远景

   **封闭空间背景模板**：

   ```
   【背景约束模块】（封闭空间必须包含）
   within enclosed walls,
   no distant mountains, no distant landscape,
   boundary visible (wall/fence/building),
   enclosed setting,
   ```

7. **【新增】植物造型约束（关键）**

   **问题根源**：AI 易生成西方式修剪灌木，不符合东方自然美学。

   **园艺风格区分**：

   | 风格 | 特征 | Prompt 关键词 |
   |------|------|--------------|
   | **中国传统园林** | 自然形态，不修剪 | `natural untrimmed`, `plants growing freely` |
   | **西方古典园林** | 几何修剪，整齐对称 | `formal garden`, `manicured hedges`（仅西方题材） |
   | **日本庭园** | 选型修剪，禅意 | `Japanese garden`, `carefully shaped`（仅日本题材） |
   | **现代园艺** | 修剪整齐 | `modern garden`, `manicured lawn`（仅现代题材） |

   **中国古典题材禁止元素**：

   | 元素 | 说明 | 负面关键词 |
   |------|------|-----------|
   | 几何灌木 | 方形/球形/锥形造型 | `no geometric hedges`, `no topiary` |
   | 修剪绿篱 | 直线排列的灌木墙 | `no manicured hedges`, `no trimmed hedge wall` |
   | 现代草坪 | 修剪整齐的草地 | `no manicured lawn` |
   | 对称花坛 | 几何图案花坛 | `no geometric flower beds` |

   **农业场景 vs 观赏园艺区分**：

   | 类型 | 特征 | Prompt 关键词 |
   |------|------|--------------|
   | 菜畦/农田 | 土地划分，种植作物 | `farm fields`, `vegetable plots`, `divided by furrows` |
   | 果园 | 果树排列，自然形态 | `fruit trees`, `orchard natural form` |
   | 绿篱/篱笆 | 天然材料编织 | `woven fence`, `natural branch fence` |
   | 修剪灌木 | 观赏用几何造型 | ❌ 禁止于中国古典题材 |

   **植物造型约束模板**：

   ```
   【植物约束模块】（中国传统园林/古典文学）
   natural untrimmed plants,
   no geometric hedges, no topiary,
   no manicured garden design,
   plants growing in natural forms,
   woven fence if needed, not trimmed hedge,
   ```

   **特殊场景例外**：
   - 现代题材可使用 `manicured garden`
   - 西方古典题材可使用 `formal French garden`, `topiary`
   - 日本题材使用 `Japanese garden style`（有特定修剪风格）

   **错误示例 vs 正确示例**：

   | ❌ 错误 | ✅ 正确 |
   |---------|---------|
   | `enclosed by hills` | `enclosed by garden walls` |
   | `sloped hillside` | `garden hillside within walls` |
   | （未说明是园内） | `within noble garden, not wild countryside` |

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

#### 【新增】生成前 Prompt 检查

每次生成前，对照元素约束表检查：

```
Prompt 检查清单：
□ 必须元素是否全部包含？
□ 禁止元素是否已排除？
□ 核心视觉符号是否突出？
□ 数量是否精确（one, two, thousands）？
□ 不确定元素是否模糊处理？
□ 古文意象是否正确转换？
□ 背景约束是否正确？
  - 封闭空间：within walls, no distant view
  - 园林内假山：courtyard rockery, not wild landscape
□ 植物造型是否正确？
  - 中国古典：no geometric hedges, no topiary
  - 菜畦因农田划分，非修剪灌木
□ 【新增】建筑规模是否正确？
  - 贵族园林：private scale, not imperial
  - 园林正殿：main hall within garden, not throne hall
```

#### 【新增】Prompt 结构化模板

```
【必须元素模块】（强制包含）
{核心符号}, {必须元素},

【原文描述模块】
{原文翻译，保留修辞和数量},

【负面约束模块】（强制排除）
no {禁止元素1}, no {禁止元素2},
no flowers (if not mentioned),

【背景约束模块】（重要！）
园林内：within enclosed garden walls, no distant mountains
园内山石：garden rockery not natural mountain
园内田园：garden farm plot not countryside

【风格模块】
{时代背景}, {氛围关键词}, {POV视角}
```

#### Prompt 模板

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
【时代背景】{明确历史时期},
【景物描述】{原文翻译成现代文字，保留数量},
【核心符号】{核心视觉符号，作为焦点},
【环境规模】{指明是园林/院落/建筑内部},
【负面约束】{排除原文未提及元素},
【POV 视角】{根据场景规模选择},
traditional Chinese ink painting aesthetic,
negative space, atmospheric perspective,
aspect ratio 16:9
```

**示例：潇湘馆（改进后）**

```
【必须元素模块】
thousands of emerald bamboo screening buildings,
bamboo grove as main visual focus,

【原文描述模块】
清代文人宅院，单层房舍非多层，
千百竿翠竹遮映数间正房，竹影婆娑，
曲折游廊穿行竹林间，
后院一株大梨花和芭蕉相映，
窄沟引泉绕竹基流过，

【负面约束模块】
no colorful garden flowers,
no ornate decorations,
no modern elements,

【风格模块】
Qing dynasty scholar courtyard,
single-story buildings,
traditional wooden lattice windows,
serene atmosphere, soft lighting,
eye-level view, enclosed courtyard
```

#### 并行执行（推荐）

MiniMax API 支持并行调用，可显著提升效率：

```
单次响应中同时调用：
mmx image generate --out-prefix {作品名}_ch{章节}_{场景名1} &
mmx image generate --out-prefix {作品名}_ch{章节}_{场景名2} &
mmx image generate --out-prefix {作品名}_ch{章节}_{场景名3} &

示例：
mmx image generate --out-prefix honglou_ch17_xiaoxiang &
mmx image generate --out-prefix honglou_ch17_daoxiang &
mmx image generate --out-prefix honglou_ch17_hengwu &

然后并行下载图片
```

**注意**：使用 `--out-prefix` 指定不同场景名称，避免冲突

**效率对比**：
| 执行方式 | 耗时 |
|----------|------|
| 串行 | ~100+ 秒 |
| 并行 | ~60 秒 |

#### 图片生成规则

遵循 `.claude/rules/novel-illustration.md` 规则：

**核心规则**：
- 人物不正面（背影/侧影/剪影/远景小人物）
- 不确定场景模糊处理（建筑楼层、具体数量）
- 视角远近分开（远景 > 中景 > 近景）
- 东方美学留白

**时代背景（必须）**：

| 文本类型 | 时代标注 |
|---------|---------|
| 古典小说（红楼梦） | `Qing dynasty`, `清代园林` |
| 古典小说（水浒传） | `Northern Song dynasty`, `北宋` |
| 古典小说（西游记） | `Tang dynasty`, `唐代` |
| 现代文本 | `modern era`, `当代` |
| 不确定 | 根据文本线索推断，或询问用户 |

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

**英文术语速查**：
| 类别 | 英文术语 |
|------|---------|
| 构图 | `wide shot`, `medium shot`, `aerial view` |
| 光影 | `rim lighting`, `soft lighting`, `dramatic lighting` |
| 氛围 | `atmospheric`, `misty`, `ethereal` |
| 风格 | `ink painting style`, `negative space`, `monochrome` |
| 视角 | `back view`, `silhouette`, `figure in distance` |

#### 音乐生成（默认不生成）

音乐生成默认跳过，仅当用户明确要求时执行。

**触发条件**：用户提及"配乐"、"背景音乐"、"BGM"

**命令**：
```bash
mmx music generate --model music-2.6 --prompt "..." --instrumental --out ./assets/xxx_bgm.mp3
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

---

### Step 5: 输出文件

**保存 Markdown**：`{作品名}_{章节}.md`（Chrome 可直接打开，支持音频播放）

**保存提示词**：`assets/{作品名}_{章节}_prompts.md`（便于回测和复用，与正文同名）

**【新增】提示词文件包含约束验证**：

```markdown
# 生成提示词记录

> 日期：{日期}
> 章节：{章节名}

---

## 场景一：{场景名}

### 元素约束表

| 类别 | 元素 | 来源 |
|------|------|------|
| ✅ 必须有 | {元素1} | 原文明确 |
| ✅ 必须有 | {元素2} | 原文明确 |
| ⚠️ 模糊处理 | {元素3} | 原文未细述 |
| ❌ 禁止有 | {元素4} | 原文未提及 |

### 核心视觉符号

{符号1}, {符号2}, {符号3}

### Prompt

```
{完整 prompt}
```

### 约束检查

| 检查项 | 状态 |
|--------|------|
| 核心元素包含 | ✅/⚠️ |
| 禁止元素排除 | ✅/⚠️ |
| 数量精确 | ✅/⚠️ |
| 意象正确 | ✅/⚠️ |

---

## 视觉考据来源

缓存文件：`~/.claude/skills/scene-img/cache/{项目名}/visual-reference.md`
```

**文件命名规范**：

```
图片：{作品名}_ch{章节}_{场景名}.jpg
提示词：{作品名}_ch{章节}_prompts.md
音乐（可选）：{作品名}_ch{章节}_{场景名}_bgm.mp3

示例：
- honglou_ch17_xiaoxiang.jpg（潇湘馆）
- honglou_ch17_daoxiang.jpg（稻香村）
- honglou_ch17_prompts.md
- honglou_ch17_xiaoxiang_bgm.mp3
```

**命名规则**：
- **无版本后缀**：不使用 `_v2`、`_v3`、`_001` 等版本标记
- **用场景名代替序号**：`_xiaoxiang` 比 `_scene01` 更易识别
- **改进覆盖**：优化 Prompt 后重新生成同名图片，覆盖旧图
- **Markdown 引用稳定**：`![图片](assets/honglou_ch17_xiaoxiang.jpg)` 无需修改

**生成命令示例**：

```bash
# 使用 --out-prefix 指定无版本号的名称
mmx image generate --prompt "..." --out-prefix honglou_ch17_xiaoxiang

# 改进后重新生成，同名覆盖
mmx image generate --prompt "优化后的prompt" --out-prefix honglou_ch17_xiaoxiang
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

---

## 执行检查清单

生成前：
- [ ] 内容获取成功
- [ ] 标题正确提取
- [ ] 结构清晰
- [ ] 元素约束表生成
- [ ] 核心视觉符号提取

生成中：
- [ ] 场景描写识别完成
- [ ] 视觉元素考据（时代/环境/器物）
- [ ] 古文意象映射
- [ ] 场景类型匹配
- [ ] Prompt 检查清单通过
- [ ] 图片 prompt 使用正确关键词

生成后：
- [ ] Markdown 格式正确
- [ ] 图片路径正确
- [ ] 提示词文件包含约束验证

---

## 示例调用

### 示例一：古典小说
```
用户: /scene-img https://www.guwendao.net/guwen/shuihu_10.aspx

Claude 执行:
1. WebFetch 获取内容
2. 分析：提取标题"林教头风雪山神庙"
3. 生成元素约束表：
   - ✅ 花枪、酒葫芦（原文明确）
   - ❌ 其他武器（原文未提及）
4. 提取核心视觉符号：背影、雪景、古庙
5. Step 2.5 视觉考据：
   - 查询 imagery-mapping.md："毡笠"→"cone-shaped douli"
6. Prompt 检查清单通过
7. 生成图片 x2
8. 输出：shuihu_chapter10.md + shuihu_chapter10_prompts.md
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
│   ├── dynasty-architecture.md
│   ├── imagery-mapping.md    # 【新增】古文意象映射
│   └── scene-templates.md     # 【新增】场景类型模板
└── cache/                # 项目专项缓存
    └── {项目名}/
        └── visual-reference.md
```
