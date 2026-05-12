#!/usr/bin/env python3
"""将 PDF、DOCX、DOC 和图片文件转换为 Markdown."""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from mdconverter import convert


# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# 批处理最大并发线程数
MAX_WORKERS = 2


def find_file(name: str) -> Path | None:
    """根据文件名查找文件，支持模糊匹配和绝对路径."""
    cwd = Path.cwd()

    # 如果是绝对路径
    if Path(name).is_absolute():
        if Path(name).exists():
            return Path(name)
        # 绝对路径但文件不存在（可能是编码问题），尝试在目标目录模糊匹配
        parent = Path(name).parent
        target_name = Path(name).name
        if parent.exists():
            for f in parent.iterdir():
                # 字节级匹配（绕过编码问题）
                try:
                    target_bytes = target_name.encode('utf-8', errors='ignore')
                    f_bytes = f.name.encode('utf-8')
                    if target_bytes and f_bytes:
                        # 检查共同字节数
                        common = set(target_bytes) & set(f_bytes)
                        if len(common) > 10:
                            return f
                except:
                    pass
        return None

    # 相对路径 - 直接匹配
    direct = cwd / name
    if direct.exists():
        return direct

    # 模糊匹配
    for f in cwd.iterdir():
        if name in f.name:
            return f

    # 按扩展名匹配
    ext = Path(name).suffix.lower()
    if ext in SUPPORTED_EXTENSIONS:
        for f in cwd.iterdir():
            if f.suffix.lower() == ext:
                return f

    return None


def collect_files(folder: Path) -> list[Path]:
    """递归收集文件夹下所有支持的文件."""
    files = []
    for f in folder.rglob('*'):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(f)
    return files


def batch_convert(folder: Path, use_vision: bool | None = None) -> tuple[int, int]:
    """
    批处理模式：遍历文件夹中的所有支持的文件并转换。

    Args:
        folder: 输入文件夹路径
        use_vision: 是否强制使用 vision API

    Returns:
        (成功数量，失败数量)
    """
    # 收集所有支持的文件
    files = collect_files(folder)

    if not files:
        print(f"警告：在 '{folder}' 中未找到支持的文件")
        return 0, 0

    print(f"找到 {len(files)} 个文件需要转换")
    print(f"输出目录：{folder / 'mdconverter-output'}")
    print(f"最大并发线程数：{MAX_WORKERS}")
    print("-" * 50)

    # 输出目录
    output_folder = folder / "mdconverter-output"
    output_folder.mkdir(exist_ok=True)

    success_count = 0
    fail_count = 0

    def process_file(input_file: Path) -> tuple[Path, bool, str]:
        """处理单个文件，返回 (文件路径，是否成功，消息)"""
        try:
            # 计算输出文件路径（保持目录结构）
            relative_path = input_file.relative_to(folder)
            output_file = output_folder / relative_path.with_suffix('.md')

            # 确保输出目录存在
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 转换
            convert(input_file, output=output_file, use_vision=use_vision)
            return (input_file, True, str(output_file.relative_to(folder)))
        except Exception as e:
            return (input_file, False, str(e))

    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_file = {executor.submit(process_file, f): f for f in files}

        # 处理完成的任务
        for i, future in enumerate(as_completed(future_to_file), 1):
            input_file = future_to_file[future]
            print(f"[{i}/{len(files)}] 完成：{input_file.relative_to(folder)}")

            try:
                file_path, success, message = future.result()
                if success:
                    print(f"        成功：{message}")
                    success_count += 1
                else:
                    print(f"        失败：{message}")
                    fail_count += 1
            except Exception as e:
                print(f"        异常：{e}")
                fail_count += 1

    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description="将 PDF、DOCX、DOC 和图片文件转换为 Markdown"
    )
    parser.add_argument(
        "input",
        help="输入文件路径（PDF、DOCX、DOC 或图片格式；或文件夹路径）"
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="输出文件路径（可选，默认为 <输入文件名>.md；批处理模式下此参数无效）"
    )
    parser.add_argument(
        "--use-vision",
        action="store_true",
        help="强制使用多模态大模型处理 PDF（适用于图片版 PDF，需配置 DASHSCOPE_API_KEY）"
    )
    parser.add_argument(
        "--no-vision",
        action="store_true",
        help="强制使用文本提取处理 PDF（仅适用于文字版 PDF）"
    )

    args = parser.parse_args()

    # 处理 vision 参数
    use_vision = None
    if args.use_vision and args.no_vision:
        print("错误：--use-vision 和 --no-vision 不能同时使用")
        sys.exit(1)
    elif args.use_vision:
        use_vision = True
    elif args.no_vision:
        use_vision = False

    input_arg = args.input
    input_path = find_file(input_arg)

    if input_path is None:
        print(f"错误：找不到文件 '{input_arg}'")
        sys.exit(1)

    # 检查是否为文件夹（批处理模式）
    if input_path.is_dir():
        print(f"检测到文件夹，进入批处理模式：{input_path}")
        print("=" * 50)

        success, failed = batch_convert(input_path, use_vision=use_vision)

        print("=" * 50)
        print(f"批处理完成：成功 {success} 个，失败 {failed} 个")

        if failed > 0:
            sys.exit(1)
        return

    # 单文件模式
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = input_path.with_suffix('.md')

    convert(input_path, output=output_file, use_vision=use_vision)
    print(f"转换成功：{output_file}")


if __name__ == "__main__":
    main()
