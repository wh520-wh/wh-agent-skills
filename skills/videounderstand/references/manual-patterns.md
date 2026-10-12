# Manual Patterns

Use these patterns when converting tutorial videos into image-text manuals.

## Default Handbook Outline

1. Title and scope: what the manual covers and who it is for.
2. Quick flow: a compact table with stage, action, and success signal.
3. Prerequisites: software, files, accounts, permissions, hardware, or network requirements.
4. Illustrated steps: one screenshot per meaningful UI or command-line transition.
5. Command/settings reference: copyable commands or option tables.
6. Troubleshooting: symptom, likely cause, fix.
7. Safety and policy notes: legal, privacy, credential, paid-content, or destructive-operation warnings.
8. Further reference: official docs, project pages, or stable local references.

## Screenshot Selection

Prefer screenshots that show:

- Official download page or repository name.
- Exact file or release asset to choose.
- Folder layout after extraction.
- Terminal command before execution.
- Terminal output proving progress or completion.
- Settings panels where the user must toggle or choose an option.
- Error messages, warnings, or authentication/cookie prompts.
- Final state confirming the task succeeded.

Avoid screenshots that only show intros, blank loading pages, repeated scrolling, or decorative transitions.

## Timestamp Manifest

Read `manifest.json` after frame extraction. Use it to build the timestamped outline and to choose screenshots for the final manual.

Each frame entry includes:

- `file`: relative image path.
- `source_type`: `interval`, `scene`, or `selected`.
- `timestamp_seconds` and `timestamp`: where the screenshot came from.
- `width` and `height`: extracted image resolution.
- `ahash`: perceptual hash for dedupe-aware scene frames.

Prefer selected or scene frames for final screenshots, but keep interval frames for sequence context. Contact sheets already include timestamps, so avoid describing a screenshot as only `frame_0012` in user-facing notes.

## Text Extraction Strategy

- If text is readable in a frame, quote short UI labels and commands exactly.
- If text is partly blocked or blurry, describe the action instead of guessing exact wording.
- Cross-check command examples against official documentation when the current syntax matters.
- Use placeholders consistently: `"视频链接"`, `"文件路径"`, `"订阅地址"`, `"输出目录"`.

## Optional OCR, Subtitles, and Audio

- Use `--extract-subtitles` to extract embedded subtitle streams when present.
- Use OCR when tiny command-line text is central and visual inspection is unreliable.
- Use audio transcription only if the user's request depends on narration details.
- If no OCR/subtitle/transcription step was run, write from visual evidence and say so when relevant.

## Verification Checklist

- Final DOCX opens with the expected number of screenshots.
- Final PDF has pages, extractable text, and expected keywords.
- `scripts/verify_manual_deliverables.py` passes or any failures are explained.
- File names are user-friendly and destination is correct.
- Temporary frames/contact sheets/scripts are removed after delivery.
- Source videos and final deliverables are untouched during cleanup.
