# Video Generation (Step 6)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S6_Video_Generation]`.

## Core Responsibility
The core function of S6 is to generate high-quality video clips for the `TO_BE_GENERATED` shots identified in the S5 Storyboard. Through iterative communication with the user, the agent determines the exact reference image/video and fine-tunes the text prompt for each shot. The final outputs and generation metadata are maintained in `asset_manifest.json`.

**Language Rule:** The agent MUST strictly communicate and output results in the language used by the user (e.g., if the user communicates in Chinese, the agent must reply and structure reports in Chinese).

## Critical Constraints & Rules
- **Copyright Avoidance**: Do NOT use copyrighted names, IP characters, or real celebrity names in the prompts (e.g., do not write "Tony Stark" or "Howard"). Use generic visual descriptors instead (e.g., "Person 1, a middle-aged man with a goatee in a 1970s suit").
- **Reference Image Limitation**: The video generation API only accepts **ONE** reference image per generation. DO NOT silently combine or stitch multiple images into one. If the user provides multiple images, explicitly inform them of this limitation and ask them to choose ONE, or suggest breaking the shot into two separate shots.
- **Strict Manifest Updating**: When the user approves a prompt and reference, you MUST update `asset_manifest.json` with the exact choices. You must save the EXACT and FULL text of the prompt (do not truncate) and the exact file path of the reference image.

## Workflow

### Step 0: Bypass Check
Check if the file `/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json` already exists. If it does, inform the user that S6 assets already exist and offer an option to skip S6 or overwrite.

### Step 1: Initialization
Execute the initialization script to read the S5 `storyboard.json` and generate the S6 folder structure and `asset_manifest.json`.
**Command:** `python /home/admin/.openclaw/workspace/auto_film_maker/tools/init_s6_assets.py --video_name <video_name>`

### Step 2: Iterative Preparation & Async Dispatch
- For each pending shot in `asset_manifest.json`, discuss the prompt and optional reference files with the user.
- Once the user approves the prompt and references, **dispatch the generation asynchronously**. DO NOT wait for it to finish.
- **Command (Async execution using nohup):**
  ```bash
  nohup python /home/admin/.openclaw/workspace/auto_film_maker/tools/sora_video_generation.py \
    --prompt "<finalized_prompt>" \
    --model "sora-2" \
    --seconds "4" \
    --resolution "1280x720" \
    --reference "<optional_reference_path>" \
    --output_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/<shot_id>/output.mp4" \
    --manifest_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json" \
    --shot_id "<shot_id>" > /dev/null 2>&1 &
  ```
- Immediately inform the user that the shot is generating in the background, and seamlessly move on to discuss the next shot.

### Step 3: Generation Status Tracking & Smart Notify
- **CRITICAL RULE:** Before sending *any* reply to the user, you MUST first read the current `asset_manifest.json`.
- Check for any shots where `"status": "completed"` AND `"user_notified": false`.
- If found, include a polite "by the way" notification in your reply (e.g., "💡 By the way, Shot_A has finished generating! You can check it in the sidebar."), and then update the `asset_manifest.json` to set `"user_notified": true` for those shots.

### Step 4: Final Review & Completion
- Allow the user to review the generated videos. If any shot needs adjustments, loop back to Step 2 for that specific shot.
- Once all shots are completed and the user is satisfied, output the implicit signal `[STEP_6_COMPLETE]` to transition to S7 (Video Editing).