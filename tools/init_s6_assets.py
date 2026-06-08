import os
import sys
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Initialize S6 asset structure from S5 storyboard.json")
    parser.add_argument("--video_name", required=True, help="Name of the video project")
    args = parser.parse_args()

    base_dir = Path("/home/admin/.openclaw/workspace/auto_film_maker/repo")
    s5_json_path = base_dir / "S5_Storyboarding" / args.video_name / "storyboard.json"
    s6_dir = base_dir / "S6_Video_Generation" / args.video_name

    if not s5_json_path.exists():
        print(f"Error: {s5_json_path} does not exist.")
        sys.exit(1)

    try:
        with open(s5_json_path, "r", encoding="utf-8") as f:
            s5_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    shots_to_generate = []

    for shot in s5_data:
        visual = shot.get("visual_track", {})
        if visual.get("type") == "TO_BE_GENERATED":
            shot_id = shot.get("shot_id")
            content = visual.get("description", "")
            if not content and "source_or_prompt" in visual:
                 content = visual.get("source_or_prompt")
            
            if shot_id:
                shots_to_generate.append({
                    "shot_id": shot_id,
                    "newshot_content": content,
                    "reference_path": [],
                    "prompt": "",
                    "output_path": "",
                    "status": "pending",
                    "user_notified": False
                })

    if not shots_to_generate:
        print("No TO_BE_GENERATED shots found in S5 storyboard.")
        sys.exit(0)

    s6_dir.mkdir(parents=True, exist_ok=True)

    for shot in shots_to_generate:
        shot_dir = s6_dir / shot["shot_id"]
        shot_dir.mkdir(exist_ok=True)

    manifest_path = s6_dir / "asset_manifest.json"
    
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(shots_to_generate, f, indent=4, ensure_ascii=False)
        print(f"Successfully initialized S6 for '{args.video_name}'. Created {len(shots_to_generate)} shot folders and asset_manifest.json.")
    except Exception as e:
        print(f"Error writing asset_manifest.json: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
