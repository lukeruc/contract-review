# Format Task Agent 参考示例

> **本文档为参考示例，非强制模板。** Architect 应根据具体任务需要自行撰写 task spec 和 system prompt，不应照搬填充。

Format Task Agent 有两种使用场景：审核意见书输出和修订合同输出。以下分别给出参考示例。

## System Prompt 参考

```
你是格式输出 Task Agent。你的任务是将 Markdown 文档转为符合法律文书排版规范的 .docx 文件。

你执行的是纯格式转换，不做任何内容修改。

工作标准：
- 输出 .docx 可用 Word 和 WPS 正常打开
- 法律文书排版：标题黑体二号居中，一级标题黑体三号，正文仿宋四号 1.5 倍行距，页边距上下 2.54cm 左右 3.17cm，页码页脚居中
- 审核意见书：风险等级颜色保留（红/黄/绿），条款编号加粗
- 修订合同：以原始 .docx 为基底应用修订标记，保持原合同排版风格
- 不改动任何文字内容
```

## Task Spec 参考示例（审核意见书）

```markdown
---
task_id: "T-FMT-01"
task_type: "format"
status: "draft"
version: 1
input_files:
  - "_internal/task-records/T-ASM-01/output.md"
output_file: "output/audit-opinion.docx"
delivery_standards:
  - "输出文件可用 Word 和 WPS 正常打开，无格式损坏"
  - "标题黑体二号居中，一级标题黑体三号，正文仿宋四号 1.5 倍行距"
  - "风险等级颜色保留（红 #DC2626 / 黄 #F59E0B / 绿 #16A34A）"
  - "条款编号加粗"
  - "不改动任何文字内容、措辞、术语"
architect_only_items: []
created: "2026-05-10 17:00"
---

# 任务描述

将审核意见书 Markdown 转为 .docx 文件。

## 格式要求

- 封面页标题：XX 工程总承包合同 审核意见书
- 正文页眉居中：审核意见书
- 页脚居中：页码
```

## Task Spec 参考示例（修订合同）

```markdown
---
task_id: "T-FMT-02"
task_type: "format"
status: "draft"
version: 1
input_files:
  - "_internal/task-records/T-REV/output.md"
  - "original/工程总承包合同.docx"
output_file: "output/工程总承包合同-revised.docx"
delivery_standards:
  - "以原始 .docx 为排版基底，在其上应用修订标记"
  - "修订标记符合 Word 修订模式标准（<w:ins>/<w:del> 元素）"
  - "原合同排版风格（字体、字号、页边距）不变"
  - "输出文件可用 Word 和 WPS 正常打开"
  - "不改动任何文字内容"
architect_only_items: []
created: "2026-05-10 17:00"
---

# 任务描述

以原始 .docx 为基底，将修订后的合同文本应用为修订模式标注。

## 格式要求

- 保持原始合同的全部排版风格
- 修订标注对应审核意见书的 15 条修改建议
- 新增文字使用下划线标记，删除文字使用删除线标记
```

## 设计要点

1. **两种场景的输出要求不同**。审核意见书是新建文档，排版自主掌控。修订合同是在原始文件上打标记，必须保持原排版。
2. **格式标准写了具体数值**（如颜色色号 #DC2626）而非"红色"——防止 LLM 用不同的红。
3. **"可用 Word 和 WPS 正常打开"是硬性标准**。如果生成的文件打不开，其他一切标准都没有意义。
4. **不改内容是底线**。Format Agent 如果"顺便"改了几个字，Architect 很难发现。
