from __future__ import annotations

import functools
import typing
from unittest.mock import MagicMock

import pytest

if typing.TYPE_CHECKING:
    from aloud.convert import to_markdown


@pytest.fixture(scope='session')
def to_markdown() -> to_markdown:
    from aloud.convert import to_markdown

    injects_image_descriptions_as_alt = MagicMock(side_effect=lambda x: x)

    @functools.wraps(to_markdown)
    def wrapper(html: str, **kwargs) -> str:
        return to_markdown(html, injects_image_descriptions_as_alt=injects_image_descriptions_as_alt, **kwargs)

    return wrapper
