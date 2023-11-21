from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from openai import OpenAI
from rich import get_console


def to_audio(speakable: str) -> bytes:
    console = get_console()
    chunk_size = 4000  # 4096 is the max, but we need to leave some space for the joined newlines
    article_chunks = [speakable[i : i + chunk_size] for i in range(0, len(speakable), chunk_size)]
    with console.status(
        f"Converting speakable to audio with alloy@tts-1...", spinner="aesthetic", refresh_per_second=10
    ) as live:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    chunk_to_audio, input=article_chunk, model="tts-1", voice="alloy", response_format="mp3"
                )
                for article_chunk in article_chunks
            ]
        audios = [future.result() for future in futures]

    audio = b"".join(audios)
    console.print("[b]🎵 Done generating audio!")
    return audio


def chunk_to_audio(
    input: str,
    model: Literal["tts-1", "tts-1-hd"] = "tts-1",
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy",
    response_format: Literal["mp3", "opus", "aac", "flac"] = "mp3",
) -> bytes:
    oai = OpenAI()
    return oai.audio.speech.create(input=input, model=model, voice=voice, response_format=response_format).content
