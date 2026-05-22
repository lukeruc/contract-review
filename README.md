# Contract Review

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An AI-powered contract review system built on Claude Code. Submit a contract (.docx / .pdf), get a **written audit opinion** and a **redlined .docx with tracked changes and comments**.

[中文文档](README_zh.md)

## Architecture

The system uses a three-layer delegation model inspired by general contracting:

```
User → Architect → Task Agents × N → Tools
            ↕
       Reviewer (complex mode only)
```

| Role | Responsibility |
|------|---------------|
| **Architect** | Single user entry point. Never performs first-hand legal analysis. Judges, plans, delegates, distills, and signs off on deliverables |
| **Task Agent** | Ephemeral sub-agent created per task, destroyed on completion. Does all the actual reading, analyzing, drafting, and editing |
| **Reviewer** | Complex mode only. Independent sub-agent that checks Task Agent output against delivery standards. Up to 3 review cycles per agent |

The core principle: the Architect delegates every substantive task — reading contracts, searching case law, analyzing clauses, drafting opinions, editing text — to Task Agents. The Architect only manages and judges.

## Modules

| Module | Entry | Purpose |
|--------|-------|---------|
| **contract-review** | `/contract-review` | The main module. Audits contracts and produces an audit opinion + redlined .docx |
| **rule-builder** | `/rule-builder` | Generates audit rule files from corporate contract templates through Q&A interaction |

Rule-builder produces rules stored in `rules/`; contract-review loads those rules to drive its audits.

## Workflow (contract-review)

```
Bootstrap (convert format → character count → confirm stance/mode)
    │
    ├── Simple mode (≤10,000 chars suggested, user can override)
    │     1. Contract type identification + rule matching
    │     2. Audit Agent reviews entire contract
    │     3. Translation Agent converts audit opinion → revisions.json (operation manual)
    │     4. Revision Agent applies changes via docx-mcp (tracked changes + comments)
    │     5. Deliver: audit-opinion.md + revised.docx
    │
    └── Complex mode (full mechanism)
          Phase 1: Preliminary design (structure → commercial conditions → cross-references)
          Phase 2: Multiple Audit Agents in parallel + Reviewer quality checks
          Phase 3: Assembly — merge audit outputs into a single opinion
          Phase 4: Translation Agent → Revision Agent (docx-mcp)
          Phase 5: Format + deliver
```

## Installation

### Prerequisites

- **Claude Code** (CLI or IDE extension)
- **Python 3.12+**
- **pandoc** (for .docx → Markdown conversion)

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt install pandoc

# Windows
winget install pandoc
```

### Step 1: Clone

```bash
git clone https://github.com/lukeruc/contract-review.git
cd contract-review
```

### Step 2: Python dependencies

```bash
pip install -r tools/requirements.txt
```

### Step 3: Install docx-mcp MCP server

docx-mcp handles Word document editing with tracked changes, comments, and paragraph insertion. **Required.**

```bash
claude mcp add docx-mcp -- uvx docx-mcp-server
```

If the `claude mcp` command is unavailable, manually add to your Claude Code MCP config (`~/.claude/settings.json`):

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

A `docx-mcp` skill auto-installs on first server start, providing usage guidance.

### Step 4: Install tool skills

Install the three helper skills from `tools/`:

#### mdconverter (document → Markdown)

```bash
claude skill add mdconverter --path tools/md-converter
# Or manually: copy tools/md-converter/ to ~/.claude/skills/mdconverter/
```

> Scanned PDFs require a Dashscope API key. Set `DASHSCOPE_API_KEY`.

#### yd-law (legal database search)

```bash
claude skill add yd-law --path tools/yd-law
```

> Requires a YD Law API key. Set `YD_KEY`. Skip this if you don't need case law search — the system will still work using contract logic and audit rules alone.

#### qcc (company registry lookup)

```bash
claude skill add qcc --path tools/qcc
```

> Requires a QCC API key. Set `QCC_KEY`. Skip if company lookups aren't needed.

### Step 5: Install entry skills

```bash
# Main module: contract review
claude skill add contract-review --path contract-review

# Rule builder (optional)
claude skill add rule-builder --path rule-builder
```

### Step 6: Verify

In Claude Code, type `/contract-review`. It should prompt you to upload a contract file. If nothing happens:

1. Check skill path: `ls ~/.claude/skills/contract-review/SKILL.md`
2. Check MCP server: `claude mcp list` should include `docx-mcp`
3. Check pandoc: `pandoc --version`
4. Check Python deps: `python -c "import docx, lxml, pymupdf4llm"`

## Directory Structure

```
contract-review/
├── SKILL.md                      # Contract review skill entry
├── scripts/                      # Local scripts (run by Architect)
│   ├── char-count.sh             # Character count
│   ├── scan-structure.py         # Clause numbering scanner (Chinese/English)
│   └── add-paraids.py            # Add w14:paraId attributes for docx-mcp
├── agent/                        # Fixed Agent definitions (mandatory templates)
│   ├── task-structure.md         # T-S01: structural analysis
│   ├── task-preliminary-report.md# T-PR: preliminary report
│   └── task-assembly.md          # T-ASM: merge audit outputs
├── workflows/                    # Process definitions
│   ├── simple.md                 # Simple mode
│   └── complex.md                # Complex mode (full mechanism)
├── rules/                        # Audit rule library (written by lawyers)
│   ├── construction-contract.md
│   └── nda.md
├── references/                   # Reference examples per agent type
├── schemas/                      # Inter-agent communication formats
├── tools/                        # External tool skills
│   ├── md-converter/
│   ├── yd-law/
│   └── qcc/
├── docs/                         # Design documentation
│   ├── DESIGN.md                 # Conceptual design
│   ├── TECHNICAL-DESIGN.md       # Technical design
│   └── RULE-BUILDER-DESIGN.md    # Rule-builder design
├── rule-builder/                 # Rule builder skill (standalone)
│   ├── SKILL.md
│   ├── scripts/scan-structure.py
│   └── agent/
├── LICENSE                       # MIT
└── README.md
```

## Environment Variables

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `DASHSCOPE_API_KEY` | Scanned PDF / image OCR (mdconverter) | Only for scanned documents |
| `YD_KEY` | Legal database search API (yd-law) | Optional |
| `QCC_KEY` | Company registry lookup API (qcc) | Optional |

The system works without external APIs — legal search and company lookup are enhancements, not requirements.

## API Access

- **Dashscope**: https://dashscope.aliyun.com/ — Alibaba Cloud model service, enable "OCR" capability
- **YD Law**: https://open.chineselaw.com/ — Chinese legal database API
- **QCC**: https://www.qcc.com/ — Chinese company information platform

## FAQ

**Q: `/contract-review` says ".doc format not supported"**

.doc is the legacy binary format. Use Word or WPS to save as .docx and resubmit.

**Q: The revised .docx won't open in Office**

Usually means docx-mcp isn't installed correctly. Run `claude mcp list` and verify `docx-mcp` appears.

**Q: Revision agent can't find paragraphs**

Your .docx likely lacks `w14:paraId` attributes (common with older Word versions). The system auto-runs `add-paraids.py` to fix this — no manual action needed.

**Q: Audit results seem off**

Audit quality depends on rule files in `rules/`. Rules are written and maintained by lawyers. To improve results:
- Check whether a matching rule file exists for your contract type
- Use `/rule-builder` to generate custom rules from your own templates
- In complex mode, use the post-preliminary-design pause to specify review priorities

**Q: Can I install just contract review without the rule builder?**

Yes. The rule builder (`rule-builder/`) is standalone — contract review works fine without it.

## Contributing

Issues and pull requests welcome. Rule contributions (`rules/`) from lawyers are especially appreciated.

## License

MIT — see [LICENSE](LICENSE)
