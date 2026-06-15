# Auto Film Maker - 前端设计与架构蓝图 (Design Map)

> 状态：视频生成流接入万象引擎 (Phase 4.1)
> 最后更新：2026-06-15 (架构总览与体验优化版)

## 1. 项目概述
“Auto Film Maker”是一个自动理解视频并进行二次创作的 AI 平台。前端页面采用高度集成的 IDE / 工作站式布局，整合了 AI 智能体对话、本地文件管理、代码/文本/媒体编辑预览、以及视频生成生命周期追踪。

## 2. 技术栈架构 (Tech Stack)
本项目目前已从纯静态 HTML 升级为带后端的全栈服务，并正式接入 OpenClaw 本地代理核心：
- **后端 (Backend)**: `FastAPI` + `Uvicorn` + `Pydantic`。负责处理文件系统的 API 路由以及静态资源（媒体）的挂载。
- **大脑 (Agent Core)**: 桥接 `openclaw agent` 命令。在 M 区的每一次对话，均通过 `subprocess` 底层真实唤起 OpenClaw Agent (并注入 `--session-id`)。这意味着前端 M 区不仅是聊天框，更直接具备了服务器所在工作区（`/home/admin/.openclaw/workspace/`）的**文件读写、环境控制和 Skill 调度权限**。
- **前端 (Frontend)**: 原生 HTML/CSS/JS + `Monaco Editor` (通过 CDN 引入)。不依赖繁重的打包框架，追求轻量级与快速响应。
- **通信**: 基于 RESTful API 进行前后端数据交换与文件流传输。公网代理通过 `Pinggy`（内网穿透）等工具生成 HTTPS 链接对外发布。

---

## 3. 空间布局系统 (Space Architecture)
整体视窗锁定为 **100vh** (全屏) 的桌面端工作站布局。
水平方向采用 **可动态调整宽度的三栏栅格系统 (CSS Grid)**，初始比例为 **3 : 10 : 3**。

### 3.1 动态伸缩控制器 (Resizer)
- L 区与 M 区之间存在拖拽分割线。
- L 区最小宽度限制为 0（即完全折叠隐藏）。
- L 区最大宽度限制为屏幕总宽度的 5/16（即 L 与 M 的比例极值限制在 5:8），确保 M 区永远有充足的工作空间。R区宽度始终固定。

### 3.2 左侧边栏 (L区) - 资源与历史
- **上部 - 对话管理 (Chat History)**：管理 AI 对话会话（每个会话独立保留 json 记录，结合 OpenClaw agent session-id 实现上下文隔离）。
- **下部 - 工作区文件树 (File Explorer)**：
  - 映射真实的本地路径：`/home/admin/.openclaw/workspace/auto_film_maker`
  - **动态响应布局**: 无论文件名多长，均会被 `...` 截断，绝对不撑破左侧边栏。
  - **文件夹状态系统**: VSCode 风格的 `>` 与 `v` 展开/收起提示箭头。
  - **全套 CRUD 交互**: 支持右键/悬浮动作栏，进行文件的 **新建**、**重命名**、**下载**、**删除**。
  - **拖拽与上传**: 支持顶部直接点击上传文件 (`python-multipart`)；支持在目录树内通过鼠标拖拽（Drag & Drop）进行文件/文件夹的移动。


### 3.3 中间主工作区 (M区) - 核心交互区
采用 **标签页 (Tabs) + 多态容器** 逻辑：
- **标签系统**: 选中的文件在顶部生成可关闭的 Tab。如果文件被编辑但未保存，Tab 标题旁会显示 **VSCode 风格的未保存白点**。
  - **弹性挤压处理**: 当 Tab 数量较多时，标签自动按照 `flex: 0 1 auto` 弹性挤压，超出文字部分变为省略号 `...`，并保证不会挤占任何 L 区的空间。
  - **无缝切换与路由绑定**: 所有对话与文件复用同一个 Tab 系统，高度对齐现代 IDE 的心智模型。
- **多态容器路由**:
  1. **代码编辑器 (Monaco)**: 遇到文本/代码/配置类文件时，注入 Monaco 实例，支持语法高亮与 `Ctrl+S` 保存。
  2. **媒体阅览器 (Media Viewer)**: 遇到图片 (`jpg`, `png`, `gif`) 或视频 (`mp4`, `webm`) 文件时，利用 FastAPI 挂载的 `/files` 静态路由，直接以原生 `<video>` 或 `<img>` 标签在 M 区全比例内嵌播放/阅览。
  3. **对话面板 (Chat)**: 执行 AI 交互指令的地方。已通过后端真实对接 OpenClaw Agent。

### 3.4 右侧边栏 (R区) - 生产力流转条
采用 **垂直时间线 (Vertical Timeline)** 设计：
- 视觉呈现：左侧贯穿轴线与状态节点，右侧辅以步骤说明文本，用来监控全流程自动出片的 8 个生命周期进度。

---

## 4. 后端 API 路由清单 (API Routes)
- `GET /` : 渲染主页面 `web_layout.html`
- `GET /api/fs/tree` : 获取当前工作区文件目录树（排除了 `.git`, `venv`, `__pycache__` 等无用目录）。
- `GET /api/fs/file?path=...` : 读取指定文本文件内容。
- `PUT /api/fs/file?path=...` : 保存编辑器中修改的文件内容。
- `POST /api/fs/create` : 创建新的文件或文件夹。
- `POST /api/fs/rename` : 重命名文件或文件夹。
- `DELETE /api/fs/delete` : 删除文件或文件夹（递归）。
- `POST /api/fs/upload` : 表单上传本地文件到工作区指定位置。
- `POST /api/fs/move` : 用于拖拽时移动文件路径的逻辑映射与防覆盖保护。
- `GET /api/fs/download?path=...` : 返回文件数据流用于浏览器下载。
- **静态挂载**: `/files` -> 映射到工作区根目录用于媒体直接加载。
- **对话路由**: `/api/chat/{chat_id}/message` -> 桥接执行 `openclaw agent --session-id {chat_id} --message {data.content} --json`，实现了浏览器前端直接命令底层 AI 代理能力的闭环。

---

## 5. 项目技能与工具集成规范 (Skill & Tool Architecture)
为了解决与 OpenClaw 默认环境配置冲突的问题（例如 `gemini-video-understanding`），本项目确立了以下技能与工具管理规范：
- **项目级独立化**: 本项目专属的 Pipeline 技能（`S2_Video_Understanding`、`S3_Script_Writing` 等）统一存放在 `auto_film_maker/skills/` 目录下。相关支持脚本统一存放于 `auto_film_maker/tools/` 下。
- **软链接注入**: 避免全局环境污染。在运行时或部署时，将 `auto_film_maker/skills/` 下的专属技能通过软链接（`ln -s`）挂载到 OpenClaw 的 `~/.openclaw/workspace/skills/` 中。
- **降级与替换**: 如果原 OpenClaw 环境中存在功能冲突的旧技能，本项目推荐直接在宿主工作区中移除（或重命名），由本项目的结构化 Pipeline 技能完全接管。例如，完全使用 `S2_Video_Understanding` 替代原有的 `gemini-video-understanding`。
- **触发隐式化**: M 区向 Agent 发送触发消息时，采用纯净路由指令（如 `[TRIGGER: S2_Video_Understanding] repo/S1_...`），将冗长的格式限制和行为约束全部后置并收敛于对应的 `SKILL.md` 内，保证用户聊天框界面的极简与专业。
*（沿用 Phase 2 的色值与字体设计系统，并拓展了交互细节的设计）*
- 交互反馈增强：所有悬浮操作按钮增加放大过渡效果（Scale）与阴影，拖拽操作增加虚线边框与半透颜色填充，提升专业软件操控手感。

### 3.5 交互细节优化 (UI/UX Refinements)
1. **上传阻断机制**: M 区回形针上传文件后，不再自动触发消息发送，而是将 `[Attached file: ...]` 路径以文本形式附加到输入框，等待用户补充 Prompt 后手动发送。
2. **AI 思考态渲染 (Streaming UX)**: 
   - 增加动态思考动画 (`Lobster 思考中...`) 与模拟的工具调用框 (`Tool Box`)。
   - 在等待底层 OpenClaw Agent 执行（常需几秒到十几秒）的过程中，为用户提供渐进式的工具调用视觉反馈。
3. **Vobile 品牌植入**: 替换了默认的 AI 助手头像，改为 Vobile 的品牌主色调与 Logo（通过 CSS SVG 实现），强化了平台的专属感。

##
### 3.6 性能与编辑器优化 (Performance & Editor Enhancements)
- **Monaco 换行支持**: 全局开启了 `wordWrap: "on"`，在编辑 markdown、json 或长文本代码时，会自动根据 M 区面板宽度进行折行。
- **保存性能与异步优化**: 将后端的 `PUT /api/fs/file` 路由升级为 `async def` 异步非阻塞处理，规范了前端 Monaco 编辑器的事件节流与快捷键接管，极大地提升了保存响应速度。
- **HLS 视频流切片播放 (M3U8)**: 实现了公网穿透/弱网环境下播放 MP4 的秒开支持。
  - **后端 (FastAPI BackgroundTasks + ffmpeg)**: 监听视频上传，立刻触发后台静默转码。利用 ffmpeg 将长视频切分为 `.m3u8` 索引与 `.ts` 切片。
  - **前端 (HLS.js)**: M区新增对 `.m3u8` 的深度识别与拦截。采用 `hls.js` 劫持并注入原生 `<video>`，实现边下边播的流媒体体验，规避预加载瓶颈。

### 3.7 工具执行动态 UI 与会话管理 (Tool UI & Session Management)
- **工具执行动态 UI**: 采用拟物化组件 (`Tool Exec Container`) 呈现工具调用状态。折叠面板内动态展示真实调用的 Skill 与 Tool 名称及操作内容。
- **L区聊天历史管理**: 对话记录支持安全删除，后端同步删除物理存储记录。支持根据加载的聊天历史智能还原右侧管线 (Pipeline) 的进度高亮状态。
- **多项目并发 (Session Isolation)**: S1 结束后，自动生成带编号的专属 `🎬 video_maker_X` 隔离会话，实现工作站内多视频项目的并行管理与进度自由切换。
- **长时任务断连保护 (Timeout UX)**: 针对大模型分析等耗时极长的任务，前端加入了友好的状态保持与断连保护机制。


## 3.8 右侧边栏 (R区) 导航更新与管线 (Pipeline)
在右侧边栏引入了由上至下的 8 步垂直生产管线 (Production Pipeline)：
1. Video Upload (视频上传)
2. Video Understanding (视频理解)
3. Script Writing (脚本编写)
4. Content Extraction (内容提取)
5. Storyboarding (故事板)
6. Video Generation (视频生成)
7. Video Editing (视频编辑)
8. Review & Export (审查与导出)

**管线交互 (Pipeline UX) 与 Vobile 品牌对齐:**
- 管线遵循**渐进式披露 (Progressive Disclosure)** 的设计原则。初始状态下，只有 **Step 1 (Video Upload)** 处于激活状态，并以 Vobile 品牌橙色 (`#F15A24`) 高亮。同时 M 区提供友好的欢迎大屏 (Welcome State)。
- **双语握手协议 (Bilingual Handshake Protocol)**: S1完成后通过注入 `(System)` 级的双语破冰消息，引导用户自然输入偏好语言，并零阻力 (Zero-Friction) 唤起 S2 工具。

**Step 2 (Video Understanding) 交互机制:**
- **触发与 UI 承载**: 点击 Step 2 后，前端自动向 M 区聊天框发送 `Run Video Understanding` 指令。视频人物截图作为 Markdown 附件 (`![name](/files/...)`) 直接渲染在现有的 M 区聊天流中。Markdown 解析已修复，支持保留原生的换行符和空行，保证阅读体验。
- **渐进式确认与一次性渲染**: Agent 自动调用多模态模型提取视频情节和主要角色时间戳，利用底层工具静默截取正脸帧，并在聊天框**一次性抛出**“剧情 + 人物表”。避免冗长的分批次问答带来的用户疲劳 (HITL Fatigue)。
- **精准的 JSON 握手截帧**: Agent 生成结构化的 JSON 数据（包含时间戳）。截帧脚本读取 JSON 并实现**高精度的准确截帧**。
- **语言自适应**: 尽管底层 `SKILL.md` 的系统指令为统一的英文，但规定了 Agent **必须跟随用户输入的语言**进行回答与文档编写，保证用户界面的亲和力。
- **动态搜索与完成流转**: 赋予用户修改命名或要求 Agent 进行 Web Search（背景设定检索）的权限。一切确认无误后，Agent 将包含图文的最终内容写入 `repo/S2_Video_Understanding/<video_name>/<video_name>.md` 文档。
- **无缝流转 (S2 -> S3)**：改变了原来依靠用户手动点击下一步的割裂感。当用户针对报告回复“进入下一阶段”后，Agent 才会打出隐式信号 `[STEP_2_COMPLETE]`。前端 JS 拦截该信号后自动将 Step 2 标记为完成（绿勾），点亮 Step 3，**并静默在后台为用户发送 `[TRIGGER: S3_Script_Writing]` 指令**，瞬间无缝唤起 S3 技能，开启对话流。

### 3.9 UX/DX 体验细节打磨 (UX & Developer Experience Refinements)
- **L区文件树状态保持**: 采集路径映射，实现了重新拉取文件树时**完全还原用户的多级展开状态**。
- **Prompt 防幻觉优化**: 明确了强制排除群演和路人等设定，提升了 JSON 截帧输出的稳定性和准确率。

**Step 3 (Script Writing) 交互机制:**
- **消除白纸综合征 (Direction Advisor)**：被静默唤起后，Agent 不会像填表一样盘问用户，而是主动根据 S2 剧情，抛出 2~3 种带有明显差异的风格预案（如高燃快剪、治愈回忆），引导用户做选择题。
- **五维特征采集 (Phase 1)**：在对话中不断采集并更新 `style`, `emotion_curve`, `pacing`, `aesthetic`, `duration` 五个维度，直至全部明确并落盘至 `features.json`。
- **三幕剧大纲构思 (Phase 2)**：基于特征 JSON 和素材，自动撰写包含 Logline、节奏策略、人物弧光和三幕剧结构的 `script.md`。经过和用户的多轮对话修改直至确认。
- **无缝流转 (S3 -> S4)**：大纲定稿后，系统再次发起确认询问。用户同意后抛出 `[STEP_3_COMPLETE]`，利用同样的静默拦截机制瞬间点亮并唤醒 S4 环节 (Content Extraction)。

**Step 4 (Content Extraction) 交互机制:**
- **消除白纸综合征 (V0 Draft Push)**：Agent 被静默唤醒后，直接在后台读取 S3 的 `features.json` 和 `script.md`，不再用空洞的问题盘问用户，而是直接生成一份“三层结构”（通用元素、类型专属、IP专属）的待抽取清单初稿 (`extract_content.md`) 推送给用户。
- **防幻觉上下文注入与语言强制 (Context & Language Injection)**：推送完清单初稿后，Agent 顺势向用户索要 `supplement_infos`。同时在底层调用 `gemini_content_extraction.py` 时，强制传入 `--lang` 参数（如 `--lang 中文`），保证生成的 `extracted_clip_details.json` 内部的时间戳解释（Reasoning/Description）严格遵循用户语言，杜绝中英夹杂。
- **全链路复用与跳过机制 (Bypass Logic)**：S2、S3、S4、S5 的流转环节均注入了 `Step 0` 状态检测。在环境被唤醒时，Agent 会利用绝对路径秒级侦测该阶段的最终产物（如 `data.json`、`features.json`、`extraction_report.md`、`storyboard.json`）。若存在，会引导用户一键跳过当前长耗时的计算/生成阶段，在研发测试及二次渲染时提供了极高的效率。

## 3.10 S5 (Storyboarding) 与 S6 规划
S5 (分镜表) 是衔接素材提炼与最终成片的核心枢纽。
- **一致性同步 (JSON ↔ MD)**: Agent 负责维护底层的 `storyboard.json` 分镜表结构，保存后通过同步脚本强制解析并输出精美的 `storyboard.md` 表格供用户在前端 M 区审核，规避了 LLM 直接生成 Markdown 表格时因换行错乱导致的排版崩溃问题。
- **轨道分离与非破坏性裁剪 (Non-destructive trimming)**: JSON 结构被拆分为 `Visual Track` 和 `Audio Track`。摒弃了“重新剪切 MP4”的重负载思路，引入轻量级的 `trim_start` 和 `trim_end` 标记参数，由 S7 统一指导 FFmpeg 进行修剪。
- **单向数据流与 S6 的分镜表预埋**: 资产被划分为两类：
  1. `EXTRACTED`: 直接引用 S4 生成好的本地资产。
  2. `TO_BE_GENERATED`: 仅在分镜表里留下初步的内容坑位。
  **S6 (Video Generation) 开发预览**: S6 被定性为“加工厂”。它不修改 S5 的分镜表，而是遍历 `storyboard.json` 中的坑位，在独立的 `asset_manifest.json` 中记录参考图、生成 Prompt 和物理结果路径。
  - **异步生成与前端 Toast 通知 (Async Generation & UI Toast)**：Agent 将生成脚本置于后台异步运行。前端静默轮询更新，完成后弹出绿色 Toast 通知，从而将 S5 的结构设计和 S6 的生产填坑隔离。

## 3.11 S6 视频生成 (Sub-clip 拆解架构)
考虑到视频生成 API 的物理限制，S6 阶段引入了 **Sub-clip (子片段) 拆解架构**：
- **版权保护与 Prompt 泛化**：受限于模型版权策略，Agent 在生成 Prompt 时，须将具体的影视剧人物替换为泛化描述。
- **强制用户确认机制**：在正式调用后台生成脚本消耗昂贵额度之前，S6 被加上了一道“锁”：必须主动询问用户是否准备好，用户许可后才执行。
- **独立日志追踪**：每个生成任务的日志被精确记录在追加模式的文件中，便于排错追溯。
- **嵌套数据结构**: `asset_manifest.json` 从扁平列表升级为嵌套的 `sub_clips` 数组，Agent 会与用户沟通拆分方案。

## 3.12 S7 视频混剪拼装 (Video Editing)
S7 负责收集所有环节准备完毕的视频素材，进行结构化合并：
- **生成融合映射表**: 提取 S5 的 `storyboard.json` 分镜表，结合 S6 的结果，梳理出包含所有单片段的统一序列文件 `shot_flow.json`。
- **安全拦截与人工校验**: 生成 JSON 后强制中断，AI 将参数呈现给用户，用户确认后方可触发最终混剪。
- **兼容性格式化组装**: 利用 FFmpeg 将所有素材进行二次转码和中心裁剪补黑填充，归一化为标准的 1080P 视频流，安全输出成片。
- **幂等与防并发锁 (Idempotency Lock)**：已在后端加入了线程级别的请求锁 (`chat_locks`)，彻底根治了公网重试机制下 Agent 鬼畜抢跑或被二次唤醒的问题。

## 3.13 S8 审查与导出 (Review & Export)
S8 是工作流的终点，主要负责闭环体验与反馈收集：
- **无缝衔接 (S7 -> S8)**: 当 S7 最终视频 `final_video.mp4` 拼装完毕且用户无修改意见时，Agent 输出 `[STEP_7_COMPLETE]`。前端将 S7 管线变暗，点亮 S8 管线，并后台隐式触发 `[TRIGGER: S8_Review_Export]`。
- **成片交付与功能预告**: Agent 首先在一个消息流中完成三件事：
  1. 指引用户在中间工作区 (M区) 预览成片，并在左侧目录树 (L区) 下载。
  2. 预告即将上线的“自动宣发文案”和“一键分发 YouTube / Bilibili”等高级功能 (Coming Soon)。
  3. 宣布当前制作流程圆满结束，并感谢用户。
- **全局反馈收集 (Global Feedback Collection)**: 鼓励用户对生成的视频或整个 Workflow 提出建议。当用户提出反馈后，Agent 会引导明确、润色，并将结构化的数据（带时间戳的 `timestamp` 与 `feedback` 字段）自动追加写入项目根目录的 `/home/admin/.openclaw/workspace/auto_film_maker/user_feedbacks.json` 文件中，为后续的流程迭代与模型调优提供数据支撑。
