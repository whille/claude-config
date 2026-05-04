# Output Format Rules

> 输出格式规范

---

## Markdown 公式

**必须使用 LaTeX 格式**（Chrome 插件才能渲染）

| 场景 | 格式 |
|------|------|
| 行内公式 | `$...$` |
| 块级公式 | `$$...$$` |

❌ 错误：代码块 `\`\`\`ζ(s) = Σ(1/n^s)\`\`\`` 不渲染

✅ 正确：`$$\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}$$`

---

## 常用 LaTeX

| 符号 | 写法 |
|------|------|
| 求和/积分 | `\sum_{i=1}^n` `\int_a^b` |
| 分数/根号 | `\frac{a}{b}` `\sqrt{x}` |
| 希腊字母 | `\alpha \beta \theta \zeta` |
| 上下标 | `x^2` `x_i` |
| 集合 | `\mathbb{R} \mathbb{Z}` |
