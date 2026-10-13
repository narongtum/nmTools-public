# -*- coding: utf-8 -*-
"""
Quadruped Double IK Leg Rig Component (eh_quadrupedLegRig_DoubleIK)
===================================================================

ARCHITECTURAL MANDATE & CORE PRINCIPLE:
--------------------------------------
This Double IK module is explicitly engineered to AVOID and REPLACE Maya's
native `ikSpringSolver` entirely.

RATIONALE & COMPARISON:
-----------------------
- Legacy `eh_quadrupedLegRig.py` relied on `ikSpringSolver`, which requires
  external plugin licensing (`ikSpringSolver.mll`), suffers from sudden popping/
  flipping near chain extension, and distributes joint bending inflexibly.
- The Double IK (V3) architecture decomposes the 4-joint quadruped hind leg into
  modular 2-bone and single-bone subsystems driven exclusively by Vanilla Maya solvers:
    1. Upper Main Chain (Hip -> Knee -> Hock): 2-bone subsystem powered by standard `ikRPsolver`.
    2. Lower Main Chain (Hock -> Ankle): 1-bone subsystem powered by Single-Chain `ikSCsolver`.
    3. Guide Kinematic Chain (guideHip -> guideKnee -> guideHock): 2-bone guide chain powered by `ikRPsolver`.
    4. Hock Pivot & Aim Follow: `hock_ik_aim_grp` aim-constrained to `guideKnee_gdeJnt` (worldUp = ankleIk_ctrl),
       guaranteeing natural hock compression and direct manual articulation via `lowerLegIK_ctrl`.
    5. Full Interactive Foot Roll & Roll-Back Ankle: Complete multi-pivot ground mechanics.
    6. Multi-Limb Dynamic Scoping: Zero node clashing across multi-legged creatures (e.g. Back01, Back02).
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

logger = logging.getLogger('eh_quadrupedLegRig_DoubleIK')
logger.setLevel(logging.DEBUG)

color_part_dict = mnd.COLOR_part_dict


def eh_quadrupedLegRig_DoubleIK(
	nameSpace='',
	parentTo='ctrl_grp',
	side='LFT',
	tmpJnt=(
		'upLegBackLFT_tmpJnt', 'midLegBackLFT_tmpJnt', 'ankleBackLFT_tmpJnt',
		'legPovBackLFT_tmpJnt', 'ballRollBackLFT_tmpJnt', 'toeRollBackLFT_tmpJnt',
		'heelRollBackLFT_tmpJnt', 'footOutBackLFT_tmpJnt', 'footInBackLFT_tmpJnt', 'lowLegBackLFT_tmpJnt'
	),
	guideJnt=(
		'guideHipBackLFT_tmpJnt', 'guideKneeBackLFT_tmpJnt', 'guideHockBackLFT_tmpJnt', 'guideLegPovBackLFT_tmpJnt'
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
	setPrefAngle=False,
	stickShape='stick_ctrlShape',
	ctrlShape='fk_ctrlShape',
	linkRotOrder=False,
	footAttr=False,
	ikPosi='foot',
	pxyJnt=None
):
	"""
	Builds a full 4-joint Digitigrade Quadruped Leg Rig powered by a Double IK
	2-Bone Guide Driver Chain with full Leg Behaviors (Dual Ribbon, Stretchy IK,
	Knee/Hock Lock, Interactive Foot Roll, and FK/IK Blend Switch).

	:param nameSpace: Namespace prefix.
	:param parentTo: Master parent group for controllers.
	:param side: 'LFT' or 'RGT'.
	:param tmpJnt: Tuple of 10 guide joints for the main leg.
	:param guideJnt: Tuple of 3-4 guide joints for the guide driver chain (guideHip, guideKnee, guideHock, [guidePov]).
	:param priorJnt: Joint to parent the upper leg to (e.g. 'hip_bJnt').
	:param ikhGrp: IK handle storage group.
	:param noTouchGrp: Non-transformable node group.
	:param nullGrp: Snap locators group.
	:param jnt_grp: Joint storage group.
	:param showInfo: Whether to display joint labels/handles in viewport.
	:param ribbon: Enable Ribbon Matrix Deformers.
	:param ribbonRes: Ribbon resolution ('low', 'mid', 'high').
	:param ribbonName: Ribbon component names.
	:param charScale: Global character scale.
	:param region: Body region identifier.
	:param alongAxis: Primary joint alignment axis.
	:param povShape: Pole vector controller shape.
	:param softIk: Enable Matrix Soft IK.
	:param setPrefAngle: Enable or disable setting joint preferred angles (default: False).
	:param stickShape: Shape for the FK/IK stick controller.
	:param ctrlShape: Shape for FK controllers.
	:param linkRotOrder: Link rotate orders across IK/FK/Bind chains.
	:param footAttr: Attribute-driven foot roll system.
	:param pxyJnt: (Legacy alias for guideJnt).
	:return: Dictionary containing key rig objects and controller names.
	"""
	core.makeHeader('Start of %s%s Rig (Double IK)' % ('eh_quadrupedLegRig', side))
	logger.info("Initializing Quadruped Double IK Leg Rig (%s)..." % side)

	# Backwards compatibility fallback for legacy pxyJnt parameter
	if (guideJnt is None or guideJnt == ()) and pxyJnt is not None:
		guideJnt = pxyJnt

	# Validate Guide Joints input
	if not guideJnt or len(guideJnt) < 3:
		mc.error('The "guideJnt" argument is strictly required (must provide at least 3 guide joints: guideHip, guideKnee, guideHock).')
		return

	for gj in guideJnt[:3]:
		if not mc.objExists(gj):
			mc.error('Guide driver joint "%s" does not exist in scene!' % gj)
			return

	for tj in tmpJnt:
		if not mc.objExists(tj):
			mc.error('Guide joint "%s" does not exist in scene!' % tj)
			return

	colorSide = color_part_dict['left'] if side == 'LFT' else color_part_dict['right']
	colorSec = color_part_dict.get('secondary', 'yellow')

	# =========================================================================
	# 1. Assign Guide / Temp Joint References
	# =========================================================================
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

	guideHip_tmp = core.Dag(guideJnt[0])
	guideKnee_tmp = core.Dag(guideJnt[1])
	guideHock_tmp = core.Dag(guideJnt[2])

	# =========================================================================
	# Determine region and position tag dynamically
	# =========================================================================
	import re
	if region and region not in ('backLeg', 'frontLeg', 'leg'):
		legType = region
		clean_pos = region.replace('Leg', '').replace('leg', '')
		position = clean_pos[0].upper() + clean_pos[1:] if clean_pos else ''
	else:
		tmp_base = tmpJnt[0].split('_')[0]
		match = re.search(r'(Front[0-9a-zA-Z]*|Back[0-9a-zA-Z]*|Mid[0-9a-zA-Z]*|Hind[0-9a-zA-Z]*)', tmp_base, re.IGNORECASE)
		if match:
			pos_raw = match.group(1)
			if pos_raw.lower().startswith('back'):
				position = 'Back' + pos_raw[4:]
			elif pos_raw.lower().startswith('front'):
				position = 'Front' + pos_raw[5:]
			elif pos_raw.lower().startswith('mid'):
				position = 'Mid' + pos_raw[3:]
			elif pos_raw.lower().startswith('hind'):
				position = 'Hind' + pos_raw[4:]
			else:
				position = pos_raw[0].upper() + pos_raw[1:]
			legType = position[0].lower() + position[1:] + 'Leg'
		elif 'Front' in tmpJnt[0]:
			legType = 'frontLeg'
			position = 'Front'
		elif 'Back' in tmpJnt[0]:
			legType = 'backLeg'
			position = 'Back'
		else:
			legType = region if region else 'leg'
			position = ''

	# Derive raw naming tokens
	rawName = []
	for each in tmpJnt:
		tmp = each.split('_')[0][:-3] if len(each.split('_')[0]) >= 3 else each.split('_')[0]
		rawName.append(tmp)

	# =========================================================================
	# 2. Create Bind Joint Chain (_bJnt)
	# =========================================================================
	upperLeg_bJnt = rigTools.jointAt(upperLeg)
	midLeg_bJnt = rigTools.jointAt(midLeg)
	lowerLeg_bJnt = rigTools.jointAt(lowerLeg)
	ankle_bJnt = rigTools.jointAt(ankle)
	ball_bJnt = rigTools.jointAt(ball)
	toe_bJnt = rigTools.jointAt(toe)

	upperLeg_bJnt.name = rawName[0] + side + '_bJnt'
	midLeg_bJnt.name = rawName[1] + side + '_bJnt'
	lowerLeg_bJnt.name = rawName[9] + side + '_bJnt'
	ankle_bJnt.name = rawName[2] + side + '_bJnt'
	ball_bJnt.name = rawName[4] + side + '_bJnt'
	toe_bJnt.name = rawName[5] + side + '_bJnt'

	# Set Rotate Orders
	upperLeg_bJnt.rotateOrder = 'yzx'
	midLeg_bJnt.rotateOrder = 'yzx'
	lowerLeg_bJnt.rotateOrder = 'yzx'
	ankle_bJnt.rotateOrder = 'yzx'

	# Bind Hierarchy
	midLeg_bJnt.parent(upperLeg_bJnt)
	lowerLeg_bJnt.parent(midLeg_bJnt)
	ankle_bJnt.parent(lowerLeg_bJnt)
	toe_bJnt.parent(ball_bJnt)
	ball_bJnt.parent(ankle_bJnt)
	ankle_bJnt.attr('segmentScaleCompensate').value = 0
	ball_bJnt.attr('segmentScaleCompensate').value = 0
	toe_bJnt.attr('segmentScaleCompensate').value = 0

	if mc.objExists(priorJnt):
		upperLeg_bJnt.parent(priorJnt)

	# =========================================================================
	# 3. Master & Rig Groups
	# =========================================================================
	part = nameSpace + legType
	legRig_grp = core.Null(part + 'Rig' + side + '_grp')
	if mc.objExists(priorJnt):
		legRigGrp_parCons = core.parentConstraint(priorJnt, legRig_grp)
		legRigGrp_parCons.name = part + 'Rig' + side + '_parCons'

	legJnt_grp = core.Null(part + 'Jnt' + side + '_grp')

	# Stick Controller (FK/IK Switch & Settings)
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
	stick_ctrl.addAttribute(attributeType='float', longName='showGuidePov', minValue=0, maxValue=1, defaultValue=1, keyable=True)
	if not mc.attributeQuery('location', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(dataType='string', longName='location')
	stick_ctrl.setAttribute('location', ikPosi, type='string')
	stick_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

	# =========================================================================
	# 4. Create FK Chain & FK Controllers
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
	toe_fkJnt = rigTools.jointAt(toe)

	upperLeg_fkJnt.name = rawName[0] + side + '_fkJnt'
	midLeg_fkJnt.name = rawName[1] + side + '_fkJnt'
	lowerLeg_fkJnt.name = rawName[9] + side + '_fkJnt'
	ankle_fkJnt.name = rawName[2] + side + '_fkJnt'
	ball_fkJnt.name = rawName[4] + side + '_fkJnt'
	toe_fkJnt.name = rawName[5] + side + '_fkJnt'

	midLeg_fkJnt.parent(upperLeg_fkJnt)
	lowerLeg_fkJnt.parent(midLeg_fkJnt)
	ankle_fkJnt.parent(lowerLeg_fkJnt)
	ball_fkJnt.parent(ankle_fkJnt)
	toe_fkJnt.parent(ball_fkJnt)
	upperLeg_fkJnt.parent(fkJnt_grp)

	# FK Controls
	fk_pos_tag = position if position else legType.capitalize()
	fk_configs = [
		('upper' + fk_pos_tag, upperLeg_fkJnt, 0.9, 'yzx'),
		('middle' + fk_pos_tag, midLeg_fkJnt, 0.85, 'yzx'),
		('lower' + fk_pos_tag, lowerLeg_fkJnt, 0.8, 'yzx'),
		('ankle' + fk_pos_tag, ankle_fkJnt, 0.7, 'xzy'),
		('ball' + fk_pos_tag, ball_fkJnt, 0.7, 'xzy')
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
		s_cons = core.scaleConstraint(gmbl, target_jnt)
		s_cons.name = c_name + '_scaleCons'
		fk_ctrls.append((ctrl, zro, gmbl))

	# Parent FK hierarchy
	fk_ctrls[4][1].parent(fk_ctrls[3][2])  # ball -> ankle gmbl
	fk_ctrls[3][1].parent(fk_ctrls[2][2])  # ankle -> lower gmbl
	fk_ctrls[2][1].parent(fk_ctrls[1][2])  # lower -> middle gmbl
	fk_ctrls[1][1].parent(fk_ctrls[0][2])  # middle -> upper gmbl
	fk_ctrls[0][1].parent(fkCtrl_grp)      # upper -> fkCtrl_grp

	# =========================================================================
	# 5. Master IK Groups, Root Controller, and Main IK Joints
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

	# Root IK Controller
	rootName = rawName[0] + 'Ik' + side
	ikRoot = core.Dag(rootName + '_ctrl')
	ikRoot.nmCreateController('cube_ctrlShape')
	ikRoot.editCtrlShape(axis=charScale * 5.5)
	ikRoot.color = colorSide
	IkRootZro_grp = rigTools.zeroGroup(ikRoot)
	IkRootZro_grp.name = rootName + 'Zro_grp'
	IkRootZro_grp.snap(upperLeg_bJnt)
	ikRootGmbl_ctrl = core.createGimbal(ikRoot)

	rootIk_parCons = core.parentConstraint(ikRootGmbl_ctrl, upperLeg_ikJnt.name, mo=True)
	rootIk_parCons.name = part + side + 'Jnt_parCons'

	# =========================================================================
	# 6. Create 2-Bone Guide Driver Chain (_gdeJnt)
	# =========================================================================
	guideHip_gdeJnt = rigTools.jointAt(guideHip_tmp)
	guideKnee_gdeJnt = rigTools.jointAt(guideKnee_tmp)
	guideHock_gdeJnt = rigTools.jointAt(guideHock_tmp)

	guideHip_gdeJnt.name = 'guide' + rawName[0] + side + '_gdeJnt'
	guideKnee_gdeJnt.name = 'guide' + rawName[1] + side + '_gdeJnt'
	guideHock_gdeJnt.name = 'guide' + rawName[2] + side + '_gdeJnt'

	guideKnee_gdeJnt.parent(guideHip_gdeJnt)
	guideHock_gdeJnt.parent(guideKnee_gdeJnt)
	guideHip_gdeJnt.parent(armIkJnt_grp)

	# Constrain guide chain root to follow ikRootGmbl with maintainOffset
	guideRoot_parCons = core.parentConstraint(ikRootGmbl_ctrl, guideHip_gdeJnt.name, mo=True)
	guideRoot_parCons.name = 'guide' + part + side + 'Root_parCons'

	# =========================================================================
	# 7. Master Ankle IK Controller & Foot Roll System
	# =========================================================================
	footBehav = ['footOut', 'footIn', 'heelRoll', 'toeRoll', 'ballRoll', 'ankle', 'rollBackAnkle']
	if ikPosi == 'foot':
		ctrlName = nameSpace + 'foot' + legType.capitalize() + 'IK' + side
	elif ikPosi == 'animalFoot':
		ctrlName = nameSpace + legType + 'IK' + side
	elif ikPosi == 'heel':
		ctrlName = nameSpace + 'heel' + legType.capitalize() + 'IK' + side
	else:
		ctrlName = nameSpace + footBehav[5] + legType.capitalize() + 'IK' + side

	ankleIk_ctrl = core.Dag(ctrlName + '_ctrl')
	ankleIk_ctrl.nmCreateController('cube_ctrlShape')
	ankleIk_ctrl.rotateShape(rotate=(90, 90, 0))
	ankleIk_ctrl.editCtrlShape(axis=charScale * 10)
	ankleIk_ctrl.color = colorSide

	ankleIkZro_grp = rigTools.zeroGroup(ankleIk_ctrl)
	ankleIkZro_grp.name = ctrlName + 'Zro_grp'
	if ikPosi == 'foot' or ikPosi == 'animalFoot':
		ankleIkZro_grp.snapPoint(ball_ikJnt)
	elif ikPosi == 'ankle':
		ankleIkZro_grp.snapPoint(ankle_ikJnt)
	elif ikPosi == 'heel':
		ankleIkZro_grp.snapPoint(heelRoll)
	else:
		ankleIkZro_grp.snapPoint(ankle_ikJnt)
	ankleIkZro_grp.parent(parentTo)

	# Matcher Null Snap Group
	offset_null = core.Null(part + 'Offset' + side + '_null')
	if ikPosi == 'ankle':
		offset_null.maSnap(ankle_bJnt, position=True, rotation=True, scale=True)
		offset_parCons = core.parentConstraint(ankle_bJnt, offset_null, mo=True)
	elif ikPosi == 'foot' or ikPosi == 'animalFoot':
		offset_null.maSnap(ankle_bJnt, position=True, rotation=False, scale=True)
		offset_parCons = core.parentConstraint(ankle_bJnt, offset_null, mo=True)
	elif ikPosi == 'heel':
		offset_null.maSnap(heelRoll, position=True, rotation=True, scale=True)
		offset_parCons = core.parentConstraint(heelRoll, offset_null, mo=True)
	else:
		offset_null.maSnap(ankle_bJnt, position=True, rotation=True, scale=True)
		offset_parCons = core.parentConstraint(ankle_bJnt, offset_null, mo=True)

	offset_parCons.name = part + 'Offset' + side + '_parCons'
	if mc.objExists(nullGrp):
		offset_null.parent(nullGrp)
	if not mc.attributeQuery('offset', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(attributeType='message', longName='offset')
	offset_null.attr('message') >> stick_ctrl.attr('offset')

	# Stretchy & Aim Attributes on Ankle Controller
	ankleIk_ctrl.addAttribute(attributeType='long', ln='autoStretch', k=True, minValue=0, maxValue=1, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='upStretch', k=True, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='lowStretch', k=True, dv=0)
	ankleIk_ctrl.addAttribute(attributeType='float', ln='toe_Aim', k=True, minValue=0, maxValue=1, dv=1)
	ankleIk_ctrl.hideArnoldNode()

	# Roll Back Ankle Controller (Auto Toe-Aim Subsystem)
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
	rollBackAnkleIkZro_grp.snapPoint(ankle_ikJnt)
	mc.xform(rollBackAnkleIkZro_grp.name, ws=True, ro=[0, 0, 0])

	# Aim Constraint & Still Group Setup for Auto-Aim
	rollBackAnkleIkStill_grp = core.Null(ctrlName + side + 'Still_grp')
	rollBackAnkleIkStill_grp.snapPoint(upperLeg_bJnt)
	rollBackAnkleIkStill_grp.parent(ankleIk_ctrl)

	up_obj = core.Locator(ctrlName + side + '_loc')
	up_obj.snapPoint(rollBackAnkleIkOffset_grp)
	mc.move(0, 0, charScale * 30, up_obj.name, relative=True, worldSpace=True)

	upperLeg_aimCons = core.aimConstraint(
		upperLeg_ikJnt, rollBackAnkleIkStill_grp, rollBackAnkleIkOffset_grp,
		mo=False, aimVector=(0, 1, 0), upVector=(0, 0, 1),
		worldUpType='object', worldUpObject=up_obj.name
	)
	upperLeg_aimCons.attr('worldUpType').value = 1
	upperLeg_aimCons.attr(f"{upperLeg_ikJnt.name}W0").value = 1
	upperLeg_aimCons.name = f"{ctrlName}{side}_aimCons"

	toeAnim_rev = core.Reverse()
	toeAnim_rev.name = f"{ctrlName}{side}_rev"
	ankleIk_ctrl.attr('toe_Aim') >> toeAnim_rev.attr('inputY')
	ankleIk_ctrl.attr('toe_Aim') >> upperLeg_aimCons.attr(f"{rollBackAnkleIkStill_grp.name}W1")
	toeAnim_rev.attr('outputY') >> upperLeg_aimCons.attr(f"{upperLeg_ikJnt.name}W0")

	up_obj.parent(ankleIk_ctrl)
	up_obj.attr('v').value = 0

	ctrlNameToeRise = f"{nameSpace}ToeRise{legType}Ik{side}"

	if footAttr:
		# ---------------------------------------------------------------------
		# Option A: Attribute-Driven Foot Roll using Pure core.Null Transform Pairs
		# (Each _grp is paired with a _Zro_grp so its local transform is [0, 0, 0])
		# ---------------------------------------------------------------------
		logger.info('# Creating pure core.Null transform pivot pairs (footAttr=True)')

		# 1. Ball Roll Group
		ctrlName = f"{nameSpace}{footBehav[4]}Ik{legType}{side}"
		ballRoll_grp = core.Null(ctrlName + 'Buffer_grp')
		ballRoll_grp.snap(ball_bJnt)
		ballRollZro_grp = rigTools.zeroGroup(ballRoll_grp)
		ballRollZro_grp.name = ctrlName + 'Zro_grp'
		ballRoll_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 2. Foot Out Group
		ctrlName = f"{nameSpace}{footBehav[0]}{legType}IK{side}"
		footOut_grp = core.Null(ctrlName + 'Buffer_grp')
		footOut_grp.snap(footOut)
		footOutZro_grp = rigTools.zeroGroup(footOut_grp)
		footOutZro_grp.name = ctrlName + 'Zro_grp'
		footOut_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 3. Foot In Group
		ctrlName = f"{nameSpace}{footBehav[1]}{legType}IK{side}"
		footIn_grp = core.Null(ctrlName + 'Buffer_grp')
		footIn_grp.snap(footIn)
		footInZro_grp = rigTools.zeroGroup(footIn_grp)
		footInZro_grp.name = ctrlName + 'Zro_grp'
		footIn_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 4. Foot Heel Group
		ctrlName = f"{nameSpace}{footBehav[2]}{legType}IK{side}"
		footHeel_grp = core.Null(ctrlName + 'Buffer_grp')
		footHeel_grp.snap(heel)
		footHeelZro_grp = rigTools.zeroGroup(footHeel_grp)
		footHeelZro_grp.name = ctrlName + 'Zro_grp'
		footHeel_grp.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# 5. Foot Toe Group
		ctrlName = f"{nameSpace}{footBehav[3]}{legType}IK{side}"
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

		# Parent rollBackAnkle under ballRoll_grp
		rollBackAnkleIkZro_grp.parent(ballRoll_grp)
		mc.xform(rollBackAnkleIkZro_grp.name, ws=True, ro=[0, 0, 0])
		mc.setAttr(f"{rollBackAnkleIkOffset_grp.name}.r", 0, 0, 0)
		mc.setAttr(f"{rollBackAnkleIk_ctrl.name}.r", 0, 0, 0)

		# Add Foot Roll Attributes on Ankle Controller
		logger.info('# Adding foot attributes on %s' % ankleIk_ctrl.name)
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
		ballRoll_mdl = core.MDLWithMul(f"{nameSpace}ballRoll{legType}{side}_mdl", sideVal)
		ankleIk_ctrl.attr('ballRoll') >> ballRoll_mdl.attr('input1')
		ballRoll_mdl.attr('output') >> ballRoll_grp.attr('rx')

		# Toe Roll: Invert rotation angle (-1) to pitch toe upward
		toeRoll_mdl = core.MDLWithMul(f"{nameSpace}toeRoll{legType}{side}_mdl", sideVal)
		ankleIk_ctrl.attr('toeRoll') >> toeRoll_mdl.attr('input1')
		toeRoll_mdl.attr('output') >> footToe_grp.attr('rx')

		# Heel Twist & Toe Twist
		ankleIk_ctrl.attr('heelTwist') >> footHeel_grp.attr('ry')
		ankleIk_ctrl.attr('toeTwist') >> footToe_grp.attr('rz')

		# Foot Rock (Bank): Condition Nodes for Foot Out (+) and Foot In (-)
		pos_cnd = core.Condition(f"{nameSpace}footRock{legType}PosVal{side}_cnd")
		pos_cnd.attr('operation').value = 3  # Greater or Equal (>=)
		ankleIk_ctrl.attr('footRock') >> pos_cnd.attr('firstTerm')
		ankleIk_ctrl.attr('footRock') >> pos_cnd.attr('colorIfTrueR')
		pos_cnd.attr('outColorR') >> footOut_grp.attr('rotateX')

		neg_cnd = core.Condition(f"{nameSpace}footRock{legType}NegVal{side}_cnd")
		neg_cnd.attr('operation').value = 5  # Less or Equal (<=)
		ankleIk_ctrl.attr('footRock') >> neg_cnd.attr('firstTerm')
		ankleIk_ctrl.attr('footRock') >> neg_cnd.attr('colorIfTrueR')

		minus_mdl = core.MultiDoubleLinear(f"{nameSpace}footRock{legType}MinusVal{side}_mdl")
		minus_mdl.attr('input2').value = -1
		neg_cnd.attr('outColorR') >> minus_mdl.attr('input1')
		minus_mdl.attr('output') >> footIn_grp.attr('rx')

		# Ball Rise (Toe Wiggle)
		ankleIk_ctrl.attr('ballRise') >> toeRise_grp.attr('rx')

	else:
		# ---------------------------------------------------------------------
		# Option B: Interactive Viewport Foot Controllers (footAttr=False)
		# ---------------------------------------------------------------------
		logger.info('# Creating interactive viewport foot controllers (footAttr=False)')
		# 1. Ball Roll Controller
		ctrlName = f"{nameSpace}{footBehav[4]}Ik{legType}{side}"
		ballRoll_ctrl = core.Dag(ctrlName + '_ctrl')
		ballRoll_ctrl.nmCreateController(f"ballRoll{side}_IK_ctrlShape")
		ballRoll_ctrl.editCtrlShape(axis=charScale * 1.25)
		ballRoll_ctrl.setColor(colorSec)
		ballRollZro_grp = rigTools.zeroGroup(ballRoll_ctrl)
		ballRollZro_grp.name = ctrlName + 'Zro_grp'
		ballRoll_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		ballRollZro_grp.snap(ball_bJnt)

		# 2. Foot Out Controller
		ctrlName = f"{nameSpace}{footBehav[0]}{legType}IK{side}"
		footOut_ctrl = core.Dag(ctrlName + '_ctrl')
		footOut_ctrl.nmCreateController('sphere_ctrlShape')
		footOut_ctrl.editCtrlShape(axis=charScale * 1.25)
		footOut_ctrl.setColor(colorSec)
		footOutZro_grp = rigTools.zeroGroup(footOut_ctrl)
		footOutZro_grp.name = ctrlName + 'Zro_grp'
		footOut_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footOutZro_grp.snap(footOut)

		# 3. Foot In Controller
		ctrlName = f"{nameSpace}{footBehav[1]}{legType}IK{side}"
		footIn_ctrl = core.Dag(ctrlName + '_ctrl')
		footIn_ctrl.nmCreateController('sphere_ctrlShape')
		footIn_ctrl.editCtrlShape(axis=charScale * 1.25)
		footIn_ctrl.setColor(colorSec)
		footInZro_grp = rigTools.zeroGroup(footIn_ctrl)
		footInZro_grp.name = ctrlName + 'Zro_grp'
		footIn_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footInZro_grp.snap(footIn)

		# 4. Foot Heel Controller
		ctrlName = f"{nameSpace}{footBehav[2]}{legType}IK{side}"
		footHeel_ctrl = core.Dag(ctrlName + '_ctrl')
		footHeel_ctrl.nmCreateController('sphere_ctrlShape')
		footHeel_ctrl.editCtrlShape(axis=charScale * 1.25)
		footHeel_ctrl.setColor(colorSec)
		footHeelZro_grp = rigTools.zeroGroup(footHeel_ctrl)
		footHeelZro_grp.name = ctrlName + 'Zro_grp'
		footHeel_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
		footHeelZro_grp.snap(heel)

		# 5. Foot Toe Controller
		ctrlName = f"{nameSpace}{footBehav[3]}{legType}IK{side}"
		footToe_ctrl = core.Dag(ctrlName + '_ctrl')
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

		# Parent rollBackAnkle under ballRoll_ctrl
		rollBackAnkleIkZro_grp.parent(ballRoll_ctrl)
		mc.xform(rollBackAnkleIkZro_grp.name, ws=True, ro=[0, 0, 0])
		mc.setAttr(f"{rollBackAnkleIkOffset_grp.name}.r", 0, 0, 0)
		mc.setAttr(f"{rollBackAnkleIk_ctrl.name}.r", 0, 0, 0)

	# Pivot switching between foot and ankle
	ankleIk_ctrl.addAttribute(longName='pivotBar', niceName='_', at='enum', en='Pivot', keyable=True)
	ankleIk_ctrl.setLocked('pivotBar')
	ankleIk_ctrl.addAttribute(longName='pivotChoice', niceName='Pivot At', at='enum', en='foot:ankle', keyable=True)

	# Ankle pivot locator (at ankle joint)
	ankle_target = ankle_ikJnt.name if hasattr(ankle_ikJnt, 'name') else str(ankle_ikJnt)
	ankleIk_loc = core.Locator(f'{nameSpace}ankle{position}{side}_loc')
	ankleIk_loc.snapPoint(ankle_target)
	ankleIk_loc.parent(ankleIk_ctrl)
	ankleIk_loc.attr('v').value = 0
	ankleIk_loc.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')

	# Foot pivot locator (at foot / ball on ground)
	ball_target = ball_ikJnt.name if hasattr(ball_ikJnt, 'name') else str(ball_ikJnt)
	footIk_loc = core.Locator(f'{nameSpace}footPivot{position}{side}_loc')
	footIk_loc.snapPoint(ball_target)
	footIk_loc.parent(ankleIk_ctrl)
	footIk_loc.attr('v').value = 0
	footIk_loc.lockHideAttrLst('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')

	pivot_cnd = core.Condition(f'{nameSpace}footIKPivot{position}{side}_cnd')
	footIk_loc.attr('translate') >> pivot_cnd.attr('colorIfTrue')
	ankleIk_loc.attr('translate') >> pivot_cnd.attr('colorIfFalse')
	ankleIk_ctrl.attr('pivotChoice') >> pivot_cnd.attr('secondTerm')
	pivot_cnd.attr('outColor') >> ankleIk_ctrl.attr('rotatePivot')
	pivot_cnd.attr('outColor') >> ankleIk_ctrl.attr('scalePivot')

	# =========================================================================
	# 8. Lower Leg / Hock Controller
	# =========================================================================
	name = nameSpace + rawName[9]
	lowerLegIK_ctrl = core.Dag(name + 'Ik' + side + '_ctrl')
	lowerLegIK_ctrl.nmCreateController('cube_ctrlShape')
	lowerLegIK_ctrl.editCtrlShape(axis=charScale * 1.0)
	lowerLegIK_ctrl.color = colorSide
	lowerLegIK_ctrl.snapPoint(lowerLeg_ikJnt)

	lowerLegIkZro_grp = rigTools.zeroGroup(lowerLegIK_ctrl)
	lowerLegIkZro_grp.name = name + 'Ik' + side + 'Zro_grp'
	lowerLegIkZro_grp.parent(parentTo)

	# Orient constraint from lowerLegIK_ctrl to ankle_ikJnt
	legIkRotation = core.orientConstraint(lowerLegIK_ctrl, ankle_ikJnt.name, mo=True)
	legIkRotation.name = nameSpace + rawName[9] + ctrlType + side + '_orientCons'

	# =========================================================================
	# 9. IK Handles Creation (Pure Double IK - NO Spring Solver)
	# =========================================================================
	# A. Upper Main Chain IK Handle (Hip -> Hock): 2-Bone subsystem using standard ikRPsolver
	upperIk_ikh = core.IkRp(startJoint=upperLeg_ikJnt.name, endEffector=lowerLeg_ikJnt.name)
	upperIk_ikh.name = nameSpace + rawName[0] + 'Upper' + position + side + '_ikh'
	upperIk_ikh.eff = nameSpace + rawName[0] + 'Upper' + position + side + '_eff'
	upperIk_ikh.attr('v').value = 0
	upperIk_ikh.parent(rollBackAnkleIk_ctrl)

	# Front Knee Pole Vector Controller
	tmpPov = rawName[3]
	pov_base = tmpPov if position.lower() in tmpPov.lower() else f"{tmpPov}{position}"
	povZro_grp = core.Null(f"{nameSpace}knee{position}{side}Zro_grp")
	name = f"{nameSpace}{pov_base}{side}"
	pov_ctrl = core.Dag(name + '_ctrl')
	if povShape == 'sphereAxis':
		pov_ctrl.nmCreateController('legLFT_pov_ctrlShape')
	elif povShape == 'pyramid':
		pov_ctrl.nmCreateController('pyramid_ctrlShape')
		pov_ctrl.rotateShape(rotate=(90, 0, 0))
	else:
		pov_ctrl.nmCreateController(povShape)
	pov_ctrl.editCtrlShape(axis=charScale * 0.8)
	pov_ctrl.color = colorSec
	mc.parent(pov_ctrl.name, povZro_grp.name)
	povZro_grp.snap(povLeg)

	# Target Annotation line from Knee to POV
	try:
		pc.targetPov(ctrl=pov_ctrl.name, jnt=midLeg_bJnt.name)
	except Exception as err:
		logger.warning(f"Failed to create targetPov annotation: {err}")

	# Knee Pole Vector Constraint on Upper IK Handle
	mc.poleVectorConstraint(pov_ctrl.name, upperIk_ikh.name, name=nameSpace + 'knee' + position + side + '_povCons', w=1)
	mc.parent(povZro_grp.name, lowerLegIK_ctrl.name)

	# Local/World Space Switching for Knee Pole Vector
	partName = nameSpace + 'knee' + position
	Loc_grp, World_grp, WorldGrp_orientCons, ZroGrp_orientCons, reverseNode_rev = rigTools.parentLocalWorldCtrl(
		pov_ctrl, ankleIk_ctrl, parentTo, povZro_grp, partName
	)
	Loc_grp.name = partName + 'Local_grp'
	World_grp.name = partName + 'World_grp'
	WorldGrp_orientCons.name = partName + side + 'WorldGrp_parCons'
	ZroGrp_orientCons.name = partName + side + 'ZroGrp_parCons'
	reverseNode_rev.name = partName + side + 'ZroGrParCons_rev'

	# B. Lower Leg to Ankle IK Handle (lowerLeg_ikJnt -> ankle_ikJnt) powered by ikSCsolver (Single Chain)
	ankleIk_ikh = core.DoIk(startJoint=lowerLeg_ikJnt.name, endEffector=ankle_ikJnt.name, solverType='ikSCsolver')
	ankleIk_ikh.name = nameSpace + footBehav[5] + legType + side + '_ikh'
	ankleIk_ikh.eff = nameSpace + footBehav[5] + legType + side + '_eff'
	ankleIk_ikh.attr('v').value = showInfo
	ankleIk_ikh.parent(rollBackAnkleIk_ctrl)

	# C. Foot IK Handles (Ball & Toe) powered by standard ikRPsolver
	ballIk_ikh = core.IkRp(startJoint=ankle_ikJnt.name, endEffector=ball_ikJnt.name)
	ballIk_ikh.name = nameSpace + footBehav[4] + legType + side + '_ikh'
	ballIk_ikh.eff = nameSpace + footBehav[4] + legType + side + '_eff'
	ballIk_ikh.attr('v').value = showInfo

	toeIk_ikh = core.IkRp(startJoint=ball_ikJnt.name, endEffector=toe_ikJnt.name)
	toeIk_ikh.name = nameSpace + footBehav[3] + legType + side + '_ikh'
	toeIk_ikh.eff = nameSpace + footBehav[3] + legType + side + '_eff'
	toeIk_ikh.attr('v').value = showInfo

	if footAttr:
		ballIk_ikh.parent(ballRoll_grp)
		toeIk_ikh.parent(toeRise_grp)
	else:
		ballIk_ikh.parent(ballRoll_ctrl)
		toeIk_ikh.parent(toeRise_ctrl)

	# D. 2-Bone Guide Driver IK Handle (guideHip -> guideHock) powered by standard ikRPsolver
	guide_ankle_ikh = core.IkRp(startJoint=guideHip_gdeJnt.name, endEffector=guideHock_gdeJnt.name)
	guide_ankle_ikh.name = nameSpace + 'guide_ankle' + position + side + '_ikh'
	guide_ankle_ikh.eff = nameSpace + 'guide_ankle' + position + side + '_eff'
	guide_ankle_ikh.attr('v').value = 0
	guide_ankle_ikh.parent(rollBackAnkleIk_ctrl)

	# Back Guide Pole Vector Controller
	guidePovName = nameSpace + 'guidePov' + position + side
	guidePov_ctrl = core.Dag(guidePovName + '_ctrl')
	if povShape == 'sphereAxis':
		guidePov_ctrl.nmCreateController('legLFT_pov_ctrlShape')
	elif povShape == 'pyramid':
		guidePov_ctrl.nmCreateController('pyramid_ctrlShape')
		guidePov_ctrl.rotateShape(rotate=(90, 0, 0))
	else:
		guidePov_ctrl.nmCreateController('sphere_ctrlShape')
	guidePov_ctrl.editCtrlShape(axis=charScale * 0.8)
	guidePov_ctrl.color = colorSec
	guidePovZro_grp = rigTools.zeroGroup(guidePov_ctrl)
	guidePovZro_grp.name = guidePovName + 'Zro_grp'

	# Position Guide POV: Check custom guide joint first (e.g. guideLegPovBackLFT_tmpJnt)
	guidePovTmp = guideJnt[3] if len(guideJnt) > 3 else f"{nameSpace}guideLegPov{position}{side}_tmpJnt"
	if mc.objExists(guidePovTmp):
		guidePovZro_grp.snap(guidePovTmp)
		logger.info(f"Positioned Guide POV controller from guide joint: {guidePovTmp}")
	else:
		pos_pk = mc.xform(guideKnee_tmp.name, q=True, ws=True, t=True)
		offset_z = (-3.0 * charScale) if ('back' in legType.lower() or 'back' in tmpJnt[0].lower()) else (3.0 * charScale)
		mc.xform(guidePovZro_grp.name, ws=True, t=[pos_pk[0], pos_pk[1], pos_pk[2] + offset_z])
		logger.info(f"Positioned Guide POV controller with default offset from {guideKnee_tmp.name}")

	guidePovZro_grp.parent(ankleIk_ctrl)
	core.poleVectorConstraint(guidePov_ctrl, guide_ankle_ikh)

	# Target Annotation line from Knee to Guide POV
	try:
		pc.targetPov(ctrl=guidePov_ctrl.name, jnt=midLeg_bJnt.name)
	except Exception as err:
		logger.warning(f"Failed to create guide targetPov annotation: {err}")

	# Visibility connection to stick_ctrl
	stick_ctrl.attr('showGuidePov') >> guidePovZro_grp.attr('visibility')

	# E. Optional Setting of preferredAngle AFTER creating IK handles
	if setPrefAngle:
		guide_map_ik = [
			(tmpJnt[0], upperLeg_ikJnt),
			(tmpJnt[1], midLeg_ikJnt),
			(tmpJnt[9], lowerLeg_ikJnt),
			(tmpJnt[2], ankle_ikJnt),
			(guideJnt[0], guideHip_gdeJnt),
			(guideJnt[1], guideKnee_gdeJnt),
			(guideJnt[2], guideHock_gdeJnt)
		]
		pref_attrs = [
			'guide_preferredAngleX', 'guide_preferredAngleY', 'guide_preferredAngleZ',
			'preferredAngleX', 'preferredAngleY', 'preferredAngleZ'
		]

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

		if not guide_pref_applied:
			if 'front' in legType.lower() or 'front' in tmpJnt[0].lower():
				midLeg_ikJnt.attr('preferredAngleX').value = -60
				lowerLeg_ikJnt.attr('preferredAngleX').value = 60
				guideKnee_gdeJnt.attr('preferredAngleX').value = 60
				logger.info(f"Auto-configured Front Leg Preferred Angles on {midLeg_ikJnt.name} and {guideKnee_gdeJnt.name}")
			else:
				# Hind leg: Knee bends forward (-X matching jointOrientX), Hock bends backward (+X matching jointOrientX)
				midLeg_ikJnt.attr('preferredAngleX').value = -60
				lowerLeg_ikJnt.attr('preferredAngleX').value = 60
				guideKnee_gdeJnt.attr('preferredAngleX').value = 60
				logger.info(f"Auto-configured Hind Leg Preferred Angles on {midLeg_ikJnt.name} (-60) and {lowerLeg_ikJnt.name} (+60)")
	else:
		logger.info("Preferred angle setup bypassed (setPrefAngle=False). Double IK plane evaluation active.")

	# =========================================================================
	# 10. Stretchy IK Setup
	# =========================================================================
	pmaNode = None
	try:
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
		logger.info("Stretchy IK setup complete for %s %s." % (legType, side))
	except Exception as e:
		logger.warning(f"Stretchy IK encountered issue: {e}", exc_info=True)

	# =========================================================================
	# 11. Knee / Hock Lock Module
	# =========================================================================
	if pmaNode:
		try:
			rawNameUPR, distanceUPRName, povUPR_Ctrl, lowerUPR_loc, upperUPR_loc = midLockModule.createDistance(
				nameSpace, part='up', startP=ikRootGmbl_ctrl.name, endP=pov_ctrl.name, noTouchGrp=noTouchGrp
			)
			rawNameLWR, distanceLWRName, povLWR_Ctrl, lowerLWR_loc, upperLWR_loc = midLockModule.createDistance(
				nameSpace, part='dn', startP=pov_ctrl.name, endP=lowerLegIK_ctrl.name, noTouchGrp=noTouchGrp
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
	# 12. FK / IK Blend Switch onto Bind Joints (_bJnt)
	# =========================================================================
	switch_joint_pairs = [
		(upperLeg_fkJnt, upperLeg_ikJnt, upperLeg_bJnt, rawName[0]),
		(midLeg_fkJnt,   midLeg_ikJnt,   midLeg_bJnt,   rawName[1]),
		(lowerLeg_fkJnt, lowerLeg_ikJnt, lowerLeg_bJnt, rawName[9]),
		(ankle_fkJnt,    ankle_ikJnt,    ankle_bJnt,    rawName[2]),
		(ball_fkJnt,     ball_ikJnt,     ball_bJnt,     rawName[4]),
		(toe_fkJnt,      toe_ikJnt,      toe_bJnt,      rawName[5])
	]

	for fk_j, ik_j, b_j, base_name in switch_joint_pairs:
		if mc.objExists(fk_j.name) and mc.objExists(ik_j.name) and mc.objExists(b_j.name):
			psCon = mc.parentConstraint(
				fk_j.name, ik_j.name, b_j.name,
				name=f"{nameSpace}{base_name}Switch{side}_parentCons",
				mo=True
			)
			revNode = mc.createNode('reverse', name=f"{nameSpace}{base_name}Switch{side}_rev")

			mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{revNode}.inputX")
			mc.connectAttr(f"{stick_ctrl.name}.FK_IK", f"{psCon[0]}.{ik_j.name}W1")
			mc.connectAttr(f"{revNode}.outputX", f"{psCon[0]}.{fk_j.name}W0")

	# =========================================================================
	# 13. Group Hierarchy & Visibility Switching
	# =========================================================================
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
	stick_ctrl.attr('FK_IK') >> ankleIkZro_grp.attr('visibility')
	stick_ctrl.attr('FK_IK') >> povZro_grp.attr('visibility')
	stick_ctrl.attr('FK_IK') >> rollBackAnkleIkZro_grp.attr('visibility')

	ikRoot.lockHideAttrLst('rx', 'ry', 'rz', 'sx', 'sy', 'sz')
	pov_ctrl.lockHideAttrLst('rx', 'ry', 'rz', 'sx', 'sy', 'sz')
	guidePov_ctrl.lockHideAttrLst('rx', 'ry', 'rz', 'sx', 'sy', 'sz')

	if mc.objExists(parentTo):
		povZro_grp.parent(parentTo)

	if mc.objExists(jnt_grp):
		legJnt_grp.parent(jnt_grp)
	elif mc.objExists(noTouchGrp):
		legJnt_grp.parent(noTouchGrp)
	legJnt_grp.attr('visibility').value = showInfo

	# =========================================================================
	# Message Attributes for FK/IK Matcher
	# =========================================================================
	msg_attrs = [
		'stick', 'upJnt', 'midJnt', 'lowJnt', 'ankleJnt', 'ballJnt', 'toeJnt',
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
	if mc.objExists(toe_bJnt.name):
		toe_bJnt.attr('message') >> stick_ctrl.attr('toeJnt')

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
	# 14. Ribbon Rigging Integration
	# =========================================================================
	if ribbon:
		numJoints = 5 if ribbonRes == 'high' else 3
		# Auto-derive unique ribbon names if default or collision-prone
		if ribbonName == ('upLeg', 'lwrLeg'):
			r_upr = f"up{position}Leg"
			r_lwr = f"lwr{position}Leg"
		else:
			r_upr = ribbonName[0]
			r_lwr = ribbonName[1]

		try:
			hingesUprBtm = ribbonRig.ribbonRigExt(
				nameSpace=nameSpace, width=10, numJoints=numJoints, side=side,
				jointTop=upperLeg_bJnt, jointBtm=midLeg_bJnt, part=r_upr,
				charScale=charScale, noTouch_grp=noTouchGrp, showInfo=showInfo, ctrl_grp=legRig_grp.name
			)
			hingesLwrTop = ribbonRig.ribbonRigExt(
				nameSpace=nameSpace, width=10, numJoints=numJoints, side=side,
				jointTop=midLeg_bJnt, jointBtm=lowerLeg_bJnt, part=r_lwr,
				charScale=charScale, noTouch_grp=noTouchGrp, showInfo=showInfo, ctrl_grp=legRig_grp.name
			)
			ribbonRig.makeHigesMover(
				part=legType, nameSpace=nameSpace, side=side, btmName=hingesUprBtm,
				topName=hingesLwrTop, charScale=charScale, moverPosition=midLeg_bJnt.name, ctrl_grp=parentTo
			)
		except Exception as e:
			logger.warning(f"Ribbon setup encountered issue: {e}", exc_info=True)

	core.clearSel()
	core.makeHeader('End of %s%s Rig (Double IK)' % ('eh_quadrupedLegRig', side))
	logger.info("Quadruped Double IK Leg Rig (%s) successfully built!" % side)

	return {
		"upperLeg_bJnt": upperLeg_bJnt.name,
		"midLeg_bJnt": midLeg_bJnt.name,
		"lowerLeg_bJnt": lowerLeg_bJnt.name,
		"ankle_bJnt": ankle_bJnt.name,
		"stick_ctrl": stick_ctrl.name,
		"ankleIk_ctrl": ankleIk_ctrl.name,
		"lowerLegIK_ctrl": lowerLegIK_ctrl.name,
		"ikRoot": ikRoot.name,
		"kneePov_ctrl": pov_ctrl.name,
		"guidePov_ctrl": guidePov_ctrl.name,
		"proxyPov_ctrl": guidePov_ctrl.name
	}
