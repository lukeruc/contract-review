# 简单模式工作流程

当用户在 Bootstrap 信息确认阶段选择简单模式时执行此流程。

简单模式不启用 Reviewer。Architect 上下文充裕，自行验收即是最完整审查。

> **前置条件**：bootstrap 步骤（创建会话目录、格式转化、获取字符数、信息确认）已在 SKILL.md Bootstrap 中完成。审核立场和修订设置已确认并记录于 `_internal/architect-materials/shared-context.md`。

## 阶段 1：合同类型判断与规则匹配

### 1.1 读取合同并判断类型

读取 `contract.md` 全文。结合已确认的审核立场（`_internal/architect-materials/shared-context.md`），判断合同类型。

### 1.2 扫描规则

扫描 `rules/` 目录下所有 `.md` 文件的 YAML frontmatter：
1. 用 `find rules/ -name "*.md"` 列出所有规则文件
2. 逐个读取 frontmatter，提取 `contract_type`、`contract_type_en`、`applicable_when`
3. 将合同内容与每条规则的 `applicable_when` 字段匹配

匹配成功 → 加载该规则文件的内容，作为制定 delivery_standards 的底本。

无匹配 → 暂停流程，向用户报告：列出已识别的合同特征，请用户选择或确认合同类型。等待用户指示后继续。

## 阶段 2：审核

### 2.1 制定交付标准

匹配到的规则文件是通用底本——它覆盖该合同类型的常见审核要点，但不了解这份具体合同的内容和用户的特殊关切。你需要基于规则文件，结合以下因素制定 T-001 的 `delivery_standards`：

- **合同实际内容**：合同中实际存在哪些条款？规则中某些检查项可能不适用（如合同无保密条款则跳过），也可能需要补充（如合同有特殊的对赌安排而规则未覆盖）
- **用户的具体要求**：用户在审核立场确认阶段可能提出了特定关切（如"重点关注付款条款"），应体现为交付标准中的侧重项
- **审核立场**：代表方不同，同一规则的审查方向不同（如"核查违约金比例是否合理"，代表承包方时关注是否过高，代表发包方时关注是否过低）

每条交付标准必须是机械可判定检查项。规则文件中已逐条列出审核要点，作为交付标准的底本——你在此基础上删减、补充、调整措辞和侧重方向。

### 2.2 创建 Audit Task Agent（T-001）

阅读 `references/task-audit.md` 参考示例了解典型结构，然后自行撰写 task spec：

**注入工具**：`yd-law`（法律检索）、`qcc`（工商查询）

**注入文件**：
- `contract.md`
- `_internal/architect-materials/shared-context.md`（含已确认的审核立场）
- 匹配到的规则文件（如有）

**任务规格书**：
- 写入 `_internal/task-records/T-001/task-spec.md`
- 遵循 `schemas/task-spec.schema.md`
- `task_type: "audit"`
- `delivery_standards` 使用步骤 2.1 制定的标准
- 正文中明确审查范围为全合同，审核立场使用已确认的代表方、审核目标和风险偏好

**下达任务**：创建 Task Agent，令其按 task-spec.md 执行，产出写入 `_internal/task-records/T-001/output.md`。

### 2.3 Architect 验收审核意见书

读取 `_internal/task-records/T-001/output.md`，对照 contract.md 和 delivery_standards 逐项验收：

- 是否有遗漏条款未审核？
- 风险标注是否准确（对照合同原文核验）？
- 法律依据引用是否正确？
- 修改建议是否可操作？

通过 → 继续。

不通过 → 重建 T-001（非修订，重新创建新 Task Agent 实例），修正 task-spec 中的问题描述，重新执行。可附上验收发现的问题作为补充说明。

## 阶段 3：修订

### 3.1 创建 Revision Task Agent（T-002）

阅读 `references/task-revision.md` 参考示例了解典型结构，然后自行撰写：

**注入工具**：`safe-docx` — `read`/`replace`/`comment`/`save`。在原 docx 上用 `--and` 串联所有 replace + comment + save 到一个命令中（MCP session 不跨进程）。逐条替换文本（自动追踪修订），每处修订附批注。

**注入文件**：
- `original/{原始文件名}`
- `_internal/task-records/T-001/output.md`（审核意见书）
- `_internal/architect-materials/shared-context.md`（审核立场、修订人姓名和术语约定）

**任务规格书**：
- 写入 `_internal/task-records/T-002/task-spec.md`
- `task_type: "revision"`
- `delivery_standards` 重点：逐条执行修改、修订可追溯、最小改动原则、按已确认的审核立场调整措辞

**下达任务**：创建 Task Agent，产出写入 `_internal/task-records/T-002/output.md`。

### 3.2 Architect 验收修订稿

读取 `_internal/task-records/T-002/output.md`，对照审核意见书逐条核验：

- 每条修改建议是否已执行？
- 未执行的是否有合理说明？
- 修改位置是否准确（未误改无关内容）？

通过 → 继续。

不通过 → 重建 T-002，附上验收发现的问题。

## 阶段 4：格式输出

### 4.1 审核意见书

将 `_internal/task-records/T-001/output.md` 复制到 `output/audit-opinion.md`。审核意见书以 .md 格式交付，不生成 .docx。

### 4.2 修订合同 .docx

创建 Format Task Agent（T-FMT-02），阅读 `references/task-format.md` 参考示例并自行撰写。要求：

**注入文件**：`_internal/task-records/T-002/output.md` + `original/{原始文件名}`
**输出路径**：`output/{原合同名}-revised.docx`
**特别要求**：每处修订附一个批注，简短说明修改原因（1-2 句）。Revision Agent 的 task spec 中注明此要求。

## 阶段 5：交付

向用户报告完成，列出交付物路径：
- `output/audit-opinion.md`
- `output/audit-work-report.md` + `output/audit-work-report.html`
- `output/{原合同名}-revised.docx`

附简要摘要：合同类型、发现的高/中/低风险数量、核心建议。

## 阶段 6：对话续接

用户此后可能有追问（"第三条风险具体怎么改""审查时检索了哪些法条"）。在会话目录下创建 `agent/`，用户在 `agent/` 路径下新开 Claude Code 实例即可直接进入对话状态。

Architect 亲自编制以下两个文件（不做法律分析，做信息蒸馏）：

### agent/CLAUDE.md

向新 Agent 提供完整语境。包含：

- **合同速览**：合同名称、类型、当事方、核心交易结构（2-3 句）、适用法律、审核立场。来自 `_internal/architect-materials/shared-context.md`
- **审查结论摘要**：总体风险评级、高/中/低风险数量、最重要的发现（3-5 条）。来自审核意见书
- **修订概况**：修改了几条、涉及哪些条款范围。来自修订产出
- **文件索引指引**：告知 Agent 去哪找完整信息——审核意见书在 `output/audit-opinion.docx`，原始合同在 `original/`，工作产品在 `_internal/`
- **常见追问导航**：预判用户可能问的方向，每个方向标注应读取哪个文件。典型问题如：
  - "某条款的风险具体是什么" → 读 `output/audit-opinion.docx`
  - "这个修改的法律依据在哪" → 读 `_internal/task-records/T-001/output.md`
  - "对方如果不同意这个修改怎么谈" → 结合审核意见书的修改建议和合同原文分析
- **Agent 自我认知**：声明"你**不是**重新审合同的 Architect，你是基于已有审查产出回答用户追问的助手。所有法律分析已完成，你的工作是定位、解释和展开"

### agent/index.md

按目录分组列出所有工作产物文件，每行含文件名、简短描述、产生者。格式：

```
# 工作产品索引

## output/
- audit-opinion.docx — 审核意见书（T-FMT-01）
- {原合同名}-revised.docx — 修订后合同（T-FMT-02）

## _internal/architect-materials/
- shared-context.md — 共享上下文（Architect）
...

## _internal/task-records/
- T-001/task-spec.md — Audit 任务规格书（Architect）
- T-001/output.md — 审核意见书正文（T-001）
...
```

### 审核工作报告

Architect 撰写 `output/audit-work-report.md`，并生成一份简洁的 `output/audit-work-report.html` 供用户阅读。报告内容：

- **合同概要**：合同名称、类型、当事方、核心交易结构。取自 shared-context.md
- **工作流程**：本次审核的执行过程——bootstrap → 合同类型判断 → 规则匹配 → 审核（T-001）→ 修订（T-002）→ 格式输出。注明每阶段的关键决策和异常情况（如有）
- **审核发现摘要**：总体风险评级、高/中/低风险数量统计、风险分布概况
- **主要修改点**：逐条列出重要的修改建议——条款编号、问题简述、修改方向、风险等级。这是报告的核心，让用户无需打开审核意见书全文即可了解最重要的修改内容
- **文件索引**：列出所有产出文件路径，方便用户查找

报告篇幅适中（建议 1500-3000 字），面向用户，语言清晰不含法律黑话。
