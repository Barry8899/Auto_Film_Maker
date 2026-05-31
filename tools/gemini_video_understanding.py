import os
import sys
import json
import argparse
import google.generativeai as genai
import time

def analyze_video(video_path, out_json):
    if not os.path.exists(video_path):
        print(json.dumps({"error": f"File not found: {video_path}"}))
        sys.exit(1)
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(json.dumps({"error": "GEMINI_API_KEY environment variable not set"}))
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    
    try:
        # Upload the video file to Gemini API
        video_file = genai.upload_file(path=video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            print(json.dumps({"error": "Video processing failed on Gemini servers."}))
            sys.exit(1)
            
        # Call the model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        prompt = """
        Analyze this video. Return a strictly valid JSON object with the following schema:
        {
          "plot_summary": "A brief summary of what happens in the video.",
          "main_characters": [
            {
              "person_name": "CharacterName or 'Unknown1'",
              "time_stamp": "00:00:10" // Approximate time (HH:MM:SS) where the character's face is clearly visible
            }
          ]
        }
        Only include main characters. Ignore background people. Ensure output is pure JSON without markdown wrappers.
        """
        response = model.generate_content([video_file, prompt], request_options={"timeout": 600})
        
        # Clean response text
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
            
        data = json.loads(result_text)
        
        # Inject source_video into each character for downstream processing
        for char in data.get("main_characters", []):
            char["source_video"] = video_path
            
        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(json.dumps({"status": "success", "out_json": out_json}))
        
        # Cleanup
        genai.delete_file(video_file.name)
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze video using Gemini API")
    parser.add_argument("--video", required=True, help="Path to the video file")
    parser.add_argument("--out_json", required=True, help="Path to save the JSON output")
    args = parser.parse_args()
    
    analyze_video(args.video, args.out_json)
