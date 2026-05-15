import threading
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import os
import pyautogui
import pyperclip
pyautogui.FAILSAFE=False
import subprocess
import json

def time_to_seconds(time_str):
    # 分割字符串以获取分钟和秒
    minutes, seconds = map(int, time_str.split(':'))
    # 计算总秒数
    total_seconds = minutes * 60 + seconds
    return total_seconds
def inter(path,monidizhi,ex):
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
            yue = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div/div[1]")
            print("判断是否是澳洲10")
            if(yue.text == "极速赛车"):
                print("正常进入啦啦啦啦啦")
                # driver.switch_to.frame("frame")
                # time.sleep(1)
                # yue = driver.find_element(By.XPATH, '//*[@id="cdClose"]')
                # print("------------------------->",yue.text)
                break
            print("还不在啊")
        except:
            print("还不在啊")
        time.sleep(5)
    time.sleep(3)

    try:#点击十字盘
        yue = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div[4]/a[2]")
        if(yue):
            yue.click()
            time.sleep(3)
    except:
        print("还不在啊")

    driver.switch_to.frame("frame")
    time.sleep(1)
    while(True):
        yue = driver.find_element(By.XPATH, '//*[@id="cdClose"]')
        print("------------------------->", yue.text)
        times = time_to_seconds(yue.text)
        if(int(times)>45):
            break
        time.sleep(1)
        print("还得等啊。。。。。")

    return driver
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

# lock = threading.Lock()
# def tz_tz(alldata,driver,mingci_flag,touzhu_flag,jine):
#     with lock:
#         result_touzhu = dianjitouzhu(alldata, str(mingci_flag), str(touzhu_flag), int(jine))
#         print("result_touzhu", result_touzhu)
#         if (result_touzhu == "1"):
#             fanhuishouye = ocr_processor.getPoint_by_data(alldata, "确定")
#             print("fanhuishouye:", fanhuishouye)
#             if (fanhuishouye != None):
#                 pyautogui.moveTo(x=fanhuishouye[0] - 25, y=fanhuishouye[1])
#                 time.sleep(1.5)
#                 pyautogui.click()
#                 time.sleep(0.1)
#
#                 while(True):
#                     try:
#                         time.sleep(1.5)
#                         # yue = driver.find_element(By.XPATH, "/html/body/div[24]/div[3]/div/button[1]")
#                         # # baijiale.click()
#                         # # time.sleep(10)
#                         # yue.click()
#                         # print("正常进入了")
#                         # print(yue)
#
#                         pyautogui.press('enter')
#
#                         time.sleep(1)
#                         break
#
#                     except:
#                         print("e没找到tz弹窗的确定按钮")
#                         time.sleep(1)
#                 # if (zongjie == "0"):
#                 #     photo_path = photo()
#                 #     alldata111 = ocr_processor.getAllData_test(photo_path)
#                 #     fanhuishouye = ocr_processor.getPoint_by_data(alldata111, "总金额")
#                 #     print("fanhuishouye22222222222222:", fanhuishouye)
#                 #     if (fanhuishouye != None):
#                 #         pyautogui.moveTo(x=fanhuishouye[0] - 100, y=fanhuishouye[1] + 53)
#                 #         updata_pkl("zongjine", str(fanhuishouye[0] - 100) + "_" + str(fanhuishouye[1] + 53))
#                 #         time.sleep(0.5)
#                 #         pyautogui.click()
#                 #         time.sleep(1)
#                 # else:
#                 #     zongjie = get_value_by_key_pkl("zongjine")
#                 #     pyautogui.moveTo(float(str(zongjie).split("_")[0]), float(str(zongjie).split("_")[1]))
#                 #     time.sleep(0.5)
#                 #     pyautogui.click()
#                 #     time.sleep(1)
#                 #     # time.sleep(5)
#
lock = threading.Lock()
thread_count = 0

def jianshuo(driver,touzhujine, saidao,zhuanjia,saidaos_length,genfanzhuanjia):
    zong = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    global thread_count
    jine_count = 0
    while(True):
        #print("saidao,zhuanjia----",saidao,zhuanjia)
        if (touzhujine[jine_count] == 0):
            while(True):
                print("当前需要等一手", touzhujine[jine_count])
                url = "https://1689567.com/api/expertsRecommend/detail.do?lotCode=10037&groupCode=1&type=0" + "&ranking=" + str(
                    saidao) + "&userId=" + str(zhuanjia)

                responses = requests.get(url=url)
                # print("responses.json----------->", responses.json())
                re_json = responses.json()
                codes = re_json["result"]["data"]["head"]["recommendCode"]
                print("codes=", codes)
                code_list = str(codes).split(",")
                print("genfanzhuanjia=", genfanzhuanjia)
                print(genfanzhuanjia == "反专家")
                if (genfanzhuanjia == "反专家"):
                    code_list = [item for item in code_list if item not in zong]

                wait_for_kaijiang()
                time.sleep(2)

                kaijiangjieguo2 = getData(saidao, "https://1689567.com/api/pks/getPksHistoryList.do?lotCode=10037")
                print("str(kaijiangjieguo2) , code_list",str(kaijiangjieguo2) ,code_list)
                if (str(kaijiangjieguo2) in code_list):
                    print("当前等一手失败")
                else:
                    print("当前等一手成功")
                    jine_count += 1
                    break



        while (True):
            yue = driver.find_element(By.XPATH, '//*[@id="cdClose"]')
            print("------------------------->", yue.text)
            times = time_to_seconds(yue.text)
            if (int(times) > 35):
                break
            time.sleep(1)
            print("还得等啊。。。。。")
        ele = '//*[@id="drawNumber"]'
        yue = driver.find_element(By.XPATH, ele)
        print("------------------------->", yue.text)
        qishu = yue.text
        print("qishu----->",qishu)
        time.sleep(5)

        with lock:
            url = "https://1689567.com/api/expertsRecommend/detail.do?lotCode=10037&groupCode=1&type=0" + "&ranking=" + str(
                saidao) + "&userId=" + str(zhuanjia)

            responses = requests.get(url=url)
            #print("responses.json----------->", responses.json())
            re_json = responses.json()
            codes = re_json["result"]["data"]["head"]["recommendCode"]
            print("codes=", codes)

            code_list = str(codes).split(",")

            print("genfanzhuanjia=", genfanzhuanjia)
            print(genfanzhuanjia == "反专家")

            if (genfanzhuanjia == "反专家"):
                code_list = [item for item in zong if item not in code_list]
                print("code_list=", code_list)

            for code in code_list:
                ele = f"/html/body/div/div[2]/div[1]/table[{saidao}]/tbody/tr[{str(int(code) + 1)}]/th/span"

                try:
                    yue = driver.find_element(By.XPATH, ele)
                    if (yue):
                        yue.click()
                    time.sleep(0.2)
                except:
                    print("不在啊。。。")

            try:
                yue11 = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/label[2]/input")
                yue11.send_keys(touzhujine[jine_count])
                time.sleep(0.3)
            except:
                print("不在啊。。。")

            try:
                yue11 = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/input[1]")
                yue11.click()
                time.sleep(1.8)
            except:
                print("不在啊。。。")

            pyautogui.press('enter')
            time.sleep(0.3)
            time.sleep(0.3)
        print("开始等待开奖-----------------rank=",saidao)

        wait_for_kaijiang()

        time.sleep(5)
        url_jiekou = "https://1689567.com/api/pks/getPksHistoryList.do?lotCode=10037"
        pos = int(saidao)
        kaijiangjieguo = getData(pos=pos,jiekoudizhi=url_jiekou)

        if(str(kaijiangjieguo) in code_list):
            print("赢了,rank=",saidao)
            jine_count = 0
        else:
            print("输了,rank=",saidao)
            jine_count += 1
            print("jine_count---------->",jine_count)
        if(jine_count>len(touzhujine)):
            jine_count = 0
        #time.sleep(3)
        print("jine_count=",jine_count)

        print("-----------------终点---------------------------")

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
def getData(pos,jiekoudizhi):
    url = jiekoudizhi
    response = get_jiekou_shuju(url)
    if response.status_code == 200:
        # 获取返回的内容
        data = response.text
        small_count = 0
        #print("data-------------->",data)
        return int(json.loads(data)["result"]["data"][small_count]["preDrawCode"].split(",")[pos-1])

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
        # print("seconds_difference:", seconds_difference)
        # print(seconds_difference % 75)
        # 判断秒数是否可以被75整除（即相差一分十五秒的倍数）
        if seconds_difference % 75 == 0:
            print("当前时间与目标时间相差一分十五秒的倍数。")
            break  # 退出循环
        # 如果没有达到条件，则等待一段时间再检查
        # 注意：这里的等待时间应该足够小，以便能够及时响应时间的变化
        # 但也不能太小，以免消耗过多的CPU资源
        time.sleep(wait_time)
def copy(content_copy):
    pyperclip.copy(content_copy)
    # time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
import requests
import time
from threading import Lock
lock11 = Lock()
# 缓存变量

def main_gui(path,touzhujine,shuzu,monidizhi,jiekoudizhi,zhuanjia,genfanzhuanjia):
    ex = ""
    # path 浏览器路径配置  touzhujine：投注策略配置，shuzu:投注赛道，monidizhi：网址，jiekoudizhi：获取结果的接口地址,zhuanjia：选择的专家
    thread111 = threading.Thread(target=main_tz,args=(path,touzhujine,shuzu,monidizhi,jiekoudizhi,ex,zhuanjia,genfanzhuanjia))
    thread111.start()

def main_tz(path,touzhujine,shuzu,monidizhi,jiekoudizhi,ex,zhuanjia,genfanzhuanjia):
    saidaos = shuzu
    driver = inter(path,monidizhi,ex)
    if(os.path.isfile("shuju_jd.pkl")):
        os.unlink("shuju_jd.pkl")
    touzhujine = [int(item)  for item in touzhujine.split(',')]
    userId = 132
    rank = 1
    if(zhuanjia == "人上人"):
        userId = 132
    if (zhuanjia == "人穷志远"):
        userId = 125
    if (zhuanjia == "罗斯"):
        userId = 140
    if (zhuanjia == "连胜"):
        userId = 130
    if (zhuanjia == "老前辈"):
        userId = 127
    if (zhuanjia == "料事如神"):
        userId = 136
    if (zhuanjia == "能掐会算"):
        userId = 128
    if (zhuanjia == "老前辈"):
        userId = 123

    for saidao in saidaos:

        if(saidao == "第1名"):
            rank = 1
        if (saidao == "第2名"):
            rank = 2
        if (saidao == "第3名"):
            rank = 3
        if (saidao == "第4名"):
            rank = 4
        if (saidao == "第5名"):
            rank = 5
        if (saidao == "第6名"):
            rank = 6
        if (saidao == "第7名"):
            rank = 7
        if (saidao == "第8名"):
            rank = 8
        if (saidao == "第9名"):
            rank = 9
        if (saidao == "第10名"):
            rank = 10

        thread = threading.Thread(target=jianshuo, args=(driver,touzhujine, rank,userId,len(saidaos),genfanzhuanjia))
        thread.start()
    #jianshuo(touzhujine, temp["mingci"], leixing_flag, jiekoudizhi)

# photo_path = photo()
# alldata = ocr_processor.getAllData_test(photo_path)
# dianjitouzhu(alldata,"冠军","da",2)
#main_gui()