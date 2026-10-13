#... Script for matrix weight relationship between main spine controllers
#... Based on Cole O'Brien de Boor spline logic and repository standards

'''
from function.rigging.de_boor.matrixSpine import eh_matrixSpine_03_weightRelationship as msw
reload(msw)

'''



import maya.cmds as mc
from function.rigging.autoRig.base import core
from function.rigging.constraint import matrixConstraint as mtc


def apply_multi_blend_matrix(target, drivers_and_weights, translate=True, rotate=True, scale=False, attr_holder=None):
	"""
	Apply a matrix-based parent blend constraint from multiple drivers to a target node.
	
	Args:
		target (str): Name of the driven node (e.g., 'L_mainCV02Zro_grp').
		drivers_and_weights (list): List of tuples/lists containing (driver_name, default_weight_float)
		translate (bool): If True, drives translation.
		rotate (bool): If True, drives rotation.
		scale (bool): If True, drives scale.
		attr_holder (str): Name of the controller node to hold the animatable weight attributes.
						   If None, we will try to find the corresponding '_ctrl' node,
						   or default to the target node.
	"""
	if not mc.objExists(target):
		mc.warning(f"Target node '{target}' does not exist. Skipping.")
		return None

	#... Validate drivers
	valid_drivers = []
	for driver, weight in drivers_and_weights:
		if mc.objExists(driver):
			valid_drivers.append((driver, weight))
		else:
			mc.warning(f"Driver node '{driver}' does not exist. Skipping driver.")

	if not valid_drivers:
		mc.warning(f"No valid drivers found for target '{target}'.")
		return None

	num_drivers = len(valid_drivers)
	base_name = core.check_name_style(name=target)[0]

	#... Try to find target controller to hold attributes if not specified
	if not attr_holder:
		#... Map target group to controller name (e.g., L_mainCV02Zro_grp -> L_mainCV02_ctrl)
		inferred_ctrl = target.replace("Zro_grp", "_ctrl").replace("_Zro", "_ctrl")
		if mc.objExists(inferred_ctrl):
			attr_holder = inferred_ctrl
		else:
			attr_holder = target

	#... Add weight attributes to the attr_holder
	weight_plugs = []
	for idx, (driver, default_weight) in enumerate(valid_drivers):
		driver_clean = core.check_name_style(name=driver)[0]
		attr_name = f"weight_{driver_clean}"

		#... Ensure attribute exists
		if not mc.attributeQuery(attr_name, node=attr_holder, exists=True):
			mc.addAttr(attr_holder, longName=attr_name, attributeType='float', defaultValue=default_weight, minValue=0.0, maxValue=1.0, keyable=True)

		weight_plugs.append(f"{attr_holder}.{attr_name}")

	#... Initialize Maya utility nodes
	decomposeMatrix = core.DecomposeMatrix(base_name)
	pickMatrix = core.PickMatrix(base_name)
	wtAddMatrix = core.WtAddMatrixWithChannal(f"{base_name}_multiBlend", num_cv=num_drivers, conn=True)

	#... Final MultMatrix converts world space blend back to local space of target's parent
	mmx_final = core.MultMatrix(f"{base_name}_final")

	#... For each driver, calculate offset and set up MultMatrix
	for idx, (driver, _) in enumerate(valid_drivers):
		#... Offset = TargetWorld * Inverse(DriverWorld)
		offMat = mtc._getLocalOffset(driver, target)

		mmx_src = core.MultMatrix(f"{base_name}_src{idx}")
		#... Set static offset matrix value
		mc.setAttr(f"{mmx_src.name}.matrixIn[0]", offMat, type='matrix')
		#... Connect driver's worldMatrix[0] to matrixIn[1]
		mc.connectAttr(f"{driver}.worldMatrix[0]", f"{mmx_src.name}.matrixIn[1]")

		#... Connect to wtAddMatrix and drive weights from attributes
		mc.connectAttr(f"{mmx_src.name}.matrixSum", f"{wtAddMatrix.name}.wtMatrix[{idx}].matrixIn")
		mc.connectAttr(weight_plugs[idx], f"{wtAddMatrix.name}.wt_{idx}")

	#... Connect blended matrix output to final MultMatrix
	mc.connectAttr(f"{wtAddMatrix.name}.matrixSum", f"{mmx_final.name}.matrixIn[0]")

	#... Parent space compensation
	parent = mc.listRelatives(target, parent=True)
	if parent:
		mc.connectAttr(f"{parent[0]}.worldInverseMatrix[0]", f"{mmx_final.name}.matrixIn[1]")

	#... Connect to pickMatrix to isolate Translate / Rotate / Scale channels
	mc.connectAttr(f"{mmx_final.name}.matrixSum", f"{pickMatrix.name}.inputMatrix")
	mc.connectAttr(f"{pickMatrix.name}.outputMatrix", f"{decomposeMatrix.name}.inputMatrix")

	if not translate:
		mc.setAttr(f"{pickMatrix.name}.useTranslate", False)
	if not rotate:
		mc.setAttr(f"{pickMatrix.name}.useRotate", False)
	if not scale:
		mc.setAttr(f"{pickMatrix.name}.useScale", False)

	#... Drive translation and scale
	if translate:
		mc.connectAttr(f"{decomposeMatrix.name}.outputTranslate", f"{target}.translate", force=True)
	if scale:
		mc.connectAttr(f"{decomposeMatrix.name}.outputScale", f"{target}.scale", force=True)

	#... Drive rotation using cycle-free quaternion math
	if rotate:
		target_eulerToQuat = core.EulerToQuat(base_name)
		target_quatInvert = core.QuatInvert(base_name)
		target_quatProd = core.QuatProd(base_name)
		target_quatToEuler = core.QuatToEuler(base_name)

		target_obj = core.Dag(target)
		if target_obj.type == 'joint':
			mc.connectAttr(f"{target}.jointOrient", f"{target_eulerToQuat.name}.inputRotate")

		mc.connectAttr(f"{target_eulerToQuat.name}.outputQuat", f"{target_quatInvert.name}.inputQuat")
		mc.connectAttr(f"{decomposeMatrix.name}.outputQuat", f"{target_quatProd.name}.input1Quat")
		mc.connectAttr(f"{target_quatInvert.name}.outputQuat", f"{target_quatProd.name}.input2Quat")
		mc.connectAttr(f"{target_quatProd.name}.outputQuat", f"{target_quatToEuler.name}.inputQuat")

		#... Connect output rotate
		mc.connectAttr(f"{target_quatToEuler.name}.outputRotate", f"{target}.rotate", force=True)

		#... Match target rotate order to the first driver and drive quatToEuler rotateOrder
		first_driver = valid_drivers[0][0]
		driver_rotOrder = mc.getAttr(f"{first_driver}.rotateOrder")
		mc.setAttr(f"{target}.rotateOrder", driver_rotOrder)
		mc.connectAttr(f"{target}.rotateOrder", f"{target_quatToEuler.name}.inputRotateOrder")

		#... Break temporary connection for jointOrient to prevent cycle evaluation
		mc.disconnectAttr(f"{target_quatInvert.name}.outputQuat", f"{target_quatProd.name}.input2Quat")
		target_eulerToQuat.deleteName()

	print(f"#... Matrix Weight Relationship Setup Complete for: {target}")
	return {
		"wtAddMatrix": wtAddMatrix.name,
		"decomposeMatrix": decomposeMatrix.name,
		"pickMatrix": pickMatrix.name,
		"finalMultMatrix": mmx_final.name
	}


def setup_relationships(relationship_dict, translate=True, rotate=True, scale=False):
	"""
	Setup multiple matrix-based weight relationships using a configuration dictionary.
	
	Args:
		relationship_dict (dict): Dictionary mapping target driven node to list of (driver, weight)
								  Example:
								  {
									  'L_mainCV02Zro_grp': [
										  ('L_mainCV01_ctrl', 0.5),
										  ('L_mainCV03_ctrl', 0.5)
									  ]
								  }
		translate (bool): Drive translation.
		rotate (bool): Drive rotation.
		scale (bool): Drive scale.
	"""
	results = {}
	for target, drivers in relationship_dict.items():
		print(f"#... Processing relationships for target node: {target}")
		res = apply_multi_blend_matrix(
			target=target,
			drivers_and_weights=drivers,
			translate=translate,
			rotate=rotate,
			scale=scale
		)
		if res:
			results[target] = res
	return results




'''



from function.rigging.de_boor.matrixSpine import eh_matrixSpine_03_weightRelationship as msw
reload(msw)

msw.relationship_dict = {
	'L_mainCV02Zro_grp': [
		('L_mainCV01_ctrl', 0.5),
		('L_mainCV03_ctrl', 0.5)
	],
	'L_mainCV04Zro_grp': [
		('L_mainCV03_ctrl', 0.5),
		('L_mainCV05_ctrl', 0.5)
	]
}


relationship_dict = {
	'C_mainCV02Zro_grp': [
		('C_mainCV01_ctrl', 0.5),
		('C_mainCV03_ctrl', 0.5)
	]
}














relationship_dict = {
	'L_mainCV04Zro_grp': [
		('L_mainCV01_ctrl', 0.1),
		('L_mainCV05_ctrl', 0.9)
	],
	'L_mainCV03Zro_grp': [
		('L_mainCV01_ctrl', 0.4),
		('L_mainCV05_ctrl', 0.6)
	],
	'L_mainCV02Zro_grp': [
		('L_mainCV01_ctrl', 0.9),
		('L_mainCV05_ctrl', 0.1)
	]
}







relationship_dict = {
	#... CV05 วิ่งตาม CV01 แบบ 1:1
	'L_mainCV05Zro_grp': [
		('L_mainCV01_ctrl', 1.0),
		('L_mainCV01_ctrl', 1.0)
	],
	#... CV04 แชร์น้ำหนัก (01 = 10% | 05 = 90%)
	'L_mainCV04Zro_grp': [
		('L_mainCV01_ctrl', 0.1),
		('L_mainCV05_ctrl', 0.9)
	],
	#... CV03 แชร์น้ำหนัก (01 = 40% | 05 = 60%)
	'L_mainCV03Zro_grp': [
		('L_mainCV01_ctrl', 0.4),
		('L_mainCV05_ctrl', 0.6)
	],
	#... CV02 แชร์น้ำหนัก (01 = 90% | 05 = 10%)
	'L_mainCV02Zro_grp': [
		('L_mainCV01_ctrl', 0.9),
		('L_mainCV05_ctrl', 0.1)
	]
}





#... ribbon like behavior 4 point
relationship_dict = {
    #... 1. CV05 วิ่งตาม CV01 แบบ 1:1
    'L_mainCV05Zro_grp': [
        ('L_mainCV01_ctrl', 1.0)
    ],
    #... 2. CV03 ตาม (01 = 40% | 05 = 60%)
    'L_mainCV03Zro_grp': [
        ('L_mainCV01_ctrl', 0.4),
        ('L_mainCV05_ctrl', 0.6)
    ],
    #... 3. CV02 ตาม (01 = 50% | 03 = 50%) -> ได้สัดส่วนพื้นที่เริ่มต้น 01/05 = 70/30
    #... และเวลาขยับ CV03 จะตาม 50%
    'L_mainCV02Zro_grp': [
        ('L_mainCV01_ctrl', 0.5),
        ('L_mainCV03_ctrl', 0.5)
    ],
    #... 4. CV04 ตาม (05 = 50% | 03 = 50%) -> ได้สัดส่วนพื้นที่เริ่มต้น 01/05 = 20/80
    #... และเวลาขยับ CV03 จะตาม 50%
    'L_mainCV04Zro_grp': [
        ('L_mainCV05_ctrl', 0.5),
        ('L_mainCV03_ctrl', 0.5)
    ]
}






#... รันคำสั่งสร้างความสัมพันธ์
setup_relationships(relationship_dict, translate=True, rotate=True, scale=False)


'''