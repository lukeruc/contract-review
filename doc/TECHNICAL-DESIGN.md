# 合同审核系统详细设计

## 0. 开发文件结构

以下为开发阶段本项目（skill）的源文件布局，区别于运行时为用户合同创建的会话目录。

```
skills/contract/
├── doc/                          # 设计文档（非运行时）
│   ├── DESIGN.md
│   ├── TECHNICAL-DESIGN.md
│   └── DISCUSSION.md
├── contract-review/              # 入口 skill
│   ├── SKILL.md
│   ├── char-count.sh
│   ├── workflows/                # 可执行的流程定义，Architect 按任务阶段读取执行
│   │   ├── simple.md
│   │   └── complex.md
│   ├── rules/                    # 审核规则库（律师编写维护）
│   │   ├── construction-contract.md
│   │   ├── equity-transfer.md
│   │   └── ...
│   ├── agent/                    # 固定 Agent 定义（强制模板，直接注入）
│   │   ├── task-structure.md
│   │   ├── task-preliminary-report.md
│   │   └── task-assembly.md
│   ├── references/               # Task Agent 与 Reviewer 参考示例
│   │   ├── reviewer.md
│   │   ├── task-audit.md
│   │   ├── task-revision.md
│   │   ├── task-structure.md
│   │   ├── task-conditions.md
│   │   ├── task-crossref.md
│   │   ├── task-assembly.md
│   │   └── task-format.md
│   └── schemas/
│       ├── task-spec.schema.md
│       ├── work-product.schema.md
│       ├── review-log.schema.md
│       ├── shared-context.schema.md
│       └── reviewer-briefing.schema.md
└── tools/                        # 工具 skill
    ├── docx-cli/                 # python-docx CLI 封装
    ├── md-converter/             # .docx/.pdf → Markdown
    ├── yd-law/                   # 法律数据库检索
    └── qcc/                      # 企业工商信息查询
```

---

## 1. 目录与文件约定

### 1.1 根目录与会话目录

系统在当前 workspace 下创建会话目录，所有文件操作在会话目录内进行：

```
./
└── contract-review-{合同名}-{yyyymmdd-hhmm}/
```

合同名从原文件名提取（去掉扩展名），时间戳为会话创建时刻。每次审核独立一个会话目录，可追溯、不互相干扰。Architect 创建目录后 `cd` 进入，此后所有路径相对于会话目录。

### 1.2 会话目录结构

```
{会话目录}/
├── original/                                 # 用户原始文件（只读保留，不改动）
│   └── 工程总承包合同.docx
├── contract.md                               # bootstrap 格式转化产物
├── output/                                   # 最终交付物
│   ├── preliminary-report.md               # 初步情况报告（仅复杂模式）
│   ├── audit-opinion.md                     # 审核意见书
│   └── 工程总承包合同-revised.docx             # 修订模式
├── agent/                                    # 对话续接入口（Architect 交付后创建）
│   ├── CLAUDE.md                             # 上下文快照，新实例自动加载
│   └── index.md                              # 全部工作产品文件索引
└── _internal/
    ├── architect-materials/
    │   ├── shared-context.md                 # 简单模式含审核立场；复杂模式含完整上下文
    │   ├── reviewer-briefing.md              # 仅复杂模式
    │   └── work-plan.md                      # 仅复杂模式
    ├── preliminary-design/                   # 仅复杂模式，初步设计阶段 Task Agent 产出
    │   ├── 01-structured-contract.md
    │   ├── 02-contract-conditions.md
    │   └── 03-cross-references.md
    └── task-records/                         # 每任务一个子目录
        ├── T-001/
        │   ├── task-spec.md                  # 任务规格书（Architect → Task Agent）
        │   ├── output.md                     # Task Agent 交付的工作产品
        │   └── review-log.md                 # Reviewer 审查记录（含多轮）；仅复杂模式
        ├── T-002/
        │   └── ...
        └── ...
```

### 1.3 命名规范

| 类别 | 命名规则 | 示例 |
|------|---------|------|
| 会话目录 | `{合同名}-{yyyymmdd-hhmm}` | `工程总承包合同-20260509-1430` |
| Architect 物料 | 固定英文名 | `shared-context.md`、`reviewer-briefing.md`、`work-plan.md` |
| 初设文档 | `{NN}-{英文描述}.md` | `01-structured-contract.md` |
| 任务子目录 | `{task_id}/` | `T-001/` |
| 规格书 | `task-spec.md`（在任务子目录下，以目录区分归属） | `T-001/task-spec.md` |
| Task Agent 产出 | `output.md`（在任务子目录下） | `T-001/output.md` |
| Reviewer 记录 | `review-log.md`（在任务子目录下） | `T-001/review-log.md` |
| 最终交付物 | `{英文描述}.docx` | `audit-opinion.md`、`{原合同名}-revised.docx` |

版本号不体现在文件名中，通过各文件自身的 YAML frontmatter 管理。Reviewer 各轮审查在 `review-log.md` 正文中以 `## Round N` 区分。

---

## 2. 文档 Schema

所有 Agent 间通讯使用 Markdown + YAML frontmatter。frontmatter 为系统元数据，body 为内容。

### 2.1 任务规格书（Architect → Task Agent）

```yaml
---
task_id: "T-001"
task_type: "audit" | "revision" | "cross-reference" | "structure" | "conditions" | "assembly" | "format" | "custom"
status: "draft" | "in_review" | "done" | "failed"
version: 1
input_files:
  - "contract.md"
  - "_internal/architect-materials/shared-context.md"
output_file: "_internal/task-records/T-001/output.md"
delivery_standards: []      # Reviewer 检查项清单（机械可判定）
architect_only_items: []    # Architect 亲审项，Reviewer 不评
created: "YYYY-MM-DD HH:MM"
---
# 任务描述

（正文：具体任务说明、范围边界、特殊要求）
```

- `task_type` 决定 Task Agent 的行为模式，由 Architect 根据任务需要自主决定，以上为常用类型。
- `input_files` 中的 `shared-context.md` 仅在复杂模式下注入。
- `delivery_standards` 每条为一个机械可判定检查项。
- `architect_only_items` 为 Reviewer 不可判定、需 Architect 亲审的项。

### 2.2 工作产品（Task Agent 产出）

```yaml
---
task_id: "T-001"
work_product: "audit-opinion" | "structured-contract" | "contract-conditions" | "cross-references" | "revised-contract" | "custom"
version: 1
status: "draft"
depends_on: []              # 依赖的其他 task_id
created: "YYYY-MM-DD HH:MM"
updated: "YYYY-MM-DD HH:MM"
---
# 正文

（Task Agent 的产出内容）
```

### 2.3 Reviewer 审查记录

```yaml
---
task_id: "T-001"
review_round: 1             # 第几轮审查，从 1 开始
result: "pass" | "fail" | "escalate"
phase: "phase1" | "phase2"
created: "YYYY-MM-DD HH:MM"
---
# 审查记录

## 逐项检查结果
- [x] 检查项 1 —— 通过
- [ ] 检查项 2 —— 不通过，原因：...

## 审查意见（不通过时填写）
（具体问题描述）

## Task Agent 回应（第 2 轮起填写）
（上一轮问题的修正说明）
```

### 2.4 共享上下文（Architect 产出）

```yaml
---
document_type: "shared_context"
version: 1
based_on: ["01-structured-contract", "02-contract-conditions", "03-cross-references"]
created: "YYYY-MM-DD HH:MM"
updated: "YYYY-MM-DD HH:MM"
---
# 共享项目上下文

## 合同基本信息
- 合同类型：
- 适用法律：
- 管辖：

## 当事方
（身份、角色、简称约定）

## 核心交易结构
（一句话概括）

## 关键术语定义
（贯穿全合同的术语及其统一释义）

## 审核立场
- 代表方：
- 审核目标：
- 风险偏好：
```

### 2.5 Reviewer 背景信息文档（Architect 产出）

```yaml
---
document_type: "reviewer_briefing"
version: 1
based_on: ["01-structured-contract", "02-contract-conditions", "03-cross-references", "shared-context"]
created: "YYYY-MM-DD HH:MM"
---
# Reviewer 背景信息

## 可核验数据清单
（金额、日期、比例、期限、当事方名称等硬数据）

## 条款关系速查
（关键引用关系、对应的合同条款编号）

## 高风险区域
（联系报告中标注的高风险交叉点、需提高审查标准的位置）

## 审查边界
（审核立场、风险偏好、Reviewer 不可判定的项目范围）
```

### 2.6 审核规则文件（律师编写，Architect 加载）

规则文件由专业律师按合同类型编写，存放于 `contract-review/rules/`。文件名规范：`{contract_type_en}.md`。Architect 通过扫描所有规则文件的 frontmatter 完成分类匹配，不设索引文件。

```yaml
---
contract_type: "建设工程施工合同"
contract_type_en: "construction-contract"
applicable_when: "合同主要内容为发包人委托承包人进行工程建设"
version: "1.0"
---
# 审核规则

## 一、合同主体与资质
- [ ] 核查承包人是否具备相应施工资质等级
- [ ] 核查分包限制与转包禁止条款
- ...

## 二、工程范围与工期
- [ ] 工程范围的描述是否明确无歧义
- [ ] 开工、竣工日期是否明确
- [ ] 工期延误的责任分配与违约金
- ...

## 三、工程款与支付
- [ ] 合同价款类型（固定总价/可调价/成本加酬金）
- [ ] 付款节点与比例是否合理
- [ ] 变更洽商的价格调整机制
- ...

（后续章节按该合同类型的审核要点逐条列举）
```

---

## 3. 工具清单

工具是 Task Agent 赖以获取信息和处理文件的设施。所有工具以 skill 形式存在。工具不做法律判断，只完成机械操作。

Architect 在创建每个 sub-agent（Task Agent 或 Reviewer）时，仅为其注入该任务所需的工具，不注入全量。例如，负责审查付款条款的 Task Agent 获得 `yd-law` 和 `qcc`，但不获得 `docx-cli`；负责格式编排的 Task Agent 获得 `docx-cli`，但不获得法律检索工具。

合同文本结构化（识别条款层级、编号体系、章节边界）不是工具——它需要法律判断（识别某段文字是条款还是叙述），由 Structure Task Agent 完成。

### 3.1 输入工具（外部格式 → Markdown）

| 工具名 | 用途 | 状态 |
|--------|------|------|
| `md-converter` | 将 .docx / .pdf / 图片 转为 Markdown。文本 PDF 用 pymupdf4llm，扫描版 PDF 和图片用 Dashscope 视觉 API，.docx 用 pandoc | 已开发 |

### 3.2 信息工具（查询 → Markdown）

| 工具名 | 用途 | 状态 |
|--------|------|------|
| `yd-law` | 检索中国法规、判例、法条。8 个 API：案例/法规/法条的关键词检索、语义检索、详情 | 已开发 |
| `qcc` | 查询企业工商信息。4 大类 67 个工具：企业信息、经营动态、知识产权、风险扫描 | 已开发 |

### 3.3 处理工具

| 工具名 | 用途 | 状态 |
|--------|------|------|
| `char-count` | 获取纯文本字符数，用于 5000 字符阈值判断 | 已开发 |

### 3.4 文档处理工具

`docx-cli` 将 python-docx 能力封装为 CLI 命令。不对修订操作做黑盒封装——Task Agent 通过原子命令组合完成修订，避免一步操作中丢失位置精度和控制权。

| 子命令 | 操作 | 说明 |
|--------|------|------|
| `create` | 新建 .docx | 创建空白文档或基于模板 |
| `read` | .docx → 文本展示 | 展示段落、表格、样式等 |
| `paragraph` | 段落增删改 | add/update/delete/list |
| `table` | 表格操作 | add/delete/cell/rows/cols/list |
| `run` | 内联格式 | add/update/list（加粗、字体、颜色、上下标等） |
| `image` | 图片 | add/list |
| `section` | 节属性 | add/update/list（页面尺寸、边距、方向） |
| `header-footer` | 页眉页脚 | add/list |
| `properties` | 文档属性 | get/set（标题、作者、日期等） |
| `style` | 样式 | list |

状态：已开发。

### 3.5 工具按需注入

每个 sub-agent 可调用哪些工具，由 Architect 在创建时根据任务需要决定。以下为典型注入方案，非硬性规定——Architect 可根据具体合同和任务调整。

| Task Agent 类型 | 注入工具 |
|-----------------|---------|
| Structure（T-S01） | `docx-cli` — `read` 读取原文 |
| Conditions（T-S02） | `docx-cli` — `read` 读取原文 |
| Cross-References（T-S03） | `docx-cli` — `read` 读取原文 |
| Audit（T-001 等） | `yd-law`（法律检索）、`qcc`（工商查询） |
| Revision（T-002/T-REV） | `docx-cli` — `create`/`paragraph`/`table`/`run`/`read` 等全命令 |
| Assembly（T-ASM） | 无工具，纯 Markdown 文本合并 |
| Format（T-FMT） | `docx-cli` — `create`/`paragraph`/`table`/`run`/`section`/`header-footer` |

| 调用者 | 注入工具 |
|--------|---------|
| Reviewer（Phase 1） | `docx-cli` — `read`（抽查核验原文） |
| Reviewer（Phase 2） | `docx-cli` — `read`（抽查核验原文） |
| Architect | `char-count`（bootstrap 阶段判断复杂度） |

---

## 4. 简单模式流程

```
[用户提交合同.docx/pdf]
       │
       ▼
[ bootstrap: 格式转化 → contract.md，原始文件 → original/ ]
       │
       ▼
[ 创建会话目录，字符数 ≤ 5000？否 → 走复杂模式 ]
       │ 是
       ▼
[ 确认审核立场：识别当事方 → 暂停流程请用户确认代表方/审核目标/风险偏好 ]
       │
       ▼
[ Architect 读 contract.md，判断合同类型 ]
       │
       ▼
[ Architect 扫描 rules/ 目录 frontmatter，匹配对应规则文件 ]
  - 匹配成功 → 加载规则
  - 无匹配 → 报告用户选择合同类型
       │
       ▼
[ Architect 根据规则制定 delivery_standards，创建 Audit Task Agent（T-001）]
  - 输入：contract.md + 规则文件
  - 产出：_internal/task-records/T-001/output.md（审核意见书正文）
       │
       ▼
[ Architect 验收审核意见书 ]
  - 对照 contract.md + delivery_standards 自行验收
  - 通过 → 继续 | 不通过 → 重建 T-001 重新执行
       │ 通过
       ▼
[ Architect 创建 Revision Task Agent（T-002）]
  - 输入：contract.md + _internal/task-records/T-001/output.md
  - 产出：_internal/task-records/T-002/output.md（含修订后的合同 Markdown）
       │
       ▼
[ Architect 验收修订稿 ]
  - 对照审核意见书逐条核验修订内容
  - 通过 → 继续 | 不通过 → 重建 T-002 重新执行
       │ 通过
       ▼
[ 审核意见书：T-001/output.md → output/audit-opinion.md（直接复制，不生成 .docx）]
[ T-002 调用 docx 工具：修订 Markdown → output/{原合同名}-revised.docx（修订模式，每处修订附批注）]
       │
       ▼
[ 交付：output/audit-opinion.md + output/{原合同名}-revised.docx ]
       │
       ▼
[ Architect 编制 agent/ 对话续接文件 ]
  - agent/CLAUDE.md：合同速览、审查结论摘要、修订概况、文件索引指引、常见追问导航、Agent 自我认知
  - agent/index.md：全部工作产品文件索引
```

简单模式不启用 Reviewer——Architect 上下文充裕，自行验收即是最完整的审查。

---

## 5. 复杂模式流程

### 5.1 初步设计阶段

```
[ 字符数 > 5000，进入复杂模式 ]
       │
       ▼
[ 确认审核立场：识别当事方 → 暂停流程请用户确认代表方/审核目标/风险偏好 ]
       │
       ▼
[ T-S01 Structure Task Agent（必须先跑——无依赖）]
  - 输入：contract.md
  - 产出：_internal/preliminary-design/01-structured-contract.md（正文 + 结构索引表同文件）
  - **固定 Agent 定义**：system prompt 和交付标准预设，Architect 直接注入，不自撰 task spec
  - **两遍处理**：第一遍只读建立全局编号认知；第二遍逐段输出并填索引表
  - **输出格式**：正文用 Markdown 标题层级（#/##/###/####）；附加索引表（章节-条款范围-条数-异常标注）
  - **错误模式清单**：system prompt 显式列明编号跳跃、附件误读、编号藏在正文中等已知陷阱
       │
       ▼ Reviewer Phase 1 审查 T-S01 — 索引表驱动核查
  - 拿到 contract.md + 结构化产出（含索引表）
  - 按索引表逐条搜索原文验证：条款编号存在于原文预期位置、层级归属与索引标注一致、条数计数正确
  - 每次检查为一次精确匹配，不依赖注意力覆盖全文
  - Reviewer 同样使用固定定义，Phase 1 对所有 T-S01 实例统一
  - 通过后继续
       │
       ▼
[ T-S02 Conditions + T-S03 Cross-References（并行）]
  - 两者均依赖 T-S01 的条款编号体系和章节边界
  ├── T-S02 输入：contract.md + 01-structured-contract.md
  │    产出：_internal/preliminary-design/02-contract-conditions.md
  └── T-S03 输入：contract.md + 01-structured-contract.md
       产出：_internal/preliminary-design/03-cross-references.md
       │
       ▼ Reviewer Phase 1 审查 T-S02、T-S03，均通过后继续
       │
       ├──────────────────────────────────────────┐
       ▼                                          ▼
[ T-PR Preliminary Report Agent ]      [ Architect 编制管理物料 ]
  - 预定义 Agent，直接注入                  - 合同类型判断 → 规则匹配
  - 输入：三份初设文档                      - shared-context.md
  - 产出：output/preliminary-report         - reviewer-briefing.md
    (.md + .docx)                           - work-plan.md
  - 与 Architect 并行执行                   - T-PR 并行执行
       │                                          │
       └──────────────┬───────────────────────────┘
                      ▼
             [ 两者均完成后，进入 Phase 2 ]
  - 借助简报判断合同类型 → 扫描 rules/ 匹配规则文件
  - 无匹配 → 报告用户选择
  - _internal/architect-materials/shared-context.md    （基于三份初设文档提炼）
  - _internal/architect-materials/reviewer-briefing.md （从初设文档提取关键数据、关系、风险标注）
  - _internal/architect-materials/work-plan.md          （详细审查阶段的审查维度与分包方案，规则文件为制定各任务 delivery_standards 的底本）
```

### 5.2 详细审查阶段

```
[ Architect 按 work-plan 创建审查 Task Agent ]
  - 每个 Task Agent 注入 shared-context.md
  - Architect 决定各 Task Agent 的依赖关系（串行/并行）
       │
       ▼
[ 对每个 Task Agent 执行 ]
  ├── Architect 下达 task-spec.md
  ├── Task Agent 执行，产出 output.md
  ├── Reviewer Phase 2 审查（独立实例，最多 3 轮）
  └── Reviewer 放行 → Architect 验收
       │
       ▼ 所有审查 Task Agent 完成
       │
       ▼
[ Architect 汇编审核意见书 — 固定 Agent + 分层合并 ]
  - 对所有 Audit 产出运行 char-count.sh 求和
  - ≤10万字 → 单次合并（一个 Assembly Agent 处理全部）
  - >10万字 → 分层合并（分组→第一层并行→Reviewer抽样→第二层串行→Reviewer抽样）
  - Assembly Agent 使用固定定义 agent/task-assembly.md，直接注入
  - 每层 Review：Reviewer 抽样 3×N 条验证合并忠实性（存在性、风险等级、描述完整性）
  - 最终产出 → _internal/task-records/T-ASM-01/output.md
  - Architect 最终验收审核意见书
       │ 通过
       ▼
[ Architect 创建 Revision Task Agent（T-REV）]
  - 输入：contract.md + T-ASM-01/output.md
  - 产出：_internal/task-records/T-REV/output.md（修订后的合同 Markdown）
  - Reviewer Phase 2 审查 → Architect 验收
       │ 通过
       ▼
[ Format Task Agents ]
  - 审核意见书：T-ASM-01/output.md → output/audit-opinion.md（直接复制，不生成 .docx）
  - T-FMT-01：修订 Markdown + original/ 原始文件 → output/{原合同名}-revised.docx（修订模式，每处修订附批注）
       │
       ▼
[ 最终交付：preliminary-report.md + audit-opinion.md + {原合同名}-revised.docx ]
       │
       ▼
[ Architect 编制 agent/ 对话续接文件 ]
  - agent/CLAUDE.md：合同速览、审查结论摘要、修订概况、文件索引指引、常见追问导航
  - agent/index.md：所有工作产品的文件索引
  - 用户此后在 agent/ 路径下新开 Claude Code 实例即可直接进入对话状态
```

---

## 6. Reviewer 生命周期

- 每次调用创建一个全新的 sub-agent 实例。
- 实例之间不共享任何上下文。
- system prompt 和核心判断立场所有实例相同。
- 上下文内容（工作要求 / shared context / reviewer briefing / 交付标准）由 Architect 在创建实例时注入。
- 任务完成或判定失败后实例销毁。

**Phase 1 与 Phase 2 上下文对比**：

| | Phase 1 | Phase 2 |
|---|---|---|
| system prompt | ✓ | ✓ |
| 工作要求 | ✓ | |
| Task Agent 交付物 | ✓ | ✓ |
| 交付标准 | ✓（附在工作要求中） | ✓（来自 task-spec） |
| shared context | | ✓ |
| reviewer briefing | | ✓ |

---

## 7. 错误处理

| 场景 | 处置 |
|------|------|
| Reviewer 第 1-2 轮不通过 | Reviewer 将审查意见退回 Task Agent 修订 |
| Reviewer 第 3 轮仍不通过 | Reviewer 向 Architect 报告任务失败，附失败记录；Architect 决定调整交付标准、更换 Task Agent、或亲自介入 |
| 简单模式 Architect 验收不通过 | Architect 重建该环节的 Task Agent 重新执行 |
| 格式转化失败 | 向用户报告，要求提供可读取的合同文件 |
| Phase 2 发现初设文档存在遗漏 | 已知设计缺口，当前由 Architect 在验收组装阶段识别并临时处置 |

---

## 8. 未决的详细设计项

1. **跨产品一致性审查** —— Reviewer Phase 2 做单点实质审查，不覆盖"两个 Task Agent 各自产出自洽但放一起矛盾"的语义冲突。是否、何时、如何引入独立审查 Agent 待定。
2. **共享上下文更新后的产物有效性** —— Architect 更新 shared-context.md 后，此前 Reviewer 已批准的产出基于旧上下文，是否仍有效、是否需重新审查，待定。
3. **文件存储与管理基础设施** —— 当前约定使用文件系统 + Markdown frontmatter 做版本标识，不提供可查询可 diff 的版本管理。待定。
4. **Phase 1 重入路径** —— Phase 2 发现初设文档缺陷时，Architect 如何修正（重建 Task Agent vs 临时填补），待定。
