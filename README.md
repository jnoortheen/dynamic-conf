# dynamic-config
Project configuration variables are declared beforehand and inferred from environment variables or configuration files. Useful while developing and deploying( CI/CD) django web-apps

-------

[![PyPi Version](https://img.shields.io/pypi/v/dynamic-conf.svg?style=flat)](https://pypi.python.org/pypi/dynamic-conf)
[![Python Version](https://img.shields.io/pypi/pyversions/returns.svg)](https://pypi.org/project/dynamic-conf/)

-------


# Install
```
pip install dynamic-conf
```

# Features
- supports `.env` or `.py` files
- supports casting with type annotations
- You also don't need to include a sample file. Since the `Config` object would be able to generate `.env.py` itself.
- It also loads Configuration variables from environment variables.
The order of preference is `env variables` > `env.py`
- Attributes are lazily evaluated.

# Getting Started

- You need to subclass the `Config` class.
- The config file should define all the variables needed for a project.

```python

# project/conf.py

from dynamic_conf import Config

class CONFIG(Config):
    """singleton to be used for configuring from os.environ and env.py"""

    SECRET_KEY:str      # required value

    # default settings
    ENV = "prod"        # optional field with a default value

    DB_NAME = "db"
    DB_HOST = "127.0.0.1"
    DB_USER = "postgres"
    DB_PASS = None      # even None could be given as default value
```

- to create `project/env.py` just run with the path to CONFIG class's module
```shell script
# you could pass environment variables or set already with export
env DB_PASS='123' dynamic-conf project/conf.py

dynamic-conf project/conf.py DB_USER='user-1' DB_PASS='123' # pass as list of key-value pair

#to filter environment variables with a prefix
env VARS_PREFIX="PROD_" dynamic-conf project/conf.py PROD_DB_USER="user-2"
```

# Usage

- To use the config simply import and use particular attribute
```python
# project/settings.py
from conf import CONFIG
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": CONFIG.DB_HOST,
        "NAME": CONFIG.DB_NAME,
        "USER": CONFIG.DB_USER,
        "PASSWORD": CONFIG.DB_PASSWORD,
        "PORT": "5432",
    }
}
```

# New release

- create a new release from Github web interface. The package is published to PyPI using Github Actions.
