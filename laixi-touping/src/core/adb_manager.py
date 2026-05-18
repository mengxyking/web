"""ADB设备管理核心模块"""
import subprocess
import threading
import time
import re
from typing import List, Dict, Optional, Callable


class Device:
    def __init__(self, serial: str, status: str = "online"):
        self.serial = serial
        self.status = status
        self.model = ""
        self.brand = ""
        self.android_version = ""
        self.screen_width = 0
        self.screen_height = 0
        self._lock = threading.Lock()

    def __repr__(self):
        return f"Device({self.serial}, {self.model or 'Unknown'})"

    def fetch_info(self):
        try:
            self.model = self._adb_shell("getprop ro.product.model").strip()
            self.brand = self._adb_shell("getprop ro.product.brand").strip()
            self.android_version = self._adb_shell("getprop ro.build.version.release").strip()
            size_output = self._adb_shell("wm size")
            # Override size is what Android uses for touch input coordinates
            m = re.search(r"Override size: (\d+)x(\d+)", size_output)
            if not m:
                m = re.search(r"Physical size: (\d+)x(\d+)", size_output)
            if m:
                self.screen_width = int(m.group(1))
                self.screen_height = int(m.group(2))
        except Exception:
            pass

    def _adb_shell(self, cmd: str) -> str:
        result = subprocess.run(
            ["adb", "-s", self.serial, "shell", cmd],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout

    def display_name(self) -> str:
        name = self.model if self.model else self.serial
        return f"{name} [{self.serial}]"


class AdbManager:
    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

    def start_monitor(self):
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitor(self):
        self._running = False

    def _monitor_loop(self):
        while self._running:
            self.refresh_devices()
            time.sleep(2)

    def refresh_devices(self):
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().split("\n")[1:]
            current_serials = set()
            changed = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                serial, status = parts[0].strip(), parts[1].strip()
                if status == "offline":
                    continue
                current_serials.add(serial)

                with self._lock:
                    if serial not in self._devices:
                        dev = Device(serial, status)
                        threading.Thread(target=dev.fetch_info, daemon=True).start()
                        self._devices[serial] = dev
                        changed = True

            with self._lock:
                removed = set(self._devices.keys()) - current_serials
                for s in removed:
                    del self._devices[s]
                    changed = True

            if changed:
                self._notify()

        except Exception:
            pass

    def get_devices(self) -> List[Device]:
        with self._lock:
            return list(self._devices.values())

    def get_device(self, serial: str) -> Optional[Device]:
        with self._lock:
            return self._devices.get(serial)

    def add_callback(self, cb: Callable):
        self._callbacks.append(cb)

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb(self.get_devices())
            except Exception:
                pass

    # ---- ADB操作 ----

    def _run(self, serial: str, *args, timeout=15) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["adb", "-s", serial] + list(args),
            capture_output=True, text=True, timeout=timeout
        )

    def shell(self, serial: str, cmd: str, timeout=15) -> str:
        r = self._run(serial, "shell", cmd, timeout=timeout)
        return r.stdout

    def batch_shell(self, serials: List[str], cmd: str):
        threads = []
        results = {}

        def run(s):
            results[s] = self.shell(s, cmd)

        for s in serials:
            t = threading.Thread(target=run, args=(s,), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return results

    def tap(self, serial: str, x: int, y: int):
        self.shell(serial, f"input tap {x} {y}")

    def swipe(self, serial: str, x1: int, y1: int, x2: int, y2: int, duration=300):
        self.shell(serial, f"input swipe {x1} {y1} {x2} {y2} {duration}")

    def input_text(self, serial: str, text: str):
        text = text.replace(" ", "%s").replace("'", "\\'")
        self.shell(serial, f"input text '{text}'")

    def key_event(self, serial: str, keycode: int):
        self.shell(serial, f"input keyevent {keycode}")

    def batch_tap(self, serials: List[str], x: int, y: int):
        threads = [threading.Thread(target=self.tap, args=(s, x, y), daemon=True) for s in serials]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def batch_swipe(self, serials: List[str], x1: int, y1: int, x2: int, y2: int, duration=300):
        threads = [threading.Thread(target=self.swipe, args=(s, x1, y1, x2, y2, duration), daemon=True) for s in serials]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def batch_input_text(self, serials: List[str], text: str):
        threads = [threading.Thread(target=self.input_text, args=(s, text), daemon=True) for s in serials]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def screenshot(self, serial: str) -> Optional[bytes]:
        try:
            r = subprocess.run(
                ["adb", "-s", serial, "exec-out", "screencap", "-p"],
                capture_output=True, timeout=10
            )
            return r.stdout if r.returncode == 0 else None
        except Exception:
            return None

    def install_apk(self, serial: str, apk_path: str, callback: Callable = None):
        def _install():
            r = self._run(serial, "install", "-r", apk_path, timeout=120)
            if callback:
                success = "Success" in r.stdout
                callback(serial, success, r.stdout + r.stderr)
        threading.Thread(target=_install, daemon=True).start()

    def batch_install_apk(self, serials: List[str], apk_path: str, callback: Callable = None):
        for s in serials:
            self.install_apk(s, apk_path, callback)

    def push_file(self, serial: str, local: str, remote: str, callback: Callable = None):
        def _push():
            r = self._run(serial, "push", local, remote, timeout=120)
            if callback:
                callback(serial, r.returncode == 0, r.stdout + r.stderr)
        threading.Thread(target=_push, daemon=True).start()

    def batch_push_file(self, serials: List[str], local: str, remote: str, callback: Callable = None):
        for s in serials:
            self.push_file(s, local, remote, callback)

    def pull_file(self, serial: str, remote: str, local: str, callback: Callable = None):
        def _pull():
            r = self._run(serial, "pull", remote, local, timeout=120)
            if callback:
                callback(serial, r.returncode == 0, r.stdout + r.stderr)
        threading.Thread(target=_pull, daemon=True).start()

    def uninstall_app(self, serial: str, package: str, callback: Callable = None):
        def _uninstall():
            r = self.shell(serial, f"pm uninstall {package}")
            if callback:
                callback(serial, "Success" in r, r)
        threading.Thread(target=_uninstall, daemon=True).start()

    def clear_app_data(self, serial: str, package: str):
        self.shell(serial, f"pm clear {package}")

    def list_packages(self, serial: str) -> List[str]:
        output = self.shell(serial, "pm list packages")
        return [line.replace("package:", "").strip() for line in output.splitlines() if line.startswith("package:")]

    def connect_wifi(self, ip: str, port: int = 5555) -> bool:
        try:
            r = subprocess.run(
                ["adb", "connect", f"{ip}:{port}"],
                capture_output=True, text=True, timeout=10
            )
            return "connected" in r.stdout.lower()
        except Exception:
            return False

    def disconnect(self, serial: str):
        try:
            subprocess.run(["adb", "disconnect", serial], timeout=5)
        except Exception:
            pass

    @staticmethod
    def check_adb() -> bool:
        try:
            subprocess.run(["adb", "version"], capture_output=True, timeout=5)
            return True
        except Exception:
            return False

    @staticmethod
    def start_server():
        try:
            subprocess.run(["adb", "start-server"], capture_output=True, timeout=10)
        except Exception:
            pass
