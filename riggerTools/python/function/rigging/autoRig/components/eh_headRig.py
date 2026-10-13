# -*- coding: utf-8 -*-
"""
Module: eh_headRig
Description: Head Rig generator based strictly on original headRig.py logic.
			 Optimized with Matrix Constraints and Matrix Space Switching.
"""

import maya.cmds as mc
from function.framework.reloadWrapper import reloadWrapper as reload

# --- Import Core ---
from function.rigging.autoRig.base import core
reload(core)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

# --- Import Rig Tools ---
from function.rigging.autoRig.base import eh_rigTools as rigTools
reload(rigTools)

# --- Import EH Controller ---
from function.rigging.controllerBox import eh_controller as eh_adjust
reload(eh_adjust)

from function.pipeline import logger
reload(logger)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

class HeadRigLogger(logger.MayaLogger):
	LOGGER_NAME = "HeadRig"

color_part_dict = mnd.COLOR_part_dict


def _createEyeSetup(nameSpace, side, eyeJnt, headJnt, charScale, parentTo, eyeCenCtrl, eyeTarget, matrixConstraint=True):
	"""
	Internal helper to create Eye Rig.
	Logic follows headRig.py _eyeCtrl strictly.
	"""
	# naming logic from original
	part = nameSpace + 'eye' + side

	# 1. Create Bind Joint
	# eyeSide_bJnt = rigTools.jointAt( eyeJntNam )
	eyeSide_bJnt = rigTools.jointAt(eyeJnt)
	eyeSide_bJnt.name = part + '_bJnt'
	eyeSide_bJnt.parent(headJnt)
	eyeSide_bJnt.freeze() # Add freeze transform to get rid orientation

	# 2. Create Controller (Manual Step to match hierarchy: Zro -> Aim -> Ctrl)
	eyeSide_ctrl = core.Dag(part + '_ctrl')
	eyeSide_ctrl.nmCreateController('sphere_ctrlShape')
	eyeSide_ctrl.editCtrlShape(axis=charScale * 1.01)
	eyeSide_ctrl.color = 'softBlue'
	eyeSide_ctrl.rotateOrder = 'zxy'

	# Create Aim Group (Legacy logic: zeroGroup(ctrl) -> name it Aim)
	eyeAimSide_grp = eh_adjust.createZeroGroup(eyeSide_ctrl)
	eyeAimSide_grp.name = part + 'Aim_grp'

	# Create Zero Group (Legacy logic: zeroGroup(aim) -> name it Zro)
	eyeSideZro_grp = eh_adjust.createZeroGroup(eyeAimSide_grp)
	eyeSideZro_grp.name = part + 'Zro_grp'

	# Gimbal
	eyeSideGmbl_ctrl = core.createGimbal(eyeSide_ctrl)
	eyeSideGmbl_ctrl.rotateOrder = 'zxy'

	# Positioning
	eyeSideZro_grp.matchPosition(eyeSide_bJnt)
	#eyeSideZro_grp.matchRotation(eyeSide_bJnt) #... match only position because of RGT side will make alway flip

	# 3. Create Eye Target
	targetPart = nameSpace + 'eyeTarget' + side

	mc.parent(eyeSideZro_grp.name, parentTo)



	# Use eh_adjust for standard controller creation here
	# Target hierarchy: Zro -> Ctrl -> Gimbal (Standard)
	target_zro, target_ctrl, target_gmbl = eh_adjust.create(
		nameSpace=None,
		name=eyeTarget,
		ctrlShape='sphere_ctrlShape',
		rotateOrder='zxy',
		charScale=charScale * 0.8,
		color='softBlue',
		constraint=False,
		parentTo=eyeCenCtrl, # Move zro grp under eyeCenter grp
		rotation=(0,0,0),
		matrixConstraint=False
	)

	# Snap to Target Temp
	# target_zro.maSnap(eyeTarget) #.. no need to snap

	# 4. Aim Constraint (Matrix/Legacy)
	if matrixConstraint:
		mtc.aimConstraintMatrix(
			source=target_ctrl.name,
			target=eyeAimSide_grp.name,
			aimVector=(0, 0, 1),
			upVector=(0, 1, 0),
			worldUpObject='', # Object Rotation mode
			maintainOffset=True
		)
	else:
		eyeAim_aimCons = mc.aimConstraint(
			target_ctrl.name,
			eyeAimSide_grp.name,
			aimVector=(0, 0, 1),
			upVector=(0, 1, 0),
			worldUpType="objectrotation",
			worldUpObject=headJnt,
			mo=True
		)[0]
		mc.rename(eyeAim_aimCons, f"{part}Aim_aimCons")

	# 5. Joint Constraint (Matrix/Legacy)
	if matrixConstraint:
		mtc.parentConMatrixGPT(
			source=eyeSideGmbl_ctrl.name,
			target=eyeSide_bJnt.name,
			mo=False,
			translate=True, rotate=True, scale=True
		)
	else:
		eyeSide_parCons = mc.parentConstraint(eyeSideGmbl_ctrl.name, eyeSide_bJnt.name, mo=False)[0]
		mc.rename(eyeSide_parCons, f"{part}Jnt_parCons")

	# Final Parent
	#eyeSideZro_grp.parent(parentTo)

	# Lock attributes
	for attr in ('rx','ry','rz','sx','sy','sz','v'):
		target_ctrl.attr(attr).lockHide()
	#... new version
	return eyeSide_bJnt



def createHeadRig(
		nameSpace='',
		parentTo='ctrl_grp',
		tmpJnt=(
			'head01_tmpJnt', 'eyeLFT_tmpJnt', 'eyeRGT_tmpJnt',          # 0-2
			'jaw01Lwr_tmpJnt', 'jaw02Lwr_tmpJnt', 'jaw03Lwr_tmpJnt',    # 3-5
			'jaw01Upr_tmpJnt', 'jaw02Upr_tmpJnt',                       # 6-7
			'eye_tmpJnt', 'eyeTargetLFT_tmpJnt', 'eyeTargetRGT_tmpJnt'  # 8-10
		),
		faceCtrl=False,
		priorJnt='', # Neck Joint
		priorCtrl='',
		charScale=1.0,
		ctrlShape='cubeExpand_ctrlShape',
		linkRotOrder=False,
		matrixConstraint=True
	):


	
	core.makeHeader('Start of Head Rig')

	# --- 1. Verify & Setup ---
	head1 = core.Dag(tmpJnt[0])
	if not head1.exists:
		HeadRigLogger.error(f"Head Joint {tmpJnt[0]} not found.")
		#return None

	# --- 2. Create Bind Joint ---
	head01_bJnt = rigTools.jointAt(head1)
	head01_bJnt.name = nameSpace + 'head' + '01' + '_bJnt'

	if mc.objExists(priorJnt) == False:
		mc.error('There are no prior joint.')
		
	head01_bJnt.setLable('CEN','head')
	head01_bJnt.attr('segmentScaleCompensate').value = 0

	# --- 3. Create Head Rig Group ---
	headRig_grp = core.Null()
	headRig_grp.name = nameSpace + 'headRig_grp'
	headRig_grp.matchPosition(head1)
	headRig_grp.matchRotation(head1)

	headRotOrder = 'xzy'

	# --- 4. Head Controller Setup ---
	part = nameSpace + 'head01'
	head_ctrl = core.Dag(part + '_ctrl')
	head_ctrl.nmCreateController(ctrlShape)

	headZro_grp = eh_adjust.createZeroGroup(head_ctrl)
	headZro_grp.name = part + 'Zro_grp'

	head_ctrl.editCtrlShape(axis=charScale * 7.0)
	headGmbl_ctrl = core.createGimbal(head_ctrl)

	ctrl_color = mnd.COLOR_part_dict['primary']
	head_ctrl.color = ctrl_color
	head_ctrl.rotateOrder = headRotOrder
	headGmbl_ctrl.rotateOrder = headRotOrder

	headZro_grp.snap(head1)
	head_ctrl.moveShape(move=(0, charScale * 4.2, 0))
	headGmbl_ctrl.moveShape(move=(0, charScale * 4.2, 0))

	if linkRotOrder:
		head_ctrl.addRotEnum()
		headGmbl_ctrl.addRotEnum()

	# --- 5. Head Local / World Setup (Matrix Optimized) ---
	partName = nameSpace + 'head'


	#... Parent bJnt under prior joint
	head01_bJnt.parent(priorJnt)

	#... Grouping
	headZro_grp.parent(headRig_grp)
	
	if priorCtrl:
		#... Use Hierarchy Parent Instead
		headRig_grp.parent(priorCtrl)
	else:
		# Fallback: Parent to parentTo (like ctrl_grp)
		headRig_grp.parent(parentTo)


	# Using Matrix Orient Switch or legacy orientLocalWorld
	if matrixConstraint:
		mtc.eh_orientLocalWorldMatrix(
			ctrl=head_ctrl.shape,
			localObj=headRig_grp,   
			worldObj=parentTo,      
			target=headZro_grp,
			attrName='localWorld',
			bodyPart=partName
		)
	else:
		from function.rigging.autoRig.base import rigTools as base_rigTools
		base_rigTools.orientLocalWorldCtrl(
			ctrl=head_ctrl.shape,
			localObj=headRig_grp.name,
			worldObj=parentTo,
			baseGrp=headZro_grp.name,
			bodyPart=partName
		)

	# Constraint Joint
	if matrixConstraint:
		mtc.parentConMatrixGPT(
			source=headGmbl_ctrl.name,
			target=head01_bJnt.name,
			mo=True,
			translate=True, rotate=True, scale=True
		)
	else:
		headJnt_parCons = mc.parentConstraint(headGmbl_ctrl.name, head01_bJnt.name, mo=True)[0]
		mc.rename(headJnt_parCons, f"{partName}01_parCons")
		headJnt_sclCons = mc.scaleConstraint(headGmbl_ctrl.name, head01_bJnt.name, mo=True)[0]
		mc.rename(headJnt_sclCons, f"{partName}01_scalCons")






	# --- 6. Face Setup ---
	if faceCtrl:
		HeadRigLogger.info("Starting Face Setup...")

		# JAW SETUP
		jaw1Lwr = tmpJnt[3]
		jaw2Lwr = tmpJnt[4]
		jaw1Upr = tmpJnt[6]

		# if mc.objExists(jaw1Lwr):
		# Create Joints
		jaw1Lwr_bJnt = rigTools.jointAt(jaw1Lwr)
		jaw2Lwr_bJnt = rigTools.jointAt(jaw2Lwr)
		jaw1Lwr_bJnt.name = nameSpace + 'jaw' + '01' +'Lwr' + '_bJnt'
		jaw2Lwr_bJnt.name = nameSpace + 'jaw' + '02' +'Lwr' + '_bJnt'

		jaw1Lwr_bJnt.parent(head01_bJnt)
		jaw2Lwr_bJnt.parent(jaw1Lwr_bJnt)
		jaw1Lwr_bJnt.attr('segmentScaleCompensate').value = 0
		jaw2Lwr_bJnt.attr('segmentScaleCompensate').value = 0

		#jaw1Upr_bJnt = None
		#if mc.objExists(jaw1Upr):
		jaw1Upr_bJnt = rigTools.jointAt(jaw1Upr)
		jaw1Upr_bJnt.name = nameSpace + 'jaw' + '01' +'Upr' + '_bJnt'
		jaw1Upr_bJnt.parent(head01_bJnt)



		# Upper Jaw Ctrl
		# if jaw1Upr_bJnt:
		part = nameSpace + 'jaw01Upr'
		# eh_adjust.create returns (zro, ctrl, gmbl)
		jUpr_zro, jUpr_ctrl, jUpr_gmbl = eh_adjust.create(
			nameSpace=None, name=jaw1Upr_bJnt.name, ctrlShape='squareExpand_ctrlShape',
			rotateOrder=headRotOrder, charScale=charScale * 3.5, color=ctrl_color,
			parentTo=headGmbl_ctrl.name, rotation=(0,0,0), matrixConstraint=matrixConstraint
		)
		#jUpr_zro.snap(jaw1Upr_bJnt)
		#mtc.parentConMatrixGPT(jUpr_gmbl.name, jaw1Upr_bJnt.name, mo=True)

		# mc.error(jaw1Upr_bJnt.name)

		# Lower Jaw Ctrl (01)
		part = nameSpace + 'jaw01Lwr'
		jLwr1_zro, jLwr1_ctrl, jLwr1_gmbl = eh_adjust.create(
		nameSpace=None, name=jaw1Lwr_bJnt.name, ctrlShape='squareExpand_ctrlShape',
		rotateOrder=headRotOrder, charScale=charScale * 2.8, color=ctrl_color,
		parentTo=headGmbl_ctrl.name, rotation=(0,0,0), matrixConstraint=matrixConstraint
		)
		#jLwr1_zro.snap(jaw1Lwr_bJnt)
		jLwr1_ctrl.moveShape(move=(0, charScale * -1.8, charScale * 2.8))
		#mtc.parentConMatrixGPT(jLwr1_gmbl.name, jaw1Lwr_bJnt.name, mo=True)

		# Lower Jaw Ctrl (02 - Gum)
		part = nameSpace + 'jaw02Lwr'
		jLwr2_zro, jLwr2_ctrl, jLwr2_gmbl = eh_adjust.create(
		nameSpace=None, name=jaw2Lwr_bJnt.name, ctrlShape='squareExpand_ctrlShape',
		rotateOrder=headRotOrder, charScale=charScale * 2.8, color=ctrl_color,
		parentTo=jLwr1_gmbl.name, rotation=(0,0,0), matrixConstraint=matrixConstraint
		)
		jLwr2_ctrl.moveShape(move=(0, 0, charScale * 4.2))

		#jLwr2_zro.snap(jaw2Lwr_bJnt)
		#mtc.parentConMatrixGPT(jLwr2_gmbl.name, jaw2Lwr_bJnt.name, mo=True)


		# EYE CENTER SETUP
		eyeCen = tmpJnt[8]
		eyeTargetLFT = tmpJnt[9]
		eyeTargetRGT = tmpJnt[10]
		eyeLFT = tmpJnt[1]
		eyeRGT = tmpJnt[2]

		# if mc.objExists(eyeCen):
		part = nameSpace + 'eyeCenter' + '_tmpJnt'

		eyeCen_obj = core.Dag(eyeCen)


		# Eye Center Ctrl
		eyeCen_zro, eyeCen_ctrl, eyeCen_gmbl = eh_adjust.create(
			nameSpace=None, name=eyeCen, ctrlShape='capsule_ctrlShape',
			rotateOrder=headRotOrder, charScale=charScale * 0.8, color=ctrl_color,
			parentTo=headGmbl_ctrl.name, rotation=(0,0,0),constraint=False, matrixConstraint=matrixConstraint
		)
		#eyeCen_zro.snap(eyeCen_obj) no need to snap 

		#mc.error(eyeTargetLFT)

		# Eye Center Local/World (Matrix/Legacy)
		if matrixConstraint:
			mtc.eh_orientLocalWorldMatrix(
				ctrl=eyeCen_ctrl.shape,
				localObj=headGmbl_ctrl, # Original: headGmbl_ctrl
				worldObj=parentTo,
				target=eyeCen_zro,
				attrName='localWorld',
				parentMode='parent',
				bodyPart=part
			)
		else:
			from function.rigging.autoRig.base import rigTools as base_rigTools
			base_rigTools.orientLocalWorldCtrl(
				ctrl=eyeCen_ctrl.shape,
				localObj=headGmbl_ctrl.name,
				worldObj=parentTo,
				baseGrp=eyeCen_zro.name,
				bodyPart=part
			)

		# Create Eyes
		_createEyeSetup(nameSpace, 'LFT', eyeLFT, head01_bJnt.name, charScale, 
						parentTo=headGmbl_ctrl.name, 
						eyeCenCtrl=eyeCen_ctrl.name, 
						eyeTarget=eyeTargetLFT,
						matrixConstraint=matrixConstraint)
						
		_createEyeSetup(nameSpace, 'RGT', eyeRGT, head01_bJnt.name, charScale, 
						parentTo=headGmbl_ctrl.name, 
						eyeCenCtrl=eyeCen_ctrl.name, 
						eyeTarget=eyeTargetRGT,
						matrixConstraint=matrixConstraint)

	# --- 7. Final Organization ---
	if not priorCtrl and priorJnt and mc.objExists(priorJnt):
		if matrixConstraint:
			mtc.parentConMatrixGPT(
				source=priorJnt,
				target=headRig_grp.name,
				mo=True,
				translate=True, rotate=True, scale=True
			)
		else:
			headRigPrior_parCons = mc.parentConstraint(priorJnt, headRig_grp.name, mo=True)[0]
			mc.rename(headRigPrior_parCons, f"{partName}Prior_parCons")

	mc.select(deselect=True)
	HeadRigLogger.info(f'#### End of {partName} Rig ####')
	return head01_bJnt.name