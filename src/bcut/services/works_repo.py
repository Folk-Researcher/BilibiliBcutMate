from __future__ import annotations

import json
from pathlib import Path
from time import time
from uuid import uuid4

from bcut.models.works import WorkInfo, WorksInfo


def _now_ms() -> int:
    return int(time() * 1000)


def load_works_info(path: str | Path) -> WorksInfo:
    p = Path(path)
    if not p.exists():
        return WorksInfo()
    data = json.loads(p.read_text(encoding="utf-8"))
    return WorksInfo.model_validate(data)


def save_works_info(info: WorksInfo, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(info.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    return p


def add_work(
    path: str | Path,
    *,
    draftId: str,
    name: str,
    duration: int = 0,
    filePath: str = "",
    imageRatio: float = 1.7777778,
    status: int = 0,
) -> WorkInfo:
    info = load_works_info(path)
    work = WorkInfo(
        draftId=draftId,
        duration=duration,
        filePath=filePath,
        id=str(uuid4()).upper(),
        imageRatio=imageRatio,
        modifyTime=_now_ms(),
        name=name,
        status=status,
    )
    info.worksInfos.append(work)
    save_works_info(info, path)
    return work


def update_work(path: str | Path, work_id: str, **fields) -> WorkInfo | None:
    info = load_works_info(path)
    for i, w in enumerate(info.worksInfos):
        if w.id == work_id:
            data = w.model_dump()
            data.update(fields)
            data["modifyTime"] = _now_ms()
            info.worksInfos[i] = WorkInfo.model_validate(data)
            save_works_info(info, path)
            return info.worksInfos[i]
    return None


def remove_work(path: str | Path, work_id: str) -> bool:
    info = load_works_info(path)
    before = len(info.worksInfos)
    info.worksInfos = [w for w in info.worksInfos if w.id != work_id]
    changed = len(info.worksInfos) < before
    if changed:
        save_works_info(info, path)
    return changed


def find_by_id(path: str | Path, work_id: str) -> WorkInfo | None:
    info = load_works_info(path)
    for w in info.worksInfos:
        if w.id == work_id:
            return w
    return None


def find_by_draft(path: str | Path, draft_id: str) -> list[WorkInfo]:
    info = load_works_info(path)
    return [w for w in info.worksInfos if w.draftId == draft_id]


def set_status(path: str | Path, work_id: str, status: int) -> WorkInfo | None:
    return update_work(path, work_id, status=status)


def set_file_path(path: str | Path, work_id: str, file_path: str) -> WorkInfo | None:
    return update_work(path, work_id, filePath=file_path)


__all__ = [
    "load_works_info",
    "save_works_info",
    "add_work",
    "update_work",
    "remove_work",
    "find_by_id",
    "find_by_draft",
    "set_status",
    "set_file_path",
]

