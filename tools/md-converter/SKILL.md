---
name: mdconverter
description: Convert PDF, DOCX, DOC, and image files to Markdown. Use when the user explicitly asks to convert a file to Markdown, runs /mdconvert, or says "convert this PDF/DOCX/image to md". Supports text-based PDFs (fast pymupdf4llm extraction), image-based/scanned PDFs (Dashscope vision API), DOCX (pandoc), DOC (LibreOffice + pandoc), and images like JPG/PNG (vision API). Also supports batch conversion of entire folders.
compatibility: Requires Python 3.12+, pymupdf4llm, dashscope, python-dotenv. System deps: pandoc (for DOCX), LibreOffice (for DOC). Dashscope API key for vision features.
---

# mdconverter — Convert files to Markdown

Bundled Python tool that converts PDF, DOCX, DOC, and image files to Markdown. Only use this skill when the user explicitly asks to convert files.

## Conversion

All commands run from the skill's `scripts/` directory. Replace `{SKILL_DIR}` with this skill's base directory.

**Single file** — output auto-saved as `<input>.md` in same directory:
```bash
cd {SKILL_DIR}/scripts && python mdconvert.py "/path/to/file.pdf"
```

**Single file with explicit output path:**
```bash
cd {SKILL_DIR}/scripts && python mdconvert.py "/path/to/file.pdf" "/path/to/output.md"
```

**Batch mode** — converts all supported files in a folder:
```bash
cd {SKILL_DIR}/scripts && python mdconvert.py "/path/to/folder/"
```
Output goes to `<folder>/mdconverter-output/`, preserving subdirectory structure.

**Force vision API** (for scanned/image-based PDFs):
```bash
cd {SKILL_DIR}/scripts && python mdconvert.py "/path/to/scanned.pdf" --use-vision
```

**Force text extraction** (skip vision auto-detection):
```bash
cd {SKILL_DIR}/scripts && python mdconvert.py "/path/to/text.pdf" --no-vision
```

## Install guide

Tell the user what to install based on what's missing:

**pymupdf4llm** (text-based PDFs):
```bash
pip install pymupdf4llm
```

**dashscope + python-dotenv** (scanned PDFs / images via vision API):
```bash
pip install dashscope python-dotenv
```
Then create a `.env` file (in the project directory or home) with:
```
DASHSCOPE_API_KEY=your_api_key_here
```
Get a key at: https://dashscope.console.aliyun.com/

**pandoc** (DOCX):
- Linux: `sudo apt install pandoc`
- macOS: `brew install pandoc`
- Windows: `choco install pandoc`

**LibreOffice** (.doc legacy files):
- Linux: `sudo apt install libreoffice`
- macOS: `brew install --cask libreoffice`
- Windows: `choco install libreoffice`

## After conversion

Tell the user where the output was saved. If the result looks wrong (garbled text, empty output), suggest:
- `--use-vision` if the PDF might be scanned/image-based
- `--no-vision` to skip vision and force text extraction
