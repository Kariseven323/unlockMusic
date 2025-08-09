#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unlock Music GUI - 音乐解密工具图形界面
支持拖拽文件并调用um.exe进行音乐文件解密
"""

import sys
import os
import subprocess
import threading
import json
from pathlib import Path
from typing import List, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
# 移除拖拽相关导入和类

class UnlockMusicGUI:
    """音乐解密工具GUI主类"""

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
# 移除拖拽设置

        # 查找um.exe路径
        self.um_exe_path = self.find_um_executable()

        # 同步后端支持的扩展名并更新UI
        self.load_supported_extensions()
        self._refresh_supported_label()

    def setup_window(self):
        """设置主窗口"""
        self.root.title("Unlock Music GUI - 音乐解密工具")
        self.root.geometry("850x650")

        # 设置最小尺寸，确保所有UI元素都能正常显示
        # 宽度750px: 足够容纳设置选项和按钮
        # 高度550px: 包含文件选择区、设置区、文件列表、日志区和控制按钮
        self.root.minsize(750, 550)

        # 设置窗口居中显示
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # 设置图标（如果有的话）
        try:
            # 尝试加载PNG图标
            if os.path.exists("unlockMusic.png"):
                # 对于PNG格式，需要使用PhotoImage
                icon_image = tk.PhotoImage(file="unlockMusic.png")
                self.root.iconphoto(True, icon_image)
            elif os.path.exists("icon.ico"):
                # 备用ICO格式
                self.root.iconbitmap("icon.ico")
        except Exception as e:
            # 如果图标加载失败，记录但不影响程序运行
            print(f"图标加载失败: {e}")
            pass

    def setup_variables(self):
        """设置变量"""
        self.output_dir = tk.StringVar(value=str(Path.home() / "Desktop" / "解密音乐"))
        self.remove_source = tk.BooleanVar(value=False)
        self.update_metadata = tk.BooleanVar(value=True)
        self.overwrite = tk.BooleanVar(value=False)
        self.verbose = tk.BooleanVar(value=True)
        # 新增：输出到源文件夹选项
        self.output_to_source = tk.BooleanVar(value=False)
        # 后端支持的扩展（由 CLI 动态提供）
        self.supported_exts: List[str] = []
        self.supported_patterns: List[str] = []  # like ['*.ncm', '*.kgm']
        self.supported_label_var = tk.StringVar(value="🎵 支持格式: 读取中...")


        self.file_queue = []  # 待处理文件队列
        self.is_processing = False

        # 动画相关变量
        self.animation_running = False
        self.fade_alpha = 0.0
        self.status_colors = {
            'idle': '#2E8B57',      # 海绿色
            'processing': '#FF6347', # 番茄红
            'success': '#32CD32',    # 酸橙绿
            'error': '#DC143C'       # 深红色
        }

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 文件拖拽区域
        self.create_drop_area(main_frame)

        # 设置区域
        self.create_settings_area(main_frame)

        # 文件列表区域
        self.create_file_list_area(main_frame)

        # 日志区域
        self.create_log_area(main_frame)

        # 控制按钮区域
        self.create_control_area(main_frame)

    def create_drop_area(self, parent):
        """创建文件选择区域"""
        file_frame = ttk.LabelFrame(parent, text="选择音乐文件", padding="20")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.info_label = ttk.Label(
            file_frame,
            textvariable=self.supported_label_var,
            font=("Arial", 11),
            anchor="center",
            justify="center"
        )
        self.info_label.pack(pady=(0, 15))

        # 文件选择按钮
        button_frame = ttk.Frame(file_frame)
        button_frame.pack()

        browse_files_btn = ttk.Button(button_frame, text="选择文件", command=self.browse_files)
        browse_files_btn.pack(side=tk.LEFT, padx=(0, 10))

        browse_folder_btn = ttk.Button(button_frame, text="选择文件夹", command=self.browse_folder)
        browse_folder_btn.pack(side=tk.LEFT)

    def create_settings_area(self, parent):
        """创建设置区域"""
        settings_frame = ttk.LabelFrame(parent, text="设置选项", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)

        # 输出目录
        ttk.Label(settings_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        output_frame = ttk.Frame(settings_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        output_frame.columnconfigure(0, weight=1)

        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.browse_output_dir).grid(row=0, column=1)

        # 输出到源文件夹选项
        output_source_frame = ttk.Frame(settings_frame)
        output_source_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        self.output_source_check = ttk.Checkbutton(
            output_source_frame,
            text="输出到源文件夹（忽略上述输出目录设置）",
            variable=self.output_to_source,
            command=self.on_output_to_source_changed
        )
        self.output_source_check.pack(side=tk.LEFT)

        # 选项复选框
        options_frame = ttk.Frame(settings_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Checkbutton(options_frame, text="处理后删除源文件", variable=self.remove_source).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="更新元数据", variable=self.update_metadata).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="覆盖已存在文件", variable=self.overwrite).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="详细日志", variable=self.verbose).pack(side=tk.LEFT)

    def create_file_list_area(self, parent):
        """创建文件列表区域"""
        list_frame = ttk.LabelFrame(parent, text="待处理文件", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 文件列表
        self.file_listbox = tk.Listbox(list_frame, height=6)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        # 清空按钮
        clear_btn = ttk.Button(list_frame, text="清空列表", command=self.clear_file_list)
        clear_btn.grid(row=1, column=0, columnspan=2, pady=(5, 0))

    def create_log_area(self, parent):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(parent, text="处理日志", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_control_area(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.start_btn = ttk.Button(control_frame, text="开始处理", command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(control_frame, text="停止处理", command=self.stop_processing, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 状态指示器
        self.status_label = ttk.Label(control_frame, text="● 就绪", foreground=self.status_colors['idle'])
        self.status_label.pack(side=tk.LEFT, padx=(10, 10))

        # 进度条
        self.progress = ttk.Progressbar(control_frame, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

    def load_supported_extensions(self):
        """调用 CLI 获取支持的扩展名，并更新过滤/扫描集合"""
        try:
            if not self.um_exe_path:
                # fallback to静态常量，尽量包含更多
                static_exts = [
                    'ncm',
                    # KUGOU
                    'kgg', 'kgm', 'kgma', 'vpr', 'kgm.flac', 'vpr.flac',
                    # KUWO
                    'kwm',
                    # QMC 系列
                    'qmc0','qmc2','qmc3','qmc4','qmc6','qmc8','qmcflac','qmcogg','tkm',
                    'bkcmp3','bkcm4a','bkcflac','bkcwav','bkcape','bkcogg','bkcwma',
                    '666c6163','6d7033','6f6767','6d3461','776176','mmp4',
                    'mgg','mgg0','mgg1','mgga','mggh','mggl','mggm',
                    'mflac','mflac0','mflac1','mflaca','mflach','mflacl','mflacm',
                    # 喜马拉雅/虾米
                    'x2m','x3m','xm',
                    # 直读原始格式（允许直接拖入）
                    'mp3','flac','ogg','m4a','wav','wma','aac'
                ]
            else:
                # 隐藏cmd窗口
                startupinfo = None
                if os.name == 'nt':  # Windows系统
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                result = subprocess.run(
                    [self.um_exe_path, "--supported-ext"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    startupinfo=startupinfo
                )
                if result.returncode == 0:
                    lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip() and ":" in ln]
                    static_exts = [ln.split(":",1)[0].strip() for ln in lines]
                else:
                    self.log_message(f"⚠️ 获取支持格式失败，使用内置列表。stderr={result.stderr.strip() if result.stderr else ''}")
                    static_exts = []
        except Exception as e:
            self.log_message(f"⚠️ 获取支持格式异常，使用内置列表: {e}")
            static_exts = []

        # 去重并排序
        ext_set = set(ext.lower().lstrip('.') for ext in static_exts)
        # 最小兜底
        if not ext_set:
            ext_set.update({'ncm','kgm','kgma','kgg','vpr','kwm','qmc0','qmc3','qmcflac','qmcogg','xm','x2m','x3m'})

        self.supported_exts = sorted(ext_set)
        # 生成文件对话框 patterns（tk不支持通配点号的两个级联如 *.kgm.flac，因此保留原位）
        patterns = []
        for ext in self.supported_exts:
            if '.' in ext:
                # pattern like *.kgm.flac
                patterns.append(f"*.{ext}")
            else:
                patterns.append(f"*.{ext}")
        self.supported_patterns = patterns

    def _refresh_supported_label(self):
        # 展示为分组名而非纯扩展，避免过长；这里简单显示核心家族
        families = [
            "QMC", "NCM", "KGM/VPR", "KWM", "Xiami", "Ximalaya"
        ]
        self.supported_label_var.set("🎵 支持格式: " + ", ".join(families))

# 移除拖拽设置方法

    def find_um_executable(self) -> Optional[str]:
        """查找um.exe可执行文件"""
        candidates = []

        # 打包后的环境 - 优先查找顺序
        if getattr(sys, 'frozen', False):
            # 1. PyInstaller 临时目录 (_MEIPASS)
            if hasattr(sys, '_MEIPASS'):
                candidates.append(os.path.join(sys._MEIPASS, "um.exe"))

            # 2. exe 同目录
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, "um.exe"))

        # 开发环境
        candidates.extend([
            "./um.exe",
            "./um",
            "um.exe",
            "um"
        ])

        # 逐一检查候选路径
        for path in candidates:
            if os.path.isfile(path):
                try:
                    # 验证文件可执行性
                    if os.access(path, os.X_OK) or path.endswith('.exe'):
                        return os.path.abspath(path)
                except:
                    continue

        # 如果没找到，记录但不立即报错（延迟到使用时）
        return None

    def browse_files(self):
        """浏览并选择文件"""
        # 构造动态过滤器
        patterns = self.supported_patterns or [
            "*.ncm",
            "*.kgg", "*.kgm", "*.kgma", "*.vpr", "*.kgm.flac", "*.vpr.flac",
            "*.kwm",
            "*.qmc0", "*.qmc2", "*.qmc3", "*.qmc4", "*.qmc6", "*.qmc8", "*.qmcflac", "*.qmcogg", "*.tkm",
            "*.bkcmp3","*.bkcm4a","*.bkcflac","*.bkcwav","*.bkcape","*.bkcogg","*.bkcwma",
            "*.666c6163","*.6d7033","*.6f6767","*.6d3461","*.776176","*.mmp4",
            "*.mgg","*.mgg0","*.mgg1","*.mgga","*.mggh","*.mggl","*.mggm",
            "*.mflac","*.mflac0","*.mflac1","*.mflaca","*.mflach","*.mflacl","*.mflacm",
            "*.x2m","*.x3m","*.xm",
            # 可选：允许原始音频格式（某些Xiami typed会伪装成这些扩展）
            "*.mp3","*.flac","*.ogg","*.m4a","*.wav","*.wma","*.aac"
        ]
        filetypes = [
            ("音乐文件", " ".join(patterns)),
            ("所有文件", "*.*")
        ]
        files = filedialog.askopenfilenames(
            title="选择要解密的音乐文件",
            filetypes=filetypes
        )
        if files:
            self.add_files_to_queue(files)

    def browse_folder(self):
        """浏览并选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含音乐文件的文件夹")
        if folder:
            # 构造扫描后缀集合（含点号）
            if self.supported_exts:
                music_extensions = {f".{ext}" for ext in self.supported_exts}
            else:
                music_extensions = {'.ncm','.kgg','.kgm','.kgma','.vpr','.kgm.flac','.vpr.flac',
                                    '.kwm',
                                    '.qmc0','.qmc2','.qmc3','.qmc4','.qmc6','.qmc8','.qmcflac','.qmcogg','.tkm',
                                    '.bkcmp3','.bkcm4a','.bkcflac','.bkcwav','.bkcape','.bkcogg','.bkcwma',
                                    '.666c6163','.6d7033','.6f6767','.6d3461','.776176','.mmp4',
                                    '.mgg','.mgg0','.mgg1','.mgga','.mggh','.mggl','.mggm',
                                    '.mflac','.mflac0','.mflac1','.mflaca','.mflach','.mflacl','.mflacm',
                                    '.x2m','.x3m','.xm'}
            files = []
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    name = filename.lower()
                    if any(name.endswith(ext) for ext in music_extensions):
                        files.append(os.path.join(root, filename))
            if files:
                self.add_files_to_queue(files)
                self.log_message(f"📁 从文件夹扫描到 {len(files)} 个音乐文件")
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的音乐文件")

    def browse_output_dir(self):
        """浏览并选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def on_output_to_source_changed(self):
        """当输出到源文件夹选项改变时的处理"""
        if self.output_to_source.get():
            # 禁用输出目录输入框和浏览按钮
            self.output_entry.config(state="disabled")
            self.log_message("📁 已启用输出到源文件夹模式")
        else:
            # 启用输出目录输入框和浏览按钮
            self.output_entry.config(state="normal")
            self.log_message("📁 已禁用输出到源文件夹模式")

    def add_files_to_queue(self, files: List[str]):
        """添加文件到处理队列"""
        for file_path in files:
            if file_path not in self.file_queue:
                self.file_queue.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))

        self.log_message(f"✅ 已添加 {len(files)} 个文件到处理队列")
        # 显示文件添加动画
        self.show_file_added_animation()

    def clear_file_list(self):
        """清空文件列表"""
        self.file_queue.clear()
        self.file_listbox.delete(0, tk.END)
        self.log_message("🗑️ 已清空文件列表")

    def log_message(self, message: str):
        """添加日志消息"""
        timestamp = threading.current_thread().name
        log_entry = f"[{timestamp}] {message}\n"

        # 在主线程中更新UI
        self.root.after(0, lambda: self._update_log_text(log_entry))

    def _update_log_text(self, message: str):
        """更新日志文本（主线程调用）"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

    def start_processing(self):
        """开始处理文件"""
        if not self.file_queue:
            messagebox.showwarning("警告", "请先添加要处理的文件")
            return

        if not self.um_exe_path:
            messagebox.showerror("错误", "未找到um.exe程序，请检查程序是否存在")
            return

        if self.is_processing:
            return

        # 创建输出目录
        output_path = Path(self.output_dir.get())
        output_path.mkdir(parents=True, exist_ok=True)

        self.is_processing = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.config(maximum=len(self.file_queue), value=0)

        # 更新状态指示器
        self.update_status_indicator('processing', '处理中')
        self.animate_status_indicator('processing')

        # 启动进度条动画
        self.animate_progress_bar()

        # 在新线程中处理文件
        processing_thread = threading.Thread(target=self._process_files, daemon=True)
        processing_thread.start()

    def stop_processing(self):
        """停止处理"""
        self.is_processing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status_indicator('idle', '已停止')
        self.log_message("⏹️ 处理已停止")

    def _process_files(self):
        """处理文件（在后台线程中运行）"""
        total_files = len(self.file_queue)
        processed = 0

        for i, file_path in enumerate(self.file_queue):
            if not self.is_processing:
                break

            self.log_message(f"🔄 正在处理: {os.path.basename(file_path)}")

            try:
                success = self._process_single_file(file_path)
                if success:
                    self.log_message(f"✅ 处理成功: {os.path.basename(file_path)}")
                    processed += 1
                else:
                    self.log_message(f"❌ 处理失败: {os.path.basename(file_path)}")

            except Exception as e:
                self.log_message(f"❌ 处理出错: {os.path.basename(file_path)} - {str(e)}")

            # 更新进度条
            self.root.after(0, lambda v=i+1: self.progress.config(value=v))

        # 处理完成
        self.root.after(0, self._processing_completed)
        self.log_message(f"🎉 处理完成! 成功: {processed}/{total_files}")

    def _process_single_file(self, file_path: str) -> bool:
        """处理单个文件"""
        try:
            # 构建um.exe命令
            cmd = [self.um_exe_path]
            cmd.extend(["-i", file_path])

            # 根据输出到源文件夹选项决定输出目录
            if self.output_to_source.get():
                # 输出到源文件所在目录
                source_dir = os.path.dirname(file_path)
                cmd.extend(["-o", source_dir])
            else:
                # 输出到指定目录
                cmd.extend(["-o", self.output_dir.get()])

            if self.remove_source.get():
                cmd.append("--remove-source")
            if self.update_metadata.get():
                cmd.append("--update-metadata")
            if self.overwrite.get():
                cmd.append("--overwrite")
            if self.verbose.get():
                cmd.append("--verbose")

            # 执行命令，隐藏cmd窗口
            startupinfo = None
            if os.name == 'nt':  # Windows系统
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                startupinfo=startupinfo
            )

            if result.returncode == 0:
                if self.verbose.get() and result.stdout:
                    self.log_message(f"📝 {result.stdout.strip()}")
                return True
            else:
                if result.stderr:
                    self.log_message(f"❌ 错误: {result.stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            self.log_message(f"⏰ 处理超时: {os.path.basename(file_path)}")
            return False
        except Exception as e:
            self.log_message(f"❌ 异常: {str(e)}")
            return False

    def _processing_completed(self):
        """处理完成后的UI更新"""
        self.is_processing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status_indicator('success', '完成')
        # 添加完成动画
        self.show_completion_animation()

    def show_startup_animation(self):
        """显示启动动画 - 窗口淡入效果"""
        try:
            # Windows系统支持窗口透明度
            if os.name == 'nt':
                self.root.attributes('-alpha', 0.0)
                self.fade_in_window()
            else:
                # 其他系统使用简单的缩放动画
                self.scale_in_window()
        except:
            # 如果不支持动画，直接显示
            pass

    def fade_in_window(self):
        """窗口淡入动画"""
        if self.fade_alpha < 1.0:
            self.fade_alpha += 0.05
            try:
                self.root.attributes('-alpha', self.fade_alpha)
            except:
                pass
            self.root.after(30, self.fade_in_window)

    def scale_in_window(self):
        """窗口缩放进入动画"""
        # 简单的几何动画效果
        original_geometry = self.root.geometry()
        # 这里可以添加更复杂的缩放逻辑
        pass

    def show_file_added_animation(self):
        """文件添加时的动画反馈"""
        try:
            # 让文件列表框闪烁一下
            original_bg = self.file_listbox.cget('bg')
            self.file_listbox.config(bg='lightgreen')

            # 创建一个临时的"已添加"提示
            added_label = tk.Label(self.root, text="✅ 文件已添加",
                                 font=("Arial", 10),
                                 fg="green", bg=self.root.cget('bg'))

            # 获取文件列表框的位置来定位提示
            try:
                x = self.file_listbox.winfo_x() + self.file_listbox.winfo_width() - 100
                y = self.file_listbox.winfo_y() + 10
                added_label.place(x=x, y=y)
            except:
                added_label.place(relx=0.8, rely=0.4)

            # 1秒后移除提示和恢复背景色
            self.root.after(200, lambda: self.file_listbox.config(bg=original_bg))
            self.root.after(1000, lambda: added_label.destroy())
        except Exception as e:
            print(f"文件添加动画失败: {e}")
            pass

    def show_completion_animation(self):
        """处理完成时的动画"""
        try:
            # 创建一个临时的成功消息标签
            success_label = tk.Label(self.root, text="🎉 处理完成！",
                                   font=("Arial", 14, "bold"),
                                   fg="green", bg=self.root.cget('bg'))
            success_label.place(relx=0.5, rely=0.5, anchor="center")

            # 让成功消息淡出
            self.fade_out_success_message(success_label, 1.0)

            # 让进度条变绿
            original_bg = self.progress.cget('background') if hasattr(self.progress, 'cget') else None
            # 2秒后恢复
            self.root.after(2000, lambda: self.reset_progress_style())
        except Exception as e:
            print(f"动画效果失败: {e}")
            pass

    def fade_out_success_message(self, label, alpha):
        """成功消息淡出动画"""
        try:
            if alpha > 0:
                # 模拟淡出效果（tkinter不直接支持alpha，使用颜色变化）
                gray_value = int(255 * (1 - alpha))
                color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
                label.config(fg=color)
                self.root.after(50, lambda: self.fade_out_success_message(label, alpha - 0.05))
            else:
                label.destroy()
        except:
            try:
                label.destroy()
            except:
                pass

    def reset_progress_style(self):
        """重置进度条样式"""
        try:
            # 重置进度条值
            self.progress.config(value=0)
        except:
            pass

    def animate_progress_bar(self):
        """进度条动画效果"""
        if self.is_processing:
            # 添加一些视觉反馈
            try:
                current_value = self.progress['value']
                # 可以添加一些波动效果
                self.root.after(100, self.animate_progress_bar)
            except:
                pass

    def update_status_indicator(self, status, text):
        """更新状态指示器"""
        try:
            color = self.status_colors.get(status, self.status_colors['idle'])
            self.status_label.config(text=f"● {text}", foreground=color)
        except:
            pass

    def animate_status_indicator(self, status):
        """状态指示器动画效果"""
        if status == 'processing':
            # 处理中的闪烁效果
            self.blink_status_indicator()

    def blink_status_indicator(self):
        """状态指示器闪烁效果"""
        if self.is_processing:
            try:
                current_color = self.status_label.cget('foreground')
                new_color = self.status_colors['processing'] if current_color != self.status_colors['processing'] else '#FFB6C1'
                self.status_label.config(foreground=new_color)
                self.root.after(500, self.blink_status_indicator)
            except:
                pass

    def add_button_hover_effects(self):
        """为按钮添加悬停效果"""
        def on_enter(event, button):
            button.config(cursor="hand2")

        def on_leave(event, button):
            button.config(cursor="")

        # 为主要按钮添加悬停效果
        try:
            self.start_btn.bind("<Enter>", lambda e: on_enter(e, self.start_btn))
            self.start_btn.bind("<Leave>", lambda e: on_leave(e, self.start_btn))
            self.stop_btn.bind("<Enter>", lambda e: on_enter(e, self.stop_btn))
            self.stop_btn.bind("<Leave>", lambda e: on_leave(e, self.stop_btn))
        except:
            pass

    def run(self):
        """运行GUI应用"""
        self.log_message("🚀 Unlock Music GUI 已启动")
        self.log_message(f"📁 默认输出目录: {self.output_dir.get()}")

        if self.um_exe_path:
            self.log_message(f"✅ 找到um.exe: {self.um_exe_path}")
        else:
            self.log_message("⚠️ 未找到um.exe，请确保已编译并放置在正确位置")

        # 启用动画效果
        self.add_button_hover_effects()
        self.show_startup_animation()

        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = UnlockMusicGUI()
        app.run()
    except Exception as e:
        import traceback
        error_msg = f"启动失败:\n{traceback.format_exc()}"

        # 尝试显示错误对话框
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("Unlock Music GUI - 启动错误", error_msg)
            root.destroy()
        except:
            # 如果 GUI 都无法启动，写入日志文件
            try:
                with open("UnlockMusicGUI_error.log", "w", encoding="utf-8") as f:
                    f.write(error_msg)
                print(f"错误已写入 UnlockMusicGUI_error.log")
            except:
                pass

        print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
