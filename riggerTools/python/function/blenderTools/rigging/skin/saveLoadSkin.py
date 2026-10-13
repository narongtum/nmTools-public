import bpy
import bmesh
import numpy as np
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty

bl_info = {
    "name": "NumPy Skinweight IO",
    "description": "Fast save and load of skin weights using NumPy",
    "author": "Noman (Assisted by AI)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N-Panel > JJMenu",
    "category": "Rigging",
}


def save_skin_data(filepath, obj):
    """Save deform bone vertex weights to a numpy (.npy) file."""
    # 1. Identify deform bones via Armature modifier
    armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE'), None)
    
    deform_bone_names = []
    if armature_mod and armature_mod.object and armature_mod.object.data:
        arm_obj = armature_mod.object
        deform_bone_names = [b.name for b in arm_obj.data.bones if b.use_deform]
    
    vg_list = obj.vertex_groups
    vg_dict = {vg.index: vg.name for vg in vg_list}
    
    # Filter vg_dict to only include deform bones (if armature is bound)
    if deform_bone_names:
        valid_vg_indices = {idx: name for idx, name in vg_dict.items() if name in deform_bone_names}
    else:
        # Fallback: Export all vertex groups if no armature is found
        valid_vg_indices = vg_dict
        
    inf_Array = list(valid_vg_indices.values())
    name_to_inf_idx = {name: i for i, name in enumerate(inf_Array)}
    vg_to_inf = {idx: name_to_inf_idx[name] for idx, name in valid_vg_indices.items()}
    
    weightsNonZero = []
    infMap = []
    vertSplit = [0]
    
    count = 0
    # Use bmesh for faster iteration
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    deform_layer = bm.verts.layers.deform.active
    
    if deform_layer is not None:
        for v in bm.verts:
            dvert = v[deform_layer]
            for vg_idx, weight in dvert.items():
                if vg_idx in vg_to_inf and weight > 0.0:
                    weightsNonZero.append(weight)
                    infMap.append(vg_to_inf[vg_idx])
                    count += 1
            vertSplit.append(count)
    else:
        # Mesh has no weight data at all
        for v in bm.verts:
            vertSplit.append(count)
            
    bm.free()
    
    # Construct numpy arrays (Matching OpenMaya format style)
    data = [
        ('legend', 'weightsNonZero_Array', 'vertSplit_Array', 'infMap_Array', 'inf_Array', 'geometry', 'vtxCount'),
        np.array(weightsNonZero, dtype=np.float32),
        np.array(vertSplit, dtype=np.int32),
        np.array(infMap, dtype=np.int32),
        np.array(inf_Array, dtype=str),
        obj.name,
        len(obj.data.vertices)
    ]
    np.save(filepath, np.array(data, dtype=object))


def load_skin_data(filepath, obj):
    """Load deform bone vertex weights from a numpy (.npy) file."""
    data = np.load(filepath, allow_pickle=True)
    legend = list(data[0])
    
    def get_item(name):
        return data[legend.index(name)]
        
    vtxCount = get_item('vtxCount')
    
    # Topology Check
    if len(obj.data.vertices) != vtxCount:
        raise ValueError(f"Vertex count mismatch! Saved: {vtxCount} verts, Current Mesh: {len(obj.data.vertices)} verts. Topology must match exactly.")
        
    inf_Array = get_item('inf_Array')
    infMap_Array = get_item('infMap_Array')
    vertSplit_Array = get_item('vertSplit_Array')
    weightsNonZero_Array = get_item('weightsNonZero_Array')
    
    # Ensure required vertex groups exist on the mesh
    for inf_name in inf_Array:
        if inf_name not in obj.vertex_groups:
            obj.vertex_groups.new(name=inf_name)
            
    # Cache indices to clear only the imported groups, preserving utility groups (Masks, GeoNodes, etc.)
    vg_indices_to_clear = set(obj.vertex_groups[name].index for name in inf_Array)
    
    # Use bmesh for high-performance weight injection
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    deform_layer = bm.verts.layers.deform.verify()
    
    for i, v in enumerate(bm.verts):
        dvert = v[deform_layer]
        
        # 1. Clear existing weights for mapped deform groups on this vertex
        for k in list(dvert.keys()):
            if k in vg_indices_to_clear:
                del dvert[k]
                
        # 2. Populate new weights from numpy arrays
        start = vertSplit_Array[i]
        end = vertSplit_Array[i+1]
        
        for j in range(start, end):
            inf_idx = infMap_Array[j]
            weight = float(weightsNonZero_Array[j])
            vg_name = inf_Array[inf_idx]
            vg_idx = obj.vertex_groups[vg_name].index
            
            dvert[vg_idx] = weight
            
    bm.to_mesh(obj.data)
    bm.free()


class SKIN_OT_save_weights(bpy.types.Operator, ExportHelper):
    """Save Skin Weights to .npy format"""
    bl_idname = "skin.save_weights_numpy"
    bl_label = "Save Skin Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".npy"
    filter_glob: StringProperty(
        default="*.npy",
        options={'HIDDEN'},
        maxlen=255, 
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'
        
    def execute(self, context):
        obj = context.active_object
        try:
            save_skin_data(self.filepath, obj)
            self.report({'INFO'}, f"Skin Weights Saved: {os.path.basename(self.filepath)}")
        except Exception as e:
            self.report({'ERROR'}, f"Save Failed: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}


class SKIN_OT_load_weights(bpy.types.Operator, ImportHelper):
    """Load Skin Weights from .npy format"""
    bl_idname = "skin.load_weights_numpy"
    bl_label = "Load Skin Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".npy"
    filter_glob: StringProperty(
        default="*.npy",
        options={'HIDDEN'},
        maxlen=255, 
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'
        
    def execute(self, context):
        obj = context.active_object
        try:
            load_skin_data(self.filepath, obj)
            self.report({'INFO'}, f"Skin Weights Loaded: {os.path.basename(self.filepath)}")
        except ValueError as ve:
            # Catch topology mismatch explicitly
            self.report({'ERROR'}, str(ve))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Load Failed: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}


class SKIN_PT_jjmenu_panel(bpy.types.Panel):
    """Creates a Panel in the N-Panel JJMenu tab"""
    bl_label = "Skinweight IO (NumPy)"
    bl_idname = "SKIN_PT_jjmenu_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "JJMenu"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row(align=True)
        row.operator("skin.save_weights_numpy", text="Save Skin (.npy)", icon='EXPORT')
        row.operator("skin.load_weights_numpy", text="Load Skin (.npy)", icon='IMPORT')


classes = (
    SKIN_OT_save_weights,
    SKIN_OT_load_weights,
    SKIN_PT_jjmenu_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
