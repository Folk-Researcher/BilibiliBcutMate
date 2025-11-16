from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkInfo(BaseModel):
    """作品（导出项）元信息。

    典型来源：`worksInfo.json` 中的单个条目。

    字段说明（常见）：
    - draftId: 关联的草稿 UUID。
    - duration: 作品时长（毫秒）。
    - filePath: 导出的目标文件路径（可能为空）。
    - id: 作品条目的唯一标识。
    - imageRatio: 预览图比例或画幅比（浮点）。
    - modifyTime: 最近修改时间戳（毫秒）。
    - name: 作品名称。
    - status: 整数状态码（不同版本含义可能不同）。
    """
    draftId: str
    duration: int
    filePath: str
    id: str
    imageRatio: float
    modifyTime: int
    name: str
    status: int


class WorksInfo(BaseModel):
    """`worksInfo.json` 顶层结构封装。

    - worksInfos: 作品条目列表。
    """
    worksInfos: List[WorkInfo] = Field(default_factory=list)


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


def load_works_info(path: str | Path) -> WorksInfo:
    """加载并解析 `worksInfo.json`。

    参数：
    - path: 文件路径（`str` 或 `Path`）。

    返回：
    - WorksInfo: 解析后的 Pydantic 对象。
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return WorksInfo.model_validate(data)


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


__all__ = [
    "WorkInfo",
    "WorksInfo",
    "DraftInfoEntry",
    "DraftInfos",
    "load_works_info",
    "load_draft_info",
    "build_drafts_index",
]