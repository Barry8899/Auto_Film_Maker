#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
from pathlib import Path

def get_api_key():
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if api_key:
        return api_key

    env_path = Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        with open(env_path, "r") as handle:
            for line in handle:
                line = line.strip()
                if line.startswith("DASHSCOPE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def get_sub_clip_data(manifest_path, shot_id, sub_clip_id):
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for shot in data:
            if shot.get("shot_id") == shot_id:
                for sc in shot.get("sub_clips", []):
                    if str(sc.get("sub_clip_id")) == str(sub_clip_id):
                        return sc
    except Exception as e:
        print(f"Failed to read manifest: {e}")
    return None

def update_manifest_sub_clip(manifest_path, shot_id, sub_clip_id, updates):
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        found = False
        for shot in data:
            if shot.get("shot_id") == shot_id:
                for sc in shot.get("sub_clips", []):
                    if str(sc.get("sub_clip_id")) == str(sub_clip_id):
                        sc.update(updates)
                        found = True
                        break
                break
        if not found:
            print(f"Warning: sub_clip {sub_clip_id} for shot {shot_id} not found in manifest.")
            return
            
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to update manifest: {e}")

def normalize_duration(seconds):
    try:
        duration = int(seconds)
    except ValueError:
        duration = 5
    if duration < 2:
        return 2
    elif duration > 15:
        return 15
    return duration

def main():
    parser = argparse.ArgumentParser(description="Generate video using Aliyun DashScope API from sub_clip definition")
    parser.add_argument("--model", default="wan2.6-i2v-us", help="Model selection")
    parser.add_argument("--seconds", default="5", help="Duration of the video in seconds (2~15)")
    parser.add_argument("--resolution", default="720P", help="Resolution of the video")
    parser.add_argument("--output_path", required=True, help="Local path to save the generated mp4 video")
    parser.add_argument("--manifest_path", required=True, help="Path to asset_manifest.json")
    parser.add_argument("--shot_id", required=True, help="Shot ID being generated")
    parser.add_argument("--sub_clip_id", required=True, help="Sub-clip ID being generated")
    
    args = parser.parse_args()

    sc_data = get_sub_clip_data(args.manifest_path, args.shot_id, args.sub_clip_id)
    if not sc_data:
        print(f"Error: sub_clip_id {args.sub_clip_id} not found in shot {args.shot_id} within manifest.")
        sys.exit(1)

    prompt = sc_data.get("prompt")
    reference = sc_data.get("reference_path")

    if not prompt:
        print("Error: prompt is missing in the manifest for this sub_clip.")
        sys.exit(1)

    update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {
        "status": "generating"
    })

    try:
        import dashscope
        from dashscope import VideoSynthesis
    except ImportError:
        print("Error: dashscope python package is required. Run 'pip install dashscope'")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
        sys.exit(1)

    api_key = get_api_key()
    if not api_key:
        print("Error: DASHSCOPE_API_KEY not found in env or ~/.openclaw/.env")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
        sys.exit(1)

    dashscope.api_key = api_key
    dashscope.base_http_api_url = "https://dashscope-us.aliyuncs.com/api/v1"

    if not reference:
        print("Error: Aliyun image-to-video mode requires a reference image in the manifest.")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
        sys.exit(1)

    abs_img_path = str(Path(reference).absolute())
    if not os.path.exists(abs_img_path):
        print(f"Error: Reference image not found at {abs_img_path}")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
        sys.exit(1)

    file_uri = f"file://{abs_img_path}"
    duration_sec = normalize_duration(args.seconds)

    print(f"Submitting video generation request to Aliyun for Shot {args.shot_id} -> Sub-clip {args.sub_clip_id}...")
    try:
        rsp = VideoSynthesis.async_call(
            model=args.model if args.model.startswith("wan2") else "wan2.6-i2v-us",
            prompt=prompt,
            img_url=file_uri,
            resolution="720P",
            duration=duration_sec
        )
        
        if rsp.status_code != 200:
            raise Exception(f"Failed to submit task (HTTP {rsp.status_code}): {rsp.message}")
            
        task_id = rsp.output.task_id
        print(f"Task submitted successfully! Task ID: {task_id}")
    except Exception as e:
        print(f"Error submitting request: {e}")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
        sys.exit(1)

    print("Waiting for video generation to complete. This may take a while...")
    
    while True:
        try:
            poll_rsp = VideoSynthesis.fetch(task_id)
            if poll_rsp.status_code != 200:
                print(f"Polling failed (HTTP {poll_rsp.status_code}): {poll_rsp.message}")
                time.sleep(10)
                continue
                
            status = poll_rsp.output.task_status
            
            if status == "SUCCEEDED":
                result_url = poll_rsp.output.video_url
                print(f"\nGeneration completed successfully! Video URL: {result_url}")
                break
            elif status == "FAILED":
                err_msg = poll_rsp.output.get("message", "Unknown failure")
                print(f"\nGeneration failed! Details: {err_msg}")
                update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
                sys.exit(1)
            else:
                print(f"\rStatus: {status} - Waiting...", end="", flush=True)
                time.sleep(10)
        except Exception as e:
            print(f"Error checking status: {e}")
            time.sleep(10)
            continue

    print(f"Downloading video to {args.output_path}...")
    try:
        import urllib.request
        output_dir = os.path.dirname(args.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        urllib.request.urlretrieve(result_url, args.output_path)
        print(f"Download complete! Saved to: {args.output_path}")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {
            "status": "completed", 
            "output_path": args.output_path, 
            "user_notified": False
        })
    except Exception as e:
        print(f"Error downloading video: {e}")
        update_manifest_sub_clip(args.manifest_path, args.shot_id, args.sub_clip_id, {"status": "failed"})
        sys.exit(1)

if __name__ == "__main__":
    main()
