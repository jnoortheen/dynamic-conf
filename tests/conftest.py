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
    def _factory(
        file_name,
        **kwargs,
    ):
        env_file = os.path.join(str(tmp_path), file_name)
        attrs = "\n".join(
            [
                f"{k}={repr(val) if file_name.endswith('.py') else val}"
                for k, val in kwargs.items()
            ]
        )
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
    def _factory(*lines, **kwargs):
        conf_file = os.path.join(str(tmp_path), "conf.py")
        attrs = "\n".join([f"    {k}={val}" for k, val in kwargs.items()])
        lines = "\n".join([f"    {l}" for l in lines])
        with open(conf_file, "w") as f:
            f.write(
                f"""\
from dynamic_conf import Config, REQUIRED
class CONFIG(Config):
{attrs}
{lines}
"""
            )
        return conf_file

    return _factory


@pytest.fixture
def config_factory(create_conf_file, create_env_file, monkeypatch):
    def _factory(file_name):
        from dynamic_conf._import import import_file

        monkeypatch.setenv("VAR", "variable")
        conf = create_conf_file(
            "REQUIRED_NUM:int",
            _file_name=repr(file_name),
            NONE_VAL="None",
            OVERLOADED='"load"',
            VAR="None",
            FROM_FILE="REQUIRED",
            MISSING="REQUIRED",
            **{"NUM:int": "1", "BOOL:bool": "'false'"},
        )
        _ = create_env_file(
            file_name=file_name,
            FROM_FILE="file",
            OVERLOADED="over-loaded",
            **{"# comment": "comment too"},
        )  # create env.py before module import
        mod = import_file(conf)
        return mod.CONFIG

    return _factory
