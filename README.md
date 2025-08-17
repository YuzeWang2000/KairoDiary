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

- macOS 10.15+ 
- Python 3.11+
- PyQt6

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

### 打包为 macOS 应用程序

使用 `setup.py` 可以将应用程序打包为独立的 macOS 应用：

1. **确保依赖已安装**：
```bash
uv sync
```

2. **执行打包命令**：
```bash
uv run python setup.py py2app
```

3. **打包完成后**，会在 `dist/` 目录中生成 `KairoDiary.app` 应用程序文件。

4. **运行打包的应用**：
   - 双击 `dist/KairoDiary.app` 即可运行
   - 或将应用拖拽到 `Applications` 文件夹进行安装

### 打包选项说明

`setup.py` 配置了以下打包选项：
- **应用图标**：使用 `assets/KairoDiary.icns` 作为应用图标
- **应用名称**：KairoDiary
- **版本号**：1.0.0
- **包标识符**：com.kairosoft.kairodiary

## 项目结构

```
KairoDiary/
├── main.py                 # 应用程序入口
├── setup.py               # 打包配置文件
├── pyproject.toml         # 项目配置和依赖
├── uv.lock               # 依赖锁定文件
├── .python-version       # Python 版本指定
├── assets/               # 资源文件
│   └── KairoDiary.icns  # 应用图标
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