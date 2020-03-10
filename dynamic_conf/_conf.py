from __future__ import print_function

import logging
import os
from typing import Type, Mapping

from six import with_metaclass

from ._env import get_env_file_path, reader, writer, DEFAULT_FILE

_UNDEFINED = object()
REQUIRED = object()  # only for Python2 support

log = logging.getLogger(__file__)


class Var(object):
    def __init__(self, module, name, default=_UNDEFINED):
        """
            if not given a default explicitly then this will raise an error.
            Get the given environment variable in following order
                1. os.environment
                2. {_file_name}.py or .env (if the name ends with .env and set by user)
                3. default value
        """
        self.name = name
        self.module = module
        self.default = default

    def __get__(self, instance, owner):
        if self.name in os.environ:
            return os.environ[self.name]
        if self.module:
            if isinstance(self.module, dict) and self.name in self.module:
                return self.module[self.name]
            if hasattr(self.module, self.name):
                return getattr(self.module, self.name)
        if self.default not in {_UNDEFINED, REQUIRED}:
            return self.default

        raise LookupError(
            "Failed to get {} variable from os.environ or {}".format(
                self.name, get_env_file_path(owner)
            )
        )


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
            env_module = reader(cls)
            for attrname, attrvalue in attrs.items():
                if not attrname.startswith("_"):
                    setattr(cls, attrname, Var(env_module, attrname, default=attrvalue))
                elif attrname == "__annotations__":
                    for annot in attrvalue:
                        setattr(cls, annot, Var(env_module, annot, default=REQUIRED))
        return cls


class Config(with_metaclass(ConfigMeta)):
    """singleton to be used for configuring from os.environ and {_file_name}.py"""

    _file_name = DEFAULT_FILE
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

    @classmethod
    def get_file_name(cls):
        if cls._file_name == DEFAULT_FILE:
            return f"{cls._file_name}.py"
        else:
            return cls._file_name
