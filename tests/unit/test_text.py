import textwrap

from aloud.text import add_line_numbers, remove_line_numbers


class TestLineNumbers:
    markdown_without_line_numbers = textwrap.dedent(
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

    markdown_with_line_numbers = (
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

    def test_add_line_numbers_to_text_without_line_numbers(self):
        actual = add_line_numbers(self.markdown_without_line_numbers).removeprefix('\n').removesuffix('\n')
        assert actual == self.markdown_with_line_numbers

    def test_add_line_numbers_to_text_already_with_line_numbers(self):
        unchanged_markdown = add_line_numbers(self.markdown_with_line_numbers)
        assert unchanged_markdown == self.markdown_with_line_numbers

    def test_remove_line_numbers_from_text_with_line_numbers(self):
        actual = remove_line_numbers(self.markdown_with_line_numbers).removeprefix('\n').removesuffix('\n')
        assert actual == self.markdown_without_line_numbers

    def test_remove_line_numbers_from_text_without_line_numbers(self):
        unchanged_markdown = remove_line_numbers(self.markdown_without_line_numbers)
        assert unchanged_markdown == self.markdown_without_line_numbers
