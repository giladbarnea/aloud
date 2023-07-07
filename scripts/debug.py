from pathlib import Path

import requests
from langchain.document_loaders import tomarkdown


def urltomd(url):
    loader = tomarkdown.ToMarkdownLoader(url, api_key=Path("~/.2markdown").expanduser().read_text().strip())
    doc = loader.load()[0]
    return doc


def get_html(url, *, remove_head: bool = True) -> str:
    from bs4 import BeautifulSoup

    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    remove_head and soup.select_one("head").decompose()
    return soup.prettify()
