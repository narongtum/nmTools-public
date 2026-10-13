#... Updated hhRibbon using matrix de_boor math with autoRig integration
import maya.cmds as mc
from maya.api import OpenMaya as om
from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.de_boor import hh_de_boor_core as core
reload(core)

from function.rigging.autoRig.base import core as autoRigCore
reload(autoRigCore)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

OPEN = 'open'
PERIODIC = 'periodic'

# AXIS_VECTOR = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)
AXIS_VECTOR = mnd.aim_axis_dict


KNOT_TO_FORM_INDEX = {OPEN: om.MFnNurbsCurve.kOpen, PERIODIC: om.MFnNurbsCurve.kPeriodic}


def de_boor_ribbon(cvs, baseName='ribbon', side='LFT', nameSpace='', charScale=1, aim_axis='x', up_axis='y', num_joints=5, tangent_offset=0.001, d=None, kv_type=OPEN,
				   param_from_length=True, tol=0.000001, use_position=True, use_tangent=True,
				   use_up=True, use_scale=False, debug = False, rotOrder='xzy'):
	"""
	AutoRig integrated de_boor_ribbon.
	"""

	partElem = nameSpace + baseName

	mod_grp = autoRigCore.Null(f'{partElem}Mod{side}_grp')
	ctls_grp = autoRigCore.Null(f'{partElem}Ctls{side}_grp')
	# jnts_grp = autoRigCore.Null(f'{partElem}Jnts{side}_grp')
	
	mod_grp.rotateOrder = rotOrder
	ctls_grp.rotateOrder = rotOrder
	
	ctls_grp.parent(mod_grp)
	# jnts_grp.parent(mod_grp)
	
	mc.matchTransform(mod_grp.name, cvs[0])

	ctls = []
	ctlZro_grps = []
	mid_ctls = []
	localAim_grps = []

	#... make middle controller
	for i, cv in enumerate(cvs):
		ctl_name = f'{partElem}Cv{i+1:02d}{side}_ctrl'
		ctl = autoRigCore.Dag(ctl_name)
		

		# 1. Create controller with appropriate shape
		if i+1 == 2 or i+1 == 4: #... is mean Middle ribbon ctrl
			ctl.nmCreateController('square_ctrlShape')
			ctl.editCtrlShape(axis=charScale * 2.5)
			ctl.color = 'yellow'
		else:
			ctl.nmCreateController('plus_ctrlShape')
			ctl.editCtrlShape(axis=charScale * 2.0)
			ctl.color = 'yellow'

		# 2. Rename based on position after creation
		if i+1 == 1:
			ctl.name = f'{partElem}TopRbn{side}_loc'
			mc.setAttr(f'{ctl.shape}.overrideEnabled', 1)
			mc.setAttr(f'{ctl.shape}.overrideDisplayType', 1)
		elif i+1 == 2 or i+1 == 4:
			ctl.name = f'{partElem}MidRbn{side}_ctrl'
			mid_ctls.append(ctl)
		elif i+1 == len(cvs):
			ctl.name = f'{partElem}BtmRbn{side}_loc'
			mc.setAttr(f'{ctl.shape}.overrideEnabled', 1)
			mc.setAttr(f'{ctl.shape}.overrideDisplayType', 1)
		
		ctl.rotateOrder = rotOrder
		ctl.maSnap(cv)
		
		ctlZro_grp = rigTools.zroNewGrpWithOffset(ctl)


		if i+1 == 1 or i+1 == len(cvs):
			# Determine position label
			pos_label = "Top" if i+1 == 1 else "Btm"
			aimed_name = f'{partElem}{pos_label}RbnAimed{side}_grp'
			
			# 1. Create aimed group
			ribbonAimed_grp = autoRigCore.Null(aimed_name)
			ribbonAimed_grp.rotateOrder = rotOrder
			
			# 2. Snap to controller
			ribbonAimed_grp.maSnap(ctl)
			
			# 3. Insert into hierarchy: Offset -> Aimed -> Ctrl
			# Parent ctl under aimed group
			mc.parent(ctl.name, ribbonAimed_grp.name)
			# Parent aimed group under Offset group (which is ctlZro_grp[1])
			mc.parent(ribbonAimed_grp.name, ctlZro_grp[1])

			localAim_grps.append(aimed_name)



		ctlZro_grps.append(ctlZro_grp)
		mc.parent(ctlZro_grp[0], ctls_grp.name)
		
		ctls.append(ctl.name)

	num_cvs = len(cvs)
	original_cvs = cvs[:]

	d = num_cvs - 1 if d is None else d

	if kv_type == OPEN:
		kv, _ = core.knot_vector(OPEN, cvs, d)
		m_kv = kv[1:-1]
		m_cvs = cvs[:]
	else:
		m_cvs = [cvs[i - 1 % len(cvs)] for i in range(len(cvs))]
		for i in range(d):
			m_cvs.append(m_cvs[i])

		m_kv_len = len(m_cvs) + d - 1
		m_kv_interval = 1 / (m_kv_len - 2 * (d - 1) - 1)
		m_kv = [-m_kv_interval * (d - 1) * (1 - t / (m_kv_len - 1)) +
				(1 + m_kv_interval * (d - 1)) * t / (m_kv_len - 1) for t in range(m_kv_len)]

		kv, cvs = core.knot_vector(PERIODIC, cvs, d)

	m_cv_poss = om.MPointArray([mc.xform(obj, q=True, ws=True, t=True) for obj in m_cvs])
	form = KNOT_TO_FORM_INDEX[kv_type]
	is_2d = False
	rational = True
	data_creator = om.MFnNurbsCurveData()
	parent = data_creator.create()

	crv_fn = om.MFnNurbsCurve()
	crv_fn.create(m_cv_poss, m_kv, d, form, is_2d, rational, parent)

	if param_from_length:
		crv_len = crv_fn.length()
		params = []
		for i in range(num_joints):
			sample_len = crv_len * i / (num_joints - 1)
			if kv_type == PERIODIC:
				t = crv_fn.findParamFromLength((sample_len + crv_len * m_kv[2] * 0.5) % crv_len)
				params.append(t - m_kv[2] * 0.5)
			else:
				t = crv_fn.findParamFromLength(sample_len)
				params.append(t)
	else:
		params = [i / (num_joints - 1) for i in range(num_joints)]

	if kv_type == PERIODIC:
		params = [(kv[d + 1] * (d * 0.5 + 0.5)) * (1 - t) + t * (1 - kv[d + 1] * (d * 0.5 - 0.5))
				  for i, t in enumerate(params)]

	par_off_plugs = []
	trans_off_plugs = []
	sca_off_plugs = []

	for i, ctl in enumerate(ctls):
		par_off = mc.createNode('multMatrix', n=f'{partElem}ParOff{i+1:02d}{side}_mm')
		mc.connectAttr(f'{ctl}.worldMatrix[0]', f'{par_off}.matrixIn[0]')
		mc.connectAttr(f'{mod_grp.name}.worldInverseMatrix[0]', f'{par_off}.matrixIn[1]')

		par_off_plugs.append(f'{par_off}.matrixSum')

		trans_off = mc.createNode('pickMatrix', n=f'{partElem}Trans{i+1:02d}{side}_pm')
		mc.connectAttr(f'{par_off}.matrixSum', f'{trans_off}.inputMatrix')
		for attr in 'useRotate', 'useScale', 'useShear':
			mc.setAttr(f'{trans_off}.{attr}', False)

		trans_off_plugs.append(f'{trans_off}.outputMatrix')

		if use_scale and use_tangent or use_up:
			sca_off = mc.createNode('pickMatrix', n=f'{partElem}ScaleOff{i+1:02d}{side}_pm')
			mc.connectAttr(f'{par_off}.matrixSum', f'{sca_off}.inputMatrix')
			for attr in 'useRotate', 'useShear', 'useTranslate':
				mc.setAttr(f'{sca_off}.{attr}', False)

			sca_off_plugs.append(f'{sca_off}.outputMatrix')

	# Create detail group for sub-controllers
	detail_grp = autoRigCore.Null(f'{partElem}Detail{side}_grp')
	detail_grp.rotateOrder = rotOrder
	detail_grp.parent(ctls_grp.name)
	mc.matchTransform(detail_grp.name, ctls_grp.name)

	# Add Detail attribute to the first Mid controller found (on its Shape node)
	if mid_ctls:
		main_mid = mid_ctls[0]
		mid_shape = autoRigCore.Dag(main_mid.shape)
		mid_shape.addAttribute(attributeType='short', longName='Detail', minValue=0, maxValue=1, defaultValue=0, keyable=True)
		mid_shape.attr('Detail') >> detail_grp.attr('visibility')

	if debug:
		mid_shape.attr('Detail').value = 1


	jnts = []

	for i, param in enumerate(params):
		num = i + 1
		detail_name = f'{partElem}RbnDetail{num:02d}{side}' #... Add Ribbon name into detail 
		
		wts = core.de_boor(len(cvs), d, param, kv, tol=tol)
		if kv_type == PERIODIC:
			wts = get_consolidated_wts(wts, original_cvs, cvs)

		tangent_param = param + tangent_offset
		aim_vector = om.MVector(AXIS_VECTOR[aim_axis])
		if tangent_param > 1:
			tangent_param = param - 2 * tangent_offset
			aim_vector *= -1

		tangent_wts = core.de_boor(len(cvs), d, tangent_param, kv, tol=tol)
		if kv_type == PERIODIC:
			tangent_wts = get_consolidated_wts(tangent_wts, original_cvs, cvs)

		position_plug = None
		tangent_plug = None

		if use_position:
			position = create_wt_add_matrix(trans_off_plugs, wts, f'{detail_name}Pos_wam', tol=tol)
			position_plug = f'{position}.matrixSum'

			if not use_tangent and not use_up:
				pass 
			if use_tangent:
				tangent = create_wt_add_matrix(trans_off_plugs, tangent_wts, f'{detail_name}Tan_wam', tol=tol)
				tangent_plug = f'{tangent}.matrixSum'

		up_plug = f'{mod_grp.name}.worldMatrix[0]'

		if use_up:
			temp = mc.createNode('transform')
			mc.parent(temp, mod_grp.name)
			ori_con = mc.orientConstraint(original_cvs, temp, mo=False)[0]
			mc.setAttr(f'{ori_con}.interpType', 2)
			for j, wt in enumerate(wts):
				mc.setAttr(f'{ori_con}.{original_cvs[j]}W{j}', wt)

			up = create_wt_add_matrix(par_off_plugs, wts, f'{detail_name}Up_wam', tol=tol)

			temp_mat = om.MMatrix(mc.getAttr(f'{temp}.matrix'))
			up_inverse = om.MMatrix(mc.getAttr(f'{up}.matrixSum')).inverse()
			up_off_val = temp_mat * up_inverse

			up_off = mc.createNode('multMatrix', n=f'{detail_name}UpOff_mm')
			mc.setAttr(f'{up_off}.matrixIn[0]', list(up_off_val), type='matrix')
			mc.connectAttr(f'{up}.matrixSum', f'{up_off}.matrixIn[1]')

			up_plug = f'{up_off}.matrixSum'
			mc.delete(temp)

		aim = mc.createNode('aimMatrix', n=f'{detail_name}Aim_am')

		if position_plug:
			mc.connectAttr(position_plug, f'{aim}.inputMatrix')
		else:
			matrices = [om.MMatrix(mc.getAttr(top)) for top in trans_off_plugs]
			trans_wt_mat = get_weighted_translation_matrix(matrices, wts)
			mc.setAttr(f'{aim}.inputMatrix', trans_wt_mat, type='matrix')

		if tangent_plug:
			mc.connectAttr(f'{tangent}.matrixSum', f'{aim}.primaryTargetMatrix')
		else:
			matrices = [om.MMatrix(mc.getAttr(top)) for top in trans_off_plugs]
			trans_wt_mat = get_weighted_translation_matrix(matrices, tangent_wts)

			if position_plug:
				position_m = om.MMatrix(mc.getAttr(position_plug))
				tangent_offset_val = trans_wt_mat * position_m.inverse()
				tangent_off = mc.createNode('multMatrix', n=f'{detail_name}TanOff_mm')
				mc.setAttr(f'{tangent_off}.matrixIn[0]', tangent_offset_val, type='matrix')
				mc.connectAttr(position_plug, f'{tangent_off}.matrixIn[1]')
				mc.connectAttr(f'{tangent_off}.matrixSum', f'{aim}.primaryTargetMatrix')
			else:
				mc.setAttr(f'{aim}.primaryTargetMatrix', trans_wt_mat, type='matrix')

		if up_plug == f'{mod_grp.name}.worldMatrix[0]':
			mod_mat = mc.getAttr(up_plug)
			mc.setAttr(f'{aim}.secondaryTargetMatrix', mod_mat, type='matrix')
		else:
			mc.connectAttr(up_plug, f'{aim}.secondaryTargetMatrix')

		output_plug = f'{aim}.outputMatrix'
		mc.setAttr(f'{aim}.primaryInputAxis', *aim_vector)
		mc.setAttr(f'{aim}.secondaryInputAxis', *AXIS_VECTOR[up_axis])
		mc.setAttr(f'{aim}.secondaryMode', 2)
		mc.setAttr(f'{aim}.secondaryTargetVector', *AXIS_VECTOR[up_axis])

		if use_scale:
			scale_wam = create_wt_add_matrix(sca_off_plugs, wts, f'{detail_name}Scale_wam', tol=tol)
			scale_mm = mc.createNode('multMatrix', n=f'{detail_name}Scale_mm')
			mc.connectAttr(f'{scale_wam}.matrixSum', f'{scale_mm}.matrixIn[0]')
			mc.connectAttr(output_plug, f'{scale_mm}.matrixIn[1]')
			output_plug = f'{scale_mm}.matrixSum'

		#... CREATE RIBBON DETAIL CONTROL
		ribbon_ctrl = autoRigCore.Dag(f'{detail_name}_ctrl')
		ribbon_ctrl.nmCreateController('circle_ctrlShape')
		ribbon_ctrl.rotateOrder = rotOrder
		ribbonZro_grp = rigTools.zeroGroupNam(ribbon_ctrl)
		ribbon_ctrl.editCtrlShape(axis=charScale * 1.8)
		ribbon_ctrl.color = 'softBlue'
		
		# Apply aimMatrix via decomposeMatrix (offsetParentMatrix is prohibited by RULE.md)
		dcp = mc.createNode('decomposeMatrix', n=f'{detail_name}OPM_dcp')
		mc.connectAttr(output_plug, f'{dcp}.inputMatrix')
		mc.connectAttr(f'{dcp}.outputTranslate', f'{ribbonZro_grp.name}.translate')
		mc.connectAttr(f'{dcp}.outputRotate', f'{ribbonZro_grp.name}.rotate')
		mc.connectAttr(f'{dcp}.outputScale', f'{ribbonZro_grp.name}.scale')
		
		mc.parent(ribbonZro_grp.name, detail_grp.name)
		
		# CREATE JOINT
		mc.select(cl=True)
		jnt = autoRigCore.Joint(f'{detail_name}_pxyJnt')
		jnt.parent(ribbon_ctrl.name)
		mc.setAttr(f'{jnt.name}.translate', 0, 0, 0)
		mc.setAttr(f'{jnt.name}.rotate', 0, 0, 0)
		mc.setAttr(f'{jnt.name}.jointOrient', 0, 0, 0)
		
		if debug:
			jnt.attr('displayLocalAxis').value = 1
			jnt.attr('radius').value = charScale * 0.5
		else:
			jnt.attr('radius').value = charScale * 0.25
			
		
		jnt.attr('overrideEnabled').value = 1
		jnt.attr('overrideColor').value = 3
		
		# ribbon_ctrl.lockHideAttrLst('v')
		
		jnts.append(jnt.name)

	makeHingesParent = None
	subRbnJnt = None


	if jnts:
		b_lower = baseName.lower()
		if any(x in b_lower for x in ['up', 'top', 'front']):
			makeHingesParent = ctlZro_grps[-1]
			subRbnJnt = jnts[-1]


		elif any(x in b_lower for x in ['lwr', 'low', 'btm', 'down', 'back']):
			makeHingesParent = ctlZro_grps[0]
			subRbnJnt = jnts[0]


			# if num_joints == 5:
			# 	middleRig_grp = ctlZro_grps[2]
			# elif num_joints == 7:
			# 	middleRig_grp = ctlZro_grps[3]

		else:
			makeHingesParent = ctlZro_grps[-1]
			subRbnJnt = jnts[-1]


	# Return structure matching legacy ribbonRigExt expectations
	# makeHingesParent: (zroGrp, offsetGrp) tuple of the connecting CV controller
	# mod_grp.name: name of the top-level module group
	# subRbnJnt: the joint closest to the connecting hinge
	# jnts: list of all generated detail joints
	return makeHingesParent, mod_grp.name, subRbnJnt, jnts, ctlZro_grps, ctls, localAim_grps


def get_consolidated_wts(wts, original_cvs, cvs):
	consolidated_wts = {cv: 0 for cv in original_cvs}
	for j, wt in enumerate(wts):
		consolidated_wts[cvs[j]] += wt
	return [consolidated_wts[cv] for cv in original_cvs]


def create_wt_add_matrix(matrix_attrs, wts, name, tol=0.000001):
	wam = mc.createNode('wtAddMatrix', n=name)
	for matrix_attr, wt, i in zip(matrix_attrs, wts, range(len(matrix_attrs))):
		if wt < tol:
			continue
		mc.connectAttr(matrix_attr, f'{wam}.wtMatrix[{i}].matrixIn')
		mc.setAttr(f'{wam}.wtMatrix[{i}].weightIn', wt)
	return wam

def get_weighted_translation_matrix(matrices, wts):
	translation_m = om.MMatrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
	for m, wt in zip(matrices, wts):
		for i in 12, 13, 14:
			translation_m[i] += m[i] * wt
	return translation_m






#... Make elbow or knee move with ribbon
def deDoor_makeHigesMover(     nameSpace = ''  ,
				part = ''       , 
				side = 'LFT'    , 
				topName = ''    , 
				btmName = ''    , 
				charScale = ''  , 
				noTouch_grp = 'noTouch_grp'     ,
				moverPosition = 'lowerArmLFT_bJnt'  ,
				ctrl_grp = 'ctrl_grp'       ,
				alongAxis = 'y'
			 ):

	core.makeHeader('Start makeHigesMover')

	# naming = charName + elem


	# ctrl_grp = '%s%s' %(  naming , ctrl_grp   ) 
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
	RibbonLogger.info('\n**THIS IS A upper bJnt ---------------------------------**')
	RibbonLogger.info(str(btmName[0][1]))

	mtc.parentConMatrixGPT(rbnHinges_ctrl.name, btmName[0][1], mo=True, baseName=name +'Top'+ side)
	mtc.parentConMatrixGPT(rbnHinges_ctrl.name, topName[0][1], mo=True, baseName=name +'Btm'+ side)

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