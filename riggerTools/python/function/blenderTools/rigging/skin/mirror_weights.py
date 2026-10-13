"""
Mirror Weights — Blender Tool
Ported from ngSkinTools2 (Maya) mirror logic.

Author  : Noman (Assisted by AI)
Version : 1.0.0
Location: View3D > N-Panel > JJMenu > Mirror Weights

Core logic ported from ngSkinTools2:
  - influenceMapping.py  → bone_mapping() : name-glob + distance KD-Tree
  - mirror.py            → execute()      : vertex loop + copy/flip weights
  - tabMirror.py         → Panel UI

Mirror Directions:
  POSITIVE_TO_NEGATIVE  : copy weights from +X side → -X side  (Left → Right)
  NEGATIVE_TO_POSITIVE  : copy weights from -X side → +X side  (Right → Left)
  FLIP                  : swap weights between both sides

Bone Mapping (name-glob patterns, same as ngSkinTools2 defaults + Blender/ARP):
  L_*  ↔  R_*
  l_*  ↔  r_*
  lf_* ↔  rt_*
  *_lf ↔  *_rt
  *.L  ↔  *.R      ← Blender/ARP convention
  *_L  ↔  *_R      ← Alternative suffix
  *-L  ↔  *-R      ← Dash variant
"""

import re
import bpy
import mathutils

bl_info = {
    "name": "Mirror Weights (ngSkinTools2 Port)",
    "description": "Mirror skin weights L↔R using name-glob + KD-Tree matching (ported from ngSkinTools2)",
    "author": "Noman (Assisted by AI)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N-Panel > JJMenu > Mirror Weights",
    "category": "Rigging",
}

# ─────────────────────────────────────────────
#  GLOB PATTERNS  (same logic as ngSkinTools2)
# ─────────────────────────────────────────────

# Each tuple = (left_glob, right_glob)
# Order matters: more specific patterns should come first
DEFAULT_GLOBS = [
    (r"^L_(.*)$",   r"R_\1"),   # L_arm     → R_arm
    (r"^l_(.*)$",   r"r_\1"),   # l_arm     → r_arm
    (r"^lf_(.*)$",  r"rt_\1"),  # lf_arm    → rt_arm
    (r"^(.*)\\.L$", r"\1.R"),   # arm.L     → arm.R  (Blender/ARP)
    (r"^(.*)_L$",   r"\1_R"),   # arm_L     → arm_R
    (r"^(.*)-L$",   r"\1-R"),   # arm-L     → arm-R
    (r"^(.*)\\.lf$",r"\1.rt"),  # *_lf      → *_rt  (dot variant)
    (r"^(.*)_lf$",  r"\1_rt"),  # arm_lf    → arm_rt
]


def _find_mirror_name(name: str) -> str | None:
    """
    Given a bone/vertex-group name, return its mirrored counterpart name.
    Checks both L→R and R→L directions.
    Returns None if no pattern matches.

    Port of ngSkinTools2 influenceMapping.nameMatches() glob logic.
    """
    for left_pat, right_repl in DEFAULT_GLOBS:
        # Try L → R
        m = re.match(left_pat, name)
        if m:
            return re.sub(left_pat, right_repl, name)

        # Try R → L  (reverse the pattern)
        right_pat  = left_pat .replace(r"^L_",   r"^R_") \
                               .replace(r"^l_",   r"^r_") \
                               .replace(r"^lf_",  r"^rt_") \
                               .replace(r"\\.L$", r"\\.R$") \
                               .replace(r"_L$",   r"_R$") \
                               .replace(r"-L$",   r"-R$") \
                               .replace(r"\\.lf$",r"\\.rt$") \
                               .replace(r"_lf$",  r"_rt$")
        left_repl  = right_repl.replace(r"R_\1",  r"L_\1") \
                                .replace(r"r_\1",  r"l_\1") \
                                .replace(r"rt_\1", r"lf_\1") \
                                .replace(r"\1.R",  r"\1.L") \
                                .replace(r"\1_R",  r"\1_L") \
                                .replace(r"\1-R",  r"\1-L") \
                                .replace(r"\1.rt", r"\1.lf") \
                                .replace(r"\1_rt", r"\1_lf")
        m = re.match(right_pat, name)
        if m:
            return re.sub(right_pat, left_repl, name)

    return None


# ─────────────────────────────────────────────
#  BONE MAPPING
# ─────────────────────────────────────────────

def build_bone_mapping(obj, distance_threshold: float = 0.001) -> dict[int, int]:
    """
    Build a mapping { vg_index_src → vg_index_dst } using:
      1. Name-glob matching  (priority, from ngSkinTools2 nameMatches)
      2. Distance matching   (fallback, from ngSkinTools2 distanceMatches)

    Returns dict mapping source VG index → destination VG index.
    Center bones (no pair found) map to themselves.
    """
    arm_mod = next((m for m in obj.modifiers if m.type == 'ARMATURE'), None)
    arm_obj = arm_mod.object if arm_mod else None

    vgs = obj.vertex_groups
    mapping: dict[int, int] = {}

    # ── 1. Name-glob matching ──
    for vg in vgs:
        mirror_name = _find_mirror_name(vg.name)
        if mirror_name and mirror_name in vgs:
            mapping[vg.index] = vgs[mirror_name].index

    # ── 2. Distance matching (fallback for center/unmatched bones) ──
    if arm_obj:
        # Collect pivots of matched src bones for skip-list
        matched_src = set(mapping.keys())
        matched_dst = set(mapping.values())

        bones = arm_obj.data.bones
        unmatched = [vg for vg in vgs if vg.index not in matched_src and vg.name in bones]

        for vg in unmatched:
            bone = bones[vg.name]
            pivot = arm_obj.matrix_world @ bone.head_local

            # Flip X to find mirror position
            mirror_pos = pivot.copy()
            mirror_pos.x = -mirror_pos.x

            best_dist = distance_threshold
            best_idx  = None

            for other_vg in vgs:
                if other_vg.name not in bones or other_vg.index == vg.index:
                    continue
                other_bone  = bones[other_vg.name]
                other_pivot = arm_obj.matrix_world @ other_bone.head_local
                d = (mirror_pos - other_pivot).length
                if d < best_dist:
                    best_dist = d
                    best_idx  = other_vg.index

            if best_idx is not None:
                mapping[vg.index] = best_idx
            else:
                # Center bone — maps to itself (seam logic handled in execute)
                mapping[vg.index] = vg.index

    return mapping


# ─────────────────────────────────────────────
#  MIRROR EXECUTE
# ─────────────────────────────────────────────

DIRECTION_POS_TO_NEG = 0   # +X → -X  (Left drives Right)
DIRECTION_NEG_TO_POS = 1   # -X → +X  (Right drives Left)
DIRECTION_FLIP       = 2   # Swap both sides


def execute_mirror(
    obj,
    direction: int          = DIRECTION_POS_TO_NEG,
    axis: int               = 0,            # 0=X, 1=Y, 2=Z
    seam_width: float       = 0.001,
    distance_threshold: float = 0.005,
    selected_only: bool     = False,
):
    """
    Main mirror function.  Port of ngSkinTools2 Mirror.mirror().

    Steps:
      1. Build bone mapping (name + distance).
      2. Build KD-Tree from mesh vertices for fast mirror-vertex lookup.
      3. Loop each vertex (or selected-only):
         - If |pos[axis]| < seam_width  → average with its mirror vertex.
         - Else if driving side         → copy weights to mirror vertex.
         - Flip mode                    → swap weights between both.

    selected_only: ถ้า True จะ mirror เฉพาะ vertex ที่ถูก select ไว้
                   (อ่านจาก mesh.vertices[i].select — ต้อง sync จาก Edit/WP mode ก่อน)
    """
    mesh = obj.data
    bone_map = build_bone_mapping(obj, distance_threshold=distance_threshold)

    # ── Build selected vertex set (if needed) ──
    # mesh.vertices[i].select จะถูก sync อัตโนมัติเมื่อ switch มา Object mode
    if selected_only:
        selected_vis = {v.index for v in mesh.vertices if v.select}
    else:
        selected_vis = None   # None = all vertices

    # ── Build KD-Tree ──
    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)
    kd.balance()

    def find_mirror_vi(co):
        """Find index of vertex closest to the mirrored position."""
        mirrored = co.copy()
        mirrored[axis] = -mirrored[axis]
        _co, index, dist = kd.find(mirrored)
        if dist <= distance_threshold:
            return index
        return None

    def get_weights(vi) -> dict[int, float]:
        """Read weights for vertex index vi as {vg_idx: weight}."""
        result = {}
        for vg in obj.vertex_groups:
            try:
                w = vg.weight(vi)
                if w > 0.0:
                    result[vg.index] = w
            except RuntimeError:
                pass
        return result

    def set_weights(vi, weights: dict[int, float]):
        """Write weights dict to vertex index vi.  Clears old values first."""
        # Clear all groups for this vertex
        for vg in obj.vertex_groups:
            vg.remove([vi])
        # Assign new weights
        for vg_idx, w in weights.items():
            obj.vertex_groups[vg_idx].add([vi], w, 'REPLACE')

    def remap_weights(weights: dict[int, float], bone_map: dict[int, int]) -> dict[int, float]:
        """Remap src bone indices → dst bone indices using bone_map."""
        result = {}
        for src_idx, w in weights.items():
            dst_idx = bone_map.get(src_idx, src_idx)
            result[dst_idx] = result.get(dst_idx, 0.0) + w
        return result

    def average_weights(w1: dict[int, float], w2: dict[int, float]) -> dict[int, float]:
        """Average two weight dicts (for seam vertices)."""
        all_keys = set(w1.keys()) | set(w2.keys())
        result = {}
        for k in all_keys:
            result[k] = (w1.get(k, 0.0) + w2.get(k, 0.0)) / 2.0
        return result

    # ── Main vertex loop ──
    processed_pairs: set[tuple[int, int]] = set()

    for v in mesh.vertices:
        vi = v.index
        pos = v.co[axis]

        # ── Selected-only filter ──
        # Process a vertex if:
        #   a) selected_only is OFF, OR
        #   b) this vertex is selected, OR
        #   c) its mirror vertex is selected (so the target still gets updated)
        if selected_vis is not None:
            mirror_vi_check = find_mirror_vi(v.co)
            if vi not in selected_vis and (mirror_vi_check is None or mirror_vi_check not in selected_vis):
                continue

        mirror_vi = find_mirror_vi(v.co)
        if mirror_vi is None or mirror_vi == vi:
            # If no mirror found OR it's a center seam vertex with no opposite
            continue

        pair = (min(vi, mirror_vi), max(vi, mirror_vi))
        if pair in processed_pairs:
            continue
        processed_pairs.add(pair)

        # ── Seam vertex (near center) ──
        if abs(pos) < seam_width:
            w_src = get_weights(vi)
            w_dst = get_weights(mirror_vi)
            w_src_remapped = remap_weights(w_src, bone_map)
            w_dst_remapped = remap_weights(w_dst, bone_map)
            avg = average_weights(w_src_remapped, w_dst_remapped)
            set_weights(vi, avg)
            set_weights(mirror_vi, avg)
            continue

        # ── Directional copy ──
        driving = None  # index of vertex that "drives" the mirror
        target  = None

        if direction == DIRECTION_POS_TO_NEG:
            if pos > 0:
                driving, target = vi, mirror_vi
            else:
                driving, target = mirror_vi, vi
        elif direction == DIRECTION_NEG_TO_POS:
            if pos < 0:
                driving, target = vi, mirror_vi
            else:
                driving, target = mirror_vi, vi
        elif direction == DIRECTION_FLIP:
            # Swap weights on both sides
            w_a = remap_weights(get_weights(vi), bone_map)
            w_b = remap_weights(get_weights(mirror_vi), bone_map)
            set_weights(vi, w_b)
            set_weights(mirror_vi, w_a)
            continue

        if driving is not None:
            w = remap_weights(get_weights(driving), bone_map)
            set_weights(target, w)

    # Refresh viewport
    mesh.update()


# ─────────────────────────────────────────────
#  OPERATOR
# ─────────────────────────────────────────────

class SKIN_OT_mirror_weights(bpy.types.Operator):
    """Mirror skin weights L↔R (ngSkinTools2 port)"""
    bl_idname  = "skin.mirror_weights"
    bl_label   = "Mirror Weights"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        name="Direction",
        description="Which side drives the mirror",
        items=[
            ('POS_TO_NEG', "+X → -X  (Left → Right)", "Copy from positive side to negative side"),
            ('NEG_TO_POS', "-X → +X  (Right → Left)", "Copy from negative side to positive side"),
            ('FLIP',       "Flip  (Swap both sides)",  "Swap weights between both sides"),
        ],
        default='POS_TO_NEG',
    )

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Mirror axis",
        items=[
            ('X', "X", "Mirror across YZ plane"),
            ('Y', "Y", "Mirror across XZ plane"),
            ('Z', "Z", "Mirror across XY plane"),
        ],
        default='X',
    )

    seam_width: bpy.props.FloatProperty(
        name="Seam Width",
        description="Vertices within this distance from center are averaged (not just copied)",
        default=0.001,
        min=0.0,
        max=1.0,
        precision=4,
        step=1,
    )

    distance_threshold: bpy.props.FloatProperty(
        name="Search Radius",
        description="Max distance to consider a vertex as the 'mirror' of another",
        default=0.005,
        min=0.0001,
        max=1.0,
        precision=4,
        step=1,
    )

    selected_only: bpy.props.BoolProperty(
        name="Selected Vertices Only",
        description="Mirror weights only for selected vertices (and their mirror counterparts)",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and len(obj.vertex_groups) > 0
            and context.mode in {'OBJECT', 'EDIT_MESH', 'PAINT_WEIGHT'}
        )

    def execute(self, context):
        obj = context.active_object

        # Switch to Object mode for weight editing
        # Blender syncs vertex selection to mesh.vertices[i].select when leaving Edit/WP mode
        original_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        try:
            dir_map = {
                'POS_TO_NEG': DIRECTION_POS_TO_NEG,
                'NEG_TO_POS': DIRECTION_NEG_TO_POS,
                'FLIP'      : DIRECTION_FLIP,
            }
            axis_map = {'X': 0, 'Y': 1, 'Z': 2}

            execute_mirror(
                obj,
                direction          = dir_map[self.direction],
                axis               = axis_map[self.axis],
                seam_width         = self.seam_width,
                distance_threshold = self.distance_threshold,
                selected_only      = self.selected_only,
            )
            mode_label = "selected" if self.selected_only else "all"
            self.report({'INFO'}, f"Mirror Weights complete ({mode_label} vertices) — {obj.name}")
        except Exception as e:
            self.report({'ERROR'}, f"Mirror Weights failed: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
        finally:
            bpy.ops.object.mode_set(mode=original_mode)

        return {'FINISHED'}


# ─────────────────────────────────────────────
#  UI PANEL  (hooks into JJMenu main panel)
# ─────────────────────────────────────────────

class VIEW3D_PT_mirror_weights_panel(bpy.types.Panel):
    """Mirror Weights panel inside JJMenu N-Panel tab"""
    bl_label    = "Mirror Weights"
    bl_idname   = "VIEW3D_PT_mirror_weights_panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id   = "VIEW3D_PT_jjtools_main"   # Hook into JJMenu main panel

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        col.label(text="Options:")

        row = col.row(align=True)
        row.label(text="Axis:")
        row.prop(scn, "nm_mirror_axis", expand=True)

        col.prop(scn, "nm_mirror_direction",     text="Direction")
        col.prop(scn, "nm_mirror_seam_width")
        col.prop(scn, "nm_mirror_search_radius")

        col.separator()
        # Selected-only toggle — highlighted when active
        row = col.row(align=True)
        row.prop(
            scn, "nm_mirror_selected_only",
            text="Selected Vertices Only",
            icon='RESTRICT_SELECT_OFF' if scn.nm_mirror_selected_only else 'RESTRICT_SELECT_ON',
            toggle=True,
        )

        col.separator()
        # ── Mirror button — passes all settings ──
        op = col.operator("skin.mirror_weights", text="Mirror Weights", icon='MOD_MIRROR')
        op.direction          = scn.nm_mirror_direction
        op.axis               = scn.nm_mirror_axis
        op.seam_width         = scn.nm_mirror_seam_width
        op.distance_threshold = scn.nm_mirror_search_radius
        op.selected_only      = scn.nm_mirror_selected_only


# ─────────────────────────────────────────────
#  SCENE PROPS (store last-used settings)
# ─────────────────────────────────────────────

def _register_scene_props():
    bpy.types.Scene.nm_mirror_axis = bpy.props.EnumProperty(
        name="Mirror Axis",
        items=[('X','X',''),('Y','Y',''),('Z','Z','')],
        default='X',
    )
    bpy.types.Scene.nm_mirror_direction = bpy.props.EnumProperty(
        name="Direction",
        items=[
            ('POS_TO_NEG', "+X → -X  (Left → Right)", ""),
            ('NEG_TO_POS', "-X → +X  (Right → Left)", ""),
            ('FLIP',       "Flip  (Swap both sides)",  ""),
        ],
        default='POS_TO_NEG',
    )
    bpy.types.Scene.nm_mirror_seam_width = bpy.props.FloatProperty(
        name="Seam Width",
        default=0.001, min=0.0, max=1.0, precision=4, step=1,
    )
    bpy.types.Scene.nm_mirror_search_radius = bpy.props.FloatProperty(
        name="Search Radius",
        default=0.005, min=0.0001, max=1.0, precision=4, step=1,
    )
    bpy.types.Scene.nm_mirror_selected_only = bpy.props.BoolProperty(
        name="Selected Vertices Only",
        description="Mirror weights only for selected vertices (and their mirror counterparts)",
        default=False,
    )


def _unregister_scene_props():
    for attr in (
        "nm_mirror_axis",
        "nm_mirror_direction",
        "nm_mirror_seam_width",
        "nm_mirror_search_radius",
        "nm_mirror_selected_only",
    ):
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)


# ─────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────

classes = (
    SKIN_OT_mirror_weights,
    VIEW3D_PT_mirror_weights_panel,
)


def register():
    _register_scene_props()
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    _unregister_scene_props()


if __name__ == "__main__":
    register()
