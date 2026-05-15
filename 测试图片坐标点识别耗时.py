import cv2
import threading
import time
import numpy as np

# 模拟一个图像，使用 NumPy 创建一个 100x100 的随机图像数据
#image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

def get_color_at_position(image, x, y):
    b, g, r = image[y, x]
    return (r, g, b)

def thread_task(image, x, y, index):
    color = get_color_at_position(image, x, y)
    color = get_color_at_position(image, 1, 3)
    color = get_color_at_position(image, 2, 3)
    color = get_color_at_position(image, 3, 4)
    color = get_color_at_position(image, 5, 5)
    color = get_color_at_position(image, 6, 6)
    color = get_color_at_position(image ,3, 6)
    color = get_color_at_position(image, 2, 7)
    color = get_color_at_position(image, 7, 1)
    color = get_color_at_position(image, 4, 8)


# 定义线程列表
threads = []
#image = cv2.imread(r"C:\Users\Administrator\Desktop\222.png")
#print(image)
# 模拟 100 个线程同时访问图像上的某个位置 (例如位置 (50, 50))
bbb = 0
while(bbb < 1000):
    for i in range(100):
        start_time = time.time()
        image = cv2.imread(r"C:\Users\Administrator\Desktop\222.png")
        t = threading.Thread(target=thread_task, args=(image, 1, 1, i))
        end_time = time.time()
        duration = end_time - start_time
        print(f"Duration: {duration:.6f} seconds")
        threads.append(t)
        t.start()

    # 等待所有线程完成
    for t in threads:
        t.join()

    bbb += 1