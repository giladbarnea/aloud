from __future__ import annotations

import random
from pathlib import Path
from typing import Annotated as _Annotated
from typing import Literal

import click
import typer

from aloud import cli_utils

del _Annotated.__init_subclass__
Undefined = object()


class Annotated(_Annotated):
    def __class_getitem__(cls, params: tuple):
        default = Undefined
        if len(params) == 3:
            *params, default = params
        # noinspection PyUnresolvedReferences
        inst = super().__class_getitem__(tuple(params))
        inst.__dict__['default'] = default
        return inst


def random_voice(ctx, param, value):  # noqa: ARG001
    if value == 'random':
        return random.choice(VOICES)
    return value


VOICES = ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
DEFAULT_VOICE = 'random'
VOICE = Literal[VOICES]
VOICE.default = DEFAULT_VOICE
VoiceOption = Annotated[
    str,
    typer.Option(
        '-v',
        '--voice',
        show_default=True,
        click_type=click.Choice((*VOICES, 'random')),
        callback=random_voice,
    ),
    DEFAULT_VOICE,
]

VOICE_MODELS = ('tts-1', 'tts-1-hd')
DEFAULT_VOICE_MODEL = 'tts-1'
VoiceModel = Literal[VOICE_MODELS]
VoiceModel.default = DEFAULT_VOICE_MODEL
VoiceModelOption = Annotated[
    str,
    typer.Option('--voice-model', click_type=click.Choice(VOICE_MODELS)),
    DEFAULT_VOICE_MODEL,
]

CHAT_MODELS = ('gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo')
DEFAULT_CHAT_MODEL = 'gpt-4-turbo'
ChatModel = Literal[CHAT_MODELS]
ChatModel.default = DEFAULT_CHAT_MODEL
ChatModelOption = Annotated[
    str,
    typer.Option('--model', click_type=click.Choice(CHAT_MODELS)),
    DEFAULT_CHAT_MODEL,
]

VOICE_RESPONSE_FORMATS = ('mp3', 'opus', 'aac', 'flac')
DEFAULT_VOICE_RESPONSE_FORMAT = 'mp3'
VoiceResponseFormat = Literal[VOICE_RESPONSE_FORMATS]
VoiceResponseFormat.default = DEFAULT_VOICE_RESPONSE_FORMAT
VoiceResponseFormatOption = Annotated[
    str,
    typer.Option('--voice-response-format', click_type=click.Choice(VOICE_RESPONSE_FORMATS)),
    DEFAULT_VOICE_RESPONSE_FORMAT,
]

OpenAIKeyOption = Annotated[
    str,
    typer.Option('-k', '--openai-api-key', callback=cli_utils.get_openai_api_key, envvar='OPENAI_API_KEY'),
]

DEFAULT_OUTPUT_DIR = Path('/tmp')
OutputDir = Annotated[Path, typer.Option('-o', '--output-dir'), DEFAULT_OUTPUT_DIR]
