import cv2
import numpy as np
from PIL import Image


def find_target_by_template(
        big_image_path: str,  # 待搜索的大图路径
        template_image_path: str,  # 目标模板小图路径
        threshold: float = 0.6  # 匹配阈值（0-1，越高越精准）
) -> tuple | None:
    """
    通过模板匹配在指定图片中查找目标区域，返回中心点坐标
    :param big_image_path: 原始大图的文件路径（如 "test.png"）
    :param template_image_path: 目标模板图的文件路径
    :param threshold: 匹配置信度阈值，建议0.8以上
    :return: 目标中心点坐标 (x, y)，未找到返回None
    """
    # 1. 读取图片
    big_img = cv2.imread(big_image_path)
    template_img = cv2.imread(template_image_path)

    # 校验图片是否读取成功
    if big_img is None:
        raise ValueError(f"无法读取大图：{big_image_path}，请检查路径是否正确")
    if template_img is None:
        raise ValueError(f"无法读取模板图：{template_image_path}，请检查路径是否正确")

    # 2. 获取模板图的宽高
    template_h, template_w = template_img.shape[:2]

    # 3. 执行模板匹配
    result = cv2.matchTemplate(big_img, template_img, cv2.TM_CCOEFF_NORMED)
    # 找到所有匹配度超过阈值的位置
    locations = np.where(result >= threshold)

    # 4. 处理匹配结果（取第一个匹配到的位置，返回中心点）
    if len(locations[0]) > 0:
        # 获取第一个匹配点的左上角坐标
        top_left_y, top_left_x = locations[0][0], locations[1][0]
        # 计算中心点坐标（x: 横向，y: 纵向）
        center_x = top_left_x + template_w // 2
        center_y = top_left_y + template_h // 2
        return (center_x, center_y)
    else:
        return None


# ------------------- 测试示例 -------------------
if __name__ == "__main__":
    # 替换成你自己的图片路径
    BIG_IMAGE_PATH = r"E:\360MoveData\Users\Administrator\Desktop\QQ20260307-175200.png"  # 待搜索的大图
    TEMPLATE_PATH = r"D:\QQ20260307-172711.png"  # 要找的目标小模板图

    try:
        target_pos = find_target_by_template(BIG_IMAGE_PATH, TEMPLATE_PATH)
        if target_pos:
            print(f"找到目标！中心点坐标：{target_pos}")
        else:
            print("未找到目标（匹配度低于阈值）")
    except Exception as e:
        print(f"执行出错：{e}")