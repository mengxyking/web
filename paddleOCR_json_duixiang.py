import re
import threading
import time
from PaddleOCR_json.PPOCR_api import GetOcrApi
import os


class OCRProcessor:
    def __init__(self):
        self.file_path = self.getFilPath()
        self.ocr = GetOcrApi(str(self.file_path))
        # ocr_args = {
        #     "use_gpu": 1,  # 1=启用 GPU，0=禁用 GPU（v2.x 用数字 1/0）
        #     "gpu_id": 0,  # GPU 卡号（多卡时指定，如 1、2）
        #     "limit_side_len": 960,  # 控制显存占用（值越小显存需求越低）
        #     #"lang": "ch"  # 识别语言（中文=ch，英文=en 等）
        # }
        #
        # ocr = GetOcrApi(
        #     exePath=str(self.file_path),  # 必传：exe 文件路径
        #     argument=ocr_args,  # 必传：包含 GPU 配置的参数字典
        #     ipcMode="socket"  # 可选：默认 pipe 模式，稳定优先
        # )

    def getFilPath(self):
        bbb = time.time()
        file_name = "PaddleOCR-json.exe"
        # 获取当前脚本所在目录的路径
        script_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(script_directory)
        # 获取父目录的父目录的路径
        grandparent_directory = os.path.dirname(parent_directory)
        # 打印父目录的父目录的路径
        #print("父目录的父目录的路径是：", grandparent_directory)

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
            #print("000---->"+str(time.time()-bbb))
            return file_path
        else:
            print("未找到文件。")
    # 初始化识别器对象，传入 PaddleOCR_json.exe 的路径

    def getPoint_BY_PaddleOCRJson(self,image,txt):#正常的在图片中获取 文字坐标的方法
        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates

    def getPoint_BY_PaddleOCRJson_GPU(self,image,txt):#正常的在图片中获取 文字坐标的方法



        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates


    def getPoint_BY_PaddleOCRJson_2(self,image,txt,txt2,txt3):#正常的在图片中获取 文字坐标的方法
        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        #print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if((str(text).count(str(txt))>0) & (str(text).count(str(txt2))>0)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates
            if ((str(text).count(str(txt)) > 0) & (str(text).count(str(txt3)) > 0)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates
    def getAllData(self,image):#获取页面所有的数据内容
        abb = time.time()
        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        #print(getObj["data"])
        return getObj["data"]
    def getAreaDataFromAlldataByPoint(self,allData,x1,x2,y1,y2):
        areaData = {}
        for tempData in allData:
            data_onece = {}
            text = tempData['text']
            box = tempData['box']
            x_sum = 0
            y_sum = 0
            for point in box:
                x_sum += point[0]
                y_sum += point[1]
            center_x = x_sum / len(box)
            center_y = y_sum / len(box)
            center_coordinates = (center_x, center_y)


            if((x1<center_x<x2) & (y1<center_y<y2)):
                #print("满足条件"+text)
                #print("坐标" + str(center_coordinates))
                #data_onece[text] = center_coordinates
                areaData[text] = center_coordinates

            #print("text="+text+",point = "+str(center_coordinates))
        return areaData

    #data1 = [{'box': [[173, 9], [304, 9], [304, 43], [173, 43]], 'score': 0.7999534010887146, 'text': '花飞尘'}, {'box': [[394, 9], [468, 9], [468, 45], [394, 45]], 'score': 0.9882611632347107, 'text': '和'}, {'box': [[1006, 12], [1096, 12], [1096, 38], [1006, 38]], 'score': 0.8587890267372131, 'text': '太虚道'}, {'box': [[2171, 9], [2271, 9], [2271, 45], [2171, 45]], 'score': 0.9619035124778748, 'text': '逍遥观'}, {'box': [[2179, 38], [2266, 43], [2264, 79], [2176, 74]], 'score': 0.7568289041519165, 'text': '70,58'}, {'box': [[1240, 48], [1304, 53], [1304, 69], [1240, 65]], 'score': 0.44175148010253906, 'text': '双贴'}, {'box': [[1794, 91], [1859, 86], [1862, 113], [1796, 118]], 'score': 0.9957038760185242, 'text': '福利'}, {'box': [[2052, 91], [2074, 91], [2074, 110], [2052, 110]], 'score': 0.9988712668418884, 'text': '城'}, {'box': [[9, 120], [70, 120], [70, 149], [9, 149]], 'score': 0.8822690844535828, 'text': '109'}, {'box': [[909, 115], [965, 115], [965, 142], [909, 142]], 'score': 0.8543662428855896, 'text': 'NPC'}, {'box': [[58, 221], [129, 221], [129, 260], [58, 260]], 'score': 0.8559197187423706, 'text': '任务'}, {'box': [[234, 219], [312, 219], [312, 267], [234, 267]], 'score': 0.9972033500671387, 'text': '队伍'}, {'box': [[1691, 231], [1720, 231], [1720, 250], [1691, 250]], 'score': 0.7341858148574829, 'text': '医'}, {'box': [[1779, 238], [1808, 238], [1808, 255], [1779, 255]], 'score': 0.9501838684082031, 'text': '席'}, {'box': [[1491, 253], [1591, 253], [1591, 279], [1491, 279]], 'score': 0.9444549083709717, 'text': '杨济时'}, {'box': [[2013, 282], [2059, 282], [2059, 301], [2013, 301]], 'score': 0.54527348279953, 'text': '百麦'}, {'box': [[117, 306], [268, 306], [268, 347], [117, 347]], 'score': 0.9653638601303101, 'text': '妖兽入侵！'}, {'box': [[21, 376], [348, 376], [348, 409], [21, 409]], 'score': 0.8087119460105896, 'text': '[师门]寻物（1/10)完成'}, {'box': [[957, 378], [1028, 378], [1028, 402], [957, 402]], 'score': 0.9417874217033386, 'text': '太虚道'}, {'box': [[14, 414], [221, 419], [221, 460], [14, 455]], 'score': 0.9481481909751892, 'text': '寻找一个红冰'}, {'box': [[2283, 429], [2335, 441], [2327, 467], [2279, 455]], 'score': 0.988801121711731, 'text': '花'}, {'box': [[12, 455], [158, 455], [158, 496], [12, 496]], 'score': 0.9442752003669739, 'text': '红冰(1/1)'}, {'box': [[53, 527], [241, 527], [241, 556], [53, 556]], 'score': 0.9018775224685669, 'text': '图任务（2/20）'}, {'box': [[2249, 544], [2303, 544], [2303, 564], [2249, 564]], 'score': 0.6746803522109985, 'text': '洼机'}, {'box': [[60, 573], [170, 573], [170, 597], [60, 597]], 'score': 0.8460703492164612, 'text': '老板娘友'}, {'box': [[187, 573], [314, 573], [314, 597], [187, 597]], 'score': 0.9324076771736145, 'text': '探得的消'}, {'box': [[160, 614], [214, 614], [214, 631], [160, 631]], 'score': 0.20907534658908844, 'text': '存'}, {'box': [[219, 614], [285, 614], [285, 631], [219, 631]], 'score': 0.8125514984130859, 'text': '杨家'}, {'box': [[2018, 617], [2186, 617], [2186, 658], [2018, 658]], 'score': 0.9682626128196716, 'text': '[师门]寻物'}, {'box': [[60, 643], [151, 643], [151, 667], [60, 667]], 'score': 0.8638050556182861, 'text': '我藏宝'}, {'box': [[163, 648], [214, 648], [214, 658], [163, 658]], 'score': 0.6612260937690735, 'text': '文'}, {'box': [[21, 679], [160, 679], [160, 706], [21, 706]], 'score': 0.7919873595237732, 'text': '翟击蒙（0'}, {'box': [[1913, 703], [2254, 703], [2254, 744], [1913, 744]], 'score': 0.8995679616928101, 'text': '?[料罗湾]道长诉危情'}, {'box': [[533, 805], [677, 805], [677, 838], [533, 838]], 'score': 0.9955618381500244, 'text': '太虚道长'}, {'box': [[336, 855], [2093, 853], [2093, 901], [336, 904]], 'score': 0.9229934215545654, 'text': '上善若水。水善利万物而不争，处众人之所恶，故几于道。居善地，心善渊，与善仁，言善信，正善'}, {'box': [[260, 906], [321, 923], [309, 961], [248, 945]], 'score': 0.9591406583786011, 'text': '治，'}, {'box': [[329, 904], [992, 908], [992, 957], [329, 952]], 'score': 0.9210331439971924, 'text': '事善能，动善时。夫唯不争，故无尤。'}, {'box': [[333, 961], [984, 961], [984, 1002], [333, 1002]], 'score': 0.9487977027893066, 'text': '达到这种不争的境界，可羽化而登仙。'}]

    #print(getAreaDataFromAlldataByPoint(data1,1491,5000,0,5210))
    def getPoint_by_data(self,det,txt):
        for item in det:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates
    def getPoint_text_by_data(self,det,txt):
        meng = {}
        for item in det:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                meng[text] = center_coordinates
                return meng
    def getPoint_by_data_true(self,det,txt):
        for item in det:
            text = item['text']
            if(str(text) == str(txt)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates
    def getPoints_by_data(self,det,txt):
        center_coordinates = []
        for item in det:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinate = (center_x, center_y)
                center_coordinates.append(center_coordinate)
        return center_coordinates

    def getPointsAndTexts_by_data(self, det, txt):
        # 创建一个字典用于存储文本和对应的中心坐标
        text_coordinates = {}
        for item in det:
            text = item['text']
            # 检查文本中是否包含目标字符串
            if str(text).count(str(txt)) > 0:
                box = item['box']
                x_sum = 0
                y_sum = 0
                # 计算边界框的中心坐标
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinate = (center_x, center_y)
                # 将文本作为键，中心坐标作为值存入字典
                text_coordinates[text] = center_coordinate
        return text_coordinates

    def getPointsAndTexts_by_data_from_small_area(self, det, txt,x1,x2,y1,y2):
        # 创建一个字典用于存储文本和对应的中心坐标
        text_coordinates = {}
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        for item in det:
            text = item['text']
            # 检查文本中是否包含目标字符串
            if str(text).count(str(txt)) > 0:
                box = item['box']
                x_sum = 0
                y_sum = 0
                # 计算边界框的中心坐标
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                if ((x1 < center_x < x2) and (y1 < center_y < y2)):
                    center_coordinate = (center_x, center_y)
                    # 将文本作为键，中心坐标作为值存入字典
                    text_coordinates[text] = center_coordinate
        return text_coordinates

    def is_Phonenumber(self,string):
        if len(string) == 0:
            return False
        if string[0] != '1':
            return False
        for char in string[1:]:
            if char not in '0123456789':
                return False
        return True
    def getPoint_by_data_back(self,det,txt):
        center_coordinates = None
        for item in det:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
        return center_coordinates
    def getPoint_BY_PaddleOCRJsons_area(self,image,txt,x1,x2,y1,y2):
        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        #print(getObj["data"])
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if(str(txt) in str(text)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                #print()
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                #print("-----------------------------")
                #print(center_coordinates)
                #center_coordinatess.append(text)
                center_coordinatess.append(center_coordinates)
                #print("------------"+str(center_coordinatess))
        return center_coordinatess

    def getPoint_BY_PaddleOCRJsons_area_from_alldata(self,alldata,txt,x1,x2,y1,y2):
        #getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        #print(getObj["data"])
        #center_coordinatess = []
        for item in alldata:
            text = item['text']
            if(str(txt) in str(text)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                #print()
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                #print("-----------------------------")
                #print(center_coordinates)
                #center_coordinatess.append(text)
                #center_coordinatess.append(center_coordinates)
                #print("------------"+str(center_coordinatess))
                return center_coordinates


    def getPoint_BY_PaddleOCRJsons_area_No_by_txt(self,alldata,x1,x2,y1,y2):
        center_coordinatess = []
        for item in alldata:
            text = item['text']

            box = item['box']
            x_sum = 0
            y_sum = 0
            for point in box:
                x_sum += point[0]
                y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                if ((x1 < center_x < x2) and (y1 < center_y < y2)):
                    center_coordinates = (center_x, center_y)
                    #print("text--------------->"+str(text))
                    return text
    def getPoint_BY_PaddleOCRJsons_area_No_by_txt_2(self,alldata,mingci,x1,x2,y1,y2):
        center_coordinatess = []
        for item in alldata:
            text = item['text']
            if (str(mingci) in str(text)):
                print("text---------------------->",text)
                box = item['box']
                print("box---------------------->", box)
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                if ((x1 < center_x < x2) and (y1 < center_y < y2)):
                    center_coordinates = (center_x, center_y)
                    print("center_coordinates--------------->"+str(center_coordinates))
                    return center_coordinates

    def getPoint_BY_PaddleOCRJsons_area_all(self,image,txt,x1,x2,y1,y2):
        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        #print(getObj["data"])
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if(str(txt) in str(text)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                print(center_coordinates)
                #center_coordinatess.append(text)
                center_coordinatess.append(center_coordinates)
                #print("------------"+str(center_coordinatess))
        return center_coordinatess

    def getPoint_BY_PaddleOCRJson_back(self,image,txt):#正常的在图片中倒序获取 文字坐标的方法
        getObj = self.ocr.run(image)
        #print(f'图片识别完毕，状态码：{getObj["code"]} 结果：\n{getObj["data"]}\n')
        #print(getObj["data"])
        center_coordinates = None
        for item in getObj["data"]:
            text = item['text']
            if(str(text).count(str(txt))>0):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
        return center_coordinates
    def getPoint_BY_PaddleOCRJson_byList_phone(self,image,list_temp):#正常的在图片中获取 文字坐标的方法
        getObj = self.ocr.run(image)
        for item in getObj["data"]:
            text = item['text']
            for temp in list_temp:
                if (str(text).count(str(temp)) > 0):
                    box = item['box']
                    x_sum = 0
                    y_sum = 0
                    for point in box:
                        x_sum += point[0]
                        y_sum += point[1]
                    center_x = x_sum / len(box)
                    center_y = y_sum / len(box)
                    center_coordinates = (center_x, center_y)
                    return center_coordinates
    def findPointToDouyin(self,alldata,list_temp,y):#正常的在图片中获取 文字坐标的方法
        center_coordinates = []
        previoustag = 0
        previoustag_y = 0
        getObj = alldata
        for item in getObj:
            text = item['text']
            for temp in list_temp:
                if temp == "回复":
                    #print("huifu")
                    if (str(text) == str(temp)):
                        box = item['box']
                        x_sum = 0
                        y_sum = 0
                        for point in box:
                            x_sum += point[0]
                            y_sum += point[1]
                        center_x = x_sum / len(box)
                        center_y = y_sum / len(box)
                        aa = (center_x, center_y)

#                        if(previoustag == 1):
#                            if(previoustag_y - center_y > 150):
                        print("回复")
                        print(aa)
                        if(center_y < int(y)-450):
                            center_coordinates.append(aa)
                        previoustag = 0
                elif(temp == "条回复"):
                    #print("tiao 回复")
                    if (str(text).count(str(temp))>0):
                        box = item['box']
                        x_sum = 0
                        y_sum = 0
                        for point in box:
                            x_sum += point[0]
                            y_sum += point[1]
                        center_x = x_sum / len(box)
                        center_y = y_sum / len(box)
                        aa = (center_x, center_y)
                        print("条回复")
                        print(aa)
                        if (len(center_coordinates) > 0):
                            center_coordinates.pop()
                        if (center_y < int(y) - 450):
                            center_coordinates.append(aa)
                        previoustag = 1
                        previoustag_y = center_y
                elif(temp == "条评论"):
                    #print("条评论")
                    if (str(text).count(str(temp))>0):
                        box = item['box']
                        x_sum = 0
                        y_sum = 0
                        for point in box:
                            x_sum += point[0]
                            y_sum += point[1]
                        center_x = x_sum / len(box)
                        center_y = y_sum / len(box)
                        aa = (center_x, center_y)
                        print("条评论")
                        print(aa)
                        if (center_y < int(y) - 450):
                            center_coordinates.append(aa)
        if(len(center_coordinates)>0):
            print("")

        return center_coordinates
    #print(getPoint_BY_PaddleOCRJson("啊啊啊"))
    def getPoint_BY_PaddleOCRJson_true(self,image,txt):
        getObj = self.ocr.run(image)
        print("-----------------------------------------------")
        print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if(str(text) ==(str(txt))):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                return center_coordinates
    def getPoint_BY_PaddleOCRJson_aa(self,image,txt):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            box = item['box']
            x_sum = 0
            y_sum = 0
            for point in box:
                x_sum += point[0]
                y_sum += point[1]
            center_x = x_sum / len(box)
            center_y = y_sum / len(box)
            center_coordinates = (center_x, center_y)
            center_coordinatess.append(text)
            center_coordinatess.append(center_coordinates)
        return center_coordinatess
    def getPoint_BY_PaddleOCRJsons(self,image,txt):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if(str(txt) in str(text)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                #center_coordinatess.append(text)
                center_coordinatess.append(center_coordinates)
        return center_coordinatess
    def getPoint_BY_PaddleOCRJsons_dakai(self,image,txt):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if((str(txt) in str(text)) & (str("已打开") not in str(text)) ):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                #center_coordinatess.append(text)
                center_coordinatess.append(center_coordinates)
        return center_coordinatess
    def getPoint_BY_PaddleOCRJson_gettxt(self,image,txt):
        getObj = self.ocr.run(image)

        temp_point = self.getPoint_BY_PaddleOCRJson(image,txt)
        if(temp_point!=None):
            members_x = temp_point[0]  # x-coordinate of members
            members_y = temp_point[1]  # y-coordinate of members
            for item in getObj["data"]:
                text = item['text']
                x = (item['box'][0][0] + item['box'][1][0]) // 2  # x-coordinate of the text
                y = (item['box'][0][1] + item['box'][2][1]) // 2  # y-coordinate of the text
                score = item['score']
                if((members_x - x) <= 100 and members_y - y < 100 and float(score) - float(0.85)>0 and txt not in text):
                    return text
    def getPoint_BY_PaddleOCRJson_int(self,image, txt):
        getObj = self.ocr.run(image)
        #for item in getObj["data"]:
        dialogue_coordinates = None
        for item in getObj["data"]:
            if item['text'] == '对话':
                dialogue_coordinates = item['box']
                break
        if dialogue_coordinates:
            for item in getObj["data"]:
                if item['text'].isdigit() and item['box'][0][0] > dialogue_coordinates[2][0] and item['box'][0][0] - dialogue_coordinates[2][0] < 100:
                    return item['text']
        else:
            print("未找到符合条件的数字")

    def getPoint_BY_PaddleOCRJson_int2(self,image, txt,x,y):
            getObj = self.ocr.run(image)
            result = []  # 存储纯数字文本的数组
            for item in getObj["data"]:
                text = item['text']
                if str(text).isdigit():  # 判断文本是否为纯数字
                    #result.append(text)
                    box = item['box']
                    x_sum = 0
                    y_sum = 0
                    for point in box:
                        x_sum += point[0]
                        y_sum += point[1]
                    center_x = x_sum / len(box)
                    center_y = y_sum / len(box)
                    center_coordinates = (center_x, center_y)
                    if(center_x > x and center_y >y and x>600):
                        result.append(center_coordinates)
            return result
    import re
    #is_valid_string(list_temp)
    def getAllData_test(self,image):#获取页面所有的数据内容
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 拼接图片的绝对路径
        abs_image_path = os.path.join(script_dir, image)
        # 检查图片是否存在
        if not os.path.exists(abs_image_path):
            print(f"错误：图片不存在 → {abs_image_path}")
            return None  # 或抛出异常

        getObj = self.ocr.run(abs_image_path)
        return getObj["data"]

    def convert_to_black_white(self,input_path, output_path=None):
        """
        将彩色图片转换为黑白（灰度）图片

        参数:
            input_path: 输入图片的路径
            output_path: 输出图片的路径，默认为在原文件名后加"_bw"
        """
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 转换为灰度模式
                # L模式表示8位灰度图，每个像素用0-255表示亮度
                bw_img = img.convert('L')

                # 如果未指定输出路径，自动生成
                if not output_path:
                    # 分离文件名和扩展名
                    file_name, file_ext = os.path.splitext(input_path)
                    output_path = f"{file_name}_bw{file_ext}"

                # 保存黑白图片
                bw_img.save(output_path)
                print(f"黑白图片已保存至: {output_path}")
                return output_path

        except Exception as e:
            print(f"转换失败: {str(e)}")
            return None

    def get_lottery_remaining_time(self,ocr_result):
        """
        基于坐标位置精准提取福袋开奖倒计时（修正版：优先坐标匹配，避免文本误判）
        """
        # 第一步：找到包含"后开奖"的目标文本项，提取其坐标基准
        target_item = None
        y_base = 0  # 后开奖文本的基准y坐标（取四个点的y均值）
        x_right = 0  # 后开奖文本的最右侧x坐标（用于限定左侧查找范围）

        for item in ocr_result:
            text = item.get('text', '').strip()
            if "后开奖" in text:
                target_item = item
                # 计算该文本的y轴均值（判断是否同一水平）和最右侧x坐标（限定左侧查找）
                box = item['box']
                y_coords = [point[1] for point in box]
                y_base = sum(y_coords) / len(y_coords)
                x_coords = [point[0] for point in box]
                x_right = max(x_coords)
                break

        if not target_item:
            return "未检测到「后开奖」文本，无法提取倒计时"

        # 第二步：基于坐标查找左侧同一水平的纯数字（分钟/秒数）—— 优先级最高
        num_pattern = re.compile(r'^\d{1,2}$')
        candidate_nums = []
        for item in ocr_result:
            text = item.get('text', '').strip()
            if not num_pattern.match(text):
                continue  # 非纯数字跳过

            # 计算当前文本的y均值和x均值
            box = item['box']
            y_coords = [point[1] for point in box]
            y_avg = sum(y_coords) / len(y_coords)
            x_coords = [point[0] for point in box]
            x_avg = sum(x_coords) / len(x_coords)

            # 核心判断：同一水平（y差≤15）+ 在左侧（x更小）
            if abs(y_avg - y_base) <= 15 and x_avg < x_right:
                candidate_nums.append({
                    'text': text,
                    'x_avg': x_avg,  # 记录x均值，用于排序（越靠右越接近"后开奖"）
                    'y_avg': y_avg
                })

        # 第三步：如果坐标匹配到数字，按x从大到小排序 → 最右=秒，次右=分钟
        if candidate_nums:
            candidate_nums.sort(key=lambda x: x['x_avg'], reverse=True)
            minutes = 0
            seconds = 0
            if len(candidate_nums) >= 1:
                seconds = int(candidate_nums[0]['text'])  # 最右侧是秒数
            if len(candidate_nums) >= 2:
                minutes = int(candidate_nums[1]['text'])  # 次右侧是分钟数
            return self.calculate_and_format(minutes, seconds)

        # 第四步：兜底——如果坐标没匹配到，再尝试从目标文本中提取时间（如"00后开奖"）
        target_text = target_item['text']
        time_match = re.search(r'(\d{1,2}):?(\d{1,2})?后开奖', target_text)
        if time_match:
            minutes = int(time_match.group(1)) if time_match.group(1) else 0
            seconds = int(time_match.group(2)) if time_match.group(2) else 0
            return self.calculate_and_format(minutes, seconds)
        else:
            return "未找到「后开奖」左侧的时间数字"


    def calculate_and_format(self,minutes, seconds):
        """计算总秒数并格式化输出"""
        total_seconds = minutes * 60 + seconds
        if total_seconds == 0:
            print(f"开奖倒计时：{minutes}分{seconds}秒（总计{total_seconds}秒，即将开奖）")
            return total_seconds

        print(f"开奖倒计时：{minutes}分{seconds}秒（总计{total_seconds}秒）")
        return total_seconds

def find_order_info(ocr_data):
    """
    终极完整版：状态 + 店铺 + 商品名 + 价格 + 实付款 + 数量
    商品名规则：
    1. 位于【原价y +50 ~ 原价y +200】垂直区域
    2. 位于【x 250 ~ 原价x-50】水平区域
    3. 自动过滤无效文本：7天无理由退货、极速退款、申请售后、去评价、再买一单、坏了包赔、晚发即赔、已享明日达
    """
    # 无效商品名过滤列表
    print(ocr_data)
    FILTER_WORDS = [
        "7天无理由退货", "极速退款", "申请售后", "去评价",
        "再买一单", "坏了包赔", "晚发即赔", "已享明日达","实付款","含运费险服务实","实付款","实付款","实付款"
    ]

    # ========== 1. 找状态锚点 ==========
    status_keywords = ["交易完成", "交易关闭", "待发货", "待收货"]
    anchor_item = None
    anchor_y = 0
    beizhus = ""

    # 拼接所有OCR文本作为备注
    for item in ocr_data:
        text = item["text"].strip()
        beizhus += text + ","

    # 查找订单状态
    for item in ocr_data:
        text = item.get("text", "").strip()
        if text in status_keywords:
            anchor_item = item
            y1 = item["box"][0][1]
            y3 = item["box"][2][1]
            anchor_y = (y1 + y3) / 2
            break

    if not anchor_item:
        return None

    # ========== 2. 找店铺名 ==========
    shop_item = None
    min_x = 9999
    anchor_y1 = anchor_item["box"][0][1]
    anchor_y3 = anchor_item["box"][2][1]

    for item in ocr_data:
        x1 = item["box"][0][0]
        y1 = item["box"][0][1]
        if anchor_y1 - 20 <= y1 <= anchor_y3 + 20:
            if x1 < 150 and x1 < min_x:
                min_x = x1
                shop_item = item

    # ========== 3. 找商品价格（￥开头 + 在锚点下方）==========
    price_item = None
    price_x = 0  # 价格的x坐标（用于商品名区域计算）
    price_y = 0  # 价格的y坐标

    for item in ocr_data:
        text = item.get("text", "").strip()
        item_y1 = item["box"][0][1]
        if text.startswith("￥") and item_y1 > anchor_y:
            price_item = text.split("￥")[-1].strip()
            price_x = item["box"][0][0]
            price_y = item["box"][0][1]
            break

    # ========== 4. 【优化核心】按坐标区域 + 过滤文本 找商品名 ==========
    goods_item = ""
    if price_item and price_x > 0:
        # 商品名坐标范围
        y_min = price_y + 50
        y_max = price_y + 200
        x_left = 250
        x_right = price_x - 50

        # 遍历找符合区域 + 有效文本的商品
        for item in ocr_data:
            text = item["text"].strip()
            print("text=",text)
            x1 = item["box"][0][0]
            y1 = item["box"][0][1]

            # 坐标匹配
            in_area = (x_left <= x1 <= x_right) and (y_min <= y1 <= y_max)
            # 文本有效（不在过滤列表里）
            valid_text = not any(filter_word in text for filter_word in FILTER_WORDS) and len(text) > 1

            if in_area and valid_text:
                goods_item = goods_item + item["text"] + ","
                #break  # 找到第一个符合条件的商品名就停止

    # ========== 5. 找实付款 ==========
    pay_item = None
    for item in ocr_data:
        text = item.get("text", "").strip()
        item_y1 = item["box"][0][1]
        if text.startswith("实付款") and item_y1 > anchor_y:
            pay_item = text.split("￥")[-1].strip()
            break

    # ========== 6. 找数量（x/X开头）==========
    count_text = None
    count_num = None
    for item in ocr_data:
        text = item.get("text", "").strip()
        item_y1 = item["box"][0][1]
        if (text.startswith("x") or text.startswith("X")) and item_y1 > anchor_y:
            count_text = text
            count_num = text.lstrip("xX").strip()  # 同时去掉小写x和大写X
            break

    # ========== 最终返回 ==========
    return {
        "订单状态": anchor_item["text"],
        "店铺名称": shop_item["text"] if shop_item else None,
        "产品": goods_item if goods_item else None,
        "原价": price_item,
        "实付": pay_item,
        "数量文本": count_text,
        "备注": beizhus,
        "数量": count_num
    }

from PIL import Image
import os
yewu_lock = threading.Lock()
def yewu(i):
    with yewu_lock:
        print(f"开始第{i}次")
        start_time = time.time()
        bb = ocr.getAllData_test(r"D:\dy_temp\20260503222507.png")
        # print(bb)
        # print(ocr.get_lottery_remaining_time(bb))
        # for temp in bb:
        #     print("------->", temp)
        # print(f"第{i}次耗时=", time.time() - start_time)
        # time.sleep(0.1)
        print(find_order_info(bb))

        return

# if __name__ == "__main__":
#     # 示例用法
#     input_image = "input.jpg"  # 替换为你的图片路径
#     output_image = "output_bw.jpg"  # 可选，输出图片路径
#
#     # 转换图片
#     convert_to_black_white(input_image, output_image)
#
from PaddleOCR_json.PPOCR_api import GetOcrApi
import inspect

# 打印 GetOcrApi 支持的所有参数
print(inspect.signature(GetOcrApi))

ocr = OCRProcessor()
#convert_to_black_white(r"C:\Users\Administrator\Desktop\66666.png",r"C:\Users\Administrator\Desktop\66666.png")
for i in range(10):
    yewu(i)
    # bbb = threading.Thread(target=yewu,args=(i,))
    # bbb.start()
    # time.sleep(1)

    # if(i%3 == 0):
    #     time.sleep(8)
# if cc:
#     first_key = next(iter(cc))  # 获取第一个键
#     first_value = cc[first_key]
# print(cc)
# print(first_key)
# print(first_value)