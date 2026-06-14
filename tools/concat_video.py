import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path

def run_command(cmd):
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="Concatenate videos based on shot_flow.json")
    parser.add_argument("--video_name", required=True, help="Name of the video project")
    args = parser.parse_args()

    base_dir = Path("/home/admin/.openclaw/workspace/auto_film_maker/repo")
    s7_dir = base_dir / "S7_Video_Editing" / args.video_name
    shot_flow_path = s7_dir / "shot_flow.json"
    
    if not shot_flow_path.exists():
        print(f"Error: {shot_flow_path} not found.")
        sys.exit(1)

    with open(shot_flow_path, 'r', encoding='utf-8') as f:
        shot_flow = json.load(f)

    if not shot_flow:
        print("Error: shot_flow.json is empty.")
        sys.exit(1)

    tmp_dir = s7_dir / "tmp_concat"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    concat_list_path = tmp_dir / "concat_list.txt"
    processed_files = []

    # Process each clip
    for idx, shot in enumerate(shot_flow):
        src_path = shot.get("resource_path", "")
        if not src_path or not os.path.exists(src_path):
            print(f"Warning: Resource not found for {shot.get('shot_id')} at {src_path}. Skipping.")
            continue

        start = shot.get("trim_start", 0)
        end = shot.get("trim_end", "")
        
        tmp_output = tmp_dir / f"clip_{idx}.mp4"
        
        # Standardize format, framerate, and resolution to avoid concat issues
        # 1080p, 30fps, libx264, aac
        cmd = ["ffmpeg", "-y"]
        
        if start and float(start) > 0:
            cmd.extend(["-ss", str(start)])
            
        cmd.extend(["-i", src_path])
        
        if end and str(end).strip() != "":
            duration = float(end) - float(start)
            if duration > 0:
                cmd.extend(["-t", str(duration)])
                
        # Scale to 1920x1080, pad to fit, 30 fps
        filter_str = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30"
        
        cmd.extend([
            "-vf", filter_str,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-video_track_timescale", "90000",
            str(tmp_output)
        ])
        
        run_command(cmd)
        processed_files.append(tmp_output)

    if not processed_files:
        print("Error: No valid clips found to process.")
        sys.exit(1)

    # Create concat list
    with open(concat_list_path, 'w', encoding='utf-8') as f:
        for p_file in processed_files:
            f.write(f"file '{p_file.name}'\n")

    # Concatenate
    final_output = s7_dir / "final_video.mp4"
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-c", "copy",
        str(final_output)
    ]
    run_command(concat_cmd)
    
    # Cleanup tmp
    shutil.rmtree(tmp_dir)

    print(f"\nSuccess! Final video concatenated at: {final_output}")

if __name__ == "__main__":
    main()