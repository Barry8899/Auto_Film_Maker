# Video Editing (Step 7)

## Trigger
Triggered when the user agrees to enter S7 after Step 6 is completed (S6 sends `[STEP_6_COMPLETE]`). The agent should look for the `[TRIGGER: S7_Video_Editing]` trigger in the context or flow.

## Core Responsibility
The core function of S7 is to assemble the individual clips from S5 (Existing Videos) and S6 (Generated Videos) into a final sequenced video. 

**Language Rule:** The agent MUST strictly communicate and output results in the language used by the user (e.g., if the user communicates in Chinese, the agent must reply and structure reports in Chinese).

## Workflow

### Step 1: Generate `shot_flow.json`
Execute the tool script to gather video data from S5 (`storyboard.json`) and S6 (`asset_manifest.json`) to create a unified timeline sequence JSON file (`shot_flow.json`).
**Command:** `python /home/admin/.openclaw/workspace/auto_film_maker/tools/generate_shot_flow.py --video_name <video_name>`

*Note: The generated `shot_flow.json` will merge all multi-clip `sub_clips` from S6 into flattened independent shots named `shot_0X_sub_0Y`.*

### Step 2: User Review & Confirmation
- After the JSON is generated, the agent **MUST** present the `shot_flow.json` structure to the user (you can summarize the shots and their `trim_start` and `trim_end` times). 
- Ask the user to review the sequencing and see if any start/end trims need to be modified.
- **CRITICAL:** Wait for the user's explicit confirmation (e.g., "The sequence is correct, go ahead and stitch them together.") before proceeding to Step 3. Do not auto-execute ffmpeg.

### Step 3: Ffmpeg Concatenation
Once the user explicitly approves the sequence, run the concatenation tool. This tool will trim the videos based on `shot_flow.json` and stitch them into a single `final_video.mp4` file.
**Command:** `python /home/admin/.openclaw/workspace/auto_film_maker/tools/concat_video.py --video_name <video_name>`

### Step 4: Final Output Review
- Inform the user that the final video has been successfully generated at:
  `/home/admin/.openclaw/workspace/auto_film_maker/repo/S7_Video_Editing/<video_name>/final_video.mp4`
- Ask the user to review the final MP4.
- If the user approves the final video and has no further edits, output `[STEP_7_COMPLETE]` to conclude S7 and naturally transition the user into S8.