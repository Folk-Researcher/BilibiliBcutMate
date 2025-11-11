import argparse
import json
import sys
from pathlib import Path

from bcut_models import (
    load_bcut_project,
    summarize_project,
    create_caption,
    add_caption,
    remove_caption,
    update_caption_text,
    shift_caption_time,
    save_bcut_project,
)
from bcut_drafts import build_drafts_index


def main():
    parser = argparse.ArgumentParser(description="Bcut 项目工具：解析单个草稿或汇总 Drafts 目录")
    subparsers = parser.add_subparsers(dest="command")

    p_parse = subparsers.add_parser("parse", help="解析单个 .bjson 草稿文件并输出摘要")
    p_parse.add_argument("file", help="Path to the Bcut .bjson file")

    p_summarize = subparsers.add_parser("summarize-drafts", help="扫描并汇总 Drafts 目录信息")
    p_summarize.add_argument("dir", help="Path to the 'Bcut Drafts' directory")

    # 字幕操作子命令
    p_add = subparsers.add_parser("add-caption", help="在指定字幕轨添加字幕")
    p_add.add_argument("file", help="Path to the Bcut .bjson file")
    p_add.add_argument("text", help="字幕文本")
    p_add.add_argument("start_ms", type=int, help="开始时间 (毫秒)")
    p_add.add_argument("duration_ms", type=int, help="持续时间 (毫秒)")
    p_add.add_argument("--track-index", type=int, default=0, help="字幕轨索引，默认 0")
    p_add.add_argument("--font-name", type=str, default=None, help="可选：字体名")
    p_add.add_argument("--font-path", type=str, default=None, help="可选：字体路径")
    p_add.add_argument("--out-path", type=str, default=None, help="输出文件路径，默认 <原文件>.modified.bjson")

    p_rm = subparsers.add_parser("remove-caption", help="按 idString 删除字幕")
    p_rm.add_argument("file", help="Path to the Bcut .bjson file")
    p_rm.add_argument("caption_id", help="字幕 idString")
    p_rm.add_argument("--track-index", type=int, default=0, help="字幕轨索引，默认 0")
    p_rm.add_argument("--out-path", type=str, default=None, help="输出文件路径，默认 <原文件>.modified.bjson")

    p_up = subparsers.add_parser("update-caption", help="按 idString 更新字幕文本")
    p_up.add_argument("file", help="Path to the Bcut .bjson file")
    p_up.add_argument("caption_id", help="字幕 idString")
    p_up.add_argument("new_text", help="新的字幕文本")
    p_up.add_argument("--track-index", type=int, default=0, help="字幕轨索引，默认 0")
    p_up.add_argument("--out-path", type=str, default=None, help="输出文件路径，默认 <原文件>.modified.bjson")

    p_sh = subparsers.add_parser("shift-caption", help="按 idString 平移字幕时间")
    p_sh.add_argument("file", help="Path to the Bcut .bjson file")
    p_sh.add_argument("caption_id", help="字幕 idString")
    p_sh.add_argument("delta_ms", type=int, help="时间偏移 (毫秒，可为负)")
    p_sh.add_argument("--track-index", type=int, default=0, help="字幕轨索引，默认 0")
    p_sh.add_argument("--out-path", type=str, default=None, help="输出文件路径，默认 <原文件>.modified.bjson")

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
    elif args.command == "add-caption":
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        try:
            project = load_bcut_project(str(file_path))
            caption = create_caption(
                text=args.text,
                in_ms=args.start_ms,
                out_ms=args.start_ms + args.duration_ms,
                font_name=args.font_name,
                font_path=args.font_path,
            )
            add_caption(project, caption, track_index=args.track_index)
            out_path = args.out_path or str(file_path.with_suffix(".modified.bjson"))
            save_bcut_project(project, out_path)
            print(f"已添加字幕 id={caption.idString} 至轨 {args.track_index}，输出: {out_path}")
        except Exception as e:
            print(f"添加失败: {e}")
            sys.exit(1)
    elif args.command == "remove-caption":
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        try:
            project = load_bcut_project(str(file_path))
            ok = remove_caption(project, args.caption_id, track_index=args.track_index)
            out_path = args.out_path or str(file_path.with_suffix(".modified.bjson"))
            save_bcut_project(project, out_path)
            print(f"删除结果: {ok}，输出: {out_path}")
        except Exception as e:
            print(f"删除失败: {e}")
            sys.exit(1)
    elif args.command == "update-caption":
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        try:
            project = load_bcut_project(str(file_path))
            ok = update_caption_text(project, args.caption_id, args.new_text, track_index=args.track_index)
            out_path = args.out_path or str(file_path.with_suffix(".modified.bjson"))
            save_bcut_project(project, out_path)
            print(f"更新结果: {ok}，输出: {out_path}")
        except Exception as e:
            print(f"更新失败: {e}")
            sys.exit(1)
    elif args.command == "shift-caption":
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        try:
            project = load_bcut_project(str(file_path))
            ok = shift_caption_time(project, args.caption_id, args.delta_ms, track_index=args.track_index)
            out_path = args.out_path or str(file_path.with_suffix(".modified.bjson"))
            save_bcut_project(project, out_path)
            print(f"平移结果: {ok}，输出: {out_path}")
        except Exception as e:
            print(f"平移失败: {e}")
            sys.exit(1)
    else:
        print("请选择命令：\n  解析单个草稿: uv run main.py parse <path/to/file.bjson>\n  汇总 Drafts 目录: uv run main.py summarize-drafts ""Bcut Drafts""")
        sys.exit(1)


if __name__ == "__main__":
    main()
