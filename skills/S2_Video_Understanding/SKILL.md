# Video Understanding (Step 2)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S2_Video_Understanding]` (e.g., `[TRIGGER: S2_Video_Understanding] repo/S1_uploaded_video/test.mp4`).

## Core Responsibilities
Analyze the video to extract the plot and the timestamps of MAIN characters ONLY. Minor or fleeting characters should be ignored. Extract facial frames (auto-appending .500 to timestamps for clarity), present them to the user for one-shot confirmation, and finally output a structured Markdown report.
**Language Rule**: All your chat responses and the final Markdown document MUST match the user's language (e.g., if the user prompts in Chinese, respond and write the report in Chinese).

## Workflow

### Step 1: Video Analysis & JSON Generation
Call the dedicated understanding script to analyze the video and save the results as a JSON file.
Ensure you instruct Gemini to ONLY identify the primary/main characters of the video. The extracted timestamps should represent their FIRST clear frontal appearance. 
```bash
python tools/gemini_video_understanding.py --video <path_to_video> --out_json repo/S2_Video_Understanding/<video_name>_data.json
```

### Step 2: Extract Character Frames
Call the extraction script passing the generated JSON file. This script will read the accurate timestamps, append '.500' to target the middle of the second, and extract frame-accurate images to the `faces/` directory.
```bash
python tools/extract_frames.py --json_file repo/S2_Video_Understanding/<video_name>_data.json
```

### Step 3: Progressive Confirmation (One-Shot)
Present the extracted information to the user in a clean format. Do not write the final markdown document yet.
Output this exact structure in the chat (translate to the user's language):

"I have finished analyzing the video! Here is the brief plot:
[Plot Summary]

I extracted [N] main characters:
🙎♂️ ![Name1](/files/repo/S2_Video_Understanding/<video_name>/faces/char1.jpg) : [Name1] (Appears at [Timestamp])
...

Are these names accurate? Would you like me to search the web for their background settings? (If everything looks good, just reply 'Proceed' or '直接生成文档')"

### Step 4: Refinement
If the user provides corrections or requests a web search, use the `web_search` tool, update your context, and PRESENT THE LIST AGAIN for final confirmation.

### Step 5: Final Output
ONLY AFTER user confirmation, generate the final markdown report at `repo/S2_Video_Understanding/<video_name>/<video_name>.md`.
It must include:
- `# Plot Summary`
- `# Scene List`
- `# Character List` (MUST embed the local image paths using `![name](/files/...)` format and include their backgrounds).

At the very end of your final chat message confirming the file is saved, you MUST append:
`[STEP_2_COMPLETE]`
