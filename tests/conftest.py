import os

from aloud import convert
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


def get_markdown_fixture(url_or_html: str, *, remove_head: bool = True) -> str:
    from convert.to_markdown import convert_to_raw_markdown
    html = convert.to_html(url_or_html, remove_head=remove_head)
    return convert_to_raw_markdown(html)


@fixture(scope='function')
def current_test_name(request):
    return request.node.name.replace("[", "_").replace("]", "_")
