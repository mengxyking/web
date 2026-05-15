def find_matching_lines(file_path, target_string):
    # 提取目标字符串的前三个字符和后两个字符
    prefix = target_string[:3]
    suffix = target_string[-2:]

    # 存储匹配行的列表
    matching_lines = []

    # 打开文件并逐行读取
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 去除行尾的换行符
            stripped_line = line.strip()
            # 检查行是否同时包含前缀和后缀
            if prefix in stripped_line and suffix in stripped_line:
                matching_lines.append(stripped_line)
                return stripped_line




# 示例使用
file_path = r'C:\Users\Administrator\Desktop\config\需要添加的联系人\phone.txt'  # 替换为你的txt文件路径
target_string = '188*******33'  # 替换为你的目标字符串

matching_lines = find_matching_lines(file_path, target_string)
print(matching_lines)