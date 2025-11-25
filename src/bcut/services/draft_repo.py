from __future__ import annotations

import json
from pathlib import Path
from time import time

from bcut.models.drafts import DraftInfoEntry, DraftInfos
from bcut.models.works import WorkInfo, WorksInfo
from bcut.services.works_repo import load_works_info
from bcut_models import BcutProject, create_empty_project, save_bcut_project
from typing import Any, Dict, List
from datetime import datetime
from uuid import uuid4


def _now_ms() -> int:
    return int(time() * 1000)


def load_draft_info(path: str | Path) -> DraftInfos:
    p = Path(path)
    if not p.exists():
        return DraftInfos()
    data = json.loads(p.read_text(encoding="utf-8"))
    return DraftInfos.model_validate(data)


def save_draft_info(info: DraftInfos, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(info.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    return p


def add_draft(
    path: str | Path,
    *,
    id: str,
    name: str,
    duration: int = 0,
    modifyTime: int | None = None,
    cloud_draft_id: str = "",
    cloud_draft_version: str = "",
    storyLineId: str = "",
    video_slice_id: str = "",
) -> DraftInfoEntry:
    info = load_draft_info(path)
    entry = DraftInfoEntry(
        cloud_draft_id=cloud_draft_id,
        cloud_draft_version=cloud_draft_version,
        duration=duration,
        id=id,
        modifyTime=modifyTime or _now_ms(),
        name=name,
        storyLineId=storyLineId,
        video_slice_id=video_slice_id,
    )
    # 如果已存在同 id，则更新；否则追加
    updated = False
    for i, d in enumerate(info.draftInfos):
        if d.id == id:
            info.draftInfos[i] = entry
            updated = True
            break
    if not updated:
        info.draftInfos.append(entry)
    save_draft_info(info, path)
    return entry


def update_draft(path: str | Path, draft_id: str, **fields) -> DraftInfoEntry | None:
    info = load_draft_info(path)
    for i, d in enumerate(info.draftInfos):
        if d.id == draft_id:
            data = d.model_dump()
            data.update(fields)
            data["modifyTime"] = _now_ms()
            info.draftInfos[i] = DraftInfoEntry.model_validate(data)
            save_draft_info(info, path)
            return info.draftInfos[i]
    return None


def remove_draft(path: str | Path, draft_id: str) -> bool:
    info = load_draft_info(path)
    before = len(info.draftInfos)
    info.draftInfos = [d for d in info.draftInfos if d.id != draft_id]
    changed = len(info.draftInfos) < before
    if changed:
        save_draft_info(info, path)
    return changed


def find_by_id(path: str | Path, draft_id: str) -> DraftInfoEntry | None:
    info = load_draft_info(path)
    for d in info.draftInfos:
        if d.id == draft_id:
            return d
    return None


__all__ = [
    "load_draft_info",
    "save_draft_info",
    "add_draft",
    "update_draft",
    "remove_draft",
    "find_by_id",
    "build_drafts_index",
    "create_draft",
]


def build_drafts_index(base_dir: str | Path) -> List[Dict[str, Any]]:
    base_dir = Path(base_dir)
    works_path = base_dir / "worksInfo.json"
    draft_path = base_dir / "draftInfo.json"

    works = load_works_info(works_path) if works_path.exists() else WorksInfo()
    drafts = load_draft_info(draft_path) if draft_path.exists() else DraftInfos()

    works_by_draft_id: Dict[str, List[WorkInfo]] = {}
    for w in works.worksInfos:
        works_by_draft_id.setdefault(w.draftId, []).append(w)

    draft_by_id: Dict[str, DraftInfoEntry] = {d.id: d for d in drafts.draftInfos}

    summaries: List[Dict[str, Any]] = []
    for child in base_dir.iterdir():
        if not child.is_dir():
            continue
        folder_id = child.name

        bjson_files = sorted([str(p) for p in child.glob("*.bjson")])
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
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    draft_id = str(uuid4()).upper()
    folder = base / draft_id
    folder.mkdir(parents=True, exist_ok=True)

    project: BcutProject = create_empty_project(
        width=width,
        height=height,
        fps_num=fps_num,
        fps_den=fps_den,
        sample_rate=sample_rate,
        channel_count=channel_count,
        draft_version=draft_version,
    )

    now = datetime.now()
    ms = int(now.microsecond / 1000)
    file_guid = uuid4()
    filename = f"{now:%H}-{now:%M}-{now:%S}-{ms:03d}--{{{file_guid}}}.bjson"
    bjson_path = folder / filename

    save_bcut_project(project, bjson_path)

    draft_info_path = base / "draftInfo.json"
    try:
        if draft_info_path.exists():
            drafts = load_draft_info(draft_info_path)
        else:
            drafts = DraftInfos()
    except Exception:
        drafts = DraftInfos()

    add_draft(
        draft_info_path,
        id=draft_id,
        name=name,
        duration=0,
        modifyTime=int(now.timestamp() * 1000),
        cloud_draft_id="",
        cloud_draft_version="",
        storyLineId="",
        video_slice_id="",
    )

    return {
        "draft_id": draft_id,
        "folder": str(folder),
        "bjson": str(bjson_path),
    }