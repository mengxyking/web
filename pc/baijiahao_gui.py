import chardet
import random
import requests
import sys
import json
import os
import threading
from util.paddleOCR_json_duixiang import OCRProcessor
import time

import pyautogui
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QGroupBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator


class RestTimeConfigurator(QMainWindow):
    """休息时间配置器主窗口"""

    def __init__(self):
        super().__init__()
        self.clicked_user = []
        # 线程管理属性
        self.auto_thread = None  # 线程对象
        self.thread_running = False  # 线程运行标志
        # 日志前缀（区分不同操作模块）
        self.log_prefix = {
            "init": "[初始化]",
            "ui": "[UI操作]",
            "thread": "[线程管理]",
            "control": "[主控制循环]",
            "screenshot": "[截图操作]",
            "ocr": "[OCR识别]",
            "click": "[点击操作]",
            "drag": "[拖拽操作]",
            "request": "[API请求]",
            "publish": "[发布流程]",
            "switch_user": "[切换用户]",
            "next_step": "[下一步操作]",
            "gen_text": "[生成文案]",
            "verify": "[安全验证]",
            "config": "[配置管理]"
        }

        # 配置文件路径
        self.config_file = "rest_time_config.json"
        print(f"{self.log_prefix['init']} 配置文件路径：{self.config_file}")
        self.ocr_processor = OCRProcessor()
        print(f"{self.log_prefix['init']} OCR处理器初始化完成")

        # 设置窗口基本属性
        self.setWindowTitle("休息时间配置器")
        self.setMinimumSize(600, 200)
        print(f"{self.log_prefix['ui']} 窗口属性设置完成：标题=休息时间配置器，最小尺寸=600x200")

        # 初始化UI
        self.init_ui()
        print(f"{self.log_prefix['ui']} UI初始化完成")

        # 初始化配置数据
        self.init_config_data()
        print(f"{self.log_prefix['config']} 配置数据初始化完成：默认间隔时间5-30分钟")

        # 加载保存的配置（如果存在）
        load_result = self.load_config()
        print(f"{self.log_prefix['config']} 配置加载结果：{'成功' if load_result else '未找到配置文件，使用默认配置'}")

    def init_ui(self):
        """初始化用户界面"""
        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        print(f"{self.log_prefix['ui']} 主布局创建完成：边距30，间距20")

        # 添加标题
        title_label = QLabel("百家号")
        title_font = QFont("SimHei", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        print(f"{self.log_prefix['ui']} 标题添加完成：文本=百家号，字体=SimHei 16号粗体")

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        print(f"{self.log_prefix['ui']} 分隔线添加完成")

        # 创建配置区域（一行布局）
        config_group = QGroupBox()
        config_layout = QHBoxLayout()
        config_layout.setSpacing(30)
        config_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 大时间配置 - 使用普通输入框
        big_time_label = QLabel("间隔时间:")
        big_time_label.setFont(QFont("SimHei", 10))
        self.big_time_input = QLineEdit()
        self.big_time_input.setValidator(QIntValidator(1, 120))
        self.big_time_input.setText("5")
        self.big_time_input.setMinimumWidth(50)
        self.big_time_input.setPlaceholderText("输入分钟数")
        print(f"{self.log_prefix['ui']} 间隔时间输入框创建完成：默认值5，范围1-120")

        # 小时间配置 - 使用普通输入框
        small_time_label = QLabel("到")
        small_time_label.setFont(QFont("SimHei", 10))
        self.small_time_input = QLineEdit()
        self.small_time_input.setValidator(QIntValidator(1, 60))
        self.small_time_input.setText("30")
        self.small_time_input.setMinimumWidth(50)
        self.small_time_input.setPlaceholderText("输入分钟数")
        print(f"{self.log_prefix['ui']} 结束时间输入框创建完成：默认值30，范围1-60")

        # 添加到布局
        config_layout.addWidget(big_time_label)
        config_layout.addWidget(self.big_time_input)
        config_layout.addWidget(small_time_label)
        config_layout.addWidget(self.small_time_input)
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        print(f"{self.log_prefix['ui']} 配置区域布局完成")

        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(20)

        # 保存配置按钮
        self.save_button = QPushButton("保存配置")
        self.save_button.setFont(QFont("SimHei", 10))
        self.save_button.setMinimumHeight(40)
        self.save_button.setMinimumWidth(120)
        self.save_button.setStyleSheet("""
            QPushButton {background-color: #2196F3; color: white; border-radius: 8px; padding: 8px;}
            QPushButton:hover {background-color: #0b7dda;}
        """)
        self.save_button.clicked.connect(self.on_save_clicked)
        print(f"{self.log_prefix['ui']} 保存配置按钮创建完成：尺寸120x40，蓝色样式")

        # 执行按钮
        self.execute_button = QPushButton("执行休息计划")
        self.execute_button.setFont(QFont("SimHei", 10))
        self.execute_button.setMinimumHeight(40)
        self.execute_button.setMinimumWidth(150)
        self.execute_button.setStyleSheet("""
            QPushButton {background-color: #4CAF50; color: white; border-radius: 8px; padding: 8px;}
            QPushButton:hover {background-color: #45a049;}
            QPushButton:pressed {background-color: #3d8b40;}
        """)
        self.execute_button.clicked.connect(self.on_execute_clicked)
        print(f"{self.log_prefix['ui']} 执行按钮创建完成：尺寸150x40，绿色样式")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.execute_button)
        main_layout.addLayout(button_layout)
        print(f"{self.log_prefix['ui']} 按钮区域布局完成")

    def init_config_data(self):
        """初始化配置数据"""
        self.config_data = {"min_interval": 5, "max_interval": 30}
        print(
            f"{self.log_prefix['config']} 默认配置：最小间隔{self.config_data['min_interval']}分钟，最大间隔{self.config_data['max_interval']}分钟")

    def getPhotoPath(self):
        pan = os.getcwd().split(':')[0] + ":"
        pic_path = pan + '//yangmao/pic'
        print(f"{self.log_prefix['screenshot']} 计算截图路径：{pic_path}")
        if not os.path.exists(pic_path):
            os.makedirs(pic_path)
            print(f"{self.log_prefix['screenshot']} 截图目录不存在，已创建：{pic_path}")
        else:
            print(f"{self.log_prefix['screenshot']} 截图目录已存在：{pic_path}")
        return pic_path

    def photo(self, auto_clean=True):
        """生成全屏截图，默认自动清理"""
        Ui_file_Name = f"{int(time.time())}_ui.png"
        path = os.path.join(self.getPhotoPath(), Ui_file_Name)
        print(f"{self.log_prefix['screenshot']} 准备生成全屏截图：{path}")
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            print(f"{self.log_prefix['screenshot']} 全屏截图生成成功：{path}")
            if auto_clean:
                self.temp_photo_path = path
                print(f"{self.log_prefix['screenshot']} 已标记为临时文件：{path}")
            return path
        except Exception as e:
            print(f"{self.log_prefix['screenshot']} 全屏截图失败：{str(e)}")
            return None

    def photo_region(self, left, top, width, height, auto_clean=True):
        """生成区域截图，默认自动清理"""
        Ui_file_Name = f"{int(time.time())}_ui.png"
        path = os.path.join(self.getPhotoPath(), Ui_file_Name)
        print(f"{self.log_prefix['screenshot']} 准备生成区域截图：{path}，区域({left},{top},{width},{height})")
        try:
            # 安全校验区域坐标
            screen_width, screen_height = pyautogui.size()
            left = max(0, min(left, screen_width))
            top = max(0, min(top, screen_height))
            width = min(width, screen_width - left)
            height = min(height, screen_height - top)
            print(f"{self.log_prefix['screenshot']} 安全校验后区域：({left},{top},{width},{height})")

            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save(path)
            print(f"{self.log_prefix['screenshot']} 区域截图生成成功：{path}")
            if auto_clean:
                self.temp_region_path = path
                print(f"{self.log_prefix['screenshot']} 已标记为临时文件：{path}")
            return path
        except Exception as e:
            print(f"{self.log_prefix['screenshot']} 区域截图失败：{str(e)}")
            return None

    def clean_temp_files(self):
        """清理所有临时文件"""
        temp_attrs = ['temp_photo_path', 'temp_region_path']
        print(f"{self.log_prefix['screenshot']} 开始清理临时文件，需检查属性：{temp_attrs}")
        for attr in temp_attrs:
            if hasattr(self, attr):
                file_path = getattr(self, attr)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        delattr(self, attr)
                        print(f"{self.log_prefix['screenshot']} 临时文件清理成功：{file_path}")
                    except Exception as e:
                        print(f"{self.log_prefix['screenshot']} 临时文件清理失败：{file_path}，错误：{str(e)}")
                else:
                    delattr(self, attr)
                    print(f"{self.log_prefix['screenshot']} 临时文件不存在，移除属性：{attr}")
            else:
                print(f"{self.log_prefix['screenshot']} 无此临时文件属性：{attr}")

    def safe_click(self, point, desc="未指定按钮"):
        """安全点击（含坐标校验）"""
        print(f"{self.log_prefix['click']} 准备点击：{desc}，原始坐标({point[0]},{point[1]})")
        try:
            screen_width, screen_height = pyautogui.size()
            # 确保坐标在屏幕范围内
            safe_x = max(0, min(point[0], screen_width - 1))
            safe_y = max(0, min(point[1], screen_height - 1))
            print(
                f"{self.log_prefix['click']} 安全校验后坐标：({safe_x},{safe_y})，屏幕尺寸({screen_width},{screen_height})")

            # 缓慢移动避免系统误判
            pyautogui.moveTo(safe_x, safe_y, duration=0.5)
            print(f"{self.log_prefix['click']} 鼠标移动到目标位置完成")
            time.sleep(0.5)

            pyautogui.click()
            print(f"{self.log_prefix['click']} 点击操作完成：{desc}")

            # 点击后移开鼠标
            pyautogui.moveTo(10, 10, duration=0.3)
            print(f"{self.log_prefix['click']} 鼠标移开至安全位置(10,10)")
            return True
        except Exception as e:
            print(f"{self.log_prefix['click']} 点击失败：{desc}，错误：{str(e)}")
            return False

    def on_save_clicked(self):
        """保存配置按钮点击事件处理"""
        print(f"{self.log_prefix['config']} 触发保存配置按钮点击事件")
        try:
            # 获取并验证当前配置的时间
            min_interval_str = self.big_time_input.text()
            max_interval_str = self.small_time_input.text()
            print(f"{self.log_prefix['config']} 当前输入框值：最小间隔={min_interval_str}，最大间隔={max_interval_str}")

            min_interval = int(min_interval_str)
            max_interval = int(max_interval_str)
            print(f"{self.log_prefix['config']} 输入值转换为整数：最小间隔={min_interval}，最大间隔={max_interval}")

            # 验证范围
            if 1 <= min_interval <= 120 and 1 <= max_interval <= 60:
                print(f"{self.log_prefix['config']} 时间范围验证通过：1-120分钟（最小），1-60分钟（最大）")
                # 确保最小值小于等于最大值
                if min_interval <= max_interval:
                    self.config_data["min_interval"] = min_interval
                    self.config_data["max_interval"] = max_interval
                    print(f"{self.log_prefix['config']} 更新配置数据：最小间隔={min_interval}，最大间隔={max_interval}")

                    # 保存到文件
                    save_result = self.save_config()
                    if save_result:
                        QMessageBox.information(self, "保存成功",
                                                f"配置已保存:\n间隔时间 {min_interval} 到 {max_interval} 分钟")
                        print(f"{self.log_prefix['config']} 配置保存成功，弹窗提示用户")
                    else:
                        print(f"{self.log_prefix['config']} 配置保存失败，未弹窗提示")
                else:
                    QMessageBox.warning(self, "输入错误", "最小值不能大于最大值！")
                    print(
                        f"{self.log_prefix['config']} 验证失败：最小值({min_interval}) > 最大值({max_interval})，弹窗提示")
            else:
                QMessageBox.warning(self, "输入错误", "时间输入超出有效范围！")
                print(f"{self.log_prefix['config']} 验证失败：时间超出范围，弹窗提示")

        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的整数时间！")
            print(f"{self.log_prefix['config']} 转换失败：输入值非整数，弹窗提示")

    def on_execute_clicked(self):
        """启动/停止自动化线程"""
        print(
            f"{self.log_prefix['thread']} 触发执行按钮点击事件，当前线程状态：{'运行中' if (self.auto_thread and self.auto_thread.is_alive()) else '未运行'}")
        # 检查线程是否已在运行
        if self.auto_thread is not None and self.auto_thread.is_alive():
            # 停止线程
            print(f"{self.log_prefix['thread']} 线程正在运行，准备停止")
            self.thread_running = False
            # 等待线程结束（最多5秒）
            wait_result = self.auto_thread.join(timeout=5)
            if wait_result is None:
                QMessageBox.information(self, "提示", "自动化任务已正常停止！")
                print(f"{self.log_prefix['thread']} 线程正常停止，弹窗提示用户")
            else:
                QMessageBox.warning(self, "提示", "自动化任务强制停止！")
                print(f"{self.log_prefix['thread']} 线程强制停止，弹窗提示用户")
            self.execute_button.setText("执行休息计划")
            print(f"{self.log_prefix['thread']} 执行按钮文字恢复为：执行休息计划")
            return

        # 启动线程
        print(f"{self.log_prefix['thread']} 线程未运行，准备启动")
        self.thread_running = True
        self.auto_thread = threading.Thread(target=self.control, daemon=True)
        self.auto_thread.start()
        print(f"{self.log_prefix['thread']} 线程启动成功，线程ID：{self.auto_thread.ident}")

        QMessageBox.information(self, "提示", "自动化任务已启动！")
        print(f"{self.log_prefix['thread']} 弹窗提示用户：自动化任务已启动")
        self.execute_button.setText("停止休息计划")
        print(f"{self.log_prefix['thread']} 执行按钮文字改为：停止休息计划")

    def control(self):
        """自动化控制主循环"""
        print(f"{self.log_prefix['control']} 主控制循环启动，线程ID：{threading.get_ident()}")
        loop_count = 0  # 循环计数器，用于日志区分
        while self.thread_running:
            loop_count += 1
            print(f"\n{self.log_prefix['control']} ===== 主循环第{loop_count}轮开始 ======")
            try:
                # 1. 处理关闭全部弹窗
                print(f"{self.log_prefix['control']} 步骤1：处理关闭全部弹窗")
                photo_path = self.photo()
                if not photo_path:
                    print(f"{self.log_prefix['control']} 步骤1失败：全屏截图生成失败，跳过本轮后续步骤")
                    time.sleep(2)
                    continue

                alldata = self.ocr_processor.getAllData(photo_path)
                print(f"{self.log_prefix['ocr']} 步骤1OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
                self.clean_temp_files()

                # 关闭全部按钮处理
                close_all_point = self.ocr_processor.getPoint_by_data(alldata, "关闭全部")
                if close_all_point:
                    print(f"{self.log_prefix['control']} 步骤1找到'关闭全部'按钮，坐标：{close_all_point}")
                    click_result = self.safe_click(close_all_point, "关闭全部弹窗按钮")
                    if click_result:
                        time.sleep(4)
                        print(f"{self.log_prefix['control']} 步骤1点击'关闭全部'后，等待4秒")
                        # 处理确定按钮
                        confirm_photo = self.photo()
                        if confirm_photo:
                            confirm_data = self.ocr_processor.getAllData(confirm_photo)
                            print(
                                f"{self.log_prefix['ocr']} 步骤1确认弹窗OCR结果：共识别到{len(confirm_data) if confirm_data else 0}个文本区域")
                            confirm_point = self.ocr_processor.getPoint_by_data_true(confirm_data, "确定")
                            if confirm_point:
                                print(f"{self.log_prefix['control']} 步骤1找到'确定'按钮，坐标：{confirm_point}")
                                self.safe_click(confirm_point, "关闭弹窗确认按钮")
                            else:
                                print(f"{self.log_prefix['control']} 步骤1未找到'确定'按钮")
                            self.clean_temp_files()
                        else:
                            print(f"{self.log_prefix['control']} 步骤1确认弹窗截图生成失败")
                        time.sleep(4)
                        print(f"{self.log_prefix['control']} 步骤1处理完成，等待4秒")
                    else:
                        print(f"{self.log_prefix['control']} 步骤1点击'关闭全部'按钮失败")
                else:
                    print(f"{self.log_prefix['control']} 步骤1未找到'关闭全部'按钮，跳过此操作")

                # 2. 切换用户
                print(f"{self.log_prefix['control']} 步骤2：切换用户")
                result_switch = self.switch_user()
                if result_switch:
                    print(f"{self.log_prefix['control']} 步骤2切换用户成功，等待8秒")
                    time.sleep(15)
                else:
                    print(f"{self.log_prefix['control']} 步骤2切换用户失败，跳过后续步骤，等待2秒")
                    time.sleep(2)
                    continue

                # 3. 点击下一步/完成
                print(f"{self.log_prefix['control']} 步骤3：点击下一步/完成")
                result_xiayibu = self.xiayibu()
                if result_xiayibu:
                    print(f"{self.log_prefix['control']} 步骤3下一步操作成功，等待8秒")
                    time.sleep(8)
                else:
                    print(f"{self.log_prefix['control']} 步骤3下一步操作失败，跳过后续步骤，等待2秒")
                    time.sleep(2)
                    continue

                # 4. 中间发布步骤
                print(f"{self.log_prefix['control']} 步骤4：中间发布步骤")
                result_inTer_fabu = self.inTer_fabu()
                if result_inTer_fabu:
                    print(f"{self.log_prefix['control']} 步骤4中间发布成功，等待8秒")
                    time.sleep(8)
                else:
                    print(f"{self.log_prefix['control']} 步骤4中间发布失败，跳过后续步骤，等待2秒")
                    time.sleep(2)
                    continue

                # 5. 生成文案
                print(f"{self.log_prefix['control']} 步骤5：生成文案")
                result_shengchengwenan = self.shengchengwenan()
                if result_shengchengwenan:
                    print(f"{self.log_prefix['control']} 步骤5生成文案成功，等待8秒")
                    time.sleep(8)
                else:
                    print(f"{self.log_prefix['control']} 步骤5生成文案失败，跳过后续步骤，等待2秒")
                    time.sleep(2)
                    continue

                # 6. 发布操作
                print(f"{self.log_prefix['control']} 步骤6：执行发布操作")
                publish_result = self.fabu()
                print(f"{self.log_prefix['control']} 步骤6发布操作结果：{'成功' if publish_result else '失败'}")

                # 随机延迟，减轻系统压力
                random_delay = random.randint(2, 5)
                print(f"{self.log_prefix['control']} 本轮操作完成，随机延迟{random_delay}秒")
                time.sleep(random_delay)

            except Exception as e:
                print(f"{self.log_prefix['control']} 主循环异常：{str(e)}，强制清理临时文件，等待3秒")
                self.clean_temp_files()
                time.sleep(3)
            print(f"{self.log_prefix['control']} ===== 主循环第{loop_count}轮结束 ======\n")

        print(f"{self.log_prefix['control']} 主控制循环退出（线程停止标志已设置）")

    def swipe_tuozhuai(self, A_x, A_y, B_x, B_y, desc="未指定拖拽操作"):
        """安全拖拽操作"""
        print(f"{self.log_prefix['drag']} 准备拖拽：{desc}，原始起点({A_x},{A_y})，原始终点({B_x},{B_y})")
        try:
            screen_width, screen_height = pyautogui.size()
            # 校验坐标
            A_x = max(0, min(A_x, screen_width - 1))
            A_y = max(0, min(A_y, screen_height - 1))
            B_x = max(0, min(B_x, screen_width - 1))
            B_y = max(0, min(B_y, screen_height - 1))
            print(
                f"{self.log_prefix['drag']} 安全校验后：起点({A_x},{A_y})，终点({B_x},{B_y})，屏幕尺寸({screen_width},{screen_height})")

            pyautogui.mouseDown(button='left', x=A_x, y=A_y)
            print(f"{self.log_prefix['drag']} 鼠标左键按下，位置：({A_x},{A_y})")

            pyautogui.moveTo(B_x, B_y, duration=1.25)
            print(f"{self.log_prefix['drag']} 鼠标移动到终点，耗时1.25秒")

            pyautogui.mouseUp(button='left', x=B_x, y=B_y)
            print(f"{self.log_prefix['drag']} 鼠标左键松开，位置：({B_x},{B_y})")

            time.sleep(1)
            print(f"{self.log_prefix['drag']} 拖拽操作完成：{desc}，等待1秒")
            return True
        except Exception as e:
            print(f"{self.log_prefix['drag']} 拖拽失败：{desc}，错误：{str(e)}")
            return False

    def extract_number_from_response(self, json_text):
        """从API返回提取数字"""
        print(f"{self.log_prefix['request']} 准备提取数字，原始JSON文本：{json_text[:100]}...")
        try:
            response_dict = json.loads(json_text)
            print(f"{self.log_prefix['request']} JSON解析成功，字典长度：{len(response_dict)}")

            data_value = response_dict.get("data")
            if not data_value:
                print(f"{self.log_prefix['request']} 提取失败：未找到'data'字段或值为空")
                return None
            print(f"{self.log_prefix['request']} 提取到'data'字段值：{data_value}")

            number_str = data_value.split("#")[0]
            print(f"{self.log_prefix['request']} 按'#'分割后取第一部分：{number_str}")

            if number_str.isdigit():
                print(f"{self.log_prefix['request']} 提取结果为有效数字：{number_str}")
                return number_str
            else:
                print(f"{self.log_prefix['request']} 提取失败：{number_str} 不是有效数字")
                return None

        except json.JSONDecodeError as e:
            print(f"{self.log_prefix['request']} 提取失败：JSON解析错误，{str(e)}")
            return None
        except Exception as e:
            print(f"{self.log_prefix['request']} 提取失败：未知错误，{str(e)}")
            return None

    def send_request_with_image(self, img_bin, desc="验证码图片"):
        """发送带图片的请求"""
        url = "http://localhost:8080/runtime/bea62ff1-fdd9-4b41-b01e-6fbd8be3750d/invoke"
        print(f"{self.log_prefix['request']} 准备发送API请求：URL={url}，请求数据类型={desc}，数据大小={len(img_bin)}字节")
        try:
            response = requests.post(url, data=img_bin, timeout=30)
            print(f"{self.log_prefix['request']} API请求发送成功，响应状态码：{response.status_code}")

            response_bytes = response.content
            print(f"{self.log_prefix['request']} 响应字节长度：{len(response_bytes)}字节")

            # 编码转换
            try:
                utf8_text = response_bytes.decode("utf-8")
                print(f"{self.log_prefix['request']} 响应按UTF-8解码成功，文本长度：{len(utf8_text)}字符")
                gb2312_bytes = utf8_text.encode("gb2312", errors="replace")
                result_text = gb2312_bytes.decode("gb2312")
                print(f"{self.log_prefix['request']} 编码转换完成（UTF-8→GB2312），最终文本长度：{len(result_text)}字符")
            except UnicodeDecodeError:
                detected_encoding = chardet.detect(response_bytes)["encoding"] or "gb2312"
                print(f"{self.log_prefix['request']} UTF-8解码失败，chardet检测编码：{detected_encoding}")
                result_text = response_bytes.decode(detected_encoding, errors="replace")
                print(f"{self.log_prefix['request']} 按{detected_encoding}解码完成，文本长度：{len(result_text)}字符")

            # 提取数字
            extracted_num = self.extract_number_from_response(result_text)
            print(f"{self.log_prefix['request']} API请求最终提取结果：{extracted_num}")
            return extracted_num

        except requests.exceptions.RequestException as e:
            print(f"{self.log_prefix['request']} API请求失败：{str(e)}")
            return None

    def yanzheng(self):
        """百度安全验证处理"""
        print(f"\n{self.log_prefix['verify']} ===== 开始百度安全验证流程 ======")
        try:
            # 1. 截图识别验证窗口
            print(f"{self.log_prefix['verify']} 步骤1：截图识别验证窗口")
            photo_path = self.photo()
            if not photo_path:
                print(f"{self.log_prefix['verify']} 步骤1失败：全屏截图生成失败")
                return False

            # 2. OCR找验证窗口坐标
            print(f"{self.log_prefix['verify']} 步骤2：OCR识别'百度安全验证'文本")
            point = self.ocr_processor.getPoint_BY_PaddleOCRJson_true(photo_path, "百度安全验证")
            self.clean_temp_files()

            if not point:
                print(f"{self.log_prefix['verify']} 步骤2失败：未识别到'百度安全验证'文本")
                return False
            print(f"{self.log_prefix['verify']} 步骤2成功：找到验证窗口坐标，({point[0]},{point[1]})")

            # 3. 移动鼠标到验证窗口
            x_t, y_t = point
            pyautogui.moveTo(x_t, y_t, duration=0.5)
            print(f"{self.log_prefix['verify']} 步骤3：鼠标移动到验证窗口，等待3秒")
            time.sleep(3)

            # 4. 截取验证码区域
            print(f"{self.log_prefix['verify']} 步骤4：截取验证码旋转区域")
            region_left = max(0, x_t - 100)
            region_top = max(0, y_t)
            result_p = self.photo_region(region_left, region_top, 500, 600)
            if not result_p:
                print(f"{self.log_prefix['verify']} 步骤4失败：区域截图生成失败")
                return False
            print(f"{self.log_prefix['verify']} 步骤4成功：验证码区域截图路径，{result_p}")

            # 5. 读取图片并发送请求
            print(f"{self.log_prefix['verify']} 步骤5：读取截图并发送API请求")
            with open(result_p, "rb") as f:
                img_bin = f.read()
            print(f"{self.log_prefix['verify']} 步骤5：读取截图完成，数据大小={len(img_bin)}字节")

            response_text = self.send_request_with_image(img_bin, "验证码旋转图片")
            self.clean_temp_files()
            if not response_text or not response_text.isdigit():
                print(f"{self.log_prefix['verify']} 步骤5失败：API返回无效结果，{response_text}")
                return False
            print(f"{self.log_prefix['verify']} 步骤5成功：API返回旋转角度，{response_text}度")

            # 6. 计算拖动距离
            print(f"{self.log_prefix['verify']} 步骤6：计算验证码拖动距离")
            res_t = int(response_text)
            if res_t < 0:
                duresion = (res_t + 360) / 360 * 550
            else:
                duresion = (360 - res_t) / 360 * 550
            duresion = max(0, min(duresion, 550))
            print(f"{self.log_prefix['verify']} 步骤6成功：计算拖动距离，{duresion:.2f}像素（原始角度{res_t}度）")

            # 7. 执行拖拽
            print(f"{self.log_prefix['verify']} 步骤7：执行验证码拖拽操作")
            drag_x = x_t - 27
            drag_y = y_t + 266
            drag_result = self.swipe_tuozhuai(drag_x, drag_y, drag_x + duresion, drag_y, "验证码旋转拖拽")
            if drag_result:
                print(f"{self.log_prefix['verify']} 步骤7成功：拖拽操作完成")
            else:
                print(f"{self.log_prefix['verify']} 步骤7失败：拖拽操作未完成")
                return False

            print(f"{self.log_prefix['verify']} ===== 百度安全验证流程完成 ======\n")
            return True

        except Exception as e:
            print(f"{self.log_prefix['verify']} 验证流程异常：{str(e)}，流程终止\n")
            self.clean_temp_files()
            return False

    def fabu(self):
        """发布操作"""
        print(f"\n{self.log_prefix['publish']} ===== 开始发布流程（最大尝试3次） ======")
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            print(f"{self.log_prefix['publish']} 发布尝试第{attempt}次/{max_attempts}次")
            try:
                # 1. 截图识别发布相关按钮
                print(f"{self.log_prefix['publish']} 步骤1：截图识别发布按钮")
                photo_path = self.photo()
                if not photo_path:
                    print(f"{self.log_prefix['publish']} 步骤1失败：全屏截图生成失败，等待2秒重试")
                    time.sleep(2)
                    continue

                alldata = self.ocr_processor.getAllData(photo_path)
                print(f"{self.log_prefix['ocr']} 步骤1OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
                self.clean_temp_files()

                # 2. 识别各种发布相关按钮
                print(f"{self.log_prefix['publish']} 步骤2：识别关键按钮")
                fabudao_baijiahao = self.ocr_processor.getPoint_by_data(alldata, "发布到百家号")
                fabuzuopin_point = self.ocr_processor.getPoint_by_data(alldata, "请添加后发布视频")
                baiduanquanyanzheng = self.ocr_processor.getPoint_by_data(alldata, "百度安全验证")
                tuwen = self.ocr_processor.getPoint_by_data_true(alldata, "图文")
                fabushipin_fafafa = self.ocr_processor.getPoint_by_data(alldata, "发布视频")
                print(f"{self.log_prefix['publish']} 步骤2识别结果：")
                print(f"  - 发布到百家号：{fabudao_baijiahao if fabudao_baijiahao else '未找到'}")
                print(f"  - 请添加后发布视频：{fabuzuopin_point if fabuzuopin_point else '未找到'}")
                print(f"  - 百度安全验证：{baiduanquanyanzheng if baiduanquanyanzheng else '未找到'}")
                print(f"  - 图文：{tuwen if tuwen else '未找到'}")
                print(f"  - 发布视频：{fabushipin_fafafa if fabushipin_fafafa else '未找到'}")

                # 3. 根据识别结果执行操作
                if fabudao_baijiahao:
                    print(f"{self.log_prefix['publish']} 步骤3：执行'发布到百家号'点击")
                    click_result = self.safe_click(fabudao_baijiahao, "发布到百家号按钮")
                    if click_result:
                        time.sleep(4)
                        print(f"{self.log_prefix['publish']} 步骤3成功：点击完成，等待4秒")
                        print(f"{self.log_prefix['publish']} ===== 发布流程成功（第{attempt}次尝试） ======\n")
                        return True
                    else:
                        print(f"{self.log_prefix['publish']} 步骤3失败：点击'发布到百家号'按钮失败")
                elif fabuzuopin_point:
                    print(f"{self.log_prefix['publish']} 步骤3：执行'添加视频'流程")
                    # 处理添加视频逻辑
                    alldata = self.ocr_processor.getAllData(self.photo())
                    self.clean_temp_files()
                    vision_point = self.ocr_processor.getPoint_by_data(alldata, "视觉中国")
                    if vision_point:
                        print(f"{self.log_prefix['publish']} 步骤3找到'视觉中国'按钮，坐标：{vision_point}")
                        click_result = self.safe_click((vision_point[0], vision_point[1] + 30),
                                                       "视觉中国下方30像素位置")
                        if click_result:
                            time.sleep(4)
                            print(f"{self.log_prefix['publish']} 步骤3点击'视觉中国'后，等待4秒")
                            # 选择视频
                            video_photo = self.photo()
                            if video_photo:
                                video_data = self.ocr_processor.getAllData(video_photo)
                                video_point = self.ocr_processor.getPoint_by_data_true(video_data, "视频")
                                self.clean_temp_files()
                                if video_point:
                                    print(f"{self.log_prefix['publish']} 步骤3找到'视频'按钮，坐标：{video_point}")
                                    click_result = self.safe_click((video_point[0] + 20, video_point[1] + 100),
                                                                   "视频按钮右20下100像素位置")
                                    if click_result:
                                        time.sleep(4)
                                        print(f"{self.log_prefix['publish']} 步骤3点击'视频'后，等待4秒，继续尝试")
                                        continue
                                    else:
                                        print(f"{self.log_prefix['publish']} 步骤3失败：点击'视频'按钮失败")
                                else:
                                    print(f"{self.log_prefix['publish']} 步骤3失败：未找到'视频'按钮")
                            else:
                                print(f"{self.log_prefix['publish']} 步骤3失败：视频选择界面截图失败")
                        else:
                            print(f"{self.log_prefix['publish']} 步骤3失败：点击'视觉中国'按钮失败")
                    else:
                        print(f"{self.log_prefix['publish']} 步骤3失败：未找到'视觉中国'按钮")
                elif baiduanquanyanzheng:
                    print(f"{self.log_prefix['publish']} 步骤3：触发百度安全验证")
                    verify_result = self.yanzheng()
                    if verify_result:
                        print(f"{self.log_prefix['publish']} 步骤3成功：安全验证通过，继续尝试")
                        continue
                    else:
                        print(f"{self.log_prefix['publish']} 步骤3失败：安全验证未通过")
                elif tuwen:
                    print(f"{self.log_prefix['publish']} 步骤3：识别到'图文'，发布流程完成")
                    print(f"{self.log_prefix['publish']} ===== 发布流程成功（第{attempt}次尝试） ======\n")
                    return True
                elif fabushipin_fafafa:
                    print(f"{self.log_prefix['publish']} 步骤3：执行'发布视频'点击")
                    click_result = self.safe_click(fabushipin_fafafa, "发布视频按钮")
                    if click_result:
                        time.sleep(4)
                        print(f"{self.log_prefix['publish']} 步骤3成功：点击完成，等待4秒")
                        print(f"{self.log_prefix['publish']} ===== 发布流程成功（第{attempt}次尝试） ======\n")
                        return True
                    else:
                        print(f"{self.log_prefix['publish']} 步骤3失败：点击'发布视频'按钮失败")

                print(f"{self.log_prefix['publish']} 第{attempt}次尝试未完成发布，等待2秒重试")
                time.sleep(2)
            except Exception as e:
                print(f"{self.log_prefix['publish']} 第{attempt}次尝试异常：{str(e)}，等待2秒重试")
                time.sleep(2)

        print(f"{self.log_prefix['publish']} ===== 发布流程失败（已达最大尝试次数{max_attempts}次） ======\n")
        return False

    def shengchengwenan(self):
        """生成文案操作"""
        print(f"\n{self.log_prefix['gen_text']} ===== 开始生成文案流程 ======")
        try:
            # 1. 点击我的积分
            print(f"{self.log_prefix['gen_text']} 步骤1：点击'我的积分'")
            photo_path = self.photo()
            if not photo_path:
                print(f"{self.log_prefix['gen_text']} 步骤1失败：全屏截图生成失败")
                return False

            alldata = self.ocr_processor.getAllData(photo_path)
            print(f"{self.log_prefix['ocr']} 步骤1OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
            self.clean_temp_files()

            score_point = self.ocr_processor.getPoint_by_data(alldata, "我的积分")
            if not score_point:
                print(f"{self.log_prefix['gen_text']} 步骤1失败：未找到'我的积分'按钮")
                return False
            print(f"{self.log_prefix['gen_text']} 步骤1找到'我的积分'按钮，坐标：{score_point}")

            click_result = self.safe_click(score_point, "我的积分按钮")
            if not click_result:
                print(f"{self.log_prefix['gen_text']} 步骤1失败：点击'我的积分'按钮失败")
                return False
            time.sleep(3)
            print(f"{self.log_prefix['gen_text']} 步骤1成功：点击完成，等待3秒")

            # 2. 点击领取
            print(f"{self.log_prefix['gen_text']} 步骤2：点击'领取'按钮")
            receive_photo = self.photo()
            if receive_photo:
                receive_data = self.ocr_processor.getAllData(receive_photo)
                print(
                    f"{self.log_prefix['ocr']} 步骤2OCR结果：共识别到{len(receive_data) if receive_data else 0}个文本区域")
                receive_point = self.ocr_processor.getPoint_by_data_true(receive_data, "领取")
                if receive_point:
                    print(f"{self.log_prefix['gen_text']} 步骤2找到'领取'按钮，坐标：{receive_point}")
                    self.safe_click(receive_point, "领取按钮")
                    time.sleep(8)
                    print(f"{self.log_prefix['gen_text']} 步骤2点击'领取'后，等待8秒")
                else:
                    print(f"{self.log_prefix['gen_text']} 步骤2未找到'领取'按钮")

                # 关闭弹窗
                print(f"{self.log_prefix['gen_text']} 步骤2：关闭领取弹窗")
                close_result = self.safe_click((score_point[0] - 300, score_point[1]),
                                               "我的积分左300像素位置（弹窗关闭）")
                if close_result:
                    print(f"{self.log_prefix['gen_text']} 步骤2成功：弹窗关闭点击完成")
                else:
                    print(f"{self.log_prefix['gen_text']} 步骤2警告：弹窗关闭点击失败")
                self.clean_temp_files()
                time.sleep(3)
                print(f"{self.log_prefix['gen_text']} 步骤2完成，等待3秒")
            else:
                print(f"{self.log_prefix['gen_text']} 步骤2失败：领取界面截图生成失败")
                return False

            # 3. 滚动操作
            print(f"{self.log_prefix['gen_text']} 步骤3：执行滚动操作")
            scroll_photo = self.photo()
            if scroll_photo:
                scroll_data = self.ocr_processor.getAllData(scroll_photo)
                print(
                    f"{self.log_prefix['ocr']} 步骤3OCR结果：共识别到{len(scroll_data) if scroll_data else 0}个文本区域")
                all_net_point = self.ocr_processor.getPoint_by_data_true(scroll_data, "全网")
                if all_net_point:
                    print(f"{self.log_prefix['gen_text']} 步骤3找到'全网'按钮，坐标：{all_net_point}")
                    # 移动到滚动区域
                    pyautogui.moveTo(all_net_point[0] + 100, all_net_point[1] + 300, duration=0.5)
                    print(
                        f"{self.log_prefix['gen_text']} 步骤3鼠标移动到滚动区域：({all_net_point[0] + 100},{all_net_point[1] + 300})")
                    # 随机滚动
                    swipe_count = random.randint(0, 2)
                    print(f"{self.log_prefix['gen_text']} 步骤3准备滚动{swipe_count}次，每次滚动-300像素")
                    for i in range(swipe_count):
                        pyautogui.scroll(-300)
                        print(f"{self.log_prefix['gen_text']} 步骤3滚动第{i + 1}次完成")
                        time.sleep(1)
                else:
                    print(f"{self.log_prefix['gen_text']} 步骤3未找到'全网'按钮，跳过滚动")
                self.clean_temp_files()
                time.sleep(3)
                print(f"{self.log_prefix['gen_text']} 步骤3完成，等待3秒")
            else:
                print(f"{self.log_prefix['gen_text']} 步骤3失败：滚动界面截图生成失败")
                return False

            # 4. 生成文案
            print(f"{self.log_prefix['gen_text']} 步骤4：点击'生成文案'")
            text_photo = self.photo()
            if text_photo:
                text_data = self.ocr_processor.getAllData(text_photo)
                print(f"{self.log_prefix['ocr']} 步骤4OCR结果：共识别到{len(text_data) if text_data else 0}个文本区域")
                text_point = self.ocr_processor.getPoint_by_data(text_data, "生成文案")
                if not text_point:
                    print(f"{self.log_prefix['gen_text']} 步骤4失败：未找到'生成文案'按钮")
                    return False
                print(f"{self.log_prefix['gen_text']} 步骤4找到'生成文案'按钮，坐标：{text_point}")

                click_result = self.safe_click(text_point, "生成文案按钮")
                if not click_result:
                    print(f"{self.log_prefix['gen_text']} 步骤4失败：点击'生成文案'按钮失败")
                    return False
                self.clean_temp_files()
                time.sleep(8)
                print(f"{self.log_prefix['gen_text']} 步骤4成功：点击完成，等待8秒")
            else:
                print(f"{self.log_prefix['gen_text']} 步骤4失败：生成文案界面截图生成失败")
                return False

            # 5. 一键成片
            print(f"{self.log_prefix['gen_text']} 步骤5：点击'一键成片'")
            film_photo = self.photo()
            if film_photo:
                film_data = self.ocr_processor.getAllData(film_photo)
                print(f"{self.log_prefix['ocr']} 步骤5OCR结果：共识别到{len(film_data) if film_data else 0}个文本区域")
                film_point = self.ocr_processor.getPoint_by_data_true(film_data, "一键成片")
                if not film_point:
                    print(f"{self.log_prefix['gen_text']} 步骤5失败：未找到'一键成片'按钮")
                    return False
                print(f"{self.log_prefix['gen_text']} 步骤5找到'一键成片'按钮，坐标：{film_point}")

                click_result = self.safe_click(film_point, "一键成片按钮")
                if not click_result:
                    print(f"{self.log_prefix['gen_text']} 步骤5失败：点击'一键成片'按钮失败")
                    return False
                self.clean_temp_files()
                time.sleep(8)
                print(f"{self.log_prefix['gen_text']} 步骤5成功：点击完成，等待8秒")
            else:
                print(f"{self.log_prefix['gen_text']} 步骤5失败：一键成片界面截图生成失败")
                return False

            # 6. 检查积分不足
            print(f"{self.log_prefix['gen_text']} 步骤6：检查积分不足提示")
            check_photo = self.photo()
            if check_photo:
                check_data = self.ocr_processor.getAllData(check_photo)
                print(f"{self.log_prefix['ocr']} 步骤6OCR结果：共识别到{len(check_data) if check_data else 0}个文本区域")
                score_lack_point = self.ocr_processor.getPoint_by_data(check_data, "积分不足")
                if score_lack_point:
                    print(f"{self.log_prefix['gen_text']} 步骤6失败：识别到'积分不足'提示")
                    return False
                print(f"{self.log_prefix['gen_text']} 步骤6未找到'积分不足'提示")

                # 处理知道了按钮
                know_point = self.ocr_processor.getPoint_by_data_true(check_data, "知道了")
                if know_point:
                    print(f"{self.log_prefix['gen_text']} 步骤6找到'知道了'按钮，坐标：{know_point}")
                    self.safe_click(know_point, "知道了按钮")
                    print(f"{self.log_prefix['gen_text']} 步骤6点击'知道了'完成")
                else:
                    print(f"{self.log_prefix['gen_text']} 步骤6未找到'知道了'按钮")
                self.clean_temp_files()
                time.sleep(8)
                print(f"{self.log_prefix['gen_text']} 步骤6完成，等待8秒")
            else:
                print(f"{self.log_prefix['gen_text']} 步骤6失败：积分检查界面截图生成失败")
                return False

            # 7. 等待补充完成
            print(f"{self.log_prefix['gen_text']} 步骤7：等待'补充中'完成（最多15次检查）")
            for i in range(15):
                wait_photo = self.photo()
                if wait_photo:
                    wait_data = self.ocr_processor.getAllData(wait_photo)
                    print(
                        f"{self.log_prefix['ocr']} 步骤7第{i + 1}次检查OCR结果：共识别到{len(wait_data) if wait_data else 0}个文本区域")
                    if not self.ocr_processor.getPoint_by_data(wait_data, "补充中"):
                        self.clean_temp_files()
                        print(f"{self.log_prefix['gen_text']} 步骤7成功：第{i + 1}次检查未找到'补充中'，生成完成")
                        print(f"{self.log_prefix['gen_text']} ===== 生成文案流程完成 ======\n")
                        return True
                    print(f"{self.log_prefix['gen_text']} 步骤7第{i + 1}次检查：仍在'补充中'，等待3秒")
                    self.clean_temp_files()
                else:
                    print(f"{self.log_prefix['gen_text']} 步骤7第{i + 1}次检查：截图生成失败，等待3秒")
                time.sleep(3)

            print(f"{self.log_prefix['gen_text']} 步骤7失败：15次检查后仍在'补充中'，超时")
            print(f"{self.log_prefix['gen_text']} ===== 生成文案流程失败 ======\n")
            return False

        except Exception as e:
            print(f"{self.log_prefix['gen_text']} 生成文案流程异常：{str(e)}，流程终止\n")
            self.clean_temp_files()
            return False

    def inTer_fabu(self):
        """中间发布步骤"""
        print(f"\n{self.log_prefix['publish']} ===== 开始中间发布步骤 ======")
        try:
            # 1. 点击发布作品
            print(f"{self.log_prefix['publish']} 步骤1：点击'发布作品'")
            photo_path = self.photo()
            if not photo_path:
                print(f"{self.log_prefix['publish']} 步骤1失败：全屏截图生成失败")
                return False

            alldata = self.ocr_processor.getAllData(photo_path)
            print(f"{self.log_prefix['ocr']} 步骤1OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
            self.clean_temp_files()

            publish_point = self.ocr_processor.getPoint_by_data(alldata, "发布作品")
            if not publish_point:
                print(f"{self.log_prefix['publish']} 步骤1失败：未找到'发布作品'按钮")
                return False
            print(f"{self.log_prefix['publish']} 步骤1找到'发布作品'按钮，坐标：{publish_point}")

            click_result = self.safe_click(publish_point, "发布作品按钮")
            if not click_result:
                print(f"{self.log_prefix['publish']} 步骤1失败：点击'发布作品'按钮失败")
                return False
            time.sleep(3)
            print(f"{self.log_prefix['publish']} 步骤1成功：点击完成，等待3秒")

            # 2. 点击视频
            print(f"{self.log_prefix['publish']} 步骤2：点击'视频'选项")
            video_photo = self.photo()
            if video_photo:
                video_data = self.ocr_processor.getAllData(video_photo)
                print(f"{self.log_prefix['ocr']} 步骤2OCR结果：共识别到{len(video_data) if video_data else 0}个文本区域")
                # 检查账号质量问题
                quality_point = self.ocr_processor.getPoint_by_data(video_data, "账号内容质量不足")
                if quality_point:
                    print(f"{self.log_prefix['publish']} 步骤2失败：识别到'账号内容质量不足'提示")
                    return False
                print(f"{self.log_prefix['publish']} 步骤2未识别到账号质量问题")

                video_point = self.ocr_processor.getPoint_by_data_true(video_data, "视频")
                if not video_point:
                    print(f"{self.log_prefix['publish']} 步骤2失败：未找到'视频'选项")
                    return False
                print(f"{self.log_prefix['publish']} 步骤2找到'视频'选项，坐标：{video_point}")

                click_result = self.safe_click(video_point, "视频选项按钮")
                if not click_result:
                    print(f"{self.log_prefix['publish']} 步骤2失败：点击'视频'选项按钮失败")
                    return False
                self.clean_temp_files()
                time.sleep(8)
                print(f"{self.log_prefix['publish']} 步骤2成功：点击完成，等待8秒")
            else:
                print(f"{self.log_prefix['publish']} 步骤2失败：视频选择界面截图生成失败")
                return False

            # 3. 点击在线创作
            print(f"{self.log_prefix['publish']} 步骤3：点击'在线创作'")
            create_photo = self.photo()
            if create_photo:
                create_data = self.ocr_processor.getAllData(create_photo)
                print(
                    f"{self.log_prefix['ocr']} 步骤3OCR结果：共识别到{len(create_data) if create_data else 0}个文本区域")
                create_point = self.ocr_processor.getPoint_by_data_true(create_data, "在线创作")
                if not create_point:
                    print(f"{self.log_prefix['publish']} 步骤3失败：未找到'在线创作'按钮")
                    return False
                print(f"{self.log_prefix['publish']} 步骤3找到'在线创作'按钮，坐标：{create_point}")

                click_result = self.safe_click(create_point, "在线创作按钮")
                if not click_result:
                    print(f"{self.log_prefix['publish']} 步骤3失败：点击'在线创作'按钮失败")
                    return False
                self.clean_temp_files()
                time.sleep(8)
                print(f"{self.log_prefix['publish']} 步骤3成功：点击完成，等待8秒")
            else:
                print(f"{self.log_prefix['publish']} 步骤3失败：在线创作界面截图生成失败")
                return False

            print(f"{self.log_prefix['publish']} ===== 中间发布步骤完成 ======\n")
            return True

        except Exception as e:
            print(f"{self.log_prefix['publish']} 中间发布步骤异常：{str(e)}，流程终止\n")
            self.clean_temp_files()
            return False

    def xiayibu(self):
        """下一步/完成操作"""
        print(f"\n{self.log_prefix['next_step']} ===== 开始下一步/完成操作（两轮尝试） ======")
        try:
            # 第一轮点击
            print(f"{self.log_prefix['next_step']} 第一轮尝试（最多3次点击）")
            for round1 in range(3):
                print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次点击")
                photo_path = self.photo()
                if not photo_path:
                    print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次失败：截图生成失败，等待2秒")
                    time.sleep(2)
                    continue

                alldata = self.ocr_processor.getAllData(photo_path)
                print(
                    f"{self.log_prefix['ocr']} 第一轮第{round1 + 1}次OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
                self.clean_temp_files()

                # 检查账号封停
                stop_point = self.ocr_processor.getPoint_by_data(alldata, "账号已被封停")
                if stop_point:
                    print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次失败：识别到'账号已被封停'")
                    return False

                # 查找各类按钮
                next_point = self.ocr_processor.getPoint_by_data(alldata, "下一步")
                finish_point = self.ocr_processor.getPoint_by_data_true(alldata, "完成")
                exp_point = self.ocr_processor.getPoint_by_data_true(alldata, "立即体验")
                print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次识别结果：")
                print(f"  - 下一步：{next_point if next_point else '未找到'}")
                print(f"  - 完成：{finish_point if finish_point else '未找到'}")
                print(f"  - 立即体验：{exp_point if exp_point else '未找到'}")

                click_done = False
                if next_point:
                    click_done = self.safe_click(next_point, f"第一轮第{round1 + 1}次-下一步按钮")
                elif finish_point:
                    click_done = self.safe_click(finish_point, f"第一轮第{round1 + 1}次-完成按钮")
                elif exp_point:
                    click_done = self.safe_click(exp_point, f"第一轮第{round1 + 1}次-立即体验按钮")
                else:
                    # 备选点击位置
                    https_point = self.ocr_processor.getPoint_by_data(alldata, "https")
                    if https_point:
                        print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次：使用备选点击位置（https左130像素）")
                        click_done = self.safe_click((https_point[0] - 130, https_point[1]),
                                                     f"第一轮第{round1 + 1}次-备选位置")
                        time.sleep(5)
                        print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次：备选点击完成，等待5秒，进入第二轮")
                        break
                    else:
                        print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次：未找到任何可点击按钮")

                if click_done:
                    print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次：点击完成，等待3秒")
                    time.sleep(3)
                else:
                    print(f"{self.log_prefix['next_step']} 第一轮第{round1 + 1}次：点击失败，等待3秒")
                    time.sleep(3)

            # 第二轮点击
            print(f"\n{self.log_prefix['next_step']} 第二轮尝试（最多3次点击）")
            for round2 in range(3):
                print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次点击")
                photo_path = self.photo()
                if not photo_path:
                    print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次失败：截图生成失败，等待2秒")
                    time.sleep(2)
                    continue

                alldata = self.ocr_processor.getAllData(photo_path)
                print(
                    f"{self.log_prefix['ocr']} 第二轮第{round2 + 1}次OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
                self.clean_temp_files()

                # 查找各类按钮
                next_point = self.ocr_processor.getPoint_by_data_true(alldata, "下一步")
                finish_point = self.ocr_processor.getPoint_by_data_true(alldata, "完成")
                exp_point = self.ocr_processor.getPoint_by_data_true(alldata, "立即体验")
                print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次识别结果：")
                print(f"  - 下一步：{next_point if next_point else '未找到'}")
                print(f"  - 完成：{finish_point if finish_point else '未找到'}")
                print(f"  - 立即体验：{exp_point if exp_point else '未找到'}")

                click_done = False
                if next_point:
                    click_done = self.safe_click(next_point, f"第二轮第{round2 + 1}次-下一步按钮")
                elif finish_point:
                    click_done = self.safe_click(finish_point, f"第二轮第{round2 + 1}次-完成按钮")
                elif exp_point:
                    click_done = self.safe_click(exp_point, f"第二轮第{round2 + 1}次-立即体验按钮")
                else:
                    # 备选点击位置
                    https_point = self.ocr_processor.getPoint_by_data(alldata, "https")
                    if https_point:
                        print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次：使用备选点击位置（https左130像素）")
                        click_done = self.safe_click((https_point[0] - 130, https_point[1]),
                                                     f"第二轮第{round2 + 1}次-备选位置")
                        time.sleep(5)
                        print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次：备选点击完成，操作成功")
                        print(f"{self.log_prefix['next_step']} ===== 下一步/完成操作成功 ======\n")
                        return True
                    else:
                        print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次：未找到任何可点击按钮")

                if click_done:
                    print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次：点击完成，等待3秒")
                    time.sleep(3)
                else:
                    print(f"{self.log_prefix['next_step']} 第二轮第{round2 + 1}次：点击失败，等待3秒")
                    time.sleep(3)

            print(f"{self.log_prefix['next_step']} 两轮尝试完成，未触发备选点击，默认操作成功")
            print(f"{self.log_prefix['next_step']} ===== 下一步/完成操作成功 ======\n")
            return True

        except Exception as e:
            print(f"{self.log_prefix['next_step']} 下一步操作异常：{str(e)}，流程终止\n")
            self.clean_temp_files()
            return False

    def switch_user(self):
        """切换用户操作"""
        print(f"\n{self.log_prefix['switch_user']} ===== 开始切换用户流程 ======")
        try:
            print(f"{self.log_prefix['switch_user']} 步骤1：等待3秒（界面加载）")
            time.sleep(3)

            # 1. 截图识别手机号位置
            print(f"{self.log_prefix['switch_user']} 步骤2：截图识别'手机号等'文本")
            photo_path = self.photo()
            if not photo_path:
                print(f"{self.log_prefix['switch_user']} 步骤2失败：全屏截图生成失败")
                return False

            alldata = self.ocr_processor.getAllData(photo_path)
            print(f"{self.log_prefix['ocr']} 步骤2OCR结果：共识别到{len(alldata) if alldata else 0}个文本区域")
            self.clean_temp_files()

            # 查找手机号等位置
            phone_point = self.ocr_processor.getPoint_by_data(alldata, "手机号等")
            if not phone_point:
                print(f"{self.log_prefix['switch_user']} 步骤2失败：未找到'手机号等'文本")
                return False
            print(f"{self.log_prefix['switch_user']} 步骤2成功：找到'手机号等'坐标，({phone_point[0]},{phone_point[1]})")

            # 2. 获取用户列表
            print(f"{self.log_prefix['switch_user']} 步骤3：获取用户列表（OCR小区域识别）")
            points_user = self.ocr_processor.getPointsAndTexts_by_data_from_small_area(
                alldata, "登录", 0, phone_point[0] + 100, phone_point[1], 99999
            )
            print(
                f"{self.log_prefix['switch_user']} 步骤3识别结果：共找到{len(points_user) if points_user else 0}个含'登录'的文本区域")

            # 3. 查找未点击的用户
            print(f"{self.log_prefix['switch_user']} 步骤4：筛选未点击的用户")
            point_yinggai = None
            target_xunhao = None
            for point_user in points_user:
                point_user_str = str(point_user)
                if "登录" in point_user_str:
                    # 提取序号（登录后3位）
                    xunhao = point_user_str.split("登录")[1][:3]
                    print(f"  - 检查用户：文本={point_user_str}，序号={xunhao}，已点击={xunhao in self.clicked_user}")
                    if xunhao not in self.clicked_user:
                        point_yinggai = points_user[point_user]
                        target_xunhao = xunhao
                        self.clicked_user.append(xunhao)
                        break

            if point_yinggai:
                print(
                    f"{self.log_prefix['switch_user']} 步骤4成功：找到未点击用户，序号={target_xunhao}，坐标={point_yinggai}")
                # 3. 安全点击用户
                print(f"{self.log_prefix['switch_user']} 步骤5：点击目标用户")
                click_result = self.safe_click(point_yinggai, f"未点击用户（序号{target_xunhao}）")
                if not click_result:
                    print(f"{self.log_prefix['switch_user']} 步骤5失败：点击目标用户失败")
                    # 移除已添加的序号（点击失败，下次仍可尝试）
                    self.clicked_user.remove(target_xunhao)
                    return False
                time.sleep(2)
                print(f"{self.log_prefix['switch_user']} 步骤5成功：点击完成，等待2秒")
                print(f"{self.log_prefix['switch_user']} ===== 切换用户流程成功 ======\n")
                return True
            else:
                print(f"{self.log_prefix['switch_user']} 步骤4失败：未找到未点击的用户，执行滚动")
                # 滚动查找更多用户
                screen_width, screen_height = pyautogui.size()
                safe_x = max(0, min(phone_point[0], screen_width - 1))
                safe_y = max(0, min(phone_point[1] + 50, screen_height - 1))
                pyautogui.moveTo(safe_x, safe_y, duration=0.5)
                print(f"{self.log_prefix['switch_user']} 步骤5：鼠标移动到滚动位置({safe_x},{safe_y})")
                time.sleep(1)
                # 滚动2次即可，避免过度滚动
                for _ in range(1):
                    pyautogui.scroll(-500)
                    time.sleep(1)
                    print(f"{self.log_prefix['switch_user']} 步骤5滚动完成，等待1秒")

                # 重新尝试识别用户
                print(f"{self.log_prefix['switch_user']} 步骤6：滚动后重新识别用户")
                new_photo = self.photo()
                if new_photo:
                    new_data = self.ocr_processor.getAllData(new_photo)
                    print(f"{self.log_prefix['ocr']} 步骤6OCR结果：共识别到{len(new_data) if new_data else 0}个文本区域")
                    new_points_user = self.ocr_processor.getPointsAndTexts_by_data_from_small_area(
                        new_data, "登录", 0, phone_point[0] + 100, phone_point[1], 99999
                    )
                    print(
                        f"{self.log_prefix['switch_user']} 步骤6新识别结果：共找到{len(new_points_user) if new_points_user else 0}个含'登录'的文本区域")

                    # 再次查找未点击用户
                    for point_user in new_points_user:
                        point_user_str = str(point_user)
                        if "登录" in point_user_str:
                            xunhao = point_user_str.split("登录")[1][:3]
                            print(
                                f"  - 检查新用户：文本={point_user_str}，序号={xunhao}，已点击={xunhao in self.clicked_user}")
                            if xunhao not in self.clicked_user:
                                point_yinggai = new_points_user[point_user]
                                target_xunhao = xunhao
                                self.clicked_user.append(xunhao)
                                break

                    if point_yinggai:
                        print(
                            f"{self.log_prefix['switch_user']} 步骤6成功：找到未点击用户，序号={target_xunhao}，坐标={point_yinggai}")
                        click_result = self.safe_click(point_yinggai, f"滚动后未点击用户（序号{target_xunhao}）")
                        if not click_result:
                            print(f"{self.log_prefix['switch_user']} 步骤6失败：点击目标用户失败")
                            self.clicked_user.remove(target_xunhao)
                            return False
                        time.sleep(2)
                        print(f"{self.log_prefix['switch_user']} 步骤6成功：点击完成，等待2秒")
                        print(f"{self.log_prefix['switch_user']} ===== 切换用户流程成功 ======\n")
                        return True
                    else:
                        print(f"{self.log_prefix['switch_user']} 步骤6失败：滚动后仍未找到未点击用户")
                else:
                    print(f"{self.log_prefix['switch_user']} 步骤6失败：滚动后截图生成失败")

                # 所有用户都已点击过，重置点击记录
                print(f"{self.log_prefix['switch_user']} 步骤7：所有用户均已点击过，重置点击记录")
                self.clicked_user = []
                print(f"{self.log_prefix['switch_user']} 步骤7：点击记录已重置，尝试点击第一个用户")

                # 尝试点击第一个用户
                if points_user:
                    first_user = next(iter(points_user.keys()))
                    first_user_str = str(first_user)
                    if "登录" in first_user_str:
                        xunhao = first_user_str.split("登录")[1][:3]
                        point_yinggai = points_user[first_user]
                        print(
                            f"{self.log_prefix['switch_user']} 步骤7：选择第一个用户，序号={xunhao}，坐标={point_yinggai}")
                        click_result = self.safe_click(point_yinggai, f"重置后第一个用户（序号{xunhao}）")
                        if click_result:
                            self.clicked_user.append(xunhao)
                            time.sleep(2)
                            print(f"{self.log_prefix['switch_user']} 步骤7成功：点击完成，等待2秒")
                            print(f"{self.log_prefix['switch_user']} ===== 切换用户流程成功 ======\n")
                            return True
                        else:
                            print(f"{self.log_prefix['switch_user']} 步骤7失败：点击第一个用户失败")
                    else:
                        print(f"{self.log_prefix['switch_user']} 步骤7失败：第一个用户不含'登录'文本")
                else:
                    print(f"{self.log_prefix['switch_user']} 步骤7失败：无用户列表可操作")

            print(f"{self.log_prefix['switch_user']} ===== 切换用户流程失败 ======\n")
            return False

        except Exception as e:
            print(f"{self.log_prefix['switch_user']} 切换用户流程异常：{str(e)}，流程终止\n")
            self.clean_temp_files()
            return False

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
            print(f"{self.log_prefix['config']} 配置已保存到文件：{self.config_file}")
            return True
        except Exception as e:
            print(f"{self.log_prefix['config']} 保存配置失败：{str(e)}")
            return False

    def load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                # 更新UI
                self.big_time_input.setText(str(self.config_data.get('min_interval', 5)))
                self.small_time_input.setText(str(self.config_data.get('max_interval', 30)))
                print(f"{self.log_prefix['config']} 从文件加载配置：{self.config_data}")
                return True
            except Exception as e:
                print(f"{self.log_prefix['config']} 加载配置失败：{str(e)}")
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RestTimeConfigurator()
    window.show()
    sys.exit(app.exec())
