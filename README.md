# 合同审核 Skill

基于 Claude Code 的智能合同审核系统。采用 EPC 三层架构，自动区分合同复杂度，产出**审核意见书**和**修订标注合同 .docx**。

## 架构

```
用户 → Architect（总承包）→ Task Agent（分包商）×N → 工具层
                ↕
           Reviewer（监理，仅复杂模式）
```

- **Architect**：唯一入口，不做第一手法律分析。负责判断、规划、委托、信息蒸馏、验收
- **Task Agent**：按需创建的 sub-agent，执行具体任务后销毁
- **Reviewer**：复杂模式专用，对照交付标准核查产出，循环上限 3 次

## 工作流程

系统收到合同后执行 Bootstrap，获取字符数后建议模式（阈值 10000 字符），用户最终决定：

| 模式 | 条件 | 机制 |
|------|------|------|
| 简单模式 | 用户选择 | 单个 Audit Agent + Architect 自行验收 |
| 复杂模式 | 用户选择 | 初设阶段（结构化→条件提取→交叉引用）+ 多 Audit Agent 分工 + Reviewer 审查 |

两种模式最终均产出 `agent/` 目录，用户可在此路径下新开对话追问审查结果。

## 项目结构

```
contract-review/
├── SKILL.md                 # 入口 skill
├── char-count.sh            # 字符数统计脚本
├── agent/                   # 固定 Agent 定义（强制模板）
├── workflows/               # 流程定义
├── references/              # 参考示例
├── schemas/                 # Agent 间通讯格式
├── rules/                   # 审核规则库（律师编写）
├── tools/                   # 工具 skill
│   ├── docx/                 # safe-docx（Word 编辑）
│   ├── md-converter/        # 文档转 Markdown
│   ├── yd-law/              # 法律数据库检索
│   └── qcc/                 # 企业工商查询
└── doc/                     # 设计文档
    ├── DESIGN.md            # 概念设计
    ├── TECHNICAL-DESIGN.md  # 技术设计
    ├── DISCUSSION.md        # 讨论记录
    └── workflow.html        # 流程可视化
```

## 安装与使用

### 1. 安装 Python 依赖

```bash
pip install -r tools/requirements.txt
```

### 2. 安装工具 skill

将 `tools/` 下的四个 skill 目录分别安装到 Claude Code：

- `mdconverter` — 文档转 Markdown
- `safe-docx` — Word 文档编辑（基于 MCP server）
- `yd-law` — 法律检索（需设置 `YD_KEY` 环境变量）
- `qcc` — 企业查询

### 3. 安装入口 skill

将 `contract-review/` 目录安装到 Claude Code。通过 `/contract-review` 命令触发。

### 4. 环境要求

- Python 3.12+（pymupdf4llm, dashscope, python-docx, click）
- pandoc（.docx 转换）
- Dashscope API key（扫描版 PDF 和图片识别）
- YD 法律数据 API key

## 关键设计决策

1. 仅通过 `/contract-review` 命令触发
2. 审核立场在 bootstrap 阶段向用户确认
3. 审核规则是 delivery_standards 的底本，Architect 根据合同内容和用户关切调整
4. Architect 不做第一手法律分析，全部委托 Task Agent
5. 工具以 skill 形式存在，按需注入 sub-agent
6. 所有 Agent 间通讯使用 Markdown + YAML frontmatter
7. Reference 文件是参考示例，非强制模板
