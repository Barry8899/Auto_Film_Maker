# Auto Film Maker - 前端设计与架构蓝图 (Design Map)

> 状态：规划中阶段 (Phase 1)
> 最后更新：2026-05-19

## 1. 项目概述
“Auto Film Maker”是一个自动理解视频并进行二次创作的 AI 平台。前端页面采用高度集成的 IDE / 工作站式布局，整合了 AI 智能体对话、本地文件管理与代码/文本编辑、以及视频生成生命周期追踪。

## 2. 空间布局系统 (Space Architecture)
整体视窗锁定为 **16:9** 的桌面端工作站布局。
水平方向采用 **3 : 10 : 3** 的三栏栅格系统：

### 2.1 左侧边栏 (L区) - 资源与历史 (占宽比 3)
垂直方向分为两部分（1 : 2）：
- **上部 (1/3) - 对话管理 (Chat History)**：
  - “新建对话”功能。
  - 历史对话列表（类似 ChatGPT/Claude），使用内容标签卡片样式。
- **下部 (2/3) - 工作区文件树 (File Explorer)**：
  - 对标 VSCode 风格的文件目录。
  - 映射路径：`/home/admin/.openclaw/workspace/auto_film_maker`
  - 交互：左键单击在 M 区打开；右键唤出上下文菜单（重命名、下载、删除）；顶部操作栏（新建文件、新建文件夹）。

### 2.2 中间主工作区 (M区) - 核心交互区 (占宽比 10)
- **模式 A：编辑器模式 (File Editor)**
  - 承载 L 区点击的文件浏览与代码/文本编辑，支持保存。
- **模式 B：智能体对话模式 (Agent Chat)**
  - 承载 AI 对话流、输入框及附件上传等核心 AI 交互。
  - *(待确认：A与B是标签页共存还是互相替换？)*

### 2.3 右侧边栏 (R区) - 生产力流转条 (占宽比 3)
垂直的流程追踪器，可视化呈现当前视频创作的 8 个生命周期阶段：
1. 原片上传 (Upload)
2. 视频理解 (Analysis)
3. 内容策划 (Planning)
4. 素材抽取 (Extraction)
5. 分镜表生成 (Storyboard)
6. 新片段生成 (Generation)
7. 视频拼接 (Stitching)
8. 成片结果 (Final Output)
- **状态视觉**：未开始 (Pending) -> 进行中 (Active/Pulse) -> 已完成 (Done/Check)

---

## 3. 设计系统规范 (Design System Declaration)
> 基于 web-design-engineer 规范

### 3.1 视觉主题风格 (Vibe & Theme)
**"Cinematic Pro-Tool" (专业影视工作站风格)**
考虑到这是视频二创工具，默认采用 **深色模式 (Dark Mode)**。消除刺眼感，让用户的视觉焦点集中在视频内容和对话上，类似 Premiere Pro 或 Cursor 带来的沉浸感。严禁使用廉价的霓虹渐变和高饱和色。

### 3.2 色彩调色板 (Color Tokens - 基于 oklch)
- **Background (背景层)**: `oklch(18% 0.01 260)` - 深石板灰，比纯黑更柔和，减少眼部疲劳。
- **Surface (面板层)**: `oklch(22% 0.01 260)` - L/R 区面板的底色，与背景形成微妙层级。
- **Primary / Accent (主色调)**: `oklch(70% 0.1 230)` - 克制的青石蓝，用于激活状态、进行中的步骤、核心按钮。
- **Text (文字)**:
  - 主文本：`oklch(90% 0.01 260)` - 柔和白。
  - 次文本/注脚：`oklch(60% 0.02 260)` - 灰阶弱化信息。

### 3.3 排版与字体 (Typography)
- **UI 界面字体 (UI & Chat)**: `Plus Jakarta Sans` (清晰、现代的无衬线几何字体)。
- **代码与文件树字体 (Code & Files)**: `JetBrains Mono` (专业等宽字体，提升 IDE 区域的专业感)。
- **展示性/标题排版**: 紧凑的字距，严谨的粗细对比（避免过度使用系统默认的 Inter）。

### 3.4 图标系统 (Iconography)
- 放弃所有 Emoji。全面采用线条干净的专业 SVG 图标集 (例如 Lucide Icons)。开发前期将使用统一的 `[Icon: Name]` 占位符进行布局。

---

## 4. 待解决的工程与设计疑问 (Q&A)
*(见聊天回复)*
