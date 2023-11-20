import os
import textwrap
from concurrent.futures import ThreadPoolExecutor

import html2text
from openai import OpenAI

oai = OpenAI()


def to_markdown(html, *, ignore_links: bool = True) -> str:
    md_converter = html2text.HTML2Text(bodywidth=int(os.environ.get("COLUMNS", 0)))
    md_converter.ignore_links = ignore_links
    markdown = md_converter.handle(html)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first_real_article_line_future = executor.submit(get_first_real_article_line, markdown)
        last_real_article_line_future = executor.submit(get_last_real_article_line, markdown)
    first_real_article_line = first_real_article_line_future.result()
    last_real_article_line = last_real_article_line_future.result()
    clean_markdown = remove_website_top_junk(markdown, first_real_article_line)
    clean_markdown = remove_website_bottom_junk(clean_markdown, last_real_article_line)
    return clean_markdown


def remove_website_top_junk(markdown, first_real_article_line):
    markdown_lines = markdown.splitlines()
    first_real_article_line_index = next(
        i for i, line in enumerate(markdown_lines) if line.startswith(first_real_article_line)
    )
    clean_markdown = "\n".join(markdown_lines[first_real_article_line_index:])
    return clean_markdown


def remove_website_bottom_junk(markdown, last_real_article_line):
    markdown_lines = markdown.splitlines()
    last_real_article_line_index = next(
        i for i, line in enumerate(reversed(markdown_lines)) if line.startswith(last_real_article_line)
    )
    clean_markdown = "\n".join(markdown_lines[:-last_real_article_line_index])
    return clean_markdown


def get_first_real_article_line(markdown):
    prompt = textwrap.dedent("""
    You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
    Often, the markdown will start with things that used to be the website's navigation bar, social media links, etc, and only after that will the actual article start, usually with a title.
    Find the line where the real article starts, and return exactly that line, and only it, without explanation or anything else.
    
    The article's markdown representation is:
    ```md
    {markdown}
    ```
    """).format(markdown=markdown).strip()
    chat_completion = oai.chat.completions.create(
        messages=[{"role": "system", "content": prompt}], model="gpt-4-1106-preview", temperature=0, stream=False
    )
    first_real_article_line = chat_completion.choices[0].message.content.strip()
    return first_real_article_line


def get_last_real_article_line(markdown):
    prompt = textwrap.dedent("""
    You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
    Often, towards the bottom of the markdown, the actual article content would end, and after that, things that used to be the website's comment section, social media links, etc would appear.
    Find the line where the real article ends, and return exactly that line, and only it, without explanation or anything else.

    The article's markdown representation is:
    ```md
    {markdown}
    ```
    """).format(markdown=markdown).strip()
    chat_completion = oai.chat.completions.create(
        messages=[{"role": "system", "content": prompt}], model="gpt-4-1106-preview", temperature=0, stream=False
    )
    last_real_article_line = chat_completion.choices[0].message.content.strip()
    return last_real_article_line
