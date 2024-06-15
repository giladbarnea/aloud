import builtins
import logging
import os
import sys
from collections.abc import Callable
from typing import ParamSpec, Self, TypeVar

import rich
import rich.pretty
from rich.color import Color
from rich.console import Console as RichConsole
from rich.console import Group, RenderableType
from rich.live import Live
from rich.logging import RichHandler
from rich.status import Status as RichStatus
from rich.style import Style, StyleType


def running_pytest() -> bool:
    return os.getenv('PYTEST_CURRENT_TEST') or 'pytest' in sys.argv[0]


P = ParamSpec('P')
R = TypeVar('R')


class Status(RichStatus):
    def __enter__(self: Self) -> Self:
        status = super().__enter__()
        builtins.live = self
        return status

    # noinspection PyMethodOverriding
    def update(
        self: Self,
        status: RenderableType | None = None,
        *,
        spinner: str | None = None,
        speed: float | None = None,
    ) -> None:
        super().update(status, spinner=spinner, spinner_style=Style(color=Color.from_rgb(0, 0, 0)), speed=speed)


class Console(RichConsole):
    logger: logging.Logger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_logger()

    def _init_logger(self):
        rich_handler = RichHandler(
            console=self,
            level='DEBUG',
            omit_repeated_times=False,
            enable_link_path=False,
            rich_tracebacks=True,
            tracebacks_extra_lines=5,
            tracebacks_show_locals=True,
            tracebacks_suppress=('.venv',),
            locals_max_string=1000,
            locals_max_length=1000,
            log_time_format='%X.%s',
        )
        logger = logging.getLogger('rich')
        [logger.removeHandler(h) for h in logger.handlers]
        logger.addHandler(rich_handler)
        logger.setLevel('DEBUG')
        self.logger = logger

    def log(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 2) -> None:
        level, objects = self._separate_level_from_objects(objects)
        self.logger.log(level, *objects, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel)

    def debug(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 3):
        self.log('DEBUG', *objects, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel)

    def info(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 3):
        self.log('INFO', *objects, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel)

    def warning(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 3):
        self.log('WARNING', *objects, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel)

    def error(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 3):
        self.log('ERROR', *objects, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel)

    def exception(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 3):
        self.log('ERROR', *objects, exc_info=True, stack_info=stack_info, stacklevel=stacklevel)

    def critical(self, *objects, exc_info=None, stack_info=False, stacklevel: int = 3):
        self.log('CRITICAL', *objects, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel)

    def panel(self, object, *objects, title=None, subtitle=None, highlight=True, **rich_panel_kwargs):
        if objects:
            object = Group(*map(rich.pretty.pretty_repr, (object, *objects)))
        else:
            object = rich.pretty.pretty_repr(object)
        self.print(rich.panel.Panel(object, title=title, subtitle=subtitle, highlight=highlight, **rich_panel_kwargs))

    # noinspection PyUnresolvedReferences
    def _separate_level_from_objects(self, objects: tuple) -> tuple[int, tuple]:
        level, *objects = objects
        default_level = logging.INFO
        if level in set(logging._nameToLevel) | set(map(str.lower, logging._nameToLevel)):
            level = logging._nameToLevel[level.upper()]
        elif level not in logging._levelToName:
            objects = (level, *objects)
            level = default_level
        return level, objects

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
    color_system='truecolor',
    force_terminal=True,
    force_interactive=True,
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
