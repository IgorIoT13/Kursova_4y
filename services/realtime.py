"""Simple in-process realtime broadcaster using per-user event queues for SSE.

This is intentionally minimal and works for single-process dev/testing. For production
use a dedicated pub/sub or websocket server.
"""
import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict


class RealtimeBroadcaster:
    def __init__(self):
        # mapping user_id -> deque of messages
        self.queues: Dict[int, Deque[str]] = defaultdict(lambda: deque())
        self.locks: Dict[int, threading.Condition] = defaultdict(lambda: threading.Condition())

    def publish(self, user_id: int, message: str):
        cond = self.locks[user_id]
        with cond:
            self.queues[user_id].append(message)
            cond.notify_all()

    def listen(self, user_id: int):
        """Generator that yields messages for the given user_id.
        Blocks waiting for new messages with a timeout to allow keep-alive comments.
        """
        cond = self.locks[user_id]
        q = self.queues[user_id]
        while True:
            with cond:
                if not q:
                    # wait up to 15s for new messages
                    cond.wait(timeout=15.0)
                while q:
                    msg = q.popleft()
                    yield msg
            # yield keepalive comment occasionally via outer loop
            yield None


# shared singleton for the app
broadcaster = RealtimeBroadcaster()
