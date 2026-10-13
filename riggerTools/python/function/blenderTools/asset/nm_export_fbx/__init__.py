bl_info = {
    "name": "NM FBX Exporter",
    "author": "Noman & Assistant",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "File > Export > NM FBX (.fbx)",
    "description": "Standalone stable FBX Exporter matching Auto-Rig Pro's export logic",
    "category": "Import-Export",
}

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty,
)
from bpy_extras.io_utils import (
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
)

@orientation_helper(axis_forward='-Z', axis_up='Y')
class NM_OT_export_fbx(bpy.types.Operator, ExportHelper):
    """Write an FBX file using the NM stable exporter"""
    bl_idname = "nm_export_scene.fbx"
    bl_label = "Export NM FBX"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".fbx"
    filter_glob: StringProperty(default="*.fbx", options={'HIDDEN'})

    ui_tab: EnumProperty(
        items=(('MAIN', "Main", "Main basic settings"),
               ('GEOMETRY', "Geometries", "Geometry-related settings"),
               ('ARMATURE', "Armatures", "Armature-related settings"),
               ('ANIMATION', "Animation", "Animation-related settings"),
               ),
        name="ui_tab",
        description="Export options categories",
    )

    use_selection: BoolProperty(
        name="Selected Objects",
        description="Export selected and visible objects only",
        default=False,
    )
    use_active_collection: BoolProperty(
        name="Active Collection",
        description="Export only objects from the active collection (and its children)",
        default=False,
    )
    global_scale: FloatProperty(
        name="Scale",
        description="Scale all data",
        min=0.001, max=1000.0,
        soft_min=0.01, soft_max=1000.0,
        default=1.0,
    )
    apply_unit_scale: BoolProperty(
        name="Apply Unit",
        description="Take into account current Blender units settings",
        default=True,
    )
    apply_scale_options: EnumProperty(
        items=(('FBX_SCALE_NONE', "All Local", "Apply custom scaling and units scaling to each object, FBX scale remains 1.0"),
               ('FBX_SCALE_UNITS', "FBX Units Scale", "Apply custom scaling to each object, units scaling to FBX scale"),
               ('FBX_SCALE_CUSTOM', "FBX Custom Scale", "Apply custom scaling to FBX scale, units scaling to each object"),
               ('FBX_SCALE_ALL', "FBX All", "Apply custom scaling and units scaling to FBX scale"),
               ),
        name="Apply Scalings",
        description="How to apply custom and units scalings",
        default='FBX_SCALE_NONE',
    )
    use_space_transform: BoolProperty(
        name="Use Space Transform",
        description="Apply global space transform to the object rotations",
        default=True,
    )
    bake_space_transform: BoolProperty(
        name="Apply Transform",
        description="Bake space transform into object data (EXPERIMENTAL)",
        default=False,
    )
    colors_type: EnumProperty(
        name="Vertex Colors",
        items=(('NONE', "None", "Do not import color attributes"),
               ('SRGB', "sRGB", "Expect file colors in sRGB color space"),
               ('LINEAR', "Linear", "Expect file colors in linear color space"),
               ),
        default='SRGB',
    )
    prioritize_active_color: BoolProperty(
        name="Prioritize Active Color",
        description="Make sure active color will be exported first",
        default=False,
    )
    object_types: EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=(('EMPTY', "Empty", ""),
               ('CAMERA', "Camera", ""),
               ('LIGHT', "Lamp", ""),
               ('ARMATURE', "Armature", ""),
               ('MESH', "Mesh", ""),
               ('OTHER', "Other", "Other geometry types"),
               ),
        default={'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'},
    )
    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects",
        default=True,
    )
    use_mesh_modifiers_render: BoolProperty(
        name="Use Modifiers Render Setting",
        description="Use render settings when applying modifiers",
        default=True,
    )
    mesh_smooth_type: EnumProperty(
        name="Smoothing",
        items=(('OFF', "Normals Only", "Export only normals"),
               ('FACE', "Face", "Write face smoothing"),
               ('EDGE', "Edge", "Write edge smoothing"),
               ),
        default='OFF',
    )
    use_subsurf: BoolProperty(
        name="Export Subdivision Surface",
        default=False,
    )
    use_mesh_edges: BoolProperty(
        name="Loose Edges",
        default=False,
    )
    use_tspace: BoolProperty(
        name="Tangent Space",
        default=False,
    )
    use_triangles: BoolProperty(
        name="Triangulate Faces",
        default=False,
    )
    use_custom_props: BoolProperty(
        name="Custom Properties",
        default=False,
    )
    add_leaf_bones: BoolProperty(
        name="Add Leaf Bones",
        default=False,
    )
    primary_bone_axis: EnumProperty(
        name="Primary Bone Axis",
        items=(('X', "X Axis", ""), ('Y', "Y Axis", ""), ('Z', "Z Axis", ""),
               ('-X', "-X Axis", ""), ('-Y', "-Y Axis", ""), ('-Z', "-Z Axis", "")),
        default='Y',
    )
    secondary_bone_axis: EnumProperty(
        name="Secondary Bone Axis",
        items=(('X', "X Axis", ""), ('Y', "Y Axis", ""), ('Z', "Z Axis", ""),
               ('-X', "-X Axis", ""), ('-Y', "-Y Axis", ""), ('-Z', "-Z Axis", "")),
        default='X',
    )
    use_armature_deform_only: BoolProperty(
        name="Only Deform Bones",
        default=False,
    )
    armature_nodetype: EnumProperty(
        name="Armature FBXNode Type",
        items=(('NULL', "Null", "'Null' FBX node, similar to Blender's Empty"),
               ('ROOT', "Root", "'Root' FBX node"),
               ('LIMBNODE', "LimbNode", "'LimbNode' FBX node"),
               ),
        default='NULL',
    )
    bake_anim: BoolProperty(
        name="Baked Animation",
        default=True,
    )
    bake_anim_use_all_bones: BoolProperty(
        name="Key All Bones",
        default=True,
    )
    bake_anim_use_nla_strips: BoolProperty(
        name="NLA Strips",
        default=True,
    )
    bake_anim_use_all_actions: BoolProperty(
        name="All Actions",
        default=True,
    )
    bake_anim_force_startend_keying: BoolProperty(
        name="Force Start/End Keying",
        default=True,
    )
    bake_anim_force_startend_keying_sk: BoolProperty(
        name="Force Start/End Keying for Shape Keys",
        default=False,
    )
    bake_anim_step: FloatProperty(
        name="Sampling Rate",
        default=1.0,
    )
    bake_anim_simplify_factor: FloatProperty(
        name="Simplify",
        default=1.0,
    )
    path_mode: path_reference_mode
    embed_textures: BoolProperty(
        name="Embed Textures",
        default=False,
    )
    batch_mode: EnumProperty(
        name="Batch Mode",
        items=(('OFF', "Off", "Active scene to file"),
               ('SCENE', "Scene", "Each scene as a file"),
               ('COLLECTION', "Collection", "Each collection as a file"),
               ('SCENE_COLLECTION', "Scene Collections", "Each collection as a file"),
               ('ACTIVE_SCENE_COLLECTION', "Active Scene Collections", "Each collection of active scene"),
               ),
        default='OFF',
    )
    use_batch_own_dir: BoolProperty(
        name="Batch Own Dir",
        default=True,
    )
    use_metadata: BoolProperty(
        name="Use Metadata",
        default=True,
        options={'HIDDEN'},
    )
    shape_keys_baked_data: StringProperty(name="sk data", default="")
    mesh_names_data: StringProperty(name="mesh names", default="")
    export_action_only: StringProperty(name="", default="")

    @property
    def check_extension(self):
        return self.batch_mode == 'OFF'

    def execute(self, context):
        from mathutils import Matrix
        if not self.filepath:
            raise Exception("filepath not set")

        global_matrix = (axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4()
                        if self.use_space_transform else Matrix())

        keywords = self.as_keywords(ignore=("check_existing",
                                            "filter_glob",
                                            "ui_tab",
                                            ))

        keywords["global_matrix"] = global_matrix

        from . import export_fbx_bin
        return export_fbx_bin.arp_save(self, context, **keywords)

def menu_func_export(self, context):
    self.layout.operator(NM_OT_export_fbx.bl_idname, text="NM FBX (.fbx)")

class VIEW3D_PT_nm_export_fbx_panel(bpy.types.Panel):
    bl_label = "NM FBX Exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(NM_OT_export_fbx.bl_idname, text="Export NM FBX", icon='EXPORT')

def register():
    bpy.utils.register_class(NM_OT_export_fbx)
    bpy.utils.register_class(VIEW3D_PT_nm_export_fbx_panel)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(NM_OT_export_fbx)
    bpy.utils.unregister_class(VIEW3D_PT_nm_export_fbx_panel)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
