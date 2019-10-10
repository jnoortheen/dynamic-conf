import os
import uuid

from dynamic_conf import Config, REQUIRED


os.environ["VAR"] = "variable"


def create_config():
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


def get_config():
    class CONFIG(Config):
        NUM = 1
        NONE_VAL = None
        OVERLOADED = "load"
        VAR = None
        FROM_FILE = REQUIRED
        MISSING = REQUIRED

    return CONFIG
