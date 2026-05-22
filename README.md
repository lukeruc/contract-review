# 合同审核 Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

基于 Claude Code 的智能合同审核系统。采用 EPC 三层架构，输入合同（.docx / .pdf），全自动产出**审核意见书**和**以修订模式标注修改的合同 .docx**。

## 系统架构

```
用户 → Architect（总承包）→ Task Agent（分包商）×N → 工具层
                ↕
           Reviewer（监理，仅复杂模式）
```

| 角色 | 职责 |
|------|------|
| **Architect** | 唯一用户入口。不做第一手法律分析。负责判断、规划、委托、信息蒸馏、验收交付物 |
| **Task Agent** | 按需创建的 sub-agent，执行单项任务后销毁 |
| **Reviewer** | 仅复杂模式启用。独立 sub-agent，对照交付标准核查 Task Agent 产出，循环上限 3 次 |

核心理念：Architect 不亲自做任何法律分析——所有读合同、检索法规、分析条款、撰写意见、修订文本均委托 Task Agent。

## 模块

| 模块 | 文件 | 功能 |
|------|------|------|
| **contract-review** | `contract-review/SKILL.md` | 合同审核主模块。通过 `/contract-review` 触发，产出审核意见书 + 修订合同 .docx |
| **rule-builder** | `rule-builder/SKILL.md` | 审核规则生成器。通过 `/rule-builder` 触发，从企业合同模板通过问答式交互生成审核规则文件 |

两者的关系：rule-builder 产出规则存入 `rules/` 目录，contract-review 加载规则执行审核。

## 工作流程（contract-review）

```
Bootstrap（格式转化 → 字符数 → 立场/模式确认）
    │
    ├── 简单模式（≤10000 字符建议，用户可选择切换）
    │     1. 合同类型判断 + 规则匹配
    │     2. Audit Agent 全合同审查
    │     3. Translation Agent 将审核意见转为操作手册 (revisions.json)
    │     4. Revision Agent 用 docx-mcp 执行修订
    │     5. 交付（审核意见书 .md + 修订合同 .docx）
    │
    └── 复杂模式（EPC 全机制）
          阶段 1：初步设计（结构化 → 商业条件 → 交叉引用）
          阶段 2：多 Audit Agent 并行详细审查 + Reviewer 质量审查
          阶段 3：Assembly 汇编审核意见书
          阶段 4：Translation Agent → Revision Agent (docx-mcp) 修订
          阶段 5：格式输出 + 交付
```

## 安装

### 前提条件

- **Claude Code**（Claude Code CLI 或 IDE 扩展）
- **Python 3.12+**
- **pandoc**（用于 .docx → Markdown 转换）

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt install pandoc

# Windows
winget install pandoc
```

### 第一步：克隆项目

```bash
git clone https://github.com/lukeruc/contract-review.git
cd contract-review
```

### 第二步：安装 Python 依赖

```bash
pip install -r tools/requirements.txt
```

### 第三步：安装 docx-mcp MCP 服务器

docx-mcp 是修订阶段的 MCP 服务器，负责 Word 文档的修订标记、批注、段落插入。**必须安装。**

```bash
claude mcp add docx-mcp -- uvx docx-mcp-server
```

如果项目里没有这个命令，手动加入 Claude Code 的 MCP 配置文件（`~/.claude/settings.json`）：

```json
{
  "mcpServers": {
    "docx-mcp": {
      "command": "uvx",
      "args": ["docx-mcp-server"]
    }
  }
}
```

> 安装后，Claude Code 中会自动出现一个 `docx-mcp` skill，提供使用指引。

### 第四步：安装工具 Skill

将 `tools/` 下的三个 skill 安装为 Claude Code skill：

#### mdconverter（文档转 Markdown）

```bash
claude skill add mdconverter --path tools/md-converter
# 或手动：将 tools/md-converter/ 复制到 ~/.claude/skills/mdconverter/
```

> 扫描版 PDF 需要 Dashscope API key。设置环境变量：`export DASHSCOPE_API_KEY=your-key`

#### yd-law（法律数据库检索）

```bash
claude skill add yd-law --path tools/yd-law
```

> 需要 YD 法律数据 API key。设置环境变量：`export YD_KEY=your-key`

如果不使用法律检索功能，此 skill 可以跳过——合同审核将仅基于审核规则和合同自身逻辑进行分析。

#### qcc（企业工商信息查询）

```bash
claude skill add qcc --path tools/qcc
```

> 需要 QCC API key。设置环境变量：`export QCC_KEY=your-key`

如果不使用企业查询功能，此 skill 可以跳过。

### 第五步：安装入口 Skill

```bash
# 主模块：合同审核
claude skill add contract-review --path contract-review

# 规则生成器（可选）
claude skill add rule-builder --path rule-builder
```

### 第六步：验证安装

在 Claude Code 中输入 `/contract-review`，系统应提示你上传合同文件。如果没有反应，检查：

1. skill 是否在正确路径：`ls ~/.claude/skills/contract-review/SKILL.md`
2. MCP 服务器是否运行：`claude mcp list` 应包含 `docx-mcp`
3. pandoc 是否可用：`pandoc --version`
4. Python 依赖是否完整：`python -c "import docx, lxml, pymupdf4llm"`

## 项目结构

```
contract-review/
├── SKILL.md                      # 合同审核 skill 入口
├── scripts/                      # 本地脚本（Architect 执行）
│   ├── char-count.sh             # 纯文本字符数统计
│   ├── scan-structure.py         # 编号体系机械扫描（中英文）
│   └── add-paraids.py            # 为 .docx 添加 w14:paraId 属性
├── agent/                        # 固定 Agent 定义（强制模板）
│   ├── task-structure.md         # T-S01 结构化
│   ├── task-preliminary-report.md# T-PR 初步情况报告
│   └── task-assembly.md          # T-ASM 审核意见汇编
├── workflows/                    # 流程定义
│   ├── simple.md                 # 简单模式
│   └── complex.md                # 复杂模式（EPC 全机制）
├── rules/                        # 审核规则库（律师编写）
│   ├── construction-contract.md
│   ├── engineering-procurement-bangladesh-buyer.md
│   └── nda.md
├── references/                   # 各 Agent 类型参考示例
├── schemas/                      # Agent 间通讯格式定义
├── tools/                        # 外部工具 skill
│   ├── md-converter/
│   ├── yd-law/
│   └── qcc/
├── doc/                          # 设计文档
│   ├── DESIGN.md                 # 概念设计
│   ├── TECHNICAL-DESIGN.md       # 技术设计
│   └── RULE-BUILDER-DESIGN.md    # Rule-builder 设计
├── rule-builder/                 # 规则生成 skill（独立）
│   ├── SKILL.md
│   ├── scripts/scan-structure.py
│   └── agent/
├── LICENSE                       # MIT
└── README.md
```

## 环境变量

| 变量 | 用途 | 必需？ |
|------|------|--------|
| `DASHSCOPE_API_KEY` | 扫描版 PDF / 图片 OCR（mdconverter） | 仅处理扫描件时需要 |
| `YD_KEY` | 法律数据库检索 API（yd-law） | 可选，不用则不设 |
| `QCC_KEY` | 企业工商信息查询 API（qcc） | 可选，不用则不设 |

不使用外部 API 时，合同审核仍可基于审核规则和合同自身的逻辑分析进行——法律检索和企业查询是增强功能，非必需。

## API 获取

- **Dashscope**：https://dashscope.aliyun.com/ — 阿里云灵积模型服务，开通"文字识别"能力
- **YD Law**：https://open.chineselaw.com/ — 法律数据 API
- **QCC**：https://www.qcc.com/ — 企业信息查询平台

## 常见问题

**Q: 启动 `/contract-review` 后提示 "不支持 .doc 格式"**

.doc 是旧版二进制格式。用 Word 或 WPS 将文件另存为 .docx 后重新提交。

**Q: 修订合同打不开，Office 报错**

通常是 docx-mcp 未正确安装。检查 `claude mcp list` 是否包含 `docx-mcp`。

**Q: 修订完成后段落找不到、提示 "paragraph not found"**

你的 .docx 文件缺少 `w14:paraId` 属性（旧版 Word 保存的文档常见问题）。系统会自动用 `add-paraids.py` 预处理，不需要你手动操作。

**Q: 审核结果不准确**

审核质量依赖于 `rules/` 目录下的规则文件质量。规则文件由专业律师编写和维护。如果遇到不准确的审核结果，可以：
- 检查匹配的规则文件是否覆盖了你的合同类型
- 使用 `/rule-builder` 从你的合同模板生成专属规则
- 在复杂模式下利用初设后暂停机制，指定重点审查领域

**Q: 可以只安装合同审核、不安装规则生成器吗？**

可以。规则生成器 (`rule-builder/`) 是独立模块，不安装不影响合同审核功能。

## 贡献

欢迎提交 Issue 和 Pull Request。规则文件 (`rules/`) 尤其欢迎律师贡献。

## License

MIT — 详见 [LICENSE](LICENSE)
