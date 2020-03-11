from dynamic_conf._env import _parse_dotenv, to_bool
import pytest


def test_parse_dotenv():
    assert _parse_dotenv("""env=1\n#commentline\n  \n""") == {"env": "1"}


def test_to_bool():
    with pytest.raises(ValueError):
        to_bool("audi")
