# Video Generation (Step 6)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S6_Video_Generation]`.

## Core Responsibility
The core function of S6 is to generate high-quality video clips for the `TO_BE_GENERATED` shots identified in the S5 Storyboard. Through iterative communication with the user, the agent determines the exact reference image/video and fine-tunes the text prompt for each shot. 

**Sub-clip Architecture**: Due to physical limitations of the Aliyun video generation API (maximum 15 seconds per call and ONE reference image per call), S6 must handle complex or long shots by splitting them into multiple smaller "sub-clips".

**Language Rule:** The agent MUST strictly communicate and output results in the language used by the user (e.g., if the user communicates in Chinese, the agent must reply and structure reports in Chinese).

## Critical Constraints & Rules
- **Physical API Limitation**: Aliyun API generates max 15s videos with ONE reference image.
- **Strict Interaction & Execution Order (Agent -> JSON -> Script -> Agent)**:
  1. **Assess & Propose**: Evaluate the shot. If it's longer than 15s or has complex action shifts, propose a "Split Plan" to the user (e.g., "Shot 3 is long. I propose splitting it into two sub-clips. Sub-clip 1: 10s, Reference A. Sub-clip 2: 10s, Reference B. Do you agree?").
  2. **Pre-fill JSON**: Once the user agrees to the prompt/references (even for un-split single clips), the Agent MUST first write/update the `asset_manifest.json`. Expand the `sub_clips` array for that shot, filling in `sub_clip_content`, `prompt`, and `reference_path`. Set `"status": "pending"`.
  3. **Serial Execution**: The Agent then calls the video generation script passing the specific `shot_id` and `sub_clip_id`. The script will read the prompt and reference directly from the JSON. **NEVER execute multiple sub-clips of the same shot in parallel.** 
  4. **Iterative Review**: Wait for Sub-clip 1 to finish, have the user review it. Only after the user approves Sub-clip 1, proceed to execute Sub-clip 2.

## Workflow

### Step 0: Skip Logic (Bypass Check)
Check the file `/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json`.
- **Condition A**: If the file contains an empty array `[]` (meaning S5 decided no new videos are needed), immediately output `[STEP_6_COMPLETE]` and skip S6.
- **Condition B**: If all `sub_clips` in the JSON have `"status": "completed"` and non-empty `output_path`, S6 is done. Output `[STEP_6_COMPLETE]`.

### Step 1: Initialization
Execute the initialization script to read the S5 `storyboard.json` and generate the S6 folder structure and `asset_manifest.json`. It will create a default single `sub_clip` (ID: 1) for each shot as a placeholder.
**Command:** `python /home/admin/.openclaw/workspace/auto_film_maker/tools/init_s6_assets.py --video_name <video_name>`

### Step 2: Iterative Preparation & Pre-fill
- For the next pending shot, discuss the prompt, reference image, and whether a sub-clip split is needed.
- Remind the user of expressions, actions, and camera movements.
- **CRITICAL**: Use Python or file editing tools to update `/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json` with the agreed `sub_clips` (prompt, reference_path) BEFORE running the script.

### Step 3: Async Dispatch (Sub-clip by Sub-clip)
- Dispatch the generation for the specific `sub_clip_id` asynchronously. 
- **Command (Async execution using nohup):**
  ```bash
  nohup python /home/admin/.openclaw/workspace/auto_film_maker/tools/aliyun_video_generation.py \
    --model "wan2.6-i2v-us" \
    --seconds "<duration_2_to_15>" \
    --output_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/<shot_id>/sub_clip_<sub_clip_id>.mp4" \
    --manifest_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/<video_name>/asset_manifest.json" \
    --shot_id "<shot_id>" \
    --sub_clip_id "<sub_clip_id>" > /dev/null 2>&1 &
  ```
- *Note: The script reads the prompt and reference directly from the JSON. When done, it writes back the output path and status.*

### Step 4: Generation Status Tracking & Smart Notify
- Before replying to the user, always read `asset_manifest.json`.
- Look for any sub_clip with `"status": "completed"` AND `"user_notified": false`.
- If found, notify the user (e.g., "💡 Sub-clip 1 of Shot A has finished generating!") and then update `"user_notified": true`.

### Step 5: Final Review & Next Sub-clip
- Ask the user to review the finished sub_clip. 
- If approved and there are more sub-clips for this shot, proceed to dispatch the next sub-clip (Step 3). 
- Once all shots and sub-clips are done, output `[STEP_6_COMPLETE]`.
