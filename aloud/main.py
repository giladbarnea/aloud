import os
import tempfile
from pathlib import Path

import click
from plum import dispatch
from rich import get_console

from aloud import convert

console = get_console()


@click.command()
@click.argument("thing")
@click.option("-o", "--output", "output_dir", type=click.Path(dir_okay=True, file_okay=False), required=False)
@click.option("--only-speakable", "only_speakable", is_flag=True, default=False)
@click.option("--only-audio", "only_audio", is_flag=True, default=False)
@click.option("-k", "--api-key", "openai_api_key", envvar="OPENAI_API_KEY", required=False)
def main(thing, output_dir: str, only_speakable, only_audio, openai_api_key):
    openai_api_key = openai_api_key or get_openai_api_key()
    assert_args_ok(only_audio, only_speakable, output_dir)
    output_dir = prepare_output_dir(output_dir)
    if only_audio:
        return process_audio(output_dir)
    if only_speakable:
        return "".join(convert.to_speakable(thing, output_dir))
    speakable: str = "".join(convert.to_speakable(thing, output_dir))
    return process_audio(speakable, output_dir)


@dispatch
def process_audio(output_dir: Path) -> bytes:
    speakable_path = Path(output_dir) / "speakable.txt"
    if not speakable_path.exists():
        raise FileNotFoundError(f"{speakable_path} does not exist, can't convert to audio")
    speakable: str = speakable_path.read_text()
    console.print("\n[b green]Fetched speakable from", output_dir)
    return process_audio(speakable, output_dir)


@dispatch
def process_audio(speakable: str, output_dir: Path) -> bytes:
    audio = convert.to_audio(speakable)
    output_audio_file = Path(output_dir) / "speakable.mp3"
    with output_audio_file.open("wb") as audio_path:
        audio_path.write(audio)
    console.print("\n[b green]Wrote audio to", audio_path.name)
    click.confirm("Play audio?") and click.launch(audio_path.name)
    return audio


def assert_args_ok(only_audio, only_speakable, output_dir):
    if only_audio and not output_dir:
        raise click.BadParameter(
            "Must specify --output when using --only-audio, because speakable.txt must already exist"
        )
    if only_audio and only_speakable:
        raise click.BadParameter("Cannot specify both --only-audio and --only-speakable")


def prepare_output_dir(output_dir: str | Path) -> Path:
    if not output_dir:
        output_dir = tempfile.mkdtemp()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_openai_api_key():
    api_key_file_path = Path.home() / ".openai-api-token-pecan"
    if not api_key_file_path.exists():
        api_key_file_path = Path.home() / ".openai-api-token"
    if not api_key_file_path.exists():
        raise click.BadParameter(
            "Must specify --openai-api-key, or set OPENAI_API_KEY environment variable, or have a file at"
            " ~/.openai-api-token"
        )
    openai_api_key = api_key_file_path.read_text().strip()
    os.environ["OPENAI_API_KEY"] = openai_api_key
    return openai_api_key


if __name__ == "__main__":
    main()
