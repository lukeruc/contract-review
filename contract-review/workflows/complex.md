# 复杂模式工作流程

当用户在 Bootstrap 信息确认阶段选择复杂模式时执行此流程。

复杂模式启用 EPC 全机制：初设 Task Agent → Reviewer 审查 → Architect 编制管理物料 → 详细审查 Task Agent → Reviewer 审查 → 汇编 → 修订 → 格式输出。

> **前置条件**：bootstrap 步骤（创建会话目录、格式转化、获取字符数、信息确认）已在 SKILL.md Bootstrap 中完成。审核立场和修订设置已确认并记录于 `_internal/architect-materials/shared-context.md`。会话目录结构包含 `_internal/preliminary-design/` 子目录。

## 阶段 1：初步设计（Preliminary Design）

### 1.1 Structure Task Agent（T-S01）

**必须先跑**——T-S02 和 T-S03 依赖其条款编号体系。

**先运行 scan-structure.py 做预扫描**（跳过 Agent 第一遍通读）：

```bash
python {SKILL_DIR}/scripts/scan-structure.py contract.md _internal/scan-result.json
```

然后创建 T-S01：读取 `agent/task-structure.md`，将其中的 System Prompt 直接注入 sub-agent，将 Task Spec 作为任务下达。

**注入工具**：无（纯 Markdown 文本处理，预扫描已由脚本完成）

**注入文件**：`contract.md` + `_internal/scan-result.json`

**产出**：`_internal/preliminary-design/01-structured-contract.md`（含结构索引表）

**审查（Reviewer Phase 1 — 索引表驱动核查）**：
创建 Reviewer sub-agent，读取 `references/reviewer.md` 了解判断立场，注入：
- `contract.md`（原文）
- `_internal/preliminary-design/01-structured-contract.md`（含结构索引表）

Reviewer 按索引表逐条核查：
1. 对索引表中每条条款，在原文中搜索确认该条款编号存在于原文预期位置
2. 确认层级归属与索引标注一致
3. 确认条数计数正确（索引说 10 条，正文中该章节下有 10 个条款标题）
4. 标注的编号异常在原文中核实

每次检查为一次精确搜索匹配，不依赖注意力覆盖全文。不通过则退回修订（上限 3 轮），通过后继续。

### 1.2 Conditions + Cross-References（T-S02、T-S03 并行）

两者均依赖 T-S01 产出（条款编号体系），彼此独立可并行。

**T-S02（Conditions Task Agent）**：
- 按 `references/task-conditions.md`
- 注入：`contract.md` + `01-structured-contract.md`
- 产出：`_internal/preliminary-design/02-contract-conditions.md`

**T-S03（Cross-References Task Agent）**：
- 按 `references/task-crossref.md`
- 注入：`contract.md` + `01-structured-contract.md`
- 产出：`_internal/preliminary-design/03-cross-references.md`

**审查（Reviewer Phase 1）**：
T-S02 和 T-S03 各自独立创建 Reviewer 实例审查（按 `references/reviewer.md` Phase 1 标准）。均通过后继续。

### 1.3 Preliminary Report + Architect 编制管理物料（并行）

以下两项工作互不依赖，并行执行：

**A. Preliminary Report Task Agent（T-PR）**

预定义 Agent，读取 `agent/task-preliminary-report.md`，将 System Prompt 直接注入，将 Task Spec 作为任务下达（替换 `{CREATED_TIME}`）。

- 输入：三份初设文档（01/02/03）
- 产出：`output/preliminary-report.md` + `output/preliminary-report.html`
- 面向用户的可读报告，让用户在详细审查开始前就能看到阶段性成果

**B. Architect 编制管理物料**

基于三份已验证初设文档，Architect 编制：

**共享上下文**（`_internal/architect-materials/shared-context.md`）：
- 按 `schemas/shared-context.schema.md` 定义
- 内容：合同基本信息、当事方、核心交易结构、关键术语定义
- **审核立场**已在 bootstrap 步骤中确认，直接填入共享上下文，无需再次确认
- 注入所有后续 Task Agent（Phase 2）和 Reviewer（Phase 2）

**Reviewer 背景信息文档**（`_internal/architect-materials/reviewer-briefing.md`）：
- 按 `schemas/reviewer-briefing.schema.md` 定义
- 内容：可核验数据清单、条款关系速查、高风险区域、审查边界
- 注入所有 Reviewer Phase 2 实例

**工作规划**（`_internal/architect-materials/work-plan.md`）：
- Architect 自用，不做格式要求
- 内容：合同类型判断结论、匹配的规则文件、详细审查阶段的审查维度与分包方案、各 Task Agent 的依赖关系和执行顺序

### 1.4 合同类型判断与规则匹配

Architect 基于三份初设文档和简报，判断合同类型。扫描 `rules/` 目录匹配规则文件。

匹配成功 → 加载规则。规则是各 Task Agent `delivery_standards` 的底本。

无匹配 → 暂停流程，向用户报告：列出合同特征和类型判断依据，请用户选择。等待指示后继续。

### 1.5 初设后确认（根据用户选择）

在 Bootstrap 阶段用户已选择初设完成后是否自动继续。此处按用户选择执行：

**自动继续**：直接进入阶段 2（详细审查）。

**等待确认**：暂停流程，向用户发送：

```
初步设计阶段已完成。产出：
- 结构化合同文本（`_internal/preliminary-design/01-structured-contract.md`）
- 主要合同条件报告（`_internal/preliminary-design/02-contract-conditions.md`）
- 合同内联系报告（`_internal/preliminary-design/03-cross-references.md`）
- 初步情况报告（`output/preliminary-report.md` + `output/preliminary-report.html`）

合同类型判断：{合同类型}，匹配规则：{规则文件名 / 无匹配}。

是否继续进入详细审查阶段？您可以调整审查重点或指定重点关注领域。
```

等待用户指示。用户可能回复"继续""重点关注XX条款""先不继续"等。收到指示后按用户要求调整（如有），进入阶段 2。

## 阶段 2：详细审查（Detailed Review）

### 2.1 创建审查 Task Agent

Architect 按 `work-plan.md` 中规划的审查方案，逐个（或按依赖关系并行）创建 Audit Task Agent。

每个 Task Agent：
- 阅读 `references/task-audit.md` 参考示例，根据分配的具体审查范围自行撰写 task spec
- 注入工具：`yd-law`（法律检索）、`qcc`（工商查询），按需由 Architect 决定
- 注入文件：`contract.md`（或指定章节） + 规则文件 + `shared-context.md`（含已确认的审核立场）
- 写入 task-spec.md（`_internal/task-records/{task_id}/task-spec.md`）
- `delivery_standards` 基于规则文件拆分/调整，每条机械可判定
- 正文中明确各 Agent 的审查范围和审核立场

### 2.2 对每个 Task Agent 执行审查循环

```
Architect 下达 task-spec.md
       │
       ▼
Task Agent 执行 → 产出 output.md
       │
       ▼
Reviewer Phase 2 审查（独立实例，按 references/reviewer.md）
       │
       ├── pass → Architect 验收
       ├── fail（第1-2轮）→ 退回 Task Agent 修订
       └── escalate（第3轮）→ Architect 决策
```

Reviewer Phase 2 注入：
- `shared-context.md`
- `reviewer-briefing.md`
- 当前任务的 task-spec.md（含 delivery_standards）
- Task Agent 产出

### 2.3 Architect 逐个验收

所有审查 Task Agent 均通过 Reviewer 审查后，Architect 最终验收每个产出。验收通过后标记该 task 为 done。

## 阶段 3：汇编审核意见书

Assembly 使用固定定义（`agent/task-assembly.md`），Architect 直接注入。合并策略由 Architect 根据总量评估决定。

### 3.1 评估总量

对所有 Audit Task Agent 的 `output.md` 逐一运行 `{SKILL_DIR}/scripts/char-count.sh` 获取字符数，求和。

- 总和 ≤ 100,000 字符 → **单次合并**（3.2）
- 总和 > 100,000 字符 → **分层合并**（3.3）

### 3.2 单次合并

创建一个 Assembly Agent 实例，读取 `agent/task-assembly.md`，直接注入 System Prompt 和 Task Spec（替换占位符）。输入所有 Audit 产出。

产出：`_internal/task-records/T-ASM-01/output.md`

### 3.3 分层合并

#### 3.3.1 分组

按条款顺序将 Audit 产出连续分组，每组 2-3 份。例如 T-001/T-002 为 A 组，T-003/T-004 为 B 组，T-005/T-006 为 C 组。

#### 3.3.2 第一层（并行）

每组创建一个 Assembly Agent 实例（A/B/C 并行），输入该组的 Audit 产出。产出中间文件：`_internal/task-records/T-ASM-A/output.md` 等。

#### 3.3.3 第一层 Review

每组合并完成后，创建 Reviewer 实例核查合并忠实性。注入：该组输入文件 + 合并输出。

Reviewer 抽样检查：从该组输入中取每份文件的第 1 条、中间 1 条、最后 1 条审核意见，在合并输出中搜索对应条款编号，验证：风险等级一致、核心描述保留、未被遗漏。

全部通过 → 进入下一层。有不通过 → 重建该组 Assembly Agent。同一组累计 3 次不通过 → 该组改用逐个串行合并（一次只合并 2 个输入）。

#### 3.3.4 第二层（串行）

创建一个 Assembly Agent 实例，输入所有第一层中间文件（A+B+C）。产出最终审核意见书：`_internal/task-records/T-ASM-01/output.md`。

第二层同样执行 Review（抽样检查中间结果 → 最终输出的一致性）。

#### 3.3.5 递归

若第一层中间文件的字符总和仍超过 100,000 字符阈值，在第一层之上再分一层。重复直到最后一层的输入总和在阈值以内。

### 3.4 Architect 最终验收审核意见书

整体审查汇编稿：结构连贯、逻辑一致、无遗漏、摘要准确。

## 阶段 4：修订合同

### 4.1 创建 Translation Task Agent（T-TRN）

将汇编后的审核意见书转换为结构化操作手册。流程同简单模式 3.1 节。

**注入工具**：无。

**注入文件**：`T-ASM-01/output.md`（审核意见书汇编稿）+ `shared-context.md`

**产出**：`_internal/task-records/T-TRN/revisions.json`

审查：Reviewer Phase 2 抽查操作手册忠实性 → Architect 验收。

### 4.2 Architect 预处理文档

```bash
python {SKILL_DIR}/scripts/add-paraids.py original/{原始文件名}
```

### 4.3 创建 Revision Task Agent（T-REV）

流程同简单模式 3.4 节。注入 `docx-mcp`，按 revisions.json 逐条执行。

**注入工具**：`docx-mcp`（MCP 原生，不需 Bash）

**注入文件**：`_internal/task-records/T-TRN/revisions.json` + `shared-context.md`

**产出**：`output/{原合同名}-revised.docx`

**审查**：Reviewer Phase 2 审查修订稿 → Architect 最终验收。

## 阶段 5：格式输出

### 5.1 审核意见书

将 `T-ASM-01/output.md` 复制到 `output/audit-opinion.md`。审核意见书以 .md 格式交付。

### 5.2 修订合同 .docx

已于阶段 4.3 生成 `output/{原合同名}-revised.docx`，无需额外步骤。

## 阶段 6：交付

向用户报告完成，列出交付物路径：
- `output/preliminary-report.md` + `output/preliminary-report.html`（初步情况报告）
- `output/audit-opinion.md`
- `output/audit-work-report.md` + `output/audit-work-report.html`（审核工作报告）
- `output/{原合同名}-revised.docx`

附简要摘要：合同类型、审核覆盖的维度、发现的高/中/低风险数量、核心建议。

## 阶段 7：对话续接

用户此后可能有追问（"第三条风险具体怎么改""T-002 和 T-003 的结论有没有矛盾"）。在会话目录下创建 `agent/`，用户在 `agent/` 路径下新开 Claude Code 实例即可直接进入对话状态。

Architect 亲自编制以下两个文件（不做法律分析，做信息蒸馏）：

### agent/CLAUDE.md

向新 Agent 提供完整语境。包含：

- **合同速览**：合同名称、类型、当事方、核心交易结构（2-3 句）、适用法律、审核立场。取自 `_internal/architect-materials/shared-context.md`
- **审查结论摘要**：总体风险评级、高/中/低风险数量、最重要的发现（3-5 条）。取自审核意见书执行摘要
- **修订概况**：修改了几条、涉及哪些条款范围
- **文件索引指引**：告知 Agent 去哪找完整信息。审核意见书在 `output/`，原始合同在 `original/`，初设文档在 `_internal/preliminary-design/`，各 Task Agent 产出在 `_internal/task-records/`
- **常见追问导航**：预判用户可能问的方向并标注应读取哪个文件。复杂模式特别关注：
  - "两个 Audit Agent 的结论有没有矛盾" → 分别读各 T-XXX/output.md，重点看 [意见分歧] 标注
  - "结构化的条款编号体系是什么" → 读 `_internal/preliminary-design/01-structured-contract.md` 的索引表
  - "交叉引用分析发现了什么" → 读 `_internal/preliminary-design/03-cross-references.md`
- **Agent 自我认知**：声明"你**不是**重新审合同的 Architect，你是基于已有审查产出回答用户追问的助手。所有法律分析和质量审查已完成，你的工作是定位、解释和展开"

### agent/index.md

按目录分组列出所有工作产物文件，每行含文件名、简短描述、产生者。

### 审核工作报告

Architect 撰写 `output/audit-work-report.md`，并生成一份简洁的 `output/audit-work-report.html` 供用户阅读。报告内容：

- **合同概要**：合同名称、类型、当事方、核心交易结构。取自 shared-context.md
- **工作流程**：本次审核的执行过程——bootstrap → 初设（T-S01/T-S02/T-S03/T-PR）→ 详细审查（各 Audit Agent + Reviewer）→ 汇编（分层合并策略）→ 翻译（T-TRN）→ 修订（T-REV docx-mcp）→ 格式输出。注明每阶段的关键决策、Reviewer 审查结果和异常情况（如有）
- **审核发现摘要**：总体风险评级、高/中/低风险数量统计、风险分布概况、审核维度覆盖情况
- **主要修改点**：逐条列出重要的修改建议——条款编号、问题简述、修改方向、风险等级。让用户无需打开审核意见书全文即可了解最重要的修改内容
- **文件索引**：列出所有产出文件路径，方便用户查找

报告篇幅适中（建议 2000-4000 字），面向用户，语言清晰不含法律黑话。
