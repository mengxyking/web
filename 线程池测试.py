import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 共享资源
shared_resource = 0
lock = threading.Lock()


# 线程任务
def thread_task(thread_id):
    global shared_resource
    print(f"Thread {thread_id} is starting.")

    # 模拟一些工作
    time.sleep(15)

    # 访问共享资源
    with lock:
        local_copy = shared_resource
        local_copy += 1
        print(f"Thread {thread_id} incremented shared_resource to {local_copy}.")
        shared_resource = local_copy

    print(f"Thread {thread_id} is finishing.")


# 线程数量
total_threads = 20
threads_per_batch = 5

# 使用 ThreadPoolExecutor 来管理线程池
with ThreadPoolExecutor(max_workers=threads_per_batch) as executor:
    # 创建所有线程任务
    futures = [executor.submit(thread_task, i) for i in range(total_threads)]

    # 五个五个地等待线程完成
    for _ in range(0, total_threads, threads_per_batch):
        for future in as_completed(futures[:threads_per_batch]):
            futures.remove(future)  # 从列表中移除已完成的 future
            future.result()  # 获取结果（如果有异常会抛出）
            print(f"Future {future} completed.")

            print("1")
        print("2")
    print("3")

print(f"Final value of shared_resource: {shared_resource}")