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


def has_line_numbers(markdown: str) -> bool:
    if not markdown:
        return False
    markdown_lines = markdown.splitlines()
    stripped_markdown_lines = [line.strip() for line in markdown_lines if line.strip()]
    if not stripped_markdown_lines:
        return False
    return f'0 {LINE_NUMBER_SEPARATOR}' in stripped_markdown_lines[0]


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


def index_of(string_lines: list[str], substring: str, *, case_sensitive=True) -> int | None:
    def _warn_ambiguity(collection, verb: str):
        indices = [_index for _index, _ in collection]
        console.warning(
            f'AmbiguousIndex: %d lines {verb} substring %r in indices %s. Returning first=%d',
            len(equal),
            substring,
            ', '.join(map(str, indices)),
            indices[0],
        )

    equal = []
    startwith = []
    contain = []
    for i, line in enumerate(string_lines):
        if line == substring:
            equal.append((i, line))
            continue
        if line.startswith(substring):
            startwith.append((i, line))
            continue
        if substring in line:
            contain.append((i, line))
            continue
    if equal:
        len(equal) > 1 and _warn_ambiguity(equal, 'equal to')
        index, line = equal[0]
        return index
    if startwith:
        len(startwith) > 1 and _warn_ambiguity(startwith, 'start with')
        index, line = startwith[0]
        return index
    if contain:
        len(contain) > 1 and _warn_ambiguity(contain, 'contain')
        index, line = contain[0]
        return index
    if case_sensitive:
        return index_of([line.casefold() for line in string_lines], substring.lower(), case_sensitive=False)
    return None
