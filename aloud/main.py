import tempfile
from pathlib import Path

import click
from rich import get_console

from aloud import convert


@click.command()
@click.argument("thing")
@click.option("-o", "--output", "output_dir", type=click.Path(exists=True, file_okay=False), required=False)
@click.option("--only-speakable", "only_speakable", is_flag=True, default=False)
@click.option("--only-audio", "only_audio", is_flag=True, default=False)
def main(thing, output_dir=None, only_speakable=False, only_audio=False):
    console = get_console()
    if only_audio and not output_dir:
        raise click.BadParameter(
            "Must specify --output when using --only-audio, because speakable.txt must already exist"
        )
    if only_audio and only_speakable:
        raise click.BadParameter("Cannot specify both --only-audio and --only-speakable")
    if only_audio:
        speakable = (Path(output_dir) / "speakable.txt").read_text()
        console.print("\n[b]Fetched speakable from", output_dir)
    else:
        speakable = convert.to_speakable(thing)
        if not output_dir:
            output_dir = tempfile.mkdtemp()
        output_text_file = Path(output_dir) / "speakable.txt"
        with output_text_file.open("w") as speakable_path:
            speakable_path.write(speakable)
        console.print("\n[b]Wrote speakable to", speakable_path.name)
    if only_speakable:
        return
    audio = convert.to_audio(speakable)
    output_audio_file = Path(output_dir) / "speakable.mp3"
    with output_audio_file.open("wb") as audio_path:
        audio_path.write(audio)
    click.confirm("Play audio?") and click.launch(audio_path.name)


if __name__ == "__main__":
    main()
