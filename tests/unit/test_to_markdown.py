import textwrap
from pathlib import Path

from aloud.cli_utils import prepare_output_dir
from aloud.console import console
from aloud.convert import to_markdown
from aloud.convert.to_markdown import (
    add_line_numbers,
    convert_to_raw_markdown,
    get_image_links,
)

p = console.print


def test_langchain_promptlayer():
    promptlayer_html = Path('tests/data/promptlayer/promptlayer.html').read_text()
    markdown = to_markdown(promptlayer_html)
    markdown_lines = markdown.splitlines()
    first_line = markdown_lines[0]
    last_line = markdown_lines[-1]
    assert first_line == '# PromptLayer'
    assert last_line.startswith('PromptLayer also provides native wrappers for')


def test_links_and_images():
    """https://www.oneusefulthing.org/p/reshaping-the-tree-rebuilding-organizations"""
    thing = 'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
    html = Path(thing).read_text()
    temp_dir = prepare_output_dir(thing, '/tmp')
    print(temp_dir)
    (temp_dir / 'html.html').write_text(html)
    raw_markdown = convert_to_raw_markdown(html)
    (temp_dir / 'raw_markdown.md').write_text(raw_markdown)
    image_links = get_image_links(raw_markdown)
    console.log('image_links:', image_links)
    return
    markdown = to_markdown(html)
    (temp_dir / 'markdown.md').write_text(markdown)
    assert markdown.endswith(
        'I am not sure who said it first, but there are only two ways to react to exponential change: '
        'too early or too late. Today’s AIs are flawed and limited in many ways. '
        'While that restricts what AI can do, the capabilities of AI are increasing exponentially, '
        'both in terms of the models themselves and the tools these models can use. '
        'It might seem too early to consider changing an organization to accommodate AI, '
        'but I think that there is a strong possibility that it will quickly become too late.'
    )


def test_add_line_numbers():
    markdown = textwrap.dedent(
        """
        # Title
        ## Subtitle
        
        Paragraph
        
        List:
        - Item 1
        - Item 2
        - Item 3
        
        Paragraph
        
        Table:
        | Header 1 | Header 2 |
        | -------- | -------- |
        | Cell 1   | Cell 2   |
        """,
    ).strip()
    markdown_with_line_numbers = add_line_numbers(markdown).removeprefix('\n').removesuffix('\n')
    expected = (
        textwrap.dedent(
            """
         0 │ # Title
         1 │ ## Subtitle
         2 │ 
         3 │ Paragraph
         4 │ 
         5 │ List:
         6 │ - Item 1
         7 │ - Item 2
         8 │ - Item 3
         9 │ 
        10 │ Paragraph
        11 │ 
        12 │ Table:
        13 │ | Header 1 | Header 2 |
        14 │ | -------- | -------- |
        15 │ | Cell 1   | Cell 2   |
        """
        )
        .removeprefix('\n')
        .removesuffix('\n')
    )
    assert markdown_with_line_numbers == expected
