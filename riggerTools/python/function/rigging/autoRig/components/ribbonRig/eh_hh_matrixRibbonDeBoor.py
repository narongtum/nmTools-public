from function.framework.reloadWrapper import reloadWrapper as reload

import maya.cmds as mc

from function.rigging.autoRig.components.ribbonRig import eh_hh_ribbonExt as hhRibbon 
reload(hhRibbon)

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.util import misc
reload(misc)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.pipeline import logger 
reload(logger)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

class RibbonLogger(logger.MayaLogger):
	LOGGER_NAME = "Ribbon"






def performMatrixRibbonRig(
	charScale = 2.5,
	jointTop = 'upperArmLFT_bJnt'	,
	jointBtm = 'lowerArmLFT_bJnt',
	aim_axis='y+',
	up_axis='z+',
	numJnts=5, #.. using 5 or 7 only
	baseName='uprArm',
	side='LFT',
	ctrl_grp = '',
	debug = False,
	noTouch_grp = 'noTouch_grp'	,
	rotOrder='xzy'
	):



	if numJnts not in (5, 7):
		mc.error('Using 5 or 7 only!!!')


	#... find mid point for make ribbon
	mid_loc = core.Joint('mid_tmpLoc', radius=10, overrideColor=2)
	top_loc = core.Joint('top_tmpLoc')
	btm_loc = core.Joint('bttom_tmpLoc')
	top_loc.maSnap(jointTop)
	btm_loc.maSnap(jointBtm)
	btm_loc.parent(top_loc)
	top_loc.freeze()
	#... find half way of top and bottom
	distance = btm_loc.attr('translateY').value
	distanceHalf = distance*0.5
	mc.parent(btm_loc.name, world=True)
	mid_loc.maSnap(jointTop)
	mid_loc.parent(top_loc)
	top_loc.freeze()
	mid_loc.attr('translateY').value = distanceHalf
	mc.parent(mid_loc.name, world=True)

	upvec_loc = core.Locator(f'{baseName}UpVec{side}_loc', scale = charScale*2.25)
	upvec_loc.maSnap(mid_loc)



	


	if side == 'LFT':
		upvec_loc.attr('translateZ').value += charScale*10
	elif side == 'RGT':
		upvec_loc.attr('translateZ').value -= charScale*10

	# Parent to jointTop so the Up-Vector rotates with the limb


	#... by pass locator to 'notouch_grp' instead
	# mc.parent(upvec_loc.name, jointTop)
	upvec_grp = core.Null(f'{baseName}UpVec{side}Zro_grp')
	upvec_grp.maSnap(upvec_loc)
	upvec_loc.parent(upvec_grp)
	mc.parent(upvec_grp.name, noTouch_grp)
	upvec_loc.setLocColor = 'white'
	mtc.parentConMatrixGPT(jointTop, upvec_grp.name, mo=True, rotate=True, baseName= f"{baseName}Upvec{side}")

	if debug == False:
		upvec_grp.attr('visibility').value = 0



	#... Find perfect midpoint (Pos & Rot) using 50/50 constraint
	#mc.delete(mc.parentConstraint(jointTop, jointBtm, mid_loc.name, mo=False))

	#... run ribbon
	makeHingesParent, modGrp, subRbnJnt, jnts_list, ribbonRig_list, ctrl_list, localAim_grps = hhRibbon.de_boor_ribbon((jointTop, mid_loc.name, jointBtm), aim_axis=aim_axis, up_axis=up_axis, num_joints=numJnts,
					   baseName=baseName, side=side,charScale = charScale, debug = debug, rotOrder = rotOrder)	



	mc.delete(top_loc.name, mid_loc.name, btm_loc.name)


	#... make middle controller follow upper and lower controller
	# mtc import moved to top of function

	#... Constraint with 2 weights (upper and lower)
	mtc.parentBlendMatrixGPT(
		source1 = ctrl_list[0],   
		source2 = ctrl_list[2],   
		target = ribbonRig_list[1][1],    
		mo = True, 
		translate = True, 
		rotate = False, 
		scale = False,
		weight = 0.5,
		baseName = f'Aimed{baseName}',
		side = side)



	aimed_axis = mnd.aim_axis_dict.get(aim_axis.lower())
	uped_axis = mnd.aim_axis_dict.get(up_axis.lower())


	#... for making middle always aim to upper and lower controller
	mtc.aimBlendMatrixGPT(
		source1=ctrl_list[0],
		source2=ctrl_list[2],
		target=ribbonRig_list[1][1], 
		upObject1=upvec_loc.name,
		upObject2=upvec_loc.name,
		aimVector=aimed_axis, 
		upVector=uped_axis, 
		mo=True,
		baseName=baseName,
		side=side,
		weight=0.5)

	#... cleanup grp
	mc.parent(modGrp, ctrl_grp)

	return ribbonRig_list, jnts_list, localAim_grps






#... Make elbow or knee move with ribbon
def makeHigesMover( 	nameSpace = ''	,
				part = ''		, 
				side = 'LFT' 	, 
				topName = ''	, 
				btmName = ''  	, 
				charScale = '' 	, 
				noTouch_grp = 'noTouch_grp' 	,
				moverPosition = 'lowerArmLFT_bJnt'	,
				ctrl_grp = 'ctrl_grp'		,
				alongAxis = 'y'
			 ):

	core.makeHeader('Start makeHigesMover')



	noTouch_grp = '%s%s' %(	nameSpace , noTouch_grp	) 


	name = nameSpace + part + 'Hinges' + 'Rbn'
	rbnHinges_ctrl = core.Dag( name + side + '_ctrl' )
	rbnHinges_ctrl.nmCreateController('squarePlain_ctrlShape')
	rbnHinges_ctrl.editCtrlShape( axis = charScale * 2.1 )
	rbnHinges_ctrl.color = 'softBlue'


	#							#
	#	set ctrl orientation	#
	#							#

	if part == 'arm':
		RibbonLogger.info('\nThis is maybe Arm.')

		if side == 'LFT' and alongAxis == 'y':
			upAxis = ( 0,0,90 )
		elif side == 'RGT':
			upAxis = ( 180,0,90 )

	elif part == 'leg' or part == 'frontLeg' or part == 'backLeg' or part == 'upLeg' or part == 'lwrLeg'  :
		RibbonLogger.info('\nThis is maybe Leg.')

		if side == 'LFT' and alongAxis == 'y':
			# upAxis = ( 0,0,180 )	default value
			upAxis = ( 0,0,180 )
		elif side == 'RGT' and alongAxis == 'y':
			# upAxis = ( 0,180,0 ) default value
			upAxis = ( 0,0,0 )
		elif side == 'LFT' and alongAxis == 'x':
			upAxis = ( 0,0,0 )
		elif side == 'RGT' and alongAxis == 'x':
			upAxis = ( 0,0,0 )

	else:
		mc.error('What part is it?')


	hinges_jnt = core.Joint()
	hinges_jnt.maSnap( moverPosition )



	'''
	# Translate elbow or knee a bit for solve weight error
	if alongAxis == 'y':
		hinges_jnt.moveObj(position = (0, charScale*0.01, 0))
	elif alongAxis == 'x':
		hinges_jnt.moveObj(position = (charScale*0.01, 0, 0))

	hinges_jnt.freeze()

	if alongAxis == 'y':
		hinges_jnt.setRotate( upAxis )
		hinges_jnt.freeze()
	'''

	rbnHinges_ctrl.maSnap( hinges_jnt ) 
	hinges_jnt.name = name + side + '_rbnBJnt'

	# #... Restore shape rotation for visual consistency
	# if alongAxis == 'y':
	# 	if part == 'leg':
	# 		rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 0 )	)
	# 	elif part == 'arm':
	# 		rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 )	)
	# elif alongAxis == 'x':
	# 	rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 )	)




	# Joint settings for exporting
	hinges_jnt.attr('radius').value = 1.5
	hinges_jnt.attr('overrideEnabled').value = 1
	hinges_jnt.attr('overrideColor').value = 3
	hinges_jnt.attr('segmentScaleCompensate').value = 0

	# Build Parent Structure first to prevent matrix double-transform
	rbnhingesZro_grp = rigTools.zroNewGrpWithOffset( rbnHinges_ctrl )
	mc.parent( rbnhingesZro_grp[0] , ctrl_grp  )

	bJntMoverPos = moverPosition.replace( 'buffJnt' , 'bJnt')
	mc.parent( hinges_jnt.name ,  bJntMoverPos )

	#... Then apply Constraints
	#... Make it follow
	mtc.parentConMatrixGPT(rbnHinges_ctrl.name, hinges_jnt.name, mo=True, baseName=name +'Mid'+ side)

	# Parent constraint  with Offset grp
	RibbonLogger.info('\n**THIS IS A upper bJnt ---------------------------------**')
	RibbonLogger.info(str(btmName[0][1]))

	mtc.parentConMatrixGPT(rbnHinges_ctrl.name, btmName[2][1], mo=True, rotate=False, baseName=name +'Top'+ side)
	mtc.parentConMatrixGPT(rbnHinges_ctrl.name, topName[0][1], mo=True, baseName=name +'Btm'+ side)

	#... Make Hinges follow bJnt
	mtc.parentConMatrixGPT(moverPosition, rbnhingesZro_grp[0], mo=True, baseName=name +'BJnt'+ side)

	RibbonLogger.info('\n**THIS IS A upper bJnt ---------------------------------**')

	RibbonLogger.info('\n**THIS IS A lower bJnt ---------------------------------**')

	mc.select( deselect = True )

	RibbonLogger.info(str(topName))
	RibbonLogger.info(str(btmName))
	core.makeHeader('End makeHigesMover')	