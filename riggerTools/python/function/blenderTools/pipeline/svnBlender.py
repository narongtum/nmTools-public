import bpy
import os
import subprocess

SVN_BIN_PATH = r"C:\Program Files\TortoiseSVN\bin"

class OBJECT_OT_svn_commit(bpy.types.Operator):
    """Commit the current file to SVN using TortoiseSVN"""
    bl_idname = "object.svn_commit"
    bl_label = "SVN Commit"
    bl_description = "Commit the active Blender file to SVN using TortoiseSVN"
    bl_options = {'REGISTER'}

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "File not saved. Please save the file first.")
            return {'CANCELLED'}
            
        filepath = os.path.normpath(filepath)
        
        # Check if TortoiseSVN bin directory exists
        if not os.path.exists(SVN_BIN_PATH):
            self.report({'ERROR'}, f"TortoiseSVN not found at: {SVN_BIN_PATH}")
            return {'CANCELLED'}
            
        # Build command: cd to SVN bin path and run TortoiseProc.exe
        command_line = r'cd "{0}" && TortoiseProc.exe /command:commit /path:"{1}" /closeonend:0'.format(
            SVN_BIN_PATH, filepath
        )
        
        try:
            # Run asynchronously so it doesn't freeze Blender UI
            subprocess.Popen(command_line, shell=True)
            self.report({'INFO'}, f"Opened SVN Commit dialog for: {os.path.basename(filepath)}.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to run SVN: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_svn_commit_panel(bpy.types.Panel):
    bl_label = "SVN Commit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        # Draw SVN Commit button
        col.operator("object.svn_commit", text="SVN Commit File", icon='EXPORT')

def register():
    bpy.utils.register_class(OBJECT_OT_svn_commit)
    bpy.utils.register_class(VIEW3D_PT_svn_commit_panel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_svn_commit)
    bpy.utils.unregister_class(VIEW3D_PT_svn_commit_panel)

if __name__ == "__main__":
    register()
