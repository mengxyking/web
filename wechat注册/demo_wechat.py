
import argparse
import sys
import os
import time
import json
import random
import string
import ipaddress

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure we can import framework.base
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
from framework.base import BaseAutomation
from framework import container_manager
import requests
import cv2
import numpy as np
import base64
import io

class DemoTask(BaseAutomation):
    def __init__(self, ip, port, device_id=None, index=1):
        super().__init__(ip, port, device_id, index)
        # 设置容器名称（从环境变量获取或使用默认值）
        try:
            env_conf = os.environ.get('MYT_CONTAINER_CONFIG')
            if env_conf:
                config = json.loads(env_conf)
                self.container_name = config.get('name', f"myt_{index}")
                self.upload_platform = config.get('upload_platform', 0)  # 上传平台设置
                self.country_code = config.get('countryCode', 'US')
                self.timezone = config.get('timezone', 'America/New_York')
            else:
                self.container_name = f"myt_{index}"
                self.upload_platform = 0
                self.country_code = 'US'
                self.timezone = 'America/New_York'
        except:
            self.container_name = f"myt_{index}"
            self.upload_platform = 0
            self.country_code = 'US'
            self.timezone = 'America/New_York'
        self.is_en = self.country_code in ('US', 'GB')  # 英文界面地区
        self.registration_success = False  # 初始化成功标记
        self.last_input_code = None  # 记录上次输入的验证码

    def get_config_name(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            lang = "英文"
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    lang = config.get("script_config", {}).get("name_lang", "英文")
                except:
                    pass  # 读取失败时使用默认值
            
            filename = "chinese_names.txt" if lang == "中文" else "english_names.txt"
            filepath = os.path.join(base_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"名字文件不存在: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            if not names:
                raise ValueError(f"名字文件为空: {filepath}")
            
            if lang == "中文":
                parts = random.choices(names, k=random.randint(2, 3))
                return "".join(parts)
            else:
                parts = random.sample(names, 2) if len(names) >= 2 else random.choices(names, k=2)
                return " ".join(parts)
        except Exception as e:
            print(f">>> [错误] 生成名字失败: {e}", flush=True)
            raise

    def get_password(self, phone):
        """生成密码（支持 前缀 / 自定义 / 随机复杂 三种模式）"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            
            # 默认配置
            pwd_mode = "prefix"
            pwd_prefix = "asdf"
            pwd_custom = ""
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                s_conf = config.get("script_config", {})
                pwd_mode = s_conf.get("pwd_mode", "prefix")
                pwd_prefix = s_conf.get("pwd_prefix", "asdf")
                pwd_custom = s_conf.get("pwd_custom", "") or ""

            # 前缀模式：前缀 + 手机号后六位
            if pwd_mode == "prefix":
                return f"{pwd_prefix}{phone[-6:]}"

            # 自定义模式：直接使用自定义密码（为空时退回前缀模式）
            if pwd_mode == "custom":
                if pwd_custom:
                    return pwd_custom
                else:
                    return f"{pwd_prefix}{phone[-6:]}"

            # 随机复杂模式：生成一个包含大小写字母和数字的 10 位密码
            if pwd_mode == "random":
                chars = string.ascii_letters + string.digits
                return "".join(random.choice(chars) for _ in range(10))

            # 兜底：仍然使用前缀 + 后六位
            return f"{pwd_prefix}{phone[-6:]}"
        except:
            # 出错兜底
            return f"asdf{phone[-6:]}"

    def solve_captcha_node(self, node):
        """处理验证码：严格流程（检查文字 -> 等待图片加载 -> 识别 -> 点击）"""
        try:
            if not self.rpc: return False
            
            # 1. 获取验证码区域
            b = node.getNodeNound()
            l, t = b['left'], b['top']
            w, h = b['right'] - l, b['bottom'] - t
            crop_t, crop_b = max(0, t), b['bottom']
            crop_l, crop_r = max(0, l), b['right']

            # 2. 提取提示语 (只要有一次提取成功即可)
            # 我们允许在等待图片加载的过程中多次尝试提取
            prompt_text = ""
            
            def get_text_recursive(n_handle, depth=0):
                if depth > 3: return ""
                try:
                    txt = n_handle.getNodeText()
                    if txt and txt.strip(): return txt
                    children = n_handle.getChild() 
                    for child in children:
                        res = get_text_recursive(child, depth+1)
                        if res: return res
                except: pass
                return ""

            # 3. 循环等待图片加载
            max_retries = 5
            valid_image_found = False
            best_crop = None
            best_grid_rect = None # [x1, y1, x2, y2] relative to crop
            best_tc_rect = None   # tcOperation full rect (char模式用)
            best_iwrap_rect = None
            best_itext_rect = None
            
            for i in range(max_retries):
                # 3.1 截图
                img_bytes = self.rpc.takeCaptrueCompress(1, 80)
                if not img_bytes: continue
                img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
                full_crop = img[crop_t:crop_b, crop_l:crop_r]
                
                # 3.2 提取文字
                try:
                    s = self.selector()
                    s.addQuery_IdEqual("instructionWrap")
                    wrap_nodes = s.execQuery(1, 100)
                    if wrap_nodes:
                        # 坐标：字符模式必需
                        try:
                            wb = wrap_nodes[0].getNodeNound()
                            best_iwrap_rect = [
                                max(0, wb['left'] - crop_l),
                                max(0, wb['top'] - crop_t),
                                min(full_crop.shape[1], wb['right'] - crop_l),
                                min(full_crop.shape[0], wb['bottom'] - crop_t),
                            ]
                        except:
                            pass
                        # 文本：只在尚未拿到时提取一次
                        if not prompt_text:
                            for n in wrap_nodes:
                                prompt_text = get_text_recursive(n)
                                print(f">>> [DEBUG] 原始文本: '{prompt_text}'", flush=True)
                                if prompt_text:
                                    # 强制去掉已知前缀（字符模式），只保留右侧的点击序列
                                    prefixes = ["Click in this order:", "Click in this order：", "按顺序点击：", "按顺序点击:"]
                                    for p in prefixes:
                                        if prompt_text.startswith(p):
                                            prompt_text = prompt_text[len(p):].strip()
                                            print(f">>> [DEBUG] 去除前缀后: '{prompt_text}'", flush=True)
                                            break
                                    # 如果没有匹配任何前缀，也保留原文本
                                    if prompt_text == get_text_recursive(n):
                                        print(f">>> [DEBUG] 无前缀匹配，保留原文本", flush=True)
                                    break
                except:
                    pass
                
                # instructionText (仅字符模式需要，用来扣掉 “Click in this order:” 区域)
                try:
                    s_it = self.selector()
                    s_it.addQuery_IdEqual("instructionText")
                    it_nodes = s_it.execQuery(1, 50)
                    if it_nodes:
                        tb = it_nodes[0].getNodeNound()
                        best_itext_rect = [
                            max(0, tb['left'] - crop_l),
                            max(0, tb['top'] - crop_t),
                            min(full_crop.shape[1], tb['right'] - crop_l),
                            min(full_crop.shape[0], tb['bottom'] - crop_t),
                        ]
                except:
                    pass
                
                # 3.3 检查图片有效性 (极致精准区域计算: tcOperation - instruction)
                grid_roi = None
                current_grid_rect = None
                
                # 获取 instruction 节点 (改为用户指定的 instruction ID)
                ib = None
                if not prompt_text: 
                     s_instr = self.selector()
                     s_instr.addQuery_IdEqual("instruction") # Changed from instructionWrap
                     nodes = s_instr.execQuery(1, 100)
                     if nodes: 
                         ib = nodes[0].getNodeNound()
                         for n in nodes: 
                             txt = get_text_recursive(n)
                             print(f">>> [DEBUG] 原始文本2: '{txt}'", flush=True)
                             if txt: 
                                 # 强制去掉已知前缀（字符模式），只保留右侧的点击序列
                                 prefixes = ["Click in this order:", "Click in this order：", "按顺序点击：", "按顺序点击:"]
                                 for p in prefixes:
                                     if txt.startswith(p):
                                         txt = txt[len(p):].strip()
                                         print(f">>> [DEBUG] 去除前缀后2: '{txt}'", flush=True)
                                         break
                                 prompt_text = txt
                                 break
                else:
                     s_instr = self.selector()
                     s_instr.addQuery_IdEqual("instruction") # Changed from instructionWrap
                     nodes = s_instr.execQuery(1, 100)
                     if nodes: ib = nodes[0].getNodeNound()

                # 获取 tcOperation 节点 (主体容器)
                s_grid = self.selector()
                s_grid.addQuery_IdEqual("tcOperation")
                grid_nodes = s_grid.execQuery(1, 100)
                
                if grid_nodes:
                    for gn in grid_nodes:
                         gb = gn.getNodeNound()
                         if gb['left'] >= l and gb['top'] >= t:
                             
                             # DEBUG: 打印节点坐标
                             print(f">>> [DEBUG] tcOperation={gb}, instruction={ib}", flush=True)

                             # --- 核心计算逻辑 (严格修正) ---
                             # Grid 区域 = tcOperation 的下半部分
                             # 切割线 = instruction 的底边 (Top = instruction.bottom)
                             
                             # 左边界
                             g_x1 = max(0, gb['left'] - crop_l)
                             
                             if ib:
                                 g_y1 = max(0, ib['bottom'] - crop_t)
                             else:
                                 g_y1 = 45 
                             
                             # 右边界
                             g_x2 = min(full_crop.shape[1], gb['right'] - crop_l)
                             
                             # 下边界
                             g_y2 = min(full_crop.shape[0], gb['bottom'] - crop_t)
                             
                             if g_x2 > g_x1 and g_y2 > g_y1:
                                 grid_roi = full_crop[g_y1:g_y2, g_x1:g_x2]
                                 current_grid_rect = [g_x1, g_y1, g_x2, g_y2]
                                 # char模式：tcOperation 完整区域
                                 try:
                                     tc_x1 = max(0, gb['left'] - crop_l)
                                     tc_y1 = max(0, gb['top'] - crop_t)
                                     tc_x2 = min(full_crop.shape[1], gb['right'] - crop_l)
                                     tc_y2 = min(full_crop.shape[0], gb['bottom'] - crop_t)
                                     if tc_x2 > tc_x1 and tc_y2 > tc_y1:
                                         best_tc_rect = [tc_x1, tc_y1, tc_x2, tc_y2]
                                 except:
                                     pass
                             break
                
                if grid_roi is None or grid_roi.size == 0:
                     print(f">>> [验证码] 节点定位中... {i+1}/{max_retries}", flush=True)
                     self.sleep(1.5)
                     continue

                # 计算标准差
                mean, std = cv2.meanStdDev(grid_roi)
                validness = np.mean(std)
                
                print(f">>> [验证码] 等待加载 {i+1}/{max_retries}: Text='{prompt_text}' ImgScore={validness:.1f}", flush=True)
                
                if validness > 15:
                    valid_image_found = True
                    best_crop = full_crop
                    best_grid_rect = current_grid_rect
                    break
                
                self.sleep(1.5)

            if not valid_image_found or best_crop is None:
                print("[!] 验证码图片加载超时或为空白", flush=True)
                return False

            if not prompt_text:
                print("[!] 未从文本提取到提示语（可能为图片字母如 A,F,R），将依赖打码服务从图中识别", flush=True)

            # 4. 请求打码 (使用客户端精准坐标)
            # 构造 layout
            layout = {
                "name": "Android-Node",
                "prompt_rect": [0, 0, best_crop.shape[1], 100], # 这里不是很重要，因为我们直接传 text
                "grid_rect": best_grid_rect, # 关键：使用 tcOperation 的精准区域
            }

            # 非字符模式才传六宫格参数
            if self.get_char_mode() != 1:
                layout["rows"] = 2
                layout["cols"] = 3
            
            print(f">>> [验证码] 请求打码: Grid={best_grid_rect} Text='{prompt_text}'", flush=True)
            print(f">>> [DEBUG] char_mode={self.get_char_mode()}", flush=True)

            payload = {
                "image": base64.b64encode(cv2.imencode('.png', best_crop)[1]).decode(),
                "layout": layout, 
                "prompt_text": prompt_text
            }

            # 复选框勾选：传 mode='char'
            try:
                if self.get_char_mode() == 1:
                    payload["mode"] = "char"
                    # 字符模式：需要传 instructionWrap / instructionText / tcOperation(full) 的精准区域
                    if best_tc_rect:
                        payload["layout"]["grid_rect"] = best_tc_rect
                    if best_iwrap_rect:
                        payload["layout"]["instruction_rect"] = best_iwrap_rect
                    if best_itext_rect:
                        payload["layout"]["instruction_text_rect"] = best_itext_rect
            except:
                pass
            
            try:
                ret = requests.post("http://127.0.0.1:9000/", json=payload, timeout=10).json()
            except Exception as e:
                print(f"[!] 服务器连接失败: {e}")
                return False

            # 5. 处理结果
            clicks = ret.get('result', {}).get('coordinates', [])
            if not ret.get("success") or not clicks:
                print(f"[!] 识别无结果 (Prompt: {prompt_text}) -> 尝试刷新?", flush=True)
                # 可选：点击刷新按钮 (id: reload_btn 或者是某个图标)
                # 暂时返回 False 让外层重试
                return False 
                
            print(f">>> [验证码] 点击 {len(clicks)} 处", flush=True)
            for p in clicks:
                self.tap(crop_l + p['x'], crop_t + p['y'])
                self.sleep(0.4)
            
            self.sleep(0.5)
            # 点击确定
            # 尝试通过ID点击，如果不行则尝试坐标
            s_btn = self.selector()
            s_btn.addQuery_IdEqual("verifyBtn")
            btns = s_btn.execQuery(1, 5)
            if btns:
                btns[0].Click_events()
            else:
                self.click_id("verifyBtn")
                
            return True
            
        except Exception as e:
            print(f"[!] 验证码流程异常: {e}")
        return False

    def run(self, skip_install=False):
        print(">>> 注册脚本启动 ", flush=True)
        self.phone = None
        self.form_filled = False # Flag to prevent re-input
        self.form_next_clicked = False # Flag to prevent re-clicking next button
        self.form_next_click_count = 0 # Counter to limit re-clicking attempts
        self.country_selected = False # Flag to prevent re-selecting country
        self.jump_count = 0
        self.max_jumps = self.get_max_jumps()
        self.channel3_mode = self.get_channel3_mode()
        self.channel1_mode = self.get_channel1_mode()
        self.last_progress_time = time.time()  # 全局无进展兜底计时器
        
        # 如果不跳过安装，则安装微信
        if not skip_install:
            # 初始化: 安装APK并启动
            apk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wx.apk")
            print(f">>> [DEBUG] Check APK: {apk_path}, Exists: {os.path.exists(apk_path)}", flush=True)
            if os.path.exists(apk_path):
                print(">>> [系统] 等待系统稳定 (15s)...", flush=True)
                self.sleep(15)
                
                install_count = 0
                while True:
                    install_count += 1
                    print(f">>> [初始化] 安装微信 (第{install_count}次): {apk_path}...", flush=True)
                    if self.install_app(apk_path):
                        print(f">>> [初始化] 安装成功！", flush=True)
                        self.sleep(2)
                        break
                    else:
                        print(f">>> [初始化] 安装失败，等待 10s 后重试...", flush=True)
                        self.sleep(10)
        else:
            # 跳过安装，执行深度清理微信
            print(">>> [系统] 跳过安装微信，执行深度清理...", flush=True)
            try:
                self.rpc.exec_cmd("pm clear com.tencent.mm")
                print(">>> [系统] 深度清理微信完成", flush=True)
                self.sleep(2)
            except Exception as e:
                print(f">>> [系统] 深度清理微信失败: {e}", flush=True)
        
        # 初始化环境（设置IP：自动判断使用爱快还是SK5）
        self.setup_proxy()
        self.setup_ikuai_pptp()
        
        while True:
            print(">>> [初始化] 启动微信...", flush=True)
            self.run_app("com.tencent.mm")
            self.sleep(8)
            
            # 检测是否启动成功 (检查前台 Activity)
            out, _ = self.rpc.exec_cmd("dumpsys window | grep mCurrentFocus")
            if not out: # 备用检测
                out, _ = self.rpc.exec_cmd("dumpsys activity activities | grep mResumedActivity")
                
            if out and "com.tencent.mm" in out:
                print(">>> [状态] 微信启动成功！", flush=True)
                break
            else:
                print(">>> [状态] 启动失败或未在前台，尝试备用启动方式...", flush=True)
                # 备用：使用 rpc.openApp 尝试启动
                if hasattr(self.rpc, 'openApp'):
                    print(">>> [初始化] 使用 rpc.openApp 备用启动...", flush=True)
                    self.rpc.openApp("com.tencent.mm")
                    self.sleep(8)
                    out, _ = self.rpc.exec_cmd("dumpsys window | grep mCurrentFocus")
                    if not out:
                        out, _ = self.rpc.exec_cmd("dumpsys activity activities | grep mResumedActivity")
                    if out and "com.tencent.mm" in out:
                        print(">>> [状态] 微信启动成功！(备用方式)", flush=True)
                        break
                print(">>> [状态] 启动失败，等待10s后重试...", flush=True)
                self.sleep(10)

        if self.is_en:
            self._run_en()
            return

        while True:
            # 1. 验证码 (最高优先级)
            if self.get_accessibility_mode() == 1:
                # 无障碍模式：点击 # 無障礙方式
                if self.click_id("accessibilityText"):
                    print(">>> [验证码] 无障碍模式：点击# 無障礙方式", flush=True)
                    self.sleep(1)
                    self.last_progress_time = time.time()
                    continue
            else:
                # 正常模式：使用打码服务
                if self._process_captcha():
                    self.last_progress_time = time.time()
                    continue

            # 0. 成功检测
            if self._process_success():
                return

            # 1. 国家 + 表单 一体化处理
            form_result = self._process_country_and_form()
            if form_result == 'STOP':
                if self.phone:
                    self.ban_phone(self.phone, reason="表单处理异常")
                return
            if form_result:
                self.last_progress_time = time.time()
                continue

            # 1.5 VISA卡表单处理 (卡號、持卡人姓名、安全碼、有效期限)
            if self._process_visa_card_form():
                self.last_progress_time = time.time()
                continue

            # 2. 验证码填写
            if self.get_accessibility_mode() == 1:
                # 无障碍模式：点击 # 無障礙方式
                if self.click_id("accessibilityText"):
                    print(">>> [验证码] 无障碍模式：点击# 無障礙方式", flush=True)
                    self.sleep(1)
                    self.last_progress_time = time.time()
                    continue
            else:
                # 正常模式：使用打码服务
                if self._process_verify_code():
                    self.last_progress_time = time.time()
                    continue

            # 3. 异常处理 (QRCode / 网络错误 / 弹窗)
            # 返回 True 表示已处理并需要 continue，返回 'STOP' 表示退出
            exc_result = self._process_exceptions()
            if exc_result == 'STOP': return
            if exc_result:
                self.last_progress_time = time.time()
                continue

            # 4. 常规按钮点击
            if self._process_buttons():
                self.last_progress_time = time.time()
                continue

            # 5. 全局兜底机制：检测不到任何状态超过5分钟 → 点击返回 + 换IP + 等10秒后继续
            elapsed = time.time() - self.last_progress_time
            if elapsed > 300:
                print(f">>> [兜底] 检测到 5 分钟无任何状态变化，尝试恢复...", flush=True)
                self.press_back()
                self.sleep(2)
                switch_ok, switch_msg = self._switch_ip()
                if switch_ok:
                    print(f">>> [兜底] IP切换成功: {switch_msg}，等待10秒后继续执行...", flush=True)
                    self.sleep(10)
                    self.last_progress_time = time.time()
                else:
                    print(f">>> [兜底] IP切换失败: {switch_msg}，标记手机号并退出本轮", flush=True)
                    if self.phone:
                        self.ban_phone(self.phone, reason="全局兜底-IP切换失败")
                continue

            self.sleep(1)
            print(".", end="", flush=True)

    def _process_captcha(self):
        """处理滑块/点选验证码（优化：主动等待验证结果）"""
        s = self.selector()
        s.addQuery_IdEqual("tcaptcha_iframe_dy")
        nodes = s.execQuery(1, 200)
        if nodes:
            if self.solve_captcha_node(nodes[0]):
                # 主动等待验证结果 (最多15秒)
                for i in range(15):
                    self.sleep(1)
                    s_check = self.selector()
                    s_check.addQuery_IdEqual("tcaptcha_iframe_dy")
                    if not s_check.execQuery(1, 50):  # 弹窗消失
                        print(">>> [验证码] 验证成功，弹窗已消失", flush=True)
                        return True
                    # 检查是否出现错误
                    s_err = self.selector()
                    s_err.addQuery_TextEqual("Close")
                    if s_err.execQuery(1, 50):
                        print(">>> [验证码] 验证超时/失败", flush=True)
                        break
            else:
                print(">>> [验证码] 处理失败，等待重试...", flush=True)
                self.sleep(2)
            return True
        return False

    def _process_verify_code(self):
        """处理验证码填写 (含轮询和重发机制) - 繁体中文界面版"""
        # 检查是否是接码页面：通过检测 t2o 节点
        s_sms = self.selector()
        s_sms.addQuery_IdEqual("com.tencent.mm:id/t2o")
        sms_nodes = s_sms.execQuery(1, 100)

        if not sms_nodes:
            # 不存在 t2o，说明不是接码页面，跳过
            return False

        s = self.selector()
        s.addQuery_IdEqual("com.tencent.mm:id/d98")
        nodes = s.execQuery(10, 100)

        # 只要检测到验证码节点(d98)存在，就进入接码流程
        if nodes and len(nodes) >= 1:
             print(f">>> [接码] 检测到验证码页面 (找到 {len(nodes)} 个节点)，开始接码...", flush=True)
             
             # 4 轮尝试 (1次初始 + 3次重发)
             for round in range(4):
                 if round > 0:
                     print(f">>> [SMS] 第 {round} 次点击重发...", flush=True)
                     if self.click_id("com.tencent.mm:id/mm7"):
                         self.sleep(5)
                     else:
                         print(">>> [SMS] 找不到重发按钮，可能还在倒计时", flush=True)
                 
                 for i in range(8):
                     code = self.get_sms_code()
                     if code:
                         # 重新获取节点，防止点击重发后节点失效或焦点丢失
                         print(f">>> [状态] 获取焦点并填写验证码: {code}", flush=True)

                         # 繁体中文界面：使用 index=1 点击输入框（第二个节点）
                         if self.click_by_id("com.tencent.mm:id/d98", index=1):
                             self.sleep(0.5)
                             self.mytapi.ClearText(20)
                             self.sleep(0.3)
                             self.input_text(code)
                             self.sleep(0.5)
                         else:
                             print(">>> [SMS] 点击输入框失败，尝试其他方式...", flush=True)
                             # 备选方案：使用节点列表的第二个节点
                             s_fresh = self.selector()
                             s_fresh.addQuery_IdEqual("com.tencent.mm:id/d98")
                             new_nodes = s_fresh.execQuery(10, 200)
                             if new_nodes and len(new_nodes) >= 2:
                                 self.click_node(new_nodes[1])
                                 self.sleep(0.3)
                                 self.mytapi.ClearText(20)
                                 self.sleep(0.3)
                                 self.input_field(new_nodes[1], code)
                             elif new_nodes and len(new_nodes) >= 1:
                                 self.click_node(new_nodes[0])
                                 self.sleep(0.3)
                                 self.mytapi.ClearText(20)
                                 self.sleep(0.3)
                                 self.input_field(new_nodes[0], code)

                         # 提交按钮
                         self.click_id("com.tencent.mm:id/sso")

                         # 确认按钮
                         self.click_id("com.tencent.mm:id/lrn")
                         self.sleep(3)

                         # 检测是否出现验证码错误提示 (ocm)
                         s_error = self.selector()
                         s_error.addQuery_IdEqual("com.tencent.mm:id/ocm")
                         if s_error.execQuery(1, 200):
                             print(">>> [SMS] 检测到验证码错误，点击确定后重试...", flush=True)

                             # 点击确定关闭错误弹窗
                             self.click_id("com.tencent.mm:id/mm_alert_ok_btn")
                             self.sleep(1)

                             # 点击重发按钮获取新验证码
                             if self.click_id("com.tencent.mm:id/mm7"):
                                 print(">>> [SMS] 已点击重发，等待新验证码...", flush=True)
                                 self.last_input_code = None  # 清空上次输入的验证码
                                 self.sleep(5)

                                 # 获取新验证码
                                 new_code = self.get_sms_code()
                                 if new_code:
                                     print(f">>> [SMS] 获取到新验证码: {new_code}", flush=True)

                                     # 点击输入框
                                     if self.click_by_id("com.tencent.mm:id/d98", index=1):
                                         self.sleep(0.5)
                                         # 清空输入框（使用SDK的ClearText方法）
                                         self.mytapi.ClearText(20)
                                         self.sleep(0.3)
                                         # 输入新验证码
                                         self.input_text(new_code)
                                         self.last_input_code = new_code  # 记录本次输入的验证码
                                         self.sleep(0.5)
                                         # 再次提交
                                         self.click_id("com.tencent.mm:id/sso")
                                         self.click_id("com.tencent.mm:id/lrn")
                                         self.sleep(5)
                                         return True
                                 else:
                                     print(">>> [SMS] 重发后未获取到新验证码", flush=True)
                             else:
                                 print(">>> [SMS] 找不到重发按钮", flush=True)
                         else:
                             # 没有错误，正常返回
                             return True

                         self.sleep(2)
                     
                     if i < 7: 
                         print(f">>> [SMS] 本轮第 {i+1}/8 次查询未果，等待 15s...", flush=True)
                         self.sleep(15)
             
             print(">>> [接码] 多次重试均失败，放弃。", flush=True)
             # 失败后，建议标记此号有问题，避免死循环
             # if self.phone: self.ban_phone(self.phone)
             return False
        return False

    def _process_country_and_form(self):
        """国家选择 + 注册表单一体化处理"""
        # 1. 先尝试处理国家选择（如果当前在国家选择页面）
        if not self._process_country_selection():
            # 2. 再尝试处理注册表单（如果当前在注册表单页面）
            return self._process_form()
        return False

    def _process_visa_card_form(self):
        """处理VISA卡表单（卡號、持卡人姓名、安全碼、有效期限）- 图像模板版"""
        # 检测是否在VISA卡表单页面 - 通过检测"wx/卡号.png"图像
        # 注意：这里只检测不点击，检测到后直接调用fill_visa_card_form去处理
        s = self.selector()
        # 先尝试用图像识别检测VISA卡表单页面是否存在
        if self.click_image("wx/卡号.png", threshold=0.7):
            print(">>> [VISA] 检测到VISA卡表单页面，开始填写...", flush=True)
            # 记录开始时间
            self.visa_form_filled_time = time.time()
            # 调用已存在的fill_visa_card_form方法
            return self.fill_visa_card_form()
        return False

    def _process_country_selection(self):
        """处理国家选择步骤"""
        try:
            # 如果已经选择过国家，直接返回
            if getattr(self, 'country_selected', False):
                return False
            
            # 先检查配置中是否有国家名称，如果没有则直接返回
            country_name = self.get_country_name()
            if not country_name:
                # 如果没有配置国家名称，直接返回（不设置标志，允许下次循环重新检查）
                return False
            
            # 检查是否存在国家选择按钮 (United States +1)
            s_country = self.selector()
            s_country.addQuery_IdEqual("com.tencent.mm:id/ck1")
            country_nodes = s_country.execQuery(5, 100)
            
            if country_nodes:
                print(f">>> [国家选择] 配置的国家名称: {country_name}", flush=True)
                print(">>> [国家选择] 检测到国家选择页面，开始选择国家...", flush=True)
                
                # 1. 点击 United States（+1）
                if self.click_id("com.tencent.mm:id/ck1"):
                    self.sleep(2)
                    print(">>> [国家选择] 已点击国家选择按钮", flush=True)
                else:
                    print(">>> [国家选择] 未找到国家选择按钮", flush=True)
                    return False
                
                # 2. 点击搜索框 (ID: jgr)
                if self.click_id("com.tencent.mm:id/jgr"):
                    self.sleep(2)
                    print(">>> [国家选择] 已点击搜索框", flush=True)
                else:
                    print(">>> [国家选择] 未找到搜索框", flush=True)
                    return False
                
                # 3. 输入国家名称到搜索框 (ID: d98)
                s_search = self.selector()
                s_search.addQuery_IdEqual("com.tencent.mm:id/d98")
                search_nodes = s_search.execQuery(5, 100)
                if search_nodes:
                    self.input_field(search_nodes[0], country_name)
                    self.sleep(2)
                    print(f">>> [国家选择] 已输入国家名称: {country_name}", flush=True)
                else:
                    print(">>> [国家选择] 未找到搜索输入框", flush=True)
                    return False
                
                # 4. 点击搜索结果 (ID: cg1)
                if self.click_id("com.tencent.mm:id/cg1"):
                    self.sleep(2)
                    print(">>> [国家选择] 已点击搜索结果", flush=True)
                else:
                    print(">>> [国家选择] 未找到搜索结果按钮", flush=True)
                    return False
                # 标记已选择国家
                self.country_selected = True
                return True
            return False
        except Exception as e:
            print(f">>> [国家选择] 处理异常: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False

    def get_country_name(self):
        """从配置文件获取国家名称"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                country = config.get("script_config", {}).get("country", "").strip()
                return country if country else None
        except:
            pass
        return None

    def get_char_mode(self):
        """从配置文件读取字符模式开关（用于验证码识别 mode='char'）"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return int(config.get("script_config", {}).get("char_mode", 0))
        except:
            pass
        return 0

    def get_accessibility_mode(self):
        """读取无障碍模式设置（不使用打码服务，点击# 無障礙方式）"""
        # 优先从环境变量读取（运行时配置）
        try:
            env_conf = os.environ.get('MYT_CONTAINER_CONFIG')
            if env_conf:
                config = json.loads(env_conf)
                return config.get('accessibility_mode', 0)
        except:
            pass
        # 其次从配置文件读取
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return int(config.get("script_config", {}).get("accessibility_mode", 0))
        except:
            pass
        return 0

    def fill_visa_card_form(self):
        """填写VISA卡表单（卡號、持卡人姓名、安全碼、有效期限）- 图像模板版"""
        print(">>> [VISA] 开始填写卡表单...", flush=True)

        # 获取VISA卡信息（不传容器参数，API不支持container参数）
        card_number, expiry_date, cvv = self.get_visa()
        if not card_number:
            print(">>> [VISA] 获取VISA失败", flush=True)
            return False

        # 保存当前卡号，用于后续标记失败
        self.current_card_number = card_number
        print(f">>> [VISA] 卡号: {card_number}, 日期: {expiry_date}, CVV: {cvv}", flush=True)

        # 随机延迟函数
        def rand_delay():
            return random.uniform(0.2, 0.5)

        # 1. 卡號 - 点击输入框后直接输入（降低阈值到0.7提高识别率）
        if self.click_image("wx/卡号.png", threshold=0.7):
            self.sleep(rand_delay())
            self.input_text(card_number)
            self.sleep(rand_delay())
        else:
            print(">>> [VISA] 卡號识别失败", flush=True)
            return False

        # 2. 持卡人姓名 - 图像识别后输入英文名（降低阈值）
        if self.click_image("wx/持卡人姓名.png", threshold=0.7):
            self.sleep(rand_delay())
            self.click_image("wx/持卡人姓名.png", threshold=0.7)  # 额外点击一次确保焦点
            self.sleep(rand_delay())
            name = self.get_config_name()
            self.input_text(name)
            self.sleep(rand_delay())
        else:
            print(">>> [VISA] 持卡人姓名识别失败", flush=True)
            return False

        # 3. 安全碼 - 图像识别后输入CVV（降低阈值）
        if self.click_image("wx/安全碼.png", threshold=0.7):
            self.sleep(rand_delay())
            self.click_image("wx/安全碼.png", threshold=0.7)  # 额外点击一次确保焦点
            self.sleep(rand_delay())
            self.input_text(cvv)
            self.sleep(rand_delay())
        else:
            print(">>> [VISA] 安全碼识别失败", flush=True)
            return False

        # 4. 有效期限 - 先向上滑动屏幕露出有效期限输入框，再识别输入
        print(">>> [VISA] 向上滑动屏幕露出有效期限输入框...", flush=True)
        self.swipe(360, 600, 360, 300, 300)  # 向上滑
        self.sleep(rand_delay())
        # 再滑动一次，确保有效期限输入框完全露出
        self.swipe(360, 600, 360, 300, 300)  # 向上滑
        self.sleep(rand_delay())
        # 再滑动一次，确保有效期限输入框完全露出

        if self.click_image("wx/有效期限.png", threshold=0.7):
            self.sleep(rand_delay())
            self.click_image("wx/有效期限.png", threshold=0.7)  # 额外点击一次确保焦点
            self.sleep(rand_delay())
            date_digits = expiry_date.replace("/", "").replace("-", "")
            self.input_text(date_digits)
            self.sleep(rand_delay())
        else:
            print(">>> [VISA] 有效期限识别失败", flush=True)
            return False

        # 5. 填写完成后，点击下一步按钮
        self.sleep(0.5)
        if self.click_image("wx/下一步.png", threshold=0.7):
            print(">>> [VISA] 已点击下一步按钮", flush=True)
            self.sleep(2)
        else:
            print(">>> [VISA] 未找到下一步按钮，等待后续处理", flush=True)

        print(">>> [VISA] 卡表单填写完成", flush=True)
        return True

    def _process_form(self):
        """处理注册表单"""
        print(">>> [DEBUG] _process_form: 开始执行", flush=True)

        s = self.selector()
        s.addQuery_IdEqual("com.tencent.mm:id/d98")
        nodes = s.execQuery(10, 200)
        print(f">>> [DEBUG] _process_form: 找到 {len(nodes) if nodes else 0} 个节点", flush=True)

        # 区分接码页面和表单页面：检查是否存在接码相关的特定元素
        # 接码页面通常有 t2o 节点（获取验证码按钮）
        s_sms = self.selector()
        s_sms.addQuery_IdEqual("com.tencent.mm:id/t2o")
        sms_nodes = s_sms.execQuery(1, 100)

        if sms_nodes:
            # 存在 t2o 节点，说明是接码页面，直接进入接码流程
            print(">>> [DEBUG] 检测到接码页面（存在 t2o 节点），开始接码流程...", flush=True)
            return self._process_verify_code()

        if nodes and len(nodes) >= 2:
            # Only fill if not filled yet
            print(f">>> [DEBUG] _process_form: form_filled={self.form_filled}, phone={self.phone}", flush=True)
            if not self.form_filled:
                # 先尝试获取手机号，没有号就什么都不填，避免反复改名字
                if not self.phone:
                    self.phone = self.get_phone()
                
                if not self.phone:
                    print(">>> [状态] 当前没有可用手机号，等待号码中...", flush=True)
                    self.sleep(5)
                    return False

                print(">>> [状态] 填写表单...", flush=True)
                nodes.sort(key=lambda n: n.getNodeNound()['top'])
                
                # 只有在拿到手机号后，才真正开始填写所有字段
                print(">>> [DEBUG] 准备调用 get_config_name()...", flush=True)
                name = self.get_config_name()
                print(f">>> [DEBUG] get_config_name() 返回: {name}", flush=True)
                self.input_field(nodes[0], name)
                self.input_field(nodes[1], self.phone)
                self.password = self.get_password(self.phone)
                self.input_field(nodes[2], self.password)
                
                self.click_id("com.tencent.mm:id/sph", random_offset=False) # Checkbox
                self.form_filled = True
                # 填写完成后，点击下一步
                print(">>> [表单] 信息已填写，尝试点击下一步...", flush=True)
                if self.click_id("com.tencent.mm:id/lrn"):
                    self.form_next_clicked = True
                    self.form_next_click_count = 1
                    self.sleep(5)
                    return True
                else:
                    print(">>> [表单] 下一步按钮点击失败", flush=True)
                    return False
            else:
                # 如果表单已填写，检查是否已经点击过下一步
                if self.form_next_clicked:
                    # 已经点击过下一步，检查是否还在表单页面
                    # 如果还在表单页面，可能是界面没有响应，等待一段时间后再次检查
                    print(f">>> [表单] 表单已填写且已点击下一步（点击次数: {self.form_next_click_count}），检查是否已离开表单页面...", flush=True)
                    self.sleep(2)
                    # 再次检查表单节点，如果节点数量减少或不存在，说明已离开表单页面
                    s_check = self.selector()
                    s_check.addQuery_IdEqual("com.tencent.mm:id/d98")
                    check_nodes = s_check.execQuery(5, 100)
                    if not check_nodes or len(check_nodes) < 3:
                        print(">>> [表单] 已离开表单页面，不再重复处理", flush=True)
                        return False
                    else:
                        # 仍在表单页面，可能是点击失败，但限制重复点击次数（最多3次）
                        if self.form_next_click_count >= 3:
                            print(">>> [表单] 已达到最大重复点击次数，尝试切换IP...", flush=True)
                            # 调用 switch_ip 切换IP
                            switch_success, switch_msg = self._switch_ip()
                            if switch_success:
                                print(f">>> [表单] IP切换成功: {switch_msg}，等待网络稳定...", flush=True)
                                # 重置点击状态，下次循环直接尝试点击下一步（不重新填写）
                                self.form_next_clicked = False
                                self.form_next_click_count = 0
                                # IP 切换后需要等待路由生效，期间不重复操作
                                self.sleep(15)
                                print(">>> [表单] 网络已稳定，下次循环将直接点击下一步", flush=True)
                                return False
                            else:
                                print(f">>> [表单] IP切换失败: {switch_msg}，标记手机号并停止本轮", flush=True)
                                if self.phone:
                                    self.ban_phone(self.phone, reason="表单点击失败-IP切换失败")
                                return 'STOP'
                        print(f">>> [表单] 仍在表单页面，可能是点击失败，尝试再次点击（第 {self.form_next_click_count + 1} 次）...", flush=True)
                        if self.click_id("com.tencent.mm:id/lrn"):
                            self.form_next_click_count += 1
                            self.sleep(5)
                            return True
                        else:
                            print(">>> [表单] 再次点击失败，跳过本次处理", flush=True)
                            return False
                else:
                    # 表单已填写但未点击下一步，可能是暂停/恢复导致的状态不一致
                    print(">>> [表单] 信息已填写，尝试点击下一步...", flush=True)
                    if self.click_id("com.tencent.mm:id/lrn"):
                        self.form_next_clicked = True
                        self.form_next_click_count = 1
                        self.sleep(5)
                        return True
                    else:
                        print(">>> [表单] 下一步按钮点击失败", flush=True)
                        return False
        return False

    def _process_exceptions(self):
        """处理异常状态"""
        # 优先检测并点击返回按钮（初始页面时，优先返回到正确页面）
        if self.click_id("com.tencent.mm:id/mjy", timeout=200) or self.click_id("com.tencent.mm:id/obc", timeout=200):
            self.sleep(2)
            return True

        # QRCode 检测
        s_qr = self.selector()
        s_qr.addQuery_TextEqual("qrcode")
        if s_qr.execQuery(1, 100):
            self.jump_count += 1
            
            if self.jump_count >= self.max_jumps:
                print(f">>> [跳码] 达到跳码次数{self.max_jumps} 已停止！", flush=True)
                if self.phone: self.ban_phone(self.phone)
                return 'STOP'
                
            print(f">>> [辅助] QRCode {self.jump_count}/{self.max_jumps}", flush=True)
            self.press_back(); self.sleep(2)
            self.click_id("com.tencent.mm:id/lrn"); self.sleep(5)
            return True

        # ID: 不是我的，继续注册新账户
        # 检测到该按钮后点击一次
        if self.click_id("android:id/title", timeout=200):
            print(">>> [处理] 点击: 不是我的，继续注册新账户", flush=True)
            self.sleep(2)
            return True

        # ID: 二次注册
        # 识别到该按钮后点击一次
        if self.click_id("com.tencent.mm:id/m43", timeout=200):
            print(">>> [处理] 点击: 二次注册", flush=True)
            self.sleep(2)
            return True

        # ID: 语音码
        # 识别到语音验证码界面后，标记当前手机号为失败并结束本轮流程
        if self.click_id("com.tencent.mm:id/owo", timeout=200):
            print(">>> [异常] 检测到语音码界面，标记手机号注册失败，开始下一轮流程", flush=True)
            if self.phone:
                self.ban_phone(self.phone)
            return 'STOP'
                # ID: aerr_wait 应用无响应等待按钮
        if self.click_id("android:id/aerr_wait", timeout=200):
            print(">>> [异常] 检测到应用无响应，点击等待按钮", flush=True)
            self.sleep(3)
            return True


        # 检测加载不完整.png，点击一次返回
        if self.click_image("wx/加载不完整.png", threshold=0.7):
            print(">>> [异常] 检测到加载不完整，点击返回", flush=True)
            self.press_back(); self.sleep(2)
            return True

        # ID: jlh 错误状态，标记为失败并结束本轮流程
        if self.click_id("com.tencent.mm:id/jlh", timeout=200):
            print(">>> [异常] 检测到 jlh 错误状态，标记手机号注册失败，开始下一轮流程", flush=True)
            # 标记VISA卡为环境异常
            if hasattr(self, 'current_card_number') and self.current_card_number:
                self.update_visa_status(self.current_card_number, "环境异常")
                print(f">>> [API] 检测到 jlh 错误状态，标记VISA卡为环境异常: {self.current_card_number}", flush=True)
            if self.phone:
                self.ban_phone(self.phone, reason="环境异常")
            return 'STOP'

        # ID: jlg 网络或装置环境异常，标记为环境异常并结束本轮流程
        if self.click_id("com.tencent.mm:id/jlg", timeout=200):
            print(">>> [异常] 检测到网络或装置环境异常，标记手机号和VISA卡为环境异常，开始下一轮流程", flush=True)
            # 标记VISA卡为环境异常
            if hasattr(self, 'current_card_number') and self.current_card_number:
                self.update_visa_status(self.current_card_number, "环境异常")
                print(f">>> [API] 检测到 jlg 环境异常，标记VISA卡为环境异常: {self.current_card_number}", flush=True)
            if self.phone:
                self.ban_phone(self.phone, reason="环境异常")
            return 'STOP'

        # 优先点击 去驗證 文本节点
        if self.click_text("去驗證", timeout=500):
            print(f">>> [去驗證] 文本点击成功: 去驗證", flush=True)
            self.sleep(2)
            return True

        # 检测 Consent Required 文本，识别到后判定为成功
        if self.click_by_text_contain("Consent Require", timeout=200):
            print(">>> [Consent] 检测到 Consent Required，判定为成功", flush=True)
            return True

        # 通道一模式：使用节点文本检测（只在无障碍模式处理完后检测）
        if self.channel1_mode == 1:
            # 使用文本检测而非图像，提高效率
            if self.click_by_text_contain("僅驗證一張可用的銀行卡", timeout=500):
                print(">>> [通道一] 文本检测成功: 僅驗證一張可用的銀行卡", flush=True)
                self.sleep(2)
                return True
        

            # 通道一模式下检测请求无效.png
            if self.click_image("wx/请求无效.png", threshold=0.7):
                print(f">>> [通道一] 检测到请求无效.png", flush=True)

                # 标记VISA卡状态为"请求无效"
                if hasattr(self, 'current_card_number') and self.current_card_number:
                    self.update_visa_status(self.current_card_number, "请求无效")
                    print(f">>> [API] 标记VISA卡状态为: 请求无效", flush=True)
                
                if self.phone:
                    # 调用API累加失败计数
                    fail_count = self.add_visa_fail_count(self.phone)
                    print(f">>> [VISA] 当前失败次数: {fail_count}/3", flush=True)

                    # 每次检测到请求无效，都先标记VISA为"请求无效"
                    if hasattr(self, 'current_card_number') and self.current_card_number:
                        self.update_visa_status(self.current_card_number, "请求无效")

                    # 根据失败次数决定后续操作
                    if fail_count >= 3:
                        # 第三次失败：标记VISA失败 + 标记手机号失败 + 删除容器
                        print(f">>> [VISA] 失败次数达到3次，标记VISA失败，标记手机号失败，删除容器", flush=True)
                        self.ban_visa(self.current_card_number)
                        self.ban_phone(self.phone)
                        # 点击返回按钮
                        if self.click_id("com.tencent.mm:id/actionbar_up_indicator_btn"):
                            print(f">>> [返回] 点击返回按钮成功", flush=True)
                        self.sleep(2)
                        return 'STOP'
                    elif fail_count >= 2:
                        # 第二次失败：标记VISA失败，获取下一个VISA
                        print(f">>> [VISA] 失败次数达到2次，标记VISA失败，继续获取下一个VISA", flush=True)
                        self.ban_visa(self.current_card_number)
                    else:
                        # 第一次失败：继续获取下一个VISA
                        print(f">>> [VISA] 失败次数1次，继续获取下一个VISA", flush=True)
                else:
                    # 没有手机号，直接返回继续
                    print(f">>> [VISA] 无手机号信息，继续获取下一个VISA", flush=True)
                
                # 点击返回按钮
                if self.click_id("com.tencent.mm:id/actionbar_up_indicator_btn"):
                    print(f">>> [返回] 点击返回按钮成功", flush=True)
                self.sleep(2)
                return True

        # 檢測繼續註冊文本
        if self.click_text("繼續註冊", timeout=500):
            print(f">>> [VISA] 檢測到繼續註冊文本，點擊继续", flush=True)
            self.sleep(2)
            return True
        
        # 通道三界面检测
        s_channel3 = self.selector()
        s_channel3.addQuery_TextContainWith("Verify and Acti")
        nodes_channel3 = s_channel3.execQuery(1, 100)
        if nodes_channel3:
            # 通道一模式：使用文本检测
            if self.channel1_mode == 1:
                # 使用文本检测"僅驗證一張可用的銀行卡"
                if self.click_by_text_contain("僅驗證一張可用的銀行卡", timeout=500):
                    print(">>> [通道一] 文本检测成功: 僅驗證一張可用的銀行卡", flush=True)
                    self.sleep(2)
                    return True
                
                # 通道一模式：点击 "Verify via Payment" 节点
                s_ch1 = self.selector()
                s_ch1.addQuery_TextContainWith("Verify via Paym")
                nodes_ch1 = s_ch1.execQuery(1, 100)
                if nodes_ch1:
                    print(f">>> [通道一] 检测到 Verify via Payment 界面，勾选了通道一模式，点击 Verify via Payment 节点", flush=True)
                    if self.click_node(nodes_ch1[0]):
                        print(f">>> [通道一] Verify via Payment 节点点击成功", flush=True)
                        self.sleep(2)
                        return True

                # 通道一模式：点击 "驗證銀行卡" 节点
                s_bank = self.selector()
                s_bank.addQuery_TextContainWith("驗證銀行卡")
                nodes_bank = s_bank.execQuery(1, 100)
                if nodes_bank:
                    print(f">>> [通道一] 检测到 驗證銀行卡 界面，勾选了通道一模式，点击 驗證銀行卡 节点", flush=True)
                    if self.click_node(nodes_bank[0]):
                        print(f">>> [通道一] 驗證銀行卡 节点点击成功", flush=True)
                        self.sleep(2)
                        return True
            
            # 如果勾选了通道三模式，则点击通道三节点（Verify and Acti本身就是通道三节点），而不是返回
            if self.channel3_mode == 1:
                print(f">>> [通道三] 检测到 Verify and Acti 界面，勾选了通道三模式，直接点击 Verify and Acti 节点", flush=True)
                # Verify and Acti 本身就是通道三的节点，直接点击
                if self.click_node(nodes_channel3[0]):
                    print(f">>> [通道三] Verify and Acti 节点点击成功", flush=True)
                    self.sleep(2)
                    return True
                else:
                    print(f">>> [通道三] Verify and Acti 节点点击失败，执行返回操作", flush=True)
                    self.press_back(); self.sleep(2)
                    self.click_id("com.tencent.mm:id/lrn"); self.sleep(5)
                    return True
            else:
                # 未勾选通道三模式，执行原来的返回逻辑
                self.jump_count += 1
                
                if self.jump_count >= self.max_jumps:
                    print(f">>> [跳码] 达到跳码次数{self.max_jumps} 已停止！", flush=True)
                    if self.phone: self.ban_phone(self.phone)
                    return 'STOP'
                    
                print(f">>> [通道三] Verify and Acti {self.jump_count}/{self.max_jumps}", flush=True)
                self.press_back(); self.sleep(2)
                self.click_id("com.tencent.mm:id/lrn"); self.sleep(5)
                return True

        # Close / Webpage Err / 關閉 / 網頁無法使用
        s_close = self.selector()
        s_close.addQuery_TextEqual("Close")
        s_close_tw = self.selector()
        s_close_tw.addQuery_TextEqual("關閉")
        s_web_err = self.selector()
        s_web_err.addQuery_TextContainWith("Webpage not ava")
        s_web_err_tw = self.selector()
        s_web_err_tw.addQuery_TextContainWith("網頁無法使用")

        if s_close_tw.execQuery(1, 100):
            # 只识别到 "關閉" 时，判定当前VISA失败
            if hasattr(self, 'current_card_number') and self.current_card_number:
                print(f">>> [VISA] 检测到 關閉，判定当前VISA失败: {self.current_card_number}", flush=True)
                self.ban_visa(self.current_card_number)
                if self.phone:
                    fail_count = self.add_visa_fail_count(self.phone)
                    print(f">>> [VISA] 当前失败次数: {fail_count}/3", flush=True)
                    if fail_count >= 3:
                        print(f">>> [VISA] 失败次数达到3次，标记手机号失败，开始下一轮流程", flush=True)
                        self.ban_phone(self.phone)
                        return 'STOP'

            print(">>> [异常] 检测到 關閉，重置网络并重试...", flush=True)
            self.setup_proxy()
            self.setup_ikuai_pptp()
            self.press_back(); self.sleep(2)
            self.click_id("com.tencent.mm:id/lrn"); self.sleep(5)
            return True

        if s_close.execQuery(1, 100) or s_web_err.execQuery(1, 100) or s_web_err_tw.execQuery(1, 100):
            print(">>> [异常] 检测到 Close/網頁無法使用 或网络错误，重置网络并重试...", flush=True)
            self.setup_proxy()
            self.setup_ikuai_pptp()
            self.press_back(); self.sleep(2)
            self.click_id("com.tencent.mm:id/lrn"); self.sleep(5)
            return True

        return False



    def get_sms_code(self):
        """从 API 获取验证码"""
        if not hasattr(self, 'sms_api_url') or not self.sms_api_url:
            return None

        try:
            resp = requests.get(self.sms_api_url, timeout=10,verify=False)
            if resp.status_code == 200:
                
                import re, html
                text = html.unescape(resp.text or "")

                # 优先尝试从 JSON 格式中提取 data.code 字段的验证码
                try:
                    json_data = resp.json()
                    if json_data and isinstance(json_data, dict):
                        # 尝试从 data.code 或 code 字段获取
                        code = None
                        if 'data' in json_data and isinstance(json_data['data'], dict):
                            code = json_data['data'].get('code', '')
                        elif 'code' in json_data:
                            code = json_data.get('code', '')

                        # 将整数/其他类型统一转成字符串再判断
                        if code is not None:
                            code_str = str(code).strip()
                            if code_str.isdigit() and len(code_str) == 6:
                                if code_str == self.last_input_code:
                                    print(f">>> [SMS] 验证码与上次相同，等待更新...", flush=True)
                                    return None
                                print(f">>> [SMS] 获取验证码成功: {code_str}", flush=True)
                                return code_str
                except:
                    pass

                
                match_list = re.findall(r'(?<!\d)(\d{6})(?!\d)', text)
                if match_list:
                    code = match_list[0]
                    if code == self.last_input_code:
                        print(f">>> [SMS] 验证码与上次相同，等待更新...", flush=True)
                        return None
                    print(f">>> [SMS] 获取验证码成功: {code}", flush=True)
                    return code

                # 兜底：基于“code/验证码”关键字附近的数字提取，允许 4-8 位，优先6位
                m = re.search(r'(?:code|验证码|verification\s*code)[^\d]{0,16}(\d{4,8})', text, re.IGNORECASE)
                if m:
                    c = m.group(1)
                    # 如果提取到非6位，尝试再在整段里找6位；否则按提取结果返回
                    if len(c) != 6:
                        match_list = re.findall(r'(?<!\d)(\d{6})(?!\d)', text)
                        if match_list:
                            code = match_list[0]
                        else:
                            code = c
                    else:
                        code = c
                    if code == self.last_input_code:
                                print(f">>> [SMS] 验证码与上次相同，等待更新...", flush=True)
                                return None
                    print(f">>> [SMS] 获取验证码成功: {code}", flush=True)
                    return code
        except Exception as e:
            print(f">>> [SMS] 请求失败: {e}", flush=True)

        return None

    def mark_phone_success(self, phone):
        """标记手机号注册成功"""
        try:
            from datetime import datetime
            time_val = datetime.now().strftime("%y/%m.%d %H:%M")
            url = "http://127.0.0.1:8080/success_phone"
            requests.get(url, params={"phone": phone, "time": time_val}, timeout=5)
            print(f">>> [API] 已标记手机号成功: {phone} (时间: {time_val})", flush=True)
        except Exception as e:
            print(f">>> [API] 标记成功失败: {e}", flush=True)

    def extract_and_save_data(self):
        """提取Wxid, A16并保存数据"""
        print(">>> [提取] 开始提取账号数据...", flush=True)
        import re
        from datetime import datetime
        
        if not self.rpc: return
        
        # 1. 获取 XML (Wxid, Phone)
        xml_cmd = "cat /data/user/0/com.tencent.mm/shared_prefs/com.tencent.mm_preferences.xml"
        output, _ = self.rpc.exec_cmd(xml_cmd)
        
        wxid = "unknown"
        xml_phone = None
        
        if output:
            m = re.search(r'login_weixin_username">([^<]+)<', output)
            if m: wxid = m.group(1)
            
            m_p = re.search(r'login_user_name">([^<]+)<', output)
            if not m_p:
                 m_p = re.search(r'last_login_bind_mobile">([^<]+)<', output)
            if m_p: xml_phone = m_p.group(1).replace("+", "")

        final_phone = xml_phone if xml_phone else (self.phone.replace("+", "") if self.phone else "unknown")
        print(f">>> [提取] Wxid: {wxid}, Phone: {final_phone}", flush=True)
        
        # 保存手机号，用于后续重命名容器
        self.last_phone = final_phone
        
        # 2. 获取 A16
        a16_cmd = "cat /data/data/com.tencent.mm/.auth_cache/2510c390-11c5-3e70-8182-423e3a695e91/1"
        out_a16, _ = self.rpc.exec_cmd(a16_cmd)
        a16 = "unknown"
        if out_a16:
             a16 = out_a16.strip().split(',')[0]
             print(f">>> [提取] A16: {a16}", flush=True)
        else:
             print(">>> [提取] A16 读取失败或为空", flush=True)
        
        # 3. 构造数据
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sms_url = getattr(self, 'sms_api_url', "No_URL")
        if not sms_url: sms_url = "No_URL"
        password = getattr(self, 'password', "unknown")
        
        # 获取主机IP和容器名称
        host_ip = getattr(self, 'host_ip', self.ip)
        container_name = getattr(self, 'container_name', 'unknown')
        
        # 从容器名称中提取坑位号 (例如: 1773637352802_1_T0001 -> 1)
        slot_number = "1"
        if container_name and '_' in container_name:
            parts = container_name.split('_')
            if len(parts) >= 2:
                slot_number = parts[1]  # 取下划线后的第二部分
        
        # 构造主机IP-坑位号
        host_ip_with_slot = f"{host_ip}-{slot_number}"
        
        line1 = f"{final_phone}----{password}----{sms_url}----{date_str}\n"
        line2 = f"{final_phone}----{password}----{sms_url}----{wxid}----{a16}----{date_str}----{host_ip_with_slot}\n"
        
        # 4. 追加写入
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        
        file1 = os.path.join(root_dir, "账号数据.txt")
        file2 = os.path.join(root_dir, "a16数据.txt")
        
        try:
            with open(file1, "a", encoding="utf-8") as f: f.write(line1)
            with open(file2, "a", encoding="utf-8") as f: f.write(line2)
            print(f">>> [保存] 数据已保存至: {file1}, {file2}", flush=True)

            # 上传平台功能（如果启用）
            if getattr(self, 'upload_platform', 0) == 1 and wxid != "unknown" and a16 != "unknown":
                try:
                    platform_url = "http://42.194.236.159:1111/PostApi/data"
                    upload_data = f"{wxid}----{password}----{a16}"
                    params = {"data": upload_data, "type": "123", "Td": "1"}
                    resp = requests.get(platform_url, params=params, timeout=10)
                    if resp.status_code == 200:
                        try:
                            result = resp.json()
                            if result.get('code') == 200:
                                print(f">>> [上传平台] 上传成功: {wxid}----{password}----{a16}", flush=True)
                            else:
                                print(f">>> [上传平台] 上传失败: {result.get('msg', '未知原因')}", flush=True)
                        except:
                            print(f">>> [上传平台] 上传成功: {wxid}----{password}----{a16}", flush=True)
                    else:
                        print(f">>> [上传平台] 上传失败 HTTP {resp.status_code}", flush=True)
                except Exception as e:
                    print(f">>> [上传平台] 上传失败: {e}", flush=True)

            # 标记VISA卡成功（在提取a16完成后）
            if hasattr(self, 'current_card_number') and self.current_card_number:
                self.success_visa(self.current_card_number)
                print(f">>> [VISA] 提取a16完成，标记VISA卡成功: {self.current_card_number}", flush=True)
            # 重置VISA失败计数
            if self.phone:
                self.reset_visa_fail_count(self.phone)

        except Exception as e:
            print(f">>> [错误] 保存文件失败: {e}", flush=True)

    def run_authorized_enterprise_post_steps(self):
        """授权企业后续步骤 - 成功后在新建/删除容器前执行（循环执行）"""
        print(">>> [授权企业] 开始执行后续步骤...", flush=True)

        step_delay = 2    # 步骤间延时
        max_loops = 100   # 最大循环次数，防止死循环
        qiyewx_clicked = False  # 企业微信服务号入口只点击一次
        search_input_done = False  # 是否已输入"企业微信小程序入口"
        search_input_clicked = False  # 是否已点击ltk（搜索结果入口）
        weuiAgree_clicked = False  # 是否已点击weuiAgree

        try:
            for loop in range(max_loops):
                print(f">>> [授权企业] 第 {loop + 1} 轮检测...", flush=True)

                # 1. 允许（任何时候都优先检测）
                if self.click_id("com.android.permissioncontroller:id/permission_allow_button"):
                    print(">>> [授权企业] 点击允许 成功", flush=True)
                    self.sleep(step_delay)
                    continue

                # 2. 检测"下一步"或"完成"按钮
                click_next = self.text_exists("下一步")
                click_finish = self.text_exists("完成")
                click_target = click_finish or click_next  # "完成"优先
                weuiAgree_exists = self.text_exists_id("weuiAgree")
                if click_target:
                    if weuiAgree_exists:
                        # 情况1：同时存在 weuiAgree + 下一步/完成 → 先点weuiAgree，再点下一步/完成
                        if self.click_id("weuiAgree"):
                            print(">>> [授权企业] 点击weuiAgree 成功", flush=True)
                            weuiAgree_clicked = True
                            self.sleep(step_delay)
                    # 无论是否有weuiAgree，都点击下一步/完成
                    target_text = "完成" if click_finish else "下一步"
                    if self.click_text(target_text):
                        print(f">>> [授权企业] 点击{target_text} 成功", flush=True)
                        self.sleep(step_delay)
                        continue
                    # 如果点击失败（比如页面已变化），也继续下一轮检测
                    continue

                # 4. 取消 - 输入搜索词之前且未点击weuiAgree才点击
                if not search_input_done and not weuiAgree_clicked and self.click_text("取消"):
                    print(">>> [授权企业] 点击取消 成功", flush=True)
                    self.sleep(step_delay)
                    continue

                # 4. 搜尋
                if not search_input_done and self.click_id("com.tencent.mm:id/jha"):
                    print(">>> [授权企业] 点击搜尋 成功，输入：企业微信小程序入口", flush=True)
                    self.sleep(step_delay)
                    self.sleep(1)
                    self.input_text("企业微信小程序入口")
                    search_input_done = True  # 标记已输入搜索词
                    self.sleep(step_delay)
                    continue

                # 5. 企业微信小程序入口 (ltk) - 输入完搜索词后点击
                if search_input_done and not search_input_clicked and self.click_id("com.tencent.mm:id/ltk"):
                    print(">>> [授权企业] 点击企业微信小程序入口 成功", flush=True)
                    search_input_clicked = True
                    self.sleep(step_delay)
                    continue

                # 6. 企业微信服务号入口（文本或图标）- 只处理一次
                if not qiyewx_clicked and (self.click_text("企业微信 服务号 账号描述:") or self.click_image("·", threshold=0.7)):
                    qiyewx_clicked = True
                    print(">>> [授权企业] 选中企业微信服务号入口 成功", flush=True)
                    self.sleep(step_delay)
                    continue

                # 7. 同意並啟用
                if self.click_id("com.tencent.mm:id/kao"):
                    print(">>> [授权企业] 点击同意並啟用 成功", flush=True)
                    self.sleep(step_delay)
                    continue

                # 8. 關注服務賬號
                if self.click_id("com.tencent.mm:id/ams"):
                    print(">>> [授权企业] 点击關注服務賬號 成功", flush=True)
                    self.sleep(step_delay)
                    continue

                # 9. 看案例 (Index 1) - 识别到后退出循环
                if self.click_by_id("com.tencent.mm:id/bln", index=1):
                    print(">>> [授权企业] 点击看案例(Index 1) 成功，识别到目标，退出循环", flush=True)
                    self.sleep(step_delay)
                    break

                self.sleep(1)

            print(">>> [授权企业] 后续步骤执行完成", flush=True)
            return True
        except Exception as e:
            print(f">>> [授权企业] 后续步骤执行异常: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False

    def _process_success(self):
        """检测注册成功 (权限弹窗 / WeChat所需同意)"""
        # 方法1: 检测权限弹窗
        s = self.selector()
        s.addQuery_IdEqual("com.android.permissioncontroller:id/permission_message")
        if s.execQuery(1, 100):
            print(f">>> [状态] 注册成功！(检测到权限弹窗)", flush=True)
            if self.phone:
                self.mark_phone_success(self.phone)

            # 提取并保存数据
            self.extract_and_save_data()

            # 设置成功标记（用于主循环判断是否保存镜像）
            self.registration_success = True

            return True

        # 方法2: 检测 WeChat 所需同意 文本节点
        s2 = self.selector()
        s2.addQuery_TextEqual("WeChat 所需同意")
        if s2.execQuery(1, 100):
            print(f">>> [状态] 注册成功！(检测到 WeChat 所需同意)", flush=True)
            if self.phone:
                self.mark_phone_success(self.phone)

            # 提取并保存数据
            self.extract_and_save_data()

            # 设置成功标记（用于主循环判断是否保存镜像）
            self.registration_success = True

            return True

        return False

    def clear_success_flag(self):
        """清除成功标记"""
        self.registration_success = False

    def _process_buttons(self):
        """常规流程按钮"""
        # 组合操作: Checkbox -> 延时 -> Next
        if self.click_id("weuiAgreeCheckbox"):
            self.sleep(random.uniform(0.5, 0.8))
            self.click_id("btnNext")
            return True

        # 兜底: 只有 Next 或 Start (不在协议页的情况)
        if self.click_id("btnNext") or self.click_image("wx/start.png"):
            self.sleep(2); return True
            
        return False

    def _run_en(self):
        """英文界面注册主循环（美国/US 地区）"""
        print(">>> [EN] 英文界面注册逻辑启动", flush=True)
        # TODO: 在这里编写英文界面的注册流程
        pass

    def setup_proxy(self):
        """配置SOCKS5代理 (使用统一的 container_manager) - 自动识别非桥接模式"""
        try:
            is_bridge_ip = self.ip.startswith("10.0.1.")
            
            # 桥接IP（10.0.1.x）→ 不使用SK5，跳过
            if is_bridge_ip:
                print(f">>> [网络] 检测到桥接IP ({self.ip})，跳过SK5配置（将使用爱快PPTP）", flush=True)
                return True
            
            # 非桥接：允许任意合法 IPv4（含 192.168.x.x）配置SK5
            try:
                ip_obj = ipaddress.ip_address(self.ip)
                if ip_obj.version != 4:
                    raise ValueError("not ipv4")
            except Exception:
                print(f">>> [网络] IP格式异常 ({self.ip})，跳过SK5配置", flush=True)
                return True
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if not os.path.exists(config_path): 
                print(f">>> [网络] 未找到config.json，跳过SK5配置", flush=True)
                return True
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 使用统一的 container_manager 设置 SOCKS5
            socks5_config = config.get("socks5", {})
            success, message = container_manager.setup_socks5_proxy(
                device_ip=self.ip,
                device_port=self.port,
                socks5_config=socks5_config
            )
            
            if success:
                print(f">>> [网络] {message}", flush=True)
            else:
                print(f">>> [网络] {message}", flush=True)
            
            return success
        except Exception as e:
            print(f">>> [网络] 配置读取异常: {e}", flush=True)
            return True

    def setup_ikuai_pptp(self):
        """配置爱快PPTP网络 (使用统一的 container_manager) - 自动识别桥接模式"""
        try:
            # 自动识别：桥接IP（10.0.1.x）→ 自动使用爱快
            is_bridge_ip = self.ip.startswith("10.0.1.")
            if not is_bridge_ip:
                print(f">>> [网络] 非桥接IP ({self.ip})，跳过PPTP配置（将使用SK5代理）", flush=True)
                return True
            
            # 桥接IP（10.0.1.x）→ 自动使用爱快，传递容器索引用于推导
            config_dict = {
                'index': self.index  # 传递容器索引，用于从宿主机IP推导容器IP（如果将来需要）
            }
            
            success, message = container_manager.setup_ikuai_pptp(
                device_ip=self.ip,
                config_dict=config_dict
            )
            
            if success:
                print(f">>> [网络] {message}", flush=True)
            else:
                print(f">>> [网络] {message}", flush=True)
            
            return success
        except Exception as e:
            print(f">>> [网络] 配置PPTP网络异常: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False

    def _switch_ip(self):
        """切换IP地址（使用统一的 container_manager）"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if not os.path.exists(config_path):
                return False, "未找到config.json"

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 构建配置字典
            config_dict = {}
            script_config = config.get("script_config", {})
            config_dict['enable_socks5'] = script_config.get("enable_socks5", False)
            config_dict['enable_ikuai'] = script_config.get("enable_ikuai", False)
            config_dict['useBridge'] = script_config.get("useBridge", False)
            config_dict['pptp_prefix'] = script_config.get("pptp_prefix", "")
            config_dict['pptp_ip_number'] = script_config.get("pptp_ip_number", "")

            # 调用 container_manager 的 switch_ip 方法
            success, message = container_manager.switch_ip(config_dict=config_dict)

            if success:
                print(f">>> [网络] IP切换成功: {message}", flush=True)
            else:
                print(f">>> [网络] IP切换失败: {message}", flush=True)

            return success, message
        except Exception as e:
            print(f">>> [网络] IP切换异常: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False, str(e)

    def ban_phone(self, phone, reason=None, time_val=None):
        """拉黑手机号"""
        try:
            from datetime import datetime
            if time_val is None:
                time_val = datetime.now().strftime("%y/%m.%d %H:%M")

            if reason:
                url = f"http://127.0.0.1:8080/ban_phone?phone={phone}&reason={reason}&time={time_val}"
                print(f">>> [API] 已拉黑手机号: {phone} (原因: {reason}, 时间: {time_val})")
            else:
                url = f"http://127.0.0.1:8080/ban_phone?phone={phone}&time={time_val}"
                print(f">>> [API] 已拉黑手机号: {phone} (时间: {time_val})")
            requests.get(url, timeout=5)
        except Exception as e:
            print(f">>> [API] 拉黑手机号失败: {e}")

    def ban_visa(self, card_number, time_val=None):
        """拉黑VISA卡"""
        try:
            from datetime import datetime
            if time_val is None:
                time_val = datetime.now().strftime("%y/%m.%d %H:%M")
            url = f"http://127.0.0.1:8080/ban_visa?card_number={card_number}&time={time_val}"
            requests.get(url, timeout=5)
            print(f">>> [API] 已拉黑VISA卡: {card_number} (时间: {time_val})")
        except Exception as e:
            print(f">>> [API] 拉黑VISA卡失败: {e}")

    def update_visa_status(self, card_number, status, time_val=None):
        """更新VISA卡状态"""
        try:
            from datetime import datetime
            if time_val is None:
                time_val = datetime.now().strftime("%y/%m.%d %H:%M")
            url = f"http://127.0.0.1:8080/update_visa_status?card_number={card_number}&status={status}&time={time_val}"
            requests.get(url, timeout=5)
            print(f">>> [API] 已更新VISA卡状态: {card_number} -> {status} (时间: {time_val})")
        except Exception as e:
            print(f">>> [API] 更新VISA卡状态失败: {e}")

    def success_visa(self, card_number, time_val=None):
        """标记VISA卡成功"""
        try:
            from datetime import datetime
            if time_val is None:
                time_val = datetime.now().strftime("%y/%m.%d %H:%M")
            url = f"http://127.0.0.1:8080/success_visa?card_number={card_number}&time={time_val}"
            requests.get(url, timeout=5)
            print(f">>> [API] 已标记VISA成功: {card_number} (时间: {time_val})")
        except Exception as e:
            print(f">>> [API] 标记VISA成功失败: {e}")

    def add_visa_fail_count(self, phone):
        """累加VISA失败计数"""
        try:
            url = f"http://127.0.0.1:8080/add_visa_fail_count?phone={phone}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            return data.get("fail_count", 0)
        except Exception as e:
            print(f">>> [API] 累加VISA失败计数失败: {e}")
            return 0

    def get_visa_fail_count(self, phone):
        """查询VISA失败计数"""
        try:
            url = f"http://127.0.0.1:8080/get_visa_fail_count?phone={phone}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            return data.get("fail_count", 0)
        except Exception as e:
            print(f">>> [API] 查询VISA失败计数失败: {e}")
            return 0

    def reset_visa_fail_count(self, phone):
        """重置VISA失败计数"""
        try:
            url = f"http://127.0.0.1:8080/reset_visa_fail_count?phone={phone}"
            requests.get(url, timeout=5)
            print(f">>> [API] VISA失败计数已重置: {phone}")
        except Exception as e:
            print(f">>> [API] 重置VISA失败计数失败: {e}")

    def get_max_jumps(self):
        """从配置文件读取最大跳码次数"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return int(config.get("script_config", {}).get("jump_count", 3))
        except: pass
        return 3

    def get_channel3_mode(self):
        """从配置文件读取通道三模式开关"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return int(config.get("script_config", {}).get("channel3_mode", 0))
        except: pass
        return 0

    def get_channel1_mode(self):
        """从配置文件读取通道一模式开关"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return int(config.get("script_config", {}).get("channel1_mode", 0))
        except: pass
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--index", type=int, default=1)
    parser.add_argument("--rebuild", action="store_true", help="Enable container rebuild in loop")
    parser.add_argument("--rebuild-count", type=int, default=1, help="Number of loops before rebuild (default: 1)")
    parser.add_argument("--no-delete-on-success", action="store_true", help="成功不删除当前容器，只新建一个继续；失败N次后删除重建")
    parser.add_argument("--authorized-enterprise", action="store_true", help="授权企业模式：成功后在新建/删除容器前先执行后续步骤")
    args = parser.parse_args()

    authorized_enterprise = args.authorized_enterprise
    no_delete_on_success = args.no_delete_on_success

    task = DemoTask(args.ip, args.port, index=args.index)

    host_ip = getattr(task, 'host_ip', None) or args.ip

    rebuild_count = args.rebuild_count if args.rebuild_count > 0 else 1
    print(f">>> [系统] 脚本启动 - 重建: {args.rebuild}, 失败{rebuild_count}次删除重建, 成功不删除: {no_delete_on_success}", flush=True)

    is_first_loop = True  # 标记是否为重建后的首次运行（需要安装微信）
    loop_count = 0  # 记录重建后运行的循环次数
    failure_count = 0  # 记录连续失败次数

    while True:
        try:
            # 1. 重置容器 (环境隔离)
            # 逻辑：
            # - 不删除重建模式首次运行：不删除旧容器，直接新建一个
            # - 不删除重建模式失败N次后：删除重建
            # - 普通重建模式：首次运行跳过（由外部工具完成），失败N次后删除重建
            should_rebuild = False
            rebuild_type = None  # "create_new"=新建(不删除旧), "rebuild"=删除重建
            container_already_created_this_round = False  # 本轮是否已经创建过新容器

            if args.rebuild:
                if no_delete_on_success:
                    # 不删除重建模式
                    # 检查本轮是否已经创建过新容器（注册成功后已创建）
                    if container_already_created_this_round:
                        print(f">>> [系统] 本轮已创建新容器，跳过重建逻辑", flush=True)
                    elif is_first_loop and loop_count == 0:
                        # 首次运行：不删除旧容器，直接新建一个
                        print(f">>> [系统] 不删除重建模式，首次运行，新建一个容器...", flush=True)
                        should_rebuild = True
                        rebuild_type = "create_new"
                    elif loop_count >= rebuild_count:
                        # 失败N次后，删除重建
                        print(f">>> [系统] 达到{rebuild_count}次失败，删除重建...", flush=True)
                        should_rebuild = True
                        rebuild_type = "rebuild"
                else:
                    # 普通重建模式
                    if is_first_loop and loop_count == 0:
                        print(f">>> [系统] 首次运行，跳过脚本内重置", flush=True)
                    else:
                        if loop_count >= rebuild_count:
                            should_rebuild = True
                            rebuild_type = "rebuild"

            # 2. 需要重建时，先创建新容器
            if should_rebuild:
                new_container_ip = None

                if rebuild_type == "create_new":
                    # 不删除重建模式：不删除旧容器，直接新建一个
                    print(f">>> [系统] 正在新建容器（不删除旧容器）...", flush=True)
                    try:
                        success, new_container_ip, msg, new_container_name = task.create_container_no_delete(task.image_keyword)
                        if success:
                            print(f">>> [系统] 新容器已创建: {msg}", flush=True)
                        else:
                            # 创建失败，不再走删除重建，等待 10s 后重试
                            print(f">>> [系统] 新容器创建失败: {msg}，等待 10s 后重试...", flush=True)
                            time.sleep(10)
                            continue
                    except Exception as e:
                        # 创建异常，不再走删除重建，等待 10s 后重试
                        print(f">>> [系统] 创建新容器异常: {e}，等待 10s 后重试...", flush=True)
                        time.sleep(10)
                        continue
                else:
                    # 删除重建
                    print(f">>> [系统] 正在重置容器（删除重建）...", flush=True)
                    success, new_container_ip, msg, new_container_name = task.reset_container(task.image_keyword)
                    if not success:
                        print(f">>> [系统] 容器重置失败: {msg}，等待 10s 后重试...", flush=True)
                        time.sleep(10)
                        continue
                    print(f">>> [系统] 容器已重置: {msg}", flush=True)

                # 如果创建了新容器，更新task的IP和容器名称
                if new_container_ip:
                    print(f">>> [系统] 更新设备连接IP: {task.ip} -> {new_container_ip}", flush=True)
                    task.ip = new_container_ip
                    # task.port 已在 create_container_no_delete 中正确设置
                    # 同时更新host_ip
                    host_ip = new_container_ip
                # 更新容器名称
                if new_container_name:
                    print(f">>> [系统] 更新容器名称: {task.container_name} -> {new_container_name}", flush=True)
                    task.container_name = new_container_name

                is_first_loop = True
                loop_count = 0
                print(f">>> [系统] 容器重建完成，将重新安装微信并开始新一轮", flush=True)

            # 3. 连接设备
            task.connect()

            # 3. 执行任务
            # 重建后的首次运行：安装微信
            # 后续运行：清理微信（不安装）
            if is_first_loop:
                skip_install = False  # 重建后的首次运行，安装微信
            else:
                skip_install = True   # 后续运行，清理微信（不安装）

            task.run(skip_install=skip_install)

            # 4. 判断本轮执行结果（成功/失败）
            registration_success = getattr(task, 'registration_success', False)
            task.clear_success_flag()

            # 授权企业模式：成功后在新建/删除容器前先执行后续步骤
            if authorized_enterprise and registration_success:
                print(f">>> [授权企业] 注册成功，先执行后续步骤...", flush=True)
                task.run_authorized_enterprise_post_steps()

            # 不删除重建模式：成功则新建容器继续，失败累计
            if no_delete_on_success:
                if registration_success:
                    # 成功：不删除当前容器，只新建一个继续
                    print(f">>> [系统] 注册成功！当前容器保留，新建一个继续...", flush=True)
                    
                    # 不删除重建模式下，将当前容器名称修改为手机号
                    if task.last_phone and task.last_phone != "unknown":
                        try:
                            import requests
                            # 获取宿主机IP
                            rename_host_ip = getattr(task, 'host_ip', None) or args.ip
                            # API端口改为8000
                            rename_api_port = 8000
                            rename_api = f"http://{rename_host_ip}:{rename_api_port}/android/rename"
                            rename_payload = {
                                "name": task.container_name.lstrip("/"),
                                "newName": task.last_phone
                            }
                            rename_resp = requests.post(rename_api, json=rename_payload, timeout=10)
                            if rename_resp.status_code == 200:
                                print(f">>> [系统] 容器名称已修改: {task.container_name} -> {task.last_phone}", flush=True)
                            else:
                                print(f">>> [系统] 容器名称修改失败: {rename_resp.text}", flush=True)
                        except Exception as e:
                            print(f">>> [系统] 容器名称修改异常: {e}", flush=True)
                    else:
                        print(f">>> [系统] 未获取到手机号，跳过重命名", flush=True)
                    
                    failure_count = 0
                    new_container_ip = None
                    new_container_name = None
                    try:
                        success, new_container_ip, msg, new_container_name = task.create_container_no_delete(task.image_keyword)
                        if success:
                            print(f">>> [系统] 新容器已创建: {msg}", flush=True)
                        else:
                            # 创建失败，不再走删除重建，等待下次重试
                            print(f">>> [系统] 新容器创建失败: {msg}，当前容器保留，等待下次重试...", flush=True)
                    except Exception as e:
                        print(f">>> [系统] 创建新容器异常: {e}，当前容器保留，等待下次重试...", flush=True)

                    # 更新task的IP和容器名称
                    if new_container_ip:
                        print(f">>> [系统] 更新设备连接IP: {task.ip} -> {new_container_ip}", flush=True)
                        task.ip = new_container_ip
                        # task.port 已在 create_container_no_delete 中正确设置
                        host_ip = new_container_ip
                        # 重要：新容器需要安装微信，设置 is_first_loop=True 让下一轮安装
                        # 同时设置 loop_count=1 避免下一轮再次触发创建新容器
                        is_first_loop = True
                        loop_count = 1
                        # 标记本轮已经创建过新容器，避免下一轮重复创建
                        container_already_created_this_round = True
                    # 更新容器名称
                    if new_container_name:
                        print(f">>> [系统] 更新容器名称: {task.container_name} -> {new_container_name}", flush=True)
                        task.container_name = new_container_name
                    # 成功创建新容器后，跳过后面的状态更新逻辑，直接进入下一轮
                    # finally块会处理task.stop()
                    print(">>> [系统] 本轮任务结束，3秒后开始下一轮...", flush=True)
                    continue
                else:
                    # 失败：累计次数，达到次数则删除重建
                    failure_count += 1
                    print(f">>> [系统] 注册失败，当前失败次数: {failure_count}/{rebuild_count}", flush=True)
                    if failure_count >= rebuild_count:
                        # 不删除重建模式下，注册失败时需要删除容器
                        if no_delete_on_success:
                            print(f">>> [系统] 达到{rebuild_count}次失败，不删除重建模式：删除当前容器并重建...", flush=True)
                            # 先删除当前容器
                            try:
                                from scripts.framework.container_manager import delete_container
                                success, msg = delete_container(task.host_ip, task.container_name)
                                print(f">>> [系统] 删除旧容器: {msg}", flush=True)
                            except Exception as e:
                                print(f">>> [系统] 删除旧容器异常: {e}", flush=True)
                        else:
                            print(f">>> [系统] 达到{rebuild_count}次失败，删除容器并重建...", flush=True)
                        should_rebuild = True
                        failure_count = 0

            if should_rebuild:
                # 不删除重建模式下，注册失败后的重建需要删除旧容器
                if no_delete_on_success:
                    # 失败重建：使用删除重建
                    print(f">>> [系统] 正在重置容器（删除重建）...", flush=True)
                    success, new_container_ip, msg, new_container_name = task.reset_container(task.image_keyword)
                    if not success:
                        print(f">>> [系统] 容器重置失败: {msg}，等待 10s 后重试...", flush=True)
                        time.sleep(10)
                        continue
                    print(f">>> [系统] 容器已重置: {msg}", flush=True)
                elif rebuild_type == "create_new":
                    # 不删除重建模式首次运行：不删除旧容器，直接新建一个
                    print(f">>> [系统] 正在新建容器（不删除旧容器）...", flush=True)
                    try:
                        success, new_container_ip, msg, new_container_name = task.create_container_no_delete(task.image_keyword)
                        if success:
                            print(f">>> [系统] 新容器已创建: {msg}", flush=True)
                            # 标记本轮已经创建过新容器
                            container_already_created_this_round = True
                        else:
                            # 创建失败，不再走删除重建，等待 10s 后重试
                            print(f">>> [系统] 新容器创建失败: {msg}，等待 10s 后重试...", flush=True)
                            time.sleep(10)
                            continue
                    except Exception as e:
                        # 创建异常，不再走删除重建，等待 10s 后重试
                        print(f">>> [系统] 创建新容器异常: {e}，等待 10s 后重试...", flush=True)
                        time.sleep(10)
                        continue

                    # 更新task的IP和容器名称
                    if new_container_ip:
                        print(f">>> [系统] 更新设备连接IP: {task.ip} -> {new_container_ip}", flush=True)
                        task.ip = new_container_ip
                        host_ip = new_container_ip
                    if new_container_name:
                        print(f">>> [系统] 更新容器名称: {task.container_name} -> {new_container_name}", flush=True)
                        task.container_name = new_container_name
                else:
                    # 删除重建
                    print(f">>> [系统] 正在重置容器（删除重建）...", flush=True)
                    success, new_container_ip, msg, new_container_name = task.reset_container(task.image_keyword)
                    if not success:
                        print(f">>> [系统] 容器重置失败: {msg}，等待 10s 后重试...", flush=True)
                        time.sleep(10)
                        continue
                    print(f">>> [系统] 容器已重置: {msg}", flush=True)
                is_first_loop = True
                loop_count = 0
                print(f">>> [系统] 容器重建完成，将重新安装微信并开始新一轮", flush=True)
                # 失败重建后也直接进入下一轮
                print(">>> [系统] 本轮任务结束，3秒后开始下一轮...", flush=True)
                continue

            # 更新状态：标记首次运行已完成，并增加循环计数
            if is_first_loop:
                is_first_loop = False
                # 首轮完成后，循环计数仍为0（下一轮才开始计数）
                if args.rebuild:
                    print(f">>> [系统] 首轮完成，后续将每 {rebuild_count} 轮重建一次容器", flush=True)
            else:
                # 非首次运行，增加循环计数
                loop_count += 1
                if args.rebuild:
                    print(f">>> [系统] 当前循环计数: {loop_count}/{rebuild_count}", flush=True)

            print(">>> [系统] 本轮任务结束，3秒后开始下一轮...", flush=True)
            
        except KeyboardInterrupt:
            print("\n>>> [系统] 用户停止脚本", flush=True)
            break
        except Exception as e:
            print(f">>> [系统] 发生未捕获异常: {e}", flush=True)
            import traceback
            traceback.print_exc()
        finally:
            # 4. 断开连接 (确保下一轮重新连接)
            task.stop()
            time.sleep(3)
