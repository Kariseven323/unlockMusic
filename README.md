# 🎵 Unlock Music GUI - 音乐解密工具图形界面

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![Go](https://img.shields.io/badge/go-1.19%2B-blue.svg)](https://golang.org/)

一个功能强大的音乐文件解密工具，支持多种加密格式，提供直观的图形用户界面。

## 📸 界面预览

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unlock Music GUI - 音乐解密工具                │
├─────────────────────────────────────────────────────────────────┤
│  🎵 支持格式: QMC, NCM, KGM/VPR, KWM, Xiami, Ximalaya           │
│                                                                 │
│  [选择文件]  [选择文件夹]                                        │
├─────────────────────────────────────────────────────────────────┤
│  输出目录: [C:\Users\Desktop\解密音乐        ] [浏览]            │
│  ☑ 输出到源文件夹（忽略上述输出目录设置）                        │
│                                                                 │
│  ☐ 删除源文件  ☑ 更新元数据  ☐ 覆盖已存在文件  ☑ 详细日志      │
├─────────────────────────────────────────────────────────────────┤
│  文件列表:                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ song1.ncm                                               │   │
│  │ song2.kgm                                               │   │
│  │ song3.qmc0                                              │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  日志输出:                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [MainThread] 🚀 Unlock Music GUI 已启动                │   │
│  │ [MainThread] ✅ 找到um.exe: ./um.exe                   │   │
│  │ [MainThread] 📁 已启用输出到源文件夹模式                │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  [开始处理]  [停止处理]  ████████████████████████ 100%          │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ 主要特性

### 🎯 核心功能
- **🔓 批量解密**: 支持单文件或整个目录的批量处理
- **🎨 元数据更新**: 自动从网络获取并更新音乐元数据和专辑封面
- **🔄 格式转换**: 自动检测音频格式并转换为标准格式
- **📊 实时进度**: 可视化进度条和详细日志输出

### 🆕 增强功能 (v2.0)
- **📁 输出到源文件夹**: 可选择将解密文件输出到源文件所在目录
- **🔇 静默处理**: 解密过程中不再弹出命令行窗口，提升用户体验
- **📐 优化界面**: 智能窗口尺寸，确保所有UI元素在任何分辨率下都能正常显示

### 🎵 支持格式
| 平台 | 格式 | 扩展名 |
|------|------|--------|
| **网易云音乐** | NCM | `.ncm` |
| **酷狗音乐** | KGM/VPR | `.kgg`, `.kgm`, `.kgma`, `.vpr` |
| **酷我音乐** | KWM | `.kwm` |
| **QQ音乐** | QMC系列 | `.qmc0`, `.qmc2`, `.qmc3`, `.qmcflac`, `.qmcogg`, `.tkm` |
| **虾米音乐** | Xiami | `.xm` |
| **喜马拉雅** | Ximalaya | `.x2m`, `.x3m` |

## 🚀 快速开始

### 方式一：下载预编译版本 (推荐)
1. 从 [Releases](../../releases) 页面下载最新版本的 `UnlockMusicGUI.exe`
2. 双击运行即可，无需安装

### 方式二：从源码构建
```bash
# 1. 克隆仓库
git clone https://github.com/your-username/unlock-music-gui.git
cd unlock-music-gui

# 2. 确保已安装依赖
# Python 3.7+ 和 Go 1.19+

# 3. 一键构建 (Windows)
simple_build.bat

# 4. 或手动构建
go build -o um.exe cmd/um/main.go
pip install pyinstaller
pyinstaller UnlockMusicGUI.spec
```

## 📖 使用指南

### 基础使用
1. **选择文件**: 点击"选择文件"或"选择文件夹"添加要解密的音乐文件
2. **设置输出**:
   - 默认输出到桌面的"解密音乐"文件夹
   - 或勾选"输出到源文件夹"直接输出到源文件所在目录
3. **配置选项**: 根据需要调整处理选项
4. **开始处理**: 点击"开始处理"按钮开始解密

### 高级选项说明
- **删除源文件**: 处理完成后自动删除原始加密文件
- **更新元数据**: 从网络获取歌曲信息和专辑封面
- **覆盖已存在文件**: 如果输出文件已存在，直接覆盖
- **详细日志**: 显示详细的处理过程信息

### 特殊格式配置
对于某些特殊格式，可能需要额外的数据库文件：
- **QMC格式**: 可能需要MMKV数据库文件
- **KGM格式**: 可能需要酷狗数据库文件

## 🛠️ 技术架构

### 项目结构
```
unlock-music-gui/
├── gui_app.py              # GUI主程序 (Python + Tkinter)
├── cmd/um/main.go          # CLI后端 (Go)
├── algo/                   # 解密算法实现
│   ├── ncm/               # 网易云音乐
│   ├── kgm/               # 酷狗音乐
│   ├── qmc/               # QQ音乐
│   └── ...
├── internal/              # 内部工具库
├── dist/                  # 构建输出目录
├── simple_build.bat       # 一键构建脚本
└── UnlockMusicGUI.spec    # PyInstaller配置
```

### 技术栈
- **前端**: Python 3.7+ + Tkinter (跨平台GUI)
- **后端**: Go 1.19+ (高性能解密引擎)
- **打包**: PyInstaller (单文件可执行程序)
- **架构**: 前后端分离，通过subprocess通信

## 🔧 开发指南

### 环境要求
- Python 3.7+
- Go 1.19+
- Windows/Linux/macOS

### 开发环境设置
```bash
# 1. 安装Python依赖
pip install tkinter  # 通常已内置

# 2. 编译Go后端
go build -o um.exe cmd/um/main.go

# 3. 运行开发版本
python gui_app.py
```

### 代码贡献
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.0.0 (2025-08-09)
- ✨ 新增"输出到源文件夹"功能
- 🔇 优化解密过程，隐藏命令行窗口
- 📐 改进窗口尺寸设置，确保UI元素完整显示
- 🎨 优化用户界面布局和交互体验

### v1.0.0
- 🎉 初始版本发布
- 🔓 支持主流音乐平台解密
- 🎨 图形化用户界面
- 📊 批量处理和进度显示

## ❓ 常见问题

### Q: 为什么某些文件解密失败？
A: 可能原因：
1. 文件格式不受支持
2. 文件已损坏
3. 需要特定的数据库文件（如QMC格式）

### Q: 解密后的文件在哪里？
A:
- 默认在桌面的"解密音乐"文件夹
- 如果勾选了"输出到源文件夹"，则在原文件所在目录

### Q: 支持哪些操作系统？
A: Windows、Linux、macOS 都支持，但预编译版本主要针对Windows

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [unlock-music](https://github.com/unlock-music) - 核心解密算法
- 所有贡献者和用户的支持

## 📞 联系方式

- 问题反馈: [Issues](../../issues)
- 功能建议: [Discussions](../../discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

Made with ❤️ by [Your Name]

</div>