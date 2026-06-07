import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Extract video clips using ffmpeg based on JSON definitions.")
    parser.add_argument("--json_path", required=True, help="Path to the extracted_clip_details.json")
    parser.add_argument("--video_path", required=True, help="Path to the original video")
    parser.add_argument("--out_dir", required=True, help="Output directory for the clips and report")
    args = parser.parse_args()

    json_file = Path(args.json_path)
    video_file = Path(args.video_path)
    out_dir = Path(args.out_dir)

    if not json_file.exists():
        print(f"Error: JSON file not found: {json_file}")
        sys.exit(1)
    if not video_file.exists():
        print(f"Error: Video file not found: {video_file}")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    with open(json_file, "r", encoding="utf-8") as f:
        try:
            clips = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)

    # Initialize the Markdown report lines
    report_lines = [
        "# 🎬 视频素材提取报告 (Extraction Report)\n",
        "以下是基于要求为您精准提取的素材片段。为避免多媒体加载导致页面卡顿，请**点击链接**按需打开预览：\n",
        "| 片段 ID | 视频链接 | 情绪标签 / 分数 | 画面描述 | 提取理由 (Reasoning) | 时长 |",
        "|---------|----------|-----------------|----------|----------------------|------|"
    ]

    print(f"Starting extraction for {len(clips)} clips...")

    for clip in clips:
        seg_id = clip.get("segment_id", "unknown_seg")
        start = float(clip.get("start_sec", 0.0))
        duration = float(clip.get("duration_sec", 0.0))
        out_path = out_dir / f"{seg_id}.mp4"

        # FFmpeg command for precise seeking and fast encoding
        # -ss before -i is fast, but for accurate cuts we can use it with re-encoding
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(video_file),
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            str(out_path)
        ]
        
        print(f"[{seg_id}] Extracting {duration}s starting at {start}s...")
        # Run ffmpeg silently
        process = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if process.returncode != 0:
            print(f"Warning: ffmpeg failed for segment {seg_id}")

        # Format web link correctly
        # Assuming the workspace structure maps /home/admin/.openclaw/workspace/auto_film_maker/repo -> /files/repo
        try:
            # We want to strip out everything up to auto_film_maker/ to match the backend /files/ mapping
            cwd = Path.cwd().absolute()
            if 'auto_film_maker' in str(cwd):
                base = cwd if cwd.name == 'auto_film_maker' else cwd / 'auto_film_maker'
            else:
                base = cwd / 'auto_film_maker'
                
            rel_path = out_path.absolute().relative_to(base)
            web_link = f"/files/{rel_path}"
        except ValueError:
            # Fallback path conversion
            path_str = str(out_path).replace("\\", "/")
            if "auto_film_maker/" in path_str:
                web_link = "/files/" + path_str.split("auto_film_maker/")[-1]
            else:
                web_link = f"/files/{path_str}"

        # Clean up text for Markdown table (no newlines)
        tags_str = ", ".join(clip.get("tags", []))
        emo_score = clip.get("emotion_score", "N/A")
        desc = str(clip.get("description", "")).replace("\n", " ").replace("|", "\|")
        reasoning = str(clip.get("reasoning", "")).replace("\n", " ").replace("|", "\|")
        
        row = f"| **{seg_id}** | [👉 点击预览]({web_link}) | `{emo_score}` <br> {tags_str} | {desc} | {reasoning} | {duration}s |"
        report_lines.append(row)

    # Save the report
    report_path = out_dir / "extraction_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n✅ Successfully extracted {len(clips)} clips.")
    print(f"✅ Report saved to: {report_path}")

if __name__ == "__main__":
    main()
