# Content Extraction (Step 4)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S4_Content_Extraction]`. (Note: The frontend will automatically send this hidden trigger when S3 completes and outputs `[STEP_3_COMPLETE]`).

## Core Responsibilities
Based on the style and script outline defined in Step 3, generate a structured 3-layer extraction checklist, run visual understanding to locate these elements in the original video, and extract the precise video clips.

**Language Rule (CRITICAL)**: All your chat responses, as well as the generated files (`extract_content.md`, `extracted_clip_details.json`, and `extraction_report.md`), MUST match the user's language (e.g., if the user speaks Chinese, all outputs and internal document text must be in Chinese).

## Workflow

### Step 0: Check Existing Data (Bypass Logic)
Before doing anything else, DO NOT overthink or explain. Immediately check if `/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/<video_name>/extraction_report.md` already exists (which implies clips are also extracted).
- If it exists, immediately tell the user: *"I detected existing extracted clips and an extraction report for this video. Would you like to use them and skip this step, or start over?"*
- If the user explicitly chooses to skip/use existing files, IMMEDIATELY ask if they want to proceed to Step 5. Upon confirmation, output `[STEP_4_COMPLETE]`. Do not run Step 1, 2, 3, or 4.

### Step 1: Checklist Generation (V0 Draft)
1. **Initialize**: Upon trigger, read `/home/admin/.openclaw/workspace/auto_film_maker/repo/S3_Script_Writing/<video_name>/features.json`, `script.md`, and `auto_film_maker/skills/S4_Content_Extraction/references/extraction_example.md`.
2. **Drafting V0**: Generate a 3-layer content extraction checklist draft and save it to `/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/<video_name>/extract_content.md` (MUST follow the 3-layer structure from the example).
3. **Present & STOP**: Show the user a brief summary of the checklist. Ask the user for **Supplement Infos** (e.g., character appearances) AND ask if the checklist needs changes.
   *DO NOT run any Python scripts yet. Wait for the user's reply.*

### Step 2: Refinement & Confirmation
1. **Refine**: If the user provides feedback, update `extract_content.md`. Save their context to a variable (`supplement_infos`).
2. **Confirmation Checkpoint**: Ask the user: *"The checklist is updated. Should I start analyzing the video to generate timestamps?"*
   *CRITICAL: YIELD your turn. DO NOT run `gemini_content_extraction.py` until they say yes.*

### Step 3: Target Clip Extraction (VLM Time-Stamping)
**ONLY trigger this step when the user explicitly says "Proceed" or "Yes" after Step 1 or Step 2.**
1. **Execution**: Run the Gemini extraction script using absolute paths (pass `--lang "<user_language>"`):
   ```bash
   python auto_film_maker/tools/gemini_content_extraction.py --target_content_list "/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/<video_name>/extract_content.md" --video_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S1_uploaded_video/<video_name>.mp4" --supplement_infos "<user_provided_supplement_infos>" --lang "<user_language>"
   ```
2. **Output & HARD STOP**: The script outputs `extracted_clip_details.json` to the correct folder. 
   Tell the user: *"The video analysis is complete and timestamps have been generated. Should I proceed to cut the final video clips using FFmpeg?"*
   **CRITICAL RULE**: YOU MUST END YOUR TURN HERE. Absolutely DO NOT run `extract_clips.py` in the same response. Wait for the user to explicitly authorize the clipping.

### Step 4: Video Clipping & Dashboard Review
**ONLY trigger this step when the user explicitly authorizes clipping after Step 3.**
1. **Clipping**: Run the FFmpeg clipping script using absolute paths:
   ```bash
   python auto_film_maker/tools/extract_clips.py --json_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/<video_name>/extracted_clip_details.json" --video_path "/home/admin/.openclaw/workspace/auto_film_maker/repo/S1_uploaded_video/<video_name>.mp4" --out_dir "/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/<video_name>/"
   ```
2. **Dashboard Presentation**: Read the generated `extraction_report.md` and **output the Markdown table text directly in the chat**. (Ensure links remain text hyperlinks, do NOT use `<video>` tags).
3. **Transition to S5**: Ask if they are satisfied. When they explicitly agree to proceed, reply with a confirmation and APPEND exactly `[STEP_4_COMPLETE]` at the end of your message.