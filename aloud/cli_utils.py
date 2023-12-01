import os
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, TypeVar

import typer

from aloud import util

CliArgValue = ParamSpec('CliArgValue')
StringReturnValue = TypeVar('StringReturnValue', bound=str)
CliArgCallback = Callable[CliArgValue, StringReturnValue]


def set_env(envvar: str) -> Callable[[CliArgCallback], CliArgCallback]:
    def decorator(cli_arg_callback: CliArgCallback) -> CliArgCallback:
        def wrapper(value: CliArgValue) -> StringReturnValue:
            return_value: StringReturnValue = cli_arg_callback(value)
            os.environ[envvar] = return_value
            return return_value

        return wrapper

    return decorator


@set_env('OPENAI_API_KEY')
def get_openai_api_key(value):
    if value and util.is_file(value):
        return Path(value).expanduser().read_text().strip()
    if value:
        return value
    if os.getenv('OPENAI_API_KEY'):
        return os.getenv('OPENAI_API_KEY')
    api_key_dotfile_names = ['.openai-api-token-pecan', '.openai-api-token']
    for api_key_dotfile_name in api_key_dotfile_names:
        api_key_file_path = Path.home() / api_key_dotfile_name
        if api_key_file_path.exists():
            return api_key_file_path.read_text().strip()
    raise typer.BadParameter(
        'Must specify --openai-api-key, or set OPENAI_API_KEY environment variable, or have a file at'
        ' ~/.openai-api-token',
    )


def infer_subdir_from_thing(thing: str) -> str | None:
    if util.is_url(url := str(thing)):
        return url.split('/')[-1]
    if util.is_pathlike(thing):
        return Path(thing).stem
    return None


def prepare_output_dir(thing: str, output_dir: str | Path) -> Path:
    from aloud.models import default_output_dir

    random_string = util.random_string(4)
    default_output_subdir = Path(default_output_dir) / random_string
    if output_dir:
        if not util.is_empty_dir(output_dir):
            if thing:
                output_dir = Path(output_dir) / (infer_subdir_from_thing(thing) or random_string)
            else:
                output_dir = default_output_subdir
    else:
        if thing:
            output_dir = infer_subdir_from_thing(thing) or default_output_subdir
        else:
            output_dir = default_output_subdir
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def assert_args_ok(only_audio: bool, only_speakable: bool, output_dir: str | Path = None):
    if only_audio and not output_dir:
        raise typer.BadParameter('Must specify --output-dir when using --only-audio')
    if only_audio and only_speakable:
        raise typer.BadParameter('Cannot specify both --only-audio and --only-speakable')
