import pickle
from pathlib import Path

import click
import convert
import elevenlabs as xi


@click.command()
@click.argument("thing")
def main(thing):
    audio = get_audio(thing)
    with open("how_to_prepare_a_talk.wav", "wb") as f:
        pickle.dump(audio, f)

    xi.play(audio)


def get_audio(thing):
    xi.set_api_key(Path("~/.elevenlabs-token").expanduser().read_text().strip())
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
