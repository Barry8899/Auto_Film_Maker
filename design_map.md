# Auto Film Maker - 前端设计与架构蓝图 (Design Map)

> 状态：视频生成流接入万象引擎 (Phase 4.1)
> 最后更新：2026-06-09 (优化版)

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
- **Monaco 换行支持**: 全局开启了 `wordWrap: "on"`，现在在编辑 markdown、json 或长文本代码时，会自动根据 M 区面板宽度进行折行，再也不需要频繁横向滚动。
- **保存性能与异步优化**: 修复了之前 `Ctrl+S` 时阻塞事件循环导致的缓慢问题。将后端的 `PUT /api/fs/file` 路由升级为 `async def` 异步非阻塞处理，同时规范了前端 Monaco 编辑器的事件节流与快捷键接管，极大地提升了保存大文件或长文档时的响应速度（从 15s 级降低到毫秒级）。
- **根目录上传修复**: 修复了 L 区由于参数映射异常导致的 `Failed to fetch` 根目录文件上传错误。统一了前后端的路径缺省逻辑（`path='.'`）。
- **HLS 视频流切片播放 (M3U8)**: 彻底解决了公网穿透/弱网环境下播放 MP4 的卡顿问题。
  - **后端 (FastAPI BackgroundTasks + ffmpeg)**: 监听 `repo/S1_uploaded_video` 路径，当用户上传视频后，立刻触发后台静默转码。利用 ffmpeg (`-preset ultrafast`) 将长视频切分为 `.m3u8` 索引与数个极小的 `.ts` 切片，并存入新建的同名 `_hls` 文件夹中。
  - **前端 (HLS.js)**: M区多态容器新增对 `.m3u8` 文件的深度识别与拦截。当用户在左侧 Explorer 点击 `.m3u8` 时，采用 `hls.js` 劫持并注入原生 `<video>`，实现毫秒级秒开和边下边播的流媒体体验，完全规避了传统 MP4 必须预加载大量文件头的带宽瓶颈。

### 3.7 工具执行动态 UI 与会话管理 (Tool UI & Session Management)
- **工具执行动态 UI**: 发送消息后，采用拟物化组件 (`Tool Exec Container`) 呈现工具调用状态。外层统一显示为 `1 skill exec running` 以保证布局整齐，折叠面板内动态展示真实调用的 Skill 与 Tool 名称及正在执行的具体操作内容。
- **L区聊天历史安全删除**: 对话记录增加防误触的红色悬停删除按钮（Hover 显示），并且后端绑定同步删除物理存储的 `.json` 记录，保证空间整洁。
- **超长任务断连保护 (Long-running Timeout UX)**: 针对 Gemini 视频理解等耗时极长的任务导致的 `Failed to fetch` 代理中断报错，前端加入了友好的断连保护 UI。不再抛出刺眼的红字错误，而是以品牌橙色温和提示用户“任务仍在后台运行，请稍后刷新对话”，极大缓解了用户的焦虑感。


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
- 管线遵循**渐进式披露 (Progressive Disclosure)** 的设计原则。初始状态下，只有 **Step 1 (Video Upload)** 处于激活状态，并以 Vobile 品牌橙色 (`#F15A24`) 高亮，其余步骤处于暗色/禁用状态。
- **上传弹窗 (Upload Modal) 增强:** 点击 Step 1 会在屏幕中央弹出一个定制的 Modal 覆盖层，而不是干瘪的系统文件选择器。它包含一个支持拖拽风格的浏览区，选择文件后会以绿勾图标确认，并提供一个带有加载动画的“Upload File”按钮。
- **已有视频复用逻辑 (Existing Video Bypass):** 上传弹窗内包含一个 "Use Existing Videos" 按钮。点击后，系统会扫描 `repo/S1_uploaded_video` 目录。如果该目录下已经存在视频文件，则跳过上传流程。
- **自动会话初始化 (Zero-Friction Chat Init)**: 修复了用户在点击管线按钮或上传视频时，由于未建立聊天室而导致的阻断弹窗 (`Please select or create a chat first`)。系统会智能检测当前是否选中了会话；如果没有，会自动创建/加载一个名为 `🎬 video_maker` 的专属会话。
- **双语握手协议 (Bilingual Handshake Protocol)**: S1完成后不再粗暴弹窗，而是通过注入 `(System) 视频上传完成...` 的双语破冰消息，引导用户自然输入偏好语言（如"中文"或"Continue"）。
  - **性能优化 (Skip Agent Boot)**: 为了避免一句简单的 "继续" 导致底层 OpenClaw Agent 进行耗时极长（30s+）的冷启动推理，我们在前后端通信中引入了 `skip_agent` 标记拦截器。对于这步纯流程性的握手，直接跳过模型推断、秒级写入聊天历史并模拟出 System 确认，实现毫秒级解锁 S2 与唤起弹窗，彻底消除卡顿感。
- **Agent 执行状态 UI 优化**: 重新打磨了拟物化工具调用框 (`Tool Exec Container`) 的尺寸。移除了默认的全宽拉伸和自动间距，采用 `width: fit-content` 以及严格限定的高宽图标 (`14px`)，避免了黑框过大、中间文字空洞的问题，整体视觉更加紧凑专业。

**Step 2 (Video Understanding) 交互机制:**
- **触发与 UI 承载**: 点击 Step 2 后，前端自动向 M 区聊天框发送 `Run Video Understanding` 指令。视频人物截图作为 Markdown 附件 (`![name](/files/...)`) 直接渲染在现有的 M 区聊天流中。Markdown 解析已修复，支持保留原生的换行符和空行，保证阅读体验。
- **渐进式确认 (Progressive Disclosure) 与一次性确认 (One-Shot Confirmation)**: Agent 自动调用 Gemini 提取视频情节和主要角色时间戳，利用专用的 `tools/extract_frames.py` 工具静默截取正脸帧，并在聊天框**一次性抛出**“简要剧情 + 带图的人物表”。避免冗长的分批次问答带来的用户疲劳 (HITL Fatigue)。
- **精准的 JSON 握手截帧**: `gemini_video_understanding.py` 现在会生成结构化的 JSON 数据（包含准确的 `time_stamp` 和 `source_video` 路径）。`extract_frames.py` 直接读取该 JSON 文件，使用 `ffmpeg -y -ss <timestamp> -i <video>` 实现**高精度的准确截帧**，解决了此前截取到错位帧或无效画面的痛点。
- **语言自适应**: 尽管底层 `SKILL.md` 的系统指令为统一的英文，但规定了 Agent **必须跟随用户输入的语言**进行回答与文档编写，保证用户界面的亲和力。
- **动态搜索与完成流转**: 赋予用户修改命名或要求 Agent 进行 Web Search（背景设定检索）的权限。一切确认无误后，Agent 将包含图文的最终内容写入 `repo/S2_Video_Understanding/<video_name>/<video_name>.md` 文档。
- **无缝流转 (S2 -> S3)**：改变了原来依靠用户手动点击下一步的割裂感。当用户针对报告回复“进入下一阶段”后，Agent 才会打出隐式信号 `[STEP_2_COMPLETE]`。前端 JS 拦截该信号后自动将 Step 2 标记为完成（绿勾），点亮 Step 3，**并静默在后台为用户发送 `[TRIGGER: S3_Script_Writing]` 指令**，瞬间无缝唤起 S3 技能，开启对话流。

### 3.9 UX/DX 体验细节打磨 (UX & Developer Experience Refinements)
- **L区文件树状态保持 (State Preservation)**：修复了 L 区由于 CRUD 操作（增删改文件）或长连刷新导致目录树全部折叠的问题。引入了 `expandedFolders` 状态集 (Set) 并在重绘 DOM 前采集路径映射，实现了重新拉取文件树时**完全还原用户的多级展开状态**，极大地提升了查看深层嵌套文件（如 `/repo/S2/...`）的便利性。
- **S2 Prompt 幻觉修复**：更新了 `gemini_video_understanding.py` 的提示词。增加并明确了 `Character inclusion rules`（强制排除群演和路人）与 `Timestamp rules`（必须提取正面清晰首帧），提升了 JSON 截帧输出的稳定性和准确率。

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
- **一致性同步 (JSON ↔ MD)**: 引入了 `sync_storyboard.py` 工具。Agent 只负责维护底层的 `storyboard.json` 蓝图结构，保存后通过该脚本强制解析并输出精美的 `storyboard.md` 表格供用户在前端 M 区审核。完美规避了 LLM 直接生成 Markdown 表格时因换行错乱导致的排版崩溃问题。
- **轨道分离与非破坏性裁剪 (Non-destructive trimming)**: JSON 结构被拆分为 `Visual Track` 和 `Audio Track`。对于存在冗余或噪音的旧素材，摒弃了“重新剪切 MP4”的重负载思路，而是引入了 `trim_start` 和 `trim_end` 标记参数。这些轻量级标记将在 S7 (最终剪切) 中指导 FFmpeg 进行毫秒级去噪过滤。
- **单向数据流与 S6 的蓝图预埋**: 彻底消灭“系统循环依赖”。在 Visual Track 中，资产被划分为两类：
  1. `EXTRACTED`: 直接引用 S4 生成好的本地资产 `seg_001.mp4`。
  2. `TO_BE_GENERATED`: 对于需要二创或原片没有的情节，只在蓝图里留下初步的内容方向坑位。
  **S6 (Video Generation) 开发预览**: S6 被定性为“加工厂”。它不会去修改 S5 的蓝图，而是只负责遍历 `storyboard.json` 中所有 `TO_BE_GENERATED` 的项，创建 `asset_manifest.json`。在 S6 阶段，AI 核心任务是陪伴用户进行“找参考 -> 定 Prompt -> 生成 -> 抽卡 -> 定稿”的互动循环。在这个过程中确定的参考图、参考视频和最终生成的视频产物路径都会记录在独立的 `asset_manifest.json` 中。
  - **异步生成与前端 Toast 通知 (Async Generation & UI Toast)**：为防止由于耗时过长导致用户阻塞，Agent 会将 `aliyun_video_generation.py` 置于后台异步运行。与此同时，前端会静默轮询 `asset_manifest.json` 的更新。当某个镜头状态变为 `completed` 时，前端界面右上角会弹出带有关闭按钮【X】的绿色 Toast 通知（`✅ Shot_X 视频已生成完成`），左侧文件树也会实时打上状态微标。从而将 S5 的结构设计和 S6 的生产填坑完美隔离。最终在 S7 环节将 S5(蓝图) 和 S6(资产映射表) 合并，完成自动混剪。

## 3.11 S6 视频生成 (Sub-clip 拆解架构)
考虑到阿里云视频生成 API 的物理限制（单次最多 15s 且只能使用一张参考图），S6 阶段引入了 **Sub-clip (子片段) 拆解架构**：
- **版权保护与 Prompt 泛化**：受限于阿里云的版权保护策略，Agent 在生成 Prompt 时，必须将具体的影视剧人物（如美国队长、托尼·斯塔克）替换为泛化描述（如“这个男人”、“身穿红蓝色战甲的超级英雄”）。
- **强制用户确认机制**：为了避免 Agent 在 `asset_manifest.json` 刚填完就擅自开始消耗昂贵的生成额度，S6 的流程被强加上了一道“锁”：在正式调用后台生成脚本之前，必须主动询问用户是否准备好开始生成。用户许可后才执行。
- **独立日志追踪**：每个生成任务的日志会精确记录在对应的 `<shot_id>_<sub_clip_id>.log` 文件中，并采用追加模式，便于多次抽卡时的排错追溯。
- **嵌套数据结构**: `asset_manifest.json` 从扁平的 shot 列表升级为嵌套结构。每个 Shot 包含一个 `sub_clips` 数组。对于复杂或超长的 Shot，Agent 会与用户沟通一个“拆分方案”，并将其裂变为多个子片段（如 `sub_clip_id: 1`, `sub_clip_id: 2`）。

## 3.12 S7 视频混剪拼装 (Video Editing)
S7 负责收集所有环节准备完毕的视频素材，进行结构化合并：
- **生成融合映射表**: 提取 S5 的 `storyboard.json` 蓝图结构，结合 S6 的 `asset_manifest.json` 生成结果，打平梳理出包含所有单片段的统一序列文件 `shot_flow.json`，包含了绝对路径、`trim_start`、`trim_end` 等剪辑参数。
- **安全拦截与人工校验**: 生成 JSON 后，强制中断流程，AI 需将打平后的剪辑参数呈现给用户，只有用户手动确认修剪片段准确无误后，方可触发 FFmpeg。
- **兼容性格式化组装**: 由于原片素材(S4提取)和生成的AI素材(S6)在编码、分辨率和帧率上往往不一致，直接硬连会报错。S7 后台拼装脚本会动态利用 FFmpeg 将所有素材进行二次转码和中心裁剪补黑填充，归一化为 1080P/30FPS/x264/aac 的标准流文件，从而安全输出终版成片 `final_video.mp4`。
- **执行顺序解耦 (Agent -> JSON -> Script -> Agent)**：
  1. Agent 与用户沟通提示词和参考图。
  2. 达成一致后，Agent **优先修改** `asset_manifest.json`，将数据填入坑位。
  3. Agent 串行调用底层脚本 `aliyun_video_generation.py`，传入具体的 `shot_id` 和 `sub_clip_id`。
  4. 脚本直接读取 JSON 内部指定的提示词和路径执行生成。
  5. 脚本生成成功后回写 JSON 状态。
  6. Agent 轮询到状态完成，向用户发送提示进行审核。
- **强制逐一审核**: 为保证成片质量并避免并行 API 竞争，同一个 Shot 下的多个子片段必须**串行生成并逐一审核**。用户对片段 1 满意后，Agent 才会发起片段 2 的生成调用。
- **思维链打点与切割 (CoT & Clipping)**：底层使用带有强 System Prompt 的 Gemini 脚本定位素材。强制输出 `reasoning` (思维链) 字段。
- **幂等与防并发锁 (Idempotency & Execution Lock)**：由于公网代理（如 Pinggy / Nginx）在遇到长耗时任务（如 Gemini 分析视频需 60s+）时，会在超时后自动重发 POST 请求。这会导致 Agent 被二次唤醒，从而产生“用户幽灵发言”（两次 `嗯嗯继续`）并错乱工作流状态。目前已在 `app.py` 中加入了线程级别的请求锁 (`chat_locks`)，遇到重发的并发请求直接返回 409 拦截，彻底根治了公网弱网环境下的 Agent 鬼畜抢跑问题。
- **Dashboard 级验收面板 (防卡顿超链接设计)**：为了防止多个切片视频在 M 区聊天框内直接渲染造成“多媒体轰炸”与浏览器卡死，裁剪完成后输出一个优雅的 `extraction_report.md`。Agent 会将 Markdown 表格直接输出在聊天流中，但**坚决避免**嵌入 `<video>` 或 `![vid]()`，而是采用文字超链接 `[👉 点击预览](/files/...)`，让用户像审阅 Dashboard 一样按需点击、集中验收。
- **无缝流转 (S4 -> S5)**：切片阶段并经用户同意后，S4 抛出 `[STEP_4_COMPLETE]`。前端拦截该信号，点亮 Step 5，并静默发送 `[TRIGGER: S5_Storyboarding]` 唤醒 S5 技能 (Storyboarding)。

## 3.13 S8 审查与导出 (Review & Export)
S8 是工作流的终点，主要负责闭环体验与反馈收集：
- **无缝衔接 (S7 -> S8)**: 当 S7 最终视频 `final_video.mp4` 拼装完毕且用户无修改意见时，Agent 输出 `[STEP_7_COMPLETE]`。前端将 S7 管线变暗，点亮 S8 管线，并后台隐式触发 `[TRIGGER: S8_Review_Export]`。
- **成片交付与功能预告**: Agent 首先在一个消息流中完成三件事：
  1. 指引用户在中间工作区 (M区) 预览成片，并在左侧目录树 (L区) 下载。
  2. 预告即将上线的“自动宣发文案”和“一键分发 YouTube / Bilibili”等高级功能 (Coming Soon)。
  3. 宣布当前制作流程圆满结束，并感谢用户。
- **全局反馈收集 (Global Feedback Collection)**: 鼓励用户对生成的视频或整个 Workflow 提出建议。当用户提出反馈后，Agent 会引导明确、润色，并将结构化的数据（带时间戳的 `timestamp` 与 `feedback` 字段）自动追加写入项目根目录的 `/home/admin/.openclaw/workspace/auto_film_maker/user_feedbacks.json` 文件中，为后续的流程迭代与模型调优提供数据支撑。
