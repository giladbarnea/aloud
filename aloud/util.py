import random
import string
from pathlib import Path
from string import punctuation

from rich import get_console


def is_url(thing) -> bool:
    return str(thing).startswith("http")


def is_file(value: str | Path) -> bool:
    try:
        return Path(value).expanduser().is_file()
    except OSError:
        return False


def is_pathlike(thing: str | Path) -> bool:
    str_thing = str(thing)
    if is_url(str_thing):
        return False
    if Path(thing).expanduser().exists():
        return True
    if "/" not in str_thing:
        return False
    illegal_path_chars = "".join(set(punctuation) - {"-", "_", "~"})
    return not any(char in illegal_path_chars for char in str_thing)


def is_empty_dir(path: Path) -> bool:
    return not any(path.iterdir())


def random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def print_diff(string_1, string_2) -> None:
    import os

    string_1_path = Path(f"/tmp/{random_string(4)}")
    string_2_path = Path(f"/tmp/{random_string(4)}")

    string_1_path.write_text(string_1)
    string_2_path.write_text(string_2)

    os.system(f"delta --side-by-side --paging never --width={get_console().width} {string_1_path} {string_2_path}")
