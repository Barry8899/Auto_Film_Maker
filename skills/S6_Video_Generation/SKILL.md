# Video Generation (Step 6)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S6_Video_Generation]`.

## Core Responsibility
The core function of S6 is to generate high-quality video clips for the `TO_BE_GENERATED` shots identified in the S5 Storyboard. Through iterative communication with the user, the agent determines the exact reference image/video and fine-tunes the text prompt for each shot. The final outputs and generation metadata are maintained in `asset_manifest.json`.

**Language Rule:** The agent MUST strictly communicate and output results in the language used by the user (e.g., if the user communicates in Chinese, the agent must reply and structure reports in Chinese).

## Critical Constraints & Rules
- **Copyright Avoidance**: Do NOT use copyrighted names, IP characters, or real celebrity names in the prompts (e.g., do not write "Tony Stark" or "Captain America"). Use generic visual descriptors instead (e.g., "Person 1, a middle-aged man with a goatee in a 1970s suit").
- **Reference Image Limitation**: The video generation API only accepts **ONE** reference image per generation. DO NOT silently combine or stitch multiple images into one. If the user provides multiple images, explicitly inform them of this limitation and ask them to choose ONE, or suggest breaking the shot into two separate shots. The `reference_path` in `asset_manifest.json` is a string to enforce this single-image rule.
- **Prompt Precision Requirement**: The Aliyun video generation model requires EXPLICIT details. You must proactively ensure the prompt clearly describes:
  1. The character's exact **facial expressions** (e.g., smiling gently, looking angry).
  2. The character's **body actions/movements** (e.g., raising a hand, walking forward).
  3. The character's **language/speech status** (e.g., mouth closed, speaking angrily).
  4. The **environmental/camera changes** (e.g., camera pans right, lighting darkens).
  If the user forgets to specify these details, the agent MUST proactively remind them or add these details into the proposed prompt to prevent chaotic or disjointed video generation.
- **Strict Manifest Updating**: When you run the generation script (`aliyun_video_generation.py`), it will automatically save the prompt and reference image path into `asset_manifest.json`. You do not need to manually write the JSON before running the script; the script handles the synchronization.

## Workflow

### Step 0: Bypass Check
Check if the file `/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json` already exists. **Then, inspect its contents:** If it exists AND all of its generated shots are fully populated (meaning `reference_path`, `prompt`, and `output_path` are not empty strings for completed shots), inform the user that S6 assets already exist and are fully populated, and offer an option to skip S6 entirely or overwrite. If the file exists but has empty/pending fields, you should continue processing the pending shots.

### Step 1: Initialization
Execute the initialization script to read the S5 `storyboard.json` and generate the S6 folder structure and `asset_manifest.json`.
**Command:** `python /home/admin/.openclaw/workspace/auto_film_maker/tools/init_s6_assets.py --video_name <video_name>`

### Step 2: Iterative Preparation & Async Dispatch
- For each pending shot in `asset_manifest.json`, discuss the prompt and a single reference image with the user.
- **Remind:** Always ensure the prompt covers expressions, actions, and camera movements before confirming!
- Once the user approves the prompt and reference, **dispatch the generation asynchronously**. DO NOT wait for it to finish.
- **Command (Async execution using nohup):**
  ```bash
  nohup python /home/admin/.openclaw/workspace/auto_film_maker/tools/aliyun_video_generation.py \
    --prompt "<finalized_prompt>" \
    --model "wan2.6-i2v-us" \
    --seconds "<duration_2_to_15>" \
    --reference "<absolute_reference_path>" \
    --output_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/<shot_id>/output.mp4" \
    --manifest_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json" \
    --shot_id "<shot_id>" > /dev/null 2>&1 &
  ```
- *Note: Running this command will automatically update the `prompt`, `reference_path`, and `status` in the `asset_manifest.json`.*
- Immediately inform the user that the shot is generating in the background, and seamlessly move on to discuss the next shot.

### Step 3: Generation Status Tracking & Smart Notify
- **CRITICAL RULE:** Before sending *any* reply to the user, you MUST first read the current `asset_manifest.json`.
- Check for any shots where `"status": "completed"` AND `"user_notified": false`.
- If found, include a polite "by the way" notification in your reply (e.g., "💡 By the way, Shot_A has finished generating! You can check it in the sidebar."), and then update the `asset_manifest.json` to set `"user_notified": true` for those shots.

### Step 4: Final Review & Completion
- Allow the user to review the generated videos. If any shot needs adjustments, loop back to Step 2 for that specific shot.
- Once all shots are completed and the user is satisfied, output the implicit signal `[STEP_6_COMPLETE]` to transition to S7 (Video Editing).