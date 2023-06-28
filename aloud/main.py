from pathlib import Path

from elevenlabs import generate, play, set_api_key

set_api_key(Path("~/.elevenlabs-token").expanduser().read_text().strip())

audio = generate(text="Hi! My name is Bella, nice to meet you!", voice="Bella", model="eleven_monolingual_v1")

play(audio)
