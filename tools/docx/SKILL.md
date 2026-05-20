---
name: safe-docx
description: >-
  Operate on Word (.docx) documents — read, edit, comment, footnote, save with tracked changes.
  Use whenever the user asks to read a Word file, edit a contract, add comments to a docx,
  redline a document, insert footnotes, or create a new docx from a template.
  Also use when the user mentions .docx files or Word documents in any context.
  This skill wraps the safe-docx MCP server via a bash helper script, since MCP tools
  are not natively available in this environment.
requires:
  binaries:
    - node (>=18.0.0)
    - npx
    - pandoc
  network:
    install_time: npm registry fetch (one-time)
    runtime: none
---

# safe-docx — Word Document Operations

Use the bundled `scripts/docx-helper.mjs` script for all DOCX operations. It talks to the safe-docx MCP server via JSON-RPC over stdio.

**Helper script location:** `<skill-base>/scripts/docx-helper.mjs`

## Quick Reference

| Operation | Command |
|-----------|---------|
| Read document | `node <skill>/scripts/docx-helper.mjs read --file <path>` |
| Search text | `node <skill>/scripts/docx-helper.mjs grep --file <path> --pattern <regex>` |
| Replace text | `node <skill>/scripts/docx-helper.mjs replace --file <path> --para <id> --old <text> --new <text>` |
| Add comment | `node <skill>/scripts/docx-helper.mjs comment --file <path> --para <id> --author <name> --text <comment>` |
| List comments | `node <skill>/scripts/docx-helper.mjs get-comments --file <path>` |
| Add footnote | `node <skill>/scripts/docx-helper.mjs footnote --file <path> --para <id> --text <content>` |
| Save document | `node <skill>/scripts/docx-helper.mjs save --file <path> --out <path> [--mode clean\|tracked\|both]` |
| Compare two docs | `node <skill>/scripts/docx-helper.mjs compare --original <path> --revised <path> --out <path>` |

`<skill>` is the path to this skill directory. Find it with: `ls ~/.claude/skills/safe-docx/scripts/docx-helper.mjs`

## Workflow: Editing an Existing Document

1. **Read** to get paragraph IDs and structure:
   ```
   node <skill>/scripts/docx-helper.mjs read --file /path/to/doc.docx
   ```
   Each paragraph gets a stable `_bk_*` ID. Note the IDs you need to target.

2. **Search** for specific text (optional):
   ```
   node <skill>/scripts/docx-helper.mjs grep --file /path/to/doc.docx --pattern "search term"
   ```
   Returns matching paragraphs with their IDs.

3. **Replace, comment, and save in one chained invocation:**
   ```
   node <skill>/scripts/docx-helper.mjs \
     replace --file /path/to/doc.docx --para _bk_xxx --old "old" --new "new" \
     --and replace --file /path/to/doc.docx --para _bk_yyy --old "old2" --new "new2" \
     --and comment --file /path/to/doc.docx --para _bk_xxx --author "Reviewer" --text "Reason" \
     --and save --file /path/to/doc.docx --out /path/to/output.docx --mode tracked
   ```
   All edits and comments must be chained in one command to share MCP session state. Only `save` persists to disk.

4. **Verify** the output:
   ```
   node <skill>/scripts/docx-helper.mjs read --file /path/to/output.docx
   node <skill>/scripts/docx-helper.mjs get-comments --file /path/to/output.docx
   ```

## Workflow: Creating a New Document from Template

safe-docx cannot create documents from scratch. Use pandoc for bootstrapping:

1. **Extract template structure:**
   ```bash
   pandoc template.docx -t markdown --wrap=none
   ```

2. **Generate content** by filling placeholders with real data. Write the result as a markdown file.

3. **Generate DOCX with template styles:**
   ```bash
   pandoc content.md -o output.docx --reference-doc=template.docx
   ```
   This inherits all styles from template.docx: fonts, colors, margins, headers/footers.

4. **Polish with safe-docx** — open the generated file, add comments, footnotes, fine-tune formatting:
   ```
   node <skill>/scripts/docx-helper.mjs read --file output.docx
   node <skill>/scripts/docx-helper.mjs comment --file output.docx ...
   node <skill>/scripts/docx-helper.mjs save --file output.docx --out final.docx
   ```

## What pandoc --reference-doc Inherits

Fonts, sizes, colors, heading styles, paragraph spacing, margins, page size, headers/footers.

## What Requires safe-docx (pandoc cannot do)

Tracked changes, comments, footnotes, watermarks, complex table formatting (merged cells, cell shading), images in specific positions.

## Critical: Chaining Operations with `--and`

**Each `node docx-helper.mjs` invocation starts a fresh MCP server process.** All modifications (replace, comment, footnote) exist only in memory within that process. When the command exits, unsaved changes are lost.

To perform multiple operations that build on each other, **chain them with `--and` within a single command**:

```
node <skill>/scripts/docx-helper.mjs \
  replace --file doc.docx --para _bk_xxx --old "旧文本" --new "新文本" \
  --and comment --file doc.docx --para _bk_xxx --author "审核方" --text "修改说明" \
  --and comment --file doc.docx --para _bk_yyy --author "审核方" --text "另一条批注" \
  --and save --file doc.docx --out output.docx --mode tracked
```

This runs all operations in the same MCP session. Each `--and` starts the next operation within the existing server process, accumulating edits and comments. The final `save` persists everything to disk.

**Read and grep are read-only — they don't need chaining** and can run independently.

## Important Notes

- `--file` in all commands refers to the same file. The MCP server loads it at the start of each operation.
- `--out` must be a different path from `--file` to avoid corruption.
- Paragraph IDs (`_bk_*`) are stable for a given file — same file, same IDs every time.
- The first call in any workflow may take a few seconds as npx fetches the package (one-time).
- Path policy restricts file access to `~/` and system temp. Use absolute paths.

## Troubleshooting

- **"Cannot read properties of undefined"**: check that `--file` exists and is a valid .docx
- **ANCHOR_NOT_FOUND**: the `--para` ID doesn't exist in the document. Re-run `read` to get current IDs.
- **npx hangs first time**: first run downloads the npm package. Subsequent runs are fast.
