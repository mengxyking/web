import threading
import os  # 新增：用于遍历文件夹
from typing import Optional
import numpy as np

file_read_lock = threading.Lock()
ocr_lock = threading.Lock()
current_scroll_position = 0
import time
import cv2

# 抖音养号+微信加好友脚本
black_zhubo = []
alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()

from typing import Tuple, Optional


def safe_load_image(image_path: str) -> Optional[np.ndarray]:
    """
    线程安全的图片加载函数（适配不同大图、兼容中文路径）
    :param image_path: 任意图片路径（支持中文）
    :return: 图片数组（BGR格式），失败返回None
    """
    # 加锁读取文件（即使不同文件，也避免同时打开过多句柄）
    with file_read_lock:
        try:
            # 解决cv2.imread无法读取中文路径的问题
            img_data = np.fromfile(image_path, dtype=np.uint8)
            if img_data.size == 0:
                raise ValueError("文件为空或无法读取")

            # 解码图片（IMREAD_COLOR：读取彩色图，忽略透明通道）
            img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("图片解码失败（格式错误/损坏）")
            return img
        except Exception as e:
            print(f"❌ 加载图片失败 {image_path}：{str(e)}")
            return None


def find_target_by_template(
        big_image_path: str,  # 待搜索的大图路径（每个线程可能不同）
        template_image_path: str,  # 目标模板小图路径
        threshold: float = 0.7,  # 匹配阈值（0-1，越高越精准）
        save_marked_image: bool = True,  # 是否保存标记后的图片
        show_image: bool = False  # 是否显示标记后的图片
) -> tuple | None:
    """
    适配「多线程读取不同大图」的模板匹配函数（线程安全）
    功能：1. 在匹配位置绘制红色方块标记 2. 返回匹配值最高的目标位置
    """
    # 1. 线程安全加载图片（替代原cv2.imread）
    time.sleep(0.2)
    big_img = safe_load_image(big_image_path)
    template_img = safe_load_image(template_image_path)

    # 校验图片加载结果
    if big_img is None:
        raise ValueError(f"无法读取大图：{big_image_path}，请检查路径/文件完整性")
    if template_img is None:
        raise ValueError(f"无法读取模板图：{template_image_path}，请检查路径/文件完整性")

    # 2. 获取模板图宽高
    template_h, template_w = template_img.shape[:2]

    # 3. 执行模板匹配（纯内存操作，线程安全）
    result = cv2.matchTemplate(big_img, template_img, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    # 创建大图的副本用于绘制标记，避免修改原图
    marked_img = big_img.copy()

    # 4. 遍历所有匹配点，记录坐标和匹配值
    match_info = []
    if len(locations[0]) > 0:
        # 遍历所有匹配位置，记录坐标和对应的匹配值
        for y, x in zip(locations[0], locations[1]):
            match_value = result[y, x]  # 获取该位置的匹配值
            center_x = x + template_w // 2
            center_y = y + template_h // 2
            match_info.append({
                "x": x,
                "y": y,
                "center_x": center_x,
                "center_y": center_y,
                "match_value": match_value
            })
            # 绘制所有匹配位置的红色方块
            cv2.rectangle(
                marked_img,
                (x, y),  # 左上角
                (x + template_w, y + template_h),  # 右下角
                (0, 0, 255),  # 红色
                2  # 线条宽度
            )
            print(f"匹配位置：中心坐标({center_x}, {center_y})，匹配值：{match_value:.4f}")

        # 5. 找到匹配值最高的那个目标
        best_match = max(match_info, key=lambda item: item["match_value"])
        # 为最佳匹配位置绘制更粗的绿色方块，突出显示
        cv2.rectangle(
            marked_img,
            (best_match["x"], best_match["y"]),
            (best_match["x"] + template_w, best_match["y"] + template_h),
            (0, 255, 0),  # 绿色
            4  # 更粗的线条，突出最佳匹配
        )
        print(f"\n🏆 最佳匹配位置：中心坐标({best_match['center_x']}, {best_match['center_y']})，匹配值：{best_match['match_value']:.4f}")

        # 6. 保存标记后的图片
        if save_marked_image:
            try:
                # 构造保存路径（在原图路径后添加"_marked_模板文件名"）
                template_name = os.path.basename(template_image_path).rsplit('.', 1)[0]
                save_path = big_image_path.rsplit('.', 1)[0] + f"_marked_{template_name}.png"
                # 解决中文路径保存问题
                cv2.imencode('.png', marked_img)[1].tofile(save_path)
                print(f"✅ 标记后的图片已保存至：{save_path}")
            except Exception as e:
                print(f"❌ 保存标记图片失败：{str(e)}")

        # 7. 显示标记后的图片（可选）
        if show_image:
            cv2.namedWindow("Matched Image", cv2.WINDOW_NORMAL)
            cv2.imshow("Matched Image", marked_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # 返回最佳匹配坐标
        return (best_match["center_x"], best_match["center_y"])
    else:
        print(f"❌ 模板 {os.path.basename(template_image_path)} 未匹配到任何目标")
        return None


def find_target_in_template_folder(
        big_image_path: str,
        template_folder_path: str,
        threshold: float = 0.7,
        save_marked_image: bool = True,
        show_image: bool = False
) -> tuple | None:
    """
    遍历指定文件夹内所有图片模板，依次匹配大图，找到第一个匹配成功的模板并返回坐标
    :param big_image_path: 大图路径
    :param template_folder_path: 模板小图所在文件夹路径
    :param threshold: 匹配阈值
    :param save_marked_image: 是否保存标记图
    :param show_image: 是否显示标记图
    :return: 第一个匹配成功的坐标，全部失败返回None
    """
    # 1. 校验模板文件夹是否存在
    if not os.path.exists(template_folder_path):
        print(f"❌ 模板文件夹不存在：{template_folder_path}")
        return None

    # 2. 获取文件夹内所有图片文件（支持常见图片格式）
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    template_files = []
    for file in os.listdir(template_folder_path):
        # 过滤非图片文件，忽略大小写
        if file.lower().endswith(image_extensions):
            template_files.append(os.path.join(template_folder_path, file))

    if not template_files:
        print(f"❌ 模板文件夹 {template_folder_path} 内未找到任何图片文件")
        return None

    print(f"\n📁 找到 {len(template_files)} 个模板文件，开始依次匹配...")
    print("template_files=",template_files)
    # 3. 遍历所有模板文件，依次匹配
    for idx, template_path in enumerate(template_files, 1):
        print(f"\n========== 正在匹配第 {idx}/{len(template_files)} 个模板：{os.path.basename(template_path)} ==========")
        try:
            # 执行匹配
            match_result = find_target_by_template(
                big_image_path=big_image_path,
                template_image_path=template_path,
                threshold=threshold,
                save_marked_image=save_marked_image,
                show_image=show_image
            )
            # 如果匹配成功，立即返回坐标
            if match_result is not None:
                print(f"\n✅ 匹配成功！使用模板：{os.path.basename(template_path)}，坐标：{match_result}")
                return match_result
        except Exception as e:
            print(f"❌ 匹配模板 {os.path.basename(template_path)} 时出错：{str(e)}")
            continue

    # 4. 所有模板都匹配失败
    print(f"\n❌ 所有 {len(template_files)} 个模板均未匹配到目标")
    return None


# ====================== 调用示例 ======================
if __name__ == "__main__":
    # 配置参数
    BIG_IMAGE_PATH = r"E:\360MoveData\Users\Administrator\Desktop\36_2026_03_22_20_16_18_5225.png"
    # 替换为你的模板小图所在文件夹路径（里面放所有要匹配的小图）
    TEMPLATE_FOLDER_PATH = r"fudai_path"
    MATCH_THRESHOLD = 0.7  # 匹配阈值，可根据需要调整

    # 执行批量模板匹配
    final_result = find_target_in_template_folder(
        big_image_path=BIG_IMAGE_PATH,
        template_folder_path=TEMPLATE_FOLDER_PATH,
        threshold=MATCH_THRESHOLD,
        save_marked_image=True,
        show_image=False
    )

    # 输出最终结果
    print(f"\n📌 最终结果：{final_result}")