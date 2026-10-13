import bpy
import json
import os

def get_script_dir():
    # 1. Try __file__ if running as a module/saved script
    try:
        if "__file__" in globals() or "__file__" in locals():
            path = os.path.dirname(os.path.realpath(__file__))
            if ".blend" in path:
                path = path.split(".blend")[0]
                path = os.path.dirname(path)
            return path
    except Exception:
        pass
        
    # 2. Try Blender's active text editor filepath
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                space = area.spaces.active
                if space and space.text and space.text.filepath:
                    path = os.path.abspath(space.text.filepath)
                    if ".blend" in path:
                        # Extract the folder containing the .blend file
                        blend_path = path.split(".blend")[0] + ".blend"
                        return os.path.dirname(blend_path)
                    return os.path.dirname(path)
    except Exception:
        pass
        
    # 3. Try blend file directory
    try:
        if bpy.data.is_saved:
            return os.path.dirname(bpy.data.filepath)
    except Exception:
        pass
        
    # 4. Fallback to current working directory
    return os.getcwd()

SCRIPT_DIR = get_script_dir()
MAPPING_FILE = os.path.join(SCRIPT_DIR, "cni_rig_mapping.json")

# Fallback: check if the JSON is in the blend file directory if not found in script directory
if not os.path.exists(MAPPING_FILE) and bpy.data.is_saved:
    blend_dir = os.path.dirname(bpy.data.filepath)
    MAPPING_FILE = os.path.join(blend_dir, "cni_rig_mapping.json")

def show_message_box(message = "", title = "CNI Tools", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def extract_game_skeleton(orig_obj):
    if not orig_obj or orig_obj.type != 'ARMATURE':
        msg = "Error: Please select the generated Rigify Armature!"
        print(msg)
        show_message_box(msg, "Selection Error", 'ERROR')
        return False

    # 1. Load the JSON mapping file
    if not os.path.exists(MAPPING_FILE):
        msg = f"Error: Mapping file not found at {MAPPING_FILE}"
        print(msg)
        show_message_box(msg, "File Error", 'ERROR')
        return False
        
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)
    
    bone_mapping = mapping_data.get("bones", {})

    # Ensure only the active armature is selected in Object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    orig_obj.select_set(True)
    bpy.context.view_layer.objects.active = orig_obj

    # 2. Duplicate the armature
    bpy.ops.object.duplicate()
    game_obj = bpy.context.active_object
    game_obj.name = f"{orig_obj.name}_GameExport"

    # Clean animation data, drivers, and custom properties on the duplicate to remove Outliner clutter
    if game_obj.animation_data:
        game_obj.animation_data_clear()
    if game_obj.data.animation_data:
        game_obj.data.animation_data_clear()
    for prop in list(game_obj.keys()):
        try:
            del game_obj[prop]
        except Exception:
            pass
    for prop in list(game_obj.data.keys()):
        try:
            del game_obj.data[prop]
        except Exception:
            pass

    # Go to Edit Mode to prune and rename bones
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = game_obj.data.edit_bones

    # Identify which bones from the JSON actually exist in the rig
    to_keep = {}  # Map: clean_name -> original_target_name
    to_delete = []

    # Map current bones in duplicate to check existence
    existing_bones = {eb.name for eb in ebs}

    for clean_name, config in bone_mapping.items():
        target_name = config.get("target")
        if target_name in existing_bones:
            to_keep[clean_name] = target_name
        else:
            # Skip missing bones (so we can have all custom bones in one master JSON)
            print(f"Warning: Target bone '{target_name}' not found on rig, skipping.")

    if not to_keep:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.delete()  # Clean up duplicate
        msg = "Error: No matching bones found based on the JSON mapping!"
        print(msg)
        show_message_box(msg, "Mapping Error", 'ERROR')
        return False

    # Identify which bones to delete (any bone not mapped to a clean name in to_keep)
    kept_target_names = set(to_keep.values())
    for eb in ebs:
        if eb.name not in kept_target_names:
            to_delete.append(eb.name)

    # Delete unmapped bones
    for bone_name in to_delete:
        eb = ebs.get(bone_name)
        if eb:
            ebs.remove(eb)

    # Rename the remaining bones to their clean names defined in the JSON
    for clean_name, orig_name in to_keep.items():
        eb = ebs.get(orig_name)
        if eb:
            eb.name = clean_name

    # Re-parent the remaining bones according to the parent property in the JSON
    for clean_name, config in bone_mapping.items():
        if clean_name in ebs:
            parent_name = config.get("parent")
            eb = ebs[clean_name]
            
            # Check if parent is defined and exists in the cleaned bones list
            if parent_name and parent_name in ebs:
                eb.parent = ebs[parent_name]
            else:
                eb.parent = None
                # Parent to root if root exists and this is not root itself
                if "root" in ebs and clean_name != "root":
                    eb.parent = ebs["root"]

    # 3. Consolidate bones into a single "Deform" collection (for Blender 4.0+) or Layer 0 (for Blender 3.x)
    if hasattr(game_obj.data, "collections"):
        deform_col = game_obj.data.collections.get("Deform")
        if not deform_col:
            deform_col = game_obj.data.collections.new("Deform")
        for eb in ebs:
            deform_col.assign(eb)
        for col in list(game_obj.data.collections):
            if col.name != "Deform":
                game_obj.data.collections.remove(col)
    else:
        for eb in ebs:
            eb.layers = [True] + [False] * 31

    # Go to Pose Mode to set up constraints
    bpy.ops.object.mode_set(mode='POSE')
    
    # Remove any existing constraints and custom properties on the duplicate
    for pb in game_obj.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
        for prop in list(pb.keys()):
            del pb[prop]
        
        # Add Copy Transforms targeting the original rig's DEF-bone
        orig_bone_name = to_keep.get(pb.name)
        if orig_bone_name:
            con = pb.constraints.new('COPY_TRANSFORMS')
            con.target = orig_obj
            con.subtarget = orig_bone_name
            con.target_space = 'WORLD'
            con.owner_space = 'WORLD'

    # Return to Object mode and select the export rig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    game_obj.select_set(True)
    bpy.context.view_layer.objects.active = game_obj

    msg = f"Success: Created clean Game Skeleton: {game_obj.name}"
    print(msg)
    show_message_box(msg, "Success", 'INFO')
    return True

if __name__ == "__main__":
    import traceback
    try:
        active_obj = bpy.context.active_object
        extract_game_skeleton(active_obj)
    except Exception as e:
        tb_str = traceback.format_exc()
        print(tb_str)
        # Write traceback to a file in the script directory or temp dir
        try:
            error_file = os.path.join(SCRIPT_DIR, "blender_error.txt")
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(tb_str)
            show_message_box(f"Script crashed. Traceback saved to {error_file}", "Script Error", 'ERROR')
        except Exception as e2:
            print(f"Could not write traceback file: {e2}")
