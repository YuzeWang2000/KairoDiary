# KairoDiary

一个基于 PyQt6 的个人日记应用程序，提供简洁优雅的界面来记录你的日常生活。

## 项目介绍

KairoDiary 是一个功能丰富的桌面日记应用，具有以下特性：

- 🖥️ **现代界面**：基于 PyQt6 构建的美观用户界面
- 📝 **日记管理**：轻松创建、编辑和管理日记条目
- 📅 **日历视图**：通过日历界面快速查看和导航日记
- 📋 **笔记功能**：支持日记之外的笔记记录
- ✅ **待办事项**：集成任务管理功能
- 🔐 **账户系统**：安全的用户登录和数据管理
- 💾 **本地存储**：数据安全存储在本地文档目录

## 系统要求

- **操作系统**：Windows 10/11 或 macOS 10.15+
- **Python**：3.11+
- **依赖管理**：uv 包管理器

## 安装和运行

### 使用 uv 包管理器

1. **安装 uv**（如果尚未安装）：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **克隆项目并进入目录**：
```bash
git clone https://github.com/YuzeWang2000/KairoDiary.git
cd KairoDiary
```

3. **安装 Python 版本和依赖**：
```bash
uv python install
uv sync
```

4. **运行应用程序**：
```bash
uv run main.py
```

## 应用打包

### 打包为 Windows 应用程序

在 Windows 系统上，使用 PyInstaller 将应用程序打包为独立的可执行文件：

#### 前置要求
- Windows 10/11
- Python 3.11+
- uv 包管理器

#### 打包步骤

1. **克隆项目并进入目录**：
```cmd
git clone https://github.com/YuzeWang2000/KairoDiary.git
cd KairoDiary
```

2. **安装依赖**：
```cmd
uv sync
```

3. **执行打包命令**：

**方法一：使用命令行**
```cmd
uv run pyinstaller --onefile --windowed --name="KairoDiary" --icon="assets/KairoDiary.ico" --add-data="assets;assets" main.py
```

**方法二：使用 spec 文件（推荐）**
```cmd
uv run pyinstaller KairoDiary.spec
```

> **注意**：spec 文件已经配置好了所有必要的参数，包括图标和资源文件，推荐使用此方法确保任务栏图标正确显示。

4. **打包完成后**，会在 `dist/` 目录中生成 `KairoDiary.exe` 可执行文件。

5. **运行打包的应用**：
   - 双击 `dist/KairoDiary.exe` 即可运行
   - 可将 exe 文件复制到任何 Windows 系统上直接运行，无需安装 Python 环境

#### PyInstaller 参数说明
- `--onefile`：打包成单个可执行文件
- `--windowed`：不显示控制台窗口（适合 GUI 应用）
- `--name="KairoDiary"`：指定生成的文件名
- `--icon="assets/KairoDiary.ico"`：指定应用程序图标（Windows 任务栏显示）
- `--add-data="assets;assets"`：将 assets 目录打包到应用中（确保运行时图标可用）

#### 任务栏图标说明
应用程序已配置为在不同操作系统中自动选择合适的图标格式：
- **Windows**: 使用 `assets/KairoDiary.ico`
- **macOS**: 使用 `assets/KairoDiary.icns`
- **Linux**: 使用 `assets/KairoDiary.ico` 或 `assets/KairoDiary.png`

打包后的应用会在系统任务栏/Dock 中正确显示应用图标。

### 打包为 macOS 应用程序

使用 `setup.py` 可以将应用程序打包为独立的 macOS 应用：

1. **确保依赖已安装**：
```bash
uv sync
```

2. **执行打包命令**：

**方法一：使用 py2app**
```bash
uv run python setup.py py2app
```

**方法二：使用 PyInstaller（推荐，更简单）**
```bash
uv run pyinstaller --windowed --name="KairoDiary" --icon="assets/KairoDiary.icns" --add-data="assets:assets" main.py
```

> **注意**：PyInstaller 方法更简单，且会自动处理图标和依赖关系，确保应用在 Dock 中正确显示图标。

3. **打包完成后**，会在 `dist/` 目录中生成 `KairoDiary.app` 应用程序文件。

4. **运行打包的应用**：
   - 双击 `dist/KairoDiary.app` 即可运行
   - 或将应用拖拽到 `Applications` 文件夹进行安装

### 打包选项说明

**Windows (PyInstaller)**：
- **应用图标**：使用 `assets/KairoDiary.ico` 作为应用图标
- **输出格式**：单文件可执行程序（.exe）
- **依赖处理**：自动打包所有依赖，生成独立可执行文件

**macOS (py2app)**：
- **应用图标**：使用 `assets/KairoDiary.icns` 作为应用图标
- **应用名称**：KairoDiary
- **版本号**：1.0.0
- **包标识符**：com.kairosoft.kairodiary

## 图标配置说明

### 图标文件
项目包含两种格式的图标文件：
- `assets/KairoDiary.ico`：Windows 系统使用（16x16 到 256x256 多尺寸）
- `assets/KairoDiary.icns`：macOS 系统使用（16x16 到 1024x1024 多尺寸）

### 自动图标选择
应用程序在运行时会自动根据操作系统选择合适的图标：
```python
# Windows: 使用 .ico 文件
# macOS: 使用 .icns 文件  
# Linux: 优先使用 .ico，备选 .png
```

### 打包时图标处理
- **PyInstaller**: 使用 `--icon` 参数指定编译时图标，使用 `--add-data` 确保运行时图标可用
- **py2app**: 在 setup.py 中通过 `iconfile` 参数配置图标
- **任务栏显示**: 打包后的应用会在系统任务栏/Dock 中正确显示应用图标

## 项目结构

```
KairoDiary/
├── main.py                 # 应用程序入口
├── setup.py               # macOS 打包配置文件
├── pyproject.toml         # 项目配置和依赖
├── uv.lock               # 依赖锁定文件
├── .python-version       # Python 版本指定
├── assets/               # 资源文件
│   ├── KairoDiary.icns  # macOS 应用图标
│   └── KairoDiary.ico   # Windows 应用图标
└── core/                # 核心模块
    ├── components/      # UI 组件
    │   ├── calendarView.py
    │   ├── diaryView.py
    │   ├── noteView.py
    │   └── todoView.py
    ├── editor/          # 编辑器模块
    │   └── diaryEditor.py
    ├── server/          # 后端服务
    │   ├── accountServer.py
    │   └── fileServer.py
    └── window/          # 窗口管理
        ├── loginWindow.py
        └── mainWindow.py
```

## 开发说明

### 数据存储

应用程序将用户数据存储在：
```
~/MyDocuments/KairoDiaryData/
```

### 开发环境设置

1. 使用 uv 管理 Python 版本和依赖
2. 确保安装了 PyQt6 开发环境
3. 遵循项目的模块化结构进行开发

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 许可证

© 2025 KairoSoft

---

**注意**：首次运行时，应用程序会自动创建必要的数据目录和配置文件。