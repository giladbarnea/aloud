from pathlib import Path

from aloud import util
from aloud.cli_utils import infer_subdir_from_thing, prepare_output_dir


def test_prepare_output_dir_both_None():
    thing, output_dir = None, None
    result = prepare_output_dir(thing, output_dir)
    assert result.parent.samefile('/tmp')
    assert len(result.name) == 4
    assert util.is_empty_dir(result)
    result.rmdir()


def test_prepare_output_dir_only_with_thing():
    output_dir = None
    thing = 'http://www.google.com/foo'
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path.cwd() / 'foo')
    assert util.is_empty_dir(result)
    result.rmdir()

    thing = 'www.google.com/bar'
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path.cwd() / 'bar')
    assert util.is_empty_dir(result)
    result.rmdir()

    thing = Path(
        'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
    )
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path.cwd() / 'reshaping-the-tree-rebuilding-organizations')
    assert util.is_empty_dir(result)
    result.rmdir()

    thing = 'DOES_NOT_EXIST_AND_DOES_NOT_LOOK_LIKE_A_PATH_OR_URL'
    result = prepare_output_dir(thing, output_dir)
    assert str(result.resolve()) != str((Path.cwd() / thing).resolve())
    assert len(result.name) == 4
    assert util.is_empty_dir(result)
    result.rmdir()


def test_prepare_output_dir_only_with_output_dir():
    thing = None
    output_dir = Path('/tmp')
    result = prepare_output_dir(thing, output_dir)
    assert result.parent.samefile('/tmp')
    assert len(result.name) == 4
    assert util.is_empty_dir(result)
    result.rmdir()

    random_string = util.random_string(4)
    output_dir = Path('/tmp') / random_string
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path('/tmp') / random_string)


def test_prepare_output_dir_with_thing_and_output_dir_and():
    thing = 'http://www.google.com/foo'
    output_dir = Path('/tmp')
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path('/tmp') / 'foo')
    assert util.is_empty_dir(result)
    result.rmdir()

    thing = 'www.google.com/bar'
    output_dir = Path('/tmp')
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path('/tmp') / 'bar')
    assert util.is_empty_dir(result)
    result.rmdir()

    thing = 'www.google.com/bar'
    random_string = util.random_string(4)
    output_dir = Path('/tmp') / random_string
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path('/tmp') / random_string / 'bar')
    assert util.is_empty_dir(result)
    result.rmdir()

    thing = Path(
        'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
    )
    output_dir = Path('/tmp')
    result = prepare_output_dir(thing, output_dir)
    assert result.samefile(Path('/tmp') / 'reshaping-the-tree-rebuilding-organizations')

    thing = 'DOES_NOT_EXIST_AND_DOES_NOT_LOOK_LIKE_A_PATH_OR_URL'
    output_dir = Path('/tmp')
    result = prepare_output_dir(thing, output_dir)
    assert str(result.resolve()) != str((Path.cwd() / thing).resolve())
    assert len(result.name) == 4
    assert util.is_empty_dir(result)
    result.rmdir()


def test_infer_subdir_from_thing():
    assert infer_subdir_from_thing('http://www.google.com/foo') == 'foo'
    assert infer_subdir_from_thing('www.google.com/bar') == 'bar'
    assert infer_subdir_from_thing('DOES_NOT_EXIST_AND_DOES_NOT_LOOK_LIKE_A_PATH_OR_URL') is None
    assert (
        infer_subdir_from_thing(
            Path(
                'tests/data/reshaping-the-tree-rebuilding-organizations/reshaping-the-tree-rebuilding-organizations.html'
            )
        )
        == 'reshaping-the-tree-rebuilding-organizations'
    )
    assert infer_subdir_from_thing('https://a16z.com/big-ideas-in-tech-2024/') == 'big-ideas-in-tech-2024'
