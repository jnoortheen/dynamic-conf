import os

import pytest

from dynamic_conf import Config, REQUIRED

os.environ["VAR"] = "variable"


class CONFIG(Config):
    NUM = 1
    NONE_VAL = None
    OVERLOADED = "load"
    VAR = None

    FROM_FILE = REQUIRED
    MISSING = REQUIRED
    # Req: str


def test_config_loading():
    assert CONFIG.NUM == 1
    assert CONFIG.NONE_VAL is None
    assert CONFIG.OVERLOADED == "over-loaded"
    assert CONFIG.VAR == "variable"
    assert CONFIG.FROM_FILE == "file"
    with pytest.raises(LookupError):
        print(CONFIG.MISSING)
    # with pytest.raises(LookupError):
    #     print(CONFIG.Req)
