import textwrap
from pathlib import Path

import pytest

from aloud.cli_utils import prepare_output_dir
from aloud.console import console
from aloud.convert import to_markdown
from aloud.convert.to_markdown import (
    add_line_numbers,
    convert_to_raw_markdown,
    extract_image_link,
    extract_image_links,
    get_image_link_indices,
generate_image_description,
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

def test_generate_image_description():
    image_url = "https://substack-post-media.s3.amazonaws.com/public/images/98f562a1-ece9-4e31-bafd-363da13fa741_667x571.png"
    image_description = generate_image_description(image_url)
    console.print(image_description)


def test_extract_image_links():
    thing = 'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
    html = Path(thing).read_text()
    temp_dir = prepare_output_dir(thing, '/tmp')
    raw_markdown = convert_to_raw_markdown(html)
    (temp_dir / 'raw_markdown.md').write_text(raw_markdown)
    markdown_with_line_numbers = add_line_numbers(raw_markdown)
    (temp_dir / 'markdown_with_line_numbers.md').write_text(markdown_with_line_numbers)
    image_links = extract_image_links(markdown_with_line_numbers)
    console.log('image_links:', image_links)
    expected = [
        'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/cd2ee4f7-3e71-42f0-92eb-4d3018127e08_1024x1024.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/26d66498-9805-4dab-8533-0266de299d9c_1024x1024.jpeg',
        'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/26d66498-9805-4dab-8533-0266de299d9c_1024x1024.jpeg',
        'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/788606a4-68fc-461a-949e-bf7eaa500d16_1230x720.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/98f562a1-ece9-4e31-bafd-363da13fa741_667x571.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/095153ca-5250-44d9-9d6e-92eb73c41e42_1668x520.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/28c82a0a-5281-4a8b-a96a-c160a01b866c_1710x495.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/ef0842ea-6a2c-412b-bf3c-e0a46433eb5b_818x1079.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/3e476d8c-2098-45c9-bded-e47c3342fa33_1844x2210.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/99263512-f895-4704-ad38-dc53b80cfb86_1686x567.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        'https://substack.com/img/avatars/logged-out.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        'https://substack-post-media.s3.amazonaws.com/public/images/d1f7fbb8-8d17-445f-b1c5-019ae6d8178f_1566x1852.jpeg',
        'https://substack-post-media.s3.amazonaws.com/public/images/4e5613be-ef51-4a07-8f2f-d745424d17f7_764x767.png',
    ]
    assert image_links == expected


def test_get_image_link_indices():
    thing = 'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
    html = Path(thing).read_text()
    temp_dir = prepare_output_dir(thing, '/tmp')
    raw_markdown = convert_to_raw_markdown(html)
    (temp_dir / 'raw_markdown.md').write_text(raw_markdown)
    markdown_with_line_numbers = add_line_numbers(raw_markdown)
    (temp_dir / 'markdown_with_line_numbers.md').write_text(markdown_with_line_numbers)
    image_links_indices = get_image_link_indices(markdown_with_line_numbers)
    console.log('image_links_indices:', image_links_indices)
    expected = [
        0,
        10,
        26,
        44,
        54,
        80,
        98,
        102,
        108,
        112,
        116,
        122,
        138,
        148,
        172,
        176,
        194,
        214,
    ]
    assert image_links_indices == expected


@pytest.mark.parametrize(
    'line,link',
    [
        (
            "  0 │ [ <img src='https://substackcdn.com/image/fetch/w_96,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2Fcd2ee4f7-3e71-42f0-92eb-4d3018127e08_1024x1024.png' /> ](</>)",
            'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/cd2ee4f7-3e71-42f0-92eb-4d3018127e08_1024x1024.png',
        ),
        (
            "10 │ <img src='https://substackcdn.com/image/fetch/w_120,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png' width='120' />",
            'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        ),
        (
            "26 │ <img src='https://substackcdn.com/image/fetch/w_128,h_128,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F26d66498-9805-4dab-8533-0266de299d9c_1024x1024.jpeg' width='128' height='128' /> <img src='https://substackcdn.com/image/fetch/w_48,h_48,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2Fcd2ee4f7-3e71-42f0-92eb-4d3018127e08_1024x1024.png' width='48' height='48' />",
            'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/26d66498-9805-4dab-8533-0266de299d9c_1024x1024.jpeg',
        ),
        (
            "44 │ [ <img src='https://substackcdn.com/image/fetch/w_80,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F26d66498-9805-4dab-8533-0266de299d9c_1024x1024.jpeg' width='80' /> ](<https://substack.com/profile/846835-ethan-mollick>)",
            'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/26d66498-9805-4dab-8533-0266de299d9c_1024x1024.jpeg',
        ),
        (
            "54 │ <img src='https://substackcdn.com/image/fetch/w_120,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png' width='120' />",
            'https://substack-post-media.s3.amazonaws.com/public/images/17f96f1e-dc62-428b-8d86-09d15d3ea309_1376x864.png',
        ),
        (
            "80 │ [ <img src='https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F788606a4-68fc-461a-949e-bf7eaa500d16_1230x720.png' width='1230' height='720' /> ](<https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F788606a4-68fc-461a-949e-bf7eaa500d16_1230x720.png>)",
            'https://substack-post-media.s3.amazonaws.com/public/images/788606a4-68fc-461a-949e-bf7eaa500d16_1230x720.png',
        ),
        (
            " 98 │ [ <img src='https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F98f562a1-ece9-4e31-bafd-363da13fa741_667x571.png' width='361' height='309.04197901049474' /> ](<https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F98f562a1-ece9-4e31-bafd-363da13fa741_667x571.png>)",
            'https://substack-post-media.s3.amazonaws.com/public/images/98f562a1-ece9-4e31-bafd-363da13fa741_667x571.png',
        ),
        (
            "102 │ [ <img src='https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F095153ca-5250-44d9-9d6e-92eb73c41e42_1668x520.png' width='1456' height='454' /> ](<https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F095153ca-5250-44d9-9d6e-92eb73c41e42_1668x520.png>)",
            'https://substack-post-media.s3.amazonaws.com/public/images/095153ca-5250-44d9-9d6e-92eb73c41e42_1668x520.png',
        ),
    ],
)
def test_extract_image_link(line, link):
    actual_link = extract_image_link(line)
    assert actual_link == link


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
