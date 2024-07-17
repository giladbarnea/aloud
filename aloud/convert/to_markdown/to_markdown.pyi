import typing
from pathlib import Path

class to_markdown(typing.Protocol):
    def __new__(
        cls,
        html: str,
        *,
        output_dir: Path | None = None,
        converts_to_raw_markdown=...,
        finds_real_article_boundaries=...,
        trims_junk_sections=...,
        injects_image_descriptions_as_alt=...,
    ) -> str: ...
