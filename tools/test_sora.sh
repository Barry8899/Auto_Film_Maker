#!/bin/bash

# Create a dummy manifest to prevent errors if it doesn't exist
mkdir -p /home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/
if [ ! -f /home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/asset_manifest.json ]; then
    echo '[{"shot_id": "Shot_06", "status": "pending"}]' > /home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/asset_manifest.json
fi

# Make sure the reference image exists (if using actual uploaded image, ensure the path matches)
# The image attached in the prompt will need to be at this path.

python /home/admin/.openclaw/workspace/auto_film_maker/tools/sora_video_generation.py \
  --prompt "A close-up of Person 1 (a middle-aged man with a goatee in 1970s attire), alone in the frame. He is smiling warmly at the camera. Soft nostalgic lighting, highly detailed emotional expressions, 35mm film grain." \
  --model "sora-2" \
  --seconds "4" \
  --resolution "1280x720" \
  --reference "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/Shot_06/refs/stark_105_8.jpg" \
  --output_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/Shot_06/test_output.mp4" \
  --manifest_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/asset_manifest.json" \
  --shot_id "Shot_06"
