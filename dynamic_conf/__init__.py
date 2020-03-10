import sys

from ._conf import Config, REQUIRED
from ._import import import_file


def _main(argv):
    conf_file = argv.pop(0)
    import_file(conf_file)
    Config.create(argv)


def main():
    argv = sys.argv
    argv.pop(0)  # remove the calling script
    _main(argv)


if __name__ == "__main__":
    main()
