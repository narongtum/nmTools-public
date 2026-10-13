import bpy
import importlib

MENU_LABEL = "JJMenu"

# 1. Operator for running the File Manager
class WM_OT_file_manager(bpy.types.Operator):
    bl_idname = "wm.file_manager"
    bl_label = "File Manager"
    bl_description = "Open the File Manager UI"

    def execute(self, context):
        try:
            # Import using the appended path structure
            from function.pipeline.file_manager.blender import run_ui_blender
            importlib.reload(run_ui_blender)
            run_ui_blender.run_file_manager()
            self.report({'INFO'}, "File Manager launched successfully.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to run File Manager: {e}")
            import traceback
            traceback.print_exc()
        return {'FINISHED'}

# 2. Operator for scaling selected controller shape (ARP)
class WM_OT_arp_scale_controller(bpy.types.Operator):
    bl_idname = "wm.arp_scale_controller"
    bl_label = "Scale Selected Controller"
    bl_description = "Scale the custom shape size of the selected bones in Pose Mode"
    bl_options = {'REGISTER', 'UNDO'}

    scale_factor: bpy.props.FloatProperty(
        name="Scale Factor",
        description="Multiply custom shape scale by this factor",
        default=1.1,
        min=0.01,
        max=100.0
    )

    def execute(self, context):
        if context.mode != 'POSE':
            self.report({'WARNING'}, "Please switch to Pose Mode first.")
            return {'CANCELLED'}
            
        selected_bones = context.selected_pose_bones
        if not selected_bones:
            self.report({'WARNING'}, "No bones selected. Please select pose bones.")
            return {'CANCELLED'}

        scaled_count = 0
        for bone in selected_bones:
            if bone.custom_shape:
                bone.custom_shape_scale_xyz[0] *= self.scale_factor
                bone.custom_shape_scale_xyz[1] *= self.scale_factor
                bone.custom_shape_scale_xyz[2] *= self.scale_factor
                scaled_count += 1

        if scaled_count == 0:
            self.report({'WARNING'}, "None of the selected bones have custom shapes.")
        else:
            self.report({'INFO'}, f"Scaled {scaled_count} bone shape(s) by {self.scale_factor:.2f}")
            
        return {'FINISHED'}

# 3. Sub-menu ARP
class TOPBAR_MT_arp_menu(bpy.types.Menu):
    bl_label = "ARP"
    bl_idname = "TOPBAR_MT_arp_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.arp_scale_controller", text="Scale Selected Controller", icon='FULLSCREEN_ENTER')

# 4. Sub-menu Rigging
class TOPBAR_MT_rigging_menu(bpy.types.Menu):
    bl_label = "Rigging"
    bl_idname = "TOPBAR_MT_rigging_menu"

    def draw(self, context):
        layout = self.layout
        layout.menu("TOPBAR_MT_arp_menu", text="ARP", icon='ARMATURE_DATA')

# 4.5 Sidebar Main Panel (N-panel)
class VIEW3D_PT_jjtools_main(bpy.types.Panel):
    bl_label = "JJMenu"
    bl_idname = "VIEW3D_PT_jjtools_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "JJMenu"

    def draw(self, context):
        pass

# 5. Main Menu Structure (nmMenu_g)
class TOPBAR_MT_nm_menu(bpy.types.Menu):
    bl_label = MENU_LABEL
    bl_idname = "JJMENU_MT_main"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.file_manager", text="File Manager", icon='FILE_NEW')
        layout.separator()
        layout.menu("TOPBAR_MT_rigging_menu", text="Rigging", icon='POSE_HLT')

# 6. Callback function to draw main menu on topbar
def draw_main_menu(self, context):
    self.layout.menu(TOPBAR_MT_nm_menu.bl_idname)

classes = (
    VIEW3D_PT_jjtools_main,
    WM_OT_file_manager,
    WM_OT_arp_scale_controller,
    TOPBAR_MT_arp_menu,
    TOPBAR_MT_rigging_menu,
    TOPBAR_MT_nm_menu,
)

def register():
    # Clean up any leftover drawing callbacks from previous test runs
    old_funcs = ["draw_menu", "draw_topbar_menu", "draw_main_menu"]
    
    # 1. Clean Topbar
    if hasattr(bpy.types.TOPBAR_MT_editor_menus, "_draw_funcs"):
        for func in list(bpy.types.TOPBAR_MT_editor_menus._draw_funcs):
            if getattr(func, "__name__", "") in old_funcs:
                try:
                    bpy.types.TOPBAR_MT_editor_menus.remove(func)
                except Exception as e:
                    print(f"Error removing topbar callback: {e}")

    # 2. Clean 3D Viewport Header (from early tests)
    if hasattr(bpy.types.VIEW3D_MT_editor_menus, "_draw_funcs"):
        for func in list(bpy.types.VIEW3D_MT_editor_menus._draw_funcs):
            if getattr(func, "__name__", "") in old_funcs:
                try:
                    bpy.types.VIEW3D_MT_editor_menus.remove(func)
                except Exception as e:
                    print(f"Error removing view3d callback: {e}")

    # Unregister classes if they exist to prevent errors
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Append to topbar main menu (prevent duplicates)
    already_appended = False
    if hasattr(bpy.types.TOPBAR_MT_editor_menus, "_draw_funcs"):
        for func in bpy.types.TOPBAR_MT_editor_menus._draw_funcs:
            if getattr(func, "__name__", "") in old_funcs:
                already_appended = True
                break

    if not already_appended:
        bpy.types.TOPBAR_MT_editor_menus.append(draw_main_menu)

def unregister():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

    # Clean drawing callbacks during unregister
    old_funcs = ["draw_menu", "draw_topbar_menu", "draw_main_menu"]
    
    if hasattr(bpy.types.TOPBAR_MT_editor_menus, "_draw_funcs"):
        for func in list(bpy.types.TOPBAR_MT_editor_menus._draw_funcs):
            if getattr(func, "__name__", "") in old_funcs:
                try:
                    bpy.types.TOPBAR_MT_editor_menus.remove(func)
                except Exception:
                    pass

if __name__ == "__main__":
    register()
