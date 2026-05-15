import cv2
import numpy as np
from typing import Tuple, Optional


def find_button_in_large(
        large_image_path: str,  # 你的大图路径
        small_image_path: str,  # 你的小图（一键发表评论按钮）路径
        confidence: float = 0.9,  # 按钮特征明显，提高置信度
        get_center: bool = True,
        draw_mark: bool = True,
        save_marked_path: str = "marked_button.png"
) -> Optional[Tuple[int, int]]:
    """
    专门优化：匹配底部红色“一键发表评论”按钮，坐标更精准
    """
    # 1. 读取彩色图（按钮是红底白字，彩色匹配更准）
    large_img = cv2.imread(large_image_path)
    small_img = cv2.imread(small_image_path)

    if large_img is None:
        raise ValueError(f"大图读取失败：{large_image_path}")
    if small_img is None:
        raise ValueError(f"小图读取失败：{small_image_path}")

    small_h, small_w = small_img.shape[:2]
    large_h, large_w = large_img.shape[:2]

    if small_h > large_h or small_w > large_w:
        raise ValueError("小图尺寸大于大图，无法匹配")

    # 2. 模板匹配（用 TM_CCOEFF_NORMED，对文字/按钮匹配最准）
    result = cv2.matchTemplate(large_img, small_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 3. 置信度判断（按钮特征强，阈值设高避免误匹配）
    if max_val < confidence:
        return None

    # 4. 计算坐标（直接在大图上，无需裁剪偏移）
    top_left_x, top_left_y = max_loc
    bottom_right_x = top_left_x + small_w
    bottom_right_y = top_left_y + small_h

    if get_center:
        center_x = top_left_x + small_w // 2
        center_y = top_left_y + small_h // 2
        target_pos = (center_x, center_y)
    else:
        target_pos = (top_left_x, top_left_y)

    # 5. 标记匹配位置（绿色框+中心点，更醒目）
    if draw_mark:
        # 画绿色矩形框（包围按钮）
        cv2.rectangle(
            large_img,
            (top_left_x, top_left_y),
            (bottom_right_x, bottom_right_y),
            (0, 255, 0),  # 绿色（BGR）
            3
        )
        # 画绿色中心点
        if get_center:
            cv2.circle(
                large_img,
                (center_x, center_y),
                8,
                (0, 255, 0),
                -1
            )
            # 标注坐标
            cv2.putText(
                large_img,
                f"({center_x}, {center_y})",
                (center_x + 15, center_y + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
        cv2.imwrite(save_marked_path, large_img)
        print(f"✅ 标记图已保存：{save_marked_path}")

    return target_pos


# ---------------------- 测试（替换成你的路径） ----------------------
if __name__ == "__main__":
    # 把下面路径改成你电脑上的实际路径
    LARGE_IMG_PATH = r"E:\360MoveData\Users\Administrator\Desktop\20260307173346_162_7.jpg"  # 待搜索的大图
    SMALL_IMG_PATH = r"E:\360MoveData\Users\Administrator\Desktop\QQ20260307-230005.png"  # 要找的目标小模板图
    SAVE_MARKED_PATH = r"E:\360MoveData\Users\Administrator\Desktop\marked_image.png"  # 标记后保存路径

    try:
        pos = find_button_in_large(
            large_image_path=LARGE_IMG_PATH,
            small_image_path=SMALL_IMG_PATH,
            confidence=0.7,  # 匹配不到就降到0.8，误匹配就升到0.9
            get_center=True,
            draw_mark=True,
            save_marked_path=SAVE_MARKED_PATH
        )

        if pos:
            print(f"✅ 精准找到按钮！中心坐标：{pos}")
            x, y = pos
            print(f"横坐标x：{x}，纵坐标y：{y}")
        else:
            print("❌ 未匹配到按钮，可尝试降低confidence（比如0.8）")
    except Exception as e:
        print(f"❌ 错误：{e}")