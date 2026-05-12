# CLAUDE.md

## 项目概述

这是一个基于 Claude Code 的合同审核 skill 项目。用户提交待审合同，系统产出两样交付物：审核意见书 + 以修订模式标注修改的合同 .docx。

核心架构是 EPC 三层模式（总承包-分包-工具），灵感来自工程总承包管理。系统按合同长度自动选择简单模式（≤5000 字符）或复杂模式（>5000 字符）。

## 角色体系

| 角色 | 技术名 | 定位 |
|------|--------|------|
| 总承包/架构师 | Architect | 唯一用户入口，不做第一手法律分析。负责判断、规划、信息蒸馏、验收。 |
| 分包商/任务代理 | Task Agent | 执行单项任务的 sub-agent。Architect 按需创建，任务完成后销毁。 |
| 监理/审查者 | Reviewer | 复杂模式专用。独立 sub-agent，对照交付标准核查 Task Agent 产出。每次调用为全新实例。 |

**核心原则**：Architect 不亲自做任何法律分析工作。所有读合同、检索法规、分析条款、撰写意见、修订文本均委托 Task Agent 执行。

## 设计文档

以下三份文档记录了完整的设计过程，开发前务必阅读：

1. **`doc/DESIGN.md`** —— 概念设计。EPC 三层模式、工作产品概念、决策上报机制、Reviewer 定位、Task Agent 间一致性保证。
2. **`doc/TECHNICAL-DESIGN.md`** —— 技术设计。开发文件结构（§0）、运行时目录约定（§1）、文档 Schema（§2）、工具清单（§3）、两种模式完整流程（§4-5）、Reviewer 生命周期（§6）、错误处理（§7）、未决设计项（§8）。
3. **`doc/DISCUSSION.md`** —— 设计讨论记录。设计决策的对答过程，仅供参考。

概念设计定义"为什么"，技术设计定义"怎么做"。两份文档已迭代多轮并经过联审，冲突已全部解决。

## 当前状态

入口 skill 框架和全部工具 skill 已开发完成。各工具已通过实际调用测试验证。

- **入口 skill**（`contract-review/`）—— 已完成。SKILL.md、workflows/、references/、schemas/、char-count.sh
- **工具 skill**（`tools/`）—— 已完成并验证。各工具需作为独立 skill 安装到 Claude Code
- **审核规则库**（`contract-review/rules/`）—— 示例文件已创建，律师编写的规则待补充

## 开发路径结构

```
skills/contract/
├── CLAUDE.md                    # 本文件
├── doc/                         # 设计文档（非运行时）
│   ├── DESIGN.md
│   ├── TECHNICAL-DESIGN.md
│   └── DISCUSSION.md
├── contract-review/             # 入口 skill
│   ├── SKILL.md
│   ├── char-count.sh
│   ├── agent/
│   │   ├── task-structure.md
│   │   ├── task-preliminary-report.md
│   │   └── task-assembly.md
│   ├── workflows/
│   │   ├── simple.md
│   │   └── complex.md
│   ├── rules/
│   │   └── construction-contract.md
│   ├── references/
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
└── tools/                       # 工具 skill（各自独立安装）
    ├── docx-cli/
    ├── md-converter/
    ├── yd-law/
    └── qcc/
```

## 关键设计决策（实现时必须遵守）

1. **仅通过 `/contract-review` 命令触发**。不做自动语义匹配触发。
2. **不接受 .doc 格式**。要求用户转换为 .docx 或 PDF 后重新提交。
3. **5000 字符阈值是纯机械判断**。用 `char-count.sh` 获取字符数，不做 AI 判断。
4. **审核立场必须在 bootstrap 阶段向用户确认**。代表哪一方、审核目标、风险偏好——不同立场下同一条款的风险判断截然相反。不得默认假设。
5. **审核规则是 delivery_standards 的底本，不是成品**。规则文件是通用参考，Architect 根据合同实际内容（删减不适用的、补充规则未覆盖的）、用户具体关切和审核立场进行调整。简单模式下同样需要此适配步骤，只是调整幅度较小。
6. **所有 Agent 间通讯使用 Markdown + YAML frontmatter**。frontmatter 承载元数据，body 承载内容。schema 定义在 `schemas/` 下，不得偏离。
7. **Architect 不做第一手法律分析**。所有读合同、检索、分析、撰写、修订工作委托 Task Agent。Architect 自己做的只有判断、规划、信息蒸馏、验收。
8. **工具以 skill 形式存在**。每个 sub-agent 仅注入其任务所需的工具 skill，由 Architect 在创建时决定。
9. **Reviewer 仅复杂模式启用**。每次调用为全新 sub-agent 实例，实例间不共享上下文。循环上限 3 次。
10. **简单模式不启用 Reviewer**。Architect 上下文充裕，自行验收即是最完整审查。
11. **版本号在 frontmatter 中管理，不体现于文件名**。
12. **所有中间产物可追溯**。Task Agent 产出保存在 `_internal/task-records/{task_id}/output.md`，Reviewer 记录保存在同目录 `review-log.md`。
13. **合同文本结构化不是工具，且 Structure Agent 使用固定定义**。识别条款层级需要法律判断，由 Structure Task Agent 完成。所有复杂合同共享同一套经过验证的 system prompt 和交付标准，Architect 直接注入，不自行撰写 task spec。Agent 两遍处理（先读后写），输出附带结构索引表，Reviewer 按索引表逐条搜索原文验证。
14. **reference 文件是参考示例，非强制模板**。Architect 阅读参考示例了解典型结构，根据具体任务自行撰写 task spec，不应照搬填充。

## 工具 skill

以下工具 skill 位于 `tools/` 目录下，各自包含 SKILL.md，需作为独立 skill 安装到 Claude Code：

| Skill 名称 | 功能 | 使用者 |
|-----------|------|--------|
| `mdconverter` | .docx/.pdf/图片 → Markdown。文本 PDF 用 pymupdf4llm，扫描版用 Dashscope 视觉 API，.docx 用 pandoc | Architect（bootstrap） |
| `docx-cli` | python-docx CLI 封装。create/read/paragraph/table/run/image/section/header-footer/properties/style | Task Agent（Structure/Conditions/CrossRef/Revision/Format） |
| `yd-law` | 法律数据库检索。8 个 API：案例/法规/法条的关键词检索、语义检索、详情查询 | Task Agent（Audit） |
| `qcc` | 企业工商信息查询。4 大类 67 个工具 | Task Agent（Audit） |

`char-count.sh` 为本地脚本，位于 `contract-review/` 下，bootstrap 阶段直接执行。

## 未决设计项（已知，不阻塞当前工作）

1. 跨产品一致性审查 Agent（复杂模式下两个 Task Agent 各自自洽但放一起矛盾）
2. 共享上下文更新后已有批准产物的有效性
3. 文件存储与管理基础设施（当前用文件系统 + frontmatter）
4. Phase 1 重入路径（Phase 2 发现初设缺陷时的修正机制）

这些是已识别的技术债务，开发中如遇到相关问题可参考但不必须解决。
