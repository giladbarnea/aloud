from pathlib import Path

import click
import elevenlabs as xi
import load


@click.command()
@click.argument("thing")
def main(thing):
    xi.set_api_key(Path("~/.elevenlabs-token").expanduser().read_text().strip())
    text = load.load(thing)
    # audio = xi.generate(text="Hi! My name is Bella, nice to meet you!", voice="Bella", model="eleven_monolingual_v1")

    # xi.play(audio)


if __name__ == "__main__":
    main()
