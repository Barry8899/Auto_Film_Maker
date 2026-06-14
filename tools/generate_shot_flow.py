import os
import sys
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate shot_flow.json from S5 and S6")
    parser.add_argument("--video_name", required=True, help="Name of the video project")
    args = parser.parse_args()

    base_dir = Path("/home/admin/.openclaw/workspace/auto_film_maker/repo")
    s5_path = base_dir / "S5_Storyboarding" / args.video_name / "storyboard.json"
    s6_path = base_dir / "S6_Video_Generation" / args.video_name / "asset_manifest.json"
    s7_dir = base_dir / "S7_Video_Editing" / args.video_name
    
    if not s5_path.exists():
        print(f"Error: {s5_path} not found.")
        sys.exit(1)
        
    with open(s5_path, 'r', encoding='utf-8') as f:
        s5_data = json.load(f)
        
    s6_data = []
    if s6_path.exists():
        with open(s6_path, 'r', encoding='utf-8') as f:
            s6_data = json.load(f)
            
    s6_dict = {item.get('shot_id'): item for item in s6_data if 'shot_id' in item}
    
    shot_flow = []
    
    for shot in s5_data:
        visual = shot.get("visual_track", {})
        v_type = visual.get("type")
        shot_id = shot.get("shot_id", "unknown_shot")
        
        if v_type == "EXISTING":
            shot_flow.append({
                "shot_id": shot_id,
                "content": visual.get("description", ""),
                "resource_path": visual.get("source_video_path", ""),
                "trim_start": 0,
                "trim_end": ""
            })
        elif v_type == "TO_BE_GENERATED":
            s6_shot = s6_dict.get(shot_id)
            if s6_shot and "sub_clips" in s6_shot:
                sub_clips = s6_shot["sub_clips"]
                for sc in sub_clips:
                    # Request: rename to shot_0X_sub_0Y for multiple sub_clips
                    sid = f"{shot_id}_sub_{sc.get('sub_clip_id', 1)}"
                    shot_flow.append({
                        "shot_id": sid,
                        "content": sc.get("sub_clip_content", ""),
                        "resource_path": sc.get("output_path", ""),
                        "trim_start": 0,
                        "trim_end": ""
                    })
            else:
                # Missing from S6, add placeholder
                shot_flow.append({
                    "shot_id": shot_id,
                    "content": visual.get("description", ""),
                    "resource_path": "",
                    "trim_start": 0,
                    "trim_end": ""
                })
                
    s7_dir.mkdir(parents=True, exist_ok=True)
    out_path = s7_dir / "shot_flow.json"
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(shot_flow, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully generated shot_flow.json at: {out_path}")

if __name__ == "__main__":
    main()