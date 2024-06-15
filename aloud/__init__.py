from rich.traceback import install

install(show_locals=True, extra_lines=7, locals_max_length=1000, locals_max_string=1000, suppress=('.venv',))

from . import convert
from .yaml import yaml
