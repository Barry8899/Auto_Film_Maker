import os
import sys
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Sync storyboard.json to storyboard.md")
    parser.add_argument("--video_name", required=True, help="Name of the video project")
    args = parser.parse_args()

    base_dir = Path(f"/home/admin/.openclaw/workspace/auto_film_maker/repo/S5_Storyboarding/{args.video_name}")
    json_path = base_dir / "storyboard.json"
    md_path = base_dir / "storyboard.md"

    if not json_path.exists():
        print(f"Error: {json_path} does not exist.")
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    # Generate MD
    lines = [
        f"# 🎬 分镜表 (Storyboard Blueprint) - {args.video_name}\n",
        "| 镜头 (Shot) | 时长 | 视觉轨 (Visual Track) | 听觉轨 (Audio Track) | 剪裁 & 转场 (Trim & FX) |",
        "|---|---|---|---|---|"
    ]

    for shot in data:
        shot_id = shot.get("shot_id", "Unknown")
        duration = str(shot.get("duration_sec", "0"))

        visual = shot.get("visual_track", {})
        v_type = visual.get("type", "UNKNOWN")
        v_source = visual.get("source_or_prompt", "").replace("\n", " ")
        v_desc = visual.get("description", "").replace("\n", " ")
        v_cam = visual.get("camera", "Static")
        v_str = f"**[{v_type}]**<br>内容: {v_desc}<br>来源/提示词: `{v_source}`<br>运镜: {v_cam}"

        audio = shot.get("audio_track", {})
        a_voice = audio.get("voiceover", "").replace("\n", " ")
        a_bgm = audio.get("bgm", "").replace("\n", " ")
        a_str = f"旁白: {a_voice}<br>BGM: {a_bgm}"

        trim = shot.get("trimming", {})
        trim_start = trim.get('trim_start', 0)
        trim_end = trim.get('trim_end', 0)
        trim_str = f"掐头: {trim_start}s<br>去尾: {trim_end}s"

        trans = shot.get("transition", {}).get("effect", "None")
        
        tf_str = f"{trim_str}<br>转场: **{trans}**"

        lines.append(f"| **{shot_id}** | {duration}s | {v_str} | {a_str} | {tf_str} |")

    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Successfully synced {md_path} from JSON.")
    except Exception as e:
        print(f"Error writing Markdown: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()