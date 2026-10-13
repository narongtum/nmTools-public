import bpy
import json
import os

def get_script_dir():
    # 1. Try __file__ if running as a module/saved script
    try:
        if "__file__" in globals() or "__file__" in locals():
            return os.path.dirname(os.path.realpath(__file__))
    except Exception:
        pass
        
    # 2. Try Blender's active text editor filepath
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                space = area.spaces.active
                if space and space.text and space.text.filepath:
                    return os.path.dirname(os.path.abspath(space.text.filepath))
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
MAPPING_FILE = os.path.join(SCRIPT_DIR, "..", "02_game_extraction", "cni_rig_mapping.json")

# Fallback paths for finding the JSON mapping file
if not os.path.exists(MAPPING_FILE):
    # Try looking in the same directory as this script
    MAPPING_FILE = os.path.join(SCRIPT_DIR, "cni_rig_mapping.json")
    
if not os.path.exists(MAPPING_FILE) and bpy.data.is_saved:
    # Try looking in the same directory as the saved .blend file
    blend_dir = os.path.dirname(bpy.data.filepath)
    MAPPING_FILE = os.path.join(blend_dir, "cni_rig_mapping.json")

def reconstrain_game_skeleton(orig_obj, game_obj, mapping):
    """Restore Copy Transforms constraints from the game skeleton to the control rig"""
    # Ensure in pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    game_obj.select_set(True)
    bpy.context.view_layer.objects.active = game_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # Map from clean name to original name
    bone_mapping = mapping.get("bones", {})
    to_keep = {}
    existing_bones = {pb.name for pb in game_obj.pose.bones}
    for clean_name, config in bone_mapping.items():
        target_name = config.get("target")
        if clean_name in existing_bones:
            to_keep[clean_name] = target_name

    for pb in game_obj.pose.bones:
        # Clear existing constraints and custom properties
        for c in list(pb.constraints):
            pb.constraints.remove(c)
        for prop in list(pb.keys()):
            try:
                del pb[prop]
            except Exception:
                pass
            
        # Add COPY_TRANSFORMS targeting the control rig
        orig_bone_name = to_keep.get(pb.name)
        if orig_bone_name and orig_bone_name in orig_obj.pose.bones:
            con = pb.constraints.new('COPY_TRANSFORMS')
            con.target = orig_obj
            con.subtarget = orig_bone_name
            con.target_space = 'WORLD'
            con.owner_space = 'WORLD'
            
    bpy.ops.object.mode_set(mode='OBJECT')

def show_message_box(message = "", title = "CNI Tools", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def bake_and_export_all_actions(orig_name, game_name, export_dir=None):
    """Iterate through all Actions, bake them on the Game Skeleton, and export to separate FBX files"""
    # Record original selected meshes before we modify the selection state
    original_selected = list(bpy.context.selected_objects)
    selected_meshes = [obj for obj in original_selected if obj.type == 'MESH']

    orig_obj = bpy.data.objects.get(orig_name)
    game_obj = bpy.data.objects.get(game_name)
    
    if not orig_obj or not game_obj:
        msg = f"Error: Control Rig '{orig_name}' or Game Skeleton '{game_name}' not found!"
        print(msg)
        show_message_box(msg, "Rig Error", 'ERROR')
        return False
        
    if not os.path.exists(MAPPING_FILE):
        msg = f"Error: Mapping file not found at {MAPPING_FILE}"
        print(msg)
        show_message_box(msg, "File Error", 'ERROR')
        return False
        
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
        
    blend_name = "Untitled"
    if bpy.data.is_saved:
        blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]

    if not export_dir:
        # Export to the directory of the blend file
        if bpy.data.is_saved:
            export_dir = os.path.dirname(bpy.data.filepath)
        else:
            export_dir = os.path.expanduser("~") # fallback to user home directory
            
    print(f"Starting bake. Export directory: {export_dir}")
    
    # Get the active action on the control rig
    active_action = orig_obj.animation_data.action if (orig_obj.animation_data and orig_obj.animation_data.action) else None
    if not active_action:
        msg = "Error: No active Action found on the control rig!"
        print(msg)
        show_message_box(msg, "Animation Error", 'ERROR')
        return False
        
    actions = [active_action]
    
    # Store current active action of original rig to restore later
    orig_action = active_action
        
    for action in actions:
        print(f"Processing action: {action.name}")
        
        # 1. Set action on original rig
        if not orig_obj.animation_data:
            orig_obj.animation_data_create()
        orig_obj.animation_data.action = action
        
        # 2. Re-constrain game skeleton to rigify to snap to this action
        reconstrain_game_skeleton(orig_obj, game_obj, mapping)
        
        # 3. Determine frame range
        start_frame = int(action.frame_range[0])
        end_frame = int(action.frame_range[1])
        
        # 4. Select the game skeleton
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        game_obj.select_set(True)
        bpy.context.view_layer.objects.active = game_obj
        
        # 5. Bake keyframes (clearing constraints in the process)
        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            step=1,
            only_selected=False,
            visual_keying=True,
            clear_constraints=True,
            bake_types={'POSE'}
        )
        
        # Select export objects (always include game skeleton; optionally include selected meshes)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Check if the premium "Better FBX" importer/exporter add-on is available
        has_better_fbx = False
        try:
            if hasattr(bpy.ops, "better_export") and hasattr(bpy.ops.better_export, "fbx"):
                has_better_fbx = True
        except Exception:
            pass
            
        if not has_better_fbx:
            # Fallback: Temporarily rename armature to "Armature" so game engines (Unity/Unreal) automatically strip it
            old_game_name = game_obj.name
            game_obj.name = "Armature"
            
        game_obj.select_set(True)
        
        # If the user originally selected meshes, select them for export
        if selected_meshes:
            for mesh in selected_meshes:
                mesh.select_set(True)
                
        # 6. Export FBX for this Action
        fbx_name = f"{blend_name}_Anim.fbx"
        fbx_path = os.path.join(export_dir, fbx_name)
        
        if has_better_fbx:
            print("Exporting animations using Better FBX Exporter...")
            bpy.ops.better_export.fbx(
                filepath=fbx_path,
                use_selection=True,
                use_ignore_armature_node=True, # Do not export armature as a dummy node (leaves only 'root' bone at top)
                use_optimize_for_game_engine=True,
                my_max_bone_influences='4', # Limit bone influences to 4 per vertex (project requirement)
                use_animation=True,
                my_animation_type='Active'
            )
        else:
            print("Exporting animations using Blender's default FBX exporter...")
            bpy.ops.export_scene.fbx(
                filepath=fbx_path,
                use_selection=True,
                add_leaf_bones=False,
                bake_anim=True,
                bake_anim_use_all_bones=True,
                bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False,
                bake_anim_step=1.0,
                axis_forward='-Z',
                axis_up='Y'
            )
            # Restore original armature object name
            game_obj.name = old_game_name
        
    # 7. Restore original action and re-constrain
    if orig_obj.animation_data:
        orig_obj.animation_data.action = orig_action
    reconstrain_game_skeleton(orig_obj, game_obj, mapping)
    msg = "Batch bake and export completed successfully!"
    print(msg)
    show_message_box(msg, "Success", 'INFO')
    return True

if __name__ == "__main__":
    active_obj = bpy.context.active_object
    # Enforce that the active selected object is an Armature and its name ends with '_GameExport'
    if active_obj and active_obj.type == 'ARMATURE' and active_obj.name.endswith("_GameExport"):
        game_name = active_obj.name
        orig_name = active_obj.name.replace("_GameExport", "")
        bake_and_export_all_actions(orig_name, game_name)
    else:
        msg = "Error: Please select the Game Skeleton armature (ends with '_GameExport')!"
        print(msg)
        show_message_box(msg, "Selection Error", 'ERROR')
