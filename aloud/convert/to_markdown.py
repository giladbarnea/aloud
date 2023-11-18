import os

import html2text


def to_markdown(html, *, ignore_links: bool = True) -> str:
    md_converter = html2text.HTML2Text(bodywidth=int(os.environ.get("COLUMNS", 0)))
    md_converter.ignore_links = ignore_links
    markdown = md_converter.handle(html)
    return markdown
