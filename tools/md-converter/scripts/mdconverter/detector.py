"""PDF 类型检测器：判断 PDF 是否为图片版（无文本层）."""

from pathlib import Path

import fitz  # pymupdf


def is_image_based_pdf(
    input_path: str | Path,
    text_threshold: int = 50,
    page_ratio_threshold: float = 0.5
) -> bool:
    """
    检测 PDF 是否为图片版（无文本层）。

    通过检查 PDF 中每页的文本含量来判断：
    - 如果大部分页面的文本内容极少，则判定为图片版 PDF
    - 如果大部分页面有充足文本，则判定为文字版 PDF

    Args:
        input_path: PDF 文件路径
        text_threshold: 判定为有文本的最小字符数阈值，默认 50 个字符
        page_ratio_threshold: 判定为文字版 PDF 所需的最小页面比例，默认 0.5

    Returns:
        True 如果是图片版 PDF，False 如果是文字版 PDF
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        doc = fitz.open(input_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    try:
        total_pages = len(doc)
        if total_pages == 0:
            return False

        # 统计有文本的页面数
        pages_with_text = 0

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text").strip()

            # 如果页面文本超过阈值，认为该页有文本
            if len(text) > text_threshold:
                pages_with_text += 1

        # 如果有文本的页面比例低于阈值，认为是图片版 PDF
        text_ratio = pages_with_text / total_pages
        return text_ratio < page_ratio_threshold

    finally:
        doc.close()


def detect_pdf_type(input_path: str | Path) -> str:
    """
    检测 PDF 类型并返回处理建议。

    Args:
        input_path: PDF 文件路径

    Returns:
        "text" 如果是文字版 PDF，"image" 如果是图片版 PDF
    """
    if is_image_based_pdf(input_path):
        return "image"
    return "text"
