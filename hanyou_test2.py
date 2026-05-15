import cv2
import numpy as np

# 读取图像
image_path = r'C:\Users\Administrator\Desktop\111.png'  # 替换为你的图像路径
image = cv2.imread(image_path)

# 转换为HSV颜色空间
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义颜色范围（这里以红色为例，但你需要根据你的图像调整这些值）
lower_white = np.array([0, 0, 200])  # 色调可以是任何值，饱和度接近0，明度较高
upper_white = np.array([179, 50, 255])  # 色调涵盖所有值，饱和度较低，明度最高
mask1 = cv2.inRange(hsv, lower_white, upper_white)

# 对于HSV中的红色范围，有时需要两个不同的范围来捕获所有红色（因为Hue是循环的）
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

# 合并两个掩码
mask = mask1 | mask2

# 查找轮廓
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 假设图像中的图标是排列成网格的，并且大小相似
# 我们可以根据轮廓的位置和大小来估计第二排第三个项目的坐标
# 这需要一些假设和试验来确定正确的索引和偏移量

# 排序轮廓（这里简单地按x坐标排序，但可能需要更复杂的逻辑来处理不同大小的图标）
contours_sorted = sorted(contours, key=lambda x: cv2.boundingRect(x)[0])

# 假设每行有N个图标，这里N需要根据你的图像来确定
N = 10  # 这是一个假设值，你需要根据实际情况调整

# 计算第二排第三个项目的索引（注意Python索引从0开始）
index = 2 * N + 2  # 第二排（从0开始计数为1，但乘以N后变为第二行的第一个索引的偏移量，再加上2得到第三个项目的索引）

# 获取轮廓的边界框并确定坐标
if index < len(contours_sorted):
    x, y, w, h = cv2.boundingRect(contours_sorted[index])
    print(f"第二排第三个项目的坐标是: ({x}, {y})")
else:
    print("没有找到第二排第三个项目的轮廓")

# 显示结果（可选）
cv2.imshow('Mask', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()