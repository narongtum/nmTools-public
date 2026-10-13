# ------------------------------------------------------------------------------
# CANCLE FOR NOW IS NOT WORK
# ------------------------------------------------------------------------------

import math
import maya.cmds as mc

from function.framework.reloadWrapper import reloadWrapper as reload
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

class RibbonLogger(logger.MayaLogger):
	LOGGER_NAME = "MatrixRibbon"

class CurveException(BaseException):
	""" Raised to indicate invalid curve parameters. """

# ==============================================================================
# DE BOOR MATH FUNCTIONS (from matrixSpine_01_setup.py)
# ==============================================================================
def defaultKnots(count, degree=3):
	knots = [0 for i in range(degree)] + [i for i in range(count - degree + 1)]
	knots += [count - degree for i in range(degree)]
	return [float(knot) for knot in knots]


def pointOnCurveWeights(cvs, t, degree, knots=None):
	order = degree + 1
	if len(cvs) <= degree:
		raise CurveException('Curves of degree %s require at least %s cvs' % (degree, degree + 1))

	knots = knots or defaultKnots(len(cvs), degree)
	if len(knots) != len(cvs) + order:
		raise CurveException('Not enough knots provided. Curves with %s cvs must have a knot vector of length %s. '
							 'Received a knot vector of length %s: %s. '
							 'Total knot count must equal len(cvs) + degree + 1.' % (len(cvs), len(cvs) + order,
																					 len(knots), knots))

	_cvs = cvs
	cvs = [i for i in range(len(cvs))]

	min_val = knots[order] - 1
	max_val = knots[len(knots) - 1 - order] + 1
	t = (t * (max_val - min_val)) + min_val

	segment = degree
	for index, knot in enumerate(knots[order:len(knots) - order]):
		if knot <= t:
			segment = index + order

	cvs = [cvs[j + segment - degree] for j in range(0, degree + 1)]
	cvWeights = [{cv: 1.0} for cv in cvs]
	
	for r in range(1, degree + 1):
		for j in range(degree, r - 1, -1):
			right = j + 1 + segment - r
			left = j + segment - degree
			alpha = (t - knots[left]) / (knots[right] - knots[left])

			weights = {}
			for cv, weight in cvWeights[j].items():
				weights[cv] = weight * alpha

			for cv, weight in cvWeights[j - 1].items():
				if cv in weights:
					weights[cv] += weight * (1 - alpha)
				else:
					weights[cv] = weight * (1 - alpha)

			cvWeights[j] = weights

	cvWeights = cvWeights[degree]
	return [[_cvs[index], weight] for index, weight in cvWeights.items()]


def tangentOnCurveWeights(cvs, t, degree, knots=None):
	order = degree + 1
	if len(cvs) <= degree:
		raise CurveException('Curves of degree %s require at least %s cvs' % (degree, degree + 1))

	knots = knots or defaultKnots(len(cvs), degree)
	if len(knots) != len(cvs) + order:
		raise CurveException('Not enough knots provided.')

	min_val = knots[order] - 1
	max_val = knots[len(knots) - 1 - order] + 1
	t = (t * (max_val - min_val)) + min_val

	segment = degree
	for index, knot in enumerate(knots[order:len(knots) - order]):
		if knot <= t:
			segment = index + order

	_cvs = cvs
	cvs = [i for i in range(len(cvs))]

	degree = degree - 1
	qWeights = [{cv: 1.0} for cv in range(0, degree + 1)]

	for r in range(1, degree + 1):
		for j in range(degree, r - 1, -1):
			right = j + 1 + segment - r
			left = j + segment - degree
			alpha = (t - knots[left]) / (knots[right] - knots[left])

			weights = {}
			for cv, weight in qWeights[j].items():
				weights[cv] = weight * alpha

			for cv, weight in qWeights[j - 1].items():
				if cv in weights:
					weights[cv] += weight * (1 - alpha)
				else:
					weights[cv] = weight * (1 - alpha)

			qWeights[j] = weights
	weights = qWeights[degree]

	cvWeights = []
	for j in range(0, degree + 1):
		weight = weights[j]
		cv0 = j + segment - degree
		cv1 = j + segment - degree - 1
		alpha = weight * (degree + 1) / (knots[j + segment + 1] - knots[j + segment - degree])
		cvWeights.append([cvs[cv0], alpha])
		cvWeights.append([cvs[cv1], -alpha])

	return [[_cvs[index], weight] for index, weight in cvWeights]


# ==============================================================================
# MAIN MATRIX RIBBON FUNCTION
# ==============================================================================
def ribbonRigExt(
	nameSpace='', 
	width=10, 
	numJoints=5, 
	side='LFT',
	jointTop='upperLegLFT_tmpJnt',
	jointBtm='lowerLegLFT_tmpJnt',
	part='upLeg',
	charScale=1,
	noTouch_grp='noTouch_grp',
	showInfo=True,
	upPlana='',
	ctrl_grp='ribbon_grp',
	alongAxis='y',
	pinMethod='matrix',
	debug=False,
	numDetail=3  # User request: 3 or 5 detail controllers
):
	"""
	De Boor Matrix Spline Ribbon AutoRig System.
	Operates as a cycle-free drop-in replacement for the classic NURBS Ribbon.
	"""
	core.makeHeader('Start Matrix Ribbon function')
	RibbonLogger.info(f'Initializing Matrix Ribbon (numDetail: {numDetail})')

	noTouch_grp = f'{nameSpace}{noTouch_grp}'
	ribbonCollect_grp = core.Null(f'{part}MatrixRibbon{side}_grp')
	
	partElem = nameSpace + part
	armRotOrder = 'yxz'

	# Axis Orientation Parsing...
	axis_config = {
		'y': {
			'LFT': {'upArm': 'x-', 'lwrArm': 'x-', 'upLeg': 'z+', 'lwrLeg': 'z+'},
			'RGT': {'upArm': 'x+', 'lwrArm': 'x+', 'upLeg': 'z-', 'lwrLeg': 'z-'}
		},
		'x': {
			'LFT': {'upArm': 'z-', 'lwrArm': 'z-', 'upLeg': 'y+', 'lwrLeg': 'y+'},
			'RGT': {'upArm': 'z+', 'lwrArm': 'z+', 'upLeg': 'y-', 'lwrLeg': 'y-'}
		}
	}

	if part in ['upArm', 'lwrArm', 'upLeg', 'lwrLeg'] and alongAxis in axis_config and side in axis_config[alongAxis]:
		if part in axis_config[alongAxis][side]:
			upPlana = axis_config[alongAxis][side][part]
	else:
		if not upPlana:
			RibbonLogger.critical('Please specify the up axis.')
			return False

	vector_config = {
		'x-': {'aim': (0,1,0),  'up': (-1,0,0), 'mid': (-10,0,0),    'sup': (-10,0,0)},
		'x+': {'aim': (0,-1,0), 'up': (0,0,-1), 'mid': (0,10,0),     'sup': (10,0,0)},
		'z+': {'aim': (0,1,0),  'up': (0,0,1),  'mid': (0,0,10),     'sup': (0,0,10)},
		'z-': {'aim': (0,1,0),  'up': (0,0,-1), 'mid': (0,0,10),     'sup': (0,0,-10)},
		'y+': {'aim': (0,1,0),  'up': (0,0,-1), 'mid': (0,0,10),     'sup': (0,10,0)},
		'y-': {'aim': (0,1,0),  'up': (0,0,-1), 'mid': (0,0,10),     'sup': (0,-10,0)}
	}

	if upPlana in vector_config:
		aimVector = vector_config[upPlana]['aim']
		upVector = vector_config[upPlana]['up']
	else:
		aimVector = (0,1,0)
		upVector = (0,0,1)

	# ---------------------------------------------------------
	# 1. MOVER SETUP: Top & Bottom Extrema
	# ---------------------------------------------------------
	topName = f'{part}TopRbnMov{side}'
	btmName = f'{part}BtmRbnMov{side}'

	ribbonTopMov_ctrl = core.Dag(f'{topName}_ctrl')
	ribbonTopMov_ctrl.nmCreateController('plus_ctrlShape')
	ribbonTopMov_ctrl.editCtrlShape(axis=charScale * 2)
	ribbonTopMov_ctrl.color = 'yellow'

	tempA_jnt = rigTools.jointAt(jointTop)
	tempA_jnt.freeze()
	if upPlana in ['x+', 'x-']:
		tempA_jnt.setRotate((0, 0, 90))

	ribbonTopMov_ctrl.maSnap(tempA_jnt)
	tempA_jnt.deleteName()
	
	ribbonTopMovZro_grp = rigTools.zroNewGrpWithOffset(ribbonTopMov_ctrl)
	core.parentConstraint(jointTop, ribbonTopMovZro_grp[0], mo=True)
	
	# Same for Bottom Mover
	ribbonBtmMov_ctrl = core.Dag(f'{btmName}_ctrl')
	ribbonBtmMov_ctrl.nmCreateController('plus_ctrlShape')
	ribbonBtmMov_ctrl.editCtrlShape(axis=charScale * 2)
	ribbonBtmMov_ctrl.color = 'yellow'

	tempB_jnt = rigTools.jointAt(jointBtm)
	tempB_jnt.freeze()
	if upPlana in ['x+', 'x-']:
		tempB_jnt.setRotate((0, 0, 90))

	ribbonBtmMov_ctrl.maSnap(tempB_jnt)
	tempB_jnt.deleteName()

	ribbonBtmMovZro_grp = rigTools.zroNewGrpWithOffset(ribbonBtmMov_ctrl)
	core.parentConstraint(jointBtm, ribbonBtmMovZro_grp[0], mo=True)

	# ---------------------------------------------------------
	# 2. MOVER SETUP: Mid Interpolated Mover (50% blend)
	# ---------------------------------------------------------
	name = partElem + 'Mid'
	ribbonMid_ctrl = core.Dag(name + 'Rbn' + side + '_ctrl')
	ribbonMid_ctrl.nmCreateController('squarePlain_ctrlShape')
	ribbonMid_ctrl.editCtrlShape(axis=charScale * 2.3)
	ribbonMid_ctrl.rotateOrder = armRotOrder
	ribbonMid_ctrl.color = 'yellow'

	# Add attributes
	for attr in ('sx','sy','sz'):
		ribbonMid_ctrl.attr(attr).lockHide()
	
	ribbonMid_ctrl.addAttribute(longName='Bar', niceName='-', at='enum', en='Twist', keyable=True)
	ribbonMid_ctrl.addAttribute(longName='Upper_Twist', defaultValue=0, keyable=True)
	ribbonMid_ctrl.addAttribute(longName='Lower_Twist', defaultValue=0, keyable=True)
	ribbonMid_ctrl.addAttribute(attributeType='short', longName='Detail', minValue=0, maxValue=1, defaultValue=0, keyable=True)
	ribbonMid_ctrl.addAttribute(attributeType='short', longName='Auto_Twist', minValue=0, maxValue=1, defaultValue=0, keyable=True)

	ribbonMidZro_tuple = rigTools.zroNewGrpWithOffset(ribbonMid_ctrl)
	ribbonMidZro_grp = ribbonMidZro_tuple[0]

	# Position via wtAddMatrix (50/50 blend)
	wt_add_midpos = core.WtAddMatrixWithChannal(f"{ribbonMid_ctrl.name}_pos_wtAdd", 2)
	mc.connectAttr(f"{ribbonTopMov_ctrl.name}.worldMatrix[0]", f"{wt_add_midpos.name}.wtMatrix[0].matrixIn")
	mc.setAttr(f"{wt_add_midpos.name}.wt_0", 0.5)
	mc.connectAttr(f"{wt_add_midpos.name}.wt_0", f"{wt_add_midpos.name}.wtMatrix[0].weightIn")

	mc.connectAttr(f"{ribbonBtmMov_ctrl.name}.worldMatrix[0]", f"{wt_add_midpos.name}.wtMatrix[1].matrixIn")
	mc.setAttr(f"{wt_add_midpos.name}.wt_1", 0.5)
	mc.connectAttr(f"{wt_add_midpos.name}.wt_1", f"{wt_add_midpos.name}.wtMatrix[1].weightIn")

	# Aimed Grp for Matrix Aim setup
	ribbonMidAim_grp = core.Null(f"{partElem}MidAimed{side}_grp")
	mc.parent(ribbonMidZro_grp, ribbonMidAim_grp.name)

	# Aim Setup
	midAimUp_loc = core.Locator(f"{partElem}MidAimUp{side}_loc")
	midAimUp_loc.attr('v').value = showInfo
	mc.parent(midAimUp_loc.name, ribbonTopMovZro_grp[0])  # Use Top's space for stable up vector
	
	# Determine Mid Up Value
	midUpValue = (0, 10, 0) # Default
	if upPlana in ['x+', 'x-']:
		midUpValue = (0, 10, 0)
	elif upPlana == 'z+' and alongAxis == 'y':
		midUpValue = (0, 0, 10)
	elif upPlana == 'z-' and alongAxis == 'y':
		midUpValue = (0, 0, 10)
	elif upPlana == 'z-' and alongAxis == 'x':
		midUpValue = (0, 10, 0)
	elif upPlana == 'y+' and alongAxis == 'x':
		midUpValue = (0, 0, 10)
	elif upPlana == 'y-' and alongAxis == 'x':
		midUpValue = (0, 0, 10)
	midAimUp_loc.setTranslate(midUpValue)

	# Adjust Mid Controller shape orientation based on axes
	if upPlana == 'y-' and alongAxis == 'x':
		ribbonMid_ctrl.rotateShape(rotate=(0, 0, 90))
	if upPlana in ['x+', 'x-']:
		ribbonMid_ctrl.rotateShape(rotate=(0, 0, 90))
		
	# Determine Correct Aim Vector for Mid to prevent flipping on Lower Arm twist
	midAimVec = aimVector
	if upPlana == 'x+':
		midAimVec = (-1, 0, 0)
	elif upPlana == 'x-':
		midAimVec = (1, 0, 0)
	elif alongAxis == 'y' and upPlana in ['z+', 'z-']:
		midAimVec = (-1, 0, 0) if upPlana == 'z+' else (1, 0, 0)

	decomp_midpos = core.DecomposeMatrix(f"{partElem}MidPos{side}_dcmp")
	mc.connectAttr(f"{wt_add_midpos.name}.matrixSum", f"{decomp_midpos.name}.inputMatrix")
	mc.connectAttr(f"{decomp_midpos.name}.outputTranslate", f"{ribbonMidAim_grp.name}.translate")
	
	# Matrix Aim
	mtc.eh_aimMatrixConstraint(
		aim_object=ribbonTopMov_ctrl.name,
		up_object=midAimUp_loc.name,
		target=ribbonMidAim_grp.name,
		aimVector=midAimVec,
		upVector=(0, 1, 0),
		mo=False,
		baseName=f"{name}Aim{side}"
	)

	# Combine all CV matrices (Top, Mid, Bottom)
	cvMatrices = [
		f"{ribbonTopMov_ctrl.name}.worldMatrix[0]",
		f"{ribbonMid_ctrl.name}.worldMatrix[0]",
		f"{ribbonBtmMov_ctrl.name}.worldMatrix[0]"
	]

	degree = 3 if len(cvMatrices) > 3 else 2

	# ---------------------------------------------------------
	# 3. SPLINE GENERATION (De Boor Matrix)
	# ---------------------------------------------------------
	rbn_ctrls = []
	rbn_zros = []
	rbn_bjnts = []

	for i in range(numJoints):
		num_name = f"{(i+1):02d}"
		name_prefix = f"{part}Rbn{num_name}{side}"
		
		# Distribute Detail Controllers between 0 and 1, exclusive of edges
		t = float(i + 1) / (numJoints + 1)
		
		# CV Controller
		sub_ctrl = core.Dag(f"{name_prefix}_ctrl")
		sub_ctrl.nmCreateController('circle_ctrlShape')
		
		# Capture the actually generated zero group name from returns
		sub_zro_tuple = rigTools.zroNewGrpWithOffset(sub_ctrl)
		sub_zro = sub_zro_tuple[0]
		
		sub_ctrl.editCtrlShape(axis=charScale * 1.8)
		
		# Rotate shape to lay flat against the ribbon surface (Legacy orientation logic)
		if upPlana == 'z+' and alongAxis == 'y':
			sub_ctrl.rotateShape(rotate=(0,0,0))
		elif upPlana == 'z-' and alongAxis == 'x':
			sub_ctrl.rotateShape(rotate=(0,0,90))
		elif upPlana == 'x-':
			sub_ctrl.rotateShape(rotate=(0,0,-90))
		elif upPlana == 'y+' and alongAxis == 'x':
			sub_ctrl.rotateShape(rotate=(0,0,90))
		elif upPlana == 'y-' and alongAxis == 'x':
			sub_ctrl.rotateShape(rotate=(0,0,90))
		elif upPlana == 'x+':
			pass
			
		sub_ctrl.color = 'softBlue'

		# Bind Joint
		b_jnt = core.Joint()
		b_jnt.name = f"{name_prefix}_rbnBJnt"
		b_jnt.attr('radius').value = 0.5
		if debug:
			b_jnt.attr('radius').value = 0.75
			b_jnt.attr('displayLocalAxis').value = True

		# 3.1 Point Weights
		pWeights = pointOnCurveWeights(cvMatrices, t, degree=degree)
		pt_wtNode = core.WtAddMatrixWithChannal(f"{name_prefix}_point_wtAdd", len(cvMatrices))
		
		for idx, (mtx_attr, wt) in enumerate(pWeights):
			mc.connectAttr(mtx_attr, f"{pt_wtNode.name}.wtMatrix[{idx}].matrixIn")
			mc.setAttr(f"{pt_wtNode.name}.wt_{idx}", wt)
			mc.connectAttr(f"{pt_wtNode.name}.wt_{idx}", f"{pt_wtNode.name}.wtMatrix[{idx}].weightIn")

		# 3.2 Tangent Weights
		tWeights = tangentOnCurveWeights(cvMatrices, t, degree=degree)
		tan_wtNode = core.WtAddMatrixWithChannal(f"{name_prefix}_tangent_wtAdd", len(cvMatrices) + 4)
		
		for idx, (mtx_attr, wt) in enumerate(tWeights):
			mc.connectAttr(mtx_attr, f"{tan_wtNode.name}.wtMatrix[{idx}].matrixIn")
			mc.setAttr(f"{tan_wtNode.name}.wt_{idx}", wt)
			mc.connectAttr(f"{tan_wtNode.name}.wt_{idx}", f"{tan_wtNode.name}.wtMatrix[{idx}].weightIn")

		# 3.25 Create stable Up Object (Locator) floating above the arm
		up_loc_zro = core.Null(f"{name_prefix}_upLocZro")
		up_loc_zro.parent(ribbonCollect_grp.name)
		
		up_loc = core.Locator(f"{name_prefix}_upLoc")
		up_loc.parent(up_loc_zro.name)
		if not debug:
			up_loc.attr('v').value = False
			
		# Offset the locator 10 units away so it floats exactly along the Up Axis
		up_loc.setTranslate((upVector[0]*10, upVector[1]*10, upVector[2]*10))
		
		# Drive ZRO position from the raw spline point (pt_wtNode) to prevent cycle!
		decomp = mc.createNode('decomposeMatrix', name=f"{name_prefix}_ptDecomp")
		mc.connectAttr(f"{pt_wtNode.name}.matrixSum", f"{decomp}.inputMatrix")
		mc.connectAttr(f"{decomp}.outputTranslate", f"{up_loc_zro.name}.translate")
		
		if part.startswith('up'):
			# Upper limbs should NOT twist when the elbow/knee bends.
			# Lock the Up Vector entirely to the Top Mover (Shoulder/Hip).
			mc.orientConstraint(ribbonTopMov_ctrl.name, up_loc_zro.name, mo=False)
		else:
			# Lower limbs need to interpolate twist from elbow to wrist.
			target_nodes = [attr.split('.')[0] for attr, w in pWeights]
			ori_cons = mc.orientConstraint(target_nodes, up_loc_zro.name, mo=False)[0]
			mc.setAttr(f"{ori_cons}.interpType", 2) # Shortest (Quaternion interpolation)
			
			for attr, wt in pWeights:
				target_node = attr.split('.')[0]
				mc.orientConstraint(target_node, up_loc_zro.name, edit=True, weight=wt)

		# 3.3 Aim Matrix node
		aim_node = core.AimMatrix(f"{name_prefix}_aimMat")
		mc.connectAttr(f"{pt_wtNode.name}.matrixSum", f"{aim_node.name}.inputMatrix")
		mc.connectAttr(f"{tan_wtNode.name}.matrixSum", f"{aim_node.name}.primaryTargetMatrix")
		
		mc.setAttr(f"{aim_node.name}.primaryMode", 1)
		mc.setAttr(f"{aim_node.name}.primaryInputAxisX", aimVector[0])
		mc.setAttr(f"{aim_node.name}.primaryInputAxisY", aimVector[1])
		mc.setAttr(f"{aim_node.name}.primaryInputAxisZ", aimVector[2])
		
		mc.setAttr(f"{aim_node.name}.secondaryMode", 2) # Mode 2: Aim At Target Position
		mc.setAttr(f"{aim_node.name}.secondaryInputAxisX", upVector[0])
		mc.setAttr(f"{aim_node.name}.secondaryInputAxisY", upVector[1])
		mc.setAttr(f"{aim_node.name}.secondaryInputAxisZ", upVector[2])
		mc.connectAttr(f"{up_loc.name}.worldMatrix[0]", f"{aim_node.name}.secondaryTargetMatrix")
		# 3.4 Discard Scale to prevent shearing
		pick_mat = mc.createNode('pickMatrix', name=f"{name_prefix}_pickMat")
		mc.connectAttr(f"{aim_node.name}.outputMatrix", f"{pick_mat}.inputMatrix")
		mc.setAttr(f"{pick_mat}.useScale", False)
		mc.setAttr(f"{pick_mat}.useShear", False)
		
		# Drive sub ctrl ZRO group and prevent Double Transformation
		# Multiplies spline output matrix by ctrl_grp's inverse to get local space matrix
		mult_to_local_mat = mc.createNode('multMatrix', name=f"{name_prefix}_localMtx_mult")
		mc.connectAttr(f"{pick_mat}.outputMatrix", f"{mult_to_local_mat}.matrixIn[0]")
		mc.connectAttr(f"{ctrl_grp}.worldInverseMatrix[0]", f"{mult_to_local_mat}.matrixIn[1]")
		
		decomp_mat = core.DecomposeMatrix(f"{name_prefix}_dcmp")
		mc.connectAttr(f"{mult_to_local_mat}.matrixSum", f"{decomp_mat.name}.inputMatrix")
		
		# Reset any transformation on the zero group before driving
		mc.xform(sub_zro, matrix=[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1], os=True)
		
		mc.connectAttr(f"{decomp_mat.name}.outputTranslate", f"{sub_zro}.translate")
		mc.connectAttr(f"{decomp_mat.name}.outputRotate", f"{sub_zro}.rotate")

		# Hook up visibility (Detail Attribute)
		mc.connectAttr(f"{ribbonMid_ctrl.name}.Detail", f"{sub_zro}.visibility")

		# Drive Binding Joint
		# 1. Snap to the Detail Controller's zero group so it aligns perfectly with the spline
		b_jnt.maSnap(sub_zro)
		# 2. Parent to the main bind joint chain
		mc.parent(b_jnt.name, jointTop)
		# 3. Freeze transformations so translate and rotate become 0,0,0 while absorbing jointOrient
		mc.makeIdentity(b_jnt.name, apply=True, t=1, r=1, s=1, n=0, pn=1)
		# 4. Matrix Constrain with mo=True. Since they are snapped, offset is essentially 0, keeping rotate values clean.
		mtc.parentConMatrixGPT(sub_ctrl.name, b_jnt.name, mo=True, baseName=name_prefix)

		rbn_ctrls.append(sub_ctrl.name)
		rbn_zros.append(sub_zro)
		rbn_bjnts.append(b_jnt.name)

	# Cleanup & Hierarchy Parent
	mc.parent([ribbonTopMovZro_grp[0], ribbonMidAim_grp.name, ribbonBtmMovZro_grp[0]], ribbonCollect_grp.name)
	for zro_name in rbn_zros:
		mc.parent(zro_name, ctrl_grp)
		
	# Export BJnts to noTouch (Removed: rbnBJnt are now parented under jointTop instead)
	# mc.parent(rbn_bjnts, noTouch_grp)

	# Compatibility for makeHigesMover
	if part[:2] == 'up':
		makeHingesParent = ribbonBtmMovZro_grp
		subRbnJnt = rbn_bjnts[-1]
	elif part[:3] == 'lwr':
		makeHingesParent = ribbonTopMovZro_grp
		subRbnJnt = rbn_bjnts[0]
	else:
		RibbonLogger.warning("Can't return value up or lwr please check.")
		makeHingesParent = ribbonBtmMovZro_grp # Fallback if part name isn't standard
		subRbnJnt = rbn_bjnts[-1]

	allRibbonGrp = [ribbonTopMovZro_grp[0], ribbonMidAim_grp.name, ribbonBtmMovZro_grp[0]]

	core.makeHeader('End Matrix Ribbon function')
	return makeHingesParent, allRibbonGrp, subRbnJnt





# Benefical of ribbon functon for make elbow or knee move
def makeHigesMover( 	nameSpace = ''	,
				part = ''		, 
				side = 'LFT' 	, 
				btmName = ''	, 
				topName = ''  	, 
				charScale = '' 	, 
				noTouch_grp = 'noTouch_grp' 	,
				moverPosition = 'lowerArmLFT_bJnt'	,
				ctrl_grp = 'ctrl_grp'		,
				alongAxis = 'y'
			 ):

	core.makeHeader('Start makeHigesMover')

	# naming = charName + elem


	# ctrl_grp = '%s%s' %(	naming , ctrl_grp	) 
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
			rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 0 )	)
		elif part == 'arm':
			rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 )	)

	elif alongAxis == 'x':
		if part == 'leg':
			rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 )	)
			if side == 'RGT':
				pass
		elif part == 'arm':
			rbnHinges_ctrl.rotateShape( rotate = ( 0 , 0 , 90 )	)


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