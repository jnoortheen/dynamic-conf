# dynamic-config
Easy to manage Config variables separate from App code. Useful while developing and deploying( CI/CD) django web-apps

# Usage

- You need to subclass the `Config` class.
- Any configuration would be loaded from `python config` file `(default: env.py)` from the same folder where library is 
inherited. This file should not be committed to version history.
- You also don't need to include a sample file. Since the `Config` object would be able to generate `env.py` itself.
- It also loads Configuration variables from environment variables. The preference is `env variables` > `env.py`
- The config file should define all the variables needed for a project.
- It can also define a prefix to limit environment variables searched.

```python

# project/conf.py

from dynamic_conf import Config

class CONFIG(Config):
    """singleton to be used for configuring from os.environ and env.py"""

    # default settings

    ENV = "prod" # optional field with a default value

    DB_NAME = "db"
    DB_HOST = "127.0.0.1"
    DB_USER = "postgres"
    DB_PASS = None # even None could be given as default value

    SECRET_KEY:str # required field. Note: it will not work in Python 2 because
```

- to create `project/env.py` just run
```shell script
# you could pass environment variables or set already with export
env DB_PASS='123' dynamic-conf

# or you could pass as list of key-value pair
dynamic-conf DB_USER='user-1' DB_PASS='123'

# to filter environment variables with a prefix
env VARS_PREFIX="PROD_" dynamic-conf PROD_DB_USER="user-2"
```

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
