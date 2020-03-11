import importlib.util
import os
import sys


def get_module_name(path):
    act_path = path.replace(os.getcwd(), "", 1)
    act_path, _ = os.path.splitext(act_path)
    act_path = act_path.strip(os.sep)
    return act_path.replace(os.sep, ".")


def import_file(path):
    # type: (str) -> any
    if os.path.exists(path):
        module_name = get_module_name(path)
        if module_name in sys.modules:
            return sys.modules[module_name]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
