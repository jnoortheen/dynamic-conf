from dynamic_conf import Config, REQUIRED


class CONFIG(Config):
    NUM = 1
    NONE_VAL = None
    OVERLOADED = "load"
    VAR = None
    FROM_FILE = REQUIRED
    MISSING = REQUIRED
