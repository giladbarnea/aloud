import os

import pytest
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from pytest import fixture
from rich.traceback import Traceback

from aloud import convert
from aloud.console import console


def pytest_sessionstart(session: pytest.Session):
    import dotenv

    dotenv.load_dotenv()
    os.environ.setdefault('COLUMNS', '160')
    os.environ.update(FORCE_COLOR='true')


def pytest_runtest_makereport(item: Item, call: CallInfo) -> TestReport | None:
    test_failed: bool = call.when == 'call' and call.excinfo is not None
    if not test_failed:
        return
    print_rich_traceback(call.excinfo.value)


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
    return request.node.name.replace('[', '_').replace(']', '_')


def print_rich_traceback(
    exception: BaseException,
    *args,
    extra_lines=7,
    show_locals=True,
    locals_max_string=1000,
    locals_max_length=1000,
    width=console.width,
    suppress=('.venv',),
    console=console,
):
    traceback = Traceback.from_exception(
        type(exception),
        exception,
        traceback=exception.__traceback__,
        extra_lines=extra_lines,
        show_locals=show_locals,
        locals_max_string=locals_max_string,
        locals_max_length=locals_max_length,
        suppress=suppress,
        width=width,
    )

    console.print(traceback, *args)
