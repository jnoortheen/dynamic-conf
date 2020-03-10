import importlib.util
import os
import sys


def import_file(path):
    if os.path.exists(path):
        module_name = os.path.basename(os.path.dirname(path))
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
