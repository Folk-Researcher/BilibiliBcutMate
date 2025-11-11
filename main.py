import argparse
import json
import sys
from pathlib import Path

from bcut_models import load_bcut_project, summarize_project
from bcut_drafts import build_drafts_index


def main():
    parser = argparse.ArgumentParser(description="Bcut 项目工具：解析单个草稿或汇总 Drafts 目录")
    subparsers = parser.add_subparsers(dest="command")

    p_parse = subparsers.add_parser("parse", help="解析单个 .bjson 草稿文件并输出摘要")
    p_parse.add_argument("file", help="Path to the Bcut .bjson file")

    p_summarize = subparsers.add_parser("summarize-drafts", help="扫描并汇总 Drafts 目录信息")
    p_summarize.add_argument("dir", help="Path to the 'Bcut Drafts' directory")

    args = parser.parse_args()

    if args.command == "parse":
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        try:
            project = load_bcut_project(str(file_path))
            summary = summarize_project(project)
            print("解析成功：")
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"解析失败: {e}")
            sys.exit(1)
    elif args.command == "summarize-drafts":
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"目录不存在: {dir_path}")
            sys.exit(1)
        try:
            index = build_drafts_index(str(dir_path))
            print(json.dumps(index, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"汇总失败: {e}")
            sys.exit(1)
    else:
        print("请选择命令：\n  解析单个草稿: uv run main.py parse <path/to/file.bjson>\n  汇总 Drafts 目录: uv run main.py summarize-drafts ""Bcut Drafts""")
        sys.exit(1)


if __name__ == "__main__":
    main()
