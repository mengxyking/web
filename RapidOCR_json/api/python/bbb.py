import os
import threading
import time

from demo1 import OCRProcessor

ocr = OCRProcessor()
testImgPath = r"sc.png"
script_dir = os.path.dirname(os.path.abspath(__file__))
# 拼接图片的绝对路径
abs_image_path = os.path.join(script_dir, testImgPath)
#convert_to_black_white(r"C:\Users\Administrator\Desktop\66666.png",r"C:\Users\Administrator\Desktop\66666.png")
for i in range(10):
    print("i=",i)
    bbb = threading.Thread(target=ocr.yewu,args=(abs_image_path,))
    bbb.start()
data_all = ocr.yewu(abs_image_path)
print(data_all)