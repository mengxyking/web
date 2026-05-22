#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔云腾工具箱
功能：扫描设备、视频推流、设置/删除SOCKS5代理、拖放上传文件/APK
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import time
import json
import os
import sys
import queue
import socket
import requests
import http.server
import socketserver
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
from flask import Flask, send_file
import re
import random
import subprocess
import glob
import hashlib


# 任务暂停/继续依赖（用于挂起/恢复子进程）
try:
    import psutil  # type: ignore
except ImportError:  # 兼容环境未安装 psutil 的情况
    psutil = None

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
mytRpc = None
container_manager = None


class VideoStreamServer:
    """本地视频流HTTP服务器"""

    def __init__(self, port=8000):
        self.port = port
        self.local_ip = self._get_local_ip()
        self.app = Flask(__name__)
        self.server_thread = None
        self.is_running = False
        self.video_folder = None
        self.video_map = {}
        self._setup_routes()

    def _get_local_ip(self):
        """获取本机局域网IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _setup_routes(self):
        """设置Flask路由"""
        @self.app.route('/video/<path:filename>')
        def serve_video(filename):
            if filename in self.video_map:
                video_path = self.video_map[filename]
                if os.path.exists(video_path):
                    return send_file(video_path, mimetype='video/mp4', conditional=True)
            if self.video_folder:
                video_path = os.path.join(self.video_folder, filename)
                if os.path.exists(video_path):
                    return send_file(video_path, mimetype='video/mp4', conditional=True)
            return {"error": "Video not found"}, 404

    def start(self, video_folder):
        """启动HTTP服务器"""
        if self.is_running:
            return True
        self.video_folder = video_folder

        def run_server():
            try:
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
                self.app.run(host='0.0.0.0', port=self.port, debug=False,
                           use_reloader=False, threaded=True)
            except Exception as e:
                print(f"服务器启动失败: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        time.sleep(1)
        return True

    def register_video(self, filepath):
        """注册视频文件"""
        filename = os.path.basename(filepath)
        self.video_map[filename] = filepath

    def get_video_url(self, filename):
        """获取视频的URL地址"""
        encoded_filename = quote(filename)
        return f"http://{self.local_ip}:{self.port}/video/{encoded_filename}"


class DeviceManageTool:
    """魔云腾工具箱主类"""
    
    def __init__(self):
        self.root = TkinterDnD.Tk()  # 使用TkinterDnD支持拖放
        self.root.title("测试工具 v1.0")
        self.root.geometry("1100x700")
        self.root.minsize(900, 700)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # macOS Cmd+Q 不触发 WM_DELETE_WINDOW，用 atexit 兜底保存
        import atexit
        atexit.register(self.save_config)
        
        # 设备相关
        self.devices = []
        self.device_checked = {}
        self.device_custom_names = {}  # {serial: custom_display_name}
        self.is_scanning = False
        
        # 扫描配置 - 内置网段
        self.scan_networks = ["192.168.11", "10.0.0", "10.0.1"]  # 内置网段（含常见局域网段）
        self.scan_start = 1
        self.scan_end = 254
        self.max_workers = 200  # 增加并发数
        self.scan_timeout = (0.3, 0.5)  # (连接超时, 读取超时)
        
        # SOCKS5配置
        self.socks5_config = {}
        
        # 成功计数
        self.success_var = tk.IntVar(value=0)
        
        # 手机号信息
        self.phones = []  # 存储手机号记录: {"phone": str, "url": str, "usage": str, "status": str, "time": str}
        self.emails = []  # 存储邮箱记录: {"email": str, "password": str, "usage": str, "status": str}
        self.custom_open_apps = []  # 用户手动添加的应用 [{"name": str, "package": str}]
        self.phone_lock = threading.Lock()  # 确保多个脚本并发获取手机号/邮箱时不重复

        # --- 平台取号配置（脚本配置Tab） ---
        # 启用后：脚本从本地 /get_phone 接口取号时，将实时从平台获取，不再从"手机号管理"列表分发
        self.platform_phone_var = tk.IntVar(value=0)  # 1=平台取号，0=手机号管理取号
        self.platform_name_var = tk.StringVar(value="tg")  # 平台名称：tg（Tiger SMS）
        self.platform_api_key_var = tk.StringVar(value="")  # 平台 key
        self.platform_country_var = tk.StringVar(value="187")  # 国家
        self.platform_service_var = tk.StringVar(value="wb")  # 业务
        self.platform_provider_ids_var = tk.StringVar(value="216")  # providerIds
        
        # VISA卡信息
        self.visas = []  # 存储VISA记录: {"card_number": str, "expiry_date": str, "cvv": str, "status": str, "get_count": int, "wait_count": int, "success_status": str, "time": str}
        self.visa_lock = threading.Lock()  # 确保多个脚本并发获取VISA时不重复
        
        # VISA失败计数（按手机号维度）
        self.visa_fail_counts = {}  # 格式：{phone: fail_count}
        self.visa_fail_lock = threading.Lock()

        # --- VISA同步管理器（用于通道三模式的VISA共享和等待同步） ---
        self.visa_sync_manager = {
            # 格式：card_number -> {
            #   'item_id': item_id,
            #   'get_count': 0,  # 获取次数
            #   'using_containers': [],  # 使用该VISA的容器编号列表
            #   'waiting_containers': [],  # 等待中的容器列表：[(key, container_suffix, wait_start_time), ...]
            #   'wait_count': 0,  # 等待计数
            #   'disabled': False,  # 是否已禁用
            #   'executed_after_cvv': {}  # 记录哪些容器在执行CVV脚本后又执行了其他脚本：{key: True}
            # }
        }
        self.visa_sync_lock = threading.Lock()  # VISA同步管理器锁
        self.visa_checked_state = {}  # VISA勾选状态
        
        # 加载配置
        self.socks5_config = {
            "proxy": "",
            "user": "",
            "passwd": "",
            "domain_filter": [],
            "vpc_node": ""
        }
        
        # 视频服务器
        self.video_server = None
        
        # 图片/文件服务器
        self.file_server_port = 8080
        self.file_server = None
        self.file_server_thread = None
        self.in_memory_files = {}  # 存储内存中的文件
        self.local_ip = self._get_local_ip()
        
        # 日志队列
        self.log_queue = queue.Queue()
        self._tab_log_texts = []  # 各Tab日志框，统一接收日志广播

        # 运行中的任务
        self.running_tasks = {}  # {device_key: subprocess.Popen}
        # 任务暂停状态：key 与 running_tasks 一致，值为 True 表示已暂停
        self.task_pause_state = {}
        # 自定义脚本暂停/停止控制
        self._cs_pause_event = threading.Event()   # set = 暂停中
        self._cs_stop_event  = threading.Event()   # set = 请求停止

        # 构建界面
        self._apply_style()
        self.setup_ui()
        
        # 启动日志处理
        self.process_log_queue()
        
        # 加载配置
        self.load_config()
        
        # 启动文件服务器
        self._start_file_server()

        # 启动自动扫描 (延迟500ms等待界面加载)
        self.root.after(500, self.scan_devices)
    
    def _apply_style(self):
        """应用现代专业 UI 样式"""
        C = {
            "bg":       "#f0f2f5",
            "panel":    "#ffffff",
            "header":   "#1a237e",
            "header2":  "#283593",
            "accent":   "#1565c0",
            "success":  "#2e7d32",
            "danger":   "#c62828",
            "warning":  "#e65100",
            "muted":    "#78909c",
            "text":     "#1c2b4a",
            "border":   "#dde3ee",
            "row_odd":  "#f4f7ff",
            "row_even": "#ffffff",
            "sel":      "#bbdefb",
        }
        self._C = C

        self.root.configure(bg=C["bg"])

        s = ttk.Style(self.root)
        s.theme_use("clam")

        # ── 基础 ──────────────────────────────────────────────────────
        s.configure(".", background=C["bg"], foreground=C["text"],
                    font=("PingFang SC", 10))
        s.configure("TFrame",     background=C["bg"])
        s.configure("TLabel",     background=C["bg"], foreground=C["text"])
        s.configure("TPanedwindow", background=C["bg"])

        # ── LabelFrame ────────────────────────────────────────────────
        s.configure("TLabelframe", background=C["bg"],
                    relief="groove", borderwidth=1, bordercolor=C["border"])
        s.configure("TLabelframe.Label",
                    background=C["bg"],
                    foreground=C["accent"],
                    font=("PingFang SC", 10, "bold"))

        # ── Notebook ──────────────────────────────────────────────────
        s.configure("TNotebook", background=C["bg"], borderwidth=0,
                    tabmargins=[2, 4, 0, 0])
        s.configure("TNotebook.Tab",
                    background="#dde8f8", foreground=C["muted"],
                    padding=[16, 7], font=("PingFang SC", 10),
                    borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C["accent"]), ("active", "#c5d8f5")],
              foreground=[("selected", "white"), ("active", C["text"])])

        # ── Treeview ──────────────────────────────────────────────────
        s.configure("Treeview",
                    background=C["panel"],
                    fieldbackground=C["panel"],
                    foreground=C["text"],
                    rowheight=30,
                    font=("PingFang SC", 10),
                    borderwidth=0,
                    relief="flat")
        s.configure("Treeview.Heading",
                    background=C["header"],
                    foreground="white",
                    font=("PingFang SC", 10, "bold"),
                    relief="flat",
                    padding=[6, 8])
        s.map("Treeview",
              background=[("selected", C["sel"])],
              foreground=[("selected", C["text"])])
        s.map("Treeview.Heading",
              background=[("active", C["header2"])])

        # ── Button ────────────────────────────────────────────────────
        for name, bg, active in (
            ("TButton",           C["accent"],  "#0d47a1"),
            ("Success.TButton",   C["success"], "#1b5e20"),
            ("Danger.TButton",    C["danger"],  "#b71c1c"),
            ("Warning.TButton",   C["warning"], "#bf360c"),
            ("Muted.TButton",     C["muted"],   "#546e7a"),
        ):
            s.configure(name, background=bg, foreground="white",
                        relief="flat", padding=[11, 6],
                        font=("PingFang SC", 10), borderwidth=0)
            s.map(name,
                  background=[("active", active), ("pressed", active)],
                  relief=[("pressed", "flat")])

        # ── Entry / Combobox / Text ───────────────────────────────────
        s.configure("TEntry",
                    fieldbackground="white", relief="flat",
                    borderwidth=1, padding=5, bordercolor=C["border"])
        s.configure("TCombobox",
                    fieldbackground="white", relief="flat",
                    borderwidth=1, padding=4)
        s.configure("TScrollbar",
                    background=C["border"], troughcolor=C["bg"],
                    relief="flat", arrowsize=13)
        s.configure("TCheckbutton",
                    background=C["bg"], foreground=C["text"])
        s.configure("TRadiobutton",
                    background=C["bg"], foreground=C["text"])

        # Treeview 交替行颜色
        self.root.after(200, self._setup_tree_tags)

    def _setup_tree_tags(self):
        """设置 Treeview 交替行颜色"""
        if hasattr(self, "device_tree"):
            style = ttk.Style()
            style.configure("Treeview", rowheight=34)
            self.device_tree.tag_configure("odd",         background="#f4f7ff")
            self.device_tree.tag_configure("even",        background="#ffffff")
            self.device_tree.tag_configure("online",      foreground="#1b5e20", font=("PingFang SC", 11, "bold"))
            self.device_tree.tag_configure("offline",     foreground="#c62828")
            self.device_tree.tag_configure("placeholder", foreground="#aaaaaa")
            self.device_tree.tag_configure("checked_row", background="#bfdbfe", foreground="#1d4ed8")

    def _get_local_ip(self):
        """获取本机局域网IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _calculate_bridge_ip(self, host_ip, container_index):
        """计算桥接IP: 10.0.0.X → 10.0.1.((X-1)*10 + index)"""
        # 10.0.0.1 → 10.0.1.1-10.0.1.10
        # 10.0.0.2 → 10.0.1.11-10.0.1.20
        # 10.0.0.3 → 10.0.1.21-10.0.1.30
        try:
            parts = host_ip.split('.')
            if len(parts) == 4:
                host_last_octet = int(parts[3])
                return f"10.0.1.{(host_last_octet - 1) * 10 + container_index}"
        except:
            pass
        return None
    
    def _get_device_connection_info(self, device, config=None):
        """获取设备连接信息（IP和端口）
        
        :param device: 设备信息字典
        :param config: 容器配置字典（可选），用于判断桥接模式
        """
        host_ip = device.get("host_ip")
        container_ip = device.get("ip", "")
        instance_index = device.get("instance_index", 1)
        
        # 优先根据配置判断桥接模式（如果提供了配置）
        if config and config.get('useBridge', False):
            bridge_ip = self._calculate_bridge_ip(host_ip, instance_index)
            if bridge_ip:
                return bridge_ip, 9083, True
        
        # 桥接模式判断：容器IP为10.0.1.XX格式（兼容旧逻辑）
        if container_ip and container_ip.startswith("10.0.1."):
            bridge_ip = self._calculate_bridge_ip(host_ip, instance_index)
            if bridge_ip:
                return bridge_ip, 9083, True
        
        # 非桥接模式
        target_ip = host_ip or container_ip
        rpa_port = device.get("rpa_port") or (30000 + (instance_index - 1) * 100 + 2)
        return target_ip, rpa_port, False

    def _get_app_path(self):
        """获取应用程序路径（兼容打包后的exe）"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe，使用exe所在目录
            return os.path.dirname(sys.executable)
        else:
            # 如果是脚本运行，使用脚本所在目录
            return os.path.dirname(os.path.abspath(__file__))
    
    def setup_ui(self):
        """构建用户界面"""
        C = getattr(self, "_C", {})

        # ── 顶部品牌栏 ───────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C.get("header", "#1a237e"), height=56)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        # 左侧图标块
        icon_block = tk.Frame(header, bg=C.get("header2", "#283593"), width=56, height=56)
        icon_block.pack(side=tk.LEFT, fill=tk.Y)
        icon_block.pack_propagate(False)
        tk.Label(icon_block, text="⚡", bg=C.get("header2", "#283593"),
                 fg="white", font=("Arial", 22)).place(relx=0.5, rely=0.5, anchor="center")

        # 标题文字列
        title_col = tk.Frame(header, bg=C.get("header", "#1a237e"))
        title_col.pack(side=tk.LEFT, fill=tk.Y, padx=14, pady=8)
        tk.Label(title_col, text="测试工具",
                 bg=C.get("header", "#1a237e"), fg="white",
                 font=("PingFang SC", 15, "bold")).pack(anchor="w")
        tk.Label(title_col, text="Device Management & Automation Platform",
                 bg=C.get("header", "#1a237e"), fg="#90caf9",
                 font=("PingFang SC", 9)).pack(anchor="w")

        # 右侧版本标签
        right_info = tk.Frame(header, bg=C.get("header", "#1a237e"))
        right_info.pack(side=tk.RIGHT, padx=18, fill=tk.Y)
        tk.Label(right_info, text="v 1.0",
                 bg=C.get("header", "#1a237e"), fg="#90caf9",
                 font=("PingFang SC", 10)).pack(side=tk.BOTTOM, pady=8)

        # ── 主框架 ───────────────────────────────────────────────────
        main_frame = ttk.Frame(self.root, padding=6)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶级主选项卡
        self.root_notebook = ttk.Notebook(main_frame)
        self.root_notebook.pack(fill=tk.BOTH, expand=True)
        
        # ==================== Tab 1: 设备中心 ====================
        device_view = ttk.Frame(self.root_notebook)
        self.root_notebook.add(device_view, text=" 设备控制中心 ")
        
        # 主分割窗格 (PanedWindow) 用于左右调整
        self.paned_window = ttk.PanedWindow(device_view, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：设备列表
        left_frame = ttk.LabelFrame(self.paned_window, text="设备列表", padding=5)
        self.paned_window.add(left_frame, weight=1)
        
        # ADB 模式提示（network_entry 保留但不显示，供 save/load_config 兼容）
        net_frame = ttk.Frame(left_frame)
        net_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(net_frame, text="扫描模式:", foreground="gray").pack(side=tk.LEFT)
        ttk.Label(net_frame, text="ADB 已连接设备", foreground="#1a7abf", font=("", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.network_entry = ttk.Entry(net_frame)  # 不 pack，保持隐藏供 save/load_config 使用
        self.network_entry.insert(0, ", ".join(self.scan_networks))
        
        # 设备树形视图
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("选择", "序号", "设备昵称", "手机SN码", "状态")
        self.device_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # 设置列
        self.device_tree.heading("选择", text="⬜")
        self.device_tree.heading("序号", text="序号")
        self.device_tree.heading("设备昵称", text="设备昵称")
        self.device_tree.heading("手机SN码", text="手机SN码")
        self.device_tree.heading("状态", text="状态")
        
        self.device_tree.column("选择", width=40, anchor="center", minwidth=30)
        self.device_tree.column("序号", width=40, anchor="center", minwidth=30)
        self.device_tree.column("设备昵称", width=80, anchor="center", minwidth=60)
        self.device_tree.column("手机SN码", width=135, anchor="center", minwidth=100)
        self.device_tree.column("状态", width=60, anchor="center", minwidth=50)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 点击事件
        self.device_tree.bind("<Button-1>", self.on_treeview_click)
        self.device_tree.bind("<Double-Button-1>", self._on_device_name_double_click)
        self.device_tree.bind("<Button-3>", self.show_context_menu)
        
        # 拖放事件
        self.device_tree.drop_target_register(DND_FILES)
        self.device_tree.dnd_bind('<<Drop>>', self._on_file_drop)
        
        ttk.Label(left_frame, text="💡 提示: 拖放图片/APK到设备行可直接上传", foreground="gray").pack(anchor="w", pady=(5, 0))
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        self.scan_button = ttk.Button(btn_frame, text="🔍 扫描设备",
                                      command=self.scan_devices, width=15,
                                      style="Success.TButton")
        self.scan_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="☑ 全选/取消",
                   command=self.toggle_all_selection, width=12,
                   style="Muted.TButton").pack(side=tk.LEFT, padx=5)
        
        # 右侧：任务执行中心
        right_view = ttk.Frame(self.paned_window, padding=5)
        self.paned_window.add(right_view, weight=2)
        
        # 1.1 隐藏容器配置和代理配置（变量仍需存在，供 save/load 使用）
        _hidden_cc = ttk.Frame(self.root)
        self._setup_container_config(_hidden_cc)
        _hidden_s5 = ttk.Frame(self.root)
        self._setup_socks5_tab(_hidden_s5)

        # 1.2 主功能 Notebook（6个Tab）
        self.main_notebook = ttk.Notebook(right_view)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        _tab_script = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(_tab_script, text="脚本配置")
        _script_paned = ttk.PanedWindow(_tab_script, orient=tk.VERTICAL)
        _script_paned.pack(fill=tk.BOTH, expand=True)
        _script_top = ttk.Frame(_script_paned)
        _script_paned.add(_script_top, weight=1)
        _scroll_inner = self._make_scrollable_tab(_script_top)
        self._setup_custom_script_shortcut_bar(_scroll_inner)
        self._setup_open_app_bar(_scroll_inner)
        self._setup_coord_tap_bar(_scroll_inner)
        self._setup_input_text_bar(_scroll_inner)
        self._setup_click_text_bar(_scroll_inner)
        self._setup_push_file_bar(_scroll_inner)
        self._setup_pull_file_bar(_scroll_inner)
        self._setup_screenshot_bar(_scroll_inner)
        self._setup_install_apk_bar(_scroll_inner)
        self._setup_script_config_tab(_scroll_inner)
        _script_log_frame = ttk.LabelFrame(_script_paned, text="运行日志", padding=3)
        _script_paned.add(_script_log_frame, weight=0)
        self.script_log_text = scrolledtext.ScrolledText(
            _script_log_frame, height=3, width=40,
            font=("Menlo", 9),
            bg="#1e2433", fg="#a8c7fa",
            insertbackground="#a8c7fa",
            selectbackground="#2d4a7a",
            selectforeground="white",
            relief="flat", borderwidth=0,
        )
        self.script_log_text.pack(fill=tk.BOTH, expand=True)

        self._tab_custom_script = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(self._tab_custom_script, text="自定义脚本")
        self._build_custom_script_tab(self._tab_custom_script)

        _tab_douyin = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(_tab_douyin, text="1")
        self._build_platform_tab(_tab_douyin, "douyin")

        _tab_kuaishou = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(_tab_kuaishou, text="2")
        self._build_platform_tab(_tab_kuaishou, "kuaishou")

        _tab_xiaohongshu = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(_tab_xiaohongshu, text="3")
        self._build_platform_tab(_tab_xiaohongshu, "xiaohongshu")

        _tab_xianyu = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(_tab_xianyu, text="4")
        self._build_platform_tab(_tab_xianyu, "xianyu")

        _tab_log = ttk.Frame(self.main_notebook, padding=3)
        self.main_notebook.add(_tab_log, text="运行日志")
        self.log_text = scrolledtext.ScrolledText(
            _tab_log, height=15, width=40,
            font=("Menlo", 9),
            bg="#1e2433", fg="#a8c7fa",
            insertbackground="#a8c7fa",
            selectbackground="#2d4a7a",
            selectforeground="white",
            relief="flat", borderwidth=0,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 1.3 执行按钮栏（固定底部）
        btn_bar = ttk.Frame(right_view)
        btn_bar.pack(fill=tk.X, pady=(0, 2))
        ttk.Button(btn_bar, text="▶ 启动任务", command=self.run_selected_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bar, text="⏸ 暂停/继续", command=self.toggle_pause_selected_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bar, text="⏹ 停止任务", command=self.stop_selected_script).pack(side=tk.LEFT, padx=2)

        # ==================== Tab 2: 手机中心 ====================
        self.phone_tab = ttk.Frame(self.root_notebook, padding=10)
        self.root_notebook.add(self.phone_tab, text=" 更多功能 ")
        self._setup_phone_tab(self.phone_tab)
        #
        # # ==================== Tab 3: 邮箱中心 ====================
        # self.email_tab = ttk.Frame(self.root_notebook, padding=10)
        # self.root_notebook.add(self.email_tab, text=" 邮箱管理 ")
        # self._setup_email_tab(self.email_tab)
        #
        # # ==================== Tab 4: VISA卡管理 ====================
        # self.visa_tab = ttk.Frame(self.root_notebook, padding=10)
        # self.root_notebook.add(self.visa_tab, text=" VISA卡管理 ")
        # self._setup_visa_tab(self.visa_tab)
        
        # 状态栏
        self.status_var = tk.StringVar(value="  ●  就绪")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            bg="#1a237e", fg="#90caf9",
            font=("PingFang SC", 9),
            anchor="w", padx=12, pady=5,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # 设置左侧设备列表初始宽度（像素），渲染完成后生效
        self.root.after(100, lambda: self.paned_window.sashpos(0, 400))
    # ── 预置应用包名表 ──────────────────────────────────────────
    _PRESET_APPS = {
        "抖音":   "com.ss.android.ugc.aweme",
        "快手":   "com.smile.gifmaker",
        "小红书": "com.xingin.xhs",
        "闲鱼":  "com.taobao.idlefish",
        "微信":  "com.tencent.mm",
        "微博":  "com.sina.weibo",
        "淘宝":  "com.taobao.taobao",
        "拼多多": "com.xunmeng.pinduoduo",
    }

    def _setup_custom_script_shortcut_bar(self, parent):
        """脚本配置Tab：快捷跳转到自定义脚本Tab的横条"""
        bar = ttk.Frame(parent)
        bar.pack(fill=tk.X, pady=(0, 8), padx=2)
        btn = tk.Label(
            bar, text="✦  点击开始自定义脚本  ✦",
            font=("PingFang SC", 11, "bold"),
            bg="#3b5bdb", fg="white",
            cursor="hand2",
            padx=12, pady=8,
        )
        btn.pack(fill=tk.X, expand=True)
        btn.bind("<Button-1>", lambda e: self.main_notebook.select(self._tab_custom_script))
        btn.bind("<Enter>", lambda e: btn.configure(bg="#4c6ef5"))
        btn.bind("<Leave>", lambda e: btn.configure(bg="#3b5bdb"))

    def _build_custom_script_tab(self, parent):
        """自定义脚本Tab：可视化步骤脚本构建器"""
        self.custom_script_steps = []

        # ── 顶部工具栏（在 PanedWindow 外，固定不被压缩）──────
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 6))

        self._cs_add_btn = ttk.Button(toolbar, text="＋ 添加步骤", width=12,
                                      command=lambda: self._cs_show_add_menu(self.custom_script_steps, self._cs_add_btn))
        self._cs_add_btn.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(toolbar, text="⟳ 添加循环块", width=13,
                   command=lambda: self._cs_add_step(
                       {"type": "loop", "vars": {"count": tk.StringVar(value="3")}, "children": []},
                       self.custom_script_steps
                   )).pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(toolbar, text="清空", width=6,
                   command=self._cs_clear).pack(side=tk.RIGHT, padx=(0, 4))

        # ── PanedWindow：上=步骤列表，下=日志框 ────────────────
        paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # 上：可滚动步骤列表
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)

        _cs_bg = self._C.get("bg", "#f0f2f5")
        self._cs_canvas = tk.Canvas(list_frame, highlightthickness=0, bg=_cs_bg)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._cs_canvas.yview)
        self._cs_inner = ttk.Frame(self._cs_canvas)
        self._cs_inner.bind(
            "<Configure>",
            lambda e: self._cs_canvas.configure(scrollregion=self._cs_canvas.bbox("all"))
        )
        win_id = self._cs_canvas.create_window((0, 0), window=self._cs_inner, anchor="nw")
        self._cs_canvas.bind("<Configure>", lambda e: self._cs_canvas.itemconfig(win_id, width=e.width))
        self._cs_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._cs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def _on_cs_wheel(e):
            step = -1 if e.delta > 0 else 1
            self._cs_canvas.yview_scroll(step, "units")
        self._cs_canvas.bind("<Enter>", lambda e: self._cs_canvas.bind_all("<MouseWheel>", _on_cs_wheel))
        self._cs_canvas.bind("<Leave>", lambda e: self._cs_canvas.unbind_all("<MouseWheel>"))

        # 下：日志框（和脚本配置一致）
        self._add_tab_log_pane(paned)

        self._cs_render()

    # ── 步骤数据操作 ──────────────────────────────────────────

    def _cs_add_step(self, step, target):
        target.append(step)
        self._cs_render()
        self.save_config()

    def _cs_remove_step(self, lst, idx):
        lst.pop(idx)
        self._cs_render()
        self.save_config()

    def _cs_move_step(self, lst, idx, direction):
        new_idx = idx + direction
        if 0 <= new_idx < len(lst):
            lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
            self._cs_render()
            self.save_config()

    def _cs_clear(self):
        self.custom_script_steps.clear()
        self._cs_render()
        self.save_config()

    def _cs_show_add_menu(self, target, anchor_widget):
        menu = tk.Menu(anchor_widget.winfo_toplevel(), tearoff=0)
        types = [
            ("open_app",   "📱  打开App",     {"app": tk.StringVar(value="")}),
            ("tap_coord",  "👆  点击坐标",    {"x": tk.StringVar(value=""), "y": tk.StringVar(value="")}),
            ("tap_text",   "🔍  点击文案",    {"keyword": tk.StringVar(value="")}),
            ("input_text", "⌨️  输入文字",    {"content": tk.StringVar(value="")}),
            ("swipe",      "👋  页面滑动",    {"direction": tk.StringVar(value="向上"), "distance": tk.StringVar(value="500"), "count": tk.StringVar(value="1")}),
            ("wait",       "⏳  等待",        {"seconds": tk.StringVar(value="1")}),
            ("key_back",   "◀  按返回键",    {}),
            ("key_home",   "🏠  按Home键",   {}),
            ("key_menu",   "☰  按菜单键",    {}),
        ]
        for stype, label, default_vars in types:
            menu.add_command(
                label=label,
                command=lambda t=stype, v=default_vars: self._cs_add_step({"type": t, "vars": v}, target)
            )
        menu.post(anchor_widget.winfo_rootx(), anchor_widget.winfo_rooty() + anchor_widget.winfo_height())

    # ── 渲染 ──────────────────────────────────────────────────

    def _cs_render(self):
        for w in self._cs_inner.winfo_children():
            w.destroy()
        if not self.custom_script_steps:
            ttk.Label(self._cs_inner, text="点击「添加步骤」或「添加循环块」开始构建",
                      foreground="#9ca3af", font=("PingFang SC", 11)).pack(pady=50)
            return
        self._cs_render_list(self._cs_inner, self.custom_script_steps, indent=False)

    def _cs_render_list(self, container, steps, indent):
        for i, step in enumerate(steps):
            if step["type"] == "loop":
                self._cs_render_loop(container, step, i, steps, indent)
            else:
                self._cs_render_row(container, step, i, steps, indent)

    def _cs_render_row(self, container, step, idx, lst, indent):
        TYPE_INFO = {
            "open_app":   ("📱", "打开App"),
            "tap_coord":  ("👆", "点击坐标"),
            "tap_text":   ("🔍", "点击文案"),
            "input_text": ("⌨", "输入文字"),
            "swipe":      ("👋", "页面滑动"),
            "wait":       ("⏳", "等待"),
            "key_back":   ("◀", "按返回键"),
            "key_home":   ("🏠", "按Home键"),
            "key_menu":   ("☰", "按菜单键"),
        }
        icon, label = TYPE_INFO.get(step["type"], ("·", step["type"]))

        row = ttk.Frame(container)
        row.pack(fill=tk.X, pady=2, padx=(28 if indent else 6, 6))

        # 左侧：类型标签
        ttk.Label(row, text=f"{icon} {label}", width=11,
                  font=("PingFang SC", 10, "bold")).pack(side=tk.LEFT, padx=(0, 6))

        # 右侧按钮先占位，剩余空间才给参数框
        ttk.Button(row, text="↑", width=1, command=lambda: self._cs_move_step(lst, idx, -1)).pack(side=tk.RIGHT, padx=1)
        ttk.Button(row, text="↓", width=1, command=lambda: self._cs_move_step(lst, idx, 1)).pack(side=tk.RIGHT, padx=1)
        ttk.Button(row, text="×", width=1, command=lambda: self._cs_remove_step(lst, idx)).pack(side=tk.RIGHT, padx=1)
        ttk.Button(row, text="测试", width=4,
                   command=lambda s=step: self._cs_test_step(s)).pack(side=tk.RIGHT, padx=(1, 2))

        # 参数框填充剩余空间
        params = ttk.Frame(row)
        params.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._cs_render_params(params, step)

        ttk.Separator(container, orient="horizontal").pack(fill=tk.X, padx=(28 if indent else 6, 6), pady=1)

    def _cs_render_params(self, container, step):
        t = step["type"]
        v = step["vars"]
        if t == "open_app":
            apps = list(self._PRESET_APPS.keys()) + [a["name"] for a in self.custom_open_apps]
            cb = ttk.Combobox(container, textvariable=v["app"], values=apps, width=18, state="readonly")
            cb.pack(side=tk.LEFT, padx=2)
        elif t == "tap_coord":
            ttk.Label(container, text="X:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["x"], width=6).pack(side=tk.LEFT, padx=(2, 8))
            ttk.Label(container, text="Y:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["y"], width=6).pack(side=tk.LEFT, padx=2)
        elif t == "tap_text":
            ttk.Label(container, text="关键词:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["keyword"], width=22).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        elif t == "input_text":
            ttk.Label(container, text="内容:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["content"], width=22).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        elif t == "swipe":
            if "count" not in v:
                v["count"] = tk.StringVar(value="1")
            ttk.Label(container, text="方向:").pack(side=tk.LEFT)
            ttk.Combobox(container, textvariable=v["direction"],
                         values=["向上", "向下", "向左", "向右"], width=5, state="readonly").pack(side=tk.LEFT, padx=(2, 6))
            ttk.Label(container, text="距离:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["distance"], width=5).pack(side=tk.LEFT, padx=(2, 6))
            ttk.Label(container, text="次数:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["count"], width=3).pack(side=tk.LEFT, padx=2)
        elif t == "wait":
            ttk.Label(container, text="时长:").pack(side=tk.LEFT)
            ttk.Entry(container, textvariable=v["seconds"], width=6).pack(side=tk.LEFT, padx=2)
            ttk.Label(container, text="秒").pack(side=tk.LEFT)
        elif t in ("key_back", "key_home", "key_menu"):
            labels = {"key_back": "按下返回键", "key_home": "按下 Home 键", "key_menu": "按下菜单键"}
            ttk.Label(container, text=labels[t], foreground="#6b7280").pack(side=tk.LEFT)

        # 给所有输入变量加防抖自动保存 trace
        for sv in step.get("vars", {}).values():
            if isinstance(sv, tk.StringVar):
                sv.trace_add("write", lambda *_: self._cs_schedule_save())

    def _cs_schedule_save(self):
        if hasattr(self, "_cs_save_after_id"):
            self.root.after_cancel(self._cs_save_after_id)
        self._cs_save_after_id = self.root.after(800, self.save_config)

    def _cs_render_loop(self, container, step, idx, lst, indent):
        outer = tk.Frame(container, bg="#dbeafe", bd=1, relief="solid")
        outer.pack(fill=tk.X, pady=5, padx=(12 if indent else 4, 4))

        # 循环头
        header = tk.Frame(outer, bg="#bfdbfe")
        header.pack(fill=tk.X)
        tk.Label(header, text="🔄 循环", bg="#bfdbfe", fg="#1e40af",
                 font=("PingFang SC", 10, "bold")).pack(side=tk.LEFT, padx=(8, 4), pady=5)
        tk.Entry(header, textvariable=step["vars"]["count"], width=4,
                 font=("PingFang SC", 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(header, text="次", bg="#bfdbfe", fg="#1e40af").pack(side=tk.LEFT, padx=(0, 10))
        step["vars"]["count"].trace_add("write", lambda *_: self._cs_schedule_save())

        # 添加步骤按钮（在循环内）
        add_inner_btn = tk.Label(header, text="＋ 添加步骤", bg="#93c5fd", fg="#1e40af",
                                 cursor="hand2", padx=6, pady=3,
                                 font=("PingFang SC", 9))
        add_inner_btn.pack(side=tk.LEFT, padx=4)
        add_inner_btn.bind("<Button-1>",
                           lambda e, s=step, b=add_inner_btn: self._cs_show_add_menu(s["children"], b))
        add_inner_btn.bind("<Enter>", lambda e: add_inner_btn.configure(bg="#60a5fa"))
        add_inner_btn.bind("<Leave>", lambda e: add_inner_btn.configure(bg="#93c5fd"))

        # 删除循环
        del_btn = tk.Label(header, text="× 删除", bg="#fecaca", fg="#dc2626",
                           cursor="hand2", padx=6, pady=3,
                           font=("PingFang SC", 9))
        del_btn.pack(side=tk.RIGHT, padx=(4, 8))
        del_btn.bind("<Button-1>", lambda e: self._cs_remove_step(lst, idx))
        del_btn.bind("<Enter>", lambda e: del_btn.configure(bg="#fca5a5"))
        del_btn.bind("<Leave>", lambda e: del_btn.configure(bg="#fecaca"))

        # 上下移动
        up_lbl = tk.Label(header, text="↑", bg="#bfdbfe", fg="#1e40af", cursor="hand2",
                          font=("PingFang SC", 10))
        up_lbl.pack(side=tk.RIGHT, padx=2)
        up_lbl.bind("<Button-1>", lambda e: self._cs_move_step(lst, idx, -1))

        dn_lbl = tk.Label(header, text="↓", bg="#bfdbfe", fg="#1e40af", cursor="hand2",
                          font=("PingFang SC", 10))
        dn_lbl.pack(side=tk.RIGHT, padx=2)
        dn_lbl.bind("<Button-1>", lambda e: self._cs_move_step(lst, idx, 1))

        # 循环体
        body = tk.Frame(outer, bg="#eff6ff")
        body.pack(fill=tk.X, padx=0, pady=(0, 2))

        if step["children"]:
            self._cs_render_list(body, step["children"], indent=True)
        else:
            tk.Label(body, text="（循环内暂无步骤，点击「＋ 添加步骤」）",
                     bg="#dbeafe", fg="#6b9fd4",
                     font=("PingFang SC", 9)).pack(pady=8)

    # ── 执行逻辑 ──────────────────────────────────────────────

    def _cs_test_step(self, step):
        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return
        plain = self._cs_steps_to_plain([step])
        threading.Thread(target=self._cs_run_worker, args=(devices, plain), daemon=True).start()

    def _cs_run(self):
        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return
        if not self.custom_script_steps:
            messagebox.showwarning("提示", "请先添加步骤")
            return
        self._cs_stop_event.clear()
        self._cs_pause_event.clear()
        steps_snapshot = self._cs_steps_to_plain(self.custom_script_steps)
        threading.Thread(target=self._cs_run_worker, args=(devices, steps_snapshot), daemon=True).start()

    def _cs_steps_to_plain(self, steps):
        result = []
        for step in steps:
            d = {"type": step["type"], "vars": {k: sv.get() for k, sv in step.get("vars", {}).items()}}
            if step["type"] == "loop":
                d["children"] = self._cs_steps_to_plain(step["children"])
            result.append(d)
        return result

    def _cs_steps_from_plain(self, data):
        steps = []
        for d in data:
            step = {"type": d["type"], "vars": {k: tk.StringVar(value=str(v)) for k, v in d.get("vars", {}).items()}}
            if d["type"] == "loop":
                step["children"] = self._cs_steps_from_plain(d.get("children", []))
            steps.append(step)
        return steps

    def _cs_run_worker(self, devices, steps):
        for device in devices:
            if self._cs_stop_event.is_set():
                break
            serial = device.get("container_name", "").strip()
            self.log_message(f"▶ [{serial}] 开始执行自定义脚本")
            try:
                self._cs_exec_steps(serial, steps)
                self.log_message(f"✓ [{serial}] 自定义脚本执行完成")
            except InterruptedError:
                self.log_message(f"⏹ [{serial}] 自定义脚本已停止")
                break
            except Exception as ex:
                self.log_message(f"✗ [{serial}] 执行异常: {ex}")

    def _cs_exec_steps(self, serial, steps):
        import uiautomator2 as u2
        for step in steps:
            # 停止检查
            if self._cs_stop_event.is_set():
                raise InterruptedError("用户停止")
            # 暂停等待
            while self._cs_pause_event.is_set():
                if self._cs_stop_event.is_set():
                    raise InterruptedError("用户停止")
                time.sleep(0.2)
            t = step["type"]
            v = step.get("vars", {})
            if t == "open_app":
                pkg = self._PRESET_APPS.get(v.get("app", "")) or next(
                    (a["package"] for a in self.custom_open_apps if a["name"] == v.get("app")), None)
                if pkg:
                    subprocess.run(["adb", "-s", serial, "shell", "monkey", "-p", pkg,
                                    "-c", "android.intent.category.LAUNCHER", "1"],
                                   capture_output=True, timeout=10)
                    self.log_message(f"  📱 [{serial}] 打开 {v.get('app')}")
            elif t == "tap_coord":
                subprocess.run(["adb", "-s", serial, "shell", "input", "tap",
                                 str(v.get("x", "0")), str(v.get("y", "0"))],
                                capture_output=True, timeout=10)
                self.log_message(f"  👆 [{serial}] 点击 ({v.get('x')}, {v.get('y')})")
            elif t == "tap_text":
                kw = v.get("keyword", "")
                try:
                    d = u2.connect(serial)
                    el = d(textContains=kw)
                    if not el.exists:
                        el = d(descriptionContains=kw)
                    if el.exists:
                        el[0].click()
                        self.log_message(f"  🔍 [{serial}] 点击文案「{kw}」成功")
                    else:
                        self.log_message(f"  🔍 [{serial}] 未找到文案「{kw}」")
                except Exception as ex:
                    self.log_message(f"  🔍 [{serial}] 点击文案异常: {ex}")
            elif t == "input_text":
                content = v.get("content", "")
                try:
                    d = u2.connect(serial)
                    edit = d(className="android.widget.EditText")
                    if edit.exists:
                        edit.set_text(content)
                        self.log_message(f"  ⌨ [{serial}] 输入「{content}」")
                    else:
                        self.log_message(f"  ⌨ [{serial}] 未找到输入框")
                except Exception as ex:
                    self.log_message(f"  ⌨ [{serial}] 输入异常: {ex}")
            elif t == "swipe":
                direction = v.get("direction", "向上")
                dist = int(v.get("distance", "500"))
                repeat = max(1, int(v.get("count", "1")))
                swipe_map = {
                    "向上":  (540, 1200, 540, 1200 - dist),
                    "向下":  (540, 400, 540, 400 + dist),
                    "向左":  (800, 960, 800 - dist, 960),
                    "向右":  (200, 960, 200 + dist, 960),
                }
                x1, y1, x2, y2 = swipe_map.get(direction, (540, 1200, 540, 400))
                for i in range(repeat):
                    if self._cs_stop_event.is_set():
                        raise InterruptedError("用户停止")
                    subprocess.run(["adb", "-s", serial, "shell", "input", "swipe",
                                     str(x1), str(y1), str(x2), str(y2), "300"],
                                    capture_output=True, timeout=10)
                    if i < repeat - 1:
                        import random
                        time.sleep(random.uniform(1, 3))
                self.log_message(f"  👋 [{serial}] 页面{direction} {dist}px × {repeat}")
            elif t == "key_back":
                subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "4"],
                                capture_output=True, timeout=10)
                self.log_message(f"  ◀ [{serial}] 按返回键")
            elif t == "key_home":
                subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "3"],
                                capture_output=True, timeout=10)
                self.log_message(f"  🏠 [{serial}] 按Home键")
            elif t == "key_menu":
                subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "82"],
                                capture_output=True, timeout=10)
                self.log_message(f"  ☰ [{serial}] 按菜单键")
            elif t == "wait":
                secs = float(v.get("seconds", "1"))
                self.log_message(f"  ⏳ [{serial}] 等待 {secs}s")
                time.sleep(secs)
            elif t == "loop":
                count = int(v.get("count", "1"))
                self.log_message(f"  🔄 [{serial}] 循环开始 × {count}")
                for i in range(count):
                    self.log_message(f"  🔄 [{serial}] 第 {i+1}/{count} 次")
                    self._cs_exec_steps(serial, step["children"])
                self.log_message(f"  🔄 [{serial}] 循环结束")

    def _setup_open_app_bar(self, parent):
        """脚本配置Tab：打开App功能栏"""
        bar = ttk.LabelFrame(parent, text="打开 App", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 右侧：打开按钮（先pack保证靠右）
        open_btn = ttk.Button(bar, text="▶  打开", width=10,
                              command=self._open_app_action)
        open_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 右侧：间隔
        ttk.Label(bar, text="秒").pack(side=tk.RIGHT, padx=(2, 10))
        self.open_app_delay_var = tk.StringVar(value="3")
        ttk.Entry(bar, textvariable=self.open_app_delay_var, width=6).pack(side=tk.RIGHT)
        ttk.Label(bar, text="间隔:").pack(side=tk.RIGHT, padx=(10, 2))

        # 左侧：应用选择 + 自定义按钮（Combobox 填充剩余空间）
        ttk.Label(bar, text="应用:").pack(side=tk.LEFT, padx=(0, 4))
        self._open_app_combo_values = list(self._PRESET_APPS.keys()) + \
            [a["name"] for a in self.custom_open_apps]
        self.open_app_var = tk.StringVar(
            value=self._open_app_combo_values[0] if self._open_app_combo_values else "")
        self.open_app_combo = ttk.Combobox(
            bar, textvariable=self.open_app_var,
            values=self._open_app_combo_values,
            state="normal")
        self.open_app_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(bar, text="＋", width=3,
                   command=self._add_custom_open_app).pack(side=tk.LEFT)

    def _setup_coord_tap_bar(self, parent):
        """脚本配置Tab：坐标点击功能栏"""
        bar = ttk.LabelFrame(parent, text="坐标点击", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 右侧：点击按钮（先pack保证靠右）
        ttk.Button(bar, text="▶  点击", width=10,
                   command=self._coord_tap_action).pack(side=tk.RIGHT, padx=(10, 0))

        # 右侧：间隔
        ttk.Label(bar, text="ms").pack(side=tk.RIGHT, padx=(2, 10))
        self.coord_tap_delay_var = tk.StringVar(value="500")
        ttk.Entry(bar, textvariable=self.coord_tap_delay_var, width=6).pack(side=tk.RIGHT)
        ttk.Label(bar, text="间隔:").pack(side=tk.RIGHT, padx=(10, 2))

        # 左侧：X / Y 输入框（grid 均分列宽，保证等宽）
        self.coord_tap_x_var = tk.StringVar(value="")
        self.coord_tap_y_var = tk.StringVar(value="")
        xy_frame = ttk.Frame(bar)
        xy_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        xy_frame.columnconfigure(1, weight=1)
        xy_frame.columnconfigure(3, weight=1)
        ttk.Label(xy_frame, text="X:").grid(row=0, column=0, padx=(0, 2))
        ttk.Entry(xy_frame, textvariable=self.coord_tap_x_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Label(xy_frame, text="Y:").grid(row=0, column=2, padx=(0, 2))
        ttk.Entry(xy_frame, textvariable=self.coord_tap_y_var).grid(
            row=0, column=3, sticky="ew")

    def _coord_tap_action(self):
        """点击坐标点击按钮：通过 ADB 在所选设备上点击指定坐标"""
        try:
            x = int(self.coord_tap_x_var.get().strip())
            y = int(self.coord_tap_y_var.get().strip())
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的 X / Y 整数坐标")
            return

        try:
            delay_ms = float(self.coord_tap_delay_var.get() or "500")
        except ValueError:
            delay_ms = 500.0

        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return

        self.log_message(f"▶ 坐标点击 ({x}, {y})，共 {len(devices)} 台设备，间隔 {delay_ms:.0f}ms")

        def run():
            for idx, device in enumerate(devices):
                if idx > 0 and delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                serial = device.get("container_name", "").strip()
                try:
                    result = subprocess.run(
                        ["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        self.log_message(f"✓ [{serial}] 点击 ({x}, {y}) 成功")
                    else:
                        self.log_message(f"✗ [{serial}] 点击失败: {result.stderr.strip()}")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] 点击异常: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _setup_input_text_bar(self, parent):
        """脚本配置Tab：输入文字功能栏"""
        bar = ttk.LabelFrame(parent, text="输入文字", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 右侧：输入文字按钮（先pack保证靠右）
        ttk.Button(bar, text="▶  输入文字", width=12,
                   command=self._input_text_action).pack(side=tk.RIGHT, padx=(10, 0))

        # 右侧：间隔
        ttk.Label(bar, text="ms").pack(side=tk.RIGHT, padx=(2, 10))
        self.input_text_delay_var = tk.StringVar(value="500")
        ttk.Entry(bar, textvariable=self.input_text_delay_var, width=6).pack(side=tk.RIGHT)
        ttk.Label(bar, text="间隔:").pack(side=tk.RIGHT, padx=(10, 2))

        # 左侧：内容输入框（填充剩余空间）
        ttk.Label(bar, text="内容:").pack(side=tk.LEFT, padx=(0, 4))
        self.input_text_var = tk.StringVar(value="")
        ttk.Entry(bar, textvariable=self.input_text_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True)

    def _input_text_action(self):
        """输入文字按钮：用 uiautomator2 找到第一个 EditText 并 set_text"""
        text = self.input_text_var.get()
        if not text:
            messagebox.showwarning("提示", "请输入要输入的文字内容")
            return

        try:
            delay_ms = float(self.input_text_delay_var.get() or "500")
        except ValueError:
            delay_ms = 500.0

        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return

        self.log_message(f"▶ 输入文字，共 {len(devices)} 台设备，间隔 {delay_ms:.0f}ms")

        def run():
            try:
                import uiautomator2 as u2
            except ImportError:
                self.log_message("✗ 未安装 uiautomator2，请先执行: pip install uiautomator2")
                return

            for idx, device in enumerate(devices):
                if idx > 0 and delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                serial = device.get("container_name", "").strip()
                try:
                    d = u2.connect(serial)
                    edit = d(className="android.widget.EditText")
                    if not edit.exists:
                        self.log_message(f"✗ [{serial}] 未找到 EditText 控件")
                        continue
                    edit.set_text(text)
                    self.log_message(f"✓ [{serial}] 已输入文字")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] 输入失败: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _setup_click_text_bar(self, parent):
        """脚本配置Tab：点击文字功能栏"""
        bar = ttk.LabelFrame(parent, text="点击文字", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 右侧：按钮
        ttk.Button(bar, text="▶  点击文字", width=12,
                   command=self._click_text_action).pack(side=tk.RIGHT, padx=(10, 0))

        # 右侧：间隔
        ttk.Label(bar, text="ms").pack(side=tk.RIGHT, padx=(2, 10))
        self.click_text_delay_var = tk.StringVar(value="500")
        ttk.Entry(bar, textvariable=self.click_text_delay_var, width=6).pack(side=tk.RIGHT)
        ttk.Label(bar, text="间隔:").pack(side=tk.RIGHT, padx=(10, 2))

        # 左侧：内容输入框
        ttk.Label(bar, text="内容:").pack(side=tk.LEFT, padx=(0, 4))
        self.click_text_var = tk.StringVar(value="")
        ttk.Entry(bar, textvariable=self.click_text_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True)

    def _click_text_action(self):
        """点击文字按钮：u2 找 text/desc 包含输入内容的第一个元素并点击"""
        keyword = self.click_text_var.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入要点击的文字内容")
            return

        try:
            delay_ms = float(self.click_text_delay_var.get() or "500")
        except ValueError:
            delay_ms = 500.0

        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return

        self.log_message(f"▶ 点击文字 [{keyword}]，共 {len(devices)} 台设备，间隔 {delay_ms:.0f}ms")

        def run():
            try:
                import uiautomator2 as u2
            except ImportError:
                self.log_message("✗ 未安装 uiautomator2，请先执行: pip install uiautomator2")
                return

            for idx, device in enumerate(devices):
                if idx > 0 and delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                serial = device.get("container_name", "").strip()
                try:
                    d = u2.connect(serial)
                    # 优先匹配 text 包含，再匹配 description 包含
                    el = d(textContains=keyword)
                    if not el.exists:
                        el = d(descriptionContains=keyword)
                    if not el.exists:
                        self.log_message(f"✗ [{serial}] 未找到包含 [{keyword}] 的元素")
                        continue
                    el[0].click()
                    self.log_message(f"✓ [{serial}] 已点击包含 [{keyword}] 的元素")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] 点击失败: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _add_custom_open_app(self):
        """把 Combobox 当前输入内容作为自定义应用保存"""
        val = self.open_app_var.get().strip()
        if not val:
            return
        existing_names = set(self._PRESET_APPS.keys()) | \
                         {a["name"] for a in self.custom_open_apps}
        if val in existing_names:
            messagebox.showinfo("提示", f'"{val}" 已在列表中')
            return
        # 如果输入的像包名（含"."）就当包名，否则名字=包名
        entry = {"name": val, "package": val}
        self.custom_open_apps.append(entry)
        self._open_app_combo_values = list(self._PRESET_APPS.keys()) + \
            [a["name"] for a in self.custom_open_apps]
        self.open_app_combo["values"] = self._open_app_combo_values
        self.save_config()
        self.log_message(f"✓ 已添加应用: {val}")

    def _find_package_by_name(self, d, app_name):
        """通过应用名在设备上找到真实包名，再由调用方 app_start(package)。
        uiautomator2 app_start() 只接受包名，无法直接传应用名。
        预置应用走映射表（快）；其余用一条 shell 命令批量查 label。
        返回 package_name 或 None。"""
        # 预置映射直接返回
        if app_name in self._PRESET_APPS:
            return self._PRESET_APPS[app_name]

        # 用 cmd package 一次性拿到所有 launcher 应用的包名+label
        # 比逐个 app_info() 快很多
        try:
            raw = d.shell(
                "cmd package query-activities"
                " -a android.intent.action.MAIN"
                " -c android.intent.category.LAUNCHER"
                " --brief"
            )
            raw = getattr(raw, "output", raw) if not isinstance(raw, str) else raw

            app_lower = app_name.lower()
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith("No") or "/" not in line:
                    continue
                pkg = line.split("/")[0].strip()
                if not pkg:
                    continue
                try:
                    label = (d.app_info(pkg).get("label") or "").strip()
                    if label.lower() == app_lower or app_lower in label.lower():
                        return pkg
                except Exception:
                    continue
        except Exception:
            pass

        return None

    def _open_app_action(self):
        """点击打开按钮：用 uiautomator2 在所选设备上启动应用"""
        app_name = self.open_app_var.get().strip()
        if not app_name:
            messagebox.showwarning("提示", "请先选择或输入要打开的应用")
            return

        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return

        try:
            delay = float(self.open_app_delay_var.get() or "3")
        except ValueError:
            delay = 3.0

        self.log_message(f"▶ 开始打开 [{app_name}]，共 {len(devices)} 台设备，间隔 {delay}s")

        def run():
            try:
                import uiautomator2 as u2
            except ImportError:
                self.log_message("✗ 未安装 uiautomator2，请先执行: pip install uiautomator2")
                return

            for idx, device in enumerate(devices):
                if idx > 0 and delay > 0:
                    time.sleep(delay)
                serial = device.get("container_name", "").strip()
                try:
                    d = u2.connect(serial)
                    package = self._find_package_by_name(d, app_name)
                    if not package:
                        self.log_message(f"✗ [{serial}] 未找到应用 '{app_name}'，请确认设备已安装该应用")
                        continue
                    d.app_start(package)
                    self.log_message(f"✓ [{serial}] 已打开 {app_name}")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] 打开失败: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _make_scrollable_tab(self, parent):
        """在 Tab Frame 内创建可滚动区域，返回内层 Frame 供子 setup 方法填充"""
        bg = self._C.get("bg", "#f0f2f5")
        canvas = tk.Canvas(parent, highlightthickness=0, bg=bg)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 鼠标进入区域时绑定滚轮，离开时解绑，避免干扰其他滚动区域
        def _on_wheel(e):
            # macOS delta 为 ±1，Windows 为 ±120，统一处理
            step = -1 if e.delta > 0 else 1
            canvas.yview_scroll(step, "units")

        def _bind_wheel(e):
            canvas.bind_all("<MouseWheel>", _on_wheel)

        def _unbind_wheel(e):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        inner.bind("<Enter>", _bind_wheel)
        inner.bind("<Leave>", _unbind_wheel)

        return inner

    def _add_tab_log_pane(self, paned):
        """向 PanedWindow 添加日志区，注册到广播列表，返回 ScrolledText"""
        log_frame = ttk.LabelFrame(paned, text="运行日志", padding=3)
        paned.add(log_frame, weight=0)
        lt = scrolledtext.ScrolledText(
            log_frame, height=3, width=40,
            font=("Menlo", 9),
            bg="#1e2433", fg="#a8c7fa",
            insertbackground="#a8c7fa",
            selectbackground="#2d4a7a",
            selectforeground="white",
            relief="flat", borderwidth=0,
        )
        lt.pack(fill=tk.BOTH, expand=True)
        self._tab_log_texts.append(lt)
        return lt

    def _build_platform_tab(self, parent, prefix, count=5):
        """为平台 Tab 创建 count 个通用配置行，StringVar 存为 self.{prefix}_cfg{N}"""
        paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(paned)
        paned.add(top, weight=1)

        for i in range(1, count + 1):
            var = tk.StringVar()
            setattr(self, f"{prefix}_cfg{i}", var)
            row = ttk.Frame(top)
            row.pack(fill=tk.X, pady=5, padx=8)
            ttk.Label(row, text=f"配置{i}:", width=8, anchor="w").pack(side=tk.LEFT)
            e = ttk.Entry(row, textvariable=var)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True)
            e.bind("<FocusOut>", lambda ev: self.save_config())
            e.bind("<Return>", lambda ev: self.save_config())

        self._add_tab_log_pane(paned)

    def _setup_socks5_tab(self, parent):
        """Web UI: SOCKS5配置Tab"""
        ttk.Label(parent, text="代理 (IP:端口:账号:密码):").pack(anchor="w")
        self.proxy_entry = ttk.Entry(parent, width=35)
        self.proxy_entry.pack(fill=tk.X, pady=2)
        # （按需求去掉示例文案）
        
        # 本地监听IP配置 + 国家代码
        ttk.Label(parent, text="本地监听IP (例如: 10.0.3.222):").pack(anchor="w", pady=(5, 0))
        listen_row = ttk.Frame(parent)
        listen_row.pack(fill=tk.X, pady=2)
        self.local_ip_entry = ttk.Entry(listen_row, width=20)
        self.local_ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=False)
        ttk.Label(listen_row, text="  国家代码:").pack(side=tk.LEFT, padx=(12, 2))
        self.proxy_country_code_entry = ttk.Entry(listen_row, width=8)
        self.proxy_country_code_entry.pack(side=tk.LEFT, padx=0)
        ttk.Label(listen_row, text="(如 US/HK)", foreground="gray").pack(side=tk.LEFT, padx=2)

        # Auto-save triggers
        self.local_ip_entry.bind("<FocusOut>", lambda e: self.save_config())
        self.local_ip_entry.bind("<Return>", lambda e: self.save_config())
        self.proxy_country_code_entry.bind("<FocusOut>", lambda e: self.save_config())
        self.proxy_country_code_entry.bind("<Return>", lambda e: self.save_config())

        # StormProxies 模式选择
        self.storm_proxy_var = tk.IntVar(value=0)
        self.storm_proxy_var.trace_add("write", lambda *args: self.save_config())
        chk_storm = ttk.Checkbutton(parent, text="使用StormProxies代理", variable=self.storm_proxy_var)
        chk_storm.pack(anchor="w", pady=(5, 0))

        # VPC节点输入框（用于设置域名屏蔽）
        ttk.Label(parent, text="VPC节点 (VLESS链接或配置):").pack(anchor="w", pady=(5, 0))
        self.vpc_node_entry = ttk.Entry(parent, width=35)
        self.vpc_node_entry.pack(fill=tk.X, pady=2)
        self.vpc_node_entry.bind("<FocusOut>", lambda e: self.save_config())
        self.vpc_node_entry.bind("<Return>", lambda e: self.save_config())

        ttk.Label(parent, text="域名过滤 (逗号分隔):").pack(anchor="w", pady=(5,0))
        self.domain_text = tk.Text(parent, height=8, width=35)
        self.domain_text.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # 增加一些按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="✅ 启用代理", command=self.set_socks5_proxy).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(btn_frame, text="🚫 停止代理", command=self.stop_socks5_proxy).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    def _setup_push_file_bar(self, parent):
        """脚本配置Tab：Push文件到手机（两行布局）"""
        bar = ttk.LabelFrame(parent, text="往手机推送文件 (Push)", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 第一行：本地文件
        row1 = ttk.Frame(bar)
        row1.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(row1, text="选择文件", width=8,
                   command=self._push_select_file).pack(side=tk.RIGHT)
        ttk.Label(row1, text="本地文件:").pack(side=tk.LEFT, padx=(0, 4))
        self.push_local_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.push_local_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        # 第二行：手机目录 + Push按钮
        row2 = ttk.Frame(bar)
        row2.pack(fill=tk.X)
        ttk.Button(row2, text="▶  Push", width=10,
                   command=self._push_file_action).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(row2, text="手机目录:").pack(side=tk.LEFT, padx=(0, 4))
        self.push_remote_var = tk.StringVar(value="")
        ttk.Entry(row2, textvariable=self.push_remote_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Label(row2, text="(空=默认/sdcard/)", foreground="#9ca3af").pack(side=tk.LEFT)

    def _push_select_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="选择要 Push 的文件")
        if path:
            self.push_local_var.set(path)

    def _push_file_action(self):
        local = self.push_local_var.get().strip()
        if not local:
            messagebox.showwarning("提示", "请先选择本地文件")
            return
        remote = self.push_remote_var.get().strip() or "/sdcard/"
        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return
        self.log_message(f"▶ Push「{local}」→ {remote}，共 {len(devices)} 台设备")

        def run():
            for device in devices:
                serial = device.get("container_name", "").strip()
                try:
                    if remote not in ("/sdcard/", "/sdcard"):
                        subprocess.run(["adb", "-s", serial, "shell", "mkdir", "-p", remote],
                                       capture_output=True, timeout=15)
                    result = subprocess.run(["adb", "-s", serial, "push", local, remote],
                                            capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        self.log_message(f"✓ [{serial}] Push 成功")
                    else:
                        self.log_message(f"✗ [{serial}] Push 失败: {result.stderr.strip()}")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] Push 异常: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _setup_pull_file_bar(self, parent):
        """脚本配置Tab：从手机拉取文件（两行布局）"""
        bar = ttk.LabelFrame(parent, text="从手机拉取文件 (Pull)", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 第一行：手机文件路径
        row1 = ttk.Frame(bar)
        row1.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(row1, text="手机文件:").pack(side=tk.LEFT, padx=(0, 4))
        self.pull_remote_var = tk.StringVar(value="/sdcard/")
        ttk.Entry(row1, textvariable=self.pull_remote_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 第二行：本地保存目录 + Pull按钮
        row2 = ttk.Frame(bar)
        row2.pack(fill=tk.X)
        ttk.Button(row2, text="▶  Pull", width=10,
                   command=self._pull_file_action).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(row2, text="选择文件夹", width=9,
                   command=self._pull_select_dir).pack(side=tk.RIGHT, padx=(0, 4))
        ttk.Label(row2, text="保存到:").pack(side=tk.LEFT, padx=(0, 4))
        self.pull_local_var = tk.StringVar(value="")
        ttk.Entry(row2, textvariable=self.pull_local_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

    def _pull_select_dir(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="选择本地保存目录")
        if path:
            self.pull_local_var.set(path)

    def _pull_file_action(self):
        remote = self.pull_remote_var.get().strip()
        if not remote:
            messagebox.showwarning("提示", "请输入手机上的文件路径")
            return
        local = self.pull_local_var.get().strip() or "."
        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return
        self.log_message(f"▶ Pull「{remote}」→「{local}」，共 {len(devices)} 台设备")

        def run():
            for device in devices:
                serial = device.get("container_name", "").strip()
                try:
                    result = subprocess.run(["adb", "-s", serial, "pull", remote, local],
                                            capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        self.log_message(f"✓ [{serial}] Pull 成功 → {local}")
                    else:
                        self.log_message(f"✗ [{serial}] Pull 失败: {result.stderr.strip()}")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] Pull 异常: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _setup_screenshot_bar(self, parent):
        """脚本配置Tab：截图并拉取到本地"""
        bar = ttk.LabelFrame(parent, text="截图", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        # 右侧按钮先占位
        ttk.Button(bar, text="▶  截图", width=10,
                   command=self._screenshot_action).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(bar, text="选择目录", width=8,
                   command=self._screenshot_select_dir).pack(side=tk.RIGHT, padx=(0, 4))

        ttk.Label(bar, text="保存到:").pack(side=tk.LEFT, padx=(0, 4))
        self.screenshot_dir_var = tk.StringVar(value="")
        ttk.Entry(bar, textvariable=self.screenshot_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Label(bar, text="(空=当前目录)", foreground="#9ca3af").pack(side=tk.LEFT)

    def _screenshot_select_dir(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="选择截图保存目录")
        if path:
            self.screenshot_dir_var.set(path)

    def _screenshot_action(self):
        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return
        save_dir = self.screenshot_dir_var.get().strip() or "."
        self.log_message(f"▶ 截图，共 {len(devices)} 台设备，保存至「{save_dir}」")

        def run():
            import time as _time
            for device in devices:
                serial = device.get("container_name", "").strip()
                remote_path = f"/sdcard/_screenshot_{serial}_{int(_time.time())}.png"
                try:
                    # 截图
                    r1 = subprocess.run(
                        ["adb", "-s", serial, "shell", "screencap", "-p", remote_path],
                        capture_output=True, timeout=15
                    )
                    if r1.returncode != 0:
                        self.log_message(f"✗ [{serial}] 截图失败")
                        continue
                    # Pull 到本地
                    r2 = subprocess.run(
                        ["adb", "-s", serial, "pull", remote_path, save_dir],
                        capture_output=True, text=True, timeout=30
                    )
                    # 删除手机上的临时截图
                    subprocess.run(
                        ["adb", "-s", serial, "shell", "rm", remote_path],
                        capture_output=True, timeout=10
                    )
                    if r2.returncode == 0:
                        self.log_message(f"✓ [{serial}] 截图已保存到「{save_dir}」")
                    else:
                        self.log_message(f"✗ [{serial}] Pull 截图失败: {r2.stderr.strip()}")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] 截图异常: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _setup_install_apk_bar(self, parent):
        """脚本配置Tab：安装 APK"""
        bar = ttk.LabelFrame(parent, text="安装应用 (APK)", padding=(8, 8))
        bar.pack(fill=tk.X, pady=(0, 6), padx=2)

        ttk.Button(bar, text="▶  安装", width=10,
                   command=self._install_apk_action).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(bar, text="选择 APK", width=9,
                   command=self._install_apk_select).pack(side=tk.RIGHT, padx=(0, 4))
        ttk.Label(bar, text="APK:").pack(side=tk.LEFT, padx=(0, 4))
        self.install_apk_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.install_apk_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _install_apk_select(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="选择 APK 文件", filetypes=[("APK 文件", "*.apk"), ("所有文件", "*.*")])
        if path:
            self.install_apk_var.set(path)

    def _install_apk_action(self):
        apk = self.install_apk_var.get().strip()
        if not apk:
            messagebox.showwarning("提示", "请先选择 APK 文件")
            return
        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选要操作的设备")
            return
        self.log_message(f"▶ 安装「{apk}」，共 {len(devices)} 台设备")

        def run():
            for device in devices:
                serial = device.get("container_name", "").strip()
                try:
                    result = subprocess.run(
                        ["adb", "-s", serial, "install", "-r", apk],
                        capture_output=True, text=True, timeout=120
                    )
                    output = (result.stdout + result.stderr).strip()
                    if result.returncode == 0 and "Success" in output:
                        self.log_message(f"✓ [{serial}] 安装成功")
                    else:
                        self.log_message(f"✗ [{serial}] 安装失败: {output}")
                except Exception as e:
                    self.log_message(f"✗ [{serial}] 安装异常: {e}")

        threading.Thread(target=run, daemon=True).start()

    def _setup_script_config_tab(self, parent):
        """Web UI: 脚本配置Tab（只保留昵称设置，其余变量静默初始化供 save_config 使用）"""
        # 昵称设置（显示）
        lang_frame = ttk.LabelFrame(parent, text="昵称设置", padding=5)
        lang_frame.pack(fill=tk.X, pady=(0, 5))
        self.name_lang_var = tk.StringVar(value="中文")
        ttk.Label(lang_frame, text="昵称设置:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(lang_frame, text="中文", variable=self.name_lang_var, value="中文").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(lang_frame, text="英文", variable=self.name_lang_var, value="英文").pack(side=tk.LEFT, padx=5)
        self.name_lang_var.trace_add("write", lambda *args: self.save_config())

        # 以下变量供 save_config / load_config 使用，不创建可见 UI
        _h = ttk.Frame(parent)   # 隐藏容器，不 pack，仅作为 Entry 的 master
        self.country_entry        = ttk.Entry(_h); self.country_entry.insert(0, "")
        self.char_mode_var        = tk.IntVar(value=0)
        self.pwd_mode_var         = tk.StringVar(value="prefix")
        self.pwd_prefix_entry     = ttk.Entry(_h)
        self.pwd_custom_entry     = ttk.Entry(_h)
        self.skip_count_entry     = ttk.Entry(_h); self.skip_count_entry.insert(0, "0")
        self.tiktok_mode_var      = tk.StringVar(value="phone")
        self.jump_mode_var        = tk.IntVar(value=0)
        self.channel3_mode_var    = tk.IntVar(value=0)
        self.channel1_mode_var    = tk.IntVar(value=0)
        self.accessibility_mode_var   = tk.IntVar(value=0)
        self.authorized_enterprise_var = tk.IntVar(value=0)
        self.upload_platform_var  = tk.IntVar(value=0)

    def _open_platform_phone_dialog(self):
        """平台取号配置弹窗：选择平台/输入key/参数"""
        win = tk.Toplevel(self.root)
        win.title("平台取号配置")
        win.geometry("420x260")
        win.transient(self.root)
        win.grab_set()

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        r1 = ttk.Frame(frm)
        r1.pack(fill=tk.X, pady=4)
        ttk.Label(r1, text="平台:").pack(side=tk.LEFT)
        cb = ttk.Combobox(r1, textvariable=self.platform_name_var, state="readonly", values=["tg"], width=10)
        cb.pack(side=tk.LEFT, padx=8)

        r2 = ttk.Frame(frm)
        r2.pack(fill=tk.X, pady=4)
        ttk.Label(r2, text="API Key:").pack(side=tk.LEFT)
        ekey = ttk.Entry(r2, textvariable=self.platform_api_key_var, show="*", width=32)
        ekey.pack(side=tk.LEFT, padx=8)

        r3 = ttk.Frame(frm)
        r3.pack(fill=tk.X, pady=4)
        ttk.Label(r3, text="country:").pack(side=tk.LEFT)
        ttk.Entry(r3, textvariable=self.platform_country_var, width=10).pack(side=tk.LEFT, padx=8)
        ttk.Label(r3, text="service:").pack(side=tk.LEFT)
        ttk.Entry(r3, textvariable=self.platform_service_var, width=10).pack(side=tk.LEFT, padx=8)

        r4 = ttk.Frame(frm)
        r4.pack(fill=tk.X, pady=4)
        ttk.Label(r4, text="providerIds:").pack(side=tk.LEFT)
        ttk.Entry(r4, textvariable=self.platform_provider_ids_var, width=12).pack(side=tk.LEFT, padx=8)
        # （按需求去掉示例文案）

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, pady=(12, 0))

        def on_ok():
            self.save_config()
            win.destroy()

        ttk.Button(btns, text="保存", command=on_ok).pack(side=tk.RIGHT)
        ttk.Button(btns, text="关闭", command=win.destroy).pack(side=tk.RIGHT, padx=8)

    def _platform_get_phone(self):
        """
        tg平台取号（Tiger SMS）
        返回: (phone, url)；url 为 getStatus 轮询链接，脚本可直接用它取验证码
        """
        platform = (self.platform_name_var.get() or "tg").strip().lower()
        if platform != "tg":
            return None, None

        api_key = (self.platform_api_key_var.get() or "").strip()
        if not api_key:
            self.log_message("⚠️ 平台取号失败：未配置API Key")
            return None, None

        country = (self.platform_country_var.get() or "187").strip()
        service = (self.platform_service_var.get() or "wb").strip()
        provider_ids = (self.platform_provider_ids_var.get() or "").strip()

        base = "https://api.tiger-sms.com/stubs/handler_api.php"
        params = {
            "api_key": api_key,
            "action": "getNumber",
            "service": service,
            "country": country,
        }
        if provider_ids:
            params["providerIds"] = provider_ids

        try:
            resp = requests.get(base, params=params, timeout=20)
            text = (resp.text or "").strip()
            # 期望：ACCESS_NUMBER:ACT_ID:PHONE
            if not text.startswith("ACCESS_NUMBER:"):
                self.log_message(f"⚠️ 平台取号返回异常: {text}")
                return None, None

            parts = text.split(":")
            if len(parts) < 3:
                self.log_message(f"⚠️ 平台取号解析失败: {text}")
                return None, None

            act_id = parts[1].strip()
            phone = parts[2].strip()
            status_url = f"{base}?api_key={api_key}&action=getStatus&id={act_id}"

            # 留痕：记录到手机号管理（不参与分发，因为已启用平台取号）
            try:
                with self.phone_lock:
                    self.phones.append({
                        "phone": phone,
                        "url": status_url,
                        "usage": "已使用",
                        "status": "未成功",
                        "time": ""
                    })
                if hasattr(self, 'phone_tree'):
                    self.root.after(0, lambda: self._refresh_phone_tree(self.phone_tree))
                self.root.after(0, self.save_config)
            except Exception:
                pass

            return phone, status_url
        except Exception as e:
            self.log_message(f"⚠️ 平台取号请求异常: {e}")
            return None, None

    def _setup_container_config(self, parent):
        """容器配置区（常显）"""
        # 在线机型数据将从设备获取
        self.model_presets = {}  # 由 sync_online_models 填充
        self.region_presets = {
            "美国 (USA) (默认)": {"tz": "America/New_York", "cc": "US"},
            "中国 (China)": {"tz": "Asia/Shanghai", "cc": "CN"},
            "香港 (Hong Kong)": {"tz": "Asia/Hong_Kong", "cc": "HK"},
            "日本 (Japan)": {"tz": "Asia/Tokyo", "cc": "JP"},
            "英国 (UK)": {"tz": "Europe/London", "cc": "GB"}
        }
        self.online_models = {}  # 存储真实机型列表数据 {name: id}
        
        # 第一行: DNS + 机型
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="DNS:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_dns = ttk.Entry(row1, width=12)
        self.entry_dns.insert(0, "8.8.8.8")
        self.entry_dns.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row1, text="机型:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_model = ttk.Combobox(row1, width=18, values=[])  # 初始为空，扫描后自动填充
        self.entry_model.pack(side=tk.LEFT)
        self.entry_model.bind("<<ComboboxSelected>>", self._on_model_selected)
        ttk.Button(row1, text="同步在线机型", command=self.sync_online_models).pack(side=tk.LEFT, padx=5)
        
        # 第二行: 地区 + GMS + 随机机型
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="地区:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_region = ttk.Combobox(row2, width=18, values=list(self.region_presets.keys()))
        self.entry_region.current(0)  # Default: USA
        self.entry_region.pack(side=tk.LEFT, padx=(0, 15))
        
        self.gms_var = tk.IntVar(value=0)
        chk_gms = tk.Checkbutton(row2, text="GMS", variable=self.gms_var, bg='#f0f0f0')
        chk_gms.pack(side=tk.LEFT, padx=(0, 15))
        
        self.random_model_var = tk.IntVar(value=0)
        chk_random = tk.Checkbutton(row2, text="随机机型", variable=self.random_model_var, bg='#f0f0f0', command=self._on_random_model_toggle)
        chk_random.pack(side=tk.LEFT, padx=(0, 15))
        
        # 指定随机机型 (Checkbox，从用户输入的机型列表中随机)
        self.static_model_var = tk.IntVar(value=0)
        self.chk_static = tk.Checkbutton(row2, text="指定随机机型", variable=self.static_model_var, bg='#f0f0f0', command=self._toggle_static_model_entry)
        self.chk_static.pack(side=tk.LEFT, padx=(0, 5))
        
        # 指定随机机型输入框容器（初始隐藏）
        self.custom_model_frame = ttk.Frame(row2)
        tk.Label(self.custom_model_frame, text="机型:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        self.custom_model_list_var = tk.StringVar(value="")
        self.entry_custom_models = ttk.Entry(self.custom_model_frame, textvariable=self.custom_model_list_var, width=30)
        self.entry_custom_models.pack(side=tk.LEFT, padx=(0, 15))
        self.entry_custom_models.bind("<FocusOut>", lambda e: self.save_config())
        self.entry_custom_models.bind("<Return>", lambda e: self.save_config())
        self.custom_model_frame.pack_forget()  # 初始隐藏
        
        # 绑定 trace 以便保存配置状态
        self.static_model_var.trace_add("write", lambda *args: self.save_config())
        
        # 第三行: 重建容器模式选择 + 桥接模式
        row3 = ttk.Frame(parent)
        row3.pack(fill=tk.X, pady=2)

        # 重建容器模式下拉选择
        tk.Label(row3, text="重建容器:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        self.rebuild_mode_var = tk.StringVar(value="不重建")
        rebuild_combo = ttk.Combobox(row3, textvariable=self.rebuild_mode_var, width=18, state="readonly")
        rebuild_combo['values'] = (
            "不重建",
            "重建容器(删除创建)",
            "不删除重建（成功保留/失败删除）"
        )
        rebuild_combo.pack(side=tk.LEFT, padx=(0, 10))
        rebuild_combo.bind("<<ComboboxSelected>>", lambda e: self._on_rebuild_mode_changed())

        # 失败次数输入框（用于"不删除重建"模式：连续失败几次后删除并重建）
        tk.Label(row3, text="失败次数:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        self.max_failures_var = tk.StringVar(value="3")
        entry_max_failures = ttk.Entry(row3, textvariable=self.max_failures_var, width=5)
        entry_max_failures.pack(side=tk.LEFT, padx=(0, 15))
        entry_max_failures.bind("<FocusOut>", lambda e: self.save_config())
        entry_max_failures.bind("<Return>", lambda e: self.save_config())
        
        # 桥接模式选项
        self.bridge_mode_var = tk.IntVar(value=0)
        chk_bridge = tk.Checkbutton(row3, text="桥接模式 (独立IP)", variable=self.bridge_mode_var, bg='#f0f0f0')
        chk_bridge.pack(side=tk.LEFT, padx=(0, 15))
        
        # 镜像版本输入框（在桥接模式右侧）
        tk.Label(row3, text="镜像版本:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        self.image_version_var = tk.StringVar(value="")
        entry_image_version = ttk.Entry(row3, textvariable=self.image_version_var, width=15)
        entry_image_version.pack(side=tk.LEFT, padx=(0, 15))
        entry_image_version.bind("<FocusOut>", lambda e: self.save_config())
        entry_image_version.bind("<Return>", lambda e: self.save_config())

        # 镜像关键字输入框
        tk.Label(row3, text="镜像关键字:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        self.image_keyword_var = tk.StringVar(value="P14")
        entry_image_keyword = ttk.Entry(row3, textvariable=self.image_keyword_var, width=10)
        entry_image_keyword.pack(side=tk.LEFT, padx=(0, 15))
        entry_image_keyword.bind("<FocusOut>", lambda e: self.save_config())
        entry_image_keyword.bind("<Return>", lambda e: self.save_config())
        
        # 自动保存绑定
        self.entry_dns.bind("<FocusOut>", lambda e: self.save_config())
        self.entry_dns.bind("<Return>", lambda e: self.save_config())
        self.entry_model.bind("<<ComboboxSelected>>", lambda e: self.save_config())
        self.entry_region.bind("<<ComboboxSelected>>", lambda e: self.save_config())
        
        # Checkbutton 变量绑定 trace
        self.gms_var.trace_add("write", lambda *args: self.save_config())
        self.random_model_var.trace_add("write", lambda *args: self.save_config())
        self.rebuild_mode_var.trace_add("write", lambda *args: self.save_config())
        self.max_failures_var.trace_add("write", lambda *args: self.save_config())
        self.bridge_mode_var.trace_add("write", lambda *args: self.save_config())

    
    def _toggle_static_model_entry(self):
        """指定随机机型开关切换，与随机机型互斥（从用户输入的机型列表中随机）"""
        if self.static_model_var.get() == 1:
            # 如果勾选了指定随机机型，取消随机机型
            self.random_model_var.set(0)
            # 显示输入框
            self.custom_model_frame.pack(side=tk.LEFT, padx=(0, 15))
        else:
            # 隐藏输入框
            self.custom_model_frame.pack_forget()

    def _on_rebuild_mode_changed(self):
        """重建模式切换回调"""
        mode = self.rebuild_mode_var.get()
        print(f"[配置] 重建模式已切换为: {mode}")
        self.save_config()

    def _on_random_model_toggle(self):
        """随机机型开关切换，与指定随机机型互斥"""
        if self.random_model_var.get() == 1:
            # 如果勾选了随机机型，取消指定随机机型（这会自动隐藏输入框）
            self.static_model_var.set(0)
    
    def _on_jump_mode_changed(self):
        """跳码模式开关切换，与通道三模式、通道一模式互斥"""
        if self.jump_mode_var.get() == 1:
            # 如果勾选了跳码模式，取消通道三模式和通道一模式
            self.channel3_mode_var.set(0)
            self.channel1_mode_var.set(0)
        self.save_config()
    
    def _on_channel3_mode_changed(self):
        """通道三模式开关切换，与跳码模式、通道一模式互斥"""
        if self.channel3_mode_var.get() == 1:
            # 如果勾选了通道三模式，取消跳码模式和通道一模式
            self.jump_mode_var.set(0)
            self.channel1_mode_var.set(0)
        self.save_config()

    def _on_channel1_mode_changed(self):
        """通道一模式开关切换，与跳码模式、通道三模式互斥"""
        if self.channel1_mode_var.get() == 1:
            # 如果勾选了通道一模式，取消跳码模式和通道三模式
            self.jump_mode_var.set(0)
            self.channel3_mode_var.set(0)
        self.save_config()
    
    def sync_online_models(self):
        """从第一台设备同步在线机型列表"""
        if not self.devices:
            messagebox.showwarning("提示", "请先扫描并发现至少一台设备")
            return
            
        # 清空旧数据
        self.online_models = {}
        self.model_presets = {}
        self.entry_model['values'] = []
        self.entry_model.set('')
        
        # 取第一台设备的IP (假设所有设备同一个网段/Host)
        target_ip = self.devices[0].get('host_ip') or self.devices[0].get('ip')
        if not target_ip:
             messagebox.showwarning("错误", "无法获取设备IP")
             return
        
        def _fetch():
            try:
                url = f"http://{target_ip}:8000/android/phoneModel"
                self.log_message(f"正在同步机型列表: {url} ...")
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json().get('data', {})
                    model_list = data.get('list', [])
                    
                    new_values = []
                    # self.online_models = {} # 已经在主线程清空了
                    
                    for m in model_list:
                        m_name = m.get('name', 'Unknown')
                        m_id = str(m.get('id', ''))
                        display_name = f"{m_name}" # 仅显示名字，ID在后台处理
                        new_values.append(display_name)
                        self.online_models[display_name] = m_id
                        
                    # 更新下拉框 (回到主线程)
                    def update_ui():
                        self.entry_model['values'] = new_values
                        if new_values:
                            self.entry_model.current(0) # 选中第一个
                            self._on_model_selected(None) # 触发联动
                    
                    self.root.after(0, update_ui)
                    
                    self.log_message(f"✓ 同步成功! 获取到 {len(new_values)} 个在线机型")
                    messagebox.showinfo("成功", f"已同步 {len(new_values)} 个机型，请点击下拉框选择")
                else:
                    self.log_message(f"同步失败: HTTP {resp.status_code}")
            except Exception as e:
                self.log_message(f"同步异常: {e}")
                
        threading.Thread(target=_fetch, daemon=True).start()

    def _on_model_selected(self, event):
        """当选择机型时，仅记录选择，无需填充UI"""
        pass

            
    def get_selected_model_id(self):
        """获取当前选择机型的ID (如果有)"""
        name = self.entry_model.get()
        return self.online_models.get(name, "") # 如果是预设或自定义，返回空字符串

    def _refresh_script_list(self):
        """扫描 scripts/ 目录，返回可用脚本列表"""
        base_dir = self._get_app_path()
        scripts_dir = os.path.join(base_dir, "scripts")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        files = sorted(glob.glob(os.path.join(scripts_dir, "*.py")))
        return [os.path.basename(f) for f in files if os.path.basename(f) != "__init__.py"]

    def run_selected_script(self):
        """运行脚本：自定义脚本Tab → 执行自定义脚本；其他Tab → 执行脚本配置里的脚本"""
        try:
            active_tab = self.main_notebook.tab(self.main_notebook.select(), "text")
        except Exception:
            active_tab = ""
        if active_tab == "自定义脚本":
            self._cs_run()
            return

        scripts = self._refresh_script_list()
        if not scripts:
             #messagebox.showwarning("提示", "scripts/ 目录中没有可用脚本")
             return
        script_name = scripts[0]
        script_path = os.path.join(self._get_app_path(), "scripts", script_name)

        devices = self.get_selected_devices()
        if not devices:
             messagebox.showwarning("提示", "请先在左侧勾选要运行的设备")
             return

        self.log_message(f"正在为 {len(devices)} 台设备启动任务: {script_name}")



        for device in devices:
             # 启动独立线程处理每台设备的 收到/运行 逻辑
             threading.Thread(target=self._run_script_worker, 
                              args=(device, script_path),
                              daemon=True).start()

    def _run_script_worker(self, device, script_path):
        """设备任务工作线程：运行脚本"""
        serial = device.get("container_name", "").lstrip("/")
        ip = device.get("ip", "")
        key = (serial, ip)

        # 获取应用路径
        app_path = self._get_app_path()

        # 创建log目录
        log_dir = os.path.join(app_path, 'log')
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
        except Exception:
            pass

        # 如果已有任务在运行则跳过
        if key in self.running_tasks:
            if self.running_tasks[key].poll() is None:
                self.log_message(f"⚠️ [{serial}] 任务已在运行，跳过")
                return
            del self.running_tasks[key]

        cmd = [sys.executable, script_path,
               "--serial", serial,
               "--index", str(device.get("instance_index", 1))]

        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='replace',
                cwd=app_path,
            )

            self.running_tasks[key] = proc
            self.log_message(f"✅ [{serial}] 脚本已启动 (PID: {proc.pid})")
            self._monitor_process_output(proc, serial)

        except Exception as e:
            self.log_message(f"❌ [{serial}] 启动失败: {e}")

    def _reset_device_container(self, host_ip, index, old_container_name, config):
        """执行容器重建操作 (使用统一的 ContainerManager)"""
        if not container_manager:
            self.log_message(f"❌ 无法加载容器管理模块")
            return False

        self.log_message(f"🔄 [{old_container_name}] 开始重建容器...")
        
        # 1. 构造配置字典
        mgr_config = {
             'name': old_container_name,
             'image_keyword': config.get('image_keyword', 'P14'),
             'image_version': config.get('image_version'),
             'dns': config.get('dns', '223.5.5.5'),
             'doboxFps': config.get('doboxFps', '60'),
             'gmsenable': config.get('gms', '0'),
             'mgenable': config.get('mgenable', '0'),
             'timezone': config.get('timezone', 'America/New_York'),
             'countryCode': config.get('countryCode', 'US'),
             'latitude': config.get('latitude', 0),
             'longitude': config.get('longitude', 0),
             'random_model': config.get('random_model', False),
             'modelId': config.get('model_id'),
             'modelName': config.get('model_name'),
             'modelStatic': config.get('modelStatic'),
             'LocalModel': config.get('LocalModel'),
             'sandboxSize': config.get('sandboxSize'),
             'useBridge': config.get('useBridge', False),
             'macVlanIp': config.get('macVlanIp'),
             'mytBridgeName': config.get('mytBridgeName'),
             'vpcID': config.get('vpcID', 0),
             'adbPort': config.get('adbPort', 5555),
             'doboxWidth': config.get('doboxWidth'),
             'doboxHeight': config.get('doboxHeight'),
             'doboxDpi': config.get('doboxDpi'),
             'offset': config.get('offset'),
             'portMappings': config.get('portMappings', []),
             'whiteListDns': config.get('whiteListDns', []),
             'customBinds': config.get('customBinds', []),
             's5User': config.get('s5User'),
             's5Password': config.get('s5Password'),
             's5IP': config.get('s5IP'),
             's5Port': config.get('s5Port'),
             's5Type': config.get('s5Type', '0'),
             'PINCode': config.get('PINCode'),
             'randomFile': config.get('randomFile', True),
             'enforce': config.get('enforce', True),
        }
        
        # 2. 调用公共模块执行重建
        # 注意: container_manager 内部已包含 Delete -> Create 的逻辑
        success, msg = container_manager.rebuild_container(host_ip, index, mgr_config)
        
        
        if not success:
            self.log_message(f"❌ [{old_container_name}] {msg}")
            return False
        else:
            self.log_message(f"✅ {msg}")
            return True



    def _monitor_process_output(self, proc, device_name):
        """监控进程输出"""
        try:
            for line in iter(proc.stdout.readline, ''):
                if line:
                    self.log_message(f"[{device_name}] {line.strip()}")
            proc.stdout.close()
        except Exception as e:
            pass
            # self.log_message(f"[{device_name}]日志监控结束: {e}")
        
        # 进程结束
        if proc.poll() is not None:
             self.log_message(f"[{device_name}] 任务已结束 (Code: {proc.returncode})")

    def toggle_pause_selected_script(self):
        """暂停/继续选中的脚本任务（基于 psutil 挂起/恢复子进程）"""
        try:
            active_tab = self.main_notebook.tab(self.main_notebook.select(), "text")
        except Exception:
            active_tab = ""
        if active_tab == "自定义脚本":
            if self._cs_pause_event.is_set():
                self._cs_pause_event.clear()
                self.log_message("▶ 自定义脚本已继续")
            else:
                self._cs_pause_event.set()
                self.log_message("⏸ 自定义脚本已暂停")
            return

        if psutil is None:
            messagebox.showwarning("提示", "未安装 psutil，无法使用暂停/继续功能。\n请先执行: pip install psutil")
            return

        devices = self.get_selected_devices()
        if not devices:
            messagebox.showwarning("提示", "请先在左侧勾选设备")
            return

        for device in devices:
            container_name = device["container_name"].lstrip("/")
            key = (container_name, device["ip"])

            proc = self.running_tasks.get(key)
            if not proc or proc.poll() is not None:
                self.log_message(f"[{container_name}] 当前没有正在运行的任务")
                # 确保状态被清理
                self.task_pause_state.pop(key, None)
                continue

            try:
                p = psutil.Process(proc.pid)
            except Exception as e:
                self.log_message(f"[{container_name}] 获取进程信息失败: {e}")
                continue

            paused = self.task_pause_state.get(key, False)
            try:
                if paused:
                    p.resume()
                    self.task_pause_state[key] = False
                    self.log_message(f"[{container_name}] 任务已继续")
                else:
                    p.suspend()
                    self.task_pause_state[key] = True
                    self.log_message(f"[{container_name}] 任务已暂停")
            except Exception as e:
                self.log_message(f"[{container_name}] 暂停/继续失败: {e}")

    def stop_selected_script(self):
        """停止选中的脚本任务"""
        try:
            active_tab = self.main_notebook.tab(self.main_notebook.select(), "text")
        except Exception:
            active_tab = ""
        if active_tab == "自定义脚本":
            self._cs_stop_event.set()
            self._cs_pause_event.clear()  # 若暂停中，先解除阻塞让线程感知到停止
            self.log_message("⏹ 自定义脚本已停止")
            return

        devices = self.get_selected_devices()
        if not devices:
             messagebox.showwarning("提示", "请先在左侧勾选设备")
             return

        for device in devices:
             container_name = device["container_name"].lstrip("/")
             key = (container_name, device["ip"])
             
             if key in self.running_tasks:
                 proc = self.running_tasks[key]
                 try:
                     self.log_message(f"正在停止设备 {container_name} 的任务 (PID: {proc.pid})...")
                     proc.terminate()
                     # 等待进程结束? 不阻塞主线程
                 except Exception as e:
                     self.log_message(f"停止任务异常: {e}")
                 
                 # 清理运行与暂停状态
                 del self.running_tasks[key]
                 self.task_pause_state.pop(key, None)
             else:
                 self.log_message(f"设备 {container_name} 没有记录的运行任务")

    def stop_socks5_proxy(self):
        """批量停止SOCKS5代理"""
        selected = self.get_selected_devices()
        if not selected:
            messagebox.showwarning("警告", "请先选择设备")
            return
        
        threading.Thread(target=lambda: [self._stop_socks5_for_device(d) for d in selected], daemon=True).start()
        
    def _stop_socks5_for_device(self, device):
        """停止单个设备代理(复用逻辑)"""
        # 使用统一的连接信息获取方法
        target_ip, target_port, is_bridge = self._get_device_connection_info(device)
        
        url = f"http://{target_ip}:{target_port}/modifydev"
        params = {'cmd': '31'} # cmd 31: 停止代理
        try:
            resp = requests.get(url, params=params, timeout=5)
            # Log result...
            if resp.status_code == 200:
                 self.log_message(f"[{device['container_name']}] 代理已停止")
            else:
                 self.log_message(f"[{device['container_name']}] 代理停止失败: {resp.text}")
        except Exception as e:
            self.log_message(f"[{device['container_name']}] 代理停止异常: {e}")

    def _set_socks5_for_device(self, device, config):
        """设置单个设备SOCKS5"""
        container_name = device.get("container_name", "")
        # 获取设备编号，例如 myt_android_1 -> 1
        device_num = container_name.split('_')[-1]
        log_prefix = f"[{device_num}]"
        
        # 使用统一的连接信息获取方法
        target_ip, target_port, is_bridge = self._get_device_connection_info(device)

        # 设置SOCKS5
        try:
            url = f"http://{target_ip}:{target_port}/modifydev"
            
            # 构造参数
            # cmd=3 Set Socks5
            params = {
                'cmd': '3',
                'ip': config['proxy'].split(':')[0],
                'port': config['proxy'].split(':')[1],
                'user': config['user'],
                'password': config['passwd']
            }
            
            self.log_message(f"{log_prefix} 正在设置SOCKS5: {config['proxy']}...")
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 200:
                    self.log_message(f"{log_prefix} ✓ SOCKS5设置成功")
                else:
                    self.log_message(f"{log_prefix} ✗ 设置失败: {res_json.get('error', res_json.get('msg', '未知错误'))}")
            else:
                self.log_message(f"{log_prefix} ✗ HTTP错误: {response.status_code}")

        except Exception as e:
            self.log_message(f"{log_prefix} ✗ 异常: {e}")
            
    def log_message(self, message):
        """添加日志消息"""
        # 检测注册成功计数
        if "注册成功" in message:
            self.success_var.set(self.success_var.get() + 1)
            self.success_label.config(text=str(self.success_var.get()))
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")

    def _reset_success_counter(self):
        """重置成功计数"""
        self.success_var.set(0)
        self.success_label.config(text="0")

    
    def process_log_queue(self):
        """处理日志队列"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                # 只有当当前滚动条已经在底部时才自动跟随滚动
                try:
                    y0, y1 = self.log_text.yview()
                    should_autoscroll = (y1 >= 0.999)
                except Exception:
                    should_autoscroll = True

                all_logs = [self.log_text]
                if hasattr(self, "script_log_text"):
                    all_logs.append(self.script_log_text)
                all_logs.extend(getattr(self, "_tab_log_texts", []))

                for lt in all_logs:
                    try:
                        lt.insert(tk.END, message + "\n")
                        if should_autoscroll:
                            lt.see(tk.END)
                    except Exception:
                        pass
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)
    
    def _on_device_name_double_click(self, event):
        """双击设备行：SN码列 → scrcpy 投屏；昵称列 → 编辑昵称"""
        if self.device_tree.identify_region(event.x, event.y) != "cell":
            return
        col = self.device_tree.identify_column(event.x)
        item = self.device_tree.identify_row(event.y)
        if not item:
            return

        tags = self.device_tree.item(item, "tags")
        serial = tags[0] if tags else self.device_tree.item(item, "values")[3]

        # 双击 SN码列（第4列）→ 启动 scrcpy 投屏
        if col == "#4":
            self._launch_scrcpy(serial)
            return

        if col != "#3":  # 非昵称列不处理
            return
        current_name = self.device_custom_names.get(serial, serial)

        win = tk.Toplevel(self.root)
        win.title("编辑设备名")
        win.geometry("320x110")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        win.lift()
        win.focus_force()

        ttk.Label(win, text=f"原始串号: {serial}", foreground="gray").pack(anchor="w", padx=12, pady=(10, 0))
        entry = ttk.Entry(win, width=38)
        entry.insert(0, current_name)
        entry.pack(padx=12, pady=6)

        def _focus_entry():
            entry.focus_set()
            entry.select_range(0, tk.END)

        win.after(50, _focus_entry)

        def _save():
            new_name = entry.get().strip()
            if new_name:
                self.device_custom_names[serial] = new_name
                display = new_name
                new_tags = (serial,)
            else:
                self.device_custom_names.pop(serial, None)
                display = "双击编辑昵称"
                new_tags = (serial, "placeholder")
            vals = list(self.device_tree.item(item, "values"))
            vals[2] = display
            self.device_tree.item(item, values=tuple(vals), tags=new_tags)
            self.save_config()
            win.destroy()

        entry.bind("<Return>", lambda _: _save())
        entry.bind("<Escape>", lambda _: win.destroy())
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        ttk.Button(btn_frame, text="保存", command=_save, width=8).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="取消", command=win.destroy, width=8).pack(side=tk.LEFT)

    def _launch_scrcpy(self, serial):
        """调用 scrcpy 对指定设备投屏（独立窗口，非阻塞）"""
        if not serial:
            messagebox.showwarning("投屏", "设备串号为空，无法投屏")
            return
        try:
            import shutil
            scrcpy_path = shutil.which("scrcpy")
            if not scrcpy_path:
                # macOS 常见安装路径兜底
                for p in ["/usr/local/bin/scrcpy", "/opt/homebrew/bin/scrcpy"]:
                    if os.path.isfile(p):
                        scrcpy_path = p
                        break
            if not scrcpy_path:
                messagebox.showerror(
                    "找不到 scrcpy",
                    "未检测到 scrcpy，请先安装：\nbrew install scrcpy"
                )
                return
            cmd = [scrcpy_path, "-s", serial, "--window-title", f"投屏 {serial}"]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log_message(f"📱 scrcpy 已启动 → {serial}")
        except Exception as e:
            messagebox.showerror("投屏失败", str(e))

    def on_treeview_click(self, event):
        """处理树形视图点击事件"""
        region = self.device_tree.identify_region(event.x, event.y)
        
        # 点击表头第一列：执行全选/反选
        if region == "heading":
            column = self.device_tree.identify_column(event.x)
            if column == "#1":  # 第一列(选择列)的表头
                self.toggle_all_selection()
                return "break"
            return
        
        # 点击单元格：仅处理第一列的勾选
        if region == "cell":
            column = self.device_tree.identify_column(event.x)
            if column != "#1":  # 不是第一列(选择列)
                return
            
            item = self.device_tree.identify_row(event.y)
            if not item:
                return
            
            # 切换选中状态（用 tag 里的原始 serial 做 key，防止自定义名后查找失败）
            values = self.device_tree.item(item, "values")
            tags = self.device_tree.item(item, "tags")
            serial = tags[0] if tags else values[2]
            container_ip = ""
            for d in self.devices:
                if d["container_name"].lstrip("/") == serial:
                    container_ip = d["ip"]
                    break
            key = (serial, container_ip)
            
            current_state = self.device_checked.get(key, False)
            self.device_checked[key] = not current_state

            new_checkbox = "✅" if not current_state else "⬜"
            new_values = (new_checkbox,) + values[1:]
            new_tags = [t for t in self.device_tree.item(item, "tags") if t != "checked_row"]
            if not current_state:  # 变为选中
                new_tags.append("checked_row")
            self.device_tree.item(item, values=new_values, tags=tuple(new_tags))
    
    def toggle_all_selection(self):
        """全选/取消全选"""
        all_items = self.device_tree.get_children()
        if not all_items:
            return
        
        # 检查是否全部选中
        def get_key_from_item(item):
            tags = self.device_tree.item(item, "tags")
            serial = tags[0] if tags else self.device_tree.item(item, "values")[2]
            for d in self.devices:
                if d["container_name"].lstrip("/") == serial:
                    return (serial, d["ip"])
            return (serial, "")
        
        all_checked = all(self.device_checked.get(get_key_from_item(item), False) for item in all_items)
        
        new_state = not all_checked
        
        for item in all_items:
            values = self.device_tree.item(item, "values")
            container_name = values[2]
            key = get_key_from_item(item)
            self.device_checked[key] = new_state
            
            new_checkbox = "✅" if new_state else "⬜"
            new_values = (new_checkbox,) + values[1:]
            new_tags = [t for t in self.device_tree.item(item, "tags") if t != "checked_row"]
            if new_state:
                new_tags.append("checked_row")
            self.device_tree.item(item, values=new_values, tags=tuple(new_tags))

        # 同步更新表头的复选框显示
        header_checkbox = "✅" if new_state else "⬜"
        self.device_tree.heading("选择", text=header_checkbox)
    
    def get_selected_devices(self):
        """获取选中的设备列表"""
        selected = []
        for device in self.devices:
            container_name = device["container_name"].lstrip("/")
            key = (container_name, device["ip"])
            if self.device_checked.get(key, False):
                selected.append(device)
        return selected
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.device_tree.identify_row(event.y)
        if item:
            self.device_tree.selection_set(item)
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="📺 视频推流", command=self.video_stream_single)
            menu.add_separator()
            menu.add_command(label="🌐 设置SK5代理", command=self.set_socks5_proxy_single)
            menu.add_command(label="❌ 删除SK5代理", command=self.stop_socks5_proxy_single)
            menu.post(event.x_root, event.y_root)
    
    # ==================== 扫描设备 ====================
    def scan_devices(self):
        """扫描 ADB 已连接设备"""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_button.config(text="🔍 扫描中...")
        self.status_var.set("正在扫描 ADB 设备...")
        self.log_message("开始扫描 ADB 已连接设备...")

        scan_thread = threading.Thread(target=self._scan_devices_thread, daemon=True)
        scan_thread.start()
    
    def _scan_devices_thread(self):
        """ADB 扫描设备线程"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().splitlines()

            # 跳过首行 "List of devices attached"
            device_lines = [l for l in lines[1:] if l.strip() and '\t' in l]

            temp_devices = []
            for idx, line in enumerate(device_lines, 1):
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                serial = parts[0].strip()
                state = parts[1].strip()

                # 解析 TCP/IP 设备格式 ip:port
                if ':' in serial:
                    ip_part, port_str = serial.rsplit(':', 1)
                    try:
                        port = int(port_str)
                    except ValueError:
                        ip_part = ""
                        port = 5555
                else:
                    ip_part = ""
                    port = 5555

                temp_devices.append({
                    "container_name": serial,
                    "ip": ip_part,
                    "host_ip": ip_part if ip_part else serial,
                    "port": port,
                    "api_port": port,
                    "rpa_port": port,
                    "instance_index": idx,
                    "host_index": idx,
                    "status": "在线" if state == "device" else state,
                })

            self.devices = temp_devices
            self.root.after(0, self._refresh_device_tree)
            if temp_devices:
                self.log_message(f"✅ ADB 扫描完成，发现 {len(temp_devices)} 个设备")
            else:
                self.log_message("ADB 扫描完成，未发现已连接设备")

        except FileNotFoundError:
            self.log_message("❌ 未找到 adb 命令，请确保 ADB 已安装并在 PATH 中")
            self.devices = []
            self.root.after(0, self._refresh_device_tree)
        except subprocess.TimeoutExpired:
            self.log_message("❌ ADB 扫描超时")
        except Exception as e:
            self.log_message(f"ADB 扫描出错: {str(e)}")
        finally:
            self.root.after(0, self._scan_complete)
    
    def _scan_single_host(self, ip, docker_port=8000):
        """扫描单个主机 - 一次请求完成检测和获取容器"""
        url = f"http://{ip}:{docker_port}/docker/containers/json"
        try:
            resp = requests.get(url, timeout=self.scan_timeout)
            if resp.status_code != 200:
                return []
            
            containers = resp.json()
            if not containers:
                return []
            
            valid_containers = []
            for c in containers:
                container_name = c["Names"][0] if c["Names"] else c["Id"][:12]
                if container_name.startswith("/myt") and not "android" in container_name:
                    # 只过滤非android的myt容器
                    continue
                valid_containers.append((container_name, c))
            
            if not valid_containers:
                return []
            
            device_list = []
            total = len(valid_containers)
            for idx, (container_name, c) in enumerate(valid_containers):
                container_ip = ""
                networks = c.get("NetworkSettings", {}).get("Networks", {})
                if networks:
                    if "bridge" in networks and networks["bridge"].get("IPAddress"):
                        container_ip = networks["bridge"]["IPAddress"]
                    else:
                        for net in networks.values():
                            if net.get("IPAddress"):
                                container_ip = net["IPAddress"]
                                break
                
                # 尝试从容器名解析序号
                try:
                    # 匹配结尾的数字，例如 android_1, myt-container-2 等
                    match = re.search(r'[_-]?(\d+)$', container_name)
                    if match:
                        host_index = int(match.group(1))
                    else:
                        host_index = total - idx
                except:
                    host_index = total - idx

                # 动态端口计算逻辑 (符合文档)
                # Base: 30000 + (index-1)*100
                base_port = 30000 + (host_index - 1) * 100
                api_port = base_port + 1
                rpa_port = base_port + 2
                
                device_list.append({
                    "container_name": container_name,
                    "ip": container_ip,
                    "host_ip": ip,
                    "port": api_port,      # 默认显示API端口
                    "api_port": api_port,  # 明确存储API端口
                    "rpa_port": rpa_port,  # 明确存储RPA端口
                    "instance_index": host_index,
                    "host_index": host_index,
                    "status": "在线",
                })
            
            if device_list:
                self.log_message(f"发现主机 {ip}: {len(device_list)} 个容器")
            return device_list
        except requests.exceptions.ConnectTimeout:
            return []
        except requests.exceptions.ReadTimeout:
            return []
        except requests.exceptions.ConnectionError:
            return []
        except Exception:
            return []
    
    def _device_sort_key(self, device):
        """设备排序键"""
        host_ip = device.get('host_ip', '0.0.0.0')
        host_index = device.get('host_index', 0)
        return (self._ip_to_int(host_ip), host_index)
    
    def _ip_to_int(self, ip):
        """IP转整数"""
        try:
            parts = ip.split('.')
            return int(parts[0]) * 16777216 + int(parts[1]) * 65536 + int(parts[2]) * 256 + int(parts[3])
        except:
            return 0
    
    def _refresh_device_tree(self):
        """刷新设备树形视图"""
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)


        sorted_devices = sorted(self.devices, key=self._device_sort_key)

        for i, device_info in enumerate(sorted_devices, 1):
            serial = device_info["container_name"].lstrip("/")
            key = (serial, device_info["ip"])
            checked = self.device_checked.get(key, False)
            checkbox = "✅" if checked else "⬜"

            has_custom = serial in self.device_custom_names
            display_name = self.device_custom_names[serial] if has_custom else "双击编辑昵称"
            row_tags_list = [serial] if has_custom else [serial, "placeholder"]
            if checked:
                row_tags_list.append("checked_row")
            row_tags = tuple(row_tags_list)

            item_id = self.device_tree.insert("", "end", values=(
                checkbox,
                i,
                display_name,
                device_info.get("host_ip", ""),
                device_info["status"]
            ), tags=row_tags)
            device_info["tree_item_id"] = item_id
    
    def _scan_complete(self):
        """扫描完成回调"""
        self.is_scanning = False
        self.scan_button.config(text="🔍 扫描设备")
        self.status_var.set(f"就绪 - 共 {len(self.devices)} 个设备")
    
    # ==================== 视频推流 ====================
    def video_stream(self):
        """视频推流（批量）"""
        selected = self.get_selected_devices()
        if not selected:
            messagebox.showwarning("警告", "请先选择设备")
            return
        self._show_video_stream_dialog(selected)
    
    def video_stream_single(self):
        """视频推流（单个）"""
        selection = self.device_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.device_tree.item(item, "values")
        container_name = values[2]
        
        for device in self.devices:
            if device["container_name"].lstrip("/") == container_name:
                self._show_video_stream_dialog([device])
                return
    
    def _show_video_stream_dialog(self, devices):
        """显示视频推流对话框"""
        if self.video_server is None:
            self.video_server = VideoStreamServer(port=8000)
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"视频推流 - {len(devices)} 个设备")
        dialog.geometry("600x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设备列表
        device_frame = ttk.LabelFrame(dialog, text="目标设备", padding=10)
        device_frame.pack(fill=tk.X, padx=10, pady=10)
        
        device_names = ", ".join([d["container_name"].lstrip("/").split("_")[-1] for d in devices[:5]])
        if len(devices) > 5:
            device_names += f" 等 {len(devices)} 个设备"
        ttk.Label(device_frame, text=device_names).pack(anchor="w")
        # 移除本地服务器显示，因为不再依赖本地HTTP服务
        # ttk.Label(device_frame, text=f"服务器: http://{self.video_server.local_ip}:{self.video_server.port}").pack(anchor="w")
        
        # 视频选择
        video_frame = ttk.LabelFrame(dialog, text="视频文件", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        btn_frame = ttk.Frame(video_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        video_files = []
        
        def select_videos():
            filetypes = [("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")]
            files = filedialog.askopenfilenames(parent=dialog, title="选择视频", filetypes=filetypes)
            for f in files:
                if f not in video_files:
                    video_files.append(f)
                    video_listbox.insert(tk.END, os.path.basename(f))
        
        def select_folder():
            folder = filedialog.askdirectory(parent=dialog, title="选择视频文件夹")
            if folder:
                self.video_server.start(folder)
                for filename in sorted(os.listdir(folder)):
                    if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        filepath = os.path.join(folder, filename)
                        if filepath not in video_files:
                            video_files.append(filepath)
                            video_listbox.insert(tk.END, filename)
        
        ttk.Button(btn_frame, text="选择视频", command=select_videos).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="选择文件夹", command=select_folder).pack(side=tk.LEFT, padx=5)
        
        # 视频列表
        list_frame = ttk.Frame(video_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        video_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=8)
        video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=video_listbox.yview)
        
        # 推流按钮
        def push_video():
            selection = video_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个视频", parent=dialog)
                return
            
            filepath = video_files[selection[0]]
            filename = os.path.basename(filepath)
            
            def push_thread():
                success_count = 0
                total_devices = len(devices)
                
                for idx, device in enumerate(devices):
                    # 更新总进度
                    progress = (idx / total_devices) * 100
                    self.root.after(0, lambda p=progress: self.status_var.set(f"正在处理推流: {p:.1f}%"))
                    
                    container_name = device.get("container_name", "")
                    device_num = container_name.split('_')[-1]
                    log_prefix = f"[{device_num}]"

                    # 使用统一的连接信息获取方法
                    target_ip, target_port, is_bridge = self._get_device_connection_info(device)
                    
                    # 2. 上传视频文件
                    self.log_message(f"{log_prefix} 正在上传视频: {filename}")
                    
                    upload_success = False
                    # API: POST http://{ip}:{port}/upload
                    upload_url = f"http://{target_ip}:{target_port}/upload"
                    
                    try:
                        with open(filepath, 'rb') as f:
                            files = {'file': (filename, f)}
                            resp = requests.post(upload_url, files=files, timeout=300)
                            
                            if resp.status_code == 200:
                                upload_success = True
                    except Exception as e:
                        self.log_message(f"{log_prefix} 视频上传异常: {e}")
                    
                    if not upload_success:
                        self.log_message(f"{log_prefix} ✗ 视频上传失败，跳过推流")
                        continue
                        
                    self.log_message(f"{log_prefix} ✓ 视频上传成功")
                    
                    # 3. 设置推流 (使用设备本地路径)
                    device_path = f"/sdcard/Download/{filename}"
                    try:
                        url = f"http://{target_ip}:{target_port}/modifydev"
                        # type=video, path=本地路径
                        params = {'cmd': '4', 'type': 'video', 'path': device_path}
                        resp = requests.get(url, params=params, timeout=30)
                        if resp.status_code == 200 and resp.json().get('code') == 200:
                            success_count += 1
                            self.log_message(f"{log_prefix} ✓ 推流配置成功")
                        else:
                            self.log_message(f"{log_prefix} ✗ 推流配置失败: {resp.text}")
                    except Exception as e:
                        self.log_message(f"{log_prefix} ✗ 推流请求异常: {e}")
                
                def show_result():
                    self.status_var.set("就绪")
                    if dialog.winfo_exists():
                         messagebox.showinfo("完成", f"推流完成: {success_count}/{len(devices)} 成功", parent=dialog)
                
                self.root.after(0, show_result)
            
            threading.Thread(target=push_thread, daemon=True).start()
        
        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(action_frame, text="开始推流", command=push_video, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="关闭", command=dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)
    
    # ==================== SOCKS5代理 ====================
    def _get_socks5_config(self):
        """获取当前SOCKS5配置，解析 IP:端口:账号:密码 格式"""
        proxy_input = self.proxy_entry.get().strip()
        local_ip = ""
        if hasattr(self, "local_ip_entry"):
            local_ip = self.local_ip_entry.get().strip()
        proxy_country_code = ""
        if hasattr(self, "proxy_country_code_entry"):
            proxy_country_code = self.proxy_country_code_entry.get().strip()
        # 域名过滤改为用逗号分隔，兼容换行
        raw_domains = self.domain_text.get("1.0", tk.END).strip()
        raw_domains = raw_domains.replace("\n", ",")
        domains = [d.strip() for d in raw_domains.split(",") if d.strip()]
        
        # 解析 IP:端口:账号:密码 格式
        proxy = ""
        user = ""
        passwd = ""
        
        if proxy_input:
            parts = proxy_input.split(":")
            if len(parts) >= 2:
                proxy = f"{parts[0]}:{parts[1]}"  # IP:端口
            if len(parts) >= 3:
                user = parts[2]  # 账号
            if len(parts) >= 4:
                passwd = ":".join(parts[3:])  # 密码（可能包含冒号）
        
        return {
            "proxy": proxy,
            "user": user,
            "passwd": passwd,
            "domain_filter": domains,
            "local_ip": local_ip,
            "proxy_country_code": proxy_country_code,
            "proxy_type": "storm" if (hasattr(self, "storm_proxy_var") and self.storm_proxy_var.get()) else "socks5",
            "vpc_node": self.vpc_node_entry.get().strip() if hasattr(self, "vpc_node_entry") else ""
        }
    
    def set_socks5_proxy(self):
        """设置SK5代理（批量）"""
        selected = self.get_selected_devices()
        if not selected:
            messagebox.showwarning("警告", "请先选择设备")
            return
        
        config = self._get_socks5_config()
        if not config["proxy"]:
            messagebox.showerror("错误", "请输入代理地址")
            return
        
        threading.Thread(target=self._batch_set_socks5, args=(selected, config), daemon=True).start()
    
    def set_socks5_proxy_single(self):
        """设置SK5代理（单个）"""
        selection = self.device_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.device_tree.item(item, "values")
        container_name = values[2]
        
        config = self._get_socks5_config()
        if not config["proxy"]:
            messagebox.showerror("错误", "请输入代理地址")
            return
        
        for device in self.devices:
            if device["container_name"].lstrip("/") == container_name:
                threading.Thread(target=self._batch_set_socks5, args=([device], config), daemon=True).start()
                return
    
    def _batch_set_socks5(self, devices, config):
        """批量设置SOCKS5代理"""
        for device in devices:
            self._set_socks5_for_device(device, config)
    
    def _set_socks5_for_device(self, device, config):
        """为单个设备设置SOCKS5代理（拆分为：代理设置 → VPC节点 → 域名直连）"""
        container_name = device.get("container_name", "")
        host_ip = device.get("host_ip")
        instance_index = device.get("instance_index")

        device_num = container_name.split('_')[-1] if container_name else device.get("ip", "")
        log_prefix = f"[{device_num}]"

        if not host_ip or instance_index is None:
            self.log_message(f"{log_prefix} 提示：SOCKS5代理仅在非桥接模式下可用")
            return

        target_ip = host_ip
        target_port = device.get("api_port") or (30000 + (instance_index - 1) * 100 + 1)

        proxy_type = config.get("proxy_type", "socks5")

        if proxy_type == "storm":
            self._setup_storm_proxy(config, target_ip, target_port, log_prefix)
        else:
            self._setup_socks5_proxy(config, target_ip, target_port, log_prefix)

    def _setup_socks5_proxy(self, config, target_ip, target_port, log_prefix):
        """设置 SOCKS5 代理"""
        proxy_addr = config.get("proxy", "")
        if ':' not in proxy_addr:
            self.log_message(f"{log_prefix} 代理地址格式错误: {proxy_addr}")
            return

        proxy_ip, proxy_port = proxy_addr.split(':', 1)
        proxy_user = config.get('user', '')

        if 'session-' in proxy_user:
            random_sess = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            new_user = re.sub(r"(session-)[a-zA-Z0-9]+", f"\\g<1>{random_sess}", proxy_user)
            if new_user != proxy_user:
                proxy_user = new_user
                self.log_message(f"{log_prefix} 🎲 生成随机Session: {random_sess}")

        params = {
            'cmd': '2', 'ip': proxy_ip, 'port': proxy_port,
            'usr': proxy_user, 'pwd': config.get('passwd', ''), 'type': '1'
        }

        try:
            url = f"http://{target_ip}:{target_port}/proxy"
            self.log_message(f"{log_prefix} 正在设置SOCKS5代理: {proxy_addr} ...")
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 200:
                    self.log_message(f"{log_prefix} ✓ SOCKS5代理设置成功")
                else:
                    self.log_message(f"{log_prefix} ✗ 代理设置失败: {res_json.get('msg')}")
            else:
                self.log_message(f"{log_prefix} ✗ 设置代理HTTP错误: {response.status_code}")
        except Exception as e:
            self.log_message(f"{log_prefix} ✗ 设置代理异常: {e}")

    def _setup_storm_proxy(self, config, target_ip, target_port, log_prefix):
        """从 StormProxies 获取代理并设置，无限重试直到成功"""
        local_ip = config.get("local_ip", "")
        if not local_ip:
            self.log_message(f"{log_prefix} 请填写本地监听IP")
            return

        if ':' in local_ip:
            host_part = local_ip.split(':')[0]
        else:
            host_part = local_ip

        while True:
            try:
                api_url = f"http://{host_part}:21000/api/get_ip_list?num=1&type=json"
                code = (config.get("proxy_country_code") or "").strip().upper()
                if code:
                    api_url += f"&code={code}"
                self.log_message(f"{log_prefix} 正在获取StormProxies代理... 请求: {api_url}")

                response = requests.get(api_url, timeout=10)
                if response.status_code != 200:
                    self.log_message(f"{log_prefix} ✗ StormProxies API请求失败: {response.status_code}，10秒后重试...")
                    time.sleep(10)
                    continue

                data = response.json()
                listen_addr_list = data.get("data", [])
                if not listen_addr_list:
                    self.log_message(f"{log_prefix} ✗ 获取StormProxies代理失败: 无数据，10秒后重试...")
                    time.sleep(10)
                    continue

                listen_addr = listen_addr_list[0].get("listenAddr", "")
                if not listen_addr:
                    self.log_message(f"{log_prefix} ✗ 获取StormProxies代理失败: 无listenAddr，10秒后重试...")
                    time.sleep(10)
                    continue

                proxy_ip, proxy_port = listen_addr.split(":")
                params = {
                    'cmd': '2', 'ip': proxy_ip, 'port': proxy_port,
                    'usr': '', 'pwd': '', 'type': '1'
                }

                url = f"http://{target_ip}:{target_port}/proxy"
                self.log_message(f"{log_prefix} 正在设置StormProxies代理: {listen_addr} ...")

                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get('code') == 200:
                        self.log_message(f"{log_prefix} ✓ StormProxies代理设置成功")
                        return
                    self.log_message(f"{log_prefix} ✗ 代理设置失败: {res_json.get('msg')}，10秒后重试获取代理...")
                else:
                    self.log_message(f"{log_prefix} ✗ 设置代理HTTP错误: {response.status_code}，10秒后重试...")
            except Exception as e:
                self.log_message(f"{log_prefix} ✗ 获取/设置代理异常: {e}，10秒后重试...")
            time.sleep(10)

    def stop_socks5_proxy(self):
        """删除SK5代理（批量）"""
        selected = self.get_selected_devices()
        if not selected:
            messagebox.showwarning("警告", "请先选择设备")
            return
        
        threading.Thread(target=self._batch_stop_socks5, args=(selected,), daemon=True).start()
    
    def stop_socks5_proxy_single(self):
        """删除SK5代理（单个）"""
        selection = self.device_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.device_tree.item(item, "values")
        container_name = values[2]
        
        for device in self.devices:
            if device["container_name"].lstrip("/") == container_name:
                threading.Thread(target=self._batch_stop_socks5, args=([device],), daemon=True).start()
                return
    
    def _batch_stop_socks5(self, devices):
        """批量删除SOCKS5代理"""
        for device in devices:
            self._stop_socks5_for_device(device)
    
    def _stop_socks5_for_device(self, device):
        """为单个设备删除SOCKS5代理"""
        container_name = device.get("container_name", "")
        host_ip = device.get("host_ip")
        instance_index = device.get("instance_index")
        ip = device.get("ip", "")
        
        device_num = container_name.split('_')[-1] if container_name else ip
        log_prefix = f"[{device_num}]"
        
        # 判断模式
        if host_ip and instance_index is not None:
            target_ip = host_ip
            # 优先使用已保存的API端口
            target_port = device.get("api_port")
            if not target_port:
                target_port = 30000 + (instance_index - 1) * 100 + 1
        else:
            target_ip = ip
            target_port = 30001
        
        try:
            url = f"http://{target_ip}:{target_port}/proxy"
            params = {'cmd': '3'}
            self.log_message(f"{log_prefix} 正在删除SOCKS5代理配置...")
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 200:
                    self.log_message(f"{log_prefix} ✓ SOCKS5代理已删除")
                else:
                    self.log_message(f"{log_prefix} ✗ 删除代理失败: {res_json.get('error', res_json.get('msg', '未知错误'))}")
            else:
                self.log_message(f"{log_prefix} ✗ 删除代理HTTP错误: {response.status_code}")
        except Exception as e:
            self.log_message(f"{log_prefix} ✗ 删除代理异常: {e}")
    
    # ==================== 配置管理 ====================
    def save_config(self):
        """保存配置"""
        # 加载期间禁止写入，避免 trace 回调把默认值覆盖掉已保存的配置
        if getattr(self, "_loading_config", False):
            return
        # 获取当前网段设置
        networks_str = self.network_entry.get().strip()
        scan_networks = [n.strip() for n in networks_str.replace('，', ',').split(',') if n.strip()]

        # 清理设备数据中的临时字段
        saved_devices = []
        for d in self.devices:
            d_copy = d.copy()
            if "tree_item_id" in d_copy:
                del d_copy["tree_item_id"]
            saved_devices.append(d_copy)

        config = {
            "socks5": self._get_socks5_config(),
            "devices": saved_devices,
            "scan_networks": scan_networks,
            "container_config": {
                "dns": self.entry_dns.get(),
                "model": self.entry_model.get(),
                "random_model": self.random_model_var.get(), # 保存随机机型设置
                "static_model": self.static_model_var.get(), # 保存指定随机机型设置
                "custom_model_list": self.custom_model_list_var.get(), # 保存自定义机型列表
                "rebuild_mode": self.rebuild_mode_var.get(), # 保存重建模式
                "max_failures": self.max_failures_var.get(), # 保存最大失败次数
                "gms": self.gms_var.get(),
                "region": self.entry_region.get(),
                "bridge_mode": self.bridge_mode_var.get(), # 保存桥接模式设置
                "image_version": self.image_version_var.get(), # 保存镜像版本
                "image_keyword": self.image_keyword_var.get(), # 保存镜像关键字
                # 保存同步的机型数据
                "online_models": self.online_models,
                "model_presets": self.model_presets
            },
            "script_config": {
                "name_lang": self.name_lang_var.get(),
                "country": self.country_entry.get(),
                "char_mode": self.char_mode_var.get() if hasattr(self, "char_mode_var") else 0,
                "pwd_mode": self.pwd_mode_var.get(),
                "pwd_prefix": self.pwd_prefix_entry.get(),
                "pwd_custom": self.pwd_custom_entry.get(),
                "skip_count": self.skip_count_entry.get(),
                "tiktok_mode": self.tiktok_mode_var.get(),
                "jump_mode": self.jump_mode_var.get(),
                "channel3_mode": self.channel3_mode_var.get(),
                "channel1_mode": self.channel1_mode_var.get(),
                "accessibility_mode": self.accessibility_mode_var.get(),
                "authorized_enterprise": self.authorized_enterprise_var.get(),
                "upload_platform": self.upload_platform_var.get(),

                # 平台取号配置
                "platform_phone": self.platform_phone_var.get(),
                "platform_name": self.platform_name_var.get(),
                "platform_api_key": self.platform_api_key_var.get(),
                "platform_country": self.platform_country_var.get(),
                "platform_service": self.platform_service_var.get(),
                "platform_provider_ids": self.platform_provider_ids_var.get(),
                # 打开App配置
                "open_app_name": self.open_app_var.get() if hasattr(self, "open_app_var") else "",
                "open_app_delay": self.open_app_delay_var.get() if hasattr(self, "open_app_delay_var") else "3",
                # 坐标点击配置
                "coord_tap_x": self.coord_tap_x_var.get() if hasattr(self, "coord_tap_x_var") else "",
                "coord_tap_y": self.coord_tap_y_var.get() if hasattr(self, "coord_tap_y_var") else "",
                "coord_tap_delay": self.coord_tap_delay_var.get() if hasattr(self, "coord_tap_delay_var") else "500",
                # 输入文字配置
                "input_text_content": self.input_text_var.get() if hasattr(self, "input_text_var") else "",
                "input_text_delay": self.input_text_delay_var.get() if hasattr(self, "input_text_delay_var") else "500",
                # 点击文字配置
                "click_text_content": self.click_text_var.get() if hasattr(self, "click_text_var") else "",
                "click_text_delay": self.click_text_delay_var.get() if hasattr(self, "click_text_delay_var") else "500",
            },
            "device_custom_names": self.device_custom_names,
            "custom_open_apps": self.custom_open_apps,
            "custom_script_steps": self._cs_steps_to_plain(self.custom_script_steps) if hasattr(self, "custom_script_steps") else [],
            "phones": self.phones,
            "emails": self.emails,
            "visas": self.visas,
            "visa_checked_state": {str(k): v for k, v in self.visa_checked_state.items()},
            "visa_sync_manager": self._serialize_visa_sync_manager(),
            # 平台养号配置
            **{
                f"{prefix}_config": {
                    f"config{i}": getattr(self, f"{prefix}_cfg{i}").get()
                    for i in range(1, 6)
                }
                for prefix in ("douyin", "kuaishou", "xiaohongshu", "xianyu")
                if hasattr(self, f"{prefix}_cfg1")
            },
        }
        
        config_path = os.path.join(self._get_app_path(), "config.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log_message("✓ 配置已保存")
        except Exception as e:
            self.log_message(f"✗ 保存配置失败: {e}")
    
    def load_config(self):
        """加载配置"""
        config_path = os.path.join(self._get_app_path(), "config.json")
        if not os.path.exists(config_path):
            return

        self._loading_config = True
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            socks5 = config.get("socks5", {})
            # 组合成 IP:端口:账号:密码 格式
            if socks5.get("proxy"):
                proxy_str = socks5["proxy"]
                if socks5.get("user"):
                    proxy_str += f":{socks5['user']}"
                    if socks5.get("passwd"):
                        proxy_str += f":{socks5['passwd']}"
                self.proxy_entry.delete(0, tk.END)
                self.proxy_entry.insert(0, proxy_str)
            if socks5.get("domain_filter"):
                self.domain_text.delete("1.0", tk.END)
                # 显示时也用逗号分隔，便于编辑
                self.domain_text.insert("1.0", ", ".join(socks5["domain_filter"]))
            # 加载本地监听IP
            if hasattr(self, "local_ip_entry"):
                self.local_ip_entry.delete(0, tk.END)
                if socks5.get("local_ip"):
                    self.local_ip_entry.insert(0, socks5.get("local_ip", ""))
            # 加载国家代码
            if hasattr(self, "proxy_country_code_entry"):
                self.proxy_country_code_entry.delete(0, tk.END)
                if socks5.get("proxy_country_code"):
                    self.proxy_country_code_entry.insert(0, socks5.get("proxy_country_code", ""))

            # 加载StormProxies模式设置
            if hasattr(self, "storm_proxy_var"):
                proxy_type = socks5.get("proxy_type", "socks5")
                self.storm_proxy_var.set(1 if proxy_type == "storm" else 0)

            # 加载VPC节点配置
            if hasattr(self, "vpc_node_entry"):
                self.vpc_node_entry.delete(0, tk.END)
                if socks5.get("vpc_node"):
                    self.vpc_node_entry.insert(0, socks5.get("vpc_node", ""))

            # 加载设备自定义名
            self.device_custom_names = config.get("device_custom_names", {})

            # 加载网段配置
            self.phones = config.get("phones", [])
            self.emails = config.get("emails", [])
            if 'visas' in config:
                self.visas = config['visas']
            if 'visa_checked_state' in config:
                self.visa_checked_state = {k: v for k, v in config['visa_checked_state'].items()}
            if 'visa_sync_manager' in config:
                visa_sync_data = config['visa_sync_manager']
                with self.visa_sync_lock:
                    for card_number, info in visa_sync_data.items():
                        self.visa_sync_manager[card_number] = {
                            'item_id': None,
                            'get_count': info.get('get_count', 0),
                            'using_containers': info.get('using_containers', []),
                            'waiting_containers': [],
                            'wait_count': info.get('wait_count', 0),
                            'disabled': info.get('disabled', False),
                            'executed_after_cvv': {}
                        }
            self.scan_networks = config.get("scan_networks", ["10.0.0", "10.0.1"])
            if "scan_networks" in config:
                self.scan_networks = config["scan_networks"]
                self.network_entry.delete(0, tk.END)
                self.network_entry.insert(0, ", ".join(self.scan_networks))

            # 加载设备列表
            if "devices" in config:
                self.devices = config["devices"]
                self._refresh_device_tree()
                self.status_var.set(f"就绪 - 已加载 {len(self.devices)} 个设备")

            # 刷新列表
            if hasattr(self, 'phone_tree'):
                self._refresh_phone_tree(self.phone_tree)
            if hasattr(self, 'email_tree'):
                self._refresh_email_tree(self.email_tree)
            if hasattr(self, 'visa_tree'):
                self._refresh_visa_tree(self.visa_tree)

            # 恢复 Grid 配置
            # 恢复 Grid 配置
            c_conf = config.get("container_config", {})
            if "dns" in c_conf: 
                self.entry_dns.delete(0, tk.END)
                self.entry_dns.insert(0, c_conf["dns"])
            
            # 加载保存的机型列表
            if "online_models" in c_conf:
                self.online_models = c_conf["online_models"]
                # 使用 online_models 恢复下拉框
                if self.online_models:
                    self.entry_model['values'] = list(self.online_models.keys())
                    
            # model_presets 不再用于恢复列表，仅保留为了兼容或后续需要
            if "model_presets" in c_conf:
                self.model_presets = c_conf["model_presets"]

            # 如果有保存的当前选中机型，则恢复选中
            if "model" in c_conf and c_conf["model"]:
                current_model = c_conf["model"]
                if current_model in self.online_models: # 确保在列表中
                    self.entry_model.set(current_model)
            
            # 恢复随机机型设置
            if "random_model" in c_conf:
                self.random_model_var.set(c_conf["random_model"])
            
            # 恢复指定随机机型设置
            if "static_model" in c_conf:
                self.static_model_var.set(c_conf["static_model"])
                # 如果勾选了指定随机机型，显示输入框
                if self.static_model_var.get() == 1:
                    self.custom_model_frame.pack(side=tk.LEFT, padx=(0, 15))
            
            # 恢复自定义机型列表
            if "custom_model_list" in c_conf:
                self.custom_model_list_var.set(c_conf["custom_model_list"])

            if "gms" in c_conf:
                self.gms_var.set(c_conf["gms"])
            if "rebuild_mode" in c_conf:
                mode = c_conf["rebuild_mode"]
                # 兼容旧选项：合并为「不删除重建」
                if mode in ("新建镜像(不删除)", "成功保存/失败删除重建"):
                    mode = "不删除重建（成功保留/失败删除）"
                self.rebuild_mode_var.set(mode)
            if "max_failures" in c_conf:
                self.max_failures_var.set(c_conf["max_failures"])
            if "region" in c_conf:
                self.entry_region.set(c_conf["region"])
            if "bridge_mode" in c_conf:
                self.bridge_mode_var.set(c_conf["bridge_mode"])
            if "image_version" in c_conf:
                self.image_version_var.set(c_conf["image_version"])
            if "image_keyword" in c_conf:
                self.image_keyword_var.set(c_conf["image_keyword"])

            # 恢复脚本配置
            s_conf = config.get("script_config", {})
            if "name_lang" in s_conf: self.name_lang_var.set(s_conf["name_lang"])
            if "country" in s_conf:
                self.country_entry.delete(0, tk.END)
                self.country_entry.insert(0, s_conf["country"])
            if "char_mode" in s_conf and hasattr(self, "char_mode_var"):
                try:
                    self.char_mode_var.set(int(s_conf["char_mode"]))
                except Exception:
                    self.char_mode_var.set(0)
            if "pwd_mode" in s_conf: self.pwd_mode_var.set(s_conf["pwd_mode"])
            if "pwd_prefix" in s_conf: 
                self.pwd_prefix_entry.delete(0, tk.END)
                self.pwd_prefix_entry.insert(0, s_conf["pwd_prefix"])
            if "pwd_custom" in s_conf:
                self.pwd_custom_entry.delete(0, tk.END)
                self.pwd_custom_entry.insert(0, s_conf["pwd_custom"])
            if "skip_count" in s_conf:
                self.skip_count_entry.delete(0, tk.END)
                self.skip_count_entry.insert(0, s_conf["skip_count"])
            if "tiktok_mode" in s_conf:
                self.tiktok_mode_var.set(s_conf["tiktok_mode"])
            if "jump_mode" in s_conf:
                self.jump_mode_var.set(s_conf["jump_mode"])
            if "channel3_mode" in s_conf:
                self.channel3_mode_var.set(s_conf["channel3_mode"])
            if "channel1_mode" in s_conf:
                self.channel1_mode_var.set(s_conf["channel1_mode"])
            
            if "accessibility_mode" in s_conf:
                self.accessibility_mode_var.set(s_conf["accessibility_mode"])

            if "authorized_enterprise" in s_conf:
                self.authorized_enterprise_var.set(s_conf["authorized_enterprise"])

            if "upload_platform" in s_conf:
                self.upload_platform_var.set(s_conf["upload_platform"])

            # 恢复平台取号配置
            if "platform_phone" in s_conf:
                try:
                    self.platform_phone_var.set(int(s_conf["platform_phone"]))
                except Exception:
                    self.platform_phone_var.set(0)
            if "platform_name" in s_conf:
                self.platform_name_var.set(s_conf["platform_name"] or "tg")
            if "platform_api_key" in s_conf:
                self.platform_api_key_var.set(s_conf["platform_api_key"] or "")
            if "platform_country" in s_conf:
                self.platform_country_var.set(s_conf["platform_country"] or "187")
            if "platform_service" in s_conf:
                self.platform_service_var.set(s_conf["platform_service"] or "wb")
            if "platform_provider_ids" in s_conf:
                self.platform_provider_ids_var.set(s_conf["platform_provider_ids"] or "216")
                


            # 恢复自定义应用列表
            self.custom_open_apps = config.get("custom_open_apps", [])
            if hasattr(self, "open_app_combo"):
                vals = list(self._PRESET_APPS.keys()) + \
                       [a["name"] for a in self.custom_open_apps]
                self._open_app_combo_values = vals
                self.open_app_combo["values"] = vals

            # 恢复打开App配置
            if "open_app_name" in s_conf and hasattr(self, "open_app_var"):
                self.open_app_var.set(s_conf["open_app_name"])
            if "open_app_delay" in s_conf and hasattr(self, "open_app_delay_var"):
                self.open_app_delay_var.set(s_conf["open_app_delay"])

            # 恢复坐标点击配置
            if "coord_tap_x" in s_conf and hasattr(self, "coord_tap_x_var"):
                self.coord_tap_x_var.set(s_conf["coord_tap_x"])
            if "coord_tap_y" in s_conf and hasattr(self, "coord_tap_y_var"):
                self.coord_tap_y_var.set(s_conf["coord_tap_y"])
            if "coord_tap_delay" in s_conf and hasattr(self, "coord_tap_delay_var"):
                self.coord_tap_delay_var.set(s_conf["coord_tap_delay"])

            # 恢复输入文字配置
            if "input_text_content" in s_conf and hasattr(self, "input_text_var"):
                self.input_text_var.set(s_conf["input_text_content"])
            if "input_text_delay" in s_conf and hasattr(self, "input_text_delay_var"):
                self.input_text_delay_var.set(s_conf["input_text_delay"])

            # 恢复点击文字配置
            if "click_text_content" in s_conf and hasattr(self, "click_text_var"):
                self.click_text_var.set(s_conf["click_text_content"])
            if "click_text_delay" in s_conf and hasattr(self, "click_text_delay_var"):
                self.click_text_delay_var.set(s_conf["click_text_delay"])

            # 恢复自定义脚本步骤
            if "custom_script_steps" in config and hasattr(self, "custom_script_steps"):
                try:
                    self.custom_script_steps = self._cs_steps_from_plain(config["custom_script_steps"])
                    if hasattr(self, "_cs_inner"):
                        self._cs_render()
                except Exception:
                    pass

            # 恢复平台养号配置
            for prefix in ("douyin", "kuaishou", "xiaohongshu", "xianyu"):
                c = config.get(f"{prefix}_config", {})
                for i in range(1, 6):
                    attr = f"{prefix}_cfg{i}"
                    if hasattr(self, attr):
                        getattr(self, attr).set(c.get(f"config{i}", ""))

            self.log_message("✓ 配置已加载")
        except Exception as e:
            self.log_message(f"加载配置失败: {e}")
        finally:
            self._loading_config = False

    # ==================== 文件服务器 ====================
    def _start_file_server(self):
        """启动本地文件服务器"""
        if self.file_server_thread and self.file_server_thread.is_alive():
            return
        
        app = self
        
        class FileHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                filename = self.path.lstrip('/')
                if filename in app.in_memory_files:
                    file_data, content_type = app.in_memory_files[filename]
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Length', len(file_data))
                    self.end_headers()
                    self.wfile.write(file_data)
                elif filename == 'get_phone':
                    # 脚本获取可用手机号接口
                    try:
                        use_platform = False
                        try:
                            use_platform = int(getattr(app, "platform_phone_var").get()) == 1
                        except Exception:
                            use_platform = False

                        if use_platform:
                            # 走平台取号（不从手机号管理列表取）
                            phone, url = app._platform_get_phone()
                            if phone:
                                self.send_response(200)
                                self.send_header('Content-Type', 'application/json; charset=utf-8')
                                self.end_headers()
                                res = json.dumps({"code": 200, "phone": phone, "url": url}, ensure_ascii=False)
                                self.wfile.write(res.encode('utf-8'))
                                app.log_message(f"📱 平台取号出号: {phone}")
                            else:
                                self.send_response(200)
                                self.send_header('Content-Type', 'application/json; charset=utf-8')
                                self.end_headers()
                                res = json.dumps({"code": 404, "message": "平台取号失败/无号码"}, ensure_ascii=False)
                                self.wfile.write(res.encode('utf-8'))
                        else:
                            # 原逻辑：从手机号管理列表取
                            with app.phone_lock:
                                target = None
                                for p in app.phones:
                                    if p["usage"] == "未使用":
                                        target = p
                                        p["usage"] = "已使用"
                                        break

                                if target:
                                    self.send_response(200)
                                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                                    self.end_headers()
                                    res = json.dumps({"code": 200, "phone": target["phone"], "url": target["url"]}, ensure_ascii=False)
                                    self.wfile.write(res.encode('utf-8'))

                                    # 异步刷新UI和保存配置
                                    if hasattr(app, 'phone_tree'):
                                        app.root.after(0, lambda: app._refresh_phone_tree(app.phone_tree))
                                    app.root.after(0, app.save_config)
                                    app.log_message(f"📱 接口分发出号: {target['phone']}")
                                else:
                                    self.send_response(200)
                                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                                    self.end_headers()
                                    res = json.dumps({"code": 404, "message": "无可用手机号"}, ensure_ascii=False)
                                    self.wfile.write(res.encode('utf-8'))
                    except Exception as e:
                        app.log_message(f"get_phone 异常: {e}")
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        res = json.dumps({"code": 500, "message": "get_phone exception"}, ensure_ascii=False)
                        self.wfile.write(res.encode('utf-8'))
                elif filename == 'get_email':
                    # 脚本获取可用邮箱接口
                    with app.phone_lock:
                        target = None
                        for e in app.emails:
                            if e["usage"] == "未使用":
                                target = e
                                e["usage"] = "已使用"
                                break

                        if target:
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 200, "email": target["email"], "password": target.get("password", "")}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))

                            app.root.after(0, lambda: app._refresh_email_tree(app.email_tree))
                            app.root.after(0, app.save_config)
                            app.log_message(f"📧 接口分发邮箱: {target['email']}")
                        else:
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 404, "message": "无可用邮箱"}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))
                elif filename == 'get_visa':
                    # 脚本获取可用VISA接口
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(self.path)
                    query = parse_qs(parsed.query)
                    container_name = query.get('container', [''])[0]

                    visa_row = app.get_next_unused_visa_row()
                    if visa_row and visa_row[1] is not None:
                        visa_idx, visa_data = visa_row
                        card_number = visa_data.get("card_number", "")
                        expiry_date = visa_data.get("expiry_date", "")
                        cvv = visa_data.get("cvv", "")

                        # 标记VISA为已使用
                        app.mark_visa_used(visa_idx, container_name)

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        res = json.dumps({
                            "code": 200,
                            "card_number": card_number,
                            "expiry_date": expiry_date,
                            "cvv": cvv
                        }, ensure_ascii=False)
                        self.wfile.write(res.encode('utf-8'))

                        app.root.after(0, lambda: app._refresh_visa_tree(app.visa_tree))
                        app.root.after(0, app.save_config)
                        app.log_message(f"💳 接口分发VISA: {card_number} -> {container_name}")
                    else:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        res = json.dumps({"code": 404, "message": "无可用VISA"}, ensure_ascii=False)
                        self.wfile.write(res.encode('utf-8'))
                elif filename.startswith('ban_visa'):
                    # 脚本标记VISA卡失败接口（成功状态设为"失败"）
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        card_number = (query.get('card_number', ['']) or [''])[0].strip()
                        time_val = (query.get('time', ['']) or [''])[0].strip()
                        if card_number:
                            with app.visa_lock:
                                for v in app.visas:
                                    if v.get("card_number") == card_number:
                                        v["success_status"] = "失败"
                                        if time_val:
                                            v["time"] = time_val
                                        else:
                                            # 自动生成时间
                                            from datetime import datetime
                                            now = datetime.now()
                                            v["time"] = now.strftime("%y/%m.%d %H:%M")
                                        app.root.after(0, lambda: app._refresh_visa_tree(app.visa_tree))
                                        app.root.after(0, app.save_config)
                                        app.log_message(f"❌ 标记VISA失败: {card_number} (时间: {v['time']})")
                                        break
                    except Exception as e:
                        app.log_message(f"ban_visa 异常: {e}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'{"code": 200}')
                elif filename.startswith('success_visa'):
                    # 脚本标记VISA卡成功接口（成功状态设为"成功"）
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        card_number = (query.get('card_number', ['']) or [''])[0].strip()
                        time_val = (query.get('time', ['']) or [''])[0].strip()
                        if card_number:
                            with app.visa_lock:
                                for v in app.visas:
                                    if v.get("card_number") == card_number:
                                        v["success_status"] = "成功"
                                        if time_val:
                                            v["time"] = time_val
                                        else:
                                            # 自动生成时间
                                            from datetime import datetime
                                            now = datetime.now()
                                            v["time"] = now.strftime("%y/%m.%d %H:%M")
                                        app.root.after(0, lambda: app._refresh_visa_tree(app.visa_tree))
                                        app.root.after(0, app.save_config)
                                        app.log_message(f"✅ 标记VISA成功: {card_number} (时间: {v['time']})")
                                        break
                    except Exception as e:
                        app.log_message(f"success_visa 异常: {e}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'{"code": 200}')
                elif filename.startswith('update_visa_status'):
                    # 脚本更新VISA卡状态接口
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        card_number = (query.get('card_number', ['']) or [''])[0].strip()
                        status = (query.get('status', ['']) or [''])[0].strip()
                        time_val = (query.get('time', ['']) or [''])[0].strip()
                        if card_number and status:
                            with app.visa_lock:
                                for v in app.visas:
                                    if v.get("card_number") == card_number:
                                        v["success_status"] = status
                                        if time_val:
                                            v["time"] = time_val
                                        else:
                                            # 自动生成时间
                                            from datetime import datetime
                                            now = datetime.now()
                                            v["time"] = now.strftime("%y/%m.%d %H:%M")
                                        app.root.after(0, lambda: app._refresh_visa_tree(app.visa_tree))
                                        app.root.after(0, app.save_config)
                                        app.log_message(f"📝 更新VISA卡状态: {card_number} -> {status} (时间: {v['time']})")
                                        break
                    except Exception as e:
                        app.log_message(f"update_visa_status 异常: {e}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'{"code": 200}')
                elif filename.startswith('success_phone'):
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        phone = (query.get('phone', ['']) or [''])[0].strip()
                        time_val = (query.get('time', ['']) or [''])[0].strip()

                        with app.phone_lock:
                            for p in app.phones:
                                if p["phone"] == phone:
                                    p["status"] = "成功"
                                    if time_val:
                                        p["time"] = time_val
                                    else:
                                        # 自动生成时间
                                        from datetime import datetime
                                        now = datetime.now()
                                        p["time"] = now.strftime("%y/%m.%d %H:%M")
                                    app.root.after(0, lambda: app._refresh_phone_tree(app.phone_tree))
                                    app.root.after(0, app.save_config)
                                    app.log_message(f"✅ 标记手机号成功: {phone} (时间: {p['time']})")
                                    break
                    except: pass
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"code": 200}')
                elif filename.startswith('ban_phone'):
                    # 脚本标记手机号失败接口
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        phone = (query.get('phone', ['']) or [''])[0].strip()
                        reason = (query.get('reason', ['']) or [''])[0].strip()
                        time_val = (query.get('time', ['']) or [''])[0].strip()
                        if phone:
                            with app.phone_lock:
                                for p in app.phones:
                                    if p["phone"] == phone:
                                        if reason:
                                            p["status"] = reason
                                        else:
                                            p["status"] = "失败"
                                        if time_val:
                                            p["time"] = time_val
                                        else:
                                            # 自动生成时间
                                            from datetime import datetime
                                            now = datetime.now()
                                            p["time"] = now.strftime("%y/%m.%d %H:%M")
                                        app.root.after(0, lambda: app._refresh_phone_tree(app.phone_tree))
                                        app.root.after(0, app.save_config)
                                        app.log_message(f"❌ 标记手机号失败: {phone} (原因: {p['status']}, 时间: {p['time']})")
                                        break
                    except Exception as e:
                        app.log_message(f"ban_phone 异常: {e}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'{"code": 200}')
                elif filename.startswith('add_visa_fail_count'):
                    # 累加VISA失败计数接口
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        phone = (query.get('phone', ['']) or [''])[0].strip()
                        if phone:
                            with app.visa_fail_lock:
                                current_count = app.visa_fail_counts.get(phone, 0)
                                app.visa_fail_counts[phone] = current_count + 1
                                new_count = app.visa_fail_counts[phone]
                            app.log_message(f"VISA fail count [{phone}]: {new_count}/3")
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 200, "fail_count": new_count}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))
                        else:
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 400, "message": "missing phone parameter"}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))
                    except Exception as e:
                        app.log_message(f"add_visa_fail_count error: {e}")
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b'{"code": 500}')
                elif filename.startswith('get_visa_fail_count'):
                    # 查询VISA失败计数接口
                    try:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        phone = (query.get('phone', ['']) or [''])[0].strip()
                        if phone:
                            with app.visa_fail_lock:
                                fail_count = app.visa_fail_counts.get(phone, 0)
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 200, "fail_count": fail_count}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))
                        else:
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 400, "message": "missing phone parameter"}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))
                    except Exception as e:
                        app.log_message(f"get_visa_fail_count error: {e}")
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b'{"code": 500}')
                elif filename.startswith('reset_visa_fail_count'):
                    # 重置VISA失败计数接口
                    try:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(self.path)
                        query = parse_qs(parsed.query)
                        phone = (query.get('phone', ['']) or [''])[0].strip()
                        if phone:
                            with app.visa_fail_lock:
                                app.visa_fail_counts[phone] = 0
                            app.log_message(f"VISA fail count reset: {phone}")
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            self.wfile.write(b'{"code": 200}')
                        else:
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            res = json.dumps({"code": 400, "message": "missing phone parameter"}, ensure_ascii=False)
                            self.wfile.write(res.encode('utf-8'))
                    except Exception as e:
                        app.log_message(f"reset_visa_fail_count error: {e}")
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b'{"code": 500}')
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # 禁止日志输出
        
        def run_server():
            try:
                with socketserver.TCPServer(("", self.file_server_port), FileHandler) as httpd:
                    self.file_server = httpd
                    httpd.serve_forever()
            except Exception as e:
                app.log_message(f"文件服务器启动失败: {e}")
        
        self.file_server_thread = threading.Thread(target=run_server, daemon=True)
        self.file_server_thread.start()
        self.log_message(f"✓ 文件服务器已启动: http://{self.local_ip}:{self.file_server_port}")
    
    # ==================== 拖放上传 ====================
    def _on_file_drop(self, event):
        """处理拖放到设备列表的文件"""
        try:
            # 解析拖放的文件路径
            file_path = event.data.strip('{}')
            if not file_path or not os.path.exists(file_path):
                self.log_message(f"文件路径无效或不存在: {file_path}")
                return
            
            # 确定文件被拖放到哪个设备
            x_root, y_root = self.device_tree.winfo_pointerxy()
            widget_x = self.device_tree.winfo_rootx()
            widget_y = self.device_tree.winfo_rooty()
            x_widget = x_root - widget_x
            y_widget = y_root - widget_y
            
            item_id = self.device_tree.identify('item', x_widget, y_widget)
            if not item_id:
                self.log_message("请将文件拖放到具体的设备行上")
                return
            
            # 获取设备信息
            values = self.device_tree.item(item_id, 'values')
            container_name = values[2]
            host_ip = values[3]
            
            # 查找完整设备信息
            target_device = None
            for d in self.devices:
                if d["container_name"].lstrip("/") == container_name:
                    target_device = d
                    break
            
            if not target_device:
                self.log_message(f"找不到设备: {container_name}")
                return
            
            # 判断文件类型
            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                # 图片文件 - 上传到设备存储
                self.log_message(f"准备上传图片 '{file_name}' 到设备 [{container_name.split('_')[-1]}]")
                threading.Thread(target=self._upload_file_to_device, 
                               args=(file_path, target_device, item_id, "图片"), daemon=True).start()
            elif file_ext in ['.apk']:
                # APK文件 - 安装应用
                self.log_message(f"准备安装APK '{file_name}' 到设备 [{container_name.split('_')[-1]}]")
                threading.Thread(target=self._install_apk_to_device, 
                               args=(file_path, target_device, item_id), daemon=True).start()
            else:
                # 其他文件类型也支持上传
                self.log_message(f"准备上传文件 '{file_name}' 到设备 [{container_name.split('_')[-1]}]")
                threading.Thread(target=self._upload_file_to_device, 
                               args=(file_path, target_device, item_id, "文件"), daemon=True).start()
                
        except Exception as e:
            self.log_message(f"处理拖放文件出错: {e}")
    
    def _upload_file_to_device(self, file_path, device, item_id, file_type="文件"):
        """上传文件到设备存储 (使用API: POST /upload)"""
        try:
            container_name = device["container_name"].lstrip("/")
            
            # 使用统一的连接信息获取方法
            target_ip, target_port, is_bridge = self._get_device_connection_info(device)
            
            device_num = container_name.split('_')[-1]
            log_prefix = f"[{device_num}]"
            
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # KB
            
            self.log_message(f"{log_prefix} 正在上传{file_type}: {file_name} ({file_size:.1f} KB)")
            self._update_device_status(item_id, "上传中...")
            
            # 使用 requests.post 上传文件
            # API: POST http://{ip}:{port}/upload
            api_url = f"http://{target_ip}:{target_port}/upload"
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                response = requests.post(api_url, files=files, timeout=60)

            if response.status_code == 200:
                # 某些接口直接返回文本 "文件上传完成！" 或 JSON
                try:
                    # 尝试解析JSON
                    if "文件上传完成" in response.text:
                         self.log_message(f"{log_prefix} ✓ {file_type}上传成功")
                         self._update_device_status(item_id, "上传成功")
                    else:
                        result = response.json()
                        if result.get('code') == 200:
                            self.log_message(f"{log_prefix} ✓ {file_type}上传成功")
                            self._update_device_status(item_id, "上传成功")
                        else:
                            self.log_message(f"{log_prefix} ✗ 上传失败: {result.get('reason', '未知原因')}")
                            self._update_device_status(item_id, "上传失败")
                except:
                    # 如果不是JSON但状态码200，且包含成功字样
                    if "上传完成" in response.text or "success" in response.text.lower():
                        self.log_message(f"{log_prefix} ✓ {file_type}上传成功")
                        self._update_device_status(item_id, "上传成功")
                    else:
                         self.log_message(f"{log_prefix} ✗ 上传响应异常: {response.text[:100]}")
                         self._update_device_status(item_id, "上传失败")
            else:
                self.log_message(f"{log_prefix} ✗ HTTP错误: {response.status_code}")
                self._update_device_status(item_id, "HTTP错误")
                
        except requests.exceptions.Timeout:
            self.log_message(f"{log_prefix} ✗ 上传超时")
            self._update_device_status(item_id, "上传超时")
        except Exception as e:
            self.log_message(f"{log_prefix} ✗ 上传{file_type}异常: {e}")
            self._update_device_status(item_id, "上传异常")
    
    def _install_apk_to_device(self, file_path, device, item_id):
        """安装APK到设备"""
        try:
            container_name = device["container_name"].lstrip("/")
            host_ip = device.get("host_ip", "")
            device_num = container_name.split('_')[-1]
            log_prefix = f"[{device_num}]"
            
            self.log_message(f"{log_prefix} 正在安装APK: {os.path.basename(file_path)}")
            
            # 调用安装APK API
            api_url = f"http://127.0.0.1:5000/and_api/v1/install_apk/{host_ip}/{container_name}"
            params = {'local': file_path}
            
            response = requests.get(api_url, params=params, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    shell_code = result.get('data', {}).get('shell_code', -1)
                    if shell_code == 0:
                        self.log_message(f"{log_prefix} ✓ APK安装成功")
                        self._update_device_status(item_id, "APK已安装")
                    else:
                        self.log_message(f"{log_prefix} ✗ 安装失败: shell_code={shell_code}")
                else:
                    self.log_message(f"{log_prefix} ✗ 安装失败: {result.get('message', '未知错误')}")
            else:
                self.log_message(f"{log_prefix} ✗ HTTP错误: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.log_message(f"{log_prefix} ✗ 安装超时")
        except Exception as e:
            self.log_message(f"{log_prefix} ✗ 安装APK异常: {e}")
    
    def _update_device_status(self, item_id, status):
        """更新设备状态显示"""
        def do_update():
            try:
                values = list(self.device_tree.item(item_id, 'values'))
                values[4] = status  # 状态列
                self.device_tree.item(item_id, values=values)
            except:
                pass
        self.root.after(0, do_update)
    
    # ==================== 手机号管理 ====================
    def _setup_phone_tab(self, parent):
        """手机号管理Tab内容"""
        self._setup_phone_ui(parent)

    def _setup_email_tab(self, parent):
        """邮箱管理Tab内容"""
        self._setup_email_ui(parent)

    def _setup_phone_ui(self, parent):
        """具体手机UI"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="📝 导入手机", command=self._import_phone_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 删除选中", command=lambda: self._delete_selected_phones(self.phone_tree)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🧨 清空全部", command=lambda: self._clear_all_phones(self.phone_tree)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 重置状态", command=self._reset_phone_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📤 导出未成功", command=self._export_failed_phones).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📤 导出全部", command=self._export_all_phones).pack(side=tk.LEFT, padx=2)
        ttk.Label(toolbar, text="成功:", foreground="green").pack(side=tk.LEFT, padx=(10, 0))
        self.success_label = ttk.Label(toolbar, text="0", foreground="green", font=("微软雅黑", 9, "bold"))
        self.success_label.pack(side=tk.LEFT, padx=(2, 0))
        ttk.Button(toolbar, text="清零", width=4, command=self._reset_success_counter).pack(side=tk.LEFT, padx=(4, 0))
        
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 增加序号列，便于查看总数和位置
        cols = ("序号", "手机号", "使用状态", "成功状态", "API链接", "时间")
        self.phone_tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.phone_tree.heading(col, text=col)
            if col == "序号":
                self.phone_tree.column(col, width=60, anchor="center")
            elif col == "手机号":
                self.phone_tree.column(col, width=120, anchor="center")
            elif "状态" in col:
                self.phone_tree.column(col, width=80, anchor="center")
            elif col == "时间":
                self.phone_tree.column(col, width=100, anchor="center")
            else:  # API链接
                self.phone_tree.column(col, width=280, anchor="w")
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.phone_tree.yview)
        self.phone_tree.configure(yscrollcommand=sb.set)
        self.phone_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.phone_tree.drop_target_register(DND_FILES)
        self.phone_tree.dnd_bind('<<Drop>>', self._on_phone_file_drop)
        
        # 手机号列表右键菜单：删除 / 标记使用状态
        self.phone_tree.bind("<Button-3>", self._on_phone_tree_right_click)
        self.phone_context_menu = tk.Menu(self.root, tearoff=0)
        self.phone_context_menu.add_command(
            label="删除选中", 
            command=lambda: self._delete_selected_phones(self.phone_tree)
        )
        self.phone_context_menu.add_separator()
        self.phone_context_menu.add_command(
            label="标记为未使用", 
            command=lambda: self._set_selected_phone_usage(self.phone_tree, "未使用")
        )
        self.phone_context_menu.add_command(
            label="标记为已使用", 
            command=lambda: self._set_selected_phone_usage(self.phone_tree, "已使用")
        )
        
        self._refresh_phone_tree(self.phone_tree)

    def _setup_email_ui(self, parent):
        """具体邮箱UI"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="📝 导入邮箱", command=self._import_email_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 删除选中", command=lambda: self._delete_selected_emails(self.email_tree)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🧨 清空全部", command=lambda: self._clear_all_emails(self.email_tree)).pack(side=tk.LEFT, padx=2)
        
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("邮箱", "密码", "使用状态", "成功状态")
        self.email_tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.email_tree.heading(col, text=col)
            self.email_tree.column(col, width=150, anchor="center")
        self.email_tree.column("邮箱", width=250, anchor="w")
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.email_tree.yview)
        self.email_tree.configure(yscrollcommand=sb.set)
        self.email_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.email_tree.drop_target_register(DND_FILES)
        self.email_tree.dnd_bind('<<Drop>>', self._on_email_file_drop)
        
        self._refresh_email_tree(self.email_tree)

    def _import_email_dialog(self):
        """导入邮箱对话框"""
        text = self._show_input_dialog("导入邮箱 (格式: 邮箱----密码)")
        if text: self._process_email_import(text, self.email_tree)

    def _on_email_file_drop(self, event):
        """邮箱文件拖放"""
        file_path = event.data.strip('{}')
        if not os.path.isfile(file_path): return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._process_email_import(content, self.email_tree)
        except Exception as e:
            self.log_message(f"读取文件失败: {e}")

    def _process_email_import(self, content, tree=None):
        """处理导入的邮箱数据"""
        lines = content.split('\n')
        count = 0
        for line in lines:
            line = line.strip()
            if not line: continue
            
            pwd = ""
            if "----" in line:
                parts = line.split("----", 1)
                email = parts[0].strip()
                pwd = parts[1].strip()
            else:
                email = line
            
            # 查重
            if not any(e["email"] == email for e in self.emails):
                self.emails.append({
                    "email": email,
                    "password": pwd,
                    "usage": "未使用",
                    "status": "-"
                })
                count += 1
        
        if tree: self._refresh_email_tree(tree)
        self.save_config()
        self.log_message(f"✓ 成功导入 {count} 个邮箱")

    def _refresh_email_tree(self, tree):
        """刷新邮箱列表"""
        if not tree: return
        for item in tree.get_children():
            tree.delete(item)
        for e in self.emails:
            tree.insert("", "end", values=(e["email"], e.get("password",""), e["usage"], e["status"]))

    def _delete_selected_emails(self, tree):
        """删除选中邮箱"""
        selected = tree.selection()
        if not selected: return
        
        to_remove = []
        for item in selected:
            val = tree.item(item, 'values')
            if val: to_remove.append(val[0]) # email
        
        self.emails = [e for e in self.emails if e["email"] not in to_remove]
        self._refresh_email_tree(tree)
        self.save_config()

    def _clear_all_emails(self, tree):
        """清空邮箱"""
        if messagebox.askyesno("确认", "确定清空所有邮箱数据吗？"):
            self.emails = []
            self._refresh_email_tree(tree)
            self.save_config()

    # ==================== VISA卡管理 ====================
    def _setup_visa_tab(self, parent):
        """VISA卡管理Tab内容"""
        self._setup_visa_ui(parent)

    def _setup_visa_ui(self, parent):
        """具体VISA UI"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="📝 导入VISA", command=self._import_visa_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 删除选中", command=lambda: self._delete_selected_visas(self.visa_tree)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🧨 清空全部", command=lambda: self._clear_all_visas(self.visa_tree)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 重置状态", command=self._reset_visa_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📤 导出未成功", command=self._export_failed_visas).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📤 导出全部", command=self._export_all_visas).pack(side=tk.LEFT, padx=2)
        
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("全/反", "序号", "卡号", "日期", "CVV", "使用状态", "获取次数", "等待计数", "成功状态", "时间")
        self.visa_tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.visa_tree.heading(col, text=col)
            if col == "全/反":
                self.visa_tree.column(col, width=50, anchor="center")
            elif col == "序号":
                self.visa_tree.column(col, width=60, anchor="center")
            elif col == "卡号":
                self.visa_tree.column(col, width=180, anchor="w")
            elif col in ["日期", "CVV"]:
                self.visa_tree.column(col, width=80, anchor="center")
            elif col == "时间":
                self.visa_tree.column(col, width=100, anchor="center")
            elif "状态" in col:
                self.visa_tree.column(col, width=100, anchor="center")
            elif col in ["获取次数", "等待计数"]:
                self.visa_tree.column(col, width=80, anchor="center")
            else:
                self.visa_tree.column(col, width=100, anchor="center")
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.visa_tree.yview)
        self.visa_tree.configure(yscrollcommand=sb.set)
        self.visa_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.visa_tree.drop_target_register(DND_FILES)
        self.visa_tree.dnd_bind('<<Drop>>', self._on_visa_file_drop)
        
        # 绑定点击事件
        self.visa_tree.bind("<Button-1>", self._on_visa_tree_click)
        self.visa_tree.bind("<Button-3>", self._show_visa_tree_context_menu)
        
        self._refresh_visa_tree(self.visa_tree)

    def _on_visa_tree_click(self, event):
        """处理VISA数据表格的点击事件，实现复选框功能"""
        region = self.visa_tree.identify("region", event.x, event.y)
        
        if region == "heading":
            column_id = self.visa_tree.identify_column(event.x)
            if column_id == '#1':  # 点击了"全/反"表头
                self._toggle_all_visa_selection()
            return
        
        item_id = self.visa_tree.identify_row(event.y)
        column_id = self.visa_tree.identify_column(event.x)
        
        if item_id and column_id == '#1':  # 点击了复选框列
            is_checked = self.visa_checked_state.get(item_id, False)
            new_state = not is_checked
            self.visa_checked_state[item_id] = new_state
            
            checkbox_char = "☑" if new_state else "☐"
            current_values = list(self.visa_tree.item(item_id, "values"))
            current_values[0] = checkbox_char
            self.visa_tree.item(item_id, values=tuple(current_values))
            self.save_config()

    def _toggle_all_visa_selection(self):
        """切换VISA数据表格中所有项的勾选状态"""
        all_item_ids = self.visa_tree.get_children()
        if not all_item_ids:
            return
        
        all_currently_checked = all(self.visa_checked_state.get(item_id, False) for item_id in all_item_ids)
        new_state = not all_currently_checked
        
        for item_id in all_item_ids:
            self.visa_checked_state[item_id] = new_state
            checkbox_char = "☑" if new_state else "☐"
            current_values = list(self.visa_tree.item(item_id, "values"))
            current_values[0] = checkbox_char
            self.visa_tree.item(item_id, values=tuple(current_values))
        
        self.save_config()

    def _import_visa_dialog(self):
        """导入VISA对话框"""
        text = self._show_input_dialog("导入VISA (格式: 卡号----日期----CVV 或 卡号\t日期\tCVV)")
        if text:
            self._process_visa_import(text, self.visa_tree)

    def _on_visa_file_drop(self, event):
        """VISA文件拖放"""
        file_path = event.data.strip('{}')
        if not os.path.isfile(file_path):
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._process_visa_import(content, self.visa_tree)
        except Exception as e:
            self.log_message(f"读取文件失败: {e}")

    def _parse_visa_line(self, line):
        """智能解析VISA数据行，支持多种格式"""
        line = line.strip()
        card_number, cvv, expiry_date = "", "", ""
        
        # 格式1: [卡号]\t[CVV]\t年份年月份月
        bracket_format = re.match(r'\[(\d{16})\]\s+\[(\d{3})\]\s+(\d{4})年(\d{1,2})月', line)
        if bracket_format:
            card_number = bracket_format.group(1)
            cvv = bracket_format.group(2)
            year = bracket_format.group(3)[-2:]
            month = bracket_format.group(4).zfill(2)
            expiry_date = f"{month}/{year}"
            return card_number, expiry_date, cvv
        
        # 格式2: 卡号----日期----CVV 或 卡号\t日期\tCVV
        if "----" in line:
            parts = line.split("----", 2)
        elif "\t" in line:
            parts = line.split("\t", 2)
        else:
            parts = line.split(",", 2)
        
        if len(parts) >= 3:
            card_number = parts[0].strip()
            expiry_date = parts[1].strip()
            cvv = parts[2].strip()
            
            # 标准化日期格式为 MM/YY
            date_match_ym = re.search(r'(\d{4})-(\d{2})', expiry_date)
            date_match_my = re.search(r'(\d{2})\/(\d{2})', expiry_date)
            if date_match_ym:
                yyyy, mm = date_match_ym.groups()
                expiry_date = f"{mm}/{yyyy[-2:]}"
            elif not date_match_my:
                # 尝试其他格式
                date_match = re.search(r'(\d{2})(\d{2})', expiry_date)
                if date_match:
                    mm, yy = date_match.groups()
                    expiry_date = f"{mm}/{yy}"
            
            if len(card_number) == 16 and len(cvv) == 3:
                return card_number, expiry_date, cvv
        
        # 格式3: 尝试从行中提取16位卡号、3位CVV和日期
        card_match = re.search(r'\b(\d{16})\b', line)
        if card_match:
            card_number = card_match.group(1)
            line = line.replace(card_number, "", 1)
        
        cvv_match = re.search(r'\b(\d{3})\b', line)
        if cvv_match:
            cvv = cvv_match.group(1)
            line = line.replace(cvv, "", 1)
        
        date_match_ym = re.search(r'(\d{4})-(\d{2})', line)
        date_match_my = re.search(r'(\d{2})\/(\d{2})', line)
        if date_match_ym:
            yyyy, mm = date_match_ym.groups()
            expiry_date = f"{mm}/{yyyy[-2:]}"
        elif date_match_my:
            expiry_date = date_match_my.group(0)
        
        if card_number and cvv and expiry_date:
            return card_number, expiry_date, cvv
        
        return None

    def _process_visa_import(self, content, tree=None):
        """处理导入的VISA数据"""
        lines = content.split('\n')
        count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 去除包含汉字的后缀（如----成功----时间----等）
            line = re.sub(r'----[\u4e00-\u9fff]+.*$', '', line)

            parsed = self._parse_visa_line(line)
            if parsed:
                card_number, expiry_date, cvv = parsed
                # 查重
                if not any(v.get("card_number") == card_number for v in self.visas):
                    self.visas.append({
                        "card_number": card_number,
                        "expiry_date": expiry_date,
                        "cvv": cvv,
                        "status": "未使用",
                        "get_count": 0,
                        "wait_count": 0,
                        "success_status": "未成功",
                        "time": ""
                    })
                    count += 1
                else:
                    self.log_message(f"跳过重复VISA: {card_number}")
            else:
                if line:
                    self.log_message(f"警告：跳过格式错误的VISA数据行: {line}")
        
        if tree:
            self._refresh_visa_tree(tree)
        self.save_config()
        self.log_message(f"✓ 成功导入 {count} 个VISA")

    def _refresh_visa_tree(self, tree):
        """刷新VISA列表"""
        if not tree:
            return
        for item in tree.get_children():
            tree.delete(item)

        for idx, v in enumerate(self.visas, 1):
            checkbox_char = "☑" if self.visa_checked_state.get(f"visa_{idx}", False) else "☐"
            item_id = tree.insert("", "end", values=(
                checkbox_char,
                idx,
                v.get("card_number", ""),
                v.get("expiry_date", ""),
                v.get("cvv", ""),
                v.get("status", "未使用"),
                str(v.get("get_count", 0)),
                str(v.get("wait_count", 0)),
                v.get("success_status", "未成功"),
                v.get("time", "")
            ))
            self.visa_checked_state[item_id] = self.visa_checked_state.get(f"visa_{idx}", False)

    def _delete_selected_visas(self, tree):
        """删除选中VISA"""
        selected = tree.selection()
        if not selected:
            return
        
        to_remove = []
        for item in selected:
            val = tree.item(item, 'values')
            if val and len(val) > 2:
                card_number = val[2]  # 卡号列
                to_remove.append(card_number)
        
        self.visas = [v for v in self.visas if v.get("card_number") not in to_remove]
        # 同时清理同步管理器中的数据
        with self.visa_sync_lock:
            for card_number in to_remove:
                if card_number in self.visa_sync_manager:
                    del self.visa_sync_manager[card_number]
        self._refresh_visa_tree(tree)
        self.save_config()

    def _clear_all_visas(self, tree):
        """清空VISA"""
        if messagebox.askyesno("确认", "确定清空所有VISA数据吗？"):
            self.visas = []
            with self.visa_sync_lock:
                self.visa_sync_manager.clear()
            self.visa_checked_state.clear()
            self._refresh_visa_tree(tree)
            self.save_config()

    def _show_visa_tree_context_menu(self, event):
        """显示VISA右键菜单"""
        item = self.visa_tree.identify_row(event.y)
        if item:
            self.visa_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="标记为未使用", command=lambda: self._set_selected_visa_status("未使用"))
            menu.add_command(label="标记为已使用", command=lambda: self._set_selected_visa_status("使用中"))
            menu.add_command(label="标记为已禁用", command=lambda: self._set_selected_visa_status("已禁用"))
            menu.add_separator()
            menu.add_command(label="复制卡号", command=lambda: self._copy_visa_value(item, 2))
            menu.post(event.x_root, event.y_root)

    def _set_selected_visa_status(self, status):
        """设置选中VISA的状态"""
        selected = self.visa_tree.selection()
        for item in selected:
            val = list(self.visa_tree.item(item, 'values'))
            if val and len(val) > 2:
                card_number = val[2]
                for v in self.visas:
                    if v.get("card_number") == card_number:
                        v["status"] = status
                        val[5] = status
                        self.visa_tree.item(item, values=tuple(val))
                        break
        self.save_config()

    def _copy_visa_value(self, item, col_index):
        """复制VISA值到剪贴板"""
        val = self.visa_tree.item(item, 'values')
        if val and len(val) > col_index:
            self.root.clipboard_clear()
            self.root.clipboard_append(val[col_index])
            self.log_message(f"已复制: {val[col_index]}")

    # ==================== VISA同步计算逻辑 ====================
    def get_next_unused_visa_row(self):
        """返回下一个未被使用的VISA，没有则返回None
        
        通道三模式下：允许同一VISA被获取最多4次
        其他模式：只返回"未使用"的VISA
        """
        with self.visa_lock:
            # 检查是否为通道三模式
            is_channel_three = self.channel3_mode_var.get() == 1
            
            for idx, v in enumerate(self.visas):
                card_number = v.get("card_number", "")
                status = v.get("status", "未使用")
                get_count = v.get("get_count", 0)
                
                # 检查是否被禁用
                with self.visa_sync_lock:
                    visa_info = self.visa_sync_manager.get(card_number, {})
                    is_disabled = visa_info.get('disabled', False)
                
                if is_disabled or status == "已禁用":
                    continue
                
                # 通道三模式：允许获取次数<4的VISA
                if is_channel_three:
                    if get_count < 4:
                        return idx, v
                else:
                    # 非通道三模式：只返回"未使用"的VISA
                    if status == "未使用":
                        return idx, v
            
            return None, None

    def mark_visa_used(self, visa_idx, container_name):
        """标记VISA为已使用
        
        通道三模式下：累加容器编号到使用状态，更新获取次数+1
        其他模式：直接标记为"使用中(容器编号)"
        """
        if visa_idx is None or visa_idx >= len(self.visas):
            return
        
        with self.visa_lock:
            v = self.visas[visa_idx]
            card_number = v.get("card_number", "")
            is_channel_three = self.channel3_mode_var.get() == 1
            
            # 提取容器编号（例如从"xxx_1_011"提取"11"）
            container_suffix = self._extract_container_suffix(container_name)
            
            if is_channel_three:
                # 通道三模式：累加容器编号，更新获取次数
                with self.visa_sync_lock:
                    if card_number not in self.visa_sync_manager:
                        self.visa_sync_manager[card_number] = {
                            'item_id': visa_idx,
                            'get_count': 0,
                            'using_containers': [],
                            'waiting_containers': [],
                            'wait_count': 0,
                            'disabled': False,
                            'executed_after_cvv': {}
                        }
                    
                    visa_info = self.visa_sync_manager[card_number]
                    
                    # 添加容器编号到列表（避免重复）
                    if container_suffix not in visa_info['using_containers']:
                        visa_info['using_containers'].append(container_suffix)
                    
                    # 更新获取次数
                    visa_info['get_count'] += 1
                    get_count = visa_info['get_count']
                    
                    # 更新数据
                    v['get_count'] = get_count
                    using_containers_sorted = sorted(visa_info['using_containers'])
                    using_containers_str = ','.join(str(x) for x in using_containers_sorted)
                    v['status'] = f"使用中({using_containers_str})"
                    
                    self.log_message(f"VISA {card_number} 被容器 {container_suffix} 获取，当前获取次数: {get_count}/4，使用容器: {using_containers_str}")
                    
                    # 获取次数达到4次时，立即禁用VISA
                    if get_count >= 4:
                        visa_info['disabled'] = True
                        v['status'] = "已禁用"
                        v['success_status'] = "已禁用"
                        self.log_message(f"VISA {card_number} 获取次数达到4次，已禁用")
            else:
                # 非通道三模式：直接标记为"使用中(容器编号)"
                v['status'] = f"使用中({container_suffix})"
            
            # 刷新UI
            self.root.after(0, lambda: self._refresh_visa_tree(self.visa_tree))
            self.save_config()

    def handle_visa_wait(self, card_number, key, ip):
        """处理VISA等待请求：容器执行完CVV脚本后进入等待状态
        
        当等待计数达到4次时，释放所有等待的容器，让它们继续执行后续流程
        """
        try:
            container_name = key[0] if isinstance(key, tuple) and len(key) > 0 else str(key)
            container_suffix = self._extract_container_suffix(container_name)
            
            self.log_message(f"📩 收到VISA等待请求：卡号={card_number}, 容器={container_suffix}, key={key}, ip={ip}")
            
            with self.visa_sync_lock:
                # 初始化VISA同步信息（如果不存在）
                if card_number not in self.visa_sync_manager:
                    self.visa_sync_manager[card_number] = {
                        'item_id': None,
                        'get_count': 0,
                        'using_containers': [],
                        'waiting_containers': [],
                        'wait_count': 0,
                        'disabled': False,
                        'executed_after_cvv': {}
                    }
                
                visa_info = self.visa_sync_manager[card_number]
                
                # 检查该容器是否已经在等待列表中（防止重复添加）
                existing_keys = [c[0] for c in visa_info['waiting_containers']]
                if key in existing_keys:
                    self.log_message(f"⚠️ 容器 {container_suffix} 已在VISA {card_number} 的等待列表中")
                    return
                
                # 添加等待容器
                current_time = time.time()
                visa_info['waiting_containers'].append((key, container_suffix, current_time))
                visa_info['wait_count'] += 1
                wait_count = visa_info['wait_count']
                
                # 更新数据中的等待计数
                for v in self.visas:
                    if v.get("card_number") == card_number:
                        v['wait_count'] = wait_count
                        break
                
                self.log_message(f"⏳ VISA {card_number} 等待计数: {wait_count}/4，等待容器: {[c[1] for c in visa_info['waiting_containers']]}")
                
                # 更新UI中的等待计数
                self.root.after(0, lambda: self._update_visa_wait_count_in_ui(card_number, wait_count))
            
            # 检查是否达到4次等待，如果是则释放所有容器
            if wait_count >= 4:
                self.log_message(f"🔔 【达到计数上限】VISA {card_number} 等待计数达到4次，立即释放所有等待容器！")
                self._release_visa_waiting_containers(card_number)
        
        except Exception as e:
            self.log_message(f"❌ 处理VISA等待请求时出错: {e}")
            import traceback
            self.log_message(traceback.format_exc())

    def _update_visa_wait_count_in_ui(self, card_number, wait_count):
        """更新UI中VISA的等待计数"""
        try:
            for item_id in self.visa_tree.get_children():
                values = list(self.visa_tree.item(item_id, "values"))
                if len(values) > 2 and values[2] == card_number:
                    # 确保values有足够的元素
                    while len(values) < 9:
                        values.append("")
                    # 更新等待计数列（第8列，索引7）
                    values[7] = str(wait_count)
                    self.visa_tree.item(item_id, values=values)
                    break
        except Exception as e:
            self.log_message(f"更新VISA等待计数UI时出错: {e}")

    def _release_visa_waiting_containers(self, card_number):
        """释放所有等待该VISA的容器"""
        with self.visa_sync_lock:
            visa_info = self.visa_sync_manager.get(card_number)
            if not visa_info:
                return
            
            waiting_containers = visa_info['waiting_containers']
            self.log_message(f"🔓 开始释放VISA {card_number}，等待容器数量: {len(waiting_containers)}")
            
            # 这里可以发送信号给等待的容器，让它们继续执行
            # 具体实现取决于你的容器通信机制
            
            # 清空等待列表
            visa_info['waiting_containers'].clear()
            visa_info['wait_count'] = 0
            
            # 更新数据
            for v in self.visas:
                if v.get("card_number") == card_number:
                    v['wait_count'] = 0
                    break
            
            self.log_message(f"VISA {card_number} 已释放所有等待容器")

    def _extract_container_suffix(self, container_name):
        """从容器名称中提取尾号数字，例如 xxx_1_011 -> 11"""
        try:
            # 去掉开头的 /
            name = str(container_name).lstrip("/")
            # 按 _ 分割，取最后一部分
            parts = name.split("_")
            if len(parts) >= 1:
                # 最后一部分转为整数
                return int(parts[-1])
        except:
            pass
        return 0

    def _serialize_visa_sync_manager(self):
        """序列化VISA同步管理器，只保存关键信息"""
        visa_sync_data = {}
        with self.visa_sync_lock:
            for card_number, info in self.visa_sync_manager.items():
                visa_sync_data[card_number] = {
                    'get_count': info.get('get_count', 0),
                    'wait_count': info.get('wait_count', 0),
                    'disabled': info.get('disabled', False),
                    'using_containers': info.get('using_containers', [])
                }
        return visa_sync_data

    def _show_input_dialog(self, title):
        """通用多行输入框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x400")
        
        txt = scrolledtext.ScrolledText(dialog)
        txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        result = [None]
        def on_ok():
            result[0] = txt.get("1.0", tk.END)
            dialog.destroy()
        
        ttk.Button(dialog, text="确定导入", command=on_ok).pack(pady=5)
        self.root.wait_window(dialog)
        return result[0]

    def _on_phone_file_drop(self, event):
        """手机号文件拖放处理"""
        file_path = event.data.strip('{}')
        if not os.path.isfile(file_path):
            return
            
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext != '.txt':
            messagebox.showwarning("格式错误", "目前只支持 .txt 文本文件导入")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._process_phone_import(content, self.phone_tree)
        except Exception as e:
            self.log_message(f"读取文件失败: {e}")

    def _process_phone_import(self, content, tree=None):
        """处理导入的数据"""
        lines = content.split('\n')
        count = 0
        for line in lines:
            line = line.strip()
            if not line: continue

            # 去除包含汉字的后缀（如----成功----时间----等）
            line = re.sub(r'----[\u4e00-\u9fff]+.*$', '', line)

            if "----" in line:
                parts = line.split("----", 1)
                phone = parts[0].strip()
                url = parts[1].strip()
                
                # 查重
                if not any(p["phone"] == phone for p in self.phones):
                    self.phones.append({
                        "phone": phone,
                        "url": url,
                        "usage": "未使用",
                        "status": "未成功",
                        "time": ""
                    })
                    count += 1
        
        self.save_config()
        if tree:
            self._refresh_phone_tree(tree)
        elif hasattr(self, 'phone_tree'):
            self._refresh_phone_tree(self.phone_tree)
            
        self.log_message(f"✓ 手机号导入成功: {count} 条")
        return count

    def _refresh_phone_tree(self, tree):
        """刷新手机号列表显示"""
        for item in tree.get_children():
            tree.delete(item)
        for idx, p in enumerate(self.phones, start=1):
            tree.insert(
                "",
                tk.END,
                values=(idx, p["phone"], p["usage"], p["status"], p["url"], p.get("time", ""))
            )

    def _import_phone_dialog(self):
        """弹出导入对话框 (文本导入)"""
        import_win = tk.Toplevel(self.root)
        import_win.title("文本导入手机号")
        import_win.geometry("600x400")
        
        ttk.Label(import_win, text="请输入数据 (格式: +123456789----http://... 每行一条):", padding=5).pack(fill=tk.X)
        
        text_area = scrolledtext.ScrolledText(import_win, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(import_win, padding=5)
        btn_frame.pack(fill=tk.X)
        
        def do_import():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                import_win.destroy()
                return
            
            self._process_phone_import(content)
            import_win.destroy()
            
        ttk.Button(btn_frame, text="确认导入", command=do_import).pack(side=tk.RIGHT, padx=5)
        
    def _delete_selected_phones(self, tree):
        """删除选中的手机号"""
        selected = tree.selection()
        if not selected:
            return
        
        if not messagebox.askyesno("确认", f"确定删除选中的 {len(selected)} 条记录吗？"):
            return
            
        for item in selected:
            values = tree.item(item, "values")
            # values: (序号, 手机号, 使用状态, 成功状态, API链接)
            phone = values[1]
            self.phones = [p for p in self.phones if p["phone"] != phone]
        
        self.save_config()
        self._refresh_phone_tree(tree)

    def _set_selected_phone_usage(self, tree, usage_value):
        """将选中的手机号修改为指定使用状态（未使用 / 已使用）"""
        selected = tree.selection()
        if not selected:
            return
        
        for item in selected:
            values = tree.item(item, "values")
            if not values:
                continue
            phone = values[1]  # 第二列是手机号
            for p in self.phones:
                if p["phone"] == phone:
                    p["usage"] = usage_value
                    break
        
        self.save_config()
        self._refresh_phone_tree(tree)

    def _on_phone_tree_right_click(self, event):
        """手机号列表右键菜单：定位行并弹出菜单"""
        try:
            # 定位到当前鼠标所在行
            item_id = self.phone_tree.identify_row(event.y)
            if item_id:
                # 选中该行，方便后续操作
                self.phone_tree.selection_set(item_id)
                self.phone_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                self.phone_context_menu.grab_release()
            except Exception:
                pass

    def _clear_all_phones(self, tree):
        """清空所有手机号"""
        if not self.phones:
            return
        if not messagebox.askyesno("确认", "确定清空所有手机号记录吗？"):
            return
            
        self.phones = []
        self.save_config()
        self._refresh_phone_tree(tree)

    def _reset_phone_status(self):
        """重置手机号状态：请求异常/失败/未成功/请求无效的使用状态改为未使用，成功状态改为未成功"""
        count_usage = 0  # 使用状态重置数量
        count_success = 0  # 成功状态重置数量
        
        for p in self.phones:
            # 处理成功状态(status)：请求异常/失败/未成功/请求无效 -> 使用状态改为未使用，成功状态改为未成功
            status = p.get("status", "")
            if status in ["请求异常", "失败", "未成功", "请求无效"]:
                p["usage"] = "未使用"
                p["status"] = "未成功"
                count_usage += 1
                count_success += 1
        
        self.save_config()
        self._refresh_phone_tree(self.phone_tree)
        self.log_message(f"✓ 重置完成：{count_usage} 个手机号已重置")

    def _export_failed_phones(self):
        """导出未成功的手机号"""
        # 筛选非成功的 (状态不是 "成功" 的都算未成功)
        failed_phones = [p for p in self.phones if p.get("status") != "成功"]
        
        if not failed_phones:
            messagebox.showinfo("提示", "没有未成功的手机号")
            return
            
        # 生成文件名: 时间 数量未成功.txt
        timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
        count = len(failed_phones)
        filename = f"{timestamp} {count}个未成功.txt"
        
        # 保存路径: 当前用户桌面\未成功手机号（兼容不同电脑）
        export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "未成功手机号")
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建导出目录: {e}")
                return

        filepath = os.path.join(export_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for p in failed_phones:
                    # 格式: phone----url----status----time
                    phone = p.get("phone", "")
                    url = p.get("url", "")
                    status = p.get("status", "")
                    time_str = p.get("time", "")
                    f.write(f"{phone}----{url}----{status}----{time_str}\n")
            
            messagebox.showinfo("导出成功", f"已导出 {count} 条数据至:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", f"无法写入文件: {e}")

    def _export_all_phones(self):
        """导出全部手机号（包含成功和未成功的）"""
        if not self.phones:
            messagebox.showinfo("提示", "没有手机号数据")
            return

        # 生成文件名: 时间 数量全部.txt
        timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
        count = len(self.phones)
        filename = f"{timestamp} {count}个全部.txt"

        # 保存路径: 当前用户桌面\二次导出手机号
        export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "二次导出手机号")
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建导出目录: {e}")
                return

        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for p in self.phones:
                    # 格式: phone----url----status----time
                    phone = p.get("phone", "")
                    url = p.get("url", "")
                    status = p.get("status", "")
                    time_str = p.get("time", "")
                    f.write(f"{phone}----{url}----{status}----{time_str}\n")

            messagebox.showinfo("导出成功", f"已导出 {count} 条数据至:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", f"无法写入文件: {e}")

    def _reset_visa_status(self):
        """重置VISA状态：请求异常/失败/未成功/请求无效的使用状态改为未使用，成功状态改为未成功，
        同时重置visa_sync_manager中的disabled和使用容器记录
        """
        count_usage = 0  # 使用状态重置数量
        count_success = 0  # 成功状态重置数量
        
        with self.visa_sync_lock:
            for v in self.visas:
                card_number = v.get("card_number", "")
                success_status = v.get("success_status", "")
                if success_status in ["请求异常", "失败", "未成功", "请求无效"]:
                    v["status"] = "未使用"
                    v["success_status"] = "未成功"
                    count_usage += 1
                    count_success += 1
                    
                    # 同时重置 visa_sync_manager 中对应的状态
                    if card_number in self.visa_sync_manager:
                        self.visa_sync_manager[card_number]['disabled'] = False
                        self.visa_sync_manager[card_number]['using_containers'] = []
        
        self.save_config()
        self._refresh_visa_tree(self.visa_tree)
        self.log_message(f"✓ 重置完成：{count_usage} 个VISA已重置")

    def _export_failed_visas(self):
        """导出未成功的VISA卡"""
        # 筛选非成功的 (成功状态不是 "成功" 的都算未成功)
        failed_visas = [v for v in self.visas if v.get("success_status") != "成功"]

        if not failed_visas:
            messagebox.showinfo("提示", "没有未成功的VISA卡")
            return

        # 生成文件名: 时间 数量个未成功.txt
        timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
        count = len(failed_visas)
        filename = f"{timestamp} {count}个未成功.txt"

        # 保存路径: 当前用户桌面\未成功visa（兼容不同电脑）
        export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "未成功visa")
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建导出目录: {e}")
                return

        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for v in failed_visas:
                    # 格式: card_number----expiry_date----cvv----success_status----time
                    card_number = v.get("card_number", "")
                    expiry_date = v.get("expiry_date", "")
                    cvv = v.get("cvv", "")
                    success_status = v.get("success_status", "")
                    time_str = v.get("time", "")
                    f.write(f"{card_number}----{expiry_date}----{cvv}----{success_status}----{time_str}\n")

            messagebox.showinfo("导出成功", f"已导出 {count} 条数据至:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", f"无法写入文件: {e}")

    def _export_all_visas(self):
        """导出全部VISA卡（包含成功和未成功的）"""
        if not self.visas:
            messagebox.showinfo("提示", "没有VISA卡数据")
            return

        # 生成文件名: 时间 数量个全部.txt
        timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
        count = len(self.visas)
        filename = f"{timestamp} {count}个全部.txt"

        # 保存路径: 当前用户桌面\二次导出visa
        export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "二次导出visa")
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建导出目录: {e}")
                return

        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for v in self.visas:
                    # 格式: card_number----expiry_date----cvv----success_status----time
                    card_number = v.get("card_number", "")
                    expiry_date = v.get("expiry_date", "")
                    cvv = v.get("cvv", "")
                    success_status = v.get("success_status", "")
                    time_str = v.get("time", "")
                    f.write(f"{card_number}----{expiry_date}----{cvv}----{success_status}----{time_str}\n")

            messagebox.showinfo("导出成功", f"已导出 {count} 条数据至:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", f"无法写入文件: {e}")

    # ==================== 后台脚本/APK安装 ====================
    def on_close(self):
        """关闭程序时保存配置"""
        self.save_config()
        self.root.destroy()

    def run(self):
        """运行程序"""
        self.root.mainloop()


def main():
    """主函数"""
    app = DeviceManageTool()
    app.run()


if __name__ == "__main__":
    main()

