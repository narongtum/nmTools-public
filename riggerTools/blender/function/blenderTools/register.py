import importlib
from function.pipeline.file_manager.blenderMenu import blenderMenu5
from function.blenderTools.rigging import skin
from function.blenderTools.asset import fixed_texture_path

# Centralized list of all modules and components to register on Blender startup.
# Edit this list in the repository when adding new tools.
REGISTRY = [
    blenderMenu5,
    skin,
    fixed_texture_path
]

def register():
    for item in REGISTRY:
        try:
            # Dynamically reload the module to ensure code changes are loaded
            if hasattr(item, "__name__"):
                try:
                    importlib.reload(item)
                except:
                    pass
            elif hasattr(item, "__module__"):
                try:
                    mod = importlib.import_module(item.__module__)
                    importlib.reload(mod)
                except:
                    pass
            
            if hasattr(item, "register"):
                item.register()
        except Exception as e:
            print(f"Failed to register {item}: {str(e)}")

def unregister():
    for item in reversed(REGISTRY):
        try:
            if hasattr(item, "unregister"):
                item.unregister()
        except Exception as e:
            print(f"Failed to unregister {item}: {str(e)}")
