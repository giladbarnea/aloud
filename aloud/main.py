import pickle
import tempfile
from pathlib import Path

import click
from aloud import convert


@click.command()
@click.argument("thing")
def main(thing):
    speakable = convert.to_speakable(thing)
    with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as tmp_speakable:
        tmp_speakable.write(speakable)
    print('Wrote speakable to', tmp_speakable.name)
    audio = convert.to_audio(speakable)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
        tmp_audio.write(audio)
    click.launch(tmp_audio.name)


def get_audio(thing):
    text = convert.to_speakable(thing)
    audio = xi.generate(
        text=text,
        voice=xi.Voice(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            name="Rachel",
            category="premade",
            settings=xi.VoiceSettings(stability=0.60, similarity_boost=0.75),
        ),
        model="eleven_monolingual_v1",
    )
    return audio


if __name__ == "__main__":
    main()
