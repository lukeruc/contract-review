"""图片版 PDF 和图片文件的多模态大模型处理模块.

使用 Dashscope API (Qwen-VL 模型) 识别 PDF 图片内容并转换为 Markdown.
支持处理图片格式文件：.jpg、.jpeg、.png、.bmp、.gif、.webp
"""

import base64
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import fitz  # pymupdf
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# Dashscope 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
# 使用 Qwen-VL 视觉模型进行图片识别
VISION_MODEL = "qwen-vl-max-latest"
MAX_CONCURRENT = 3  # 最大并发数
DPI = 150  # 渲染分辨率


def _get_api_key() -> str:
    """获取 Dashscope API Key."""
    if not DASHSCOPE_API_KEY:
        raise RuntimeError(
            "DASHSCOPE_API_KEY not found. Please create a .env file with your API key. "
            "See .env.example for reference."
        )
    return DASHSCOPE_API_KEY


def _pdf_page_to_image(page: fitz.Page, dpi: int = DPI) -> bytes:
    """
    将 PDF 页面渲染为 PNG 图片.

    Args:
        page: pymupdf 页面对象
        dpi: 渲染分辨率

    Returns:
        PNG 图片的字节数据
    """
    # 计算缩放矩阵
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    # 渲染页面为图片
    pix = page.get_pixmap(matrix=mat, alpha=False)

    # 转换为 PNG 字节
    return pix.tobytes("png")


def _bytes_to_base64(data: bytes) -> str:
    """将字节数据转换为 base64 字符串."""
    return base64.b64encode(data).decode("utf-8")


def _process_single_page(
    page_num: int,
    image_data: bytes,
    api_key: str,
) -> tuple[int, str | None, str | None]:
    """
    处理单个 PDF 页面.

    Args:
        page_num: 页码（从 1 开始）
        image_data: 页面图片的字节数据
        api_key: Dashscope API Key

    Returns:
        (page_num, markdown_content, error_message)
    """
    import dashscope
    from dashscope import MultiModalConversation

    dashscope.api_key = api_key

    # 准备图片数据
    image_base64 = _bytes_to_base64(image_data)
    image_data_uri = f"data:image/png;base64,{image_base64}"

    # 构建请求消息
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": image_data_uri,
                },
                {
                    "text": "请识别这张图片中的所有文字内容，并按照原始排版格式输出为 Markdown。保持标题、列表、表格等结构的完整性。"
                }
            ]
        }
    ]

    try:
        response = MultiModalConversation.call(
            model=VISION_MODEL,
            messages=messages,
        )

        if response.status_code == 200:
            # 解析响应内容
            try:
                choice = response.output.choices[0]
                message = choice.message

                # qwen-vl-max 返回格式：content[0]["text"]
                content = None

                if hasattr(message, 'content'):
                    content_val = message.content

                    # 情况 1: content 是列表
                    if isinstance(content_val, list) and len(content_val) > 0:
                        item = content_val[0]
                        if isinstance(item, dict) and "text" in item:
                            content = item["text"]
                        elif hasattr(item, 'text') and item.text:
                            content = item.text

                    # 情况 2: content 是字符串（非空）
                    elif isinstance(content_val, str) and content_val.strip():
                        content = content_val

                if content is None:
                    return (page_num, None, f"Unable to parse response: content is empty")

                return (page_num, content, None)

            except Exception as parse_err:
                return (page_num, None, f"Parse error: {str(parse_err)}")
        else:
            error_msg = f"API call failed: {response.code} - {response.message}"
            return (page_num, None, error_msg)

    except Exception as e:
        return (page_num, None, f"Error: {str(e)}")


def convert_vision_pdf(
    input_path: str | Path,
    output: str | Path | None = None,
    dpi: int = DPI,
    max_concurrent: int = MAX_CONCURRENT,
) -> str:
    """
    使用多模态大模型将图片版 PDF 转换为 Markdown.

    处理流程：
    1. 将 PDF 每页渲染为 PNG 图片
    2. 并发调用 Dashscope API 识别每页内容
    3. 按页码顺序拼接结果，用分页符分隔

    Args:
        input_path: PDF 文件路径
        output: 可选的输出文件路径，如果为 None 则返回字符串
        dpi: 渲染分辨率，默认 150
        max_concurrent: 最大并发数，默认 3

    Returns:
        Markdown 内容字符串

    Raises:
        FileNotFoundError: 如果输入文件不存在
        RuntimeError: 如果 API Key 未配置或转换失败
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 获取 API Key
    api_key = _get_api_key()

    # 打开 PDF
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    try:
        total_pages = len(doc)
        if total_pages == 0:
            return ""

        # 预先渲染所有页面为图片（避免重复渲染）
        print(f"正在渲染 {total_pages} 页 PDF 为图片...")
        page_images = []
        for page_num in range(total_pages):
            page = doc[page_num]
            image_data = _pdf_page_to_image(page, dpi)
            page_images.append(image_data)

        print(f"正在调用大模型识别内容（最大并发 {max_concurrent}）...")

        # 并发处理所有页面
        results = {}
        errors = []

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {
                executor.submit(
                    _process_single_page,
                    page_num + 1,  # 页码从 1 开始
                    page_images[page_num],
                    api_key,
                ): page_num
                for page_num in range(total_pages)
            }

            for future in as_completed(futures):
                page_num, content, error = future.result()
                if error:
                    errors.append(f"Page {page_num}: {error}")
                else:
                    results[page_num] = content

                # 显示进度
                completed = len(results) + len(errors)
                if completed % 5 == 0 or completed == total_pages:
                    print(f"  进度：{completed}/{total_pages} 页")

        # 报告错误
        if errors:
            print("警告：以下页面处理失败:")
            for err in errors:
                print(f"  - {err}")

        # 按页码顺序拼接结果
        markdown_parts = []
        for page_num in range(1, total_pages + 1):
            if page_num in results:
                markdown_parts.append(f"---\n\n# Page {page_num}\n\n{results[page_num]}")
            else:
                markdown_parts.append(f"---\n\n# Page {page_num}\n\n[无法识别此页内容]")

        # 移除第一个分页符
        markdown_content = "\n\n".join(markdown_parts)
        if markdown_content.startswith("---\n\n"):
            markdown_content = markdown_content[4:]  # 移除开头的 "---\n\n"

        # 写入文件
        if output:
            output_path = Path(output).resolve()
            output_path.write_text(markdown_content, encoding="utf-8")

        return markdown_content

    finally:
        doc.close()


def convert_image(
    input_path: str | Path,
    output: str | Path | None = None,
) -> str:
    """
    使用多模态大模型将图片文件（JPG、PNG 等）转换为 Markdown.

    支持格式：.jpg、.jpeg、.png、.bmp、.gif、.webp

    Args:
        input_path: 图片文件路径
        output: 可选的输出文件路径，如果为 None 则返回字符串

    Returns:
        Markdown 内容字符串

    Raises:
        FileNotFoundError: 如果输入文件不存在
        RuntimeError: 如果 API Key 未配置或转换失败
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 获取 API Key
    api_key = _get_api_key()

    # 读取图片文件
    try:
        image_data = input_path.read_bytes()
    except Exception as e:
        raise RuntimeError(f"Failed to read image file: {e}")

    print(f"正在调用大模型识别图片内容...")

    # 处理单张图片
    page_num, content, error = _process_single_page(1, image_data, api_key)

    if error:
        raise RuntimeError(f"Image recognition failed: {error}")

    # 写入文件
    if output:
        output_path = Path(output).resolve()
        output_path.write_text(content, encoding="utf-8")

    return content
