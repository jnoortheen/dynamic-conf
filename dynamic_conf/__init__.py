import importlib
import os
import sys

from ._conf import Config, REQUIRED


def _main(argv):
    conf_file = argv.pop(0)
    conf_dir, conf_file = os.path.split(conf_file)
    if conf_dir:
        sys.path.insert(0, conf_dir)
    importlib.import_module(os.path.splitext(conf_file)[0])
    Config.create(argv)


def main():
    argv = sys.argv
    argv.pop(0)  # remove the calling script
    _main(argv)


if __name__ == "__main__":
    main()
