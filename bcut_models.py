from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RGBA(BaseModel):
    r: float
    g: float
    b: float
    a: float


class AssetInfo(BaseModel):
    assetItemType: int
    content: str
    duration: int
    fontID: int
    fontSrcPath: str
    realMaterialId: str
    type: int

    # Extended fields observed in detailed caption assets
    audioType: Optional[int] = None
    coverPath: Optional[str] = None
    customInfos: Optional[Dict[str, Any]] = None
    displayName: Optional[str] = None
    frameRateDen: Optional[int] = None
    frameRateNum: Optional[int] = None
    height: Optional[int] = None
    itemName: Optional[str] = None
    originDuration: Optional[int] = None
    originSrcPath: Optional[str] = None
    originType: Optional[int] = None
    shotClipId: Optional[str] = None
    shotIndex: Optional[int] = None
    srcPath: Optional[str] = None
    videoType: Optional[int] = None
    width: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class Caption(BaseModel):
    assetInfo: AssetInfo
    captionText: str
    idString: str
    uid: str
    inPoint: int
    outPoint: int

    # Optional visual/text properties
    defaultFontName: Optional[str] = None
    defaultFontPath: Optional[str] = None
    fontPackagePath: Optional[str] = None
    opacity: Optional[float] = None
    scaleX: Optional[float] = None
    scaleY: Optional[float] = None
    textAlignment: Optional[int] = None
    textColor: Optional[RGBA] = None

    # Extended caption properties
    drawBackgroundColor: Optional[bool] = None
    drawOutline: Optional[bool] = None
    drawShadowColor: Optional[bool] = None
    fancyWordId: Optional[str] = None
    fancyWordPath: Optional[str] = None
    fontId: Optional[str] = None
    fontName: Optional[str] = None
    inAnimationDuration: Optional[int] = None
    inAnimationId: Optional[str] = None
    inAnimationPath: Optional[str] = None
    isVerticalLayout: Optional[bool] = None
    letterSpacing: Optional[int] = None
    lineSpacing: Optional[int] = None
    loopAnimationDuration: Optional[int] = None
    loopAnimationId: Optional[str] = None
    loopAnimationPath: Optional[str] = None
    outAnimationDuration: Optional[int] = None
    outAnimationId: Optional[str] = None
    outAnimationPath: Optional[str] = None
    rotation: Optional[float] = None
    transX: Optional[int] = None
    transY: Optional[int] = None
    underline: Optional[bool] = None
    textBold: Optional[bool] = None
    textItalic: Optional[bool] = None
    templateId: Optional[str] = None
    templatePackagePath: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class CaptionTrack(BaseModel):
    captions: List[Caption] = Field(default_factory=list)
    idString: Optional[str] = None
    index: Optional[int] = None
    trackType: Optional[int] = None
    compacted: Optional[bool] = None

    model_config = ConfigDict(extra="allow")


class AudioRes(BaseModel):
    channelCount: int
    sampleRate: int


class VideoRes(BaseModel):
    height: int
    width: int


class VideoFps(BaseModel):
    den: int
    num: int


class TimelineConfig(BaseModel):
    audioRes: AudioRes
    videoFps: VideoFps
    videoRes: VideoRes

    model_config = ConfigDict(extra="allow")


class VideoTrack(BaseModel):
    clips: List[Dict[str, Any]] = Field(default_factory=list)
    idString: Optional[str] = None
    index: Optional[int] = None
    mute: Optional[bool] = None
    split: Optional[bool] = None
    trackType: Optional[int] = None
    transitions: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class Ruler(BaseModel):
    MarkPointInfo: List[Dict[str, Any]] = Field(default_factory=list)


class Timeline(BaseModel):
    adjustTracks: List[Dict[str, Any]] = Field(default_factory=list)
    audioTracks: List[Dict[str, Any]] = Field(default_factory=list)
    captionTracks: List[CaptionTrack] = Field(default_factory=list)
    config: TimelineConfig
    filterTracks: List[Dict[str, Any]] = Field(default_factory=list)
    idString: str
    stickerTracks: List[Dict[str, Any]] = Field(default_factory=list)
    timelineVideoFxTracks: List[Dict[str, Any]] = Field(default_factory=list)
    videoTracks: List[VideoTrack] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class TimelineWidget(BaseModel):
    linkage: bool
    linkageDelegate: Dict[str, Any]
    magnet: bool
    ruler: Ruler
    timeline: Timeline

    # Some project drafts embed these at this level
    tracking: Dict[str, Any] = Field(default_factory=dict)
    tts: Dict[str, Any] = Field(default_factory=dict)
    ttv: Optional[Ttv] = None

    model_config = ConfigDict(extra="allow")


class BrowserPanelFile(BaseModel):
    duration: int  # pydantic will coerce numeric strings to int
    frameRateDen: int
    frameRateNum: int
    height: int
    importTime: str
    itemType: int
    recentlyUsedTime: str
    srcPath: str
    width: int

    model_config = ConfigDict(extra="allow")


class MainWindow(BaseModel):
    browserPanelFiles: List[BrowserPanelFile] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class Ttv(BaseModel):
    enableDetach: bool
    is_set_bgm: bool


class BcutProject(BaseModel):
    draftCreatedVersion: str
    mainWindow: MainWindow
    timelineWidget: TimelineWidget

    # Some versions place these at top-level, others under timelineWidget
    tracking: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tts: Optional[Dict[str, Any]] = Field(default_factory=dict)
    ttv: Optional[Ttv] = None

    model_config = ConfigDict(extra="allow")


def load_bcut_project(path: str) -> BcutProject:
    """Load and validate a Bcut project JSON file into models."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return BcutProject.model_validate(data)


def summarize_project(project: BcutProject) -> Dict[str, Any]:
    """Return a concise summary of resolution, fps and captions count."""
    config = project.timelineWidget.timeline.config
    resolution = {
        "width": config.videoRes.width,
        "height": config.videoRes.height,
    }
    fps = config.videoFps.num / config.videoFps.den if config.videoFps.den else config.videoFps.num

    caption_tracks = project.timelineWidget.timeline.captionTracks
    captions_count = sum(len(track.captions) for track in caption_tracks) if caption_tracks else 0

    return {
        "resolution": resolution,
        "fps": fps,
        "caption_tracks": len(caption_tracks),
        "captions_total": captions_count,
    }


__all__ = [
    "RGBA",
    "AssetInfo",
    "Caption",
    "CaptionTrack",
    "AudioRes",
    "VideoRes",
    "VideoFps",
    "TimelineConfig",
    "VideoTrack",
    "Ruler",
    "Timeline",
    "TimelineWidget",
    "BrowserPanelFile",
    "MainWindow",
    "Ttv",
    "BcutProject",
    "load_bcut_project",
    "summarize_project",
]