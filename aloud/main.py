import os
import tempfile
from pathlib import Path
from typing import Annotated

import typer
from plum import dispatch
from rich import get_console

from aloud import convert

console = get_console()


def set_env(envvar: str):
    def decorator(func):
        def wrapper(value: str):
            return_value = func(value)
            os.environ[envvar] = return_value
            return return_value

        return wrapper

    return decorator


@set_env("OPENAI_API_KEY")
def get_openai_api_key(value):
    if is_file(value):
        return Path(value).expanduser().read_text().strip()
    if value:
        return value
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")
    api_key_dotfile_names = [".openai-api-token-pecan", ".openai-api-token"]
    for api_key_dotfile_name in api_key_dotfile_names:
        api_key_file_path = Path.home() / api_key_dotfile_name
        if api_key_file_path.exists():
            return api_key_file_path.read_text().strip()
    raise typer.BadParameter(
        "Must specify --openai-api-key, or set OPENAI_API_KEY environment variable, or have a file at"
        " ~/.openai-api-token"
    )


def is_file(value: str | Path) -> bool:
    try:
        return Path(value).expanduser().is_file()
    except OSError:
        return False


def prepare_output_dir(output_dir: str | Path) -> Path:
    if not output_dir:
        output_dir = tempfile.mkdtemp()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def process(
    thing,
    only_speakable: bool = False,
    only_audio: bool = False,
    openai_api_key: Annotated[
        str, typer.Option("-k", "--openai-api-key", callback=get_openai_api_key, envvar="OPENAI_API_KEY")
    ] = None,
    output_dir: Annotated[Path, typer.Option("-o", "--output-dir", callback=prepare_output_dir)] = None,
):
    assert_args_ok(only_audio, only_speakable, output_dir)
    output_dir = prepare_output_dir(output_dir)
    if only_audio:
        return process_audio(output_dir)
    if only_speakable:
        return "".join(convert.to_speakable(thing, output_dir))
    speakable: str = "".join(convert.to_speakable(thing, output_dir))
    return process_audio(speakable, output_dir)


def assert_args_ok(only_audio: bool, only_speakable: bool, output_dir: str | Path = None):
    if only_audio and not output_dir:
        raise typer.BadParameter("Must specify --output-dir when using --only-audio")
    if only_audio and only_speakable:
        raise typer.BadParameter("Cannot specify both --only-audio and --only-speakable")


@dispatch
def process_audio(output_dir: Path) -> bytes:
    speakable_path = output_dir / f"{output_dir.name}.txt"
    if not speakable_path.exists():
        raise FileNotFoundError(f"{speakable_path} does not exist, can't convert to audio")
    speakable: str = speakable_path.read_text()
    console.print("\n[b green]Fetched speakable from", output_dir)
    return process_audio(speakable, output_dir)


@dispatch
def process_audio(speakable: str, output_dir: Path) -> bytes:
    audio = convert.to_audio(speakable)
    output_audio_file = output_dir / f"{output_dir.name}.mp3"
    with output_audio_file.open("wb") as audio_path:
        audio_path.write(audio)
    console.print("\n[b green]Wrote audio to", audio_path.name)
    typer.confirm("Play audio?") and typer.launch(audio_path.name)
    return audio


def main():
    typer.run(process)


if __name__ == "__main__":
    main()
