# 来喜投屏 (复刻版)

Android多设备群控管理系统，复刻来喜投屏核心功能。

## 功能特性

- **屏幕投屏**：实时将Android设备屏幕镜像到电脑（USB/WiFi）
- **多设备群控**：同步控制多台设备（点击/滑动/输入）
- **ADB指令**：批量执行ADB Shell指令
- **文件管理**：批量安装APK、推送/拉取文件
- **快捷话术**：分组管理话术并一键发送
- **定时任务**：支持循环/定时/单次任务
- **WiFi连接**：支持无线ADB连接

## 安装依赖

```bash
pip install -r requirements.txt
```

## 前置要求

1. 安装 [Android SDK Platform-Tools](https://developer.android.com/studio/releases/platform-tools)（包含ADB）
2. 将 `adb` 添加到系统 PATH
3. Android设备开启开发者模式和USB调试

## 启动

```bash
python main.py
```

## 项目结构

```
laixi-touping/
├── main.py                    # 程序入口
├── requirements.txt           # Python依赖
├── quick_replies.json         # 话术配置（自动生成）
└── src/
    ├── core/
    │   ├── adb_manager.py     # ADB设备管理
    │   ├── screen_mirror.py   # 屏幕镜像
    │   └── task_manager.py    # 任务调度
    ├── ui/
    │   ├── main_window.py     # 主窗口
    │   ├── device_card.py     # 设备卡片组件
    │   ├── control_panel.py   # 群控操作面板
    │   └── wifi_connect_dialog.py  # WiFi连接对话框
    └── utils/
        └── quick_reply.py     # 话术管理
```

## 使用说明

1. USB连接Android手机，确保已允许USB调试
2. 启动程序后设备会自动出现在左侧列表
3. 勾选设备卡片进行选中（不选则默认操作所有设备）
4. 点击"开启全部投屏"查看实时屏幕
5. 在右侧面板执行群控操作
