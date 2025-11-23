import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

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
from bcut_drafts import build_drafts_index, create_draft
from bcut.services.works_repo import (
    load_works_info,
    add_work,
    update_work,
    remove_work,
    find_by_id,
    find_by_draft,
)


def main():
    parser = argparse.ArgumentParser(description="Bcut 项目工具：解析单个草稿或汇总 Drafts 目录")
    subparsers = parser.add_subparsers(dest="command")

    p_parse = subparsers.add_parser("parse", help="解析单个 .bjson 草稿文件并输出摘要")
    p_parse.add_argument("file", help="Path to the Bcut .bjson file")

    p_summarize = subparsers.add_parser("summarize-drafts", help="扫描并汇总 Drafts 目录信息")
    p_summarize.add_argument("dir", help="Path to the 'Bcut Drafts' directory")

    p_create = subparsers.add_parser("create-draft", help="创建草稿目录与空工程")
    p_create.add_argument("dir", help="Path to the 'Bcut Drafts' directory")
    p_create.add_argument("name", help="草稿名称")
    p_create.add_argument("--width", type=int, default=1920, help="视频宽度，默认 1920")
    p_create.add_argument("--height", type=int, default=1080, help="视频高度，默认 1080")
    p_create.add_argument("--fps-num", type=int, default=30, help="帧率分子，默认 30")
    p_create.add_argument("--fps-den", type=int, default=1, help="帧率分母，默认 1")
    p_create.add_argument("--sample-rate", type=int, default=48000, help="音频采样率，默认 48000")
    p_create.add_argument("--channel-count", type=int, default=2, help="音频声道数，默认 2")
    p_create.add_argument("--draft-version", type=str, default="3.11.8", help="草稿创建版本，默认 3.11.8")

    p_wl = subparsers.add_parser("works-list", help="列出 worksInfo.json 中的作品条目")
    p_wl.add_argument("dir", help="Path to the 'Bcut Drafts' directory")

    p_wa = subparsers.add_parser("works-add", help="新增作品条目")
    p_wa.add_argument("dir", help="Path to the 'Bcut Drafts' directory")
    p_wa.add_argument("--draft-id", required=True)
    p_wa.add_argument("--name", required=True)
    p_wa.add_argument("--duration", type=int, default=0)
    p_wa.add_argument("--file-path", default="")
    p_wa.add_argument("--image-ratio", type=float, default=1.7777778)
    p_wa.add_argument("--status", type=int, default=0)

    p_wu = subparsers.add_parser("works-update", help="更新作品条目")
    p_wu.add_argument("dir", help="Path to the 'Bcut Drafts' directory")
    p_wu.add_argument("--id", required=True)
    p_wu.add_argument("--name")
    p_wu.add_argument("--duration", type=int)
    p_wu.add_argument("--file-path")
    p_wu.add_argument("--image-ratio", type=float)
    p_wu.add_argument("--status", type=int)

    p_wr = subparsers.add_parser("works-remove", help="删除作品条目")
    p_wr.add_argument("dir", help="Path to the 'Bcut Drafts' directory")
    p_wr.add_argument("--id", required=True)

    p_wf = subparsers.add_parser("works-find", help="查询作品条目")
    p_wf.add_argument("dir", help="Path to the 'Bcut Drafts' directory")
    g = p_wf.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--draft-id")

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
    elif args.command == "create-draft":
        try:
            result = create_draft(
                base_dir=args.dir,
                name=args.name,
                width=args.width,
                height=args.height,
                fps_num=args.fps_num,
                fps_den=args.fps_den,
                sample_rate=args.sample_rate,
                channel_count=args.channel_count,
                draft_version=args.draft_version,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"创建失败: {e}")
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
    elif args.command == "works-list":
        works_path = Path(args.dir) / "worksInfo.json"
        try:
            info = load_works_info(works_path)
            items = [
                {
                    "id": w.id,
                    "draftId": w.draftId,
                    "name": w.name,
                    "status": w.status,
                    "modifyTime": w.modifyTime,
                }
                for w in info.worksInfos
            ]
            print(json.dumps(items, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"列出失败: {e}")
            sys.exit(1)
    elif args.command == "works-add":
        works_path = Path(args.dir) / "worksInfo.json"
        try:
            w = add_work(
                works_path,
                draftId=args.draft_id,
                name=args.name,
                duration=args.duration,
                filePath=args.file_path,
                imageRatio=args.image_ratio,
                status=args.status,
            )
            print(json.dumps(w.model_dump(), ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"新增失败: {e}")
            sys.exit(1)
    elif args.command == "works-update":
        works_path = Path(args.dir) / "worksInfo.json"
        try:
            fields = {}
            if args.name is not None:
                fields["name"] = args.name
            if args.duration is not None:
                fields["duration"] = args.duration
            if args.file_path is not None:
                fields["filePath"] = args.file_path
            if args.image_ratio is not None:
                fields["imageRatio"] = args.image_ratio
            if args.status is not None:
                fields["status"] = args.status
            w = update_work(works_path, args.id, **fields)
            print(json.dumps(w.model_dump() if w else None, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"更新失败: {e}")
            sys.exit(1)
    elif args.command == "works-remove":
        works_path = Path(args.dir) / "worksInfo.json"
        try:
            ok = remove_work(works_path, args.id)
            print(json.dumps({"removed": ok}, ensure_ascii=False))
        except Exception as e:
            print(f"删除失败: {e}")
            sys.exit(1)
    elif args.command == "works-find":
        works_path = Path(args.dir) / "worksInfo.json"
        try:
            if args.id:
                w = find_by_id(works_path, args.id)
                print(json.dumps(w.model_dump() if w else None, ensure_ascii=False, indent=2))
            else:
                arr = [w.model_dump() for w in find_by_draft(works_path, args.draft_id)]
                print(json.dumps(arr, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"查询失败: {e}")
            sys.exit(1)
    else:
        print("请选择命令：\n  解析单个草稿: uv run main.py parse <path/to/file.bjson>\n  汇总 Drafts 目录: uv run main.py summarize-drafts ""Bcut Drafts""\n  创建草稿: uv run main.py create-draft ""Bcut Drafts"" ""测试草稿"" [--width 1920 --height 1080 --fps-num 30 --fps-den 1 --sample-rate 48000 --channel-count 2 --draft-version 3.11.8]\n  列出作品: uv run main.py works-list ""Bcut Drafts""\n  新增作品: uv run main.py works-add ""Bcut Drafts"" --draft-id <UUID> --name <NAME> [--duration N --file-path P --image-ratio R --status S]\n  更新作品: uv run main.py works-update ""Bcut Drafts"" --id <UUID> [--name --duration --file-path --image-ratio --status]\n  删除作品: uv run main.py works-remove ""Bcut Drafts"" --id <UUID>\n  查询作品: uv run main.py works-find ""Bcut Drafts"" (--id <UUID> | --draft-id <UUID>)")
        sys.exit(1)


if __name__ == "__main__":
    main()
