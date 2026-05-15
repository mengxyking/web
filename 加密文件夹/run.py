from cryptography.fernet import Fernet
import sys
import base64
import hashlib
import io
import json
import platform
import re
import shutil
import threading
import random
import traceback
import uuid
from datetime import datetime, time
import os
import pickle
import subprocess
from pathlib import Path

# 第三方依赖
import uiautomator2 as u2
from PIL import Image, ImageGrab
from lxml import etree
import xml.etree.ElementTree as ET

# PyQt6
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer

# ===================== 你的密钥 =====================
KEY = b"6f0yj5uxf_WLUIBORs3ylmLmZVNR_L7_WzA5SCqzVGs="

# ===================== 全局变量（你要传递的参数） =====================
current_scroll_position = 0
start_time = datetime.now()
file_lock = threading.Lock()
video_lock = threading.Lock()
json_file = "qqqq.json"
json_fileQQ = "qqqqqq.json"
alldata = ""
shuju_file = "shuju_config_qq_reg.pkl"

# ===================== 资源路径兼容 =====================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ===================== 解密 + 带环境运行 =====================
try:
    # 读取加密的代码
    with open(resource_path("code.secret"), "rb") as f:
        enc_data = f.read()

    # 解密
    fernet = Fernet(KEY)
    raw_code = fernet.decrypt(enc_data).decode("utf-8")

    # 构造完整运行环境（关键：把所有导入+全局变量传进去）
    exec_globals = globals().copy()

    # 执行解密后的代码
    exec(raw_code, exec_globals)

except Exception as e:
    print(f"运行出错：{e}")
    traceback.print_exc()
    input("按回车退出")