# 企业信息查询 Skill 技术手册（qcc）

本文件记载 qcc 工具调用方式和技术细节。

---

## 一、工具概述

qcc 是一个企业信息查询 CLI 工具，提供 4 大类服务，共 67 个查询工具：

| 服务 | 工具数量 | 用途 |
|------|----------|------|
| `company` | 14 | 企业基本信息、股东结构、分支机构、上市信息 |
| `operation` | 13 | 经营动态、资质许可、信用评价、舆情监控 |
| `ipr` | 6 | 知识产权：专利、商标、著作权、标准 |
| `risk` | 34 | 风险扫描：诉讼、执行、失信、行政处罚 |

---

## 二、调用方式

### 基本语法

```bash
qcc <服务名> <工具名> --参数 值
```

### 全局选项

```bash
qcc -V, --version    # 显示版本号
qcc -h, --help       # 显示帮助信息
```

### 查看工具列表

```bash
# 列出所有服务
qcc list-tools

# 列出指定服务的工具
qcc list-tools company
qcc list-tools operation
qcc list-tools ipr
qcc list-tools risk
```

---

## 三、服务与工具详情

### 1. company（企业信息）- 14 个工具

#### get_company_registration_info（核心登记信息）

```bash
qcc company get_company_registration_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：企业名称、统一社会信用代码、法定代表人、注册资本、成立日期、登记状态、注册地址

**适用场景**：验证企业身份、了解基本概况

---

#### get_shareholder_info（股东信息）

```bash
qcc company get_shareholder_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：投资人姓名、持股比例、认缴出资额、出资时间

**适用场景**：股权结构分析、实际控制人识别

---

#### get_key_personnel（主要管理人员）

```bash
qcc company get_key_personnel --searchKey "企业名称或统一社会信用代码"
```

**返回**：姓名、职务（董事、监事、高管）

**适用场景**：管理团队了解、核心人员识别

---

#### get_actual_controller（实际控制人）

```bash
qcc company get_actual_controller --searchKey "企业名称或统一社会信用代码"
```

**返回**：实际控制人详情

**适用场景**：企业风险评估、关联交易识别

---

#### get_beneficial_owners（受益所有人）

```bash
qcc company get_beneficial_owners --searchKey "企业名称或统一社会信用代码"
```

**返回**：受益所有人信息

**适用场景**：反洗钱合规（AML）、穿透式监管分析

---

#### get_branches（分支机构）

```bash
qcc company get_branches --searchKey "企业名称或统一社会信用代码"
```

**返回**：分支机构名称、负责人、地区、成立日期、登记状态

**适用场景**：了解企业组织架构

---

#### get_change_records（变更记录）

```bash
qcc company get_change_records --searchKey "企业名称或统一社会信用代码"
```

**返回**：变更事项、变更前后内容、变更日期

**适用场景**：股权变更跟踪、经营范围调整查询

---

#### get_company_profile（企业简介）

```bash
qcc company get_company_profile --searchKey "企业名称或统一社会信用代码"
```

**返回**：企业简介

**适用场景**：企业画像构建、业务分析

---

#### get_annual_reports（年度报告）

```bash
qcc company get_annual_reports --searchKey "企业名称或统一社会信用代码"
```

**返回**：报告年度、经营状态、从业人数、股东股权转让、投资信息

**数据更新**：每年更新（通常6月前）

---

#### get_external_investments（对外投资）

```bash
qcc company get_external_investments --searchKey "企业名称或统一社会信用代码"
```

**返回**：被投资企业名称、状态、成立日期、持股比例、认缴出资额

**适用场景**：分析企业投资布局

---

#### get_listing_info（上市信息）

```bash
qcc company get_listing_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：上市日期、股票简称、股票代码、上市交易所、总市值、总股本

**适用场景**：投资分析

---

#### get_contact_info（联系方式）

```bash
qcc company get_contact_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：电话号码、邮箱、企业网站、ICP备案

**适用场景**：拓客、获取企业联系方式

---

#### get_tax_invoice_info（税号开票信息）

```bash
qcc company get_tax_invoice_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：纳税人识别号、企业类型、地址、电话、开户行、账号

**适用场景**：财务开票

---

#### verify_company_accuracy（信息核验）

```bash
qcc company verify_company_accuracy --searchKey "统一社会信用代码" --name "企业名称"
```

**返回**：名称、法人、统一社会信用代码的匹配性

**适用场景**：企业实名认证、准入资质初审

---

### 2. operation（经营信息）- 13 个工具

#### get_qualifications（资质证书）

```bash
qcc operation get_qualifications --searchKey "企业名称或统一社会信用代码"
```

**返回**：证书类型、等级、有效期、状态

**适用场景**：专业能力评估、行业准入资格确认

---

#### get_administrative_license（行政许可）

```bash
qcc operation get_administrative_license --searchKey "企业名称或统一社会信用代码"
```

**返回**：行政许可信息

**适用场景**：合法经营资质核查、业务准入审查

---

#### get_credit_evaluation（信用评价）

```bash
qcc operation get_credit_evaluation --searchKey "企业名称或统一社会信用代码"
```

**返回**：纳税信用等级、海关信用等级、评价年度、评价单位

**适用场景**：税务合规性核查、海关资质评估

---

#### get_bidding_info（招投标信息）

```bash
qcc operation get_bidding_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：项目名称、中标情况、项目金额、招标单位

**适用场景**：业务拓展分析、市场份额评估

---

#### get_recruitment_info（招聘信息）

```bash
qcc operation get_recruitment_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：发布日期、招聘职位、月薪、学历、经验、办公地点

**适用场景**：人才需求分析、业务扩张判断

---

#### get_financing_records（融资信息）

```bash
qcc operation get_financing_records --searchKey "企业名称或统一社会信用代码"
```

**返回**：创投融资、上市融资、增发融资

**适用场景**：成长轨迹追踪、投融资历史分析

---

#### get_news_sentiment（舆情信息）

```bash
qcc operation get_news_sentiment --searchKey "企业名称或统一社会信用代码"
```

**返回**：新闻标题、发布时间、情感倾向

**适用场景**：声誉监控、品牌形象分析、危机预警

---

#### get_import_export_credit（进出口信用）

```bash
qcc operation get_import_export_credit --searchKey "企业名称或统一社会信用代码"
```

**返回**：海关信用等级、备案日期、经营类别

**适用场景**：国际贸易合作评估

---

#### get_spot_check_info（抽查检查）

```bash
qcc operation get_spot_check_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：检查实施机关、类型、日期、结果

**适用场景**：经营资质核查

---

#### get_telecom_license（电信许可）

```bash
qcc operation get_telecom_license --searchKey "企业名称或统一社会信用代码"
```

**返回**：许可证号、业务分类、覆盖范围、是否有效

**适用场景**：电信业务合规性评估

---

#### get_company_announcement（企业公告）

```bash
qcc operation get_company_announcement --searchKey "企业名称或统一社会信用代码"
```

**返回**：上市企业各类公告

**适用场景**：重大动态追踪、披露信息核查

---

#### get_honor_info（荣誉信息）

```bash
qcc operation get_honor_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：荣誉名称、类型、级别、认证年份

**适用场景**：企业声誉评估

---

#### get_ranking_list_info（榜单信息）

```bash
qcc operation get_ranking_list_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：榜单名称、榜内排名、来源、发布日期

**适用场景**：资本运作分析

---

### 3. ipr（知识产权）- 6 个工具

#### get_patent_info（专利信息）

```bash
qcc ipr get_patent_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：专利信息

**适用场景**：技术创新能力评估、核心技术储备分析

**数据更新**：每周更新

---

#### get_trademark_info（商标信息）

```bash
qcc ipr get_trademark_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：商标注册信息

**适用场景**：品牌资产评估、知识产权布局分析

**数据更新**：每周更新

---

#### get_software_copyright_info（软件著作权）

```bash
qcc ipr get_software_copyright_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：软件名称、登记号、版本号、登记日期

**适用场景**：软件资产分析、知识产权保护

---

#### get_copyright_work_info（作品著作权）

```bash
qcc ipr get_copyright_work_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：作品著作权信息

**适用场景**：文创资产价值评估、版权保护分析

---

#### get_standard_info（标准信息）

```bash
qcc ipr get_standard_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：参与制定的各类标准

**适用场景**：行业影响力评估、技术领先地位判断

---

#### get_internet_service_info（互联网服务备案）

```bash
qcc ipr get_internet_service_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：ICP备案、APP备案、小程序备案、算法备案信息

**适用场景**：网络服务分析、互联网合规性检查

---

### 4. risk（风险信息）- 34 个工具

#### get_dishonest_info（失信被执行人）

```bash
qcc risk get_dishonest_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：失信被执行人名称、涉案金额、执行法院、立案日期

**适用场景**：信用评估、法律风险分析、欠款违约调查

**数据源**：最高人民法院中国执行信息公开网

---

#### get_judgment_debtor_info（被执行人信息）

```bash
qcc risk get_judgment_debtor_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：执行标的、立案时间、执行法院

**适用场景**：债务执行情况了解、强制执行风险判断

---

#### get_high_consumption_restriction（限制高消费）

```bash
qcc risk get_high_consumption_restriction --searchKey "企业名称或统一社会信用代码"
```

**返回**：限制法定代表人、申请人、立案日期

**适用场景**：信用风险评估、合作伙伴风险排查

---

#### get_administrative_penalty（行政处罚）

```bash
qcc risk get_administrative_penalty --searchKey "企业名称或统一社会信用代码"
```

**返回**：处罚结果、处罚日期、处罚金额、处罚机关

**适用场景**：合规经营情况评估、违规成本分析

---

#### get_environmental_penalty（环保处罚）

```bash
qcc risk get_environmental_penalty --searchKey "企业名称或统一社会信用代码"
```

**返回**：处罚结果、处罚日期、处罚单位、处罚金额

**适用场景**：环保合规评估、环境风险控制

---

#### get_business_exception（经营异常）

```bash
qcc risk get_business_exception --searchKey "企业名称或统一社会信用代码"
```

**返回**：列入日期、移出原因、决定机关

**适用场景**：正常经营状态判断、轻微违规情况了解

---

#### get_serious_violation（严重违法失信）

```bash
qcc risk get_serious_violation --searchKey "企业名称或统一社会信用代码"
```

**返回**：列入原因、列入机关、列入日期

**适用场景**：企业准入严选、重大合规性审查

---

#### get_judicial_documents（法院判决文书）

```bash
qcc risk get_judicial_documents --searchKey "企业名称或统一社会信用代码"
```

**返回**：案由、裁判结果、涉案金额、当事人信息

**适用场景**：法律纠纷历史分析、诉讼风险评估

**数据更新**：T+1至T+7（存在一定延迟）

---

#### get_case_filing_info（法院立案信息）

```bash
qcc risk get_case_filing_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：案号、案由、立案日期、原被告双方

**适用场景**：诉讼情况初步了解、法律纠纷数量统计

---

#### get_hearing_notice（开庭公告）

```bash
qcc risk get_hearing_notice --searchKey "企业名称或统一社会信用代码"
```

**返回**：案号、案由、开庭时间、当事人身份

**适用场景**：诉讼动态跟踪、庭审时间安排查询

---

#### get_court_notice（法院公告）

```bash
qcc risk get_court_notice --searchKey "企业名称或统一社会信用代码"
```

**返回**：公告类型、案由、原告被告信息、刊登日期

**适用场景**：法律事务公告查询、司法程序进展跟踪

---

#### get_equity_freeze（股权冻结）

```bash
qcc risk get_equity_freeze --searchKey "企业名称或统一社会信用代码"
```

**返回**：被冻结股权数额、冻结期限、执行法院

**适用场景**：股东权益风险评估、股权变更限制了解

**数据更新**：T+1

---

#### get_equity_pledge_info（股权出质）

```bash
qcc risk get_equity_pledge_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：出质人、质权人、出质股权数额、登记日期

**适用场景**：融资状况分析、股权风险评估

**数据更新**：T+1

---

#### get_stock_pledge_info（股票质押）

```bash
qcc risk get_stock_pledge_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：质押人、质押权人、质押股份总数、市值

**适用场景**：股票质押风险分析

---

#### get_chattel_mortgage_info（动产抵押）

```bash
qcc risk get_chattel_mortgage_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：登记编号、抵押人、抵押权人、债权数额、状态

**适用场景**：动产融资评估

---

#### get_land_mortgage_info（土地抵押）

```bash
qcc risk get_land_mortgage_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：土地坐落、抵押人、抵押权人、抵押金额、用途

**适用场景**：土地资产抵押分析

**数据更新**：T+1

---

#### get_bankruptcy_reorganization（破产重整）

```bash
qcc risk get_bankruptcy_reorganization --searchKey "企业名称或统一社会信用代码"
```

**返回**：案号、申请人、被申请人、公开日期

**适用场景**：破产风险识别、重整程序跟踪

**数据源**：全国企业破产重整案件信息网

---

#### get_liquidation_info（清算信息）

```bash
qcc risk get_liquidation_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：清算组负责人、清算组成员

**适用场景**：破产或解散清算分析

---

#### get_simple_cancellation_info（简易注销）

```bash
qcc risk get_simple_cancellation_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：公告期、注销结果、登记机关

**适用场景**：注销程序了解、简易注销适用情况确认

---

#### get_cancellation_record_info（注销备案）

```bash
qcc risk get_cancellation_record_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：注销原因、注销日期、公告状态

**适用场景**：存续状态确认、注销程序了解

---

#### get_default_info（债券违约）

```bash
qcc risk get_default_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：债券简称、违约状态、首次违约日期、累计违约本金

**适用场景**：债券投资风险分析

---

#### get_judicial_auction（司法拍卖）

```bash
qcc risk get_judicial_auction --searchKey "企业名称或统一社会信用代码"
```

**返回**：拍卖标题、起拍价、评估价、拍卖时间、处置单位

**适用场景**：资产被执行处置了解、债权人受偿可能性评估

---

#### get_valuation_inquiry（询价评估）

```bash
qcc risk get_valuation_inquiry --searchKey "企业名称或统一社会信用代码"
```

**返回**：案号、标的物、所有人、询价结果、法院

**适用场景**：资产评估

---

#### get_public_exhortation（公示催告）

```bash
qcc risk get_public_exhortation --searchKey "企业名称或统一社会信用代码"
```

**返回**：票据号、申请人、票面金额、票据类型、公告日期

**适用场景**：票据遗失等法律程序查询

---

#### get_guarantee_info（担保信息）

```bash
qcc risk get_guarantee_info --searchKey "企业名称或统一社会信用代码"
```

**返回**：担保方、被担保方、担保方式、担保金额、履行状态

**适用场景**：评估企业担保风险

---

#### get_exit_restriction（限制出境）

```bash
qcc risk get_exit_restriction --searchKey "企业名称或统一社会信用代码"
```

**返回**：相关人员被法院限制出境情况

**适用场景**：高管个人风险排查、重大案件执行跟踪

---

#### get_disciplinary_list（惩戒名单）

```bash
qcc risk get_disciplinary_list --searchKey "企业名称或统一社会信用代码"
```

**返回**：类型、惩戒名单领域、列入原因、列入机关

**适用场景**：信用评估

---

#### get_pre_litigation_mediation（诉前调解）

```bash
qcc risk get_pre_litigation_mediation --searchKey "企业名称或统一社会信用代码"
```

**返回**：案号、案由、当事人、法院、立案日期

**适用场景**：纠纷解决跟踪

---

#### get_service_announcement（仲裁公告）

```bash
qcc risk get_service_announcement --searchKey "企业名称或统一社会信用代码"
```

**返回**：仲裁案号、申请人、被申请人、公告发布日期

**适用场景**：劳动纠纷监控、劳动仲裁程序跟踪

---

#### get_service_notice（送达公告）

```bash
qcc risk get_service_notice --searchKey "企业名称或统一社会信用代码"
```

**返回**：案号、案由、当事人、法院、发布日期

**适用场景**：法律文书送达情况

---

#### get_tax_abnormal（税务非正常户）

```bash
qcc risk get_tax_abnormal --searchKey "企业名称或统一社会信用代码"
```

**返回**：税务非正常户记录

**适用场景**：税务合规性扫描、税务黑名单核查

---

#### get_tax_arrears_notice（欠税公告）

```bash
qcc risk get_tax_arrears_notice --searchKey "企业名称或统一社会信用代码"
```

**返回**：欠税税种、欠税余额、发布单位、发布日期

**适用场景**：纳税信用评估、税务风险判断

---

#### get_tax_violation（税收违法）

```bash
qcc risk get_tax_violation --searchKey "企业名称或统一社会信用代码"
```

**返回**：案件性质、所属税务机关、发布日期

**适用场景**：纳税信用评估、税务合规风险识别

---

#### get_terminated_cases（终结执行）

```bash
qcc risk get_terminated_cases --searchKey "企业名称或统一社会信用代码"
```

**返回**：终本日期、执行标的、未履行金额

**适用场景**：执行风险了解、债务清偿能力评估

---

## 四、工具选择速查表

### 按场景选择工具

| 场景 | 推荐工具 |
|------|----------|
| **基础尽调** | get_company_registration_info → get_shareholder_info → get_key_personnel |
| **股权穿透** | get_shareholder_info → get_actual_controller → get_beneficial_owners → get_external_investments |
| **风险扫描** | get_dishonest_info → get_judgment_debtor_info → get_judicial_documents → get_administrative_penalty |
| **合规检查** | get_business_exception → get_serious_violation → get_tax_abnormal → get_tax_violation |
| **投资分析** | get_listing_info → get_financing_records → get_external_investments → get_news_sentiment |
| **合作评估** | get_qualifications → get_credit_evaluation → get_bidding_info → get_guarantee_info |
| **知产尽调** | get_patent_info → get_trademark_info → get_software_copyright_info → get_standard_info |
| **诉讼准备** | get_judicial_documents → get_case_filing_info → get_hearing_notice → get_judgment_debtor_info |

---

## 五、数据更新频率说明

| 频率 | 数据源 |
|------|--------|
| T+0 | 国家企业信用信息公示系统、裁判文书网、执行信息公开网 |
| T+1 | 自然资源部、知识产权局、版权局 |
| 每周 | 专利、商标公开数据 |
| 每年 | 年度报告（每年6月前集中更新） |
| 定期 | 荣誉、榜单、联系方式（人工维护） |

---

## 六、注意事项

1. **查询关键词**：优先使用统一社会信用代码，避免同名企业混淆
2. **数据延迟**：部分数据存在 T+1 至 T+7 延迟，注意时效性
3. **信息完整性**：非上市公司部分信息可能未完全公开
4. **隐私保护**：查询结果仅供工作使用，注意保护敏感信息

---

## 七、依赖

- `qcc` CLI 工具已安装并配置
- 无需额外环境变量

---

## 八、参考

- `qcc --help` - 命令行帮助
- `qcc list-tools` - 工具列表
