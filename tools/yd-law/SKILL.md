---
name: yd-law
description: 通过 YD 法律数据 API（open.chineselaw.com）检索中国案例、法律法规、法条。当用户需要查找判决书、案例、法律法规、法条，或进行法律语义检索、法律研究时使用。
---

# YD 法律数据检索

通过统一 CLI 脚本 `scripts/yd.py` 检索中国法律数据。脚本封装了 YD 开放平台全部 8 个 API，自动处理鉴权和请求构造。

## 前置条件

- 设置环境变量：`export YD_KEY="sk_..."`
- 脚本路径：`./scripts/yd.py`（相对于本 skill 目录）
- 依赖：仅使用 Python 标准库（argparse, json, os, sys, urllib），无需 pip install

## 命令速查

脚本用法：`python scripts/yd.py <资源> <操作> [参数]`

### 案例（case）

```
# 关键词检索普通案例
python scripts/yd.py case search --qw "违约金 逾期" --ay "买卖合同纠纷" --xzqh-p "北京" -n 5

# 案例详情（按 ID 或案号）
python scripts/yd.py case detail --ah "（2023）京0101民初123号" --type ptal

# 语义检索案例
python scripts/yd.py case semantic --query "入户盗窃后主动投案自首" -n 5
```

### 法条（statute）

```
# 关键词检索法条
python scripts/yd.py statute search --keyword "行政处罚" --sxx "现行有效" -n 10

# 法条详情（按 ID，或按"法规名+法条号"）
python scripts/yd.py statute detail --fgmc "中华人民共和国刑法" --ftnum "第一百条"
```

### 法规（law）

```
# 关键词检索法规（keyword 可选，不传则纯条件过滤）
python scripts/yd.py law search --keyword "行政处罚" -n 10
python scripts/yd.py law search --sxx "现行有效" --xljb-1 "法律" -n 10

# 法规详情
python scripts/yd.py law detail --fgmc "中华人民共和国刑法"

# 语义检索法规
python scripts/yd.py law semantic --query "入户盗窃的法律规定"
```

## 如何选择

| 用户意图 | 命令 |
|---------|------|
| 按条件搜案例（案由、法院、日期、关键词等） | `case search` |
| 自然语言描述场景搜案例 | `case semantic` |
| 已知案号或 ID 想看判决书全文 | `case detail` |
| 按关键词/条件搜具体法条 | `statute search` |
| 已知法规名和法条号，看具体条文 | `statute detail` |
| 搜法规概要或按效力/时效浏览法规 | `law search` |
| 已知法规名看全文 | `law detail` |
| 自然语言描述法律问题找法规 | `law semantic` |

## 参数速查 vs 详细参考

**日常使用 `--help`**：每个子命令自带帮助，列出参数名和用法。

**以下情况去读 `references/`**：

| 情况 | 读哪个文件 |
|------|-----------|
| 需要知道参数有哪些合法可选值（如省份、效力级别、文书种类编码） | 对应接口文档的"字段说明"表格 |
| 想知道返回字段含义（如 `total` 是对象不是数字） | 对应接口文档的"返回信息"章节 |
| 需要看完整请求/响应示例 | 对应接口文档末尾的示例 |
| 搜权威案例（脚本暂未封装 `/open/rh_qwal_search`） | `references/权威案例关键词检索接口.md` |
| 不确定接口行为边界（如空 body、非法参数会怎样） | 对应接口文档的"校验与默认值"章节 |

references/ 目录文件：

```
references/
├── 普通案例关键词检索接口.md
├── 权威案例关键词检索接口.md
├── 案例语义检索接口.md
├── 案例详情接口.md
├── 法条关键词检索接口.md
├── 法条详情接口.md
├── 法规关键词检索接口.md
├── 法规详情接口.md
├── 法律法规语义检索接口.md
└── 平台介绍.md
```
