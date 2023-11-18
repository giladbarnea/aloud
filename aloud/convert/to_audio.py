from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI
from rich import get_console


def to_audio(speakable: str) -> bytes:
    console = get_console()
    chunk_size = 4096
    article_chunks = [
        "\n".join(filter(bool, speakable[i : i + chunk_size].splitlines()))
        for i in range(0, len(speakable), chunk_size)
    ]
    for i, article_chunk in enumerate(article_chunks[:-1]):
        chunk_lines = article_chunk.splitlines()
        last_chunk_line = chunk_lines[-1]
        article_chunks[i] = "\n".join(chunk_lines[:-1])
        article_chunks[i + 1] = last_chunk_line + article_chunks[i + 1]
    oai = OpenAI()
    with console.status(
        f"Converting speakable to audio with alloy@tts-1...", spinner="aesthetic", refresh_per_second=100
    ) as live:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    oai.audio.speech.create, input=article_chunk, model="tts-1", voice="alloy", response_format="mp3"
                )
                for article_chunk in article_chunks
            ]
        audios = [future.result() for future in futures]

    audio = b"".join(audio.content for audio in audios)
    print("🎵 Done generating audio!")
    return audio
