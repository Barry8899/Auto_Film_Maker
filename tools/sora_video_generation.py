import os
import sys
import time
import argparse
import requests
import json

SORA_API_KEY = "sk-2JVld2GD1R4mAuTi9w2EC0Lu2XwaCLuMkOVhvsXOo2cdRr8l"
BASE_URL = "https://api.bianxie.ai/v1/videos"

def update_manifest(manifest_path, shot_id, updates):
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for shot in data:
            if shot.get("shot_id") == shot_id:
                shot.update(updates)
                break
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to update manifest: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate video using Sora API")
    parser.add_argument("--prompt", required=True, help="Text prompt for video generation")
    parser.add_argument("--model", default="sora-2", help="Model selection")
    parser.add_argument("--reference", default=None, help="Path to reference image or video (optional)")
    parser.add_argument("--seconds", default="4", help="Duration of the video in seconds (default 4)")
    parser.add_argument("--resolution", default="1280x720", help="Resolution of the video (e.g. 1280x720)")
    parser.add_argument("--output_path", required=True, help="Local path to save the generated mp4 video")
    parser.add_argument("--manifest_path", required=True, help="Path to asset_manifest.json")
    parser.add_argument("--shot_id", required=True, help="Shot ID being generated")
    
    args = parser.parse_args()

    update_manifest(args.manifest_path, args.shot_id, {"status": "generating"})

    headers = {
        "Authorization": f"Bearer {SORA_API_KEY}"
    }

    data = {
        "prompt": args.prompt,
        "model": args.model,
        "seconds": args.seconds,
        "size": args.resolution
    }

    files = {}
    if args.reference:
        if not os.path.exists(args.reference):
            print(f"Error: Reference file not found at {args.reference}")
            update_manifest(args.manifest_path, args.shot_id, {"status": "failed"})
            sys.exit(1)
        files["input_reference"] = open(args.reference, "rb")

    print(f"Submitting video generation request...")
    try:
        if files:
            response = requests.post(BASE_URL, headers=headers, data=data, files=files)
        else:
            response = requests.post(BASE_URL, headers=headers, data=data)
        
        response.raise_for_status()
        res_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error submitting request: {e}")
        if 'response' in locals() and response is not None:
            print(f"Response: {response.text}")
        update_manifest(args.manifest_path, args.shot_id, {"status": "failed"})
        print("Note: The API seems to be returning 'model_not_found'. The testing might fail due to provider availability. Exiting.")
        sys.exit(1)

    video_id = res_json.get("id")
    if not video_id:
        print(f"Failed to get video ID from response: {res_json}")
        update_manifest(args.manifest_path, args.shot_id, {"status": "failed"})
        sys.exit(1)
    
    print(f"Task submitted successfully! Video ID: {video_id}")

    print("Waiting for video generation to complete. This may take a while...")
    status_url = f"{BASE_URL}/{video_id}"
    
    while True:
        try:
            status_res = requests.get(status_url, headers=headers)
            status_res.raise_for_status()
            status_json = status_res.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            time.sleep(10)
            continue
        
        status = status_json.get("status")
        progress = status_json.get("progress", 0)
        
        if status == "completed":
            print("\nGeneration completed successfully!")
            break
        elif status == "failed" or status == "error":
            print(f"\nGeneration failed! Details: {status_json.get('error')}")
            update_manifest(args.manifest_path, args.shot_id, {"status": "failed"})
            sys.exit(1)
        else:
            print(f"\rStatus: {status} - Progress: {progress}%", end="", flush=True)
            time.sleep(10)

    print(f"Downloading video to {args.output_path}...")
    content_url = f"{BASE_URL}/{video_id}/content"
    try:
        download_res = requests.get(content_url, headers=headers, stream=True)
        download_res.raise_for_status()
        
        output_dir = os.path.dirname(args.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output_path, "wb") as f:
            for chunk in download_res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Download complete! Saved to: {args.output_path}")
        update_manifest(args.manifest_path, args.shot_id, {
            "status": "completed", 
            "output_path": args.output_path, 
            "user_notified": False
        })
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")
        if 'download_res' in locals() and download_res is not None:
            print(f"Response: {download_res.text}")
        update_manifest(args.manifest_path, args.shot_id, {"status": "failed"})
        sys.exit(1)
        
if __name__ == "__main__":
    main()
