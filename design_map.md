# Auto Film Maker - 前端设计与架构蓝图 (Design Map)

> 状态：M区真机联动与公网代理 (Phase 4)
> 最后更新：2026-05-25 (优化版)

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

## 5. 设计系统规范 (Design System Declaration)
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
- **工具调用拟物化组件**: 发送消息后，采用可折叠的工具调用组件 (`Tool Exec Container`) 代替纯文本日志，精确匹配原生 OpenClaw 的交互心智（`▶ [🔧扳手图标] 1 tool exec ... running`）。
- **L区聊天历史安全删除**: 对话记录增加防误触的红色悬停删除按钮（Hover 显示），并且后端绑定同步删除物理存储的 `.json` 记录，保证空间整洁。


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
- **已有视频复用逻辑 (Existing Video Bypass):** 上传弹窗内包含一个 "Use Existing Videos" 按钮。点击后，系统会扫描 `repo/S1_uploaded_video` 目录。如果该目录下已经存在视频文件，则跳过上传流程，直接解锁 Step 2，并在聊天框打印系统成功消息。如果不存在视频文件，则弹出错误提示并阻断跳转。
- **自动会话初始化 (Zero-Friction Chat Init)**: 修复了用户在点击管线按钮或上传视频时，由于未建立聊天室而导致的阻断弹窗 (`Please select or create a chat first`)。现在，当用户执行任何需要与 Agent 交互的操作时，系统会智能检测当前是否选中了会话；如果没有，会自动加载最近的会话，或者静默创建一个名为 `Production Pipeline` 的专属会话，保证生产管线的沉浸感与无缝衔接。
- 当上传完成（或复用成功）后，Modal 自动关闭，Step 1 会变成绿色完成状态，并**自动点亮 Step 2**，无缝引导用户进入下一环节。所有上传的视频文件会被直接路由保存至 `repo/S1_uploaded_video/` 目录下。

**Step 2 (Video Understanding) 交互机制:**
- **触发与 UI 承载**: 点击 Step 2 后，前端自动向 M 区聊天框发送 `Run Video Understanding` 指令。视频人物截图作为 Markdown 附件 (`![name](/files/...)`) 直接渲染在现有的 M 区聊天流中。
- **渐进式确认 (Progressive Disclosure) 与一次性确认 (One-Shot Confirmation)**: Agent 自动调用 Gemini 提取视频情节和主要角色时间戳，利用专用的 `tools/extract_frames.py` 工具静默截取正脸帧，并在聊天框**一次性抛出**“简要剧情 + 带图的人物表”。避免冗长的分批次问答带来的用户疲劳 (HITL Fatigue)。
- **动态搜索与完成流转**: 赋予用户修改命名或要求 Agent 进行 Web Search（背景设定检索）的权限。一切确认无误后，Agent 将包含图文的最终内容写入 `repo/S2_Video_Understanding/<video_name>/<video_name>.md` 文档，并在消息末尾抛出 `[STEP_2_COMPLETE]` 信号，前端 JS 拦截该信号后自动将 Step 2 标记为完成（绿勾）并点亮 Step 3。
