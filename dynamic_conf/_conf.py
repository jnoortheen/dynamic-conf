from __future__ import print_function

from collections import OrderedDict
from typing import Type

from ._import import import_file

try:
    reload
except Exception:
    from importlib import reload

import importlib
import os

from six import with_metaclass
import logging


_UNDEFINED = object()
REQUIRED = object()  # only for Python2 support
log = logging.getLogger(__file__)


class Var(object):
    def __init__(self, module, name, default=_UNDEFINED):
        """
            if not given a default explicitly then this will raise an error.
            Get the given environment variable in following order
                1. os.environment
                2. {file_name}.py or .env (if the name ends with .env and set by user)
                3. default value
        """
        self.name = name
        self.module = module
        self.default = default

    def __get__(self, instance, owner):
        if self.name in os.environ:
            return os.environ[self.name]
        if self.module and hasattr(self.module, self.name):
            return getattr(self.module, self.name)
        if self.default not in {_UNDEFINED, REQUIRED}:
            return self.default

        raise LookupError(
            "Failed to get {} variable from os.environ or {}".format(
                self.name, get_env_file_path(owner)
            )
        )


def get_env_file_path(cls):
    conf = cls._registry[-1]
    mod = importlib.import_module(conf.__module__)
    mod_dir = os.path.dirname(mod.__file__) if hasattr(mod, "__file__") else "."
    return os.path.join(mod_dir, "{}.py".format(cls.file_name))


def import_env_module(cls):
    # reload os.environ
    reload(os)

    # an object that supports getattr
    env_module = None
    file_path = get_env_file_path(cls)
    try:
        env_module = import_file(file_path)
    except ImportError:
        log.info(
            "{} is not found. Getting variables from environment.".format(file_path)
        )
    return env_module


class ConfigMeta(type):
    def __new__(mcls, name, bases, attrs):
        # Go over attributes and see if they should be renamed.
        cls = super(ConfigMeta, mcls).__new__(
            mcls, name, bases, attrs
        )  # type: Type[Config]
        cls._registry.append(cls)
        if len(cls._registry) > 2:
            raise NotImplementedError(
                "{} should be used as a singleton and not be inherited multiple times".format(
                    cls
                )
            )

        if len(cls._registry) > 1:
            env_module = import_env_module(cls)
            for attrname, attrvalue in attrs.items():
                if not attrname.startswith("_"):
                    setattr(cls, attrname, Var(env_module, attrname, default=attrvalue))
                elif attrname == "__annotations__":
                    for annot in attrvalue:
                        setattr(cls, annot, Var(env_module, annot, default=REQUIRED))
        return cls


def _normalize_prefix(default_prefix):
    prefix = os.environ.get("VARS_PREFIX", default_prefix)
    vals = OrderedDict()
    if prefix:
        for k, val in os.environ.items():
            if k.startswith(prefix):
                vals[k.replace(prefix, "")] = val
    return vals


DEFAULT_FILE = "env"


def writer(cls, argv):
    # type: (Config, str) -> OrderedDict

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

    if vals:
        log.info(
            "Writing following keys\n\t"
            + "\n\t".join(vals.keys())
            + "\n to "
            + CONF_FILE
        )
        with open(CONF_FILE, "w") as f:
            f.write(
                "\n".join(["{} = {}".format(k, repr(val)) for k, val in vals.items()])
            )
    else:
        log.info("Dynamic-Conf: No variables available.")

    return vals


class Config(with_metaclass(ConfigMeta)):
    """singleton to be used for configuring from os.environ and {file_name}.py"""

    file_name = DEFAULT_FILE
    """by default the suffix will be .py unless the file name is changed in the subclass"""

    _default_prefix = ""
    _registry = []

    @classmethod
    def create(cls, argv):
        if len(cls._registry) < 2:
            raise NotImplementedError(
                "Config object is not inherited or the config file is not loaded."
            )

        return writer(cls._registry[-1], argv)
