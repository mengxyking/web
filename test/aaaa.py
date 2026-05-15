import os


def get_next_img_name_img(folder_path, img_name):
    """
    自动给重复文件加 _a _b 后缀
    :param folder_path: 文件夹路径
    :param img_name: 原始文件名 如 test.png
    :return: 不重复的文件名 test.png / test_a.png / test_b.png
    """
    # 拆分文件名和后缀
    name, ext = os.path.splitext(img_name)
    ext = ext.lower()

    # 候选后缀：空 → a → b → c ...
    suffixes = ['', '_a', '_b', '_c', '_d', '_e']

    for suf in suffixes:
        # 拼接新文件名
        new_name = f"{name}{suf}{ext}"
        # 拼接完整路径判断是否存在
        full_path = os.path.join(folder_path, new_name)
        if not os.path.exists(full_path):
            return new_name

    # 兜底（最多到_e，一般用不到）
    return f"{name}"


print(get_next_img_name_img(r"E:\360MoveData\Users\Administrator\Desktop\话术配置\1-8-1-新","韵达快递 321032689838358.png"))