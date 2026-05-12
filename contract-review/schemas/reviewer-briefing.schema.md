# Reviewer 背景信息文档 Schema

Architect 从初设文档中提炼的关键参照信息，供 Reviewer Phase 2 在单点实质性审查时使用。

## 适用场景

- Architect 在编制 shared-context.md 后，同步编制此文档。
- 写入路径：`_internal/architect-materials/reviewer-briefing.md`
- 注入对象：所有 Reviewer Phase 2 实例

## Frontmatter

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `document_type` | string | 是 | 固定值 `reviewer_briefing` |
| `version` | integer | 是 | 版本号，从 1 开始递增 |
| `based_on` | string[] | 是 | 所依据的初设文档及 shared-context 文件名列表 |
| `created` | datetime | 是 | 创建时间，格式 `YYYY-MM-DD HH:MM` |

## Body

Markdown 格式。必须包含以下章节：

### ## 可核验数据清单

从合同中提取的硬数据，Reviewer 可据此验证 Task Agent 产出中的事实引用是否准确：

- 金额：（列明各条款中的金额、币种）
- 日期：（开工日、竣工日、付款日、关键节点日期）
- 比例：（违约金比例、付款比例、股权比例等）
- 期限：（质保期、通知期、异议期等）
- 当事方名称：（完整法定名称及简称对应关系）

### ## 条款关系速查

关键引用关系的索引表，Reviewer 可据此快速定位：

- 条款 X 引用条款 Y
- 条款 A 为条款 B 的前提条件
- 条款 C 与条款 D 存在潜在冲突

### ## 高风险区域

联系报告中标注的高风险交叉点和需要提高审查标准的位置。Reviewer 在这些区域应从严审查。

### ## 审查边界

- 审核立场与风险偏好（与 shared-context 一致）
- Reviewer 不可判定的项目范围（对应 task-spec 中的 `architect_only_items`）
- 明确告知 Reviewer：不确定即不标注，不猜测
