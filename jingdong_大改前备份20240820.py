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
    import win32con
    import ctypes
    ctypes.windll.user32.MessageBoxTimeoutW(0, f'{tishi}\n', '提示', win32con.MB_YESNO, 0, 1500)
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

from selenium.common.exceptions import NoSuchElementException
def inter(path,monidizhi):
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
def jianshuo(touzhu,mingci_flag,touzhu_flag,jiekoudizhi):
    alldata = ""
    diyici_flag = 0
    while(True):
        kaijiangshijian = 0
        photo_path = photo()
        alldata = ocr_processor.getAllData_test(photo_path)

        if (str(alldata).count("距离开奖") > 0):
            print("alldata:", str(alldata))
            point1 = ocr_processor.getPoint_by_data(alldata, "距离开奖")
            print("point1:", str(point1))
            if (point1 != None):
                jinrishuying = ocr_processor.getText_BY_point_in_alldata(alldata, point1[0] + 63, point1[1])
                print("距离开奖2222:", str(jinrishuying))
                if (jinrishuying != None):
                    aa = str(jinrishuying).split(":")
                    print("aa-------------------:", aa)
                    if (len(aa) >= 3):
                        # if(str(aa[len(aa)-2]).count("距离开奖")>0):
                        if (str(aa[len(aa) - 2]).endswith("01")):
                            kaijiangshijian = 60 + int(aa[len(aa) - 1])
                        else:
                            kaijiangshijian = int(aa[len(aa) - 1])
                    if (len(aa) == 2):
                        if (str(aa[0]) == "01"):
                            kaijiangshijian = 60 + int(aa[1])
                        else:
                            kaijiangshijian = int(aa[1])
        print("计算后的开奖时间:", kaijiangshijian)
        if (int(kaijiangshijian) > 55):
            break
        else:
            toast("还得等待。。。")
            print("还得等待。。。")
        time.sleep(3)

    touzhu_flag = str(touzhu_flag)
    mingci_flag = str(mingci_flag)
    mingci_flag_shuzi = 1
    if(mingci_flag == "冠军"):
        mingci_flag_shuzi =1
    if (mingci_flag == "亚军"):
        mingci_flag_shuzi = 2
    if (mingci_flag == "第三名"):
        mingci_flag_shuzi = 3
    if (mingci_flag == "第四名"):
        mingci_flag_shuzi = 4
    if (mingci_flag == "第五名"):
        mingci_flag_shuzi = 5
    if (mingci_flag == "第六名"):
        mingci_flag_shuzi = 6
    if (mingci_flag == "第七名"):
        mingci_flag_shuzi = 7
    if (mingci_flag == "第八名"):
        mingci_flag_shuzi = 8
    if (mingci_flag == "第九名"):
        mingci_flag_shuzi = 9
    if (mingci_flag == "第十名"):
        mingci_flag_shuzi = 10
    qishu_flag = 0

    qishu_flag_while = 0

    riqi = 1
    dangqiancixu = 0
    while (True):
            print("dangqiancixu:",dangqiancixu)
        # try:
            if(len(touzhu) <1):
                print("配置的数据不对")
                return "配置的数据不对"
            # if(dangqiancixu == 0):
            #     result_count_1 = count_leading_zeros(touzhu)
            #     if(result_count_1>0):
            #         while(True):
            #             result_2 = getData(result_count_1, mingci_flag_shuzi,jiekoudizhi)
            #             dangqiancixu = result_count_1
            #             print("dangqiancixu---------------"+str(dangqiancixu))
            #             if (touzhu_flag == "da"):
            #                 result_judge = judge_numbers(result_2, "xiao")
            #                 if(result_judge == True):
            #                     break
            #             if (touzhu_flag == "xiao"):
            #                 result_judge = judge_numbers(result_2, "da")
            #                 if (result_judge == True):
            #                     break
            #             if (touzhu_flag == "dan"):
            #                 result_judge = judge_numbers(result_2, "shuang")
            #                 if (result_judge == True):
            #                     break
            #             if (touzhu_flag == "shuang"):
            #                 result_judge = judge_numbers(result_2, "dan")
            #                 if (result_judge == True):
            #                     break
            #             toast("还没有等到手")
            #             time.sleep(3)
            #     else:
            #         toast("当前不用等手")
            #         print("当前不用等手")
            time.sleep(0.1)
            #print("开始获取余额")


            # if(str(alldata).count("今日输赢")>0):
            #     point1 = ocr_processor.getPoint_by_data(alldata,"今日输赢")
            #     if(point1 !=None):
            #         jinrishuying = ocr_processor.getText_BY_point_in_alldata(alldata,point1[0]+47,point1[1])
            #         print("今日输赢",jinrishuying)
            if(touzhu[dangqiancixu] == 0):
                print("当前需要等一手")
                temp_small = getData_qishu_2(jiekoudizhi)
                while (True):

                    #print("getData_qishu_2(jiekoudizhi):",getData_qishu_2(jiekoudizhi))
                    #print("qishu_flag_while:",qishu_flag_while)
                    temp  = getData_qishu_2(jiekoudizhi)
                    print("temp_small:",temp_small)
                    print("temp:", temp)
                    if(temp_small != temp):
                        result_2 = getData(1, mingci_flag_shuzi,jiekoudizhi)
                        print("result_2:",result_2)
                        dangqiancixu = dangqiancixu
                        print("dangqiancixu---------------"+str(dangqiancixu))
                        if (touzhu_flag == "da"):
                            result_judge = judge_numbers(result_2, "xiao")
                            print("result_judge:",result_judge)
                            if(result_judge == True):
                                dangqiancixu+=1
                                mingci_flag_shuzi+=1
                                qishu_flag_while = temp
                                print("等到手了。。。。")
                                break
                        if (touzhu_flag == "xiao"):
                            result_judge = judge_numbers(result_2, "da")
                            print("result_judge:", result_judge)
                            if (result_judge == True):
                                dangqiancixu += 1
                                mingci_flag_shuzi += 1
                                qishu_flag_while = temp
                                print("等到手了。。。。")
                                break
                        if (touzhu_flag == "dan"):
                            result_judge = judge_numbers(result_2, "shuang")
                            print("result_judge:", result_judge)
                            if (result_judge == True):
                                dangqiancixu += 1
                                mingci_flag_shuzi += 1
                                qishu_flag_while = temp
                                print("等到手了。。。。")
                                break
                        if (touzhu_flag == "shuang"):
                            result_judge = judge_numbers(result_2, "dan")
                            print("result_judge:", result_judge)
                            if (result_judge == True):
                                dangqiancixu += 1
                                mingci_flag_shuzi += 1
                                qishu_flag_while = temp
                                print("等到手了。。。。")
                                break
                        toast("还没有等到手")
                    wait_for_kaijiang()
                    time.sleep(5)
            print("等手之后qishu_flag_while：",qishu_flag_while)
            photo_path = photo()
            alldata = ocr_processor.getAllData_test(photo_path)
            if (str(alldata).count("距离开奖") > 0):
                #print("alldata:",str(alldata))
                point1 = ocr_processor.getPoint_by_data(alldata, "距离开奖")
                print("point1:", str(point1))
                if (point1 != None):
                    jinrishuying = ocr_processor.getText_BY_point_in_alldata(alldata, point1[0] + 63, point1[1])
                    print("距离开奖2222:", str(jinrishuying))
                    if(jinrishuying != None):
                        aa = str(jinrishuying).split(":")
                        print("aa-------------------:",aa)
                        if(len(aa)>=3):
                            weiba = str(aa[len(aa) - 1])
                            if(weiba.endswith("载入")):
                                weiba = str(aa[len(aa) - 1])[:2]
                            #if(str(aa[len(aa)-2]).count("距离开奖")>0):
                            if (str(aa[len(aa)-2]).endswith("01")):
                                kaijiangshijian = 60 + int(weiba)
                            else:
                                kaijiangshijian = int(aa[len(aa)-1])
                        if(len(aa) == 2):
                            weiba = str(aa[1])
                            if (weiba.endswith("载入")):
                                weiba = str(aa[len(aa) - 1])[:2]
                            if (str(aa[0]) == "01"):
                                kaijiangshijian = 60 + int(weiba)
                            else:
                                kaijiangshijian = int(weiba)
            print("计算后的开奖时间:", kaijiangshijian)
            if(int(kaijiangshijian)>43):
                print("时间满足 可以开奖")
                toast("时间满足模拟测试")
                print("获取期数")
                if (str(alldata).count("距离开奖") > 0):
                    print("qi")
                    riqi = ocr_processor.getAll_by_small_In_data(alldata,"距离封盘").split("期")[0]
                    print("------里头的日期：",riqi)
                    print("------里头的qishu_flag：", qishu_flag)
                    print("------里头的qishu_flag_while：", qishu_flag_while)
                    if((riqi == qishu_flag) or (riqi == qishu_flag_while)):
                        toast("当前日期不满足")
                        continue
                    qishu_flag = riqi
                print("riqi",riqi)
                print("mingci_flag:",mingci_flag)
                print("touzhu_flag:",touzhu_flag)
                dangqiancixu = int(dangqiancixu)
                print("touzhu[dangqiancixu]:",(touzhu[dangqiancixu]))
                toast("开始模拟:"+",名次:"+str(mingci_flag)+",类型:"+str(touzhu_flag)+",额度:"+str(int(touzhu[dangqiancixu])))

                if(mingci_flag_shuzi == 1):
                    mingci_flag = "冠军"
                if (mingci_flag_shuzi == 2):
                    mingci_flag = "亚军"
                if (mingci_flag_shuzi == 3):
                    mingci_flag = "第三名"
                if (mingci_flag_shuzi == 4):
                    mingci_flag = "第四名"
                if (mingci_flag_shuzi == 5):
                    mingci_flag = "第五名"
                if (mingci_flag_shuzi == 6):
                    mingci_flag = "第六名"
                if (mingci_flag_shuzi == 7):
                    mingci_flag = "第七名"
                if (mingci_flag_shuzi == 8):
                    mingci_flag = "第八名"
                if (mingci_flag_shuzi == 9):
                    mingci_flag = "第九名"
                if (mingci_flag_shuzi == 10):
                    mingci_flag = "第十名"

                result_touzhu = dianjitouzhu(alldata,str(mingci_flag),str(touzhu_flag),int(touzhu[dangqiancixu]))
                print("result_touzhu",result_touzhu)
                if(result_touzhu == "1"):
                    fanhuishouye = ocr_processor.getPoint_by_data(alldata,"确定")
                    print("fanhuishouye:",fanhuishouye)
                    if(fanhuishouye != None):
                        pyautogui.moveTo(x=fanhuishouye[0]-25 , y=fanhuishouye[1])
                        time.sleep(1)
                        pyautogui.click()
                        time.sleep(1.5)
                        zongjie = get_value_by_key_pkl("zongjine")
                        if(zongjie == "0"):
                            photo_path = photo()
                            alldata111 = ocr_processor.getAllData_test(photo_path)
                            fanhuishouye = ocr_processor.getPoint_by_data(alldata111,"总金额")
                            print("fanhuishouye22222222222222:", fanhuishouye)
                            if (fanhuishouye != None):
                                pyautogui.moveTo(x=fanhuishouye[0]-100, y=fanhuishouye[1]+53)
                                updata_pkl("zongjine",str(fanhuishouye[0]-100)+"_"+str(fanhuishouye[1]+53))
                                time.sleep(0.5)
                                pyautogui.click()
                                time.sleep(1)
                                #time.sleep(5)
                                result_success = getData_true(riqi,mingci_flag_shuzi,touzhu_flag,jiekoudizhi)
                                print("result_success----结果是:",result_success)
                                if(result_success==True):
                                    toast("模拟结果成功，从头开始")
                                else:
                                    toast("模拟结果失败，下一个")
                                dangqiancixu+=1
                                mingci_flag_shuzi+=1
                                if(mingci_flag_shuzi>10):
                                    mingci_flag_shuzi = 1
                                if (result_success == True):
                                    dangqiancixu = 0
                                    mingci_flag_shuzi = 1
                                if(dangqiancixu>len(touzhu)-1):
                                    dangqiancixu = 0
                        else:
                            zongjie = get_value_by_key_pkl("zongjine")
                            pyautogui.moveTo(float(str(zongjie).split("_")[0]), float(str(zongjie).split("_")[1]))
                            time.sleep(0.5)
                            pyautogui.click()
                            time.sleep(1)
                            # time.sleep(5)
                            result_success = getData_true(riqi, mingci_flag_shuzi, touzhu_flag, jiekoudizhi)
                            print("result_success----结果是:", result_success)
                            if (result_success == True):
                                toast("模拟结果成功，从头开始")
                            else:
                                toast("模拟结果失败，下一个")
                            dangqiancixu += 1
                            mingci_flag_shuzi += 1
                            if (mingci_flag_shuzi > 10):
                                mingci_flag_shuzi = 1
                            if (result_success == True):
                                dangqiancixu = 0
                                mingci_flag_shuzi =1
                            if (dangqiancixu > len(touzhu) - 1):
                                dangqiancixu = 0
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
        guanjun = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata,mingci,0,int(fanhuishouye[0])+150,int(guanyada[1]),3000)
        print("guanjun:",guanjun)
        if(guanjun != None):
            if(daxiao == "da"):
                print("da:", daxiao)
                pyautogui.moveTo(x=guanjun[0]+56, y=guanjun[1]+30)
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                return "1"
            if (daxiao == "xiao"):
                pyautogui.moveTo(x=guanjun[0] + 56, y=guanjun[1] + 60)
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                return "1"
            if (daxiao == "dan"):
                pyautogui.moveTo(x=guanjun[0] + 56, y=guanjun[1] + 90)
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                return "1"
            if (daxiao == "shuang"):
                pyautogui.moveTo(x=guanjun[0] + 56, y=guanjun[1] + 120)
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                copy(touzhujine)
                return "1"
        return "0"
def getData(count,pos,jiekoudizhi):
    import requests
    result = []
    # 接口的URL
    url = jiekoudizhi
    response = requests.get(url)
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
    response = requests.get(jiekoudizhi)
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
        response = requests.get(url)
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
        time.sleep(5)
def getData_qishu(qishu,count,pos):
    import requests
    result = []
    # 接口的URL
    url = 'https://www.ip5276.com/member/dresult?lottery=PK10JSC'
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": "08062a46822a=78ac11448cf6c4107137c9f9a88fc67993c6ae07; _skin_=blue; defaultSetting=5%2C10%2C20%2C50%2C100%2C200%2C500%2C1000; settingChecked=0; defaultLT=PK10JSC; _ga=GA1.2.243689521.1723263246; _gid=GA1.2.884956751.1723263246; _ga_MX33GN91MD=GS1.2.1723278214.2.1.1723278382.0.0.0; ssid1=5ce08e8528b7c725160ba7b4dc5a3f56; random=5182; token=78ac11448cf6c4107137c9f9a88fc67993c6ae07",
        "Host": "www.ip5276.com",
        "Priority": "u=0, i",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers:Upgrade-Insecure-Requests:1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
        # 添加更多的请求头信息...
    }

    # 发送GET请求
    response = requests.get(url, headers=header)

    # 检查请求是否成功
    if response.status_code == 200:
        # 获取返回的内容
        data = response.text
        # print(data)

        from bs4 import BeautifulSoup

        # 获取HTML页面源代码
        html = data
        # 使用BeautifulSoup解析HTML并提取特定数据
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        data = soup.find_all('td')
        # print(data[0])
        # print(data[2])
        # print(data[20])
        # print(data[22])
        count1 = 0

        while count1< count:
            # print(data[count1 * 20])
            # print(data[count1 * 20+2+pos-1])
            result.append(data[count1 * 20 + 2 + pos - 1].text)
            count1+=1

        # for temp in data:
        #     print(temp)
    else:
        print('请求失败，状态码：', response.status_code)
    return result

#
def main_tz(path,touzhujine,touzhumingci,touzhuleixing,monidizhi,jiekoudizhi):
    inter(path,monidizhi)
    if(os.path.isfile("shuju_jd.pkl")):
        os.unlink("shuju_jd.pkl")
    touzhujine = [int(item)  for item in touzhujine.split(',')]
    leixing_flag = "da"
    print(touzhujine)
    if(touzhuleixing == "大" ):
        leixing_flag = "da"
    if (touzhuleixing == "小"):
        print("-------------------xiao")
        leixing_flag = "xiao"
    if (touzhuleixing == "单"):
        leixing_flag = "dan"
    if (touzhuleixing == "双"):
        leixing_flag = "shuang"
    jianshuo(touzhujine,touzhumingci,leixing_flag,jiekoudizhi)

# photo_path = photo()
# alldata = ocr_processor.getAllData_test(photo_path)
# dianjitouzhu(alldata,"冠军","da",2)
