import builtins

from aloud.console import console

LINE_NUMBER_SEPARATOR = '│'


def add_line_numbers(markdown: str) -> str:
    if has_line_numbers(markdown):
        return markdown
    markdown_lines = markdown.splitlines()
    digits = len(str(len(markdown_lines)))
    for i, line in enumerate(markdown_lines):
        line_number = str(i).rjust(digits)
        markdown_lines[i] = f'{line_number} {LINE_NUMBER_SEPARATOR} {line}'
    markdown = '\n'.join(markdown_lines)
    return markdown


def remove_line_numbers(markdown: str) -> str:
    if not has_line_numbers(markdown):
        return markdown
    markdown_lines = markdown.splitlines()
    for i, line in enumerate(markdown_lines):
        markdown_lines[i] = line.partition(f' {LINE_NUMBER_SEPARATOR} ')[2]
    markdown = '\n'.join(markdown_lines)
    return markdown


def remove_lines_until(markdown: str, line: str) -> str:
    markdown_lines = markdown.splitlines()
    line_index = index_of(markdown_lines, line)
    console.log(f'remove_lines_until => line (idx {line_index}):\n%r', line)
    clean_markdown = '\n'.join(markdown_lines[line_index:])
    return clean_markdown


def remove_lines_after(markdown: str, line: str) -> str:
    markdown_lines = markdown.splitlines()
    reversed_markdown_lines = list(reversed(markdown_lines))
    line_reverse_index = index_of(reversed_markdown_lines, line)
    console.log(f'remove_lines_after => line (idx -{line_reverse_index}):\n%r', line)
    if line_reverse_index == 0:
        return markdown
    clean_markdown = '\n'.join(markdown_lines[:-line_reverse_index])
    return clean_markdown


def index_of(string_lines: list[str], substring: str, *, case_sensitive=True) -> int:
    lines_equal_to_substring = [line for line in string_lines if line == substring]
    if lines_equal_to_substring:
        if len(lines_equal_to_substring) > 1:
            console.warning(
                '%d lines equal to substring %r' % (len(lines_equal_to_substring), substring),
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


def has_line_numbers(markdown: str) -> bool:
    if not markdown:
        return False
    markdown_lines = markdown.splitlines()
    stripped_markdown_lines = [line.strip() for line in markdown_lines if line.strip()]
    if not stripped_markdown_lines:
        return False
    return f'0 {LINE_NUMBER_SEPARATOR}' in stripped_markdown_lines[0]
