import bpy

class OBJECT_OT_limit_and_normalize_weights(bpy.types.Operator):
    """Limit weights to maximum influences and normalize all (unlock active)"""
    bl_idname = "object.limit_and_normalize_weights"
    bl_label = "Limit and Normalize Weights"
    bl_description = "Limit vertex weights to max influences and normalize all (unlock active)"
    bl_options = {'REGISTER', 'UNDO'}
    
    limit: bpy.props.IntProperty(
        name="Max Influences",
        description="Maximum number of bone weights allowed per vertex",
        default=4,
        min=1,
        max=32
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'
        
    def execute(self, context):
        obj = context.active_object
        original_mode = obj.mode
        
        try:
            # Switch to Object Mode to safely manipulate vertex weights in Python
            if original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # 1. Prune, Normalize, and Quantize (8-bit, 255 steps) in Python using Largest Remainder Method
            for v in obj.data.vertices:
                influences = []
                for g in v.groups:
                    w = g.weight
                    if w > 0.00001:
                        influences.append((g.group, w))
                        
                if not influences:
                    continue
                    
                # Prune to max influences (sort by weight descending)
                influences.sort(key=lambda x: x[1], reverse=True)
                if len(influences) > self.limit:
                    influences = influences[:self.limit]
                    
                # Normalize
                weights = [inf[1] for inf in influences]
                total_w = sum(weights)
                if total_w <= 0.00001:
                    continue
                weights = [w / total_w for w in weights]
                
                # Quantize to 8-bit precision (255 steps)
                scaled = [w * 255.0 for w in weights]
                floored = [int(s) for s in scaled]
                remainders = [(i, s - floored[i]) for i, s in enumerate(scaled)]
                
                current_sum = sum(floored)
                diff = 255 - current_sum
                
                remainders.sort(key=lambda x: x[1], reverse=True)
                for k in range(diff):
                    idx = remainders[k][0]
                    floored[idx] += 1
                
                # Clear all vertex weights for non-allowed groups
                allowed_groups = {inf[0] for inf in influences}
                for g in list(v.groups):
                    if g.group not in allowed_groups:
                        obj.vertex_groups[g.group].remove([v.index])
                
                # Write back quantized and normalized weights
                for idx, inf in enumerate(influences):
                    g_idx = inf[0]
                    q_w = floored[idx] / 255.0
                    obj.vertex_groups[g_idx].add([v.index], q_w, 'REPLACE')
            
            # 2. Clean up unused vertex groups (groups with 0 use count)
            vg_use_count = {vg.index: 0 for vg in obj.vertex_groups}
            for v in obj.data.vertices:
                for g in v.groups:
                    if g.weight > 0.00001:
                        if g.group in vg_use_count:
                            vg_use_count[g.group] += 1
            
            unused_vgs = [vg for vg in obj.vertex_groups if vg_use_count[vg.index] == 0]
            deleted_count = len(unused_vgs)
            
            for vg in unused_vgs:
                obj.vertex_groups.remove(vg)
            
            # Restore original mode
            if original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=original_mode)
            
            msg = f"Weights limited to {self.limit} influences, normalized, and quantized (8-bit)."
            if deleted_count > 0:
                msg += f" Removed {deleted_count} unused vertex groups."
            else:
                msg += " No unused vertex groups found."
                
            self.report({'INFO'}, msg)
            return {'FINISHED'}
            
        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass
            self.report({'ERROR'}, f"Failed to limit, normalize, and quantize: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_limit_normalize_panel(bpy.types.Panel):
    bl_label = "limit_and_normalize"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        # Single button to Prune (Limit 4) & Normalize & Quantize
        op = col.operator("object.limit_and_normalize_weights", text="Prune (Limit 4) & Quantize", icon='PROPERTIES')
        op.limit = 4

def register():
    bpy.utils.register_class(OBJECT_OT_limit_and_normalize_weights)
    bpy.utils.register_class(VIEW3D_PT_limit_normalize_panel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_limit_and_normalize_weights)
    bpy.utils.unregister_class(VIEW3D_PT_limit_normalize_panel)

if __name__ == "__main__":
    register()
