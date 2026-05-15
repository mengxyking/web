import timeit

from PIL import Image


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
    for x in range(x1, x2, 5):
        print("x----",x)
        for y in range(y1, y2, 5):
            print("y----", y)
            # 获取像素的色值
            r, g, b = get_pixel(x, y)
            # 打印色值及其坐标
            print(f"坐标: ({x}, {y}), 色值: RGB({r}, {g}, {b})")

image_path = r'C:\Users\Administrator\Desktop\222.jpg'  # 替换为你的图片路径
#get_every_second_pixel(image_path,910,1000,800,828)

elapsed_time = timeit.timeit(lambda: get_every_second_pixel(image_path,0,30,0,30), number=1)
print(f"方法运行时间: {elapsed_time} 秒")

# 示例用法
