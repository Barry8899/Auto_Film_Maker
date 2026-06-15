# Auto Film Maker

Auto Film Maker 是一个基于 OpenClaw 的 **Agentic 全自动视频生成与剪辑工作站**。
本项目通过高交互性的 IDE 风格 UI、实时的前后端协同以及智能体底层能力，将传统繁琐的视频二创过程重塑为一个高度自动化的 8 步流水线。从理解视频、构思脚本、到素材抽取、AI 扩充生成及最终混剪，全生命周期均由 AI Agent 主导，并允许用户随时介入微调。

### 🔄 八步核心管线 (8-Step Pipeline)
1. **Video Upload (视频上传)**: 支持拖拽上传或选取已有视频，系统自动进行 HLS m3u8 切片以便实时流媒体预览。
2. **Video Understanding (视频理解)**: Agent 自动截取正脸关键帧，并调用多模态大模型对剧情与人物进行深度解析，提取时间戳。
3. **Script Writing (脚本编写)**: 基于人物与情节分析，与用户对话确认风格后，自动生成三幕剧视频脚本。
4. **Content Extraction (内容提取)**: 根据脚本自动定位并切割原始视频素材，产出高精度的物理切片。
5. **Storyboarding (故事板)**: 生成结构化的 JSON 故事蓝图，规划出已有素材 (Extracted) 和需要大模型生成的素材 (To_Be_Generated)。
6. **Video Generation (视频生成)**: Agent 与用户交互，通过 Aliyun 视频生成模型 (如 wan2.6-i2v) 串行拆解并生成所有缺失的分镜视频素材。
7. **Video Editing (视频编辑)**: 根据最终版故事板，自动统一所有素材的编码格式、分辨率和帧率，并利用 FFmpeg 执行无缝合并剪辑。
8. **Review & Export (审查与导出)**: 闭环产出最终的高清成片，同步进行新功能预告与结构化用户反馈收集。

---

## 🚀 Quick Start for Vobile Reviewers

本项目为 Agentic 应用，强依赖本地 OpenClaw 智能体环境与沙盒文件系统。
为方便评委体验，服务已配置为长效稳定的公网访问链路。您可以直接通过浏览器访问以下链接（二者等效）：

- **🔗 专属体验链接 (推荐):** [https://bit.ly/vobile-auto-film-maker](https://bit.ly/vobile-auto-film-maker)
- **🌐 底层直连链接 (Ngrok):** [https://fountain-handmade-backwash.ngrok-free.dev](https://fountain-handmade-backwash.ngrok-free.dev)

> **⚠️ 注意：** 上述体验链接依赖于沙盒后台服务的持续运行。如果发现链接失效或服务意外终止，评委可以直接在沙盒终端运行以下命令，一键重新启动后端服务与公网穿透：
>
> ```bash
> cd /home/admin/.openclaw/workspace/auto_film_maker
> bash start_auto_film_maker.sh
> ```

---

## 📁 核心项目结构 (Project Structure)

整个 Auto Film Maker 的核心文件与目录架构如下：

### 核心服务层
- `app.py`: FastAPI 后端服务入口。接管文件读写 CRUD、视频转码流式下发，并桥接前端 UI 与底层 OpenClaw Agent。
- `web_layout.html`: 纯前端工作站界面。包含文件树自动刷新、代码与媒体预览热更新、Markdown 渲染、多级拖拽防抖以及与用户对话流的交互逻辑。
- `start_auto_film_maker.sh`: 供沙盒环境使用的一键部署脚本，自动清理环境、拉起后端服务并构建 Ngrok 内网穿透。
- `design_map.md`: 详尽的系统架构、API 规划、以及各阶段 Agent 执行交互的底层逻辑说明文档。

### 业务与智能体逻辑层
- `repo/`: **核心业务存储区**。严格按照 8 步管线划分目录结构。存放了所有的物理视频切片、`storyboard.json` 蓝图、`features.json` 状态以及 `final_video.mp4` 最终成片。
- `skills/`: **Agent 专属技能目录**。包含了 S2 至 S8 各个阶段的 `SKILL.md`，定义了 Agent 在每个流程节点应该遵循的指令规则、约束限制、跳过逻辑以及对外工具调用方式。
- `tools/`: **工具链脚本区**。供 Agent 或系统后端自动调用的 Python 物理执行器。包含了如 `ffmpeg` 高清截帧、视频裁剪组装、大模型 API 交互以及时区对齐的反馈收集工具等。
- `chats/`: 对话状态池。通过 JSON 持久化保存每个视频项目独立的会话记录，以支持系统在重启或多开场景下的无缝状态恢复。
- `user_feedbacks.json`: 结构化用户反馈存储文件。收集在 S8 阶段用户留下的评语。
- `vobile_logo_new.png`: 界面渲染所使用的 Vobile 品牌视觉资源。