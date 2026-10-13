import bpy
import bmesh

class OBJECT_OT_jj_hammer_weights(bpy.types.Operator):
    """Smooths weights of selected vertices based on surrounding unselected vertices (Maya Hammer Style)"""
    bl_idname = "object.jj_hammer_weights"
    bl_label = "Hammer Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    iterations: bpy.props.IntProperty(
        name="Iterations", 
        default=1, 
        min=1, 
        max=10,
        description="Number of times to smooth the weights"
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'
        
    def execute(self, context):
        obj = context.active_object
        original_mode = obj.mode
        
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            
            me = obj.data
            bm = bmesh.new()
            bm.from_mesh(me)
            
            deform_layer = bm.verts.layers.deform.verify()
            
            selected_verts = [v for v in bm.verts if v.select]
            if not selected_verts:
                self.report({'WARNING'}, "Please select at least one vertex!")
                bm.free()
                bpy.ops.object.mode_set(mode=original_mode)
                return {'CANCELLED'}
                
            unselected_verts = set(v for v in bm.verts if not v.select)
            
            for _ in range(self.iterations):
                new_weights_map = {}
                
                for v in selected_verts:
                    neighbors = [e.other_vert(v) for e in v.link_edges]
                    
                    valid_neighbors = [n for n in neighbors if n in unselected_verts]
                    
                    if not valid_neighbors:
                        valid_neighbors = neighbors
                        
                    if not valid_neighbors:
                        continue
                        
                    avg_weights = {}
                    for n in valid_neighbors:
                        d_dict = n[deform_layer]
                        for g_idx, weight in d_dict.items():
                            avg_weights[g_idx] = avg_weights.get(g_idx, 0.0) + weight
                            
                    num_n = len(valid_neighbors)
                    for g_idx in avg_weights:
                        avg_weights[g_idx] /= num_n
                        
                    total_weight = sum(avg_weights.values())
                    if total_weight > 0:
                        for g_idx in avg_weights:
                            avg_weights[g_idx] /= total_weight
                            
                    new_weights_map[v] = avg_weights
                    
                for v, weights in new_weights_map.items():
                    d_dict = v[deform_layer]
                    d_dict.clear()
                    for g_idx, weight in weights.items():
                        d_dict[g_idx] = weight
                        
            bm.to_mesh(me)
            bm.free()
            
            bpy.ops.object.mode_set(mode=original_mode)
            self.report({'INFO'}, f"Hammered {len(selected_verts)} vertices successfully!")
            return {'FINISHED'}
            
        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass
            self.report({'ERROR'}, f"Failed to hammer weights: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_hammer_weights_panel(bpy.types.Panel):
    bl_label = "Hammer Weights"
    bl_idname = "VIEW3D_PT_hammer_weights_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main" # Hook into the main JJmenu pipeline
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.jj_hammer_weights", text="Hammer Weights (Maya Style)", icon='MOD_SMOOTH')

def register():
    for cls in (OBJECT_OT_jj_hammer_weights, VIEW3D_PT_hammer_weights_panel):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_jj_hammer_weights)
    bpy.utils.unregister_class(VIEW3D_PT_hammer_weights_panel)

if __name__ == "__main__":
    register()
