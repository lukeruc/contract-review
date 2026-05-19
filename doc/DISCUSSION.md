# 讨论与待解决问题

本文档记录项目当前正在讨论的设计问题、测试发现和待决策事项。已解决的问题移入 DESIGN.md 或 TECHNICAL-DESIGN.md，不再保留于此。

---

# 合同结构化耗时问题分析

## 问题

T-S01（Structure Task Agent）运行时间非常长。这影响 contract-review 复杂模式和 rule-builder 两个 skill 的体验——结构化是后续所有工作的前置依赖（T-S02/T-S03 依赖其编号体系），它卡住，整个流程就卡住。

## 成因分析

当前 Structure Agent 的设计（两遍处理 + 单 Agent 串行）存在三个层面的耗时因素：

### 一、两遍全文处理

Agent 的工作方式：第一遍通读全文建立编号体系心智模型 → 第二遍逐段输出结构化文本 + 填写索引表。对一份 10 万字的合同，相当于 Agent 需要两次完整遍历全文，每次都要保持对全部编号关系的注意力。这不是"读两遍"——第二遍中 Agent 同时在写作（输出结构化文本）和校对（保证与原文一致、与索引表一致）。

### 二、五项错误模式的自检成本

System Prompt 中列举了五项常见错误（编号跳跃、附件清单误读、正文内引用误判、长篇款项拆散、前言正文混淆）。Agent 在输出时需要对每一条款逐一检查这五项。五项检查 × N 条条款 = 5N 次判断。这些判断中大部分是"此模式不适用"的否定判断，但 Agent 仍需消耗注意力来排除。

### 三、不可并行

当前设计下，整个结构化工作由单个 Agent 串行完成。即使合同有 12 章 200 条，也必须等 Agent 从头到尾处理完。这在本质上是"单线程处理长文本"的性能瓶颈——不是 Agent 不努力，而是任务模型决定了无法加速。

### 根本矛盾

结构化的任务性质存在一个内在矛盾：**编号体系的识别需要全局视野（必须看全文），但条款正文的结构化是局部操作（只操作当前条款）**。当前设计将两者捆绑在一个 Agent 的一个任务中，导致全局扫描的成本被全文的每一个局部操作分担。

## 解决方案：工具辅助预扫描

核心思路：编写一个轻量 Python 脚本，用正则逐行扫描合同 Markdown，机械提取条款编号体系、层级结构和行号映射。将识别编号体系的工作从 AI 降级为脚本——脚本秒级完成，Agent 跳过第一遍通读直接进入结构化输出。

### 详细设计

#### 整体思路

编写一个 Python 脚本，用正则逐行扫描合同 Markdown 文件，机械提取条款编号体系、层级结构和行号映射。Agent 拿到这份机械预扫描结果后，跳过第一遍通读，直接进入结构化输出。异常判断仍由 Agent 完成，但"我该在哪里切分条款、编号之间是什么关系"这个耗时最多的机械问题由脚本秒级解决。

#### 脚本位置

```
contract-review/scan-structure.py          # contract-review 和 rule-builder 共用
```

Architect 在 Bootstrap 阶段、创建 T-S01 之前调用：

```bash
python {SKILL_DIR}/scan-structure.py contract.md > _internal/scan-result.json
```

然后将 `scan-result.json` 注入 Structure Agent，替代第一遍通读。

#### 识别模式

中文合同常见的编号体系，按层级从高到低：

| 层级 | 模式 | 正则 | 示例 |
|------|------|------|------|
| 编 | `第[数]编` | `^第[一二三四五六七八九十百千\d]+编\s*` | 第一编 总则 |
| 章 | `第[数]章` | `^第[一二三四五六七八九十百千\d]+章\s*` | 第三章 工程质量 |
| 节 | `第[数]节` | `^第[一二三四五六七八九十百千\d]+节\s*` | 第一节 一般规定 |
| 条 | `第[数]条` | `^第[一二三四五六七八九十百千\d]+条\s*` | 第十二条 违约责任 |
| 款 | 自然段（通常无编号） | — | 条内第一个自然段 |
| 项 | `（[数]）` | `^（[一二三四五六七八九十\d]+）` | （一） / （3） |
| 目 | `[数]、` | `^\d+、` | 1、 / 12、 |

关键设计点：

- **中文数字转换**：脚本内置 `cn2int("三百二十五") → 325`，用于比对编号连续性。
- **编号容错**：同时匹配"第十二条"和"第12条"两种写法。混合使用的合同并不少见。
- **不是简单的全行匹配**：条的编号可能不在行首（如"乙方应按照第十二条的约定……"——"第十二条"在这里是引用，不是条款起始）。通过规则过滤：只有行首的编号才算条款起始；行中的数字编号通常是引用。

#### 条款起始 vs 行中引用

这是脚本最关键的正误判断。过滤规则：

1. **条款起始**：行首（忽略空白）以"第X条"开头，后面紧跟标题文字或换行。
2. **行中引用**："第X条"出现在行中，前面有其他文字（如"按照第十二条的约定"），不是条款起始。
3. **附件清单误判**：连续出现的"附件一：XX"、"附件二：XX"——以"附件"开头，不标记为条款。
4. **前言/鉴于**：出现在合同正文开头、第一条之前的文字块——通过"第一条"的位置反推前言边界。

正则策略：

```python
# 条款起始：行首的"第X条"
ARTICLE_START = re.compile(r'^\s*第([一二三四五六七八九十百千\d]+)条\s*')

# 编/章/节
PART_CHAPTER = re.compile(r'^\s*第([一二三四五六七八九十百千\d]+)(编|章|节)\s*')

# 款内的项（子项）
SUB_ITEM = re.compile(r'^\s*（([一二三四五六七八九十\d]+)）\s*')

# 行中引用（用于确认不是条款起始）
INLINE_REF = re.compile(r'.+第[一二三四五六七八九十百千\d]+条')
```

#### 输出结构

脚本输出 JSON，包含三个部分：编号体系描述、条款清单、异常报告。

```json
{
  "file": "contract.md",
  "total_chars": 234567,
  "numbering_scheme": {
    "language": "zh",
    "has_part": false,
    "has_chapter": true,
    "has_section": false,
    "article_format": "chinese",       
    "sub_item_format": "chinese_paren"
  },
  "chapters": [
    {
      "num": "第一章",
      "title": "总则",
      "line_start": 2,
      "article_range": ["第1条", "第10条"],
      "article_count": 10
    }
  ],
  "articles": [
    {
      "num": "第1条",
      "num_int": 1,
      "title": "定义",
      "line_start": 4,
      "line_end": 18,
      "chapter": "第一章",
      "paragraphs": 3,
      "has_sub_items": true,
      "sub_item_count": 4
    }
  ],
  "anomalies": [
    {"type": "skip", "detail": "第5条→第7条，第6条缺失", "after_article": "第5条", "at_line": 94},
    {"type": "duplicate", "detail": "第12条出现两次", "lines": [200, 350]},
    {"type": "format_change", "detail": "第15条附近编号从中文切换为阿拉伯数字", "at_line": 280}
  ],
  "preamble": {
    "line_start": 1,
    "line_end": 3,
    "preview": "甲乙双方经友好协商，就……达成如下协议："
  },
  "attachment_list": {
    "line_start": 5120,
    "items": ["附件一 工程量清单", "附件二 图纸目录"]
  }
}
```

#### 编号空间语义

脚本需要理解一个关键概念：**每个层级有独立的编号空间**。"第X条"是全局连续还是每章内重新开始？

- **全局连续**：整份合同第1条→第200条，不因章节变化重置。绝大多数中文合同采用此模式。
- **章内重置**：每章从第1条开始编号。常见于英美合同翻译件。

脚本通过检测"第一章"之后的"第1条"来判断：
- 如果第一章有"第1条"，第二章开头又是"第1条" → 章内重置
- 如果第一章有"第1-10条"，第二章开头是"第11条" → 全局连续

这决定了异常检测逻辑——章内重置时，"第1条重复出现"不是异常。

#### 与 Agent 的协作方式

Architect 创建 Structure Agent 时，注入 `scan-result.json`，并在 System Prompt 中追加：

```
## 预扫描结果

脚本已为你完成了第一遍通读的机械部分。以下是扫描结果的关键信息：

1. 编号体系：{has_chapter}章，条{article_count}条，{numbering_scheme}
2. 条款起始行号已标注（见 scan-result.json 中的 articles 数组）
3. 已识别的异常：{anomalies_summary}
4. 前言范围：第 {preamble_start}-{preamble_end} 行
5. 附件清单范围：第 {attachment_start} 行起

你不需要重新识别编号体系和条款边界。你的工作是：
- 验证扫描结果（如发现误判，标注 [编号异常] 纠正）
- 为每一条款生成结构化输出（Markdown 标题层级）
- 判断条款内部的款/项结构（脚本不做段落级分析）
- 标注叙述性内容（前言、附件清单等使用 > 块引用）
```

这样 Agent 跳过了最耗时的"茫茫文本中找条款边界"阶段，从全局扫描降为局部验证 + 格式化输出。

#### 实现可行性

核心代码约 80-120 行 Python（不含中文数字转换函数）。中文数字转换是一个已知问题的成熟实现——网上有大量 `cn2num.py` 实现，约 30 行。脚本整体约 120-150 行。

不需要外部依赖（stdlib only），不增加 requirements.txt 条目。

#### 局限性（脚本不替代 Agent 的部分）

脚本是纯机械工具，以下工作仍需 Agent 完成：

1. **条款正文内部层级判断**：一条条款内部有几款、款内有无分项。这需要读条款正文的语义，不是正则能解决的。
2. **叙述性内容边界精确判定**：脚本只能标记"前言大致在第1-3行"，但前言和第一条之间的精确边界需要 Agent 判断。
3. **编号异常的最终定性**：脚本标记"疑似异常"，但"第6条缺失"是真的是原文遗漏还是编号写法不统一（"第六条"写作"第六条之一"），需要 Agent 判断。
4. **条款标题 vs 条款正文的分界**：有些合同"第十二条"之后直接跟正文，有些在标题和正文间有换行——Agent 需要正确切分。

#### 英文合同适配

系统接收的合同可能是英文或双语。脚本需同时支持英文编号体系。

**语言检测**：扫描前 100 行，统计 CJK 字符占比。CJK 占比 > 30% → 中文模式，< 10% → 英文模式，介于之间 → 双语模式（两套正则均启用，以最先匹配到的为准）。

**英文编号体系**：

| 层级 | 模式 | 正则 | 示例 |
|------|------|------|------|
| Article | `ARTICLE [数]` | `^\s*ARTICLE\s+([IVXLCDM\d]+)\b` | ARTICLE 1 / ARTICLE I |
| Section | `Section [数]` | `^\s*Section\s+([\d.]+)\b` | Section 1.1 / Section 2 |
| Clause | `[数].` | `^\s*(\d+)\.\s+` | 1. / 12. |
| Sub-clause | `[数].[数]` | `^\s*(\d+\.\d+)\s+` | 1.1 / 3.2 |
| Paragraph | `([字母])` | `^\s*\(([a-zA-Z])\)\s+` | (a) / (A) |
| Sub-paragraph | `([罗马])` | `^\s*\(([ivxlcdm]+)\)\s+` | (i) / (iv) |

**罗马数字转换**：脚本内置 `roman2int("XIV") → 14`，用于 Article 层级和子段层的连续检测。

**英文合同的编号空间**：英文合同几乎总是 Article 内独立编号——每个 Article 下的 Section 或 Clause 从 1 开始。脚本通过检测 ARTICLE 边界自动切换编号空间，不将不同 Article 内的 Section 1 标记为重复。

**输出 JSON 中的语言标识**：

```json
"numbering_scheme": {
    "language": "en",
    "has_article": true,
    "has_section": true,
    "section_format": "dotted",
    "sub_item_format": "alpha_paren"
}
```

**与中文模式的统一**：脚本对中英文合同输出相同结构的 JSON（`articles` 数组、`anomalies` 数组、`chapters` → 英文下为 `articles_top`）。Structure Agent 无需关心语言差异——它只看到统一的条款编号和行号映射。

# Sub-Agent 文件写入权限问题

## 问题

T-RB-S01 运行中遇到 Write 权限限制，回退到通过 Bash 写入文件。Sub-agent 的 Write 工具可能受限，而所有 Task Agent 都需要将产出写入 `_internal/` 或 `output/` 目录。

## 分析

这是 Claude Code 的 sub-agent 权限模型问题，不是 rule-builder 或 contract-review 特有的。Sub-agent 可用的工具集取决于其类型和系统配置——Write 工具在某些 sub-agent 类型中可能被限制，而 Bash 工具通常可用（回退写入已验证可行）。

这个问题的本质是：**我们的固定 Agent 定义中，对"如何写文件"没有明确指令，Agent 自行选择工具，遇到权限问题后回退。回退成功，但增加了运行时间。**

## 解决方案

三个选项，按侵入性从低到高排列：

### 选项 A：不做特殊处理（当前状态）

Sub-agent 自行选择写文件方式。Write 受限时回退到 Bash，验证可行。不修改任何 Agent 定义。

- 优点：零改动。回退机制已证明可用。
- 缺点：每次遇到权限问题都有一次失败的 Write 调用 + 回退延迟。

### 选项 B：Architect 侧预创建输出路径

Architect 在创建 sub-agent 之前，用 Bash 预创建输出文件的父目录并设置权限。

```bash
mkdir -p "${SESSION_DIR}/_internal" && touch "${SESSION_DIR}/_internal/template-structured.md"
```

- 优点：目录存在且权限正确，可能减少 Write 失败概率。
- 缺点：不从根本上解决问题——如果 Write 工具本身被限制，有空文件也不能覆盖。

### 选项 C：Agent 定义中明确指示使用 Bash 写文件

在 Task Spec 中增加一条交付标准或说明，让 Agent 直接用 Bash 写入产出文件，跳过 Write 工具。

```markdown
## 输出方式

使用 Bash 将内容写入输出文件：
```bash
cat > _internal/template-structured.md <<'ENDOFFILE'
...完整内容...
ENDOFFILE
```
```



