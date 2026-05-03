# 风格一致性增强

> 作品级风格统一策略

---

## 问题背景

**现象**：同一作品不同帧风格差异大，画面割裂感强。

**根因**：
1. 风格描述过于抽象
2. 每帧风格描述不统一
3. 模型随机性导致风格漂移

**解决方案**：建立作品级风格约束体系，最大化一致性。

---

## 核心策略

### 1. 种子词固定（作品级）

**定义**：每个作品开头固定 50 字符的风格描述，全片不变。

**格式**：
```
{时代} {题材} {艺术风格}, {技法}, {色调}, {氛围},
```

**示例**：

| 作品 | 种子词 |
|------|--------|
| 红楼梦 | `Qing dynasty noble garden story, ink wash painting aesthetic, traditional Chinese art style, soft brush strokes, muted color palette, elegant composition,` |
| 水浒传 | `Northern Song dynasty martial tale, bold ink strokes, dynamic composition, earth tones, heroic atmosphere, traditional Chinese illustration style,` |
| 三国演义 | `Three Kingdoms era war epic, grand scale, classical Chinese painting style, dramatic lighting, military atmosphere, traditional ink wash,` |

### 2. 负面提示词统一

**固定负面词**：
```
--no modern, Western, photorealistic, anime, manga, 3D render, digital art, cartoon, flat design, minimalist, abstract, surreal
```

**作品特定负面词**：

| 作品 | 额外负面词 |
|------|------------|
| 红楼梦 | `--no battle scenes, violence, blood, weapons, army` |
| 水浒传 | `--no feminine aesthetics, soft colors, delicate features` |
| 三国演义 | `--no feminine aesthetics, soft colors, indoor scenes` |

### 3. 模型固定

**规则**：全片使用同一模型参数

```
model: image-01
aspect_ratio: 16:9 (横版) 或 9:16 (竖版)
prompt_optimizer: true
```

### 4. 角色锚定词

每个角色固定 3 个核心词汇，每帧必含至少 2 个。

| 角色 | 锚定词 |
|------|--------|
| 林黛玉 | `delicate`, `pale`, `melancholic` |
| 贾宝玉 | `young nobleman`, `red robes`, `jade ornament` |
| 王熙凤 | `phoenix eyes`, `elaborate headdress`, `commanding` |

### 5. 批量生成优化

**同场景多帧策略**：
1. 提取场景公共描述
2. 每帧共用公共部分
3. 仅变化动作/表情

**示例**：

公共部分：
```
Qing dynasty noble garden, ink wash painting aesthetic, traditional Chinese art style,
bamboo pavilion interior, delicate furniture, soft daylight through window,
Lin Daiyu, delicate beauty, pale complexion, greenish-white robes, melancholic eyes,
no modern, Western, photorealistic,
```

帧1：
```
{公共部分},
sitting by window, reading poetry, downcast gaze,
```

帧2：
```
{公共部分},
standing up, walking towards door, slight frown,
```

---

## Prompt 模板结构

### 完整模板

```
【种子词】（固定 50 字符）
{时代} {题材} {艺术风格}, {技法}, {色调},

【景别与运镜】
{景别}, {运镜},

【场景描述】
{场景固定描述},

【人物描述】
{角色基准描述（含锚定词）},

【动作与表情】
{动作}, {表情},

【氛围】
{氛围关键词},

【负面约束】
no {负面提示词}
```

### 示例：红楼梦第 17 回

```
Qing dynasty noble garden story, ink wash painting aesthetic, traditional Chinese art style, soft brush strokes, muted color palette,
medium shot, slow camera push-in,
five-bay gate hall, barrel tiles, polished brick wall, spring daylight,
Jia Baoyu, young nobleman, red robes, jade ornament at waist, gentle expression,
walking beside Jia Zheng, listening attentively,
respectful atmosphere, soft lighting,
no modern, Western, photorealistic, anime, manga, 3D render,
```

---

## 分场景风格约束

### 室内场景

| 场景 | 风格关键词 |
|------|------------|
| 书房 | `scholar's study, book shelves, ink and brush, calligraphy` |
| 卧室 | `delicate curtains, carved bed frame, soft lighting` |
| 厅堂 | `formal hall, red pillars, ornate ceiling, grand scale` |

### 室外场景

| 场景 | 风格关键词 |
|------|------------|
| 花园 | `garden paths, rockery, pond, willow trees, flowers` |
| 庭院 | `courtyard, moon gate, pavilion, bamboo grove` |
| 街道 | `market street, shop fronts, crowd, bustling atmosphere` |

### 自然场景

| 场景 | 风格关键词 |
|------|------------|
| 山水 | `mountains, river, mist, pine trees, atmospheric perspective` |
| 季节 | `spring flowers, summer lotus, autumn leaves, winter snow` |

---

## 风格检查清单

生成后检查：

### 整体风格

- [ ] 种子词是否一致
- [ ] 色调是否统一
- [ ] 画幅比例是否一致
- [ ] 艺术风格是否统一

### 人物风格

- [ ] 同角色服装颜色是否一致
- [ ] 同角色年龄感是否一致
- [ ] 同角色气质是否一致

### 环境风格

- [ ] 同场景建筑风格是否一致
- [ ] 同场景色调是否一致
- [ ] 同时代元素是否统一

---

## 与其他模块协作

| 模块 | 协作方式 |
|------|----------|
| `character-reference.md` | 种子词 + 角色基准描述 |
| `camera-movement.md` | 种子词 + 运镜控制 |
| `transition-rules.md` | 风格一致性嵌入转场规则 |

---

## 技术实现

### 种子词存储

在作品配置文件中存储：

```json
{
  "作品名": {
    "seed_prompt": "Qing dynasty noble garden story...",
    "negative_prompt": "modern, Western, photorealistic...",
    "model": "image-01",
    "aspect_ratio": "16:9"
  }
}
```

### 批量生成时应用

```python
def generate_frame_prompt(scene_type, character, action, emotion):
    """生成单帧 Prompt"""
    prompt = SEED_PROMPT + ", "
    prompt += f"{scene_type}, "
    prompt += f"{character.base_prompt}, "
    prompt += f"{action}, {emotion}, "
    prompt += f"no {NEGATIVE_PROMPT}"
    return prompt
```

---

## 最佳实践

### 风格漂移修复

如果发现风格漂移：
1. 检查是否遗漏种子词
2. 增强负面提示词
3. 考虑手动筛选后重新生成

### 多作品区分

确保不同作品有明显不同的种子词：

| 作品 | 种子词开头 |
|------|------------|
| 红楼梦 | `Qing dynasty noble garden` |
| 水浒传 | `Northern Song dynasty martial` |
| 西游记 | `mythological fantasy, magical` |

---

## 限制与替代方案

### API 限制

- text_to_image 无参考图功能
- 无法精确控制风格一致性

### 替代方案

| 方案 | 可行性 |
|------|--------|
| 生成后人工筛选 | 可行，效率低 |
| 风格迁移后处理 | 需要 AI 修图工具 |
| 切换支持参考图的 API | 如 Midjourney --sref |

**当前最佳实践**：严格遵循模板 + 手动筛选 + 适当容忍
