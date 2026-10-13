# -*- coding: utf-8 -*-
"""
Date: 23.01.Jan.31.Tue.08_

Create IK joint chains
from an existing joint chain
and add FK controls offsets.
(Non-Dynamic Version)
"""

from function.framework.reloadWrapper import reloadWrapper as reload

from maya import cmds as mc
import pymel.core as pm
import maya.mel as mel

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.util import misc as misc
reload(misc)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.pipeline import logger 
reload(logger)


class IkLogger(logger.MayaLogger):
	LOGGER_NAME = "ikSpineLogger"


def createNoneDynamicTail(
		# arg
		side = 'LFT',
		baseName = 'breast',
		firstJnt = 'breast01LFT_bJnt' ,
		lastJnt = 'breast02LFT_bJnt'  ,		
		charScale = 1					,
		nameSpace = ''					,
		curlCtrl = False				,
		nbrOfCtrl = None				,
		parentTo = 'ctrl_grp'  			,
		priorJnt = 'hip_bJnt'			,
		ctrlShape ='cube_ctrlShape'		,
		meta = False					,
		localWorld = False				,
		localWorld_worldObj = 'ctrl_grp'	):

	if mc.objExists(firstJnt) and mc.objExists(lastJnt):
		pass
	else:
		raise RuntimeError('No joint attached found.')

	# make spIkJnt Chain
	spIkJnt = mc.duplicate (firstJnt, rr = 1)
	mc.select (spIkJnt, hi = 1)

	lastName = misc.findLastName(firstJnt)
	misc.searchReplace( searchText = lastName, replaceText='spIkJnt' )
	spIkJnt = misc.searchReplace( searchText='spIkJnt1', replaceText='spIkJnt' )
	pm.select( clear=True )

	# define joint chain
	mc.select (cl = 1)
	mc.select (firstJnt, hi = 1)
	jntChain = mc.ls (sl = 1)
	lastJntIndx = jntChain.index(lastJnt)

	# create curve prepare for ik skine rig
	jntsPositions = []
	for jnt in jntChain:
		mc.setAttr(jnt + '.segmentScaleCompensate', 0) #... make scalable
		jntPos = mc.xform (jnt, q = 1, ws = 1, t = 1)
		jntsPositions.append (jntPos)
	rawCrv = mc.curve (d = 3, ep = jntsPositions)
	baseCrv = mc.rename (rawCrv, baseName + side + "Ik_baseCurve")

	if not nbrOfCtrl:
		# create fk control
		nbrOfCtrl = len(jntChain) # number of control
		IkLogger.info('Using specific joint number: %s ' %nbrOfCtrl)

	if nbrOfCtrl == 0:
		mc.error ("You have to create at least two FK control.")
	elif nbrOfCtrl > len(jntChain):
		mc.error ("The number of FK controls can't be superior to the number of joints in the chain.")

	# Create the Ik spline
	dynIkSplineRaw = mc.ikHandle (sol = "ikSplineSolver", ccv = 0, pcv = 0, sj = spIkJnt[0], ee = spIkJnt[-1], c = baseCrv)
	dynIkSpline = mc.rename (dynIkSplineRaw[0], baseName + side +"Ik_ikh")
	mc.rename (dynIkSplineRaw[1], baseName + side +"Ik_eff")
	mc.setAttr (dynIkSpline + ".visibility", 0)

	# create Temp joint for fk joint chain
	origCrv = baseCrv
	x = 0
	fkJntChain = []
	radius = mc.joint (firstJnt, q = 1, rad = 1) [0]
	crv = mc.duplicate (origCrv, rr = 1)
	mc.rebuildCurve (crv, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 0, kep = 1, kt = 1, s = 20, d = 3, tol = 0)

	IkLogger.info('This number of ctrl is more than two.')
	
	# for make output following arg that user want
	nbrOfCtrl = nbrOfCtrl - 1

	for x in range (x, nbrOfCtrl + 1, x + 1):
		incr = (1.0/nbrOfCtrl) * x
		ptOnCrvPos = mc.pointOnCurve (crv, pr = incr)
		rawFkJnt = mc.joint (rad = radius*0.75)
		fkJnt = mc.rename (rawFkJnt, baseName + "0%d_temp" % (x + 1) + side)
		fkJntChain.append (fkJnt)
		mc.xform (ws = 1, t = ptOnCrvPos)
	mc.delete (crv)
	
	# fix the orientation
	mc.joint (fkJntChain[0], e = 1, oj = "yxz", secondaryAxisOrient = "xdown", ch = 1, zso = 1)
	mc.setAttr (fkJntChain[-1] + ".jointOrientX", 0)
	mc.setAttr (fkJntChain[-1] + ".jointOrientY", 0)
	mc.setAttr (fkJntChain[-1] + ".jointOrientZ", 0)
	IkLogger.info('%s is joint chain.' %fkJntChain)

	# MAKE TEMP JOINT TO IK JOINT
	from function.rigging.autoRig.addRig import createFkRig
	reload(createFkRig)

	# dup fk joint chain to ik joint
	ikSpGen_jnt_grp = createFkRig.newCreateFkRig(	nameSpace = ''  ,  name = baseName + 'Ik' , parentTo = ''  ,
						tmpJnt = 	fkJntChain	,
						charScale = charScale	, priorJnt = '' 			,
						side = side ,ctrlShape = ctrlShape  , localWorld = False , 
						color = 'white' , curlCtrl = curlCtrl ,suffix = '_ikJnt'	)
										
	pm.delete( fkJntChain )					

	#... Matrix Local World Space Switch
	if localWorld:
		first_ctrl = ikSpGen_jnt_grp[3][0]
		first_zro = first_ctrl.name.replace('_ctrl', 'Zro_grp')
		
		mtc.eh_orientLocalWorldMatrix(
			ctrl = first_ctrl.shape,
			localObj = priorJnt,
			worldObj = localWorld_worldObj,
			target = first_zro,
			attrName = 'localWorld',
			parentMode = 'orient',
			bodyPart = baseName + side
		)

	# skin ik joint to curve
	mc.select (ikSpGen_jnt_grp[2], baseCrv, r = 1)
	mc.skinCluster (n = baseName + side +"Ik_Fk_skinCluster", tsb = 1, bm = 0, sm = 0, nw = 1, wd = 0, mi = 5, omi = 1, dr = 4, rui = 1)

	#... Matrix Constraint Requirement: Parent into final hierarchy before creating matrix constraints
	if priorJnt:
		try:
			mc.parent(firstJnt, priorJnt)
		except RuntimeError:
			pass

	#... Making pair psCon between ik << bJnt >> ik
	ikChain = spIkJnt
	bJntChain = jntChain

	num = 0
	for i in range(len(bJntChain)):
		print ('# # # pair constraint # # #')
		IkLogger.info(baseName + '%02d%s_psCon' %(( num +1),side))
		psCon = mtc.parentConMatrixGPT(
			source=ikChain[i],
			target=bJntChain[i],
			mo=True,
			baseName=baseName + '%02d%s' %(( num +1), side)
		)
		num = num+1

	# clearSceneAndScript
	all_dyn_grp = mc.group (n = baseName + side + "IkSpine_grp", em = 1)
	mc.parent (baseCrv, all_dyn_grp)
	mc.parent (dynIkSpline, all_dyn_grp)
	mc.setAttr (all_dyn_grp + ".visibility", 0)

	mc.setAttr ( str(ikSpGen_jnt_grp[2][0]) + ".visibility", 0)
	mc.setAttr ( spIkJnt[0]+ ".visibility", 0)

	all_jnt_grp = mc.group (n = baseName + side + "Jnt_grp", em = 1)
	mc.parent ( spIkJnt[0], all_jnt_grp )
	mc.parent ( ikSpGen_jnt_grp[2][0], all_jnt_grp )

	# Parent the joint group to the rig's noTouch or jnt group to ensure it follows the character
	if mc.objExists('noTouch_grp'):
		mc.parent(all_jnt_grp, 'noTouch_grp')
	elif mc.objExists('jnt_grp'):
		mc.parent(all_jnt_grp, 'jnt_grp')

	pm.select( clear=True )

	print ('\n')
	misc.makeHeader('None Dynamics IK Spine Chains Ending')

	# parenting group
	if priorJnt:
		IkLogger.info(all_dyn_grp)

		# Constraint rig_grp to prior controller grp
		mtc.parentConMatrixGPT( 
			source = priorJnt , 
			target = ikSpGen_jnt_grp[1] , 
			mo = True , 
			baseName = baseName + side + 'RigGrp' 
		)

	if parentTo:
		mc.parent(ikSpGen_jnt_grp[1], parentTo)

	#... Create network node for store data
	dynIkSpline_meta = core.MetaGeneric(baseName + side)

	mc.connectAttr(priorJnt + '.message', dynIkSpline_meta.name + '.Rig_Prior')

	dynIkSpline_meta.setAttribute('Base_Name', all_dyn_grp , type = 'string')
	dynIkSpline_meta.addAttribute( dataType = 'string' , longName = 'Input')
	dynIkSpline_meta.setAttribute('Input', [firstJnt,lastJnt] , type = 'string')

	if side:
		dynIkSpline_meta.setAttribute('Side', side , type = 'string')

	# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
	# Global Scale Connection for IK Spline Joints
	# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
	global_ctrl = 'placement_ctrl'
	
	if mc.objExists(global_ctrl):
		# Create a list of all joints in the spline chains
		all_spline_jnts = mc.ls(spIkJnt, dag=True, type='joint') + mc.ls(ikSpGen_jnt_grp[2], dag=True, type='joint')
		
		for jnt in all_spline_jnts:
			# Ensure Segment Scale Compensate is ON to prevent double transformations
			mc.setAttr(jnt + ".segmentScaleCompensate", 1)
			
			# Connect Global Scale (using Y axis as master) to all Joint Scale axes
			try:
				mc.connectAttr(global_ctrl + '.scaleY', jnt + '.scaleX', force=True)
				mc.connectAttr(global_ctrl + '.scaleY', jnt + '.scaleY', force=True)
				mc.connectAttr(global_ctrl + '.scaleY', jnt + '.scaleZ', force=True)
			except Exception as e:
				IkLogger.warning('Could not connect scale to %s: %s' % (jnt, str(e)))
	else:
		IkLogger.warning('Global control "%s" does not exist. Skipping global scale connection.' % global_ctrl)

	core.makeHeader('END of Function')
	return firstJnt, spIkJnt[0], ikSpGen_jnt_grp[1], ikSpGen_jnt_grp[2][0], None, ikSpGen_jnt_grp[3], all_dyn_grp, None, None, all_jnt_grp, None, dynIkSpline_meta
