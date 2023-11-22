import os

import pytest
import requests
from pytest import fixture


def pytest_sessionstart(session: pytest.Session):
    import dotenv

    dotenv.load_dotenv()
    os.environ.setdefault("COLUMNS", "160")
    os.environ.update(FORCE_COLOR="true")


@fixture(scope="session")
def get_html():
    return get_html_fixture


def get_html_fixture(url, *, remove_head: bool = True) -> str:
    from bs4 import BeautifulSoup

    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    remove_head and soup.select_one("head").decompose()
    return soup.prettify()


@fixture(scope="session")
def get_markdown():
    return get_markdown_fixture


def get_markdown_fixture(url_or_html, *, remove_head: bool = True, ignore_links=True) -> str:
    import html2text

    if url_or_html.startswith("http"):
        url = url_or_html
        html = get_html_fixture(url, remove_head=remove_head)
    else:
        html = url_or_html
    md_converter = html2text.HTML2Text(bodywidth=int(os.environ.get("COLUMNS", 0)))
    md_converter.ignore_links = ignore_links
    markdown = md_converter.handle(html)
    return markdown
