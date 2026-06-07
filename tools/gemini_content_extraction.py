import os
import sys
import time
import json
import argparse
from pathlib import Path
import google.generativeai as genai

def setup_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set. Please set it before running.")
        sys.exit(1)
    genai.configure(api_key=api_key)

def upload_and_wait(video_path):
    print(f"Uploading {video_path} to Gemini...")
    try:
        video_file = genai.upload_file(path=video_path)
    except Exception as e:
        print(f"Error uploading video: {e}")
        sys.exit(1)
        
    print(f"Uploaded as {video_file.name}. Waiting for processing...")
    while video_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(5)
        video_file = genai.get_file(video_file.name)
        
    if video_file.state.name == "FAILED":
        print("\nVideo processing failed.")
        sys.exit(1)
        
    print("\nVideo processing complete.")
    return video_file

def main():
    parser = argparse.ArgumentParser(description="Extract video clips using Gemini based on a content list.")
    parser.add_argument("--target_content_list", required=True, help="Path to the markdown file containing the 3-layer checklist.")
    parser.add_argument("--video_path", required=True, help="Path to the source video.")
    parser.add_argument("--supplement_infos", default="", help="Optional supplementary info (who is who, context, etc.).")
    args = parser.parse_args()

    setup_gemini()

    # Resolve paths
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
        
    target_list_path = Path(args.target_content_list)
    if not target_list_path.exists():
        print(f"Error: Target list file not found: {target_list_path}")
        sys.exit(1)
        
    with open(target_list_path, "r", encoding="utf-8") as f:
        target_content_list = f.read()

    video_name = video_path.stem
    # Standard output directory: repo/S4_Content_Extraction/<video_name>
    # Note: ensure we write relative to the workspace correctly.
    output_dir = Path("auto_film_maker/repo/S4_Content_Extraction") / video_name
    output_dir.mkdir(parents=True, exist_ok=True)
    out_json_path = output_dir / "extracted_clip_details.json"

    video_file = upload_and_wait(str(video_path))

    prompt = f"""You are an elite video editor and AI visual analyst.
Your task is to analyze the provided video and extract specific moments that match the 'Target Content List'.

TARGET CONTENT LIST (The elements we need to extract):
{target_content_list}

SUPPLEMENTARY INFOS (Context to help you identify characters/scenes):
{args.supplement_infos}

INSTRUCTIONS & RULES:
1. Analyze the video and find the most representative moments matching the layers in the Target Content List.
2. For each identified moment, create a segment entry.
3. TIMESTAMPS (CRITICAL - AVOID ABRUPT CUTS): 
   - When you find the exact action, you MUST add a 1.5-second padding to both sides.
   - start_sec = exact_start - 1.5 (if this is < 0, set to 0.0)
   - end_sec = exact_end + 1.5
   - duration_sec = end_sec - start_sec
4. REASONING (Chain of Thought): For each segment, provide a "reasoning" field explaining your thought process on why this specific timestamp accurately represents the tags and how you identified the subjects based on the supplementary info.
5. OUTPUT FORMAT: You must return ONLY a valid JSON array. No markdown blocks, no extra text.

Expected JSON Schema (Array of Objects):
[
  {{
    "segment_id": "seg_001",
    "start_sec": 0.0,
    "end_sec": 4.5,
    "duration_sec": 4.5,
    "emotion_score": 0.2, // Float between 0.0 and 1.0 representing emotional intensity
    "tags": ["Space/Environment", "High Contrast"],
    "description": "Detailed description of the visual scene",
    "reasoning": "I selected this because...",
    "output_path": "/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/{video_name}/seg_001.mp4"
  }}
]
"""
    
    print("Analyzing video and generating extraction JSON (This may take a while depending on video length)...")
    # Gemini 1.5 Pro is best for complex long-context reasoning
    model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")
    
    # We force JSON output using response_mime_type
    response = model.generate_content(
        [video_file, prompt],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )

    try:
        result_json = json.loads(response.text)
        
        # Enforce segment IDs and strict output paths locally, just in case the LLM drifted
        for i, item in enumerate(result_json):
            item["segment_id"] = f"seg_{i+1:03d}"
            # ensure start_sec is never negative
            item["start_sec"] = max(0.0, float(item.get("start_sec", 0.0)))
            item["duration_sec"] = round(float(item.get("end_sec", 0.0)) - item["start_sec"], 2)
            item["output_path"] = f"/home/admin/.openclaw/workspace/{output_dir}/{item['segment_id']}.mp4"
            
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=2)
            
        print(f"Extraction details successfully saved to {out_json_path}")
        
    except Exception as e:
        print(f"Failed to parse or save JSON. Error: {e}")
        print(f"Raw response: {response.text}")
        sys.exit(1)
    finally:
        # Cleanup video from Gemini server to free up user's quota
        try:
            genai.delete_file(video_file.name)
            print("Cleaned up temporary video from Gemini server.")
        except:
            pass

if __name__ == "__main__":
    main()
