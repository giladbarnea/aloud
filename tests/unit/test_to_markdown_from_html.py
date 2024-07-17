from aloud.convert.to_markdown.from_html import convert_to_raw_markdown


def test_trims_multiple_spaces_to_single_space():
    markdown = convert_to_raw_markdown('<p>hello    world</p>')
    assert markdown == 'hello world'
    markdown = convert_to_raw_markdown('<p>hello  world</p>')
    assert markdown == 'hello world'
