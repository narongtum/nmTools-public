# -*- coding: utf-8 -*-
"""
===============================================================================
Module: eh_weightedHelperJnt.py
===============================================================================
Overview:
    Matrix-Based Single-Weight Parent/Driver Helper Joint System for Autodesk Maya.

    Built to replace the two-knob (driverRotWeight + parentRotWeight) rotation
    model used in eh_midpointHelper.py / eh_rbfMatrixHelper.py, which fought
    itself: Step 6 already isolates the driver's parent-independent rotation
    delta via parent.worldInverseMatrix cancellation (zero-drift, proven), but
    an extra Step 8 counter-compensation network was layered on top to fight
    Maya's automatic DAG parent->child inheritance a second time, producing
    unpredictable, non-linear quaternion composition results.

    Architecture here uses a SINGLE blendMatrix per motion channel:
      - inputMatrix (weight=0.0 endpoint)  = constant snap_local_rest matrix.
        Because it is constant and expressed in priorJnt's local space, it
        rides 1:1 with priorJnt's live rotation through ordinary DAG
        inheritance -> helper matches priorJnt exactly at weight=0.0.
      - target matrix (weight=1.0 endpoint) = driver_jnt's motion isolated
        from priorJnt via live parent.worldInverseMatrix cancellation
        (driver_offset * driver_jnt.worldMatrix * priorJnt.worldInverseMatrix)
        -> when re-composed by the DAG (local * priorJnt.worldMatrix) this
        yields driver_offset * driver_jnt.worldMatrix exactly -> helper
        matches driver_jnt exactly at weight=1.0.
      - blendMatrix does slerp on rotation and lerp on translation between
        these two, driven by two independent live attrs (positionWeight,
        rotationWeight), with NO separate counter-compensation network.

    Both endpoints reduce to the constant snap_local_rest matrix at build
    time (rest pose), so the helper sits exactly at snap_to regardless of
    weight values -- zero-drift is guaranteed by construction, not by a
    secondary correction pass.

    Restraint Space (restraint_jnt, required):
    A pure 2-endpoint (parent/driver) blend always commits the helper 100%
    to one of the two joints -- there is no way to hold it back. restraint_jnt
    adds a third target (e.g. a spine/chest joint sitting above priorJnt in
    the hierarchy) onto the SAME blendMatrix used for the parent/driver blend,
    isolated from priorJnt with the identical live worldInverseMatrix
    cancellation technique as the driver target. restraintWeight (0.0-1.0)
    then dampens the helper's positionWeight/rotationWeight result back
    toward restraint_jnt's own live motion instead of a frozen rest pose,
    so broader body motion (e.g. spine bend) is still respected while the
    helper avoids over-committing to priorJnt or driver_jnt alone.
    restraintWeight is never keyed directly -- it is always driven live off
    currentPush through its own remapValue (restraintDynamicMin/Max tune the
    output range), so folding priorJnt one way vs. the other can restrain by
    a different amount automatically.

    Corrective bulge push (currentPush -> dual remapValue S-curve -> push_axis)
    is carried over unchanged from eh_rbfMatrixHelper.py; that part was never
    the source of the parent-coupling problem.

Author: Antigravity AI / nmTools
===============================================================================
"""

import maya.cmds as mc
import maya.api.OpenMaya as om2

from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.base import core
reload(core)
from function.rigging.util import misc
reload(misc)
from function.rigging.util import generic_maya_dict as mnd
reload(mnd)
from function.rigging.connection import eh_rotationReader as rdr
reload(rdr)


def _resolve_rot_plug(node, axis_str):
    """
    #... Resolves rotation axis token ('rx', 'ry', 'rz', 'rotatex', etc.) to full Maya plug name.
    """
    if not node or not mc.objExists(str(node)):
        mc.error(f"[eh_weightedHelperJnt] Node '{node}' does not exist in scene for rotation trigger resolution!")
        return None
    axis_clean = str(axis_str).lower().strip()
    axis_map = {
        'rx': 'rotateX', 'rotatex': 'rotateX', 'x': 'rotateX',
        'ry': 'rotateY', 'rotatey': 'rotateY', 'y': 'rotateY',
        'rz': 'rotateZ', 'rotatez': 'rotateZ', 'z': 'rotateZ'
    }
    if axis_clean in axis_map:
        attr = axis_map[axis_clean]
        if not mc.attributeQuery(attr, node=node, exists=True):
            mc.error(f"[eh_weightedHelperJnt] Node '{node}' does not have rotation attribute '{attr}'!")
            return None
        return f"{node}.{attr}"
    mc.error(f"[eh_weightedHelperJnt] Invalid rotation axis '{axis_str}'. Expected 'rx', 'ry', or 'rz'.")
    return None


def eh_createWeightedHelperJnt(
    name='helper',
    side='LFT',
    priorJnt='clavLFT_bJnt',
    driver_jnt='upperArmLFT_bJnt',
    snap_to=None,
    position_weight=0.5,
    rotation_weight=0.5,
    restraint_jnt='',
    restraint_dynamic_min=0.1,
    restraint_dynamic_max=0.6,
    trigger_node=None,
    trigger_axis='rz',
    push_axis='y',
    push_distance=10.0,
    push_distance_neg=0.0,
    push_weight=1.0,
    trigger_start_angle=15.0,
    trigger_start_angle_neg=None,
    trigger_angle=45.0,
    trigger_angle_neg=None,
    trigger_direction='auto',
    bidirectional=True,
    attr_holder=None,
    radius=2.5,
    joint_color='white',
    charScale=1.0,
    prefix='',
    suffix='_bJnt',
    freeze_joint_orient=True,
):
    """
    #... Creates a matrix-driven helper joint DAG-parented under priorJnt (for outliner clarity
    #... only) whose translation and rotation are each controlled by a single 0.0-1.0 weight
    #... slider between priorJnt (0.0) and driver_jnt (1.0), plus a required restraint_jnt third
    #... space (e.g. spine/chest) that pulls the helper back via restraintWeight so it never has
    #... to commit 100% to either priorJnt or driver_jnt. Zero-drift rest pose is guaranteed for
    #... all three spaces, and an independent rotation-triggered corrective bulge push is included.

    Args:
        name (str): Base name of the helper joint (default 'helper')
        side (str): Side token ('LFT', 'RGT', or '')
        priorJnt (str): DAG parent joint for outliner placement (e.g. 'clavLFT_bJnt'). Also the
            positionWeight=0.0 / rotationWeight=0.0 endpoint.
        driver_jnt (str, optional): The positionWeight=1.0 / rotationWeight=1.0 endpoint
            (e.g. 'upperArmLFT_bJnt'). Can be None (helper then just rigidly follows priorJnt).
        snap_to (str, optional): Guide locator/joint for initial rest position. Defaults to driver_jnt.
        position_weight (float): Translation slide between priorJnt (0.0) and driver_jnt (1.0), default 0.5
        rotation_weight (float): Rotation slerp between priorJnt (0.0) and driver_jnt (1.0), default 0.5
        restraint_jnt (str): REQUIRED. Third reference joint ABOVE priorJnt in the hierarchy (e.g. a
            spine/chest joint) used to pull the helper back and dampen how far it follows the
            positionWeight/rotationWeight blend. Must exist in scene, or execution aborts.
        restraint_dynamic_min (float): restraintWeight value when currentPush is at its POSITIVE branch
            extreme (pushValuePos * pushWeight, default 0.1). Exposed as keyable attr
            `restraintDynamicMin` on attr_host.
        restraint_dynamic_max (float): restraintWeight value when currentPush is at its NEGATIVE branch
            extreme (pushValueNeg * pushWeight, default 0.6). Exposed as keyable attr
            `restraintDynamicMax` on attr_host. Linear ramp between the two (no S-curve smoothing).
            restraintWeight itself is ALWAYS computed live from currentPush via remapValue -- it is a
            read-only Channel Box display, never freely keyable (tune restraintDynamicMin/Max instead).
        trigger_node (str, optional): Node whose rotation triggers the push. Defaults to priorJnt.
        trigger_axis (str): Rotation axis triggering the push ('rx', 'ry', 'rz', default 'rz')
        push_axis (str): Local translation axis along which the joint pushes out ('x', 'y', 'z', default 'y')
        push_distance (float): Peak push distance at trigger_angle for positive rotation (default 10.0)
        push_distance_neg (float): Peak push distance at trigger_angle_neg for negative rotation (default 0.0)
        push_weight (float): Master push multiplier weight (default 1.0)
        trigger_start_angle (float): Angle threshold where positive push starts activating (default 15.0)
        trigger_start_angle_neg (float, optional): Negative direction activation threshold
        trigger_angle (float): Reference rotation angle in degrees where push_distance is reached (default 45.0)
        trigger_angle_neg (float, optional): Reference rotation angle for negative direction
        trigger_direction (str/float): Direction of trigger rotation ('auto', 1.0, -1.0)
        bidirectional (bool): If True (default), builds dual positive & negative push branches via remapValue
        attr_holder (str, optional): External node where Channel Box attributes live. Defaults to helper_jnt.
        radius (float): Joint display radius
        joint_color (str): Maya joint display color name
        charScale (float): Overall character scale multiplier
        prefix (str): Optional naming prefix
        suffix (str): Joint naming suffix (default '_bJnt')
        freeze_joint_orient (bool): Freeze rest rotation into jointOrient

    Returns:
        dict: Created nodes and helper joint name
    """
    core.makeHeader(f"Start of eh_createWeightedHelperJnt: {name}{side}")

    #... 1. Validate prerequisites (Strict Fail-Fast: halt immediately if ANY specified node is missing)
    if not priorJnt or not mc.objExists(str(priorJnt)):
        mc.error(f"[eh_weightedHelperJnt] priorJnt '{priorJnt}' does not exist in scene! Aborting execution.")
        return None

    if driver_jnt is not None:
        if not mc.objExists(str(driver_jnt)):
            mc.error(f"[eh_weightedHelperJnt] driver_jnt '{driver_jnt}' does not exist in scene! Check naming or set driver_jnt=None.")
            return None

    if not restraint_jnt or not mc.objExists(str(restraint_jnt)):
        mc.error(f"[eh_weightedHelperJnt] restraint_jnt is required and must exist in scene! Got '{restraint_jnt}'. Aborting execution.")
        return None

    if trigger_node is not None:
        if not mc.objExists(str(trigger_node)):
            mc.error(f"[eh_weightedHelperJnt] trigger_node '{trigger_node}' does not exist in scene! Check node naming or omit to default to priorJnt.")
            return None
        trig_node = trigger_node
    else:
        trig_node = priorJnt

    full_name = f"{prefix}{name}{side}{suffix}"

    if snap_to is not None:
        if not mc.objExists(str(snap_to)):
            mc.error(f"[eh_weightedHelperJnt] snap_to target '{snap_to}' does not exist in scene! Check guide locator/joint naming.")
            return None
        snap_target = str(snap_to)
    elif driver_jnt and mc.objExists(str(driver_jnt)):
        snap_target = str(driver_jnt)
    else:
        snap_target = str(priorJnt)

    if attr_holder is not None:
        if not mc.objExists(str(attr_holder)):
            mc.error(f"[eh_weightedHelperJnt] attr_holder '{attr_holder}' does not exist in scene! Check controller naming or set attr_holder=None.")
            return None

    # Resolve translation push axis
    trans_map = {
        'x': 'X', 'tx': 'X', 'translatex': 'X',
        'y': 'Y', 'ty': 'Y', 'translatey': 'Y',
        'z': 'Z', 'tz': 'Z', 'translatez': 'Z'
    }
    push_axis_clean = str(push_axis).lower().strip().replace('+', '').replace('-', '')
    if push_axis_clean not in trans_map:
        mc.error(f"[eh_weightedHelperJnt] Invalid push_axis '{push_axis}'. Expected 'x', 'y', 'z' (or 'tx', 'ty', 'tz').")
        return None
    axis_upper = trans_map[push_axis_clean]

    trigger_plug = _resolve_rot_plug(trig_node, trigger_axis)
    if not trigger_plug:
        return None

    # Resolve trigger direction (+1.0 or -1.0)
    if isinstance(trigger_direction, (int, float)):
        dir_sign = 1.0 if trigger_direction >= 0 else -1.0
    elif str(trigger_direction).lower() == 'positive':
        dir_sign = 1.0
    elif str(trigger_direction).lower() == 'negative':
        dir_sign = -1.0
    else:
        dir_sign = -1.0 if (side.upper() == 'RGT' or trigger_angle < 0) else 1.0

    abs_trigger_start_angle = max(0.0, float(trigger_start_angle))
    abs_trigger_start_angle_neg = max(0.0, float(trigger_start_angle_neg)) if trigger_start_angle_neg is not None else abs_trigger_start_angle
    abs_trigger_angle = abs(float(trigger_angle)) if abs(float(trigger_angle)) > 1e-4 else 45.0
    abs_trigger_angle_neg = abs(float(trigger_angle_neg)) if (trigger_angle_neg is not None and abs(float(trigger_angle_neg)) > 1e-4) else abs_trigger_angle

    #... 2. Create Helper Joint
    helper_jnt = mc.createNode('joint', name=full_name)

    mc.setAttr(f"{helper_jnt}.radius", radius * charScale)
    mc.setAttr(f"{helper_jnt}.segmentScaleCompensate", 0)

    try:
        jnt_dag = core.Dag(helper_jnt)
        jnt_dag.setJointColor(joint_color)
        jnt_dag.setJointOutlineColor('white')
    except Exception:
        pass

    #... 3. Calculate Space Matrices
    parent_mat_list = mc.xform(priorJnt, q=True, ws=True, m=True)
    parent_world = om2.MMatrix(parent_mat_list)
    parent_world_inv = parent_world.inverse()

    snap_mat_list = mc.xform(snap_target, q=True, ws=True, m=True)
    snap_world = om2.MMatrix(snap_mat_list)
    snap_local_rest = snap_world * parent_world_inv
    snap_matrix_list = list(snap_local_rest)

    #... 4. Position and parent under priorJnt (Strict World Match to snap_target)
    mc.delete(mc.parentConstraint(snap_target, helper_jnt, mo=False))

    if mc.attributeQuery('rotateOrder', node=snap_target, exists=True):
        snap_ro = mc.getAttr(f"{snap_target}.rotateOrder")
        mc.setAttr(f"{helper_jnt}.rotateOrder", snap_ro)

    mc.parent(helper_jnt, priorJnt)

    if freeze_joint_orient and mc.nodeType(helper_jnt) == 'joint':
        mc.makeIdentity(helper_jnt, apply=True, t=False, r=True, s=False)
    elif not freeze_joint_orient and mc.nodeType(helper_jnt) == 'joint':
        mc.setAttr(f"{helper_jnt}.jointOrient", 0.0, 0.0, 0.0)

    #... 5. Single blendMatrix drives BOTH translate and rotate between priorJnt (0.0) and driver_jnt (1.0)
    blend_node = mc.createNode('blendMatrix', name=f"{prefix}{name}Blend{side}_bmx")
    mc.setAttr(f"{blend_node}.inputMatrix", snap_matrix_list, type='matrix')

    #... 6. Driver Target: isolate driver_jnt's own motion from priorJnt via live worldInverseMatrix
    #... cancellation. At rest this reduces exactly to snap_local_rest (zero-drift by construction).
    if driver_jnt and mc.objExists(driver_jnt):
        driver_mat_list = mc.xform(driver_jnt, q=True, ws=True, m=True)
        driver_world = om2.MMatrix(driver_mat_list)
        driver_world_inv = driver_world.inverse()

        driver_offset = snap_world * driver_world_inv
        driver_offset_list = list(driver_offset)

        driver_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}DriverSpace{side}_mmx")
        mc.setAttr(f"{driver_mmx}.matrixIn[0]", driver_offset_list, type='matrix')
        mc.connectAttr(f"{driver_jnt}.worldMatrix[0]", f"{driver_mmx}.matrixIn[1]", force=True)
        mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{driver_mmx}.matrixIn[2]", force=True)

        mc.connectAttr(f"{driver_mmx}.matrixSum", f"{blend_node}.target[0].targetMatrix", force=True)
        mc.setAttr(f"{blend_node}.target[0].weight", 1.0)
        mc.setAttr(f"{blend_node}.target[0].shearWeight", 0.0)
        mc.setAttr(f"{blend_node}.target[0].scaleWeight", 0.0)

        mc.addAttr(helper_jnt, ln='weightSettings', at='enum', en='-------:', k=True)
        mc.setAttr(f"{helper_jnt}.weightSettings", lock=True)

        pos_w = 0.5 if position_weight is None else float(position_weight)
        rot_w = 0.5 if rotation_weight is None else float(rotation_weight)

        mc.addAttr(helper_jnt, ln='positionWeight', at='float', min=0.0, max=1.0, dv=pos_w, k=True)
        mc.addAttr(helper_jnt, ln='rotationWeight', at='float', min=0.0, max=1.0, dv=rot_w, k=True)

        mc.connectAttr(f"{helper_jnt}.positionWeight", f"{blend_node}.target[0].translateWeight", force=True)
        mc.connectAttr(f"{helper_jnt}.rotationWeight", f"{blend_node}.target[0].rotateWeight", force=True)

    #... 6b. Restraint Target (required third space): a joint ABOVE priorJnt (e.g. spine/chest) that
    #... pulls the helper back, dampening how far it follows the positionWeight/rotationWeight blend.
    #... Isolated from priorJnt using the exact same live worldInverseMatrix cancellation as the driver
    #... target above, so it is zero-drift at rest regardless of restraintWeight.
    restraint_target_index = 1 if (driver_jnt and mc.objExists(driver_jnt)) else 0

    restraint_mat_list = mc.xform(restraint_jnt, q=True, ws=True, m=True)
    restraint_world = om2.MMatrix(restraint_mat_list)
    restraint_world_inv = restraint_world.inverse()

    restraint_offset = snap_world * restraint_world_inv
    restraint_offset_list = list(restraint_offset)

    restraint_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}RestraintSpace{side}_mmx")
    mc.setAttr(f"{restraint_mmx}.matrixIn[0]", restraint_offset_list, type='matrix')
    mc.connectAttr(f"{restraint_jnt}.worldMatrix[0]", f"{restraint_mmx}.matrixIn[1]", force=True)
    mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{restraint_mmx}.matrixIn[2]", force=True)

    mc.connectAttr(f"{restraint_mmx}.matrixSum", f"{blend_node}.target[{restraint_target_index}].targetMatrix", force=True)
    mc.setAttr(f"{blend_node}.target[{restraint_target_index}].weight", 1.0)
    mc.setAttr(f"{blend_node}.target[{restraint_target_index}].shearWeight", 0.0)
    mc.setAttr(f"{blend_node}.target[{restraint_target_index}].scaleWeight", 0.0)

    #... restraintWeight is ALWAYS driven live from currentPush (Step 15, after the push chain exists
    #... below) -- read-only display here, never a freely keyable attr. Tune via restraintDynamicMin/Max.
    mc.addAttr(helper_jnt, ln='restraintWeight', at='float', k=False)
    mc.setAttr(f"{helper_jnt}.restraintWeight", channelBox=True)
    mc.connectAttr(f"{helper_jnt}.restraintWeight", f"{blend_node}.target[{restraint_target_index}].translateWeight", force=True)
    mc.connectAttr(f"{helper_jnt}.restraintWeight", f"{blend_node}.target[{restraint_target_index}].rotateWeight", force=True)

    #... 7. Bake-Safe TRS Decompose
    identity_mat = [1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0]
    try:
        mc.setAttr(f"{helper_jnt}.offsetParentMatrix", identity_mat, type='matrix')
    except Exception:
        pass

    decomp_node = mc.createNode('decomposeMatrix', name=f"{prefix}{name}Result{side}_dcmp")
    mc.connectAttr(f"{blend_node}.outputMatrix", f"{decomp_node}.inputMatrix", force=True)

    #... 8. Quaternion jointOrient Compensation (no separate parent counter-compensation network --
    #... Step 6 already fully resolves parent coupling for both weight endpoints)
    if not mc.pluginInfo('quatNodes', q=True, loaded=True):
        try:
            mc.loadPlugin('quatNodes', qt=False)
        except Exception:
            pass

    q2e_node = mc.createNode('quatToEuler', name=f"{prefix}{name}Result{side}_q2e")
    mc.connectAttr(f"{helper_jnt}.rotateOrder", f"{q2e_node}.inputRotateOrder", force=True)

    if mc.nodeType(helper_jnt) == 'joint':
        e2q_node = mc.createNode('eulerToQuat', name=f"{prefix}{name}JO{side}_e2q")
        inv_node = mc.createNode('quatInvert', name=f"{prefix}{name}JO{side}_inv")
        prod_node = mc.createNode('quatProd', name=f"{prefix}{name}JO{side}_prod")

        mc.connectAttr(f"{helper_jnt}.jointOrient", f"{e2q_node}.inputRotate", force=True)
        mc.connectAttr(f"{e2q_node}.outputQuat", f"{inv_node}.inputQuat", force=True)

        mc.connectAttr(f"{decomp_node}.outputQuat", f"{prod_node}.input1Quat", force=True)
        mc.connectAttr(f"{inv_node}.outputQuat", f"{prod_node}.input2Quat", force=True)
        mc.connectAttr(f"{prod_node}.outputQuat", f"{q2e_node}.inputQuat", force=True)
    else:
        mc.connectAttr(f"{decomp_node}.outputQuat", f"{q2e_node}.inputQuat", force=True)

    mc.connectAttr(f"{q2e_node}.outputRotate", f"{helper_jnt}.rotate", force=True)

    #... 9. Push Control Attributes in Channel Box
    if attr_holder and mc.objExists(attr_holder):
        attr_host = attr_holder
    else:
        attr_host = helper_jnt

    header_name = f"{name}PushSettings" if attr_host != helper_jnt else 'pushSettings'
    if not mc.attributeQuery(header_name, node=attr_host, exists=True):
        mc.addAttr(attr_host, ln=header_name, at='enum', en='-------:', k=True)
        mc.setAttr(f"{attr_host}.{header_name}", lock=True)

    if not mc.attributeQuery('pushValuePos', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='pushValuePos', at='float', dv=push_distance, k=True)
    else:
        mc.setAttr(f"{attr_host}.pushValuePos", push_distance)

    if bidirectional:
        if not mc.attributeQuery('pushValueNeg', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='pushValueNeg', at='float', dv=push_distance_neg, k=True)
        else:
            mc.setAttr(f"{attr_host}.pushValueNeg", push_distance_neg)

    if not mc.attributeQuery('pushWeight', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='pushWeight', at='float', min=0.0, dv=push_weight, k=True)
    else:
        mc.setAttr(f"{attr_host}.pushWeight", push_weight)

    if not mc.attributeQuery('triggerStartAnglePos', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='triggerStartAnglePos', at='float', min=0.0, dv=abs_trigger_start_angle, k=True)
    else:
        mc.setAttr(f"{attr_host}.triggerStartAnglePos", abs_trigger_start_angle)

    if not mc.attributeQuery('triggerAnglePos', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='triggerAnglePos', at='float', min=0.001, dv=abs_trigger_angle, k=True)
    else:
        mc.setAttr(f"{attr_host}.triggerAnglePos", abs_trigger_angle)

    if bidirectional:
        if not mc.attributeQuery('triggerStartAngleNeg', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='triggerStartAngleNeg', at='float', min=0.0, dv=abs_trigger_start_angle_neg, k=True)
        else:
            mc.setAttr(f"{attr_host}.triggerStartAngleNeg", abs_trigger_start_angle_neg)

        if not mc.attributeQuery('triggerAngleNeg', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='triggerAngleNeg', at='float', min=0.001, dv=abs_trigger_angle_neg, k=True)
        else:
            mc.setAttr(f"{attr_host}.triggerAngleNeg", abs_trigger_angle_neg)

    if not mc.attributeQuery('triggerDirection', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='triggerDirection', at='float', dv=dir_sign, k=True)
    else:
        mc.setAttr(f"{attr_host}.triggerDirection", dir_sign)

    if not mc.attributeQuery('currentPush', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='currentPush', at='float', k=False)
        mc.setAttr(f"{attr_host}.currentPush", channelBox=True)
    else:
        mc.setAttr(f"{attr_host}.currentPush", lock=False)
        mc.setAttr(f"{attr_host}.currentPush", channelBox=True)

    if not mc.attributeQuery('restraintDynamicMin', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='restraintDynamicMin', at='float', min=0.0, max=1.0, dv=restraint_dynamic_min, k=True)
    else:
        mc.setAttr(f"{attr_host}.restraintDynamicMin", restraint_dynamic_min)

    if not mc.attributeQuery('restraintDynamicMax', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='restraintDynamicMax', at='float', min=0.0, max=1.0, dv=restraint_dynamic_max, k=True)
    else:
        mc.setAttr(f"{attr_host}.restraintDynamicMax", restraint_dynamic_max)

    # If attr_host is on an external controller, mirror weight + push attributes onto it
    if attr_host != helper_jnt and driver_jnt and mc.objExists(driver_jnt):
        if not mc.attributeQuery('weightSettings', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='weightSettings', at='enum', en='-------:', k=True)
            mc.setAttr(f"{attr_host}.weightSettings", lock=True)

        mirror_weight_attrs = [('positionWeight', pos_w), ('rotationWeight', rot_w)]

        for w_attr, d_val in mirror_weight_attrs:
            if not mc.attributeQuery(w_attr, node=attr_host, exists=True):
                mc.addAttr(attr_host, ln=w_attr, at='float', min=0.0, max=1.0, dv=d_val, k=True)
            else:
                mc.setAttr(f"{attr_host}.{w_attr}", d_val)
            try:
                mc.connectAttr(f"{attr_host}.{w_attr}", f"{helper_jnt}.{w_attr}", force=True)
            except Exception:
                pass

        if not mc.attributeQuery('pushSettings', node=helper_jnt, exists=True):
            mc.addAttr(helper_jnt, ln='pushSettings', at='enum', en='-------:', k=True)
            mc.setAttr(f"{helper_jnt}.pushSettings", lock=True)

        mirror_push_attrs = ['pushValuePos', 'triggerStartAnglePos', 'triggerAnglePos', 'pushWeight', 'triggerDirection', 'restraintDynamicMin', 'restraintDynamicMax']
        if bidirectional:
            mirror_push_attrs.extend(['pushValueNeg', 'triggerStartAngleNeg', 'triggerAngleNeg'])

        for mirror_attr in mirror_push_attrs:
            if not mc.attributeQuery(mirror_attr, node=helper_jnt, exists=True):
                mc.addAttr(helper_jnt, ln=mirror_attr, at='float', k=True)
            try:
                mc.connectAttr(f"{attr_host}.{mirror_attr}", f"{helper_jnt}.{mirror_attr}", force=True)
            except Exception:
                pass

        if not mc.attributeQuery('currentPush', node=helper_jnt, exists=True):
            mc.addAttr(helper_jnt, ln='currentPush', at='float', k=False)
            mc.setAttr(f"{helper_jnt}.currentPush", channelBox=True)

    #... 10. Rotation Trigger Sign Multiplier Node
    dir_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}{name}TriggerSign{side}_mdl")
    mc.connectAttr(trigger_plug, f"{dir_mdl}.input1", force=True)
    mc.connectAttr(f"{attr_host}.triggerDirection", f"{dir_mdl}.input2", force=True)

    #... 11. Positive Branch: Remap Trigger Rotation through remapValue node (S-Curve & Threshold)
    remap_pos = mc.createNode('remapValue', name=f"{prefix}{name}PushPos{side}_remap")
    mc.connectAttr(f"{dir_mdl}.output", f"{remap_pos}.inputValue", force=True)
    mc.connectAttr(f"{attr_host}.triggerStartAnglePos", f"{remap_pos}.inputMin", force=True)
    mc.connectAttr(f"{attr_host}.triggerAnglePos", f"{remap_pos}.inputMax", force=True)
    mc.setAttr(f"{remap_pos}.outputMin", 0.0)
    mc.setAttr(f"{remap_pos}.outputMax", 1.0)
    try:
        mc.setAttr(f"{remap_pos}.value[0].value_Interp", 2)  # Spline smooth S-curve
        mc.setAttr(f"{remap_pos}.value[1].value_Interp", 2)  # Spline smooth S-curve
    except Exception:
        pass

    dist_pos = mc.createNode('multDoubleLinear', name=f"{prefix}{name}PushDistPos{side}_mdl")
    mc.connectAttr(f"{remap_pos}.outValue", f"{dist_pos}.input1", force=True)
    mc.connectAttr(f"{attr_host}.pushValuePos", f"{dist_pos}.input2", force=True)

    #... 12. Negative Branch: Remap Inverted Trigger Rotation through remapValue node
    if bidirectional:
        inv_neg = mc.createNode('multDoubleLinear', name=f"{prefix}{name}TriggerInvNeg{side}_mdl")
        mc.connectAttr(f"{dir_mdl}.output", f"{inv_neg}.input1", force=True)
        mc.setAttr(f"{inv_neg}.input2", -1.0)

        remap_neg = mc.createNode('remapValue', name=f"{prefix}{name}PushNeg{side}_remap")
        mc.connectAttr(f"{inv_neg}.output", f"{remap_neg}.inputValue", force=True)
        mc.connectAttr(f"{attr_host}.triggerStartAngleNeg", f"{remap_neg}.inputMin", force=True)
        mc.connectAttr(f"{attr_host}.triggerAngleNeg", f"{remap_neg}.inputMax", force=True)
        mc.setAttr(f"{remap_neg}.outputMin", 0.0)
        mc.setAttr(f"{remap_neg}.outputMax", 1.0)
        try:
            mc.setAttr(f"{remap_neg}.value[0].value_Interp", 2)  # Spline smooth S-curve
            mc.setAttr(f"{remap_neg}.value[1].value_Interp", 2)  # Spline smooth S-curve
        except Exception:
            pass

        dist_neg = mc.createNode('multDoubleLinear', name=f"{prefix}{name}PushDistNeg{side}_mdl")
        mc.connectAttr(f"{remap_neg}.outValue", f"{dist_neg}.input1", force=True)
        mc.connectAttr(f"{attr_host}.pushValueNeg", f"{dist_neg}.input2", force=True)

        sum_adl = mc.createNode('addDoubleLinear', name=f"{prefix}{name}PushSum{side}_adl")
        mc.connectAttr(f"{dist_pos}.output", f"{sum_adl}.input1", force=True)
        mc.connectAttr(f"{dist_neg}.output", f"{sum_adl}.input2", force=True)
        combined_push_plug = f"{sum_adl}.output"
    else:
        combined_push_plug = f"{dist_pos}.output"
        inv_neg = None
        remap_neg = None
        dist_neg = None
        sum_adl = None

    #... 13. Multiply Combined Push Offset by pushWeight
    weight_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}{name}PushWeight{side}_mdl")
    mc.connectAttr(combined_push_plug, f"{weight_mdl}.input1", force=True)
    mc.connectAttr(f"{attr_host}.pushWeight", f"{weight_mdl}.input2", force=True)

    try:
        mc.setAttr(f"{attr_host}.currentPush", lock=False)
        mc.connectAttr(f"{weight_mdl}.output", f"{attr_host}.currentPush", force=True)
        mc.setAttr(f"{attr_host}.currentPush", lock=True)
    except Exception:
        pass

    #... 14. Dynamic Restraint Weight: drive restraintWeight live from currentPush via remapValue.
    #... Positive branch extreme (pushValuePos * pushWeight) maps to restraintDynamicMin (less
    #... restraint), negative branch extreme (pushValueNeg * pushWeight) maps to restraintDynamicMax
    #... (more restraint) -- e.g. fold clav up = slide a little, fold clav down = slide a lot.
    pos_extreme_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}{name}RestraintExtremePos{side}_mdl")
    mc.connectAttr(f"{attr_host}.pushValuePos", f"{pos_extreme_mdl}.input1", force=True)
    mc.connectAttr(f"{attr_host}.pushWeight", f"{pos_extreme_mdl}.input2", force=True)

    restraint_dynamic_remap = mc.createNode('remapValue', name=f"{prefix}{name}RestraintDynamic{side}_remap")
    mc.connectAttr(f"{weight_mdl}.output", f"{restraint_dynamic_remap}.inputValue", force=True)
    mc.connectAttr(f"{pos_extreme_mdl}.output", f"{restraint_dynamic_remap}.inputMin", force=True)
    mc.setAttr(f"{restraint_dynamic_remap}.value[0].value_Interp", 1)  # Linear ramp (explicit, not left to node default)
    mc.setAttr(f"{restraint_dynamic_remap}.value[1].value_Interp", 1)  # Linear ramp (explicit, not left to node default)

    if bidirectional:
        neg_extreme_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}{name}RestraintExtremeNeg{side}_mdl")
        mc.connectAttr(f"{attr_host}.pushValueNeg", f"{neg_extreme_mdl}.input1", force=True)
        mc.connectAttr(f"{attr_host}.pushWeight", f"{neg_extreme_mdl}.input2", force=True)
        mc.connectAttr(f"{neg_extreme_mdl}.output", f"{restraint_dynamic_remap}.inputMax", force=True)
    else:
        neg_extreme_mdl = None
        mc.setAttr(f"{restraint_dynamic_remap}.inputMax", 0.0)

    mc.connectAttr(f"{attr_host}.restraintDynamicMin", f"{restraint_dynamic_remap}.outputMin", force=True)
    mc.connectAttr(f"{attr_host}.restraintDynamicMax", f"{restraint_dynamic_remap}.outputMax", force=True)

    mc.connectAttr(f"{restraint_dynamic_remap}.outValue", f"{helper_jnt}.restraintWeight", force=True)

    #... 15. Combine Base Translation and Corrective Push Offset
    adl_node = mc.createNode('addDoubleLinear', name=f"{prefix}{name}Push{axis_upper}{side}_adl")

    mc.connectAttr(f"{decomp_node}.outputTranslate{axis_upper}", f"{adl_node}.input1", force=True)
    mc.connectAttr(f"{weight_mdl}.output", f"{adl_node}.input2", force=True)
    mc.connectAttr(f"{adl_node}.output", f"{helper_jnt}.translate{axis_upper}", force=True)

    other_axes = [ax for ax in ['X', 'Y', 'Z'] if ax != axis_upper]
    for ax in other_axes:
        mc.connectAttr(f"{decomp_node}.outputTranslate{ax}", f"{helper_jnt}.translate{ax}", force=True)

    core.makeHeader(f"End of eh_createWeightedHelperJnt: {helper_jnt}")

    return {
        'helper_joint': helper_jnt,
        'blend_matrix': blend_node,
        'decompose_matrix': decomp_node,
        'trigger_mdl': dir_mdl,
        'remap_pos': remap_pos,
        'dist_pos': dist_pos,
        'inv_neg': inv_neg,
        'remap_neg': remap_neg,
        'dist_neg': dist_neg,
        'sum_adl': sum_adl,
        'weight_mdl': weight_mdl,
        'push_adl': adl_node,
        'restraint_dynamic_remap': restraint_dynamic_remap,
        'restraint_extreme_pos': pos_extreme_mdl,
        'restraint_extreme_neg': neg_extreme_mdl
    }


def eh_createSimpleWeightedHelper(
    name='helper',
    side='LFT',
    priorJnt='clavLFT_bJnt',
    driver_jnt='upperArmLFT_bJnt',
    restraint_jnt='',
    snap_to=None,
    trigger_axis='rz',
    use_swing_reader=False,
    aim_axis='x',
    position_weight=0.5,
    rotation_weight=0.5,
    push_axis='y',
    trigger_direction=1.0,
    push_speed=1.0,
    restraint_dynamic_min=0.1,
    restraint_dynamic_max=0.6,
    restraint_push_range=10.0,
    attr_holder=None,
    radius=2.5,
    joint_color='white',
    charScale=1.0,
    prefix='',
    suffix='_bJnt',
):
    """
    #... Simplified matrix-driven helper joint with four features only:
    #...   1. Read-only `priorRotation` attr displaying priorJnt's rotation on trigger_axis.
    #...   2. Independent `positionWeight` + `rotationWeight` attrs (0.0-1.0 each) driving
    #...      translateWeight and rotateWeight separately on a blendMatrix between priorJnt (0.0)
    #...      and driver_jnt (1.0) -- same two-slider layout as eh_createWeightedHelperJnt.
    #...   3. Simple one-directional push: as priorRotation moves in the direction set by
    #...      trigger_direction, helper pushes out along push_axis proportionally, scaled by the
    #...      keyable `pushSpeed` attr. Rotating back past rest clamps push to exactly 0 (never
    #...      pushes inward) -- no S-curve, no threshold angles, no bidirectional branches.
    #...   4. Restraint space (restraint_jnt, REQUIRED): a third blendMatrix target (e.g. a
    #...      spine/chest joint above priorJnt) that pulls the helper back via restraintWeight,
    #...      same isolation technique and same third-target pattern as eh_createWeightedHelperJnt.
    #...      restraintWeight is never keyed directly -- it is always driven live off THIS
    #...      function's own simple `currentPush` (push_speed_mdl output, not the S-curve one from
    #...      eh_createWeightedHelperJnt) through a linear remapValue: currentPush=0.0 maps to
    #...      restraintDynamicMin, currentPush=restraintPushRange maps to restraintDynamicMax.
    #...
    #... Extracted from eh_createWeightedHelperJnt for simpler use cases where the full dual-branch
    #... S-curve push system is overkill, while keeping restraint space (needed in production).
    #... The original function and eh_createWeightedHelperJnt are untouched.

    Args:
        name (str): Base name of the helper joint (default 'helper')
        side (str): Side token ('LFT', 'RGT', or '')
        priorJnt (str): DAG parent joint. Also the positionWeight=0.0 / rotationWeight=0.0 endpoint.
        driver_jnt (str): The positionWeight=1.0 / rotationWeight=1.0 endpoint (e.g. 'upperArmLFT_bJnt').
        restraint_jnt (str): REQUIRED. Third reference joint ABOVE priorJnt in the hierarchy (e.g. a
            spine/chest joint) that pulls the helper back and dampens how far it follows the
            positionWeight/rotationWeight blend. Must exist in scene, or execution aborts.
        snap_to (str): REQUIRED. Guide JOINT that dictates the helper's rest position -- joints only,
            a locator or plain transform aborts with mc.error, as does omitting it entirely (no
            driver_jnt fallback: the rest position must be explicitly authored). The helper joint
            also inherits this node's display `radius`.
        trigger_axis (str): Rotation axis of priorJnt to read ('rx', 'ry', 'rz', default 'rz').
            When use_swing_reader=True this also selects the reader's sign_axis ('rz' -> 'z').
        use_swing_reader (bool): False (default) reads priorJnt's raw Euler channel exactly as
            before -- existing call sites are completely unaffected. True swaps in
            eh_rotationReader's signed swing angle instead: rotateOrder-independent, blind to
            axial twist, and able to see rotation arriving via jointOrient / constraints / IK,
            none of which a raw Euler channel reports. Both paths output signed DEGREES, so
            pushSpeed and everything downstream keep the same meaning -- but the NUMBER differs
            in mixed-axis poses, so expect to retune pushSpeed on any helper you switch over.
            Safe to enable on one helper at a time and compare against the others in the same scene.
        aim_axis (str): Used only when use_swing_reader=True. The axis pointing DOWN THE BONE on
            priorJnt ('x', 'y', 'z', signable, default 'x'). Rotation around this axis (axial
            twist) is deliberately invisible to the reader.
        position_weight (float): Initial value for positionWeight attr (0.0=priorJnt, 1.0=driver_jnt, default 0.5)
        rotation_weight (float): Initial value for rotationWeight attr (0.0=priorJnt, 1.0=driver_jnt, default 0.5)
        push_axis (str): Local translate axis the helper pushes out along ('x', 'y', 'z', default 'y')
        trigger_direction (float): 1.0 or -1.0 -- sign applied to priorRotation before clamping to
            0 minimum, so only rotation in the chosen direction ever produces push (default 1.0)
        push_speed (float): Initial value for the keyable `pushSpeed` accelerator attr -- multiplies
            the clamped rotation directly into push distance (no separate angle-mapping, default 1.0).
            No hard min: negative values are valid and flip push direction along push_axis (magnitude
            still controls speed/distance) -- use a negative push_speed on sides where the local
            push_axis points the opposite way in world space (e.g. RGT mirrored vs LFT).
        restraint_dynamic_min (float): restraintWeight value when currentPush is at 0.0 (rest), default 0.1.
            Exposed as keyable attr `restraintDynamicMin`.
        restraint_dynamic_max (float): restraintWeight value when currentPush reaches restraintPushRange,
            default 0.6. Exposed as keyable attr `restraintDynamicMax`. Linear ramp between the two.
            restraintWeight itself is ALWAYS computed live from currentPush -- read-only display, never
            freely keyable (tune restraintDynamicMin/Max/restraintPushRange instead).
        restraint_push_range (float): currentPush magnitude at which restraintWeight reaches
            restraintDynamicMax (default 10.0). Exposed as keyable attr `restraintPushRange` -- retune
            if pushSpeed makes currentPush reach much larger or smaller magnitudes.
        attr_holder (str, optional): External node where Channel Box attributes live. Defaults to helper_jnt.
        radius (float): NOT APPLIED -- the helper joint's display radius is inherited from the snap
            target joint instead. Kept in the signature so existing call sites passing radius= keep working.
        joint_color (str): Maya joint display color name
        charScale (float): NOT APPLIED to radius -- the inherited radius is used raw, since the snap
            target joint already sits in the scene at its final scale. Kept for signature compatibility.
        prefix (str): Optional naming prefix
        suffix (str): Joint naming suffix (default '_bJnt')

    Returns:
        dict: Created nodes and helper joint name
    """
    core.makeHeader(f"Start of eh_createSimpleWeightedHelper: {name}{side}")

    #... 1. Validate prerequisites (Strict Fail-Fast)
    if not priorJnt or not mc.objExists(str(priorJnt)):
        mc.error(f"[eh_createSimpleWeightedHelper] priorJnt '{priorJnt}' does not exist in scene! Aborting.")
        return None

    if not driver_jnt or not mc.objExists(str(driver_jnt)):
        mc.error(f"[eh_createSimpleWeightedHelper] driver_jnt '{driver_jnt}' does not exist in scene! Aborting.")
        return None

    if not restraint_jnt or not mc.objExists(str(restraint_jnt)):
        mc.error(f"[eh_createSimpleWeightedHelper] restraint_jnt is required and must exist in scene! Got '{restraint_jnt}'. Aborting.")
        return None

    if attr_holder is not None:
        if not mc.objExists(str(attr_holder)):
            mc.error(f"[eh_createSimpleWeightedHelper] attr_holder '{attr_holder}' does not exist in scene! Aborting.")
            return None

    #... Resolve push_axis to translate channel letter
    trans_map = {
        'x': 'X', 'tx': 'X', 'translatex': 'X',
        'y': 'Y', 'ty': 'Y', 'translatey': 'Y',
        'z': 'Z', 'tz': 'Z', 'translatez': 'Z'
    }
    push_axis_clean = str(push_axis).lower().strip()
    if push_axis_clean not in trans_map:
        mc.error(f"[eh_createSimpleWeightedHelper] Invalid push_axis '{push_axis}'. Expected 'x', 'y', 'z'.")
        return None
    axis_upper = trans_map[push_axis_clean]

    #... Resolve snap target. snap_to is REQUIRED and must be a JOINT (not a locator/transform):
    #... it dictates the helper's rest position, and the helper also inherits its display radius
    #... from it -- no fallback guessing, fail-fast on missing/nonexistent/wrong node type.
    if not snap_to:
        mc.error(f"[eh_createSimpleWeightedHelper] snap_to is required -- it is the guide joint that dictates "
                 f"the helper's rest position and supplies its display radius. Aborting.")
        return None

    if not mc.objExists(str(snap_to)):
        mc.error(f"[eh_createSimpleWeightedHelper] snap_to target '{snap_to}' does not exist in scene! Aborting.")
        return None

    if mc.nodeType(str(snap_to)) != 'joint':
        mc.error(f"[eh_createSimpleWeightedHelper] snap_to '{snap_to}' is a '{mc.nodeType(str(snap_to))}', not a joint! "
                 f"snap_to accepts joints only (its radius is inherited by the helper joint). Aborting.")
        return None

    snap_target = str(snap_to)

    #... Inherit display radius straight from the snap target joint (raw value, NOT scaled by
    #... charScale -- the source joint already sits in the scene at its final scale).
    snap_radius = mc.getAttr(f"{snap_target}.radius")

    #... Resolve the rotation read head (all pure validation above is done by this point, so
    #... nothing has been created in the scene yet if any prerequisite failed).
    #...   use_swing_reader=False (default): read priorJnt's raw Euler channel, as before.
    #...   use_swing_reader=True: signed swing angle in degrees from eh_rotationReader --
    #...   rotateOrder-independent, blind to axial twist, and it also sees rotation arriving
    #...   via jointOrient / constraints / IK, which the raw channel cannot report.
    #... Both paths hand back a signed scalar in DEGREES, so everything downstream is identical.
    if use_swing_reader:
        sign_token = str(trigger_axis).lower().strip()
        if sign_token.startswith('rotate'):
            sign_token = sign_token[len('rotate'):]
        elif sign_token.startswith('r'):
            sign_token = sign_token[1:]

        swing_reader = rdr.eh_createRotationReader(
            node=priorJnt,
            aim_axis=aim_axis,
            sign_axis=sign_token,
            name=f"{name}Read",
            side=side,
            prefix=prefix)
        trigger_plug = swing_reader['plug']
    else:
        swing_reader = None
        trigger_plug = _resolve_rot_plug(priorJnt, trigger_axis)
        if not trigger_plug:
            return None

    full_name = f"{prefix}{name}{side}{suffix}"

    #... 2. Create Helper Joint
    helper_jnt = mc.createNode('joint', name=full_name)
    mc.setAttr(f"{helper_jnt}.radius", snap_radius)
    mc.setAttr(f"{helper_jnt}.segmentScaleCompensate", 0)

    try:
        jnt_dag = core.Dag(helper_jnt)
        jnt_dag.setJointColor(joint_color)
        jnt_dag.setJointOutlineColor('white')
    except Exception:
        pass

    #... 3. Calculate Space Matrices
    parent_mat_list = mc.xform(priorJnt, q=True, ws=True, m=True)
    parent_world = om2.MMatrix(parent_mat_list)
    parent_world_inv = parent_world.inverse()

    snap_mat_list = mc.xform(snap_target, q=True, ws=True, m=True)
    snap_world = om2.MMatrix(snap_mat_list)
    snap_local_rest = snap_world * parent_world_inv
    snap_matrix_list = list(snap_local_rest)

    #... 4. Position and parent under priorJnt (World Match to snap_target)
    mc.delete(mc.parentConstraint(snap_target, helper_jnt, mo=False))

    if mc.attributeQuery('rotateOrder', node=snap_target, exists=True):
        snap_ro = mc.getAttr(f"{snap_target}.rotateOrder")
        mc.setAttr(f"{helper_jnt}.rotateOrder", snap_ro)

    mc.parent(helper_jnt, priorJnt)

    #... Freeze rotation into jointOrient
    if mc.nodeType(helper_jnt) == 'joint':
        mc.makeIdentity(helper_jnt, apply=True, t=False, r=True, s=False)

    #... 5. blendMatrix: positionWeight/rotationWeight drive translate/rotate independently
    blend_node = mc.createNode('blendMatrix', name=f"{prefix}{name}Blend{side}_bmx")
    mc.setAttr(f"{blend_node}.inputMatrix", snap_matrix_list, type='matrix')

    #... 6. Driver Target: isolate driver_jnt motion from priorJnt via live worldInverseMatrix cancellation
    driver_mat_list = mc.xform(driver_jnt, q=True, ws=True, m=True)
    driver_world = om2.MMatrix(driver_mat_list)
    driver_world_inv = driver_world.inverse()

    driver_offset = snap_world * driver_world_inv
    driver_offset_list = list(driver_offset)

    driver_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}DriverSpace{side}_mmx")
    mc.setAttr(f"{driver_mmx}.matrixIn[0]", driver_offset_list, type='matrix')
    mc.connectAttr(f"{driver_jnt}.worldMatrix[0]", f"{driver_mmx}.matrixIn[1]", force=True)
    mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{driver_mmx}.matrixIn[2]", force=True)

    mc.connectAttr(f"{driver_mmx}.matrixSum", f"{blend_node}.target[0].targetMatrix", force=True)
    mc.setAttr(f"{blend_node}.target[0].weight", 1.0)
    mc.setAttr(f"{blend_node}.target[0].shearWeight", 0.0)
    mc.setAttr(f"{blend_node}.target[0].scaleWeight", 0.0)

    #... 6b. Restraint Target (required third space): a joint ABOVE priorJnt (e.g. spine/chest) that
    #... pulls the helper back, dampening how far it follows the positionWeight/rotationWeight blend.
    #... Isolated from priorJnt using the exact same live worldInverseMatrix cancellation as the driver
    #... target above, so it is zero-drift at rest regardless of restraintWeight.
    restraint_mat_list = mc.xform(restraint_jnt, q=True, ws=True, m=True)
    restraint_world = om2.MMatrix(restraint_mat_list)
    restraint_world_inv = restraint_world.inverse()

    restraint_offset = snap_world * restraint_world_inv
    restraint_offset_list = list(restraint_offset)

    restraint_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}RestraintSpace{side}_mmx")
    mc.setAttr(f"{restraint_mmx}.matrixIn[0]", restraint_offset_list, type='matrix')
    mc.connectAttr(f"{restraint_jnt}.worldMatrix[0]", f"{restraint_mmx}.matrixIn[1]", force=True)
    mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{restraint_mmx}.matrixIn[2]", force=True)

    mc.connectAttr(f"{restraint_mmx}.matrixSum", f"{blend_node}.target[1].targetMatrix", force=True)
    mc.setAttr(f"{blend_node}.target[1].weight", 1.0)
    mc.setAttr(f"{blend_node}.target[1].shearWeight", 0.0)
    mc.setAttr(f"{blend_node}.target[1].scaleWeight", 0.0)

    #... restraintWeight is ALWAYS driven live from currentPush (Step 8c, after the simple push chain
    #... exists below) -- read-only display here, never a freely keyable attr.
    mc.addAttr(helper_jnt, ln='restraintWeight', at='float', k=False)
    mc.setAttr(f"{helper_jnt}.restraintWeight", channelBox=True)
    mc.connectAttr(f"{helper_jnt}.restraintWeight", f"{blend_node}.target[1].translateWeight", force=True)
    mc.connectAttr(f"{helper_jnt}.restraintWeight", f"{blend_node}.target[1].rotateWeight", force=True)

    #... 7. positionWeight + rotationWeight: two independent knobs, same layout as eh_createWeightedHelperJnt
    pos_w = max(0.0, min(1.0, float(position_weight)))
    rot_w = max(0.0, min(1.0, float(rotation_weight)))

    mc.addAttr(helper_jnt, ln='positionWeight', at='float', min=0.0, max=1.0, dv=pos_w, k=True)
    mc.addAttr(helper_jnt, ln='rotationWeight', at='float', min=0.0, max=1.0, dv=rot_w, k=True)
    mc.connectAttr(f"{helper_jnt}.positionWeight", f"{blend_node}.target[0].translateWeight", force=True)
    mc.connectAttr(f"{helper_jnt}.rotationWeight", f"{blend_node}.target[0].rotateWeight", force=True)

    #... 8. priorRotation attr: read-only display of priorJnt rotation on trigger_axis
    mc.addAttr(helper_jnt, ln='priorRotation', at='float', k=False)
    mc.setAttr(f"{helper_jnt}.priorRotation", channelBox=True)
    mc.connectAttr(trigger_plug, f"{helper_jnt}.priorRotation", force=True)

    #... 8b. Simple one-directional push: sign the rotation by triggerDirection, clamp negative to
    #... 0 (never pushes past rest in the wrong direction), multiply by pushSpeed, done. No angle
    #... thresholds, no S-curve, no bidirectional branches. pushSpeed has NO hard min -- negative
    #... values are valid and intentional (mirrors eh_createWeightedHelperJnt's signed push_distance
    #... convention) for sides where the local push_axis points the opposite way in world space
    #... (e.g. RGT vs LFT mirroring); magnitude still controls speed/distance, sign controls direction.
    mc.addAttr(helper_jnt, ln='triggerDirection', at='float', dv=float(trigger_direction), k=True)
    mc.addAttr(helper_jnt, ln='pushSpeed', at='float', dv=float(push_speed), k=True)
    mc.addAttr(helper_jnt, ln='currentPush', at='float', k=False)
    mc.setAttr(f"{helper_jnt}.currentPush", channelBox=True)

    push_dir_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}{name}PushDir{side}_mdl")
    mc.connectAttr(trigger_plug, f"{push_dir_mdl}.input1", force=True)
    mc.connectAttr(f"{helper_jnt}.triggerDirection", f"{push_dir_mdl}.input2", force=True)

    push_clamp = mc.createNode('clamp', name=f"{prefix}{name}PushClamp{side}_cmp")
    mc.connectAttr(f"{push_dir_mdl}.output", f"{push_clamp}.inputR", force=True)
    mc.setAttr(f"{push_clamp}.minR", 0.0)
    mc.setAttr(f"{push_clamp}.maxR", 999999.0)

    push_speed_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}{name}PushSpeed{side}_mdl")
    mc.connectAttr(f"{push_clamp}.outputR", f"{push_speed_mdl}.input1", force=True)
    mc.connectAttr(f"{helper_jnt}.pushSpeed", f"{push_speed_mdl}.input2", force=True)

    mc.connectAttr(f"{push_speed_mdl}.output", f"{helper_jnt}.currentPush", force=True)

    #... 8c. Dynamic Restraint Weight: drive restraintWeight live from THIS function's own simple
    #... currentPush via a linear remapValue -- currentPush=0.0 (rest) maps to restraintDynamicMin,
    #... currentPush=restraintPushRange maps to restraintDynamicMax. No S-curve (keeps parity with
    #... the simple one-directional push above, unlike eh_createWeightedHelperJnt's dual-branch version).
    mc.addAttr(helper_jnt, ln='restraintDynamicMin', at='float', min=0.0, max=1.0, dv=max(0.0, min(1.0, float(restraint_dynamic_min))), k=True)
    mc.addAttr(helper_jnt, ln='restraintDynamicMax', at='float', min=0.0, max=1.0, dv=max(0.0, min(1.0, float(restraint_dynamic_max))), k=True)
    mc.addAttr(helper_jnt, ln='restraintPushRange', at='float', min=0.001, dv=max(0.001, float(restraint_push_range)), k=True)

    restraint_dynamic_remap = mc.createNode('remapValue', name=f"{prefix}{name}RestraintDynamic{side}_remap")
    mc.connectAttr(f"{push_speed_mdl}.output", f"{restraint_dynamic_remap}.inputValue", force=True)
    mc.setAttr(f"{restraint_dynamic_remap}.inputMin", 0.0)
    mc.connectAttr(f"{helper_jnt}.restraintPushRange", f"{restraint_dynamic_remap}.inputMax", force=True)
    mc.connectAttr(f"{helper_jnt}.restraintDynamicMin", f"{restraint_dynamic_remap}.outputMin", force=True)
    mc.connectAttr(f"{helper_jnt}.restraintDynamicMax", f"{restraint_dynamic_remap}.outputMax", force=True)
    mc.setAttr(f"{restraint_dynamic_remap}.value[0].value_Interp", 1)  # Linear ramp (explicit, not left to node default)
    mc.setAttr(f"{restraint_dynamic_remap}.value[1].value_Interp", 1)  # Linear ramp (explicit, not left to node default)

    mc.connectAttr(f"{restraint_dynamic_remap}.outValue", f"{helper_jnt}.restraintWeight", force=True)

    #... 9. Mirror attrs to attr_holder if external controller specified
    if attr_holder and mc.objExists(attr_holder):
        attr_host = str(attr_holder)

        for wt_attr, wt_val in (('positionWeight', pos_w), ('rotationWeight', rot_w)):
            if not mc.attributeQuery(wt_attr, node=attr_host, exists=True):
                mc.addAttr(attr_host, ln=wt_attr, at='float', min=0.0, max=1.0, dv=wt_val, k=True)
            mc.connectAttr(f"{attr_host}.{wt_attr}", f"{helper_jnt}.{wt_attr}", force=True)

        if not mc.attributeQuery('priorRotation', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='priorRotation', at='float', k=False)
            mc.setAttr(f"{attr_host}.priorRotation", channelBox=True)
        mc.connectAttr(trigger_plug, f"{attr_host}.priorRotation", force=True)

        for w_attr, d_val, w_kwargs in (
            ('triggerDirection', float(trigger_direction), {}),
            ('pushSpeed', float(push_speed), {}),
            ('restraintDynamicMin', max(0.0, min(1.0, float(restraint_dynamic_min))), {'min': 0.0, 'max': 1.0}),
            ('restraintDynamicMax', max(0.0, min(1.0, float(restraint_dynamic_max))), {'min': 0.0, 'max': 1.0}),
            ('restraintPushRange', max(0.001, float(restraint_push_range)), {'min': 0.001}),
        ):
            if not mc.attributeQuery(w_attr, node=attr_host, exists=True):
                mc.addAttr(attr_host, ln=w_attr, at='float', dv=d_val, k=True, **w_kwargs)
            mc.connectAttr(f"{attr_host}.{w_attr}", f"{helper_jnt}.{w_attr}", force=True)

        if not mc.attributeQuery('currentPush', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='currentPush', at='float', k=False)
            mc.setAttr(f"{attr_host}.currentPush", channelBox=True)
        mc.connectAttr(f"{push_speed_mdl}.output", f"{attr_host}.currentPush", force=True)

        if not mc.attributeQuery('restraintWeight', node=attr_host, exists=True):
            mc.addAttr(attr_host, ln='restraintWeight', at='float', k=False)
            mc.setAttr(f"{attr_host}.restraintWeight", channelBox=True)
        mc.connectAttr(f"{helper_jnt}.restraintWeight", f"{attr_host}.restraintWeight", force=True)

    #... 10. Bake-Safe TRS Decompose (no offsetParentMatrix dependency)
    identity_mat = [1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0]
    try:
        mc.setAttr(f"{helper_jnt}.offsetParentMatrix", identity_mat, type='matrix')
    except Exception:
        pass

    decomp_node = mc.createNode('decomposeMatrix', name=f"{prefix}{name}Result{side}_dcmp")
    mc.connectAttr(f"{blend_node}.outputMatrix", f"{decomp_node}.inputMatrix", force=True)

    #... 11. Quaternion jointOrient Compensation
    if not mc.pluginInfo('quatNodes', q=True, loaded=True):
        try:
            mc.loadPlugin('quatNodes', qt=False)
        except Exception:
            pass

    q2e_node = mc.createNode('quatToEuler', name=f"{prefix}{name}Result{side}_q2e")
    mc.connectAttr(f"{helper_jnt}.rotateOrder", f"{q2e_node}.inputRotateOrder", force=True)

    if mc.nodeType(helper_jnt) == 'joint':
        e2q_node = mc.createNode('eulerToQuat', name=f"{prefix}{name}JO{side}_e2q")
        inv_node = mc.createNode('quatInvert', name=f"{prefix}{name}JO{side}_inv")
        prod_node = mc.createNode('quatProd', name=f"{prefix}{name}JO{side}_prod")

        mc.connectAttr(f"{helper_jnt}.jointOrient", f"{e2q_node}.inputRotate", force=True)
        mc.connectAttr(f"{e2q_node}.outputQuat", f"{inv_node}.inputQuat", force=True)

        mc.connectAttr(f"{decomp_node}.outputQuat", f"{prod_node}.input1Quat", force=True)
        mc.connectAttr(f"{inv_node}.outputQuat", f"{prod_node}.input2Quat", force=True)
        mc.connectAttr(f"{prod_node}.outputQuat", f"{q2e_node}.inputQuat", force=True)
    else:
        mc.connectAttr(f"{decomp_node}.outputQuat", f"{q2e_node}.inputQuat", force=True)

    #... 12. Connect final TRS into helper joint. push_axis channel gets the base translate PLUS
    #... the simple push offset; the other two axes connect straight from decomp_node.
    mc.connectAttr(f"{q2e_node}.outputRotate", f"{helper_jnt}.rotate", force=True)

    push_adl = mc.createNode('addDoubleLinear', name=f"{prefix}{name}Push{axis_upper}{side}_adl")
    mc.connectAttr(f"{decomp_node}.outputTranslate{axis_upper}", f"{push_adl}.input1", force=True)
    mc.connectAttr(f"{push_speed_mdl}.output", f"{push_adl}.input2", force=True)
    mc.connectAttr(f"{push_adl}.output", f"{helper_jnt}.translate{axis_upper}", force=True)

    for ax in [a for a in ('X', 'Y', 'Z') if a != axis_upper]:
        mc.connectAttr(f"{decomp_node}.outputTranslate{ax}", f"{helper_jnt}.translate{ax}", force=True)

    core.makeHeader(f"End of eh_createSimpleWeightedHelper: {helper_jnt}")

    return {
        'helper_joint': helper_jnt,
        'blend_matrix': blend_node,
        'driver_mmx': driver_mmx,
        'restraint_mmx': restraint_mmx,
        'restraint_dynamic_remap': restraint_dynamic_remap,
        'decompose_matrix': decomp_node,
        'push_clamp': push_clamp,
        'push_speed_mdl': push_speed_mdl,
        'push_adl': push_adl,
        'swing_reader': swing_reader,
    }


def eh_createChainWeightedHelper(
    name='helper',
    side='LFT',
    grandparentJnt='upperBody_jnt',
    priorJnt='clavLFT_bJnt',
    driver_jnt='upperArmLFT_bJnt',
    snap_to=None,
    prior_weight=0.5,
    driver_weight=0.5,
    attr_holder=None,
    radius=2.5,
    joint_color='white',
    charScale=1.0,
    prefix='',
    suffix='_bJnt',
):
    """
    #... Two INDEPENDENT damping weights along a 3-joint chain (grandparentJnt -> priorJnt ->
    #... driver_jnt), instead of a single priorJnt<->driver_jnt slider:
    #...   - priorWeight (0.0-1.0): how much of priorJnt's OWN rotation/translation (measured
    #...     relative to grandparentJnt, the stable reference) the helper inherits.
    #...   - driverWeight (0.0-1.0): how much of driver_jnt's OWN rotation/translation (measured
    #...     relative to priorJnt) the helper inherits.
    #... Rotating ONLY priorJnt now visibly moves the helper by priorWeight's amount, without
    #... needing driver_jnt to move at all (unlike positionWeight/rotationWeight in
    #... eh_createSimpleWeightedHelper, which only differ from 0% if driver_jnt moves
    #... independently of priorJnt).
    #...
    #... Both weights are isolated using the same live worldInverseMatrix cancellation technique
    #... proven elsewhere in this module, chained in two stages (prior-vs-grandparent, then
    #... driver-vs-prior re-attached to the DAMPENED prior frame), then localized once against
    #... priorJnt (the real DAG parent) at the very end. Zero-drift at rest holds for ANY
    #... combination of priorWeight/driverWeight by construction (verified algebraically: every
    #... stage collapses to its rest matrix when live == rest, regardless of blend weight).

    Args:
        name (str): Base name of the helper joint (default 'helper')
        side (str): Side token ('LFT', 'RGT', or '')
        grandparentJnt (str): Stable reference joint ABOVE priorJnt (e.g. 'upperBody_jnt').
            priorJnt's "own" rotation is measured relative to this.
        priorJnt (str): DAG parent joint for outliner placement (e.g. 'clavLFT_bJnt'). Also the
            priorWeight=0.0 anchor.
        driver_jnt (str): Child joint whose own motion (relative to priorJnt) is weighted by
            driverWeight (e.g. 'upperArmLFT_bJnt').
        snap_to (str, optional): Guide locator/joint for initial rest position. Defaults to driver_jnt.
        prior_weight (float): Initial value for priorWeight attr (0.0-1.0, default 0.5)
        driver_weight (float): Initial value for driverWeight attr (0.0-1.0, default 0.5)
        attr_holder (str, optional): External node where Channel Box attributes live. Defaults to helper_jnt.
        radius (float): Joint display radius
        joint_color (str): Maya joint display color name
        charScale (float): Overall character scale multiplier
        prefix (str): Optional naming prefix
        suffix (str): Joint naming suffix (default '_bJnt')

    Returns:
        dict: Created nodes and helper joint name
    """
    core.makeHeader(f"Start of eh_createChainWeightedHelper: {name}{side}")

    #... 1. Validate prerequisites (Strict Fail-Fast)
    if not grandparentJnt or not mc.objExists(str(grandparentJnt)):
        mc.error(f"[eh_createChainWeightedHelper] grandparentJnt '{grandparentJnt}' does not exist in scene! Aborting.")
        return None

    if not priorJnt or not mc.objExists(str(priorJnt)):
        mc.error(f"[eh_createChainWeightedHelper] priorJnt '{priorJnt}' does not exist in scene! Aborting.")
        return None

    if not driver_jnt or not mc.objExists(str(driver_jnt)):
        mc.error(f"[eh_createChainWeightedHelper] driver_jnt '{driver_jnt}' does not exist in scene! Aborting.")
        return None

    if attr_holder is not None:
        if not mc.objExists(str(attr_holder)):
            mc.error(f"[eh_createChainWeightedHelper] attr_holder '{attr_holder}' does not exist in scene! Aborting.")
            return None

    if snap_to is not None:
        if not mc.objExists(str(snap_to)):
            mc.error(f"[eh_createChainWeightedHelper] snap_to target '{snap_to}' does not exist in scene! Aborting.")
            return None
        snap_target = str(snap_to)
    else:
        snap_target = str(driver_jnt)

    full_name = f"{prefix}{name}{side}{suffix}"

    #... 2. Capture REST world matrices (static, python-side)
    gp_world_rest = om2.MMatrix(mc.xform(grandparentJnt, q=True, ws=True, m=True))
    prior_world_rest = om2.MMatrix(mc.xform(priorJnt, q=True, ws=True, m=True))
    driver_world_rest = om2.MMatrix(mc.xform(driver_jnt, q=True, ws=True, m=True))
    snap_world_rest = om2.MMatrix(mc.xform(snap_target, q=True, ws=True, m=True))

    #... 3. Create Helper Joint, snap to snap_target, parent under priorJnt
    helper_jnt = mc.createNode('joint', name=full_name)
    mc.setAttr(f"{helper_jnt}.radius", radius * charScale)
    mc.setAttr(f"{helper_jnt}.segmentScaleCompensate", 0)

    try:
        jnt_dag = core.Dag(helper_jnt)
        jnt_dag.setJointColor(joint_color)
        jnt_dag.setJointOutlineColor('white')
    except Exception:
        pass

    mc.delete(mc.parentConstraint(snap_target, helper_jnt, mo=False))

    if mc.attributeQuery('rotateOrder', node=snap_target, exists=True):
        mc.setAttr(f"{helper_jnt}.rotateOrder", mc.getAttr(f"{snap_target}.rotateOrder"))

    mc.parent(helper_jnt, priorJnt)

    if mc.nodeType(helper_jnt) == 'joint':
        mc.makeIdentity(helper_jnt, apply=True, t=False, r=True, s=False)

    #... 4. Stage 1: priorJnt's OWN local-to-grandparent, blended between rest (0.0) and live (1.0)
    prior_local_rest_vs_gp = list(prior_world_rest * gp_world_rest.inverse())

    prior_local_live_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}PriorLocal{side}_mmx")
    mc.connectAttr(f"{priorJnt}.worldMatrix[0]", f"{prior_local_live_mmx}.matrixIn[0]", force=True)
    mc.connectAttr(f"{grandparentJnt}.worldInverseMatrix[0]", f"{prior_local_live_mmx}.matrixIn[1]", force=True)

    prior_stage_bmx = mc.createNode('blendMatrix', name=f"{prefix}{name}PriorStage{side}_bmx")
    mc.setAttr(f"{prior_stage_bmx}.inputMatrix", prior_local_rest_vs_gp, type='matrix')
    mc.connectAttr(f"{prior_local_live_mmx}.matrixSum", f"{prior_stage_bmx}.target[0].targetMatrix", force=True)
    mc.setAttr(f"{prior_stage_bmx}.target[0].weight", 1.0)
    mc.setAttr(f"{prior_stage_bmx}.target[0].shearWeight", 0.0)
    mc.setAttr(f"{prior_stage_bmx}.target[0].scaleWeight", 0.0)

    mc.addAttr(helper_jnt, ln='priorWeight', at='float', min=0.0, max=1.0, dv=max(0.0, min(1.0, float(prior_weight))), k=True)
    mc.connectAttr(f"{helper_jnt}.priorWeight", f"{prior_stage_bmx}.target[0].translateWeight", force=True)
    mc.connectAttr(f"{helper_jnt}.priorWeight", f"{prior_stage_bmx}.target[0].rotateWeight", force=True)

    effective_prior_world_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}EffectivePrior{side}_mmx")
    mc.connectAttr(f"{prior_stage_bmx}.outputMatrix", f"{effective_prior_world_mmx}.matrixIn[0]", force=True)
    mc.connectAttr(f"{grandparentJnt}.worldMatrix[0]", f"{effective_prior_world_mmx}.matrixIn[1]", force=True)

    #... 5. Stage 2: driver_jnt's OWN local-to-REAL-priorJnt, blended between rest (0.0) and live (1.0),
    #... then re-attached to the DAMPENED effective prior frame from Stage 1 (not the real priorJnt).
    driver_local_rest_vs_prior = list(driver_world_rest * prior_world_rest.inverse())

    driver_local_live_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}DriverLocal{side}_mmx")
    mc.connectAttr(f"{driver_jnt}.worldMatrix[0]", f"{driver_local_live_mmx}.matrixIn[0]", force=True)
    mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{driver_local_live_mmx}.matrixIn[1]", force=True)

    driver_stage_bmx = mc.createNode('blendMatrix', name=f"{prefix}{name}DriverStage{side}_bmx")
    mc.setAttr(f"{driver_stage_bmx}.inputMatrix", driver_local_rest_vs_prior, type='matrix')
    mc.connectAttr(f"{driver_local_live_mmx}.matrixSum", f"{driver_stage_bmx}.target[0].targetMatrix", force=True)
    mc.setAttr(f"{driver_stage_bmx}.target[0].weight", 1.0)
    mc.setAttr(f"{driver_stage_bmx}.target[0].shearWeight", 0.0)
    mc.setAttr(f"{driver_stage_bmx}.target[0].scaleWeight", 0.0)

    mc.addAttr(helper_jnt, ln='driverWeight', at='float', min=0.0, max=1.0, dv=max(0.0, min(1.0, float(driver_weight))), k=True)
    mc.connectAttr(f"{helper_jnt}.driverWeight", f"{driver_stage_bmx}.target[0].translateWeight", force=True)
    mc.connectAttr(f"{helper_jnt}.driverWeight", f"{driver_stage_bmx}.target[0].rotateWeight", force=True)

    final_pre_snap_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}FinalPreSnap{side}_mmx")
    mc.connectAttr(f"{driver_stage_bmx}.outputMatrix", f"{final_pre_snap_mmx}.matrixIn[0]", force=True)
    mc.connectAttr(f"{effective_prior_world_mmx}.matrixSum", f"{final_pre_snap_mmx}.matrixIn[1]", force=True)

    #... 6. Fold in snap_to's rest offset (relative to driver_jnt), then localize ONCE against the
    #... real priorJnt (the actual DAG parent) so the DAG's automatic composition reproduces the
    #... intended world result exactly, regardless of priorJnt's live rotation.
    snap_offset = list(snap_world_rest * driver_world_rest.inverse())

    final_world_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}FinalWorld{side}_mmx")
    mc.setAttr(f"{final_world_mmx}.matrixIn[0]", snap_offset, type='matrix')
    mc.connectAttr(f"{final_pre_snap_mmx}.matrixSum", f"{final_world_mmx}.matrixIn[1]", force=True)

    helper_local_mmx = mc.createNode('multMatrix', name=f"{prefix}{name}HelperLocal{side}_mmx")
    mc.connectAttr(f"{final_world_mmx}.matrixSum", f"{helper_local_mmx}.matrixIn[0]", force=True)
    mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{helper_local_mmx}.matrixIn[1]", force=True)

    #... 7. Bake-Safe TRS Decompose
    identity_mat = [1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0]
    try:
        mc.setAttr(f"{helper_jnt}.offsetParentMatrix", identity_mat, type='matrix')
    except Exception:
        pass

    decomp_node = mc.createNode('decomposeMatrix', name=f"{prefix}{name}Result{side}_dcmp")
    mc.connectAttr(f"{helper_local_mmx}.matrixSum", f"{decomp_node}.inputMatrix", force=True)

    #... 8. Quaternion jointOrient Compensation
    if not mc.pluginInfo('quatNodes', q=True, loaded=True):
        try:
            mc.loadPlugin('quatNodes', qt=False)
        except Exception:
            pass

    q2e_node = mc.createNode('quatToEuler', name=f"{prefix}{name}Result{side}_q2e")
    mc.connectAttr(f"{helper_jnt}.rotateOrder", f"{q2e_node}.inputRotateOrder", force=True)

    if mc.nodeType(helper_jnt) == 'joint':
        e2q_node = mc.createNode('eulerToQuat', name=f"{prefix}{name}JO{side}_e2q")
        inv_node = mc.createNode('quatInvert', name=f"{prefix}{name}JO{side}_inv")
        prod_node = mc.createNode('quatProd', name=f"{prefix}{name}JO{side}_prod")

        mc.connectAttr(f"{helper_jnt}.jointOrient", f"{e2q_node}.inputRotate", force=True)
        mc.connectAttr(f"{e2q_node}.outputQuat", f"{inv_node}.inputQuat", force=True)

        mc.connectAttr(f"{decomp_node}.outputQuat", f"{prod_node}.input1Quat", force=True)
        mc.connectAttr(f"{inv_node}.outputQuat", f"{prod_node}.input2Quat", force=True)
        mc.connectAttr(f"{prod_node}.outputQuat", f"{q2e_node}.inputQuat", force=True)
    else:
        mc.connectAttr(f"{decomp_node}.outputQuat", f"{q2e_node}.inputQuat", force=True)

    #... 9. Mirror attrs to attr_holder if external controller specified
    if attr_holder and mc.objExists(attr_holder):
        attr_host = str(attr_holder)
        for w_attr in ('priorWeight', 'driverWeight'):
            d_val = mc.getAttr(f"{helper_jnt}.{w_attr}")
            if not mc.attributeQuery(w_attr, node=attr_host, exists=True):
                mc.addAttr(attr_host, ln=w_attr, at='float', min=0.0, max=1.0, dv=d_val, k=True)
            mc.connectAttr(f"{attr_host}.{w_attr}", f"{helper_jnt}.{w_attr}", force=True)

    #... 10. Connect final TRS into helper joint
    mc.connectAttr(f"{q2e_node}.outputRotate", f"{helper_jnt}.rotate", force=True)
    mc.connectAttr(f"{decomp_node}.outputTranslate", f"{helper_jnt}.translate", force=True)

    core.makeHeader(f"End of eh_createChainWeightedHelper: {helper_jnt}")

    return {
        'helper_joint': helper_jnt,
        'prior_stage_blend': prior_stage_bmx,
        'driver_stage_blend': driver_stage_bmx,
        'effective_prior_mmx': effective_prior_world_mmx,
        'final_world_mmx': final_world_mmx,
        'helper_local_mmx': helper_local_mmx,
        'decompose_matrix': decomp_node,
    }
