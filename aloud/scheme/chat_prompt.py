from pathlib import Path
from typing import Any, Self

from aloud.yaml import yaml
from schemas.models import Chat


class ChatPrompt(Chat):
    def __init__(self: Self, *args, **data: Any) -> None:
        if args:
            data = yaml.load(Path(args[0]).read_text())
        super().__init__(**data)
