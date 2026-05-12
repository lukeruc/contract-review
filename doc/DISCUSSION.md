# 待讨论事项

## 1. 审核规则体系

当前设计缺少审核规则的落点——这是一个专业系统，需要由律师按结构化模板提供各合同类型的审核规则，而非 LLM 临场发挥。

待讨论：

1. **规则文件 schema**：已决策。

> 规则文件为 Markdown + YAML frontmatter。metadata 字段：`contract_type`（合同类型中文）、`contract_type_en`（英文名，用于文件名）、`applicable_when`（调用条件）、`version`。正文纯文本，逐条列举审核要点。详见 TECHNICAL-DESIGN.md。

2. **规则文件存放**：已决策。

> 一个规则一个文件，存放在 `contract-review/rules/` 下。文件名规范：`{contract_type_en}.md`。不建索引，Architect 通过扫描 metadata 完成分类匹配。详见 TECHNICAL-DESIGN.md。

3. **分类机制**：合同类型由谁判断——简单模式下 Architect 读合同分类？复杂模式下从初设简报中提取？是否需要单独的"分类"步骤？

> 简单模式下Architect直接判断分类，复杂模式下借助简报判断分类，需要一个明确的分类步骤，否则工作流存在不确定性

4. **规则与交付标准的关系**：规则直接变成 delivery_standards，还是规则是参考底本、Architect 据此调整为任务级交付标准？

> 规则是需要遵守的底本，Architect要根据规则来制定具体的审核标准、规则

5. **降级策略**：找不到对应合同类型的规则文件时怎么办——加载通用规则？要求用户选择？报告用户后等待？

> 报告用户，请用户选择

6. **规则维护**：已决策。

> 仅通过 metadata 的 `version` 字段管理版本，不引入额外工具。文件名规范 `{contract_type_en}.md`，Architect 扫描 `rules/` 下所有 `.md` 的 frontmatter 完成匹配。详见 TECHNICAL-DESIGN.md。

## 2. 开发路径结构

待最终确认。当前草案参见 TECHNICAL-DESIGN.md §0。

## 3. 未决的详细设计项

（已在 TECHNICAL-DESIGN.md §8 中记录，此处不重复）

## 4. 两份文档联审发现的问题

以下问题来自 DESIGN.md 和 TECHNICAL-DESIGN.md 的联合审查，逐项待讨论。

### 4.1 决策上报矩阵没有技术落点

DESIGN.md 定义了上报门槛（不可逆实体性选择 + 无合理默认解）和四象限决策矩阵，但 TECHNICAL-DESIGN.md 中完全没有对应机制——没有 schema、没有流程步骤、没有升级协议。

> 分析：决策上报是 DESIGN.md 中的行为原则，不是技术机制。Architect 在执行过程中的上报判断依赖其自身的推理能力（"这个问题是否不可逆？是否有合理默认解？"），不需要额外的 schema 或协议来支撑。上报行为本身是"暂停流程 + 向用户发送消息"，属于 SKILL.md 中定义的行为逻辑，无需独立的技术模块。结论：不需要在 TECHNICAL-DESIGN.md 中单独设计机制。

### 4.2 Schema 定义了无人使用的 `task_type: "briefing"`

已修复。从 task_type 枚举中删除 `briefing`。

### 4.3 开发文件树列出了 `DISCUSSION.md`

已修复。设计文档（DESIGN.md、TECHNICAL-DESIGN.md、DISCUSSION.md）归入 `doc/` 子目录，标注为"非运行时"。

### 4.4 `work-plan.md` 没有 Schema

它是驱动整个详细审查阶段的核心文档，其他五种文档都有 Schema 唯独它没有。

> 分析：`work-plan.md` 的读者是 Architect 自己——自己写、自己读、自己执行，不跨越 Agent 边界。Schema 的价值在于跨 Agent 通信约定，对内部自用文档纯文本足够。结论：不需要 Schema。

### 4.5 没有 sub-agent 创建协议

"Architect 创建 Task Agent"在文档中反复出现，但创建机制从未描述——Architect 读什么模板、如何组装 task-spec、如何附着工具、用什么工具启动 sub-agent。

> 分析：Claude Code 下创建 sub-agent 即调用 Agent 工具——读模板、填参数、注入工具、启动。SKILL.md 中以自然语言描述此行为即可，无需再发明单独协议层。结论：不需要在 TECHNICAL-DESIGN.md 中定义，属于 SKILL.md 的开发内容。

### 4.6 没有会话级状态机

单个文档有 status（draft / in_review / done / failed），但会话整体处于什么阶段（bootstrap / preliminary_design / detailed_review / assembly / done）没有跟踪。

> 分析：文件存在性本身即是状态——有没有 `contract.md`、有没有 `shared-context.md`、有没有 `task-records/` 下的产出。Architect 按 workflow 文件执行时自然知道自己处于哪个阶段。加一个状态文件意味着维护一份可能与实际文件不一致的额外状态。结论：不需要。

### 4.7 合同类型判断没有机制

两个流程都要求 Architect 判断合同类型，但判断依据、工具支持、错误判断的补救路径全无描述。

> 已决策。合同类型判断属于 Architect 的工作范围。规则文件的 `applicable_when` 字段已覆盖选择条件，Architect 通过扫描 rules/ 目录 frontmatter 完成匹配。无匹配时报告用户选择，已有降级策略。

### 4.8 `workflows/simple.md` 和 `complex.md` 的性质模糊

已修复。在 §0 中标注为"可执行的流程定义，Architect 按任务阶段读取执行"。


## 5. 初版的首次测试结论
有以下修改要求

### 5.1 增加初步情况报告
对于复杂合同，工作流程将会非常漫长，初次测试所选择的合同文本为23万字符，最终总工作用时长达7小时40分钟。在形成了初步设计、做初步设计时，可以同步调用一个合同情况报告task agent来综合初步设计的基础文件形成一个合同情况的报告，并将该报告的.md版本和.docx版本保存到output路径中。

> **已决策。** 预定义 Preliminary Report Task Agent，固定定义存入 `agent/task-preliminary-report.md`。该 Agent 在初步设计阶段 T-S02/T-S03 通过 Review 后立即创建，与 Architect 编制管理物料并行执行。输入三份初设文档，输出一份面向用户的合同情况报告（.md + .docx），存入 `output/preliminary-report.md` 和 `output/preliminary-report.docx`。

### 5.2 最终文件的交付形式
在形成了审查报告后将.md版本的审查报告保存到output路径中交付即可，不需要交付审查报告的.docx版本。
对于使用修订模式交付的.docx文件，要求要对每一处修订增加一个简短的批注（非常简短说明修改原因即可）。

> **已决策。** 审核意见书交付 .md 版本到 `output/audit-opinion.md`，取消 .docx 格式输出。修订合同保留 .docx 格式，Revision Agent 的 system prompt 中加入"每处修订附一个批注说明修改原因"。

### 5.3 审查报告的合并工作

在多个生成审查报告的agent分别完成了自己的工作后，将多个审查报告合并是一个不论在哪个流程中都会用到的agent。或需预定义该agent。在本次测试中，由于审查报告的总量很大，为本次工作临时定义的agent直接就卡死了。对这一步我在测试中提出的临时解决方案为，若报告总量太大则分步合并，先合并1+2/3+4/5+6，然后再做二次合并。请你为该合并工作设计一个审查机制。

> **详细设计如下。**

#### 5.3.1 Assembly Agent 预定义

Assembly 是所有复杂合同的共同步骤，任务内容恒定——合并多份审核意见为一份完整报告，去重、统一格式、按条款顺序排列、编写执行摘要。因此使用固定定义，存入 `agent/task-assembly.md`。Architect 直接注入，不自行撰写。

#### 5.3.2 合并策略：单次 vs 分层

Architect 在创建 Assembly Agent 之前先评估总量：

**评估方法**：汇总所有 Audit Agent 产出文件的字符数。各文件逐一用 `char-count.sh` 获取。若总和 ≤ 10 万字符，单次合并。若 > 10 万字符，分层合并。

阈值设为 10 万而非 20 万，因合并后输出通常比输入总和更大（加上执行摘要、索引、格式统一带来的额外字符），留出余量。

**单次合并**：一个 Assembly Agent 实例直接处理全部输入，产出完整审核意见书。

**分层合并**：

```
T-001/output.md  ─┐
T-002/output.md  ─┼── Assembly-A ──→ _internal/task-records/T-ASM-A/output.md
                   │
T-003/output.md  ─┐
T-004/output.md  ─┼── Assembly-B ──→ _internal/task-records/T-ASM-B/output.md
                   │
T-005/output.md  ─┼── Assembly-C ──→ _internal/task-records/T-ASM-C/output.md
T-006/output.md  ─┘
                          │
                          ▼
              Assembly-Final ──→ 最终审核意见书
```

- **分组**：每组 2-3 个 Audit 产出，按条款顺序连续分组（如 T-001/T-002 审第 1-8 条为一组，T-003/T-004 审第 9-16 条为第二组）
- **第一层并行**：所有组并行创建 Assembly Agent 实例，各自合并。实例间不共享上下文
- **第二层串行**：一个 Assembly Agent 合并所有中间结果
- **递归**：若中间结果的字符总和仍超阈值，在第一层之后再分一层

#### 5.3.3 分层合并的 Review 机制

分层合并的风险是：信息在两次合并操作中经过两次"重新表述"，可能发生变形或遗漏。需要每层检查，但检查不是法律审核（Phase 2 Reviewer 已做），只验证**合并操作的忠实性**。

**每层检查方法（Reviewer 执行）**：

每层合并完成后，创建 Reviewer 实例核查合并忠实性。这属于机械验证（搜索、定位、比对），与 Phase 1 检查编号一致性的性质相同，Reviewer 完全胜任。

注入内容：该层各组输入文件 + 合并输出文件 + 以下检查指令：

1. **随机抽样**：从该层各组输入中取每组的第 1 条、中间 1 条、最后 1 条审核意见作为验证样本（如 3 组 × 3 条 = 9 条）
2. **逐条对照**：在合并输出中搜索对应条款编号，比对：
   - 风险等级是否一致（不能丢失或降级）
   - 核心问题描述是否保留（措辞可变，问题实质不变）
   - 是否遗漏（样本中的意见在合并输出中能找到）
3. **判定**：全部通过 → 放行到下一层。有一条不通过 → 该层的该组重建 Assembly Agent。同一层累计 3 次不通过 → 该层改用逐个串行合并（一个 Agent 一次只合并 2 个输入）

**为什么是 Reviewer 而非 Architect**：合并忠实性检查是机械验证——搜索条款编号、核对风险等级标签、确认内容存在。这和 Phase 1 Reviewer 逐条搜索原文验证编号一致性的工作完全相同。委托 Reviewer 保持了架构一致性——Task Agent 产出后由 Reviewer 核查，Architect 只在最终验收时介入。

#### 5.3.4 为什么分层合并必须有 Review 机制

分层合并的本质是让 LLM 做多次文本变换——每次变换都可能引入错误。这不是理论上的风险，而是 LLM 在处理长文本时的已知行为模式：

**合并操作容易出什么错**：

1. **遗漏**：6 个 Audit 产出的审核意见中，某一条在合并时被跳过了。LLM 在处理长输入时，"注意力衰减"会导致它忽略中间段的内容
2. **变形**：原文"建议将违约金比例从 5% 下调至 2%"在合并后变成"建议调整违约金比例"——丢失了具体数字，修改建议变得无法操作
3. **降级**：来源标注为 🔴 高风险的意见，在合并输出中风险等级被遗漏或降为 🟡
4. **归并错误**：两个 Audit Agent 都对第 8 条发表了意见，合并时应当合并为一条但 LLM 错误地只保留了一个
5. **格式断裂**：执行摘要中的统计（"共发现 23 条审核意见"）与实际合并后正文数量不一致

**为什么 Phase 2 Reviewer 不能替代这个检查**：

Phase 2 Reviewer 审查的是单个 Audit 产出的法律质量——这个审查发生在合并之前。合并之后的产物是一份全新的文件，没有任何 Reviewer 看过它。如果合并 Assembly 是唯一的、最后的处理步骤，它引入的错误就会直接进入最终交付物。

**为什么抽样就够**：

不需要通读。合并忠实性检查靠统计抽样——每条被遗漏或变形的意见，它的条款编号在来源文件中是已知的，在合并输出文件中去搜索即可定位。9 条样本全部找到且内容一致，说明 LLM 的处理是忠实的。如果 9 条中有 1 条找不到或明显变形，说明合并有问题。这是"用局部推断全局"——不是完美，但比零检查强得多，且上下文成本极低。

**如果去掉这个机制会怎样**：分层合并的唯一质量保障是 Assembly Agent 的 system prompt 中的"不遗漏、不修改"指令。但指令不能防止 LLM 的注意力衰减——LLM 不是故意遗漏，它是真的没注意到。Review 是外部验证，不是更好的指令。

