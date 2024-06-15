from pathlib import Path
from typing import overload

from schemas.models import Chat

class ChatPrompt(Chat):
    @overload
    def __init__(self, file_path: str | Path) -> None: ...
    @overload
    def __init__(self, **data) -> None: ...
