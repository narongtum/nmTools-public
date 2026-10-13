from function.rigging.autoRig.components.ribbonRig import eh_hh_ribbonExt as hhRibbon 
reload(hhRibbon)
from function.rigging.autoRig.base import core
reload(core)



import function.rigging.constraint.matrixConstraint as mtc
reload(mtc)



def performMatrixRibbonRig(
	charScale = 2.5,
	jointTop = 'upperArmLFT_bJnt'	,
	jointBtm = 'lowerArmLFT_bJnt',
	aim_axis='y+',
	up_axis='z+',
	numJnts=5, #.. using 5 or 7 only
	baseName='uprArm',
	side='LFT'
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



	#... Find perfect midpoint (Pos & Rot) using 50/50 constraint
	#mc.delete(mc.parentConstraint(jointTop, jointBtm, mid_loc.name, mo=False))

	#... run ribbon
	makeHingesParent, modGrp, subRbnJnt, jnts_list, ribbonRig_list, ctrl_list = hhRibbon.de_boor_ribbon((jointTop, mid_loc.name, jointBtm), aim_axis=aim_axis, up_axis=up_axis, num_joints=numJnts,
					   baseName=baseName, side=side,charScale = charScale, debug = True)	



	mc.delete(top_loc.name, mid_loc.name, btm_loc.name)


	#... make middle controller follow upper and lower controller


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

	from function.rigging.util import generic_maya_dict as mnd
	reload(mnd)

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

	return ribbonRig_list




upr_ribbonRig_list = performMatrixRibbonRig(
	charScale = 2.5,
	jointTop = 'upperArmLFT_bJnt'	,
	jointBtm = 'lowerArmLFT_bJnt',
	aim_axis='y+',
	up_axis='z+',
	numJnts=5, #.. using 5 or 7 only
	baseName='uprArm',
	side='LFT'
	)

lwr_ribbonRig_list = performMatrixRibbonRig(
	charScale = 2.5,
	jointTop = 'lowerArmLFT_bJnt'	,
	jointBtm = 'handLFT_bJnt',
	aim_axis='y+',
	up_axis='z+',
	numJnts=5, #.. using 5 or 7 only
	baseName='lwrArm',
	side='LFT'
	)





#... makeHigesMover for elbow or knee 




nameSpace = ''  
part = 'arm'       
side = 'LFT'    
topName = ''    
btmName = ''    
charScale = charScale  
noTouch_grp = 'noTouch_grp'     
moverPosition = 'lowerArmLFT_bJnt'  
ctrl_grp = 'ctrl_grp'       
alongAxis = 'y'


core.makeHeader('Start makeHigesMover')

class RibbonLogger(logger.MayaLogger):
	LOGGER_NAME = "Ribbon"

noTouch_grp = '%s%s' %( nameSpace , noTouch_grp ) 


name = nameSpace + part + 'Hinges' + 'Rbn'
rbnHinges_ctrl = core.Dag( name + side + '_ctrl' )
rbnHinges_ctrl.nmCreateController('squarePlain_ctrlShape')
rbnHinges_ctrl.editCtrlShape( axis = charScale * 2.1 )
rbnHinges_ctrl.color = 'softBlue'


#                           #
#   set ctrl orientation    #
#                           #

if part == 'arm':
	RibbonLogger.info('\nThis is maybe Arm.')

	if side == 'LFT' and alongAxis == 'y':
		upAxis = ( 0,0,90 )
	elif side == 'RGT':
		upAxis = ( 180,0,90 )

elif part == 'leg' or part == 'frontLeg' or part == 'backLeg' or part == 'upLeg' or part == 'lwrLeg'  :
	RibbonLogger.info('\nThis is maybe Leg.')

	if side == 'LFT' and alongAxis == 'y':
		# upAxis = ( 0,0,180 )  default value
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


# Translate elbow or knee a bit for solve weight error
if alongAxis == 'y':
	hinges_jnt.moveObj(position = (0, charScale*0.01, 0))
elif alongAxis == 'x':
	hinges_jnt.moveObj(position = (charScale*0.01, 0, 0))


hinges_jnt.freeze()

if alongAxis == 'y':
	hinges_jnt.setRotate( upAxis )
	hinges_jnt.freeze()

rbnHinges_ctrl.maSnap( hinges_jnt ) 
hinges_jnt.name = name + side + '_rbnBJnt'





if alongAxis == 'y':

	if part == 'leg':
		rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 0 )  )
	elif part == 'arm':
		rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 ) )

elif alongAxis == 'x':
	if part == 'leg':
		rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 ) )
		if side == 'RGT':
			pass
	elif part == 'arm':
		rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 ) )


# sys.exit(rbnHinges_ctrl.name)




# Parent to bind joint for exporting
# hinges_jnt.parent( moverPosition )
hinges_jnt.attr('radius').value = 1.5
hinges_jnt.attr('overrideEnabled').value = 1
# Make it gray
hinges_jnt.attr('overrideColor').value = 3
# For make controller scalable
hinges_jnt.attr('segmentScaleCompensate').value = 0

# Build Parent Structure first to prevent matrix double-transform
rbnhingesZro_grp = rigTools.zroNewGrpWithOffset( rbnHinges_ctrl )
mc.parent( rbnhingesZro_grp[0] , ctrl_grp  )

bJntMoverPos = moverPosition.replace( 'buffJnt' , 'bJnt')
mc.parent( hinges_jnt.name ,  bJntMoverPos )

# Then apply Constraints
# Make it follow
mtc.parentConMatrixGPT(rbnHinges_ctrl.name, hinges_jnt.name, mo=True, baseName=name +'Mid'+ side)

# Parent constraint  with Offset grp
#RibbonLogger.info('\n**THIS IS A upper bJnt ---------------------------------**')
#RibbonLogger.info(str(btmName[0][1]))
upr_ribbonRig_list[2][1]
#'uprArmBtmRbnLFTOffset_grp
mtc.parentConMatrixGPT(rbnHinges_ctrl.name, upr_ribbonRig_list[2][1], mo=True, baseName=name +'Top'+ side)
mtc.parentConMatrixGPT(rbnHinges_ctrl.name, lwr_ribbonRig_list[2][1], mo=True, baseName=name +'Btm'+ side)

# Make Hinges follow bJnt
mtc.parentConMatrixGPT(moverPosition, rbnhingesZro_grp[0], mo=True, baseName=name +'BJnt'+ side)

RibbonLogger.info('\n**THIS IS A upper bJnt ---------------------------------**')
RibbonLogger.info(str(btmName[2]))

RibbonLogger.info('\n**THIS IS A lower bJnt ---------------------------------**')
RibbonLogger.info(str(topName[2]))

mc.select( deselect = True )

RibbonLogger.info(str(topName))
RibbonLogger.info(str(btmName))
core.makeHeader('End makeHigesMover')











import function.rigging.constraint.matrixConstraint as mtc
reload(mtc)
eh_aimMatrixConstraint(
	aim_object = 'handLFT_bJnt', 
	up_object = 'pSphere1', 
	target = 'local_aim', 
	aimVector=(0, 1, 0), 
	upVector=(0, 0, 1), 
	mo=True,
	baseName='makeTwist'
)