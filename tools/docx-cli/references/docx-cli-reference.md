# Docx CLI Reference

## Global conventions

| Convention | Detail |
|---|---|
| Index origin | 0-based for paragraphs, tables, runs, sections, rows, columns |
| Output control | `-o, --output PATH` writes to a new file instead of modifying in-place |
| JSON mode | `--json` flag on any list/read command outputs structured JSON |
| Numeric values | Sizes in points (pt); images in inches (in); colors in hex (RRGGBB) |

---

## `docx read <file>`

Read document content. Default: paragraphs + tables.

```
Options:
  --paragraphs / --no-paragraphs    Show paragraphs (default: yes)
  --tables / --no-tables            Show tables (default: yes)
  --sections / --no-sections        Show section info
  --styles / --no-styles            List styles
  --headers-footers / --no-headers-footers  Show header/footer text
  --images / --no-images            List images
  --properties / --no-properties    Show core properties
  --json                            JSON output
```

---

## `docx create <file>`

Create a new blank document. Use `--template` to base it on an existing file.

```
Options:
  --template PATH    Existing .docx to use as template
```

---

## `docx paragraph`

### `add`
```
docx paragraph add <file> --text TEXT [--style NAME] [--after N]
                   [--alignment left|center|right|justify] [-o PATH]
```
- `--after N`: insert after paragraph index N; omit to append to end
- `--style`: use any built-in style like "Heading 1", "Title", "Normal"

### `list`
```
docx paragraph list <file> [--json]
```

### `delete`
```
docx paragraph delete <file> --index N [-o PATH]
```

### `update`
```
docx paragraph update <file> --index N [--text TEXT] [--style NAME]
                    [--alignment left|center|right|justify]
                    [--line-spacing single|1.5|double]
                    [--space-before PT] [--space-after PT] [-o PATH]
```
- All options are optional; only provided ones are changed
- `--text` replaces all existing runs with a single new run

---

## `docx run`

### `add`
```
docx run add <file> --para N --text TEXT
          [--bold|--no-bold] [--italic|--no-italic]
          [--underline|--no-underline]
          [--size PT] [--font "Font Name"] [--color RRGGBB]
          [--highlight COLOR_NAME] [--strike|--no-strike]
          [--double-strike|--no-double-strike]
          [--superscript|--no-superscript] [--subscript|--no-subscript]
          [--all-caps|--no-all-caps] [--small-caps|--no-small-caps]
          [--hidden|--no-hidden] [--style "Character Style"] [-o PATH]
```
- `--color`: hex format, e.g. `FF0000` or `#FF0000` for red
- `--highlight`: color name: YELLOW, CYAN, RED, GREEN, BLUE, PINK, etc.

### `list`
```
docx run list <file> --para N [--json]
```

### `update`
```
docx run update <file> --para N --run M [--text TEXT] [same font options as add] [-o PATH]
```

---

## `docx table`

### `add`
```
docx table add <file> --rows N --cols N
            [--header "Col1,Col2,..."] [--data JSON_ARRAY]
            [--after N] [--style "Table Grid"] [-o PATH]
```
- `--header`: comma-separated column headers (fills row 0)
- `--data`: JSON array of arrays, e.g. `[["a","b"],["c","d"]]`

### `list`
```
docx table list <file> [--json]
```

### `delete`
```
docx table delete <file> --index N [-o PATH]
```

### `cell`
```
docx table cell <file> --table N --row N --col N [--text TEXT] [-o PATH]
```
- Omit `--text` to read the cell value instead of writing

### `rows`
```
docx table rows <file> --table N [--add N] [--delete N] [-o PATH]
```
- `--add N`: add N empty rows to the end
- `--delete N`: delete row at index N

### `cols`
```
docx table cols <file> --table N [--add N] [--delete N] [-o PATH]
```
- `--add N`: add N columns (1 inch wide each)
- `--delete N`: delete column at index N

---

## `docx image`

### `add`
```
docx image add <file> <image_path> [--para N] [--width IN] [--height IN] [-o PATH]
```
- Supports PNG, JPEG, GIF, BMP
- Width/height in inches; if omitted, uses image's native size

### `list`
```
docx image list <file> [--json]
```

---

## `docx section`

### `add`
```
docx section add <file> [--type continuous|new_page|new_column|even_page|odd_page]
               [--orientation portrait|landscape] [-o PATH]
```
- Default start type: `new_page`

### `list`
```
docx section list <file> [--json]
```

### `update`
```
docx section update <file> --index N
                [--orientation portrait|landscape]
                [--margin-top PT] [--margin-bottom PT]
                [--margin-left PT] [--margin-right PT]
                [--page-width PT] [--page-height PT] [-o PATH]
```
- Page dimensions in points (1 inch = 72 pt)
- A4 default: 595 x 842 pt; Letter default: 612 x 792 pt

---

## `docx header-footer`

### `add`
```
docx header-footer add <file>
    --type header|footer|first_page_header|first_page_footer
    --text TEXT [--section N] [--style NAME]
    [--alignment left|center|right|justify] [-o PATH]
```
- `--section N`: target section (default: 0)
- Using `first_page_header`/`first_page_footer` automatically enables
  different-first-page mode on the section

### `list`
```
docx header-footer list <file> [--section N] [--json]
```

---

## `docx style`

### `list`
```
docx style list <file> [--type paragraph|character|table|list] [--json]
```
- Common built-in styles: Normal, Heading 1-9, Title, Subtitle, List Bullet,
  Table Grid, etc.

---

## `docx properties`

### `get`
```
docx properties get <file> [--json]
```
Returns: author, title, subject, keywords, category, comments, created,
modified, last_modified_by, revision.

### `set`
```
docx properties set <file> [--title TEXT] [--author TEXT] [--subject TEXT]
                   [--keywords TEXT] [--category TEXT] [--comments TEXT] [-o PATH]
```

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | General error (invalid index, file not found, bad parameter) |
| 2 | Usage error (missing required option) |
