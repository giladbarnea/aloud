import re
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import html2text

from aloud.console import console
from aloud.openai import oai
from aloud.text import has_line_numbers, remove_lines_after, remove_lines_until
from aloud.vision import inject_image_descriptions_as_alt


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


def find_real_article_boundaries(markdown):
    with ThreadPoolExecutor(max_workers=3) as executor:
        first_real_article_line_future = executor.submit(find_first_real_article_line, markdown)
        first_post_title_line_future = executor.submit(find_first_post_title_line, markdown)
        last_real_article_line_future = executor.submit(find_last_real_article_line, markdown)
    first_real_article_line = first_real_article_line_future.result()
    first_post_title_line = first_post_title_line_future.result()
    last_real_article_line = last_real_article_line_future.result()
    return first_real_article_line, first_post_title_line, last_real_article_line


def find_first_real_article_line(markdown: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Often, the markdown will start with things that used to be the website's navigation bar, social media links, etc, and only after that will the actual article start, usually with a title.
            Find the line where the real article starts, and return exactly that line, and only it, without explanation or anything else.
        
            The article's markdown representation is:
            
            {markdown}
            
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


def find_first_post_title_line(markdown: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Often, right after the main title of the article, and just before the real actual content woudl start, and after that, things that used to be social media links, buttons and statistics would appear. Those elements are called "junk elements".
            Find the line where the real article starts, just after the "junk elements", and return exactly that line, and only it, without explanation or anything else.
            If the article does not contain "junk elements", your instruction stays the same: return the first line.
        
            The article's markdown representation is:
            
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
    last_real_article_line = chat_completion.choices[0].message.content.splitlines()[0]
    return last_real_article_line


def find_last_real_article_line(markdown: str) -> str:
    prompt = (
        textwrap.dedent(
            """
            You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
            Often, at the bottom of the article, the article's real actual content would end, and after that, things that used to be the website's comment section, social media links, navigation elements and buttons would appear. Those elements are called "junk elements".
            Find the last line of the real content, just before where the "junk elements" appear, and return exactly that last real content line, and only it, without explanation.
            If the article does not contain "junk elements", your instruction stays the same: return the last line.
        
            The article's markdown representation is:
            
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
    last_real_article_line = chat_completion.choices[0].message.content.splitlines()[0]
    return last_real_article_line


def clean_junk_sections(raw_markdown, first_real_article_line, first_post_title_line, last_real_article_line):
    clean_markdown = remove_lines_until(raw_markdown, first_real_article_line)
    clean_markdown = remove_lines_until(clean_markdown, first_post_title_line)
    clean_markdown = remove_lines_after(clean_markdown, last_real_article_line)
    clean_markdown = clean_markdown.strip()
    return clean_markdown


@console.with_status('Converting to markdown...')
def to_markdown(
    html: str,
    *,
    output_dir: Path = None,
    converts_to_raw_markdown=convert_to_raw_markdown,
    finds_real_article_boundaries=find_real_article_boundaries,
    cleans_junk_sections=clean_junk_sections,
    injects_image_descriptions_as_alt=inject_image_descriptions_as_alt,
) -> str:
    raw_markdown = converts_to_raw_markdown(html)
    first_real_article_line, first_post_title_line, last_real_article_line = finds_real_article_boundaries(raw_markdown)
    clean_markdown = cleans_junk_sections(
        raw_markdown, first_real_article_line, first_post_title_line, last_real_article_line
    )
    if output_dir:
        markdown_path = output_dir / f'{output_dir.name}.md'
        markdown_path.write_text(clean_markdown)
        console.print('\n[b green]Wrote markdown to', markdown_path.name)
    enriched_markdown = injects_image_descriptions_as_alt(clean_markdown)
    assert not has_line_numbers(enriched_markdown)
    return enriched_markdown
