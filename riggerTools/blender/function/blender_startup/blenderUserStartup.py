r"""
Blender User Startup Script

Place or symlink this file to Blender's startup folder to run it automatically on launch:
Windows:
    C:\Users\<User>\AppData\Roaming\Blender Foundation\Blender\<Version>\scripts\startup\blenderUserStartup.py
"""

import sys
import os
import builtins
import importlib

# Inject reload into builtins for ease of use in Blender (Python 3)
builtins.reload = importlib.reload

# Append the repository path to sys.path
module_path = r"D:\sysTools\nmTools_github\riggerTools\blender"
if module_path not in sys.path:
    sys.path.append(module_path)
    print(f"Added path to sys.path: {module_path}")

# Import the central register module from the repository
from function.blenderTools import register as repo_register

def register():
    repo_register.register()

def unregister():
    repo_register.unregister()
