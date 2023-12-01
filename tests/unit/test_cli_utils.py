from pathlib import Path

from aloud.cli_utils import prepare_output_dir
from aloud import util

def test_prepare_output_dir():
    # None, None
    thing, output_dir = None, None
    result = prepare_output_dir(thing, output_dir)
    assert result.parent == Path('/tmp')
    assert len(result.name) == 4
    assert util.is_empty_dir(result)

    # thing, None
    thing, output_dir = "http://www.google.com/foo", None
    result = prepare_output_dir(thing, output_dir)
    assert result.resolve() == (Path.cwd() / 'foo').resolve()
    assert util.is_empty_dir(result)

    thing, output_dir = "www.google.com/bar", None
    result = prepare_output_dir(thing, output_dir)
    assert result.resolve() == (Path.cwd() / 'bar').resolve()
    assert util.is_empty_dir(result)

    thing, output_dir = Path('/tmp'), None
    result = prepare_output_dir(thing, output_dir).resolve()
    assert result.parent == Path('/tmp')
    assert len(result.name) == 4
    assert util.is_empty_dir(result)

    random_string = util.random_string(4)
    thing, output_dir = Path('/tmp') / random_string, None
    result = prepare_output_dir(thing, output_dir).resolve()
    assert result == (Path('/tmp') / random_string).resolve()
    assert util.is_empty_dir(result)

    # None, output_dir
    thing, output_dir = None, Path('/tmp')
    result = prepare_output_dir(thing, output_dir).resolve()
    assert result.parent == Path('/tmp')
    assert len(result.name) == 4
    assert util.is_empty_dir(result)

    random_string = util.random_string(4)
    thing, output_dir = None, Path('/tmp') / random_string
    result = prepare_output_dir(thing, output_dir).resolve()
    assert result == (Path('/tmp') / random_string).resolve()

    # thing, output_dir
