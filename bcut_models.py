"""Bcut 项目模型与字幕操作工具。

包含 Pydantic 模型（时间线、轨道、字幕等），以及常用的字幕轨操作函数，
用于解析/修改/保存 Bcut 的 .bjson 草稿文件。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RGBA(BaseModel):
    """RGBA 颜色结构，分量取值 0–1 浮点数。"""
    r: float  # 红色分量（0–1，推测为归一化）
    g: float  # 绿色分量（0–1）
    b: float  # 蓝色分量（0–1）
    a: float  # 透明度（Alpha，0=全透明，1=不透明）


class AssetInfo(BaseModel):
    """字幕素材信息（assetInfo）。

    常见字段：文本内容、时长、字体 ID/路径、素材类型等；
    兼容扩展字段（不同版本可能存在）：封面、帧率、原始路径、视频/音频类型等。
    """
    assetItemType: int  # 素材项类型枚举（如 15=字幕文本，推测）
    content: str  # 文本内容或素材名（用于显示/搜索）
    duration: int  # 时长（毫秒）
    fontID: int  # 字体 ID（内部或系统映射）
    fontSrcPath: str  # 字体源路径（本地或资源包路径）
    realMaterialId: str  # 真实素材 ID（-4 为占位/内置，推测）
    type: int  # 素材大类（如 4=字幕/文本，推测）

    # Extended fields observed in detailed caption assets
    audioType: Optional[int] = None  # 音频类型（人声/BGM/效果等枚举，推测）
    coverPath: Optional[str] = None  # 封面图路径（视频/模板封面）
    customInfos: Optional[Dict[str, Any]] = None  # 自定义元信息（版本差异字段容器）
    displayName: Optional[str] = None  # 展示名称（通常与 content 同步）
    frameRateDen: Optional[int] = None  # 帧率分母（素材原始帧率）
    frameRateNum: Optional[int] = None  # 帧率分子（素材原始帧率）
    height: Optional[int] = None  # 像素高度（素材尺寸）
    itemName: Optional[str] = None  # 项名（库中显示名称，推测）
    originDuration: Optional[int] = None  # 原始素材时长（毫秒）
    originSrcPath: Optional[str] = None  # 原始素材路径（导入前或源文件）
    originType: Optional[int] = None  # 原始素材类型枚举（推测）
    shotClipId: Optional[str] = None  # 拍摄片段/镜头 ID（推测）
    shotIndex: Optional[int] = None  # 镜头索引（素材内分段，推测）
    srcPath: Optional[str] = None  # 素材当前路径（工程引用）
    videoType: Optional[int] = None  # 视频类型枚举（普通/慢动作/导入来源等，推测）
    width: Optional[int] = None  # 像素宽度（素材尺寸）

    model_config = ConfigDict(extra="allow")


class Caption(BaseModel):
    """字幕条目对象。

    包含时间点（`inPoint`/`outPoint`）、文本与样式（字体、颜色、字距等）、
    动画与模板信息，以及素材信息 `assetInfo`。
    """
    assetInfo: AssetInfo  # 关联素材信息（文本/字体/时长等）
    captionText: str  # 字幕显示文本
    idString: str  # 字幕唯一标识（项目内引用）
    uid: str  # 运行时/UI 唯一标识（与 idString 并存，推测）
    inPoint: int  # 开始时间点（毫秒）
    outPoint: int  # 结束时间点（毫秒）

    # Optional visual/text properties
    defaultFontName: Optional[str] = None  # 默认字体名（优先于 fontName，推测）
    defaultFontPath: Optional[str] = None  # 默认字体路径
    fontPackagePath: Optional[str] = None  # 字体包路径（资源包）
    opacity: Optional[float] = None  # 不透明度（0–1）
    scaleX: Optional[float] = None  # X 轴缩放
    scaleY: Optional[float] = None  # Y 轴缩放
    textAlignment: Optional[int] = None  # 文本对齐（0=左/1=中/2=右，推测）
    textColor: Optional[RGBA] = None  # 文本颜色

    # Extended caption properties
    drawBackgroundColor: Optional[bool] = None  # 是否绘制背景色块
    drawOutline: Optional[bool] = None  # 是否描边
    drawShadowColor: Optional[bool] = None  # 是否启用阴影/阴影颜色（推测）
    fancyWordId: Optional[str] = None  # 花字模板 ID（特效文字）
    fancyWordPath: Optional[str] = None  # 花字模板路径
    fontId: Optional[str] = None  # 字体资源 ID（与 fontID 可能来源不同）
    fontName: Optional[str] = None  # 字体显示名称（覆盖默认）
    inAnimationDuration: Optional[int] = None  # 入场动画时长（毫秒）
    inAnimationId: Optional[str] = None  # 入场动画 ID
    inAnimationPath: Optional[str] = None  # 入场动画路径
    isVerticalLayout: Optional[bool] = None  # 竖排布局开关
    letterSpacing: Optional[int] = None  # 字间距（单位/百分比，推测）
    lineSpacing: Optional[int] = None  # 行间距（单位/比例，推测）
    loopAnimationDuration: Optional[int] = None  # 循环动画时长
    loopAnimationId: Optional[str] = None  # 循环动画 ID
    loopAnimationPath: Optional[str] = None  # 循环动画路径
    outAnimationDuration: Optional[int] = None  # 出场动画时长
    outAnimationId: Optional[str] = None  # 出场动画 ID
    outAnimationPath: Optional[str] = None  # 出场动画路径
    rotation: Optional[float] = None  # 旋转角度（度）
    transX: Optional[int] = None  # X 轴平移（像素或坐标单位，推测）
    transY: Optional[int] = None  # Y 轴平移（像素或坐标单位，推测）
    underline: Optional[bool] = None  # 下划线开关
    textBold: Optional[bool] = None  # 加粗开关
    textItalic: Optional[bool] = None  # 斜体开关
    templateId: Optional[str] = None  # 字幕模板 ID
    templatePackagePath: Optional[str] = None  # 字幕模板包路径

    model_config = ConfigDict(extra="allow")


class CaptionTrack(BaseModel):
    """字幕轨对象，包含字幕列表与轨道元数据（id/index/type/compacted）。"""
    captions: List[Caption] = Field(default_factory=list)  # 该轨上的所有字幕
    idString: Optional[str] = None  # 轨道唯一标识
    index: Optional[int] = None  # 轨道序号（0 基）
    trackType: Optional[int] = None  # 轨类型枚举（如 3=字幕轨，推测）
    compacted: Optional[bool] = None  # 是否紧凑显示/合并（推测）

    model_config = ConfigDict(extra="allow")


# ========= Utility Methods for captionTracks =========
def ensure_caption_track(project: "BcutProject", index: int = 0) -> CaptionTrack:
    """获取指定索引的字幕轨，若不存在则创建并返回。"""
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
    """创建一个带合理默认值的字幕对象。

    - `text`: 字幕文本
    - `in_ms`/`out_ms`: 开始/结束时间（毫秒），要求 `out_ms >= in_ms`
    - `font_name`/`font_path`: 可选字体名称/路径
    """
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
    """向指定字幕轨追加字幕；若轨不存在则自动创建。"""
    track = ensure_caption_track(project, track_index)
    track.captions.append(caption)
    return caption


def remove_caption(project: "BcutProject", caption_id: str, track_index: int = 0) -> bool:
    """按 `idString` 删除字幕；成功返回 True。"""
    track = ensure_caption_track(project, track_index)
    before = len(track.captions)
    track.captions = [c for c in track.captions if c.idString != caption_id]
    return len(track.captions) < before


def update_caption_text(project: "BcutProject", caption_id: str, new_text: str, track_index: int = 0) -> bool:
    """更新字幕文本，并同步 `assetInfo.content/displayName`；成功返回 True。"""
    track = ensure_caption_track(project, track_index)
    for c in track.captions:
        if c.idString == caption_id:
            c.captionText = new_text
            c.assetInfo.content = new_text
            c.assetInfo.displayName = new_text
            return True
    return False


def shift_caption_time(project: "BcutProject", caption_id: str, delta_ms: int, track_index: int = 0) -> bool:
    """平移字幕的开始/结束时间（毫秒），确保非负并同步时长；成功返回 True。"""
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
    """将项目写回磁盘，使用紧凑的单行 JSON（保持与 Bcut 兼容）。"""
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    data = project.model_dump()
    out_p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return out_p


class AudioRes(BaseModel):
    """时间线配置中的音频参数。"""
    channelCount: int  # 声道数（如 2=立体声）
    sampleRate: int  # 采样率（Hz）


class VideoRes(BaseModel):
    """视频分辨率。"""
    height: int  # 像素高度
    width: int  # 像素宽度


class VideoFps(BaseModel):
    """视频帧率（分子/分母）。"""
    den: int  # 分母（如 1000）
    num: int  # 分子（如 30000 表示 30fps）


class TimelineConfig(BaseModel):
    """时间线配置，包含音频参数、视频分辨率与帧率。"""
    audioRes: AudioRes  # 音频参数
    videoFps: VideoFps  # 帧率设置
    videoRes: VideoRes  # 分辨率设置

    model_config = ConfigDict(extra="allow")


class VideoTrack(BaseModel):
    """视频轨对象；字段保持兼容，clips/transitions 使用任意结构。"""
    clips: List[Dict[str, Any]] = Field(default_factory=list)  # 片段列表（视频段/素材片段）
    idString: Optional[str] = None  # 轨道唯一标识
    index: Optional[int] = None  # 轨序号
    mute: Optional[bool] = None  # 静音开关
    split: Optional[bool] = None  # 是否存在切分标记/被切分（推测）
    trackType: Optional[int] = None  # 轨类型枚举（视频/贴纸/特效，推测）
    transitions: List[Dict[str, Any]] = Field(default_factory=list)  # 转场效果列表

    model_config = ConfigDict(extra="allow")


class Ruler(BaseModel):
    """时间轴标尺信息，含标记点列表。"""
    MarkPointInfo: List[Dict[str, Any]] = Field(default_factory=list)  # 标记点信息列表（时间轴打点）


class Timeline(BaseModel):
    """时间线对象，聚合各类轨道与配置。"""
    adjustTracks: List[Dict[str, Any]] = Field(default_factory=list)  # 调整/变换轨（色彩/速度等，推测）
    audioTracks: List[Dict[str, Any]] = Field(default_factory=list)  # 音频轨集合
    captionTracks: List[CaptionTrack] = Field(default_factory=list)  # 字幕轨集合
    config: TimelineConfig  # 时间线配置
    filterTracks: List[Dict[str, Any]] = Field(default_factory=list)  # 滤镜轨集合
    idString: str  # 时间线唯一标识
    stickerTracks: List[Dict[str, Any]] = Field(default_factory=list)  # 贴纸轨集合
    timelineVideoFxTracks: List[Dict[str, Any]] = Field(default_factory=list)  # 时间线级视频特效轨集合
    videoTracks: List[VideoTrack] = Field(default_factory=list)  # 视频轨集合

    model_config = ConfigDict(extra="allow")


class TimelineWidget(BaseModel):
    """时间线控件与相关 UI 状态。

    注意：部分草稿版本将 `tracking`/`tts`/`ttv` 放置在此层级。
    """
    linkage: bool  # 轨道联动开关（移动剪辑是否联动音视频）
    linkageDelegate: Dict[str, Any]  # 联动策略/委托配置（推测）
    magnet: bool  # 磁吸开关（片段吸附对齐）
    ruler: Ruler  # 标尺/打点
    timeline: Timeline  # 时间线对象

    # Some project drafts embed these at this level
    tracking: Dict[str, Any] = Field(default_factory=dict)  # 追踪设置（对象/人脸等，推测）
    tts: Dict[str, Any] = Field(default_factory=dict)  # 文本转语音设置（推测）
    ttv: Optional[Ttv] = None  # 工程状态扩展（如分离音频/BGM）

    model_config = ConfigDict(extra="allow")


class BrowserPanelFile(BaseModel):
    """素材面板文件条目。"""
    duration: int  # 文件时长（毫秒；pydantic 可将字符串转为 int）
    frameRateDen: int  # 帧率分母
    frameRateNum: int  # 帧率分子
    height: int  # 像素高度
    importTime: str  # 导入时间（字符串）
    itemType: int  # 项类型枚举（视频/音频/图片等，推测）
    recentlyUsedTime: str  # 最近使用时间
    srcPath: str  # 源文件路径
    width: int  # 像素宽度

    model_config = ConfigDict(extra="allow")


class MainWindow(BaseModel):
    """主窗口状态，包含素材面板文件列表。"""
    browserPanelFiles: List[BrowserPanelFile] = Field(default_factory=list)  # 面板文件条目列表

    model_config = ConfigDict(extra="allow")


class Ttv(BaseModel):
    """工程级状态：如是否分离音频、设置 BGM 等。"""
    enableDetach: bool  # 是否启用音频分离
    is_set_bgm: bool  # 是否已设置背景音乐


class BcutProject(BaseModel):
    """Bcut 草稿项目对象（顶层）。

    注意：`tracking`/`tts`/`ttv` 在不同版本中可能位于顶层或 `timelineWidget` 内部。
    本模型允许额外字段（`extra=allow`）以兼容不同版本。
    """
    draftCreatedVersion: str  # 草稿创建版本号字符串
    mainWindow: MainWindow  # 主窗口状态
    timelineWidget: TimelineWidget  # 时间线控件状态

    # Some versions place these at top-level, others under timelineWidget
    tracking: Optional[Dict[str, Any]] = Field(default_factory=dict)  # 顶层追踪设置（版本差异）
    tts: Optional[Dict[str, Any]] = Field(default_factory=dict)  # 顶层 TTS 设置（版本差异）
    ttv: Optional[Ttv] = None  # 顶层工程状态扩展（版本差异）

    model_config = ConfigDict(extra="allow")


def load_bcut_project(path: str) -> BcutProject:
    """加载并校验 Bcut 项目 `.bjson` 文件为 Pydantic 模型。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return BcutProject.model_validate(data)


def summarize_project(project: BcutProject) -> Dict[str, Any]:
    """返回简要摘要：分辨率、帧率、字幕轨数量与字幕总数。"""
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