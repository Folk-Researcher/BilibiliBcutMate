from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkInfo(BaseModel):
    draftId: str
    duration: int
    filePath: str
    id: str
    imageRatio: float
    modifyTime: int
    name: str
    status: int


class WorksInfo(BaseModel):
    worksInfos: List[WorkInfo] = Field(default_factory=list)


class DraftInfoEntry(BaseModel):
    cloud_draft_id: Optional[str] = ""
    cloud_draft_version: Optional[str] = ""
    duration: int
    id: str
    modifyTime: int
    name: str
    storyLineId: Optional[str] = ""
    video_slice_id: Optional[str] = ""


class DraftInfos(BaseModel):
    draftInfos: List[DraftInfoEntry] = Field(default_factory=list)


def load_works_info(path: str | Path) -> WorksInfo:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return WorksInfo.model_validate(data)


def load_draft_info(path: str | Path) -> DraftInfos:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return DraftInfos.model_validate(data)


def build_drafts_index(base_dir: str | Path) -> List[Dict[str, Any]]:
    """Scan a Bcut Drafts directory and return a summary for each draft folder.

    Each item includes:
    - folder_id
    - cover_path
    - bjson_files
    - works (matching by draftId)
    - draft (matching by id)
    """
    base_dir = Path(base_dir)
    works_path = base_dir / "worksInfo.json"
    draft_path = base_dir / "draftInfo.json"

    works = load_works_info(works_path) if works_path.exists() else WorksInfo()
    drafts = load_draft_info(draft_path) if draft_path.exists() else DraftInfos()

    # Index metadata by ids for quick lookup
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


__all__ = [
    "WorkInfo",
    "WorksInfo",
    "DraftInfoEntry",
    "DraftInfos",
    "load_works_info",
    "load_draft_info",
    "build_drafts_index",
]