import re

import html2text


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
