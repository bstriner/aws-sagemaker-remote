from types import ModuleType
import os


def module_path(module):
    if isinstance(module, ModuleType):
        path = os.path.abspath(module.__file__)
        if path.endswith("__init__.py"):
            path = os.path.dirname(path)
        return path
    else:
        return module
