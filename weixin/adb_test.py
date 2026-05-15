import subprocess


def run_adb_command(command, connect_target):
    """
    执行ADB命令，失败时尝试重新连接设备后再次执行

    参数:
        command (list): ADB命令列表（如["adb", "devices"]）
        connect_target (str): 设备连接目标（如"192.168.1.100:5555"）

    返回:
        dict: 包含执行结果的字典，包含以下键:
            - success: 布尔值，命令是否最终执行成功
            - stdout: 命令输出
            - stderr: 错误输出
            - returncode: 命令返回码
            - message: 执行状态描述
    """

    def _execute(cmd):
        """内部执行命令的辅助函数"""
        try:
            # 执行命令，捕获 stdout 和 stderr
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # 直接返回字符串而非字节流
            )
            return result.stdout, result.stderr, result.returncode
        except FileNotFoundError:
            return "", "未找到ADB命令，请检查ADB是否已安装并添加到环境变量", 1
        except Exception as e:
            return "", f"执行命令时发生错误: {str(e)}", 1

    # 第一次执行命令
    stdout, stderr, returncode = _execute(command)

    # 如果第一次执行成功，直接返回结果
    if returncode == 0:
        return {
            "success": True,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "message": "命令执行成功"
        }

    # 第一次执行失败，尝试重新连接设备
    print(f"命令执行失败，尝试重新连接设备 {connect_target}...")
    connect_cmd = ["adb", "connect", connect_target]
    connect_stdout, connect_stderr, connect_rc = _execute(connect_cmd)

    if connect_rc != 0:
        # 连接失败，返回原始错误信息
        return {
            "success": False,
            "stdout": stdout,
            "stderr": f"连接设备失败: {connect_stderr}\n原始命令错误: {stderr}",
            "returncode": returncode,
            "message": "命令执行失败且设备连接失败"
        }

    # 连接成功后，再次执行原始命令
    print(f"设备连接成功，重试原始命令...")
    retry_stdout, retry_stderr, retry_rc = _execute(command)

    return {
        "success": retry_rc == 0,
        "stdout": retry_stdout,
        "stderr": retry_stderr,
        "returncode": retry_rc,
        "message": "重新连接后命令执行成功" if retry_rc == 0 else "重新连接后命令仍执行失败"
    }


# 示例用法
if __name__ == "__main__":
    # 示例1：获取设备列表（需要替换为你的设备连接目标）
    device_target = "10.100.129.253:36319"  # 替换为实际设备的IP:端口
    adb_command = ["adb", "shell", "input", "text", "11", "111"]

    result = run_adb_command(adb_command, device_target)

    print(f"执行结果: {'成功' if result['success'] else '失败'}")
    print(f"返回码: {result['returncode']}")
    print("输出内容:")
    print(result['stdout'])
    if result['stderr']:
        print("错误信息:")
        print(result['stderr'])

    # 示例2：执行shell命令（如查看设备内存）
    # adb_command = ["adb", "shell", "free"]
    # result = run_adb_command(adb_command, device_target)