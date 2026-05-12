---
name: qcc
description: "企业信息查询 Skill：当用户要求查询特定企业，或回答问题/完成任务需要了解企业背景时调用"
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "🏢"
    requires:
      bins: ["qcc"]
      env: []
---

# 企业信息查询 Skill（qcc）

## 何时使用

当用户有以下需求时，激活本 Skill：

1. **明确查询企业**：用户直接要求查询某家企业的信息
   - 示例："查一下阿里巴巴的企业信息"
   - 示例："帮我调查一下这家公司的背景"

2. **任务需要企业信息**：回答问题或完成任务需要了解企业背景
   - 示例："起草一份与腾讯的合作协议"（需要查询腾讯的注册信息、法定代表人等）
   - 示例："分析一下华为的股权结构"

3. **法律尽职调查**：需要全面了解目标企业的资质和风险状况
   - 示例："对这家公司做尽职调查"
   - 示例："评估一下与这家企业合作的风险"

---

## 工作流程

### 第一步：识别查询意图

**类型A：简单信息查询**
- 用户只需要某项具体信息（如注册号、法定代表人）
- 处理：调用对应工具，直接返回结果

**类型B：企业背景调查**
- 用户需要全面了解企业情况
- 处理：执行标准调查流程（基础信息 → 股东结构 → 风险扫描）

**类型C：尽职调查**
- 用于法律或商业决策的深度调查
- 处理：执行完整尽调流程（企业信息 + 经营状况 + 知识产权 + 风险扫描）

---

### 第二步：查询策略

#### 基础信息（必查）

| 工具 | 服务 | 用途 |
|------|------|------|
| `get_company_registration_info` | company | 核心登记信息：名称、法人、注册资本、成立日期、登记状态、注册地址 |
| `get_shareholder_info` | company | 股东构成、持股比例、认缴出资额 |
| `get_key_personnel` | company | 主要管理人员（董事、监事、高管） |

#### 扩展信息（按需）

| 工具 | 服务 | 用途 |
|------|------|------|
| `get_actual_controller` | company | 实际控制人 |
| `get_beneficial_owners` | company | 受益所有人（反洗钱合规） |
| `get_external_investments` | company | 对外投资布局 |
| `get_branches` | company | 分支机构 |
| `get_annual_reports` | company | 年度报告（从业人数、投资信息） |
| `get_listing_info` | company | 上市信息（股票代码、市值） |
| `get_contact_info` | company | 联系方式、网站 |

#### 经营信息（评估企业活力）

| 工具 | 服务 | 用途 |
|------|------|------|
| `get_qualifications` | operation | 资质证书 |
| `get_administrative_license` | operation | 行政许可 |
| `get_credit_evaluation` | operation | 纳税信用等级、海关信用等级 |
| `get_bidding_info` | operation | 招投标项目 |
| `get_recruitment_info` | operation | 招聘信息（反映业务扩张） |
| `get_financing_records` | operation | 融资历史 |
| `get_news_sentiment` | operation | 舆情监控 |

#### 知识产权（科技企业必查）

| 工具 | 服务 | 用途 |
|------|------|------|
| `get_patent_info` | ipr | 专利信息 |
| `get_trademark_info` | ipr | 商标注册 |
| `get_software_copyright_info` | ipr | 软件著作权 |
| `get_copyright_work_info` | ipr | 作品著作权 |
| `get_standard_info` | ipr | 参与制定标准 |

#### 风险扫描（合规必查）

| 工具 | 服务 | 用途 |
|------|------|------|
| `get_dishonest_info` | risk | 失信被执行人 |
| `get_judgment_debtor_info` | risk | 被执行人信息 |
| `get_high_consumption_restriction` | risk | 限制高消费 |
| `get_administrative_penalty` | risk | 行政处罚 |
| `get_business_exception` | risk | 经营异常名录 |
| `get_serious_violation` | risk | 严重违法失信名单 |
| `get_judicial_documents` | risk | 法院判决文书 |
| `get_case_filing_info` | risk | 法院立案信息 |
| `get_equity_freeze` | risk | 股权冻结 |
| `get_equity_pledge_info` | risk | 股权出质 |
| `get_chattel_mortgage_info` | risk | 动产抵押 |
| `get_bankruptcy_reorganization` | risk | 破产重整 |

---

### 第三步：执行查询

#### 调用方式

```bash
qcc <服务名> <工具名> --searchKey "企业名称或统一社会信用代码"
```

#### 示例调用

```bash
# 查询企业基本信息
qcc company get_company_registration_info --searchKey "腾讯科技（深圳）有限公司"

# 查询股东信息
qcc company get_shareholder_info --searchKey "腾讯科技（深圳）有限公司"

# 查询失信信息
qcc risk get_dishonest_info --searchKey "腾讯科技（深圳）有限公司"

# 查询专利信息
qcc ipr get_patent_info --searchKey "腾讯科技（深圳）有限公司"
```

---

### 第四步：信息整合

根据查询结果，整理输出：

1. **企业概况**：注册信息、成立时间、注册资本、法定代表人
2. **股权结构**：股东构成、实际控制人、受益所有人
3. **经营状况**：资质许可、信用等级、业务动态
4. **知识产权**：专利、商标、著作权（如适用）
5. **风险状况**：诉讼、执行、行政处罚、经营异常

---

## 注意事项

### 信息准确性

- 优先使用 **统一社会信用代码** 查询，避免同名企业混淆
- 数据更新频率不同（T+0 至 T+7），注意时效性标注

### 数据完整性

- 部分企业信息可能未公开（如非上市公司股东详情）
- 新注册企业数据可能存在滞后

### 隐私合规

- 查询结果仅供工作使用，不得用于非法用途
- 注意保护企业敏感信息（如联系方式、详细地址）

### 工具选择原则

| 场景 | 推荐工具组合 |
|------|-------------|
| 快速了解 | 企业基本信息 + 股东信息 |
| 合作评估 | 基本信息 + 风险扫描 + 信用评价 |
| 投资尽调 | 完整流程（企业+经营+知识产权+风险） |
| 诉讼准备 | 风险信息全量查询（判决文书+立案+执行） |

---

## 输出格式

### 标准报告模板

```
【企业基本信息】
- 企业名称：
- 统一社会信用代码：
- 法定代表人：
- 注册资本：
- 成立日期：
- 登记状态：
- 注册地址：

【股权结构】
- 股东构成：（列表）
- 实际控制人：（如有）
- 受益所有人：（如有）

【经营状况】
- 主要资质：（列表）
- 信用评级：
- 近期动态：（招投标/融资/招聘）

【知识产权】（如适用）
- 专利数量：
- 商标数量：
- 软件著作权：

【风险提示】
- 涉诉情况：
- 被执行情况：
- 行政处罚：
- 经营异常：
- 其他风险：

【结论建议】
- 综合评价：
- 注意事项：
```

---

## 参考文档

- TECHNICAL.md — 完整工具列表和调用方式
