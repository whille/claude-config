# 角色基准描述机制

> 解决 AI 生成图片的角色一致性问题

---

## 问题背景

**现象**：同一角色在不同帧中形象差异大，"换脸"问题严重。

**根因**：
1. 每帧独立生成，无基准图约束
2. 文字描述过于抽象，约束力不足
3. MiniMax text_to_image 不支持参考图（如 Midjourney --cref）

**解决方案**：建立角色基准描述体系，通过标准化 Prompt 增强一致性。

---

## 角色基准描述结构

### 完整结构

```json
{
  "角色名": {
    "base_prompt": "核心视觉描述，固定不变",
    "anchor_words": ["关键词1", "关键词2", "关键词3"],
    "forbidden": ["禁止元素1", "禁止元素2"],
    "variants": {
      "情绪变体": {
        "悲伤": "追加描述",
        "愤怒": "追加描述"
      }
    }
  }
}
```

### 字段说明

| 字段 | 用途 | 示例 |
|------|------|------|
| `base_prompt` | 核心描述，每帧必须包含 | `"Lin Daiyu, delicate beauty, slender figure..."` |
| `anchor_words` | 锚定词，每帧至少选 2 个 | `["delicate", "pale", "bamboo"]` |
| `forbidden` | 禁止元素，避免偏离 | `["no smiling", "no bright colors"]` |
| `variants` | 情境变体，按需追加 | `{"悲伤": "tears in eyes"}` |

---

## 红楼梦角色基准示例

### 林黛玉

```json
{
  "林黛玉": {
    "base_prompt": "Lin Daiyu, delicate beauty, slender figure, pale complexion, thin curved eyebrows, melancholic eyes, wearing light greenish-white robes, bamboo surroundings, poetic aura, traditional Chinese beauty, Qing dynasty style",
    "anchor_words": ["delicate", "pale", "melancholic", "slender", "bamboo"],
    "forbidden": ["no smiling", "no bright colors", "no heavy makeup", "no western style"],
    "variants": {
      "悲伤": "tears in eyes, downcast gaze",
      "沉思": "distant gaze, hand touching chin",
      "病态": "coughing, leaning on support"
    }
  }
}
```

### 贾宝玉

```json
{
  "贾宝玉": {
    "base_prompt": "Jia Baoyu, young nobleman, handsome face, red robes, jade ornament at waist, gentle expression, aristocratic bearing, about 15 years old, traditional Chinese beauty, Qing dynasty style",
    "anchor_words": ["young nobleman", "red robes", "jade ornament", "handsome", "gentle"],
    "forbidden": ["no western clothing", "no modern elements", "no beard", "no stern expression"],
    "variants": {
      "惊讶": "eyes wide, mouth slightly open",
      "沉思": "brow furrowed, hand on chin",
      "欢喜": "slight smile, bright eyes"
    }
  }
}
```

### 王熙凤

```json
{
  "王熙凤": {
    "base_prompt": "Wang Xifeng, sharp-eyed beauty, phoenix eyes, elaborate headdress, luxurious robes, commanding presence, authoritative stance, traditional Chinese beauty, Qing dynasty style",
    "anchor_words": ["phoenix eyes", "elaborate headdress", "luxurious robes", "commanding"],
    "forbidden": ["no simple clothing", "no shy expression", "no western style"],
    "variants": {
      "威严": "stern gaze, upright posture",
      "狡黠": "slight smirk, narrowed eyes",
      "愤怒": "glaring, pointing finger"
    }
  }
}
```

---

## Prompt 组装规则

### 基础组装

```
{base_prompt},
{情绪变体（可选）},
no {forbidden 元素},
```

### 示例：林黛玉悲伤场景

```
Lin Daiyu, delicate beauty, slender figure, pale complexion, thin curved eyebrows, melancholic eyes, wearing light greenish-white robes, bamboo surroundings, poetic aura, traditional Chinese beauty, Qing dynasty style,
tears in eyes, downcast gaze,
no smiling, no bright colors, no heavy makeup, no western style,
```

### 多角色同框

```
{角色A base_prompt} standing left,
{角色B base_prompt} standing right,
interaction description,
no {合并 forbidden 列表},
```

**示例**：
```
Lin Daiyu, delicate beauty, slender figure, pale complexion, wearing light greenish-white robes, Qing dynasty style, standing left, looking down,
Jia Baoyu, young nobleman, handsome face, red robes, jade ornament at waist, Qing dynasty style, standing right, looking at Lin Daiyu,
gentle concern in his expression,
no smiling, no bright colors, no western style,
```

---

## 使用流程

### Step 1: 读取角色库

```
读取 _shared/characters/{作品}.json
提取 base_prompt 和 anchor_words
```

### Step 2: 选择情绪变体

根据场景情绪选择对应变体：
- 悲伤场景 → `variants.悲伤`
- 喜悦场景 → `variants.喜悦`
- 无明确情绪 → 不追加变体

### Step 3: 组装 Prompt

```
base_prompt + 情绪变体 + forbidden
```

### Step 4: 验证

检查 Prompt 是否包含：
- [ ] 至少 2 个 anchor_words
- [ ] 完整 base_prompt
- [ ] 所有 forbidden 元素

---

## 质量检查

### 一致性检查清单

| 检查项 | 标准 |
|--------|------|
| 同角色不同帧 | 服装颜色一致 |
| 同角色不同帧 | 体型一致（slender/robust） |
| 同角色不同帧 | 年龄感一致 |
| 同角色不同帧 | 发型/头饰一致 |

### 常见问题修复

| 问题 | 修复方法 |
|------|----------|
| 服装颜色变化 | 在 base_prompt 中明确颜色词 |
| 年龄感变化 | 添加 "about X years old" |
| 体型变化 | 添加 "slender/robust figure" |
| 气质变化 | 添加气质关键词 "melancholic/gentle/sharp" |

---

## 与其他模块协作

| 模块 | 关系 |
|------|------|
| `style-consistency.md` | 角色描述 + 风格前缀 |
| `camera-movement.md` | 角色描述 + 运镜控制 |
| `expression-mapping.md` | 情绪变体参考 |

---

## 扩展指南

### 新增角色

1. 确定 base_prompt（核心视觉特征）
2. 选择 3-5 个 anchor_words
3. 列出 forbidden 元素
4. 添加常用情绪变体

### 新增作品

在 `_shared/characters/` 下创建 `{作品名}.json`，遵循相同结构。

---

## 限制与替代方案

### MiniMax API 限制

| 限制 | 影响 |
|------|------|
| 不支持参考图 | 无法像 MJ --cref 那样精确绑定 |
| 单次生成独立 | 无法保证跨帧完全一致 |

### 替代方案

| 方案 | 可行性 |
|------|--------|
| 生成后人工筛选 | 可行，但效率低 |
| 使用支持参考图的 API | 需切换平台（如 Midjourney） |
| 后处理一致性修复 | 需要 AI 修图工具 |

**当前最佳实践**：标准化 Prompt + 严格遵循 + 后期筛选
