from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


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
    draftInfos: list[DraftInfoEntry] = Field(default_factory=list)


__all__ = [
    "DraftInfoEntry",
    "DraftInfos",
]