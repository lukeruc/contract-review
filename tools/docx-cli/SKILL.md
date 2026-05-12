---
name: docx
description: >
  Create, read, and edit .docx (Microsoft Word) documents. Use this skill
  whenever the user needs to work with Word documents — generating reports,
  reading or extracting text, modifying formatting, adding tables/images,
  setting headers/footers, changing page layout, or any other .docx task.
  This is THE skill for .docx files; do not write raw python-docx code.
---

# Docx CLI Skill

Use the `docx` CLI tool to work with `.docx` files. It wraps python-docx
so you never need to write Python code. The tool is at
`./scripts/docx_cli.py` relative to this skill directory. All commands
follow this pattern:

```
python <skill-dir>/scripts/docx_cli.py <command> [options]
```

## Core concepts

- **0-based indexing**: paragraphs, tables, runs, sections, rows, and
  columns are all numbered starting from 0. Use the `list` subcommands to
  see what exists.
- **In-place editing**: write commands modify the file directly unless
  `-o/--output` is given to save a copy.
- **JSON mode**: most `list` commands and `read` support `--json` for
  structured output that is easier to parse.
- **Format safety**: the tool keeps the OOXML structure valid; output
  files open in Word, WPS, LibreOffice without errors.

## Reading documents

```
docx read <file> [flags]
```

By default shows paragraphs and tables. Add flags to see more:
`--headers-footers`, `--sections`, `--styles`, `--images`, `--properties`.
Use `--json` for structured output.

To focus on one aspect, use the specific `list` subcommands:
- `docx paragraph list <file> [--json]` — every paragraph with its index and style
- `docx run list <file> --para N [--json]` — runs within a paragraph with font details
- `docx table list <file> [--json]` — tables with dimensions, styles, and cell text
- `docx image list <file> [--json]` — inline shapes and drawing elements
- `docx section list <file> [--json]` — page dimensions, margins, orientation
- `docx header-footer list <file> [--section N] [--json]` — header/footer text
- `docx style list <file> [--type paragraph|character|table|list] [--json]`
- `docx properties get <file> [--json]` — author, title, dates, etc.

## Creating documents

```
docx create <file> [--template <existing.docx>]
```

Creates an empty `.docx` (or from a template). Then add content with the
commands below.

## Paragraphs

```
docx paragraph add <file> --text "..." [--style "Heading 1"] [--after N]
                   [--alignment left|center|right|justify] [-o out.docx]

docx paragraph update <file> --index N [--text "..."] [--style "..."]
                      [--alignment ...] [--line-spacing single|1.5|double]
                      [--space-before PT] [--space-after PT] [-o out.docx]

docx paragraph delete <file> --index N [-o out.docx]
```

`--after N` inserts the new paragraph after paragraph N (0-indexed).
Without `--after`, the paragraph is appended to the end.

## Runs (inline formatting)

A paragraph contains runs — spans of text with uniform formatting. Use
runs to make some words bold, change font size, etc.

```
docx run add <file> --para N --text "..." [--bold] [--italic] [--size 14]
            [--font "Times New Roman"] [--color FF0000] [--highlight YELLOW]
            [--underline] [--strike] [--superscript|--subscript]
            [--all-caps] [--small-caps] [--hidden] [-o out.docx]

docx run list <file> --para N [--json]

docx run update <file> --para N --run M [same formatting options as add] [-o out.docx]
```

Boolean font flags support explicit `--bold`/`--no-bold` (tri-state:
omitted = leave unchanged).

## Tables

```
docx table add <file> --rows N --cols N [--header "Col1,Col2"]
              [--data '[["a","b"],["c","d"]]'] [--style "Table Grid"]
              [--after N] [-o out.docx]

docx table list <file> [--json]

docx table delete <file> --index N [-o out.docx]

docx table cell <file> --table N --row N --col N [--text "..."] [-o out.docx]

docx table rows <file> --table N [--add N] [--delete N] [-o out.docx]

docx table cols <file> --table N [--add N] [--delete N] [-o out.docx]
```

`--data` accepts a JSON array of arrays. Each inner array is one row of
cell values. When `--header` is used, `--data` fills rows starting at row 1.

## Images

```
docx image add <file> <image_path> [--para N] [--width INCHES] [--height INCHES] [-o out.docx]

docx image list <file> [--json]
```

If `--para` is given, the image is added to a new run inside that
paragraph. Otherwise it's added as a standalone image at the end.

## Sections

```
docx section add <file> [--type continuous|new_page|new_column|even_page|odd_page]
               [--orientation portrait|landscape] [-o out.docx]

docx section list <file> [--json]

docx section update <file> --index N [--orientation ...] [--margin-top PT]
                    [--margin-bottom PT] [--margin-left PT] [--margin-right PT]
                    [--page-width PT] [--page-height PT] [-o out.docx]
```

## Headers and footers

```
docx header-footer add <file> --type header|footer|first_page_header|first_page_footer
                      --text "..." [--section N] [--alignment ...] [-o out.docx]

docx header-footer list <file> [--section N] [--json]
```

## Document properties

```
docx properties get <file> [--json]

docx properties set <file> [--title "..."] [--author "..."] [--subject "..."]
                   [--keywords "..."] [--category "..."] [--comments "..."] [-o out.docx]
```

## Common workflows

**Create a report from scratch:**
```
docx create report.docx
docx paragraph add report.docx --text "Annual Report" --style "Title"
docx paragraph add report.docx --text "Introduction" --style "Heading 1"
docx paragraph add report.docx --text "Lorem ipsum..."
docx table add report.docx --rows 4 --cols 3 --header "Q1,Q2,Q3" --data '[["10","20","30"],["40","50","60"],["70","80","90"]]'
docx properties set report.docx --title "Annual Report" --author "Jane"
```

**Edit an existing document:**
```
docx read existing.docx                    # see what's there
docx paragraph update existing.docx --index 2 --text "Updated text"
docx run add existing.docx --para 0 --text "IMPORTANT: " --bold --color FF0000
docx table cell existing.docx --table 0 --row 1 --col 0 --text "New value"
```

**Reformat a document:**
```
docx paragraph update existing.docx --index 0 --alignment center
docx section update existing.docx --index 0 --margin-left 72 --margin-right 72
```

## When things go wrong

- **"File not found"**: create it with `docx create` first
- **"Index out of range"**: use `list` or `read` to check valid indices
- **Style not found**: use `docx style list` to see available style names
- **JSON parse error**: check `--data` syntax — use double quotes, not single

## Reference

For full option details, read `references/docx-cli-reference.md`.
