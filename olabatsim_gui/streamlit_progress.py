# streamlit_progress.py
import time

import streamlit as st
from olabatsim.progressutils import ProgressHandler


class StreamlitHandler(ProgressHandler):
    def __init__(self, desc="Processing"):
        self.desc = desc
        self.progress_bar = None
        self.status = None
        self.total = 1
        self.current = 0

    def _format_time(self, seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}h {m}m {s}s"
        elif m > 0:
            return f"{m}m {s}s"
        else:
            return f"{s}s"

    def start(self, total):
        self.total = total
        self.current = 0
        self.progress_bar = st.progress(0)
        self.status = st.empty()
        self.start_time = time.time()
        self.status.write(f"{self.desc}: 0 / {self.total}")

    def update(self, n=1):
        self.current += n
        percent = int((self.current / self.total) * 100)
        elapsed = time.time() - self.start_time
        eta = (
            (elapsed / self.current) * (self.total - self.current)
            if self.current
            else 0
        )
        self.progress_bar.progress(min(percent, 100))
        self.status.write(
            f"{self.desc}: {self.current} / {self.total} | "
            f"Elapsed: {self._format_time(elapsed)} | "
            f"ETA: {self._format_time(eta)}"
        )

    def elapsed_time(self):
        return time.time() - getattr(self, "start_time", 0)

    def close(self):
        # self.progress_bar.empty()
        if self.status:
            self.status.write(
                f"{self.desc} done ✅\nTotal time: {self._format_time(self.elapsed_time())}"
            )
