import builtins
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import html2text

from aloud.console import console
from aloud.openai import oai


@console.with_status('Converting to markdown...')
def to_markdown(html: str, *, output_dir: Path = None) -> str:
    markdown = convert_to_raw_markdown(html)
    with ThreadPoolExecutor(max_workers=3) as executor:
        first_real_article_line_future = executor.submit(get_first_real_article_line, markdown)
        first_post_title_line_future = executor.submit(get_first_post_title_line, markdown)
        last_real_article_line_future = executor.submit(get_last_real_article_line, markdown)
    first_real_article_line = first_real_article_line_future.result()
    first_post_title_line = first_post_title_line_future.result()
    last_real_article_line = last_real_article_line_future.result()
    clean_markdown = remove_lines_until(markdown, first_real_article_line)
    clean_markdown = remove_lines_until(clean_markdown, first_post_title_line)
    clean_markdown = remove_lines_after(clean_markdown, last_real_article_line)
    clean_markdown = clean_markdown.strip()
    if output_dir:
        markdown_path = output_dir / f'{output_dir.name}.md'
        markdown_path.write_text(clean_markdown)
        console.print('\n[b green]Wrote markdown to', markdown_path.name)
    return clean_markdown


def convert_to_raw_markdown(html: str) -> str:
    """https://github.com/Alir3z4/html2text/blob/master/docs/usage.md"""
    md_converter = html2text.HTML2Text(bodywidth=0)
    # md_converter.ignore_links             # Do not include any formatting for links. default False
    # md_converter.unicode_snob             # Use unicode throughout instead of ASCII. default False
    # md_converter.images_as_html           # always generate HTML tags for images; preserves `height`, `width`, `alt` if possible.
    #  default False.
    # md_converter.drop_white_space
    # md_converter.empty_link
    # md_converter.inline_links             # for formatting images and links. default True
    # md_converter.links_each_paragraph     # putting links after every paragraph. default False
    # md_converter.mark_code                # wrap 'pre' blocks with [code]...[/code] tags. default False
    # md_converter.maybe_automatic_link
    # md_converter.protect_links            # protect from line breaks. default False
    # md_converter.use_automatic_links      # convert <a href='http://xyz'>http://xyz</a> to <http://xyz>. default True
    # md_converter.pad_tables               # Use padding to make tables look good. default False
    # md_converter.bypass_tables            # format tables in HTML rather than Markdown. default False
    # md_converter.ignore_tables            # ignore table-related tags (table, th, td, tr) while keeping rows. default False
    # md_converter.wrap_links               # links have to be wrapped during text wrapping (implies INLINE_LINKS = False). default False
    # md_converter.wrap_list_items          # list items have to be wrapped during text wrapping. default False
    # md_converter.skip_internal_links      # default True
    # md_converter.single_line_break        # Use a single line break after a block element rather than two. default False
    md_converter.unicode_snob = True
    md_converter.protect_links = True
    md_converter.pad_tables = True
    markdown = md_converter.handle(html).strip()
    markdown = re.sub(r'\n\n\n+', '\n\n', markdown)
    markdown = re.sub(r'  +', ' ', markdown)
    markdown = '\n'.join(line.strip() for line in markdown.splitlines())
    return markdown


def get_first_real_article_line(markdown: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Often, the markdown will start with things that used to be the website's navigation bar, social media links, etc, and only after that will the actual article start, usually with a title.
            Find the line where the real article starts, and return exactly that line, and only it, without explanation or anything else.
        
            The article's markdown representation is:
            ```md
            {markdown}
            ```
            """,
        )
        .format(markdown=markdown)
        .strip()
    )
    chat_completion = oai.chat.completions.create(
        messages=[{'role': 'system', 'content': prompt}],
        model='gpt-4-1106-preview',
        temperature=0,
        stream=False,
        timeout=10,
    )
    first_real_article_line = chat_completion.choices[0].message.content.splitlines()[0]
    return first_real_article_line


def get_first_post_title_line(markdown: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Often, right after the main title of the article, and just before the real actual content woudl start, and after that, things that used to be social media links, buttons and statistics would appear. Those elements are called "junk elements".
            Find the line where the real article starts, just after the "junk elements", and return exactly that line, and only it, without explanation or anything else.
            If the article does not contain "junk elements", your instruction stays the same: return the first line.
        
            The article's markdown representation is, enclosed in triple backticks:
            ```md
            {markdown}
            ```
            """,
        )
        .format(markdown=markdown.strip())
        .strip()
    )
    chat_completion = oai.chat.completions.create(
        messages=[{'role': 'system', 'content': prompt}],
        model='gpt-4-1106-preview',
        temperature=0,
        stream=False,
        timeout=10,
    )
    last_real_article_line = chat_completion.choices[0].message.content.splitlines()[0]
    return last_real_article_line


def get_last_real_article_line(markdown: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Often, at the bottom of the article, the article's real actual content would end, and after that, things that used to be the website's comment section, social media links, navigation elements and buttons would appear. Those elements are called "junk elements".
            Find the last line of the real content, just before where the "junk elements" appear, and return exactly that last real content line, and only it, without explanation.
            If the article does not contain "junk elements", your instruction stays the same: return the last line.
        
            The article's markdown representation is, enclosed in triple backticks:
            ```md
            {markdown}
            ```
            """,
        )
        .format(markdown=markdown.strip())
        .strip()
    )
    chat_completion = oai.chat.completions.create(
        messages=[{'role': 'system', 'content': prompt}],
        model='gpt-4-1106-preview',
        temperature=0,
        stream=False,
        timeout=10,
    )
    last_real_article_line = chat_completion.choices[0].message.content.splitlines()[0]
    return last_real_article_line


def remove_lines_until(markdown: str, line: str) -> str:
    markdown_lines = markdown.splitlines()
    line_index = index_of(markdown_lines, line)
    console.log(f'line (idx {line_index}):\n{line!r}')
    clean_markdown = '\n'.join(markdown_lines[line_index:])
    return clean_markdown


def remove_lines_after(markdown: str, line: str) -> str:
    markdown_lines = markdown.splitlines()
    reversed_markdown_lines = list(reversed(markdown_lines))
    line_reverse_index = index_of(reversed_markdown_lines, line)
    console.log(f'line (idx -{line_reverse_index}):\n{line!r}')
    if line_reverse_index == 0:
        return markdown
    clean_markdown = '\n'.join(markdown_lines[:-line_reverse_index])
    return clean_markdown


def index_of(string_lines: list[str], substring: str, *, case_sensitive=True) -> int:
    lines_equal_to_substring = [line for line in string_lines if line == substring]
    if lines_equal_to_substring:
        return string_lines.index(lines_equal_to_substring[0])
    lines_starting_with_substring = [line for line in string_lines if line.startswith(substring)]
    if lines_starting_with_substring:
        return string_lines.index(lines_starting_with_substring[0])
    lines_containing_substring = [line for line in string_lines if substring in line]
    if lines_containing_substring:
        return string_lines.index(lines_containing_substring[0])
    if case_sensitive:
        return index_of([line.lower() for line in string_lines], substring.lower(), case_sensitive=False)
    hasattr(builtins, 'live') and builtins.live.stop()
    breakpoint()
