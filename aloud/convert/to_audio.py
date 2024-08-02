from aloud import models
from aloud.console import console
from aloud.oai import oai
from aloud.thread_pool_executor import ThreadPoolExecutor


def to_audio(
    speakable: str,
    voice: models.VOICE = models.VOICE.default,
    voice_model: models.VoiceModel = models.VoiceModel.default,
    voice_response_format: models.VoiceResponseFormat = models.VoiceResponseFormat.default,
) -> bytes:
    chunk_size = 4000  # 4096 is the max, but we need to leave some space for the joined newlines
    article_chunks = [speakable[i : i + chunk_size] for i in range(0, len(speakable), chunk_size)]
    with console.status(f'Converting speakable to audio with {voice}@{voice_model}...'):
        with ThreadPoolExecutor() as executor:
            # noinspection PyTypeChecker
            futures = [
                executor.submit(chunk_to_audio, article_chunk, voice, voice_model, voice_response_format)
                for article_chunk in article_chunks
            ]
        audios = [future.result() for future in futures]

    audio = b''.join(audios)
    console.print('\n[b green]🎵 Done generating audio!')
    return audio


# noinspection PyShadowingBuiltins
def chunk_to_audio(
    input: str,
    voice: models.VOICE = models.VOICE.default,
    voice_model: models.VoiceModel = models.VoiceModel.default,
    voice_response_format: models.VoiceResponseFormat = models.VoiceResponseFormat.default,
) -> bytes:
    return oai.audio.speech.create(
        input=input,
        model=voice_model,
        voice=voice,
        response_format=voice_response_format,
    ).content
