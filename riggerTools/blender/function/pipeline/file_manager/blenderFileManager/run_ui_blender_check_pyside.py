import sys
import subprocess
import bpy

# 1. Check Blender and choose suitable module
python_exe = sys.executable
blender_major_version = bpy.app.version[0]
package_to_install = "PySide6" if blender_major_version >= 4 else "PySide2"

print(f"Detecting Blender {bpy.app.version_string}...")

# Check pyside is already exists
pyside_installed = False
try:
	if package_to_install == "PySide6":
		from PySide6 import QtWidgets
	else:
		from PySide2 import QtWidgets
	pyside_installed = True
	print(f"{package_to_install} is already installed.")
except ImportError:
	print(f"{package_to_install} not found. Starting installation...")

# if not install via pip of inside Blender 
if not pyside_installed:
	try:
		# enable pip (if not)
		subprocess.check_call([python_exe, "-m", "ensurepip"])
		# upgrade pip
		subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
		# install PySide
		subprocess.check_call([python_exe, "-m", "pip", "install", package_to_install])
		print(f"Successfully installed {package_to_install}!")
	except Exception as e:
		print(f"Failed to install {package_to_install} via pip: {e}")

# 2. Add Project 'nmTools_github' path
module_path = r"D:\sysTools\nmTools_github\riggerTools\blender"

#  (insert  0)
if module_path not in sys.path:
    sys.path.insert(0, module_path)
else:
    sys.path.remove(module_path)
    sys.path.insert(0, module_path)

# Clear cache
for key in list(sys.modules.keys()):
    if key == "function" or key.startswith("function."):
        del sys.modules[key]



print("--- Debug Path ---")
print("Module Path Target:", module_path)
import os
print("Is folder exists?:", os.path.exists(module_path))
print("Files in folder:", os.listdir(module_path) if os.path.exists(module_path) else "Folder not found")
print("------------------")





# 3. import and run UI
try:
	from function.pipeline.file_manager.blenderFileManager import run_ui_blender
	import importlib
	importlib.reload(run_ui_blender)
	run_ui_blender.run_file_manager()
	print("FileManager UI launched successfully!")
except Exception as e:
	import traceback
	print("Error launching FileManager:")
	traceback.print_exc()
