# Video Understanding (Step 2)

## 核心职责 (Core Responsibilities)
此 Skill 是专门处理 `S2` 视频理解流转的最高优先级指令。**一旦触发此 Skill，你必须无视其他任何全局的 Video Understanding 规则（严禁输出 6 点格式的默认分析报告）。**
你的目标是：调用专属的 Python 工具分析视频，调用截帧脚本，随后向用户输出**唯一标准化**的“带图一次性确认”话术。绝对不要在未获用户同意前就擅自生成 Markdown 文档！

## 交互与设计原则 (UX & Interaction Principles)
遵循 Web Design Engineer 中的 **"渐进式确认 (Progressive Disclosure)"** 和反繁琐最佳实践：
- **聪明且克制**：不要抛出长篇大论的提问或冗长的 QA，严禁自说自话地把结果直接写入文档。
- **一次性确认 (One-Shot Confirmation)**：将剧情梗概、人物截图、人物名称合并在一次消息中展示，把命名权与背景检索权交给用户。

---

## 执行流程 (Workflow)

### Step 1: 调用专属脚本进行视频理解
你必须调用以下工具脚本来理解视频（不要仅依赖默认的多模态指令）：
```bash
python /home/admin/.openclaw/workspace/auto_film_maker/tools/gemini_video_understanding.py --video repo/S1_uploaded_video/<目标视频文件.mp4>
```
该脚本将返回一段 JSON 数据，包含 `plot_summary` (剧情梗概) 和 `main_characters` (主要人物正脸时间戳列表)。

### Step 2: 提取人物截图
基于 Step 1 获得的 JSON 数据，你必须调用专门的截帧脚本，将画面保存到 `repo/S2_Video_Understanding/<video_name>/faces/` 目录下：
```bash
python /home/admin/.openclaw/workspace/auto_film_maker/tools/extract_frames.py --video repo/S1_uploaded_video/<目标视频文件.mp4> --out_dir repo/S2_Video_Understanding/<video_name>/faces --frames '[{"name":"char1", "timestamp":"00:00:12"}]'
```

### Step 3: 向用户抛出确认信息（严禁偏离此格式！）
完成上述两步后，在 M 区聊天框中，**一字不差地严格按照以下模板结构**向用户发送确认消息。**绝对不要**在这里输出 6 点式长篇分析报告，也**绝对不要**提及文件保存路径！

```text
我已经看完了视频！视频的简要剧情如下：
[这里填入由脚本获取的简要剧情]

我提取到了 [N] 位主要人物：
🙎‍♂️ ![人物名1](/files/repo/S2_Video_Understanding/<video_name>/faces/char1.jpg) ：[人物名1] (出现在 [时间戳])
🙎‍♀️ ![人物名2](/files/repo/S2_Video_Understanding/<video_name>/faces/char2.jpg) ：[人物名2] (出现在 [时间戳])
...

请问命名是否准确，或者需要我联网搜索他们的背景设定吗？（如果你觉得没问题，回复“直接生成文档”即可）
```
> **命名规则**：利用你自身的知识储备对脚本返回的角色进行识别（例如认出是“钢铁侠”）。如果无法识别，默认为“人物1”、“人物2”等。

### Step 4: 响应用户反馈
- **如果用户要求修改或搜索**（例如：“男的叫钢铁侠，去搜一下他的剧情”）：
  1. 调用 `web_search` 工具搜索该角色的背景设定。
  2. 根据检索结果，在你的上下文中更新剧情或人物背景。
  3. **必须重复展示** 包含更新后的图片和设定的确认话术。
- **如果用户确认通过**（例如回复“直接生成文档”、“没问题”）：
  进入 Step 5。

### Step 5: 生成最终文档与结束流转
1. **只有在用户明确确认后**，才允许在 `repo/S2_Video_Understanding/<video_name>/` 目录下生成 `<video_name>.md` 文件。
2. **文档结构必须包含**：
   - `# 剧情梗概` (Plot Summary)
   - `# 场景表` (Scene List)
   - `# 人物表` (Character List - 必须包含内嵌的 `/files/...` 截图格式和检索到的设定)
3. **关键结束信号**：文档保存成功后，你**必须在回复用户的最后一行**，输出系统关键字（用于解锁UI）：
   `[STEP_2_COMPLETE]`