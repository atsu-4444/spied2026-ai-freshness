import platform
import threading
import time

import cv2


class CameraStream:
    """Continuously keeps only the newest frame from the webcam."""

    def __init__(self, camera_id=0, width=640, height=480, fps=15, max_failures=20):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.max_failures = max_failures

        self.cap = None
        self.latest_frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.failure_count = 0

    def _open_camera(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        if platform.system() == "Windows":
            cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(self.camera_id)
        else:
            cap = cv2.VideoCapture(self.camera_id)

        if not cap.isOpened():
            return False

        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.cap = cap
        self.failure_count = 0
        return True

    def _loop(self):
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                if not self._open_camera():
                    time.sleep(1.0)
                    continue

            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.failure_count += 1
                if self.failure_count >= self.max_failures:
                    try:
                        self.cap.release()
                    except Exception:
                        pass
                    self.cap = None
                time.sleep(0.03)
                continue

            self.failure_count = 0
            with self.lock:
                self.latest_frame = frame

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def get_frame(self):
        with self.lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()

    def wait_until_ready(self, timeout=10.0):
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if self.get_frame() is not None:
                return True
            time.sleep(0.1)
        return False

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2.0)
            self.thread = None
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
