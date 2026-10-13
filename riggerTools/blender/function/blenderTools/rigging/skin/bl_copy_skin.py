# -= bl_copy_skin.py =-
# Blender Skin Weight Transfer Tool
# Copy skin weights from source mesh to selected vertices
# Inspired by ml_copySkin.py for Maya by Morgan Loomis
#
# Installation:
# 1. Open Blender
# 2. Go to Edit > Preferences > Add-ons > Install
# 3. Select this file
# 4. Enable "Rigging: Copy Skin Weights"
#
# Usage:
# 1. Select source mesh (with armature modifier)
# 2. Select destination mesh
# 3. In Edit mode, select vertices to transfer weights to
# 4. Open 3D View > Sidebar (N) > Rigging tab
# 5. Click "Set Source Mesh" button
# 6. Click "Copy Skin Weights" button

bl_info = {
    "name": "Copy Skin Weights",
    "author": "Clude Sonnet 4.5",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Rigging Tab",
    "description": "Copy skin weights from source mesh to selected vertices",
    "category": "CopySkin",
}

import bpy
from bpy.props import StringProperty, EnumProperty, FloatProperty
from bpy.types import Operator, Panel, PropertyGroup


# ============================================
# Core Functions
# ============================================

def get_armature_modifier(obj):
    """Get the armature modifier from an object"""
    if obj and obj.type == 'MESH':
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                return mod
    return None


def get_vertex_groups(obj):
    """Get all vertex groups from an object"""
    if obj and obj.type == 'MESH':
        return [vg.name for vg in obj.vertex_groups]
    return []


def get_armature_from_object(obj):
    """Get the armature object from a mesh"""
    arm_mod = get_armature_modifier(obj)
    if arm_mod:
        return arm_mod.object
    return None


def ensure_vertex_groups(source, dest):
    """Ensure destination has all vertex groups from source"""
    source_groups = get_vertex_groups(source)
    dest_groups = get_vertex_groups(dest)
    
    for group_name in source_groups:
        if group_name not in dest_groups:
            dest.vertex_groups.new(name=group_name)


def ensure_armature_modifier(source, dest):
    """Ensure destination has armature modifier with same armature as source"""
    source_armature = get_armature_from_object(source)
    
    if not source_armature:
        return False
    
    dest_arm_mod = get_armature_modifier(dest)
    
    if not dest_arm_mod:
        # Add armature modifier
        arm_mod = dest.modifiers.new(name="Armature", type='ARMATURE')
        arm_mod.object = source_armature
    elif dest_arm_mod.object != source_armature:
        dest_arm_mod.object = source_armature
    
    return True


def copy_weights_to_vertices(source_obj, dest_obj, vertex_indices):
    """
    Copy skin weights from source object to specific vertices on destination object
    
    Args:
        source_obj: Source mesh object with weights
        dest_obj: Destination mesh object
        vertex_indices: List of vertex indices to copy weights to
    """
    if not source_obj or not dest_obj:
        return False
    
    if source_obj.type != 'MESH' or dest_obj.type != 'MESH':
        return False
    
    # Ensure destination has all vertex groups from source
    ensure_vertex_groups(source_obj, dest_obj)
    
    # Ensure destination has armature modifier
    ensure_armature_modifier(source_obj, dest_obj)
    
    # Create temporary vertex group for selected vertices
    temp_group_name = "temp_transfer_mask"
    
    # Remove existing temp group if it exists
    if temp_group_name in dest_obj.vertex_groups:
        dest_obj.vertex_groups.remove(dest_obj.vertex_groups[temp_group_name])
    
    # Create new temp group and add selected vertices
    temp_group = dest_obj.vertex_groups.new(name=temp_group_name)
    temp_group.add(vertex_indices, 1.0, 'REPLACE')
    
    # Store current selection and mode
    current_mode = bpy.context.object.mode
    selected_objects = bpy.context.selected_objects[:]
    active_object = bpy.context.active_object
    
    try:
        # Deselect all
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select source first, then destination (destination will be active)
        source_obj.select_set(True)
        dest_obj.select_set(True)
        bpy.context.view_layer.objects.active = dest_obj
        
        # Add Data Transfer modifier
        mod = dest_obj.modifiers.new(name="DataTransfer_Temp", type='DATA_TRANSFER')
        mod.object = source_obj
        mod.use_vert_data = True
        mod.data_types_verts = {'VGROUP_WEIGHTS'}
        mod.vert_mapping = 'NEAREST'
        mod.vertex_group = temp_group_name
        
        # Move modifier to first position in stack to avoid warning
        if len(dest_obj.modifiers) > 1:
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
        
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        # Clean up temp vertex group
        if temp_group_name in dest_obj.vertex_groups:
            dest_obj.vertex_groups.remove(dest_obj.vertex_groups[temp_group_name])
        
        return True
        
    except Exception as e:
        print(f"Error during weight transfer: {e}")
        # Clean up on error
        if temp_group_name in dest_obj.vertex_groups:
            dest_obj.vertex_groups.remove(dest_obj.vertex_groups[temp_group_name])
        return False
        
    finally:
        # Restore selection and mode
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = active_object
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=current_mode)


def copy_weights_to_mesh(source_obj, dest_obj):
    """
    Copy skin weights from source object to entire destination mesh
    
    Args:
        source_obj: Source mesh object with weights
        dest_obj: Destination mesh object
    """
    if not source_obj or not dest_obj:
        return False
    
    if source_obj.type != 'MESH' or dest_obj.type != 'MESH':
        return False
    
    # Ensure destination has all vertex groups from source
    ensure_vertex_groups(source_obj, dest_obj)
    
    # Ensure destination has armature modifier
    ensure_armature_modifier(source_obj, dest_obj)
    
    # Store current selection and mode
    current_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    selected_objects = bpy.context.selected_objects[:]
    active_object = bpy.context.active_object
    
    try:
        # Deselect all
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select source first, then destination (destination will be active)
        source_obj.select_set(True)
        dest_obj.select_set(True)
        bpy.context.view_layer.objects.active = dest_obj
        
        # Add Data Transfer modifier
        mod = dest_obj.modifiers.new(name="DataTransfer_Temp", type='DATA_TRANSFER')
        mod.object = source_obj
        mod.use_vert_data = True
        mod.data_types_verts = {'VGROUP_WEIGHTS'}
        mod.vert_mapping = 'NEAREST'
        
        # Move modifier to first position in stack to avoid warning
        if len(dest_obj.modifiers) > 1:
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
        
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        return True
        
    except Exception as e:
        print(f"Error during weight transfer: {e}")
        return False
        
    finally:
        # Restore selection and mode
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = active_object
        if bpy.context.object and current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=current_mode)


# ============================================
# Operators
# ============================================

class COPYSKIN_OT_set_source(Operator):
    """Set the selected mesh as source for skin weight transfer"""
    bl_idname = "copyskin.set_source"
    bl_label = "Set Source Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}
        
        if not get_armature_modifier(obj):
            self.report({'WARNING'}, "Selected mesh has no armature modifier")
        
        context.scene.copyskin_props.source_mesh = obj.name
        self.report({'INFO'}, f"Source mesh set to: {obj.name}")
        
        return {'FINISHED'}


class COPYSKIN_OT_copy_to_selection(Operator):
    """Copy skin weights from source mesh to selected vertices"""
    bl_idname = "copyskin.copy_to_selection"
    bl_label = "Copy Skin Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.copyskin_props
        source_name = props.source_mesh
        
        if not source_name or source_name not in bpy.data.objects:
            self.report({'ERROR'}, "Please set a valid source mesh first")
            return {'CANCELLED'}
        
        source_obj = bpy.data.objects[source_name]
        
        # Check if we're in edit mode with vertices selected
        if context.mode == 'EDIT_MESH':
            dest_obj = context.active_object
            
            if not dest_obj or dest_obj.type != 'MESH':
                self.report({'ERROR'}, "Active object is not a mesh")
                return {'CANCELLED'}
            
            # Get selected vertices
            bpy.ops.object.mode_set(mode='OBJECT')
            selected_verts = [v.index for v in dest_obj.data.vertices if v.select]
            bpy.ops.object.mode_set(mode='EDIT')
            
            if not selected_verts:
                self.report({'ERROR'}, "No vertices selected")
                return {'CANCELLED'}
            
            # Copy weights to selected vertices
            bpy.ops.object.mode_set(mode='OBJECT')
            success = copy_weights_to_vertices(source_obj, dest_obj, selected_verts)
            bpy.ops.object.mode_set(mode='EDIT')
            
            if success:
                self.report({'INFO'}, f"Copied weights to {len(selected_verts)} vertices")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to copy weights")
                return {'CANCELLED'}
        
        # Object mode - copy to entire mesh
        elif context.mode == 'OBJECT':
            selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
            
            if not selected_objects:
                self.report({'ERROR'}, "Please select destination mesh(es)")
                return {'CANCELLED'}
            
            success_count = 0
            for dest_obj in selected_objects:
                if dest_obj.name == source_name:
                    continue
                
                if copy_weights_to_mesh(source_obj, dest_obj):
                    success_count += 1
            
            if success_count > 0:
                self.report({'INFO'}, f"Copied weights to {success_count} mesh(es)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to copy weights")
                return {'CANCELLED'}
        
        else:
            self.report({'ERROR'}, "Please use in Object or Edit mode")
            return {'CANCELLED'}


class COPYSKIN_OT_clear_source(Operator):
    """Clear the source mesh"""
    bl_idname = "copyskin.clear_source"
    bl_label = "Clear Source"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.copyskin_props.source_mesh = ""
        self.report({'INFO'}, "Source mesh cleared")
        return {'FINISHED'}


# ============================================
# Properties
# ============================================

class CopySkinProperties(PropertyGroup):
    source_mesh: StringProperty(
        name="Source Mesh",
        description="Source mesh to copy skin weights from",
        default=""
    )


# ============================================
# UI Panel
# ============================================

class VIEW3D_PT_copy_skin_panel(Panel):
    """Copy Skin Weights Panel"""
    bl_label = "bl_copy_skin"
    bl_idname = "VIEW3D_PT_copy_skin_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.copyskin_props
        
        # Source mesh section
        box = layout.box()
        box.label(text="Source Mesh:", icon='MESH_DATA')
        
        if props.source_mesh and props.source_mesh in bpy.data.objects:
            row = box.row()
            row.label(text=props.source_mesh, icon='CHECKMARK')
            row.operator("copyskin.clear_source", text="", icon='X')
        else:
            box.label(text="(Not Set)", icon='ERROR')
        
        layout.operator("copyskin.set_source", icon='EYEDROPPER')
        
        # Copy weights section
        layout.separator()
        box = layout.box()
        box.label(text="Transfer Weights:", icon='MOD_DATA_TRANSFER')
        
        col = box.column(align=True)
        col.label(text="Edit Mode: Selected vertices")
        col.label(text="Object Mode: Entire mesh(es)")
        
        layout.operator("copyskin.copy_to_selection", icon='PASTEDOWN')
        
        # Instructions
        layout.separator()
        box = layout.box()
        box.label(text="Instructions:", icon='INFO')
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="1. Select source mesh")
        col.label(text="2. Click 'Set Source Mesh'")
        col.label(text="3. Select destination mesh")
        col.label(text="4. (Optional) Enter Edit mode")
        col.label(text="5. (Optional) Select vertices")
        col.label(text="6. Click 'Copy Skin Weights'")


# ============================================
# Registration
# ============================================

classes = (
    CopySkinProperties,
    COPYSKIN_OT_set_source,
    COPYSKIN_OT_copy_to_selection,
    COPYSKIN_OT_clear_source,
    VIEW3D_PT_copy_skin_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.copyskin_props = bpy.props.PointerProperty(type=CopySkinProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.copyskin_props


if __name__ == "__main__":
    register()
