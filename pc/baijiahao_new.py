import time
import pyautogui
import os
import pyperclip
import pywinauto.mouse as mouse
from util.paddleOCR_json_duixiang import OCRProcessor
file_zhanghao = "zhanghao.txt"
file_mima = "mima.txt"
file_ck_path = "ck.txt"
file_ck_config_path = "ck_config.txt"
file_baijiahao_nick = "nick.txt"
file_baijiahao_video_path = "video.txt"
file_baijiahao_title_path = "title.txt"
file_baijiahao_sleep_time = "sleep_time.txt"
file_zong_time = "zong_time.txt"
 # 杀死notepad.exe进程
ocr_processor = OCRProcessor()
def getFilPath(file_name):

    #file_name = "close_icon"
    # 获取当前脚本所在目录的路径
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)
    # 获取父目录的父目录的路径
    grandparent_directory = os.path.dirname(os.path.dirname(os.path.dirname(parent_directory)))
    # 打印父目录的父目录的路径
    print("父目录的父目录的路径是：", grandparent_directory)

    # 递归搜索文件并返回绝对路径
    def search_file(directory, file_name):
        for root, dirs, files in os.walk(directory):
            if file_name in files:
                return os.path.join(root, file_name)
        return None

    # 查找文件并返回绝对路径
    file_path = search_file(grandparent_directory, file_name)
    # 打印文件的绝对路径
    if file_path:
        print("文件的绝对路径是：", file_path)
        return file_path
    else:
        print("未找到文件。")
def Photo_phone(): #获取当前图片
    n = "phone"
    Ui_file_Name = n + "_" + str(int(time.time())) + "_ui.png"
    #print("adb -s " + n + " shell screencap -p /sdcard/" + Ui_file_Name+"---888888888888888888888888")
    result = os.system("adb " + "" + " shell screencap -p /sdcard/" + Ui_file_Name)
    if result == 0:  # 等于零就代表执行成功了，往下走开始分析xml、
        cmd ="adb " + "" + " pull /sdcard/" + Ui_file_Name + " "+getPhotoPath()
        result_pull_file = os.system(cmd)
        time.sleep(3)
        if result_pull_file == 0:  # 0 代表执行成功
            os.system("adb " + "" + " shell rm /sdcard/" + Ui_file_Name)
        return getPhotoPath()+"/"+Ui_file_Name
def swipe_tuozhuai(A_x,A_y,B_x,B_y):
    import pyautogui
    import time
    # A点和B点的坐标（这里假设的坐标，你需要根据你的屏幕和需要来设置）
    # 可选：移动到A点（如果你知道鼠标当前不在A点）
    pyautogui.mouseDown(button='left', x=A_x, y=A_y)
    # 移动鼠标到B点（同时鼠标左键是按下的）
    pyautogui.moveTo(B_x, B_y, duration=0.25)  # duration参数表示移动所需的时间（秒）

    # 释放鼠标左键
    pyautogui.mouseUp(button='left', x=B_x, y=B_y)

    # 等待一段时间以便你可以看到鼠标移动和拖拽的效果（可选）
    time.sleep(1)


def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    print("00000000000000000000000000---------")
    print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
def photo():
    Ui_file_Name =  str(int(time.time())) + "_ui.png"
    path = getPhotoPath()+"/"+Ui_file_Name
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path
def photo_region(left, top, width, height):
    Ui_file_Name =  str(int(time.time())) + "_ui.png"
    path = getPhotoPath()+"/"+Ui_file_Name
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(path)
    return path

import subprocess
import re
def yanzheng():
    from pc import demo
    print()
    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "百度安全验证")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        print("有打开")
        time.sleep(3)
        print(point[0]-100,point[1],point[0]-100+500,point[1]+600)
        result_p = photo_region(point[0]-100,point[1],500,600)
        print(result_p)
        res_t = int(demo.image_post(result_p))
        print(res_t)
        if(res_t<0):
            duresion = (res_t+360)/360*400
        else:
            duresion = (360 - res_t) / 360 * 400
        print(duresion)

        x = point[0]-27
        y = point[1]+407

        swipe_tuozhuai(x,y,x+duresion,y)



        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
#yanzheng()
#swipe(765,699,850,699)
def get_screen_width_via_adb():
    # ADB命令来获取屏幕信息
    adb_command = ['adb', 'shell', 'wm', 'size']

    # 执行ADB命令并捕获输出
    result = subprocess.run(adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 检查命令是否成功执行
    if result.returncode != 0:
        print(f"Error executing adb command: {result.stderr}")
        return None

        # 解析输出以获取屏幕宽度
    # 假设输出是类似 "Physical size: 1080x2340" 的字符串
    match = re.search(r'Physical size: (\d+)x\d+', result.stdout)
    if match:
        return int(match.group(1))
    else:
        print("Failed to parse screen width from adb output")
        return None

    # 调用函数并打印屏幕宽度




def open_air():

    cmd = "adb shell am start -a android.settings.AIRPLANE_MODE_SETTINGS"
    result = os.system(cmd)
    print(result == 0)
    if (result != 0):
        return "0"
    time.sleep(5)
    w = get_screen_width_via_adb()
    ph = Photo_phone()
    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(ph,"飞行模式")
    if(point != None):
        cmd = "adb shell input tap "+str(w-100)+" "+str(point[1])
        result = os.system(cmd)
        print(result == 0)
        if(result == 0):
            return "1"
    return "0"
def open_PC_exe(path):
    #app_path = r"C:\Program Files\ByteDance\douyin\douyin_launcher.exe"  # 替换为你要打开的应用程序路径
    app_path = str(path).strip()
    print("app_path==="+str(app_path))
    subprocess.Popen(app_path,shell=True)
    time.sleep(3)


def readFileByName(txt):
    file_path = "data.txt"  # 文件路径
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # 按行读取文件内容
            for line in lines:
                if(str(txt) in str(line)):
                    templist = line.split(":")
                    if(len(templist)==2):
                        return templist[1]
                    elif(len(templist)==3):
                        return str(templist[1])+":"+str(templist[2])
    except FileNotFoundError:
     print("文件不存在")
    except IOError:
     print("文件读取错误")




import subprocess

def open_and_bring_to_front(program):
    subprocess.run(program)
    win32gui.EnumWindows(lambda h, p: win32gui.SetForegroundWindow(h), None)

def test():
    # 使用记事本作为示例
    notepad_program = r"C:\Users\Administrator\Desktop\百度CK换设备登录 V1.4版本(1)\百度CK换设备登录 V1.4版本(1).exe"

    #notepad_program = r"C:\Program Files\bitbrowser\比特浏览器.exe"
    #open_and_bring_to_front(notepad_program)

    import pygetwindow as gw

    # Get the handle of the application by its title
    app_title = "宙斯CK登录"
    app_handle = gw.getWindowsWithTitle(app_title)[0]._hWnd

    print("Handle of the application:", app_handle)


    from pywinauto import Desktop, Application

    # Get the handle of the application by its title
    app_title = "百度CK换设备登录 V1.4版本"
    #app_handle = 0x000000  # Replace this with the actual handle value you obtained

    # Create an Application object using the handle
    app = Application().connect(handle=app_handle)

    # Get all the elements under the handle
    app_elements = app.window(handle=app_handle).children()

    print("Elements under the handle of the application:")
    for element in app_elements:
        print(element)

        for subelement in element.children():
            print(subelement)


def print_listview_items(listview):
    for item_index in range(listview.item_count()):
        item_text = listview.get_item(item_index).text()
        print(item_text)
def rightHouse(item):
    import pyautogui
    import time
    # Get the position of the control (you can replace these coordinates with the actual coordinates of the control)
    item_rect = item.rectangle()

    # Calculate the coordinates for right-click based on the item's position
    right_click_x = item_rect.left + (item_rect.width() // 2)
    right_click_y = item_rect.top + (item_rect.height() // 2)
    print(item_rect.left)
    print(item_rect.top)
    print(right_click_x)
    print(right_click_x)

    # Perform a right-click on the item
    mouse.right_click(coords=(right_click_x, right_click_y))

    print("Right-click performed on the first item in the ListView control.")



def fabu():
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "切换")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]-270, y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")

    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "发布")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")

    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "视频")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0] , y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")

    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "点击上传或")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")

    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "文件名")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]+200, y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
    filename= rename_first_video_in_folder(read_txt_file(file_baijiahao_video_path),read_txt_file(file_baijiahao_title_path))
    if(filename == None):
        return
    pyperclip.copy(filename)
    # time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(3)
    point = ocr_processor.getPoint_BY_PaddleOCRJson_back(photo(), "打开")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0] , y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)

        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return

    toast("等待上传视频")
    time.sleep(20)
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "00:00:00")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]-84, y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(20)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return

    pyautogui.scroll(-300)
    time.sleep(1)
    pyautogui.scroll(-300)
    pyautogui.scroll(-300)

    time.sleep(1)
    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "发布")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(20)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return
    return "1"
# def read_txt_file(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             content = file.read()
#         return content
#     except FileNotFoundError:
#         print(f"文件 {file_path} 未找到")
#         return None
def check_connected_android_devices():
    import subprocess
    # 调用adb devices命令并获取输出
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # 如果命令执行失败（例如adb未安装或未找到设备），则返回False
    if result.returncode != 0:
        return False

        # 移除输出中的表头（如果有的话）
    output = result.stdout.strip().split('\n')[1:]

    # 计数连接的设备数量
    device_count = 0
    for line in output:
        # adb devices的输出通常格式是：<设备ID>\t<设备状态>
        # 如果状态是device，则它是一个连接的设备
        if line and 'device' in line.split('\t')[1]:
            device_count += 1

            # 如果有且仅有一个设备连接，则返回True，否则返回False
    return device_count == 1

def read_txt_file(file_path):
    try:
        with open(file_path, 'r') as file:  # 使用'with'语句确保文件正确关闭
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None
def read_txt_file_utf(file_path):
    try:
        with open(file_path, 'r',encoding="utf-8") as file:  # 使用'with'语句确保文件正确关闭
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None
def getHour():
    from datetime import datetime
    # 获取当前时间
    now = datetime.now()
    # 获取当前小时（24小时制）
    current_hour = now.hour
    print(current_hour)
    return current_hour
import random
def main_baijiahao(check_hour):

    print("")
    toast("开始执行脚本")
    subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'])
    subprocess.run(['taskkill', '/F', '/IM', 'javaw.exe'])
    time.sleep(1)
    notepad_program = read_txt_file(file_ck_path)
    open_PC_exe(notepad_program)
    time.sleep(5)
    login_result = login()

    if(login_result != "1"):
        return

    daoru_result = daoru()
    if(daoru_result == "0"):
        return

    list_count = daoru_result.split("\n")
    print("------------------"+str(list_count))
    print("------------------" + str(len(list_count)))
    open_count = 0
    while open_count<len(list_count):
        print("check_hour------")
        print(check_hour)
        if(str(getHour()) in check_hour):
            toast("当前时间满足，开始执行任务")
            print("")
            result_open = open_bro()

            if (result_open == "1"):
                reslt_updateinfo = updateInfo()
                if (reslt_updateinfo == "1"):
                    fabu()

            #设置等待时间
            toast("开始等待")
            sleep_time = str(read_txt_file(file_baijiahao_sleep_time)).split("-")
            random_int = random.randint(int(sleep_time[0]), int(sleep_time[1]))
            print(random_int)
            time.sleep(random_int)
            time.sleep(5)
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'])
            check_result = check_connected_android_devices()
            if (check_result == True):
                open_air()
                time.sleep(5)
                open_air()
                time.sleep(5)
            else:
                return "0"
            point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "删除选中行")
            if (point != None):
                print(point)
                pyautogui.moveTo(x=point[0], y=point[1])
                pyautogui.click()
                print("有打开")
                time.sleep(3)
                # 如果有的话 需要全部删除
            else:
                print("没有浏览器")
            open_count += 1
        else:
            toast("当前时间不满足，等待中")
            print("当前时间不满足，等待中")
            time.sleep(30)

def open_bro():
    time.sleep(3)
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "编号")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]-77, y=point[1]+37)
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return "0"

    time.sleep(1)
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "开始CK登录")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0] , y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return "0"

    return "1"
def updateInfo():
    time.sleep(10)

    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "立即参与")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1]+156)
        pyautogui.click()
        print("有打开")
        time.sleep(3)

    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "忽略")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        print("忽略")
        time.sleep(3)

    info_file_path = read_txt_file(file_baijiahao_nick)
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "切换")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0] - 270, y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")

    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "发布")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        #pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return "0"

    point = swipeandsearch("百家号设置")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        time.sleep(16)
    else:
        print("没有百家号设置")

    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "修改资料")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        time.sleep(3)
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return "0"

    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "账号名称")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]+300, y=point[1])
        pyautogui.click()
        time.sleep(3)

        delete_count = 0
        while delete_count < 20:
            pyautogui.press('backspace')
            time.sleep(0.1)
            delete_count+=1
    else:
        print("没有百家号设置")

    account_name = get_and_remove_first_line(info_file_path)
    if(account_name == None):
        return "0"
    copy(account_name)
    time.sleep(2)

    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "提交")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        print("有提交")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有提交")

    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "提交成功")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]+475, y=point[1])
        pyautogui.click()
        print("有提交")
        time.sleep(10)
        # 如果有的话 需要全部删除
    else:
        print("没有提交")

    return "1"


def daoru():
    print()
    ck_file_path = read_txt_file(file_ck_config_path)
    ck_content = read_txt_file(ck_file_path)
    print(ck_content)
    pyperclip.copy(ck_content)
    time.sleep(3)
    point = ocr_processor.getPoint_BY_PaddleOCRJson_back(photo(), "表中无内容")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        mouse.right_click(coords=(int(point[0]), int(point[1])))
        print("有打开")
        pyautogui.moveTo(x=point[0]-100, y=point[1]-100)
        time.sleep(2)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return "0"

    time.sleep(1)
    point = ocr_processor.getPoint_BY_PaddleOCRJson_back(photo(), "从剪贴板导入数据")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        print("有打开")
        time.sleep(3)
        # 如果有的话 需要全部删除
    else:
        print("没有浏览器")
        return "0"

    return ck_content


    # 示例用法

def copy(content_copy):
    pyperclip.copy(content_copy)
    # time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
def login():
    #open_and_bring_to_front(r"C:\Users\Administrator\AppData\Roaming\BitBrowser\Chrome-bin\122\win122.0.9\BitBrowser.exe")
    #account = "谢谢惠顾"
    account = read_txt_file_utf(file_zhanghao)
    secret = read_txt_file_utf(file_mima)
    print("开始百家号")
    time.sleep(1)
    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "账号")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0]+150, y=point[1])
        pyautogui.click()
        print("you浏览器窗口")
        time.sleep(1)
        copy(account)
    else:
        print("meiyou浏览器窗口")
        return "0"
    pyautogui.moveTo(1,1)
    time.sleep(2)
    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "密码")
    if (point != None):
        print("密码")
        print(point)
        pyautogui.moveTo(x=point[0]+150, y=point[1])
        pyautogui.click()
        print("you浏览器窗口")
        time.sleep(1)
        copy(secret)
    else:
        print("meiyou浏览器窗口")
        return "0"

    print("点击登录")
    time.sleep(2)
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "登陆")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        pyautogui.click()
        print("有点急刷新")
        time.sleep(1)
        #pyautogui.moveTo(x=1, y=1)
    else:
        print("没有点击刷新")
        return "0"

    time.sleep(10)
    point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), "编号")
    if (point != None):
        print(point)
        pyautogui.moveTo(x=point[0], y=point[1])
        return "1"
        # pyautogui.moveTo(x=1, y=1)
    else:
        print("没有点击刷新")
        return "0"



def QQPhoto():
    import time
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('alt')
    pyautogui.keyDown('a')
    pyautogui.keyUp('a')
    pyautogui.keyUp('alt')
    pyautogui.keyUp('ctrl')
    time.sleep(1)
    pyautogui.doubleClick(300, 500)
    time.sleep(1)

import win32gui
import win32process
import win32con

def bring_window_to_front(window_title):
   try:
       # 枚举窗口回调函数
       def enum_windows_proc(hwnd, window_title):
           if win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd) == window_title:
               win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 还原窗口
               win32gui.SetForegroundWindow(hwnd)  # 将窗口带到前台
               return False
           return True

       # 枚举所有窗口，找到匹配的窗口
       win32gui.EnumWindows(lambda hwnd, window_title=window_title: enum_windows_proc(hwnd, window_title), window_title)
   except:
       print("崩溃了。。。")

def getFiveLineFromFile(file_temp):
    # 读取txt文件的前五行并排除空白行
    with open(file_temp, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
        first_five_lines = lines[:5]
    # 从文本中删除获取到的行
    with open(file_temp, 'r') as file:
        lines = file.readlines()
    with open(file_temp, 'w') as file:
        for line in lines:
            if line.strip() not in first_five_lines:
                file.write(line)
    return first_five_lines


def get_and_remove_first_line(file_path):
    #try:
        # 以读写模式打开文件
        with open(file_path, 'r+',encoding="utf-8") as file:
            # 读取第一行
            first_line = file.readline().strip()
            # 如果文件不为空且成功读取到第一行
            if first_line:
                # 读取除了第一行之外的所有内容
                remaining_content = file.read()
                # 如果文件不只有一行，则保留第一行后的换行符（如果有的话）
                if '\n' in remaining_content:
                    remaining_content = remaining_content.split('\n', 1)[1]
                    # 将文件指针重新定位到文件开头
                file.seek(0)
                # 写入除了第一行之外的所有内容
                file.write(remaining_content)
                # 截断文件，移除多余的部分
                file.truncate()
                # 返回第一行
                return first_line
            else:
                # 文件为空或没有读取到第一行（可能是一个空文件或只有一个空行）
                return None


def swipeandsearch(key):
    count = 0
    while count<10:
        time.sleep(1)
        pyautogui.scroll(-300)
        time.sleep(2)
        point = ocr_processor.getPoint_BY_PaddleOCRJson(photo(), key)
        if (point != None):
            print(point)
            print("代理IP管理")
            return point
        count += 1
import psutil
def is_process_running(process_name):
    """Check if there is any running process that contains the given name."""
    # Iterate over the all the running process
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False



def toast(tishi):
    import win32con
    import ctypes
    ctypes.windll.user32.MessageBoxTimeoutW(0, f'{tishi}\n', '提示', win32con.MB_YESNO, 0, 3000)


import os
import shutil


def rename_first_video_in_folder(folder_path, config_file_path):
    # 确保文件夹存在
    if not os.path.isdir(folder_path):
        print(f"Error: Folder {folder_path} does not exist.")
        return None

        # 读取配置文件的第一行，并删除它
    try:
        new_name = get_and_remove_first_line(config_file_path)
    except FileNotFoundError:
        print(f"Error: Config file {config_file_path} does not exist.")
        return None

        # 查找文件夹中的第一个视频文件
    video_files = [f for f in os.listdir(folder_path) if
                   any(f.lower().endswith(ext) for ext in ('.mp4', '.avi', '.mov', '.mkv'))]
    if not video_files:
        print("Error: No video files found in the folder.")
        return None
    print("video_files--------")
    print(video_files)

        # 获取第一个视频文件的完整路径
    first_video_path = os.path.join(folder_path, video_files[0])
    print("first_video_path-----")
    print(first_video_path)

    # 获取视频文件的扩展名
    _, ext = os.path.splitext(first_video_path)
    print("ext---------")
    print(ext)

    # 给视频文件重命名
    new_video_path = os.path.join(folder_path, f"{new_name}{ext}")
    os.rename(first_video_path, new_video_path)
    print(f"Renamed video to: {new_video_path}")

    # 创建backup文件夹（如果尚不存在）
    backup_folder = os.path.join(folder_path, 'backup')
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

        # 将重命名后的视频移动到backup文件夹
    backup_video_path = os.path.join(backup_folder, f"{new_name}{ext}")
    shutil.move(new_video_path, backup_video_path)
    print(f"Moved renamed video to: {backup_video_path}")

    # 返回backup文件夹中的视频目录（这里只返回单个文件的路径）
    return backup_video_path

import subprocess


def check_connected_android_devices():
    # 调用adb devices命令并获取输出
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # 如果命令执行失败（例如adb未安装或未找到设备），则返回False
    if result.returncode != 0:
        return False

        # 移除输出中的表头（如果有的话）
    output = result.stdout.strip().split('\n')[1:]

    # 计数连接的设备数量
    device_count = 0
    for line in output:
        # adb devices的输出通常格式是：<设备ID>\t<设备状态>
        # 如果状态是device，则它是一个连接的设备
        if line and 'device' in line.split('\t')[1]:
            device_count += 1

            # 如果有且仅有一个设备连接，则返回True，否则返回False
    return device_count == 1



# 使用方法并打印结果
#print(check_connected_android_devices())

#print(Photo_phone())

# width = get_screen_width_via_adb()
# if width:
#     print(f"Screen width: {width}px")