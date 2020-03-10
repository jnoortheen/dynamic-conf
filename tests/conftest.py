import os

import pytest

from dynamic_conf import Config


@pytest.fixture
def clean_config():
    yield
    if len(Config._registry) == 2:
        # cleanup
        Config._registry.pop()


@pytest.fixture
def create_env_file(tmp_path, clean_config):
    def _factory(**kwargs):
        env_file = os.path.join(str(tmp_path), "env.py")
        attrs = "\n".join([f"{k}={val}" for k, val in kwargs.items()])
        with open(env_file, "w") as f:
            f.write(
                f"""\
{attrs}
"""
            )

        return env_file

    return _factory


@pytest.fixture
def create_conf_file(tmp_path, clean_config):
    def _factory(**kwargs):
        conf_file = os.path.join(str(tmp_path), "conf.py")
        attrs = "\n".join([f"    {k}={val}" for k, val in kwargs.items()])
        with open(conf_file, "w") as f:
            f.write(
                f"""\
from dynamic_conf import Config, REQUIRED
class CONFIG(Config):
{attrs}
"""
            )
        return conf_file

    return _factory


@pytest.fixture
def CONFIG(create_conf_file, create_env_file):
    from dynamic_conf._import import import_file

    os.environ["VAR"] = "variable"
    conf = create_conf_file(
        NUM=1,
        NONE_VAL="None",
        OVERLOADED='"load"',
        VAR="None",
        FROM_FILE="REQUIRED",
        MISSING="REQUIRED",
    )
    create_env_file(
        FROM_FILE='"file"', OVERLOADED='"over-loaded"'
    )  # create env.py before module import

    mod = import_file(conf)
    yield mod.CONFIG
    os.environ.pop("VAR")
