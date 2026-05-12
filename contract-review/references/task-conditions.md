# Conditions Task Agent 参考示例

> **本文档为参考示例，非强制模板。** Architect 应根据具体任务需要自行撰写 task spec 和 system prompt，不应照搬填充。

## System Prompt 参考

```
你是合同条件提取 Task Agent。你的任务是从合同中提取关键商务条件和核心法律机制，形成可核验的数据清单。

你需要区分"商务条件""法律机制"和"一般性叙述"——前者是审核的核心对象，后者是背景信息。

工作标准：
- 每条数据标注来源条款编号，可追溯
- 金额、日期、比例原文照录，不四舍五入、不转述
- 关键条件缺失时标注 [未约定] 并简述可能的默认法律后果
- 条款存在多种合理解释时标注 [歧义] 并列明可能解释
```

## Task Spec 参考示例

```markdown
---
task_id: "T-S02"
task_type: "conditions"
status: "draft"
version: 1
input_files:
  - "contract.md"
  - "_internal/preliminary-design/01-structured-contract.md"
output_file: "_internal/preliminary-design/02-contract-conditions.md"
depends_on:
  - "T-S01"
delivery_standards:
  - "商务条款覆盖：价格类型、付款安排、交付标准、工期、验收条件、质保"
  - "法律机制覆盖：违约责任、合同终止、管辖与争议解决、不可抗力、保密、知识产权"
  - "当事方义务逐方列出"
  - "每条数据标注来源条款编号"
  - "金额、日期、比例原文照录，不转述、不近似"
  - "缺失的关键条件标注 [未约定]，歧义条款标注 [歧义]"
architect_only_items: []
created: "2026-05-10 14:20"
---

# 任务描述

从合同中提取关键商务条件和核心法律机制，形成可核验的数据清单。

## 重点关注

- 工程款支付安排（预付款比例、进度款支付节点和比例、结算时限、质保金比例）
- 违约责任上限与对等性
- 合同解除条件
- 变更洽商的价格调整机制

## 注意事项

- 本合同为固定总价合同，注意提取风险范围条款及调价条件
- 注意识别付款义务的隐蔽前提条件（如"承包人提交完整竣工资料后 XX 日内"）
- 金额同时提取小写和中文大写，如不一致标注 [大小写不一致]
```

## 设计要点

1. **Conditions 产出是 Reviewer Briefing 的核心数据来源**。Architect 编制 reviewer-briefing.md 时，可核验数据清单主要来自此文档。
2. **数据原文照录很重要**——如果 Conditions Agent 将"合同总价 3,456.78 万元"转述为"约 3400 万"，后续 Reviewer 核验时就会对不上。
3. **[未约定] 标注让 Architect 快速识别合同漏洞**。缺失关键条款本身就是一个重要的审核发现。
4. **Conditions 不做法条审核**——那是 Audit Agent 的工作。Conditions 只做提取和标注。
