import bpy
import bmesh

# -----------------------------------------------------------------------------------
# Ported from tf_smoothSkinWeight.py by Tom Ferstl
# Original logic: blend between averaged neighbor weights and current vertex weights
# using a strength factor (replicates Maya's artisan brush blend behavior)
#
# Core formula (per influence):
#   new_weight[i] = (avg_neighbor[i] * strength) + (old_weight[i] * (1 - strength))
#
# strength = 1.0 -> 100% smooth (same as Hammer)
# strength = 0.1 -> 10% smooth blended with 90% original
# -----------------------------------------------------------------------------------

class OBJECT_OT_jj_smooth_skin_weight(bpy.types.Operator):
    """Smooth skin weights by blending vertex weights with surrounding neighbors.
Ported from tf_smoothSkinWeight.py (Tom Ferstl).
Strength 1.0 = full smooth (like Hammer), lower values blend with original."""
    bl_idname = "object.jj_smooth_skin_weight"
    bl_label = "Smooth Skin Weight"
    bl_options = {'REGISTER', 'UNDO'}

    strength: bpy.props.FloatProperty(
        name="Strength",
        description="Blend factor: 1.0 = full smooth like Hammer, 0.1 = light smooth",
        default=1.0,
        min=0.0,
        max=1.0,
        precision=3,
        subtype='FACTOR'
    )

    iterations: bpy.props.IntProperty(
        name="Iterations",
        description="Number of smooth passes",
        default=1,
        min=1,
        max=20
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return False
        # Allow both Edit Mode and Weight Paint Mode
        return context.mode in {'EDIT_MESH', 'PAINT_WEIGHT'}

    def execute(self, context):
        obj = context.active_object
        original_mode = obj.mode

        try:
            bpy.ops.object.mode_set(mode='OBJECT')

            me = obj.data
            vgs = obj.vertex_groups

            if not vgs:
                self.report({'WARNING'}, "Mesh has no vertex groups (skin weights)!")
                bpy.ops.object.mode_set(mode=original_mode)
                return {'CANCELLED'}

            # In Weight Paint mode: check if vertex masking is active
            # If no vertices are selected (or masking is off), process ALL vertices
            using_all_verts = False

            # Build a fast lookup: {vert_index: {group_index: weight}}
            def build_weight_map():
                wmap = {}
                for v in me.vertices:
                    wmap[v.index] = {g.group: g.weight for g in v.groups}
                return wmap

            # Build neighbor lookup from edge connectivity
            neighbor_map = {v.index: [] for v in me.vertices}
            for edge in me.edges:
                a, b = edge.vertices[0], edge.vertices[1]
                neighbor_map[a].append(b)
                neighbor_map[b].append(a)

            selected_indices = [v.index for v in me.vertices if v.select]

            # Weight Paint mode with no vertex masking -> process all vertices
            if not selected_indices:
                if original_mode == 'PAINT_WEIGHT':
                    selected_indices = [v.index for v in me.vertices]
                    using_all_verts = True
                else:
                    self.report({'WARNING'},
                        "No vertices selected. In Edit Mode: select verts first. "
                        "In Weight Paint Mode: enable Vertex Masking (dot icon in header).")
                    bpy.ops.object.mode_set(mode=original_mode)
                    return {'CANCELLED'}

            num_groups = len(vgs)
            strength = self.strength

            for _ in range(self.iterations):
                weight_map = build_weight_map()
                new_weights = {}

                for v_idx in selected_indices:
                    neighbors = neighbor_map[v_idx]
                    if not neighbors:
                        continue

                    old_weights = weight_map.get(v_idx, {})
                    neighbor_count = len(neighbors)

                    # Average neighbor weights across all influences (like surrWeights in Maya)
                    avg_neighbor = {}
                    for n_idx in neighbors:
                        n_weights = weight_map.get(n_idx, {})
                        for g_idx, w in n_weights.items():
                            avg_neighbor[g_idx] = avg_neighbor.get(g_idx, 0.0) + w

                    for g_idx in avg_neighbor:
                        avg_neighbor[g_idx] /= neighbor_count

                    # Core formula from tf_smoothSkinWeight.py:
                    # new = (avg_neighbor * strength) + (old * (1 - strength))
                    all_group_indices = set(old_weights.keys()) | set(avg_neighbor.keys())
                    blended = {}
                    for g_idx in all_group_indices:
                        old_w = old_weights.get(g_idx, 0.0)
                        avg_w = avg_neighbor.get(g_idx, 0.0)
                        blended[g_idx] = (avg_w * strength) + (old_w * (1.0 - strength))

                    # Normalize so total = 1.0
                    total = sum(blended.values())
                    if total > 0.00001:
                        for g_idx in blended:
                            blended[g_idx] /= total

                    new_weights[v_idx] = blended

                # Write blended weights back to vertex groups
                for v_idx, weights in new_weights.items():
                    # Clear all existing weights for this vertex
                    for vg in vgs:
                        vg.remove([v_idx])
                    # Set new blended weights
                    for g_idx, w in weights.items():
                        if g_idx < len(vgs) and w > 0.00001:
                            vgs[g_idx].add([v_idx], w, 'REPLACE')

            bpy.ops.object.mode_set(mode=original_mode)
            scope = "all verts" if using_all_verts else f"{len(selected_indices)} selected verts"
            self.report({'INFO'},
                f"Smooth Skin Weight: {scope}, "
                f"strength={strength:.2f}, iter={self.iterations}")
            return {'FINISHED'}

        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass
            self.report({'ERROR'}, f"Failed: {str(e)}")
            return {'CANCELLED'}


class VIEW3D_PT_smooth_skin_weight_panel(bpy.types.Panel):
    bl_label = "Smooth Skin Weight"
    bl_idname = "VIEW3D_PT_smooth_skin_weight_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_jjtools_main"
    # Visible in both Edit Mode and Weight Paint Mode
    bl_context = ""

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # Weight Paint mode hint
        if context.mode == 'PAINT_WEIGHT':
            ts = context.tool_settings
            has_mask = getattr(ts, 'use_vertex_group_weights', False)
            if not any(v.select for v in context.active_object.data.vertices):
                box = col.box()
                box.label(text="No mask: will smooth ALL verts", icon='INFO')
                box.label(text="Enable vertex masking to limit scope", icon='VERTEXSEL')

        # Quick presets
        col.label(text="Quick Presets:", icon='PRESET')

        op = col.operator("object.jj_smooth_skin_weight", text="Smooth (Full)", icon='MOD_SMOOTH')
        op.strength = 1.0
        op.iterations = 1

        op = col.operator("object.jj_smooth_skin_weight", text="Smooth (Light 50%)", icon='MOD_SMOOTH')
        op.strength = 0.5
        op.iterations = 1

        op = col.operator("object.jj_smooth_skin_weight", text="Smooth (Light 10%)", icon='MOD_SMOOTH')
        op.strength = 0.1
        op.iterations = 1

        col.separator()
        col.label(text="Custom:", icon='SETTINGS')
        col.operator("object.jj_smooth_skin_weight", text="Run Custom...", icon='PLAY')


def register():
    for cls in (OBJECT_OT_jj_smooth_skin_weight, VIEW3D_PT_smooth_skin_weight_panel):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_jj_smooth_skin_weight)
    bpy.utils.unregister_class(VIEW3D_PT_smooth_skin_weight_panel)


if __name__ == "__main__":
    register()
