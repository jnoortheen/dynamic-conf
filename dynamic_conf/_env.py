"""Envs file types

1. .py
2. .env
"""

import logging
from _collections import OrderedDict

from ._import import import_file

try:
    reload
except Exception:
    from importlib import reload

import os
import inspect

log = logging.getLogger(__file__)

DEFAULT_FILE = "env"


def get_env_file_path(cls):
    conf = cls._registry[-1]
    mod_path = "."
    try:
        mod_path = os.path.dirname(inspect.getfile(conf))
    except TypeError:  # pragma: no cover - case where the class is defined in REPL
        pass  # pragma: no cover
    return os.path.join(mod_path, cls.get_file_name())


def reader(cls):
    # reload os.environ
    reload(os)

    # an object that supports getattr
    file_path = get_env_file_path(cls)
    _, ext = os.path.splitext(file_path)
    if ext == ".py":
        env_module = import_file(file_path)
    else:
        env_module = _read_dotenv(file_path)
    if not env_module:
        log.info(
            "{} is not found. Getting variables from environment.".format(file_path)
        )

    return env_module


def _parse_dotenv(content):
    """
    :type content str
    """

    env_vars = {}
    for line in content.splitlines():
        if (
            line.strip().startswith("#") or not line.strip()
        ):  # skip comments and empty lines
            continue
        key, value = line.strip().split("=", 1)
        env_vars[key] = value  # Save to a list
    return env_vars


def _read_dotenv(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            return _parse_dotenv(f.read())


def _normalize_prefix(default_prefix):
    prefix = os.environ.get("VARS_PREFIX", default_prefix)
    vals = OrderedDict()
    if prefix:
        for k, val in os.environ.items():  # type: str, object
            if k.startswith(prefix):
                vals[k.replace(prefix, "", 1)] = val
    return vals


def _write_py(file, vals):
    file.write("\n".join(["{} = {}".format(k, repr(val)) for k, val in vals.items()]))


def _write_env(file, vals):
    file.write("\n".join(["{}={}".format(k, val) for k, val in vals.items()]))


def _write(CONF_FILE, vals):
    log.info(
        "Writing following keys\n\t" + "\n\t".join(vals.keys()) + "\n to " + CONF_FILE
    )
    with open(CONF_FILE, "w") as f:
        if CONF_FILE.endswith(".py"):
            _write_py(f, vals)
        else:
            _write_env(f, vals)


def to_bool(value):
    """utility function for boolean casting
    >>> to_bool("True")
    True
    >>> to_bool("False")
    False
    >>> to_bool(True)
    True

    :type value any
    """
    valid = {
        "True": True,
        "true": True,
        "on": True,
        "t": True,
        "1": True,
        "False": False,
        "false": False,
        "off": False,
        "f": False,
        "0": False,
    }

    if isinstance(value, bool):
        return value

    lower_value = value.lower()
    if lower_value in valid:
        return valid[lower_value]
    else:
        raise ValueError(
            "invalid literal for boolean: {}. Possible values are {}".format(
                value, list(valid)
            )
        )


def writer(cls, argv):
    conf_file_path = get_env_file_path(cls)
    if os.path.exists(conf_file_path):
        raise Exception(f"Found {conf_file_path} existing already")

    vals = OrderedDict()
    vals.update(_normalize_prefix(cls._default_prefix))
    for k in cls.__dict__.keys():
        if k in os.environ:
            vals[k] = os.environ[k]

    for arg in argv:
        if "=" in arg:
            k, val = arg.split("=")
            vals[k] = val

    dump = os.environ.get("VARS_DUMP", cls._dump)  # type: Union[bool, List[str]]
    if dump:
        for k in cls.__dict__.keys():
            if isinstance(dump, (list, tuple)) and k not in dump:
                continue
            if k not in vals and not k.startswith("_"):
                vals[k] = getattr(cls, k)

    if vals:
        ordered_vals = OrderedDict()
        for k in cls.__dict__.keys():
            if k in vals:
                ordered_vals[k] = vals.pop(k)

        ordered_vals.update(vals)
        _write(conf_file_path, ordered_vals)
    else:
        log.info("Dynamic-Conf: No variables available.")  # pragma: no cover

    return vals
