__version__ = "0.0.1"
from .conf import Config, REQUIRED


def main():
    Config.create()


if __name__ == "__main__":
    main()
