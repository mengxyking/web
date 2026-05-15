import comtypes.client
import platform
print(platform.architecture())  # 输出('64bit', 'WindowsPE') 或 ('32bit', 'WindowsPE')

# 创建大漠插件对象
dm = comtypes.client.CreateObject("dm.dmsoft")


# 示例1：区域找图（返回匹配图片的坐标）
def find_image():
    # 参数说明：
    # 1. 图片路径（需提前用大漠插件的"字库工具"制作）
    # 2. 颜色偏差（0为精确匹配）
    # 3. 相似度（0-100）
    # 4. 搜索区域(x1,y1,x2,y2)，None表示全屏
    # 5. 是否返回多图坐标（0返回第一个，1返回所有）
    result = dm.FindPic(0, 0, 1024, 768, "test.bmp", "000000", 0.9, 0)
    if result:
        x, y = result.split("|")[1].split(",")[:2]  # 解析返回的坐标字符串
        print(f"找到图片，坐标: ({x}, {y})")
        return int(x), int(y)
    else:
        print("未找到图片")
        return None

# 示例2：找色（返回指定颜色点的坐标）
def find_color():
    # 参数说明：
    # 1. 搜索区域(x1,y1,x2,y2)
    # 2. 颜色值（16进制格式，如"FF0000"表示红色）
    # 3. 颜色偏差（0为精确匹配）
    # 4. 搜索方向（0从左到右，1从右到左等）
    pos = dm.FindColor(0, 0, 1024, 768, "FF0000", 0, 0)
    if pos != -1:
        x = pos & 0xFFFF  # 低16位是X坐标
        y = pos >> 16     # 高16位是Y坐标
        print(f"找到颜色，坐标: ({x}, {y})")
        return x, y
    else:
        print("未找到颜色")
        return None

# 执行示例
if __name__ == "__main__":
    find_image()
    find_color()