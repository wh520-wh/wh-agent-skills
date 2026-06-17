<div align="center">

# VideoUnderstand | 视频理解

> *「10 分钟教程视频，3 分钟出可验证的图文手册。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-videounderstand-blueviolet)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**把本地教程视频变成 DOCX/PDF 图文手册，带截图、时间戳、联系表、交付验证。**

[看效果](#效果示例) · [安装](#快速开始) · [触发方式](#触发方式) · [它和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界)

</div>

---

## 它解决什么问题

你有一堆录屏教程——软件安装、操作演示、配置流程——想转成图文手册分享给同事或留档。

手动做？一帧一帧截图、标注、排版，一个 10 分钟的视频能磨一下午。

临时问 Agent？它能帮你写文字，但没法系统地提取关键帧、生成联系表、验证最终产物是否完整。

这个 Skill 换了个思路：**先把视频"看懂"（提取周期帧+场景帧+去重），再把过程"写下来"（结构化手册），最后"验收"（DOCX/PDF 产物检查）**。端到端流水线，不是单点功能。

---

## 效果示例

**输入：** 一个 10 分钟的软件安装教程视频 (`.mp4`)

**执行过程：**
1. 探测视频元数据（时长、分辨率、编码）
2. 提取周期帧（每 10 秒一帧）+ 场景变化帧
3. 生成联系表（带时间戳标签的缩略图网格）
4. 根据帧内容推断操作步骤
5. 输出 DOCX/PDF 图文手册
6. 验证交付物（页数、图片数、关键词命中）

**输出：**
```
工作目录/
├── probe.json              # 视频元数据
├── manifest.json           # 帧清单（时间戳、来源、分辨率、哈希）
├── frames_interval/        # 周期截图
├── frames_scene/           # 场景变化截图
├── contact_sheets/         # 联系表（快速浏览用）
└── 最终交付：manual.docx / manual.pdf
```

---

## 快速开始

### 前置条件

- Python 3.10+
- ffmpeg / ffprobe（在 PATH 中，或通过 `--ffmpeg-dir` 指定）
- Python 依赖：`pip install Pillow python-docx pypdf`

### 安装

```bash
# 克隆仓库
git clone https://github.com/wh520-wh/VideoUnderstanding-skill.git
cd VideoUnderstanding-skill

# 安装 Python 依赖
pip install Pillow python-docx pypdf
```

装完对 Agent 说：

```text
帮我把 D:\videos\tutorial.mp4 转成图文手册
```

---

## 触发方式

以下说法都能触发这个 Skill：

- "帮我把这个视频转成图文手册"
- "从这个录屏里提取关键步骤，生成 PDF"
- "把这个教程视频变成 DOCX 操作手册"
- "分析这个视频，截图并整理成文档"
- "视频转图文，输出到桌面"
- "看下这个录屏，帮我写个操作指南"

---

## 能做什么 / 它会交付什么

| 能力 | 交付物 | 典型耗时 |
|---|---|---|
| 视频探测 | `probe.json`（时长、分辨率、编码、音频） | < 5 秒 |
| 周期帧提取 | `frames_interval/` 目录 | 视频时长 / 间隔 |
| 场景帧提取 | `frames_scene/` 目录（去重后） | 视频复杂度决定 |
| 联系表生成 | `contact_sheets/` 目录 | 帧数决定 |
| 手册生成 | `manual.docx` / `manual.pdf` | 内容复杂度决定 |
| 交付验证 | 验证报告（JSON） | < 5 秒 |

---

## 它和同类有什么不同

| 维度 | 同类做法 | VideoUnderstand |
|---|---|---|
| **功能范围** | 只做视频转文字（transcribe） | 端到端：帧提取→联系表→手册生成→交付验证 |
| **帧提取** | 无或依赖外部工具 | 内置：周期帧+场景帧+感知哈希去重 |
| **交付验证** | 无 | 内置验证脚本：检查 DOCX/PDF 结构、图片数、关键词 |
| **联系表** | 无 | 自动生成带时间戳的缩略图网格 |
| **手册结构** | 无模板 | 提供标准大纲（标题→流程→前置→步骤→命令→排障→安全） |
| **中文支持** | 多数面向英文 | 中文字体、中文占位符规范 |

---

## 安全边界

- **不会删除源视频**——除非你明确要求
- **不会上传视频**——所有处理在本地完成
- **不会擅自清理交付物**——临时文件自动清理，最终产物保留
- **ffmpeg 缺失时会停下来报告**——不会静默降级

---

## 文件结构

```
VideoUnderstanding-skill/
├── SKILL.md                                # Skill 主文件（工作流定义）
├── README.md                               # 本文件
├── CLAUDE.md                               # 开发指南
├── LICENSE                                 # MIT 协议
├── agents/
│   └── openai.yaml                         # Agent 接口配置
├── references/
│   └── manual-patterns.md                  # 手册结构模板
├── scripts/
│   ├── prepare_video_understanding.py      # 帧提取脚本
│   └── verify_manual_deliverables.py       # 交付验证脚本
└── examples/
    └── (待补充：真实运行产物样例)
```

---

## 验证与测试

**验收 prompt：**

```text
帮我把 examples/demo.mp4 转成图文手册，输出到桌面，验证一下 DOCX 里至少有 5 张截图。
```

**合格表现：**
- 帧提取完成，`manifest.json` 包含帧清单
- DOCX 文件存在，图片数 ≥ 5
- 验证脚本输出 `{"ok": true}`

---

## 致谢

- [ffmpeg](https://ffmpeg.org/) — 视频处理基础设施
- [Pillow](https://python-pillow.org/) — 图像处理
- [python-docx](https://python-docx.readthedocs.io/) — DOCX 生成
- [pypdf](https://pypdf.readthedocs.io/) — PDF 验证

---

## License

[MIT](LICENSE)

---

<div align="center">

*视频在变，手册在手。*

</div>
