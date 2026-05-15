#!/Users/4paradigm/PycharmProjects/PythonProject/Open-AutoGLM/.venv/bin/python
"""
直播间福袋坐标检测工具
支持：颜色识别、模板匹配、OCR 三种方案
适用于 ADB 截图 + 坐标点击自动化场景
"""

import cv2
import numpy as np
from pathlib import Path


# ──────────────────────────────────────────────
# 方案一：HSV 颜色过滤 + 轮廓检测（最快，无需依赖）
# ──────────────────────────────────────────────

def detect_by_color(image: np.ndarray, debug: bool = False) -> list[tuple[int, int, int, int]]:
    """
    通过颜色识别福袋（红/橙色圆形按钮）
    返回: [(x, y, w, h), ...] 候选区域列表，按面积从大到小排序
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 红色在 HSV 中跨越 0 和 180 附近，需要两段合并
    red_lower1 = np.array([0,   120, 100])
    red_upper1 = np.array([10,  255, 255])
    red_lower2 = np.array([160, 120, 100])
    red_upper2 = np.array([180, 255, 255])

    # 橙色范围
    orange_lower = np.array([10, 120, 100])
    orange_upper = np.array([25, 255, 255])

    mask_r1     = cv2.inRange(hsv, red_lower1, red_upper1)
    mask_r2     = cv2.inRange(hsv, red_lower2, red_upper2)
    mask_orange = cv2.inRange(hsv, orange_lower, orange_upper)

    mask = cv2.bitwise_or(mask_r1, mask_r2)
    mask = cv2.bitwise_or(mask, mask_orange)

    # 形态学去噪：先腐蚀再膨胀
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 300:          # 过滤太小的噪点
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / h if h > 0 else 0
        if 0.3 < aspect < 3.5:  # 过滤过于细长的区域
            results.append((x, y, w, h))

    results.sort(key=lambda r: r[2] * r[3], reverse=True)

    if debug:
        vis = image.copy()
        for (x, y, w, h) in results[:5]:
            cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cx, cy = x + w // 2, y + h // 2
            cv2.circle(vis, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(vis, f"({cx},{cy})", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite("debug_color.jpg", vis)
        cv2.imwrite("debug_mask.jpg",  mask)
        print(f"[颜色识别] 找到 {len(results)} 个候选区域，已保存调试图")

    return results


def get_center(bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    x, y, w, h = bbox
    return x + w // 2, y + h // 2


# ──────────────────────────────────────────────
# 方案二：模板匹配（精确，需要预先截取福袋模板图）
# ──────────────────────────────────────────────

def detect_by_template(image: np.ndarray, template_path: str,
                        threshold: float = 0.75,
                        debug: bool = False) -> list[tuple[int, int, int, int]]:
    """
    模板匹配方式检测福袋
    template_path: 预先截取的福袋小图路径
    threshold: 匹配置信度阈值（0~1，越高越严格）
    返回: [(x, y, w, h), ...]
    """
    template = cv2.imread(template_path)
    if template is None:
        raise FileNotFoundError(f"模板图不存在: {template_path}")

    # 灰度匹配更稳定
    gray_img = cv2.cvtColor(image,    cv2.COLOR_BGR2GRAY)
    gray_tpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    th, tw = gray_tpl.shape[:2]
    result = cv2.matchTemplate(gray_img, gray_tpl, cv2.TM_CCOEFF_NORMED)

    locations = np.where(result >= threshold)
    results   = []

    for pt in zip(*locations[::-1]):  # (x, y)
        results.append((pt[0], pt[1], tw, th))

    # NMS：去除重叠框
    results = _nms(results, iou_threshold=0.3)

    if debug:
        vis = image.copy()
        for (x, y, w, h) in results:
            cv2.rectangle(vis, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imwrite("debug_template.jpg", vis)
        print(f"[模板匹配] 找到 {len(results)} 个匹配区域")

    return results


def _nms(boxes: list, iou_threshold: float = 0.3) -> list:
    """简单非极大值抑制，去除重叠检测框"""
    if not boxes:
        return []
    boxes  = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
    keep   = []
    while boxes:
        best = boxes.pop(0)
        keep.append(best)
        boxes = [b for b in boxes if _iou(best, b) < iou_threshold]
    return keep


def _iou(a, b) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0, min(ax+aw, bx+bw) - max(ax, bx))
    iy = max(0, min(ay+ah, by+bh) - max(ay, by))
    inter = ix * iy
    union = aw*ah + bw*bh - inter
    return inter / union if union > 0 else 0


# ──────────────────────────────────────────────
# 方案三：OCR 文字识别（识别"福袋"文字最可靠）
# ──────────────────────────────────────────────

def detect_by_ocr(image: np.ndarray, debug: bool = False) -> list[tuple[int, int, int, int]]:
    """
    使用 PaddleOCR 识别"福袋"文字坐标
    需要安装：pip install paddleocr paddlepaddle
    返回: [(x, y, w, h), ...]
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("[OCR] 未安装 PaddleOCR，跳过。安装命令：pip install paddleocr paddlepaddle")
        return []

    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    ocr_result = ocr.ocr(image, cls=True)

    results = []
    keywords = ["福袋", "fudai", "抢福袋", "领福袋"]

    for line in (ocr_result[0] or []):
        box, (text, confidence) = line
        if confidence < 0.5:
            continue
        if any(kw in text for kw in keywords):
            pts = np.array(box, dtype=np.int32)
            x, y, w, h = cv2.boundingRect(pts)
            results.append((x, y, w, h))
            if debug:
                print(f"[OCR] 找到文字「{text}」置信度={confidence:.2f}  坐标=({x},{y},{w},{h})")

    return results


# ──────────────────────────────────────────────
# 组合策略：颜色优先，OCR 兜底
# ──────────────────────────────────────────────

def find_fudai(image_path: str,
               template_path: str | None = None,
               use_ocr: bool = False,
               debug: bool = False) -> tuple[int, int] | None:
    """
    主入口：自动选择最优方案，返回福袋中心坐标 (x, y)
    image_path:    截图路径
    template_path: 模板图路径（可选，提供后优先使用模板匹配）
    use_ocr:       是否启用 OCR 兜底（需要安装 paddleocr）
    debug:         是否保存调试图片
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"截图不存在: {image_path}")

    print(f"[INFO] 图像尺寸: {image.shape[1]}x{image.shape[0]}")

    # 1. 模板匹配（最精确）
    if template_path and Path(template_path).exists():
        print("[方案] 使用模板匹配")
        results = detect_by_template(image, template_path, debug=debug)
        if results:
            cx, cy = get_center(results[0])
            print(f"[结果] 福袋坐标: ({cx}, {cy})")
            return cx, cy

    # 2. 颜色识别
    print("[方案] 使用颜色识别")
    results = detect_by_color(image, debug=debug)
    if results:
        # 福袋通常在屏幕左下角，优先选择靠近底部的候选
        h = image.shape[0]
        bottom_results = [r for r in results if r[1] + r[3] > h * 0.5]
        target = bottom_results[0] if bottom_results else results[0]
        cx, cy = get_center(target)
        print(f"[结果] 福袋坐标: ({cx}, {cy})  区域: {target}")
        return cx, cy

    # 3. OCR 兜底
    if use_ocr:
        print("[方案] 颜色识别未找到，使用 OCR 识别")
        results = detect_by_ocr(image, debug=debug)
        if results:
            cx, cy = get_center(results[0])
            print(f"[结果] 福袋坐标: ({cx}, {cy})")
            return cx, cy

    print("[结果] 未找到福袋")
    return None


# ──────────────────────────────────────────────
# ADB 集成：截图 → 识别 → 点击
# ──────────────────────────────────────────────

def adb_screenshot(save_path: str = "/tmp/screen.png") -> str:
    """通过 ADB 截取手机屏幕"""
    import subprocess
    subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
    subprocess.run(["adb", "pull", "/sdcard/screen.png", save_path],          check=True)
    return save_path


def adb_tap(x: int, y: int):
    """通过 ADB 点击坐标"""
    import subprocess
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
    print(f"[ADB] 已点击坐标: ({x}, {y})")


def auto_click_fudai(template_path: str | None = None, debug: bool = False):
    """一键：截图 → 识别福袋 → 自动点击"""
    print("正在截取手机屏幕...")
    screenshot = adb_screenshot()

    coord = find_fudai(screenshot, template_path=template_path,
                       use_ocr=False, debug=debug)
    if coord:
        adb_tap(*coord)
    else:
        print("未找到福袋，请检查手机屏幕或调整颜色参数")


# ──────────────────────────────────────────────
# 调试工具：分析图片中的颜色分布
# ──────────────────────────────────────────────

def analyze_color(image_path: str, click_x: int, click_y: int, radius: int = 10):
    """
    分析指定坐标附近的 HSV 颜色值，用于调整颜色阈值
    用法：先手动找到福袋位置，传入坐标，查看 HSV 范围
    """
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    x1 = max(0, click_x - radius)
    y1 = max(0, click_y - radius)
    x2 = min(w, click_x + radius)
    y2 = min(h, click_y + radius)

    roi  = img[y1:y2, x1:x2]
    hsv  = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    print(f"区域 ({x1},{y1}) ~ ({x2},{y2}) 的 HSV 统计：")
    print(f"  H: min={hsv[:,:,0].min()}  max={hsv[:,:,0].max()}  mean={hsv[:,:,0].mean():.1f}")
    print(f"  S: min={hsv[:,:,1].min()}  max={hsv[:,:,1].max()}  mean={hsv[:,:,1].mean():.1f}")
    print(f"  V: min={hsv[:,:,2].min()}  max={hsv[:,:,2].max()}  mean={hsv[:,:,2].mean():.1f}")


# ──────────────────────────────────────────────
# 使用示例
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # if len(sys.argv) < 2:
    #     print("用法:")
    #     print("  # 检测本地截图")
    #     print("  python fudai_detector.py <截图路径> [--debug]")
    #     print()
    #     print("  # 自动截图并点击")
    #     print("  python fudai_detector.py --auto [--debug]")
    #     print()
    #     print("  # 分析颜色（调参用）")
    #     print("  python fudai_detector.py --color <图片> <x> <y>")
    #     sys.exit(0)

    # if sys.argv[1] == "--auto":
    #     debug = "--debug" in sys.argv
    #     auto_click_fudai(debug=debug)

    # elif sys.argv[1] == "--color" and len(sys.argv) >= 5:
    #     analyze_color(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))

    # else:
    #     img_path = sys.argv[1]
    #     debug    = "--debug" in sys.argv
    #     coord    = find_fudai(img_path, debug=debug)
    #     if coord:
    #         print(f"福袋中心坐标: x={coord[0]}, y={coord[1]}")

    debug = True
    coord = find_fudai("/Users/4paradigm/Desktop/211111.png", debug=debug)
    if coord:
        print(f"福袋中心坐标: x={coord[0]}, y={coord[1]}")
