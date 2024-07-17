from pathlib import Path

import requests
from bs4 import BeautifulSoup

from aloud import util
from aloud.console import console


@console.with_status('Fetching HTML of article...')
def to_html(url: str, *, remove_head: bool = False, output_dir: Path | None = None) -> str:
    if not util.is_url(url):
        return url
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    remove_head and soup.select_one('head').decompose()
    html = soup.prettify()
    if output_dir:
        html_path = output_dir / f'{output_dir.name}.html'
        html_path.write_text(html)
        console.print('\n[b green]Wrote HTML to', html_path.name)
    return html
