# -*- coding: utf-8 -*-
"""
===============================================================================
Module: fkIkMatcherUI.py
===============================================================================
Overview:
    Modern PySide2/PySide6 FK/IK Matcher and Space Switcher Tool for Maya.
    Supports:
      1. Standard 3-Bone Limbs (Arms, Biped Legs)
      2. Plantigrade Front Limbs (UpperLeg, LowerLeg, Ankle, Ball, Toe)
      3. Quadruped Double-IK Hind Limbs (UpperLeg, LowerLeg, Hock, Ankle, Ball)

Features:
    - Pure Python PySide UI (cross-version Maya 2017-2026+ and multi-machine portable)
    - Viewport Selection auto-detection & Scene stick controller enumeration
    - Live Mode Indicator (FK vs IK)
    - Discrete Snap buttons: [Snap FK -> IK], [Snap IK -> FK]
    - One-Click [⚡ SNAP & SWITCH] (Auto-detects mode, snaps opposite chain, flips FK_IK)
    - [x] Auto-Keyframe option to prevent animation popping across timeline
    - [x] Time Range Baking: 2-pass frame range transfer with stepped FK_IK keyframes
    - Dual resolution: Message attributes connection with graceful naming pattern fallback
"""

import sys
import math
import maya.cmds as mc
import maya.OpenMayaUI as omui

try:
    from importlib import reload
except ImportError:
    pass

__version__ = "v4.4.0"

try:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from PySide6 import QtWidgets, QtGui, QtCore
        from shiboken6 import wrapInstance
    except ImportError:
        pass


def get_maya_main_window():
    """Returns the QWidget instance of Maya's main application window."""
    try:
        ptr = omui.MQtUtil.mainWindow()
        if ptr:
            return wrapInstance(int(ptr), QtWidgets.QWidget)
    except Exception:
        pass
    return None


# =============================================================================
# Vector Math Utilities
# =============================================================================

def _v_sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def _v_add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

def _v_scale(a, s):
    return [a[0] * s, a[1] * s, a[2] * s]

def _v_mult(a, s):
    return [a[0] * s, a[1] * s, a[2] * s]

def _v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _v_len(a):
    return math.sqrt(max(0.0, _v_dot(a, a)))

def _v_norm(a):
    l = _v_len(a)
    return _v_mult(a, 1.0 / l) if l > 1e-6 else [0.0, 1.0, 0.0]


def calculate_pole_vector_pos(up_node, mid_node, low_node, distance_mult=1.2):
    """
    Calculates the exact 3D world position for a Pole Vector controller
    to preserve the current knee/elbow angle without rotational twisting.
    """
    p_up = mc.xform(up_node, q=True, ws=True, t=True)
    p_mid = mc.xform(mid_node, q=True, ws=True, t=True)
    p_low = mc.xform(low_node, q=True, ws=True, t=True)

    v_hypotenuse = _v_sub(p_low, p_up)
    v_mid = _v_sub(p_mid, p_up)

    hyp_len_sq = _v_dot(v_hypotenuse, v_hypotenuse)
    if hyp_len_sq < 1e-6:
        return _v_add(p_mid, [0.0, 0.0, 20.0])

    proj_scalar = _v_dot(v_mid, v_hypotenuse) / hyp_len_sq
    p_proj = _v_add(p_up, _v_mult(v_hypotenuse, proj_scalar))

    v_bend = _v_sub(p_mid, p_proj)
    bend_len = _v_len(v_bend)

    # Total limb length estimate
    arm_len = _v_len(v_mid) + _v_len(_v_sub(p_low, p_mid))
    pv_dist = max(arm_len * 0.5, bend_len * distance_mult, 10.0)

    if bend_len > 1e-4:
        v_dir = _v_norm(v_bend)
    else:
        # Collinear fallback: use up node local Z or Y axis
        v_dir = [0.0, 0.0, 1.0]

    return _v_add(p_mid, _v_mult(v_dir, pv_dist))


# =============================================================================
# Matcher Core Engine
# =============================================================================

class FkIkMatcherEngine(object):
    """Core logic to inspect, match, and toggle FK/IK chains."""

    @staticmethod
    def get_all_stick_controllers():
        """Scans Maya scene for all potential FK/IK Stick controllers."""
        candidates = mc.ls('*Stick*_ctrl', '*stick*_ctrl', type='transform') or []
        sticks = []
        for c in candidates:
            if mc.attributeQuery('FK_IK', node=c, exists=True):
                sticks.append(c)
        return sorted(list(set(sticks)))

    @staticmethod
    def resolve_stick_from_selection():
        """Resolves the relevant stick controller from the current Maya selection."""
        sel = mc.ls(sl=True) or []
        if not sel:
            return None

        for node in sel:
            # 1. Direct stick check
            if mc.attributeQuery('FK_IK', node=node, exists=True):
                return node

            # 2. Check message connection to stick
            if mc.attributeQuery('stick', node=node, exists=True):
                con = mc.listConnections(f"{node}.stick")
                if con and mc.attributeQuery('FK_IK', node=con[0], exists=True):
                    return con[0]

            # 3. Check incoming connections to see if any stick connects to this node
            incoming = mc.listConnections(f"{node}.message", d=True, s=False) or []
            for inc in incoming:
                if 'Stick' in inc and mc.attributeQuery('FK_IK', node=inc, exists=True):
                    return inc

            # 4. Naming convention deduction (e.g. upperArmFkLFT_ctrl -> armStickLFT_ctrl)
            name_parts = node.split('_')[0]
            for side in ['LFT', 'RGT', 'L', 'R', 'MID', 'C']:
                if side in node:
                    for token in ['arm', 'leg', 'frontLeg', 'backLeg', 'legBack01', 'legBack02']:
                        if token.lower() in node.lower():
                            candidate = f"{token}Stick{side}_ctrl"
                            if mc.objExists(candidate) and mc.attributeQuery('FK_IK', node=candidate, exists=True):
                                return candidate

        # Fallback: return first valid stick in scene if available
        all_sticks = FkIkMatcherEngine.get_all_stick_controllers()
        return all_sticks[0] if all_sticks else None

    @staticmethod
    def get_stick_data(stick):
        """
        Inspects the stick controller and returns a structured dictionary of
        connected joints, FK controllers, IK controllers, and limb metadata.
        Uses message attributes first, with robust naming pattern fallbacks.
        """
        if not stick or not mc.objExists(stick):
            return None

        def _get_con(attr_name):
            if mc.attributeQuery(attr_name, node=stick, exists=True):
                c = mc.listConnections(f"{stick}.{attr_name}")
                return c[0] if c else None
            return None

        def _get_attr(attr_name, default=''):
            if mc.attributeQuery(attr_name, node=stick, exists=True):
                return mc.getAttr(f"{stick}.{attr_name}") or default
            return default

        # Basic attributes
        fk_ik_val = mc.getAttr(f"{stick}.FK_IK") if mc.attributeQuery('FK_IK', node=stick, exists=True) else 0.0
        region = _get_attr('region', '')
        location = _get_attr('location', '')

        # Gather joints from message connections
        up_jnt = _get_con('upJnt')
        mid_jnt = _get_con('midJnt')
        low_jnt = _get_con('lowJnt')
        ankle_jnt = _get_con('ankleJnt')
        ball_jnt = _get_con('ballJnt')
        toe_jnt = _get_con('toeJnt')

        # Gather FK controllers from message connections
        up_fk = _get_con('upFkCtrl')
        mid_fk = _get_con('midFkCtrl')
        low_fk = _get_con('lowFkCtrl')
        ankle_fk = _get_con('ankleFkCtrl')
        ball_fk = _get_con('ballFkCtrl')
        toe_fk = _get_con('toeFkCtrl')

        # Gather IK controllers from message connections
        ik_ctrl = _get_con('ikCtrl')
        ik_root_ctrl = _get_con('ikRootCtrl')
        mid_ik_ctrl = _get_con('midIkCtrl')
        pov_ctrl = _get_con('pov')
        offset_null = _get_con('offset')
        ik_ref_jnt = _get_con('ikRefJnt')
        ik_posi = _get_attr('ikPosi', '') or location

        # Fallback references for scenes built before ikRefJnt was added
        if not ik_ref_jnt:
            if ik_posi in ['foot', 'animalFoot'] and ball_jnt:
                ik_ref_jnt = ball_jnt
            else:
                ik_ref_jnt = ankle_jnt or low_jnt

        # Detect side and part naming tokens for heuristics
        side = 'LFT' if 'LFT' in stick else ('RGT' if 'RGT' in stick else '')
        if not ik_root_ctrl and up_jnt:
            raw_up = up_jnt.replace('_bJnt', '')
            candidate_root = f"{raw_up}IkRoot{side}_ctrl"
            if mc.objExists(candidate_root):
                ik_root_ctrl = candidate_root

        is_hind_double_ik = 'back' in stick.lower() or 'double' in str(location).lower() or mid_ik_ctrl is not None
        is_front_plantigrade = 'front' in stick.lower() or 'plantigrade' in str(location).lower() or ball_jnt is not None

        # Determine limb classification string
        if is_hind_double_ik:
            limb_type = 'Double-IK Hind Leg'
        elif is_front_plantigrade:
            limb_type = 'Plantigrade Front Leg'
        else:
            limb_type = 'Standard 3-Bone Arm/Leg'

        # =====================================================================
        # Strict Validation — NO silent fallback name guessing
        # =====================================================================
        # If message connections are missing, report exactly what's missing
        # and return None to halt execution instead of guessing wrong names.
        required_msg = {
            'upJnt': up_jnt,
            'midJnt': mid_jnt,
            'lowJnt': low_jnt,
            'upFkCtrl': up_fk,
            'midFkCtrl': mid_fk,
            'lowFkCtrl': low_fk,
            'ikCtrl': ik_ctrl,
            'pov': pov_ctrl,
        }
        missing = [k for k, v in required_msg.items() if not v]

        if missing:
            mc.warning(
                "FK/IK Matcher: '{}' is missing message attribute connections: [{}]. "
                "Please rebuild the rig with the updated auto-rig code, "
                "or run the patch script to add message attributes.".format(
                    stick, ', '.join(missing)
                )
            )
            return None

        # Validate that resolved nodes actually exist in the scene
        all_nodes = {
            'upJnt': up_jnt, 'midJnt': mid_jnt, 'lowJnt': low_jnt,
            'upFkCtrl': up_fk, 'midFkCtrl': mid_fk, 'lowFkCtrl': low_fk,
            'ikCtrl': ik_ctrl, 'pov': pov_ctrl,
        }
        if ankle_jnt:
            all_nodes['ankleJnt'] = ankle_jnt
        if ball_jnt:
            all_nodes['ballJnt'] = ball_jnt
        if ball_fk:
            all_nodes['ballFkCtrl'] = ball_fk
        if offset_null:
            all_nodes['offset'] = offset_null

        not_found = [f"{k} -> '{v}'" for k, v in all_nodes.items()
                     if v and not mc.objExists(v)]
        if not_found:
            mc.warning(
                "FK/IK Matcher: '{}' has message attrs but these nodes don't exist "
                "in scene: [{}]. Check if the rig was built correctly.".format(
                    stick, ', '.join(not_found)
                )
            )
            return None

        # Build list of FK controller -> Joint pairs for matching
        fk_pairs = []
        if up_fk and up_jnt and mc.objExists(up_fk) and mc.objExists(up_jnt):
            fk_pairs.append((up_fk, up_jnt))
        if mid_fk and mid_jnt and mc.objExists(mid_fk) and mc.objExists(mid_jnt):
            fk_pairs.append((mid_fk, mid_jnt))
        if low_fk and low_jnt and mc.objExists(low_fk) and mc.objExists(low_jnt):
            fk_pairs.append((low_fk, low_jnt))
        if ankle_fk and ankle_jnt and mc.objExists(ankle_fk) and mc.objExists(ankle_jnt):
            fk_pairs.append((ankle_fk, ankle_jnt))
        if ball_fk and ball_jnt and mc.objExists(ball_fk) and mc.objExists(ball_jnt):
            fk_pairs.append((ball_fk, ball_jnt))
        if toe_fk and toe_jnt and mc.objExists(toe_fk) and mc.objExists(toe_jnt):
            fk_pairs.append((toe_fk, toe_jnt))

        # Resolve Main IK Handle (ikh) for precise Delta Correction
        ikh = _get_con('ikh') or _get_con('ikHandle')
        if not ikh or not mc.objExists(ikh):
            # 1. Look up via poleVectorConstraint on pov_ctrl
            if pov_ctrl and mc.objExists(pov_ctrl):
                pvc_list = mc.listConnections(pov_ctrl, type='poleVectorConstraint') or []
                for pvc in pvc_list:
                    ikh_list = mc.listConnections(pvc, type='ikHandle') or []
                    if ikh_list:
                        ikh = ikh_list[0]
                        break
            # 2. Look up via metaNode
            if not ikh:
                meta = _get_con('meta')
                if meta and mc.objExists(meta) and mc.attributeQuery('ikh_Name', node=meta, exists=True):
                    meta_ikh = mc.listConnections(f"{meta}.ikh_Name")
                    ikh = meta_ikh[0] if meta_ikh else mc.getAttr(f"{meta}.ikh_Name")
            # 3. Naming heuristic fallback
            if not ikh and up_jnt:
                raw_up = up_jnt.replace('_bJnt', '')
                part_stem = raw_up.replace('upperLeg', 'leg').replace('upperArm', 'arm').replace('upper', '')
                candidates = [
                    f"{raw_up}_ikh",
                    f"{raw_up.replace('upperLeg', 'upperLegIk')}_ikh",
                    f"{raw_up.replace('upperArm', 'upperArmIk')}_ikh",
                    f"{part_stem}Ik{side}_ikh",
                    f"{part_stem}{side}_ikh",
                    f"{raw_up}Ik_ikh",
                    f"{region}Ik{side}_ikh" if region else "",
                    f"{region}{side}_ikh" if region else "",
                    f"lowerLeg{side}_ikSpring_handle",
                    f"ankle{side}_ikh"
                ]
                for cand in candidates:
                    if cand and mc.objExists(cand):
                        ikh = cand
                        break

        return {
            'stick': stick,
            'fk_ik': fk_ik_val,
            'region': region,
            'location': location,
            'ik_posi': ik_posi,
            'ik_ref_jnt': ik_ref_jnt,
            'ik_root_ctrl': ik_root_ctrl,
            'ikh': ikh,
            'limb_type': limb_type,
            'side': side,
            'up_jnt': up_jnt,
            'mid_jnt': mid_jnt,
            'low_jnt': low_jnt,
            'ankle_jnt': ankle_jnt,
            'ball_jnt': ball_jnt,
            'toe_jnt': toe_jnt,
            'up_fk': up_fk,
            'mid_fk': mid_fk,
            'low_fk': low_fk,
            'ankle_fk': ankle_fk,
            'ball_fk': ball_fk,
            'toe_fk': toe_fk,
            'ik_ctrl': ik_ctrl,
            'mid_ik_ctrl': mid_ik_ctrl,
            'pov_ctrl': pov_ctrl,
            'offset_null': offset_null,
            'fk_pairs': fk_pairs
        }

    @staticmethod
    def match_transform_ws(target, source, pos=True, rot=True):
        """Matches world space transformation from source to target."""
        if not target or not source or not mc.objExists(target) or not mc.objExists(source):
            return

        if hasattr(mc, 'matchTransform'):
            mc.matchTransform(target, source, pos=pos, rot=rot)
        else:
            if pos:
                p = mc.xform(source, q=True, ws=True, t=True)
                mc.xform(target, ws=True, t=p)
            if rot:
                r = mc.xform(source, q=True, ws=True, ro=True)
                mc.xform(target, ws=True, ro=r)

    @classmethod
    def snap_fk_to_ik(cls, stick, auto_key=False):
        """Snaps all FK controllers to match the current IK pose."""
        data = cls.get_stick_data(stick)
        if not data:
            mc.warning(f"Invalid stick controller: {stick}")
            return False

        fk_pairs = data['fk_pairs']
        modified_nodes = []

        for fk_ctrl, b_jnt in fk_pairs:
            # Zero out any gimbal controller under this FK control
            gmb = f"{fk_ctrl[:-5]}_gmbCtrl" if fk_ctrl.endswith('_ctrl') else f"{fk_ctrl}_gmb"
            if mc.objExists(gmb):
                for ch in ['rx', 'ry', 'rz']:
                    if not mc.getAttr(f"{gmb}.{ch}", lock=True):
                        mc.setAttr(f"{gmb}.{ch}", 0.0)
                modified_nodes.append(gmb)

            # Match world transform to bind joint with rotate order safety
            try:
                old_ro = mc.getAttr(f"{b_jnt}.ro")
                ctrl_ro = mc.getAttr(f"{fk_ctrl}.ro")
                mc.setAttr(f"{b_jnt}.ro", ctrl_ro)
                pos = mc.xform(b_jnt, q=True, ws=True, t=True)
                rot = mc.xform(b_jnt, q=True, ws=True, ro=True)
                mc.setAttr(f"{b_jnt}.ro", old_ro)
                mc.xform(fk_ctrl, ws=True, t=pos, ro=rot)
            except Exception:
                cls.match_transform_ws(fk_ctrl, b_jnt, pos=True, rot=True)

            modified_nodes.append(fk_ctrl)

        if auto_key and modified_nodes:
            mc.setKeyframe(modified_nodes)

        return True

    @classmethod
    def snap_ik_to_fk(cls, stick, auto_key=False):
        """
        Snaps the IK controller and Pole Vector to match the current FK pose.
        Uses the proven 5-step architecture:
          1. Read pristine FK joint coordinates & orientations.
          2. Reset sub-roll attributes and IK handle twist.
          3. Synchronize IK Root position AND rotation.
          4. Snap IK controller and apply exact Delta IK Handle Correction.
          5. Snap Mid IK controller (for double-IK hind legs).
          6. Snap Pole Vector strictly LAST along planar geometric projection
             (prevents local-space dragging from ankle parent constraints).
        """
        data = cls.get_stick_data(stick)
        if not data:
            mc.warning(f"Invalid stick controller: {stick}")
            return False

        modified_nodes = []

        up_jnt = data.get('up_jnt')
        mid_jnt = data.get('mid_jnt')
        low_jnt = data.get('low_jnt')
        ankle_jnt = data.get('ankle_jnt') or low_jnt
        ik_ctrl = data.get('ik_ctrl')
        ik_root = data.get('ik_root_ctrl')
        mid_ik_ctrl = data.get('mid_ik_ctrl')
        pov_ctrl = data.get('pov_ctrl')
        offset_null = data.get('offset_null')
        ik_ref_jnt = data.get('ik_ref_jnt')
        ikh = data.get('ikh')

        # --- Step 1: Read pristine FK coordinates ---
        fk_up_pos = mc.xform(up_jnt, q=True, ws=True, t=True) if (up_jnt and mc.objExists(up_jnt)) else None
        fk_mid_pos = mc.xform(mid_jnt, q=True, ws=True, t=True) if (mid_jnt and mc.objExists(mid_jnt)) else None
        fk_low_pos = mc.xform(low_jnt, q=True, ws=True, t=True) if (low_jnt and mc.objExists(low_jnt)) else None

        # Rotation for IK Root (match rotateOrder of up_jnt to avoid flipping)
        fk_up_rot = None
        if up_jnt and mc.objExists(up_jnt) and ik_root and mc.objExists(ik_root):
            try:
                src_ro = mc.getAttr(f"{up_jnt}.ro")
                tgt_ro = mc.getAttr(f"{ik_root}.ro")
                if src_ro != tgt_ro:
                    mc.setAttr(f"{up_jnt}.ro", tgt_ro)
                    fk_up_rot = mc.xform(up_jnt, q=True, ws=True, ro=True)
                    mc.setAttr(f"{up_jnt}.ro", src_ro)
                else:
                    fk_up_rot = mc.xform(up_jnt, q=True, ws=True, ro=True)
            except Exception:
                fk_up_rot = mc.xform(up_jnt, q=True, ws=True, ro=True)

        # Orientation source for main IK controller
        snap_source = offset_null if (offset_null and mc.objExists(offset_null)) else (ik_ref_jnt or ankle_jnt)
        snap_rot = None
        if snap_source and mc.objExists(snap_source) and ik_ctrl and mc.objExists(ik_ctrl):
            try:
                src_ro = mc.getAttr(f"{snap_source}.ro")
                tgt_ro = mc.getAttr(f"{ik_ctrl}.ro")
                if src_ro != tgt_ro:
                    mc.setAttr(f"{snap_source}.ro", tgt_ro)
                    snap_rot = mc.xform(snap_source, q=True, ws=True, ro=True)
                    mc.setAttr(f"{snap_source}.ro", src_ro)
                else:
                    snap_rot = mc.xform(snap_source, q=True, ws=True, ro=True)
            except Exception:
                snap_rot = mc.xform(snap_source, q=True, ws=True, ro=True)

        # --- Step 2: Reset Sub-Roll Attributes & IK Handle Twist ---
        if ik_ctrl and mc.objExists(ik_ctrl):
            roll_attrs = [
                'ballRoll', 'heelRoll', 'footOut', 'footIn', 'toeRoll', 'toe_Aim',
                'footRock', 'ballRise', 'autoStretch', 'upStretch', 'lowStretch'
            ]
            for attr in roll_attrs:
                if mc.attributeQuery(attr, node=ik_ctrl, exists=True) and not mc.getAttr(f"{ik_ctrl}.{attr}", lock=True):
                    mc.setAttr(f"{ik_ctrl}.{attr}", 0.0)

        if ikh and mc.objExists(ikh):
            if mc.attributeQuery('twist', node=ikh, exists=True) and not mc.getAttr(f"{ikh}.twist", lock=True):
                if not mc.listConnections(f"{ikh}.twist", s=True, d=False):
                    mc.setAttr(f"{ikh}.twist", 0.0)

        # --- Step 3: Snap IK Root Controller (Position & Rotation) ---
        if ik_root and mc.objExists(ik_root) and fk_up_pos:
            mc.xform(ik_root, ws=True, t=fk_up_pos)
            if fk_up_rot and not mc.getAttr(f"{ik_root}.rotateX", lock=True):
                mc.xform(ik_root, ws=True, ro=fk_up_rot)
            modified_nodes.append(ik_root)

        # --- Step 4: Snap IK Controller & Apply Delta IK Handle Correction ---
        # (Must be done BEFORE Pole Vector to avoid dragging PV in Local Space)
        if ik_ctrl and mc.objExists(ik_ctrl) and fk_low_pos:
            if snap_rot:
                mc.xform(ik_ctrl, ws=True, ro=snap_rot)
            mc.xform(ik_ctrl, ws=True, t=fk_low_pos)
            mc.refresh()

            # Delta Correction: Compensate for rotatePivot offsets and foot roll group displacement
            if ikh and mc.objExists(ikh):
                current_ikh_pos = mc.xform(ikh, q=True, ws=True, t=True)
                delta = [fk_low_pos[i] - current_ikh_pos[i] for i in range(3)]
                delta_dist = math.sqrt(sum(x * x for x in delta))
                if delta_dist > 0.0001:
                    current_ctrl_pos = mc.xform(ik_ctrl, q=True, ws=True, t=True)
                    corrected_ctrl_pos = [current_ctrl_pos[i] + delta[i] for i in range(3)]
                    mc.xform(ik_ctrl, ws=True, t=corrected_ctrl_pos)
                    mc.refresh()

            modified_nodes.append(ik_ctrl)

        # --- Step 5: Snap Mid IK Controller (Double-IK Hind Leg) ---
        if mid_ik_ctrl and mc.objExists(mid_ik_ctrl) and mid_jnt and mc.objExists(mid_jnt):
            cls.match_transform_ws(mid_ik_ctrl, mid_jnt, pos=True, rot=True)
            modified_nodes.append(mid_ik_ctrl)

        # --- Step 6: Calculate and Snap Pole Vector (STRICTLY LAST STEP) ---
        # Snapping pov_ctrl after ik_ctrl guarantees it lands at the exact geometric position
        # without being dragged by any parent constraint on ankleIk_ctrl in Local space.
        if pov_ctrl and mc.objExists(pov_ctrl) and fk_up_pos and fk_mid_pos and fk_low_pos:
            v_base = _v_sub(fk_low_pos, fk_up_pos)
            v_mid = _v_sub(fk_mid_pos, fk_up_pos)
            base_len_sq = sum(x * x for x in v_base)

            curr_pv_pos = mc.xform(pov_ctrl, q=True, ws=True, t=True)
            curr_dist = math.sqrt(sum((curr_pv_pos[i] - fk_mid_pos[i]) ** 2 for i in range(3)))
            pv_dist = max(curr_dist, 25.0)

            if base_len_sq > 0.00001:
                proj_factor = sum(v_mid[i] * v_base[i] for i in range(3)) / base_len_sq
                p_proj = [fk_up_pos[i] + v_base[i] * proj_factor for i in range(3)]
                bend_dir = [fk_mid_pos[i] - p_proj[i] for i in range(3)]
                bend_len = math.sqrt(sum(x * x for x in bend_dir))
                if bend_len > 0.001:
                    bend_unit = [x / bend_len for x in bend_dir]
                    pv_pos = [fk_mid_pos[i] + bend_unit[i] * pv_dist for i in range(3)]
                else:
                    pv_pos = [fk_mid_pos[0], fk_mid_pos[1], fk_mid_pos[2] - pv_dist]
            else:
                pv_pos = [fk_mid_pos[0], fk_mid_pos[1], fk_mid_pos[2] - pv_dist]

            mc.xform(pov_ctrl, ws=True, t=pv_pos)
            mc.refresh()
            modified_nodes.append(pov_ctrl)

        if auto_key and modified_nodes:
            mc.setKeyframe(modified_nodes)

        return True

    @classmethod
    def switch_to_fk(cls, stick, auto_key=True):
        """Snaps FK controllers to match current IK pose, then sets FK_IK to 0.0 (FK Mode)."""
        success = cls.snap_fk_to_ik(stick, auto_key=auto_key)
        if not success:
            return False
        mc.setAttr(f"{stick}.FK_IK", 0.0)
        if auto_key:
            mc.setKeyframe(f"{stick}.FK_IK")
        return True

    @classmethod
    def switch_to_ik(cls, stick, auto_key=True):
        """Snaps IK controller & POV to match current FK pose, then sets FK_IK to 1.0 (IK Mode)."""
        success = cls.snap_ik_to_fk(stick, auto_key=auto_key)
        if not success:
            return False
        mc.setAttr(f"{stick}.FK_IK", 1.0)
        if auto_key:
            mc.setKeyframe(f"{stick}.FK_IK")
        return True

    @classmethod
    def snap_and_switch(cls, stick, auto_key=True):
        """
        Detects current mode, snaps the opposite chain, and flips the FK_IK attribute (0 <-> 1).
        """
        data = cls.get_stick_data(stick)
        if not data:
            mc.warning(f"Invalid stick controller: {stick}")
            return False

        current_val = mc.getAttr(f"{stick}.FK_IK")
        if current_val >= 0.5:
            # Currently IK -> Snapping FK to match IK, then switching to FK (0.0)
            return cls.switch_to_fk(stick, auto_key=auto_key)
        else:
            # Currently FK -> Snapping IK to match FK, then switching to IK (1.0)
            return cls.switch_to_ik(stick, auto_key=auto_key)

    @classmethod
    def get_timeline_range(cls):
        """
        Retrieves the active range from Maya's Time Slider selection,
        or falls back to the playback range min/max.
        Returns (start_frame, end_frame) as integers.
        """
        try:
            import maya.mel as mel
            g_slider = mel.eval('$tmpVar = $gPlayBackSlider')
            if g_slider and mc.timeControl(g_slider, exists=True):
                ra = mc.timeControl(g_slider, q=True, rangeArray=True)
                if ra and (ra[1] - ra[0]) > 1:
                    # In Maya timeControl, rangeArray returns [start, end+1]
                    return int(ra[0]), int(ra[1]) - 1
        except Exception:
            pass

        try:
            start_frame = int(mc.playbackOptions(q=True, minTime=True))
            end_frame = int(mc.playbackOptions(q=True, maxTime=True))
            return start_frame, end_frame
        except Exception:
            return 1, 24

    @classmethod
    def snap_fk_to_ik_range(cls, stick, start_frame, end_frame, progress_callback=None):
        """Snaps and keys FK controllers to match IK across range without altering FK_IK."""
        start_f = min(int(start_frame), int(end_frame))
        end_f = max(int(start_frame), int(end_frame))
        total_frames = end_f - start_f + 1
        orig_time = mc.currentTime(q=True)
        mc.undoInfo(openChunk=True)
        try:
            for f in range(start_f, end_f + 1):
                mc.currentTime(f, edit=True)
                mc.refresh()
                cls.snap_fk_to_ik(stick, auto_key=True)
                if progress_callback:
                    progress_callback(f, total_frames, 1)
            mc.currentTime(orig_time, edit=True)
            return True
        except Exception as e:
            mc.warning(f"Error during snap_fk_to_ik_range: {e}")
            return False
        finally:
            mc.undoInfo(closeChunk=True)

    @classmethod
    def snap_ik_to_fk_range(cls, stick, start_frame, end_frame, progress_callback=None):
        """Snaps and keys IK controllers to match FK across range without altering FK_IK."""
        start_f = min(int(start_frame), int(end_frame))
        end_f = max(int(start_frame), int(end_frame))
        total_frames = end_f - start_f + 1
        orig_time = mc.currentTime(q=True)
        mc.undoInfo(openChunk=True)
        try:
            for f in range(start_f, end_f + 1):
                mc.currentTime(f, edit=True)
                mc.refresh()
                cls.snap_ik_to_fk(stick, auto_key=True)
                if progress_callback:
                    progress_callback(f, total_frames, 1)
            mc.currentTime(orig_time, edit=True)
            return True
        except Exception as e:
            mc.warning(f"Error during snap_ik_to_fk_range: {e}")
            return False
        finally:
            mc.undoInfo(closeChunk=True)

    @classmethod
    def bake_to_fk_range(cls, stick, start_frame, end_frame, progress_callback=None):
        """
        Bakes FK matching across a frame range [start_frame, end_frame].
        Uses 2-pass architecture to prevent FK/IK attribute interpolation popping:
          Pass 1: Snaps FK controllers to match IK pose at each frame,
                  keyframing them with auto_key=True while FK_IK remains in IK mode.
          Pass 2: Sets and keyframes stick.FK_IK = 0.0 (FK) across all frames.
        """
        start_f = min(int(start_frame), int(end_frame))
        end_f = max(int(start_frame), int(end_frame))
        total_frames = end_f - start_f + 1

        orig_time = mc.currentTime(q=True)
        mc.undoInfo(openChunk=True)
        try:
            # Anchor key on stick.FK_IK at (start_f - 1) if keys exist before start_f
            try:
                min_playback = int(mc.playbackOptions(q=True, minTime=True))
                if start_f > min_playback:
                    has_prior = mc.keyframe(f"{stick}.FK_IK", q=True, time=(None, start_f - 1), keyframeCount=True)
                    if has_prior:
                        prev_val = mc.getAttr(f"{stick}.FK_IK", time=start_f - 1)
                        mc.setKeyframe(f"{stick}.FK_IK", time=start_f - 1, value=prev_val, outTangentType='step')
            except Exception:
                pass

            # Pass 1: Match and key FK controllers
            for f in range(start_f, end_f + 1):
                mc.currentTime(f, edit=True)
                mc.refresh()
                cls.snap_fk_to_ik(stick, auto_key=True)
                if progress_callback:
                    progress_callback(f, total_frames, 1)

            # Pass 2: Switch and key FK_IK = 0.0
            for f in range(start_f, end_f + 1):
                mc.currentTime(f, edit=True)
                mc.setAttr(f"{stick}.FK_IK", 0.0)
                mc.setKeyframe(f"{stick}.FK_IK", time=f, value=0.0, inTangentType='step', outTangentType='step')
                if progress_callback:
                    progress_callback(f, total_frames, 2)

            mc.currentTime(orig_time, edit=True)
            return True
        except Exception as e:
            mc.warning(f"Error during bake_to_fk_range: {e}")
            return False
        finally:
            mc.undoInfo(closeChunk=True)

    @classmethod
    def bake_to_ik_range(cls, stick, start_frame, end_frame, progress_callback=None):
        """
        Bakes IK matching across a frame range [start_frame, end_frame].
        Uses 2-pass architecture to prevent FK/IK attribute interpolation popping:
          Pass 1: Snaps IK controller, root, and PV to match FK pose at each frame,
                  keyframing them with auto_key=True while FK_IK remains in FK mode.
          Pass 2: Sets and keyframes stick.FK_IK = 1.0 (IK) across all frames.
        """
        start_f = min(int(start_frame), int(end_frame))
        end_f = max(int(start_frame), int(end_frame))
        total_frames = end_f - start_f + 1

        orig_time = mc.currentTime(q=True)
        mc.undoInfo(openChunk=True)
        try:
            # Anchor key on stick.FK_IK at (start_f - 1) if keys exist before start_f
            try:
                min_playback = int(mc.playbackOptions(q=True, minTime=True))
                if start_f > min_playback:
                    has_prior = mc.keyframe(f"{stick}.FK_IK", q=True, time=(None, start_f - 1), keyframeCount=True)
                    if has_prior:
                        prev_val = mc.getAttr(f"{stick}.FK_IK", time=start_f - 1)
                        mc.setKeyframe(f"{stick}.FK_IK", time=start_f - 1, value=prev_val, outTangentType='step')
            except Exception:
                pass

            # Pass 1: Match and key IK controllers
            for f in range(start_f, end_f + 1):
                mc.currentTime(f, edit=True)
                mc.refresh()
                cls.snap_ik_to_fk(stick, auto_key=True)
                if progress_callback:
                    progress_callback(f, total_frames, 1)

            # Pass 2: Switch and key FK_IK = 1.0
            for f in range(start_f, end_f + 1):
                mc.currentTime(f, edit=True)
                mc.setAttr(f"{stick}.FK_IK", 1.0)
                mc.setKeyframe(f"{stick}.FK_IK", time=f, value=1.0, inTangentType='step', outTangentType='step')
                if progress_callback:
                    progress_callback(f, total_frames, 2)

            mc.currentTime(orig_time, edit=True)
            return True
        except Exception as e:
            mc.warning(f"Error during bake_to_ik_range: {e}")
            return False
        finally:
            mc.undoInfo(closeChunk=True)

    @classmethod
    def bake_and_switch_range(cls, stick, start_frame, end_frame, progress_callback=None):
        """
        Detects mode at start_frame (or current frame), snaps opposite chain, and flips FK_IK across range.
        """
        data = cls.get_stick_data(stick)
        if not data:
            mc.warning(f"Invalid stick controller: {stick}")
            return False

        start_f = min(int(start_frame), int(end_frame))
        try:
            current_val = mc.getAttr(f"{stick}.FK_IK", time=start_f)
        except Exception:
            current_val = mc.getAttr(f"{stick}.FK_IK")

        if current_val >= 0.5:
            # Currently IK -> Bake to FK
            return cls.bake_to_fk_range(stick, start_frame, end_frame, progress_callback=progress_callback)
        else:
            # Currently FK -> Bake to IK
            return cls.bake_to_ik_range(stick, start_frame, end_frame, progress_callback=progress_callback)

    # Backward compatibility aliases
    bake_fk_to_ik_range = bake_to_ik_range
    bake_ik_to_fk_range = bake_to_fk_range


# =============================================================================
# PySide UI Window
# =============================================================================

class FkIkMatcherWindow(QtWidgets.QDialog):
    WINDOW_TITLE = f"NM FK/IK Matcher {__version__}"
    WINDOW_INSTANCE = None

    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(FkIkMatcherWindow, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumWidth(360)
        self.setWindowFlags(QtCore.Qt.Window)

        self._build_ui()
        self._populate_sticks()
        self._init_range_values()
        self._refresh_status()

    def _build_ui(self):
        # Native Maya Dark Theme Monochrome Stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #c8c8c8;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
            QGroupBox {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 14px;
                padding-top: 14px;
                font-weight: bold;
                color: #b0b0b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QComboBox {
                background-color: #222222;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 4px 8px;
                color: #d8d8d8;
                font-weight: normal;
            }
            QComboBox:hover {
                border: 1px solid #525252;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #222222;
                color: #d8d8d8;
                selection-background-color: #444444;
                border: 1px solid #3c3c3c;
            }
            QPushButton {
                background-color: #383838;
                border: 1px solid #484848;
                border-radius: 3px;
                padding: 6px 12px;
                color: #d0d0d0;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #484848;
                border-color: #606060;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #262626;
                border-color: #333333;
            }
            QCheckBox {
                color: #a8a8a8;
                spacing: 6px;
            }
            QCheckBox:hover {
                color: #d8d8d8;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                background-color: #222222;
                border: 1px solid #444444;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #525252;
                border: 1px solid #686868;
            }
            QSpinBox {
                background-color: #222222;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 3px 6px;
                color: #d8d8d8;
                font-weight: normal;
                min-width: 50px;
            }
            QSpinBox:hover {
                border: 1px solid #525252;
            }
            QSpinBox:focus {
                border: 1px solid #666666;
                background-color: #1a1a1a;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #333333;
                border: 1px solid #444444;
                width: 14px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #484848;
            }
            QSpinBox:disabled {
                background-color: #262626;
                color: #555555;
                border-color: #333333;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Header Title with Version (Clean Monochrome)
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("🐾  NM FK / IK Matcher")
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #dcdcdc;")
        header_layout.addWidget(title_label)

        version_badge = QtWidgets.QLabel(f" {__version__} ")
        version_badge.setStyleSheet(
            "background-color: #222222; color: #787878; font-size: 10px; "
            "font-weight: bold; border-radius: 2px; border: 1px solid #383838; padding: 1px 4px;"
        )
        header_layout.addWidget(version_badge)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # ---------------------------------------------------------------------
        # 1. Controller Selection Group
        # ---------------------------------------------------------------------
        sel_group = QtWidgets.QGroupBox("Target Stick Controller")
        sel_layout = QtWidgets.QVBoxLayout(sel_group)
        sel_layout.setSpacing(8)

        combo_layout = QtWidgets.QHBoxLayout()
        self.stick_combo = QtWidgets.QComboBox()
        self.stick_combo.currentIndexChanged.connect(self._on_stick_changed)
        combo_layout.addWidget(self.stick_combo, 1)

        self.pick_btn = QtWidgets.QPushButton("<< Pick")
        self.pick_btn.setToolTip("Pick selected controller from 3D Viewport")
        self.pick_btn.clicked.connect(self._on_pick_selected)
        combo_layout.addWidget(self.pick_btn)
        sel_layout.addLayout(combo_layout)

        # Status row
        status_layout = QtWidgets.QHBoxLayout()
        self.mode_badge = QtWidgets.QLabel("[ Mode: Unknown ]")
        self.mode_badge.setStyleSheet(
            "font-weight: bold; padding: 2px 6px; border-radius: 2px; "
            "background-color: #222222; color: #787878; border: 1px solid #383838;"
        )
        status_layout.addWidget(self.mode_badge)

        self.limb_type_label = QtWidgets.QLabel("Type: -")
        self.limb_type_label.setStyleSheet("color: #707070; font-style: italic;")
        status_layout.addWidget(self.limb_type_label, 1, QtCore.Qt.AlignRight)
        sel_layout.addLayout(status_layout)

        main_layout.addWidget(sel_group)

        # ---------------------------------------------------------------------
        # 2. Options Group (Animation & Range Baking)
        # ---------------------------------------------------------------------
        opt_group = QtWidgets.QGroupBox("Animation & Baking Options")
        opt_layout = QtWidgets.QVBoxLayout(opt_group)
        opt_layout.setSpacing(6)

        self.auto_key_check = QtWidgets.QCheckBox("Auto-Keyframe (Key matched controls & switch)")
        self.auto_key_check.setChecked(False)
        opt_layout.addWidget(self.auto_key_check)

        # Range Mode Checkbox
        self.range_check = QtWidgets.QCheckBox("Bake over Frame Range (Multi-frame transfer)")
        self.range_check.setChecked(False)
        self.range_check.toggled.connect(self._on_range_toggled)
        opt_layout.addWidget(self.range_check)

        # Range inputs container (active only when range_check is True)
        self.range_widget = QtWidgets.QWidget()
        range_layout = QtWidgets.QHBoxLayout(self.range_widget)
        range_layout.setContentsMargins(18, 2, 0, 2)
        range_layout.setSpacing(6)

        start_lbl = QtWidgets.QLabel("Start:")
        start_lbl.setStyleSheet("color: #a0a0a0;")
        range_layout.addWidget(start_lbl)

        self.start_spin = QtWidgets.QSpinBox()
        self.start_spin.setRange(-999999, 999999)
        self.start_spin.setValue(0)
        self.start_spin.valueChanged.connect(self._update_button_labels)
        range_layout.addWidget(self.start_spin)

        end_lbl = QtWidgets.QLabel("End:")
        end_lbl.setStyleSheet("color: #a0a0a0;")
        range_layout.addWidget(end_lbl)

        self.end_spin = QtWidgets.QSpinBox()
        self.end_spin.setRange(-999999, 999999)
        self.end_spin.setValue(10)
        self.end_spin.valueChanged.connect(self._update_button_labels)
        range_layout.addWidget(self.end_spin)

        self.get_range_btn = QtWidgets.QPushButton("Get Timeline")
        self.get_range_btn.setToolTip("Query highlighted range or playback min/max from Maya Time Slider")
        self.get_range_btn.clicked.connect(self._on_get_timeline_range)
        range_layout.addWidget(self.get_range_btn)

        opt_layout.addWidget(self.range_widget)
        self.range_widget.setEnabled(False)

        main_layout.addWidget(opt_group)

        # ---------------------------------------------------------------------
        # 3. Actions Group (Clean Maya Monochrome)
        # ---------------------------------------------------------------------
        act_group = QtWidgets.QGroupBox("Match & Switch Mode")
        act_layout = QtWidgets.QVBoxLayout(act_group)
        act_layout.setSpacing(8)

        pair_layout = QtWidgets.QHBoxLayout()
        self.to_fk_btn = QtWidgets.QPushButton("Switch to FK (Snap & Flip)")
        self.to_fk_btn.setStyleSheet("""
            QPushButton {
                background-color: #343434;
                border: 1px solid #484848;
                padding: 7px 10px;
                color: #c8c8c8;
            }
            QPushButton:hover {
                background-color: #424242;
                border-color: #5c5c5c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #242424;
            }
        """)
        self.to_fk_btn.setToolTip("Snaps FK controls to match current IK pose, then sets stick.FK_IK to 0.0 (FK Mode)")
        self.to_fk_btn.clicked.connect(self._on_switch_to_fk)
        pair_layout.addWidget(self.to_fk_btn)

        self.to_ik_btn = QtWidgets.QPushButton("Switch to IK (Snap & Flip)")
        self.to_ik_btn.setStyleSheet("""
            QPushButton {
                background-color: #343434;
                border: 1px solid #484848;
                padding: 7px 10px;
                color: #c8c8c8;
            }
            QPushButton:hover {
                background-color: #424242;
                border-color: #5c5c5c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #242424;
            }
        """)
        self.to_ik_btn.setToolTip("Snaps IK controller & POV to match current FK pose, then sets stick.FK_IK to 1.0 (IK Mode)")
        self.to_ik_btn.clicked.connect(self._on_switch_to_ik)
        pair_layout.addWidget(self.to_ik_btn)
        act_layout.addLayout(pair_layout)

        # Primary Snap & Switch Button (Maya Accent Highlight)
        self.switch_btn = QtWidgets.QPushButton("⚡ AUTO TOGGLE (Current 0 ↔ 1)")
        self.switch_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #f0f0f0;
                font-size: 11px;
                font-weight: bold;
                padding: 9px;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #525252;
                border-color: #707070;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
                border-color: #3c3c3c;
            }
        """)
        self.switch_btn.clicked.connect(self._on_snap_and_switch)
        act_layout.addWidget(self.switch_btn)

        main_layout.addWidget(act_group)

        # Status Footer
        self.footer_label = QtWidgets.QLabel("Ready")
        self.footer_label.setStyleSheet("color: #707070; font-size: 10px;")
        main_layout.addWidget(self.footer_label)

    # -------------------------------------------------------------------------
    # UI Slots & Helpers
    # -------------------------------------------------------------------------

    def _populate_sticks(self):
        self.stick_combo.blockSignals(True)
        self.stick_combo.clear()
        sticks = FkIkMatcherEngine.get_all_stick_controllers()
        for s in sticks:
            self.stick_combo.addItem(s)

        # Try to resolve from active selection
        active = FkIkMatcherEngine.resolve_stick_from_selection()
        if active and active in sticks:
            idx = self.stick_combo.findText(active)
            if idx >= 0:
                self.stick_combo.setCurrentIndex(idx)

        self.stick_combo.blockSignals(False)

    def _get_current_stick(self):
        return self.stick_combo.currentText().strip()

    def _on_stick_changed(self):
        self._refresh_status()

    def _on_pick_selected(self):
        active = FkIkMatcherEngine.resolve_stick_from_selection()
        if active:
            idx = self.stick_combo.findText(active)
            if idx >= 0:
                self.stick_combo.setCurrentIndex(idx)
            else:
                self.stick_combo.addItem(active)
                self.stick_combo.setCurrentIndex(self.stick_combo.count() - 1)
            self.footer_label.setText(f"Picked: {active}")
        else:
            self.footer_label.setText("No stick resolved from current selection.")
        self._refresh_status()

    def _refresh_status(self):
        stick = self._get_current_stick()
        if not stick or not mc.objExists(stick):
            self.mode_badge.setText("[ No Stick Selected ]")
            self.mode_badge.setStyleSheet("color: #888888; background-color: #333333;")
            self.limb_type_label.setText("Type: -")
            return

        data = FkIkMatcherEngine.get_stick_data(stick)
        if not data:
            return

        val = data['fk_ik']
        if val >= 0.5:
            self.mode_badge.setText(f"IK Mode ({val:.2f})")
            self.mode_badge.setStyleSheet(
                "color: #e0e0e0; background-color: #383838; border: 1px solid #505050; font-weight: bold; padding: 2px 6px; border-radius: 2px;"
            )
        else:
            self.mode_badge.setText(f"FK Mode ({val:.2f})")
            self.mode_badge.setStyleSheet(
                "color: #c0c0c0; background-color: #2b2b2b; border: 1px solid #424242; font-weight: bold; padding: 2px 6px; border-radius: 2px;"
            )

        self.limb_type_label.setText(f"Type: {data['limb_type']}")

    def _init_range_values(self):
        s, e = FkIkMatcherEngine.get_timeline_range()
        self.start_spin.blockSignals(True)
        self.end_spin.blockSignals(True)
        self.start_spin.setValue(s)
        self.end_spin.setValue(e)
        self.start_spin.blockSignals(False)
        self.end_spin.blockSignals(False)
        self._update_button_labels()

    def _on_range_toggled(self, checked):
        self.range_widget.setEnabled(checked)
        if checked:
            self.auto_key_check.setChecked(True)
            s, e = FkIkMatcherEngine.get_timeline_range()
            self.start_spin.blockSignals(True)
            self.end_spin.blockSignals(True)
            self.start_spin.setValue(s)
            self.end_spin.setValue(e)
            self.start_spin.blockSignals(False)
            self.end_spin.blockSignals(False)
        self._update_button_labels()

    def _on_get_timeline_range(self):
        s, e = FkIkMatcherEngine.get_timeline_range()
        self.start_spin.blockSignals(True)
        self.end_spin.blockSignals(True)
        self.start_spin.setValue(s)
        self.end_spin.setValue(e)
        self.start_spin.blockSignals(False)
        self.end_spin.blockSignals(False)
        self._update_button_labels()
        self.footer_label.setText(f"Timeline range queried: {s} - {e}")
        self.footer_label.setStyleSheet("color: #a0a0a0; font-size: 10px;")

    def _update_button_labels(self):
        if self.range_check.isChecked():
            s = self.start_spin.value()
            e = self.end_spin.value()
            self.to_fk_btn.setText(f"Bake to FK ({s} - {e})")
            self.to_fk_btn.setToolTip(f"Bake FK to match IK from frame {s} to {e} and set FK_IK = 0.0")
            self.to_ik_btn.setText(f"Bake to IK ({s} - {e})")
            self.to_ik_btn.setToolTip(f"Bake IK to match FK from frame {s} to {e} and set FK_IK = 1.0")
            self.switch_btn.setText(f"⚡ BAKE & TOGGLE ({s} - {e})")
            self.switch_btn.setToolTip(f"Auto-detect mode, bake opposite chain from frame {s} to {e}, and flip FK_IK")
        else:
            self.to_fk_btn.setText("Switch to FK (Snap & Flip)")
            self.to_fk_btn.setToolTip("Snaps FK controls to match current IK pose, then sets stick.FK_IK to 0.0 (FK Mode)")
            self.to_ik_btn.setText("Switch to IK (Snap & Flip)")
            self.to_ik_btn.setToolTip("Snaps IK controller & POV to match current FK pose, then sets stick.FK_IK to 1.0 (IK Mode)")
            self.switch_btn.setText("⚡ AUTO TOGGLE (Current 0 ↔ 1)")
            self.switch_btn.setToolTip("Auto-detects mode, snaps opposite chain, and flips FK_IK attribute on current frame")

    def _on_switch_to_fk(self):
        stick = self._get_current_stick()
        if not stick:
            return

        if self.range_check.isChecked():
            start_f = self.start_spin.value()
            end_f = self.end_spin.value()

            def progress(cur, tot, pass_num):
                self.footer_label.setText(f"Baking to FK: Frame {cur} (Pass {pass_num}/2)...")
                QtWidgets.QApplication.processEvents()

            success = FkIkMatcherEngine.bake_to_fk_range(stick, start_f, end_f, progress_callback=progress)
            if success:
                self.footer_label.setText(f"Successfully baked FK from frame {start_f} to {end_f} ({stick})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        else:
            auto_key = self.auto_key_check.isChecked()
            success = FkIkMatcherEngine.switch_to_fk(stick, auto_key=auto_key)
            if success:
                self.footer_label.setText(f"Switched to FK Mode: {stick}")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        self._refresh_status()

    def _on_switch_to_ik(self):
        stick = self._get_current_stick()
        if not stick:
            return

        if self.range_check.isChecked():
            start_f = self.start_spin.value()
            end_f = self.end_spin.value()

            def progress(cur, tot, pass_num):
                self.footer_label.setText(f"Baking to IK: Frame {cur} (Pass {pass_num}/2)...")
                QtWidgets.QApplication.processEvents()

            success = FkIkMatcherEngine.bake_to_ik_range(stick, start_f, end_f, progress_callback=progress)
            if success:
                self.footer_label.setText(f"Successfully baked IK from frame {start_f} to {end_f} ({stick})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        else:
            auto_key = self.auto_key_check.isChecked()
            success = FkIkMatcherEngine.switch_to_ik(stick, auto_key=auto_key)
            if success:
                self.footer_label.setText(f"Switched to IK Mode: {stick}")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        self._refresh_status()

    def _on_snap_fk_to_ik(self):
        stick = self._get_current_stick()
        if not stick:
            return

        if self.range_check.isChecked():
            start_f = self.start_spin.value()
            end_f = self.end_spin.value()

            def progress(cur, tot, pass_num):
                self.footer_label.setText(f"Snapping FK: Frame {cur}...")
                QtWidgets.QApplication.processEvents()

            success = FkIkMatcherEngine.snap_fk_to_ik_range(stick, start_f, end_f, progress_callback=progress)
            if success:
                self.footer_label.setText(f"Snapped FK from frame {start_f} to {end_f} ({stick})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        else:
            auto_key = self.auto_key_check.isChecked()
            success = FkIkMatcherEngine.snap_fk_to_ik(stick, auto_key=auto_key)
            if success:
                self.footer_label.setText(f"Snapped FK to match IK ({stick})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        self._refresh_status()

    def _on_snap_ik_to_fk(self):
        stick = self._get_current_stick()
        if not stick:
            return

        if self.range_check.isChecked():
            start_f = self.start_spin.value()
            end_f = self.end_spin.value()

            def progress(cur, tot, pass_num):
                self.footer_label.setText(f"Snapping IK: Frame {cur}...")
                QtWidgets.QApplication.processEvents()

            success = FkIkMatcherEngine.snap_ik_to_fk_range(stick, start_f, end_f, progress_callback=progress)
            if success:
                self.footer_label.setText(f"Snapped IK from frame {start_f} to {end_f} ({stick})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        else:
            auto_key = self.auto_key_check.isChecked()
            success = FkIkMatcherEngine.snap_ik_to_fk(stick, auto_key=auto_key)
            if success:
                self.footer_label.setText(f"Snapped IK to match FK ({stick})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        self._refresh_status()

    def _on_snap_and_switch(self):
        stick = self._get_current_stick()
        if not stick:
            return

        if self.range_check.isChecked():
            start_f = self.start_spin.value()
            end_f = self.end_spin.value()

            def progress(cur, tot, pass_num):
                self.footer_label.setText(f"Baking & Toggling: Frame {cur} (Pass {pass_num}/2)...")
                QtWidgets.QApplication.processEvents()

            success = FkIkMatcherEngine.bake_and_switch_range(stick, start_f, end_f, progress_callback=progress)
            if success:
                self.footer_label.setText(f"Successfully baked & switched {stick} ({start_f} - {end_f})")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        else:
            auto_key = self.auto_key_check.isChecked()
            success = FkIkMatcherEngine.snap_and_switch(stick, auto_key=auto_key)
            if success:
                self.footer_label.setText(f"Switched & Snapped: {stick}")
                self.footer_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            else:
                self.footer_label.setText(f"FAILED: Check Script Editor for details ({stick})")
                self.footer_label.setStyleSheet("color: #ff5555; font-size: 10px; font-weight: bold;")
        self._refresh_status()


def show_ui():
    """Launches or brings to front the singleton instance of FkIkMatcherWindow."""
    global _fk_ik_matcher_window_instance
    try:
        if _fk_ik_matcher_window_instance is not None:
            _fk_ik_matcher_window_instance.close()
            _fk_ik_matcher_window_instance.deleteLater()
    except Exception:
        pass

    _fk_ik_matcher_window_instance = FkIkMatcherWindow()
    _fk_ik_matcher_window_instance.show()
    return _fk_ik_matcher_window_instance


if __name__ == '__main__':
    show_ui()
