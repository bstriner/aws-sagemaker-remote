from types import ModuleType
import os


def module_path(module):
    if isinstance(module, ModuleType):
        path = os.path.abspath(module.__file__)
        return os.path.dirname(path)
    else:
        return module
