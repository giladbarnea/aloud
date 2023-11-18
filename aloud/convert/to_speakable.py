import textwrap
from pathlib import Path

from openai import OpenAI
from plum import dispatch
from bs4 import BeautifulSoup
import requests
from rich.color import Color
from rich.style import Style

from . import to_markdown
from rich import get_console


def fetch_html(url: str, *, remove_head: bool = False) -> str:
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    remove_head and soup.select_one("head").decompose()
    return soup.prettify()


@dispatch
def to_speakable(path: Path):
    return to_speakable(path.read_text())


@dispatch
def to_speakable(thing: str) -> str:
    console = get_console()
    if thing.startswith("http"):
        with console.status("Getting HTML of article...", spinner="aesthetic", refresh_per_second=100) as live:
            html = fetch_html(thing)
    else:
        html = thing
    with console.status("Converting to markdown...", spinner="aesthetic", refresh_per_second=100) as live:
        markdown = to_markdown.to_markdown(html)
    oai = OpenAI()
    prompt = textwrap.dedent("""
    You are given a markdown representation of an article from the internet.

    Convert the syntax of the markdown into text that can be read out. 
    The general principle is that, as you know, saying "hashtag hastag <something>" does not make sense to humans, so you should convert that to something like "Moving on to the next part: <something>.", or "Next: <something>", or similar (be creative, mix it up).
    Similarly, saying "Open square brackets, Press here, close square brackets, open parenthesis, https://www.google.com, close parenthesis" does not make sense to humans, so you should convert that to "There's a link to Google here.".
    If a title is followed immediately by a subtitle, say "Moving on to the next part: <title>. Subtitle: <subtitle>".
    When you encounter a table, replace it with "There's a table here that communicates the following information: <short textual summary of information embedded in the table>".
    Generalize this to the entirety of the markdown syntax.
    The transitions should be smooth and natural.
    Keep the text of the article exactly the same.

    The article's markdown representation is:
    ```md
    {markdown}
    ```
    """).format(markdown=markdown).strip()
    model = "gpt-4-1106-preview"
    speakable = "\n"
    with console.status(
        f"Converting markdown to speakable with {model}...", spinner="aesthetic", refresh_per_second=100
    ) as live:
        for stream_chunk in oai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=model, temperature=0, stream=True
        ):
            speakable += stream_chunk.choices[0].delta.content or ""
            live.update(speakable[-1000:], spinner_style=Style(color=Color.from_rgb(0, 0, 0)))
    return speakable.strip()
