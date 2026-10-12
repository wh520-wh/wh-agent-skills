---
name: videounderstand
description: >
  Turn local tutorial videos or screen-recording videos (.webm, .mp4, .mkv, .mov, etc.)
  into structured understanding artifacts such as image-text workflows, operating manuals,
  DOCX/PDF handbooks, step-by-step summaries, timestamped notes, and screenshot-based guides.
  Use when the user asks to watch/analyze a video file, extract key frames, organize a tutorial
  into pictures and text, create a desktop PDF/DOCX manual, or clean temporary video-understanding
  work files afterward.
negative_triggers:
  - Do NOT use for downloading online videos (YouTube, Bilibili, etc.)
  - Do NOT use for copyright-protected content extraction without permission
  - Do NOT use for audio-only transcription without visual frames
  - Do NOT use for real-time video streaming analysis
---

# Videounderstand

Use this skill to convert a local tutorial video into a verified, screenshot-backed workflow document. The core pattern is: inspect the video, extract frames, infer the procedure from visuals, build a concise manual, verify deliverables, then clean temporary files while preserving final outputs.

## Workflow

1. Confirm deliverables and destination.
   - If the user asks for a manual, default to both DOCX and PDF when prior context or wording implies both.
   - Place final files where requested; otherwise use the desktop for user-facing documents.
   - Keep a scratch directory under the current workspace, never beside the source video unless requested.

2. Locate tooling.
   - Prefer `ffmpeg`/`ffprobe` near the video file, in the workspace, or on `PATH`.
   - If binaries are elsewhere, pass `--ffmpeg-dir` or set `VIDEOUNDERSTAND_FFMPEG_DIR`.
   - If working with DOCX/PDF manuals, use the `documents` skill and bundled workspace Python dependencies.
   - Use `scripts/prepare_video_understanding.py` to probe and extract frames when useful.

3. Probe the video before generating content.
   - Capture duration, resolution, codec, audio presence, and file size.
   - Choose extraction density from length: 5-10 seconds for short tutorials, 15-30 seconds for long videos, plus scene-change frames.
   - Record these facts in working notes; do not expose raw logs unless useful to the user.

4. Extract review frames.
   - Generate periodic frames and scene-change frames.
   - Make contact sheets for rapid visual scanning; each tile should show a timestamp label.
   - Read `manifest.json` before drafting. It maps every screenshot to file name, timestamp, source type, and resolution.
   - For long videos, cap scene frames and dedupe similar frames instead of loading every detected scene.
   - Select high-signal screenshots around UI changes, command examples, settings pages, error messages, and final results.
   - Re-extract selected screenshots at full useful resolution for the manual.

5. Understand the procedure.
   - Build a timestamped outline first: setup, installation, configuration, execution, advanced options, troubleshooting.
   - For unclear text, inspect neighboring frames rather than guessing.
   - Use OCR, embedded subtitles, or audio transcription only when needed and available.
   - Keep factual claims anchored to visible frames, extracted text, or stable general tool knowledge.
   - For modern software versions, websites, prices, regulations, or current release details, browse or verify from primary sources when freshness matters.

6. Build the manual.
   - Use screenshots as evidence, not decoration. Annotate key areas with boxes or labels when it improves comprehension.
   - Prefer this structure for operator handbooks:
     - Title and scope
     - Quick flow overview
     - Tool prerequisites
     - Step-by-step illustrated procedure
     - Common commands/settings table
     - Troubleshooting
     - Safety, legal, or usage caveats
   - For DOCX, follow the `documents` skill requirements: pick a design preset, use real styles/lists/tables, and verify render when possible.
   - For PDF, embed fonts that support Chinese when writing Chinese manuals.

7. Verify before reporting completion.
   - Confirm final files exist at the requested destination and have non-trivial sizes.
   - Validate DOCX with `python-docx`: paragraphs, tables, image count, and table text.
   - Validate PDF with `pypdf`: page count, encryption state, and keyword extraction.
   - Prefer `scripts/verify_manual_deliverables.py` for repeatable DOCX/PDF checks.
   - Try visual render checks when the environment supports them. If LibreOffice/Poppler is unavailable, say so plainly and report the structural checks you did run.

8. Clean temporary files.
   - Delete only the scratch directory and helper scripts created for this run.
   - Resolve absolute paths before recursive deletion and ensure they remain inside the intended workspace.
   - Never delete the source video or final desktop deliverables unless the user explicitly asks.

## Helper Scripts

Use `scripts/prepare_video_understanding.py` for the repeatable extraction stage:

```powershell
# 将 SKILL_DIR 替换为本 Skill 所在目录的实际路径
# 例如: C:\Users\你的用户名\.claude\skills\videounderstand
python "<SKILL_DIR>/scripts/prepare_video_understanding.py" `
  "path/to/your/video.webm" `
  --work-dir ".\work_example" `
  --interval 10 `
  --scene-threshold 0.32 `
  --max-scene-frames 120 `
  --select "00:00:20,00:01:10,00:03:40"
```

The script creates:

- `probe.json` with ffprobe metadata.
- `manifest.json` with filename, timestamp, source type, resolution, contact sheets, subtitles, and removed duplicate frames.
- `frames_interval/` for periodic screenshots.
- `frames_scene/` for scene-change screenshots.
- `contact_sheets/` for quick scanning, with timestamp labels.
- `selected_frames/` when `--select` timestamps are provided.
- `subtitles/` when `--extract-subtitles` finds embedded subtitle streams.

Use `scripts/verify_manual_deliverables.py` after creating final files:

```powershell
python "<SKILL_DIR>/scripts/verify_manual_deliverables.py" `
  --docx "path/to/manual.docx" `
  --pdf "path/to/manual.pdf" `
  --keywords "关键词1,关键词2"
```

On Windows consoles with Chinese keyword encoding issues, write one keyword per line to a UTF-8 file and pass `--keywords-file`.

Read `references/manual-patterns.md` when writing a tutorial handbook or deciding what sections to include.

## Safety Boundaries

- Never delete the source video unless explicitly requested.
- Never upload video content to external services without user consent.
- Temporary files (frames, contact sheets, scripts) are created in a scratch directory and cleaned up after delivery.
- Final deliverables are placed at the user-specified destination (default: desktop).
- If ffmpeg is missing, stop and report clearly—do not attempt silent fallbacks.

## Quality Rules

- Do not pretend to have watched audio narration unless you actually transcribed or inspected it.
- Do not overfit the manual to one frame; use nearby frames and `manifest.json` to confirm sequence.
- Keep commands copyable and distinguish placeholders such as `"视频链接"` and `"文件路径"` from literal arguments.
- Include warnings for copyright, account access, paid content, security-sensitive settings, or destructive operations when the tutorial touches them.
- Final response should be short: link final files, state verification, and mention any unavailable visual QA dependency.
