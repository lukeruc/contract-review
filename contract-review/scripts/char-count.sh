#!/bin/bash
# 输出文件的纯文本字符数
# 用法: char-count.sh <filepath>

if [ $# -lt 1 ]; then
    echo "Usage: char-count.sh <filepath>" >&2
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: file not found: $1" >&2
    exit 1
fi

wc -m < "$1" | tr -d ' '
