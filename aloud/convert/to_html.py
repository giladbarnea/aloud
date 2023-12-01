import requests
from bs4 import BeautifulSoup


def to_html(url: str, *, remove_head: bool = False) -> str:
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    remove_head and soup.select_one('head').decompose()
    return soup.prettify()
