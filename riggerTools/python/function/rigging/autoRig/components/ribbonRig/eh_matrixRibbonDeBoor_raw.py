from function.rigging.autoRig.components.ribbonRig import eh_hh_ribbonExt as hhRibbon 
reload(hhRibbon)
from function.rigging.autoRig.base import core
reload(core)

charScale = 2.5
jointTop = 'lowerArmLFT_bJnt'	
jointBtm = 'handLFT_bJnt'	
aim_axis='y+'
up_axis='z+'
numJnts=7 #.. using 5 or 7 only
baseName='lwrArm'
side='LFT'
upVec_obj = 'lwrupVec_loc'

#... find mid point for make ribbon
mid_loc = core.Joint('mid_tmpLoc', radius=10, overrideColor=2)

#... Find perfect midpoint (Pos & Rot) using 50/50 constraint
mc.delete(mc.parentConstraint(jointTop, jointBtm, mid_loc.name, mo=False))

#... run ribbon
makeHingesParent, modGrp, subRbnJnt, jnts_list, ribbonRig_list, ctrl_list = hhRibbon.de_boor_ribbon((jointTop, mid_loc.name, jointBtm), aim_axis=aim_axis, up_axis=up_axis, num_joints=numJnts,
				   baseName=baseName, side=side,charScale = charScale)		   		   
mc.delete(mid_loc.name)


#... make middle controller follow upper and lower controller
import function.rigging.constraint.matrixConstraint as mtc
reload(mtc)

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
	upObject1=upVec_obj,
	upObject2=upVec_obj,
	aimVector=aimed_axis, 
	upVector=uped_axis, 
	mo=True,
	baseName=baseName,
	side=side,
	weight=0.5)
