import builtins
from typing import Self

from rich.color import Color
from rich.console import Console as RichConsole
from rich.console import RenderableType
from rich.status import Status as RichStatus
from rich.style import Style, StyleType


class Status(RichStatus):
    def __enter__(self) -> Self:
        status = super().__enter__()
        builtins.live = self
        return status

    # noinspection PyMethodOverriding
    def update(
        self, status: RenderableType | None = None, *, spinner: str | None = None, speed: float | None = None
    ) -> None:
        super().update(status, spinner=spinner, spinner_style=Style(color=Color.from_rgb(0, 0, 0)), speed=speed)


class Console(RichConsole):
    def status(
        self,
        status: RenderableType,
        *,
        spinner: str = "aesthetic",
        spinner_style: StyleType = "status.spinner",
        speed: float = 1.0,
        refresh_per_second: float = 12.5
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


console = Console(
    color_system="truecolor",
    force_terminal=True,
    force_interactive=True,
    stderr=True,
    tab_size=4,
    log_time_format="%F %X.%s",  # or "[%T]", see https://docs.python.org/3/library/time.html#time.strftime
)