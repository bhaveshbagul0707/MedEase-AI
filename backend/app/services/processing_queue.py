from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Any


class ProcessingQueue(ABC):
    @abstractmethod
    async def enqueue(self, func: Callable[..., Any], *args, **kwargs) -> None:
        """Enqueue a processing task represented by func(*args, **kwargs)."""


class InProcessQueue(ProcessingQueue):
    def __init__(self):
        # simple in-process queue - tasks will be scheduled on the event loop
        self._tasks = set()

    async def enqueue(self, func: Callable[..., Any], *args, **kwargs) -> None:
        """Enqueue the task. If a keyword arg 'session' is provided, run inline (await) so the task can reuse the
        request-scoped AsyncSession (useful in tests). Otherwise schedule as background task on the event loop."""
        # If caller passed a session, run inline to reuse the same DB session/transaction
        if "session" in kwargs:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                await result
            return

        # schedule the task and keep reference to avoid garbage collection
        loop = asyncio.get_event_loop()

        async def _runner():
            try:
                result = func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    await result
            finally:
                # task will be removed by callback
                pass

        task = loop.create_task(_runner())

        def _on_done(t):
            self._tasks.discard(t)

        task.add_done_callback(_on_done)
        self._tasks.add(task)
