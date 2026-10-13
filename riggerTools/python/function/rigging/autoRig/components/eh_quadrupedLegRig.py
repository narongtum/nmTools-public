# -*- coding: utf-8 -*-
"""
Quadruped Leg Rig Component Module (Digitigrade & Plantigrade)
Migrated & Upgraded from bodyRig.quradrupedLegRig
"""

import logging
import maya.cmds as mc
import maya.mel as mel

from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.util import misc
reload(misc)

from function.rigging.autoRig.components.limbRig import eh_midLockModule as midLockModule
reload(midLockModule)

from function.rigging.autoRig.components.limbRig import eh_createIKStretch as create
reload(create)

from function.rigging.autoRig.components.limbRig import eh_fkIkTwistGenRig_rbnMatrix as fitr
reload(fitr)

from function.rigging.autoRig.components.limbRig import eh_twistRig as tr
reload(tr)

from function.rigging.autoRig.components.limbRig import eh_createSoftIk as softIkfunc
reload(softIkfunc)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.rigging.tools import proc as pc
reload(pc)

from function.rigging.autoRig.components.ribbonRig import eh_ribbonRigExt as ribbonRig
reload(ribbonRig)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)




'''
# Example: Using the upgraded quadruped leg rig component
from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.components import eh_quadrupedLegRig as qLegRig
reload(qLegRig)

# Build Left Hind Leg (Digitigrade)
result = qLegRig.eh_quadrupedLegRig(
	nameSpace='',
	parentTo='ctrl_grp',
	side='LFT',
	tmpJnt=(
		'upLegBackLFT_tmpJnt', 'midLegBackLFT_tmpJnt', 'ankleBackLFT_tmpJnt',
		'legPovBackLFT_tmpJnt', 'ballRollBackLFT_tmpJnt', 'toeRollBackLFT_tmpJnt',
		'heelRollBackLFT_tmpJnt', 'footOutBackLFT_tmpJnt', 'footInBackLFT_tmpJnt', 'lowLegBackLFT_tmpJnt'
	),
	priorJnt='hip_bJnt',
	charScale=1.0,
	region='backLeg',
	softIk=False,       # Set True to enable Matrix Soft IK
	doubleIK=None       # Pass list of 3 proxy joints for Double IK if needed
)

'''







logger = logging.getLogger('eh_quadrupedLegRig')
logger.setLevel(logging.DEBUG)

color_part_dict = mnd.COLOR_part_dict


def eh_quadrupedLegRig(
	nameSpace='',
	parentTo='ctrl_grp',
	side='LFT',
	tmpJnt=(
		'upLegBackLFT_tmpJnt', 'midLegBackLFT_tmpJnt', 'ankleBackLFT_tmpJnt',
		'legPovBackLFT_tmpJnt', 'ballRollBackLFT_tmpJnt', 'toeRollBackLFT_tmpJnt',
		'heelRollBackLFT_tmpJnt', 'footOutBackLFT_tmpJnt', 'footInBackLFT_tmpJnt', 'lowLegBackLFT_tmpJnt'
	),
	priorJnt='hip_bJnt',
	ikhGrp='ikh_grp',
	noTouchGrp='noTouch_grp',
	nullGrp='snapNull_grp',
	jnt_grp='jnt_grp',
	showInfo=False,
	ribbon=True,
	ribbonRes='low',
	ribbonName=('upLeg', 'lwrLeg'),
	charScale=1.0,
	region='backLeg',
	alongAxis='y',
	povShape='sphereAxis',
	softIk=False,
	doubleIK=None,
	linkRotOrder=False,
	stickShape='stick_ctrlShape',
	ctrlShape='fk_ctrlShape'
):
	"""
	Builds a full 4-joint Digitigrade Quadruped Hind Leg Rig.
	Supports FK, Stretchy IK with Spring/RP solvers, Knee/Hock locking, Foot Roll, and Ribbon Rigging.
	Optional features: Matrix Soft IK and Double IK proxy chains.
	"""
	core.makeHeader('Start of %s%s Rig' % ('eh_quadrupedLegRig', side))
	logger.info("Initializing Quadruped Leg Rig (%s)..." % side)

	colorSide = color_part_dict['left'] if side == 'LFT' else color_part_dict['right']
	colorSec = color_part_dict.get('secondary', 'yellow')

	# Assign Guide / Temp Joint references
	upperLeg = core.Dag(tmpJnt[0])
	midLeg = core.Dag(tmpJnt[1])
	lowerLeg = core.Dag(tmpJnt[9])  # 4th limb joint (hock/shank)
	ankle = core.Dag(tmpJnt[2])
	povLeg = core.Dag(tmpJnt[3])
	ball = core.Dag(tmpJnt[4])
	toe = core.Dag(tmpJnt[5])
	heel = core.Dag(tmpJnt[6])
	footIn = core.Dag(tmpJnt[7])
	footOut = core.Dag(tmpJnt[8])

	# Create Bind Joint Chain
	upperLeg_bJnt = rigTools.jointAt(upperLeg)
	midLeg_bJnt = rigTools.jointAt(midLeg)
	lowerLeg_bJnt = rigTools.jointAt(lowerLeg)
	ankle_bJnt = rigTools.jointAt(ankle)
	ball_bJnt = rigTools.jointAt(ball)
	toe_bJnt = rigTools.jointAt(toe)

	# Determine region and position tag
	if 'Front' in tmpJnt[0]:
		legType = 'frontLeg'
		position = 'Front'
	elif 'Back' in tmpJnt[0]:
		legType = 'backLeg'
		position = 'Back'
	else:
		legType = 'leg'
		position = ''

	# Derive raw names
	rawName = []
	for each in tmpJnt:
		tmp = each.split('_')[0][:-3] if len(each.split('_')[0]) >= 3 else each.split('_')[0]
		rawName.append(tmp)

	upperLeg_bJnt.name = rawName[0] + side + '_bJnt'
	midLeg_bJnt.name = rawName[1] + side + '_bJnt'
	lowerLeg_bJnt.name = rawName[9] + side + '_bJnt'
	ankle_bJnt.name = rawName[2] + side + '_bJnt'
	ball_bJnt.name = rawName[4] + side + '_bJnt'
	toe_bJnt.name = rawName[5] + side + '_bJnt'

	# Adjust rotate orders
	upperLeg_bJnt.rotateOrder = 'yzx'
	midLeg_bJnt.rotateOrder = 'yzx'
	lowerLeg_bJnt.rotateOrder = 'yzx'
	ankle_bJnt.rotateOrder = 'yzx'

	# Hierarchy: upper -> mid -> lower -> ankle -> ball -> toe
	midLeg_bJnt.parent(upperLeg_bJnt)
	lowerLeg_bJnt.parent(midLeg_bJnt)
	ankle_bJnt.parent(lowerLeg_bJnt)
	toe_bJnt.parent(ball_bJnt)
	ball_bJnt.parent(ankle_bJnt)
	ankle_bJnt.attr('segmentScaleCompensate').value = 0

	if mc.objExists(priorJnt):
		upperLeg_bJnt.parent(priorJnt)

	# =========================================================================
	# Master & Rig Groups
	# =========================================================================
	part = nameSpace + legType
	legRig_grp = core.Null(part + 'Rig' + side + '_grp')
	if mc.objExists(priorJnt):
		legRigGrp_parCons = core.parentConstraint(priorJnt, legRig_grp)
		legRigGrp_parCons.name = part + 'Rig' + side + '_parCons'

	legJnt_grp = core.Null(part + 'Jnt' + side + '_grp')

	# =========================================================================
	# Stick Controller (Space Switch & Scale)
	# =========================================================================
	stick_ctrl = core.Dag(part + 'Stick' + side + '_ctrl')
	stick_ctrl.nmCreateController(stickShape)
	stick_ctrl.editCtrlShape(axis=charScale * 3.6)
	stick_ctrl.color = colorSec
	stick_ctrl.hideArnoldNode()
	stick_ctrl.attr('rotateX').value -= 90

	stickZro_grp = rigTools.zeroGroup(stick_ctrl)
	stickZro_grp.name = part + 'Stick' + side + 'Zro_grp'
	stickZro_grp.matchPosition(ankle_bJnt)

	ctrlGrp_parCons = core.parentConstraint(ankle_bJnt, stickZro_grp, mo=True)
	ctrlGrp_parCons.name = part + side + 'Stick_parCons'

	stick_ctrl.addAttribute(longName='legScale', defaultValue=1, keyable=True)
	stick_ctrl.addAttribute(attributeType='float', longName='FK_IK', minValue=0, maxValue=1, defaultValue=0, keyable=True)
	stick_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

	# =========================================================================
	# FK System
	# =========================================================================
	fkCtrl_grp = core.Null(part + 'FkCtrl' + side + '_grp')
	if mc.objExists(priorJnt):
		fkCtrl_grp.snap(priorJnt)
	fkCtrl_grp.parent(legRig_grp)

	fkJnt_grp = core.Null(part + 'FkJnt' + side + '_grp')
	if mc.objExists(priorJnt):
		fkJnt_grp.snap(priorJnt)
	fkJnt_grp.parent(legJnt_grp)

	upperLeg_fkJnt = rigTools.jointAt(upperLeg)
	midLeg_fkJnt = rigTools.jointAt(midLeg)
	lowerLeg_fkJnt = rigTools.jointAt(lowerLeg)
	ankle_fkJnt = rigTools.jointAt(ankle)
	ball_fkJnt = rigTools.jointAt(ball)

	upperLeg_fkJnt.name = rawName[0] + side + '_fkJnt'
	midLeg_fkJnt.name = rawName[1] + side + '_fkJnt'
	lowerLeg_fkJnt.name = rawName[9] + side + '_fkJnt'
	ankle_fkJnt.name = rawName[2] + side + '_fkJnt'
	ball_fkJnt.name = rawName[4] + side + '_fkJnt'

	midLeg_fkJnt.parent(upperLeg_fkJnt)
	lowerLeg_fkJnt.parent(midLeg_fkJnt)
	ankle_fkJnt.parent(lowerLeg_fkJnt)
	ball_fkJnt.parent(ankle_fkJnt)
	upperLeg_fkJnt.parent(fkJnt_grp)

	# FK Controls
	fk_configs = [
		('upper' + legType.capitalize(), upperLeg_fkJnt, 0.9, 'yzx'),
		('middle' + legType.capitalize(), midLeg_fkJnt, 0.85, 'yzx'),
		('lower' + legType.capitalize(), lowerLeg_fkJnt, 0.8, 'yzx'),
		('ankle' + legType.capitalize(), ankle_fkJnt, 0.7, 'xzy'),
		('ball' + legType.capitalize(), ball_fkJnt, 0.7, 'xzy')
	]

	fk_ctrls = []
	for p_name, target_jnt, scale_mult, rot_order in fk_configs:
		c_name = nameSpace + p_name + 'Fk' + side
		ctrl = core.Dag(c_name + '_ctrl')
		ctrl.nmCreateController(ctrlShape)
		zro = rigTools.zeroGroup(ctrl)
		zro.name = c_name + 'Zro_grp'
		ctrl.editCtrlShape(axis=charScale * scale_mult)
		gmbl = core.createGimbal(ctrl)
		ctrl.color = colorSide
		ctrl.rotateOrder = rot_order
		gmbl.rotateOrder = rot_order
		zro.matchPosition(target_jnt)
		zro.matchRotation(target_jnt)
		p_cons = core.parentConstraint(gmbl, target_jnt)
		p_cons.name = c_name + '_parCons'
		fk_ctrls.append((ctrl, zro, gmbl))

	# Parent FK hierarchy
	fk_ctrls[4][1].parent(fk_ctrls[3][2])  # ball -> ankle gmbl
	fk_ctrls[3][1].parent(fk_ctrls[2][2])  # ankle -> lower gmbl
	fk_ctrls[2][1].parent(fk_ctrls[1][2])  # lower -> middle gmbl
	fk_ctrls[1][1].parent(fk_ctrls[0][2])  # middle -> upper gmbl
	fk_ctrls[0][1].parent(fkCtrl_grp)      # upper -> fkCtrl_grp

	# =========================================================================
	# IK System
	# =========================================================================
	ctrlType = 'Ik'
	armIkCtrl_grp = core.Null(part + ctrlType + 'Ctrl' + side + '_grp')
	if mc.objExists(priorJnt):
		armIkCtrl_grp.snap(priorJnt)
	armIkCtrl_grp.parent(legRig_grp)

	armIkJnt_grp = core.Null(part + ctrlType + 'Jnt' + side + '_grp')
	if mc.objExists(priorJnt):
		armIkJnt_grp.snap(priorJnt)
	armIkJnt_grp.parent(legJnt_grp)

	upperLeg_ikJnt = rigTools.jointAt(upperLeg)
	midLeg_ikJnt = rigTools.jointAt(midLeg)
	lowerLeg_ikJnt = rigTools.jointAt(lowerLeg)
	ankle_ikJnt = rigTools.jointAt(ankle)
	ball_ikJnt = rigTools.jointAt(ball)
	toe_ikJnt = rigTools.jointAt(toe)

	upperLeg_ikJnt.name = rawName[0] + side + '_ikJnt'
	midLeg_ikJnt.name = rawName[1] + side + '_ikJnt'
	lowerLeg_ikJnt.name = rawName[9] + side + '_ikJnt'
	ankle_ikJnt.name = rawName[2] + side + '_ikJnt'
	ball_ikJnt.name = rawName[4] + side + '_ikJnt'
	toe_ikJnt.name = rawName[5] + side + '_ikJnt'

	midLeg_ikJnt.parent(upperLeg_ikJnt)
	lowerLeg_ikJnt.parent(midLeg_ikJnt)
	ankle_ikJnt.parent(lowerLeg_ikJnt)
	ball_ikJnt.parent(ankle_ikJnt)
	toe_ikJnt.parent(ball_ikJnt)
	upperLeg_ikJnt.parent(armIkJnt_grp)

	# Main IK Handle (Spring solver or RP Solver)
	# IMPORTANT: Create IK handle FIRST, then set preferredAngle.
	# IK Spring Solver resets preferredAngle on all joints in the chain
	# when the IK handle is created, so setting it before has no effect.
	try:
		lowerIk_ikh = core.IkSpring(startJoint=upperLeg_ikJnt.name, endEffector=lowerLeg_ikJnt.name)
	except Exception as err:
		logger.warning(f"IkSpring solver failed ({err}), falling back to IkRp solver.")
		lowerIk_ikh = core.IkRp(startJoint=upperLeg_ikJnt.name, endEffector=lowerLeg_ikJnt.name)

	# Transfer preferredAngle from guide to IK joints AFTER IK handle creation
	guide_map_ik = [
		(tmpJnt[0], upperLeg_ikJnt),
		(tmpJnt[1], midLeg_ikJnt),
		(tmpJnt[9], lowerLeg_ikJnt),
		(tmpJnt[2], ankle_ikJnt)
	]
	pref_attrs = ['guide_preferredAngleX', 'guide_preferredAngleY', 'guide_preferredAngleZ', 'preferredAngleX', 'preferredAngleY', 'preferredAngleZ']

	guide_pref_applied = False
	for guide_jnt, ik_jnt in guide_map_ik:
		for attr in pref_attrs:
			if mc.attributeQuery(attr, node=guide_jnt, exists=True):
				val = mc.getAttr(guide_jnt + '.' + attr)
				if val != 0:
					target_attr = attr.replace('guide_', '')
					ik_jnt.attr(target_attr).value = val
					logger.info('Set %s.%s to %s from guide.' % (ik_jnt.name, target_attr, val))
					guide_pref_applied = True

	# Auto-detect bend direction for Front Leg vs Back Leg if no guide preferredAngle was applied
	if not guide_pref_applied:
		if 'front' in legType.lower() or 'front' in tmpJnt[0].lower():
			# Front leg elbow bends backward (-X)
			midLeg_ikJnt.attr('preferredAngleX').value = -60
			lowerLeg_ikJnt.attr('preferredAngleX').value = 60
			logger.info(f"Auto-configured Front Leg Preferred Angles on {midLeg_ikJnt.name} (-60) and {lowerLeg_ikJnt.name} (+60)")
		else:
			# Hind leg: Knee bends forward (-X matching jointOrientX), Hock bends backward (+X matching jointOrientX)
			midLeg_ikJnt.attr('preferredAngleX').value = -60
			lowerLeg_ikJnt.attr('preferredAngleX').value = 60
			logger.info(f"Auto-configured Hind Leg Preferred Angles on {midLeg_ikJnt.name} (-60) and {lowerLeg_ikJnt.name} (+60)")

	lowerIk_ikh.name = rawName[9] + side + '_ikSpring_handle'
	lowerIk_ikh.eff = rawName[9] + side + '_eff'
	lowerIk_ikh.attr('v').value = 0

	# Lower Leg IK Controller (Knee/Hock handle)
	name = nameSpace + rawName[9]
	lowerLegIK_ctrl = core.Dag(name + 'Ik' + side + '_ctrl')
	lowerLegIK_ctrl.nmCreateController('cube_ctrlShape')
	lowerLegIK_ctrl.editCtrlShape(axis=charScale * 1)
	lowerLegIK_ctrl.setColor(colorSide)
	lowerLegIK_ctrl.snapPoint(lowerLeg_ikJnt)

	lowerLegIkZro_grp = rigTools.zeroGroup(lowerLegIK_ctrl)
	lowerLegIkZro_grp.name = name + 'Ik' + side + 'Zro_grp'

	legIkRotation = core.orientConstraint(lowerLegIK_ctrl, ankle_ikJnt.name, mo=True)
	legIkRotation.name = name + ctrlType + side + '_orientCons'

	# Pole Vector Controller
	tmpPov = rawName[3]
	povZro_grp = core.Null(nameSpace + 'knee' + legType.capitalize() + side + 'Zro_grp')
	name = nameSpace + tmpPov + legType.capitalize() + side
	pov_ctrl = core.Dag(name + '_ctrl')

	if povShape == 'sphereAxis':
		pov_ctrl.nmCreateController('legLFT_pov_ctrlShape')
	elif povShape == 'pyramid':
		pov_ctrl.nmCreateController('pyramid_ctrlShape')
		pov_ctrl.rotateShape(rotate=(90, 0, 0))
		pc.targetPov(ctrl=pov_ctrl.name, jnt=lowerLeg_bJnt.name)
	else:
		pov_ctrl.nmCreateController(povShape)

	pov_ctrl.editCtrlShape(axis=charScale * 0.8)
	pov_ctrl.setColor(colorSec)
	mc.parent(pov_ctrl.name, povZro_grp.name)
	povZro_grp.snap(povLeg)

	# Root IK Controller
	rootName = rawName[0] + 'Ik' + side
	ikRoot = core.Dag(rootName + '_ctrl')
	ikRoot.nmCreateController('cube_ctrlShape')
	ikRoot.editCtrlShape(axis=charScale * 5.5)
	ikRoot.setColor(colorSide)
	IkRootZro_grp = rigTools.zeroGroup(ikRoot)
	IkRootZro_grp.name = rootName + 'Zro_grp'
	IkRootZro_grp.snap(upperLeg_bJnt)
	ikRootGmbl_ctrl = core.createGimbal(ikRoot)

	rootIk_parCons = core.parentConstraint(ikRootGmbl_ctrl, upperLeg_ikJnt.name)
	rootIk_parCons.name = part + side + 'Jnt_parCons'

	# Ankle Main IK Controller
	footBehav = ['footOut', 'footIn', 'heelRoll', 'toeRoll', 'ballRoll', 'ankle', 'rollBackAnkle']
	ctrlName = nameSpace + footBehav[5] + legType + 'IK' + side
	ankleIk_ctrl = core.Dag(ctrlName + '_ctrl')
	ankleIk_ctrl.nmCreateController('cube_ctrlShape')
	ankleIk_ctrl.rotateShape(rotate=(90, 90, 0))
	ankleIk_ctrl.editCtrlShape(axis=charScale * 10)
	ankleIk_ctrl.setColor(colorSide)

	ankleIkZro_grp = rigTools.zeroGroup(ankleIk_ctrl)
	ankleIkZro_grp.name = ctrlName + 'Zro_grp'
	ankleIkZro_grp.snapPoint(ankle_ikJnt)

	# Pole vector constraint
	mc.poleVectorConstraint(pov_ctrl.name, lowerIk_ikh.name, name=nameSpace + 'knee' + legType.capitalize() + side + '_povCons', w=1)
	mc.parent(povZro_grp.name, lowerLegIK_ctrl.name)

	# Pole Vector Local/World Space Switching
	partName = nameSpace + 'knee'
	Loc_grp, World_grp, WorldGrp_orientCons, ZroGrp_orientCons, reverseNode_rev = rigTools.parentLocalWorldCtrl(
		pov_ctrl, ankleIk_ctrl, parentTo, povZro_grp, partName
	)
	Loc_grp.name = part + 'Local_grp'
	World_grp.name = part + 'World_grp'
	WorldGrp_orientCons.name = part + side + 'WorldGrp_parCons'
	ZroGrp_orientCons.name = part + side + 'ZroGrp_parCons'
	reverseNode_rev.name = part + side + 'ZroGrParCons_rev'

	# Attributes on Ankle Controller
	ankleIk_ctrl.addAttribute(attributeType='float', ln='toe_Aim', k=True, minValue=0, maxValue=1, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='long', ln='autoStretch', k=True, minValue=0, maxValue=1, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='upStretch', k=True, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='lowStretch', k=True, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='long', ln='Upper_IK', k=True, minValue=0, maxValue=1, dv=0)
	ankleIk_ctrl.hideArnoldNode()

	# Stretchy IK System
	stretchNode = create.iKStretch(
		ikJnt=(upperLeg_ikJnt.name, midLeg_ikJnt.name, lowerLeg_ikJnt.name),
		ikCtrl=(ikRoot.name, ankleIk_ctrl.name),
		region=legType,
		side=side,
		scaleCtrl='placement_ctrl',
		noTouchGrp=noTouchGrp,
		lowNam=rawName[2]
	)
	pmaNode = stretchNode[0]
	psStreEndName = stretchNode[1]

	# Optional Soft IK
	if softIk:
		try:
			logger.info("Setting up Soft IK Matrix for Quadruped Hind Leg...")
			softIkfunc.createSoftIk(
				ikRoot=ikRoot.name,
				ikCtrl=ankleIk_ctrl.name,
				ikhName=lowerIk_ikh.name,
				side=side,
				prefix=part,
				charScale=charScale
			)
		except Exception as e:
			logger.error(f"Failed to setup Soft IK: {e}", exc_info=True)

	# Optional Double IK Proxy Chain
	if doubleIK is not None and len(doubleIK) >= 3:
		try:
			logger.info("Configuring Double IK Proxy Chain: %s" % str(doubleIK))
			dIk_hip = core.Dag(doubleIK[0])
			dIk_knee = core.Dag(doubleIK[1])
			dIk_ankle = core.Dag(doubleIK[2])

			pxyHip = rigTools.jointAt(dIk_hip)
			pxyKnee = rigTools.jointAt(dIk_knee)
			pxyAnkle = rigTools.jointAt(dIk_ankle)

			pxyHip.name = 'proxy' + rawName[0] + side + '_pxyJnt'
			pxyKnee.name = 'proxy' + rawName[1] + side + '_pxyJnt'
			pxyAnkle.name = 'proxy' + rawName[2] + side + '_pxyJnt'

			pxyKnee.parent(pxyHip)
			pxyAnkle.parent(pxyKnee)
			pxyHip.parent(armIkJnt_grp)
		except Exception as e:
			logger.error(f"Failed to setup Double IK proxy chain: {e}", exc_info=True)

	# =========================================================================
	# Foot Roll Setup
	# =========================================================================
	# Ball roll
	ctrlName = nameSpace + footBehav[4] + 'Ik' + legType + side
	ballRoll_ctrl = core.Dag(ctrlName + '_ctrl')
	ballRoll_ctrl.nmCreateController('ballRoll%s_IK_ctrlShape' % side)
	ballRoll_ctrl.editCtrlShape(axis=charScale * 1.25)
	ballRoll_ctrl.setColor(colorSec)
	ballRollZro_grp = rigTools.zeroGroup(ballRoll_ctrl)
	ballRollZro_grp.name = ctrlName + 'Zro_grp'
	ballRollZro_grp.snap(ball_bJnt)

	# Foot Out
	ctrlName = nameSpace + footBehav[0] + 'IK' + legType + side
	footOut_ctrl = core.Dag(ctrlName + '_ctrl')
	footOut_ctrl.nmCreateController('sphere_ctrlShape')
	footOut_ctrl.editCtrlShape(axis=charScale * 1.25)
	footOut_ctrl.setColor(colorSec)
	footOutZro_grp = rigTools.zeroGroup(footOut_ctrl)
	footOutZro_grp.name = ctrlName + 'Zro_grp'
	footOutZro_grp.snap(footOut)

	# Foot In
	ctrlName = nameSpace + footBehav[1] + 'IK' + legType + side
	footIn_ctrl = core.Dag(ctrlName + '_ctrl')
	footIn_ctrl.nmCreateController('sphere_ctrlShape')
	footIn_ctrl.editCtrlShape(axis=charScale * 1.25)
	footIn_ctrl.setColor(colorSec)
	footInZro_grp = rigTools.zeroGroup(footIn_ctrl)
	footInZro_grp.name = ctrlName + 'Zro_grp'
	footInZro_grp.snap(footIn)

	# Foot Heel
	ctrlName = nameSpace + footBehav[2] + legType + 'IK' + side
	footHeel_ctrl = core.Dag(ctrlName + '_ctrl')
	footHeel_ctrl.nmCreateController('sphere_ctrlShape')
	footHeel_ctrl.editCtrlShape(axis=charScale * 1.25)
	footHeel_ctrl.setColor(colorSec)
	footHeelZro_grp = rigTools.zeroGroup(footHeel_ctrl)
	footHeelZro_grp.name = ctrlName + 'Zro_grp'
	footHeelZro_grp.snap(heel)

	# Foot Toe
	ctrlName = nameSpace + footBehav[3] + legType + 'IK' + side
	footToe_ctrl = core.Dag(ctrlName + '_ctrl')
	footToe_ctrl.nmCreateController('sphere_ctrlShape')
	footToe_ctrl.editCtrlShape(axis=charScale * 1.25)
	footToe_ctrl.setColor(colorSec)
	footToeZro_grp = rigTools.zeroGroup(footToe_ctrl)
	footToeZro_grp.name = ctrlName + 'Zro_grp'
	footToeZro_grp.snap(toe_bJnt)

	# Foot IK handles
	ankleIk_ikh = core.IkRp(startJoint=lowerLeg_ikJnt, endEffector=ankle_ikJnt)
	ankleIk_ikh.name = nameSpace + footBehav[5] + legType + side + '_ikh'
	ankleIk_ikh.eff = nameSpace + footBehav[5] + legType + side + '_eff'
	ankleIk_ikh.attr('v').value = showInfo

	ballIk_ikh = core.IkRp(startJoint=ankle_ikJnt, endEffector=ball_ikJnt)
	ballIk_ikh.name = nameSpace + footBehav[4] + legType + side + '_ikh'
	ballIk_ikh.eff = nameSpace + footBehav[4] + legType + side + '_eff'
	ballIk_ikh.attr('v').value = showInfo

	toeIk_ikh = core.IkRp(startJoint=ball_ikJnt, endEffector=toe_ikJnt)
	toeIk_ikh.name = nameSpace + footBehav[3] + legType + side + '_ikh'
	toeIk_ikh.eff = nameSpace + footBehav[3] + legType + side + '_eff'
	toeIk_ikh.attr('v').value = showInfo

	# Roll Back Ankle Controller
	ctrlName = nameSpace + footBehav[6] + legType + 'IK'
	rollBackAnkleIk_ctrl = core.Dag(ctrlName + side + '_ctrl')
	rollBackAnkleIkZro_grp = core.Null(ctrlName + 'Aim' + side + 'Zro_grp')
	rollBackAnkleIkOffset_grp = core.Null(ctrlName + 'Aim' + side + 'Offset_grp')
	rollBackAnkleIk_ctrl.nmCreateController('orientAxisC_ctrlShape')
	rollBackAnkleIk_ctrl.rotateShape(rotate=(0, 0, 90))
	rollBackAnkleIk_ctrl.editCtrlShape(axis=charScale * 0.75)
	rollBackAnkleIk_ctrl.hideArnoldNode()
	rollBackAnkleIk_ctrl.setColor(colorSide)

	rollBackAnkleIkOffset_grp.parent(rollBackAnkleIkZro_grp)
	rollBackAnkleIk_ctrl.parent(rollBackAnkleIkOffset_grp)
	
	# Snap only position to ankle joint so world orientation remains completely straight [0, 0, 0]
	rollBackAnkleIkZro_grp.snapPoint(ankle_ikJnt)
	mc.xform(rollBackAnkleIkZro_grp.name, ws=True, ro=[0, 0, 0])

	# Foot Hierarchy
	ankleIkZro_grp.parent(lowerLegIK_ctrl)
	footInZro_grp.parent(footOut_ctrl)
	footHeelZro_grp.parent(footIn_ctrl)
	footToeZro_grp.parent(footHeel_ctrl)
	footOutZro_grp.parent(ankleIk_ctrl)
	ballRollZro_grp.parent(footToe_ctrl)
	
	# Parent under ballRoll_ctrl while preserving straight world orientation
	rollBackAnkleIkZro_grp.parent(ballRoll_ctrl)
	mc.xform(rollBackAnkleIkZro_grp.name, ws=True, ro=[0, 0, 0])
	mc.setAttr(f"{rollBackAnkleIkOffset_grp.name}.r", 0, 0, 0)
	mc.setAttr(f"{rollBackAnkleIk_ctrl.name}.r", 0, 0, 0)

	ballIk_ikh.parent(ballRoll_ctrl)
	toeIk_ikh.parent(footToe_ctrl)

	rollBackAnkleIkStill_grp = core.Null(ctrlName + side + 'Still_grp')
	rollBackAnkleIkStill_grp.snapPoint(upperLeg_bJnt)
	rollBackAnkleIkStill_grp.parent(ankleIk_ctrl)

	# RollBack Aim constraint
	up_obj = core.Locator(ctrlName + side + '_loc')
	up_obj.snapPoint(rollBackAnkleIkOffset_grp)
	mc.move(0, 0, charScale * 30, up_obj.name, relative=True, worldSpace=True)

	upperLeg_aimCons = core.aimConstraint(
		upperLeg_ikJnt, rollBackAnkleIkStill_grp, rollBackAnkleIkOffset_grp,
		mo=False, aimVector=(0, 1, 0), upVector=(0, 0, 1),
		worldUpType='object', worldUpObject=up_obj.name
	)
	upperLeg_aimCons.attr('worldUpType').value = 1
	upperLeg_aimCons.attr(upperLeg_ikJnt.name + 'W0').value = 1
	upperLeg_aimCons.name = ctrlName + side + '_aimCons'

	toeAnim_rev = core.Reverse()
	toeAnim_rev.name = ctrlName + side + '_rev'
	ankleIk_ctrl.attr('toe_Aim') >> toeAnim_rev.attr('inputY')
	ankleIk_ctrl.attr('toe_Aim') >> upperLeg_aimCons.attr(rollBackAnkleIkStill_grp.name + 'W1')
	toeAnim_rev.attr('outputY') >> upperLeg_aimCons.attr(upperLeg_ikJnt.name + 'W0')

	ankleIk_ikh.parent(rollBackAnkleIk_ctrl)
	lowerIk_ikh.parent(rollBackAnkleIk_ctrl)
	lowerLegIkZro_grp.parent(parentTo)
	up_obj.parent(ankleIk_ctrl)
	up_obj.attr('v').value = 0

	# =========================================================================
	# Knee / Hock Lock Module
	# =========================================================================
	try:
		rawNameUPR, distanceUPRName, povUPR_Ctrl, lowerUPR_loc, upperUPR_loc = midLockModule.createDistance(
			nameSpace, part='up', startP=ikRootGmbl_ctrl.name, endP=pov_ctrl.name
		)
		rawNameLWR, distanceLWRName, povLWR_Ctrl, lowerLWR_loc, upperLWR_loc = midLockModule.createDistance(
			nameSpace, part='dn', startP=pov_ctrl.name, endP=lowerLegIK_ctrl.name
		)
		blendName, invertNodeName = midLockModule.createBlendColor(
			nameSpace, uprDistance=distanceUPRName, lwrDistance=distanceLWRName, side=side, uprNam=rawNameUPR
		)
		attrName = midLockModule.doAddAttr(povUPR_Ctrl, region)
		midLockModule.connectIkJnt(
			stretchNode=pmaNode, upperIKJnt=midLeg_ikJnt.name, lowerIKJnt=lowerLeg_ikJnt.name,
			blendName=blendName, namLock=attrName, povName=povUPR_Ctrl, alongAxis=alongAxis
		)
	except Exception as err:
		logger.warning(f"Knee/Hock lock setup encountered error: {err}")

	# =========================================================================
	# FK / IK Blend Switch on Bind Joints
	# =========================================================================
	switch_jnt_names = [
		'upLeg%s' % position,
		'lowLeg%s' % position,
		'midLeg%s' % position,
		'ankle%s' % position,
		'ballRoll%s' % position
	]

	for each in switch_jnt_names:
		fk_j = each + side + '_fkJnt'
		ik_j = each + side + '_ikJnt'
		b_j = each + side + '_bJnt'

		if mc.objExists(fk_j) and mc.objExists(ik_j) and mc.objExists(b_j):
			psCon = mc.parentConstraint(fk_j, ik_j, b_j, name=each + 'Switch_parentCons', mo=True)
			revNode = mc.createNode('reverse', name=each + 'Switch' + side + '_rev')

			mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{revNode}.inputX")
			mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{psCon[0]}.{ik_j}W1")
			mc.connectAttr(f"{revNode}.outputX", f"{psCon[0]}.{fk_j}W0")

	# Final hierarchy grouping & visibility switching
	if mc.objExists('jnt_grp'):
		legJnt_grp.parent('jnt_grp')
	legJnt_grp.attr('visibility').value = showInfo

	legRig_grp.parent(parentTo)
	stickZro_grp.parent(parentTo)
	IkRootZro_grp.parent(armIkCtrl_grp)

	stickVis_rev = core.Reverse()
	stickVis_rev.name = part + 'StickVis' + side + '_rev'
	stick_ctrl.attr('FK_IK') >> stickVis_rev.attr('inputX')
	stickVis_rev.attr('outputX') >> fkCtrl_grp.attr('visibility')

	stick_ctrl.attr('FK_IK').value = 1
	stick_ctrl.attr('FK_IK') >> lowerLegIkZro_grp.attr('visibility')
	stick_ctrl.attr('FK_IK') >> IkRootZro_grp.attr('visibility')

	ikRoot.lockHideAttrLst('rx', 'ry', 'rz', 'sx', 'sy', 'sz')
	pov_ctrl.lockHideAttrLst('rx', 'ry', 'rz', 'sx', 'sy', 'sz')
	mc.connectAttr(f"{ankleIk_ctrl.name}.Upper_IK", f"{lowerLegIK_ctrl.shape}.visibility", f=True)

	# =========================================================================
	# Message Attributes for FK/IK Matcher
	# =========================================================================
	msg_attrs = [
		'stick', 'upJnt', 'midJnt', 'lowJnt', 'ankleJnt', 'ballJnt',
		'upFkCtrl', 'midFkCtrl', 'lowFkCtrl', 'ankleFkCtrl', 'ballFkCtrl',
		'ikCtrl', 'midIkCtrl', 'pov'
	]
	for attr_name in msg_attrs:
		if not mc.attributeQuery(attr_name, node=stick_ctrl.name, exists=True):
			stick_ctrl.addAttribute(attributeType='message', longName=attr_name)

	stick_ctrl.attr('message') >> stick_ctrl.attr('stick')
	upperLeg_bJnt.attr('message') >> stick_ctrl.attr('upJnt')
	midLeg_bJnt.attr('message') >> stick_ctrl.attr('midJnt')
	lowerLeg_bJnt.attr('message') >> stick_ctrl.attr('lowJnt')
	ankle_bJnt.attr('message') >> stick_ctrl.attr('ankleJnt')
	if mc.objExists(ball_bJnt.name):
		ball_bJnt.attr('message') >> stick_ctrl.attr('ballJnt')

	fk_ctrls[0][0].attr('message') >> stick_ctrl.attr('upFkCtrl')
	fk_ctrls[1][0].attr('message') >> stick_ctrl.attr('midFkCtrl')
	fk_ctrls[2][0].attr('message') >> stick_ctrl.attr('lowFkCtrl')
	if len(fk_ctrls) > 3:
		fk_ctrls[3][0].attr('message') >> stick_ctrl.attr('ankleFkCtrl')
	if len(fk_ctrls) > 4:
		fk_ctrls[4][0].attr('message') >> stick_ctrl.attr('ballFkCtrl')

	ankleIk_ctrl.attr('message') >> stick_ctrl.attr('ikCtrl')
	lowerLegIK_ctrl.attr('message') >> stick_ctrl.attr('midIkCtrl')
	pov_ctrl.attr('message') >> stick_ctrl.attr('pov')

	if not mc.attributeQuery('region', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='region')
	stick_ctrl.setAttribute('region', legType, type='string')

	if not mc.attributeQuery('scale_Attr', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='scale_Attr')
	stick_ctrl.setAttribute('scale_Attr', 'legScale', type='string')

	# =========================================================================
	# Ribbon Rigging
	# =========================================================================
	if ribbon:
		numJoints = 5 if ribbonRes == 'high' else 3
		try:
			hingesUprBtm = ribbonRig.ribbonRigExt(
				nameSpace=nameSpace, width=10, numJoints=numJoints, side=side,
				jointTop=upperLeg_bJnt, jointBtm=midLeg_bJnt, part=ribbonName[0],
				charScale=charScale, noTouch_grp=noTouchGrp, showInfo=showInfo, ctrl_grp=legRig_grp.name
			)
			hingesLwrTop = ribbonRig.ribbonRigExt(
				nameSpace=nameSpace, width=10, numJoints=numJoints, side=side,
				jointTop=midLeg_bJnt, jointBtm=lowerLeg_bJnt, part=ribbonName[1],
				charScale=charScale, noTouch_grp=noTouchGrp, showInfo=showInfo, ctrl_grp=legRig_grp.name
			)
			ribbonRig.makeHigesMover(
				part=legType, nameSpace=nameSpace, side=side, btmName=hingesUprBtm,
				topName=hingesLwrTop, charScale=charScale, moverPosition=midLeg_bJnt.name, ctrl_grp=parentTo
			)
		except Exception as e:
			logger.warning(f"Ribbon setup encountered issue: {e}")

	logger.info(f"#### End of {part} {side} Rig ####")
	return {
		"upperLeg_bJnt": upperLeg_bJnt.name,
		"midLeg_bJnt": midLeg_bJnt.name,
		"lowerLeg_bJnt": lowerLeg_bJnt.name,
		"ankle_bJnt": ankle_bJnt.name,
		"stick_ctrl": stick_ctrl.name,
		"ankleIk_ctrl": ankleIk_ctrl.name
	}


def plantigradeLegRig(
	nameSpace='',
	parentTo='ctrl_grp',
	side='LFT',
	tmpJnt=(
		'upperLegLFT_tmpJnt', 'lowerLegLFT_tmpJnt', 'ankleLFT_tmpJnt',
		'legLFT_pov_tmpJnt', 'ballLFT_tmpJnt', 'toesTipLFT_tmpJnt',
		'heelRollFrontLFT_tmpJnt', 'footOutFrontLFT_tmpJnt', 'footInFrontLFT_tmpJnt'
	),
	priorJnt='hip_bJnt',
	ikhGrp='ikh_grp',
	noTouchGrp='noTouch_grp',
	nullGrp='snapNull_grp',
	jnt_grp='jnt_grp',
	showInfo=False,
	ribbon=False,
	ribbonRes='high',
	ribbonName=('upLeg', 'lwrLeg'),
	charScale=1.0,
	alongAxis='y',
	scaleCtrl='placement_ctrl',
	ikPosi='foot',
	footAttr=True,
	keepFkIkBoth=True,
	povShape='pyramid',
	ctrlShape='fk_ctrlShape',
	stickShape='stick_ctrlShape',
	creTwistJnt=True
):
	"""
	Builds a 3-joint Plantigrade / Biped-like Leg Rig (e.g. bear, human-like quadruped limbs).
	Supports attribute-driven foot roll (footAttr=True) and ikPosi placement ('foot', 'ankle', 'animalFoot').
	"""
	core.makeHeader('Start of %s%s Rig' % ('plantigradeLegRig', side))
	logger.info("Initializing Plantigrade Leg Rig (%s)..." % side)

	colorSide = color_part_dict['left'] if side == 'LFT' else color_part_dict['right']
	colorSec = color_part_dict.get('secondary', 'yellow')

	upperLeg = core.Dag(tmpJnt[0])
	lowerLeg = core.Dag(tmpJnt[1])
	ankle = core.Dag(tmpJnt[2])
	povLeg = core.Dag(tmpJnt[3])
	ball = core.Dag(tmpJnt[4])
	toe = core.Dag(tmpJnt[5])
	heel = core.Dag(tmpJnt[6])
	footIn = core.Dag(tmpJnt[7])
	footOut = core.Dag(tmpJnt[8])

	upperLeg_bJnt = rigTools.jointAt(upperLeg)
	lowerLeg_bJnt = rigTools.jointAt(lowerLeg)
	ankle_bJnt = rigTools.jointAt(ankle)
	ball_bJnt = rigTools.jointAt(ball)
	toe_bJnt = rigTools.jointAt(toe)

	if 'Front' in tmpJnt[0]:
		legType = 'frontLeg'
	elif 'Back' in tmpJnt[0]:
		legType = 'backLeg'
	else:
		legType = 'leg'

	rawName = []
	for each in tmpJnt:
		tmp = each.split('_')[0][:-3] if len(each.split('_')[0]) >= 3 else each.split('_')[0]
		rawName.append(tmp)

	upperLeg_bJnt.name = rawName[0] + side + '_bJnt'
	lowerLeg_bJnt.name = rawName[1] + side + '_bJnt'
	ankle_bJnt.name = rawName[2] + side + '_bJnt'
	ball_bJnt.name = rawName[4] + side + '_bJnt'
	toe_bJnt.name = rawName[5] + side + '_bJnt'

	upperLeg_bJnt.rotateOrder = 'yzx'
	lowerLeg_bJnt.rotateOrder = 'yzx'
	ankle_bJnt.rotateOrder = 'yzx'

	lowerLeg_bJnt.parent(upperLeg_bJnt)
	ankle_bJnt.parent(lowerLeg_bJnt)
	toe_bJnt.parent(ball_bJnt)
	ball_bJnt.parent(ankle_bJnt)

	upperLeg_bJnt.setLable(side, 'none')
	lowerLeg_bJnt.setLable(side, 'knee')
	ankle_bJnt.setLable(side, 'foot')
	toe_bJnt.setLable(side, 'toe')
	ankle_bJnt.attr('segmentScaleCompensate').value = 0
	ball_bJnt.attr('segmentScaleCompensate').value = 0
	toe_bJnt.attr('segmentScaleCompensate').value = 0

	if mc.objExists(priorJnt):
		upperLeg_bJnt.parent(priorJnt)

	part = nameSpace + legType
	legRig_grp = core.Null(part + 'Rig' + side + '_grp')
	if mc.objExists(priorJnt):
		legRigGrp_parCons = core.parentConstraint(priorJnt, legRig_grp)
		legRigGrp_parCons.name = part + 'Rig' + side + '_parCons'

	legJnt_grp = core.Null(part + 'Jnt' + side + '_grp')

	# Stick Control
	stick_ctrl = core.Dag(part + 'Stick' + side + '_ctrl')
	stick_ctrl.nmCreateController(stickShape)
	stick_ctrl.editCtrlShape(axis=charScale * 3.6)
	stick_ctrl.color = colorSec
	stick_ctrl.hideArnoldNode()
	stick_ctrl.attr('rotateX').value -= 90

	stickZro_grp = rigTools.zeroGroup(stick_ctrl)
	stickZro_grp.name = part + 'Stick' + side + 'Zro_grp'
	stickZro_grp.matchPosition(ankle_bJnt)

	ctrlGrp_parCons = core.parentConstraint(ankle_bJnt, stickZro_grp, mo=True)
	ctrlGrp_parCons.name = part + side + 'Stick_parCons'
	stick_ctrl.addAttribute(longName='legScale', defaultValue=1, keyable=True)
	stick_ctrl.addAttribute(attributeType='float', longName='FK_IK', minValue=0, maxValue=1, defaultValue=0, keyable=True)
	if not mc.attributeQuery('location', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='location')
	stick_ctrl.setAttribute('location', ikPosi, type='string')
	stick_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

	# FK Chain
	armFkCtrl_grp = core.Null(part + 'FkCtrl' + side + '_grp')
	if mc.objExists(priorJnt):
		armFkCtrl_grp.snap(priorJnt)
	armFkCtrl_grp.parent(legRig_grp)

	armFkJnt_grp = core.Null(part + 'FkJnt' + side + '_grp')
	if mc.objExists(priorJnt):
		armFkJnt_grp.snap(priorJnt)
	armFkJnt_grp.parent(legJnt_grp)

	upperLeg_fkJnt = rigTools.jointAt(upperLeg)
	lowerLeg_fkJnt = rigTools.jointAt(lowerLeg)
	ankle_fkJnt = rigTools.jointAt(ankle)
	ball_fkJnt = rigTools.jointAt(ball)

	upperLeg_fkJnt.name = rawName[0] + side + '_fkJnt'
	lowerLeg_fkJnt.name = rawName[1] + side + '_fkJnt'
	ankle_fkJnt.name = rawName[2] + side + '_fkJnt'
	ball_fkJnt.name = rawName[4] + side + '_fkJnt'

	lowerLeg_fkJnt.parent(upperLeg_fkJnt)
	ankle_fkJnt.parent(lowerLeg_fkJnt)
	ball_fkJnt.parent(ankle_fkJnt)
	upperLeg_fkJnt.parent(armFkJnt_grp)

	# FK Controls
	fk_configs = [
		('upper' + legType.capitalize(), upperLeg_fkJnt, 0.9, 'yzx'),
		('lower' + legType.capitalize(), lowerLeg_fkJnt, 0.8, 'yzx'),
		('ankle' + legType.capitalize(), ankle_fkJnt, 0.7, 'xzy'),
		('ball' + legType.capitalize(), ball_fkJnt, 0.7, 'xzy')
	]

	fk_ctrls = []
	for p_name, target_jnt, scale_mult, rot_order in fk_configs:
		c_name = nameSpace + p_name + 'Fk' + side
		ctrl = core.Dag(c_name + '_ctrl')
		ctrl.nmCreateController(ctrlShape)
		zro = rigTools.zeroGroup(ctrl)
		zro.name = c_name + 'Zro_grp'
		ctrl.editCtrlShape(axis=charScale * scale_mult)
		gmbl = core.createGimbal(ctrl)
		ctrl.color = colorSide
		ctrl.rotateOrder = rot_order
		gmbl.rotateOrder = rot_order
		zro.matchPosition(target_jnt)
		zro.matchRotation(target_jnt)
		p_cons = core.parentConstraint(gmbl, target_jnt)
		p_cons.name = c_name + '_parCons'
		fk_ctrls.append((ctrl, zro, gmbl))

	fk_ctrls[3][1].parent(fk_ctrls[2][2])  # ball -> ankle
	fk_ctrls[2][1].parent(fk_ctrls[1][2])  # ankle -> lower
	fk_ctrls[1][1].parent(fk_ctrls[0][2])  # lower -> upper
	fk_ctrls[0][1].parent(armFkCtrl_grp)

	# IK Chain
	armIkCtrl_grp = core.Null(part + 'IkCtrl' + side + '_grp')
	if mc.objExists(priorJnt):
		armIkCtrl_grp.snap(priorJnt)
	armIkCtrl_grp.parent(legRig_grp)

	armIkJnt_grp = core.Null(part + 'IkJnt' + side + '_grp')
	if mc.objExists(priorJnt):
		armIkJnt_grp.snap(priorJnt)
	armIkJnt_grp.parent(legJnt_grp)

	upperLeg_ikJnt = rigTools.jointAt(upperLeg)
	lowerLeg_ikJnt = rigTools.jointAt(lowerLeg)
	ankle_ikJnt = rigTools.jointAt(ankle)
	ball_ikJnt = rigTools.jointAt(ball)
	toe_ikJnt = rigTools.jointAt(toe)

	upperLeg_ikJnt.name = rawName[0] + side + '_ikJnt'
	lowerLeg_ikJnt.name = rawName[1] + side + '_ikJnt'
	ankle_ikJnt.name = rawName[2] + side + '_ikJnt'
	ball_ikJnt.name = rawName[4] + side + '_ikJnt'
	toe_ikJnt.name = rawName[5] + side + '_ikJnt'

	lowerLeg_ikJnt.parent(upperLeg_ikJnt)
	ankle_ikJnt.parent(lowerLeg_ikJnt)
	ball_ikJnt.parent(ankle_ikJnt)
	toe_ikJnt.parent(ball_ikJnt)
	upperLeg_ikJnt.parent(armIkJnt_grp)

	leg_ikh = core.IkRp(startJoint=upperLeg_ikJnt, endEffector=ankle_ikJnt)
	leg_ikh.name = rawName[0] + side + '_ikh'
	leg_ikh.eff = rawName[0] + side + '_eff'
	leg_ikh.attr('v').value = showInfo

	# IK Root Controller (First joint mover)
	ikRootName = nameSpace + rawName[0] + 'IkRoot' + side
	ikRoot_ctrl = core.Dag(ikRootName + '_ctrl')
	ikRoot_ctrl.nmCreateController('cube_ctrlShape')
	ikRoot_ctrl.editCtrlShape(axis=charScale * 5.5)
	ikRoot_ctrl.setColor(colorSec)
	ikRoot_ctrl.rotateOrder = 'yzx'

	ikRootZro_grp = rigTools.zeroGroup(ikRoot_ctrl)
	ikRootZro_grp.name = ikRootName + 'Zro_grp'
	ikRootZro_grp.snap(upperLeg_bJnt)
	ikRootZro_grp.parent(armIkCtrl_grp)

	ikRootGmbl_ctrl = core.createGimbal(ikRoot_ctrl)
	ikRootGmbl_ctrl.rotateOrder = 'yzx'

	rootIk_parCons = core.parentConstraint(ikRootGmbl_ctrl, upperLeg_ikJnt, mo=True)
	rootIk_parCons.name = ikRootName + '_parCons'

	# Ankle / Foot IK Control
	if ikPosi == 'foot':
		ctrlName = nameSpace + 'foot' + 'IK' + (legType.capitalize() if legType != 'leg' else '') + side
	elif ikPosi == 'animalFoot':
		ctrlName = nameSpace + (legType if legType != 'leg' else 'foot') + 'IK' + side
	elif ikPosi == 'heel':
		ctrlName = nameSpace + 'heel' + 'Ik' + (legType.capitalize() if legType != 'leg' else '') + side
	else:
		ctrlName = nameSpace + rawName[2] + 'Ik' + side

	ankleIk_ctrl = core.Dag(ctrlName + '_ctrl')
	ankleIk_ctrl.nmCreateController('cube_ctrlShape')
	ankleIk_ctrl.rotateShape(rotate=(90, 90, 0))
	ankleIk_ctrl.editCtrlShape(axis=charScale * 10)
	ankleIk_ctrl.setColor(colorSide)
	ankleIkZro_grp = rigTools.zeroGroup(ankleIk_ctrl)
	ankleIkZro_grp.name = ctrlName + 'Zro_grp'

	if ikPosi == 'foot' or ikPosi == 'animalFoot':
		ankleIkZro_grp.snapPoint(ball_ikJnt)
	elif ikPosi == 'ankle':
		ankleIkZro_grp.snapPoint(ankle_ikJnt)
	elif ikPosi == 'heel':
		ankleIkZro_grp.snapPoint(heel)
	else:
		ankleIkZro_grp.snapPoint(ankle_ikJnt)

	# Stretchy Attributes on Ankle Controller
	ankleIk_ctrl.addAttribute(attributeType='long', ln='autoStretch', k=True, minValue=0, maxValue=1, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='upStretch', k=True, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='lowStretch', k=True, dv=0)
	ankleIk_ctrl.hideArnoldNode()

	# Pole Vector
	povZro_grp = core.Null(nameSpace + 'knee' + legType.capitalize() + side + 'Zro_grp')
	pov_ctrl = core.Dag(nameSpace + 'knee' + legType.capitalize() + side + '_ctrl')
	if povShape == 'sphereAxis':
		pov_ctrl.nmCreateController('legLFT_pov_ctrlShape')
	elif povShape == 'pyramid':
		pov_ctrl.nmCreateController('pyramid_ctrlShape')
		pov_ctrl.rotateShape(rotate=(90, 0, 0))
	else:
		pov_ctrl.nmCreateController(povShape)
	pov_ctrl.editCtrlShape(axis=charScale * 0.8)
	pov_ctrl.setColor(colorSec)
	mc.parent(pov_ctrl.name, povZro_grp.name)
	povZro_grp.snap(povLeg)
	mc.poleVectorConstraint(pov_ctrl.name, leg_ikh.name, name=nameSpace + 'knee' + legType.capitalize() + side + '_povCons', w=1)

	# Local/World Space Switching for Knee Pole Vector
	partName = nameSpace + 'knee'
	Loc_grp, World_grp, WorldGrp_orientCons, ZroGrp_orientCons, reverseNode_rev = rigTools.parentLocalWorldCtrl(
		pov_ctrl, ankleIk_ctrl, parentTo, povZro_grp, partName
	)
	Loc_grp.name = part + 'Local_grp'
	World_grp.name = part + 'World_grp'
	WorldGrp_orientCons.name = part + side + 'WorldGrp_parCons'
	ZroGrp_orientCons.name = part + side + 'ZroGrp_parCons'
	reverseNode_rev.name = part + side + 'ZroGrParCons_rev'

	# Target Annotation line from Knee/Elbow to POV
	try:
		pc.targetPov(ctrl=pov_ctrl.name, jnt=lowerLeg_bJnt.name)
	except Exception as err:
		logger.warning(f"Failed to create targetPov annotation: {err}")

	# Determine reference joint for IK based on ikPosi
	if ikPosi == 'ankle':
		ref_jnt = ankle_bJnt
	elif ikPosi == 'foot' or ikPosi == 'animalFoot':
		ref_jnt = ball_bJnt
	elif ikPosi == 'heel':
		ref_jnt = heel
	else:
		ref_jnt = ankle_bJnt

	# Matcher Null Snap Group
	offset_null = core.Null(part + 'Offset' + side + '_null')
	offset_null.maSnap(ref_jnt, position=True, rotation=False, scale=True)
	offset_parCons = core.parentConstraint(ref_jnt, offset_null, mo=True)
	offset_parCons.name = part + 'Offset' + side + '_parCons'
	if mc.objExists(nullGrp):
		offset_null.parent(nullGrp)
	if not mc.attributeQuery('offset', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(attributeType='message', longName='offset')
	offset_null.attr('message') >> stick_ctrl.attr('offset')

	# =========================================================================
	# Message Attributes for FK/IK Matcher
	# =========================================================================
	msg_attrs = [
		'stick', 'upJnt', 'midJnt', 'lowJnt', 'ballJnt', 'toeJnt',
		'upFkCtrl', 'midFkCtrl', 'lowFkCtrl', 'ballFkCtrl',
		'ikCtrl', 'ikRootCtrl', 'pov', 'ikRefJnt'
	]
	for attr_name in msg_attrs:
		if not mc.attributeQuery(attr_name, node=stick_ctrl.name, exists=True):
			stick_ctrl.addAttribute(attributeType='message', longName=attr_name)

	stick_ctrl.attr('message') >> stick_ctrl.attr('stick')
	upperLeg_bJnt.attr('message') >> stick_ctrl.attr('upJnt')
	lowerLeg_bJnt.attr('message') >> stick_ctrl.attr('midJnt')
	ankle_bJnt.attr('message') >> stick_ctrl.attr('lowJnt')
	ball_bJnt.attr('message') >> stick_ctrl.attr('ballJnt')
	if mc.objExists(toe_bJnt.name):
		toe_bJnt.attr('message') >> stick_ctrl.attr('toeJnt')

	fk_ctrls[0][0].attr('message') >> stick_ctrl.attr('upFkCtrl')
	fk_ctrls[1][0].attr('message') >> stick_ctrl.attr('midFkCtrl')
	fk_ctrls[2][0].attr('message') >> stick_ctrl.attr('lowFkCtrl')
	if len(fk_ctrls) > 3:
		fk_ctrls[3][0].attr('message') >> stick_ctrl.attr('ballFkCtrl')

	ankleIk_ctrl.attr('message') >> stick_ctrl.attr('ikCtrl')
	ikRoot_ctrl.attr('message') >> stick_ctrl.attr('ikRootCtrl')
	pov_ctrl.attr('message') >> stick_ctrl.attr('pov')
	ref_jnt.attr('message') >> stick_ctrl.attr('ikRefJnt')

	if not mc.attributeQuery('ikh', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(attributeType='message', longName='ikh')
	leg_ikh.attr('message') >> stick_ctrl.attr('ikh')

	# String tags for Matcher
	if not mc.attributeQuery('region', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='region')
	stick_ctrl.setAttribute('region', legType, type='string')

	if not mc.attributeQuery('ikPosi', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='ikPosi')
	stick_ctrl.setAttribute('ikPosi', ikPosi, type='string')

	if not mc.attributeQuery('scale_Attr', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='scale_Attr')
	stick_ctrl.setAttribute('scale_Attr', 'legScale', type='string')

	# =========================================================================
	# Foot Roll Controls & System
	# =========================================================================
	footBehav = ['footOut', 'footIn', 'heelRoll', 'toeRoll', 'ballRoll']

	ballIk_ikh = core.IkRp(startJoint=ankle_ikJnt, endEffector=ball_ikJnt)
	ballIk_ikh.name = nameSpace + footBehav[4] + legType.capitalize() + side + '_ikh'
	ballIk_ikh.attr('v').value = 0

	toeIk_ikh = core.IkRp(startJoint=ball_ikJnt, endEffector=toe_ikJnt)
	toeIk_ikh.name = nameSpace + footBehav[3] + legType.capitalize() + side + '_ikh'
	toeIk_ikh.attr('v').value = 0

	ctrlNameToeRise = f"{nameSpace}ToeRise{legType.capitalize()}Ik{side}"

	

	if footAttr:
		# ---------------------------------------------------------------------
		# Option A: Attribute-Driven Foot Roll using Pure core.Null Transform Pairs
		# (Each _grp is paired with a _Zro_grp so its local transform is [0, 0, 0])
		# ---------------------------------------------------------------------
		logger.info(f"# Creating pure core.Null transform pivot pairs for {part}{side} (footAttr=True)")

		# 1. Ball Roll Group
		ctrlName = f"{nameSpace}{footBehav[4]}Ik{legType.capitalize()}{side}"
		ballRoll_grp = core.Null(ctrlName + 'Buffer_grp')
		ballRoll_grp.snap(ball_bJnt)
		ballRollZro_grp = rigTools.zeroGroup(ballRoll_grp)
		ballRollZro_grp.name = ctrlName + 'Zro_grp'
		ballRoll_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 2. Foot Out Group
		ctrlName = f"{nameSpace}{footBehav[0]}IK{legType.capitalize()}{side}"
		footOut_grp = core.Null(ctrlName + 'Buffer_grp')
		footOut_grp.snap(footOut)
		footOutZro_grp = rigTools.zeroGroup(footOut_grp)
		footOutZro_grp.name = ctrlName + 'Zro_grp'
		footOut_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 3. Foot In Group
		ctrlName = f"{nameSpace}{footBehav[1]}IK{legType.capitalize()}{side}"
		footIn_grp = core.Null(ctrlName + 'Buffer_grp')
		footIn_grp.snap(footIn)
		footInZro_grp = rigTools.zeroGroup(footIn_grp)
		footInZro_grp.name = ctrlName + 'Zro_grp'
		footIn_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 4. Foot Heel Group
		ctrlName = f"{nameSpace}{footBehav[2]}IK{legType.capitalize()}{side}"
		footHeel_grp = core.Null(ctrlName + 'Buffer_grp')
		footHeel_grp.snap(heel)
		footHeelZro_grp = rigTools.zeroGroup(footHeel_grp)
		footHeelZro_grp.name = ctrlName + 'Zro_grp'
		footHeel_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 5. Foot Toe Group
		ctrlName = f"{nameSpace}{footBehav[3]}IK{legType.capitalize()}{side}"
		footToe_grp = core.Null(ctrlName + 'Buffer_grp')
		footToe_grp.snap(toe_bJnt)
		footToeZro_grp = rigTools.zeroGroup(footToe_grp)
		footToeZro_grp.name = ctrlName + 'Zro_grp'
		footToe_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 6. Toe Rise (Offset Group)
		toeRise_grp = core.Null(ctrlNameToeRise + 'Buffer_grp')
		toeRise_grp.snap(ball_bJnt)
		toeRiseZro_grp = rigTools.zeroGroup(toeRise_grp)
		toeRiseZro_grp.name = ctrlNameToeRise + 'Zro_grp'
		toeRise_grp.lockHideAttrLst('tx', 'ty', 'tz', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

		# Pure Group Hierarchy (Standard Clean Space [0, 0, 0])
		footInZro_grp.parent(footOut_grp)
		footHeelZro_grp.parent(footIn_grp)
		footToeZro_grp.parent(footHeel_grp)
		toeRiseZro_grp.parent(footHeel_grp)
		ballRollZro_grp.parent(footToe_grp)
		footOutZro_grp.parent(ankleIk_ctrl)

		
		# Add Foot Roll Attributes on Ankle Controller
		logger.info(f"# Adding foot attributes on {ankleIk_ctrl.name}")
		ankleIk_ctrl.addAttribute(longName='footBar', niceName='_', at='enum', en='Foot', keyable=True)
		ankleIk_ctrl.addAttribute(attributeType='float', ln='ballRoll', minValue=0.0, k=True, dv=0)
		ankleIk_ctrl.addAttribute(attributeType='float', ln='toeRoll', minValue=0.0, k=True, dv=0)
		ankleIk_ctrl.addAttribute(attributeType='float', ln='heelTwist', k=True, dv=0)
		ankleIk_ctrl.addAttribute(attributeType='float', ln='toeTwist', k=True, dv=0)
		ankleIk_ctrl.addAttribute(attributeType='float', ln='footRock', k=True, dv=0)
		ankleIk_ctrl.addAttribute(attributeType='float', ln='ballRise', k=True, dv=0)

		# Connect Foot Attributes to Math Network
		logger.info('# Connecting foot math network to pivot groups')
		sideVal = -1
		# Ball Roll: Invert rotation angle (-1) to pitch foot upward
		ballRoll_mdl = core.MDLWithMul(f"{nameSpace}ballRoll{legType.capitalize()}{side}_mdl", sideVal)
		ankleIk_ctrl.attr('ballRoll') >> ballRoll_mdl.attr('input1')
		ballRoll_mdl.attr('output') >> ballRoll_grp.attr('rx')

		# Toe Roll: Invert rotation angle (-1) to pitch toe upward
		toeRoll_mdl = core.MDLWithMul(f"{nameSpace}toeRoll{legType.capitalize()}{side}_mdl", sideVal)
		ankleIk_ctrl.attr('toeRoll') >> toeRoll_mdl.attr('input1')
		toeRoll_mdl.attr('output') >> footToe_grp.attr('rx')

		
		# Heel Twist & Toe Twist
		ankleIk_ctrl.attr('heelTwist') >> footHeel_grp.attr('ry')
		ankleIk_ctrl.attr('toeTwist') >> footToe_grp.attr('rz')

		# Foot Rock (Bank): Condition Nodes for Foot Out (+) and Foot In (-)
		pos_cnd = core.Condition(f"{nameSpace}footRock{legType.capitalize()}PosVal{side}_cnd")
		pos_cnd.attr('operation').value = 3  # Greater or Equal (>=)
		ankleIk_ctrl.attr('footRock') >> pos_cnd.attr('firstTerm')
		ankleIk_ctrl.attr('footRock') >> pos_cnd.attr('colorIfTrueR')
		pos_cnd.attr('outColorR') >> footOut_grp.attr('rotateX')

		neg_cnd = core.Condition(f"{nameSpace}footRock{legType.capitalize()}NegVal{side}_cnd")
		neg_cnd.attr('operation').value = 5  # Less or Equal (<=)
		ankleIk_ctrl.attr('footRock') >> neg_cnd.attr('firstTerm')
		ankleIk_ctrl.attr('footRock') >> neg_cnd.attr('colorIfTrueR')

		

		minus_mdl = core.MultiDoubleLinear(f"{nameSpace}footRock{legType.capitalize()}MinusVal{side}_mdl")
		minus_mdl.attr('input2').value = -1
		neg_cnd.attr('outColorR') >> minus_mdl.attr('input1')
		minus_mdl.attr('output') >> footIn_grp.attr('rx')

		# Ball Rise (Toe Wiggle)
		ankleIk_ctrl.attr('ballRise') >> toeRise_grp.attr('rx')

		# Parent IK Handles under pivot groups
		leg_ikh.parent(ballRoll_grp)
		ballIk_ikh.parent(ballRoll_grp)
		toeIk_ikh.parent(toeRise_grp)
		


	else:
		# ---------------------------------------------------------------------
		# Option B: Interactive Viewport Foot Controllers (footAttr=False)
		# ---------------------------------------------------------------------
		logger.info(f"# Creating interactive viewport foot controllers for {part}{side} (footAttr=False)")
		# 1. Ball Roll Controller
		ctrlName = f"{nameSpace}{footBehav[4]}Ik{legType.capitalize()}{side}"
		ballRoll_ctrl = core.Dag(ctrlName + '_ctrl')
		ballRoll_ctrl.nmCreateController('ballRoll%s_IK_ctrlShape' % side)
		ballRoll_ctrl.editCtrlShape(axis=charScale * 1.25)
		ballRoll_ctrl.setColor(colorSec)
		ballRollZro_grp = rigTools.zeroGroup(ballRoll_ctrl)
		ballRollZro_grp.name = ctrlName + 'Zro_grp'
		ballRoll_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		ballRollZro_grp.snap(ball_bJnt)

		# 2. Foot Out Controller
		ctrlName = f"{nameSpace}{footBehav[0]}IK{legType.capitalize()}{side}"
		footOut_ctrl = core.Dag(ctrlName + '_ctrl')
		footOut_ctrl.nmCreateController('sphere_ctrlShape')
		footOut_ctrl.editCtrlShape(axis=charScale * 1.25)
		footOut_ctrl.setColor(colorSec)
		footOutZro_grp = rigTools.zeroGroup(footOut_ctrl)
		footOutZro_grp.name = ctrlName + 'Zro_grp'
		footOut_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footOutZro_grp.snap(footOut)

		# 3. Foot In Controller
		ctrlName = f"{nameSpace}{footBehav[1]}IK{legType.capitalize()}{side}"
		footIn_ctrl = core.Dag(ctrlName + '_ctrl')
		footIn_ctrl.nmCreateController('sphere_ctrlShape')
		footIn_ctrl.editCtrlShape(axis=charScale * 1.25)
		footIn_ctrl.setColor(colorSec)
		footInZro_grp = rigTools.zeroGroup(footIn_ctrl)
		footInZro_grp.name = ctrlName + 'Zro_grp'
		footIn_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footInZro_grp.snap(footIn)

		# 4. Foot Heel Controller
		ctrlName = f"{nameSpace}{footBehav[2]}IK{legType.capitalize()}{side}"
		footHeel_ctrl = core.Dag(ctrlName + '_ctrl')
		footHeel_ctrl.nmCreateController('sphere_ctrlShape')
		footHeel_ctrl.editCtrlShape(axis=charScale * 1.25)
		footHeel_ctrl.setColor(colorSec)
		footHeelZro_grp = rigTools.zeroGroup(footHeel_ctrl)
		footHeelZro_grp.name = ctrlName + 'Zro_grp'
		footHeel_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footHeelZro_grp.snap(heel)

		# 5. Foot Toe Controller
		ctrlName = f"{nameSpace}{footBehav[3]}IK{legType.capitalize()}{side}"
		footToe_ctrl = core.Dag(footToeName + '_ctrl')
		footToe_ctrl.nmCreateController('sphere_ctrlShape')
		footToe_ctrl.editCtrlShape(axis=charScale * 1.25)
		footToe_ctrl.setColor(colorSec)
		footToeZro_grp = rigTools.zeroGroup(footToe_ctrl)
		footToeZro_grp.name = ctrlName + 'Zro_grp'
		footToe_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footToeZro_grp.snap(toe_bJnt)

		# 6. Toe Rise Controller
		toeRiseZro_grp = core.Null(ctrlNameToeRise + 'Zro_grp')
		toeRise_ctrl = core.Dag(ctrlNameToeRise + '_ctrl')
		toeRise_ctrl.nmCreateController('circle_ctrlShape')
		toeRise_ctrl.color = colorSide
		toeRise_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		toeRise_ctrl.editCtrlShape(axis=charScale * 1.5)
		toeRise_ctrl.setColor(colorSide)
		toeRise_ctrl.parent(toeRiseZro_grp)
		toeRiseZro_grp.snap(ball_bJnt)

		# Controller Hierarchy
		footInZro_grp.parent(footOut_ctrl)
		footHeelZro_grp.parent(footIn_ctrl)
		footToeZro_grp.parent(footHeel_ctrl)
		toeRiseZro_grp.parent(footHeel_ctrl)
		ballRollZro_grp.parent(footToe_ctrl)
		footOutZro_grp.parent(ankleIk_ctrl)

		# Parent IK Handles under controllers
		leg_ikh.parent(ballRoll_ctrl)
		ballIk_ikh.parent(ballRoll_ctrl)
		toeIk_ikh.parent(toeRise_ctrl)

	if mc.objExists(ikhGrp):
		ankleIkZro_grp.parent(ikhGrp)
	else:
		ankleIkZro_grp.parent(parentTo)

	# Pivot switching between foot and ankle
	ankleIk_ctrl.addAttribute(longName='pivotBar', niceName='_', at='enum', en='Pivot', keyable=True)
	ankleIk_ctrl.setLocked('pivotBar')
	ankleIk_ctrl.addAttribute(longName='pivotChoice', niceName='Pivot At', at='enum', en='foot:ankle', keyable=True)

	# Ankle pivot locator (at ankle joint)
	ankle_target = ankle_ikJnt.name if hasattr(ankle_ikJnt, 'name') else str(ankle_ikJnt)
	ankleIk_loc = core.Locator(f'{nameSpace}ankle{legType.capitalize()}{side}_loc')
	ankleIk_loc.snapPoint(ankle_target)
	ankleIk_loc.parent(ankleIk_ctrl)
	ankleIk_loc.attr('v').value = 0
	ankleIk_loc.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')

	# Foot pivot locator (at foot / ball on ground)
	ball_target = ball_ikJnt.name if hasattr(ball_ikJnt, 'name') else str(ball_ikJnt)
	footIk_loc = core.Locator(f'{nameSpace}footPivot{legType.capitalize()}{side}_loc')
	footIk_loc.snapPoint(ball_target)
	footIk_loc.parent(ankleIk_ctrl)
	footIk_loc.attr('v').value = 0
	footIk_loc.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')

	pivot_cnd = core.Condition(f'{nameSpace}{part}Pivot{side}_cnd')
	footIk_loc.attr('translate') >> pivot_cnd.attr('colorIfTrue')
	ankleIk_loc.attr('translate') >> pivot_cnd.attr('colorIfFalse')
	ankleIk_ctrl.attr('pivotChoice') >> pivot_cnd.attr('secondTerm')
	pivot_cnd.attr('outColor') >> ankleIk_ctrl.attr('rotatePivot')
	pivot_cnd.attr('outColor') >> ankleIk_ctrl.attr('scalePivot')

	# =========================================================================
	# Stretchy IK Setup (Positioned after ankleIk_ctrl pivot & group parenting)
	# =========================================================================
	pmaNode = None
	try:
		pmaNode, psStreEndName = create.iKStretch(
			ikJnt=(upperLeg_ikJnt.name, lowerLeg_ikJnt.name, ankle_ikJnt.name),
			ikCtrl=(ikRoot_ctrl.name, ankleIk_ctrl.name),
			side=side,
			scaleCtrl=scaleCtrl,
			region=legType,
			noTouchGrp=noTouchGrp,
			nameSpace=nameSpace,
			lowNam=rawName[2],
			alongAxis=alongAxis,
			povPosi='front'
		)
		logger.info(f"IK Stretch created successfully for {part} {side}")
	except Exception as err:
		logger.warning(f"Failed to create IK Stretch: {err}")

	# Blend switch & Twist Rig
	if creTwistJnt:
		# Create Buffer Joints
		buffJnt_grp = core.Null(f"{nameSpace}{legType}BuffJnt{side}_grp")
		upper_buffJnt = rigTools.jointAt(upperLeg_bJnt)
		middle_buffJnt = rigTools.jointAt(lowerLeg_bJnt)
		lower_buffJnt = rigTools.jointAt(ankle_bJnt)

		upper_buffJnt.name = f"{rawName[0]}{side}_buffJnt"
		middle_buffJnt.name = f"{rawName[1]}{side}_buffJnt"
		lower_buffJnt.name = f"{rawName[2]}{side}_buffJnt"

		middle_buffJnt.parent(upper_buffJnt)
		lower_buffJnt.parent(middle_buffJnt)
		upper_buffJnt.parent(buffJnt_grp)
		buffJnt_grp.parent(legJnt_grp)

		upper_buffJnt.setJointColor('softGray')
		middle_buffJnt.setJointColor('softGray')
		lower_buffJnt.setJointColor('softGray')

		upper_buffJnt.attr('radius').value = 1.25
		middle_buffJnt.attr('radius').value = 1.25
		lower_buffJnt.attr('radius').value = 1.25

		upper_buffJnt.rotateOrder = upperLeg_bJnt.rotateOrder
		middle_buffJnt.rotateOrder = lowerLeg_bJnt.rotateOrder
		lower_buffJnt.rotateOrder = ankle_bJnt.rotateOrder

		# Blend FK and IK to Buffer Joints
		for base in [rawName[0], rawName[1], rawName[2]]:
			fk_j = base + side + '_fkJnt'
			ik_j = base + side + '_ikJnt'
			buff_j = base + side + '_buffJnt'
			if mc.objExists(fk_j) and mc.objExists(ik_j) and mc.objExists(buff_j):
				psCon = mc.parentConstraint(fk_j, ik_j, buff_j, name=f"{base}Switch{side}_parCons", mo=True)
				revNode = mc.createNode('reverse', name=f"{base}Switch{side}_rev")
				mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{revNode}.inputX")
				mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{psCon[0]}.{ik_j}W1")
				mc.connectAttr(f"{revNode}.outputX", f"{psCon[0]}.{fk_j}W0")

		# Ball blending directly to ball_bJnt
		fk_ball = rawName[4] + side + '_fkJnt'
		ik_ball = rawName[4] + side + '_ikJnt'
		b_ball = rawName[4] + side + '_bJnt'
		if mc.objExists(fk_ball) and mc.objExists(ik_ball) and mc.objExists(b_ball):
			psCon = mc.parentConstraint(fk_ball, ik_ball, b_ball, name=f"{rawName[4]}Switch{side}_parCons", mo=True)
			revNode = mc.createNode('reverse', name=f"{rawName[4]}Switch{side}_rev")
			mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{revNode}.inputX")
			mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{psCon[0]}.{ik_ball}W1")
			mc.connectAttr(f"{revNode}.outputX", f"{psCon[0]}.{fk_ball}W0")

		# Create Twist Rig (isolating roll/twist from upper leg)
		logger.info(f"Creating Twist Rig for {legType}{side}...")
		upper_fk_ctrl = fk_ctrls[0][0].name
		follow_grp, upperTwist01 = tr.twistRigAuto(
			nameSpace=nameSpace,
			parent_jnt=upper_buffJnt.name,
			child_jnt=middle_buffJnt.name,
			fk_shoulderCtrl=upper_fk_ctrl,
			ik_shoulderCtrl=ikRoot_ctrl.name,
			side=side,
			region=legType,
			priorJnt=priorJnt,
			stick_ctrl=stick_ctrl.name,
			charScale=charScale,
			showInfo=showInfo,
			alongAxis=alongAxis
		)
		if mc.objExists(noTouchGrp):
			mc.parent(follow_grp, noTouchGrp)
		elif mc.objExists(parentTo):
			mc.parent(follow_grp, parentTo)

		# Final Connections: Twist & Buffer -> Bind Joints
		upperTwist_parCons = core.parentConstraint(upperTwist01, upperLeg_bJnt.name, mo=True)
		upperTwist_parCons.name = f"{nameSpace}upper{legType.capitalize()}Twist{side}_parCons"
		upperTwist_scalCons = core.scaleConstraint(upperTwist01, upperLeg_bJnt.name, mo=True)
		upperTwist_scalCons.name = f"{nameSpace}upper{legType.capitalize()}Twist{side}_scalCons"

		midTwist_parCons = core.parentConstraint(middle_buffJnt.name, lowerLeg_bJnt.name, mo=True)
		midTwist_parCons.name = f"{nameSpace}mid{legType.capitalize()}Twist{side}_parCons"
		midTwist_scalCons = core.scaleConstraint(middle_buffJnt.name, lowerLeg_bJnt.name, mo=True)
		midTwist_scalCons.name = f"{nameSpace}mid{legType.capitalize()}Twist{side}_scalCons"

		lwrTwist_parCons = core.parentConstraint(lower_buffJnt.name, ankle_bJnt.name, mo=True)
		lwrTwist_parCons.name = f"{nameSpace}lwr{legType.capitalize()}Twist{side}_parCons"
		lwrTwist_scalCons = core.scaleConstraint(lower_buffJnt.name, ankle_bJnt.name, mo=True)
		lwrTwist_scalCons.name = f"{nameSpace}lwr{legType.capitalize()}Twist{side}_scalCons"

	else:
		# Direct FK/IK blend without twist isolation (legacy fallback)
		switch_jnts = [rawName[0], rawName[1], rawName[2], rawName[4]]
		for each in switch_jnts:
			fk_j = each + side + '_fkJnt'
			ik_j = each + side + '_ikJnt'
			b_j = each + side + '_bJnt'
			if mc.objExists(fk_j) and mc.objExists(ik_j) and mc.objExists(b_j):
				psCon = mc.parentConstraint(fk_j, ik_j, b_j, name=each + 'Switch_parentCons', mo=True)
				revNode = mc.createNode('reverse', name=each + 'Switch' + side + '_rev')
				mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{revNode}.inputX")
				mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{psCon[0]}.{ik_j}W1")
				mc.connectAttr(f"{revNode}.outputX", f"{psCon[0]}.{fk_j}W0")

	legRig_grp.parent(parentTo)
	stickZro_grp.parent(parentTo)
	if mc.objExists(parentTo):
		povZro_grp.parent(parentTo)

	if mc.objExists(jnt_grp):
		legJnt_grp.parent(jnt_grp)
	elif mc.objExists(noTouchGrp):
		legJnt_grp.parent(noTouchGrp)
	legJnt_grp.attr('visibility').value = showInfo

	stickVis_rev = core.Reverse()
	stick_ctrl.attr('FK_IK') >> stickVis_rev.attr('inputX')
	stickVis_rev.attr('outputX') >> armFkCtrl_grp.attr('visibility')
	stick_ctrl.attr('FK_IK') >> armIkCtrl_grp.attr('visibility')
	stick_ctrl.attr('FK_IK') >> ankleIkZro_grp.attr('visibility')
	stick_ctrl.attr('FK_IK') >> povZro_grp.attr('visibility')

	logger.info(f"#### End of Plantigrade {part} {side} Rig ####")
	return {
		"upperLeg_bJnt": upperLeg_bJnt.name,
		"lowerLeg_bJnt": lowerLeg_bJnt.name,
		"ankle_bJnt": ankle_bJnt.name,
		"ikRoot_ctrl": ikRoot_ctrl.name,
		"stick_ctrl": stick_ctrl.name,
		"ankleIk_ctrl": ankleIk_ctrl.name
	}


# Backward compatibility aliases
quradrupedLegRig = eh_quadrupedLegRig
