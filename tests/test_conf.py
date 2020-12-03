import os

import pytest


def create_config_cls():
    import uuid
    from dynamic_conf import REQUIRED, Config

    return type(
        "CONFIG" + str(uuid.uuid4().hex),
        (Config,),
        dict(
            NUM=1,
            NONE_VAL=None,
            OVERLOADED="load",
            VAR=None,
            FROM_FILE=REQUIRED,
            MISSING=REQUIRED,
        ),
    )


@pytest.mark.parametrize("file", ["env.py", ".env"])
def test_config_reading(file, config_factory):
    CONF = config_factory(file)
    assert CONF.NUM == 1  # check type casting
    assert CONF.BOOL == False  # check type casting
    assert CONF.NONE_VAL is None
    assert CONF.VAR == "variable"
    assert CONF.OVERLOADED == "over-loaded"
    assert CONF.FROM_FILE == "file"
    with pytest.raises(LookupError):
        print(CONF.MISSING)


@pytest.mark.parametrize(
    "file, result",
    [
        ("env.py", "ARG1 = 'VAL1'\nARG2 = 'VAL2'"),
        (".env", "ARG1=VAL1\nARG2=VAL2"),
    ],
)
def test_cofig_writing(file, result, create_conf_file, monkeypatch):
    monkeypatch.setenv("ARG1", "VAL1")
    from dynamic_conf import _main

    conf_file = create_conf_file(_file_name=repr(file), ARG1=1)
    _main(conf_file, ["ARG2=VAL2"])  # start write

    env_file = os.path.join(os.path.dirname(conf_file), file)
    assert os.path.exists(env_file)
    with open(env_file) as f:
        content = f.read()
        assert content == result

    with pytest.raises(Exception) as ex:
        _main(conf_file, ["ARG2=VAL2"])  # start write again
        assert "Found" in str(ex)


@pytest.mark.parametrize(
    "file, result",
    [
        ("env.py", "ARG1 = 'VAL1'\nARG2 = 'VAL2'"),
        (".env", "ARG1=VAL1\nARG2=VAL2"),
    ],
)
def test_cofig_writing_with_filter_prefix(file, result, create_conf_file, monkeypatch):
    monkeypatch.setenv("PRE_ARG1", "VAL1")
    monkeypatch.setenv("VARS_PREFIX", "PRE_")
    from dynamic_conf import _main

    conf_file = create_conf_file(_file_name=repr(file), ARG1=1)

    _main(conf_file, ["ARG2=VAL2"])

    env_file = os.path.join(os.path.dirname(conf_file), file)
    assert os.path.exists(env_file)
    with open(env_file) as f:
        content = f.read()
        assert content == result


@pytest.mark.parametrize(
    "file, result",
    [
        ("env.py", "ARG1 = 'VAL1'\nARG3 = 3\nARG2 = 'VAL2'"),
        (".env", "ARG1=VAL1\nARG3=3\nARG2=VAL2"),
    ],
)
def test_cofig_writing_with_dump(file, result, create_conf_file, monkeypatch):
    monkeypatch.setenv("ARG1", "VAL1")
    monkeypatch.setenv("VARS_DUMP", "True")
    from dynamic_conf import _main

    conf_file = create_conf_file(_file_name=repr(file), ARG1=1, ARG3=3)

    _main(conf_file, ["ARG2=VAL2"])

    env_file = os.path.join(os.path.dirname(conf_file), file)
    assert os.path.exists(env_file)
    with open(env_file) as f:
        content = f.read()
        assert content == result


def test_singleton(clean_config):
    create_config_cls()
    with pytest.raises(NotImplementedError):
        create_config_cls()
