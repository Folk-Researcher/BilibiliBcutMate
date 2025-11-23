from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pydantic import BaseModel, Field
from bcut_models import BcutProject, create_empty_project, save_bcut_project
from bcut.models.works import WorkInfo, WorksInfo
from bcut.services.works_repo import load_works_info


 


class DraftInfoEntry(BaseModel):
    """草稿（Draft）元信息条目。

    典型来源：`draftInfo.json` 中的单个条目。

    字段说明（常见）：
    - id: 草稿的唯一标识（UUID）。
    - name: 草稿名称。
    - modifyTime: 最近修改时间戳（毫秒）。
    - duration: 草稿时长（毫秒）。
    - cloud_draft_id/cloud_draft_version: 云草稿相关标识（可能为空）。
    - storyLineId/video_slice_id: 版本相关的拓展字段（可能为空）。
    """
    cloud_draft_id: Optional[str] = ""
    cloud_draft_version: Optional[str] = ""
    duration: int
    id: str
    modifyTime: int
    name: str
    storyLineId: Optional[str] = ""
    video_slice_id: Optional[str] = ""


class DraftInfos(BaseModel):
    """`draftInfo.json` 顶层结构封装。

    - draftInfos: 草稿条目列表。
    """
    draftInfos: List[DraftInfoEntry] = Field(default_factory=list)


 


def load_draft_info(path: str | Path) -> DraftInfos:
    """加载并解析 `draftInfo.json`。

    参数：
    - path: 文件路径（`str` 或 `Path`）。

    返回：
    - DraftInfos: 解析后的 Pydantic 对象。
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return DraftInfos.model_validate(data)


def build_drafts_index(base_dir: str | Path) -> List[Dict[str, Any]]:
    """扫描 Bcut Drafts 目录并为每个草稿子目录生成汇总信息。

    返回的每个字典包含：
    - folder_id: 草稿子目录名（通常为 UUID）。
    - cover: 子目录中的封面路径（`cover.jpg`），若不存在则为 `None`。
    - bjson_files: 该目录内的 `.bjson` 文件列表（字符串路径，按文件名排序）。
    - works: 关联的作品信息（根据 `draftId` 关联）。
    - draft: 关联的草稿元数据（根据 `id` 关联），若缺失则为 `None`。

    说明：同一草稿目录内可能包含多个 `.bjson` 快照，实践中“最新文件通常为当前有效，较早者为备份/历史版本”。
    判定最新可参考文件名时间戳与 mtime（文件修改时间）。
    """
    base_dir = Path(base_dir)
    works_path = base_dir / "worksInfo.json"
    draft_path = base_dir / "draftInfo.json"

    works = load_works_info(works_path) if works_path.exists() else WorksInfo()
    drafts = load_draft_info(draft_path) if draft_path.exists() else DraftInfos()

    # 根据草稿 ID 建立作品索引，便于快速关联（一个草稿可能对应多个作品）。
    works_by_draft_id: Dict[str, List[WorkInfo]] = {}
    for w in works.worksInfos:
        works_by_draft_id.setdefault(w.draftId, []).append(w)

    # 根据草稿 ID 建立草稿元数据字典，便于 O(1) 查找。
    draft_by_id: Dict[str, DraftInfoEntry] = {d.id: d for d in drafts.draftInfos}

    summaries: List[Dict[str, Any]] = []
    for child in base_dir.iterdir():
        if not child.is_dir():
            continue
        folder_id = child.name

        # 按文件名对 .bjson 进行排序（便于人为阅读与粗略时间序列）。
        bjson_files = sorted([str(p) for p in child.glob("*.bjson")])
        # 提取封面路径（如存在）。
        cover_path = str(child / "cover.jpg") if (child / "cover.jpg").exists() else None

        summaries.append({
            "folder_id": folder_id,
            "cover": cover_path,
            "bjson_files": bjson_files,
            "works": [w.model_dump() for w in works_by_draft_id.get(folder_id, [])],
            "draft": draft_by_id.get(folder_id).model_dump() if folder_id in draft_by_id else None,
        })

    return summaries


def create_draft(
    base_dir: str | Path,
    name: str,
    width: int = 1920,
    height: int = 1080,
    fps_num: int = 30,
    fps_den: int = 1,
    sample_rate: int = 48000,
    channel_count: int = 2,
    draft_version: str = "3.11.8",
) -> Dict[str, Any]:
    """创建一个新的草稿目录与空 `.bjson` 工程文件，并更新 `draftInfo.json`。

    - base_dir: `Bcut Drafts` 根目录路径。
    - name: 草稿名称（写入 `draftInfo.json`）。
    - 其余参数：分辨率/帧率/音频配置与草稿版本。

    返回：
    - dict: `{ draft_id, folder, bjson }`，分别为目录 UUID、目录路径、创建的 `.bjson` 路径。
    """
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    # 生成草稿目录 UUID（与示例一致采用大写）
    draft_id = str(uuid4()).upper()
    folder = base / draft_id
    folder.mkdir(parents=True, exist_ok=True)

    # 构建空工程对象
    project: BcutProject = create_empty_project(
        width=width,
        height=height,
        fps_num=fps_num,
        fps_den=fps_den,
        sample_rate=sample_rate,
        channel_count=channel_count,
        draft_version=draft_version,
    )

    # 生成文件名：HH-MM-SS-sss--{GUID}.bjson
    now = datetime.now()
    ms = int(now.microsecond / 1000)
    file_guid = uuid4()
    filename = f"{now:%H}-{now:%M}-{now:%S}-{ms:03d}--{{{file_guid}}}.bjson"
    bjson_path = folder / filename

    # 写入 .bjson（紧凑单行）
    save_bcut_project(project, bjson_path)

    # 更新/创建 draftInfo.json
    draft_info_path = base / "draftInfo.json"
    entry = DraftInfoEntry(
        cloud_draft_id="",
        cloud_draft_version="",
        duration=0,
        id=draft_id,
        modifyTime=int(now.timestamp() * 1000),
        name=name,
        storyLineId="",
        video_slice_id="",
    )
    try:
        if draft_info_path.exists():
            with open(draft_info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            drafts = DraftInfos.model_validate(data)
        else:
            drafts = DraftInfos()
    except Exception:
        # 若现有文件损坏或格式不符，则回退为新结构
        drafts = DraftInfos()

    # 若已存在同 UUID，更新名称与修改时间；否则追加
    updated = False
    for d in drafts.draftInfos:
        if d.id == draft_id:
            d.name = name
            d.modifyTime = entry.modifyTime
            updated = True
            break
    if not updated:
        drafts.draftInfos.append(entry)

    with open(draft_info_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(drafts.model_dump(), ensure_ascii=False, indent=2))

    return {
        "draft_id": draft_id,
        "folder": str(folder),
        "bjson": str(bjson_path),
    }


__all__ = [
    "WorkInfo",
    "WorksInfo",
    "DraftInfoEntry",
    "DraftInfos",
    "load_works_info",
    "load_draft_info",
    "build_drafts_index",
    "create_draft",
]