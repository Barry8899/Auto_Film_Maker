import os
import sys
import time
import argparse
import requests

SORA_API_KEY = "sk-2JVld2GD1R4mAuTi9w2EC0Lu2XwaCLuMkOVhvsXOo2cdRr8l"
BASE_URL = "https://api.bianxie.ai/v1/videos"

def main():
    parser = argparse.ArgumentParser(description="Generate video using Sora API")
    parser.add_argument("--prompt", required=True, help="Text prompt for video generation")
    parser.add_argument("--model", default="sora-2", choices=["sora-2", "sora-2-pro"], help="Model selection")
    parser.add_argument("--reference", default=None, help="Path to reference image or video (optional)")
    parser.add_argument("--seconds", default="4", help="Duration of the video in seconds (default 4)")
    parser.add_argument("--resolution", default="1280x720", help="Resolution of the video (e.g. 1280x720)")
    parser.add_argument("--output_path", required=True, help="Local path to save the generated mp4 video")
    
    args = parser.parse_args()

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
            sys.exit(1)
        files["input_reference"] = open(args.reference, "rb")

    # 1. 提交生成任务
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
        sys.exit(1)

    video_id = res_json.get("id")
    if not video_id:
        print(f"Failed to get video ID from response: {res_json}")
        sys.exit(1)
    
    print(f"Task submitted successfully! Video ID: {video_id}")

    # 2. 轮询等待视频生成完成
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
            sys.exit(1)
        else:
            print(f"\rStatus: {status} - Progress: {progress}%", end="", flush=True)
            time.sleep(10)

    # 3. 下载视频
    print(f"Downloading video to {args.output_path}...")
    content_url = f"{BASE_URL}/{video_id}/content"
    try:
        download_res = requests.get(content_url, headers=headers, stream=True)
        download_res.raise_for_status()
        
        # 确保输出目录存在
        output_dir = os.path.dirname(args.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output_path, "wb") as f:
            for chunk in download_res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Download complete! Saved to: {args.output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")
        if 'download_res' in locals() and download_res is not None:
            print(f"Response: {download_res.text}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
