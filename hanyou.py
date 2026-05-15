import uiautomator2 as u2
import cv2
import os
import time
from PIL import Image
def get_color_at_position(image, x, y):
    b, g, r = image[y, x]

    #hex_color = "#{:02X}{:02X}{:02X}".format(b, g, r)
    return (r, g, b)
def get_color_at_position_six(image, x, y):
    b, g, r = image[y, x]

    hex_color = "#{:02X}{:02X}{:02X}".format(b, g, r)

    return hex_color
def get_every_second_pixel(image_path,x1,x2,y1,y2):
    # 打开图片
    img = Image.open(image_path)

    # 获取图片的宽度和高度
    width, height = img.size
    print("width, height=",width, height)

    # 检查图片的模式
    mode = img.mode
    if mode == 'RGB':
        # 对于RGB模式，每个像素有三个值（红、绿、蓝）
        def get_pixel(x, y):
            return img.getpixel((x, y))
    elif mode == 'RGBA':
        # 对于RGBA模式，每个像素有四个值（红、绿、蓝、透明度）
        def get_pixel(x, y):
            r, g, b, a = img.getpixel((x, y))
            # 如果不需要透明度信息，可以只返回RGB
            return r, g, b
    else:
        # 对于其他模式，你可能需要特殊处理
        raise ValueError(f"Unsupported image mode: {mode}")

    # 遍历图片的像素，每隔两个像素获取一个色值及其坐标
    print("x1, x2===",x1, x2)
    for x in range(x1, x2, 3):
        print("x----",x)
        for y in range(y1, y2, 3):
            print("y----", y)
            # 获取像素的色值
            r, g, b = get_pixel(x, y)
            # 打印色值及其坐标
            print(f"坐标: ({x}, {y}), 色值: RGB({r}, {g}, {b})")

def get_device(serial):
    #d = ""
    #print("之前的d", d)
    #print(f"正在连接设备: {serial}")
    d = u2.connect(serial)
    d.watcher.remove()
    return d
def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    #print("00000000000000000000000000---------")
    #print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
def photo(s):
    Ui_file_Name =  str(int(time.time()))+"_"+str(s)+"_ui.png"
    path = getPhotoPath()+"/"+Ui_file_Name
    return path
s = "384da6"
d = get_device(s)
path = photo(s)
screenshot_image = d.screenshot()
screenshot_image.save(path)
image = cv2.imread(path)
print(get_color_at_position(image,1950,476))
print(get_color_at_position(image,2064,247))

get_every_second_pixel(path,1992,2090,230,339)





