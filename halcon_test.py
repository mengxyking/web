import halcon as ha


def halcon_image_processing(image_path):
    try:
        # 1. 读取本地图像
        image = ha.read_image(image_path)

        # 2. 转换为灰度图（彩色图必须先灰度化）
        gray_image = ha.rgb1_to_gray(image)

        # 3. 高斯滤波去噪，核大小5x5
        smooth_image = ha.gauss_filter(gray_image, 5)

        # 4. 全局阈值分割，提取灰度值128-255的亮区域
        region = ha.threshold(smooth_image, 128, 255)

        # 5. 形态学处理：去除小区域噪声，优化分割结果
        region_clean = ha.opening_circle(region, 3.5)

        # 6. 计算目标区域的面积和中心坐标
        area, row, column = ha.area_center(region_clean)

        # 7. 创建显示窗口并展示结果
        window = ha.open_window(0, 0, 640, 480, 'visible', '')
        ha.set_window_attr(window, 0, 'background_color', 'black')
        ha.disp_obj(image, window)
        ha.disp_obj(region_clean, window)

        # 8. 输出计算结果
        print(f"目标区域面积: {area:.2f}")
        print(f"目标区域中心坐标: ({row:.2f}, {column:.2f})")

        # 等待按键关闭窗口
        input("按下Enter键关闭窗口...")

    except Exception as e:
        print(f"程序执行出错: {str(e)}")
    finally:
        # 9. 释放所有资源
        ha.close_window(window)
        print("资源已释放")


if __name__ == "__main__":
    # 替换为你的图像路径（支持png/jpg/bmp等格式）
    IMAGE_PATH = "test_image.png"
    halcon_image_processing(IMAGE_PATH)