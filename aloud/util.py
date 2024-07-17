import os.path
import random
import string
from pathlib import Path
from string import punctuation

from aloud.console import console


def is_url(thing) -> bool:
    str_thing = str(thing)
    return str_thing.startswith(('http', 'www.'))


def is_file(value: str | Path) -> bool:
    try:
        return Path(value).expanduser().is_file()
    except OSError:
        return False


def is_pathlike(thing: str | Path | None) -> bool:
    if not thing:
        return False
    str_thing = str(thing)
    if is_url(str_thing):
        return False
    if Path(thing).expanduser().exists():
        return True
    if os.path.sep not in str_thing:
        return False
    legal_path_punctuation = {'-', '_', '~'}
    illegal_path_chars = ''.join(set(punctuation) - legal_path_punctuation)
    return not any(char in illegal_path_chars for char in str_thing)


def is_empty_dir(path: Path) -> bool:
    return not any(path.iterdir())


def random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def print_diff(string_1, string_2) -> None:
    import os

    string_1_path = Path(f'/tmp/{random_string(4)}')
    string_2_path = Path(f'/tmp/{random_string(4)}')

    string_1_path.write_text(string_1)
    string_2_path.write_text(string_2)

    os.system(f'delta --side-by-side --paging never --width={console.width} {string_1_path} {string_2_path}')  # noqa: S605  Shell


def strip_surrounding_punctuation(s: str) -> str:
    """
    >>> strip_surrounding_punctuation('!#hello!world!')
    'hello!world'
    >>> strip_surrounding_punctuation('whenim64')
    'whenim64'
    """
    return s.strip('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
