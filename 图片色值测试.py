import cv2
import numpy as np

# 读取图像
image = cv2.imread(r'C:\Users\Administrator\Desktop\666.jpg')

# 定义感兴趣的区域（ROI）
# 假设ROI的左上角坐标是(x1, y1)，右下角坐标是(x2, y2)
x1, y1, x2, y2 = 50, 50, 800, 800  # 根据你的实际情况调整这些值
roi = image[y1:y2, x1:x2]

# 定义颜色阈值（HSV空间中的范围）
# 白色：H在0-10和160-180，S和V都很高
# 红色：H在0-10和160-179（考虑红色在不同光照下的变化），S较高，V适中
# 黑色：V很低
white_lower = np.array([0, 200, 200])
white_upper = np.array([10, 255, 255])
red_lower1 = np.array([0, 120, 70])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([160, 120, 70])
red_upper2 = np.array([180, 255, 255])
black_lower = np.array([0, 0, 0])
black_upper = np.array([180, 255, 50])  # 50是一个阈值，可以根据实际情况调整

# 转换到HSV空间
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# 创建颜色掩码
white_mask = cv2.inRange(hsv, white_lower, white_upper)
red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
red_mask = cv2.bitwise_or(red_mask1, red_mask2)
black_mask = cv2.inRange(hsv, black_lower, black_upper)

# 检查是否包含白色、红色和黑色
contains_white = np.any(white_mask > 0)
contains_red = np.any(red_mask > 0)
contains_black = np.any(black_mask > 0)

# 输出结果
print(f"ROI中是否包含白色: {contains_white}")
print(f"ROI中是否包含红色: {contains_red}")
print(f"ROI中是否包含黑色: {contains_black}")

#可视化结果（可选）
white_result = cv2.bitwise_and(roi, roi, mask=white_mask)
red_result = cv2.bitwise_and(roi, roi, mask=red_mask)
black_result = cv2.bitwise_and(roi, roi, mask=black_mask)

#显示图像和掩码（可选）
cv2.imshow('White Mask', white_mask)
cv2.imshow('Red Mask', red_mask)
cv2.imshow('Black Mask', black_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()