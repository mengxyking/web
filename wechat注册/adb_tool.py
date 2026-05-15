#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB 工具箱
布局参考 sbgj.py，设备列表改为 adb devices，其余区域为空架子。
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import queue

try:
    from tkinterdnd2 import TkinterDnD
    _HAS_DND = True
except ImportError:
    _HAS_DND = False


class AdbTool:
    def __init__(self):
        if _HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("ADB 工具箱 v1.0")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 设备相关
        self.devices = []          # [{"id": str, "status": str}]
        self.device_checked = {}   # {iid: bool}
        self.is_refreshing = False

        # 日志队列
        self.log_queue = queue.Queue()

        # 构建界面
        self.setup_ui()

        # 启动日志轮询
        self.process_log_queue()

        # 启动后自动刷新
        self.root.after(500, self.refresh_devices)

    # ─────────────────────────── UI ───────────────────────────

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.root_notebook = ttk.Notebook(main_frame)
        self.root_notebook.pack(fill=tk.BOTH, expand=True)

        # ══ Tab 1: 设备控制中心 ══════════════════════════════════
        device_view = ttk.Frame(self.root_notebook)
        self.root_notebook.add(device_view, text=" 设备控制中心 ")

        self.paned_window = ttk.PanedWindow(device_view, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # ── 左侧：设备列表 ────────────────────────────────────
        left_frame = ttk.LabelFrame(self.paned_window, text="设备列表", padding=5)
        self.paned_window.add(left_frame, weight=1)

        # 顶部信息行
        top_row = ttk.Frame(left_frame)
        top_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top_row, text="ADB 已连接设备:").pack(side=tk.LEFT)
        self.device_count_label = ttk.Label(top_row, text="(0 台)", foreground="gray")
        self.device_count_label.pack(side=tk.LEFT, padx=5)

        # TreeView
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("选择", "序号", "设备ID", "状态")
        self.device_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=15
        )
        self.device_tree.heading("选择", text="☐")
        self.device_tree.heading("序号", text="序号")
        self.device_tree.heading("设备ID", text="设备 ID")
        self.device_tree.heading("状态", text="状态")
        self.device_tree.column("选择", width=40,  anchor="center")
        self.device_tree.column("序号", width=50,  anchor="center")
        self.device_tree.column("设备ID", width=260)
        self.device_tree.column("状态", width=90,  anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                   command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.device_tree.bind("<Button-1>", self.on_treeview_click)

        # 按钮行
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        self.refresh_button = ttk.Button(
            btn_frame, text="🔍 刷新设备",
            command=self.refresh_devices, width=15
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="☑ 全选/取消",
            command=self.toggle_all_selection, width=12
        ).pack(side=tk.LEFT, padx=5)

        # ── 右侧 ──────────────────────────────────────────────
        right_view = ttk.Frame(self.paned_window, padding=5)
        self.paned_window.add(right_view, weight=2)

        # 容器配置中心（占位）
        container_frame = ttk.LabelFrame(right_view, text="容器配置中心", padding=5)
        container_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(container_frame, text="（待开发）", foreground="gray").pack(anchor="w")

        # 功能 Notebook
        self.func_notebook = ttk.Notebook(right_view)
        self.func_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        for tab_name in ("脚本任务", "代理网络", "脚本配置"):
            tab = ttk.Frame(self.func_notebook, padding=5)
            self.func_notebook.add(tab, text=tab_name)
            ttk.Label(tab, text=f"（{tab_name}区待开发）", foreground="gray").pack(expand=True)

        # 运行日志
        log_frame = ttk.LabelFrame(right_view, text="运行日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=15, width=40, font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ══ Tab 2: 手机号管理 ════════════════════════════════════
        phone_tab = ttk.Frame(self.root_notebook, padding=10)
        self.root_notebook.add(phone_tab, text=" 手机号管理 ")
        ttk.Label(phone_tab, text="（手机号管理区待开发）", foreground="gray").pack(expand=True)

        # ══ Tab 3: 邮箱管理 ══════════════════════════════════════
        email_tab = ttk.Frame(self.root_notebook, padding=10)
        self.root_notebook.add(email_tab, text=" 邮箱管理 ")
        ttk.Label(email_tab, text="（邮箱管理区待开发）", foreground="gray").pack(expand=True)

        # ══ Tab 4: VISA卡管理 ════════════════════════════════════
        visa_tab = ttk.Frame(self.root_notebook, padding=10)
        self.root_notebook.add(visa_tab, text=" VISA卡管理 ")
        ttk.Label(visa_tab, text="（VISA卡管理区待开发）", foreground="gray").pack(expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor="w").pack(fill=tk.X, side=tk.BOTTOM)

    # ─────────────────────── 设备刷新 ─────────────────────────

    def refresh_devices(self):
        if self.is_refreshing:
            return
        self.is_refreshing = True
        self.refresh_button.config(state="disabled", text="刷新中...")
        self.status_var.set("正在执行 adb devices …")
        threading.Thread(target=self._do_refresh, daemon=True).start()

    def _do_refresh(self):
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().splitlines()
            # 第一行固定是 "List of devices attached"，跳过
            devices = []
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 1)
                dev_id = parts[0]
                status = parts[1] if len(parts) > 1 else "unknown"
                devices.append({"id": dev_id, "status": status})
            self.devices = devices
            self.log_queue.put(f"[ADB] 共发现 {len(devices)} 台设备")
            self.root.after(0, self._update_tree)
        except FileNotFoundError:
            self.log_queue.put("[错误] 找不到 adb，请确认已安装并加入 PATH")
            self.root.after(0, self._refresh_done)
        except subprocess.TimeoutExpired:
            self.log_queue.put("[错误] adb devices 超时（>10s）")
            self.root.after(0, self._refresh_done)
        except Exception as e:
            self.log_queue.put(f"[错误] {e}")
            self.root.after(0, self._refresh_done)

    def _update_tree(self):
        for iid in self.device_tree.get_children():
            self.device_tree.delete(iid)
        self.device_checked.clear()

        for i, dev in enumerate(self.devices, 1):
            status = dev["status"]
            tag = "online" if status == "device" else "offline"
            iid = self.device_tree.insert(
                "", "end",
                values=("☐", i, dev["id"], status),
                tags=(tag,)
            )
            self.device_checked[iid] = False

        self.device_tree.tag_configure("online",  foreground="black")
        self.device_tree.tag_configure("offline", foreground="gray")
        self.device_count_label.config(text=f"({len(self.devices)} 台)")
        self.status_var.set(f"就绪 — 共 {len(self.devices)} 台设备")
        self._refresh_done()

    def _refresh_done(self):
        self.is_refreshing = False
        self.refresh_button.config(state="normal", text="🔍 刷新设备")

    # ──────────────────── TreeView 交互 ───────────────────────

    def on_treeview_click(self, event):
        region = self.device_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.device_tree.identify_column(event.x)
        if col != "#1":   # 仅"选择"列响应
            return
        iid = self.device_tree.identify_row(event.y)
        if not iid:
            return
        checked = not self.device_checked.get(iid, False)
        self.device_checked[iid] = checked
        vals = list(self.device_tree.item(iid, "values"))
        vals[0] = "☑" if checked else "☐"
        self.device_tree.item(iid, values=vals)

    def toggle_all_selection(self):
        children = self.device_tree.get_children()
        new_state = not all(self.device_checked.get(iid, False) for iid in children)
        for iid in children:
            self.device_checked[iid] = new_state
            vals = list(self.device_tree.item(iid, "values"))
            vals[0] = "☑" if new_state else "☐"
            self.device_tree.item(iid, values=vals)

    def get_selected_devices(self):
        """返回当前勾选的设备列表"""
        return [
            self.devices[i]
            for i, iid in enumerate(self.device_tree.get_children())
            if self.device_checked.get(iid, False)
        ]

    # ─────────────────────────── 日志 ─────────────────────────

    def log(self, msg: str):
        self.log_queue.put(msg)

    def process_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)

    # ──────────────────────── 生命周期 ────────────────────────

    def on_close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AdbTool()
    app.run()
