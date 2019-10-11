from __future__ import print_function

from collections import OrderedDict

try:
    reload
except Exception:
    from importlib import reload

import importlib
import os

from six import with_metaclass

_UNDEFINED = object()
REQUIRED = object()  # only for Python2 support


class Var(object):
    def __init__(self, module, name, default=_UNDEFINED):
        """
            if not given a default explicitly then this will raise an error.
            Get the given environment variable in followind order
                1. os.environment
                2. {_file_name}.py
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
                self.name, owner.get_env_file_path()
            )
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
            reload(os)
            env_module = import_env_module(cls)
            for attrname, attrvalue in attrs.items():
                if not attrname.startswith("_"):
                    setattr(cls, attrname, Var(env_module, attrname, default=attrvalue))
                elif attrname == "__annotations__":
                    for annot in attrvalue:
                        setattr(cls, annot, Var(env_module, annot, default=REQUIRED))
        return cls


class Config(with_metaclass(ConfigMeta)):
    """singleton to be used for configuring from os.environ and {_file_name}.py"""

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
    def _create(cls, argv):
        CONF_FILE = cls.get_env_file_path()
        if os.path.exists(CONF_FILE):
            print("Found", CONF_FILE, "existing already")
            return

        vals = OrderedDict()
        prefix = os.environ.get("VARS_PREFIX", cls._default_prefix)
        for k, val in os.environ.items():
            if k.startswith(prefix):
                vals[k.replace(prefix, "")] = val
        for k in cls.__dict__.keys():
            if k in os.environ:
                vals[k] = os.environ[k]

        for arg in argv:
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

    @classmethod
    def create(cls, argv):
        if len(cls._registry) < 2:
            raise NotImplementedError(
                "Config object is not inherited or the config file is not loaded."
            )

        return cls._registry[-1]._create(argv)
