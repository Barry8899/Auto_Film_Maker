# Content Extraction (Step 4)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S4_Content_Extraction]`. (Note: The frontend will automatically send this hidden trigger when S3 completes and outputs `[STEP_3_COMPLETE]`).

## Core Responsibilities
Based on the style and script outline defined in Step 3, generate a structured 3-layer extraction checklist, run visual understanding to locate these elements in the original video, and extract the precise video clips.

**Language Rule (CRITICAL)**: All your chat responses, as well as the generated files (`extract_content.md`, `extracted_clip_details.json`, and `extraction_report.md`), MUST match the user's language (e.g., if the user speaks Chinese, all outputs and internal document text must be in Chinese).

## Workflow

## Workflow Constraints (CRITICAL)
You MUST NOT execute all phases at once. You must perform Phase 1, wait for the user, then perform Phase 2, wait for the user, and so on.

### Phase 1: Checklist Generation (The 3-Layer Draft)
1. **Initialize & Read**: Upon trigger, read `repo/S3_Script_Writing/<video_name>/features.json` and `repo/S3_Script_Writing/<video_name>/script.md`. Also read the reference structure from `auto_film_maker/skills/S4_Content_Extraction/references/extraction_example.md`.
2. **Drafting V0**: DO NOT ask the user empty questions. Instead, directly generate a 3-layer content extraction checklist draft and save it to `repo/S4_Content_Extraction/<video_name>/extract_content.md`.
   The 3 layers MUST follow the structure shown in the `extraction_example.md` reference file:
   - **Layer 1: Generic Elements** (Space/Environment, Character/Emotion, Action/Behavior, Voice/Dialogue, Lighting/Atmosphere).
   - **Layer 2: Type-Specific Elements** (e.g., Sci-Fi: HUD, mecha; Suspense: peephole, mirrors; Action: weapons, slow-mo).
   - **Layer 3: IP-Specific Elements** (Specific to this video, e.g., "Avengers assemble", Iron Man's armor).
3. **Present & STOP**: Show the user a brief summary of the extraction checklist you created. Then, explicitly ask the user for **Supplement Infos** AND to confirm before moving to Phase 2.
   *"I have generated the V0 extraction checklist based on our script. To help my visual engine perfectly recognize the video, are there any specific visual cues you can provide? (e.g., 'The one in the red armor is Iron Man'). Once you are satisfied with this list and any supplements, let me know to proceed to the extraction phase."*
   **CRITICAL RULE**: YIELD your turn here. DO NOT run any python scripts. DO NOT move to Phase 2.

4. **Refine (If needed)**: If the user provides feedback or supplement info, update `extract_content.md` and save their supplementary context to a variable (`supplement_infos`). Again, **DO NOT automatically run Phase 2** unless they explicitly say "proceed to next phase" or "start extraction".

### Phase 2: Target Clip Extraction (VLM Time-Stamping)
Only execute this when the user explicitly agrees to proceed from Phase 1.
1. **Execution**: Tell the user you are analyzing the video to find the exact timestamps. Run the Gemini extraction script (be sure to pass the user's language using `--lang`):
   ```bash
   python tools/gemini_content_extraction.py --target_content_list "repo/S4_Content_Extraction/<video_name>/extract_content.md" --video_path "repo/S1_uploaded_video/<video_name>.mp4" --supplement_infos "<user_provided_supplement_infos>" --lang "<user_language>"
   ```
2. **Output & HARD STOP**: The script will output a JSON file: `repo/S4_Content_Extraction/<video_name>/extracted_clip_details.json`. 
   **CRITICAL RULE**: Once `gemini_content_extraction.py` finishes, you are **ABSOLUTELY FORBIDDEN** from running `extract_clips.py` in the same response. You MUST END YOUR TURN.
   Tell the user: *"The video has been analyzed and timestamps have been generated. Should I proceed to cut the video clips with FFmpeg?"*
   DO NOT perform any actions from Phase 3. Wait for the user to reply.

### Phase 3: Video Clipping & Dashboard Review
Only execute this when the user explicitly agrees to proceed from Phase 2.
1. **Clipping**: Run the FFmpeg clipping script:
   ```bash
   python tools/extract_clips.py --json_path "repo/S4_Content_Extraction/<video_name>/extracted_clip_details.json" --video_path "repo/S1_uploaded_video/<video_name>.mp4" --out_dir "repo/S4_Content_Extraction/<video_name>/"
   ```
   This script will cut the `.mp4` clips and generate an `extraction_report.md` (A Markdown table with embedded video links for review).
2. **Dashboard Presentation**: DO NOT flood the chat with multiple video files or direct `<video>` tags. To prevent UI freezing, read the generated `extraction_report.md` and **output the Markdown table text directly in the chat**. 
   - Ensure the links remain as text hyperlinks (e.g., `[👉 点击预览](/files/...)`).
   - Tell the user: *"The clips have been successfully extracted! You can click the links below to preview them individually without overloading the page."*
3. **Confirmation**: Ask if they are satisfied with the clips or if any adjustments are needed.
4. **Transition to S5**: When the user explicitly agrees to proceed, reply with a simple confirmation and APPEND the exact string `[STEP_4_COMPLETE]` at the very end of your message.