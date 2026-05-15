import uiautomator2 as u2


def get_device_info():
    # 连接设备
    d = u2.connect("384da6")  # 自动连接第一个设备，也可以指定设备ID
    print(d.info)
    # 获取设备信息
    brand = d.info.get('brand', '未知品牌')  # 品牌，如 "Xiaomi"
    model = d.info.get('model', '未知型号')  # 型号，如 "MI 9"
    device_name = d.info.get('device', '未知设备')  # 设备名，如 "cepheus"
    version = d.info.get('version', '未知版本')  # Android版本，如 "10"

    return {
        'brand': brand,
        'model': model,
        'device_name': device_name,
        'android_version': version
    }


if __name__ == "__main__":
    info = get_device_info()
    print(f"品牌: {info['brand']}")
    print(f"型号: {info['model']}")
    print(f"设备名: {info['device_name']}")
    print(f"Android版本: {info['android_version']}")