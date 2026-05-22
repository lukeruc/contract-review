# 合同审核

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

基于 Claude Code 的 AI 合同审核系统。输入合同（.docx / .pdf），全自动产出**审核意见书**和**以修订模式标注修改的合同 .docx**。

[English](README.md)

## 架构

系统采用三层委托模型（灵感来自工程总承包管理）：

```
用户 → Architect（总负责人）→ Task Agent（任务代理）×N → 工具层
                ↕
           Reviewer（质量监理，仅复杂模式）
```

| 角色 | 职责 |
|------|------|
| **Architect** | 唯一用户入口。不做第一手法律分析。负责判断、规划、委托、信息蒸馏、验收交付物 |
| **Task Agent** | 按需创建的 sub-agent，执行单项任务后销毁。所有读合同、检索法规、分析条款、撰写意见、修订文本均由 Task Agent 完成 |
| **Reviewer** | 仅复杂模式启用。独立 sub-agent，逐条对照交付标准核查 Task Agent 产出，单 Agent 循环上限 3 次 |

核心理念：Architect 不亲自做任何法律分析，全部委托 Task Agent 执行，自己只做管理和判断。

## 模块

| 模块 | 入口 | 功能 |
|------|------|------|
| **contract-review** | `/contract-review` | 合同审核主模块。产出审核意见书 + 修订合同 .docx |
| **rule-builder** | `/rule-builder` | 审核规则生成器。从企业合同模板通过问答式交互生成审核规则文件 |

关系：rule-builder 产出规则存入 `rules/`，contract-review 加载规则执行审核。

## 工作流程（contract-review）

```
Bootstrap（格式转化 → 字符数统计 → 确认立场和模式）
    │
    ├── 简单模式（≤10000 字符建议，用户可切换）
    │     1. 合同类型判断 + 规则匹配
    │     2. Audit Agent 全合同审查
    │     3. Translation Agent 将审核意见转为操作手册 (revisions.json)
    │     4. Revision Agent 用 docx-mcp 执行修订（修订标记 + 批注）
    │     5. 交付：audit-opinion.md + revised.docx
    │
    └── 复杂模式（全机制）
          阶段 1：初步设计（结构化 → 商业条件提取 → 交叉引用分析）
          阶段 2：多 Audit Agent 并行详细审查 + Reviewer 质量审查
          阶段 3：汇编——合并多份审计产出为统一审核意见书
          阶段 4：Translation Agent → Revision Agent (docx-mcp) 修订
          阶段 5：格式输出 + 交付
```

## 安装

### 前提

- **Claude Code**（CLI 或 IDE 扩展）
- **Python 3.12+**
- **pandoc**（.docx → Markdown 转换）

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt install pandoc

# Windows
winget install pandoc
```

### 第一步：克隆

```bash
git clone https://github.com/lukeruc/contract-review.git
cd contract-review
```

### 第二步：Python 依赖

```bash
pip install -r tools/requirements.txt
```

### 第三步：安装 docx-mcp MCP 服务器

docx-mcp 负责 Word 文档的修订标记、批注和段落插入。**必须安装。**

```bash
claude mcp add docx-mcp -- uvx docx-mcp-server
```

如果 `claude mcp` 命令不可用，手动添加到 Claude Code 的 MCP 配置文件（`~/.claude/settings.json`）：

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

首次启动 MCP 服务器时会自动安装 `docx-mcp` skill，提供使用指引。

### 第四步：安装工具 skill

将 `tools/` 下的三个 skill 安装到 Claude Code：

#### mdconverter（文档转 Markdown）

```bash
claude skill add mdconverter --path tools/md-converter
# 或手动将 tools/md-converter/ 复制到 ~/.claude/skills/mdconverter/
```

> 扫描版 PDF 需要 Dashscope API key。设置环境变量 `DASHSCOPE_API_KEY`。

#### yd-law（法律数据库检索）

```bash
claude skill add yd-law --path tools/yd-law
```

> 需要 YD 法律数据 API key。设置 `YD_KEY`。不使用法律检索也可以——系统会基于审核规则和合同自身逻辑完成分析。

#### qcc（企业工商信息查询）

```bash
claude skill add qcc --path tools/qcc
```

> 需要 QCC API key。设置 `QCC_KEY`。不使用企业查询也可以。

### 第五步：安装入口 skill

```bash
# 主模块：合同审核
claude skill add contract-review --path contract-review

# 规则生成器（可选）
claude skill add rule-builder --path rule-builder
```

### 第六步：验证

在 Claude Code 中输入 `/contract-review`，系统应提示上传合同文件。如果没有反应：

1. 检查 skill 路径：`ls ~/.claude/skills/contract-review/SKILL.md`
2. 检查 MCP 服务器：`claude mcp list` 应包含 `docx-mcp`
3. 检查 pandoc：`pandoc --version`
4. 检查 Python 依赖：`python -c "import docx, lxml, pymupdf4llm"`

## 目录结构

```
contract-review/
├── SKILL.md                      # 合同审核 skill 入口
├── scripts/                      # 本地脚本（Architect 执行）
│   ├── char-count.sh             # 字符数统计
│   ├── scan-structure.py         # 编号体系机械扫描（中英文）
│   └── add-paraids.py            # 为 .docx 添加 w14:paraId（docx-mcp 兼容）
├── agent/                        # 固定 Agent 定义（强制模板）
│   ├── task-structure.md         # T-S01 结构化
│   ├── task-preliminary-report.md# T-PR 初步情况报告
│   └── task-assembly.md          # T-ASM 审核意见汇编
├── workflows/                    # 流程定义
│   ├── simple.md                 # 简单模式
│   └── complex.md                # 复杂模式（全机制）
├── rules/                        # 审核规则库（律师编写）
│   ├── construction-contract.md
│   └── nda.md
├── references/                   # 各类型 Agent 参考示例
├── schemas/                      # Agent 间通讯格式定义
├── tools/                        # 外部工具 skill
│   ├── md-converter/
│   ├── yd-law/
│   └── qcc/
├── docs/                         # 设计文档
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
| `DASHSCOPE_API_KEY` | 扫描版 PDF / 图片 OCR | 仅处理扫描件时需要 |
| `YD_KEY` | 法律数据库检索 API | 可选 |
| `QCC_KEY` | 企业工商信息查询 API | 可选 |

不使用外部 API 时，系统仍可基于审核规则和合同自身逻辑完成分析。

## API 获取

- **Dashscope**：https://dashscope.aliyun.com/ — 阿里云灵积模型服务，开通"文字识别"
- **YD Law**：https://open.chineselaw.com/ — 法律数据 API
- **QCC**：https://www.qcc.com/ — 企业信息查询平台

## 常见问题

**Q: 提示"不支持 .doc 格式"**

.doc 是旧版二进制格式。用 Word 或 WPS 另存为 .docx 后重新提交。

**Q: 修订后的 .docx 打不开**

通常是 docx-mcp 未正确安装。运行 `claude mcp list` 检查是否包含 `docx-mcp`。

**Q: 修订时提示找不到段落**

你的 .docx 文件缺少 `w14:paraId` 属性（旧版 Word 保存的常见问题）。系统会用 `add-paraids.py` 自动预处理，不需要手动操作。

**Q: 审核结果不准确**

审核质量依赖 `rules/` 下的规则文件。规则由专业律师编写维护。改进方法：
- 检查是否有匹配你合同类型的规则文件
- 用 `/rule-builder` 从你的合同模板生成专属规则
- 复杂模式下利用初设后暂停机制，指定重点审查领域

**Q: 可以只装合同审核不装规则生成器吗？**

可以。rule-builder 是独立模块，不装不影响合同审核。

## 贡献

欢迎 Issue 和 Pull Request。规则文件 (`rules/`) 尤其欢迎律师贡献。

## License

MIT — 详见 [LICENSE](LICENSE)
