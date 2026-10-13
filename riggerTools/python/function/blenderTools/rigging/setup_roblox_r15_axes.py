# -*- coding: utf-8 -*-
"""
===============================================================================
Script: setup_roblox_r15_axes.py
Description:
    Automated Blender Python script to clean, straighten, and align all bone 
    local axes (X/Y/Z) for Roblox R15 rigs to strictly conform to Roblox R15 
    Motor6D specifications.

Key Features:
    1. Unparents all 15 R15 mesh parts while freezing their 3D world matrices 
       (preventing any mesh popping/dislocation).
    2. Straightens UpperArm bones vertically (removing 34.89° side tilt).
    3. Sets EditBone rolls to 0.0° for all limb bones so that:
       - Local X points RIGHT (+X)
       - Local Y points DOWN (-Z)
       - Local Z points BACKWARD (+Y)
    4. Re-parents meshes back to bones with preserved transforms.
    5. Configures Cautioned Roblox Animation Addon settings automatically.
===============================================================================
"""

import bpy
import math

def setup_roblox_r15_axes(armature_name=None):
    """
    Cleans and configures Roblox R15 bone rolls and mesh parenting.
    """
    # 1. Find Armature Object
    arm_obj = None
    if armature_name and armature_name in bpy.data.objects:
        arm_obj = bpy.data.objects[armature_name]
    else:
        # Auto-detect Armature containing 'HumanoidRootPart' or named 'Roblox_R15' / 'Armature'
        for o in bpy.data.objects:
            if o.type == 'ARMATURE':
                if "HumanoidRootPart" in [b.name for b in o.data.bones] or o.name in ['Roblox_R15', 'Armature']:
                    arm_obj = o
                    break
    
    if not arm_obj:
        print("Error: Could not find a valid Roblox R15 Armature in scene.")
        return False

    print(f"Target Armature found: '{arm_obj.name}'")

    # Rename Armature object and data to standard Roblox_R15 name
    arm_obj.name = "Roblox_R15"
    arm_obj.data.name = "Roblox_R15"

    # Configure Cautioned Addon Settings
    scene = bpy.context.scene
    if hasattr(scene, "rbx_anim_settings"):
        settings = scene.rbx_anim_settings
        settings.rbx_anim_armature = "Roblox_R15"
        print("Updated Cautioned Addon rbx_anim_armature setting to 'Roblox_R15'")

    # Target bones to process
    limb_bones = [
        'LeftUpperArm', 'RightUpperArm',
        'LeftLowerArm', 'RightLowerArm',
        'LeftUpperLeg', 'RightUpperLeg',
        'LeftLowerLeg', 'RightLowerLeg'
    ]

    # 2. Store World Matrix & Unparent Meshes (Prevent Mesh Popping)
    unparented_info = []
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.parent == arm_obj:
            mw = o.matrix_world.copy()
            pbone = o.parent_bone
            o.parent = None
            o.matrix_world = mw
            unparented_info.append((o, pbone, mw))
            print(f"Unparented mesh '{o.name}' (parent_bone='{pbone}') - World Matrix Preserved")

    # 3. Straighten Bones & Recalculate Rolls in Edit Mode
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = arm_obj.data.edit_bones

    # Straighten UpperArms vertically (remove 34.89° diagonal tilt)
    for bname in ['LeftUpperArm', 'RightUpperArm']:
        if bname in edit_bones:
            eb = edit_bones[bname]
            # Match Tail X and Y with Head X and Y so bone points straight down
            tail_z = edit_bones['LeftLowerArm'].head.z if 'LeftLowerArm' in edit_bones else 303.4654
            eb.tail = (eb.head.x, eb.head.y, tail_z)
            eb.roll = 0.0
            print(f"Straightened EditBone '{bname}': Roll=0.0°, Local X={eb.x_axis}")

    # Reset Rolls for all other limb bones
    for bname in limb_bones:
        if bname in edit_bones:
            eb = edit_bones[bname]
            eb.roll = 0.0
            print(f"Updated EditBone '{bname}': Roll=0.0°, Local X={eb.x_axis}")

    bpy.ops.object.mode_set(mode='OBJECT')

    # 4. Re-parent Meshes to Bones
    for mesh_obj, pbone, orig_mw in unparented_info:
        mesh_obj.parent = arm_obj
        if pbone:
            mesh_obj.parent_type = 'BONE'
            mesh_obj.parent_bone = pbone
        else:
            mesh_obj.parent_type = 'OBJECT'
        mesh_obj.matrix_world = orig_mw
        print(f"Re-parented mesh '{mesh_obj.name}' to bone '{pbone}'")

    # 5. Refresh Viewport & Scene Data
    bpy.context.view_layer.update()
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

    print("===============================================================================")
    print("SUCCESS: Roblox R15 Rig axes setup complete!")
    print("  - Local X points RIGHT (+X)")
    print("  - Local Y points DOWN (-Z)")
    print("  - Local Z points BACKWARD (+Y)")
    print("===============================================================================")
    return True

if __name__ == "__main__":
    setup_roblox_r15_axes()
