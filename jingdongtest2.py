from util.paddleOCR_json_duixiang import OCRProcessor
import os
import time
import pyautogui
import pyperclip
# def getPhotoPath():
#     pan = os.getcwd().split(':')[0] + ":"
#     pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
#     print("00000000000000000000000000---------")
#     print(pic_path)
#     if (os.path.exists(pic_path) == False):
#         os.makedirs(pic_path)
#     return pic_path
# def Photo_phone(): #获取当前图片
#     n = "phone"
#     Ui_file_Name = n + "_" + str(int(time.time())) + "_ui.png"
#     #print("adb -s " + n + " shell screencap -p /sdcard/" + Ui_file_Name+"---888888888888888888888888")
#     result = os.system("adb " + "" + " shell screencap -p /sdcard/" + Ui_file_Name)
#     if result == 0:  # 等于零就代表执行成功了，往下走开始分析xml、
#         cmd ="adb " + "" + " pull /sdcard/" + Ui_file_Name + " "+getPhotoPath()
#         result_pull_file = os.system(cmd)
#         time.sleep(3)
#         if result_pull_file == 0:  # 0 代表执行成功
#             os.system("adb " + "" + " shell rm /sdcard/" + Ui_file_Name)
#         return getPhotoPath()+"/"+Ui_file_Name
# def photo():
#     Ui_file_Name =  str(int(time.time())) + "_ui.png"
#     path = getPhotoPath()+"/"+Ui_file_Name
#     screenshot = pyautogui.screenshot()
#     screenshot.save(path)
#     return path
# ocr_processor = OCRProcessor()
# def copy(content_copy):
#     pyperclip.copy(content_copy)
#     # time.sleep(1)
#     pyautogui.hotkey('ctrl', 'v')
# def dianjitouzhu(alldata,mingci,daxiao,touzhujine):
#     print()
#     if(str(alldata).count(mingci)>0):
#         print("alldata:",alldata)
#         fanhuishouye = ocr_processor.getPoint_by_data(alldata,"结果走势")
#         print("fanhuishouye:",fanhuishouye)
#         guanjun = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata,mingci,0,int(fanhuishouye[0]),0,3000)
#         if(guanjun != None):
#             print("有返回首页")
#             if(daxiao == "da"):
#                 pyautogui.moveTo(x=guanjun[0]+80, y=guanjun[1]+43)
#                 print("da",guanjun[0]+80,guanjun[1]+43)
#                 time.sleep(1)
#                 pyautogui.click()
#                 time.sleep(1)
#                 copy(touzhujine)
#                 return "1"
#             if (daxiao == "xiao"):
#                 pyautogui.moveTo(x=guanjun[0] + 80, y=guanjun[1] + 86)
#                 time.sleep(1)
#                 pyautogui.click()
#                 time.sleep(1)
#                 copy(touzhujine)
#                 return "1"
#             if (daxiao == "dan"):
#                 pyautogui.moveTo(x=guanjun[0] + 80, y=guanjun[1] + 125)
#                 time.sleep(1)
#                 pyautogui.click()
#                 time.sleep(1)
#                 copy(touzhujine)
#                 return "1"
#             if (daxiao == "shuang"):
#                 pyautogui.moveTo(x=guanjun[0] + 80, y=guanjun[1] + 171)
#                 time.sleep(1)
#                 pyautogui.click()
#                 time.sleep(1)
#                 copy(touzhujine)
#                 return "1"
#         return "0"
#
#print(ocr_processor.getAllData_test(r"C:\Users\Administrator\Desktop\33333.png"))
#ocr_processor.getText_BY_point_in_alldata(OCRProcessor.getText_BY_point_in_alldata())
# alldata = ocr_processor.getAllData_test(r"C:\Users\Administrator\Desktop\33333.png")
# print(alldata)
# point1 = ocr_processor.getPoint_by_data(alldata,"今日输赢")
# print(point1)
# print(ocr_processor.getText_BY_point_in_alldata(alldata,point1[0]+47,point1[1]))
# photo_path = photo()
# alldata = ocr_processor.getAllData_test(photo_path)
# dianjitouzhu(alldata,"冠军","da",2)


def getData_true(riqi,pos,flag):
    import requests
    import json
    # 接口的URL
    url = 'https://1689628.com/api/pks/getPksHistoryList.do?lotCode=10037'
    while(True):
        response = requests.get(url)
        # 检查请求是否成功
        if response.status_code == 200:
            # 获取返回的内容
            data = response.text
            print(data)

            temp = int(json.loads(data)["result"]["data"][0]["preDrawIssue"])
            print(temp)
            time.sleep(8)
            break

print(getData_true(33274423,1,"da"))