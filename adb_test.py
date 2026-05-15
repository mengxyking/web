import subprocess
def get_connected_devices_ip():
    """获取已连接的安卓设备列表"""
    try:
        # 运行 adb devices 命令
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 检查命令是否成功执行
        if result.returncode != 0:
            print(f"Error running adb devices: {result.stderr}")
            return []

        # 解析输出
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
        devices = [str(line.split('\t')[0]).split(".")[-1].split(":")[0] for line in lines if line.strip() and line.split('\t')[1] == 'device']
        return devices
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
#print(get_connected_devices_ip())
import re

def extract_first_parentheses_content(s):
    # 使用正则表达式匹配第一个括号内的内容
    match = re.search(r'\((.*?)\)', s)
    if match:
        # 返回匹配到的内容（不包括括号）
        return match.group(1)
    else:
        # 如果没有找到匹配的内容，返回 None 或者你可以抛出一个异常
        return None

# 示例字符串
example_string = "这是一个测试字符串，包含(一些内容) 和其他(内容)"

# 提取第一个括号内的内容
result = extract_first_parentheses_content(example_string)

print(result)  # 输出: 一些内容