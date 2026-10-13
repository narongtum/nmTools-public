"""
Vertex Weight Copy-Paste Utility for Blender
===========================================
A robust utility script to copy vertex weights from a source vertex and paste 
them to all selected target vertices. Works consistently in both Edit Mode and 
Weight Paint Mode by utilizing a temporary mode-toggling pipeline.

Features:
- Preserves exact weight mappings by copying by vertex group name (allows cross-mesh pasting).
- Completely overwrites target vertex weights cleanly (removes old weights to prevent skewing).
- Redraws the 3D viewport instantly to refresh weight colors.

Usage:
1. Open this script in Blender's Text Editor and click the "Run Script" (Play) button.
2. In the 3D Viewport, press 'N' to open the Sidebar and go to the "Tool" tab.
3. Locate the "Weight Copy-Paste" panel.
4. If in Weight Paint Mode, ensure Vertex Selection Masking is enabled.
5. Select a source vertex and press 'Ctrl + Shift + C' (or click "Copy Selected Vertex Weight").
6. Select target vertices and press 'Ctrl + Shift + V' (or click "Paste Weight to Selected").
"""

import bpy
import bmesh

# Global clipboard
_weights_clipboard = {}

class OBJECT_OT_copy_vertex_weights(bpy.types.Operator):
    bl_idname = "object.copy_vertex_weights"
    bl_label = "Copy Vertex Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'
        
    def execute(self, context):
        global _weights_clipboard
        obj = context.active_object
        original_mode = obj.mode
        
        if original_mode not in ['EDIT', 'PAINT_WEIGHT', 'WEIGHT_PAINT']:
            self.report({'WARNING'}, "Must be in Edit Mode or Weight Paint Mode with selection mask active.")
            return {'CANCELLED'}
            
        if original_mode in ['PAINT_WEIGHT', 'WEIGHT_PAINT']:
            if not (obj.data.use_paint_mask_vertex or obj.data.use_paint_mask):
                self.report({'WARNING'}, "Please enable Vertex Selection Masking in Weight Paint mode.")
                return {'CANCELLED'}
                
        target_mode = 'WEIGHT_PAINT' if original_mode in ['PAINT_WEIGHT', 'WEIGHT_PAINT'] else original_mode
        
        # Switch to Edit mode to get active vertex from bmesh history
        if original_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
            
        bm = bmesh.from_edit_mesh(obj.data)
        active_index = -1
        
        active_vert = bm.select_history.active
        if active_vert and isinstance(active_vert, bmesh.types.BMVert):
            active_index = active_vert.index
            
        if active_index == -1:
            for v in bm.verts:
                if v.select:
                    active_index = v.index
                    break
                    
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if active_index == -1 or active_index >= len(obj.data.vertices):
            bpy.ops.object.mode_set(mode=target_mode)
            self.report({'WARNING'}, "No vertex selected to copy weights from.")
            return {'CANCELLED'}
            
        # Copy weights (only copy groups with non-zero weight for clean transfer)
        v = obj.data.vertices[active_index]
        _weights_clipboard = {}
        for g in v.groups:
            if g.group < len(obj.vertex_groups):
                vg = obj.vertex_groups[g.group]
                _weights_clipboard[vg.name] = g.weight
                
        bpy.ops.object.mode_set(mode=target_mode)
        
        self.report({'INFO'}, f"Copied weights from vertex {active_index}: {len(_weights_clipboard)} groups.")
        return {'FINISHED'}

class OBJECT_OT_paste_vertex_weights(bpy.types.Operator):
    bl_idname = "object.paste_vertex_weights"
    bl_label = "Paste Vertex Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'
        
    def execute(self, context):
        global _weights_clipboard
        if not _weights_clipboard:
            self.report({'WARNING'}, "Clipboard is empty. Copy weights first.")
            return {'CANCELLED'}
            
        obj = context.active_object
        original_mode = obj.mode
        
        if original_mode not in ['EDIT', 'PAINT_WEIGHT', 'WEIGHT_PAINT']:
            self.report({'WARNING'}, "Must be in Edit Mode or Weight Paint Mode with selection mask active.")
            return {'CANCELLED'}
            
        if original_mode in ['PAINT_WEIGHT', 'WEIGHT_PAINT']:
            if not (obj.data.use_paint_mask_vertex or obj.data.use_paint_mask):
                self.report({'WARNING'}, "Please enable Vertex Selection Masking in Weight Paint mode.")
                return {'CANCELLED'}
                
        target_mode = 'WEIGHT_PAINT' if original_mode in ['PAINT_WEIGHT', 'WEIGHT_PAINT'] else original_mode
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        selected_indices = [v.index for v in obj.data.vertices if v.select]
        
        if not selected_indices:
            bpy.ops.object.mode_set(mode=target_mode)
            self.report({'WARNING'}, "No vertices selected to paste weights to.")
            return {'CANCELLED'}
            
        # Ensure target vertex groups exist
        vg_map = {}
        for name in _weights_clipboard.keys():
            vg = obj.vertex_groups.get(name)
            if not vg:
                vg = obj.vertex_groups.new(name=name)
            vg_map[name] = vg
            
        # Paste weights
        for v_idx in selected_indices:
            # Remove vertex from all current groups (clean overwrite)
            for vg in obj.vertex_groups:
                vg.remove([v_idx])
            # Add to copied groups with weights
            for name, weight in _weights_clipboard.items():
                vg_map[name].add([v_idx], weight, 'REPLACE')
                
        bpy.ops.object.mode_set(mode=target_mode)
        
        # Redraw viewport to refresh weight colors
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
                
        self.report({'INFO'}, f"Pasted weights to {len(selected_indices)} vertices.")
        return {'FINISHED'}



class VIEW3D_PT_weight_copy_paste(bpy.types.Panel):
    bl_label = "copy_paste_weights"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.copy_vertex_weights", text="Copy Selected Vertex Weight", icon='COPYDOWN')
        col.operator("object.paste_vertex_weights", text="Paste Weight to Selected", icon='PASTEDOWN')
        
        global _weights_clipboard
        if _weights_clipboard:
            box = layout.box()
            box.label(text="Clipboard Contents:")
            for name, weight in _weights_clipboard.items():
                row = box.row()
                row.label(text=name)
                row.label(text=f"{weight:.4f}")
        else:
            layout.label(text="Clipboard is empty.")

classes = (
    OBJECT_OT_copy_vertex_weights,
    OBJECT_OT_paste_vertex_weights,
    VIEW3D_PT_weight_copy_paste,
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Register Shortcuts
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        
        # Copy: Ctrl + Shift + C
        kmi_copy = km.keymap_items.new(
            OBJECT_OT_copy_vertex_weights.bl_idname, 
            type='C', 
            value='PRESS', 
            ctrl=True, 
            shift=True
        )
        addon_keymaps.append((km, kmi_copy))
        
        # Paste: Ctrl + Shift + V
        kmi_paste = km.keymap_items.new(
            OBJECT_OT_paste_vertex_weights.bl_idname, 
            type='V', 
            value='PRESS', 
            ctrl=True, 
            shift=True
        )
        addon_keymaps.append((km, kmi_paste))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    # Unregister Shortcuts
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
