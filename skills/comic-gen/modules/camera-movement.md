# 运镜控制

> 增强画面动态感与电影感

---

## 问题背景

**现象**：生成的图片画面僵硬，缺乏动态感和电影感。

**根因**：
1. 缺少运镜控制提示词
2. 静态画面描述过于平淡
3. 未区分"静态镜头"与"动态运镜"

**解决方案**：在 Prompt 中添加运镜控制词汇，指导 AI 生成更有动态感的画面。

---

## 运镜类型速查表

| 运镜 | 英文 Prompt | 视觉效果 | 适用场景 |
|------|-------------|----------|----------|
| 推镜头 | `Slow camera push-in` | 画面向主体推进，聚焦 | 情绪聚焦、重要揭示 |
| 拉镜头 | `Camera pull-back` | 画面从主体拉远，扩展视野 | 环境交代、全景展示 |
| 左摇 | `Pan left` | 镜头水平左转 | 环境展示、跟随视线 |
| 右摇 | `Pan right` | 镜头水平右转 | 环境展示、跟随视线 |
| 上摇 | `Tilt up` | 镜头垂直上转 | 展示高度、仰视感 |
| 下摇 | `Tilt down` | 镜头垂直下转 | 展示地面、俯视感 |
| 跟随镜头 | `Tracking shot` | 镜头跟随主体移动 | 行走、追逐、对话移动 |
| 升降镜头 | `Pedestal up / Pedestal down` | 镜头整体升降 | 高低位切换 |
| 静态镜头 | `Static shot` | 镜头固定不动 | 对话、静谧、肖像 |
| 摇晃镜头 | `Shaky cam` | 镜头晃动，紧张感 | 战斗、追逐、恐慌 |
| 环绕镜头 | `Orbit shot` | 镜头环绕主体 | 展示全貌、强调主体 |
| 变焦推拉 | `Zoom in / Zoom out` | 光学变焦，背景压缩/扩展 | 聚焦/揭示环境 |

---

## 运镜与场景类型映射

### 情绪场景

| 情绪 | 推荐运镜 | 组合示例 |
|------|----------|----------|
| 紧张 | 推镜头 + 摇晃 | `Slow camera push-in, slight shaky cam` |
| 悲伤 | 静态 + 缓慢拉远 | `Static shot, then slow camera pull-back` |
| 欢快 | 跟随 + 环绕 | `Tracking shot, orbit around subjects` |
| 愤怒 | 推镜头 + 低角度 | `Low angle, slow camera push-in` |
| 恐惧 | 摇晃 + 推镜头 | `Shaky cam, slow camera push-in` |
| 平静 | 静态 | `Static shot, calm composition` |

### 动作场景

| 动作类型 | 推荐运镜 | 组合示例 |
|----------|----------|----------|
| 打斗 | 快速切换 + 摇晃 | `Fast cuts, shaky cam, dynamic angles` |
| 追逐 | 跟随 + 摇 | `Tracking shot, pan left to follow` |
| 飞行/跳跃 | 升降 + 仰视 | `Pedestal up, low angle` |
| 慢动作 | 推镜头 + 静态 | `Slow motion, static shot, slow camera push-in` |
| 击打瞬间 | 特写 + 推镜头 | `Extreme close-up, quick push-in` |

### 对话场景

| 对话类型 | 推荐运镜 | 组合示例 |
|----------|----------|----------|
| 双人对话 | 静态 + 切换 | `Static shot, over-the-shoulder` |
| 争论 | 摇晃 + 推镜头 | `Slight shaky cam, slow push-in` |
| 告白 | 推镜头 + 柔焦 | `Slow camera push-in, soft focus` |
| 群体讨论 | 环绕 + 全景 | `Orbit shot, wide establishing shot` |

---

## 运镜序列模板

### 三帧序列（基础）

```
帧1: 全景 + 静态（交代环境）
帧2: 中景 + 推镜头（聚焦主体）
帧3: 近景 + 静态（情绪特写）
```

### 五帧序列（完整）

```
帧1: 全景 + 静态（环境交代）
帧2: 中景 + 跟随（主体进入）
帧3: 近景 + 推镜头（情绪聚焦）
帧4: 特写 + 静态（细节展示）
帧5: 远景 + 拉镜头（收尾氛围）
```

### 动作序列

```
帧1: 全景 + 低角度（对峙）
帧2: 中景 + 跟随（动作开始）
帧3: 近景 + 摇晃（动作高潮）
帧4: 特写 + 推镜头（击中瞬间）
帧5: 远景 + 拉镜头（结果展示）
```

---

## Prompt 组装规则

### 标准顺序

```
{景别}, {运镜},
{场景描述},
{人物描述},
{动作描述},
{氛围关键词},
```

### 示例

**推镜头情绪聚焦**：
```
medium shot, slow camera push-in,
Qing dynasty noble garden, bamboo pavilion,
Lin Daiyu, delicate beauty, pale complexion, greenish-white robes,
standing alone, gazing into distance,
melancholic atmosphere, soft lighting,
```

**跟随镜头行走**：
```
medium shot, tracking shot, pan right,
Qing dynasty garden path, spring flowers blooming,
Jia Baoyu, young nobleman in red robes, jade ornament at waist,
walking briskly, looking around with curiosity,
bright daylight, cheerful atmosphere,
```

**低角度仰视**：
```
low angle, wide shot, static shot,
grand hall entrance, red pillars, ornate ceiling,
Jia Zheng, middle-aged official in dark robes, stern posture,
standing imperiously, looking down,
formal atmosphere, imposing presence,
```

---

## 与其他模块协作

| 模块 | 协作方式 |
|------|----------|
| `transition-rules.md` | 运镜类型嵌入转场序列 |
| `character-reference.md` | 人物描述 + 运镜控制 |
| `style-consistency.md` | 运镜 + 风格前缀 |

---

## MiniMax API 注意事项

### 支持的运镜关键词

MiniMax text_to_image 支持以下运镜词：
- `wide shot` / `medium shot` / `close-up`
- `low angle` / `high angle` / `bird's eye view`
- `static shot` / `tracking shot`

### 可能不生效的词汇

以下词汇可能效果有限：
- `shaky cam`（静止图片无法表现）
- `zoom in/out`（需要视频才能表现）
- `slow camera push-in`（单帧难以表现）

**替代方案**：
- 用景别变化暗示运镜：`wide shot → medium shot → close-up`
- 用视角变化暗示动态：`low angle` + `high angle` 交替

---

## 最佳实践

### 静态图片的动态感

对于 text_to_image 生成的静态图片：

| 效果 | 实现方法 |
|------|----------|
| 推镜头感 | 使用 `close-up` + `sharp focus` |
| 拉镜头感 | 使用 `wide shot` + `atmospheric perspective` |
| 跟随感 | 使用 `subject in motion` + `motion blur hint` |
| 环绕感 | 使用 `profile view` + `three-quarter view` |

### 视频生成的运镜

如需真正的运镜效果，需使用 `generate_video` API：

```python
# 图片序列生成视频
mcp__MiniMax__generate_video(
    first_frame_image="frame_01.jpg",
    prompt="Slow camera push-in on the character, emotional focus",
    model="I2V-01"
)
```

---

## 检查清单

分镜生成时检查：
- [ ] 每帧是否有运镜词
- [ ] 运镜是否适合场景类型
- [ ] 运镜序列是否有节奏变化
- [ ] 是否避免过度使用相同运镜

---

## 扩展阅读

- 电影运镜基础：[Cinematography Basics](https://www.studiobinder.com/blog/how-to-use-camera-movement/)
- 镜头语言指南：[Shot Sizes and Camera Movements](https://www.filmsite.org/visualelements.html)
