---
name: comic-gen
version: 1.0.0
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

### Step 3: 生成分镜脚本

**引用独有模块**：

```
~/.claude/skills/comic-gen/modules/
├── expression-mapping.md  # 表情映射
├── action-mapping.md      # 动作映射
└── transition-rules.md    # 转场规则
```

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

**批量生成**：

使用 MiniMax API 并行生成图片：

```bash
# 每帧生成一张图片
mmx image generate --prompt "..." --out-prefix {作品名}_ch{章节}_frame{序号}
```

**图片生成规则**（继承 scene-img）：

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

- mmx CLI (MiniMax API)
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
   - 拆解为 8 帧
   - 确定景别序列
   - 生成每帧 Prompt
5. Step 4 生成图片 x 8
6. 输出：shuihu_ch10_script.md + shuihu_ch10_comic.md + 8 张图片
```
