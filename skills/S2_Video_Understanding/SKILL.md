# Video Understanding (Step 2)

## 核心职责 (Core Responsibilities)
此 Skill 负责处理用户上传的视频（Step 2 流转）。你需要理解视频内容，提取剧情梗概和主要角色的正脸时间戳，并通过自动化截图与用户进行渐进式交互确认，最终输出结构化的 Markdown 视频分析文档。

## 交互与设计原则 (UX & Interaction Principles)
遵循 Web Design Engineer 中的 **"渐进式确认 (Progressive Disclosure)"** 和反繁琐最佳实践：
- **聪明且克制**：不要向用户抛出长篇大论的提问或冗长的 QA，而是先给出初步的优质结果，让用户做选择题（确认或补充）。
- **一次性确认 (One-Shot Confirmation)**：将剧情梗概、人物截图、人物名称合并在一次消息中展示，避免多轮零碎对话带来的人类疲劳 (HITL Fatigue)。

---

## 执行流程 (Workflow)

### Step 1: 视频理解与时间戳提取
1. **定位视频**：从工作区 `repo/S1_uploaded_video/` 目录下找到最新上传的视频文件。
2. **初始分析**：分析该视频（使用视觉工具或你的原生视频理解能力），提取出：
   - 简要剧情梗概 (Plot Summary)
   - 仅限 **主要人物** 出现的 **正脸时间戳** (过滤掉配角、群演和背影)。

### Step 2: 提取人物截图
1. **后台截帧**：基于步骤 1 获得的时间戳，直接调用提供的专门截帧脚本 `tools/extract_frames.py` 在本地截取主要人物的画面。
2. **保存规范**：截图必须保存至 `repo/S2_Video_Understanding/<video_name>/faces/` 目录下。
   *(执行示例：`python tools/extract_frames.py --video repo/S1_uploaded_video/test.mp4 --out_dir repo/S2_Video_Understanding/test/faces --frames '[{"name":"char1", "timestamp":"00:00:12"}]'`)*

### Step 3: 向用户抛出确认信息
在 M 区聊天框中，**严格按照以下格式**向用户发送确认消息，并将截取的图片渲染在聊天流中：

```text
我已经看完了视频！视频的简要剧情如下：
[简要剧情]

我提取到了 [N] 位主要人物：
🙎‍♂️ ![人物名1](/files/repo/S2_Video_Understanding/<video_name>/faces/char1.jpg) ：[人物名1] (出现在 [时间戳])
🙎‍♀️ ![人物名2](/files/repo/S2_Video_Understanding/<video_name>/faces/char2.jpg) ：[人物名2] (出现在 [时间戳])
...

请问命名是否准确，或者需要我联网搜索他们的背景设定吗？（如果你觉得没问题，回复“直接生成文档”即可）
```

> **命名规则**：利用你自身的知识储备进行识别命名（例如认出是“钢铁侠”、“马斯克”）。如果知识库无法识别，默认为“人物1”、“人物2”等，把命名权交给用户。

### Step 4: 响应用户反馈
- **如果用户要求修改或搜索**（例如：“男的叫钢铁侠，去搜一下他的剧情”）：
  1. 调用 `web_search` 工具搜索该角色的背景设定。
  2. 根据检索结果，在你的上下文中更新剧情或人物背景。
  3. **必须重复展示** 更新后的人物表和剧情，再次让用户进行最终确认。
- **如果用户确认通过**（例如回复“直接生成文档”、“直接生成”或“没问题”）：
  直接进入 Step 5。

### Step 5: 生成最终文档与结束流转
1. **写入 Markdown**：在 `repo/S2_Video_Understanding/<video_name>/` 目录下生成 `<video_name>.md` 文件。
2. **文档结构必须包含**：
   - `# 剧情梗概` (Plot Summary)
   - `# 场景表` (Scene List)
   - `# 人物表` (Character List - 必须包含内嵌的 `/files/...` 格式的人物截图和背景设定)
3. **关键结束信号**：文档保存成功后，你**必须在回复用户的最后一行**，输出系统关键字：
   `[STEP_2_COMPLETE]`
   *(前端监控到此关键字将自动流转到下一阶段)*

---

## 约束与边界 (Constraints)
- 提取和询问必须一次性完成，绝不允许对每一个角色单独发问。
- 输出图片路径时，必须加上 `/files/` 前缀以便在 Web UI 的媒体挂载容器中正确渲染（例如 `![name](/files/repo/...)`）。
- **不要编造图片路径**，必须在 `ffmpeg` 真实截取出图片后再返回路径。