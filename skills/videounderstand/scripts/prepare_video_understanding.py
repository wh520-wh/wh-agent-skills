#!/usr/bin/env python3
"""Prepare screenshots, contact sheets, and a timestamp manifest for video understanding."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def parse_timestamp(value: str) -> float:
    parts = [float(p) for p in value.strip().split(":")]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 1:
        return parts[0]
    raise ValueError(f"Timestamp must be SS, MM:SS, or HH:MM:SS: {value}")


def format_timestamp(seconds: float) -> str:
    seconds = max(0.0, seconds)
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    if ms == 1000:
        whole += 1
        ms = 0
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    if ms:
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def safe_timestamp(seconds: float) -> str:
    return format_timestamp(seconds).replace(":", "-").replace(".", "-")


def find_binary(name: str, video: Path, ffmpeg_dir: Path | None = None) -> str:
    suffix = ".exe" if os.name == "nt" else ""
    bases: list[Path] = []
    if ffmpeg_dir:
        bases.append(ffmpeg_dir)
    env_dir = os.environ.get("VIDEOUNDERSTAND_FFMPEG_DIR") or os.environ.get("FFMPEG_DIR")
    if env_dir:
        bases.append(Path(env_dir))
    bases.extend([video.parent, Path.cwd()])

    candidates: list[Path] = []
    for base in bases:
        candidates.extend([
            base / f"{name}{suffix}",
            base / "ffmpeg" / f"{name}{suffix}",
            base / "bin" / f"{name}{suffix}",
        ])
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    found = shutil.which(name) or shutil.which(f"{name}{suffix}")
    if found:
        return found
    raise FileNotFoundError(
        f"Could not find {name}. Use --ffmpeg-dir, set VIDEOUNDERSTAND_FFMPEG_DIR, "
        "place it near the video/workspace, or add it to PATH."
    )


def run(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}")
    return proc.stdout


def capture(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr}")
    return proc.stdout


def probe_video(ffprobe: str, video: Path, out: Path) -> dict[str, Any]:
    raw = capture([
        ffprobe,
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        str(video),
    ])
    data = json.loads(raw)
    (out / "probe.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def summarize_probe(data: dict[str, Any]) -> dict[str, Any]:
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    fmt = data.get("format", {})
    return {
        "duration_seconds": float(fmt.get("duration", 0) or 0),
        "size_bytes": int(fmt.get("size", 0) or 0),
        "video_codec": video_stream.get("codec_name"),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "audio_codec": audio_stream.get("codec_name"),
    }


def image_info(path: Path) -> dict[str, int]:
    with Image.open(path) as im:
        return {"width": im.width, "height": im.height}


def extract_at_timestamp(ffmpeg: str, video: Path, target: Path, seconds: float, width: int) -> None:
    run([
        ffmpeg,
        "-hide_banner",
        "-y",
        "-ss", format_timestamp(seconds),
        "-i", str(video),
        "-frames:v", "1",
        "-vf", f"scale='min({width},iw)':-2",
        "-q:v", "2",
        str(target),
    ])


def extract_interval(
    ffmpeg: str,
    video: Path,
    out: Path,
    interval: int,
    width: int,
    duration: float,
) -> list[dict[str, Any]]:
    target = out / "frames_interval"
    target.mkdir(parents=True, exist_ok=True)
    vf = f"fps=1/{interval},scale='min({width},iw)':-2"
    run([ffmpeg, "-hide_banner", "-y", "-i", str(video), "-vf", vf, "-q:v", "3", str(target / "frame_%04d.jpg")])
    entries = []
    files = sorted(target.glob("frame_*.jpg"))
    for index, path in enumerate(files):
        seconds = min(index * interval, max(0.0, duration))
        info = image_info(path)
        entries.append({
            "file": str(path.relative_to(out)).replace("\\", "/"),
            "source_type": "interval",
            "timestamp_seconds": round(seconds, 3),
            "timestamp": format_timestamp(seconds),
            **info,
        })
    return entries


def parse_showinfo_timestamps(output: str) -> list[float]:
    return [float(x) for x in re.findall(r"pts_time:([0-9.]+)", output)]


def extract_scene(
    ffmpeg: str,
    video: Path,
    out: Path,
    threshold: float,
    width: int,
    max_scene_frames: int,
) -> list[dict[str, Any]]:
    target = out / "frames_scene"
    target.mkdir(parents=True, exist_ok=True)
    vf = f"select='gt(scene,{threshold})',showinfo,scale='min({width},iw)':-2"
    output = run([
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i", str(video),
        "-vf", vf,
        "-vsync", "vfr",
        "-q:v", "3",
        str(target / "scene_%06d.jpg"),
    ])
    timestamps = parse_showinfo_timestamps(output)
    files = sorted(target.glob("scene_*.jpg"))
    entries = []
    for index, path in enumerate(files):
        seconds = timestamps[index] if index < len(timestamps) else 0.0
        info = image_info(path)
        entries.append({
            "file": str(path.relative_to(out)).replace("\\", "/"),
            "source_type": "scene",
            "timestamp_seconds": round(seconds, 3),
            "timestamp": format_timestamp(seconds),
            **info,
        })
    if max_scene_frames > 0 and len(entries) > max_scene_frames:
        entries = sample_entries(entries, max_scene_frames)
        keep = {out / entry["file"] for entry in entries}
        for path in files:
            if path not in keep:
                path.unlink(missing_ok=True)
    return entries


def extract_selected(ffmpeg: str, video: Path, out: Path, timestamps: list[str], width: int) -> list[dict[str, Any]]:
    target = out / "selected_frames"
    target.mkdir(parents=True, exist_ok=True)
    entries = []
    for value in timestamps:
        seconds = parse_timestamp(value)
        path = target / f"{safe_timestamp(seconds)}.jpg"
        extract_at_timestamp(ffmpeg, video, path, seconds, width)
        info = image_info(path)
        entries.append({
            "file": str(path.relative_to(out)).replace("\\", "/"),
            "source_type": "selected",
            "timestamp_seconds": round(seconds, 3),
            "timestamp": format_timestamp(seconds),
            **info,
        })
    return entries


def sample_entries(entries: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit <= 0 or len(entries) <= limit:
        return entries
    if limit == 1:
        return [entries[0]]
    indexes = sorted({round(i * (len(entries) - 1) / (limit - 1)) for i in range(limit)})
    return [entries[i] for i in indexes]


def average_hash(path: Path, size: int = 8) -> int:
    with Image.open(path) as im:
        im = im.convert("L").resize((size, size), Image.Resampling.LANCZOS)
        if hasattr(im, "get_flattened_data"):
            pixels = list(im.get_flattened_data())
        else:
            pixels = list(im.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for idx, pixel in enumerate(pixels):
        if pixel >= avg:
            bits |= 1 << idx
    return bits


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def dedupe_entries(out: Path, entries: list[dict[str, Any]], threshold: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if threshold < 0:
        return entries, []
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    hashes: list[int] = []
    for entry in entries:
        path = out / entry["file"]
        digest = average_hash(path)
        if hashes and min(hamming(digest, old) for old in hashes) <= threshold:
            entry = {**entry, "removed_reason": "perceptual_duplicate"}
            removed.append(entry)
            path.unlink(missing_ok=True)
            continue
        entry["ahash"] = f"{digest:016x}"
        kept.append(entry)
        hashes.append(digest)
    return kept, removed


def load_font(size: int) -> ImageFont.ImageFont:
    for path in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_contact_sheets(out: Path, entries: list[dict[str, Any]], columns: int, thumb_width: int) -> list[str]:
    sheet_entries = [entry for entry in entries if entry["source_type"] in {"interval", "scene"}]
    if not sheet_entries:
        return []
    target = out / "contact_sheets"
    target.mkdir(parents=True, exist_ok=True)
    font = load_font(18)
    thumbs = []
    for entry in sheet_entries:
        path = out / entry["file"]
        im = Image.open(path).convert("RGB")
        ratio = thumb_width / im.width
        thumb = im.resize((thumb_width, int(im.height * ratio)))
        label = f"{entry['timestamp']}  {entry['source_type']}  {Path(entry['file']).name}"
        canvas = Image.new("RGB", (thumb.width, thumb.height + 34), "white")
        canvas.paste(thumb, (0, 0))
        ImageDraw.Draw(canvas).text((6, thumb.height + 6), label, fill=(20, 20, 20), font=font)
        thumbs.append(canvas)
    rows_per_sheet = 4
    per_sheet = columns * rows_per_sheet
    sheet_files = []
    for sheet_index in range(0, len(thumbs), per_sheet):
        chunk = thumbs[sheet_index:sheet_index + per_sheet]
        cell_w = max(t.width for t in chunk)
        cell_h = max(t.height for t in chunk)
        rows = math.ceil(len(chunk) / columns)
        sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
        for idx, thumb in enumerate(chunk):
            sheet.paste(thumb, ((idx % columns) * cell_w, (idx // columns) * cell_h))
        sheet_path = target / f"sheet_{sheet_index // per_sheet + 1:02d}.jpg"
        sheet.save(sheet_path, quality=88)
        sheet_files.append(str(sheet_path.relative_to(out)).replace("\\", "/"))
    return sheet_files


def extract_subtitles(ffmpeg: str, video: Path, out: Path) -> list[str]:
    target = out / "subtitles"
    target.mkdir(parents=True, exist_ok=True)
    # This only extracts embedded subtitle streams. Online captions or speech transcription remain separate tasks.
    run([
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i", str(video),
        "-map", "0:s?",
        "-c:s", "srt",
        str(target / "subtitle_%02d.srt"),
    ])
    return [str(path.relative_to(out)).replace("\\", "/") for path in sorted(target.glob("*.srt"))]


def write_manifest(
    out: Path,
    video: Path,
    probe_summary: dict[str, Any],
    entries: list[dict[str, Any]],
    removed: list[dict[str, Any]],
    contact_sheets: list[str],
    subtitles: list[str],
    args: argparse.Namespace,
) -> None:
    manifest = {
        "video": str(video),
        "probe": probe_summary,
        "options": {
            "interval": args.interval,
            "scene_threshold": args.scene_threshold,
            "max_scene_frames": args.max_scene_frames,
            "dedupe_threshold": args.dedupe_threshold,
            "width": args.width,
        },
        "frames": entries,
        "removed_frames": removed,
        "contact_sheets": contact_sheets,
        "subtitles": subtitles,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Extract frames, timestamp manifest, and contact sheets for tutorial-video understanding.")
    parser.add_argument("video", type=Path)
    parser.add_argument("--work-dir", type=Path, default=Path("work_video_understanding"))
    parser.add_argument("--ffmpeg-dir", type=Path, default=None, help="Directory containing ffmpeg/ffprobe.")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--scene-threshold", type=float, default=0.32)
    parser.add_argument("--max-scene-frames", type=int, default=120, help="Evenly sample scene frames when extraction exceeds this count; 0 means unlimited.")
    parser.add_argument("--dedupe-threshold", type=int, default=6, help="Perceptual hash distance for duplicate removal; -1 disables.")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--select", default="", help="Comma-separated timestamps, e.g. 00:00:20,00:01:10")
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--skip-scene", action="store_true")
    parser.add_argument("--extract-subtitles", action="store_true", help="Extract embedded subtitle streams when present; does not transcribe speech.")
    args = parser.parse_args()

    video = args.video.resolve()
    if not video.exists():
        raise FileNotFoundError(video)
    out = args.work_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    ffmpeg = find_binary("ffmpeg", video, args.ffmpeg_dir.resolve() if args.ffmpeg_dir else None)
    ffprobe = find_binary("ffprobe", video, args.ffmpeg_dir.resolve() if args.ffmpeg_dir else None)
    probe_data = probe_video(ffprobe, video, out)
    summary = summarize_probe(probe_data)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.probe_only:
        return

    entries: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    duration = float(summary.get("duration_seconds") or 0)
    entries.extend(extract_interval(ffmpeg, video, out, args.interval, args.width, duration))
    if not args.skip_scene:
        scene_entries = extract_scene(ffmpeg, video, out, args.scene_threshold, args.width, args.max_scene_frames)
        kept_scene, removed_scene = dedupe_entries(out, scene_entries, args.dedupe_threshold)
        entries.extend(kept_scene)
        removed.extend(removed_scene)
    selections = [x.strip() for x in args.select.split(",") if x.strip()]
    if selections:
        entries.extend(extract_selected(ffmpeg, video, out, selections, args.width))
    entries = sorted(entries, key=lambda item: (item["timestamp_seconds"], item["source_type"], item["file"]))
    contact_sheets = make_contact_sheets(out, entries, columns=3, thumb_width=420)
    subtitles = extract_subtitles(ffmpeg, video, out) if args.extract_subtitles else []
    write_manifest(out, video, summary, entries, removed, contact_sheets, subtitles, args)
    print(f"Prepared video-understanding assets in: {out}")
    print(f"Manifest: {out / 'manifest.json'}")


if __name__ == "__main__":
    main()
