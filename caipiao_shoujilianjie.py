import subprocess
import uiautomator2 as u2
import time


def get_connected_devices():
    """获取当前连接的安卓设备列表"""
    try:
        # 执行adb命令获取设备列表
        result = subprocess.run(
            ["adb", "devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        # 检查命令是否执行成功
        if result.returncode != 0:
            print(f"ADB命令执行失败: {result.stderr.strip()}")
            return []

        # 解析输出结果
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
        for line in lines:
            line = line.strip()
            if line and 'device' in line:
                device_id = line.split()[0]
                devices.append(device_id)

        return devices

    except FileNotFoundError:
        print("未找到ADB工具，请确保ADB已安装并添加到系统PATH")
        return []
    except Exception as e:
        print(f"获取设备列表时发生错误: {str(e)}")
        return []


# def connect_first_device():
#     """连接第一个可用的安卓设备"""
#     # 获取设备列表
#     devices = get_connected_devices()
#
#     if not devices:
#         print("未找到任何连接的安卓设备")
#         return None
#
#     # 取第一个设备
#     first_device_id = devices[0]
#     print(f"找到设备列表: {devices}")
#     print(f"尝试连接第一个设备: {first_device_id}")
#
#     try:
#         # 初始化设备连接
#         d = u2.connect(first_device_id)
#
#         # 检查连接状态
#         if d.healthcheck():
#             print(f"成功连接设备: {first_device_id}")
#
#             # 确保uiautomator服务已启动
#             if not d.service("uiautomator").running():
#                 print("启动uiautomator服务...")
#                 d.service("uiautomator").start()
#                 time.sleep(2)  # 等待服务启动
#
#             return d
#         else:
#             print(f"设备 {first_device_id} 连接检查失败")
#             return None
#
#     except Exception as e:
#         print(f"连接设备 {first_device_id} 时发生错误: {str(e)}")
#         return None
#

if __name__ == "__main__":
    # 连接第一个设备
    device = get_connected_devices()
    print(device)

    # 如果连接成功，可以进行后续操作示例
    # if device:
    #     print("\n设备信息:")
    #     print(f"设备型号: {device.device_info.get('model', '未知')}")
    #     print(f"Android版本: {device.device_info.get('android_version', '未知')}")
    #     print(f"分辨率: {device.window_size()}")
    #
    #     # 示例操作：获取当前屏幕截图
    #     try:
    #         screenshot_path = "screenshot.png"
    #         device.screenshot(screenshot_path)
    #         print(f"已保存屏幕截图到: {screenshot_path}")
    #     except Exception as e:
    #         print(f"截图失败: {str(e)}")
