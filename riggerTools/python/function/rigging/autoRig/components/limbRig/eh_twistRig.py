# -*- coding: utf-8 -*-
from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.base import core
reload(core)
from function.rigging.autoRig.base import rigTools
reload(rigTools)
import maya.cmds as mc
from function.rigging.util import misc
reload(misc)
from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

def twistRigAuto(nameSpace='', parent_jnt='upperLegLFT_bJnt', child_jnt='lowerLegLFT_bJnt', 
				 fk_shoulderCtrl='upperArmFkLFT_ctrl', ik_shoulderCtrl='upperArmIkRootLFT_ctrl',
				 side='LFT', region='leg', priorJnt='handStickLFT_ctrl', stick_ctrl='', 
				 charScale=1.0, showInfo=True, alongAxis='y'):
	"""
	Create single joint at the same position of shoulder or thigh that ignore rotation y (twist)
	matrixConstraint version.
	"""
	core.makeHeader(f'Start of twistRigAuto {side}')

	region = region.capitalize() 
	shoulder_jnt = core.Dag(parent_jnt)
	elbow_jnt = core.Dag(child_jnt)

	# Find distance between shoulder to elbow
	if alongAxis == 'y':
		length = elbow_jnt.attr('translateY').value 
	elif alongAxis == 'x':
		length = elbow_jnt.attr('translateX').value 

	# Divide half
	length = length / 2

	# Change value by side
	if side == 'LFT' and alongAxis == 'y':
		i = 1
		aimVec = (0, 1, 0)
		upVec = (0, 0, -1)
	elif side == 'RGT' and alongAxis == 'y':
		i = -1
		aimVec = (0, -1, 0)
		upVec = (0, 0, 1)
	elif side == 'LFT' and alongAxis == 'x':
		i = 1
		aimVec = (1, 0, 0)
		upVec = (0, -1, 0)
	elif side == 'RGT' and alongAxis == 'x':
		i = -1
		aimVec = (-1, 0, 0)
		upVec = (0, 1, 0)

	upperTwist01_jnt = core.Joint()
	upperTwist01_jnt.name = f"{nameSpace}upper{region}Twist01{side}_twJnt"
	twistShapeJnt = core.Locator('tmpName')
	# Swap shape node of locator to joint 
	mc.parent(twistShapeJnt.shape, upperTwist01_jnt.name, s=True, r=True)
	mc.rename(f"{twistShapeJnt.name}Shape", f"{upperTwist01_jnt.name}Shape")
	mc.delete(twistShapeJnt.name)
	upperTwist01_jnt.setOutlineColor('white')
	upperTwist01_jnt.setJointColor('white')

	upperTwist02_jnt = core.Joint()
	upperTwist02_jnt.name = f"{nameSpace}upper{region}Twist02{side}_twJnt"
	twistShapeJnt = core.Locator('tmpName')
	# Swap shape node of locator to joint 
	mc.parent(twistShapeJnt.shape, upperTwist02_jnt.name, s=True, r=True)
	mc.rename(f"{twistShapeJnt.name}Shape", f"{upperTwist02_jnt.name}Shape")
	mc.delete(twistShapeJnt.name)
	upperTwist02_jnt.setOutlineColor('white')
	upperTwist02_jnt.setJointColor('white')

	upperTwist01_jnt.maSnap(parent_jnt)

	# make it forward a bit
	if alongAxis == 'y':
		mc.move(0, i * 0.0125, 0, upperTwist01_jnt.name, relative=True, objectSpace=True, worldSpaceDistance=True)
	elif alongAxis == 'x':
		mc.move(i * 0.0125, 0, 0, upperTwist01_jnt.name, relative=True, objectSpace=True, worldSpaceDistance=True)

	upperTwist01_jnt.freeze()

	upperTwist02_jnt.maSnap(upperTwist01_jnt)
	upperTwist02_jnt.parent(upperTwist01_jnt)

	upperTwist01_jnt.parent(shoulder_jnt)

	upperTwist02_jnt.freeze()
	if alongAxis == 'y':
		upperTwist02_jnt.attr('translateY').value = length
	elif alongAxis == 'x':
		upperTwist02_jnt.attr('translateX').value = length

	upperTwist01_jnt.attr('radius').value = charScale * 4

	upperTwist01_jnt.attr('localScaleX').value = charScale * 0.1
	upperTwist01_jnt.attr('localScaleY').value = charScale * 0.1
	upperTwist01_jnt.attr('localScaleZ').value = charScale * 0.1

	upperTwist02_jnt.attr('localScaleX').value = charScale * 0.1
	upperTwist02_jnt.attr('localScaleY').value = charScale * 0.1
	upperTwist02_jnt.attr('localScaleZ').value = charScale * 0.1

	# Create locator for guide upVector
	upVectorGuide_loc = core.Locator(f"{nameSpace}upper{region}AimUp{side}_loc")
	upVectorGuide_loc.maSnap(upperTwist01_jnt)

	if alongAxis == 'y':
		MOVE_POSITION = (0, 0, length * -1 * 1.25)
		MOVE_UPVEC = (0, 0, length * -1 * 2.5)
	elif alongAxis == 'x':
		MOVE_POSITION = (0, length * -1 * 1.25, 0)
		MOVE_UPVEC = (0, length * -1 * 2.5, 0)

	# Move Guide
	upVectorGuide_loc.moveObj(position=MOVE_UPVEC)
	upVectorGuide_loc.setColor('white')

	# --- Native Aim Constraint (from original twistRig.py) ---
	twist_aimCons = core.aimConstraint(
		child_jnt,
		upperTwist01_jnt.name,
		aimVector=aimVec,
		mo=False,
		upVector=upVec,
		worldUpType="object",
		worldUpObject=upVectorGuide_loc.name
	)
	twist_aimCons.name = f"{nameSpace}upper{region}Twist01{side}_aimCons"

	# create following joint 
	upperFollow01_jnt = rigTools.jointAt(upperTwist01_jnt)
	upperFollow01_jnt.name = f"{nameSpace}upper{region}Follow01{side}_twJnt"
	upperFollow01_jnt.moveObj(position=MOVE_POSITION)
	upperFollow01_jnt.setJointColor('white')

	upperFollow01_jnt.freeze()

	upperFollow02_jnt = rigTools.jointAt(upperTwist02_jnt)
	upperFollow02_jnt.name = f"{nameSpace}upper{region}Follow02{side}_twJnt"
	upperFollow02_jnt.moveObj(position=MOVE_POSITION)
	upperFollow02_jnt.setJointColor('white')
	upperFollow02_jnt.parent(upperFollow01_jnt)

	upVectorGuide_loc.parent(upperFollow01_jnt)

	upVectorGuide_loc.attr('localScaleX').value = charScale * 0.1
	upVectorGuide_loc.attr('localScaleY').value = charScale * 0.1
	upVectorGuide_loc.attr('localScaleZ').value = charScale * 0.1

	# twistAim_ikh
	twistAim_ikh = core.DoIk(startJoint=upperFollow01_jnt, endEffector=upperFollow02_jnt, solverType='ikRPsolver')
	twistAim_ikh.name = f"{nameSpace}upper{region}Follow{side}_ikh"

	twistAim_ikh.parent(child_jnt)
	twistAim_ikh.maSnap(child_jnt)

	# reset value for enable twist effect proper
	twistAim_ikh.attr('poleVectorX').value = 0
	twistAim_ikh.attr('poleVectorY').value = 0
	twistAim_ikh.attr('poleVectorZ').value = 0

	# Manipulate Enable and attr value function
	fk_shoulder_ctrl = core.Dag(fk_shoulderCtrl)
	ik_shoulder_ctrl = core.Dag(ik_shoulderCtrl)

	# Enable / Disable twist option (Weight of Aim Constraint)
	if not mc.attributeQuery(f'{region}Twist', node=fk_shoulder_ctrl.name, exists=True):
		fk_shoulder_ctrl.addAttribute(attributeType='bool', longName=f'{region}Twist', min=0, max=1, defaultValue=1, keyable=True)

	weight_aliases = mc.aimConstraint(twist_aimCons.name, q=True, weightAliasList=True)
	if weight_aliases:
		mc.connectAttr(f"{fk_shoulder_ctrl.name}.{region}Twist", f"{twist_aimCons.name}.{weight_aliases[0]}", f=True)
	else:
		clean_child = child_jnt.split('|')[-1].split(':')[-1]
		if mc.objExists(f"{twist_aimCons.name}.{clean_child}W0"):
			mc.connectAttr(f"{fk_shoulder_ctrl.name}.{region}Twist", f"{twist_aimCons.name}.{clean_child}W0", f=True)

	# bypass twist value to fk
	if not mc.attributeQuery(f'{region}FkTwist', node=fk_shoulder_ctrl.name, exists=True):
		fk_shoulder_ctrl.addAttribute(longName=f'{region}FkTwist', defaultValue=0, keyable=True)
	
	fk_invertVal_mdl = core.MDLWithMul(f'{nameSpace}{region}FkInVal{side}')
	fk_invertVal_mdl.attr('multiply').value = i * 0.5
	fk_shoulder_ctrl.attr(f'{region}FkTwist') >> fk_invertVal_mdl.attr('input1')

	# bypass twist value to ik
	if not mc.attributeQuery(f'{region}IkTwist', node=ik_shoulder_ctrl.name, exists=True):
		ik_shoulder_ctrl.addAttribute(longName=f'{region}IkTwist', defaultValue=0, keyable=True)
	
	ik_invertVal_mdl = core.MDLWithMul(f'{nameSpace}{region}InVal{side}Ik')
	ik_invertVal_mdl.attr('multiply').value = i * 0.5
	ik_shoulder_ctrl.attr(f'{region}IkTwist') >> ik_invertVal_mdl.attr('input1')

	limbSwitch_ctrl = core.Dag(stick_ctrl)

	# create condition for plug that two line together
	shoulder_con = core.Condition(f'{nameSpace}{region}Twist{side}_con')
	if mc.objExists(f"{limbSwitch_ctrl.name}.FK_IK"):
		limbSwitch_ctrl.attr('FK_IK') >> shoulder_con.attr('firstTerm')
	fk_invertVal_mdl.attr('output') >> shoulder_con.attr('colorIfTrueR')
	ik_invertVal_mdl.attr('output') >> shoulder_con.attr('colorIfFalseR')

	# make upVec translatable via attr
	shoulder_con.attr('outColorR') >> upVectorGuide_loc.attr('tx')

	# Parent constraint the follow upper jnt (humerus) for follow as the rest of the body joint
	# create null grp
	follow_grp = core.Null(f"{nameSpace}upper{region}Follow{side}_grp")
	upperFollow01_jnt.parent(follow_grp)

	followGrp_parCons = core.parentConstraint(priorJnt, follow_grp, mo=True)
	followGrp_parCons.name = f"{nameSpace}upper{region}Follow{side}_psCons"
	followGrp_scalCons = core.scaleConstraint(priorJnt, follow_grp, mo=True)
	followGrp_scalCons.name = f"{nameSpace}upper{region}Follow{side}_scalCons"

	if not showInfo:
		upperFollow01_jnt.attr('visibility').value = 0

	misc.makeHeader(f"{nameSpace}twistRigAuto {region}{side} Complete")

	return follow_grp.name, upperTwist01_jnt.name