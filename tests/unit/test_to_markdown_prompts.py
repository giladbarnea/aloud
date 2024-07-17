import pytest

from aloud.convert.to_markdown import prompts
from aloud.convert.to_markdown.prompts.prompts import PROMPTS_MODULE_PATH

MARKDOWN_PROMPT_NAMES = [
    'find_first_post_title_article_line',
    'find_first_real_article_line',
    'find_last_real_article_line',
]
assert {path.stem for path in PROMPTS_MODULE_PATH.glob('*.yaml')} == set(MARKDOWN_PROMPT_NAMES)


@pytest.mark.parametrize(
    'prompt_name',
    MARKDOWN_PROMPT_NAMES,
)
def test_yaml_constructs_fine(prompt_name):
    template = prompts.get(prompt_name)
    assert template


@pytest.mark.parametrize(
    'prompt_name',
    MARKDOWN_PROMPT_NAMES,
)
def test_templates_expect_only_markdown_variable(prompt_name):
    template = prompts.get(prompt_name)
    prompt_value = template.format_prompt(markdown='# Markdown')
    assert prompt_value
