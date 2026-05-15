import os
import sys
import threading
import time
import uuid  # 用于生成唯一临时文件名
from datetime import datetime

from RapidOCR_json.api.python.RapidOCR_api import OcrAPI
from PIL import Image

# 全局锁：确保所有线程串行执行OCR流程，避免资源竞争
global_ocr_lock = threading.Lock()


class OCRProcessor:
    def __init__(self):
        self.file_path = self.getFilPath()
        self.ocr = OcrAPI(str(self.file_path))

    def getAllData_test(self, image):  # 获取页面所有的数据内容
        print("1")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 拼接图片的绝对路径
        abs_image_path = os.path.join(script_dir, image)
        # 检查图片是否存在
        if not os.path.exists(abs_image_path):
            print(f"错误：图片不存在 → {abs_image_path}")
            return None  # 或抛出异常

        getObj = self.ocr.run(abs_image_path)
        return getObj["data"]

    # 【省略原有其他方法，保留不变】
    # （注：以下仅展示修改/新增的核心方法，原有方法全部保留）

    def convert_to_black_white(self, input_path, output_path=None):
        """
        将彩色图片转换为黑白（灰度）图片
        新增：支持自定义输出路径，避免多线程文件冲突
        参数:
            input_path: 输入图片的路径
            output_path: 输出图片的路径，默认为在原文件名后加"_bw_唯一标识"
        """
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 转换为灰度模式
                bw_img = img.convert('L')

                # 如果未指定输出路径，生成唯一临时文件名（避免多线程冲突）
                if not output_path:
                    file_name, file_ext = os.path.splitext(input_path)
                    # 用uuid生成唯一标识，避免多线程覆盖
                    unique_id = str(uuid.uuid4())[:8]
                    output_path = f"{file_name}_bw_{unique_id}{file_ext}"

                # 保存黑白图片
                bw_img.save(output_path)
                # print(f"黑白图片已保存至: {output_path}")
                return output_path

        except Exception as e:
            print(f"转换失败: {str(e)}")
            return None

    def getFilPath(self):
        bbb = time.time()
        file_name = "RapidOCR-json.exe"
        # 获取当前脚本所在目录的路径
        script_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(script_directory)
        parent_directory = os.path.dirname(parent_directory)
        grandparent_directory = os.path.dirname(parent_directory)

        # 递归搜索文件并返回绝对路径
        def search_file(directory, file_name):
            for root, dirs, files in os.walk(directory):
                if file_name in files:
                    return os.path.join(root, file_name)
            return None

        # 查找文件并返回绝对路径
        file_path = search_file(grandparent_directory, file_name)
        if file_path:
            # print("文件的绝对路径是：", file_path)
            return file_path
        else:
            print("未找到文件。")
            return None

    def yewu(self, imgPath, temp_bw_path=None):
        """
        改造后：支持传入临时黑白图片路径，避免多线程文件冲突
        :param imgPath: 原始图片路径
        :param temp_bw_path: 自定义黑白图片临时路径（可选）
        :return: OCR识别结果
        """
        # 生成唯一临时黑白图片路径（避免多线程覆盖）
        imgPath = self.convert_to_black_white(imgPath, output_path=temp_bw_path)
        if not imgPath:
            print("黑白图片转换失败，跳过OCR")
            return None

        try:
            start_time = time.time()
            bb = self.getAllData_test(imgPath)
            print(f"OCR耗时={time.time() - start_time:.2f}秒")

            # 清理临时黑白图片（可选，根据需求保留/删除）
            if os.path.exists(imgPath):
                os.remove(imgPath)
                # print(f"已清理临时文件: {imgPath}")

            return bb
        except BaseException as e:
            print(f"OCR执行异常: {e}")
            # 异常时也清理临时文件
            if os.path.exists(imgPath):
                os.remove(imgPath)
            return None

    # 保留原有其他方法（全部不变）
    def getPoint_BY_PaddleOCRJson(self, image, txt):
        getObj = self.ocr.run(image)
        print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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

    def getPoint_BY_PaddleOCRJson_GPU(self, image, txt):
        getObj = self.ocr.run(image)
        print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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

    def getPoint_BY_PaddleOCRJson_2(self, image, txt, txt2, txt3):
        getObj = self.ocr.run(image)
        for item in getObj["data"]:
            text = item['text']
            if ((str(text).count(str(txt)) > 0) & (str(text).count(str(txt2)) > 0)):
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

    def getAllData(self, image):
        abb = time.time()
        getObj = self.ocr.run(image)
        return getObj["data"]

    def getAreaDataFromAlldataByPoint(self, allData, x1, x2, y1, y2):
        areaData = {}
        for tempData in allData:
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
            if ((x1 < center_x < x2) & (y1 < center_y < y2)):
                areaData[text] = center_coordinates
        return areaData

    def getPoint_by_data(self, det, txt):
        for item in det:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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

    def getPoint_by_datas(self, det, txt, txt2):
        for item in det:
            text = item['text']
            if (str(text).count(str(txt)) > 0 and str(text).count(str(txt2)) > 0):
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

    def getPoint_text_by_data(self, det, txt):
        meng = {}
        for item in det:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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

    def getPoint_by_data_true(self, det, txt):
        for item in det:
            text = item['text']
            if (str(text) == str(txt)):
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

    def getPoints_by_data(self, det, txt):
        center_coordinates = []
        for item in det:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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
        text_coordinates = {}
        for item in det:
            text = item['text']
            if str(text).count(str(txt)) > 0:
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinate = (center_x, center_y)
                text_coordinates[text] = center_coordinate
        return text_coordinates

    def getPointsAndTexts_by_data_from_small_area(self, det, txt, x1, x2, y1, y2):
        text_coordinates = {}
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        print("det=", det)
        for item in det:
            text = item['text']
            if str(text).count(str(txt)) > 0:
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                if ((x1 < center_x < x2) and (y1 < center_y < y2)):
                    center_coordinate = (center_x, center_y)
                    text_coordinates[text] = center_coordinate
        return text_coordinates

    def getQianmianAndTexts_by_data_from_small_area(self, det, txt):
        print("det=", det)
        for index, item in enumerate(det):
            text = item['text']
            if str(text) == txt:
                return det[index - 1]["text"]

    def getQianmianAndTexts_by_data_from_small_area_zhineng(self, det, txt):
        print("det=", det)
        target_index = -1
        for index, item in enumerate(det):
            text = item['text']
            if str(text) == txt:
                target_index = index
                break
        if target_index == -1:
            return None
        start_index = max(0, target_index - 1)
        end_index = max(0, target_index - 10)
        for i in range(start_index, end_index - 1, -1):
            current_text = det[i]['text']
            try:
                float(current_text)
                return current_text
            except (ValueError, TypeError):
                continue
        return None

    def getIntAndTexts_by_data_from_small_area(self, det, x1, x2, y1, y2):
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        print("det=", det)
        for item in det:
            text = item['text']
            if str(text).isdigit():
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                if ((x1 < center_x < x2) and (y1 < center_y < y2)):
                    return text
        return None

    def getPoint_by_data_from_small_area(self, det, txt, x1, x2, y1, y2):
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        print("det=", det)
        for item in det:
            text = item['text']
            if str(text).count(str(txt)) > 0:
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                if ((x1 < center_x < x2) and (y1 < center_y < y2)):
                    center_coordinate = (center_x, center_y)
                    return center_coordinate

    def is_Phonenumber(self, string):
        if len(string) == 0:
            return False
        if string[0] != '1':
            return False
        for char in string[1:]:
            if char not in '0123456789':
                return False
        return True

    def getPoint_by_data_back(self, det, txt):
        center_coordinates = None
        for item in det:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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

    def getPoint_BY_PaddleOCRJsons_area(self, image, txt, x1, x2, y1, y2):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if (str(txt) in str(text)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                center_coordinatess.append(center_coordinates)
        return center_coordinatess

    def getPoint_BY_PaddleOCRJsons_area_from_alldata(self, alldata, txt, x1, x2, y1, y2):
        for item in alldata:
            text = item['text']
            if (str(txt) in str(text)):
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

    def getPoint_BY_PaddleOCRJsons_area_No_by_txt(self, alldata, x1, x2, y1, y2):
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
                    return text

    def getPoint_BY_PaddleOCRJsons_area_No_by_txt_2(self, alldata, mingci, x1, x2, y1, y2):
        for item in alldata:
            text = item['text']
            if (str(mingci) in str(text)):
                print("text---------------------->", text)
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
                    print("center_coordinates--------------->" + str(center_coordinates))
                    return center_coordinates

    def getPoint_BY_PaddleOCRJsons_area_all(self, image, txt, x1, x2, y1, y2):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if (str(txt) in str(text)):
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
                center_coordinatess.append(center_coordinates)
        return center_coordinatess

    def getPoint_BY_PaddleOCRJson_back(self, image, txt):
        getObj = self.ocr.run(image)
        center_coordinates = None
        for item in getObj["data"]:
            text = item['text']
            if (str(text).count(str(txt)) > 0):
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

    def getPoint_BY_PaddleOCRJson_byList_phone(self, image, list_temp):
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

    def findPointToDouyin(self, alldata, list_temp, y):
        center_coordinates = []
        previoustag = 0
        previoustag_y = 0
        getObj = alldata
        for item in getObj:
            text = item['text']
            for temp in list_temp:
                if temp == "回复":
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
                        print("回复")
                        print(aa)
                        if (center_y < int(y) - 450):
                            center_coordinates.append(aa)
                        previoustag = 0
                elif (temp == "条回复"):
                    if (str(text).count(str(temp)) > 0):
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
                elif (temp == "条评论"):
                    if (str(text).count(str(temp)) > 0):
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
        if (len(center_coordinates) > 0):
            print("")
        return center_coordinates

    def getPoint_BY_PaddleOCRJson_true(self, image, txt):
        getObj = self.ocr.run(image)
        print("-----------------------------------------------")
        print(getObj["data"])
        for item in getObj["data"]:
            text = item['text']
            if (str(text) == (str(txt))):
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

    def getPoint_BY_PaddleOCRJson_aa(self, image, txt):
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

    def getPoint_BY_PaddleOCRJsons(self, image, txt):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if (str(txt) in str(text)):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                center_coordinatess.append(center_coordinates)
        return center_coordinatess

    def getPoint_BY_PaddleOCRJsons_dakai(self, image, txt):
        getObj = self.ocr.run(image)
        center_coordinatess = []
        for item in getObj["data"]:
            text = item['text']
            if ((str(txt) in str(text)) & (str("已打开") not in str(text))):
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                center_coordinatess.append(center_coordinates)
        return center_coordinatess

    def getPoint_BY_PaddleOCRJson_gettxt(self, image, txt):
        getObj = self.ocr.run(image)
        temp_point = self.getPoint_BY_PaddleOCRJson(image, txt)
        if (temp_point != None):
            members_x = temp_point[0]
            members_y = temp_point[1]
            for item in getObj["data"]:
                text = item['text']
                x = (item['box'][0][0] + item['box'][1][0]) // 2
                y = (item['box'][0][1] + item['box'][2][1]) // 2
                score = item['score']
                if ((members_x - x) <= 100 and members_y - y < 100 and float(score) - float(
                        0.85) > 0 and txt not in text):
                    return text

    def getPoint_BY_PaddleOCRJson_int(self, image, txt):
        getObj = self.ocr.run(image)
        dialogue_coordinates = None
        for item in getObj["data"]:
            if item['text'] == '对话':
                dialogue_coordinates = item['box']
                break
        if dialogue_coordinates:
            for item in getObj["data"]:
                if item['text'].isdigit() and item['box'][0][0] > dialogue_coordinates[2][0] and item['box'][0][0] - \
                        dialogue_coordinates[2][0] < 100:
                    return item['text']
        else:
            print("未找到符合条件的数字")

    def getPoint_BY_PaddleOCRJson_int2(self, image, txt, x, y):
        getObj = self.ocr.run(image)
        result = []
        for item in getObj["data"]:
            text = item['text']
            if str(text).isdigit():
                box = item['box']
                x_sum = 0
                y_sum = 0
                for point in box:
                    x_sum += point[0]
                    y_sum += point[1]
                center_x = x_sum / len(box)
                center_y = y_sum / len(box)
                center_coordinates = (center_x, center_y)
                if (center_x > x and center_y > y and x > 600):
                    result.append(center_coordinates)
        return result

    def yewu_no_jiabai(self, imgPath):
        with global_ocr_lock:
            try:
                start_time = time.time()
                bb = self.getAllData_test(imgPath)
                print(bb)
                print(f"第{1}次耗时=", time.time() - start_time)
                return bb
            except BaseException as e:
                print("bengkuile ", e)
                return None

    def getPoint_qiandao(self, alldata, x1, x2, y1, y2):
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
                center_coordinatess.append(text)
        print(center_coordinatess)
        for temp in center_coordinatess:
            temp = str(temp).replace(" ", "")
            if (str(temp).count("金币")):
                lists = str(temp).split("金币")
                if (str(lists[0]).isdigit()):
                    print("是纯数字啊")
                    print(lists[0])
                    return lists[0]
            if (str(temp).isdigit()):
                print("meiyou 截取就是纯数字啊")
                print(temp)
                return temp
            if (str(temp).startswith("金币")):
                print("当前是金币开头的啊")
                lists = str(temp).split("金币")
                if (str(lists[-1]).isdigit()):
                    print("是纯数字啊")
                    print(lists[-1])
                    return lists[-1]
            if (str(temp).count("折合")):
                lists = str(temp).split("折合")
                if (str(lists[0]).isdigit()):
                    print("是纯数字啊")
                    print(lists[0])
                    return lists[0]
            if (str(temp).count("金")):
                lists = str(temp).split("金")
                if (str(lists[0]).isdigit()):
                    print("是纯数字啊")
                    print(lists[0])
                    return lists[0]
            if (str(temp).startswith("金币") and str(temp).count("万") and str(temp).count(".")):
                return 10000
            if (str(temp).startswith("金币") and str(temp).count("元") and str(temp).count(".")):
                lists = str(temp).split(".")
                jibi = lists[0][2:]
                if (str(jibi).isdigit()):
                    print("是纯数字啊")
                    print(jibi)
                    return jibi[:-1]
            if (str(temp).count("火苗")):
                lists = str(temp).split("火苗")
                jibi = lists[1][1:]
                if (str(jibi).isdigit()):
                    print("是纯数字啊")
                    print(jibi)
                    return jibi
        return None

    def getPoint_qiandao_jiahao(self, alldata, x1=600, x2=2000, y1=300, y2=1500):

        data_today = datetime.today().strftime("%Y-%m-%d")
        data_today_2 = datetime.now().strftime("%Y.%m.%d")
        print("data_today=",data_today,data_today_2)
        temp_y = 0
        if(str(alldata).count(data_today)<1 and str(alldata).count(data_today_2)<1):
            print("当前没有当前日期，判定为失败")
            return None
        # if(str(alldata).count(data_today)>0):
        #     temp_y = alldata[data_today]["box"][3][1]
        #     print("----",temp_y)
        # else:
        #     temp_y = alldata[data_today_2]["box"][3][1]
        #     print("----", temp_y)

        for item in alldata:
            text = item['text']
            box = item['box']
            if (text == data_today) :
                x_sum = 0
                y_sum = 0
                for point in box:
                    #x_sum += point[0]
                    temp_y= point[1]

                break
            elif( text == data_today_2):
                for point in box:
                    #x_sum += point[0]
                    temp_y= point[1]
                break
        else:
            return None

        print("----", temp_y)

        y2 = temp_y+30
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
                center_coordinatess.append(text)
        print(center_coordinatess)
        for temp in center_coordinatess:
            temp = str(temp).replace(" ", "")
            if (str(temp).count("+")):
                temp_str = str(temp)[1:]
                if(str(temp_str).isdigit()):
                    return str(temp_str).strip()
                else:
                    digits = [c for c in str(temp_str).strip() if c.isdigit()]
                    # 拼接成纯数字字符串
                    num_str = ''.join(digits)
                    # 转为整数（按需选择）
                    num = int(num_str)
                    return num


            # if (str(temp).isdigit()):
            #     print("meiyou 截取就是纯数字啊")
            #     print(temp)
            #     return temp
            # if (str(temp).startswith("金币")):
            #     print("当前是金币开头的啊")
            #     lists = str(temp).split("金币")
            #     if (str(lists[-1]).isdigit()):
            #         print("是纯数字啊")
            #         print(lists[-1])
            #         return lists[-1]
            # if (str(temp).count("折合")):
            #     lists = str(temp).split("折合")
            #     if (str(lists[0]).isdigit()):
            #         print("是纯数字啊")
            #         print(lists[0])
            #         return lists[0]
            # if (str(temp).count("金")):
            #     lists = str(temp).split("金")
            #     if (str(lists[0]).isdigit()):
            #         print("是纯数字啊")
            #         print(lists[0])
            #         return lists[0]
            # if (str(temp).startswith("金币") and str(temp).count("万") and str(temp).count(".")):
            #     return 10000
            # if (str(temp).startswith("金币") and str(temp).count("元") and str(temp).count(".")):
            #     lists = str(temp).split(".")
            #     jibi = lists[0][2:]
            #     if (str(jibi).isdigit()):
            #         print("是纯数字啊")
            #         print(jibi)
            #         return jibi[:-1]
            # if (str(temp).count("火苗")):
            #     lists = str(temp).split("火苗")
            #     jibi = lists[1][1:]
            #     if (str(jibi).isdigit()):
            #         print("是纯数字啊")
            #         print(jibi)
            #         return jibi
        return None


# 多线程调用函数（加全局锁确保串行执行）
def ocr_thread_worker(ocr_instance, img_path, thread_id):
    """
    OCR多线程工作函数（串行执行）
    :param ocr_instance: OCRProcessor实例
    :param img_path: 图片路径
    :param thread_id: 线程ID（用于日志区分）
    """
    print(f"\n===== 线程{thread_id} 开始执行 =====")
    # 加全局锁：确保所有线程串行执行，避免资源竞争
    with global_ocr_lock:
        alldata = ocr_instance.yewu(img_path)
        print(f"线程{thread_id} 执行结果: {alldata}")
        print(f"===== 线程{thread_id} 执行完成 =====\n")
        return alldata


# 读取目录文件函数（保留）
def get_files_in_dir(dir_path: str, return_relative_path: bool = False) -> list:
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"目录不存在：{dir_path}")
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"不是有效目录：{dir_path}")

    file_list = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            if return_relative_path:
                file_list.append(item_path)
            else:
                file_list.append(item)
    return file_list

#
# 主程序入口
# if __name__ == "__main__":
#     # 配置参数
#     testImgPath = r"C:\Users\Administrator\Desktop\微信图片_20260102202440_139_7.jpg"
#     ocrPath = r"D:\pycharm\Project\wb\RapidOCR-json_v0.2.0\RapidOCR-json.exe"
#
#     # 校验OCR引擎路径
#     if not os.path.exists(ocrPath):
#         print(f"未在以下路径找到引擎！\n{ocrPath}")
#         sys.exit()
#
#     # 初始化OCR实例（全局唯一）
#     ocr = OCRProcessor()
#     alldata = ocr.yewu(r"C:\Users\Administrator\Desktop\微信图片_20260103125902_390_1756.png")
#     print(alldata)
#     print(ocr.getPoint_qiandao_jiahao(alldata))
#
#     # ========== 多线程调用示例 ==========
#     # 示例1：调用3次同一个图片（模拟多线程串行执行）
#     thread_count = 100  # 要启动的线程数
#     threads = []
#
#     # 创建并启动线程
#     for i in range(thread_count):
#         t = threading.Thread(
#             target=ocr_thread_worker,
#             args=(ocr, testImgPath, i + 1)  # 传入OCR实例、图片路径、线程ID
#         )
#         threads.append(t)
#         t.start()
#
#     # 等待所有线程执行完成
#     for t in threads:
#         t.join()
#
#     print("\n所有线程执行完毕！")