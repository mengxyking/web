"""定时/循环任务管理"""
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from enum import Enum


class TaskType(Enum):
    ONCE = "once"
    LOOP = "loop"
    SCHEDULED = "scheduled"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class Task:
    name: str
    func: Callable
    task_type: TaskType
    interval: float = 0          # loop: seconds between runs
    delay: float = 0             # once/scheduled: delay before first run
    repeat_count: int = -1       # -1 = infinite for loop
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: TaskStatus = TaskStatus.PENDING
    run_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_run: float = 0
    error: str = ""
    _thread: Optional[threading.Thread] = field(default=None, repr=False)
    _stop_event: threading.Event = field(default_factory=threading.Event, repr=False)


class TaskManager:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._lock = threading.Lock()
        self._on_update: Optional[Callable] = None

    def set_update_callback(self, cb: Callable):
        self._on_update = cb

    def _notify(self):
        if self._on_update:
            try:
                self._on_update(self.get_tasks())
            except Exception:
                pass

    def add_task(self, name: str, func: Callable, task_type: TaskType,
                 interval: float = 0, delay: float = 0, repeat_count: int = -1) -> Task:
        task = Task(
            name=name, func=func, task_type=task_type,
            interval=interval, delay=delay, repeat_count=repeat_count
        )
        with self._lock:
            self._tasks[task.id] = task
        self._start_task(task)
        self._notify()
        return task

    def _start_task(self, task: Task):
        task._stop_event.clear()
        task.status = TaskStatus.PENDING

        def runner():
            if task.delay > 0:
                task._stop_event.wait(task.delay)
                if task._stop_event.is_set():
                    task.status = TaskStatus.STOPPED
                    self._notify()
                    return

            if task.task_type == TaskType.ONCE:
                self._run_once(task)
            elif task.task_type == TaskType.LOOP:
                self._run_loop(task)
            elif task.task_type == TaskType.SCHEDULED:
                self._run_once(task)

        task._thread = threading.Thread(target=runner, daemon=True)
        task._thread.start()

    def _run_once(self, task: Task):
        task.status = TaskStatus.RUNNING
        self._notify()
        try:
            task.func()
            task.run_count += 1
            task.last_run = time.time()
            task.status = TaskStatus.DONE
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        self._notify()

    def _run_loop(self, task: Task):
        task.status = TaskStatus.RUNNING
        self._notify()
        while not task._stop_event.is_set():
            if task.repeat_count != -1 and task.run_count >= task.repeat_count:
                break
            try:
                task.func()
                task.run_count += 1
                task.last_run = time.time()
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                self._notify()
                return
            if task.interval > 0:
                task._stop_event.wait(task.interval)
        if not task._stop_event.is_set():
            task.status = TaskStatus.DONE
        else:
            task.status = TaskStatus.STOPPED
        self._notify()

    def stop_task(self, task_id: str):
        with self._lock:
            task = self._tasks.get(task_id)
        if task:
            task._stop_event.set()
            self._notify()

    def remove_task(self, task_id: str):
        with self._lock:
            task = self._tasks.pop(task_id, None)
        if task:
            task._stop_event.set()
        self._notify()

    def get_tasks(self) -> List[Task]:
        with self._lock:
            return list(self._tasks.values())

    def stop_all(self):
        with self._lock:
            tasks = list(self._tasks.values())
        for t in tasks:
            t._stop_event.set()
