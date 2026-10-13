"""
================================================================================
Snake / Tentacle Auto Rigger (Spline IK + FK + Sine Deformer)
================================================================================

EXECUTION ORDER (How to use this module):
--------------------------------------------------------------------------------
Step 1: snakeRigFk_Ik_Deform(...)
    - Runs the core rig generation.
    - Creates the FK chain, Spline IK chain, and Deformers (Sine, Squash).
    - Generates detail joints bound to the NURBS surface.

Step 2: Skinning / Paint Weights (Manual)
    - Bind your mesh to the detail joints (e.g., spineBCK_detail01_bJnt ... 24).

Step 3: setup_slide_hierarchy(...)
    - REQUIRED for the 'Snake Slide Path' UI tool.
    - Run this after the main rig is generated.
    - It creates the Snap (_SN) and Parent Handle (_PH) hierarchy wrappers around 
      the master FK controllers and registers them to `rig_grp.slide_ctrls`.
================================================================================
"""

#... Fk first and then Ik and then Deformer
#... IK spine Rig for tentacle make deformer before Ik spine
#... make stretchy by using arcLength
#... increase detail joint to 24
#... make sin wave for tail
#... TODO collect ikh name to stick
#... [ATTENTION !!! ] Need to paintweight deformer and normal state after finish

import maya.cmds as mc
import maya.api.OpenMaya as om
import pymel.core as pm
import json
from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.addRig import createFkRig
reload(createFkRig)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.controllerBox import adjustController as adjust
reload(adjust)

from function.rigging.de_boor import hh_de_boor_to_curve as hh
reload(hh)

from function.rigging.constraint import pinLocatorToSurface as pls
reload(pls)

from function.rigging.de_boor import hh_de_boor_to_mesh as hm
reload(hm)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.rigging.util import generic_maya_dict as gmd
reload(gmd)

import logging
from function.pipeline import logger 
reload(logger)

class TentacleRig(logger.MayaLogger):
	LOGGER_NAME = "TentacleRig"

TentacleRig.set_level(logging.DEBUG)


def snakeRigFk_Ik_Deform(
	SIDE='',
	BASE_NAME='spineBCK',
	SCALE=20,
	COUNT_DETAIL=24,
	COUNT_MAIN=6,
	stickShape='stickCircle_Y_long_ctrlShape',
	mesh='serpent_ply',
	smoothCrv=False,
	smoothweight=False,
	sineDef=False,
	squashDef=False,
	priorJnt='hip_bJnt',
	parentTo='hip_gmbCtrl',
	place_ctrl='placement_ctrl',
	enableTwist=True,
	worldUpType='Object Up',
	twistValueType='Start/End',
	twistEnd=1.0,
	twistStart=0.0,
	forwardAxis='z-',
	worldUpAxis='y+',
	worldUpVector=(0, 0, 1),
	worldUpVectorEnd=(0, 0, 1),
	upObject='upFRTObj_crv',
	upObjectEnd='upBCKObj_crv'):
	"""
	Procedural Snake / Tentacle AutoRig with FK/IK Deformer, Spline IK, Sine Deformer, and Stretch.
	Supports string arguments for twist setup (e.g. worldUpType='Object Up', twistValueType='Start/End').
	"""

	#... Create Null grp
	if mc.objExists(priorJnt):
		pass
	else:
		core.Joint('root')

	if SIDE == '':
		COMP_BASE_NAME = BASE_NAME
	else:
		COMP_BASE_NAME = f'{SIDE}_{BASE_NAME}'

	#... Create Null grp
	nurbAll_grp = core.Null(f'{COMP_BASE_NAME}AllNurbe_grp')
	nurbAll_grp.lockAllAttr(attrs=['t', 'r', 's'])

	ik_detail_joints = core.generate_named_pattern(f'{COMP_BASE_NAME}##_ikJnt', COUNT_DETAIL)
	spine_crv = f'{COMP_BASE_NAME}_ikSpine_crv'
	ik_nrb = f'{COMP_BASE_NAME}_ik_nrb'
	ik_nrb_shape = mc.listRelatives(ik_nrb, shapes=True)[0]

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Make FK controller
	core.makeHeader('Make FK controller')

	ik_joints = core.generate_named_pattern(f'{COMP_BASE_NAME}##_masterIk_ikJnt', COUNT_DETAIL)
	bJnts_list = []

	for num in range(0, COUNT_MAIN):
		print(num)
		print(ik_joints[num])
		ik_jnt = core.Dag(ik_joints[num])
		fk_jnt = core.Joint(ik_joints[num].replace('masterIk_ikJnt', 'masterFk_fkJnt'))
		fk_jnt.maSnap(ik_jnt)
		fk_jnt.attr('radius').value = 2
		fk_jnt.setJointColor('gray')
		bJnts_list.append(fk_jnt.name)

	#... parent to hierarchy
	for num in range(0, COUNT_MAIN):
		print(num)
		if num != 0:
			mc.parent(bJnts_list[num], bJnts_list[num-1])

	fk_rig = createFkRig.fkRig_omni_newCurl(
		nameSpace='',
		parentCtrlTo='',
		jntLst=bJnts_list,
		charScale=1 * SCALE,
		priorJnt='',
		side=SIDE,
		ctrlShape='ring_ctrlShape',
		localWorld=False,
		color='yellow',
		curlCtrl=True,
		curlPosiAtFirst=False,
		rotateOrder='zxy',
		parentToPriorJnt=False,
		parentMatrix=False,
		curlCtrlShape=stickShape
	)

	TentacleRig.debug(f'{fk_rig[5]}')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ..................  create IK spine controller
	joints = core.generate_named_pattern(f'{COMP_BASE_NAME}##_masterIk_ikJnt', COUNT_MAIN)

	main_ik_ctrl = adjust.creControllerFunc(
		selected=joints,
		scale=5 * SCALE,
		ctrlShape='cube_ctrlShape',
		color='yellow',
		constraint=True,
		matrixConst=False,
		mo=False,
		translate=True,
		rotate=True,
		scaleConstraint=True,
		rotateOrder='xzy',
		parentUnder=False
	)

	master_ik_zroGrp = core.generate_named_pattern(f'{COMP_BASE_NAME}##_masterIkZro_grp', COUNT_MAIN)
	master_fk_gmbl = core.generate_named_pattern(f'{COMP_BASE_NAME}##_masterFk_gmbCtrl', COUNT_MAIN)
	for index, each in enumerate(master_fk_gmbl):
		mc.parent(master_ik_zroGrp[index], each)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. create Ik handle
	ik_detail_jnt = core.generate_named_pattern(f'{COMP_BASE_NAME}##_ikJnt', COUNT_DETAIL)

	ikHandle = core.DoIkSpline(
		startJoint=ik_detail_jnt[0],
		endEffector=ik_detail_jnt[-1],
		solverType='ikSplineSolver',
		createCurve=False,
		curveName=spine_crv,
		parentCurve=False
	)

	ikHandle.name = f'{COMP_BASE_NAME}_ikh'
	ikHandle.eff = f'{COMP_BASE_NAME}_eff'

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. skinweight joint to curve
	TentacleRig.info('\n#.................................... skinweight joint to curve')

	skin_name = f'{COMP_BASE_NAME}_ikCrv_skc'
	skin_cluster = mc.skinCluster(joints, spine_crv, toSelectedBones=True, name=skin_name)[0]

	if smoothCrv:
		jnts = hh.list_joints_from_skincluster(skin_name)
		hh.split_curve_cvs_with_de_boor_v4(jnts, spine_crv, degree=3, falloff_mode='linear', falloff_width=0.01)

	TentacleRig.info('#.................................... skinweight joint to ik_nrb curve for make match blendshape')

	joints = core.generate_named_pattern(f'{COMP_BASE_NAME}##_ikJnt', COUNT_DETAIL)

	skin_name = f'{COMP_BASE_NAME}_ikNrb_skc'
	skin_cluster = mc.skinCluster(joints, ik_nrb, toSelectedBones=True, name=skin_name)[0]

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Blendshape ik nurbe to combine nurbe
	combineFkIk_nrb = mc.duplicate(ik_nrb, n=ik_nrb.replace('ik', 'combineFkIk'))[0]
	mc.blendShape(ik_nrb, combineFkIk_nrb, frontOfChain=True, name=f'{COMP_BASE_NAME}_bsh', w=[(0, 1)])

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Create Detail Joint
	core.makeHeader('Create Detail Joint')
	ik_detail_jnt = core.generate_named_pattern(f'{COMP_BASE_NAME}##_ikJnt', COUNT_DETAIL)
	locs = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_loc', COUNT_DETAIL)

	for num in range(0, COUNT_DETAIL):
		print(locs[num])
		locator = core.Locator(locs[num])
		ik_jnt = core.Dag(ik_detail_jnt[num])
		locator.maSnap(ik_jnt)

	tenTail_resultDef_nrb_grp = pls.pin_locator_surface(
		nurbs=combineFkIk_nrb,
		region=f'{BASE_NAME}_combineFkik',
		side=SIDE,
		source_loc=locs,
		locator_scale=1 * SCALE,
		creJnt=True,
		suffixJnt='pxyJnt',
		creCtrl=True,
		ctrlShape='circle_Y_along_ctrlShape',
		snapAtEnd=False,
		priorJnt='',
		scale=20
	)

	#... parent joint under pin
	detail_gmbl_ctrl = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_gmbCtrl', COUNT_DETAIL)
	detail_jnt = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_pxyJnt', COUNT_DETAIL)

	for num in range(0, COUNT_DETAIL):
		mc.parent(detail_jnt[num], detail_gmbl_ctrl[num])

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Create bind joint from detail joint
	bind_jnt_list = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_bJnt', COUNT_DETAIL)
	for index, each in enumerate(bind_jnt_list):
		pxy_jnt = core.Dag(detail_jnt[index])
		bind_jnt = rigTools.jointAt(pxy_jnt)
		bind_jnt.attr('radius').value = 0.5
		bind_jnt.name = each

	#... parent to hierarchy
	for i in range(1, len(bind_jnt_list)):
		mc.parent(bind_jnt_list[i], bind_jnt_list[i-1])

	#... Skin bind joint to mesh
	skin_cluster = mc.skinCluster(bind_jnt_list, mesh, toSelectedBones=True, name=f'{COMP_BASE_NAME}{mesh}_skc')[0]

	jntPxy_list = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_pxyJnt', COUNT_DETAIL)

	if mc.objExists(priorJnt):
		mc.parent(bind_jnt_list[0], priorJnt)

		for index, each in enumerate(bind_jnt_list):
			print(f'parent {jntPxy_list[index]} and {each}')
			mtc.parentConMatrixGPT(jntPxy_list[index], each, mo=True, translate=True, rotate=True, scale=True)

	#... parent to grp
	detail_grp = core.Null(f'{COMP_BASE_NAME}_detailJnt_grp')
	detail_grp.lockAllAttr(attrs=['t', 'r', 's'])
	detail_loc = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_loc', COUNT_DETAIL)

	for each in detail_loc:
		mc.parent(each, detail_grp)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Split weight to mesh
	if smoothweight is True:
		spine_crv_dag = core.Dag(spine_crv)
		jnts = hh.list_joints_from_skincluster(skin_cluster)
		hm.split_with_curve_to_mesh_V2(mesh, jnts, spine_crv_dag.name, d=3, tol=0.1)
	elif smoothweight == 'reverse':
		spine_crv_dag = core.Dag(spine_crv)
		jnts = hh.list_joints_from_skincluster(skin_cluster)
		jnts = jnts[::-1]
		hm.split_with_curve_to_mesh_V2(mesh, jnts, spine_crv_dag.name, d=3, tol=0.1)
	else:
		TentacleRig.info('Do nothing pass.')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Make stretchy version 2
	stick_ctrl = core.Dag(fk_rig[5])
	stick_ctrlShape = core.Dag(stick_ctrl.shape)
	stick_ctrlShape.addAttribute(attributeType='float', longName='stretchy', minValue=0, maxValue=1, defaultValue=1, keyable=True)

	curveInfo = core.CurveInfo(f'{COMP_BASE_NAME}')
	spine_crv_dag = core.Dag(spine_crv)
	spine_crv_dag.attr('worldSpace[0]') >> curveInfo.attr('inputCurve')

	#... get length
	crv_length = curveInfo.attr('arcLength').value
	length_ratio_mdv = core.MultiplyDivineWithVal(f'{COMP_BASE_NAME}_length_ratio_mdv', 2)
	curveInfo.attr('arcLength') >> length_ratio_mdv.attr('input1X')
	length_ratio_mdv.attr('input2X').value = crv_length
	length_ratio_mdv.attr('input1Y').value = 1
	length_ratio_mdv.setLocked('input2X')
	length_ratio_mdv.setLocked('input1Y')
	length_ratio_mdv.setLocked('input2Y')

	length_store = core.MultiDoubleLinear(f'{COMP_BASE_NAME}_length_store')
	length_store.attr('input2').value = 1
	envelope_bta = core.BlendTwoAttr(f'{COMP_BASE_NAME}_length_store')
	length_ratio_mdv.attr('outputY') >> envelope_bta.attr('input[0]')
	length_ratio_mdv.attr('outputX') >> envelope_bta.attr('input[1]')
	envelope_bta.attr('output') >> length_store.attr('input1')

	minorIK_jnt_list = core.generate_named_pattern(f'{COMP_BASE_NAME}##_ikJnt', COUNT_DETAIL)

	for index, each in enumerate(minorIK_jnt_list):
		minorIK_jnt = core.Dag(each)
		baseName = core.check_name_style(each)[0]
		
		# Root joint should not stretch along its translate (it moves the whole chain in space)
		if index == 0:
			continue
			
		tx = mc.getAttr(f'{each}.translateX')
		ty = mc.getAttr(f'{each}.translateY')
		tz = mc.getAttr(f'{each}.translateZ')
		
		# Dynamically find the primary bone aim axis (largest absolute translation)
		axes = {'X': tx, 'Y': ty, 'Z': tz}
		primary_axis = max(axes, key=lambda k: abs(axes[k]))
		axis_val = axes[primary_axis]
		
		multiStartVal_adl = core.MDLWithMul(f'{baseName}_stretch', dv=axis_val)
		length_store.attr('output') >> multiStartVal_adl.attr('input1')
		multiStartVal_adl.attr('output') >> minorIK_jnt.attr(f'translate{primary_axis}')

	stick_ctrl.attr('stretchy') >> envelope_bta.attr('attributesBlender')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Make Squash Tentacle (optional)
	if squashDef:
		squash_nrb = mc.duplicate(ik_nrb, n=ik_nrb.replace('ik', 'squash'))[0]
		squash_loc_list = core.generate_named_pattern(f'{COMP_BASE_NAME}Squash##_loc', COUNT_DETAIL)

		mc.parent(squash_nrb, nurbAll_grp)

		for num in range(0, COUNT_DETAIL):
			locator = core.Locator(squash_loc_list[num])
			ik_jnt = core.Dag(ik_detail_jnt[num])
			locator.maSnap(ik_jnt)

		squash_nrb_grp = pls.pin_locator_surface(
			nurbs=squash_nrb,
			region=f'{BASE_NAME}Squash',
			side=SIDE,
			source_loc=squash_loc_list,
			locator_scale=1 * SCALE,
			creJnt=False,
			suffixJnt='pxyJnt',
			creCtrl=False,
			ctrlShape='circle_Y_along_ctrlShape',
			snapAtEnd=False,
			priorJnt='',
			scale=20
		)

		mc.setAttr(f"{COMP_BASE_NAME}_squash_nrb.tx", lock=False)
		mc.setAttr(f"{COMP_BASE_NAME}_squash_nrb.ty", lock=False)
		mc.setAttr(f"{COMP_BASE_NAME}_squash_nrb.tz", lock=False)
		mc.setAttr(f"{COMP_BASE_NAME}_squash_nrb.rx", lock=False)
		mc.setAttr(f"{COMP_BASE_NAME}_squash_nrb.ry", lock=False)
		mc.setAttr(f"{COMP_BASE_NAME}_squash_nrb.rz", lock=False)

		mc.setAttr(f"{squash_nrb}.rotateX", 90)
		mc.setAttr(f"{squash_nrb}.rotateZ", 180)
		mc.setAttr(f"{squash_nrb}.rotateY", 0)

		mc.setAttr(f"{squash_nrb}.translateX", 0)
		mc.setAttr(f"{squash_nrb}.translateY", 0)
		mc.setAttr(f"{squash_nrb}.translateZ", 0)

		squash_meta = core.MetaBlank(f'{COMP_BASE_NAME}_squash_xVal')
		squash_deformer, squash_handle = mc.nonLinear(squash_nrb, type='squash', name=f'{COMP_BASE_NAME}_squash_deformer')
		jntPxy_list = core.generate_named_pattern(f'{COMP_BASE_NAME}_detail##_pxyJnt', COUNT_DETAIL)

		for index, each in enumerate(squash_loc_list):
			mc.setAttr(f'{each}Shape.parameterV', 1)

			baseName = core.check_name_style(squash_loc_list[index])[0]
			multi01 = core.MDLWithMul(f'{baseName}_multiply', dv=0.1)
			plus01 = core.AddDoubleLinear(f'{baseName}_plus01', input2=1)

			multi01.attr('output') >> plus01.attr('input1')
			squash_meta.addAttribute(attributeType='float', longName=f'squash_{index+1:02}', minValue=-100, maxValue=100, defaultValue=0, keyable=True)
			squash_loc = core.Dag(each)
			squash_loc.attr('translateX') >> multi01.attr('input1')
			plus01.attr('output') >> squash_meta.attr(f'squash_{index+1:02}')

			if not mc.objExists(place_ctrl):
				pxy_jnt = core.Dag(jntPxy_list[index])
				squash_meta.attr(f'squash_{index+1:02}') >> pxy_jnt.attr('scaleY')
				squash_meta.attr(f'squash_{index+1:02}') >> pxy_jnt.attr('scaleZ')

		if not mc.objExists(place_ctrl):
			TentacleRig.info('Error, please specify placement controller.')
		else:
			placeObj_ctrl = core.Dag(place_ctrl)

			minusOne_pma = core.PlusMinusAverage(f'{COMP_BASE_NAME}_minusOne')
			minusOne_pma.attr('operation').value = 2
			placeObj_ctrl.attr('scaleX') >> minusOne_pma.attr('input3D[0].input3Dx')
			placeObj_ctrl.attr('scaleY') >> minusOne_pma.attr('input3D[0].input3Dy')
			placeObj_ctrl.attr('scaleZ') >> minusOne_pma.attr('input3D[0].input3Dz')

			minusOne_pma.attr('input3D[1].input3Dx').value = 1
			minusOne_pma.attr('input3D[1].input3Dy').value = 1
			minusOne_pma.attr('input3D[1].input3Dz').value = 1

			for index, each in enumerate(squash_loc_list):
				storeValue = core.PlusMinusAverage(f'{COMP_BASE_NAME}_storeValue{index+1:02}')
				storeValue.attr('input3D[1].input3Dx').value = 1

				minusOne_pma.attr('output3Dx') >> storeValue.attr('input3D[0].input3Dx')
				minusOne_pma.attr('output3Dy') >> storeValue.attr('input3D[0].input3Dy')
				minusOne_pma.attr('output3Dz') >> storeValue.attr('input3D[0].input3Dz')

				squash_meta.attr(f'squash_{index+1:02}') >> storeValue.attr('input3D[1].input3Dy')
				squash_meta.attr(f'squash_{index+1:02}') >> storeValue.attr('input3D[1].input3Dz')

				detailObj_loc = core.Dag(detail_loc[index])
				storeValue.attr('output3Dx') >> detailObj_loc.attr('scaleX')
				storeValue.attr('output3Dy') >> detailObj_loc.attr('scaleY') 
				storeValue.attr('output3Dz') >> detailObj_loc.attr('scaleZ')

		offset_X = squash_loc.attr('translateX').value
		offset_X_forHandle = offset_X * -2

		mc.setAttr(f'{squash_handle}.translateX', offset_X_forHandle)
		mc.setAttr(f'{squash_nrb}.translateX', offset_X * -1)

		TentacleRig.debug(f'This is storeValue: {storeValue.name}')

		squashLoc_list = core.generate_named_pattern(f'{COMP_BASE_NAME}Squash##_loc', COUNT_DETAIL)

		squash_grp = core.Null(f'{COMP_BASE_NAME}_squashLoc_grp')
		squash_grp.lockAllAttr(attrs=['t', 'r', 's'])

		for each in squashLoc_list:
			mc.parent(each, squash_grp.name)

		mc.parent(squash_handle, squash_grp.name)

		stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_Squash:", longName='Squash')
		stick_ctrlShape.addAttribute(attributeType='float', longName='factor', minValue=0, maxValue=1, defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='expan', minValue=-1, maxValue=2, defaultValue=1, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='expan_pos', minValue=0.02, maxValue=0.90, defaultValue=0.8, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='start_smooth', defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='end_smooth', defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='low_bound', minValue=-10, maxValue=0, defaultValue=-1, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='high_bound', minValue=0, maxValue=10, defaultValue=1, keyable=True)
		squash_deformer = core.Dag(squash_deformer)
		inv_value_mdl = core.MDLWithMul(f'{COMP_BASE_NAME}_squash_invValue', dv=-1)

		stick_ctrlShape.attr('factor') >> inv_value_mdl.attr('input1')
		inv_value_mdl.attr('output') >> squash_deformer.attr('factor')

		stick_ctrlShape.attr('expan_pos') >> squash_deformer.attr('maxExpandPos')
		stick_ctrlShape.attr('start_smooth') >> squash_deformer.attr('startSmoothness')
		stick_ctrlShape.attr('end_smooth') >> squash_deformer.attr('endSmoothness')

		stick_ctrlShape.attr('expan') >> squash_deformer.attr('expand')
		stick_ctrlShape.attr('low_bound') >> squash_deformer.attr('lowBound')
		stick_ctrlShape.attr('high_bound') >> squash_deformer.attr('highBound')

		mc.setAttr(f'{squash_nrb}.visibility', 0)
		squash_grp.attr('visibility').value = 0

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. create sine wave deformer
	if sineDef:
		sine_def_nrb = mc.duplicate(ik_nrb, n=ik_nrb.replace('ik', 'sine'))[0]
		sine_deformer, sine_handle = mc.nonLinear(sine_def_nrb, type='sine', name=f'{COMP_BASE_NAME}_sineDef')
		sine_zro_grp = core.Null(f'{COMP_BASE_NAME}_sineDefZroGrp')
		mc.parent(sine_handle, sine_zro_grp.name)
		sine_zro_grp.attr('visibility').value = 0
		sine_zro_grp.lockAllAttr(attrs=['t', 'r', 's'])

		#... BlendShape target
		mc.blendShape(f'{COMP_BASE_NAME}_bsh', e=True, t=(f'{COMP_BASE_NAME}_combineFkIk_nrb', 2, sine_def_nrb, 1.0))
		mc.setAttr(f'{COMP_BASE_NAME}_bsh.{sine_def_nrb}', 1)

		#... Connect value for stick
		stick_ctrlShape = core.Dag(stick_ctrl.shape)
		stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_SINE:", longName='SINE')
		stick_ctrlShape.addAttribute(attributeType='float', longName='envelope', minValue=0, maxValue=1, defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='amplitude', defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='wavelength', defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='offset', defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='orientation', defaultValue=0, keyable=True)

		sine_deformer = core.Dag(sine_deformer)
		#... set starter volume
		stick_ctrlShape.attr('envelope').value = 0
		stick_ctrlShape.attr('amplitude').value = 0.3
		stick_ctrlShape.attr('wavelength').value = 1.5

		#... store value for upcoming connection
		offset_store_val = core.PlusMinusAverage(f'{COMP_BASE_NAME}_offsetStoreVal_pma')
		amp_store_val = core.PlusMinusAverage(f'{COMP_BASE_NAME}_ampStoreVal_pma')
		length_store_val = core.PlusMinusAverage(f'{COMP_BASE_NAME}_lengthStoreVal_pma')

		stick_ctrlShape.attr('offset') >> offset_store_val.attr('input1D[0]')
		stick_ctrlShape.attr('amplitude') >> amp_store_val.attr('input1D[0]')
		stick_ctrlShape.attr('wavelength') >> length_store_val.attr('input1D[0]')

		offset_store_val.attr('output1D') >> sine_deformer.attr('offset')
		sine_handle = core.Dag(sine_handle)

		
		

		#... set orient for Snake 
		sine_deformer.attr('rotateX').value = 90
		stick_ctrlShape.attr('orientation') >> sine_handle.attr('rotateZ')

		stick_ctrlShape.attr('envelope') >> sine_deformer.attr('envelope')
		amp_store_val.attr('output1D') >> sine_deformer.attr('amplitude')
		length_store_val.attr('output1D') >> sine_deformer.attr('wavelength')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Cleanup
	stick_ctrlShape.deleteAttribute('Detail')

	stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_MAIN:", longName='MAIN_CTRL')
	stick_ctrlShape.addAttribute(attributeType='float', longName='ten_FKIK', minValue=0, maxValue=1, defaultValue=0, keyable=True)
	stick_ctrlShape.addAttribute(attributeType='float', longName='ten_IK', minValue=0, maxValue=1, defaultValue=0, keyable=True)
	stick_ctrlShape.addAttribute(attributeType='float', longName='ten_Detail', minValue=0, maxValue=1, defaultValue=0, keyable=True)
	masterFk_zrpGrp = core.Dag(f'{COMP_BASE_NAME}01_masterFkZro_grp')

	masterFk_zrpGrp.disconnectAttr('visibility')
	stick_ctrlShape.attr('ten_FKIK') >> masterFk_zrpGrp.attr('visibility')
	stick_ctrlShape.attr('ten_Detail') >> detail_grp.attr('visibility')
	stick_ctrlShape.attr('ten_FKIK').value = 1

	if sineDef:
		mc.setAttr(f'{sine_def_nrb}.visibility', 0)
		mc.parent(sine_def_nrb, nurbAll_grp.name)

	mc.setAttr(f'{ik_nrb}.visibility', 0)

	mc.parent(ik_nrb, nurbAll_grp.name)
	mc.parent(combineFkIk_nrb, nurbAll_grp.name)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Create meta node
	if sineDef:
		chain_meta = core.Dag(fk_rig[-1])
		chain_meta.addAttribute(dataType='string', longName='storeValue')
		chain_meta.attr('storeValue').value = f'{offset_store_val.name}, {amp_store_val.name}, {length_store_val.name}'
		chain_meta.setLocked('storeValue')
		chain_meta.addAttribute(dataType='string', longName='stickName')
		chain_meta.attr('stickName').value = stick_ctrl.name
		chain_meta.setLocked('stickName')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Hide Ik ctrl vis
	master_ik_ctrl = core.generate_named_pattern(f'{COMP_BASE_NAME}##_masterIk_ctrl', COUNT_DETAIL)

	for each in master_ik_ctrl:
		master_ik_ctrlShape = core.Dag(core.shapeName(each))
		stick_ctrlShape.attr('ten_IK') >> master_ik_ctrlShape.attr('visibility')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. make scalable
	if sineDef is False or squashDef is False:
		if mc.objExists(place_ctrl):
			placeObj_ctrl = core.Dag(place_ctrl)
			for index, each in enumerate(detail_loc):
				detail_loc_dag = core.Dag(each)
				placeObj_ctrl.attr('scaleX') >> detail_loc_dag.attr('scaleX')
				placeObj_ctrl.attr('scaleY') >> detail_loc_dag.attr('scaleY')
				placeObj_ctrl.attr('scaleZ') >> detail_loc_dag.attr('scaleZ')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Parent Important grp
	if not mc.objExists('tentacleStill_grp'):
		tenStillStore_grp = core.Null('tentacleStill_grp')
	else:
		tenStillStore_grp = core.Dag('tentacleStill_grp')

	mc.parent(nurbAll_grp.name, tenStillStore_grp.name)
	mc.parent(detail_grp.name, tenStillStore_grp.name)

	if not mc.objExists('tentacleIkh_grp'):
		tenIkhStore_grp = core.Null('tentacleIkh_grp')
	else:
		tenIkhStore_grp = core.Dag('tentacleIkh_grp')

	mc.parent(ikHandle.name, tenIkhStore_grp)

	if sineDef:
		mc.parent(sine_zro_grp.name, tenStillStore_grp.name)

	if squashDef:
		mc.parent(squash_grp.name, tenStillStore_grp.name)

	if not mc.objExists('tentacleFkJnt_grp'):
		tenFkJnt_grp = core.Null('tentacleFkJnt_grp')
	else:
		tenFkJnt_grp = core.Dag('tentacleFkJnt_grp')

	mc.parent(f'{COMP_BASE_NAME}01_masterFk_fkJnt', tenFkJnt_grp.name)

	if mc.objExists(parentTo):
		print(f'{COMP_BASE_NAME}01_masterFkRig_grp')
		master_fk_zroGrp = core.Dag(f'{COMP_BASE_NAME}01_masterFkRig_grp')
		mc.parent(master_fk_zroGrp, parentTo)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Assign ikh to stick
	stick_ctrl.addAttribute(attributeType='message', longName='ikh_msg')
	ikHandle.attr('message') >> stick_ctrl.attr('ikh_msg')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Set IK twist 
	if enableTwist:
		up_type_val = gmd.get_ik_world_up_type(worldUpType, default=1)
		twist_type_val = gmd.get_ik_twist_value_type(twistValueType, default=1)

		ikHandle.attr('dWorldUpType').value = up_type_val
		ikHandle.attr('dTwistValueType').value = twist_type_val
		if twistEnd is not None:
			ikHandle.attr('dTwistEnd').value = twistEnd
		if twistStart is not None:
			ikHandle.attr('dTwistStart').value = twistStart

		ikHandle.enableTwistControl(
			forwardAxis=forwardAxis,
			worldUpAxis=worldUpAxis,
			worldUpVector=worldUpVector,
			worldUpVectorEnd=worldUpVectorEnd,
			worldUpType=up_type_val,
			upObject=upObject,
			upObjectEnd=upObjectEnd,
			twistValueType=twist_type_val,
			twistEnd=twistEnd,
			twistStart=twistStart
		)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Parent Up Objects
	if upObject and mc.objExists(upObject) and parentTo and mc.objExists(parentTo):
		try:
			mc.parent(upObject, parentTo)
		except Exception:
			pass

	end_ctrl = f'{COMP_BASE_NAME}0{COUNT_MAIN}_masterFk_ctrl' if COUNT_MAIN < 10 else f'{COMP_BASE_NAME}{COUNT_MAIN}_masterFk_ctrl'
	if upObjectEnd and mc.objExists(upObjectEnd) and mc.objExists(end_ctrl):
		try:
			mc.parent(upObjectEnd, end_ctrl)
		except Exception:
			pass
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Connect Twist to Master Curl
	if enableTwist and upObject and upObjectEnd and mc.objExists(upObject) and mc.objExists(upObjectEnd):
		start_twist = core.Dag(upObject)
		end_twist = core.Dag(upObjectEnd)

		stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_TWIST:", longName='TWIST_CTRL')
		stick_ctrlShape.addAttribute(attributeType='float', longName='Start', defaultValue=0, keyable=True)
		stick_ctrlShape.addAttribute(attributeType='float', longName='End', defaultValue=0, keyable=True)

		startTwist_mul = core.MultiplyDivine(f'{COMP_BASE_NAME}_startTwist_mul', operation=1)
		startTwist_mul.attr('input2X').value = 25
		stick_ctrlShape.attr('Start') >> startTwist_mul.attr('input1X')
		startTwist_mul.attr('outputX') >> start_twist.attr('translateX')

		endTwist_mul = core.MultiplyDivine(f'{COMP_BASE_NAME}_endTwist_mul', operation=1)
		endTwist_mul.attr('input2X').value = 25
		stick_ctrlShape.attr('End') >> endTwist_mul.attr('input1X')
		endTwist_mul.attr('outputX') >> end_twist.attr('translateX')

		start_twist.attr('visibility').value = 0
		end_twist.attr('visibility').value = 0

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # .................. Done
	core.makeHeader('DONE')

	return {
		'ikHandle': ikHandle,
		'stick_ctrl': stick_ctrl,
		'bind_joints': bind_jnt_list
	}

def setup_slide_hierarchy(ctrls=None, rig_node='rig_grp'):
	"""
	Setup Slide Path Controllers Hierarchy (PH/SN) and register to rig_grp.
	Must be run to enable 'Snap to Path' / Slide Path follow functionality in the UI tool.
	
	Creates:
	  - {ctrl}_SN (Snap Group)
	  - {ctrl}_PH (Parent Handle Group)
	Registers:
	  - rig_grp.slide_ctrls (JSON array string)
	
	:param ctrls: list of controller names
	:param rig_node: root rig node (default 'rig_grp')
	"""
	if not ctrls:
		sel = mc.ls(sl=True, type='transform')
		if not sel:
			om.MGlobal.displayWarning("[SlideSetup] No controllers specified and nothing selected.")
			return []
		ctrls = sel

	processed_ctrls = []

	for ctrl in ctrls:
		if not mc.objExists(ctrl):
			om.MGlobal.displayWarning(f"[SlideSetup] Controller not found, skipped: {ctrl}")
			continue

		sn_grp = f"{ctrl}_SN"
		ph_grp = f"{ctrl}_PH"

		# Check if already setup
		if mc.objExists(ph_grp) and mc.objExists(sn_grp):
			om.MGlobal.displayInfo(f"[SlideSetup] PH/SN already exists for: {ctrl}")
			processed_ctrls.append(ctrl)
			continue

		# Get world pivot position of controller
		piv = mc.xform(ctrl, q=True, rp=True, ws=True)

		# 1. Create Snap Group (_SN) wrapping the controller
		if not mc.objExists(sn_grp):
			mc.group(ctrl, n=sn_grp)
			mc.xform(sn_grp, piv=piv, ws=True)

		# 2. Create Parent Handle (_PH) wrapping the _SN group
		if not mc.objExists(ph_grp):
			mc.group(sn_grp, n=ph_grp)
			mc.xform(ph_grp, piv=piv, ws=True)

		om.MGlobal.displayInfo(f"[SlideSetup] Successfully created PH/SN for: {ctrl}")
		processed_ctrls.append(ctrl)

	# 3. Register to rig_node.slide_ctrls
	if mc.objExists(rig_node):
		if not mc.attributeQuery('slide_ctrls', node=rig_node, exists=True):
			mc.addAttr(rig_node, ln='slide_ctrls', dt="string")
		mc.setAttr(f"{rig_node}.slide_ctrls", json.dumps(processed_ctrls), type="string")
		om.MGlobal.displayInfo(f"[SlideSetup] Registered {len(processed_ctrls)} controllers to {rig_node}.slide_ctrls: {processed_ctrls}")
	else:
		om.MGlobal.displayWarning(f"[SlideSetup] '{rig_node}' node not found in scene! Attributes not saved on rig node.")

	return processed_ctrls


if __name__ == '__main__':
	snakeRigFk_Ik_Deform()