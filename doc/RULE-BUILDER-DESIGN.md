# 规则生成器设计思路

## 项目目标

用户指定一份企业合同模板（.docx），系统交付一份可直接用于合同审核系统的规则文件（.md）。

核心思路：**从模板出发，先理解模板的商事安排逻辑和风险分配结构，再通过问答式交互将用户的专业知识提取为结构化审核规则。**

## 问题背景

合同审核系统的有效运转依赖规则文件。编写规则要求用户同时具备三个能力——理解合同条款结构、预判风险点、编写机械可判定检查项。即便对专业律师，从零写一份完整规则也是几个小时的工作。企业用户面对的是空规则库。

模板本身已经包含了企业关心的条款范围，更包含了**该企业设计交易的方式**——它默认把哪些风险推给对方、在哪些地方留了谈判空间、哪些条款互相关联形成保护网。从模板出发理解其商事逻辑，再逐条引导用户确认"这条款对我方意味着什么、底线在哪"，比从零编写效率高得多。

## 总体设计：Architect + Task Agent 两层模式

rule-builder 是独立 skill，不依赖 contract-review 运行。它采用与合同审核系统相同的角色体系，但简化了机制：

- **Architect**：用户唯一入口。不做第一手模板分析。负责判断、委托、验收、与用户交互。
- **Task Agent**：按需创建的 sub-agent 实例，执行单项任务后销毁。
- **不设 Reviewer**（v0.1）。Architect 上下文充裕，自行验收即可。

> 合同模板可能非常长（数万到十几万字符），必须采用 Architect / Task Agent 模式——Architect 不亲自读模板全文做分析，而是委托 Task Agent 执行，自己只做验收和决策。

## Skill 文件结构

```
rule-builder/
├── SKILL.md                          # 入口 skill
└── agent/                            # 固定 Agent 定义
    ├── task-structure.md             # Structure Task Agent
    ├── task-conditions.md            # Conditions Task Agent
    ├── task-crossref.md              # Cross-References Task Agent
    ├── task-question-gen.md          # Question Generation Task Agent
    └── task-rule-gen.md              # Rule Generation Task Agent
```

> 与 contract-review 不同，rule-builder 没有 `workflows/`、`references/`、`schemas/`、`rules/` 子目录。任务类型少且标准化程度高，流程定义直接写在 SKILL.md 中，Agent 定义均为固定模板。

### 角色对照

| 角色 | 技术名 | rule-builder 中的职责 |
|------|--------|---------------------|
| 总负责人 | Architect | 流程控制、立场确认、验收交付物、与用户交互 |
| 结构化 Agent | Structure Task Agent（T-S01） | 将模板 .md 整理为结构化文本（固定定义） |
| 条件提取 Agent | Conditions Task Agent（T-S02） | 提取商业安排结构——不是数字，是交易逻辑（固定定义） |
| 交叉引用 Agent | Cross-References Task Agent（T-S03） | 分析条款间引用关系，揭示起草方保护网（固定定义） |
| 问题生成 Agent | Question Generation Task Agent | 基于初设三文档分析模板，生成问题清单（固定定义） |
| 规则生成 Agent | Rule Generation Task Agent | 将用户回答的清单转化为规则文件（固定定义） |

## 工作流程

```
用户指定模板 .docx
       │
       ▼
[ Bootstrap ]
  ├── 文件格式检查（仅 .docx）
  ├── 创建会话目录
  ├── md-converter 转化 → template.md
  └── 审核立场确认（暂停，等待用户确认代表哪一方）
       │
       ▼
[ 阶段 1：初步设计 ]
  ├── T-S01 Structure（必须先跑——T-S02/T-S03 依赖其编号体系）
  ├── T-S02 Conditions ─┐
  └── T-S03 Cross-Refs  ─┤ 两者依赖 T-S01，彼此独立可并行
       │
       ▼
[ 阶段 2：问题清单生成 ]
  Architect 创建 Question Generation Task Agent
  ├── 注入：conditions 报告 + crossref 报告 + 结构索引表
  ├── 输入：正向标准 + 反向标准 + 30 条上限 + 优先级原则（均在 System Prompt 中）
  │         审核立场（通过上下文文件传递）
  ├── 结构化全文在磁盘上，Agent 可按需通过索引定位后读取
  └── 产出：output/checklist.md
       │
       ▼
[ 用户填写清单 ]（离线进行，用户回答完毕后通知 Architect）
       │
       ▼
[ 阶段 3：规则文件生成 ]
  Architect 创建 Rule Generation Task Agent
  ├── 输入：output/checklist.md（含用户答案）
  └── 产出：output/{规则文件名}.md
       │
       ▼
[ 交付 ]
  向用户报告产出路径：
  output/checklist.md + output/{规则文件名}.md
```

### 阶段详解

### Bootstrap

Architect 亲自执行。四步：文件格式检查（仅 .docx）、创建会话目录并进入、调用 `md-converter` 将模板转化为 `template.md`、**暂停流程**向用户确认审核立场（代表哪一方）。

立场确认是必须确认的根本性决定——立场不同，生成的问题指向截然相反。同一条违约金条款，代表承包方问"比例是否过高"，代表发包方问"比例是否足够约束对方"。

### 阶段 1：初步设计

与合同审核的复杂模式一样，rule-builder 在生成问题之前需要先理解模板的全貌。这不是因为要提取硬数据（模板中大多是占位符），而是因为要理解模板的**商事安排逻辑和风险分配结构**。

**T-S01 Structure（必须先跑）**：将模板按条款层级和编号体系整理为结构化文本，输出含结构索引表。这是纯立场中立的格式处理。T-S02 和 T-S03 依赖其条款编号体系作为定位基准。

**T-S02 Conditions**：提取模板中的**商业安排结构**——不是具体数字（模板里是变量），而是交易逻辑。例如：付款如何分段、各段与什么节点挂钩、质保期从哪个事件起算、违约金是固定金额还是按日计算、终止权是否有前置条件。这些结构在模板中已经存在，不以具体数值是否填写为转移。一份模板的付款条款写的是"预付款 ${X}%，到货款 ${Y}%，质保金 ${Z}%"，变量没有填，但**三段式付款结构**已经存在——这个结构本身就值得生成问题。

**T-S03 Cross-References**：分析条款之间的引用、制约、补充关系。模板起草人通常确保了内部一致性，但"一致性"不等于"对各方公平"。违约条款引用了付款条款的节点定义、终止条款引用了违约条款的构成条件——这些引用链条暴露了起草方的**保护网设计**。不理解这张网，Question Generation Agent 只能问出孤立的问题。

**T-S02 和 T-S03 可并行执行**（均依赖 T-S01 产出，彼此独立）。

Architect 自行验收两份产出：Conditions 是否覆盖了主要商务条款、Cross-References 是否识别了关键引用链。不通过则退回修订。

### 阶段 2：问题清单生成

这是 rule-builder 的核心步骤。与前一版设计的关键区别：Question Generation Agent 不是仅基于结构化全文逐条审视，而是先通过初设三文档建立对模板商事逻辑的全局理解，再生成问题。

**上下文注入策略**——考虑到结构化全文可能很长，不将其全部注入 Agent 上下文：

- **直接注入上下文**：conditions 报告 + crossref 报告 + 结构索引表（章节-条款范围-条数-编号异常）
- **磁盘上可按需读取**：结构化全文（`_internal/template-structured.md`）。Agent 通过索引表定位到特定条款后，通过工具读取原文核实具体措辞

System Prompt 中固化：正向标准（8 大类 36 条）、反向标准（6 大类 20 条）、30 条硬上限、5 级优先级原则。审核立场通过上下文文件传递。

Architect 验收：抽查清单是否覆盖了核心条款（如付款、违约、终止、管辖），问题是否带有明确的立场指向，是否体现了对模板保护网的理解。有问题则退回修订。

### 用户填写清单

清单产出后，Architect 告知用户清单路径。用户离线逐条回答，完成后通知 Architect。此步骤不在 Agent 工作流内——是纯粹的用户编辑。

### 阶段 3：规则文件生成

Architect 创建 Rule Generation Task Agent，将用户回答的清单转化为规则文件。

Architect 验收：检查检查项是否机械可判定（有具体数值/标准），是否遗漏了用户已回答的问题。

### 交付

向用户报告完成，列出交付物路径。

## 会话目录结构

```
rule-builder-{模板名}-{yyyymmdd-hhmm}/
├── original/                          # 用户原始模板（只读）
│   └── {模板名}.docx
├── template.md                        # Bootstrap 格式转化产物
├── output/
│   ├── checklist.md                   # 问题清单（用户在此填写）
│   └── {规则文件名}.md                 # 最终规则文件
└── _internal/
    ├── template-structured.md         # 结构化模板（T-S01 产出，含索引表）
    ├── template-conditions.md         # 商务条件结构报告（T-S02 产出）
    └── template-crossref.md           # 交叉引用分析报告（T-S03 产出）
```

## Agent 定义

### Structure Task Agent（固定定义）

位置：`rule-builder/agent/task-structure.md`

嵌入本 skill，两遍处理、索引表输出、五项错误模式清单。Architect 直接注入，不自行撰写 task spec。

### Conditions Task Agent（固定定义）

位置：`rule-builder/agent/task-conditions.md`

嵌入本 skill。任务：从结构化模板中提取商业安排结构。与 contract-review 的 T-S02 不同——rule-builder 的 Conditions 不追求"可核验数据清单"（模板中无硬数据），而是产出"商业安排结构描述"：付款结构、交付与验收链条、风险分配机制、违约与终止触发逻辑、关键变量的分布位置。这份描述供 Question Generation Agent 建立对模板商业逻辑的全局理解。

### Cross-References Task Agent（固定定义）

位置：`rule-builder/agent/task-crossref.md`

嵌入本 skill。任务：分析条款间的引用、制约、补充关系。与 contract-review 的 T-S03 不同——rule-builder 的 Cross-References 不侧重"冲突检测"（模板起草人已确保内部一致），而是侧重"保护网分析"：哪些条款互相关联形成了对一方的系统性保护、引用链条的核心节点在哪、哪些条款的修改会影响其他条款的有效性。这份分析供 Question Generation Agent 理解模板设计者的意图。

### Question Generation Task Agent（固定定义）

位置：`rule-builder/agent/task-question-gen.md`

正向/反向标准固化在 system prompt 中。Architect 直接注入。审核立场通过上下文文件传递。

**上下文注入**：conditions 报告 + crossref 报告 + 结构索引表（不含结构化正文）。结构化全文在磁盘上按需读取。

### Rule Generation Task Agent（固定定义）

位置：`rule-builder/agent/task-rule-gen.md`

格式转换逻辑固化——清单格式→规则格式的映射规则是恒定的。Architect 直接注入。

> 五种 Agent 均使用固定定义。与 contract-review 不同，rule-builder 没有"参考示例"——每个任务的内容高度标准化。

## 工具注入

| Task Agent | 注入工具 |
|-----------|---------|
| Structure | `docx-cli` — `read`（读取原文核实） |
| Conditions | `docx-cli` — `read`（读取原文核实） |
| Cross-References | `docx-cli` — `read`（读取原文核实） |
| Question Generation | `docx-cli` — `read`（通过索引定位后按需读取结构化全文） |
| Rule Generation | 无工具，纯文本转换 |

Bootstrap 阶段 Architect 调用 `md-converter` skill 做格式转化。

## 与 contract-review 的关系

- **独立运行**：rule-builder 不读取 contract-review 的任何文件，不依赖其 skill 定义。两个 skill 可以独立安装使用。
- **输出对接**：rule-builder 生成的规则文件位于会话目录 `output/` 下。用户可将其复制到 `contract-review/rules/` 目录，供合同审核系统使用。输出格式与合同审核系统的规则文件格式完全一致。
- **知识复用**：Structure Agent 的工作方式（两遍处理、索引表、错误模式）在两个 skill 中相同，但定义各自独立维护。如果一边的设计改进，需要手动同步到另一边。
- **初设阶段的设计同位**：两个 skill 都有初步设计阶段（Structure → Conditions → Cross-References），服务于相同的目标——在深入分析之前建立对合同的全局理解。但交付标准各有侧重：contract-review 侧重可核验性和冲突检测，rule-builder 侧重商业逻辑理解和保护网分析。

## 关键设计决策

1. **独立 skill，自包含**。不依赖 contract-review 路径，所有 Agent 定义嵌入自身 `agent/` 目录。
2. **Architect + Task Agent 两层，不设 Reviewer**（v0.1）。任务串行、Agent 数量少、Architect 上下文可控。
3. **设有初步设计阶段**。T-S01 Structure + T-S02 Conditions + T-S03 Cross-References，与合同审核复杂模式同位。目的是理解模板的商事安排逻辑和风险分配结构，而非提取硬数据。
4. **T-S02 和 T-S03 的交付标准与 contract-review 不同**。Conditions 侧重商业安排结构描述，Cross-References 侧重保护网分析。
5. **五种 Task Agent 均使用固定定义**。任务内容标准化程度高，Architect 直接注入 system prompt，不自撰 task spec。
6. **审核立场在结构化之前确认**。立场影响问题指向，所有分析都需要在明确立场的前提下进行。
7. **Question Generation Agent 的上下文注入为 conditions + crossref + 结构索引**。结构化全文在磁盘上按需读取，避免上下文溢出。
8. **正向/反向标准固化在 Question Generation Agent 的 system prompt 中**。这是经过讨论形成的判断知识，不是可变参数。
9. **30 条硬上限**。抑制过度生成，迫使 Agent 做优先级排序。
10. **仅用于初次生成**。不设迭代回补机制，用户自行维护规则文件。
11. **规则文件以 YAML frontmatter + checkbox body 格式输出**。与 contract-review 的规则文件格式完全一致。

## 未决设计项

1. **超长模板的分段处理**：模板如果超过单 Agent 上下文窗口，Question Generation 可能需要按章节拆分给多个 Agent。v0.1 暂不处理。详细分析见 DISCUSSION.md。

2. **二次生成的效率优化**：用户对同一模板生成不同立场的规则（如先做承包方版，后做发包方版）时，Bootstrap 和初步设计阶段的结果可复用。可仿照 contract-review 增加 `agent/` 目录输出（CLAUDE.md + index.md），使第二次运行能跳过格式转化和初设，直接从立场确认后开始。v0.1 暂不处理。

