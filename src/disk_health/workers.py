"""Worker threads pour les opérations asynchrones."""

import asyncio
from collections.abc import Awaitable

from PySide6.QtCore import QThread, Signal


class AsyncWorker(QThread):
    """Worker thread pour les opérations asynchrones."""

    finished = Signal(object)

    def __init__(self, coroutine: Awaitable) -> None:  # ANN401
        super().__init__()
        self.coroutine = coroutine

    def run(self) -> None:
        """Exécute la coroutine de manière asynchrone."""
        result = asyncio.run(self.coroutine)
        self.finished.emit(result)
