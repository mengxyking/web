"""
屏幕镜像 — 三档自动降级
  1. ScrcpyServerMirror : scrcpy 4.0 server 协议 + ffmpeg 解码（最高画质/帧率）
  2. ScreenshotMirror   : while true; do screencap -p; done 持久流（兜底）
"""
import socket
import subprocess
import threading
import io
import os
import random
import time
import shutil
from typing import Optional, Callable
from PIL import Image

_FFMPEG = shutil.which("ffmpeg")

# ── 常量 ──────────────────────────────────────────────────────────────────────
_PNG_HEADER = b'\x89PNG\r\n\x1a\n'
_PNG_IEND   = b'IEND\xaeB`\x82'
_JPEG_SOI   = b'\xff\xd8'
_JPEG_EOI   = b'\xff\xd9'

_SCRCPY_SERVER_LOCAL = next(
    (p for p in [
        "/opt/homebrew/share/scrcpy/scrcpy-server",
        "/opt/homebrew/Cellar/scrcpy/4.0/share/scrcpy/scrcpy-server",
        "/usr/local/share/scrcpy/scrcpy-server",
    ] if os.path.exists(p)), None
)
_DEVICE_JAR = "/data/local/tmp/scrcpy-server.jar"


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def _recv_exact(sock: socket.socket, n: int) -> Optional[bytes]:
    buf = b''
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except OSError:
            return None
        if not chunk:
            return None
        buf += chunk
    return buf


# ── ScrcpyServerMirror ────────────────────────────────────────────────────────
class ScrcpyServerMirror:
    """
    利用 scrcpy 4.0 server 协议在设备端做硬件编码（H.264），
    通过 ADB 反向隧道传回 PC，用 ffmpeg 解码成 JPEG 帧显示。

    协议要点（scrcpy 4.0）：
      - socket 名：localabstract:scrcpy_<scid>
      - 隧道方向：设备主动连 PC（adb reverse）
      - 帧包格式：[PTS 8B big-endian][size 4B big-endian][H.264 data]
      - config 包 PTS = 0xFFFF_FFFF_FFFF_FFFF（SPS/PPS，也直接送 ffmpeg）
    """

    def __init__(self, serial: str, width: int = 0, height: int = 0):
        self.serial = serial
        self._max_size = min(720, max(width, height)) if max(width, height) > 0 else 720
        # scrcpy server parses scid with Integer.parseInt(hex) — must be signed int32
        self._scid = "%08x" % random.randint(0, 0x7FFFFFFF)
        self._socket_name = f"scrcpy_{self._scid}"

        self._running = False
        self._srv_sock: Optional[socket.socket] = None   # PC 监听 socket
        self._cli_sock: Optional[socket.socket] = None   # 设备连进来的 socket
        self._adb_proc = None
        self._ffmpeg_proc = None

        self._frame_callback: Optional[Callable] = None
        self._error_callback: Optional[Callable] = None
        self._latest_frame: Optional[Image.Image] = None
        self._frame_lock = threading.Lock()
        self._new_frame = threading.Event()

        self._thread: Optional[threading.Thread] = None
        self._deliver_thread: Optional[threading.Thread] = None

    # ── 公开接口 ──────────────────────────────────────────────────────────────

    def set_frame_callback(self, cb: Callable): self._frame_callback = cb
    def set_error_callback(self, cb: Callable): self._error_callback = cb

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True,
                                        name=f"scrcpy-{self.serial}")
        self._deliver_thread = threading.Thread(target=self._deliver_loop, daemon=True,
                                                name=f"scrcpy-del-{self.serial}")
        self._thread.start()
        self._deliver_thread.start()

    def stop(self):
        self._running = False
        self._new_frame.set()
        self._cleanup()

    def get_last_frame(self) -> Optional[Image.Image]:
        with self._frame_lock:
            return self._latest_frame

    # ── 内部逻辑 ──────────────────────────────────────────────────────────────

    def _cleanup(self):
        for s in (self._cli_sock, self._srv_sock):
            try: s and s.close()
            except: pass
        for p in (self._adb_proc, self._ffmpeg_proc):
            try: p and p.kill()
            except: pass
        try:
            subprocess.run(
                ["adb", "-s", self.serial, "reverse", "--remove",
                 f"localabstract:{self._socket_name}"],
                capture_output=True, timeout=5
            )
        except: pass

    def _run_loop(self):
        fail = 0
        while self._running:
            try:
                self._run_once()
                fail = 0
            except Exception as e:
                fail += 1
                if self._error_callback:
                    self._error_callback(self.serial, f"scrcpy server 流错误: {e}")
                self._cleanup()
                if not self._running:
                    break
                time.sleep(min(5.0, 0.5 * fail))

    def _run_once(self):
        if not _SCRCPY_SERVER_LOCAL:
            raise Exception("找不到 scrcpy-server，请运行: brew install scrcpy")
        if not _FFMPEG:
            raise Exception("找不到 ffmpeg")

        # 1. 推 server JAR
        r = subprocess.run(
            ["adb", "-s", self.serial, "push", _SCRCPY_SERVER_LOCAL, _DEVICE_JAR],
            capture_output=True, timeout=30
        )
        if r.returncode != 0:
            raise Exception(f"推送 server 失败: {r.stderr.decode()[:200]}")

        # 2. PC 端 TCP 服务器（等设备来连）
        self._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv_sock.bind(('127.0.0.1', 0))
        port = self._srv_sock.getsockname()[1]
        self._srv_sock.listen(5)
        self._srv_sock.settimeout(15)

        # 3. adb reverse：设备 abstract socket → PC 端口
        subprocess.run(
            ["adb", "-s", self.serial, "reverse",
             f"localabstract:{self._socket_name}", f"tcp:{port}"],
            capture_output=True, timeout=10
        )

        # 4. 启动设备端 server
        server_cmd = (
            f"CLASSPATH={_DEVICE_JAR} app_process / "
            f"com.genymobile.scrcpy.Server 4.0 "
            f"scid={self._scid} log_level=info "
            f"audio=false control=false "
            f"max_size={self._max_size} video_codec=h264 "
            f"send_device_meta=false send_dummy_byte=false "
            f"send_codec_meta=true send_frame_meta=true"
        )
        self._adb_proc = subprocess.Popen(
            ["adb", "-s", self.serial, "shell", server_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # 5. 等待设备连进来（video socket）
        try:
            self._cli_sock, _ = self._srv_sock.accept()
        except socket.timeout:
            raise Exception("等待设备连接超时（15s）")
        self._cli_sock.settimeout(10)

        # 6. 读 codec meta（16字节）：codec_id[4] + flags[4] + width[4] + height[4]
        #    实测 scrcpy 4.0 在 send_device_meta=false 时仍发 16 字节头
        codec_hdr = _recv_exact(self._cli_sock, 16)
        if not codec_hdr:
            raise Exception("读取 codec meta 失败")
        codec_id = codec_hdr[:4].decode('ascii', errors='replace')
        w = int.from_bytes(codec_hdr[8:12], 'big')
        h = int.from_bytes(codec_hdr[12:16], 'big')

        # 7. 启动 ffmpeg 解码器
        self._ffmpeg_proc = subprocess.Popen(
            [_FFMPEG, "-loglevel", "quiet",
             "-f", "h264", "-i", "pipe:0",
             "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "5",
             "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

        # 8. 解析帧包，把 H.264 data 送给 ffmpeg
        threading.Thread(target=self._feed_ffmpeg, daemon=True).start()

        # 9. 读 ffmpeg 输出的 JPEG 流
        self._read_jpeg(self._ffmpeg_proc.stdout)

    def _feed_ffmpeg(self):
        """
        解析 scrcpy 帧包格式：
          [PTS 8B big-endian] [size 4B big-endian] [H.264 data N bytes]
        config 包 PTS = 0xFFFFFFFFFFFFFFFF，data = SPS/PPS（同样送 ffmpeg）
        """
        try:
            while self._running:
                hdr = _recv_exact(self._cli_sock, 12)
                if not hdr:
                    break
                size = int.from_bytes(hdr[8:12], 'big')
                if size > 10 * 1024 * 1024:
                    break
                if size == 0:
                    continue
                data = _recv_exact(self._cli_sock, size)
                if not data:
                    break
                self._ffmpeg_proc.stdin.write(data)
                self._ffmpeg_proc.stdin.flush()
        except Exception:
            pass
        try:
            self._ffmpeg_proc.stdin.close()
        except Exception:
            pass

    def _read_jpeg(self, stdout):
        buf = b''
        while self._running:
            try:
                chunk = stdout.read(65536)
            except Exception:
                break
            if not chunk:
                break
            buf += chunk
            while True:
                s = buf.find(_JPEG_SOI)
                if s == -1:
                    buf = b''
                    break
                if s > 0:
                    buf = buf[s:]
                e = buf.find(_JPEG_EOI, 2)
                if e == -1:
                    break
                e += 2
                try:
                    img = Image.open(io.BytesIO(buf[:e]))
                    img.load()
                    with self._frame_lock:
                        self._latest_frame = img
                    self._new_frame.set()
                except Exception:
                    pass
                buf = buf[e:]

    def _deliver_loop(self):
        while self._running:
            self._new_frame.wait(timeout=2.0)
            self._new_frame.clear()
            if not self._running:
                break
            with self._frame_lock:
                img = self._latest_frame
            if img and self._frame_callback:
                try:
                    self._frame_callback(self.serial, img)
                except Exception:
                    pass


# ── ScreenshotMirror（兜底）─────────────────────────────────────────────────
class ScreenshotMirror:
    """持久 screencap 流 — 全设备兜底方案"""

    def __init__(self, adb_manager, serial: str):
        self._adb = adb_manager
        self.serial = serial
        self._running = False
        self._frame_callback: Optional[Callable] = None
        self._error_callback: Optional[Callable] = None
        self._latest_frame: Optional[Image.Image] = None
        self._frame_lock = threading.Lock()
        self._new_frame = threading.Event()
        self._fail = 0
        self._capture_t: Optional[threading.Thread] = None
        self._deliver_t: Optional[threading.Thread] = None

    def set_frame_callback(self, cb: Callable): self._frame_callback = cb
    def set_error_callback(self, cb: Callable): self._error_callback = cb

    def start(self):
        if self._running:
            return
        self._running = True
        self._capture_t = threading.Thread(target=self._capture_loop, daemon=True,
                                           name=f"cap-{self.serial}")
        self._deliver_t = threading.Thread(target=self._deliver_loop, daemon=True,
                                           name=f"cap-del-{self.serial}")
        self._capture_t.start()
        self._deliver_t.start()

    def stop(self):
        self._running = False
        self._new_frame.set()

    def get_last_frame(self) -> Optional[Image.Image]:
        with self._frame_lock:
            return self._latest_frame

    def _capture_loop(self):
        while self._running:
            try:
                proc = subprocess.Popen(
                    ["adb", "-s", self.serial, "exec-out",
                     "while true; do screencap -p; done"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
                )
                buf = b''
                while self._running:
                    chunk = proc.stdout.read(65536)
                    if not chunk:
                        break
                    buf += chunk
                    while True:
                        s = buf.find(_PNG_HEADER)
                        if s == -1:
                            buf = buf[-8:] if len(buf) >= 8 else buf
                            break
                        if s > 0:
                            buf = buf[s:]
                        e = buf.find(_PNG_IEND)
                        if e == -1:
                            break
                        e += len(_PNG_IEND)
                        try:
                            img = Image.open(io.BytesIO(buf[:e]))
                            img.load()
                            with self._frame_lock:
                                self._latest_frame = img
                            self._new_frame.set()
                            self._fail = 0
                        except Exception:
                            pass
                        buf = buf[e:]
                proc.kill()
            except Exception as e:
                self._fail += 1
                if self._error_callback:
                    self._error_callback(self.serial, str(e))
            if not self._running:
                break
            time.sleep(min(5.0, 0.3 * self._fail))

    def _deliver_loop(self):
        while self._running:
            self._new_frame.wait(timeout=2.0)
            self._new_frame.clear()
            if not self._running:
                break
            with self._frame_lock:
                img = self._latest_frame
            if img and self._frame_callback:
                try:
                    self._frame_callback(self.serial, img)
                except Exception:
                    pass


# ── MirrorManager ─────────────────────────────────────────────────────────────
def _create_mirror(adb_manager, serial: str, device=None):
    if _SCRCPY_SERVER_LOCAL and _FFMPEG:
        w = getattr(device, 'screen_width', 0) if device else 0
        h = getattr(device, 'screen_height', 0) if device else 0
        return ScrcpyServerMirror(serial, w, h)
    return ScreenshotMirror(adb_manager, serial)


class MirrorManager:
    def __init__(self, adb_manager):
        self._adb = adb_manager
        self._mirrors: dict = {}

    def start_mirror(self, serial: str, device=None,
                     callback: Callable = None,
                     error_callback: Callable = None):
        if serial in self._mirrors:
            self._mirrors[serial].stop()
        m = _create_mirror(self._adb, serial, device)
        if callback:
            m.set_frame_callback(callback)
        if error_callback:
            m.set_error_callback(error_callback)
        m.start()
        self._mirrors[serial] = m
        return m

    def stop_mirror(self, serial: str):
        if serial in self._mirrors:
            self._mirrors[serial].stop()
            del self._mirrors[serial]

    def stop_all(self):
        for m in self._mirrors.values():
            m.stop()
        self._mirrors.clear()

    def get_mirror(self, serial: str):
        return self._mirrors.get(serial)
