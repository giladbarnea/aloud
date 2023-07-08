from pathlib import Path


def to_speakable(thing):
    return Path(thing).read_text()
