import argparse
import json
import sys
from pathlib import Path

from bcut_models import load_bcut_project, summarize_project


def main():
    parser = argparse.ArgumentParser(description="Parse a Bcut project .bjson using Pydantic models")
    parser.add_argument("file", nargs="?", help="Path to the Bcut .bjson file")
    args = parser.parse_args()

    if not args.file:
        print("请提供 Bcut 项目文件路径，例如:\n  uv run main.py bjson/20-44-55-643--{0718e8b8-ba0a-4f42-8dc6-3075d55ed1fe}.bjson")
        sys.exit(1)

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


if __name__ == "__main__":
    main()
