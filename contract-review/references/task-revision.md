# Revision Task Agent 参考示例

> **本文档为参考示例，非强制模板。** Architect 应根据具体任务需要自行撰写 task spec 和 system prompt，不应照搬填充。

## System Prompt 参考

```
你是合同修订 Task Agent。你的任务是根据已通过的审核意见书，在合同文本上逐条执行修改，产出含修订标注的合同文本。

工作标准：
- 逐条执行审核意见书中的所有修改建议，不遗漏
- 每处修改标注对应的审核意见条款号，可追溯
- 修订以 shared-context.md 中指定的修订人姓名作为 Word 修订作者名（操作 XML `w:ins` 元素的 `w:author` 属性）
- 最小改动原则——只修改审核意见指出的问题，不主动做额外优化
- 修订后整体检查条款编号连续性和交叉引用有效性
- 无法执行的修改标注 [未执行] 并说明原因

审核意见书路径和工具由 Architect 在创建时指定。
```

## Task Spec 参考示例

```markdown
---
task_id: "T-REV"
task_type: "revision"
status: "draft"
version: 1
input_files:
  - "contract.md"
  - "_internal/task-records/T-ASM-01/output.md"
  - "_internal/architect-materials/shared-context.md"
output_file: "_internal/task-records/T-REV/output.md"
delivery_standards:
  - "逐条执行审核意见书中的所有 15 条修改建议，不遗漏"
  - "每处修改以 Markdown 删除线+粗体标注：~~原文~~**修改后文字**"
  - "无法执行的修改标注 [未执行] 并说明原因"
  - "修订后检查条款编号连续性"
  - "附修改索引表，按合同条款顺序排列"
architect_only_items:
  - "修订后合同的整体逻辑一致性和商业合理性"
created: "2026-05-10 16:00"
---

# 任务描述

根据已通过的审核意见书（T-ASM-01/output.md），在合同文本上逐条执行修改。

## 修订原则

- 最小改动——只改审核意见指出的问题
- 保持原文风格和术语体系
- 当事方简称遵循 shared-context.md 中的约定
- 涉及金额的修改同时标注中文大写

## 输出

- 修订后的完整合同 Markdown（含修订标注）
- 修改索引表：序号、条款号、修改类型（删除/新增/替换）、对应的审核意见编号
```

## 设计要点

1. **Revision Agent 依赖已通过的审核意见书**。在简单模式下输入为单个 Audit 产出，复杂模式下输入为 Assembly 合并后的完整意见书。
2. **最小改动原则很重要**——如果没有这条约束，LLM 可能借机"顺便优化"其他条款，引入不必要的风险。
3. **[未执行] 标注机制**让 Architect 能快速识别哪些修改建议因技术原因无法执行（如目标条款不存在、修改会造成新冲突）。
4. **修改索引表**是 Architect 逐条核验修订内容的关键工具。没有索引表，验收只能逐页对比原文。
5. **修订人姓名**需从 shared-context.md 的修订设置中获取，用于 Word 修订模式的作者标注。python-docx 设置修订作者需操作 XML 层（`w:ins`/`w:del` 元素的 `w:author` 属性），不是简单的属性赋值。如合同中多处修订，需逐个元素设置。
