# Review & Export (Step 8)

## Trigger
Triggered when the user agrees to enter S8 after Step 7 is completed (S7 sends `[STEP_7_COMPLETE]`). The agent should look for the `[TRIGGER: S8_Review_Export]` trigger in the context or flow.

## Core Responsibility
The core function of S8 is to conclude the video generation workflow, present the final output, tease upcoming features, and collect user feedback.

**Language Rule:** The agent MUST strictly communicate and output results in the language used by the user (e.g., if the user communicates in Chinese, the agent must reply and structure reports in Chinese).

## Workflow

### Step 1: Final Presentation & Farewell
Immediately upon entering S8, the agent must present the following three points to the user in a single cohesive message:
1. **Video Location:** Inform the user of the final video path: `/home/admin/.openclaw/workspace/auto_film_maker/repo/S7_Video_Editing/<video_name>/final_video.mp4`. Remind them that they can preview the video in the middle workspace (M-zone) and manually download it from the left file tree (L-zone).
2. **Coming Soon Features:** Inform the user that we are planning to add automated promotional copywriting and one-click publishing to major platforms (like YouTube and Bilibili). Let them know these features are currently under development and coming soon.
3. **Workflow Conclusion & Feedback Request:** Inform the user that the entire Auto Film Maker workflow is now complete and thank them for their time. Ask if they have any suggestions, feedback, or if they would like to start over with a new video project.

### Step 2: Feedback Collection
- If the user provides feedback, the agent should interact with them (asking clarifying questions if necessary) to fully understand their thoughts.
- Once the feedback is clear, the agent must polish the feedback for readability and clarity.
- The agent must then append this polished feedback to the global feedbacks file at `/home/admin/.openclaw/workspace/auto_film_maker/user_feedbacks.json`.
- The format for adding to the JSON array is:
  ```json
  {
    "timestamp": "YYYY-MM-DD HH:MM:SS",
    "feedback": "<polished_feedback_content>"
  }
  ```
  *(Note: Read the existing `user_feedbacks.json` file, append the new object to the list, and overwrite the file. If the file doesn't exist, create it with an initial list containing this object.)*
- Thank the user again for their valuable feedback.