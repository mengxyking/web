from PIL import Image, ImageDraw
import numpy as np

# 打开图像文件
image_path = r'C:\Users\Administrator\Desktop\111.png'  # 替换为你的图像路径
image = Image.open(image_path)

# 确保图像是RGB模式
if image.mode != 'RGB':
    image = image.convert('RGB')

# 将图像转换为NumPy数组
image_array = np.array(image)

# 定义黑色背景的颜色阈值（这里假设黑色为(0, 0, 0)，但可能需要根据实际情况调整）
black_threshold = (30, 30, 30)  # 由于图像可能不是完全的黑色，所以设置一个容忍度

# 创建一个与原图像大小相同的布尔数组，用于标记非黑色像素
non_black_mask = np.all(image_array > black_threshold, axis=-1)

# 使用形态学操作（如膨胀和腐蚀）来清理和连接非黑色区域（可选）
from scipy.ndimage import binary_dilation, binary_erosion

# 膨胀操作可以帮助连接紧密的非黑色区域
dilated_mask = binary_dilation(non_black_mask, structure=np.ones((3,3),np.uint8))

# 腐蚀操作可以帮助去除小的噪声点
cleaned_mask = binary_erosion(dilated_mask, structure=np.ones((3,3),np.uint8))

# 查找轮廓（这里使用OpenCV库，因为Pillow没有直接的轮廓查找功能）
import cv2

# 将布尔数组转换为OpenCV可以处理的格式（0和255）
opencv_mask = (cleaned_mask * 255).astype(np.uint8)

# 查找轮廓
contours, _ = cv2.findContours(opencv_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 遍历轮廓并绘制矩形框（这里只是为了可视化，实际上你可以根据需要处理这些轮廓）
print("=================>",len(contours))
for contour in contours:
    print("------------------------------------")
    # 获取轮廓的边界框
    x, y, w, h = cv2.boundingRect(contour)
    print(x, y, w, h)
    # 在原图像上绘制矩形框（使用Pillow，因为OpenCV处理RGB图像时颜色顺序不同）
    image_draw = Image.fromarray(cv2.cvtColor(cv2.merge([opencv_mask, opencv_mask, opencv_mask]), cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_draw)
    draw.rectangle([(x, y), (x+w, y+h)], outline="red")

# 显示结果图像
image_draw.show()

# 注意：上面的代码中，我们实际上并没有直接“分割”出每一个方格，而是找到了它们的边界框。
# 如果你需要进一步的分割，你可能需要根据这些边界框裁剪出原始的图像部分。