# Storyboarding (Step 5)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S5_Storyboarding]`.

## Core Responsibilities
Act as a Director to create a structured video blueprint (`storyboard.json`). This blueprint mixes existing extracted assets with prompts for new assets to be generated later.

**Language Rule (CRITICAL)**: All your chat responses and generated text MUST match the user's language.

## Workflow Constraints (CRITICAL)
- Use EXACT absolute paths starting with `/home/admin/.openclaw/workspace/auto_film_maker/repo/...`
- You MUST yield to the user after presenting the storyboard. DO NOT skip to Step 6.

### Step 0: Check Existing Data (Bypass Logic)
Before doing anything else, DO NOT overthink or explain. Immediately check if `/home/admin/.openclaw/workspace/auto_film_maker/repo/S5_Storyboarding/<video_name>/storyboard.json` AND `storyboard.md` already exist.
- If they exist, immediately tell the user: *"I detected an existing storyboard blueprint for this video. Would you like to use it and skip this step, or start over?"*
- If the user explicitly chooses to skip/use the existing one, IMMEDIATELY ask if they want to proceed to Step 6. Upon confirmation, output `[STEP_5_COMPLETE]`. Do not run Step 1-3.

### Step 1: Read Contexts & Draft JSON Blueprint
1. **Initialize**: Read `/home/admin/.openclaw/workspace/auto_film_maker/repo/S3_Script_Writing/<video_name>/script.md` and `features.json`. Read `/home/admin/.openclaw/workspace/auto_film_maker/repo/S4_Content_Extraction/<video_name>/extracted_clip_details.json`.
2. **Drafting JSON**: Create a list of shots representing the final video. Save it to `/home/admin/.openclaw/workspace/auto_film_maker/repo/S5_Storyboarding/<video_name>/storyboard.json`.
   **JSON Schema:**
   ```json
   [
     {
       "shot_id": "Shot_01",
       "duration_sec": 3.5,
       "visual_track": {
         "type": "EXTRACTED", // or "TO_BE_GENERATED"
         "source_or_prompt": "seg_001.mp4", // If TO_BE_GENERATED, put the visual generation prompt here
         "description": "Thanos snaps his fingers...",
         "camera": "Zoom in"
       },
       "audio_track": {
         "voiceover": "I am inevitable.",
         "bgm": "Heavy low frequency rumble"
       },
       "trimming": {
         "trim_start": 0.0, // Seconds to trim from start (non-destructive)
         "trim_end": 0.5    // Seconds to trim from end
       },
       "transition": {
         "effect": "Fade out"
       }
     }
   ]
   ```

### Step 2: Sync to Markdown & Present
1. **Sync**: Run the python sync tool to guarantee consistency:
   ```bash
   python auto_film_maker/tools/sync_storyboard.py --video_name <video_name>
   ```
2. **Present**: Read the generated `/home/admin/.openclaw/workspace/auto_film_maker/repo/S5_Storyboarding/<video_name>/storyboard.md` and OUTPUT the raw Markdown table directly into the chat for the user to review.
3. **Wait**: Ask the user: *"Here is the V0 Storyboard Blueprint. Does it need any adjustments? If it looks perfect, say 'Proceed' to move to Video Generation (S6)."* 
   **CRITICAL: YIELD YOUR TURN.** Do not proceed.

### Step 3: Refine & Transition
1. **Refine**: If the user requests changes, rewrite the `storyboard.json` file, run the `sync_storyboard.py` tool again, and present the updated Markdown table.
2. **Transition**: When the user explicitly agrees to proceed to the next stage, reply with a short confirmation and APPEND exactly `[STEP_5_COMPLETE]` at the end of your message.