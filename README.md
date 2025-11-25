# BilibiliBcutMate

> 中文名：哔哩哔哩剪辑小助手  
> 口号：让 Bcut 剪辑更轻松，让创作更高效！

## 项目由来

“BilibiliBcutMate” 这个名字拆解开来就是：  
**Bilibili**（B站）＋**Bcut**（B站官方剪辑软件）＋**Mate**（伙伴、助手、伙计）。  
合起来的意思很明确——**B站剪辑软件 Bcut 的“下手”**，一个帮你跑腿、打杂、干重活的贴心小助手。  
它不会抢你创意，只会默默帮你处理那些重复、机械、耗时的步骤，让你把更多时间留给真正的创作。

## 功能亮点（持续更新）

- 一键批量导入 / 导出素材  
- 自动对齐字幕与音频节奏  
- 智能识别高能弹幕并生成剪辑节点  
- 快速渲染预设模板（竖版 / 横版 / 封面）  
- 轻量级插件化架构，随装随用，不污染 Bcut 本体  

## 快速开始

1. 确保已安装最新版 [Bcut](https://cut.bilibili.com)。  
2. 下载本仓库最新 Release，解压到任意目录。  
3. 双击 `BcutMate.exe`（或 `BcutMate.sh`）即可启动，首次运行会自动检测 Bcut 路径。  
4. 把素材拖进来，剩下的交给 Mate！

## 开发指南

- 运行环境：`Python >= 3.12`（项目根含 `.python-version` 指定 3.12）
- 安装依赖：
  - 推荐使用系统 Python 并安装依赖：`pip install -U pydantic mcp[cli]`
- 代码布局：`src/` 树形结构，避免本地包遮蔽；运行入口为 `main.py`。

## 目录与数据文件

- `Bcut Drafts/`（示例路径）：存放 Bcut 草稿数据与元信息
  - `draftInfo.json`：草稿元信息列表（id/name/modifyTime/duration 等）
  - `worksInfo.json`：本地作品列表（驱动必剪“本地作品”UI）
  - `{UUID}/`：草稿子目录，包含多个 `.bjson` 草稿快照与可选 `cover.jpg`

## CLI 用法

- 解析单个草稿 `.bjson`
  - `python main.py parse <path/to/file.bjson>`
- 汇总草稿目录（封面、`.bjson` 列表、草稿/作品元数据）
  - `python main.py summarize-drafts "Bcut Drafts"`
- 创建草稿目录与空工程（写入 `draftInfo.json`）
  - `python main.py create-draft "Bcut Drafts" "测试草稿" --width 1920 --height 1080 --fps-num 30 --fps-den 1 --sample-rate 48000 --channel-count 2 --draft-version 3.11.8`

### 本地作品（worksInfo.json）

- 列出本地作品：`python main.py works-list "Bcut Drafts"`
- 新增作品：`python main.py works-add "Bcut Drafts" --draft-id <UUID> --name <NAME> [--duration N --file-path P --image-ratio R --status S]`
- 更新作品：`python main.py works-update "Bcut Drafts" --id <UUID> [--name --duration --file-path --image-ratio --status]`
- 删除作品：`python main.py works-remove "Bcut Drafts" --id <UUID>`
- 查询作品：`python main.py works-find "Bcut Drafts" (--id <UUID> | --draft-id <UUID>)`

### 草稿元信息（draftInfo.json）

- 列出草稿：`python main.py drafts-list "Bcut Drafts"`
- 新增/覆盖草稿条目：`python main.py drafts-add "Bcut Drafts" --id <UUID> --name <NAME> [--duration N --cloud-draft-id C --cloud-draft-version V --storyLineId S --video_slice_id VS]`
- 更新草稿条目：`python main.py drafts-update "Bcut Drafts" --id <UUID> [--name --duration --cloud-draft-id --cloud-draft-version --storyLineId --video_slice_id]`
- 删除草稿条目：`python main.py drafts-remove "Bcut Drafts" --id <UUID>`
- 查询草稿条目：`python main.py drafts-find "Bcut Drafts" --id <UUID>`

### 字幕操作（captionTracks）

- 添加字幕：`python main.py add-caption <file.bjson> <text> <start_ms> <duration_ms> [--track-index 0] [--font-name 名称] [--font-path 路径] [--out-path 输出.bjson]`
- 删除字幕：`python main.py remove-caption <file.bjson> <caption_id> [--track-index 0] [--out-path 输出.bjson]`
- 更新字幕文本：`python main.py update-caption <file.bjson> <caption_id> <new_text> [--track-index 0] [--out-path 输出.bjson]`
- 平移字幕时间：`python main.py shift-caption <file.bjson> <caption_id> <delta_ms> [--track-index 0] [--out-path 输出.bjson]`

## 示例：为草稿批量添加《满江红》字幕

1. 创建空草稿：
   - `python main.py create-draft "Bcut Drafts" "满江红字幕演示"`
2. 获取输出中的 `.bjson` 路径，依次添加分段字幕（示例时长单位：毫秒）：
   - `python main.py add-caption <bjson> "怒发冲冠，凭栏处，潇潇雨歇。" 0 4000 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "抬望眼，仰天长啸，壮怀激烈。" 4000 3500 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "三十功名尘与土，八千里路云和月。" 7500 4500 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "莫等闲，白了少年头，空悲切。" 12000 3500 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "靖康耻，犹未雪；臣子恨，何时灭？" 15500 4500 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "驾长车，踏破贺兰山缺。" 20000 3500 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "壮志饥餐胡虏肉，笑谈渴饮匈奴血。" 23500 4500 --track-index 0 --out-path <bjson>`
   - `python main.py add-caption <bjson> "待从头，收拾旧山河，朝天阙。" 28000 4500 --track-index 0 --out-path <bjson>`
3. 解析确认：`python main.py parse <bjson>` 显示字幕轨与总条数。

## 测试

- 运行：`python -m unittest -v`
- 包含：
  - 草稿创建与索引：`tests/test_create_draft.py`
  - 本地作品 CRUD：`tests/test_works_repo.py`
