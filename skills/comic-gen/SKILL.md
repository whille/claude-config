---
name: comic-gen
version: 1.1.0
description: 小说转漫画工作流 - 将小说章节转换为分镜脚本并生成漫画图片
user-invocable: true
argument-hint: "<URL或本地路径或文本>"
triggers:
  - "小说转漫画"
  - "分镜脚本"
  - "漫画生成"
  - "comic"
last_updated: 2026-05-04
---

# comic-gen: 小说转漫画工作流

将小说章节拆解为分镜脚本，生成每帧图片，输出完整的漫画式 Markdown 文档。

适用于：古典小说、现代小说、剧本、故事文本。

---

## 触发条件

用户提到：`小说转漫画`、`分镜脚本`、`漫画生成`、`/comic-gen`，或提供小说文本要求转换为漫画。

---

## 工作流程

### Step 1: 获取内容

根据用户输入类型选择工具：

| 输入类型 | 工具 |
|----------|------|
| URL (http/https) | WebFetch 抓取 |
| WPS 文档 (365.kdocs.cn) | mcp__ksc-local-mcp__get_wps_content |
| 本地路径 (.md/.txt) | Read 读取 |

---

### Step 2: 分析内容

自动分析并提取：

1. **识别作品和章节**
   - 提取作品名、章节号、回目
   - 识别时代背景（唐/宋/明/清/现代）

2. **提取主要人物**
   - 识别出场人物
   - 读取角色库 `_shared/characters/{作品}.json`
   - 获取人物视觉关键词

3. **拆解情节点**
   - 识别关键事件
   - 标记对话和动作
   - 划分场景变化

4. **生成元素约束表**
   - 必须元素：原文明确提及
   - 禁止元素：原文未提及

---

### Step 2.5: 视觉考据（必需）

**引用公共模块**：

```
~/.claude/skills/_shared/
├── dynasty/
│   ├── architecture.md   # 建筑风格
│   ├── costume.md        # 服饰特点
│   └── props.md          # 器物参考
├── imagery/
│   └── mapping.md        # 古文意象映射
├── scene/
│   └── templates.md      # 场景类型模板
└── characters/
    └── {作品}.json       # 角色库
```

**执行流程**：

1. 读取 `dynasty/architecture.md` 确认建筑风格
2. 读取 `dynasty/costume.md` 确认服饰特点
3. 读取 `dynasty/props.md` 确认器物
4. 读取 `imagery/mapping.md` 转换古文意象
5. 读取 `scene/templates.md` 匹配场景类型
6. 读取 `characters/{作品}.json` 获取角色描述

---

### Step 2.6: 角色基准与风格设定（必需）

**目的**：建立角色一致性和风格一致性约束

**引用模块**：

```
~/.claude/skills/comic-gen/modules/
├── character-reference.md   # 角色基准描述
├── style-consistency.md     # 风格一致性策略
└── camera-movement.md       # 运镜控制
```

**执行流程**：

1. **提取角色基准描述**
   - 读取 `_shared/characters/{作品}.json`
   - 提取每个角色的 `base_prompt`、`anchor_words`、`forbidden`
   - 根据场景情绪选择 `variants`

2. **设定风格种子词**
   - 作品级固定风格前缀（50 字符）
   - 统一负面提示词
   - 确定画幅比例

3. **确定运镜方案**
   - 根据场景类型选择运镜
   - 情绪场景 → 推镜头/静态
   - 动作场景 → 跟随/摇晃
   - 对话场景 → 静态/切换

**输出**：
- 角色基准描述表
- 风格种子词
- 运镜方案

---

### Step 3: 生成分镜脚本

**引用独有模块**：

```
~/.claude/skills/comic-gen/modules/
├── expression-mapping.md  # 表情映射
├── action-mapping.md      # 动作映射
└── transition-rules.md    # 转场规则
```

---

## ⚠️ 帧数估算规则（重要）

**问题**：帧数过少会导致情节跳跃、叙事不完整。

**估算公式**：

| 情节类型 | 帧数估算 |
|----------|----------|
| 场景转换 | 1-2 帧（环境交代） |
| 人物出场 | 1-2 帧（引入+定位） |
| 对话 | 2-3 帧（说话+反应+回应） |
| 动作序列 | 3-5 帧（起势+过程+结果） |
| 情绪高潮 | 2-3 帧（铺垫+爆发+余韵） |
| 转场过渡 | 1 帧（空镜或环境） |

**总帧数估算**：

```
最小帧数 = 场景数 × 2 + 重要对话数 × 2 + 动作序列数 × 3
```

**经验值**：
- 短篇章节（< 2000 字）：15-20 帧
- 中篇章节（2000-4000 字）：20-30 帧
- 长篇章节（> 4000 字）：30-50 帧

**检查点**：分镜脚本生成后，确认帧数是否符合估算。如果帧数过少，检查是否遗漏情节点。

---

## ⚠️ 风格一致性策略（重要）

**问题**：每帧独立生成导致风格差异、人物变化。

### 解决方案

#### 1. 统一风格前缀（必须）

每帧 Prompt 必须以风格前缀开头：

```
【风格前缀模板】
{时代} {题材} {艺术风格},
ink wash painting aesthetic,
traditional Chinese art style,
soft brush strokes, elegant composition,
muted color palette, atmospheric perspective,
```

**示例**：
```
Qing dynasty noble garden, ink wash painting aesthetic,
traditional Chinese art style, soft brush strokes,
```

#### 2. 人物描述标准化（必须）

同一人物在所有帧中使用相同关键词：

```
【贾政标准化描述】
Jia Zheng, middle-aged official in dark formal robes,
stern posture, traditional Qing dynasty official attire,
figure shown from behind or side,

【宝玉标准化描述】
Jia Baoyu, young nobleman in red robes,
jade ornament at waist, about 15 years old,
figure shown from behind or side,
```

#### 3. 环境约束标准化（必须）

同一场景的所有帧使用相同环境关键词：

```
【大观园环境约束】
within enclosed garden walls,
no distant mountains, no distant landscape,
private noble garden scale, not imperial,
Qing dynasty architecture, spring daylight,
```

#### 4. 禁止元素列表（必须）

所有帧末尾添加：

```
no frontal faces, no detailed faces,
no Western elements, no modern elements,
```

### Prompt 模板结构

#### 中文模板（即梦推荐）

```
【完整 Prompt 模板】
{时代背景} {题材} {艺术风格}，
{景别}，{运镜}，
{场景描述}，
{人物描述}，
{动作描述}，
{表情描述}，
{氛围关键词}
```

**示例**：
```
清朝贵族园林，水墨画风格，中国传统艺术，
中景镜头，缓慢推进，
大观园竹林小径，春日花开，
贾宝玉，少年公子，红色锦袍，腰系玉佩，温润如玉，
缓步前行，侧耳倾听，
柔和光线，淡雅色调
```

#### 英文模板（MiniMax）

```
【完整 Prompt 模板】
{风格前缀（种子词）}
{景别}, {运镜},
{场景固定描述},
{角色基准描述（含锚定词）},
{动作描述（如有）},
{表情描述（如有）},
{环境约束},
no {负面提示词}
```

**示例**：
```
Qing dynasty noble garden, ink wash painting aesthetic,
traditional Chinese art style, soft brush strokes,
medium shot, slow camera push-in,
five-bay gate hall, barrel tiles, polished brick wall,
Jia Baoyu, young nobleman in red robes, jade ornament, gentle expression,
walking beside Jia Zheng, listening attentively,
within enclosed garden walls, spring daylight,
no modern, Western, photorealistic, anime,
```

---

**分镜生成流程**：

1. **拆解情节为帧**
   - 每个情节点 2-5 帧
   - 关键对话独立成帧
   - 动作序列多帧展示

2. **确定景别序列**
   - 参考 `transition-rules.md`
   - 全景→中景→近景 标准序列
   - 根据情绪调整节奏

3. **生成每帧描述**
   - 环境描述
   - 人物动作（引用 `action-mapping.md`）
   - 人物表情（引用 `expression-mapping.md`）
   - 对白（引用原文）

4. **生成 Prompt**
   - 结构化 Prompt 片段
   - 包含景别、环境、人物、动作、表情

---

### Step 4: 生成图片

**推荐工具**：即梦 CLI（火山方舟 API）

#### 方案一：即梦 CLI（推荐）

**首次配置**：

```bash
# 1. 安装依赖
pip install openai

# 2. 初始化配置
jimeng init
```

按照提示输入：
1. API Key（火山方舟控制台获取）
2. 推理接入点 ID（选择 Doubao-Seedream-3.0-t2i 模型）

**获取配置信息**：
1. 访问火山方舟控制台: https://console.volcengine.com/ark
2. API Key管理 → 创建 API Key
3. 在线推理 → 创建推理接入点 → 选择 `Doubao-Seedream-3.0-t2i`

**生成图片**：

```bash
# 单张生成
jimeng generate "林黛玉，病态美，潇湘馆竹林，水墨风格"

# 批量生成
cat > prompts.txt << EOF
林黛玉，潇湘馆，抚琴
林黛玉，潇湘馆，执笔写字
林黛玉，潇湘馆，倚窗远眺
EOF
jimeng batch prompts.txt -p hongloumeng_ch17
```

**优势**：
- 中国风理解最好
- 原生支持中文 Prompt
- 命令行批量生成
- 无水印输出

#### 方案二：即梦网页（备选）

如果不想配置 API，可以使用网页版：
- 访问 jimeng.jianying.com
- 手动生成图片

详细指南：参考 `modules/jimeng-guide.md`

#### 方案三：MiniMax API（备选）

```bash
mmx image generate --prompt "..." --out-prefix {作品名}_ch{章节}_frame{序号}
```

**工具对比**：

| 维度 | 即梦 CLI | 即梦网页 | MiniMax |
|------|----------|----------|---------|
| 中国风 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 角色一致性 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 批量效率 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 自动化 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**图片生成规则**：

- 人物不正面（背影/侧影/剪影）
- 东方美学留白
- 视角远近分开
- 时代背景准确

---

### Step 5: 构建输出

**输出文件**：

1. **分镜脚本**：`{作品名}_ch{章节}_script.md`
2. **漫画文档**：`{作品名}_ch{章节}_comic.md`
3. **图片文件**：`{作品名}_ch{章节}_frame{序号}.jpg`
4. **提示词记录**：`{作品名}_ch{章节}_prompts.md`

**漫画文档格式**：

```markdown
# {作品名} - 第 {N} 回

## 第 1 帧

![Frame 1](assets/xxx_frame1.jpg)

> {原文描述}

---

## 第 2 帧

...
```

---

## 模块引用速查

### 公共模块（_shared）

| 模块 | 路径 | 用途 |
|------|------|------|
| 建筑风格 | `_shared/dynasty/architecture.md` | 朝代建筑参考 |
| 服饰特点 | `_shared/dynasty/costume.md` | 朝代服饰参考 |
| 器物参考 | `_shared/dynasty/props.md` | 器物参考 |
| 意象映射 | `_shared/imagery/mapping.md` | 古文→英文术语 |
| 场景模板 | `_shared/scene/templates.md` | 场景类型模板 |
| 角色库 | `_shared/characters/{作品}.json` | 角色视觉描述 |

### 独有模块（comic-gen）

| 模块 | 路径 | 用途 |
|------|------|------|
| 表情映射 | `modules/expression-mapping.md` | 情绪→表情 Prompt |
| 动作映射 | `modules/action-mapping.md` | 动词→动作 Prompt |
| 转场规则 | `modules/transition-rules.md` | 镜头切换序列 |
| 分镜模板 | `templates/script-template.md` | 输出格式模板 |
| 角色基准 | `modules/character-reference.md` | 角色一致性描述 |
| 运镜控制 | `modules/camera-movement.md` | 运镜类型与映射 |
| 风格一致性 | `modules/style-consistency.md` | 作品级风格统一 |
| 智能分镜 | `modules/storyboard-enhancement.md` | 两阶段分镜机制 |
| 即梦指南 | `modules/jimeng-guide.md` | 即梦平台使用说明 |

---

## 与 scene-img 的区别

| 维度 | scene-img | comic-gen |
|------|-----------|-----------|
| 输出 | 单张图片 | 多帧漫画序列 |
| 重点 | 场景渲染 | 人物+动作+情节 |
| 人物 | 避免 | 必要（但含蓄） |
| 文本处理 | 提取场景 | 拆解情节 |
| 时长 | 单次 | 系列帧 |

---

## 执行检查清单

生成前：
- [ ] 内容获取成功
- [ ] 作品/章节识别正确
- [ ] 时代背景确认
- [ ] 角色库读取成功

生成中：
- [ ] 视觉考据完成
- [ ] 分镜脚本生成
- [ ] 景别序列合理
- [ ] 人物描述一致

生成后：
- [ ] 图片生成成功
- [ ] 文档格式正确
- [ ] 图片路径正确

---

## 依赖

### 图片生成工具（二选一）

| 工具 | 用途 | 访问方式 |
|------|------|----------|
| **即梦**（推荐） | 中国风、角色一致性 | jimeng.jianying.com |
| **MiniMax** | 批量生成、API 集成 | mmx CLI |

### 其他依赖

- WebFetch / Read / MCP 工具
- `_shared/` 公共模块
- `.claude/rules/novel-illustration.md`（文生图规则）

---

## 示例调用

```
用户: /comic-gen https://www.guwendao.net/guwen/shuihu_10.aspx

Claude 执行:
1. WebFetch 获取内容
2. 分析：水浒传第10回"林教头风雪山神庙"
3. Step 2.5 视觉考据：
   - 读取 dynasty/architecture.md → 北宋建筑
   - 读取 dynasty/costume.md → 北宋服饰
   - 读取 characters/shuihu.json → 林冲角色描述
4. Step 3 生成分镜脚本：
   - 帧数估算：中篇章节（约3000字）→ 20-30帧
   - 场景：草料场、山神庙、古庙内
   - 动作：杀敌、放火、奔逃
   - 拆解为 25 帧
   - 确定景别序列
   - 生成每帧 Prompt（中文和英文两版）
5. Step 4 图片生成：
   【即梦方案】
   - 复制中文 Prompt 到即梦
   - 生成首图，开启角色一致性
   - 批量生成后续帧
   - 下载整理到项目目录

   【MiniMax 方案】
   - 使用英文 Prompt
   - mmx 批量生成 25 张图片
6. 输出：shuihu_ch10_script.md + shuihu_ch10_comic.md + 25 张图片
```

**红楼梦第十七回示例**（实际执行）：

```
用户: /comic-gen https://www.guwendao.net/guwen/bookv_2b8e16a52cf2.aspx

Claude 执行:
1. WebFetch 获取内容 → 红楼梦第17回"大观园试才题对额"
2. 分析：长篇章节（约6000字），10个场景单元
3. 帧数估算：
   - 场景数 10 × 2 = 20 帧
   - 重要对话 8 × 2 = 16 帧
   - 动作序列 3 × 3 = 9 帧
   - 最小帧数 ≈ 25-30 帧
4. 生成 28 帧分镜脚本
5. 生成中文 Prompt（即梦）和英文 Prompt（MiniMax）两版：
   【中文版示例】
   "清朝贵族园林，水墨画风格，中国传统艺术，
    中景镜头，大观园入口，春日，
    贾政，中年官员，深色官服，严肃表情，
    贾宝玉跟随，红色锦袍，温润如玉"

   【英文版示例】
   "Qing dynasty noble garden, ink wash painting aesthetic,
    traditional Chinese art style, soft brush strokes,
    medium shot, slow camera push-in,
    five-bay gate hall, barrel tiles, polished brick wall,
    Jia Baoyu, young nobleman in red robes, jade ornament..."
6. 图片生成（二选一）：
   - 即梦：手动生成，角色一致性 70%+
   - MiniMax：批量生成，角色一致性 50%
```
