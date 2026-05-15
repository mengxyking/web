import cv2
import numpy as np

# 读取图像
image = cv2.imread(r'C:\Users\Administrator\Desktop\666.jpg', cv2.IMREAD_GRAYSCALE)

# 检查图像是否成功加载
if image is None:
    print("Error: Could not load image.")
    exit()

# 应用高斯模糊进行降噪
blurred_image = cv2.GaussianBlur(image, (5, 5), 0)

# 应用自适应阈值进行二值化
# 你可以调整参数来获得更好的结果
_, binary_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 或者使用全局阈值进行二值化
# thresh_value = 127  # 你可以根据需要调整这个值
# _, binary_image = cv2.threshold(blurred_image, thresh_value, 255, cv2.THRESH_BINARY)

# 显示原始图像、降噪后的图像和二值化后的图像
cv2.imshow('Original Image', image)
cv2.imshow('Blurred Image', blurred_image)
cv2.imshow('Binary Image', binary_image)

# 等待按键操作并关闭所有窗口
cv2.waitKey(0)
cv2.destroyAllWindows()

# 如果需要保存二值化后的图像
cv2.imwrite(r'C:\Users\Administrator\Desktop\binary_image.jpg', image)