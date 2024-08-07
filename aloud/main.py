from pathlib import Path

import typer
from plum import dispatch

from aloud import convert, models
from aloud.cli_utils import assert_args_ok, prepare_output_dir
from aloud.console import console


def process(
    thing: str,
    only_speakable: bool = False,  # noqa: FBT001,FBT002 Boolean positional
    only_audio: bool = False,  # noqa: FBT001,FBT002 Boolean positional
    chat_model: models.ChatModelOption = models.ChatModelOption.default,
    voice: models.VoiceOption = models.VoiceOption.default,
    voice_model: models.VoiceModelOption = models.VoiceModelOption.default,
    voice_response_format: models.VoiceResponseFormatOption = models.VoiceResponseFormatOption.default,
    output_dir: models.OutputDir = models.OutputDir.default,
    openai_api_key: models.OpenAIKeyOption | None = None,  # noqa: ARG001 Unused argument
) -> bytes:
    assert_args_ok(only_audio, only_speakable, output_dir)
    output_dir = prepare_output_dir(thing, output_dir)
    if only_speakable:
        return ''.join(convert.to_speakable(thing, output_dir, chat_model)).encode()
    if only_audio:
        return process_audio(voice, voice_model, voice_response_format, output_dir)
    speakable: str = ''.join(convert.to_speakable(thing, output_dir, chat_model))
    return process_audio(speakable, voice, voice_model, voice_response_format, output_dir)


@dispatch
def process_audio(voice, voice_model, voice_response_format, output_dir: Path) -> bytes:
    speakable_path = output_dir / f'{output_dir.name}.txt'
    if not speakable_path.exists():
        raise FileNotFoundError(f"{speakable_path} does not exist, can't convert to audio")
    speakable: str = speakable_path.read_text()
    console.print('\n[b green]Fetched speakable from', output_dir)
    return process_audio(speakable, voice, voice_model, voice_response_format, output_dir)


@dispatch
def process_audio(speakable: str | bytes, voice, voice_model, voice_response_format, output_dir: Path) -> bytes:
    speakable = speakable.decode() if isinstance(speakable, bytes) else speakable
    audio = convert.to_audio(
        speakable,
        voice=voice,
        voice_model=voice_model,
        voice_response_format=voice_response_format,
    )
    output_audio_file = output_dir / f'{output_dir.name}.mp3'
    with output_audio_file.open('wb') as audio_path:
        audio_path.write(audio)
    console.print('\n[b green]Wrote audio to', audio_path.name)
    typer.confirm('Play audio?') and typer.launch(audio_path.name)
    return audio


def main():
    typer.run(process)


if __name__ == '__main__':
    main()
