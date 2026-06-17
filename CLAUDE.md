# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Codex skill called **videounderstand** that converts local tutorial videos (.webm, .mp4, .mkv, .mov) into structured image-text manuals (DOCX/PDF). The workflow: probe video → extract frames → generate contact sheets → understand procedure → build manual → verify → cleanup.

## Key Commands

### Extract frames from video
```powershell
python scripts\prepare_video_understanding.py "path\to\video.mp4" `
  --work-dir ".\work_output" `
  --interval 10 `
  --scene-threshold 0.32 `
  --max-scene-frames 120 `
  --select "00:00:20,00:01:10,00:03:40"
```

Options:
- `--probe-only` — only output video metadata, skip frame extraction
- `--skip-scene` — skip scene-change detection
- `--extract-subtitles` — extract embedded subtitle streams (not speech transcription)
- `--ffmpeg-dir` — path to ffmpeg/ffprobe binaries
- `--dedupe-threshold` — perceptual hash distance for duplicate removal (-1 disables)

### Verify final deliverables
```powershell
python scripts\verify_manual_deliverables.py `
  --docx "path\to\manual.docx" `
  --pdf "path\to\manual.pdf" `
  --keywords "关键词1,关键词2"
```

For Chinese keyword encoding issues on Windows, use `--keywords-file` with a UTF-8 file (one keyword per line).

## Dependencies

- **ffmpeg/ffprobe** — video probing and frame extraction (find via `--ffmpeg-dir`, `VIDEOUNDERSTAND_FFMPEG_DIR`, or PATH)
- **Pillow** — image processing, contact sheets, perceptual hashing
- **python-docx** — DOCX generation and validation
- **pypdf** — PDF validation

## Architecture

### Output Structure (work directory)
```
work_dir/
├── probe.json              # ffprobe metadata
├── manifest.json           # frame inventory with timestamps, hashes, source types
├── frames_interval/        # periodic screenshots (default every 10s)
├── frames_scene/           # scene-change screenshots
├── selected_frames/        # user-specified timestamp screenshots
├── contact_sheets/         # thumbnail grids with timestamp labels
└── subtitles/              # extracted embedded subtitle streams
```

### manifest.json Schema
Each frame entry contains:
- `file` — relative path to image
- `source_type` — `interval`, `scene`, or `selected`
- `timestamp_seconds` / `timestamp` — extraction point
- `width` / `height` — image dimensions
- `ahash` — perceptual hash (scene frames only, after dedupe)

### Frame Selection Strategy
1. Prefer `selected` or `scene` frames for final manual screenshots
2. Keep `interval` frames for sequence context
3. Scene frames are deduped via perceptual hashing (hamming distance ≤ threshold)
4. Long videos: scene frames capped at `--max-scene-frames` via even sampling

## Manual Structure (from references/manual-patterns.md)

Default handbook outline:
1. Title and scope
2. Quick flow overview (stage/action/success table)
3. Prerequisites
4. Illustrated steps (one screenshot per UI transition)
5. Command/settings reference
6. Troubleshooting (symptom/cause/fix)
7. Safety and policy notes
8. Further reference

## Quality Rules

- Never fabricate audio narration claims — only state what was visually verified
- Cross-check commands against official docs when syntax matters
- Use placeholders consistently: `"视频链接"`, `"文件路径"`, `"订阅地址"`, `"输出目录"`
- Include warnings for copyright, credentials, paid content, destructive operations
- For Chinese PDF manuals, embed Chinese-supporting fonts
- Keep temporary files in workspace, never beside source video
- Never delete source video or final deliverables during cleanup
