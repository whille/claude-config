# 场景类型模板

> 针对常见场景类型，提供默认约束和 Prompt 片段，实现快速复用

---

## 使用方法

1. 识别场景类型
2. 应用对应模板的约束
3. 复用 Prompt 片段
4. 根据原文调整细节

---

## 文人宅院 / Scholar's Study

**代表场景**：潇湘馆、蘅芜苑、文人书房

**氛围**：serene, scholarly, refined, quiet

### 必须元素

| 元素 | 说明 |
|------|------|
| 书卷气 | books, writing materials, scrolls |
| 简洁陈设 | simple furniture, modest decor |
| 清雅植物 | bamboo, plum, orchid |
| 单层建筑 | single-story building |

### 禁止元素

| 元素 | 说明 |
|------|------|
| 金碧辉煌 | no ornate decorations |
| 彩色花卉 | no colorful garden flowers |
| 现代元素 | no modern elements |
| 多层楼阁 | no multi-story buildings |

### Prompt 片段

```
scholar's study, simple wooden desk, books stacked,
ink stones and brushes, bamboo window screens,
elegant but modest, no ornate decorations,
single-story building,
serene atmosphere, soft natural lighting,
traditional Chinese scholar aesthetic
```

### 与贵族园林对比

| 维度 | 文人宅院 | 贵族园林 |
|------|----------|----------|
| 装饰 | 简洁 | 精致 |
| 色彩 | 淡雅 | 华丽 |
| 植物 | 竹、梅、兰 | 牡丹、海棠、蔷薇 |

---

## 贵族园林 / Noble Garden

**代表场景**：怡红院、正殿、省亲别墅

**氛围**：ornate, traditional, grand, elaborate

### 必须元素

| 元素 | 说明 |
|------|------|
| 精致对称 | symmetrical layout, refined details |
| 传统木结构 | traditional wooden architecture |
| 游廊串联 | covered corridors connecting buildings |
| 单层或多层混合 | mostly single-story with occasional pavilions |

### 禁止元素

| 元素 | 说明 |
|------|------|
| 现代玻璃窗 | no modern glass windows |
| 西方风格 | no Western architecture |
| 简陋 | no crude or rough elements |

### Prompt 片段

```
Qing dynasty noble garden,
elaborate wooden architecture,
traditional lattice windows not modern glass,
covered walkways connecting courtyards,
ornate but not excessive,
symmetrical layout,
诸侯级建筑（亲王）,
green glazed tiles,
grand but within garden walls
```

### 建筑等级参考

| 等级 | 特征 |
|------|------|
| 皇家 | 金琉璃瓦、九开间 |
| 亲王 | 绿琉璃瓦、七开间 |
| 官员 | 灰瓦、三五开间 |
| 庶民 | 灰瓦、三开间以下 |

---

## 田园茅舍 / Rustic Farmhouse

**代表场景**：稻香村、农家小院

**氛围**：rustic, pastoral, peaceful, humble

### 必须元素

| 元素 | 说明 |
|------|------|
| 茅草屋顶 | thatched roof |
| 黄泥墙 | yellow mud walls |
| 菜园果木 | vegetable garden, fruit trees |
| 简单工具 | simple farming tools |

### 禁止元素

| 元素 | 说明 |
|------|------|
| 精雕细琢 | no ornate carvings |
| 华丽装饰 | no elaborate decorations |
| 现代设备 | no modern machinery |

### Prompt 片段

```
rustic farmhouse, thatched roof,
yellow mud walls, simple cottage,
vegetable patches, fruit trees in blossom,
apricot blossoms filling the view,
simple country life, warm natural light,
pastoral scenery,
no ornate decorations, no modern elements
```

### 花卉对照

| 场景 | 代表花卉 | 意象 |
|------|----------|------|
| 稻香村 | 杏花 | 如喷火蒸霞 |
| 文人宅 | 竹、梅 | 坚韧清高 |
| 贵族园 | 牡丹、海棠 | 富贵荣华 |

---

## 山水自然 / Landscape Nature

**代表场景**：蓼汀花溆、山水游记、自然风光

**氛围**：vast, atmospheric, meditative, ethereal

### 必须元素

| 元素 | 说明 |
|------|------|
| 留白 | negative space, empty areas |
| 远近层次 | atmospheric perspective, depth |
| 小人物参照 | small figure for scale |
| 气氛渲染 | mist, fog, atmosphere |

### 禁止元素

| 元素 | 说明 |
|------|------|
| 现代建筑 | no modern buildings |
| 详细人物 | no detailed faces or individuals |
| 喧闹人群 | no crowds |

### Prompt 片段

```
traditional Chinese landscape painting style,
vast negative space, atmospheric mist,
layers of mountains receding into distance,
small figure in distance for scale,
no detailed faces, impressionistic details,
ink wash painting aesthetic,
ethereal atmosphere
```

### 构图原则

| 原则 | 说明 |
|------|------|
| 远虚近实 | distant elements softer |
| 留白 | empty areas for imagination |
| 气韵生动 | atmosphere over detail |

---

## 建筑特写 / Architecture Detail

**代表场景**：园门入口、亭台楼阁、装饰细节

**氛围**：structural, detailed, architectural

### 必须元素

| 元素 | 说明 |
|------|------|
| 结构清晰 | clear architectural structure |
| 细节可见 | visible details and carvings |
| 正确材质 | appropriate materials for era |

### 禁止元素

| 元素 | 说明 |
|------|------|
| 人物遮挡 | no blocking figures |
| 过度背景 | minimal background |

### Prompt 片段

```
architectural detail shot,
traditional Chinese wooden structure,
carved beams and painted rafters,
elaborate lattice windows,
stone foundation and steps,
clear structural elements,
fill frame with architecture
```

---

## 庙宇禅房 / Temple Monastery

**代表场景**：栊翠庵、山神庙、道观

**氛围**：meditative, quiet, sacred, humble

### 必须元素

| 元素 | 说明 |
|------|------|
| 简单朴素 | simple and plain |
| 香火痕迹 | incense offerings |
| 宗教符号 | religious symbols（subtle） |

### 禁止元素

| 元素 | 说明 |
|------|------|
| 喧闹人群 | no crowds |
| 豪华装饰 | no ornate decorations |
| 详细佛像 | no detailed Buddha statues（respect） |

### Prompt 片段

```
small humble shrine,
simple temple architecture,
incense burner, meditation atmosphere,
quiet and secluded,
no crowds, no detailed religious statues,
serene spiritual mood
```

---

## 环境约束速查

### 室内 vs 室外

| 环境 | Prompt 关键词 |
|------|--------------|
| 室内 | `interior view`, `inside building`, `no outdoor view` |
| 室外院落 | `enclosed courtyard`, `within garden walls` |
| 室外开放 | `open landscape`, `distant mountains` |
| 半开放 | `covered walkway`, `veranda` |

### 尺度约束

| 尺度 | Prompt 关键词 |
|------|--------------|
| 近景 | `close-up`, `detail shot` |
| 中景 | `medium shot`, `eye-level view` |
| 远景 | `wide shot`, `distant view` |
| 全景 | `panoramic view`, `bird's eye view` |

---

## 场景组合示例

### 潇湘馆（文人宅院 + 植物）

```
【类型】文人宅院
【核心符号】翠竹千百竿

scholar's courtyard,
thousands of emerald bamboo as main focus,
bamboo grove screening buildings,
simple wooden structure, single-story,
traditional lattice windows,
serene atmosphere, soft lighting,
no colorful flowers, no ornate decorations
```

### 稻香村（田园茅舍 + 花卉）

```
【类型】田园茅舍
【核心符号】杏花如霞、茅屋

rustic farmhouse in noble garden,
thatched cottage with yellow mud walls,
apricot blossoms like rosy clouds covering view,
vegetable patches, simple country life,
pastoral scenery within enclosed walls,
warm spring light,
no ornate architecture
```

### 怡红院（贵族园林 + 植物对比）

```
【类型】贵族园林
【核心符号】芭蕉海棠对比

noble's courtyard,
banana leaves and red crabapple flowers in contrast,
traditional wooden architecture, single-story,
covered walkways, moon gate entrance,
ornate but elegant,
rose vines cascading on walls,
within garden walls, no distant mountains
```
