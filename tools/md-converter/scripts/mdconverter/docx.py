"""DOCX to Markdown converter using pandoc.

Also handles .doc files by converting them to .docx first using LibreOffice.
"""

import shutil
import subprocess
from pathlib import Path


# Common LibreOffice installation paths on Windows
LIBREOFFICE_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def find_libreoffice() -> str:
    """
    Find the LibreOffice executable.

    First tries to find 'soffice' in PATH, then checks common installation locations.

    Returns:
        Path to the LibreOffice executable.

    Raises:
        RuntimeError: If LibreOffice is not installed.
    """
    # Try to find in PATH first
    soffice = shutil.which("soffice")
    if soffice:
        return soffice

    # Check common Windows installation paths
    for path in LIBREOFFICE_PATHS:
        if Path(path).exists():
            return path

    raise RuntimeError(
        "LibreOffice not found. Please install LibreOffice from "
        "https://www.libreoffice.org/download/ and ensure it's in your PATH."
    )


def _run_command_with_chinese_support(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """
    Run a subprocess command with proper encoding for Chinese paths.

    On Windows with Git Bash, we need to handle encoding carefully.
    """
    # Create a subprocess with proper encoding
    import sys
    startupinfo = None
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        startupinfo=startupinfo,
        **kwargs,
    )


def convert_doc_to_docx(doc_path: Path) -> Path:
    """
    Convert a .doc file to .docx using LibreOffice.

    Args:
        doc_path: Path to the .doc file.

    Returns:
        Path to the converted .docx file.

    Raises:
        RuntimeError: If LibreOffice is not installed or conversion fails.
    """
    # Find LibreOffice executable
    soffice = find_libreoffice()

    # LibreOffice headless conversion
    libreoffice_cmd = [
        soffice,
        "--headless",
        "--convert-to", "docx",
        "--outdir", str(doc_path.parent),
        str(doc_path)
    ]

    result = _run_command_with_chinese_support(libreoffice_cmd)

    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

    # The converted file should have the same name but with .docx extension
    docx_path = doc_path.with_suffix(".docx")
    if not docx_path.exists():
        raise RuntimeError(f"Converted .docx file not found at {docx_path}")

    return docx_path


def convert_docx(input_path: str | Path, output: str | Path | None = None, convert_legacy: bool = False) -> str:
    """
    Convert a DOCX file to Markdown using pandoc.

    Args:
        input_path: Path to the input DOCX file.
        output: Optional path to write the output. If None, returns the markdown string.
        convert_legacy: If True, first convert .doc to .docx before processing.

    Returns:
        The markdown content as a string.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If pandoc is not installed or conversion fails.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    temp_docx = None
    try:
        # Handle .doc files by converting to .docx first
        if convert_legacy or input_path.suffix.lower() == ".doc":
            temp_docx = convert_doc_to_docx(input_path)
            input_path = temp_docx

        # Build pandoc command: pandoc -f docx -t markdown <input>
        cmd = ["pandoc", "-f", "docx", "-t", "markdown", str(input_path)]

        result = _run_command_with_chinese_support(cmd)

        if result.returncode != 0:
            raise RuntimeError(f"pandoc conversion failed: {result.stderr}")

        markdown_content = result.stdout

        if output:
            output_path = Path(output).resolve()
            output_path.write_text(markdown_content, encoding="utf-8")

        return markdown_content
    finally:
        # Clean up temporary .docx file if created
        if temp_docx and temp_docx.exists():
            try:
                temp_docx.unlink()
            except Exception:
                pass  # Ignore cleanup errors


def convert_doc(input_path: str | Path, output: str | Path | None = None) -> str:
    """
    Convert a .doc file to Markdown.

    First converts .doc to .docx using LibreOffice, then uses pandoc for Markdown conversion.

    Args:
        input_path: Path to the input .doc file.
        output: Optional path to write the output. If None, returns the markdown string.

    Returns:
        The markdown content as a string.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If LibreOffice or pandoc is not installed, or conversion fails.
    """
    return convert_docx(input_path, output, convert_legacy=True)
