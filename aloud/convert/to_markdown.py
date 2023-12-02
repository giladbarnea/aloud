import builtins
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

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
    markdown_with_line_numbers = add_line_numbers(markdown)
    image_links = extract_image_links(markdown_with_line_numbers)
    return clean_markdown


def convert_to_raw_markdown(html: str, **html2text_kwargs) -> str:
    """https://github.com/Alir3z4/html2text/blob/master/docs/usage.md"""
    md_converter = html2text.HTML2Text(bodywidth=0)
    # md_converter.ignore_links             # Do not include any formatting for links. default False
    # md_converter.drop_white_space
    # md_converter.empty_link
    # md_converter.inline_links             # for formatting images and links. default True
    # md_converter.links_each_paragraph     # putting links after every paragraph. default False
    # md_converter.mark_code                # wrap 'pre' blocks with [code]...[/code] tags. default False
    # md_converter.maybe_automatic_link
    # md_converter.use_automatic_links      # convert <a href='http://xyz'>http://xyz</a> to <http://xyz>. default True
    # md_converter.bypass_tables            # format tables in HTML rather than Markdown. default False
    # md_converter.ignore_tables            # ignore table-related tags (table, th, td, tr) while keeping rows. default False
    # md_converter.wrap_links               # links have to be wrapped during text wrapping (implies INLINE_LINKS = False). default False
    # md_converter.wrap_list_items          # list items have to be wrapped during text wrapping. default False
    # md_converter.skip_internal_links      # default True
    # md_converter.single_line_break        # Use a single line break after a block element rather than two. default False
    md_converter.images_as_html = (
        True  # always generate HTML tags for images; preserves `height`, `width`, `alt` if possible. default False.
    )
    md_converter.unicode_snob = True  # Use unicode throughout instead of ASCII. default False
    md_converter.protect_links = True  # Protect from line breaks. default False
    md_converter.pad_tables = True  # Use padding to make tables look good. default False
    for key, value in html2text_kwargs.items():
        setattr(md_converter, key, value)
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
        
            The article's markdown representation is, enclosed in triple backticks:
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
        
            The article's markdown representation, enclosed in triple backticks:
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
        
            The article's markdown representation, enclosed in triple backticks:
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


def generate_image_description(image_link: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given an image link.
            Generate a short description for the image, and return exactly it, without explanation or anything else.
            If the image link is broken, or the image is not accessible, or the image is not an image, return: None
            
            The image link:
            {image_link}
            """,
        )
        .format(image_link=image_link.strip())
        .strip()
    )
    chat_completion = oai.chat.completions.create(
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {'type': 'image_url', 'image_url': {'url': image_link, 'detail':'high'}},
                ],
            }
        ],
        model='gpt-4-vision-preview',
        temperature=0,
        stream=False,
        timeout=10,
        max_tokens=1000
    )
    image_description = chat_completion.choices[0].message.content.splitlines()[0].strip()
    return image_description


def extract_image_links(markdown: str) -> list[str]:
    image_link_indices = get_image_link_indices(markdown)
    image_link_futures = []
    with ThreadPoolExecutor(max_workers=len(image_link_indices)) as executor:
        markdown_lines = markdown.splitlines()
        for index in image_link_indices:
            line = markdown_lines[index]
            future = executor.submit(extract_image_link, line)
            image_link_futures.append(future)
    image_links = []
    for future in image_link_futures:
        image_link = future.result()
        image_links.append(image_link)
    return image_links


def get_image_link_indices(markdown: str) -> list[int]:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Line numbers are shown on the left "gutter" of the markdown; the special vertical line `│` separates each line number from the rest of the line, and the first line is 0.
            Find all the image links in the article, and return their line numbers as listed in the gutters of the lines where the image links appear, separated by line breaks, and only them, without explanation or anything else.
            If the article does not contain any images, return: None

            The article's markdown representation:
            
            {markdown}
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
    image_link_indices = []
    for index in chat_completion.choices[0].message.content.splitlines():
        image_link_indices.append(int(index.strip()))
    return image_link_indices


def extract_image_link(markdown_line: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown line which contains an image link.
            Extract the image link, and return exactly it, without explanation or anything else.
            Note that sometimes, the domain of the link is that of a CDN, or analytics, or similar, but the actual image link is a parameter of the URL. An oversimplified example of such a link is: https://cdn.irrelevant.com/https://actual-link.com/image.png?width=100&height=100, in which case, you would return: https://actual-link.com/image.png 
            
            The markdown line, enclosed in triple backticks:
            ```md
            {markdown_line}
            ```
            """,
        )
        .format(markdown_line=markdown_line.strip())
        .strip()
    )
    chat_completion = oai.chat.completions.create(
        messages=[{'role': 'system', 'content': prompt}],
        model='gpt-4-1106-preview',
        temperature=0,
        stream=False,
        timeout=10,
    )
    image_link = chat_completion.choices[0].message.content.splitlines()[0].strip()
    unquoted_image_link = unquote(image_link)
    return unquoted_image_link


def add_line_numbers(markdown: str, *, separator='│') -> str:
    markdown_lines = markdown.splitlines()
    digits = len(str(len(markdown_lines)))
    for i, line in enumerate(markdown_lines):
        line_number = str(i).rjust(digits)
        markdown_lines[i] = f'{line_number} {separator} {line}'
    markdown = '\n'.join(markdown_lines)
    return markdown


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
        if len(lines_equal_to_substring) > 1:
            console.log(
                '⚠️ %d lines equal to substring %r' % (len(lines_equal_to_substring), substring), _stack_offset=2
            )
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
