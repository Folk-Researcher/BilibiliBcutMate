from __future__ import annotations

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
    worksInfos: list[WorkInfo] = Field(default_factory=list)


__all__ = [
    "WorkInfo",
    "WorksInfo",
]

