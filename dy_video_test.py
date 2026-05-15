import os
import random
import pickle


def get_random_pkl_file_in_directory(directory):
    # 获取目录下所有 .pkl 文件的列表
    pkl_files = [f for f in os.listdir(directory) if f.endswith('.pkl')]

    # 如果没有 .pkl 文件，则直接返回 False
    if not pkl_files:
        return False

    # 循环直到找到一个满足条件的文件或者所有文件都不满足条件
    while pkl_files:
        # 随机选择一个 .pkl 文件
        chosen_file = random.choice(pkl_files)
        file_path = os.path.join(directory, chosen_file)

        # 从列表中移除已选择的文件，以便在下次循环时不再选择它
        pkl_files.remove(chosen_file)

        # 尝试读取文件内容
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)

            # 检查数据是否满足条件
            if 'TONGJI' in data and 'BIG_COUNT' in data and isinstance(data['TONGJI'], (int, float)) and isinstance(
                    data['BIG_COUNT'], (int, float)):
                if data['TONGJI'] <= data['BIG_COUNT']:
                    return chosen_file
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    # 如果没有文件满足条件，则返回 False
    return False


import pickle


def update_pkl_file(file_path, key, new_value):
    # 尝试读取 pkl 文件
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)

        # 检查 key 是否存在于字典中
        if key in data:
            # 更新字典中的值
            data[key] = new_value

            # 将修改后的数据写回到 pkl 文件中
            with open(file_path, 'wb') as file:
                pickle.dump(data, file)

            print(f"Successfully updated {key} to {new_value} in {file_path}")
            return True
        else:
            print(f"Key {key} not found in {file_path}")
            return False

    except Exception as e:
        print(f"Error reading or writing to {file_path}: {e}")
        return False


# 示例用法
file_path = "task_config/"+'CeioKu93.pkl'
key_to_update = 'TONGJI'
new_value = 1500088

result = update_pkl_file(file_path, key_to_update, new_value)
if result:
    print("Update successful.")
else:
    print("Update failed.")

# 示例用法
directory = 'task_config'
result = get_random_pkl_file_in_directory(directory)
print(result)