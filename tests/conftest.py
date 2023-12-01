import os

import convert
import pytest
from pytest import fixture


def pytest_sessionstart(session: pytest.Session):
    import dotenv

    dotenv.load_dotenv()
    os.environ.setdefault('COLUMNS', '160')
    os.environ.update(FORCE_COLOR='true')


@fixture(scope='session')
def to_html():
    return convert.to_html


@fixture(scope='session')
def get_markdown():
    return get_markdown_fixture


def get_markdown_fixture(url_or_html, *, remove_head: bool = True, ignore_links=True) -> str:
    if url_or_html.startswith('http'):
        url = url_or_html
        html = convert.to_html(url, remove_head=remove_head)
    else:
        html = url_or_html
    from convert.to_markdown import convert_to_raw_markdown

    return convert_to_raw_markdown(html, ignore_links=ignore_links)
