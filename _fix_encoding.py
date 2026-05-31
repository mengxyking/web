import glob

OLD = '''def get_random_line_from_file(file_path):
    """
    从指定的文本文件中随机选择并返回一行。

    :param file_path: 文本文件的路径
    :return: 随机选择的一行文本
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 读取所有行并存储在一个列表中
            lines = file.readlines()

        # 如果文件不为空，随机选择一行
        if lines:
            random_line = random.choice(lines)
            return random_line.strip()  # 去除行尾的换行符
        else:
            return None  # 或者抛出一个异常，表示文件为空
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")'''

NEW = '''def get_random_line_from_file(file_path):
    """
    从指定的文本文件中随机选择并返回一行。
    自动检测编码（utf-8-sig / gbk / gb18030 / utf-8），失败时返回空字符串。

    :param file_path: 文本文件的路径
    :return: 随机选择的一行文本，失败时返回空字符串
    """
    for enc in ("utf-8-sig", "gbk", "gb18030", "utf-8", "latin-1"):
        try:
            with open(file_path, "r", encoding=enc) as file:
                lines = [l.strip() for l in file.readlines() if l.strip()]
            if lines:
                return random.choice(lines)
            return ""
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return ""
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
            return ""
    return ""'''

files = glob.glob("**/*.py", recursive=True)
changed = 0
for f in files:
    try:
        content = open(f, "r", encoding="utf-8").read()
        if OLD in content:
            open(f, "w", encoding="utf-8").write(content.replace(OLD, NEW, 1))
            print(f"✓  {f}")
            changed += 1
    except Exception as e:
        print(f"✗  {f}: {e}")

print(f"\n共修改 {changed} 个文件")
