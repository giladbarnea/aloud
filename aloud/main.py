import os
import tempfile
from pathlib import Path

import click
from rich import get_console

from aloud import convert
from threading import Thread
from concurrent.futures import Future


@click.command()
@click.argument("thing")
@click.option("-o", "--output", "output_dir", type=click.Path(dir_okay=True, file_okay=False), required=False)
@click.option("--only-speakable", "only_speakable", is_flag=True, default=False)
@click.option("--only-audio", "only_audio", is_flag=True, default=False)
@click.option("-k", "--api-key", "openai_api_key", envvar="OPENAI_API_KEY", required=False)
def main(thing, output_dir: str, only_speakable, only_audio, openai_api_key):
    console = get_console()
    if not openai_api_key:
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
    if not output_dir:
        output_dir = tempfile.mkdtemp()
    output_dir = Path(output_dir)
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True)
    if only_audio and not output_dir:
        raise click.BadParameter(
            "Must specify --output when using --only-audio, because speakable.txt must already exist"
        )
    if only_audio and only_speakable:
        raise click.BadParameter("Cannot specify both --only-audio and --only-speakable")
    if only_audio:
        speakable_path = Path(output_dir) / "speakable.txt"
        if not speakable_path.exists():
            raise click.BadParameter(f"--only-audio was specified, but file {speakable_path} does not exist")
        speakable: str = speakable_path.read_text()
        console.print("\n[b]Fetched speakable from", output_dir)
        audio = convert.to_audio(speakable)
        output_audio_file = Path(output_dir) / "speakable.mp3"
        with output_audio_file.open("wb") as audio_path:
            audio_path.write(audio)
        click.confirm("Play audio?") and click.launch(audio_path.name)
    else:
        if only_speakable:
            speakable: str = "".join(convert.to_speakable(thing, output_dir))
            audio = convert.to_audio(speakable)
            output_audio_file = Path(output_dir) / "speakable.mp3"
            with output_audio_file.open("wb") as audio_path:
                audio_path.write(audio)
            click.confirm("Play audio?") and click.launch(audio_path.name)
        else:
            audios = []
            speakable_chunks = []
            audio_chunk_futures = []
            speakable_current_chunk = ""
            for speakable_delta in convert.to_speakable(thing, output_dir):
                speakable_current_chunk += speakable_delta
                if len(speakable_current_chunk) > 4000:
                    speakable_chunks.append(speakable_current_chunk)
                    future = Future()
                    convert_to_audio_and_set_result = lambda curr_chunk=speakable_current_chunk: future.set_result(
                        convert.chunk_to_audio(curr_chunk)
                    )
                    thread = Thread(target=convert_to_audio_and_set_result)
                    thread.start()
                    audio_chunk_futures.append(future)
                    speakable_current_chunk = ""
            if speakable_current_chunk:
                speakable_chunks.append(speakable_current_chunk)
                future = Future()
                convert_to_audio_and_set_result = lambda curr_chunk=speakable_current_chunk: future.set_result(
                    convert.chunk_to_audio(curr_chunk)
                )
                thread = Thread(target=convert_to_audio_and_set_result)
                thread.start()
                audio_chunk_futures.append(future)
            speakable = "".join(speakable_chunks)
            output_text_file = Path(output_dir) / "speakable.txt"
            with output_text_file.open("w") as speakable_path:
                speakable_path.write(speakable)
            console.print("\n[b]Wrote speakable to", speakable_path.name)
            with console.status(
                f"Converting speakable to audio with alloy@tts-1...", spinner="aesthetic", refresh_per_second=10
            ) as live:
                for audio_chunk_future in audio_chunk_futures:
                    audios.append(audio_chunk_future.result())
            audio = b"".join(audios)
            console.print("[b]🎵 Done generating audio!")
            output_audio_file = Path(output_dir) / "speakable.mp3"
            with output_audio_file.open("wb") as audio_path:
                audio_path.write(audio)
            click.confirm("Play audio?") and click.launch(audio_path.name)


if __name__ == "__main__":
    main()
