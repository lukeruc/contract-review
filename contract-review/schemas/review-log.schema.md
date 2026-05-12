# 审查记录 Schema

Reviewer 审查 Task Agent 产出后撰写的审查记录。

## 适用场景

- Reviewer 完成审查后，将记录写入任务子目录。
- 写入路径：`_internal/task-records/{task_id}/review-log.md`
- 多轮审查在同一文件中以 `## Round N` 区分，每轮更新 frontmatter 中的 `review_round`。

## Frontmatter

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 被审查的任务 ID |
| `review_round` | integer | 是 | 第几轮审查，从 1 开始 |
| `result` | enum | 是 | 本轮审查结果 |
| `phase` | enum | 是 | 审查阶段 |
| `created` | datetime | 是 | 审查完成时间，格式 `YYYY-MM-DD HH:MM` |

### result 枚举值

| 值 | 说明 |
|----|------|
| `pass` | 通过，放行给 Architect 验收 |
| `fail` | 不通过，退回 Task Agent 修订（第 1-2 轮） |
| `escalate` | 上报，3 轮后仍不通过，报告 Architect |

### phase 枚举值

| 值 | 说明 |
|----|------|
| `phase1` | 初设阶段审查，仅做形式审核 |
| `phase2` | 详细审查阶段，具备单点实质性审查能力 |

## Body

Markdown 格式。必须包含以下章节：

### ## 逐项检查结果

逐条对照 delivery_standards 的检查清单，格式：

```
- [x] 检查项描述 —— 通过
- [ ] 检查项描述 —— 不通过，原因：...
```

### ## 审查意见

（result 为 `fail` 或 `escalate` 时填写）

具体问题描述，分条列出需修正的内容及原因。

### ## Task Agent 回应

（第 2 轮起填写，由 Task Agent 在修订后补充）

对上一轮审查意见的逐条回应，说明修改方式及位置。
