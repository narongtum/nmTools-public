# -*- coding: utf-8 -*-
"""
Module: eh_rotationReader.py
Author: Antigravity AI / nmTools
Description:
    Reusable rotation "read head" for corrective / helper-joint systems.

    Measures how far a joint has swung away from its REST orientation, relative to a
    reference frame (its DAG parent by default), and outputs a SIGNED angle in DEGREES
    on a single plug -- ready to drive push/corrective networks.

    Why not read node.rotateZ directly:
      - a raw Euler channel only sees ONE axis and is rotate-order / gimbal dependent
      - it misses rotation that arrives via jointOrient, constraints or IK
      - it mixes axial twist (bone rolling on its own axis) into the reading

    Why angleBetween instead of a quaternion swing-twist chain:
      - angleBetween.angle is already in DEGREES, so existing degree-based tuning values
        (triggerAngle, triggerStartAngle, pushSpeed) stay meaningful
      - axial twist does not move the aim vector at all, so twist is excluded for free
      - 5 nodes, and the graph reads plainly in the Node Editor months later

    Method:
        1. live aim vector = bone aim axis pushed through (node.world * ref.worldInverse)
        2. angleBetween(rest aim vector, live aim vector) -> .angle (degrees, unsigned 0-180)
           and .axis (the axis the swing happened around, in reference space)
        3. sign/plane projection = dot(.axis, sign_axis)  -> +1 one way, -1 the other,
           attenuating smoothly toward 0 for swings that happen off the chosen plane
        4. output = .angle * projection  -> signed degrees

Usage:
    from function.rigging.connection import eh_rotationReader as rdr
    reload(rdr)

    # --- 1. Basic: read how far a clavicle has swung, signed, in degrees --------------
    reader = rdr.eh_createRotationReader(
        node='clavRGT_bJnt',        # joint being measured
        ref_node=None,              # None = its DAG parent (usual choice)
        aim_axis='x',               # axis pointing DOWN THE BONE on clavRGT_bJnt
        sign_axis='z',              # axis IN PARENT SPACE defining the + direction
        name='clavSwing',
        side='RGT',
        attr_holder='clavRGT_ctrl') # optional read-only Channel Box display

    reader['plug']   # -> 'clavSwingReadSignedRGT_mdl.output', signed degrees, 0.0 at rest

    # --- 2. Feeding a push / corrective network --------------------------------------
    # The plug is a plain signed scalar in degrees, so it substitutes 1:1 for a raw
    # Euler channel anywhere a corrective system reads rotation:
    #
    #     trigger_plug = 'clavRGT_bJnt.rotateZ'        # before
    #     trigger_plug = reader['plug']                # after -- nothing else changes
    #
    # Degree-based tuning values (triggerAngle, triggerStartAngle, pushSpeed) keep the
    # same meaning, because the output is already in degrees.
    mc.connectAttr(reader['plug'], f"{some_mdl}.input1", force=True)

    # --- 3. Mirrored side -------------------------------------------------------------
    # Flip direction with the axis token itself; no separate direction multiplier needed.
    L_reader = rdr.eh_createRotationReader(
        node='clavLFT_bJnt', aim_axis='x', sign_axis='-z',
        name='clavSwing', side='LFT', attr_holder='clavLFT_ctrl')

    # --- 4. Choosing aim_axis / sign_axis --------------------------------------------
    # aim_axis  : the bone's own long axis. Rotation AROUND it (axial twist) is invisible
    #             to this reader by design. Get it from the joint's local rotation axes
    #             in the viewport (Display > Transform Display > Local Rotation Axes).
    # sign_axis : lives in ref_node's space, not the measured joint's. Pick the axis the
    #             swing rotates around -- for a clavicle lifting up/down under a spine
    #             joint that is usually the parent's Z. Wrong guess shows up immediately
    #             as a reading that stays near 0.0 while the joint clearly moves.

    # --- 5. Verifying in-scene --------------------------------------------------------
    #     mc.setAttr('clavRGT_ctrl.rotateZ', 0);   print(mc.getAttr(reader['plug']))  # ~0.0
    #     mc.setAttr('clavRGT_ctrl.rotateZ', 30);  print(mc.getAttr(reader['plug']))  # ~+30
    #     mc.setAttr('clavRGT_ctrl.rotateZ', -30); print(mc.getAttr(reader['plug']))  # ~-30
    #
    # Reading ~0.5 instead of ~30 means the degrees->radians unitConversion was not
    # neutralised (see step 7 below). Reading ~30 for BOTH directions means sign_axis is
    # perpendicular to the real swing axis. A reading far smaller than the joint's actual
    # rotation means the swing is off the sign_axis plane and is being projected onto it --
    # that attenuation is intended; re-pick sign_axis if it is not what you want.

Notes:
    - No rotateOrder anywhere: the whole chain is matrix / vector / axis-angle math, so
      changing the measured joint's rotateOrder later does not affect or break the reader.
      (angleBetween's `.euler` output WOULD carry an implied order -- it is deliberately
      unused here.)
    - Negative-scale mirroring flips matrix handedness and therefore the `.axis` direction;
      correct it with a signed sign_axis ('-z') rather than reworking the graph.
"""

import maya.cmds as mc
import maya.api.OpenMaya as om2

from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.base import core
reload(core)


def _axis_to_vector(axis_str, label):
    """
    #... Resolves an axis token ('x', 'y', 'z', optionally signed '-z') to a unit vector tuple.
    """
    clean = str(axis_str).lower().strip()
    negative = clean.startswith('-')
    clean = clean.lstrip('+-')

    table = {'x': (1.0, 0.0, 0.0), 'y': (0.0, 1.0, 0.0), 'z': (0.0, 0.0, 1.0)}
    if clean not in table:
        mc.error(f"[eh_rotationReader] Invalid {label} '{axis_str}'. Expected 'x', 'y', 'z' (optionally signed, e.g. '-z').")
        return None

    vec = table[clean]
    return tuple(-c for c in vec) if negative else vec


def eh_createRotationReader(
    node,
    ref_node=None,
    aim_axis='x',
    sign_axis='z',
    name=None,
    side='',
    prefix='',
    attr_holder=None,
    attr_name='readAngle',
):
    """
    #... Builds a signed swing-angle read head for `node` and returns the output plug.
    #... Output is in DEGREES, positive when `node` swings around `sign_axis` in the
    #... right-hand-rule positive direction, negative the other way, and exactly 0.0 at
    #... the rest pose captured when this function runs.

    Args:
        node (str): The joint/transform whose swing is measured (e.g. 'clavRGT_bJnt').
        ref_node (str, optional): Frame the swing is measured in. Defaults to node's DAG
            parent, which makes the reading independent of whole-character motion. Aborts
            if omitted and `node` has no parent.
        aim_axis (str): The axis pointing DOWN THE BONE on `node` ('x', 'y', 'z', signable).
            This is the axis the swing is measured away from; rotation around it (axial
            twist) is intentionally invisible to this reader. Default 'x'.
        sign_axis (str): Axis IN REFERENCE SPACE defining the positive swing direction
            ('x', 'y', 'z', signable -- use '-z' to flip for a mirrored side instead of
            adding a separate direction multiplier). Default 'z'.
        name (str, optional): Base name for created nodes. Defaults to `node` with a
            trailing '_bJnt'/'_jnt' suffix stripped.
        side (str): Side token appended to node names ('LFT', 'RGT', or '').
        prefix (str): Optional naming prefix.
        attr_holder (str, optional): Node given a read-only Channel Box display of the
            live reading. Skipped when None.
        attr_name (str): Name of that read-only display attr (default 'readAngle').

    Returns:
        dict: {'plug': signed-degrees output plug, plus every node created}
    """
    core.makeHeader(f"Start of eh_createRotationReader: {node}")

    #... 1. Validate prerequisites (Strict Fail-Fast)
    if not node or not mc.objExists(str(node)):
        mc.error(f"[eh_rotationReader] node '{node}' does not exist in scene! Aborting.")
        return None

    node = str(node)

    if ref_node is None:
        parents = mc.listRelatives(node, parent=True, fullPath=False)
        if not parents:
            mc.error(f"[eh_rotationReader] node '{node}' has no DAG parent to measure against, "
                     f"and ref_node was not supplied. Pass ref_node explicitly. Aborting.")
            return None
        ref_node = parents[0]
    else:
        if not mc.objExists(str(ref_node)):
            mc.error(f"[eh_rotationReader] ref_node '{ref_node}' does not exist in scene! Aborting.")
            return None
        ref_node = str(ref_node)

    if attr_holder is not None and not mc.objExists(str(attr_holder)):
        mc.error(f"[eh_rotationReader] attr_holder '{attr_holder}' does not exist in scene! Aborting.")
        return None

    aim_vector = _axis_to_vector(aim_axis, 'aim_axis')
    sign_vector = _axis_to_vector(sign_axis, 'sign_axis')
    if aim_vector is None or sign_vector is None:
        return None

    if name is None:
        name = node.replace('_bJnt', '').replace('_jnt', '')

    base = f"{prefix}{name}"

    #... 2. Capture the REST aim direction in reference space (static, python-side)
    node_world_rest = om2.MMatrix(mc.xform(node, q=True, ws=True, m=True))
    ref_world_rest = om2.MMatrix(mc.xform(ref_node, q=True, ws=True, m=True))
    local_rest = node_world_rest * ref_world_rest.inverse()

    rest_aim = (om2.MVector(aim_vector) * local_rest).normal()

    #... 3. Live local matrix of node relative to ref_node
    local_mmx = mc.createNode('multMatrix', name=f"{base}ReadLocal{side}_multMatrix")
    mc.connectAttr(f"{node}.worldMatrix[0]", f"{local_mmx}.matrixIn[0]", force=True)
    mc.connectAttr(f"{ref_node}.worldInverseMatrix[0]", f"{local_mmx}.matrixIn[1]", force=True)

    #... 4. Live aim vector = aim axis pushed through that matrix (rotation only, normalized)
    aim_vp = mc.createNode('vectorProduct', name=f"{base}ReadAim{side}_vecProd")
    mc.setAttr(f"{aim_vp}.operation", 3)  # Vector Matrix Product (ignores translation)
    mc.setAttr(f"{aim_vp}.normalizeOutput", 1)
    mc.setAttr(f"{aim_vp}.input1", aim_vector[0], aim_vector[1], aim_vector[2], type='double3')
    mc.connectAttr(f"{local_mmx}.matrixSum", f"{aim_vp}.matrix", force=True)

    #... 5. Swing magnitude in DEGREES (unsigned 0-180) + the axis it swung around
    angle_btw = mc.createNode('angleBetween', name=f"{base}ReadSwing{side}_angleBtw")
    mc.setAttr(f"{angle_btw}.vector1", rest_aim.x, rest_aim.y, rest_aim.z, type='double3')
    mc.connectAttr(f"{aim_vp}.output", f"{angle_btw}.vector2", force=True)

    #... 6. Project that swing axis onto sign_axis to recover direction. Dot Product writes its
    #... scalar to outputX only (outputY/Z stay 0.0). normalizeOutput stays 0 so the result is the
    #... cosine, not a hard +/-1: a swing exactly in the chosen plane reports its full angle, and
    #... one tilted off that plane is attenuated smoothly instead of snapping between branches.
    sign_vp = mc.createNode('vectorProduct', name=f"{base}ReadSign{side}_vecProd")
    mc.setAttr(f"{sign_vp}.operation", 1)  # Dot Product
    mc.setAttr(f"{sign_vp}.normalizeOutput", 0)
    mc.connectAttr(f"{angle_btw}.axis", f"{sign_vp}.input1", force=True)
    mc.setAttr(f"{sign_vp}.input2", sign_vector[0], sign_vector[1], sign_vector[2], type='double3')

    #... 7. Signed reading = magnitude * direction
    signed_mdl = mc.createNode('multDoubleLinear', name=f"{base}ReadSigned{side}_mdl")
    mc.connectAttr(f"{angle_btw}.angle", f"{signed_mdl}.input1", force=True)
    mc.connectAttr(f"{sign_vp}.outputX", f"{signed_mdl}.input2", force=True)

    #... angleBetween.angle is a doubleAngle plug while multDoubleLinear.input1 is a plain double,
    #... so Maya silently inserts a unitConversion that scales degrees into radians (x0.0174533).
    #... Force it back to 1.0 -- downstream tuning values (triggerAngle, pushSpeed) are in degrees.
    conversion_nodes = mc.listConnections(f"{signed_mdl}.input1", source=True, destination=False,
                                          type='unitConversion') or []
    for conv in conversion_nodes:
        mc.setAttr(f"{conv}.conversionFactor", 1.0)

    output_plug = f"{signed_mdl}.output"

    #... 8. Optional read-only Channel Box display
    if attr_holder is not None:
        attr_holder = str(attr_holder)
        if not mc.attributeQuery(attr_name, node=attr_holder, exists=True):
            mc.addAttr(attr_holder, ln=attr_name, at='float', k=False)
            mc.setAttr(f"{attr_holder}.{attr_name}", channelBox=True)
        mc.connectAttr(output_plug, f"{attr_holder}.{attr_name}", force=True)

    core.makeHeader(f"End of eh_createRotationReader: {output_plug}")

    return {
        'plug': output_plug,
        'node': node,
        'ref_node': ref_node,
        'local_mmx': local_mmx,
        'aim_vecprod': aim_vp,
        'angle_between': angle_btw,
        'sign_vecprod': sign_vp,
        'signed_mdl': signed_mdl,
        'rest_aim': (rest_aim.x, rest_aim.y, rest_aim.z),
        'unit_conversions': conversion_nodes,
    }
