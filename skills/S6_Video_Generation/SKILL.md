# Video Generation (Step 6)

## Trigger
Triggered when the user sends a message starting with `[TRIGGER: S6_Video_Generation]`.

## 核心定位 (Core Responsibility)
S6（Video Generation）是“加工厂”，纯粹负责素材填补。它只处理 S5 分镜表里被标记为 `TO_BE_GENERATED` 的新视频片段。
核心任务是陪伴用户打磨每一个新生成的素材，完成“找参考 -> 定 Prompt -> 生成 -> 修改 -> 定稿”的互动循环，并且管理好产出的文件路径。

## 执行流转要求 (Execution Rules)

1. **初始化资源目录与Manifest (Initialization)**
   - 收到触发指令后，第一件事必须**使用提供的初始化工具脚本**，自动读取 S5 分镜表，生成对应的 S6 子目录与初始 JSON。
   - **执行命令**: `python /home/admin/.openclaw/workspace/auto_film_maker/tools/init_s6_assets.py --video_name <视频名称>`
   - 这会为所有 `TO_BE_GENERATED` 镜头在 `/repo/S6_Video_Generation/<video_name>/<shot_id>/` 创建专属目录，并生成一个整合记录所有待生成镜头信息的 `/repo/S6_Video_Generation/<video_name>/asset_manifest.json`。

2. **打磨循环与参考指引 (Polishing Loop with User)**
   - 根据初始化的 `asset_manifest.json`，按顺序与用户沟通需要生成的 `shot_id`。
   - 向用户展示 `newshot_content` 的要求。
   - **参考图像/视频**：主动询问用户是否需要提供参考图像或参考视频（用户可以利用工作区的本地文件，也可以现场传图）。如果用户确认了参考文件，将其记录在对应 `shot_id` 的 `reference_path` 数组中。
   - **提示词定稿**：根据 S5 的初步要求和用户的最新意图，构思具体的视频生成模型 Prompt（包括尺寸比例、动作、风格），并与用户确认。敲定后写入 JSON 的 `prompt` 字段。

3. **执行生成与产出维护 (Generation & Output Maintenance)**
   - 确定好 Prompt 与参考图/视频后，执行实际的视频生成工具（如使用对应的 API 脚本，这部分根据系统后续接入的模型工具而定，目前模拟或执行实际生成流程）。
   - 将生成的视频文件放置在对应的 `shot_id` 目录下，并确保将最新定稿的路径更新至 `asset_manifest.json` 的 `output_path` 字段中。

4. **实时更新与确认 (Manifest Updates)**
   - 每完成一个镜头的参考图确认、Prompt 修改或最终视频生成定稿，你都必须**实时更新 `asset_manifest.json` 文件**。
   - 所有的更新只允许针对当前 `shot_id` 的条目。

5. **完结反馈 (Completion)**
   - 当 `asset_manifest.json` 中的所有条目均获得了满意的 `output_path` 后，通知用户本环节全部完成。
   - 等待用户指令。当用户确认进入最终剪辑后，抛出隐式信号 `[STEP_6_COMPLETE]`。
