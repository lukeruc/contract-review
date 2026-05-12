"""PDF to Markdown converter using pymupdf4llm."""

from pathlib import Path

import pymupdf4llm


def convert_pdf(input_path: str | Path, output: str | Path | None = None) -> str:
    """
    Convert a PDF file to Markdown using pymupdf4llm.

    Args:
        input_path: Path to the input PDF file.
        output: Optional path to write the output. If None, returns the markdown string.

    Returns:
        The markdown content as a string.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If conversion fails.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        markdown_content = pymupdf4llm.to_markdown(str(input_path))
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}") from e

    if output:
        output_path = Path(output).resolve()
        output_path.write_text(markdown_content, encoding="utf-8")

    return markdown_content
