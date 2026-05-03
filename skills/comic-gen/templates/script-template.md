# 分镜脚本模板

> 小说转漫画的标准输出格式

---

## 基本信息

```markdown
# {作品名} - 第 {N} 回

> 分镜脚本

**回目**：{原文回目}
**主要人物**：{人物列表}
**场景**：{主要场景}
**氛围**：{整体氛围}
```

---

## 分镜脚本格式

```markdown
---

## 第 1 帧

### 信息

| 项目 | 内容 |
|------|------|
| 景别 | 全景 |
| 内容 | {画面描述} |
| 人物 | {出现人物} |
| 动作 | {人物动作} |
| 表情 | {人物表情} |
| 对白 | "{原文对白}" |
| 转场 | 硬切 |
| 时长 | 中 |

### Prompt

```
{景别英文},
{环境描述},
{人物描述},
{动作描述},
{表情描述},
{时代背景},
{氛围关键词},
{负面约束}
```

---

## 第 2 帧

...
```

---

## 模板示例

```markdown
# 水浒传 - 第 10 回

> 分镜脚本

**回目**：林教头风雪山神庙
**主要人物**：林冲
**场景**：山神庙、草料场
**氛围**：悲壮、紧张

---

## 第 1 帧

### 信息

| 项目 | 内容 |
|------|------|
| 景别 | 全景 |
| 内容 | 雪夜，破旧山神庙，风雪交加 |
| 人物 | 无（环境镜头） |
| 动作 | - |
| 表情 | - |
| 对白 | - |
| 转场 | 硬切 |
| 时长 | 长 |

### Prompt

```
wide shot,
Northern Song dynasty,
winter night, heavy snowfall,
small dilapidated shrine in snowstorm,
weathered wooden temple,
thick snow covering everything,
howling wind, swirling snowflakes,
desolate atmosphere,
traditional Chinese ink painting style,
aspect ratio 16:9
```

---

## 第 2 帧

### 信息

| 项目 | 内容 |
|------|------|
| 景别 | 中景 |
| 内容 | 林冲提着花枪，走向山神庙 |
| 人物 | 林冲 |
| 动作 | 行走，持枪 |
| 表情 | 沉重，警惕 |
| 对白 | - |
| 转场 | 硬切 |
| 时长 | 中 |

### Prompt

```
medium shot,
Lin Chong from Water Margin,
middle-aged man, weathered face,
cone-shaped douli (bamboo hat),
heavy winter robes,
carrying spear with tassel (spear with decorative shaft),
walking through snow,
alert expression, determined stance,
Northern Song dynasty military attire,
snowstorm environment,
traditional Chinese style,
aspect ratio 16:9
```

---

## 第 3 帧

### 信息

| 项目 | 内容 |
|------|------|
| 景别 | 近景 |
| 内容 | 林冲推开庙门 |
| 人物 | 林冲 |
| 动作 | 推门 |
| 表情 | 警惕，疲惫 |
| 对白 | - |
| 转场 | 硬切 |
| 时长 | 短 |

### Prompt

```
close-up shot,
Lin Chong pushing wooden door,
weathered hands gripping door frame,
alert eyes, tired expression,
snow on shoulders and hat,
dim interior visible through crack,
tension in posture,
Northern Song dynasty setting,
traditional Chinese style,
aspect ratio 16:9
```
```

---

## 输出文件命名

| 文件类型 | 命名规则 |
|----------|----------|
| 分镜脚本 | `{作品名}_ch{章节}_script.md` |
| 图片 | `{作品名}_ch{章节}_frame{序号}.jpg` |
| 提示词记录 | `{作品名}_ch{章节}_prompts.md` |

---

## 注意事项

1. **每帧独立生成**：确保每帧可以独立生成图片
2. **人物一致性**：使用角色库保持人物描述一致
3. **场景连贯性**：相同场景的环境描述保持一致
4. **节奏控制**：通过景别切换控制叙事节奏
5. **原文引用**：对白使用原文，保持原著风格
