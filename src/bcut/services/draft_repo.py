from __future__ import annotations

import json
from pathlib import Path
from time import time

from bcut.models.drafts import DraftInfoEntry, DraftInfos


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
]