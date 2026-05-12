"""Markdown converter for PDF, DOCX, DOC, and image files."""

from pathlib import Path

from .docx import convert_doc, convert_docx
from .pdf import convert_pdf
from .vision import convert_vision_pdf, convert_image

__all__ = ["convert", "convert_doc", "convert_docx", "convert_pdf", "convert_vision_pdf", "convert_image"]


def convert(
    input_path: str | Path,
    output: str | Path | None = None,
    use_vision: bool | None = None,
) -> str:
    """
    Convert a PDF, DOCX, DOC, or image file to Markdown.

    The converter is automatically selected based on the file extension.
    DOC files are first converted to DOCX using LibreOffice, then to Markdown.

    For PDF files:
    - By default, auto-detects whether the PDF is text-based or image-based.
    - Image-based PDFs are processed using Dashscope vision API (Qwen-VL).
    - Text-based PDFs use pymupdf4llm for faster extraction.
    - Use `use_vision=True` to force vision API processing.
    - Use `use_vision=False` to force text extraction (will fail if no text layer).

    For image files (.jpg, .jpeg, .png, .bmp, .gif, .webp):
    - Always processed using Dashscope vision API (Qwen-VL).

    Args:
        input_path: Path to the input file (PDF, DOCX, DOC, or image).
        output: Optional path to write the output. If None, returns the markdown string.
        use_vision: Force vision API usage (True) or text extraction (False).
                    If None (default), auto-detects based on PDF content.

    Returns:
        The markdown content as a string.

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If conversion fails or API key is not configured.
    """
    input_path = Path(input_path)
    suffix = input_path.suffix.lower()

    if suffix == ".pdf":
        # For PDF, decide whether to use vision API
        if use_vision is None:
            # Auto-detect: check if PDF is image-based
            from .detector import is_image_based_pdf

            try:
                if is_image_based_pdf(input_path):
                    return convert_vision_pdf(input_path, output)
                else:
                    return convert_pdf(input_path, output)
            except Exception:
                # If detection fails, fall back to text extraction
                return convert_pdf(input_path, output)
        elif use_vision:
            return convert_vision_pdf(input_path, output)
        else:
            return convert_pdf(input_path, output)
    elif suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]:
        # Image files always use vision API
        return convert_image(input_path, output)
    elif suffix == ".docx":
        return convert_docx(input_path, output)
    elif suffix == ".doc":
        return convert_doc(input_path, output)
    else:
        raise ValueError(f"Unsupported file extension: {suffix}. Supported: .pdf, .docx, .doc, .jpg, .jpeg, .png, .bmp, .gif, .webp")
