from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
from typing import Any

from aloud.settings import dev_settings


class ThreadPoolExecutor(_ThreadPoolExecutor):
    def __init__(
        self,
        max_workers: int | None = None,
        thread_name_prefix: str = '',
        initializer: Callable[..., object] | None = None,
        initargs: tuple[Any, ...] = (),
    ):
        if not dev_settings.dev_allow_concurrency:
            max_workers = 1
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)
