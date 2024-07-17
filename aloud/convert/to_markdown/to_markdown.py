from pathlib import Path

from aloud.console import console
from aloud.text import has_line_numbers
from aloud.vision import inject_image_descriptions_as_alt

from .article_trimming import find_real_article_boundaries, trim_junk_sections
from .from_html import convert_to_raw_markdown


@console.with_status('Converting to markdown...')
def to_markdown(
    html: str,
    *,
    output_dir: Path | None = None,
    converts_to_raw_markdown=convert_to_raw_markdown,
    finds_real_article_boundaries=find_real_article_boundaries,
    trims_junk_sections=trim_junk_sections,
    injects_image_descriptions_as_alt=inject_image_descriptions_as_alt,
) -> str:
    raw_markdown = converts_to_raw_markdown(html)
    first_real_article_line, first_post_title_line, last_real_article_line = finds_real_article_boundaries(raw_markdown)
    clean_markdown = trims_junk_sections(
        raw_markdown,
        first_real_article_line,
        first_post_title_line,
        last_real_article_line,
    )
    if output_dir:
        markdown_path = output_dir / f'{output_dir.name}.md'
        markdown_path.write_text(clean_markdown)
        console.print('\n[b green]Wrote markdown to', markdown_path.name)
    enriched_markdown = injects_image_descriptions_as_alt(clean_markdown)
    assert not has_line_numbers(enriched_markdown)
    return enriched_markdown
