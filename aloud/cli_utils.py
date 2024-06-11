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
    possible_api_key_file_paths = (
        '~/.openai-api-key',
        # repo root / '.openai-api-key',
    )
    for api_key_file_path in possible_api_key_file_paths:
        if (file_path := Path(api_key_file_path).expanduser()).exists():
            return file_path.read_text().strip()
    raise typer.BadParameter(
        'Must specify --openai-api-key, or set OPENAI_API_KEY environment variable, or have a file '
        'containing the key at one of the following locations: '
        ', '.join(possible_api_key_file_paths),
    )


def infer_subdir_from_thing(thing: str | Path) -> str | None:
    if util.is_url(url := str(thing)):
        return url.removesuffix('/').split('/')[-1]
    if util.is_pathlike(thing):
        return Path(thing).stem
    return None


def ensure_dir_exists(returns_path: Callable[..., Path]) -> Callable[..., Path]:
    def wrapper(*args, **kwargs) -> Path:
        path = returns_path(*args, **kwargs)
        path.mkdir(parents=True, exist_ok=True)
        return path

    return wrapper


@ensure_dir_exists
def prepare_output_dir(thing: str | Path | None, output_dir: str | Path | None) -> Path:
    random_string = util.random_string(4)
    inferred_subdir = infer_subdir_from_thing(thing)
    if output_dir:
        output_dir = Path(output_dir)
        if output_dir.is_file():
            raise typer.BadParameter(f'{output_dir} is a file. --output-dir must be a directory (or omitted)')
        if output_dir.exists():
            if util.is_empty_dir(output_dir):
                if thing:
                    if inferred_subdir:
                        return output_dir / inferred_subdir
                    return output_dir
                return output_dir
            if thing:
                if inferred_subdir:
                    return output_dir / inferred_subdir
                return output_dir / random_string
            return output_dir / random_string
        if thing:
            if inferred_subdir:
                return output_dir / inferred_subdir
            return output_dir / random_string
        return output_dir
    if thing:
        if inferred_subdir:
            return Path.cwd() / inferred_subdir
        return Path.cwd() / random_string
    from aloud.models import default_output_dir

    return default_output_dir / random_string


def assert_args_ok(only_audio: bool, only_speakable: bool, output_dir: str | Path = None):  # noqa: FBT001
    if only_audio and not output_dir:
        raise typer.BadParameter('Must specify --output-dir when using --only-audio')
    if only_audio and only_speakable:
        raise typer.BadParameter('Cannot specify both --only-audio and --only-speakable')
