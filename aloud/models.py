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


def random_voice(ctx, param, value):
    if value == 'random':
        return random.choice(voices)
    return value


voices = ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
default_voice = 'random'
Voice = Literal[voices]
Voice.default = default_voice
VoiceOption = Annotated[
    str,
    typer.Option(
        '-v', '--voice', show_default=True, click_type=click.Choice((*voices, 'random')), callback=random_voice
    ),
    default_voice,
]

voice_models = ('tts-1', 'tts-1-hd')
default_voice_model = 'tts-1'
VoiceModel = Literal[voice_models]
VoiceModel.default = default_voice_model
VoiceModelOption = Annotated[
    str,
    typer.Option('--voice-voice_model', show_default=True, click_type=click.Choice(voice_models)),
    default_voice_model,
]

voice_response_formats = ('mp3', 'opus', 'aac', 'flac')
default_voice_response_format = 'mp3'
VoiceResponseFormat = Literal[voice_response_formats]
VoiceResponseFormat.default = default_voice_response_format
VoiceResponseFormatOption = Annotated[
    str,
    typer.Option('--voice-response-format', show_default=True, click_type=click.Choice(voice_response_formats)),
    default_voice_response_format,
]

OpenAIKey = Annotated[
    str, typer.Option('-k', '--openai-api-key', callback=cli_utils.get_openai_api_key, envvar='OPENAI_API_KEY')
]

default_output_dir = '/tmp'
OutputDir = Annotated[Path, typer.Option('-o', '--output-dir'), default_output_dir]
