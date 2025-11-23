# Bcut Drafts 目录与文件格式说明

本文档描述 Bcut 的草稿目录结构、`draftInfo.json` 与 `worksInfo.json` 的用途，以及以 UUID 命名的草稿子目录中 `.bjson` 草稿文件的主要结构与字段含义。

## 目录结构概览

- 根目录包含：
  - `draftInfo.json`：草稿（Draft）元数据列表。
  - `worksInfo.json`：作品（Work/导出项）元数据列表。
  - 若干以 `UUID` 命名的子目录（例如：`F7977726-7E28-49AD-908A-6F01D772240A`），每个子目录对应一个草稿集合：
    - 若干 `.bjson` 草稿文件，文件名通常包含时间戳与 `{GUID}`，例如：`21-33-29-453--{36ba2901-f623-4d48-bee1-1c90b644fcbc}.bjson`
    - `cover.jpg`：草稿封面图。

## draftInfo.json

- 顶层结构：
  - `draftInfos`: 数组，每个元素为一个草稿条目，典型字段：
    - `id`: 草稿的唯一标识（UUID）。
    - `name`: 草稿名称（用户在 Bcut 中可见）。
    - `modifyTime`: 最近修改时间戳（毫秒）。
    - 可能包含 `draftId` 或与目录名一致的标识，用于关联到具体草稿目录（不同版本可能字段名有差异）。
- 用途：
  - 提供草稿层面的基础元信息，用于在 UI 列表中显示名称、时间，或在工具中建立目录与草稿的映射关系。

## worksInfo.json（本地作品来源）

- 顶层结构：
  - `worksInfos`: 数组，每个元素为一个作品条目，典型字段：
    - `draftId`: 关联的草稿 ID（通常与 UUID 子目录名称一致）。
    - `name`: 作品名称。
    - `duration`: 时长（毫秒）。
    - `filePath`: 导出生成的文件路径（可能为空或指向导出的视频/音频）。
    - `status`: 整数状态码，表示作品当前状态（导出中/已完成/失败等，不同版本含义可能有差异）。
- 用途：
  - 驱动必剪软件“本地作品”列表的全部内容；每个条目对应 `worksInfo.json` 中的一项。
  - 管理与草稿关联的导出作品，便于显示导出结果、持续时间、输出路径等信息。

## 草稿子目录（UUID）与 `.bjson` 草稿文件

### 命名与组织

- 子目录名称为草稿的 UUID，例如：`F7977726-7E28-49AD-908A-6F01D772240A`。
- 目录内包含多个 `.bjson` 文件，每个文件代表某次保存的草稿快照；文件名包含时间戳与一个 `{GUID}`。

#### 版本与有效文件规则

- 同一草稿目录中可能存在多个 `.bjson` 文件（自动保存或多次手动保存的快照）。
- 实务经验：最新的 `.bjson` 通常视为“当前有效文件”，较早的文件可视作“备份/历史版本”。
- 判定“最新”的建议：
  - 优先依据文件名中的时间戳（例如 `21-33-29-453--{...}.bjson` 的前缀含时间信息）。
  - 同时检查文件系统修改时间（mtime）。若文件名时间戳与 mtime 不一致，以 mtime 为准更稳妥。
- 工具与脚本处理建议：
  - 读取草稿目录后，按上述规则排序，选取“最新”一个作为当前版本，其余保留为历史版本。
  - 写回修改时不建议覆盖原文件，推荐输出到新文件或使用后缀（例如：`<原文件>.modified.bjson`），以便回退。
  - 不同版本的 Bcut 可能存在命名差异，必要时以 mtime 作为最终依据。

### `.bjson` 顶层结构（典型）

以下字段在不同版本可能存在于顶层或嵌套位置（例如嵌在 `timelineWidget` 中）：

- `draftCreatedVersion`: 草稿创建时的 Bcut 版本（例如 `3.11.8`）。
- `mainWindow`：与编辑器主窗口相关的状态（如 `browserPanelFiles`）。
- `timelineWidget`：时间线控件与轨道集合，是草稿的核心结构：
  - `linkage`/`magnet`/`ruler` 等 UI/交互设置；`ruler` 下常见 `MarkPointInfo` 列表。
  - `timeline`: 时间线对象：
    - `config`: 基本配置
      - `audioRes`: 音频参数，例如 `{ "channelCount": 2, "sampleRate": 48000 }`
      - `videoRes`: 视频分辨率，例如 `{ "width": 1920, "height": 1080 }`
      - `videoFps`: 帧率，例如 `{ "num": 30, "den": 1 }`
    - 轨道集合（数组）：
      - `videoTracks`: 视频轨。
      - `audioTracks`: 音频轨。
      - `captionTracks`: 字幕轨。
      - `filterTracks` / `stickerTracks` / `timelineVideoFxTracks` / `adjustTracks`: 效果、贴纸、调节等轨道。
    - 轨道通用字段：`idString`（轨唯一字符串 ID）、`index`（索引）、`trackType`（类型：视频/音频/字幕等，字幕常为 `3`）、`compacted`（是否收缩显示）。
- `tracking`/`tts`/`ttv`：不同版本的草稿可能将这些状态字段放在顶层或 `timelineWidget` 内，用于记录分离音频、字幕、BGM 等项目级状态。

### 字幕轨与字幕对象（captionTracks）

- `captionTracks`: 数组，每个元素为一个字幕轨对象：
  - `captions`: 字幕列表。
  - 轨道字段：`idString`、`index`、`trackType`（通常为 `3`）、`compacted`。

- 字幕对象（示例字段，因版本可能有增减）：
  - 关键时间：
    - `inPoint`：开始时间（毫秒）。
    - `outPoint`：结束时间（毫秒）。
  - 标识：
    - `idString`：字幕字符串 ID（唯一标识）。
    - `uid`：字幕实例的唯一标识。
  - 文本与样式：
    - `captionText`：字幕文本。
    - `defaultFontName` / `defaultFontPath` / `fontPackagePath`：默认字体信息。
    - `fontName` / `fontId`：字体标识（有时为空或为 `"0"`）。
    - `textAlignment`：对齐方式（如 `1`）。
    - `textColor`：RGBA 颜色，`{ r, g, b, a }` 为 0–1 浮点数。
    - `letterSpacing` / `lineSpacing`：字距/行距（如 `100`/`0`）。
    - `textBold` / `textItalic` / `underline`：样式布尔值。
    - `rotation` / `scaleX` / `scaleY` / `transX` / `transY`：变换与位置。
    - `drawBackgroundColor` / `drawOutline` / `drawShadowColor`：绘制背景/描边/阴影。
    - `inAnimation*` / `outAnimation*` / `loopAnimation*`：入场/出场/循环动画配置（`*` 代表 `Duration`、`Id`、`Path` 等）。
    - `templateId` / `templatePackagePath` / `fancyWordId` / `fancyWordPath`：模板与特效相关。
  - `assetInfo`：与素材相关的详细信息（部分字段因版本不同而存在与否）：
    - 核心：`assetItemType`（字幕素材类型，常见 `15`）、`type`（素材类型值）、`content`（文本）、`duration`（时长，毫秒）、`fontID`、`fontSrcPath`、`realMaterialId`（字幕素材 ID，常见 `"-4"`）。
    - 扩展：`displayName`、`coverPath`、`srcPath`、`origin*`、`frameRate*`、`videoType`、`audioType`、`width`/`height` 等。

#### 时间与单位

- 时间字段（如 `inPoint`、`outPoint`、`assetInfo.duration`）单位为毫秒（ms）。
- 在调整字幕时间时需保持 `outPoint >= inPoint`，并同步更新 `assetInfo.duration = outPoint - inPoint`。

### `.bjson` 的序列化特性

- Bcut 原生 `.bjson` 常为单行紧凑 JSON（压缩的 separators 格式）。
- 为保持兼容，建议写回时也采用紧凑单行（避免在 Bcut 中打开出现意外差异）。

## 关联关系与典型工作流

- `draftInfo.json` 描述草稿基本信息；`worksInfo.json` 描述与草稿关联的作品信息，并直接作为“本地作品”列表的数据来源。
- 每个草稿目录（UUID）内的 `.bjson` 是具体的编辑时间线与轨道数据快照。
- 典型流程：通过 `draftInfo.json` 找到草稿 ID 与名称 → 在同名 UUID 子目录中定位 `.bjson` 草稿文件 → 读取并解析时间线（如字幕轨）进行操作 → 保存回 `.bjson`。

## 本仓库支持的解析与操作

- 代码文件：
  - `bcut_models.py`：Pydantic 模型定义与工具方法（解析 `.bjson`、操作 `captionTracks`，如添加/删除/更新/平移字幕，并保存）。
  - `bcut_drafts.py`：`draftInfo.json` / `worksInfo.json` 的模型与装载函数，以及扫描 `Bcut Drafts` 目录并建立索引的辅助方法。
  - `main.py`：命令行工具，支持：
    - `parse`：解析并输出单个 `.bjson` 摘要（分辨率、FPS、字幕条目等）。
    - `summarize-drafts`：扫描 `Bcut Drafts`，输出每个草稿目录的封面、`.bjson` 列表与元数据汇总。
    - `add-caption` / `remove-caption` / `update-caption` / `shift-caption`：对字幕轨进行增删改与时间平移，并另存为新的 `.bjson` 文件。

## 示例（节选）

```json
{
  "draftCreatedVersion": "3.11.8",
  "timelineWidget": {
    "timeline": {
      "config": {
        "audioRes": { "channelCount": 2, "sampleRate": 48000 },
        "videoFps": { "den": 1, "num": 30 },
        "videoRes": { "width": 1920, "height": 1080 }
      },
      "captionTracks": [
        {
          "idString": "...",
          "index": 1,
          "trackType": 3,
          "compacted": false,
          "captions": [
            {
              "idString": "...",
              "uid": "...",
              "inPoint": 0,
              "outPoint": 3000,
              "captionText": "默认文本",
              "textAlignment": 1,
              "letterSpacing": 100,
              "textColor": { "r": 1, "g": 1, "b": 1, "a": 1 },
              "assetInfo": {
                "assetItemType": 15,
                "type": 4,
                "content": "默认文本",
                "duration": 3000,
                "fontID": 0,
                "realMaterialId": "-4"
              }
            }
          ]
        }
      ]
    }
  }
}
```

## 备注

- 不同版本的 Bcut 草稿可能在顶层或 `timelineWidget` 内放置 `tracking`/`tts`/`ttv` 等字段，解析时需做兼容。
- 字段值可能存在空字符串或默认值（如 `fontName` 为空、`fontId` 为 `"0"`），这通常为正常情况。
- 如果需要将解析或操作后的数据重新导入 Bcut，建议保留字段结构与单行 JSON 写法，以减少不兼容风险。