---
name: ebook-to-md
version: 1.0.0
description: 将 PDF/PNG/JPEG/MOBI/EPUB 转换为 Markdown。使用百度 OCR。适用于扫描版 PDF、图片 OCR、电子书转换。
user-invocable: true
argument-hint: "<文件路径> [--output <输出路径>]"
triggers:
  - "pdf转markdown"
  - "pdf转md"
  - "图片转文字"
  - "ocr识别"
  - "电子书转换"
  - "pdf ocr"
  - "扫描pdf"
last_updated: 2026-05-02
---

# ebook-to-md 技能

将 PDF、图片、MOBI、EPUB 转为 Markdown。仅使用百度 OCR。

## 支持格式

| 格式 | 说明 |
|------|------|
| PDF | 扫描版/图像型 PDF |
| PNG/JPEG | 单张图片 |
| MOBI/EPUB | 需安装 Calibre |

## 使用方式

### 基本用法

```bash
/ebook-to-md /path/to/file.pdf
```

### 指定输出路径

```bash
/ebook-to-md /path/to/file.pdf --output /path/to/output.md
```

### 图片 OCR

```bash
/ebook-to-md /path/to/screenshot.png
```

### MOBI/EPUB

```bash
/ebook-to-md /path/to/book.epub
```

## 依赖

### Python 包

```bash
pip install requests
```

### 系统依赖

- **Calibre**（mobi/epub）：`brew install calibre`
- **百度 OCR**：需设置环境变量

### 环境变量

```bash
export BAIDU_OCR_API_KEY="your_api_key"
export BAIDU_OCR_SECRET_KEY="your_secret_key"
```

## 执行逻辑

调用脚本：

```bash
python ${CLAUDE_SKILL_DIR}/scripts/ebook_to_md.py \
  --input_path=<输入文件> \
  --output_path=<输出文件>
```

## 输出

- 成功：返回 Markdown 内容预览
- 失败：返回错误信息

## 示例输出

```
转换成功，已写入: ./output.md

预览:
# 第一章 标题

内容正文...
```

## 注意事项

1. **百度 OCR API**：需要有效的 API 密钥
2. **大文件**：处理时间较长，需耐心等待
3. **图片质量**：清晰度影响识别准确率

## 相关技能

- `pdf_to_markdown`：原生文本 PDF 转换（docling）
