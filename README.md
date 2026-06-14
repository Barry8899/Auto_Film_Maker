# Auto Film Maker

## 🚀 Quick Start for Vobile Reviewers

本项目为 Agentic 应用，强依赖本地 OpenClaw 智能体环境与沙盒文件系统。
评委可以直接在沙盒终端运行以下命令，一键启动后端服务并获取公网体验链接：

```bash
cd /home/admin/.openclaw/workspace/auto_film_maker
bash start_auto_film_maker.sh
```

启动后，终端将自动配置环境并输出一个可供直接访问的公网 HTTPS 链接。

---

这是一个自动化视频制作控制台 (Control UI)。

## 项目结构
- `app.py`: FastAPI 后端服务入口
- `web_layout.html`: 前端界面模板（供后端渲染）
- `requirements.txt`: Python 依赖库列表
- `design_map.md`: 设计及 API 规划文档
- `start_auto_film_maker.sh`: 供沙盒环境使用的一键部署脚本

## 环境配置与启动 (供非沙盒环境开发者参考)

我们推荐使用 Python 的虚拟环境 (venv) 或 conda 来隔离项目依赖。以下是在本地机器上配置和启动的具体步骤：

### 1. 克隆代码库 (如果你还没有克隆)
```bash
git clone git@github.com:Barry8899/Auto_Film_Maker.git
cd Auto_Film_Maker
```

### 2. 创建并激活虚拟环境

**使用 venv (推荐):**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境 (Linux / macOS)
source venv/bin/activate

# 激活虚拟环境 (Windows CMD)
# venv\Scripts\activate
# 激活虚拟环境 (Windows PowerShell)
# .\venv\Scripts\Activate.ps1
```

**或者使用 Conda:**
```bash
conda create -n auto_film_maker python=3.10
conda activate auto_film_maker
```

### 3. 安装依赖
在激活的虚拟环境中，安装 `requirements.txt` 中列出的依赖项：
```bash
pip install -r requirements.txt
```

### 4. 启动服务
使用 uvicorn 启动 FastAPI 后端服务：
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
- `--reload`: 开发模式下，代码修改后服务会自动重启。

### 5. 访问网页
打开浏览器，访问以下地址即可看到 UI 界面：
[http://localhost:8000](http://localhost:8000)