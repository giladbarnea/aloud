from pathlib import Path

from aloud.cli_utils import prepare_output_dir
from aloud.console import console
from aloud.convert import to_markdown
from aloud.convert.to_markdown import convert_to_raw_markdown

print = console.print


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
    html = Path(
        'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
    ).read_text()
    temp_dir = prepare_output_dir(None, None)
    raw_markdown = convert_to_raw_markdown(html)
    Path(temp_dir / 'raw_markdown.md').write_text(raw_markdown)
    markdown = to_markdown(html)
    Path(temp_dir / 'markdown.md').write_text(markdown)
    print(markdown)
    print()
