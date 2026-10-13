import bpy
import os

class FixedTexturePathProperties(bpy.types.PropertyGroup):
    texture_dir: bpy.props.StringProperty(
        name="Texture Directory",
        description="Path to the directory containing the textures",
        default="",
        subtype='DIR_PATH'
    )

class OBJECT_OT_fix_texture_paths(bpy.types.Operator):
    bl_idname = "object.fix_texture_paths"
    bl_label = "Fix Texture Paths"
    bl_description = "Repath all image textures in the scene to point to the selected directory"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.fixed_texture_path_props
        
        # Resolve target directory path
        new_dir = props.texture_dir
        if not new_dir:
            self.report({'ERROR'}, "Please select a valid directory first.")
            return {'CANCELLED'}
            
        new_dir = bpy.path.abspath(new_dir)
        if not os.path.isdir(new_dir):
            self.report({'ERROR'}, f"Directory not found: {new_dir}")
            return {'CANCELLED'}
            
        updated_count = 0
        found_count = 0
        missing_count = 0
        
        # Filter only valid external file images
        file_images = [img for img in bpy.data.images if img.source == 'FILE' and os.path.basename(img.filepath)]
        
        if not file_images:
            msg = "No texture files found in the current scene to update."
            self.report({'WARNING'}, msg)
            print(f"[Texture Path Fixer] {msg}")
            return {'CANCELLED'}
        
        for img in file_images:
            filename = os.path.basename(img.filepath)
            
            # Build target filepath
            new_filepath = os.path.join(new_dir, filename)
            
            # Set path regardless of physical file existence
            if bpy.data.is_saved:
                img.filepath = bpy.path.relpath(new_filepath)
            else:
                img.filepath = new_filepath
                
            # Track physical existence for user feedback
            if os.path.exists(new_filepath):
                found_count += 1
            else:
                missing_count += 1
                
            try:
                img.reload()
                updated_count += 1
            except Exception as e:
                # Reload might fail if file doesn't exist physically yet
                pass
                
        msg = f"Completed! Updated {updated_count} texture path(s) to target directory."
        if found_count > 0 or missing_count > 0:
            msg += f" ({found_count} found on disk, {missing_count} missing)"
            
        self.report({'INFO'}, msg)
        print(f"[Texture Path Fixer] {msg}")
        return {'FINISHED'}

class VIEW3D_PT_fixed_texture_path_panel(bpy.types.Panel):
    bl_label = "fixed_texture_path"
    bl_idname = "VIEW3D_PT_fixed_texture_path_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.fixed_texture_path_props
        
        row = layout.row(align=True)
        # Using row.prop with align=True creates a contiguous text box and button.
        # We specify text="path" as in the user's sketch.
        row.prop(props, "texture_dir", text="path")
        row.operator("object.fix_texture_paths", text="set")

classes = (
    FixedTexturePathProperties,
    OBJECT_OT_fix_texture_paths,
    VIEW3D_PT_fixed_texture_path_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fixed_texture_path_props = bpy.props.PointerProperty(type=FixedTexturePathProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.fixed_texture_path_props
