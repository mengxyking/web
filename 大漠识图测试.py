import time

import cv2
import numpy as np

# 读取图片

def image_quzao(path):
    image_path = path  # 替换为你的图片路径
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 检查图片是否成功加载
    if image is None:
        print("Error: Could not load image.")
        exit()
    a_path = str(time.time())+".jpg"
    cv2.imwrite(a_path, image)
    return a_path

image_quzao(r"D:\yangmao\pic\1735830216_ui.png")

