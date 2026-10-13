# -*- coding: utf-8 -*-
import maya.cmds as mc
from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.util import misc
reload(misc)

# --- Updated Modules ---
from function.rigging.controllerBox import eh_controller as eh_adjust
reload(eh_adjust)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.rigging.autoRig.components.limbRig import eh_midLockModule as midLockModule
reload(midLockModule)

from function.rigging.autoRig.components.limbRig import eh_twistRig as tr
reload(tr)

from function.rigging.autoRig.components.limbRig import eh_createIKStretch as createIK
reload(createIK)

# from function.rigging.autoRig.components.ribbonRig import eh_ribbonRigExt as ribbonRig
# reload(ribbonRig)

# # from function.rigging.autoRig.components.ribbonRig import eh_matrixRibbonRig as ribbonRig
# # reload(ribbonRig)

# from function.rigging.autoRig.components.ribbonRig import eh_hh_ribbonExt as ribbonRig 
# reload(ribbonRig)

from function.rigging.autoRig.components.ribbonRig import eh_hh_matrixRibbonDeBoor as ribbonRig
reload(ribbonRig)

from function.rigging.tools import proc as pc
reload(pc)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

import logging
logger = logging.getLogger('eh_fkIkTwistGenRig')
logger.setLevel(logging.DEBUG)

color_part_dict = mnd.COLOR_part_dict

def fkIkTwistGenRig(
				nameSpace='',				
				charScale=1,			
				parentTo='ctrl_grp',			
				side='LFT',
				region='arm',							
				tmpJnt=('upperArmLFT_tmpJnt', 'lowerArmLFT_tmpJnt', 'handLFT_tmpJnt', 'armPovLFT_tmpJnt'),
				priorJnt='clavLFT_bJnt',	
				ikhGrp='ikh_grp',			
				noTouchGrp='noTouch_grp',			
				nullGrp='snapNull_grp',			
				jnt_grp='jnt_grp',
				showInfo=False,
				ribbon=True,	
				ribbonRes='low',
				ribbonName=('upLeg', 'lwrLeg'),
				propCtrl=False,
				keepFkIkBoth=False,	
				povShape='sphereAxis',
				ikPosi=None,
				linkRotOrder=False,
				ctrlShape='fk_ctrlShape',
				creTwistJnt=True,
				stickShape='stickCircle_Y_long_ctrlShape',
				alongAxis='y',
				pinMethod='matrix',
				povPosi='front',
				aimAxis='y+',
				upAxis='z+',
				createPvSpaceSwitch=True
				):
				
	core.makeHeader(f'Start of {region}{side} Rig (EH Version)')
	
	# Parse axis strings to vectors
	aimVector = mnd.aim_axis_dict.get(aimAxis.lower(), (0, 1, 0))
	upVector = mnd.aim_axis_dict.get(upAxis.lower(), (0, 0, 1))



	# --- 1. Setup Joint & Names ---
	if side == 'LFT':
		colorSide = color_part_dict['left']
	elif side == 'RGT':
		colorSide = color_part_dict['right']
	else:
		colorSide = color_part_dict['primary']

	rotOrder = 'xzy' # Standard for this rig

	# Parse Names
	rawName = [tmp.split('_')[0][:-3] for tmp in tmpJnt]
	
	# Create Bind Joints
	upper_bJnt = rigTools.jointAt(nameSpace + tmpJnt[0])
	middle_bJnt = rigTools.jointAt(nameSpace + tmpJnt[1])
	lower_bJnt = rigTools.jointAt(nameSpace + tmpJnt[2])

	upper_bJnt.name = f"{nameSpace}{rawName[0]}{side}_bJnt"
	middle_bJnt.name = f"{nameSpace}{rawName[1]}{side}_bJnt"
	lower_bJnt.name = f"{nameSpace}{rawName[2]}{side}_bJnt"

	# Hierarchy
	middle_bJnt.parent(upper_bJnt)
	lower_bJnt.parent(middle_bJnt)
	upper_bJnt.parent(priorJnt)

	# Set Attributes
	for jnt in [upper_bJnt, middle_bJnt, lower_bJnt]:
		jnt.rotateOrder = rotOrder
		jnt.attr('segmentScaleCompensate').value = 0
		# Note: Freezing joint is generally risky for auto-rigs if joints have orientation, 
		# but following original logic:
		jnt.freeze() 

	# --- 2. Main Groups ---
	part = nameSpace + rawName[2] # e.g. hand or ankle
	fkIkRig_grp = core.Null(f"{part}Rig{side}_grp")
	fkIkJnt_grp = core.Null(f"{part}Jnt{side}_grp")
	
	# IMPORTANT: Parent groups to hierarchy BEFORE binding matrix constraints.
	# If parented afterwards, offsetParentMatrix misses the inverse parent context, causing double transformation!
	fkIkRig_grp.parent(parentTo)
	fkIkJnt_grp.parent(jnt_grp)
	fkIkJnt_grp.attr('visibility').value = 0

	# Group Constraint (Matrix)
	mtc.parentConMatrixGPT(priorJnt, fkIkRig_grp.name, mo=True)

	# --- 3. Stick Controller (The Switch) ---
	stickName = rawName[2] + 'Stick'
	stick_ctrl = core.Dag(f"{nameSpace}{stickName}{side}_ctrl")
	stick_ctrl.nmCreateController(stickShape)
	
	stickZro_grp = eh_adjust.createZeroGroup(stick_ctrl)
	stickZro_grp.name = f"{nameSpace}{stickName}{side}Zro_grp"
	
	stick_ctrl.editCtrlShape(axis=charScale * 1.8)
	stick_ctrl.color = 'yellow'
	stick_ctrl.hideArnoldNode()

	# Positioning
	stickZro_grp.matchPosition(lower_bJnt)
	stickZro_grp.matchRotation(lower_bJnt)
	
	# IMPORTANT: Parent BEFORE matrix constraint to avoid double transformations
	stickZro_grp.parent(parentTo)

	# Orientation Fixes (Legacy Logic)
	if region in ['leg', 'frontLeg', 'backLeg']:
		val = -90 if side == 'LFT' else 90
		stick_ctrl.attr('rotateX').value = val
	elif region == 'arm':
		val = 90 if side == 'LFT' else -90
		stick_ctrl.attr('rotateZ').value = val

	# Constraint Stick to Lower (Matrix)
	mtc.parentConMatrixGPT(lower_bJnt.name, stickZro_grp.name, mo=True)

	# Attributes
	stickScalNam = 'hand' if region == 'arm' else region
	attScaleName = f"{stickScalNam}Scale"
	stick_ctrl.addAttribute(longName=attScaleName, defaultValue=1, keyable=True)
	stick_ctrl.lockHideAttrLst('tx','ty','tz','rx','ry','rz','sx','sy','sz','v')

	# --- 4. FK System ---
	fkCtrl_grp = core.Null(f"{part}FkCtrl{side}_grp")
	fkCtrl_grp.snap(priorJnt)
	fkCtrl_grp.parent(fkIkRig_grp)

	fkJnt_grp = core.Null(f"{part}FkJnt{side}_grp")
	fkJnt_grp.snap(priorJnt)
	fkJnt_grp.parent(fkIkJnt_grp)

	# FK Joints
	upper_fkJnt = rigTools.jointAt(upper_bJnt)
	middle_fkJnt = rigTools.jointAt(middle_bJnt)
	lower_fkJnt = rigTools.jointAt(lower_bJnt)

	upper_fkJnt.name = f"{nameSpace}{rawName[0]}{side}_fkJnt"
	middle_fkJnt.name = f"{nameSpace}{rawName[1]}{side}_fkJnt"
	lower_fkJnt.name = f"{nameSpace}{rawName[2]}{side}_fkJnt"

	middle_fkJnt.parent(upper_fkJnt)
	lower_fkJnt.parent(middle_fkJnt)
	upper_fkJnt.parent(fkJnt_grp)

	# FK Controllers using eh_adjust
	# Upper
	upr_zro, upr_ctrl, upr_gmbl = eh_adjust.create(
		nameSpace, f"{rawName[0]}Fk{side}_ctrl", ctrlShape, rotOrder, 
		parentTo=fkCtrl_grp.name, charScale=charScale*0.9, color=colorSide, 
		constraint=False # Matrix Constraint handled manually below
	)
	if side == 'RGT': upr_ctrl.flipCtrlShape(axis='Y', color=colorSide)
	upr_zro.matchPosition(upper_fkJnt)
	upr_zro.matchRotation(upper_fkJnt)
	# Re-apply constraint to ensure correct target (since we matched after creation)
	mtc.parentConMatrixGPT(upr_gmbl.name, upper_fkJnt.name, mo=True, baseName=f"{nameSpace}{rawName[0]}{side}_trFK")
	mtc.parentConMatrixGPT(upr_gmbl.name, upper_fkJnt.name, mo=True, translate=False, rotate=False, scale=True, baseName=f"{nameSpace}{rawName[0]}{side}_scaleFK")

	# Middle
	mid_zro, mid_ctrl, mid_gmbl = eh_adjust.create(
		nameSpace, f"{rawName[1]}Fk{side}_ctrl", ctrlShape, rotOrder, 
		parentTo=upr_gmbl.name, charScale=charScale*0.8, color=colorSide,
		constraint=False
	)
	if side == 'RGT': mid_ctrl.flipCtrlShape(axis='Y', color=colorSide)
	mid_zro.matchPosition(middle_fkJnt)
	mid_zro.matchRotation(middle_fkJnt)
	mtc.parentConMatrixGPT(mid_gmbl.name, middle_fkJnt.name, mo=True, baseName=f"{nameSpace}{rawName[1]}{side}_trFK")
	mtc.parentConMatrixGPT(mid_gmbl.name, middle_fkJnt.name, mo=True, translate=False, rotate=False, scale=True, baseName=f"{nameSpace}{rawName[1]}{side}_scaleFK")

	# Lower
	lwr_zro, lwr_ctrl, lwr_gmbl = eh_adjust.create(
		nameSpace, f"{rawName[2]}Fk{side}_ctrl", ctrlShape, rotOrder, 
		parentTo=mid_gmbl.name, charScale=charScale*0.7, color=colorSide,
		constraint=False
	)
	if side == 'RGT': lwr_ctrl.flipCtrlShape(axis='Y', color=colorSide)
	lwr_zro.matchPosition(lower_fkJnt)
	lwr_zro.matchRotation(lower_fkJnt)
	mtc.parentConMatrixGPT(lwr_gmbl.name, lower_fkJnt.name, mo=True, baseName=f"{nameSpace}{rawName[2]}{side}_trFK")
	mtc.parentConMatrixGPT(lwr_gmbl.name, lower_fkJnt.name, mo=True, translate=False, rotate=False, scale=True, baseName=f"{nameSpace}{rawName[2]}{side}_scaleFK")

	# Space Switching for Upper Arm (FK)
	# [0] controller itself, [1] local group space, [2] world group space, [3] zero group of controller
	mtc.eh_orientLocalWorldMatrix(
		ctrl=upr_ctrl, 
		localObj=fkCtrl_grp, 
		worldObj=parentTo, 
		target=upr_zro, 
		attrName='localWorld', 
		bodyPart=f"{nameSpace}{rawName[0]}Fk{side}"
	)
	# Need to query the created groups from eh_orientLocalWorldMatrix if we want to return them
	# But for now, we assume the function handles the structure correctly.
	# (Note: Original code returned Loc_grp, World_grp variables. eh_orientLocalWorldMatrix returns a dict of nodes)

	# --- 5. IK System ---
	ikCtrl_grp = core.Null(f"{part}IkCtrl{side}_grp")
	ikCtrl_grp.snap(priorJnt)
	ikCtrl_grp.parent(fkIkRig_grp)

	ikJnt_grp = core.Null(f"{part}IkJnt{side}_grp")
	ikJnt_grp.snap(priorJnt)
	ikJnt_grp.parent(fkIkJnt_grp)

	# IK Joints
	upper_IkJnt = rigTools.jointAt(upper_bJnt)
	middle_IkJnt = rigTools.jointAt(middle_bJnt)
	lower_IkJnt = rigTools.jointAt(lower_bJnt)

	upper_IkJnt.name = f"{nameSpace}{rawName[0]}{side}_ikJnt"
	middle_IkJnt.name = f"{nameSpace}{rawName[1]}{side}_ikJnt"
	lower_IkJnt.name = f"{nameSpace}{rawName[2]}{side}_ikJnt"

	middle_IkJnt.parent(upper_IkJnt)
	lower_IkJnt.parent(middle_IkJnt)
	upper_IkJnt.parent(ikJnt_grp)

	# Create IK Handle
	ikhName = mc.ikHandle(n=f"{part}Ik{side}_ikh", sj=upper_IkJnt.name, ee=lower_IkJnt.name, sol='ikRPsolver')
	mc.rename(ikhName[1], f"{lower_IkJnt.name}_eff")
	ikhNam = ikhName[0]
	mc.setAttr(f"{ikhNam}.visibility", 0)

	#... IK Controller Setup
	if region in ['leg', 'frontLeg', 'backLeg']:
		ikShape = 'rectanglePlain_ctrlShape'
		ikScaleMult = 40 # Larger for Leg
	else:
		ikShape = 'cube_ctrlShape'
		ikScaleMult = 8 # Normal for Arm

	# Using eh_adjust.create
	ikZro_grp, lowerIk_ctrl, ikGmbl_ctrl = eh_adjust.create(
		nameSpace=None,
		name=f"{nameSpace}{rawName[2]}Ik{side}_ctrl", 
		ctrlShape=ikShape,
		rotateOrder=rotOrder,
		charScale=charScale * ikScaleMult,
		color=colorSide,
		parentTo=ikhGrp, # Parent to independent ikh_grp so it doesn't follow COG/placement
		constraint=False, # We handle constraints manually
		matrixConstraint=False
	)
	
	lowerIk_ctrl.addAttribute(at='long', ln='autoStretch', k=True, min=0, max=1, dv=0)
	lowerIk_ctrl.addAttribute(at='float', ln='upStretch', k=True, dv=0)
	lowerIk_ctrl.addAttribute(at='float', ln='lowStretch', k=True, dv=0)

	# Orient IK Controller
	if region == 'arm':
		misc.snapParentConst(lower_IkJnt.name, ikZro_grp.name)
	else:
		misc.snapPointConst(lower_IkJnt.name, ikZro_grp.name)

	# Constraint Joint to Controller (Matrix Orient)
	mtc.orientConstraintMatrix(ikGmbl_ctrl.name, lower_IkJnt.name, mo=True, baseName=f"{nameSpace}{rawName[2]}{side}_rotIK")

	# IKH Hierarchy with SoftIK Prep
	ikhZro_grp = mc.group(em=True, n=f"{part}Ikh{side}Zro_grp")
	misc.snapParentConst(lower_bJnt.name, ikhZro_grp)
	mc.parent(ikhZro_grp, ikGmbl_ctrl.name)
	mc.parent(ikhNam, ikhZro_grp)
	mc.rotate(0, 0, 0, ikhNam, os=True, fo=True)

	# Pole Vector
	povZro_grp = mc.group(em=True, n=f"{nameSpace}{rawName[3]}{side}Zro_grp")
	pov_ctrl = core.Dag(f"{nameSpace}{rawName[3]}{side}_ctrl")
	
	# Shape Logic
	if povShape == 'pyramid':
		pov_ctrl.nmCreateController('pyramid_ctrlShape')
		pov_ctrl.rotateShape(rotate=(90, 0, 0))
		pc.targetPov(ctrl=pov_ctrl.name, jnt=middle_bJnt.name)
	else:
		pov_ctrl.nmCreateController('legLFT_pov_ctrlShape')
	
	pov_ctrl.editCtrlShape(axis=charScale*1.4)
	pov_ctrl.setColor(colorSide)
	mc.parent(pov_ctrl.name, povZro_grp)
	
	# Snap POV
	misc.snapPointConst(f"{nameSpace}{tmpJnt[3]}", povZro_grp)
	
	# Pole Vector Constraint (Standard PV constraint is best, Matrix PV exists but standard is reliable)
	# NOTE: Using standard constraint for PV is usually fine, or custom Matrix calculation. 
	# Let's use standard for now to match original reliability unless requested otherwise.
	mc.poleVectorConstraint(pov_ctrl.name, ikhNam, w=1, n=f"{nameSpace}{rawName[0]}Pov{side}_povCons")
	mc.parent(povZro_grp, ikZro_grp.name)

	# Space Switch for POV
	if createPvSpaceSwitch:
		mtc.eh_orientLocalWorldMatrix(
			ctrl=pov_ctrl,
			localObj=ikGmbl_ctrl,
			worldObj=parentTo,
			target=povZro_grp,
			attrName='localWorld',
			parentMode='parent', # Use Parent Mode (Trans+Rot) for PV space
			bodyPart=f"{nameSpace}{rawName[0]}Pov{side}"
		)

	# IK Root Controller
	ikRootName = f"{nameSpace}{rawName[0]}IkRoot{side}_ctrl"
	ikRootZro, ikRoot_ctrl, ikRootGmbl = eh_adjust.create(
		nameSpace=None, name=ikRootName, ctrlShape='cube_ctrlShape',
		rotateOrder=rotOrder, charScale=charScale*5.5, color='yellow',
		parentTo=ikCtrl_grp.name, constraint=False
	)
	ikRootZro.snap(upper_bJnt)
	
	# Matrix Parent Constraint IK Root -> IK Joint
	mtc.parentConMatrixGPT(ikRootGmbl.name, upper_IkJnt.name, mo=True, baseName=f"{nameSpace}{rawName[0]}{side}_rotIK")

	# --- 6. IK Stretch (Refactored Module) ---
	# Passing updated arguments to createIKStretch
	pmaNode, psStreEndName = createIK.iKStretch(
		ikJnt=(upper_IkJnt.name, middle_IkJnt.name, lower_IkJnt.name),
		ikCtrl=(ikRoot_ctrl.name, lowerIk_ctrl.name),
		side=side, scaleCtrl='placement_ctrl',
		region=region, noTouchGrp=noTouchGrp, nameSpace=nameSpace,
		lowNam=rawName[2], alongAxis=alongAxis, povPosi=povPosi
	)

	# --- 7. FK/IK Switch Attributes ---
	stick_ctrl.addAttribute(attributeType='float', longName='FK_IK', min=0, max=1, dv=0, k=True)
	if keepFkIkBoth:
		stick_ctrl.addAttribute(attributeType='bool', longName='fkVis', min=0, max=1, dv=1, k=True)
		stick_ctrl.addAttribute(attributeType='bool', longName='ikVis', min=0, max=1, dv=1, k=True)

	# --- 7.5 Adding message to attr ---
	logger.info('Create message attributes')
	if not mc.objExists(f"{stick_ctrl.name}.region"):
		stick_ctrl.addAttribute(dataType='string', longName='region')
		stick_ctrl.setAttribute('region', region, type='string')
		stick_ctrl.lockHideAttrLst('region')

	if not mc.objExists(f"{stick_ctrl.name}.location"):
		stick_ctrl.addAttribute(dataType='string', longName='location')
		stick_ctrl.setAttribute('location', region, type='string')

	if not mc.objExists(f"{stick_ctrl.name}.scale_Attr"):
		stick_ctrl.addAttribute(dataType='string', longName='scale_Attr')
		stick_ctrl.setAttribute('scale_Attr', attScaleName, type='string')
		stick_ctrl.lockHideAttrLst('scale_Attr')

	message_Dict = mnd.MESSAGE_dict
	for keys in message_Dict:
		if keys != 'listString':
			for each in message_Dict[keys]:
				if not mc.objExists(f"{stick_ctrl.name}.{each}"):
					stick_ctrl.addAttribute(attributeType='message', longName=each)

	# Strict validation: Ensure critical message attributes were generated from mnd.MESSAGE_dict
	for each in ['stick', 'upJnt', 'midJnt', 'lowJnt', 'upFkCtrl', 'midFkCtrl', 'lowFkCtrl', 'pov', 'ikCtrl', 'ikRootCtrl']:
		if not mc.objExists(f"{stick_ctrl.name}.{each}"):
			mc.error(f"[{region}{side}] Blueprint Error: Critical attribute '{each}' is missing on '{stick_ctrl.name}'! It is not defined in mnd.MESSAGE_dict. Please update generic_maya_dict.py immediately.")

	stick_ctrl.attr('message') >> stick_ctrl.attr('stick')
	upper_bJnt.attr('message') >> stick_ctrl.attr('upJnt')
	middle_bJnt.attr('message') >> stick_ctrl.attr('midJnt')
	lower_bJnt.attr('message') >> stick_ctrl.attr('lowJnt')
	upr_ctrl.attr('message') >> stick_ctrl.attr('upFkCtrl')
	mid_ctrl.attr('message') >> stick_ctrl.attr('midFkCtrl')
	lwr_ctrl.attr('message') >> stick_ctrl.attr('lowFkCtrl')
	pov_ctrl.attr('message') >> stick_ctrl.attr('pov')
	lowerIk_ctrl.attr('message') >> stick_ctrl.attr('ikCtrl')
	ikRoot_ctrl.attr('message') >> stick_ctrl.attr('ikRootCtrl')

	# --- 8. Buffer Joints & Blending (The Critical Part) ---
	# To replace parentConstraint(w0,w1) we use mtc.parentMulMatrix
	
	buffJnt_grp = core.Null(f"{nameSpace}{region}BuffJnt{side}_grp")
	buffJnt_grp.parent(fkIkJnt_grp)

	upper_buffJnt = rigTools.jointAt(upper_bJnt)
	middle_buffJnt = rigTools.jointAt(middle_bJnt)
	lower_buffJnt = rigTools.jointAt(lower_bJnt)

	upper_buffJnt.name = f"{nameSpace}{rawName[0]}{side}_buffJnt"
	middle_buffJnt.name = f"{nameSpace}{rawName[1]}{side}_buffJnt"
	lower_buffJnt.name = f"{nameSpace}{rawName[2]}{side}_buffJnt"

	middle_buffJnt.parent(upper_buffJnt)
	lower_buffJnt.parent(middle_buffJnt)
	upper_buffJnt.parent(buffJnt_grp)

	# Blending Loop
	jnt_names = [rawName[0], rawName[1], rawName[2]]
	for i, base in enumerate(jnt_names):
		fk_jnt = f"{nameSpace}{base}{side}_fkJnt"
		ik_jnt = f"{nameSpace}{base}{side}_ikJnt"
		buff_jnt = f"{nameSpace}{base}{side}_buffJnt"
		
		# Use parentMulMatrix from mtc
		# Note: parentMulMatrix returns the wtAddMatrix node
		# src=[fk, ik], tgt=buff
		wt_node = mtc.parentMulMatrix(src=[fk_jnt, ik_jnt], tgt=buff_jnt, mo=True, t=True, r=True, s=True)
		
		# Connect Blending
		# Weight 0 (FK) = 1 - FK_IK
		# Weight 1 (IK) = FK_IK
		
		revNode = core.ReverseNam(f"{nameSpace}{base}Switch{side}_rev")
		stick_ctrl.attr('FK_IK') >> revNode.attr('inputX')
		
		# parentMulMatrix returns the NAME of wtAddMatrix.
		
		mc.connectAttr(revNode.name + '.outputX', wt_node + '.wtMatrix[0].weightIn', f=True)
		mc.connectAttr(stick_ctrl.name + '.FK_IK', wt_node + '.wtMatrix[1].weightIn', f=True)
	

	# --- 9. Visibility Switching ---
	if keepFkIkBoth:
		stick_ctrl.attr('ikVis') >> ikZro_grp.attr('visibility')
		stick_ctrl.attr('ikVis') >> ikRootZro.attr('visibility')
		stick_ctrl.attr('fkVis') >> fkCtrl_grp.attr('visibility')
	else:
		stickVis_rev = core.Reverse()
		stickVis_rev.name = f"{part}StickVis{side}_rev"
		stick_ctrl.attr('FK_IK') >> stickVis_rev.attr('inputX')
		
		stickVis_rev.attr('outputX') >> fkCtrl_grp.attr('visibility')
		stick_ctrl.attr('FK_IK') >> ikZro_grp.attr('visibility')
		stick_ctrl.attr('FK_IK') >> ikRootZro.attr('visibility')

	# --- 10. Mid Lock (Elbow/Knee) ---
	# Using updated midLockModule
	logger.info("Creating Knee/Elbow Lock...")
	rawNameUPR, distanceUPRName, povUPR_Ctrl, lowerUPR_loc, upperUPR_loc = midLockModule.createDistance(
		nameSpace, part='up', startP=ikRootGmbl.name, endP=pov_ctrl.name
	)
	rawNameLWR, distanceLWRName, povLWR_Ctrl, lowerLWR_loc, upperLWR_loc = midLockModule.createDistance(
		nameSpace, part='dn', startP=pov_ctrl.name, endP=ikGmbl_ctrl.name
	)
	
	blendName, invertNodeName = midLockModule.createBlendColor(
		nameSpace, uprDistance=distanceUPRName, lwrDistance=distanceLWRName, side=side, uprNam=rawNameUPR
	)
	attrName = midLockModule.doAddAttr(povUPR_Ctrl, region)
	midLockModule.connectIkJnt(
		stretchNode=pmaNode, upperIKJnt=middle_IkJnt.name, lowerIKJnt=lower_IkJnt.name,
		blendName=blendName, namLock=attrName, povName=povUPR_Ctrl, alongAxis=alongAxis
	)

	# --- 11. Scale Connections ---
	stick_ctrl.attr(attScaleName) >> lower_buffJnt.attr('sx')
	stick_ctrl.attr(attScaleName) >> lower_buffJnt.attr('sy')
	stick_ctrl.attr(attScaleName) >> lower_buffJnt.attr('sz')

	# --- 12. Ribbon & Twist Setup ---
	if ribbon:
		
		numJoints = 5 if ribbonRes == 'high' else 3


		upr_ribbonRig_list, upr_jnt_list, upr_localAim_grps= ribbonRig.performMatrixRibbonRig(
			charScale = charScale,
			jointTop = upper_bJnt.name	,
			jointBtm = middle_bJnt.name,
			aim_axis='y+',
			up_axis='z+',
			numJnts=5, #.. using 5 or 7 only
			baseName=f"{nameSpace}{ribbonName[0]}",
			side=side,
			ctrl_grp = parentTo,
			debug = False,
			rotOrder=rotOrder
			)



		lwr_ribbonRig_list, lwr_jnt_list, lwr_localAim_grps = ribbonRig.performMatrixRibbonRig(
			charScale = charScale,
			jointTop = middle_bJnt.name	,
			jointBtm = lower_bJnt.name,
			aim_axis='y+',
			up_axis='z+',
			numJnts=5, #.. using 5 or 7 only
			baseName=f"{nameSpace}{ribbonName[1]}",
			side=side,
			ctrl_grp = parentTo,
			debug = False,
			rotOrder=rotOrder
			)


		# hingesUprBtm = ribbonRig.ribbonRigExt(
		# 	nameSpace=nameSpace, width=10, numJoints=numJoints, side=side,
		# 	jointTop=upper_bJnt.name, jointBtm=middle_bJnt.name,
		# 	part=ribbonName[0], charScale=charScale, noTouch_grp=noTouchGrp,
		# 	showInfo=showInfo, ctrl_grp=fkIkRig_grp.name, alongAxis=alongAxis, debug = True)
		# hingesLwrTop = ribbonRig.ribbonRigExt(
		# 	nameSpace=nameSpace, width=10, numJoints=numJoints, side=side,
		# 	jointTop=middle_bJnt.name, jointBtm=lower_bJnt.name,
		# 	part=ribbonName[1], charScale=charScale, noTouch_grp=noTouchGrp,
		# 	showInfo=showInfo, ctrl_grp=fkIkRig_grp.name, alongAxis=alongAxis, debug = True)

		# mc.error(f'This is hingesUprBtm{hingesUprBtm}\n This is hingesLwrTop{hingesLwrTop}')

		# --- Ribbon End Connections (Solving Issue 1 & 2) ---
		# Upper Ribbon: Top to Shoulder (make plus controller follow upperArm)
		mtc.parentConMatrixGPT(upper_bJnt.name, upr_ribbonRig_list[0][1], mo=True, baseName=f"{nameSpace}{ribbonName[0]}TopRbn{side}_follow")
		# Give Upper Ribbon Bottom CV (at elbow) rotation from Elbow Twist (Quaternion)
		# mtc.parentConMatrixGPT(upper_bJnt.name, upr_ribbonRig_list[2][1], mo=True, translate=False, scale=False, baseName=f"{nameSpace}{ribbonName[0]}BtmRbn{side}_rotFollow")
		
		# Lower Ribbon: Top to Elbow
		# Note: makeHigesMover already handles the translation for the top CV of the lower ribbon at the elbow.
		# But for the bottom CV (at wrist), we apply the same		# For the bottom CV (at wrist), follow Wrist twist (Quaternion)
		mtc.parentConMatrixGPT(lower_bJnt.name, lwr_ribbonRig_list[2][1], mo=True, rotate=False, baseName=f"{nameSpace}{ribbonName[1]}BtmRbn{side}_trFollow")
		# mtc.parentConMatrixGPT(middle_bJnt.name, lwr_ribbonRig_list[2][1], mo=True, translate=False, scale=False, baseName=f"{nameSpace}{ribbonName[1]}BtmRbn{side}_rotFollow")
		
		
		#... [step:513][uprArm][btm]_make mid ctrl twist follow
		mtc.eh_aimMatrixConstraint(
			aim_object=upper_bJnt.name,
			up_object=f"{nameSpace}{ribbonName[0]}UpVec{side}_loc",
			target=upr_localAim_grps[1],
			aimVector=aimVector,
			upVector=upVector,
			mo=True,
			baseName=f"{nameSpace}{ribbonName[0]}BtmRbn{side}"
		)

		# Add auto_twist attr on shape
		uprMidShape = core.Dag(core.Dag(f"{nameSpace}{ribbonName[0]}MidRbn{side}_ctrl").shape)
		if not mc.attributeQuery('auto_twist', node=uprMidShape.name, exists=True):
			uprMidShape.addAttribute(attributeType='float', longName='auto_twist', minValue=0, maxValue=1, defaultValue=1, keyable=True)

		upr_e2q, upr_q2e = core.extract_rotationToQuat(
			baseName=f"{nameSpace}{ribbonName[0]}BtmTwist{side}",
			source=middle_bJnt.name,
			target=f"{nameSpace}{ribbonName[0]}BtmRbn{side}_loc",
			rotAxis='y'
		)

		uprTwist_md = mc.createNode('multiplyDivide', n=f"{nameSpace}{ribbonName[0]}BtmTwist{side}_md")
		mc.disconnectAttr(f"{upr_q2e.name}.outputRotate", f"{nameSpace}{ribbonName[0]}BtmRbn{side}_loc.rotate")
		mc.connectAttr(f"{upr_q2e.name}.outputRotate", f"{uprTwist_md}.input1")
		
		mc.connectAttr(f"{uprMidShape.name}.auto_twist", f"{uprTwist_md}.input2X")
		mc.connectAttr(f"{uprMidShape.name}.auto_twist", f"{uprTwist_md}.input2Y")
		mc.connectAttr(f"{uprMidShape.name}.auto_twist", f"{uprTwist_md}.input2Z")
		
		mc.connectAttr(f"{uprTwist_md}.output", f"{nameSpace}{ribbonName[0]}BtmRbn{side}_loc.rotate")

		#... [step:513][lwrArm][btm]_make mid ctrl twist follow
		mtc.eh_aimMatrixConstraint(
			aim_object=middle_bJnt.name,
			up_object=f"{nameSpace}{ribbonName[1]}UpVec{side}_loc",
			target=lwr_localAim_grps[1],
			aimVector=aimVector,
			upVector=upVector,
			mo=True,
			baseName=f"{nameSpace}{ribbonName[1]}BtmRbn{side}"
		)

		# Add auto_twist attr on shape
		lwrMidShape = core.Dag(core.Dag(f"{nameSpace}{ribbonName[1]}MidRbn{side}_ctrl").shape)
		if not mc.attributeQuery('auto_twist', node=lwrMidShape.name, exists=True):
			lwrMidShape.addAttribute(attributeType='short', longName='auto_twist', minValue=0, maxValue=1, defaultValue=1, keyable=True)

		lwr_e2q, lwr_q2e = core.extract_rotationToQuat(
			baseName=f"{nameSpace}{ribbonName[1]}BtmTwist{side}",
			source=lower_bJnt.name,
			target=f"{nameSpace}{ribbonName[1]}BtmRbn{side}_loc",
			rotAxis='y'
		)

		lwrTwist_md = mc.createNode('multiplyDivide', n=f"{nameSpace}{ribbonName[1]}BtmTwist{side}_md")
		mc.disconnectAttr(f"{lwr_q2e.name}.outputRotate", f"{nameSpace}{ribbonName[1]}BtmRbn{side}_loc.rotate")
		mc.connectAttr(f"{lwr_q2e.name}.outputRotate", f"{lwrTwist_md}.input1")
		
		mc.connectAttr(f"{lwrMidShape.name}.auto_twist", f"{lwrTwist_md}.input2X")
		mc.connectAttr(f"{lwrMidShape.name}.auto_twist", f"{lwrTwist_md}.input2Y")
		mc.connectAttr(f"{lwrMidShape.name}.auto_twist", f"{lwrTwist_md}.input2Z")
		
		mc.connectAttr(f"{lwrTwist_md}.output", f"{nameSpace}{ribbonName[1]}BtmRbn{side}_loc.rotate")

		# --- Ribbon Bind Joint Creation (Solving Issue 3) ---
		for rbn_jnts, part_name, parent_jnt in [(upr_jnt_list, rawName[0], upper_bJnt.name), (lwr_jnt_list, rawName[1], middle_bJnt.name)]:
			for i, pxy in enumerate(rbn_jnts):
				
				# Determine suffix based on position (filter out hinge overlaps)
				suffix = "_rbnBJnt"
				if (part_name == rawName[0] and i == len(rbn_jnts) - 1) or (part_name == rawName[1] and i == 0):
					suffix = "_jnt"

				# Create actual joint
				bJnt_name = f"{nameSpace}{part_name}Rbn{i+1:02d}{side}{suffix}"
				rbn_bJnt = core.Joint(bJnt_name)
				rbn_bJnt.maSnap(pxy)
				
				# Parent to main root bJnt chain
				mc.parent(rbn_bJnt.name, parent_jnt)
				
				# Freeze Transform before constraint
				rbn_bJnt.freeze()
				
				rbn_bJnt.attr('radius').value = charScale * 1.5
				rbn_bJnt.attr('overrideEnabled').value = 1
				rbn_bJnt.attr('overrideColor').value = 3
				rbn_bJnt.rotateOrder = rotOrder
				rbn_bJnt.attr('segmentScaleCompensate').value = 0
				
				# Constraint bJnt to pxyJnt (Matrix Constraint)
				mtc.parentConMatrixGPT(pxy, rbn_bJnt.name, mo=True, baseName=f"{bJnt_name}_follow")

				# Extra settings for filtered joints (overlaps at hinge)
				if suffix == "_jnt":
					rbn_bJnt.attr('visibility').value = 0
					rbn_bJnt.attr('overrideDisplayType').value = 1  # Template mode

		ribbonRig.makeHigesMover(
			part=region, nameSpace=nameSpace, side=side,
			btmName=upr_ribbonRig_list, topName=lwr_ribbonRig_list,
			charScale=charScale, moverPosition=middle_buffJnt.name,
			ctrl_grp=fkIkRig_grp.name, alongAxis=alongAxis)

		#... Hide overlapping detail controllers at the elbow hinge
		upr_last_detail = f"{nameSpace}{ribbonName[0]}RbnDetail{numJoints:02d}{side}_ctrl"
		lwr_first_detail = f"{nameSpace}{ribbonName[1]}RbnDetail01{side}_ctrl"
		
		if mc.objExists(upr_last_detail):
			mc.setAttr(f"{upr_last_detail}.visibility", 0)
		if mc.objExists(lwr_first_detail):
			mc.setAttr(f"{lwr_first_detail}.visibility", 0)


		# mc.error('BREAK for debug')


	#... Twist Rig
	if creTwistJnt:
		logger.info('Create Twist Rig function ...')
		# Updated to accept ikRoot_ctrl.name (which we have) and use matrix constraints internally
		follow_grp, upperTwist01 = tr.twistRigAuto(
			nameSpace=nameSpace, parent_jnt=upper_buffJnt.name, child_jnt=middle_buffJnt.name,
			fk_shoulderCtrl=upr_ctrl.name, ik_shoulderCtrl=ikRoot_ctrl.name,
			side=side, region=region, priorJnt=priorJnt, stick_ctrl=stick_ctrl.name,
			charScale=charScale, showInfo=showInfo, alongAxis=alongAxis
		)
		mc.parent(follow_grp, noTouchGrp)

	# --- 13. Final Connections (Buffer -> Bind) ---
	regionCap = region.capitalize()
	
	# Using Matrix Constraints for final drive
	if creTwistJnt:
		# Upper bind joint follows the twist joint
		mtc.parentConMatrixGPT(upperTwist01, upper_bJnt.name, mo=True)
	else:
		# Upper bind joint follows the buffer joint directly
		mtc.parentConMatrixGPT(upper_buffJnt.name, upper_bJnt.name, mo=True)

	mtc.parentConMatrixGPT(middle_buffJnt.name, middle_bJnt.name, mo=True)
	mtc.parentConMatrixGPT(lower_buffJnt.name, lower_bJnt.name, mo=True)

	# mc.error('BREAK for DEBUG.................................')

	# --- 14. Meta Data ---
	# (Keeping original Meta logic, just ensuring variables match)
	fkIkTwistRig_meta = core.MetaGeneric(f"{nameSpace}{region.lower()}FkIkTwistRig{side}_meta")
	mc.connectAttr(f"{priorJnt}.message", f"{fkIkTwistRig_meta.name}.Rig_Prior")
	
	# Add Attributes
	for attr in ['ikh_Name', 'ikh_Zro_Name', 'stick_ctrl_name', 'ikh_ctrl_name']:
		fkIkTwistRig_meta.addAttribute(dataType='string', longName=attr)

	fkIkTwistRig_meta.setAttribute('Base_Name', __name__, type='string')
	fkIkTwistRig_meta.setAttribute('Side', side, type='string')
	fkIkTwistRig_meta.setAttribute('ikh_Name', ikhNam, type='string')
	fkIkTwistRig_meta.setAttribute('ikh_Zro_Name', ikhZro_grp, type='string')
	fkIkTwistRig_meta.setAttribute('stick_ctrl_name', stick_ctrl.name, type='string')
	fkIkTwistRig_meta.setAttribute('ikh_ctrl_name', lowerIk_ctrl.name, type='string')

	# Connect to Stick
	metaName = mnd.MESSAGE_dict['meta'][0]
	if not mc.objExists(f"{stick_ctrl.name}.{metaName}"):
		stick_ctrl.addAttribute(attributeType='message', longName=metaName)
	fkIkTwistRig_meta.attr('message') >> stick_ctrl.attr(metaName)
	fkIkTwistRig_meta.lockAllAttr()

	# Return data for SoftIK
	# ikhNam, povZro_grp, Loc_grp, World_grp, ikhZro_grp (Loc/World comes from eh_orientLocalWorldMatrix dict return)
	# Since eh_orient return a dict, we need to extract logic or just pass what's needed.
	# Original returned: Loc_grp.name, World_grp.name
	# eh_orientLocalWorldMatrix returns: {"mult_local":..., "mult_world":...}
	# SoftIK mainly needs ikhNam and ctrlName.
	
	ikhAll_name = (ikhNam, povZro_grp, "Local_Placeholder", "World_Placeholder", ikhZro_grp)
	softIk_name = [lowerIk_ctrl.name]

	logger.info(f"Gen Rig {region}{side} Complete.")
	return stick_ctrl.name, lower_bJnt.name, middle_bJnt.name, upper_bJnt.name, ikhAll_name, psStreEndName, softIk_name, fkIkTwistRig_meta