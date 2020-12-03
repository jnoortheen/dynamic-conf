from pathlib import Path
import typing as tp
from arger import Arger
import argparse as ap
from ._conf import Config, REQUIRED
from ._import import import_file


def _main(conf_file: Path, vars: tp.List[str]):
    """CLI to create env.py or .env file from vars positional argument or from ENV variables.

    Parameters
    ----------
    conf_file:
        file path to the config file. (one that import dynamic_conf.Config class)
    vars:
        a list of variables can defined to endup in the env file in `key=value` format

    Examples
    --------
    # you could pass environment variables or set already with export
    $ env DB_PASS='123' dynamic-conf project/conf.py

    $ dynamic-conf project/conf.py DB_USER='user-1' DB_PASS='123' # pass as list of key-value pair

    #to filter environment variables with a prefix
    $ env VARS_PREFIX="PROD_" dynamic-conf project/conf.py PROD_DB_USER="user-2"
    """
    import_file(conf_file)
    Config.create(vars)


def main():
    Arger(_main, formatter_class=ap.RawTextHelpFormatter).run()


if __name__ == "__main__":
    main()
