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


def check_element_by_id(element_id):
    # 使用UI Automator的selector来查找元素
    element = d(resourceId=element_id)  # 设置一个超时时间
    print(element)
    element.click()


# 设置watcher
def on_element_appear(element):
    # 这里定义当元素出现时你要执行的动作
    print("ddd=",element)
    d.press("back")  # 比如按下返回键


# 注册watcher，使用lambda函数包装我们的检查函数

s = "384da6"
d = get_device(s)

elements = d.dump_window_hierarchy()  # 这将返回一个包含UI元素树的字典或对象

# 但是，dump_window_hierarchy() 返回的通常是一个复杂的嵌套结构，不是简单的元素列表。
# 为了简化处理，我们可以使用 uiautomator2 提供的选择器来遍历元素。

# 一个更常用的方法是使用 d(resourceId=..., text=..., ...).all() 来获取匹配条件的所有元素
# 例如，获取所有按钮元素（假设按钮的resourceId包含'button'）：
all_buttons = d(resourceId="*.button").all()

# 打印所有按钮的文本和描述信息（如果可用）
for button in all_buttons:
    print(f"Button text: {button.text}, description: {button.description}")






