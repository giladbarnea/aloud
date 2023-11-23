import builtins
from collections.abc import Generator
from pathlib import Path
from typing import TypeAlias

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from rich import get_console
from rich.color import Color
from rich.style import Style
from rich.text import Text
from rich.traceback import install

from aloud import util

from .to_markdown import to_markdown

Prompt: TypeAlias = str
install(show_locals=True)

TO_SPEAKABLE: Prompt = """
You are given a markdown representation of an article from the internet.

Convert the syntax of the markdown into text that can be read out, and keep any real text that is not markdown syntax as-is.
The general principle is that, as you know, saying "hashtag hastag <something>" does not make sense to humans, so you should convert that to something like "Moving on to the next part: <something>.", "Next: <something>", "Next Part: <something>", "Next Section: <something>", etc. You can make up new ways to say this. Be creative, mix it up.
Similarly, saying "Open square brackets, Press here, close square brackets, open parenthesis, https://www.google.com, close parenthesis" does not make sense to humans, so you should convert that to "There's a link to Google here.".
If a title is followed immediately by a subtitle, say "Moving on to the next part: <title>. Subtitle: <subtitle>".
Be mindful of how many levels of markdown headers the article contains; Choose the most appropriate way to announce the header, based on its depth. Different depths need to be announced differently.
If you encounter a table, replace it with "There's a table here that communicates the following information: <information>", where <information> is a short textual summary of the data in the table, and any conclusions that the reader is supposed to draw from it.
If you encounter code, replace it with "There's a code block here that <description>", where <description> is a short textual description of what the code accepts as input, what it outputs and what takeaway the reader was supposed to get from it. If there are a few code blocks somewhat consequtively, announce the subsequent ones with "Another code block describes <description>", "An additional code block shows <description>", etc.
Sentences that are completely in emphasis should be announced as "Now, this is important: <sentence>", or "This is important: <sentence>", or "Note, the following is emphasized: <sentence>", or "The following is emphasized: <sentence>", etc (You can make up new ways to say this. Be creative, mix it up).
Sentences with a word or a short phrase in emphasis should be followed by "the '<emphasized-words-with-hyphens>' part was emphasized".
Generalize this to the entirety of the markdown syntax.
The transitions should be smooth and natural.
Where the text is plain, without any markdown syntax or formatting, keep it exactly the same. Do not summarize.

The article's markdown representation is:
```md
{markdown}
```
""".strip()


def to_speakable(thing: str | Path, output_dir: str | Path) -> Generator[str, None, None]:
    console = get_console()
    if Path(thing).is_file():
        thing = Path(thing).read_text()
    if util.is_url(url := str(thing)):
        with console.status("Fetching HTML of article...", spinner="aesthetic", refresh_per_second=10) as live:
            builtins.live = live
            html = fetch_html(url, remove_head=True)
    else:
        html = thing
    output_dir = Path(output_dir)
    html_path = output_dir / f"{output_dir.name}.html"
    console.print("\n[b green]Wrote HTML to", html_path.name)
    html_path.write_text(html)
    with console.status("Converting to markdown...", spinner="aesthetic", refresh_per_second=10) as live:
        builtins.live = live
        markdown = to_markdown(html)
    markdown_path = output_dir / f"{output_dir.name}.md"
    markdown_path.write_text(markdown)
    console.print("\n[b green]Wrote markdown to", markdown_path.name)
    oai = OpenAI()
    model = "gpt-4-1106-preview"
    speakable = "\n"
    with console.status(
        f"Converting markdown to speakable with {model}...", spinner="aesthetic", refresh_per_second=10
    ) as live:
        builtins.live = live
        start_color = (125, 125, 125)
        end_color = (255, 255, 255)
        to_speakable_with_markdown = TO_SPEAKABLE.format(markdown=markdown)
        for stream_chunk in oai.chat.completions.create(
            messages=[{"role": "user", "content": to_speakable_with_markdown}], model=model, temperature=0, stream=True
        ):
            delta = stream_chunk.choices[0].delta.content or ""
            yield delta
            speakable += delta
            speakable_lines = speakable.splitlines()
            display_speakable = Text()
            num_lines = console.height - 5
            for i, line in enumerate(speakable_lines[-num_lines:]):
                color_rgb = get_gradient_color(start_color, end_color, num_lines - 1, i)
                color = Color.from_rgb(*color_rgb)
                display_speakable += Text(f"{line}\n", style=Style(color=color))
            live.update(display_speakable, spinner_style=Style(color=Color.from_rgb(0, 0, 0)))
    console.print(speakable)
    speakable_text_path = output_dir / f"{output_dir.name}.txt"
    speakable_text_path.write_text(speakable)
    console.print("\n[b green]Wrote speakable to", speakable_text_path)


def fetch_html(url: str, *, remove_head: bool = False) -> str:
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    remove_head and soup.select_one("head").decompose()
    return soup.prettify()


def get_gradient_color(start_color, end_color, num_steps, step):
    r_start, g_start, b_start = start_color
    r_end, g_end, b_end = end_color

    r = r_start + (r_end - r_start) * step / num_steps
    g = g_start + (g_end - g_start) * step / num_steps
    b = b_start + (b_end - b_start) * step / num_steps

    return int(r), int(g), int(b)
