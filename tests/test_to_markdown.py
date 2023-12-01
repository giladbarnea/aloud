from pathlib import Path

from aloud.convert import to_markdown


def test_langchain_promptlayer():
    promptlayer_html = Path('tests/data/promptlayer.html').read_text()
    markdown = to_markdown(promptlayer_html)
    markdown_lines = markdown.splitlines()
    first_line = markdown_lines[0]
    last_line = markdown_lines[-1]
    assert first_line == '# PromptLayer'
    assert last_line.startswith('PromptLayer also provides native wrappers for')
