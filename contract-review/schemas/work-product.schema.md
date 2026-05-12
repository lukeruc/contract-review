# 工作产品 Schema

Task Agent 产出时使用的通讯格式。所有 Task Agent 的输出必须遵循此 Schema。

## 适用场景

- Task Agent 完成任务后，将产出写入 `output.md`。
- 写入路径：`_internal/task-records/{task_id}/output.md`

## Frontmatter

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 对应的任务 ID，与 task-spec 一致 |
| `work_product` | enum | 是 | 工作产品类型 |
| `version` | integer | 是 | 产品版本号，从 1 开始递增 |
| `status` | enum | 是 | 当前状态 |
| `depends_on` | string[] | 否 | 依赖的其他 task_id 列表 |
| `created` | datetime | 是 | 创建时间，格式 `YYYY-MM-DD HH:MM` |
| `updated` | datetime | 是 | 最后更新时间，格式 `YYYY-MM-DD HH:MM` |

### work_product 枚举值

| 值 | 说明 |
|----|------|
| `audit-opinion` | 审核意见书章节或全文 |
| `structured-contract` | 结构化合同文本 |
| `contract-conditions` | 关键合同条件报告 |
| `cross-references` | 合同内交叉引用分析 |
| `revised-contract` | 含修订标注的合同文本 |
| `custom` | 自定义产品，正文中说明类型 |

### status 枚举值

| 值 | 说明 |
|----|------|
| `draft` | 初稿，Task Agent 初次产出 |
| `reviewed` | 已通过 Reviewer 审查（复杂模式） |
| `approved` | 已通过 Architect 最终验收 |
| `rejected` | 被退回，需修订 |

## Body

Markdown 格式。内容结构由 `work_product` 类型决定，正文自由组织。建议以 `# 标题` 开头。
