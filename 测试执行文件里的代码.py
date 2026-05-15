# main_script.py
import os

# 假设code_to_execute.py在同一目录下
file_path = 'tz_daoxu.py'

# 检查文件是否存在
if os.path.isfile(file_path):
    with open(file_path, 'r',encoding = "utf-8") as file:
        code = file.read()

    # 使用exec()执行代码（不推荐在生产环境中这样做，因为它不安全）
    # 这里的exec()是在全局命名空间中执行的，所以它可以访问main_script.py中定义的变量和函数
    # 同时，由于它是在当前进程中执行的，所以它也可以访问和操作GUI元素（如果有的话）
    exec(code)
else:
    print(f"File {file_path} does not exist.")