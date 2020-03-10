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


def test_config_loading(CONFIG):
    assert CONFIG.NUM == 1
    assert CONFIG.NONE_VAL is None
    assert CONFIG.OVERLOADED == "over-loaded"
    assert CONFIG.VAR == "variable"
    assert CONFIG.FROM_FILE == "file"
    with pytest.raises(LookupError):
        print(CONFIG.MISSING)


def test_cofig_writing(create_conf_file):
    from dynamic_conf import _main

    conf_file = create_conf_file(
        NUM=1, NONE_VAL="None", OVERLOADED='"load"', VAR="None",
    )

    _main([conf_file, "ARG1=VAL1", "ARG2=VAL2"])

    env_file = os.path.join(os.path.dirname(conf_file), "env.py")
    assert os.path.exists(env_file)
    with open(env_file) as f:
        assert f.read() == "ARG1 = 'VAL1'\nARG2 = 'VAL2'"


def test_singleton(clean_config):
    create_config_cls()
    with pytest.raises(NotImplementedError):
        create_config_cls()
