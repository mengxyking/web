import threading
import time
import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from platform import system
from urllib import request
from util.paddleOCR_json_duixiang import OCRProcessor
import os
import time
import pyautogui
import pyperclip
pyautogui.FAILSAFE=False
import subprocess
import json
import ctypes
alldata = ""
def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    print("00000000000000000000000000---------")
    print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
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
def photo():
    Ui_file_Name =  str(int(time.time())) + "_ui.png"
    path = getPhotoPath()+"/"+Ui_file_Name
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path
ocr_processor = OCRProcessor()
print("开始。。。。。。。。。。。。")
def toast(tishi):
    print()
    #ctypes.windll.user32.MessageBoxTimeoutW(0, f'{tishi}\n', '提示', win32con.MB_YESNO, 0, 1500)
def click_locxy(dr, x, y, left_click=True):
  '''
  dr:浏览器
  x:页面x坐标
  y:页面y坐标
  left_click:True为鼠标左键点击，否则为右键点击
  '''
  if left_click:
    ActionChains(dr).move_by_offset(x, y).click().perform()
  else:
    ActionChains(dr).move_by_offset(x, y).context_click().perform()
  ActionChains(dr).move_by_offset(-x, -y).perform() # 将鼠标位置恢复到移动前

def inter(path,monidizhi,ex):
    alldata = ""
    subprocess.run(['taskkill', '/F', '/IM', 'Firefox.exe'])
    time.sleep(4)
    options = Options()
    # options.add_argument('-headless')
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    gecko_driver_path = './geckodriver.exe'
    options._binary_location = path
    # 固定搭配直接用就行了
    service = Service(executable_path=gecko_driver_path)
    driver = webdriver.Firefox(options=options, service=service)
    driver.get(monidizhi)  # 替换为你要打开的网页链接
    # 定位到包含文案的元素
    time.sleep(15)
    while (True):
        try:
            yue = driver.find_element(By.ID, "result_balls")
            print("正常进入了")
            print(yue)
            toast("正常进入了")
            break
        except:
            print("还不在啊")
            toast("等待进入并且登录")
        time.sleep(5)
    while(True):
        try:
            yue = driver.find_element(By.XPATH, "/html/body/div[15]/div/div[1]/button")
            #baijiale.click()
            #time.sleep(10)
            yue.click()
            print("正常进入了")
            print(yue)
            toast("正常进入了")
            break
        except:
            print("还不在啊")
            toast("等待进入并且登录")
        try:
            yue = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/div[6]/ul/li[4]/div/a/span")
            #baijiale.click()
            #time.sleep(10)
            yue.click()
            print("正常进入了")
            print(yue)
            toast("正常进入了")
            break
        except:
            print("还不在啊")
            toast("等待进入并且登录")

        time.sleep(5)

    try:
        yue = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/div[6]/ul/li[4]/div/a/span")
        #baijiale.click()
        #time.sleep(10)
        yue.click()
        print("正常进入了")
        print(yue)
        toast("正常进入了")
    except:
        print("还不在啊")
        toast("等待进入并且登录")
    time.sleep(3)
    while (True):
        photo_path = photo()
        alldata = ocr_processor.getAllData_test(photo_path)
        if ((str(alldata).count("距离开奖") > 0) & (str(alldata).count("冠军") > 0)):
            print("等到了啊。。。。。。。,当前数据正确")
            break
        time.sleep(3)
    wait_for_start()

    return alldata,driver
# touzhu = [1,3,4,8,16,32,64]
# touzhu_flag = "xiao"
# mingci_flag = "冠军"
def count_leading_zeros(arr):
    count = 0
    for num in arr:
        if num == 0:
            count += 1
        else:
            break
    return count

#print(count_leading_zeros(touzhu))  # 输出: 2
def judge_numbers(arr, criterion):
    if criterion == "dan":
        return all(num % 2 != 0 for num in arr)
    elif criterion == "shuang":
        return all(num % 2 == 0 for num in arr)
    elif criterion == "da":
        return all(num > 5 for num in arr)
    elif criterion == "xiao":
        return all(num <= 5 for num in arr)
    else:
        return False

lock = threading.Lock()
def tz_tz(alldata,driver,mingci_flag,touzhu_flag,jine):
    with lock:
        result_touzhu = dianjitouzhu(alldata, str(mingci_flag), str(touzhu_flag), int(jine))
        print("result_touzhu", result_touzhu)
        if (result_touzhu == "1"):
            fanhuishouye = ocr_processor.getPoint_by_data(alldata, "确定")
            print("fanhuishouye:", fanhuishouye)
            if (fanhuishouye != None):
                pyautogui.moveTo(x=fanhuishouye[0] - 25, y=fanhuishouye[1])
                time.sleep(1.5)
                pyautogui.click()
                time.sleep(0.1)

                while(True):
                    try:
                        time.sleep(1.5)
                        # yue = driver.find_element(By.XPATH, "/html/body/div[24]/div[3]/div/button[1]")
                        # # baijiale.click()
                        # # time.sleep(10)
                        # yue.click()
                        # print("正常进入了")
                        # print(yue)

                        pyautogui.press('enter')

                        time.sleep(1)
                        break

                    except:
                        print("e没找到tz弹窗的确定按钮")
                        time.sleep(1)
                # if (zongjie == "0"):
                #     photo_path = photo()
                #     alldata111 = ocr_processor.getAllData_test(photo_path)
                #     fanhuishouye = ocr_processor.getPoint_by_data(alldata111, "总金额")
                #     print("fanhuishouye22222222222222:", fanhuishouye)
                #     if (fanhuishouye != None):
                #         pyautogui.moveTo(x=fanhuishouye[0] - 100, y=fanhuishouye[1] + 53)
                #         updata_pkl("zongjine", str(fanhuishouye[0] - 100) + "_" + str(fanhuishouye[1] + 53))
                #         time.sleep(0.5)
                #         pyautogui.click()
                #         time.sleep(1)
                # else:
                #     zongjie = get_value_by_key_pkl("zongjine")
                #     pyautogui.moveTo(float(str(zongjie).split("_")[0]), float(str(zongjie).split("_")[1]))
                #     time.sleep(0.5)
                #     pyautogui.click()
                #     time.sleep(1)
                #     # time.sleep(5)


def jianshuo(alldata,driver,touzhu,mingci_flag,touzhu_flag,jiekoudizhi,ex):
    start_mingci_flag = 0
    diyici_flag = 0
    shunxu_flag = 0
    touzhu_flag = str(touzhu_flag)
    mingci_flag = str(mingci_flag)
    #mingci_flag_shuzi = 1

    mingcishuzu = mingci_flag.split(",")
    mingcishuzu_index = 0

    # if(ex.button.text() == "开始"):
    #     print("结束了。。。。")
    #     return
    print("mingcishuzu------------->",mingcishuzu,mingcishuzu[0])

    print("------------------>",int(mingcishuzu[0]) == 5)
    if(int(mingcishuzu[0])  == 1):
        #mingci_flag_shuzi =1
        start_mingci_flag = 1
    if (int(mingcishuzu[0])  == 2):
        #mingci_flag_shuzi = 2
        start_mingci_flag = 2
    if (int(mingcishuzu[0])  == 3):
        #mingci_flag_shuzi = 3
        start_mingci_flag = 3
    if (int(mingcishuzu[0])  == 4):
        #mingci_flag_shuzi = 4
        start_mingci_flag = 4
    if (int(mingcishuzu[0])  == 5):
        #mingci_flag_shuzi = 5
        start_mingci_flag = 5
    if (int(mingcishuzu[0])  == 6):
        #mingci_flag_shuzi = 6
        start_mingci_flag = 6
    if (int(mingcishuzu[0])  == 7):
        #mingci_flag_shuzi = 7
        start_mingci_flag = 7
    if (int(mingcishuzu[0])  == 8):
        #mingci_flag_shuzi = 8
        start_mingci_flag = 8
    if (int(mingcishuzu[0])  == 9):
        #mingci_flag_shuzi = 9
        start_mingci_flag = 9
    if (int(mingcishuzu[0])  == 10):
        #mingci_flag_shuzi = 10
        start_mingci_flag = 10
    qishu_flag = 0
    qishu_flag_while = 0

    riqi = 1
    dangqiancixu = 0
    while (True):
            print("开始-------------------------脚本开始--------------------------")
            print("dangqiancixu:",dangqiancixu)
        # try:
            if(len(touzhu) <1):
                print("配置的数据不对")
                return "配置的数据不对"
            time.sleep(0.1)
            if(touzhu[dangqiancixu] == 0):
                print("开始-------------------------等一手--------------------------")
                print("当前需要等一手")
                temp_small = getData_qishu_2(jiekoudizhi)
                print("当前期数是。。。。。。。。。。------------------》",temp_small)
                while (True):
                    time.sleep(8)
                    count_0 = count_leading_zeros(touzhu)
                    temp  = getData_qishu_2(jiekoudizhi)
                    print("temp_small:",temp_small)
                    print("temp:", temp)
                    print("count_0:", count_0)
                    print("当前lao期数是。。。。。。。。。。------------------》", temp_small)
                    print("当前新期数是。。。。。。。。。。------------------》", temp)
                    if(temp_small != temp):
                        print("-------------------------真正开始等一手了啊。。。。----------------------》当前等的是几，等的策略是啥",mingcishuzu[mingcishuzu_index],touzhu_flag)
                        result_2 = getData(count_0, int(mingcishuzu[mingcishuzu_index]),jiekoudizhi)
                        print("result_2:",result_2)
                        dangqiancixu = dangqiancixu
                        print("dangqiancixu---------------"+str(dangqiancixu))
                        if (touzhu_flag == "da"):
                            result_judge = judge_numbers(result_2, "xiao")
                            print("result_judge:",result_judge)
                            if(result_judge == True):
                                dangqiancixu = count_0
                                #mingci_flag_shuzi+=1
                                mingcishuzu_index +=1
                                qishu_flag_while = temp
                                print("等到手了。。。。")
                                break
                        if (touzhu_flag == "xiao"):
                            result_judge = judge_numbers(result_2, "da")
                            print("result_judge:", result_judge)
                            if (result_judge == True):
                                dangqiancixu = count_0
                                #mingci_flag_shuzi += 1
                                qishu_flag_while = temp
                                mingcishuzu_index += 1
                                print("等到手了。。。。")
                                break
                        if (touzhu_flag == "dan"):
                            result_judge = judge_numbers(result_2, "shuang")
                            print("result_judge:", result_judge)
                            if (result_judge == True):
                                dangqiancixu = count_0
                                #mingci_flag_shuzi += 1
                                qishu_flag_while = temp
                                mingcishuzu_index += 1
                                print("等到手了。。。。")
                                break
                        if (touzhu_flag == "shuang"):
                            result_judge = judge_numbers(result_2, "dan")
                            print("result_judge:", result_judge)
                            if (result_judge == True):
                                dangqiancixu = count_0
                                #mingci_flag_shuzi += 1
                                qishu_flag_while = temp
                                mingcishuzu_index += 1
                                print("等到手了。。。。")
                                break
                        #toast("还没有等到手")
                    wait_for_kaijiang()
                    time.sleep(10)

            # if(mingci_flag_shuzi>10):
            #     mingci_flag_shuzi = 1
            if(mingcishuzu_index > len(mingcishuzu)-1):
                mingcishuzu_index = 0
            print("等手之后qishu_flag_while：",qishu_flag_while)
            kaijiangshijian = kaijiang_time()
            print("计算后的开奖时间:", kaijiangshijian)
            if(int(kaijiangshijian)>43):
                print("时间满足 可以开奖")
                #toast("时间满足模拟测试")
                print("获取期数")
                riqi = int(getData_qishu_2(jiekoudizhi))+1
                if((riqi == qishu_flag) or (riqi == qishu_flag_while)):
                    #toast("当前日期不满足")
                    continue
                qishu_flag = riqi
                print("riqi",riqi)
                print("mingci_flag:",mingci_flag)
                print("touzhu_flag:",touzhu_flag)
                dangqiancixu = int(dangqiancixu)
                print("touzhu[dangqiancixu]:",(touzhu[dangqiancixu]))
                #toast("开始模拟:"+",名次:"+str(mingci_flag)+",类型:"+str(touzhu_flag)+",额度:"+str(int(touzhu[dangqiancixu])))

                if(int(mingcishuzu[mingcishuzu_index]) == 1):
                    mingci_flag = "冠军"
                if (int(mingcishuzu[mingcishuzu_index]) == 2):
                    mingci_flag = "亚军"
                if (int(mingcishuzu[mingcishuzu_index])== 3):
                    mingci_flag = "第三名"
                if (int(mingcishuzu[mingcishuzu_index]) == 4):
                    mingci_flag = "第四名"
                if (int(mingcishuzu[mingcishuzu_index]) == 5):
                    mingci_flag = "第五名"
                if (int(mingcishuzu[mingcishuzu_index]) == 6):
                    mingci_flag = "第六名"
                if (int(mingcishuzu[mingcishuzu_index]) == 7):
                    mingci_flag = "第七名"
                if (int(mingcishuzu[mingcishuzu_index]) == 8):
                    mingci_flag = "第八名"
                if (int(mingcishuzu[mingcishuzu_index]) == 9):
                    mingci_flag = "第九名"
                if (int(mingcishuzu[mingcishuzu_index]) == 10):
                    mingci_flag = "第十名"
                print("alldata---------------->",alldata)
                tz_tz(alldata,driver, str(mingci_flag), str(touzhu_flag), int(touzhu[dangqiancixu]))
                result_success = getData_true(riqi, int(mingcishuzu[mingcishuzu_index]), touzhu_flag, jiekoudizhi)
                print("result_success----结果是:", result_success)
                if (result_success == True):
                    print("模拟结果成功，从头开始")
                    #toast("模拟结果成功，从头开始")
                else:
                    print("模拟结果失败，下一个")
                    #mingci_flag_shuzi += 1
                    mingcishuzu_index += 1
                    #toast("模拟结果失败，下一个")
                dangqiancixu += 1
                # if(start_mingci_flag == 1):
                #     mingci_flag_shuzi += 1
                #     mingcishuzu_index += 1
                # else:
                #     if (shunxu_flag == 1):
                #         mingci_flag_shuzi -= 1
                #     else:
                #         mingci_flag_shuzi += 1
                # if (mingci_flag_shuzi > 10):
                #     if (start_mingci_flag == 1):
                #         mingci_flag_shuzi = 1
                #     else:
                #         shunxu_flag = 0
                #         mingci_flag_shuzi = 1
                if(mingcishuzu_index > len(mingcishuzu)-1):
                    mingcishuzu_index = 0
                # if(shunxu_flag == 1):
                #     if(mingci_flag_shuzi <4):
                #         mingci_flag_shuzi = start_mingci_flag
                #         shunxu_flag = 0

                if (result_success == True):
                    dangqiancixu = 0
                    mingci_flag_shuzi = start_mingci_flag
                    mingcishuzu_index = 0
                    print("mingci_flag_shuzi:",mingci_flag_shuzi)
                if (dangqiancixu > len(touzhu) - 1):
                    dangqiancixu = 0
                print("最后报账，，，")
                #print("mingci_flag_shuzi:", mingci_flag_shuzi)
                print("dangqiancixu:",dangqiancixu)
        # except:
        #     print("还不在啊")
        #     toast("还不行啊")
            #time.sleep(5)
def wait_for_kaijiang():
    from datetime import datetime
    import time
    # 目标时间，精确到秒
    target_time_str = '2024-08-17 21:34:15'
    target_time = datetime.strptime(target_time_str, '%Y-%m-%d %H:%M:%S')
    # 初始化一个很小的等待时间，以便循环能够运行
    # 注意：在实际应用中，你可能不需要这个等待时间，因为这会导致不必要的延迟
    # 但为了演示目的，我们保留它
    wait_time = 0.3  # 秒
    # 开始循环
    while True:
        # 获取当前时间，精确到秒
        current_time = datetime.now()

        # 计算时间差，得到timedelta对象
        time_difference = current_time - target_time

        # 将timedelta对象转换为秒数
        seconds_difference = int(time_difference.total_seconds())
        print("seconds_difference:", seconds_difference)
        print(seconds_difference % 75)
        # 判断秒数是否可以被75整除（即相差一分十五秒的倍数）
        if seconds_difference % 75 == 0:
            print("当前时间与目标时间相差一分十五秒的倍数。")
            break  # 退出循环
        # 如果没有达到条件，则等待一段时间再检查
        # 注意：这里的等待时间应该足够小，以便能够及时响应时间的变化
        # 但也不能太小，以免消耗过多的CPU资源
        time.sleep(wait_time)
def wait_for_start():
    from datetime import datetime
    import time
    # 目标时间，精确到秒
    target_time_str = '2024-08-17 21:34:15'
    target_time = datetime.strptime(target_time_str, '%Y-%m-%d %H:%M:%S')
    # 初始化一个很小的等待时间，以便循环能够运行
    # 注意：在实际应用中，你可能不需要这个等待时间，因为这会导致不必要的延迟
    # 但为了演示目的，我们保留它
    wait_time = 0.3  # 秒
    # 开始循环
    while True:
        # 获取当前时间，精确到秒
        current_time = datetime.now()

        # 计算时间差，得到timedelta对象
        time_difference = current_time - target_time

        # 将timedelta对象转换为秒数
        seconds_difference = int(time_difference.total_seconds())
        print("seconds_difference:", seconds_difference)
        print(seconds_difference % 75)
        # 判断秒数是否可以被75整除（即相差一分十五秒的倍数）
        if seconds_difference % 75 <15:
            print("等待完成，可以开始了")
            break  # 退出循环
        # 如果没有达到条件，则等待一段时间再检查
        # 注意：这里的等待时间应该足够小，以便能够及时响应时间的变化
        # 但也不能太小，以免消耗过多的CPU资源
        time.sleep(wait_time)
def kaijiang_time():
    from datetime import datetime
    import time
    # 目标时间，精确到秒
    target_time_str = '2024-08-17 21:34:15'
    target_time = datetime.strptime(target_time_str, '%Y-%m-%d %H:%M:%S')
    # 初始化一个很小的等待时间，以便循环能够运行
    # 注意：在实际应用中，你可能不需要这个等待时间，因为这会导致不必要的延迟
    # 但为了演示目的，我们保留它
    wait_time = 0.3  # 秒
    # 开始循环
    # 获取当前时间，精确到秒
    current_time = datetime.now()

    # 计算时间差，得到timedelta对象
    time_difference = current_time - target_time

    # 将timedelta对象转换为秒数
    seconds_difference = int(time_difference.total_seconds())
    print("seconds_difference:", seconds_difference)
    print(seconds_difference % 75)
    print("还有多久开奖，",str(75-seconds_difference % 75))
    # 判断秒数是否可以被75整除（即相差一分十五秒的倍数）
    return 75-seconds_difference % 75

def copy(content_copy):
    pyperclip.copy(content_copy)
    # time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
def dianjitouzhu(alldata,mingci,daxiao,touzhujine):
    print("------------------------")
    if(str(alldata).count(mingci)>0):
        print("有名次了。。。。。")
        fanhuishouye = ocr_processor.getPoint_by_data(alldata,"返回首页")
        guanyada = ocr_processor.getPoint_by_data(alldata, "冠亚大")
        print("guanyada:", guanyada)
        print("mingci:", mingci)
        print(0,int(fanhuishouye[0])+100,int(guanyada[1]),3000)
        guanjun = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt_2(alldata,mingci,0,int(fanhuishouye[0])+100,int(guanyada[1]),3000)
        print("guanjun:",guanjun)
        if(guanjun != None):
            if(daxiao == "da"):
                print("da:", daxiao)
                pyautogui.moveTo(x=guanjun[0]+56, y=guanjun[1]+30)
                time.sleep(1.5)
                pyautogui.click()
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                time.sleep(1.5)
                return "1"
            if (daxiao == "xiao"):
                pyautogui.moveTo(x=guanjun[0] + 56, y=guanjun[1] + 60)
                time.sleep(1.5)
                pyautogui.click()
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                time.sleep(1.5)
                return "1"
            if (daxiao == "dan"):
                pyautogui.moveTo(x=guanjun[0] + 56, y=guanjun[1] + 90)
                time.sleep(1.5)
                pyautogui.click()
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                time.sleep(1.5)
                return "1"
            if (daxiao == "shuang"):
                pyautogui.moveTo(x=guanjun[0] + 56, y=guanjun[1] + 120)
                time.sleep(1.5)
                pyautogui.click()
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                time.sleep(1.5)
                return "1"
        return "0"
import requests
import time
from threading import Lock
lock11 = Lock()
# 缓存变量
cached_data = None
cache_time = 0
def get_jiekou_shuju(jiekoudizhi, retries=3, delay=1):
    global cached_data, cache_time
    current_time = time.time()
     # 检查缓存是否有效
    if cached_data is not None and (current_time - cache_time) < 5:
        print("使用缓存数据")
        return cached_data
    with lock11:  # 确保只有一个线程可以进行请求
        # 再次检查缓存，因为可能有其他线程已经填充了缓存
        if cached_data is not None and (current_time - cache_time) < 5:
            print("使用缓存数据")
            return cached_data
         # 尝试请求数据，最多重试 retries 次
        for attempt in range(retries):
            try:
                response = requests.get(jiekoudizhi)
                # 检查请求是否成功
                if response.status_code == 200:
                    # 获取返回的内容
                    data = response
                    print(f"请求到的新数据: {data}")
                    # 更新缓存
                    cached_data = data
                    cache_time = current_time
                    return data
                else:
                    print(f"请求失败，状态码: {response.status_code}")
            except requests.RequestException as e:
                print(f"请求异常: {e}")
             # 等待一段时间再重试
            time.sleep(delay)
        print("所有重试均失败")
        return None


def getData(count,pos,jiekoudizhi):
    import requests
    result = []
    # 接口的URL
    url = jiekoudizhi
    response = get_jiekou_shuju(jiekoudizhi)
    result111 = []
    # 检查请求是否成功
    if response.status_code == 200:
        # 获取返回的内容
        data = response.text
        small_count = 0
        while(small_count < count):
            result111.append(int(json.loads(data)["result"]["data"][small_count]["preDrawCode"].split(",")[pos-1]))
            small_count += 1
    return result111

def getData_qishu_2(jiekoudizhi):
    import requests
    result = []
    # 接口的URL
    response = get_jiekou_shuju(jiekoudizhi)
    # 检查请求是否成功
    if response.status_code == 200:
        # 获取返回的内容
        data = response.text
        temp = int(json.loads(data)["result"]["data"][0]["preDrawIssue"])
        print(temp)
        return temp
import pickle
def get_value_by_key_pkl(key):
    pklfile = "shuju_jd.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"zongjine": "0"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    aaa = dic.get(key)
    return aaa
def updata_pkl(key,value):
    pklfile = "shuju_jd.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"zongjine": "0"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    dic[key]=value
    with open(pklfile, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)
def getData_true(riqi,pos,flag,jiekoudizhi):
    import requests
    import json
    # 接口的URL
    url = jiekoudizhi
    while(True):
        response = get_jiekou_shuju(jiekoudizhi)
        # 检查请求是否成功
        if response.status_code == 200:
            # 获取返回的内容
            data = response.text
            if(str(data).count(str(riqi))>0):
                temp = int(json.loads(data)["result"]["data"][0]["preDrawCode"].split(",")[pos - 1])
                if (flag == "da"):
                    if(int(temp)>5):
                        return True
                    else:
                        return False
                if (flag == "xiao"):
                    if(int(temp)<6):
                        return True
                    else:
                        return False
                if (flag == "dan"):
                    if(int(temp)%2!=0):
                        return True
                    else:
                        return False
                if (flag == "shuang"):
                    if(int(temp)%2==0):
                        return True
                    else:
                        return False
        print("还没到。。。。")
        wait_for_kaijiang()
        time.sleep(10)
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QScreen


class PersistentNotification(QMainWindow):  # 改为继承自 QMainWindow 以获得标题栏和关闭按钮
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle('模拟测试控制')

        # 初始化UI
        self.initUI()

        # 设置窗口默认展示在桌面的右上角
        self.moveToDesktopCorner()

    def initUI(self):
        # 创建中央小部件和布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 创建暂停/开始按钮
        self.button = QPushButton('暂停', central_widget)
        self.button.clicked.connect(self.toggle_button_state)
        layout.addWidget(self.button)

        # 创建关闭按钮（通常不需要，因为QMainWindow已经有一个）
        # 但如果你想要一个额外的关闭按钮，可以这样做：
        # close_button = QPushButton('关闭', central_widget)
        # close_button.clicked.connect(self.close)  # 连接到窗口的close方法
        # layout.addWidget(close_button)

    def toggle_button_state(self):
        # 切换按钮状态
        if self.button.text() == '暂停':
            self.button.setText('开始')
        else:
            self.button.setText('暂停')

    def moveToDesktopCorner(self):
        # 获取主屏幕的几何信息
        screen = QApplication.primaryScreen()
        screen_geo = screen.geometry()

        # 设置窗口的宽度和高度
        width, height = 300, 100

        # 计算窗口的x和y坐标，使其位于屏幕右上角
        x = screen_geo.width() - width-100
        y = screen_geo.y()+100  # 通常是0，除非你有多个屏幕且主屏幕不是最上面的

        # 设置窗口的位置和大小
        self.setGeometry(x, y, width, height)
def main_gui(path,touzhujine,shuzu,monidizhi,jiekoudizhi):
    # app = QApplication(sys.argv)
    # # 创建窗口实例
    # ex = PersistentNotification()
    # # 显示窗口
    # ex.show()
    # 运行应用
    ex = ""
    print("shuzu----------",shuzu)
    thread111 = threading.Thread(target=main_tz,args=(path,touzhujine,shuzu,monidizhi,jiekoudizhi,ex))
    thread111.start()
    #sys.exit(app.exec_())
#
def main_tz(path,touzhujine,shuzu,monidizhi,jiekoudizhi,ex):
    result_alldata,driver = inter(path,monidizhi,ex)
    if(os.path.isfile("shuju_jd.pkl")):
        os.unlink("shuju_jd.pkl")
    touzhujine = [int(item)  for item in touzhujine.split(',')]
    for temp in shuzu:
        leixing_flag = "da"
        print(touzhujine)
        if (temp["leixing"] == "大"):
            leixing_flag = "da"
        if (temp["leixing"] == "小"):
            print("-------------------xiao")
            leixing_flag = "xiao"
        if (temp["leixing"] == "单"):
            leixing_flag = "dan"
        if (temp["leixing"] == "双"):
            leixing_flag = "shuang"
        if(len(str(result_alldata))>8):
            thread = threading.Thread(target=jianshuo, args=(result_alldata,driver,touzhujine, temp["mingci"], leixing_flag, jiekoudizhi,ex,))
            thread.start()
        #jianshuo(touzhujine, temp["mingci"], leixing_flag, jiekoudizhi)

# photo_path = photo()
# alldata = ocr_processor.getAllData_test(photo_path)
# dianjitouzhu(alldata,"冠军","da",2)
#main_gui()