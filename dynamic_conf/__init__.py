__version__ = "0.0.1"

import importlib
import sys

from .conf import Config, REQUIRED


def main(argv):
    conf_module_path = argv.pop(0)
    importlib.import_module(conf_module_path)
    Config.create(argv)


if __name__ == "__main__":
    main(sys.argv)
