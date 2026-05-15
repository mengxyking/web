import cv2
import pytesseract


def tesseract_ocr_demo(image_path):
    """
    使用Tesseract OCR进行文字识别（CPU）
    :param image_path: 图片路径
    :return: 识别出的文字内容
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图片：{image_path}")

    # 将图片转换为灰度图（有助于提高识别效果）
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 执行OCR识别
    text = pytesseract.image_to_string(gray, lang='chi_sim')  # 默认识别英文，可根据需求修改为'chi_sim'（简体中文）等
    return text


if __name__ == "__main__":
    # 替换为你的测试图片路径，支持常见的图片格式如jpg、png等
    test_image_path = r"C:\Users\Administrator\Desktop\QQ20251018-194215.png"
    result = tesseract_ocr_demo(test_image_path)
    print("识别结果：")
    print(result)