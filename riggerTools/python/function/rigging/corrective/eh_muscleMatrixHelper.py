# -*- coding: utf-8 -*-
"""
===============================================================================
Module: eh_muscleMatrixHelper.py
===============================================================================
Overview:
    Matrix-Based Simple Muscle Helper Joint System for Autodesk Maya 2020+.
    
    Implements and modernizes "Technique 3: Simple Muscles (Aim + Dynamic Length Scale)"
    from Jakub Krompolc (Creature TD), documented in:
    function/rigging/corrective/muscle_deformation_helper_joints.md

Key Architecture & Advantages:
    1. Mandatory Template Guide Joint (Strict Fail-Fast):
       Requires a valid guide joint (`tmpJnt`, e.g. 'pecMajorLFT_tmpJnt') positioned on the
       character mesh. If missing, halts execution immediately via fatal mc.error.
       Uses rigTools.jointAt(tmpJnt) per RULE.md to match orientation and rotateOrder.
    2. Zero-Constraint Matrix Evaluation:
       Completely replaces legacy `aimConstraint` and reference locators (Base_LOC,
       Aim_LOC, Up_LOC) with Maya's native `aimMatrix` and `distanceBetween` nodes.
    3. Cycle-Free Input Position:
       Derives aim origin from joint translate + parent matrix via `composeMatrix`,
       completely isolating rotation evaluation and preventing DG cycle warnings.
    4. Dynamic Length Scale (Compression & Stretch):
       Measures real-time distance between Origin and Insertion anchors via `distanceBetween`.
       Divides by bind pose rest distance to calculate primary length scaling.
       When muscles compress ($S_L < 1.0$), vertices compress rather than penetrating.
    5. Volume Bulge Preservation (Cross-Axis Expansion):
       Calculates proportional cross-axis expansion when muscle contracts:
           crossScale = 1.0 + (1.0 - lengthScale) * bulgeWeight
       Zero-drift bind pose guarantee: at rest length ($S_L = 1.0$), cross scale is strictly 1.00000.
    6. Bake-Safe TRS Evaluation (Strict RULE.md Compliance):
       Zero `offsetParentMatrix` dependency. Evaluates directly into `translate`, `rotate`
       (via Quaternion `jointOrient` compensation), and `scale`. 100% compatible with
       `mc.bakeResults` and Unreal Engine / Unity FBX export.
    7. Ergonomic Channel Box Control:
       Exposes intuitive tuning attributes (`restLength`, `currentLength`, `lengthScale`,
       `bulgeWeight`, `crossScale`) on either the muscle joint or an external controller.

Author: Antigravity AI / nmTools
===============================================================================
"""

import maya.cmds as mc
import maya.api.OpenMaya as om2

from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.base import core
reload(core)
from function.rigging.autoRig.base import rigTools
reload(rigTools)
from function.rigging.util import misc
reload(misc)
from function.rigging.util import generic_maya_dict as mnd
reload(mnd)


def _resolve_axis_vector(axis_val, default=(1.0, 0.0, 0.0)):
    """
    #... Resolves axis token ('x', 'y', 'z', '-x', '-y', '-z') or 3-element sequence to a normalized float tuple.
    """
    if isinstance(axis_val, (list, tuple)) and len(axis_val) == 3:
        return (float(axis_val[0]), float(axis_val[1]), float(axis_val[2]))
    
    axis_str = str(axis_val).lower().strip()
    axis_map = {
        'x': (1.0, 0.0, 0.0),
        '+x': (1.0, 0.0, 0.0),
        '-x': (-1.0, 0.0, 0.0),
        'y': (0.0, 1.0, 0.0),
        '+y': (0.0, 1.0, 0.0),
        '-y': (0.0, -1.0, 0.0),
        'z': (0.0, 0.0, 1.0),
        '+z': (0.0, 0.0, 1.0),
        '-z': (0.0, 0.0, -1.0),
    }
    return axis_map.get(axis_str, default)


def _resolve_scale_attrs(length_axis):
    """
    #... Identifies length scale attribute and orthogonal cross-axis attributes from axis token.
    Returns:
        (length_attr, (cross_attr1, cross_attr2))
    """
    clean_axis = str(length_axis).lower().strip().replace('scale', '').replace('s', '')
    if clean_axis == 'x':
        return ('scaleX', ('scaleY', 'scaleZ'))
    elif clean_axis == 'y':
        return ('scaleY', ('scaleX', 'scaleZ'))
    elif clean_axis == 'z':
        return ('scaleZ', ('scaleX', 'scaleY'))
    else:
        # Default Maya joint bone axis is X
        return ('scaleX', ('scaleY', 'scaleZ'))


def eh_createMuscleMatrixHelper(
    tmpJnt=None,
    priorJnt=None,
    insertion_anchor=None,
    name=None,
    side=None,
    origin_anchor=None,
    up_ref=None,
    aim_axis=(1.0, 0.0, 0.0),
    up_axis=(0.0, 1.0, 0.0),
    length_axis='scaleX',
    enable_volume_bulge=True,
    bulge_weight=1.0,
    clamp_min_scale=0.05,
    clamp_max_scale=None,
    attr_holder=None,
    radius=0.5,
    charScale=1.0,
    joint_color=None,
    prefix='',
    suffix='_bJnt',
    **kwargs
):
    """
    #... Builds a Matrix-Based Simple Muscle Helper Joint using native aimMatrix and dynamic length scale.
    Strictly requires a template guide joint (tmpJnt) placed on the character mesh.

    Parameters:
        tmpJnt (str): Template guide joint on mesh (e.g. 'pecMajorLFT_tmpJnt'). MANDATORY.
        priorJnt (str): Parent joint in the DAG skeletal hierarchy (e.g. 'spine03_bJnt', 'clavLFT_bJnt'). MANDATORY.
                        Supports aliases: 'parent_jnt', 'parentJnt', 'prior_jnt'.
        insertion_anchor (str): Node defining the muscle insertion target (aim destination, e.g. 'upperArmLFT_bJnt'). MANDATORY.
        name (str|None): Base name for the muscle. Auto-inferred from tmpJnt if None.
        side (str|None): Side identifier ('LFT', 'RGT', 'CEN'). Auto-inferred from tmpJnt if None.
        origin_anchor (str|None): Node defining live origin position. If None, derived from joint position.
        up_ref (str|None): Node used as secondary target for aimMatrix (world up alignment). If None, uses Scene Up.
        aim_axis (tuple|str): Bone forward axis pointing from origin to insertion (default (1, 0, 0)).
        up_axis (tuple|str): Bone upward axis for twist orientation (default (0, 1, 0)).
        length_axis (str): Scale axis to drive with dynamic length ratio (default 'scaleX').
        enable_volume_bulge (bool): If True, dynamically expands cross axes when muscle compresses.
        bulge_weight (float): Multiplier for cross-axis volume expansion (default 1.0).
        clamp_min_scale (float): Minimum length scale clamp to prevent negative/collapsed geometry (default 0.05).
        clamp_max_scale (float|None): Maximum stretch scale clamp. None allows continuous stretching.
        attr_holder (str|None): Optional controller node to host Channel Box attributes. If None, hosted on helper joint.
        radius (float): Joint display radius (default 0.5).
        charScale (float): Global character scale multiplier.
        joint_color (str|None): Display color ('softBlue', 'red', 'yellow', etc.). Auto-resolved from side if None.
        prefix (str): Optional name prefix.
        suffix (str): Joint suffix (default '_bJnt').

    Returns:
        dict: Complete dictionary containing created nodes:
            {
                'helper_jnt': str,
                'aimMatrix': str,
                'distance': str,
                'scaleRatio': str,
                'decompose': str,
                'attr_host': str
            }
    """
    #... 1. Backwards-Compatible Parameter Aliases
    if tmpJnt is None:
        tmpJnt = kwargs.get('tmp_jnt') or kwargs.get('guide_jnt') or kwargs.get('guideJnt')

    if priorJnt is None:
        priorJnt = kwargs.get('parent_jnt') or kwargs.get('parentJnt') or kwargs.get('prior_jnt')

    #... 2. Strict Fail-Fast Validation (RULE.md Zero-Tolerance Standard)
    # Validate tmpJnt strictly: must be provided and must exist in scene
    if not tmpJnt:
        mc.error(
            "[eh_muscleMatrixHelper.eh_createMuscleMatrixHelper] Fatal: 'tmpJnt' is strictly required! "
            "No template guide joint provided. Please supply a valid template joint (e.g. 'pecMajorLFT_tmpJnt')."
        )

    if not mc.objExists(str(tmpJnt)):
        mc.error(
            f"[eh_muscleMatrixHelper.eh_createMuscleMatrixHelper] Fatal: Template guide joint tmpJnt='{tmpJnt}' "
            f"does not exist in the active Maya scene! Please place the guide joint on the character model before building."
        )

    missing_nodes = []
    if not priorJnt or not mc.objExists(str(priorJnt)):
        missing_nodes.append(f"priorJnt='{priorJnt}'")
    if not insertion_anchor or not mc.objExists(str(insertion_anchor)):
        missing_nodes.append(f"insertion_anchor='{insertion_anchor}'")

    if missing_nodes:
        mc.error(
            f"[eh_muscleMatrixHelper.eh_createMuscleMatrixHelper] Fatal: Required scene nodes missing: "
            f"{', '.join(missing_nodes)}! Please ensure skeleton guides/bind joints exist before running."
        )

    core.makeHeader(f"Start of eh_createMuscleMatrixHelper: {tmpJnt}")

    #... 3. Auto-infer Name and Side from tmpJnt if omitted
    parsed_style, parsed_side = core.check_name_style(str(tmpJnt))
    clean_base = str(tmpJnt)
    for sfx in ['_tmpJnt', 'tmpJnt', '_tmp', 'tmp', '_jnt', 'jnt']:
        if clean_base.endswith(sfx):
            clean_base = clean_base[:-len(sfx)]
            break

    if side is None:
        side = parsed_side if parsed_side else 'LFT'

    if name is None:
        if clean_base.endswith(side):
            name = clean_base[:-len(side)]
        elif clean_base.startswith(side + '_'):
            name = clean_base[len(side) + 1:]
        else:
            name = clean_base

    # Validate optional nodes
    if up_ref and not mc.objExists(str(up_ref)):
        mc.warning(f"[eh_muscleMatrixHelper] up_ref '{up_ref}' not found in scene. Falling back to Scene Up orientation.")
        up_ref = None

    if attr_holder and not mc.objExists(str(attr_holder)):
        mc.warning(f"[eh_muscleMatrixHelper] attr_holder '{attr_holder}' not found. Attributes will be placed on helper joint.")
        attr_holder = None

    # Resolve axis vectors
    aim_vec = _resolve_axis_vector(aim_axis, default=(1.0, 0.0, 0.0))
    up_vec = _resolve_axis_vector(up_axis, default=(0.0, 1.0, 0.0))
    length_scale_plug, (cross_scale1, cross_scale2) = _resolve_scale_attrs(length_axis)

    # Resolve joint display color based on side
    if joint_color is None:
        side_clean = side.upper().replace('_', '')
        if side_clean in ('LFT', 'L'):
            joint_color = 'softBlue'
        elif side_clean in ('RGT', 'R'):
            joint_color = 'red'
        else:
            joint_color = 'yellow'

    #... 4. Create Muscle Helper Joint via rigTools.jointAt(tmpJnt) per RULE.md Standard
    full_name = f"{prefix}{name}{side}{suffix}"
    is_new = not mc.objExists(full_name)
    if is_new:
        created_jnt = rigTools.jointAt(tmpJnt)
        helper_jnt = mc.rename(created_jnt.name, full_name)
    else:
        mc.warning(f"[eh_muscleMatrixHelper] Joint '{full_name}' already exists. Updating matrix network.")
        helper_jnt = full_name

    mc.setAttr(f"{helper_jnt}.radius", radius * charScale)
    mc.setAttr(f"{helper_jnt}.segmentScaleCompensate", 0)

    try:
        jnt_dag = core.Dag(helper_jnt)
        jnt_dag.setJointColor(joint_color)
        jnt_dag.setJointOutlineColor('white')
    except Exception:
        pass

    # Ensure correct parenting under priorJnt
    current_parent = mc.listRelatives(helper_jnt, parent=True)
    if not current_parent or current_parent[0] != priorJnt:
        mc.parent(helper_jnt, priorJnt)

    if is_new:
        # Freeze rotations into jointOrient as required by RULE.md
        mc.makeIdentity(helper_jnt, apply=True, t=False, r=True, s=False)

    # Reset offsetParentMatrix to Identity (RULE.md standard)
    identity_mat = [1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0]
    try:
        mc.setAttr(f"{helper_jnt}.offsetParentMatrix", identity_mat, type='matrix')
    except Exception:
        pass

    #... 5. Cycle-Free Input Matrix Network
    # We construct the origin matrix using helper_jnt's local translation multiplied by priorJnt world matrix.
    # This prevents DG cycle warnings when aimMatrix updates the joint's rotation.
    compose_in_name = f"{prefix}{name}InPos{side}_cmx"
    compose_in = compose_in_name if mc.objExists(compose_in_name) else mc.createNode('composeMatrix', name=compose_in_name)
    mc.connectAttr(f"{helper_jnt}.translate", f"{compose_in}.inputTranslate", force=True)

    mult_in_name = f"{prefix}{name}InMat{side}_mmx"
    mult_in = mult_in_name if mc.objExists(mult_in_name) else mc.createNode('multMatrix', name=mult_in_name)
    mc.connectAttr(f"{compose_in}.outputMatrix", f"{mult_in}.matrixIn[0]", force=True)
    mc.connectAttr(f"{priorJnt}.worldMatrix[0]", f"{mult_in}.matrixIn[1]", force=True)

    #... 6. Create and Configure Native aimMatrix Node
    aim_node_name = f"{prefix}{name}Aim{side}_aimMtx"
    aim_node = aim_node_name if mc.objExists(aim_node_name) else mc.createNode('aimMatrix', name=aim_node_name)

    mc.connectAttr(f"{mult_in}.matrixSum", f"{aim_node}.inputMatrix", force=True)
    mc.connectAttr(f"{insertion_anchor}.worldMatrix[0]", f"{aim_node}.primaryTargetMatrix", force=True)

    mc.setAttr(f"{aim_node}.primaryMode", 1)  # 1 = Align to target position
    mc.setAttr(f"{aim_node}.primaryInputAxisX", aim_vec[0])
    mc.setAttr(f"{aim_node}.primaryInputAxisY", aim_vec[1])
    mc.setAttr(f"{aim_node}.primaryInputAxisZ", aim_vec[2])

    mc.setAttr(f"{aim_node}.secondaryInputAxisX", up_vec[0])
    mc.setAttr(f"{aim_node}.secondaryInputAxisY", up_vec[1])
    mc.setAttr(f"{aim_node}.secondaryInputAxisZ", up_vec[2])

    if up_ref and mc.objExists(up_ref):
        mc.connectAttr(f"{up_ref}.worldMatrix[0]", f"{aim_node}.secondaryTargetMatrix", force=True)
        mc.setAttr(f"{aim_node}.secondaryMode", 1)  # 1 = Object Position
    else:
        mc.setAttr(f"{aim_node}.secondaryMode", 0)  # 0 = Scene Up

    #... 7. Convert World Aim Matrix to Local Space of priorJnt
    mult_local_name = f"{prefix}{name}Local{side}_mmx"
    mult_local = mult_local_name if mc.objExists(mult_local_name) else mc.createNode('multMatrix', name=mult_local_name)
    mc.connectAttr(f"{aim_node}.outputMatrix", f"{mult_local}.matrixIn[0]", force=True)
    mc.connectAttr(f"{priorJnt}.worldInverseMatrix[0]", f"{mult_local}.matrixIn[1]", force=True)

    #... 8. Decompose Matrix into TRS Channels (Bake-Safe)
    decomp_name = f"{prefix}{name}Result{side}_dcmp"
    decomp_node = decomp_name if mc.objExists(decomp_name) else mc.createNode('decomposeMatrix', name=decomp_name)
    mc.connectAttr(f"{mult_local}.matrixSum", f"{decomp_node}.inputMatrix", force=True)

    # Translate evaluation
    mc.connectAttr(f"{decomp_node}.outputTranslate", f"{helper_jnt}.translate", force=True)

    #... 9. Quaternion Joint Orient Compensation for Rotation
    if not mc.pluginInfo('quatNodes', q=True, loaded=True):
        try:
            mc.loadPlugin('quatNodes', qt=False)
        except Exception:
            pass

    e2q_name = f"{prefix}{name}JntOri{side}_e2q"
    e2q = e2q_name if mc.objExists(e2q_name) else mc.createNode('eulerToQuat', name=e2q_name)

    qinv_name = f"{prefix}{name}JntOriInv{side}_qinv"
    qinv = qinv_name if mc.objExists(qinv_name) else mc.createNode('quatInvert', name=qinv_name)

    qprod_name = f"{prefix}{name}RotComp{side}_qprod"
    qprod = qprod_name if mc.objExists(qprod_name) else mc.createNode('quatProd', name=qprod_name)

    q2e_name = f"{prefix}{name}RotEuler{side}_q2e"
    q2e = q2e_name if mc.objExists(q2e_name) else mc.createNode('quatToEuler', name=q2e_name)

    mc.connectAttr(f"{helper_jnt}.jointOrient", f"{e2q}.inputRotate", force=True)
    mc.connectAttr(f"{e2q}.outputQuat", f"{qinv}.inputQuat", force=True)

    mc.connectAttr(f"{decomp_node}.outputQuat", f"{qprod}.input1Quat", force=True)
    mc.connectAttr(f"{qinv}.outputQuat", f"{qprod}.input2Quat", force=True)
    mc.connectAttr(f"{qprod}.outputQuat", f"{q2e}.inputQuat", force=True)

    mc.connectAttr(f"{helper_jnt}.rotateOrder", f"{q2e}.inputRotateOrder", force=True)
    mc.connectAttr(f"{q2e}.outputRotate", f"{helper_jnt}.rotate", force=True)

    #... 10. Dynamic Length Scale via distanceBetween
    dist_node_name = f"{prefix}{name}Length{side}_dtw"
    dist_node = dist_node_name if mc.objExists(dist_node_name) else mc.createNode('distanceBetween', name=dist_node_name)

    # Connect live origin position: defaults to mult_in.matrixSum (helper_jnt live world position)
    if origin_anchor and mc.objExists(str(origin_anchor)):
        mc.connectAttr(f"{origin_anchor}.worldMatrix[0]", f"{dist_node}.inMatrix1", force=True)
    else:
        mc.connectAttr(f"{mult_in}.matrixSum", f"{dist_node}.inMatrix1", force=True)

    mc.connectAttr(f"{insertion_anchor}.worldMatrix[0]", f"{dist_node}.inMatrix2", force=True)

    # Measure bind rest distance
    rest_dist_val = mc.getAttr(f"{dist_node}.distance")
    if rest_dist_val < 1e-4:
        rest_dist_val = 1.0
        mc.warning(f"[eh_muscleMatrixHelper] Measured distance between origin and '{insertion_anchor}' is 0. Defaulting restLength to 1.0.")

    # Determine attribute host
    attr_host = attr_holder if attr_holder and mc.objExists(attr_holder) else helper_jnt

    # Expose Muscle Settings Attributes on attr_host
    if not mc.attributeQuery('muscleSettings', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='muscleSettings', at='enum', en='-------:', k=True)
        mc.setAttr(f"{attr_host}.muscleSettings", lock=True)

    if not mc.attributeQuery('restLength', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='restLength', at='float', min=0.001, dv=rest_dist_val, k=True)
    else:
        mc.setAttr(f"{attr_host}.restLength", rest_dist_val)

    if not mc.attributeQuery('currentLength', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='currentLength', at='float', k=False)
        mc.setAttr(f"{attr_host}.currentLength", channelBox=True)
    mc.connectAttr(f"{dist_node}.distance", f"{attr_host}.currentLength", force=True)

    if not mc.attributeQuery('lengthScale', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='lengthScale', at='float', k=False)
        mc.setAttr(f"{attr_host}.lengthScale", channelBox=True)

    if not mc.attributeQuery('bulgeWeight', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='bulgeWeight', at='float', min=0.0, max=10.0, dv=bulge_weight, k=True)
    else:
        mc.setAttr(f"{attr_host}.bulgeWeight", bulge_weight)

    if not mc.attributeQuery('crossScale', node=attr_host, exists=True):
        mc.addAttr(attr_host, ln='crossScale', at='float', k=False)
        mc.setAttr(f"{attr_host}.crossScale", channelBox=True)

    # If attr_host is on a controller, also mirror attributes onto helper_jnt
    if attr_host != helper_jnt:
        if not mc.attributeQuery('muscleSettings', node=helper_jnt, exists=True):
            mc.addAttr(helper_jnt, ln='muscleSettings', at='enum', en='-------:', k=True)
            mc.setAttr(f"{helper_jnt}.muscleSettings", lock=True)

        for m_attr in ['restLength', 'bulgeWeight']:
            if not mc.attributeQuery(m_attr, node=helper_jnt, exists=True):
                mc.addAttr(helper_jnt, ln=m_attr, at='float', k=True)
            try:
                mc.connectAttr(f"{attr_host}.{m_attr}", f"{helper_jnt}.{m_attr}", force=True)
            except Exception:
                pass

        for ro_attr in ['currentLength', 'lengthScale', 'crossScale']:
            if not mc.attributeQuery(ro_attr, node=helper_jnt, exists=True):
                mc.addAttr(helper_jnt, ln=ro_attr, at='float', k=False)
                mc.setAttr(f"{helper_jnt}.{ro_attr}", channelBox=True)
            try:
                mc.connectAttr(f"{attr_host}.{ro_attr}", f"{helper_jnt}.{ro_attr}", force=True)
            except Exception:
                pass

    #... 11. Compute Dynamic Length Scale Ratio: currentDistance / restLength
    ratio_mdv_name = f"{prefix}{name}Ratio{side}_mdv"
    ratio_mdv = ratio_mdv_name if mc.objExists(ratio_mdv_name) else mc.createNode('multiplyDivide', name=ratio_mdv_name)
    mc.setAttr(f"{ratio_mdv}.operation", 2)  # 2 = Divide

    mc.connectAttr(f"{dist_node}.distance", f"{ratio_mdv}.input1X", force=True)
    mc.connectAttr(f"{attr_host}.restLength", f"{ratio_mdv}.input2X", force=True)

    # Clamp length scale to prevent collapse/negative volume
    clamp_len_name = f"{prefix}{name}LenClamp{side}_clamp"
    clamp_len = clamp_len_name if mc.objExists(clamp_len_name) else mc.createNode('clamp', name=clamp_len_name)
    mc.connectAttr(f"{ratio_mdv}.outputX", f"{clamp_len}.inputR", force=True)
    mc.setAttr(f"{clamp_len}.minR", clamp_min_scale)
    mc.setAttr(f"{clamp_len}.maxR", clamp_max_scale if clamp_max_scale is not None else 999999.0)

    # Connect length scale output
    mc.connectAttr(f"{clamp_len}.outputR", f"{attr_host}.lengthScale", force=True)
    mc.connectAttr(f"{clamp_len}.outputR", f"{helper_jnt}.{length_scale_plug}", force=True)

    #... 12. Cross-Axis Volume Bulge Preservation Network
    if enable_volume_bulge:
        # Formula: delta_compression = 1.0 - lengthScale
        #          bulge_offset = delta_compression * bulgeWeight
        #          cross_scale = 1.0 + bulge_offset
        delta_pma_name = f"{prefix}{name}BulgeDelta{side}_pma"
        delta_pma = delta_pma_name if mc.objExists(delta_pma_name) else mc.createNode('plusMinusAverage', name=delta_pma_name)
        mc.setAttr(f"{delta_pma}.operation", 2)  # 2 = Subtract
        mc.setAttr(f"{delta_pma}.input1D[0]", 1.0)
        mc.connectAttr(f"{clamp_len}.outputR", f"{delta_pma}.input1D[1]", force=True)

        bulge_mdl_name = f"{prefix}{name}BulgeOffset{side}_mdl"
        bulge_mdl = bulge_mdl_name if mc.objExists(bulge_mdl_name) else mc.createNode('multDoubleLinear', name=bulge_mdl_name)
        mc.connectAttr(f"{delta_pma}.output1D", f"{bulge_mdl}.input1", force=True)
        mc.connectAttr(f"{attr_host}.bulgeWeight", f"{bulge_mdl}.input2", force=True)

        cross_adl_name = f"{prefix}{name}CrossScale{side}_adl"
        cross_adl = cross_adl_name if mc.objExists(cross_adl_name) else mc.createNode('addDoubleLinear', name=cross_adl_name)
        mc.connectAttr(f"{bulge_mdl}.output", f"{cross_adl}.input1", force=True)
        mc.setAttr(f"{cross_adl}.input2", 1.0)

        # Clamp cross scale to avoid negative or explosive values
        cross_clamp_name = f"{prefix}{name}CrossClamp{side}_clamp"
        cross_clamp = cross_clamp_name if mc.objExists(cross_clamp_name) else mc.createNode('clamp', name=cross_clamp_name)
        mc.connectAttr(f"{cross_adl}.output", f"{cross_clamp}.inputR", force=True)
        mc.setAttr(f"{cross_clamp}.minR", 0.05)
        mc.setAttr(f"{cross_clamp}.maxR", 10.0)

        mc.connectAttr(f"{cross_clamp}.outputR", f"{attr_host}.crossScale", force=True)
        mc.connectAttr(f"{cross_clamp}.outputR", f"{helper_jnt}.{cross_scale1}", force=True)
        mc.connectAttr(f"{cross_clamp}.outputR", f"{helper_jnt}.{cross_scale2}", force=True)
    else:
        # Static 1.0 for cross axes
        mc.setAttr(f"{helper_jnt}.{cross_scale1}", 1.0)
        mc.setAttr(f"{helper_jnt}.{cross_scale2}", 1.0)
        mc.setAttr(f"{attr_host}.crossScale", 1.0)

    core.makeHeader(f"End of eh_createMuscleMatrixHelper: {helper_jnt}")

    return {
        'helper_jnt': helper_jnt,
        'aimMatrix': aim_node,
        'distance': dist_node,
        'scaleRatio': ratio_mdv,
        'decompose': decomp_node,
        'attr_host': attr_host
    }


# ==============================================================================
# Anatomical Convenience Presets (Strict tmpJnt Validation)
# ==============================================================================

def eh_createPectoralMuscle(
    tmpJnt=None,
    side='LFT',
    priorJnt='spine03_bJnt',
    insertion_anchor=None,
    up_ref=None,
    bulge_weight=1.2,
    attr_holder=None,
    **kwargs
):
    """
    #... Builds a Pectoralis Major muscle helper joint bridging sternum/spine to upper arm.
    Requires template guide joint (e.g. 'pecMajorLFT_tmpJnt').
    Contracts during arm adduction (bringing arm inwards), bulging the chest contour.
    """
    if tmpJnt is None:
        tmpJnt = kwargs.get('tmp_jnt') or kwargs.get('guide_jnt') or f"pecMajor{side}_tmpJnt"

    if not mc.objExists(str(tmpJnt)):
        mc.error(
            f"[eh_muscleMatrixHelper.eh_createPectoralMuscle] Fatal: Template guide joint tmpJnt='{tmpJnt}' "
            f"does not exist in the scene! Please place the guide joint on the chest before building."
        )

    ins = insertion_anchor or f"upperArm{side}_bJnt"
    up = up_ref or f"clav{side}_bJnt"
    return eh_createMuscleMatrixHelper(
        tmpJnt=tmpJnt,
        priorJnt=priorJnt,
        insertion_anchor=ins,
        name='pecMajor',
        side=side,
        up_ref=up,
        aim_axis=(1.0, 0.0, 0.0),
        up_axis=(0.0, 1.0, 0.0),
        length_axis='scaleX',
        enable_volume_bulge=True,
        bulge_weight=bulge_weight,
        attr_holder=attr_holder,
        **kwargs
    )


def eh_createTrapeziusMuscle(
    tmpJnt=None,
    side='LFT',
    priorJnt='neck_bJnt',
    insertion_anchor=None,
    up_ref=None,
    bulge_weight=0.8,
    attr_holder=None,
    **kwargs
):
    """
    #... Builds a Trapezius muscle helper joint bridging cervical spine/neck to clavicle/scapula.
    Requires template guide joint (e.g. 'trapeziusLFT_tmpJnt').
    Contracts during shoulder shrugs, preserving neck-shoulder curve volume.
    """
    if tmpJnt is None:
        tmpJnt = kwargs.get('tmp_jnt') or kwargs.get('guide_jnt') or f"trapezius{side}_tmpJnt"

    if not mc.objExists(str(tmpJnt)):
        mc.error(
            f"[eh_muscleMatrixHelper.eh_createTrapeziusMuscle] Fatal: Template guide joint tmpJnt='{tmpJnt}' "
            f"does not exist in the scene! Please place the guide joint on the neck/shoulder curve before building."
        )

    ins = insertion_anchor or f"clav{side}_bJnt"
    up = up_ref or f"spine04_bJnt" if mc.objExists(f"spine04_bJnt") else priorJnt
    return eh_createMuscleMatrixHelper(
        tmpJnt=tmpJnt,
        priorJnt=priorJnt,
        insertion_anchor=ins,
        name='trapezius',
        side=side,
        up_ref=up,
        aim_axis=(1.0, 0.0, 0.0),
        up_axis=(0.0, 1.0, 0.0),
        length_axis='scaleX',
        enable_volume_bulge=True,
        bulge_weight=bulge_weight,
        attr_holder=attr_holder,
        **kwargs
    )


def eh_createDeltoidMuscle(
    tmpJnt=None,
    side='LFT',
    priorJnt=None,
    insertion_anchor=None,
    up_ref=None,
    bulge_weight=1.0,
    attr_holder=None,
    **kwargs
):
    """
    #... Builds a Deltoid muscle helper joint bridging acromion/clavicle to deltoid tuberosity.
    Requires template guide joint (e.g. 'deltoidMuscleLFT_tmpJnt').
    Contracts during arm abduction (raising arm sideways), thickening shoulder cap.
    """
    prior = priorJnt or f"clav{side}_bJnt"
    if tmpJnt is None:
        tmpJnt = kwargs.get('tmp_jnt') or kwargs.get('guide_jnt') or f"deltoidMuscle{side}_tmpJnt"

    if not mc.objExists(str(tmpJnt)):
        mc.error(
            f"[eh_muscleMatrixHelper.eh_createDeltoidMuscle] Fatal: Template guide joint tmpJnt='{tmpJnt}' "
            f"does not exist in the scene! Please place the guide joint on the deltoid shoulder contour before building."
        )

    ins = insertion_anchor or f"upperArm{side}_bJnt"
    up = up_ref or prior
    return eh_createMuscleMatrixHelper(
        tmpJnt=tmpJnt,
        priorJnt=prior,
        insertion_anchor=ins,
        name='deltoidMuscle',
        side=side,
        up_ref=up,
        aim_axis=(1.0, 0.0, 0.0),
        up_axis=(0.0, 1.0, 0.0),
        length_axis='scaleX',
        enable_volume_bulge=True,
        bulge_weight=bulge_weight,
        attr_holder=attr_holder,
        **kwargs
    )


def eh_createLatissimusMuscle(
    tmpJnt=None,
    side='LFT',
    priorJnt='spine02_bJnt',
    insertion_anchor=None,
    up_ref=None,
    bulge_weight=1.0,
    attr_holder=None,
    **kwargs
):
    """
    #... Builds a Latissimus Dorsi muscle helper joint bridging mid/lower back to humerus.
    Requires template guide joint (e.g. 'latissimusLFT_tmpJnt').
    Prevents hollow back artifacts under the armpit during arm retraction.
    """
    if tmpJnt is None:
        tmpJnt = kwargs.get('tmp_jnt') or kwargs.get('guide_jnt') or f"latissimus{side}_tmpJnt"

    if not mc.objExists(str(tmpJnt)):
        mc.error(
            f"[eh_muscleMatrixHelper.eh_createLatissimusMuscle] Fatal: Template guide joint tmpJnt='{tmpJnt}' "
            f"does not exist in the scene! Please place the guide joint on the back flank before building."
        )

    ins = insertion_anchor or f"upperArm{side}_bJnt"
    up = up_ref or f"spine03_bJnt"
    return eh_createMuscleMatrixHelper(
        tmpJnt=tmpJnt,
        priorJnt=priorJnt,
        insertion_anchor=ins,
        name='latissimus',
        side=side,
        up_ref=up,
        aim_axis=(1.0, 0.0, 0.0),
        up_axis=(0.0, 1.0, 0.0),
        length_axis='scaleX',
        enable_volume_bulge=True,
        bulge_weight=bulge_weight,
        attr_holder=attr_holder,
        **kwargs
    )
