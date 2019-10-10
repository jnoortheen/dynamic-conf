import os

import pytest

from dynamic_conf import Config
from .conf import create_config, get_config


@pytest.yield_fixture(name="clean_config")
def clean_config():
    yield
    if len(Config._registry) == 2:
        # cleanup
        Config._registry.pop()


def test_config_loading(clean_config):
    CONFIG = get_config()
    assert CONFIG.NUM == 1
    assert CONFIG.NONE_VAL is None
    assert CONFIG.OVERLOADED == "over-loaded"
    assert CONFIG.VAR == "variable"
    assert CONFIG.FROM_FILE == "file"
    with pytest.raises(LookupError):
        print(CONFIG.MISSING)
    # with pytest.raises(LookupError):
    #     print(CONFIG.Req)


def test_cofig_writing(tmp_path, clean_config):
    conf_file = os.path.join(tmp_path, "conf.py")
    with open(conf_file, "w") as f:
        f.write(
            """\
from dynamic_conf import Config
class CONFIG(Config):
    NUM = 1
    NONE_VAL = None
    OVERLOADED = "load"
    VAR = None       
"""
        )

    from dynamic_conf import main
    import sys

    sys.path.append(str(tmp_path))
    main(["conf", "ARG1=VAL1", "ARG2=VAL2"])

    env_file = os.path.join(tmp_path, "env.py")
    assert os.path.exists(env_file)
    with open(env_file) as f:
        assert f.read() == "ARG1 = 'VAL1'\nARG2 = 'VAL2'"


def test_singleton(clean_config):
    create_config()
    with pytest.raises(NotImplementedError):
        create_config()
