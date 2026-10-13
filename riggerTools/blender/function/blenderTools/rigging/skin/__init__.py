import os
import importlib

# Find all python files in the current folder (excluding __init__.py)
_dir = os.path.dirname(__file__)
_modules = []

for file in os.listdir(_dir):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]
        module = importlib.import_module(f".{module_name}", package=__name__)
        _modules.append(module)

def register():
    for module in _modules:
        if hasattr(module, "register"):
            module.register()

def unregister():
    for module in reversed(_modules):
        if hasattr(module, "unregister"):
            module.unregister()
