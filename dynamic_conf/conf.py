from __future__ import print_function

import importlib
import os
import sys

from six import with_metaclass

_UNDEFINED = object()
REQUIRED = object()  # only for Python2 support


def get_conf_var(module, name, default=_UNDEFINED):
    """
        if not given a default explicitly then this will raise an error.
        Get the given environment variable in followind order
            1. os.environment
            2. env.py
            3. default value
    """

    if name in os.environ:
        return os.environ[name]
    if module and hasattr(module, name):
        return getattr(module, name)
    if default != _UNDEFINED:
        return default

    raise Exception(
        "Failed to get {} variable from os.environ or {}".format(name, module)
    )


def import_env_module(cls):
    env_module = None

    pre_mod = cls.__module__.rsplit(".", 1)[:-1]
    env_module_path = ".".join(pre_mod + [cls._file_name])
    try:
        env_module = importlib.import_module(env_module_path)
    except ImportError:
        print(
            "{} is not found. Getting variables from environment.".format(
                cls.get_env_file_path()
            )
        )
    return env_module


class ConfigMeta(type):
    def __new__(mcls, name, bases, attrs):
        # Go over attributes and see if they should be renamed.
        cls = super(ConfigMeta, mcls).__new__(mcls, name, bases, attrs)
        cls._registry.append(cls)
        if len(cls._registry) > 2:
            raise NotImplementedError(
                "{} should be used as a singleton and not be inherited multiple times".format(
                    cls
                )
            )

        if len(cls._registry) > 1:
            # reload os.environ
            importlib.reload(os)
            env_module = import_env_module(cls)
            for attrname, attrvalue in attrs.items():
                if not attrname.startswith("_"):
                    setattr(
                        cls,
                        attrname,
                        get_conf_var(env_module, attrname, default=attrvalue),
                    )
        return cls


class Config(with_metaclass(ConfigMeta)):
    """singleton to be used for configuring from os.environ and env.py"""

    _file_name = "env"
    _default_prefix = "PROD_"
    _registry = []

    @classmethod
    def get_env_file_path(cls):
        conf = cls._registry[-1]
        mod = importlib.import_module(conf.__module__)
        return os.path.join(
            os.path.dirname(mod.__file__), "{}.py".format(cls._file_name)
        )

    @classmethod
    def create(cls):
        CONF_FILE = cls.get_env_file_path()
        if os.path.exists(CONF_FILE):
            print("Found", CONF_FILE, "existing already")
            return

        vals = {}
        prefix = os.environ.get("VARS_PREFIX", cls._default_prefix)
        for k, val in os.environ.items():
            if k.startswith(prefix):
                vals[k.replace(prefix, "")] = val
        for k in cls.__dict__.keys():
            if k in os.environ:
                vals[k] = os.environ[k]

        for arg in sys.argv:
            if "=" in arg:
                k, val = arg.split("=")
                vals[k] = val

        if vals:
            print(
                "Writing following keys\n\t"
                + "\n\t".join(vals.keys())
                + "\n to "
                + CONF_FILE
            )
            with open(CONF_FILE, "w") as f:
                f.write(
                    "\n".join(
                        ["{} = {}".format(k, repr(val)) for k, val in vals.items()]
                    )
                )
        else:
            print("Dynamic-Conf: No variables available.")

        return vals
