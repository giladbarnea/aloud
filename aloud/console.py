import builtins
import os
import sys
from collections.abc import Callable
from typing import ParamSpec, Self, TypeVar

from rich.color import Color
from rich.console import Console as RichConsole
from rich.console import RenderableType
from rich.live import Live
from rich.status import Status as RichStatus
from rich.style import Style, StyleType

running_pytest = lambda: os.getenv('PYTEST_CURRENT_TEST') or 'pytest' in sys.argv[0]

P = ParamSpec('P')
R = TypeVar('R')


class Status(RichStatus):
    def __enter__(self) -> Self:
        status = super().__enter__()
        builtins.live = self
        return status

    # noinspection PyMethodOverriding
    def update(
        self,
        status: RenderableType | None = None,
        *,
        spinner: str | None = None,
        speed: float | None = None,
    ) -> None:
        super().update(status, spinner=spinner, spinner_style=Style(color=Color.from_rgb(0, 0, 0)), speed=speed)


class Console(RichConsole):
    def status(
        self,
        status: RenderableType,
        *,
        spinner: str = 'aesthetic',
        spinner_style: StyleType = 'status.spinner',
        speed: float = 1.0,
        refresh_per_second: float = 12.5,
    ) -> Status:
        status_renderable = Status(
            status,
            console=self,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
            refresh_per_second=refresh_per_second,
        )
        return status_renderable

    def set_live(self, live: Live) -> None:
        # todo: queue of lives
        with self._lock:
            if self._live is not None:
                self._live.stop()
            self._live = live

    def with_status(
        self,
        status: RenderableType,
        *,
        spinner: str = 'aesthetic',
        spinner_style: StyleType = 'status.spinner',
        speed: float = 1.0,
        refresh_per_second: float = 12.5,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            if running_pytest():
                return func
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with self.status(
                    status,
                    spinner=spinner,
                    spinner_style=spinner_style,
                    speed=speed,
                    refresh_per_second=refresh_per_second,
                ):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


console = Console(
    # color_system='truecolor',
    # force_terminal=True,
    # force_interactive=True,
    stderr=True,
    tab_size=4,
    log_time_format='%F %X',  # or "[%T]", see https://docs.python.org/3/library/time.html#time.strftime
)


def get_gradient_color(start_color, end_color, num_steps, step):
    r_start, g_start, b_start = start_color
    r_end, g_end, b_end = end_color

    r = r_start + (r_end - r_start) * step / num_steps
    g = g_start + (g_end - g_start) * step / num_steps
    b = b_start + (b_end - b_start) * step / num_steps

    return int(r), int(g), int(b)
