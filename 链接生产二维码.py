import qrcode
from PIL import Image

# 你想要编码的链接
link = "https://www.baidu.com"

# 创建一个QRCode对象
qr = qrcode.QRCode(
    version=1,  # 控制二维码的大小（1到40），数字越大，二维码越大
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # 控制二维码的纠错级别
    box_size=10,  # 每个“盒子”的像素数
    border=4,  # 边框的盒子厚度
)

# 将数据添加到QRCode对象中
qr.add_data(link)
qr.make(fit=True)

# 创建一个Image对象
img = qr.make_image(fill='black', back_color='white')

# 保存图像到文件
img.save('qrcode.png')

# 如果你想要显示图像（在某些环境下可能需要安装额外的库，如matplotlib）
# img.show()