# Unlock Music CLI

[![Go Version](https://img.shields.io/badge/go-%3E%3D1.23-blue.svg)](https://golang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://github.com/unlock-music/cli/releases)

🎵 一个强大的命令行工具，用于解密各种加密音乐文件格式并转换为标准音频格式。

## 📋 功能特性

### 🎶 支持的音乐格式

| 格式 | 来源平台 | 状态 |
|------|----------|------|
| **QMC** | QQ音乐 | ✅ 完全支持 |
| **NCM** | 网易云音乐 | ✅ 完全支持 |
| **KGM** | 酷狗音乐 | ✅ 完全支持 |
| **KWM** | 酷我音乐 | ✅ 完全支持 |
| **TM** | 音乐平台 | ✅ 完全支持 |
| **Xiami** | 虾米音乐 | ✅ 完全支持 |
| **Ximalaya** | 喜马拉雅 | ✅ 完全支持 |

### 🚀 核心功能

- **🔓 批量解密**: 支持单文件或整个目录的批量处理
- **📁 目录监控**: 实时监控输入目录，自动处理新文件
- **🎨 元数据更新**: 自动从网络获取并更新音乐元数据和专辑封面
- **🔄 格式转换**: 自动检测音频格式并转换为标准格式
- **⚙️ 灵活配置**: 丰富的命令行参数支持各种使用场景
- **📊 详细日志**: 支持详细日志输出，便于问题排查

## 📦 安装

### 方式一：下载预编译版本
```bash
# 从 GitHub Releases 下载最新版本
wget https://github.com/unlock-music/cli/releases/latest/download/um-linux-amd64
chmod +x um-linux-amd64
sudo mv um-linux-amd64 /usr/local/bin/um
```

### 方式二：从源码构建
```bash
# 克隆仓库
git clone https://github.com/unlock-music/cli.git
cd cli

# 构建
go build -o um cmd/um/main.go

# 安装到系统路径（可选）
sudo mv um /usr/local/bin/
```

### 方式三：使用 Go 安装
```bash
go install unlock-music.dev/cli/cmd/um@latest
```

## 🎯 使用方法

### 基础用法

```bash
# 处理单个文件
um input.ncm

# 处理整个目录
um -i /path/to/music/dir -o /path/to/output/dir

# 显示支持的文件扩展名
um --supported-ext
```

### 高级用法

```bash
# 批量处理并更新元数据
um -i ./music -o ./output --update-metadata

# 监控目录模式（实时处理新文件）
um -i ./watch_dir -o ./output --watch

# 处理后删除源文件
um -i ./music -o ./output --remove-source

# 覆盖已存在的输出文件
um -i ./music -o ./output --overwrite

# 详细日志模式
um -i ./music -o ./output --verbose
```

### QMC 格式特殊配置

```bash
# 使用 MMKV 数据库解密 QMC 文件
um -i ./qmc_files --qmc-mmkv /path/to/mmkv/file --qmc-mmkv-key "your_16_char_key"

# 使用酷狗数据库
um -i ./kgm_files --kgg-db /path/to/KGMusicV3.db
```

## 📖 命令行参数

| 参数 | 简写 | 描述 | 默认值 |
|------|------|------|--------|
| `--input` | `-i` | 输入文件或目录路径 | 当前目录 |
| `--output` | `-o` | 输出目录路径 | 输入目录 |
| `--qmc-mmkv` | `--db` | QMC MMKV 数据库路径 | - |
| `--qmc-mmkv-key` | `--key` | MMKV 密码（16位ASCII字符） | - |
| `--kgg-db` | - | 酷狗数据库路径 | 自动检测 |
| `--remove-source` | `-rs` | 转换成功后删除源文件 | `false` |
| `--skip-noop` | `-n` | 跳过无操作解码器 | `true` |
| `--verbose` | `-V` | 详细日志输出 | `false` |
| `--update-metadata` | - | 从网络更新元数据和封面 | `false` |
| `--overwrite` | - | 覆盖已存在的输出文件 | `false` |
| `--watch` | - | 监控输入目录处理新文件 | `false` |
| `--supported-ext` | - | 显示支持的文件扩展名 | `false` |

## 🏗️ 项目结构

```
cli/
├── algo/                    # 解密算法实现
│   ├── common/             # 通用接口和工具
│   ├── qmc/                # QQ音乐 QMC 格式
│   ├── ncm/                # 网易云音乐 NCM 格式
│   ├── kgm/                # 酷狗音乐 KGM 格式
│   ├── kwm/                # 酷我音乐 KWM 格式
│   ├── tm/                 # TM 格式
│   ├── xiami/              # 虾米音乐格式
│   └── ximalaya/           # 喜马拉雅格式
├── cmd/um/                 # 主程序入口
├── internal/               # 内部工具库
│   ├── ffmpeg/            # FFmpeg 集成
│   ├── logging/           # 日志系统
│   ├── sniff/             # 文件类型检测
│   └── utils/             # 通用工具
└── misc/                   # 构建脚本和工具
```

## 🔧 开发

### 环境要求

- Go 1.23.3 或更高版本
- FFmpeg（用于元数据处理）

### 构建和测试

```bash
# 克隆项目
git clone https://github.com/unlock-music/cli.git
cd cli

# 安装依赖
go mod download

# 运行测试
go test ./...

# 构建
go build -o um cmd/um/main.go

# 交叉编译
GOOS=windows GOARCH=amd64 go build -o um.exe cmd/um/main.go
GOOS=darwin GOARCH=amd64 go build -o um-darwin cmd/um/main.go
GOOS=linux GOARCH=amd64 go build -o um-linux cmd/um/main.go
```

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🤝 致谢

- 感谢所有为此项目做出贡献的开发者
- 特别感谢 [Unlock Music](https://git.unlock-music.dev/um/cli) 项目组

## 📞 支持

- 🐛 [报告 Bug](https://github.com/unlock-music/cli/issues)
- 💡 [功能请求](https://github.com/unlock-music/cli/issues)
- 📖 [项目文档](https://git.unlock-music.dev/um/cli)

## ⚠️ 免责声明

本工具仅供学习和研究使用，请勿用于商业用途。使用本工具处理音乐文件时，请确保您拥有相应的版权或使用权限。

---

<div align="center">

**🎵 让音乐自由流动 | Made with ❤️ by Unlock Music Team**

</div>
