# 任务规格书 Schema

Architect 向 Task Agent 下达任务时使用的通讯格式。

## 适用场景

- Architect 创建 Task Agent 时，按此 Schema 组装任务规格书。
- 写入路径：`_internal/task-records/{task_id}/task-spec.md`

## Frontmatter

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务唯一标识，格式 `T-XXX`（简单模式）或 `T-SXX`（初设阶段） |
| `task_type` | enum | 是 | 任务类型，决定 Task Agent 行为模式 |
| `status` | enum | 是 | 当前状态 |
| `version` | integer | 是 | 规格书版本号，从 1 开始递增 |
| `input_files` | string[] | 是 | 注入 Task Agent 上下文的文件路径列表（相对于会话根目录） |
| `output_file` | string | 是 | Task Agent 产出文件路径（相对于会话根目录） |
| `delivery_standards` | string[] | 否 | Reviewer 检查项清单，每条为机械可判定检查项 |
| `architect_only_items` | string[] | 否 | Architect 亲审项，Reviewer 不评 |
| `created` | datetime | 是 | 创建时间，格式 `YYYY-MM-DD HH:MM` |

### task_type 枚举值

| 值 | 说明 |
|----|------|
| `audit` | 法律审核，产出一份审核意见书章节 |
| `revision` | 合同修订，在合同文本上以修订模式标注修改 |
| `cross-reference` | 合同内交叉引用分析，识别条款间的引用与冲突关系 |
| `structure` | 合同结构化，识别条款层级与编号体系 |
| `conditions` | 关键条件提取，提取商务条件与法律机制 |
| `assembly` | 文本汇编，合并多个 Task Agent 产出为完整文档 |
| `format` | 格式输出，将 Markdown 转为 .docx |
| `custom` | 自定义任务，正文中说明具体要求 |

### status 枚举值

| 值 | 说明 |
|----|------|
| `draft` | 草稿，Architect 正在编写或已下达 |
| `in_review` | Reviewer 正在审查（仅复杂模式） |
| `done` | 任务完成，已通过验收 |
| `failed` | 任务失败，Reviewer 3 轮后仍未通过或 Architect 判定不可接受 |

## Body

Markdown 格式。必须包含以下章节：

### # 任务描述

具体任务说明：审查范围、关注重点、排除事项。

### # 范围边界

明确此任务覆盖什么、不覆盖什么。

### # 特殊要求

（可选）补充约束条件，如必须引用的法条、必须对照的合同条款编号、格式要求等。
