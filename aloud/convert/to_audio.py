from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from rich import get_console


def to_audio(speakable: str) -> bytes:
    console = get_console()
    chunk_size = 4000  # 4096 is the max, but we need to leave some space for the joined newlines
    article_chunks = [speakable[i : i + chunk_size] for i in range(0, len(speakable), chunk_size)]
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
    console.print("[b]🎵 Done generating audio!")
    return audio
