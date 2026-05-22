# CLAUDE.md

## 项目概述

这是一个基于 Claude Code 的合同智能审核系统，包含两个协同工作的 skill：

- **contract-review** — 合同审核模块。接收待审合同，产出审核意见书 + 以修订模式标注修改的合同 .docx。
- **rule-builder** — 规则生成模块。接收企业合同模板，通过问答式交互自动生成审核规则文件。

两个模块的关系：rule-builder 产出审核规则存入 `rules/`，contract-review 加载规则执行审核。

核心架构是 EPC 三层模式（Architect - Task Agent - Reviewer），灵感来自工程总承包管理。按合同字符数建议处理模式（阈值 10000），用户最终确认。

## 角色体系

| 角色 | 技术名 | 定位 |
|------|--------|------|
| 总负责人 | Architect | 唯一用户入口，**不做第一手法律/模板分析**。负责判断、规划、委托 Task Agent、信息蒸馏、验收交付物。 |
| 任务代理 | Task Agent | 执行单项任务的 sub-agent 实例（`general-purpose`），任务完成后销毁。Architect 按需创建。 |
| 质量监理 | Reviewer | 仅 contract-review 复杂模式启用。独立 sub-agent，对照交付标准核查 Task Agent 产出。每次调用为全新实例，循环上限 3 次。 |

**核心原则**：Architect 不亲自做任何法律分析或模板分析工作。所有读合同/模板、检索法规、分析条款、撰写意见、修订文本、生成问题均委托 Task Agent 执行。Architect 只做判断、规划、信息蒸馏、验收。

## 设计文档

| 文档 | 内容 | 状态 |
|------|------|------|
| `doc/DESIGN.md` | contract-review 概念设计。EPC 三层模式、工作产品、决策上报、Reviewer 定位 | 已迭代稳定 |
| `doc/TECHNICAL-DESIGN.md` | contract-review 技术设计。目录约定、Schema、工具清单、双模式流程、Reviewer 生命周期 | 已迭代稳定 |
| `doc/RULE-BUILDER-DESIGN.md` | rule-builder 完整设计。Architect+Task Agent 两层、初设阶段、问题生成引擎、Skill 文件结构 | v0.1 已完成 |
| `doc/PROJECT-STATUS.md` | 面向非技术领导的汇报文档。两个 skill 的工作原理和开发状态 | 定期更新 |
| `doc/DISCUSSION.md` | 活跃讨论记录。当前话题：结构化耗时优化（scan-structure.py）、英文合同适配 | 动态更新 |
| `doc/workflow.html` | 可视化流程图。两个 skill 完整流程和架构展示 | 随设计同步更新 |

概念设计定义"为什么"，技术设计定义"怎么做"。开发前务必查阅对应文档。

## 当前状态

| 模块 | 核心设计 | 代码 | 测试 |
|------|---------|------|------|
| contract-review | 已完成 | 已完成 | 实测中，优化处理速度 |
| rule-builder | 已完成 | v0.1 已完成 | 实测中 |
| 底层工具 | 已完成 | 已完成 | 已通过测试 |
| 审核规则库 | — | 示例文件 | 待律师编写 |

已完成的主要工作：
- 完整的 EPC 三层架构设计
- contract-review 双模式流程（简单 + 复杂 7 阶段）
- rule-builder 5 Agent 固定定义 + 初设阶段
- docx-mcp 替代 revise.py，MCP 原生修订标记支持，eliminate OOXML 手工构造风险
- scan-structure.py 预扫描脚本，消除 Structure Agent 第一遍通读
- 底层工具：mdconverter、docx-mcp、yd-law、qcc

## 开发路径结构

```
skills/contract/
├── CLAUDE.md                         # 本文件
├── README.md                         # GitHub README
├── doc/                              # 设计文档（非运行时）
│   ├── DESIGN.md
│   ├── TECHNICAL-DESIGN.md
│   ├── RULE-BUILDER-DESIGN.md
│   ├── PROJECT-STATUS.md
│   ├── DISCUSSION.md
│   └── workflow.html
├── contract-review/                  # 合同审核 skill
│   ├── SKILL.md                      # 入口
│   ├── scripts/                         # 本地脚本（Bash/Python）
│   │   ├── char-count.sh
│   │   ├── scan-structure.py
│   │   └── add-paraids.py
│   ├── agent/                        # 固定 Agent 定义（强制模板）
│   │   ├── task-structure.md         # T-S01 结构化
│   │   ├── task-preliminary-report.md# T-PR 初步情况报告
│   │   └── task-assembly.md          # T-ASM 审核意见汇编
│   ├── workflows/                    # 流程定义
│   │   ├── simple.md                 # 简单模式（≤10000）
│   │   └── complex.md                # 复杂模式（EPC 全机制）
│   ├── rules/                        # 审核规则库（律师编写）
│   │   ├── construction-contract.md
│   │   └── nda.md
│   ├── references/                   # 参考示例（非强制模板）
│   │   ├── reviewer.md
│   │   ├── task-audit.md
│   │   ├── task-revision.md
│   │   ├── task-structure.md
│   │   ├── task-conditions.md
│   │   ├── task-crossref.md
│   │   ├── task-assembly.md
│   │   └── task-format.md
│   └── schemas/                      # Agent 间通讯格式
│       ├── task-spec.schema.md
│       ├── work-product.schema.md
│       ├── review-log.schema.md
│       ├── shared-context.schema.md
│       └── reviewer-briefing.schema.md
├── rule-builder/                     # 规则生成 skill（独立）
│   ├── SKILL.md                      # 入口
│   ├── scripts/                       # 本地脚本
│   │   └── scan-structure.py
│   └── agent/                        # 固定 Agent 定义（强制模板）
│       ├── task-structure.md         # T-RB-S01 模板结构化
│       ├── task-conditions.md        # T-RB-S02 商业安排结构提取
│       ├── task-crossref.md          # T-RB-S03 保护网分析
│       ├── task-question-gen.md      # T-RB-S04 问题清单生成
│       └── task-rule-gen.md          # T-RB-S05 规则文件生成
└── tools/                            # 工具 skill（各自独立安装）
    ├── md-converter/                 # 文档转 Markdown
    ├── yd-law/                       # 法律数据库检索
    ├── qcc/                          # 企业工商信息查询
    └── requirements.txt
```

## 两个 Skill 的流程概览

### contract-review

```
Bootstrap（格式转化 → 字符数 → 立场/模式/修订人确认）
    │
    ├── 简单模式（≤10000，用户可选择切换）
    │     1. 合同类型判断 + 规则匹配
    │     2. Audit Agent 审查全合同 → Architect 验收
    │     3. Translation Agent 产出 revisions.json（操作手册）
    │     4. Revision Agent 用 docx-mcp 执行修订
    │     5. 交付 + 对话续接
    │
    └── 复杂模式（EPC 全机制）
          阶段 1：初步设计
            ├── scan-structure.py 预扫描
            ├── T-S01 Structure → Reviewer 索引表核查
            ├── T-S02 Conditions + T-S03 CrossRef 并行 → Reviewer 审查
            └── T-PR 初步报告 + Architect 编制管理物料（并行）
          阶段 1.5：初设后确认（用户可选暂停）
          阶段 2：多 Audit Agent 并行审查 → Reviewer Phase 2
          阶段 3：Assembly 汇编（分层合并）
          阶段 4：Translation Agent 产出 revisions.json → Revision Agent 用 docx-mcp 修订
          阶段 5：格式输出
          阶段 6：交付
          阶段 7：对话续接 + 审核工作报告
```

### rule-builder

```
Bootstrap（格式转化 → 立场确认）
    │
    阶段 1：初步设计
      ├── scan-structure.py 预扫描
      ├── T-RB-S01 Structure
      ├── T-RB-S02 Conditions + T-RB-S03 CrossRef 并行
    阶段 2：T-RB-S04 问题清单生成
      （注入 conditions + crossref + 结构索引；结构化全文磁盘按需读取）
    用户填写清单
    阶段 3：T-RB-S05 规则文件生成
    交付 + agent/ 目录（二次生成效率优化）
```

## 关键设计决策（实现时必须遵守）

### 通用原则

1. **仅通过 slash command 触发**。`/contract-review` 和 `/rule-builder`，不做语义匹配。
2. **不接受 .doc 格式**。要求用户转换为 .docx 或 PDF 重新提交。
3. **Architect 不做第一手分析**。所有读、检索、分析、撰写、修订工作委托 Task Agent。
4. **审核立场必须在 bootstrap 阶段向用户确认**。代表哪一方、审核目标、风险偏好——不同立场下风险判断截然相反。rule-builder 同样在结构化之前确认立场。
5. **所有 Agent 间通讯使用 Markdown + YAML frontmatter**。schema 定义在 `schemas/` 下。
6. **工具以 skill 形式存在**，按需注入 sub-agent。每个 sub-agent 仅获得其任务需要的工具。
7. **固定 Agent 定义由 Architect 直接注入**，不自行撰写或修改 task spec。
8. **Reference 文件是参考示例，非强制模板**。Architect 阅读参考了解典型结构，根据具体任务自行撰写。
9. **Sub-agent 写入文件使用 Bash**（`cat > file <<'EOF'`），不依赖 Write 工具（可能存在权限限制）。

### contract-review 专属

10. **10000 字符为建议阈值，用户最终决定模式**。用 `char-count.sh` 获取字符数，系统给建议，用户确认。
11. **审核规则是 delivery_standards 的底本，不是成品**。Architect 根据合同实际内容和用户关切进行调整。
12. **Reviewer 仅复杂模式启用**。每次调用为全新 sub-agent 实例，循环上限 3 次。简单模式由 Architect 自行验收。
13. **scan-structure.py 预扫描**：复杂模式 T-S01 之前运行，机械提取编号体系为 JSON，Agent 跳过第一遍通读直接进入结构化输出。支持中英文合同。
14. **Structure Agent 两遍处理 → 预扫描跳过第一遍**。扫描脚本秒级完成编号体系提取，Agent 只做验证和格式化。
15. **Assembly 分层合并**：审计产出总字符 ≤10 万单次合并，>10 万分组合并 + Reviewer 抽样检查忠实性。
16. **修订合同 .docx 每处修订附批注**（1-2 句修改原因）。
17. **修订人姓名在 bootstrap 确认**，默认"审核方"。
18. **修订阶段分两步：翻译 → 修订**。Translation Agent（T-TRN）将审核意见书（说理报告）转换为结构化操作手册 revisions.json。Revision Agent（T-REV）使用 docx-mcp 按操作手册逐条在 .docx 上执行修订。翻译和修订的职责分离，各 Agent 上下文可控。
19. **Revision Agent 使用 docx-mcp 原生 MCP 工具**，不需 Bash。解决了 sub-agent Bash 权限问题，且修订标记由成熟库保证 OOXML 正确性，避免手工构造 XML 的不可靠性。
20. **修订前须预处理 paraId**。docx-mcp 依赖 `w14:paraId` 定位段落——旧版 Word 生成的 .docx 可能缺失此属性。Architect 在修订阶段前用 `add-paraids.py` 原地补充。
21. **复杂模式初设后默认暂停等待用户确认**（用户可选自动继续）。
22. **交付后创建 agent/ 目录**（CLAUDE.md + index.md），支持对话续接。

### rule-builder 专属

23. **独立 skill，自包含**。不依赖 contract-review 路径，所有 Agent 定义嵌入自身 `agent/` 目录。
24. **不设 Reviewer（v0.1）**。Task Agent 数量少、任务串行、Architect 上下文充裕。
25. **设有初步设计阶段**（T-RB-S01 → T-RB-S02+T-RB-S03），与 contract-review 同位。目的是理解模板的商事安排逻辑和风险分配结构。
26. **T-RB-S02 侧重商业安排结构描述**（不是数据提取）；**T-RB-S03 侧重保护网分析**（不是冲突检测）。
27. **Question Generation Agent 上下文注入为 conditions + crossref + 结构索引**。结构化全文在磁盘上按需读取，避免上下文溢出。
28. **正向标准 36 条 + 反向标准 20 条 + 30 条硬上限**。固化在 System Prompt 中。
29. **仅用于初次生成**。不设迭代回补机制，用户自行维护规则文件。
30. **规则文件以 YAML frontmatter + checkbox body 格式输出**。与 contract-review 规则格式完全一致。

## 工具 skill

| Skill 名称 | 类型 | 功能 | 调用者 |
|-----------|------|------|--------|
| `mdconverter` | 文档转换 | .docx/.pdf/图片 → Markdown。文本 PDF 用 pymupdf4llm，扫描版用 Dashscope 视觉 API，.docx 用 pandoc | Architect（bootstrap） |
| `docx-mcp` | 文档编辑 | MCP 原生 Word 文档编辑。支持修订标记（`<w:del>`/`<w:ins>`）、批注、段落插入、脚注等。要求文档有 `w14:paraId` 属性（缺失时用 `add-paraids.py` 预处理）。Revision Agent 通过 MCP 工具直接操作，不需 Bash | Revision Agent（T-REV） |
| `yd-law` | 法律检索 | 法律数据库检索，8 个 API：案例/法规/法条的关键词与语义检索、详情查询 | Task Agent（Audit） |
| `qcc` | 企业查询 | 企业工商信息查询，4 大类 67 个工具 | Task Agent（Audit） |

**本地脚本**（位于各 skill 目录下，Bash 直接执行）：

| 脚本 | 位置 | 用途 |
|------|------|------|
| `char-count.sh` | `contract-review/scripts/` | 纯文本字符数统计，用于 10000 字符阈值建议和汇编总量评估 |
| `scan-structure.py` | `contract-review/scripts/` + `rule-builder/scripts/` | 中英文合同编号体系机械扫描，输出 JSON（条款编号、行号范围、层级、异常）。秒级完成，替代 Structure Agent 第一遍通读 |
| `add-paraids.py` | `contract-review/scripts/` | 为 .docx 所有段落添加 `w14:paraId` 属性。docx-mcp 依赖此属性定位段落，旧版 Word 生成的文档可能缺失。Architect 在修订前执行 |

## 未决设计项

1. **跨产品一致性审查 Agent** — 复杂模式下两个 Audit Agent 各自自洽但放一起可能存在语义矛盾。留待后续设计。
2. **共享上下文更新后已有批准产物的有效性** — Architect 更新 shared-context 后，此前基于旧上下文批准的产出是否仍然有效。留待后续设计。
3. **结构化并行章节处理** — 当前为单 Agent 处理 + scan-structure.py 预扫描。超大型合同的并行章节结构化方案已讨论（DISCUSSION.md），未实现。
4. **规则库扩展** — 当前仅有一个示例规则文件。需要通过 rule-builder 或律师手工编写扩充。

这些是已识别的技术债务，不阻塞当前工作。
