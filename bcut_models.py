from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
from pathlib import Path

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


# ========= Utility Methods for captionTracks =========
def ensure_caption_track(project: "BcutProject", index: int = 0) -> CaptionTrack:
    """Return an existing caption track by index or create one if missing."""
    if project.timelineWidget is None or project.timelineWidget.timeline is None:
        raise ValueError("timelineWidget.timeline 未定义，无法获取字幕轨道")
    tracks = project.timelineWidget.timeline.captionTracks or []
    # Ensure list exists
    if project.timelineWidget.timeline.captionTracks is None:
        project.timelineWidget.timeline.captionTracks = []
        tracks = project.timelineWidget.timeline.captionTracks
    # Grow list until index exists
    while len(tracks) <= index:
        tracks.append(
            CaptionTrack(
                captions=[],
                idString=str(uuid4()),
                index=len(tracks),
                trackType=3,
                compacted=False,
            )
        )
    return tracks[index]


def create_caption(text: str, in_ms: int, out_ms: int,
                   font_name: Optional[str] = None,
                   font_path: Optional[str] = None) -> Caption:
    """Create a Caption with sensible defaults observed in Bcut drafts."""
    if out_ms < in_ms:
        raise ValueError("out_ms 必须大于等于 in_ms")
    duration = out_ms - in_ms
    return Caption(
        assetInfo=AssetInfo(
            assetItemType=15,
            content=text,
            duration=duration,
            fontID=0,
            fontSrcPath=font_path or "",
            realMaterialId="-4",
            type=4,
            displayName=text,
        ),
        captionText=text,
        defaultFontName=font_name or None,
        defaultFontPath=font_path or None,
        fontPackagePath=font_path or None,
        idString=str(uuid4()),
        uid=str(uuid4()),
        inPoint=in_ms,
        outPoint=out_ms,
        letterSpacing=100,
        textAlignment=1,
        opacity=1.0,
        scaleX=1.0,
        scaleY=1.0,
        textColor=RGBA(r=1, g=1, b=1, a=1),
    )


def add_caption(project: "BcutProject", caption: Caption, track_index: int = 0) -> Caption:
    """Append a caption to the given track (create track if needed)."""
    track = ensure_caption_track(project, track_index)
    track.captions.append(caption)
    return caption


def remove_caption(project: "BcutProject", caption_id: str, track_index: int = 0) -> bool:
    """Remove a caption by idString from the given track. Return True if removed."""
    track = ensure_caption_track(project, track_index)
    before = len(track.captions)
    track.captions = [c for c in track.captions if c.idString != caption_id]
    return len(track.captions) < before


def update_caption_text(project: "BcutProject", caption_id: str, new_text: str, track_index: int = 0) -> bool:
    """Update captionText and assetInfo.content/displayName for the caption."""
    track = ensure_caption_track(project, track_index)
    for c in track.captions:
        if c.idString == caption_id:
            c.captionText = new_text
            c.assetInfo.content = new_text
            c.assetInfo.displayName = new_text
            return True
    return False


def shift_caption_time(project: "BcutProject", caption_id: str, delta_ms: int, track_index: int = 0) -> bool:
    """Shift inPoint/outPoint by delta_ms for the caption, ensuring non-negative times."""
    track = ensure_caption_track(project, track_index)
    for c in track.captions:
        if c.idString == caption_id:
            new_in = max(0, c.inPoint + delta_ms)
            new_out = max(new_in, c.outPoint + delta_ms)
            c.inPoint = new_in
            c.outPoint = new_out
            c.assetInfo.duration = new_out - new_in
            return True
    return False


def save_bcut_project(project: "BcutProject", out_path: str | Path) -> Path:
    """Write project back to disk in compact JSON format (single line)."""
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    data = project.model_dump()
    out_p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return out_p


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