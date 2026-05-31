import argparse
import os
import subprocess
import json
import sys

def extract_frames(video_path, out_dir, frames_data):
    """
    frames_data is a JSON string representing a list of dicts:
    [{"name": "IronMan", "timestamp": "00:00:12"}, {"name": "CaptainAmerica", "timestamp": "00:01:05"}]
    """
    if not os.path.exists(video_path):
        print(json.dumps({"error": f"Video file not found: {video_path}"}))
        sys.exit(1)
        
    os.makedirs(out_dir, exist_ok=True)
    
    try:
        data = json.loads(frames_data)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON string for frames"}))
        sys.exit(1)
    
    results = []
    for item in data:
        name = str(item.get("name", "unknown")).replace(" ", "_")
        timestamp = str(item.get("timestamp", "00:00:00"))
        
        out_path = os.path.join(out_dir, f"{name}.jpg")
        
        cmd = [
            "ffmpeg", "-y", "-ss", timestamp, "-i", video_path,
            "-vframes", "1", "-q:v", "2", out_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(out_path):
                results.append({"name": name, "timestamp": timestamp, "path": out_path, "status": "success"})
            else:
                results.append({"name": name, "timestamp": timestamp, "error": "File not generated", "status": "failed"})
        except Exception as e:
            results.append({"name": name, "timestamp": timestamp, "error": str(e), "status": "failed"})
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract specific frames from a video using ffmpeg")
    parser.add_argument("--video", required=True, help="Path to the video file")
    parser.add_argument("--out_dir", required=True, help="Output directory for the extracted frames")
    parser.add_argument("--frames", required=True, help='JSON string of frames to extract, e.g., \'[{"name":"char1", "timestamp":"00:12"}]\'')
    
    args = parser.parse_args()
    extract_frames(args.video, args.out_dir, args.frames)
