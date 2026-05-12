# 共享上下文 Schema

Architect 编制的跨 Task Agent 共同信息基础。复杂模式下注入所有详细审查 Task Agent 的上下文，确保各方阅读理解合同局部时基于一致的前提假设。

## 适用场景

- Architect 在初设阶段完成后编制。
- 写入路径：`_internal/architect-materials/shared-context.md`
- 注入对象：所有 Phase 2 Task Agent、Reviewer（Phase 2）

## Frontmatter

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `document_type` | string | 是 | 固定值 `shared_context` |
| `version` | integer | 是 | 版本号，从 1 开始递增 |
| `based_on` | string[] | 是 | 所依据的初设文档文件名列表 |
| `created` | datetime | 是 | 创建时间，格式 `YYYY-MM-DD HH:MM` |
| `updated` | datetime | 是 | 最后更新时间，格式 `YYYY-MM-DD HH:MM` |

## Body

Markdown 格式。必须包含以下章节：

### ## 合同基本信息

- 合同类型：（根据合同内容判断，如"建设工程施工合同"）
- 适用法律：（如"中华人民共和国合同法"）
- 管辖：（管辖法院或仲裁机构）

### ## 当事方

逐方列出：身份（发包人/承包人/担保人等）、角色、全文使用的简称约定。

### ## 核心交易结构

一句话概括合同的核心交易安排。

### ## 关键术语定义

贯穿全合同的术语及其统一释义。确保各 Task Agent 使用一致的术语理解。

### ## 审核立场

- 代表方：（审核所代表的当事方）
- 审核目标：（核心关注点，如"控制付款风险""确保交付可执行"）
- 风险偏好：（保守/平衡/进取，影响修改建议的力度）
