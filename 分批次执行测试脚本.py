import time
import random
import threading
from threading import Lock, Condition


# 移除原来的全局变量，改为通过类来封装批次资源


class DouyinBatchManager:
    """抖音执行批次管理器：每个批次一个独立实例，隔离资源"""

    def __init__(self):
        self.threads = []  # 当前批次的所有线程
        self.execution_lock = Lock()  # 当前批次的互斥锁
        self.condition = Condition()  # 当前批次的条件变量
        self.current_running = None  # 当前批次正在执行的线程
        self.is_batch_running = True  # 批次是否运行

    def select_next_thread(self):
        """随机选择当前批次下一个要执行的线程"""
        with self.condition:
            # 过滤当前批次的活跃线程
            active_threads = [t for t in self.threads if t.is_running and t.is_alive()]
            if active_threads:
                self.current_running = random.choice(active_threads)
                print(f"【批次{id(self)}】选中下一个执行的线程：{self.current_running.name}")
            else:
                self.current_running = None
            self.condition.notify_all()

    def stop_batch(self):
        """停止当前批次的所有线程"""
        self.is_batch_running = False
        with self.condition:
            self.condition.notify_all()  # 唤醒所有等待的线程
        # 等待所有线程结束
        for t in self.threads:
            t.stop()
            t.join()
        print(f"【批次{id(self)}】所有线程已停止")


class DouyinThread(threading.Thread):
    def __init__(self, serial, file_path, batch_manager):
        super().__init__()
        self.serial = serial
        self.file_path = file_path
        self.is_running = True
        self.device = None
        self.batch_manager = batch_manager  # 关联到所属的批次管理器

    def run(self):
        """线程主执行逻辑（关联到批次管理器）"""
        self.device = get_device(self.serial)
        self._init_device_watcher()

        # 读取配置
        # self.wait_min = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao"))
        # self.wait_max = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da"))
        self.wait_min = 1
        self.wait_max = 3

        while self.is_running and self.batch_manager.is_batch_running:
            with self.batch_manager.condition:
                # 等待直到当前线程被本批次选中
                while (self.batch_manager.current_running is not None and
                       self.batch_manager.current_running != self and
                       self.batch_manager.is_batch_running):
                    self.batch_manager.condition.wait()

                # 批次已停止则退出
                if not self.batch_manager.is_batch_running:
                    break

                # 检查是否在直播间
                if not self._check_in_live_room():
                    print(f"【批次{id(self.batch_manager)}】线程 {self.name}：不在直播间，跳过")
                    self.batch_manager.select_next_thread()
                    continue

                try:
                    # 执行直播间操作（本批次内串行）
                    with self.batch_manager.execution_lock:
                        print(f"【批次{id(self.batch_manager)}】线程 {self.name} 执行liveRoom")
                        self.liveRoom()
                        self.backToDyLiveRoom()

                    # 生成等待时间，本批次所有线程共同等待
                    sleep_time = random.randint(self.wait_min, self.wait_max)
                    print(f"【批次{id(self.batch_manager)}】执行完成，所有线程等待 {sleep_time} 秒")

                    # 重置当前执行状态，通知所有线程等待
                    self.batch_manager.current_running = None
                    self.batch_manager.condition.notify_all()

                    # 所有线程等待
                    time.sleep(sleep_time)

                    # 选择本批次下一个执行线程
                    self.batch_manager.select_next_thread()

                except Exception as e:
                    print(f"【批次{id(self.batch_manager)}】线程 {self.name} 出错：{e}")
                    self.batch_manager.current_running = None
                    self.batch_manager.condition.notify_all()

    def _init_device_watcher(self):
        """初始化设备监听器"""
        self.device.watcher.when("以后再说").click()
        self.device.watcher.when("忽略").click()
        self.device.watcher.when("残忍放弃").click()
        self.device.watcher.start()

    def _check_in_live_room(self):
        """检查是否在直播间"""
        return self.device(text='说点什么...').exists(timeout=3)

    def liveRoom(self):
        """直播间核心操作"""
        content = get_random_line_from_file(self.file_path)

        if self.device(text='说点什么...').exists(timeout=3):
            random_click_view(self.device, self.device(text='说点什么...'))
            time.sleep(random.randint(1, 3))
        else:
            print(f"【批次{id(self.batch_manager)}】线程 {self.name}：无输入框入口")
            return

        if self.device(className="android.widget.EditText").exists(timeout=12):
            self.device(className="android.widget.EditText").set_text(content)
            time.sleep(random.randint(1, 3))
        else:
            print(f"【批次{id(self.batch_manager)}】线程 {self.name}：无输入框")
            return

        if self.device(text='发送').exists(timeout=3):
            random_click_view(self.device, self.device(text='发送'))
            time.sleep(random.randint(1, 3))
        else:
            print(f"【批次{id(self.batch_manager)}】线程 {self.name}：无发送按钮")
            return

    def backToDyLiveRoom(self):
        """返回直播间（保留原有逻辑）"""
        time.sleep(random.randint(1, 2))

    def stop(self):
        """停止当前线程"""
        self.is_running = False


# 对外暴露的批次启动函数
def start_douyin_batch(serial_list, file_path):
    """
    启动一个独立的抖音执行批次
    :param serial_list: 本批次的设备序列号列表
    :param file_path: 文案文件路径
    :return: 批次管理器实例（用于后续控制）
    """
    # 创建独立的批次管理器
    batch_manager = DouyinBatchManager()

    # 为每个设备创建线程，关联到当前批次管理器
    for serial in serial_list:
        thread = DouyinThread(serial, file_path, batch_manager)
        batch_manager.threads.append(thread)
        thread.start()

    # 选中本批次第一个执行的线程
    batch_manager.select_next_thread()

    return batch_manager


# 辅助函数（保持和之前一致）
def get_device(serial):
    """获取设备对象（补充你的实现）"""
    pass


def get_value_by_key_pkl(pkl_file, key):
    """从pkl读取配置（补充你的实现）"""
    pass


def get_random_line_from_file(file_path):
    """读取随机文案（补充你的实现）"""
    pass


def random_click_view(d, view):
    """随机点击（补充你的实现）"""
    pass


# 使用示例：多批次执行
if __name__ == "__main__":
    # 启动第一批：设备1、2
    batch1 = start_douyin_batch(["serial1", "serial2"], "content1.txt")
    print(f"启动批次1，管理器ID：{id(batch1)}")

    # 模拟间隔一段时间后启动第二批：设备3、4
    time.sleep(10)
    batch2 = start_douyin_batch(["serial3", "serial4"], "content2.txt")
    print(f"启动批次2，管理器ID：{id(batch2)}")

    # 运行一段时间后停止批次
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        pass

    # 停止批次1
    batch1.stop_batch()
    # 停止批次2
    batch2.stop_batch()