import textwrap
from pathlib import Path

import pytest

from aloud.text import add_line_numbers, index_of, remove_line_numbers

SOURCE_INTERCONNECTS_Q_STAR = Path('tests/data/interconnects_q_star/interconnects_q_star.md').read_text()

EQUALS_UNIQUE = dict(
    source=SOURCE_INTERCONNECTS_Q_STAR,
    substring='And the funny feedback interface they used (which will be replaced by AIs), but is instructive:',
    expected_index=113,
)
EQUAL_MULTIPLE = dict(
    source="""how
hello world

are you
hello
hello world
bye""",
    substring='hello world',
    expected_index=1,
)
STARTWITH_UNIQUE = dict(
    source=SOURCE_INTERCONNECTS_Q_STAR,
    substring='Promoting techniques like “take a deep breath” and “think step by step”',
    expected_index=71,
)
STARTWITH_MULTIPLE = dict(
    source=SOURCE_INTERCONNECTS_Q_STAR,
    substring='As I’ve',
    expected_index=40,
)
SUBSTRING_UNIQUE = dict(
    source=SOURCE_INTERCONNECTS_Q_STAR,
    substring='**ToT seems like the first “recursive” prompting technique for improving inference performance**',
    expeced_substring=81,
)
SUBSTRING_MULTIPLE = dict(
    source=SOURCE_INTERCONNECTS_Q_STAR,
    substring='can be',
    expeced_substring=84,
)


@pytest.mark.parametrize(
    ('source_string', 'substring', 'expected_index'),
    [
        EQUALS_UNIQUE.values(),
        EQUAL_MULTIPLE.values(),
        STARTWITH_UNIQUE.values(),
        STARTWITH_MULTIPLE.values(),
        SUBSTRING_UNIQUE.values(),
        SUBSTRING_MULTIPLE.values(),
    ],
)
def test_index_of(source_string, substring, expected_index):
    index = index_of(source_string.splitlines(), substring, case_sensitive=True)
    assert index == expected_index
    index = index_of(source_string.upper().splitlines(), substring.lower())
    assert index == expected_index


class test_line_numbers:
    MARKDOWN_WITHOUT_LINE_NUMBERS = textwrap.dedent(
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

    MARKDOWN_WITH_LINE_NUMBERS = (
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
    """,  # noqa: W291 Trailing whitespace
        )
        .removeprefix('\n')
        .removesuffix('\n')
    )

    def test_add_line_numbers_to_text_without_line_numbers(self):
        actual = add_line_numbers(self.MARKDOWN_WITHOUT_LINE_NUMBERS).removeprefix('\n').removesuffix('\n')
        assert actual == self.MARKDOWN_WITH_LINE_NUMBERS

    def test_add_line_numbers_to_text_already_with_line_numbers(self):
        unchanged_markdown = add_line_numbers(self.MARKDOWN_WITH_LINE_NUMBERS)
        assert unchanged_markdown == self.MARKDOWN_WITH_LINE_NUMBERS

    def test_remove_line_numbers_from_text_with_line_numbers(self):
        actual = remove_line_numbers(self.MARKDOWN_WITH_LINE_NUMBERS).removeprefix('\n').removesuffix('\n')
        assert actual == self.MARKDOWN_WITHOUT_LINE_NUMBERS

    def test_remove_line_numbers_from_text_without_line_numbers(self):
        unchanged_markdown = remove_line_numbers(self.MARKDOWN_WITHOUT_LINE_NUMBERS)
        assert unchanged_markdown == self.MARKDOWN_WITHOUT_LINE_NUMBERS
