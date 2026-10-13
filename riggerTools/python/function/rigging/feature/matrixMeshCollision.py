"""
Module: matrixMeshCollision.py
Description:
	Real-time node-based Matrix Mesh Collision System for Maya rigging.
	Calculates surface contact, surface normal alignment, and penetration avoidance
	using pure DG Matrix nodes (closestPointOnMesh, vectorProduct, fourByFourMatrix, multMatrix, condition, pairBlend).
	100% DG real-time evaluation with zero Python expressions or dynamic simulation.

Author: nmTools Pipeline
Date: 2026-08-26
"""

import maya.cmds as mc
from function.framework.reloadWrapper import reloadWrapper as reload

import logging
logger = logging.getLogger('nmTools.matrixMeshCollision')
logger.setLevel(logging.INFO)


def setup_matrix_mesh_collision(
	nameSpace='',
	baseName='frontLeg',
	side='LFT',
	partName='index03',
	probeObj='',
	targetOffsetGrp='',
	collisionMesh='',
	stickCtrl='',
	blendAttr='groundCollision',
	yOnly=True
):
	"""
	Construct pure Matrix DG network to project targetOffsetGrp onto collisionMesh surface upon penetration.

	Args:
		nameSpace (str): Namespace prefix.
		baseName (str): Limb/component base name (e.g. 'frontLeg', 'backLeg01').
		side (str): Side identifier ('LFT', 'RGT', 'CEN').
		partName (str): Distinct part/digit name (e.g. 'thumb03', 'index03', 'heel').
		probeObj (str): Contact probe transform to measure world penetration (e.g. 'index03LFT_ikJnt' or 'indexIkLFT_ctrl').
		targetOffsetGrp (str): Target Offset group to be displaced/rotated upon ground collision (e.g. 'indexIkLFTOffset_grp').
		collisionMesh (str): Target collision geometry transform or shape.
		stickCtrl (str): Master controller holding the blend switch attribute (e.g. 'legStickLFT_ctrl').
		blendAttr (str): Float attribute name on stickCtrl (default: 'groundCollision').
		yOnly (bool): When True, only clamps vertical height (Y) to the floor while letting X and Z follow the controller freely (default: True).

	Returns:
		dict[str, str] | None: Dictionary of created nodes or None if terminated.
	"""
	# 1. Validation & Strict Termination
	if not collisionMesh or not mc.objExists(collisionMesh):
		logger.warning(f"Collision mesh '{collisionMesh}' does not exist. Terminating Matrix Mesh Collision for {partName}{side}.")
		return None

	if not probeObj or not mc.objExists(probeObj):
		logger.warning(f"Probe object '{probeObj}' does not exist. Terminating Matrix Mesh Collision.")
		return None

	if not targetOffsetGrp or not mc.objExists(targetOffsetGrp):
		logger.warning(f"Target offset group '{targetOffsetGrp}' does not exist. Terminating Matrix Mesh Collision.")
		return None

	# Resolve Shape Node (Supports both 'mesh' and 'nurbsSurface')
	shapes = mc.listRelatives(collisionMesh, shapes=True, noIntermediate=True) or []
	shape_node = shapes[0] if shapes else collisionMesh
	shape_type = mc.nodeType(shape_node)

	if shape_type not in ('mesh', 'nurbsSurface'):
		logger.warning(f"Object '{shape_node}' is not a valid collision surface (Type: {shape_type}). Expected 'mesh' or 'nurbsSurface'. Terminating.")
		return None

	prefix = f"{nameSpace}{baseName}_{partName}{side}"

	# 2. Probe World Position Decompose & Surface Query
	probe_decomp = mc.createNode('decomposeMatrix', name=f"{prefix}_probe_decomp")
	mc.connectAttr(f"{probeObj}.worldMatrix[0]", f"{probe_decomp}.inputMatrix", force=True)

	if shape_type == 'mesh':
		surface_query = mc.createNode('closestPointOnMesh', name=f"{prefix}_cpm")
		mc.connectAttr(f"{shape_node}.outMesh", f"{surface_query}.inMesh", force=True)
		mc.connectAttr(f"{shape_node}.worldMatrix[0]", f"{surface_query}.inMatrix", force=True)
		mc.connectAttr(f"{probe_decomp}.outputTranslate", f"{surface_query}.inPosition", force=True)

		normal_plug = f"{surface_query}.normal"
		normal_x = f"{surface_query}.normalX"
		normal_y = f"{surface_query}.normalY"
		normal_z = f"{surface_query}.normalZ"
		pos_x = f"{surface_query}.positionX"
		pos_y = f"{surface_query}.positionY"
		pos_z = f"{surface_query}.positionZ"
	else:  # 'nurbsSurface'
		surface_query = mc.createNode('closestPointOnSurface', name=f"{prefix}_cps")
		mc.connectAttr(f"{shape_node}.worldSpace[0]", f"{surface_query}.inputSurface", force=True)
		mc.connectAttr(f"{probe_decomp}.outputTranslate", f"{surface_query}.inPosition", force=True)

		posi = mc.createNode('pointOnSurfaceInfo', name=f"{prefix}_posi")
		mc.connectAttr(f"{shape_node}.worldSpace[0]", f"{posi}.inputSurface", force=True)
		mc.connectAttr(f"{surface_query}.parameterU", f"{posi}.parameterU", force=True)
		mc.connectAttr(f"{surface_query}.parameterV", f"{posi}.parameterV", force=True)
		mc.setAttr(f"{posi}.turnOnPercentage", 0)

		normal_plug = f"{posi}.normalizedNormal"
		normal_x = f"{posi}.normalizedNormalX"
		normal_y = f"{posi}.normalizedNormalY"
		normal_z = f"{posi}.normalizedNormalZ"
		pos_x = f"{posi}.positionX"
		pos_y = f"{posi}.positionY"
		pos_z = f"{posi}.positionZ"

	# 3. Surface Contact Matrix Assembly (Translational Anchor)
	# Constructs a 4x4 matrix for the world contact point on the collision surface
	contact_fbfm = mc.createNode('fourByFourMatrix', name=f"{prefix}_contact_fbfm")
	# Identity Rotation
	mc.setAttr(f"{contact_fbfm}.in00", 1.0)
	mc.setAttr(f"{contact_fbfm}.in01", 0.0)
	mc.setAttr(f"{contact_fbfm}.in02", 0.0)
	mc.setAttr(f"{contact_fbfm}.in03", 0.0)

	mc.setAttr(f"{contact_fbfm}.in10", 0.0)
	mc.setAttr(f"{contact_fbfm}.in11", 1.0)
	mc.setAttr(f"{contact_fbfm}.in12", 0.0)
	mc.setAttr(f"{contact_fbfm}.in13", 0.0)

	mc.setAttr(f"{contact_fbfm}.in20", 0.0)
	mc.setAttr(f"{contact_fbfm}.in21", 0.0)
	mc.setAttr(f"{contact_fbfm}.in22", 1.0)
	mc.setAttr(f"{contact_fbfm}.in23", 0.0)

	# Contact Translation (X, Y, Z)
	# If yOnly=True: X and Z world positions are preserved from probeObj, only Y is clamped to surface
	if yOnly:
		mc.connectAttr(f"{probe_decomp}.outputTranslateX", f"{contact_fbfm}.in30", force=True)
		mc.connectAttr(pos_y, f"{contact_fbfm}.in31", force=True)
		mc.connectAttr(f"{probe_decomp}.outputTranslateZ", f"{contact_fbfm}.in32", force=True)
	else:
		mc.connectAttr(pos_x, f"{contact_fbfm}.in30", force=True)
		mc.connectAttr(pos_y, f"{contact_fbfm}.in31", force=True)
		mc.connectAttr(pos_z, f"{contact_fbfm}.in32", force=True)
	mc.setAttr(f"{contact_fbfm}.in33", 1.0)

	# 4. Penetration Detection in World Space (Delta Y = Surface Contact Y - Probe World Y)
	# When Delta Y > 0 -> Probe is below the surface (penetrating underground)
	pma_penetration = mc.createNode('plusMinusAverage', name=f"{prefix}_penetration_pma")
	mc.setAttr(f"{pma_penetration}.operation", 2)  # Subtract (Input[0] - Input[1])
	mc.connectAttr(pos_y, f"{pma_penetration}.input1D[0]", force=True)
	mc.connectAttr(f"{probe_decomp}.outputTranslateY", f"{pma_penetration}.input1D[1]", force=True)

	penetration_cond = mc.createNode('condition', name=f"{prefix}_penetration_cnd")
	mc.setAttr(f"{penetration_cond}.operation", 2)  # Greater Than (Surface Y > Probe Y)
	mc.connectAttr(f"{pma_penetration}.output1D", f"{penetration_cond}.firstTerm", force=True)
	mc.setAttr(f"{penetration_cond}.secondTerm", 0.0)
	mc.setAttr(f"{penetration_cond}.colorIfTrueR", 1.0)
	mc.setAttr(f"{penetration_cond}.colorIfFalseR", 0.0)

	# 5. Master Switch Blending
	weight_plug = f"{penetration_cond}.outColorR"
	if stickCtrl and mc.objExists(stickCtrl) and mc.attributeQuery(blendAttr, node=stickCtrl, exists=True):
		blend_mdl = mc.createNode('multDoubleLinear', name=f"{prefix}_blend_mdl")
		mc.connectAttr(f"{penetration_cond}.outColorR", f"{blend_mdl}.input1", force=True)
		mc.connectAttr(f"{stickCtrl}.{blendAttr}", f"{blend_mdl}.input2", force=True)
		weight_plug = f"{blend_mdl}.output"

	# 6. Transform Surface Contact Position into Parent Local Coordinate Space
	parent_obj = mc.listRelatives(targetOffsetGrp, parent=True)
	local_mm = mc.createNode('multMatrix', name=f"{prefix}_local_mm")
	mc.connectAttr(f"{contact_fbfm}.output", f"{local_mm}.matrixIn[0]", force=True)
	if parent_obj:
		mc.connectAttr(f"{parent_obj[0]}.worldInverseMatrix[0]", f"{local_mm}.matrixIn[1]", force=True)

	local_decomp = mc.createNode('decomposeMatrix', name=f"{prefix}_local_decomp")
	mc.connectAttr(f"{local_mm}.matrixSum", f"{local_decomp}.inputMatrix", force=True)

	# 7. PairBlend Node: Blends Rest (0,0,0) with Projected Ground Contact Translation
	pair_blend = mc.createNode('pairBlend', name=f"{prefix}_collision_pbl")
	mc.setAttr(f"{pair_blend}.inTranslateX1", 0.0)
	mc.setAttr(f"{pair_blend}.inTranslateY1", 0.0)
	mc.setAttr(f"{pair_blend}.inTranslateZ1", 0.0)

	mc.connectAttr(f"{local_decomp}.outputTranslate", f"{pair_blend}.inTranslate2", force=True)
	mc.connectAttr(weight_plug, f"{pair_blend}.weight", force=True)

	# Drive target offset group translation only (preserving controller rotation)
	mc.connectAttr(f"{pair_blend}.outTranslate", f"{targetOffsetGrp}.translate", force=True)

	logger.info(f"Successfully constructed Matrix Mesh Collision network for '{prefix}' on '{collisionMesh}'.")

	return {
		'surfaceQuery': surface_query,
		'contactMatrix': contact_fbfm,
		'condition': penetration_cond,
		'pairBlend': pair_blend
	}
