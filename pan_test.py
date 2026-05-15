import os

def create_folder_on_current_disk():
    # 获取当前代码文件所在的路径
    current_script_path = os.path.abspath(__file__)
    # 提取当前代码所在的磁盘（如 'C:\\' 或 'D:\\'）
    current_disk = os.path.splitdrive(current_script_path)[0] + os.sep
    # 拼接新建文件夹的路径（以磁盘根目录为例）
    folder_path = os.path.join(current_disk, "dy_temp")
    # 新建文件夹
    try:
        os.makedirs(folder_path)
        print(f"已在 {current_disk} 上成功创建文件夹：{folder_path}")
    except FileExistsError:
        print(f"文件夹 {folder_path} 已存在")
    except Exception as e:
        print(f"创建文件夹失败：{e}")
    return folder_path

# 执行函数
#create_folder_on_current_disk()

import random


def generate_array(data):
    # 原始数据
    # 解析各组数据为列表
    groups = []
    for item in data:
        key = next(iter(item))
        groups.append(item[key].split(','))

    # 第一组作为起始
    result = groups[0].copy()

    # 可选的其他组（第二到第五组）
    other_groups = groups[1:]

    # 随机添加其他组数据直到长度不小于50
    while len(result) < 50:
        # 随机选择一个其他组
        selected_group = random.choice(other_groups)
        # 添加到结果中
        result.extend(selected_group)

    return result

data = [
        {'diyizu': '1跟,反,跟,反,跟,反,跟,反,跟,反,跟,反'},
        {'dierzu': '跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反'},
        {'disanzu': '跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反'},
        {'disizu': '跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反'},
        {'diwuzu': '跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反,跟,反'}
    ]
# 示例使用
generated = generate_array(data)
print(generated)
print(f"生成的数组长度: {len(generated)}")