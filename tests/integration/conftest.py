from __future__ import annotations

import typing

import pytest

if typing.TYPE_CHECKING:
    from aloud.convert.to_markdown.to_markdown import _to_markdown


@pytest.fixture(scope='session')
def to_markdown() -> _to_markdown:
    from aloud.convert import to_markdown

    return to_markdown
