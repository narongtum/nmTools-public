# -*- coding: utf-8 -*-
"""
===============================================================================
Auto Skirt Matrix Follow System (eh_autoSkirtFollow.py)
===============================================================================
A modular, procedural auto-skirt rigging tool for Autodesk Maya.
Dynamically blends skirt joints / offset groups between Pelvis (Rest Space)
and Upper Leg (Follow Space) based on leg deviation vectors.

Key Features:
- Matrix Blend Constraint via wtAddMatrix + decomposeMatrix (Zero cycle, bake-friendly).
- Vector Deviation Tracking: Measures leg abduction (outward spread) and flexion (lifting).
- Inward Clamping (Adduction): Clamps inward leg movement to 0, keeping the skirt at rest.
- Smooth Hermite S-Curve Falloff: Smooth 0.0 -> 1.0 weight transition up to maxAngle.
- Animator Controls: Keyable 'autoFollow' multiplier and 'maxAngle' threshold.
- Strict Fail-Fast Validation and console execution banners.

Author: Antigravity AI / nmTools
===============================================================================
"""

import math
import maya.cmds as mc
import maya.api.OpenMaya as om2

from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)


def create_auto_skirt_matrix_follow(
	skirt_target,
	pelvis_source,
	leg_source,
	knee_joint=None,
	attr_occur=None,
	parentToPriorJnt=False,
	side=None,
	baseName=None,
	max_angle=50.0,
	translate=True,
	rotate=True,
	scale=False,
	mo=True,
	ctrl_holder=None
):
	"""
	Binds a skirt target (joint or offset group) to follow the leg dynamically
	using a Matrix Blend Constraint driven by leg vector deviation.

	Args:
		skirt_target (str or core.Dag): Driven object (e.g. 'skirt01Offset_grp' or 'skirt01_bJnt').
		pelvis_source (str or core.Dag): Base resting driver (e.g. 'hip_bJnt' or 'pelvis_bJnt').
		leg_source (str or core.Dag): Follow driver joint (e.g. 'upperLegLFT_bJnt').
		knee_joint (str, optional): Child joint of leg_source (e.g. 'lowerLegLFT_bJnt'). Auto-detected if None.
		attr_occur (str, optional): Controller or shape holding animator attributes (e.g. 'skirt01_ctrl' or 'skirt01_ctrlShape'). Defaults to skirt_target.
		parentToPriorJnt (bool): If True, parents skirt_target under pelvis_source before calculating matrices and constraints. Defaults to False.
		side (str, optional): 'LFT', 'RGT', 'L', or 'R'. Auto-detected from leg_source if None.
		baseName (str, optional): Base name for generated utility nodes. Auto-derived if None.
		max_angle (float): Leg deviation angle (in degrees) at which follow weight reaches 1.0. Defaults to 50.0.
		translate (bool): Constrain translation channels. Defaults to True.
		rotate (bool): Constrain rotation channels. Defaults to True.
		scale (bool): Constrain scale channels. Defaults to False.
		mo (bool): Maintain offset at rest pose. Defaults to True.
		ctrl_holder (str, optional): Deprecated alias for attr_occur.

	Returns:
		dict: Dictionary containing created nodes and references.
	"""
	#... Start of execution banner
	core.makeHeader("Start of Auto Skirt Matrix Follow")

	#... 1. Fail-Fast Prerequisite Validation
	target_name = str(skirt_target.name if hasattr(skirt_target, 'name') else skirt_target)
	pelvis_name = str(pelvis_source.name if hasattr(pelvis_source, 'name') else pelvis_source)
	leg_name = str(leg_source.name if hasattr(leg_source, 'name') else leg_source)

	for node in [target_name, pelvis_name, leg_name]:
		if not mc.objExists(node):
			mc.error(
				f"[eh_autoSkirtFollow] Required node '{node}' does not exist in the active Maya scene. "
				f"Please verify scene hierarchy before executing."
			)

	#... Optional: Parent skirt_target under pelvis_source before matrix calculation
	if parentToPriorJnt:
		current_parent = mc.listRelatives(target_name, parent=True) or []
		if pelvis_name not in current_parent:
			mc.parent(target_name, pelvis_name)
			print(f"# [eh_autoSkirtFollow] Parented '{target_name}' under '{pelvis_name}'.")

	#... Auto-detect Knee joint if not explicitly provided
	if not knee_joint:
		child_joints = mc.listRelatives(leg_name, children=True, type='joint') or []
		if not child_joints:
			mc.error(
				f"[eh_autoSkirtFollow] Unable to auto-detect child knee joint under '{leg_name}'. "
				f"Please specify 'knee_joint' argument explicitly."
			)
		knee_name = child_joints[0]
	else:
		knee_name = str(knee_joint.name if hasattr(knee_joint, 'name') else knee_joint)
		if not mc.objExists(knee_name):
			mc.error(f"[eh_autoSkirtFollow] Specified knee_joint '{knee_name}' does not exist in scene.")

	#... 2. Resolve Naming & Side Indicators
	if not side:
		try:
			parsed_info = core.check_name_style(name=leg_name)
			side = parsed_info[1] if isinstance(parsed_info, (list, tuple)) else 'LFT'
		except Exception:
			side = 'LFT'

	side_upper = str(side).upper()
	is_right = 'RGT' in side_upper or side_upper == 'R'
	side_multiplier = -1.0 if is_right else 1.0

	if not baseName:
		try:
			raw_base = core.check_name_style(name=target_name)[0]
		except Exception:
			raw_base = target_name.split('_')[0]
		base_name = f"{raw_base}_autoFollow"
	else:
		base_name = baseName

	#... Resolve attribute occurrence node (attr_occur)
	target_attr_holder = attr_occur if attr_occur is not None else ctrl_holder
	holder_name = str(target_attr_holder.name if hasattr(target_attr_holder, 'name') else target_attr_holder) if target_attr_holder else target_name
	if not mc.objExists(holder_name):
		holder_name = target_name

	#... 3. Measure Rest Pose Coordinates in Pelvis Local Space
	knee_world_list = mc.xform(knee_name, q=True, ws=True, m=True)
	pelvis_world_list = mc.xform(pelvis_name, q=True, ws=True, m=True)

	knee_world_mtx = om2.MMatrix(knee_world_list)
	pelvis_world_mtx = om2.MMatrix(pelvis_world_list)

	knee_in_pelvis_mtx = knee_world_mtx * pelvis_world_mtx.inverse()
	rest_x = knee_in_pelvis_mtx[12]
	rest_y = knee_in_pelvis_mtx[13]
	rest_z = knee_in_pelvis_mtx[14]

	leg_length = math.sqrt(rest_x**2 + rest_y**2 + rest_z**2)
	if leg_length < 0.001:
		leg_length = 10.0

	#... Calculate reference threshold distance for max_angle (chord distance)
	rad = math.radians(max_angle * 0.5)
	ref_threshold_dist = 2.0 * leg_length * math.sin(rad)
	if ref_threshold_dist < 0.001:
		ref_threshold_dist = 1.0

	#... 4. Create Animator Attribute Channels on Controller Holder
	if not mc.attributeQuery('autoFollow', node=holder_name, exists=True):
		mc.addAttr(holder_name, longName='autoFollow', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
	if not mc.attributeQuery('maxAngle', node=holder_name, exists=True):
		mc.addAttr(holder_name, longName='maxAngle', attributeType='float', defaultValue=float(max_angle), minValue=5.0, maxValue=120.0, keyable=True)
	if not mc.attributeQuery('skirtFollowWeight', node=holder_name, exists=True):
		mc.addAttr(holder_name, longName='skirtFollowWeight', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=False)
		mc.setAttr(f"{holder_name}.skirtFollowWeight", channelBox=True)

	#... 5. Build Dependency Graph (DG) Vector Deviation Network
	#... 5.1 Real-time Knee Position in Pelvis Space
	knee_mmx = mc.createNode('multMatrix', name=f"{base_name}_kneeInPelvis_mmx")
	mc.connectAttr(f"{knee_name}.worldMatrix[0]", f"{knee_mmx}.matrixIn[0]")
	mc.connectAttr(f"{pelvis_name}.worldInverseMatrix[0]", f"{knee_mmx}.matrixIn[1]")

	knee_decomp = mc.createNode('decomposeMatrix', name=f"{base_name}_kneeInPelvis_deComp")
	mc.connectAttr(f"{knee_mmx}.matrixSum", f"{knee_decomp}.inputMatrix")

	#... 5.2 Displacement from Rest Pose (Delta = Current - Rest)
	delta_pma = mc.createNode('plusMinusAverage', name=f"{base_name}_delta_pma")
	mc.setAttr(f"{delta_pma}.operation", 2)  # Subtract
	mc.connectAttr(f"{knee_decomp}.outputTranslate", f"{delta_pma}.input3D[0]")
	mc.setAttr(f"{delta_pma}.input3D[1]", rest_x, rest_y, rest_z, type='double3')

	#... 5.3 Inward Clamping (Adduction): Outward is positive, inward clamped to 0
	outward_mdl = mc.createNode('multDoubleLinear', name=f"{base_name}_outwardSign_mdl")
	mc.connectAttr(f"{delta_pma}.output3Dx", f"{outward_mdl}.input1")
	mc.setAttr(f"{outward_mdl}.input2", side_multiplier)

	inward_clamp = mc.createNode('clamp', name=f"{base_name}_inward_cmp")
	mc.setAttr(f"{inward_clamp}.minR", 0.0)
	mc.setAttr(f"{inward_clamp}.maxR", 999999.0)
	mc.connectAttr(f"{outward_mdl}.output", f"{inward_clamp}.inputR")

	#... 5.4 Upward Lift Clamping: Only upward rise contributes (Y delta > 0)
	lift_clamp = mc.createNode('clamp', name=f"{base_name}_lift_cmp")
	mc.setAttr(f"{lift_clamp}.minR", 0.0)
	mc.setAttr(f"{lift_clamp}.maxR", 999999.0)
	mc.connectAttr(f"{delta_pma}.output3Dy", f"{lift_clamp}.inputR")

	#... 5.5 Effective Deviation Magnitude via distanceBetween
	# point1 = (0, 0, 0), point2 = (outward_clamped, lift_clamped, delta_z)
	dist_node = mc.createNode('distanceBetween', name=f"{base_name}_effectiveDist_dtw")
	mc.setAttr(f"{dist_node}.point1", 0.0, 0.0, 0.0, type='double3')
	mc.connectAttr(f"{inward_clamp}.outputR", f"{dist_node}.point2X")
	mc.connectAttr(f"{lift_clamp}.outputR", f"{dist_node}.point2Y")
	mc.connectAttr(f"{delta_pma}.output3Dz", f"{dist_node}.point2Z")

	#... 5.6 Dynamic Threshold Distance based on holder.maxAngle
	# Scale factor: distance per degree = ref_threshold_dist / max_angle
	deg_to_dist_factor = ref_threshold_dist / float(max_angle)
	thresh_mdl = mc.createNode('multDoubleLinear', name=f"{base_name}_threshDist_mdl")
	mc.connectAttr(f"{holder_name}.maxAngle", f"{thresh_mdl}.input1")
	mc.setAttr(f"{thresh_mdl}.input2", deg_to_dist_factor)

	#... 5.7 Smooth S-Curve Remap (0.0 -> 1.0 with Hermite Spline Interpolation)
	remap_node = mc.createNode('remapValue', name=f"{base_name}_weight_remap")
	mc.setAttr(f"{remap_node}.inputMin", 0.0)
	mc.connectAttr(f"{thresh_mdl}.output", f"{remap_node}.inputMax")
	mc.setAttr(f"{remap_node}.outputMin", 0.0)
	mc.setAttr(f"{remap_node}.outputMax", 1.0)
	# Default linear ramp (interpolation=2 for Spline smooth S-curve)
	mc.setAttr(f"{remap_node}.value[0].value_Interp", 2)
	mc.setAttr(f"{remap_node}.value[1].value_Interp", 2)
	mc.connectAttr(f"{dist_node}.distance", f"{remap_node}.inputValue")

	#... 5.8 Master Multiplier (remap * autoFollow)
	master_mdl = mc.createNode('multDoubleLinear', name=f"{base_name}_masterWeight_mdl")
	mc.connectAttr(f"{remap_node}.outValue", f"{master_mdl}.input1")
	mc.connectAttr(f"{holder_name}.autoFollow", f"{master_mdl}.input2")
	mc.connectAttr(f"{master_mdl}.output", f"{holder_name}.skirtFollowWeight", force=True)

	#... 5.9 Complementary Weight (1.0 - weight) for Pelvis source
	rev_node = mc.createNode('reverse', name=f"{base_name}_weight_rev")
	mc.connectAttr(f"{holder_name}.skirtFollowWeight", f"{rev_node}.inputX")

	#... 6. Matrix Blend Constraint Setup
	# Build matrix constraint blending Pelvis (source1) and Upper Leg (source2)
	tgt_dag, sources, wt_add_mtx = mtc.parentBlendMatrixGPT(
		source1=pelvis_name,
		source2=leg_name,
		target=target_name,
		mo=mo,
		translate=translate,
		rotate=rotate,
		scale=scale,
		weight=0.5,
		baseName=base_name,
		add_attr=False
	)

	#... 7. Hook Dynamic Weights into wtAddMatrix
	# wt_0 = Pelvis influence (1.0 - weight)
	# wt_1 = Upper Leg influence (weight)
	mc.connectAttr(f"{rev_node}.outputX", f"{wt_add_mtx.name}.wt_0", force=True)
	mc.connectAttr(f"{holder_name}.skirtFollowWeight", f"{wt_add_mtx.name}.wt_1", force=True)

	#... End of execution banner
	core.makeHeader("End of Auto Skirt Matrix Follow")

	return {
		'target': target_name,
		'pelvis': pelvis_name,
		'leg': leg_name,
		'knee': knee_name,
		'attr_occur': holder_name,
		'holder': holder_name,
		'wtAddMatrix': wt_add_mtx.name,
		'remapNode': remap_node,
		'distanceNode': dist_node
	}
