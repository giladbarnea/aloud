import requests
from pytest import fixture


@fixture(scope="session")
def get_html(url, *, remove_head: bool = True) -> str:
    from bs4 import BeautifulSoup

    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    remove_head and soup.select_one("head").decompose()
    return soup.prettify()
