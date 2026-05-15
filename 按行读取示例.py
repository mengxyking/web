def read_specific_line(line_number):
    file_path = 'tz_config.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 通过生成器表达式读取指定行，并捕获 StopIteration 异常
            lines = (line for index, line in enumerate(file, start=1) if index == line_number)
            # 使用 next() 尝试获取第一（也是唯一）个值，如果生成器为空则返回 None
            return next(lines, None)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# 示例使用
file_path = 'tz_config.txt'
line_number = 2
result = read_specific_line(line_number).strip()
print(result.split(","))
if result:
    print(f"Line {line_number}: {result}")
else:
    print(f"Line {line_number} does not exist in the file.")