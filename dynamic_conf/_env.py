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
    except TypeError:
        pass
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


def _read_dotenv(file_path):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path) as f:
            for line in f:
                if (
                    line.strip().startswith("#") or not line.strip()
                ):  # skip comments and empty lines
                    continue
                key, value = line.strip().split("=", 1)
                env_vars[key] = value  # Save to a list
    return env_vars


def _normalize_prefix(default_prefix):
    prefix = os.environ.get("VARS_PREFIX", default_prefix)
    vals = OrderedDict()
    if prefix:
        for k, val in os.environ.items():  # type: str, object
            if k.startswith(prefix):
                vals[k.lstrip(prefix)] = val
    return vals


def _write_py(file, vals):
    file.write("\n".join(["{} = {}".format(k, repr(val)) for k, val in vals.items()]))


def _write_env(file, vals):
    file.write("\n".join(["{}={}".format(k, val) for k, val in vals.items()]))


def writer(cls, argv):
    CONF_FILE = get_env_file_path(cls)
    if os.path.exists(CONF_FILE):
        raise Exception(f"Found {CONF_FILE} existing already")

    vals = OrderedDict()
    vals.update(_normalize_prefix(cls._default_prefix))
    for k in cls.__dict__.keys():
        if k in os.environ:
            vals[k] = os.environ[k]

    for arg in argv:
        if "=" in arg:
            k, val = arg.split("=")
            vals[k] = val

    if os.environ.get("VARS_DUMP", cls._dump):
        for k in cls.__dict__.keys():
            if k not in vals and not k.startswith("_"):
                vals[k] = getattr(cls, k)

    if vals:
        log.info(
            "Writing following keys\n\t"
            + "\n\t".join(vals.keys())
            + "\n to "
            + CONF_FILE
        )
        with open(CONF_FILE, "w") as f:
            if CONF_FILE.endswith(".py"):
                _write_py(f, vals)
            else:
                _write_env(f, vals)
    else:
        log.info("Dynamic-Conf: No variables available.")

    return vals
