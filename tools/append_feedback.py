import os
import json
import argparse
from datetime import datetime, timezone, timedelta

def main():
    parser = argparse.ArgumentParser(description="Append user feedback to the feedbacks JSON file.")
    parser.add_argument("--feedback", type=str, required=True, help="The polished feedback content.")
    args = parser.parse_args()

    # Define Beijing Time (UTC+8)
    tz_bj = timezone(timedelta(hours=8))
    current_time = datetime.now(tz_bj).strftime("%Y-%m-%d %H:%M:%S")

    file_path = "/home/admin/.openclaw/workspace/auto_film_maker/user_feedbacks.json"
    
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data.append({
        "timestamp": current_time,
        "feedback": args.feedback
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully appended feedback to {file_path}")

if __name__ == "__main__":
    main()
