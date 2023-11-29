from rich.traceback import install

from . import convert

install(show_locals=True, extra_lines=7, locals_max_length=1000, locals_max_string=1000)
