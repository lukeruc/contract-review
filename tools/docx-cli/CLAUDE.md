# CLAUDE.md

## 项目概述

这是一个 Claude Code skill 项目，目标是将 python-docx 库的功能尽可能完整地封装为 CLI 命令，使 Agent 可以通过命令行完成 .docx 文件的读取、创建和修改操作，无需编写 Python 代码。

## 原则

- 覆盖 python-docx 的主要能力：段落、表格、样式、批注、修订标记、页眉页脚、节属性等。
- CLI 接口设计由 python-docx 的 API 结构自然驱动。先梳理库能做什么，再映射为子命令和参数。
- 保证格式完整性。任何操作后的 .docx 必须可用 Word/WPS 正常打开。
- 修改类的操作默认原地修改文件，提供 `--output` 参数指定输出路径。
