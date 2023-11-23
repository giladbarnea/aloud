import random
import string
from pathlib import Path
from string import punctuation


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
