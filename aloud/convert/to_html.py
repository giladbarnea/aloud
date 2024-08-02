from pathlib import Path

import requests
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from aloud import util
from aloud.console import console


@console.with_status('Fetching HTML of article...')
def to_html(url: str, *, remove_head: bool = False, output_dir: Path | None = None) -> str:
    if not util.is_url(url):
        return url
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if not response.ok:
        response.raise_for_status()
    html = response.text
    textual_soup = BeautifulSoup(html, 'html.parser')
    original_soup = BeautifulSoup(html, 'html.parser')
    remove_head and textual_soup.select_one('head').decompose()
    _remove_useless_elements_inplace(textual_soup)
    _flatten_nested_elements(textual_soup)
    _remove_comments(textual_soup)
    links = _pluck_links(textual_soup, url)
    # _remove_attributes_from_images(textual_soup)
    images, videos, audios = _pluck_media(textual_soup)
    code_blocks = _pluck_code_blocks(textual_soup)
    _remove_empty_and_low_word_count_elements(textual_soup)
    textual_html = textual_soup.prettify()
    textual_html =_sanitize_html(textual_html)
    if output_dir:
        html_path = output_dir / f'{output_dir.name}.html'
        html_path.write_text(textual_html)
        console.print('\n[b green]Wrote HTML to', html_path.name)
    return textual_html


def _pluck_links(soup: BeautifulSoup, url) -> dict[str, list[Tag]]:
    links = {'internal': [], 'external': []}
    body = soup.body

    # Extract and remove from soup all internal and external links
    for a in body.find_all('a', href=True):
        href = a['href']
        url_base = url.split('/')[2]
        if href.startswith('http') and url_base not in href:
            links['external'].append(a)
        else:
            links['internal'].append(a)
        a.decompose()
    return links


def _remove_useless_elements_inplace(
    soup: BeautifulSoup,
    useless_tags=('script', 'style', 'link', 'meta', 'noscript'),
) -> None:
    # Remove script, style, and other tags that don't carry useful content from body
    for tag in soup.body.find_all(useless_tags):
        tag.decompose()


def _remove_attributes_from_images(soup: BeautifulSoup) -> None:
    # Remove all attributes from remaining tags in body, except for img tags
    for tag in soup.body.find_all():
        if tag.name != 'img':
            tag.attrs = {}


def _pluck_media(soup: BeautifulSoup) -> tuple[list[Tag], list[Tag], list[Tag]]:
    images = []
    videos = []
    audios = []

    # Extract all images
    for img in soup.find_all('img'):
        images.append(img)
        img.decompose()

    # Extract all videos
    for video in soup.find_all('video'):
        videos.append(video)
        video.decompose()

    # Extract all audio
    for audio in soup.find_all('audio'):
        audios.append(audio)
        audio.decompose()

    return images, videos, audios


def _pluck_code_blocks(soup: BeautifulSoup):
    code_blocks = []

    # Extract all code blocks
    for pre in soup.find_all('pre'):
        code_blocks.append({'text': pre.get_text(), 'type': 'code'})
        pre.decompose()

    return code_blocks


def _remove_empty_and_low_word_count_elements(soup: BeautifulSoup, *, word_count_threshold=1) -> None:
    for tag in soup.find_all():
        if _is_empty_element(tag):
            tag.decompose()
            continue
        text = tag.get_text(strip=True).strip()
        if not text:
            tag.decompose()
            continue
        words = list(map(str.strip, text.split()))
        if not words:
            tag.decompose()
            continue
        if len(words) < word_count_threshold:
            tag.decompose()


def _is_empty_element(tag: Tag) -> bool:
    is_empty_element = getattr(tag, 'is_empty_element', False)
    if isinstance(tag, NavigableString):
        no_text: bool = not tag.strip()
        assert is_empty_element == no_text, f'tag.is_empty_element={is_empty_element} != no_text={no_text}: {tag!r}'
        return no_text
    assert not hasattr(
        tag,
        'strip',
    ), f'Assumed only NavigableString can .strip(), but discovered that the following tag also has .strip(): {tag!r}'
    if not tag.contents:
        assert is_empty_element, f'tag.is_empty_element={is_empty_element} but tag has no children: {tag!r}'
        return True
    return all(_is_empty_element(child) for child in tag.children)


def _flatten_nested_elements(soup: BeautifulSoup) -> None:
    """Flatten nested elements with only one child of the same type."""
    for tag in soup.find_all():
        if len(tag.contents) == 1 and tag.contents[0].name == tag.name:
            tag.replace_with(tag.contents[0])


def _remove_comments(soup: BeautifulSoup) -> None:
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()


def _sanitize_html(html: str) -> str:
    sanitized = html
    while '\n\n' in sanitized:
        sanitized = sanitized.replace('\n\n', '\n')
    while '  ' in sanitized:
        sanitized = sanitized.replace('  ', ' ')
    return sanitized.replace('"', '\\"').replace("'", "\\'")
