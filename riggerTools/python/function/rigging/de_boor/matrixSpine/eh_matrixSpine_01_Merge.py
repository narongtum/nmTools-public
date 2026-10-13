#... 24.02.Feb.13.Tue.09_De boor matrix spine_Chris bag
#... 24.05.May.07.Tue.10_Change attr link to wtMatrix
#... 2026.08.19_Modular Function & Zro_grp wrapping by Antigravity

"""
===============================================================================
De Boor Matrix Spline Rig Setup (Spine / Tentacle / Neck)
===============================================================================

Overview:
    Procedural Matrix Spline spine rig using a modified de Boor B-spline algorithm.
    Evaluates spline positions and tangent orientations mathematically through native 
    Maya matrix nodes (`wtAddMatrix`, `aimMatrix`, `pickMatrix`, `multMatrix`), 
    eliminating follicle flips, up-vector gimbal lock, and cycle dependencies.

Mathematical Foundations:
    - de Boor's Algorithm: Evaluates curve positions recursively from Control Vertices (CVs).
    - Derivative Tangent Evaluation: Evaluates the tangent direction by computing weights 
      on a lower-degree curve basis.
    - Static Offset Compensation: Calculates $M_{offset} = M_{guide} \\times M_{spline}^{-1}$
      so that slave controllers maintain a clean [0, 0, 0] default transform.
    - Parent Space Compensation: Connects $parent.worldInverseMatrix[0]$ into the offset matrix
      chain to prevent double transformation (space popping) when grouped.

Author / References:
    - Mathematical spline weighting based on Cole O'Brien's matrix spline research:
      https://coleobrien.medium.com/matrix-splines-in-maya-ec17f3b3741
    - Refactored and integrated for nmTools AutoRig Pipeline by Antigravity.
"""

import math
import maya.cmds as mc
import maya.api.OpenMaya as om
from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.util import misc
reload(misc)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)


class CurveException(BaseException):
	"""
	Custom exception raised when curve parameters or knot vector lengths are invalid.
	"""


def defaultKnots(count, degree=3):
	"""
	Generate a standard clamped knot vector for a given number of CVs and curve degree.

	Args:
		count (int): Total number of control vertices (CVs).
		degree (int, optional): Degree of the B-spline curve. Defaults to 3 (Cubic).

	Returns:
		list[float]: Clamped knot vector list with clamped endpoints.
	"""
	knots = [0 for i in range(degree)] + [i for i in range(count - degree + 1)]
	knots += [count - degree for i in range(degree)]
	return [float(knot) for knot in knots]


def pointOnCurveWeights(cvs, t, degree, knots=None):
	"""
	Calculate CV blend weights at parameter $t$ along a B-spline curve using de Boor's algorithm.

	Args:
		cvs (list): List of CV objects, matrices, or string identifiers.
		t (float): Normalized curve parameter value in range [0.0, 1.0].
		degree (int): B-spline curve degree (e.g. 2 for Quadratic, 3 for Cubic).
		knots (list[float], optional): Knot vector. If None, computes default clamped knots.

	Raises:
		CurveException: If CV count is less than or equal to degree, or if knot length is invalid.

	Returns:
		list[list[Any, float]]: List of [cv_identifier, weight_float] pairs for active CVs.
	"""
	order = degree + 1
	if len(cvs) <= degree:
		raise CurveException('Curves of degree %s require at least %s cvs' % (degree, degree + 1))

	knots = knots or defaultKnots(len(cvs), degree)
	if len(knots) != len(cvs) + order:
		raise CurveException('Not enough knots provided. Total knot count must equal len(cvs) + degree + 1.')

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
	"""
	Calculate derivative tangent blend weights at parameter $t$ along a B-spline curve.

	Args:
		cvs (list): List of CV objects, matrices, or string identifiers.
		t (float): Normalized curve parameter value in range [0.0, 1.0].
		degree (int): B-spline curve degree (e.g. 2 for Quadratic, 3 for Cubic).
		knots (list[float], optional): Knot vector. If None, computes default clamped knots.

	Raises:
		CurveException: If CV count is less than or equal to degree, or if knot length is invalid.

	Returns:
		list[list[Any, float]]: List of [cv_identifier, weight_float] pairs for tangent derivative.
	"""
	order = degree + 1
	if len(cvs) <= degree:
		raise CurveException('Curves of degree %s require at least %s cvs' % (degree, degree + 1))

	knots = knots or defaultKnots(len(cvs), degree)
	if len(knots) != len(cvs) + order:
		raise CurveException('Not enough knots provided. Total knot count must equal len(cvs) + degree + 1.')

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


def apply_static_offset(slave_ctrl, guide_loc, spline_output_node):
	"""
	Calculate and apply a static offset matrix to zero out a slave controller transform.

	Computes the difference matrix between the guide locator's world matrix and the spline 
	evaluation matrix ($M_{offset} = M_{guide} \\times M_{spline}^{-1}$). Inserts a `multMatrix` 
	node connecting into `offsetParentMatrix` with parent space compensation, resetting local 
	translate/rotate to [0, 0, 0] and scale to [1, 1, 1].

	Args:
		slave_ctrl (str): Name of the child/slave controller node (e.g. 'C_childCV01_ctrl').
		guide_loc (str): Name of the reference guide locator (e.g. 'C_childCV01').
		spline_output_node (str): Name of the pickMatrix node outputting spline TRS matrix.

	Returns:
		str | None: Name of the created `multMatrix` offset node, or None if skipped.
	"""
	if not mc.objExists(slave_ctrl):
		mc.warning(f"Controller '{slave_ctrl}' does not exist. Skipping static offset.")
		return None

	if not mc.objExists(guide_loc):
		mc.warning(f"Guide locator '{guide_loc}' does not exist. Skipping static offset.")
		return None

	if not mc.objExists(spline_output_node):
		mc.warning(f"Spline output node '{spline_output_node}' does not exist. Skipping static offset.")
		return None

	# Match rotateOrder of the controller to the guide locator
	rot_order = mc.getAttr(f"{guide_loc}.rotateOrder")
	if isinstance(rot_order, (list, tuple)):
		rot_order = rot_order[0]
	mc.setAttr(f"{slave_ctrl}.rotateOrder", rot_order)

	# Get matrices using API 2.0
	guide_matrix = om.MMatrix(mc.getAttr(f"{guide_loc}.worldMatrix[0]"))
	spline_matrix = om.MMatrix(mc.getAttr(f"{spline_output_node}.outputMatrix"))

	# Calculate offset matrix: Offset = Guide * Inverse(Spline)
	offset_matrix = guide_matrix * spline_matrix.inverse()

	clean_name = core.check_name_style(name=slave_ctrl)[0]
	offset_node = f"{clean_name}Offset_mm"

	if not mc.objExists(offset_node):
		offset_node = mc.createNode("multMatrix", name=offset_node)

	# Set static offset matrix value
	mc.setAttr(f"{offset_node}.matrixIn[0]", list(offset_matrix), type="matrix")

	# Connect spline to multMatrix
	if not mc.isConnected(f"{spline_output_node}.outputMatrix", f"{offset_node}.matrixIn[1]"):
		mc.connectAttr(f"{spline_output_node}.outputMatrix", f"{offset_node}.matrixIn[1]", force=True)

	# Parent space compensation (connect parent worldInverseMatrix directly to convert world coordinates cleanly into parent local space)
	parent_list = mc.listRelatives(slave_ctrl, parent=True)
	if parent_list:
		if not mc.isConnected(f"{parent_list[0]}.worldInverseMatrix[0]", f"{offset_node}.matrixIn[2]"):
			mc.connectAttr(f"{parent_list[0]}.worldInverseMatrix[0]", f"{offset_node}.matrixIn[2]", force=True)
	else:
		connections = mc.listConnections(f"{offset_node}.matrixIn[2]", plugs=True)
		if connections:
			for conn in connections:
				mc.disconnectAttr(conn, f"{offset_node}.matrixIn[2]")

	# Connect multMatrix to offsetParentMatrix of the control
	if mc.isConnected(f"{spline_output_node}.outputMatrix", f"{slave_ctrl}.offsetParentMatrix"):
		mc.disconnectAttr(f"{spline_output_node}.outputMatrix", f"{slave_ctrl}.offsetParentMatrix")

	mc.connectAttr(f"{offset_node}.matrixSum", f"{slave_ctrl}.offsetParentMatrix", force=True)

	# Reset local transform values to zero
	for attr in ["tx", "ty", "tz", "rx", "ry", "rz"]:
		mc.setAttr(f"{slave_ctrl}.{attr}", 0)
	for attr in ["sx", "sy", "sz"]:
		mc.setAttr(f"{slave_ctrl}.{attr}", 1)

	return offset_node


def matrix_spine_setup(
	main_guides,
	child_guides=None,
	pCount=None,
	side='C',
	nameSpace='',
	baseName='spine',
	mainBaseName='mainCV',
	childBaseName='childCV',
	mainName=None,
	childName=None,
	charScale=1.0,
	mainSize=1.0,
	childSize=0.02,
	mainColor='yellow',
	childColor='white',
	mainCtrlShape='cube_ctrlShape',
	childCtrlShape='plainSphereB_ctrlShape',
	gimbal=True,
	rotOrder='xzy',
	ctrl_grp=None,
	detail_grp=None,
	mod_grp=None,
	parentTo=None,
	inheritScale=False,
	zero_out=True,
	parentJntTo=None,
	aimAxis=(0, 1, 0),
	upAxis=(0, 0, 1),
	upVector=(0, 0, 1),
	useUpVector=False,
	secondaryMode=2
):
	"""
	Construct a modular De Boor Matrix Spline rig for spine, neck, or tentacle components.

	Builds a procedural 2-tier spline setup:
	1. **Macro Layer (Master CVs):** Creates master controllers (`{side}_{mainBaseName}*_ctrl`) wrapped in zero groups 
	   (`{side}_{mainBaseName}*Zro_grp`) and optional gimbal controllers (`{side}_{mainBaseName}*Gmbl_ctrl`).
	2. **Micro Layer (Slave CVs):** Creates detail controllers (`{side}_{childBaseName}*_ctrl`) driven along the 
	   evaluated B-spline curve using `wtAddMatrix` and `aimMatrix` nodes, with integrated static 
	   zero-out and parent space compensation.
	3. **Bind Joint Chain (Optional):** If `parentJntTo` is specified, generates a sequential bind joint chain 
	   (`{side}_{childBaseName}*_bJnt`) parented to `parentJntTo` and driven by matrix parent constraints.

	Args:
		main_guides (list[str|core.Dag] | tuple | int): List of master guide transforms / locators, 
			or integer count of master CVs to generate.
		child_guides (list[str|core.Dag] | tuple, optional): List of slave/child guide transforms.
		pCount (int, optional): Number of slave detail controllers. Defaults to `len(child_guides)` 
			or `count * 4`.
		side (str, optional): Side identifier prefix (e.g. 'C', 'LFT', 'RGT'). Defaults to 'C'.
		nameSpace (str, optional): Global namespace prefix. Defaults to ''.
		baseName (str, optional): Subsystem module identifier (e.g. 'spine', 'neck'). Defaults to 'spine'.
		mainBaseName (str, optional): Base token name for master controllers. Defaults to 'mainCV'.
		childBaseName (str, optional): Base token name for slave detail controllers. Defaults to 'childCV'.
		mainName (str, optional): Alias for mainBaseName (backwards compatibility).
		childName (str, optional): Alias for childBaseName (backwards compatibility).
		charScale (float, optional): Character scale multiplier. Defaults to 1.0.
		mainSize (float, optional): Master controller curve size multiplier. Defaults to 1.0.
		childSize (float, optional): Slave controller curve size multiplier. Defaults to 0.02.
		mainColor (str, optional): Color preset for master controllers. Defaults to 'yellow'.
		childColor (str, optional): Color preset for slave controllers. Defaults to 'white'.
		mainCtrlShape (str, optional): Curve shape type for master controllers. Defaults to 'cube_ctrlShape'.
		childCtrlShape (str, optional): Curve shape type for slave controllers. Defaults to 'plainSphereB_ctrlShape'.
		gimbal (bool, optional): If True, generates gimbal controllers under each master CV. Defaults to True.
		rotOrder (str, optional): Default rotate order string for DAG nodes. Defaults to 'xzy'.
		ctrl_grp (str | core.Dag, optional): Target parent group for master controller zero groups.
		detail_grp (str | core.Dag, optional): Target parent group for slave detail controllers.
		mod_grp (str | core.Dag, optional): Top-level module group.
		parentTo (str | core.Dag, optional): Target parent group / controller for the top module group.
		inheritScale (bool, optional): If True, passes spline tangent scale. Defaults to False (Scale Isolation).
		zero_out (bool, optional): If True, computes and connects static offset matrices to zero out 
			slave controller transforms. Defaults to True.
		parentJntTo (str | core.Joint | core.Dag, optional): Target parent joint (e.g. 'hip_bJnt') under which 
			the bind joint chain is parented. If provided, creates a sequential bind joint chain ('*_bJnt') 
			matching child CVs driven by matrix constraints. Defaults to None.
		aimAxis (tuple[float, float, float] | str, optional): Local aim axis pointing along the curve tangent. 
			Defaults to (0, 1, 0) (+Y along).
		upAxis (tuple[float, float, float] | str, optional): Local secondary up axis. Defaults to (0, 0, 1) (+Z up).
		upVector (tuple[float, float, float] | str, optional): Up-vector direction in world/matrix space. 
			Defaults to (0, 0, 1) (+Z front/up).
		useUpVector (bool, optional): If True, connects the interpolated point matrix to 
			aimMatrix secondaryTargetMatrix and enables secondaryMode (default Mode 2 Align) with secondaryTargetVector
			to eliminate 180-degree aim singularity / roll flipping. Defaults to False.
		secondaryMode (int | str, optional): Mode for aimMatrix secondary evaluation:
			- 0 or 'off' / 'none': Rely on inputMatrix reference.
			- 1 or 'aim' / 'point': Point secondary axis towards secondaryTargetMatrix position.
			- 2 or 'align' / 'vector': Align secondary axis with secondaryTargetVector (stable directional up-vector). Defaults to 2.

	Returns:
		dict[str, Any]: Dictionary containing generated DAG names and matrix nodes:
			- `'mod_grp'` (str): Name of the top module group.
			- `'ctrl_grp'` (str): Name of the master controllers group.
			- `'detail_grp'` (str): Name of the slave detail controllers group.
			- `'main_ctrls'` (list[str]): Names of generated master controllers (`*_ctrl`).
			- `'main_zro_grps'` (list[str]): Names of master zero groups (`*Zro_grp`).
			- `'gimbal_ctrls'` (list[str]): Names of gimbal controllers (`*Gmbl_ctrl`).
			- `'child_ctrls'` (list[str]): Names of slave detail controllers (`*_ctrl`).
			- `'child_bJnts'` (list[str]): Names of generated bind joints (`*_bJnt`).
			- `'bind_joints'` (list[str]): Alias for `'child_bJnts'`.
			- `'point_matrix_nodes'` (list[str]): Names of point weight `wtAddMatrix` nodes.
			- `'tangent_matrix_nodes'` (list[str]): Names of tangent weight `wtAddMatrix` nodes.
			- `'aim_matrix_nodes'` (list[str]): Names of generated `aimMatrix` nodes.
			- `'pick_matrix_nodes'` (list[str]): Names of scale-filtering `pickMatrix` nodes.
			- `'offset_matrix_nodes'` (list[str]): Names of static offset `multMatrix` nodes.

	Examples:
		>>> from function.rigging.de_boor.matrixSpine import eh_matrixSpine_01_setup as matrixSpine
		>>> reload(matrixSpine)
		>>> spine_data = matrixSpine.matrix_spine_setup(
		...     main_guides=['C_mainCV01_loc', 'C_mainCV02_loc', 'C_mainCV03_loc'],
		...     pCount=6,
		...     side='C',
		...     mainBaseName='mainCV',
		...     childBaseName='childCV',
		...     charScale=10.0,
		...     mainSize=1.0,
		...     childSize=0.02,
		...     gimbal=True,
		...     zero_out=True
		... )
	"""
	misc.makeHeader('Start Matrix Spine Setup')

	# Handle backwards compatibility for mainName and childName
	if mainName is not None:
		mainBaseName = mainName
	if childName is not None:
		childBaseName = childName

	# Auto-infer baseName if baseName is default 'spine' and mainBaseName is custom
	if baseName == 'spine' and mainBaseName != 'mainCV':
		cleaned_base = mainBaseName
		for remove_token in ['MainCV', 'mainCV', 'Main', 'main', 'ChildCV', 'childCV', 'Child', 'child']:
			cleaned_base = cleaned_base.replace(remove_token, '')
		baseName = cleaned_base or mainBaseName

	# Construct naming prefixes
	side_prefix = f"{side}_" if side else ""
	ns_prefix = f"{nameSpace}" if nameSpace else ""

	# Axis vector conversion helper
	axis_map = {
		'x': (1.0, 0.0, 0.0),
		'y': (0.0, 1.0, 0.0),
		'z': (0.0, 0.0, 1.0),
		'-x': (-1.0, 0.0, 0.0),
		'-y': (0.0, -1.0, 0.0),
		'-z': (0.0, 0.0, -1.0),
	}
	aim_vec = axis_map.get(str(aimAxis).lower(), (0.0, 1.0, 0.0)) if isinstance(aimAxis, str) else [float(v) for v in aimAxis]
	up_axis_vec = axis_map.get(str(upAxis).lower(), (0.0, 0.0, 1.0)) if isinstance(upAxis, str) else [float(v) for v in upAxis]
	up_vec = axis_map.get(str(upVector).lower(), (0.0, 0.0, 1.0)) if isinstance(upVector, str) else [float(v) for v in upVector]

	# Resolve secondary mode mapping for aimMatrix (0=None, 1=Aim, 2=Align)
	sec_mode_map = {
		'off': 0, 'none': 0, 0: 0,
		'aim': 1, 'point': 1, 1: 1,
		'align': 2, 'vector': 2, 2: 2
	}
	resolved_sec_mode = sec_mode_map.get(secondaryMode, 2) if isinstance(secondaryMode, (int, str)) else int(secondaryMode)

	# Handle main_guides as count int or list
	if isinstance(main_guides, int):
		count = main_guides
		guide_inputs = [f"{side_prefix}{mainBaseName}{i+1:02d}" for i in range(count)]
	else:
		main_guides = list(main_guides)
		count = len(main_guides)
		guide_inputs = [str(g) for g in main_guides]

	if count < 2:
		mc.error("Matrix spline requires at least 2 main guides.")

	# Helper to resolve existing guide locator names with common fallbacks
	def resolve_guide(input_name, num_idx):
		if input_name and mc.objExists(input_name):
			return input_name
		fallbacks = [
			f"{side_prefix}{mainBaseName}{num_idx:02d}",
			f"{side_prefix}{mainBaseName}{num_idx:02d}_loc",
			f"{side_prefix}main{num_idx:02d}",
			f"{side_prefix}main{num_idx:02d}_loc",
			f"main{num_idx:02d}_{side}",
			f"main{num_idx:02d}_{side}_loc",
			f"{mainBaseName}{num_idx:02d}_{side}",
			f"{mainBaseName}{num_idx:02d}_{side}_loc",
		]
		for fb in fallbacks:
			if mc.objExists(fb):
				return fb
		return None

	# Determine spline degree
	degree = min(count - 1, 3)

	# Determine child count and resolve child guide names
	if child_guides and isinstance(child_guides, (list, tuple)):
		pCount = len(child_guides)
		child_guide_inputs = [str(g) for g in child_guides]
	else:
		pCount = pCount or (count * 4)
		child_guide_inputs = [f"{side_prefix}{childBaseName}{i+1:02d}" for i in range(pCount)]

	def resolve_child_guide(input_name, num_idx):
		if input_name and mc.objExists(input_name):
			return input_name
		fallbacks = [
			f"{side_prefix}{childBaseName}{num_idx:02d}",
			f"{side_prefix}{childBaseName}{num_idx:02d}_loc",
			f"{side_prefix}child{num_idx:02d}",
			f"{side_prefix}child{num_idx:02d}_loc",
			f"child{num_idx:02d}_{side}",
			f"child{num_idx:02d}_{side}_loc",
			f"{childBaseName}{num_idx:02d}_{side}",
			f"{childBaseName}{num_idx:02d}_{side}_loc",
		]
		for fb in fallbacks:
			if mc.objExists(fb):
				return fb
		return None

	# =========================================================================
	# PRE-FLIGHT VALIDATION: Verify all main_guides and child_guides exist
	# =========================================================================
	missing_main_guides = []
	duplicate_main_guides = []

	for num, raw_guide in enumerate(guide_inputs):
		startNum = num + 1
		target_guide = resolve_guide(raw_guide, startNum)
		if not target_guide or not mc.objExists(target_guide):
			missing_main_guides.append(str(raw_guide))
		else:
			matches = mc.ls(target_guide)
			if len(matches) > 1:
				duplicate_main_guides.append(f"'{target_guide}' ({len(matches)} objects found: {matches})")

	missing_child_guides = []
	duplicate_child_guides = []

	if zero_out:
		for i in range(pCount):
			num = i + 1
			raw_child_guide = child_guide_inputs[i] if i < len(child_guide_inputs) else None
			guide_loc = resolve_child_guide(raw_child_guide, num)
			if not guide_loc or not mc.objExists(guide_loc):
				missing_child_guides.append(str(raw_child_guide))
			else:
				matches = mc.ls(guide_loc)
				if len(matches) > 1:
					duplicate_child_guides.append(f"'{guide_loc}' ({len(matches)} objects found: {matches})")

	# Terminate and alert user immediately if missing or non-unique guide objects exist
	error_report = []
	if missing_main_guides:
		error_report.append(f"  * Missing Main Guide(s) ({len(missing_main_guides)}): {', '.join(missing_main_guides)}")
	if missing_child_guides:
		error_report.append(f"  * Missing Child Guide(s) ({len(missing_child_guides)}): {', '.join(missing_child_guides)}")
	if duplicate_main_guides:
		error_report.append(f"  * Non-Unique/Duplicate Main Guide(s): {', '.join(duplicate_main_guides)}")
	if duplicate_child_guides:
		error_report.append(f"  * Non-Unique/Duplicate Child Guide(s): {', '.join(duplicate_child_guides)}")

	if error_report:
		err_msg = (
			f"\n{'='*70}\n"
			f"[matrix_spine_setup ERROR] Rigging terminated due to missing or invalid guide objects:\n"
			+ "\n".join(error_report) +
			f"\nPlease verify that all guide locators/joints exist in the scene with unique names.\n"
			f"{'='*70}"
		)
		mc.error(err_msg)

	# Create module groups
	prefix = f"{ns_prefix}{side}_{baseName}" if side else f"{ns_prefix}{baseName}"

	if not mod_grp:
		mod_grp = core.Null(f"{prefix}Mod_grp")
		mod_grp.rotateOrder = rotOrder
	elif isinstance(mod_grp, str):
		mod_grp = core.Dag(mod_grp)

	if parentTo and mc.objExists(str(parentTo)):
		parent_target_grp = parentTo.name if hasattr(parentTo, 'name') else str(parentTo)
		mod_grp.parent(parent_target_grp)

	if not ctrl_grp:
		ctrl_grp = core.Null(f"{prefix}MainCtls_grp")
		ctrl_grp.rotateOrder = rotOrder
		ctrl_grp.parent(mod_grp)
	elif isinstance(ctrl_grp, str):
		ctrl_grp = core.Dag(ctrl_grp)

	if not detail_grp:
		detail_grp = core.Null(f"{prefix}DetailCtls_grp")
		detail_grp.rotateOrder = rotOrder
		detail_grp.parent(mod_grp)
	elif isinstance(detail_grp, str):
		detail_grp = core.Dag(detail_grp)

	# 1. Create Main CV Controllers with Zro_grp and Gimbal
	main_ctrls = []
	main_zro_grps = []
	gimbal_ctrls = []
	cvMatrices = []

	for num, raw_guide in enumerate(guide_inputs):
		startNum = num + 1
		ctrl_base_name = f"{ns_prefix}{side_prefix}{mainBaseName}{startNum:02d}"
		
		ctl = core.Dag(f"{ctrl_base_name}_ctrl")
		ctl.nmCreateController(mainCtrlShape)
		ctl.rotateOrder = rotOrder
		ctl.editCtrlShape(axis=charScale * mainSize * 1.8)
		# Set color AFTER editCtrlShape so it is preserved
		ctl.setColor(mainColor)

		target_guide = resolve_guide(raw_guide, startNum)
		if target_guide and mc.objExists(target_guide):
			ctl.maSnap(target_guide)
		else:
			mc.warning(f"Guide '{raw_guide}' could not be resolved. Controller {ctl.name} placed at default position.")

		# Create Zro_grp wrapping mainCV
		zro_grp = rigTools.zeroGroupNam(ctl)
		zro_grp.rotateOrder = rotOrder
		zro_grp.parent(ctrl_grp)

		main_ctrls.append(ctl.name)
		main_zro_grps.append(zro_grp.name)

		# Add Gimbal control if requested
		if gimbal:
			gmbl = core.createGimbal(ctl)
			gmbl.rotateOrder = rotOrder
			gmbl.setColor('white')
			gimbal_ctrls.append(gmbl.name)
			active_matrix_source = gmbl.name
		else:
			active_matrix_source = ctl.name

		cvMatrices.append(f"{active_matrix_source}.worldMatrix[0]")

	# 2. Create Child CV Controllers and De Boor Matrix Spline Chain
	child_ctrls = []
	point_matrix_nodes = []
	tangent_matrix_nodes = []
	aim_matrix_nodes = []
	pick_matrix_nodes = []
	offset_matrix_nodes = []

	for i in range(pCount):
		num = i + 1
		t = i / (float(pCount) - 1) if pCount > 1 else 0.0

		child_base_name = f"{ns_prefix}{side_prefix}{childBaseName}{num:02d}"
		pNode = core.Dag(f"{child_base_name}_ctrl")
		pNode.nmCreateController(childCtrlShape)
		pNode.rotateOrder = rotOrder
		pNode.editCtrlShape(axis=charScale * childSize * 1.8)
		# Set color AFTER editCtrlShape so it is preserved
		pNode.setColor(childColor)
		pNode.parent(detail_grp)
		child_ctrls.append(pNode.name)

		# Create Point Matrix weights
		pointMatrixWeights = pointOnCurveWeights(cvMatrices, t, degree=degree)
		pointMatrixNode = core.WtAddMatrixWithChannal(f"{side_prefix}{childBaseName}Point{num:02d}", count)
		point_matrix_nodes.append(pointMatrixNode)

		for index, (matrix, weight) in enumerate(pointMatrixWeights):
			mc.connectAttr(matrix, f"{pointMatrixNode}.wtMatrix[{index}].matrixIn", force=True)
			mc.setAttr(f"{pointMatrixNode}.wt_{index}", weight)
			mc.connectAttr(f"{pointMatrixNode}.wt_{index}", f"{pointMatrixNode}.wtMatrix[{index}].weightIn", force=True)

		# Create Tangent Matrix weights
		tangentMatrixWeights = tangentOnCurveWeights(cvMatrices, t, degree=degree)
		tangentMatrixNode = core.WtAddMatrixWithChannal(f"{side_prefix}{childBaseName}Tangent{num:02d}", count + 4)
		tangent_matrix_nodes.append(tangentMatrixNode)

		for index, (matrix, weight) in enumerate(tangentMatrixWeights):
			mc.connectAttr(matrix, f"{tangentMatrixNode}.wtMatrix[{index}].matrixIn", force=True)
			mc.setAttr(f"{tangentMatrixNode}.wt_{index}", weight)
			mc.connectAttr(f"{tangentMatrixNode}.wt_{index}", f"{tangentMatrixNode}.wtMatrix[{index}].weightIn", force=True)

		# Combine Point + Tangent to create the actual World Aim Target (P + T)
		aimTargetNode = core.WtAddMatrixWithChannal(f"{side_prefix}{childBaseName}AimTarget{num:02d}", 2)
		mc.connectAttr(f"{pointMatrixNode}.matrixSum", f"{aimTargetNode}.wtMatrix[0].matrixIn", force=True)
		mc.setAttr(f"{aimTargetNode}.wt_0", 1.0)
		mc.connectAttr(f"{aimTargetNode}.wt_0", f"{aimTargetNode}.wtMatrix[0].weightIn", force=True)
		mc.connectAttr(f"{tangentMatrixNode}.matrixSum", f"{aimTargetNode}.wtMatrix[1].matrixIn", force=True)
		mc.setAttr(f"{aimTargetNode}.wt_1", 1.0)
		mc.connectAttr(f"{aimTargetNode}.wt_1", f"{aimTargetNode}.wtMatrix[1].weightIn", force=True)

		# Create Aim Matrix node
		aimMatrixNode = mc.createNode('aimMatrix', name=f"{side_prefix}{childBaseName}Aim{num:02d}_aimMat")
		mc.connectAttr(f"{pointMatrixNode}.matrixSum", f"{aimMatrixNode}.inputMatrix", force=True)
		mc.connectAttr(f"{aimTargetNode}.matrixSum", f"{aimMatrixNode}.primaryTargetMatrix", force=True)

		mc.setAttr(f"{aimMatrixNode}.primaryMode", 1)
		mc.setAttr(f"{aimMatrixNode}.primaryInputAxis", *aim_vec)
		mc.setAttr(f"{aimMatrixNode}.secondaryInputAxis", *up_axis_vec)
		if useUpVector:
			# Connect Up-Vector constraint (Mode 2 Align with vector) to eliminate aim singularity / 180-degree roll flipping
			mc.connectAttr(f"{pointMatrixNode}.matrixSum", f"{aimMatrixNode}.secondaryTargetMatrix", force=True)
			mc.setAttr(f"{aimMatrixNode}.secondaryMode", resolved_sec_mode)
			mc.setAttr(f"{aimMatrixNode}.secondaryTargetVector", *up_vec)
		else:
			mc.setAttr(f"{aimMatrixNode}.secondaryMode", 0)
		aim_matrix_nodes.append(aimMatrixNode)

		# Scale filtering via pickMatrix (prevents non-uniform shear while allowing global scale)
		pickMatrixNode = mc.createNode('pickMatrix', name=f"{side_prefix}{childBaseName}PickMat{num:02d}_pickMat")
		mc.connectAttr(f"{aimMatrixNode}.outputMatrix", f"{pickMatrixNode}.inputMatrix", force=True)
		mc.setAttr(f"{pickMatrixNode}.useScale", inheritScale)
		mc.setAttr(f"{pickMatrixNode}.useShear", False)
		pick_matrix_nodes.append(pickMatrixNode)

		# Apply static offset zero-out or direct connection
		raw_child_guide = child_guide_inputs[i] if i < len(child_guide_inputs) else None
		guide_loc = resolve_child_guide(raw_child_guide, num)

		has_follow_rot = (i == 0 or i == pCount - 1)
		if has_follow_rot:
			# Guarantee followRotation is True during initial offset calculation
			# so offset_matrix captures the true rest alignment with full spline rotation
			mc.setAttr(f"{pickMatrixNode}.useRotate", True)

		if zero_out and guide_loc and mc.objExists(guide_loc):
			off_node = apply_static_offset(pNode.name, guide_loc, pickMatrixNode)
			if off_node:
				offset_matrix_nodes.append(off_node)
		else:
			mc.connectAttr(f"{pickMatrixNode}.outputMatrix", f"{pNode.name}.offsetParentMatrix", force=True)

		# Advanced Follow Rotation Architecture:
		# Blend between Follow Mode (spline matrix) and Static Mode (rest matrix)
		# Guarantees that toggling followRotation between On and Off at Rest Pose NEVER pops!
		if has_follow_rot:
			if not mc.attributeQuery('followRotation', node=pNode.name, exists=True):
				mc.addAttr(pNode.name, longName='followRotation', attributeType='float', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=True)

			# 1. Capture pure static rest orientation in slave parent local space
			curr_opm = mc.getAttr(f"{pNode.name}.offsetParentMatrix")
			static_pick = mc.createNode('pickMatrix', name=f"{side_prefix}{childBaseName}StaticPickMat{num:02d}_pickMat")
			mc.connectAttr(f"{off_node}.matrixSum" if (zero_out and guide_loc and mc.objExists(guide_loc)) else f"{pickMatrixNode}.outputMatrix", f"{static_pick}.inputMatrix", force=True)
			mc.setAttr(f"{static_pick}.useRotate", False)

			# Static rest rotation matrix (offsetParentMatrix at rest pose with no translation)
			rest_rot_matrix = list(curr_opm)
			rest_rot_matrix[12] = 0.0
			rest_rot_matrix[13] = 0.0
			rest_rot_matrix[14] = 0.0

			# MultMatrix to hold static rotation + live translation/scale:
			# StaticOrientation = rest_rot_matrix * static_pick(TRS without rotation)
			static_rot_mm = mc.createNode('multMatrix', name=f"{side_prefix}{childBaseName}StaticRot{num:02d}_mm")
			mc.setAttr(f"{static_rot_mm}.matrixIn[0]", rest_rot_matrix, type="matrix")
			mc.connectAttr(f"{static_pick}.outputMatrix", f"{static_rot_mm}.matrixIn[1]", force=True)

			# 2. Blend between Static Orientation (target[0]) and Follow Orientation (inputMatrix)
			blend_mat = mc.createNode('blendMatrix', name=f"{side_prefix}{childBaseName}FollowRot{num:02d}_blendMat")
			follow_source = f"{off_node}.matrixSum" if (zero_out and guide_loc and mc.objExists(guide_loc)) else f"{pickMatrixNode}.outputMatrix"
			
			# inputMatrix = Static rest orientation (when followRotation = 0.0)
			mc.connectAttr(f"{static_rot_mm}.matrixSum", f"{blend_mat}.inputMatrix", force=True)
			# target[0].targetMatrix = Follow spline live orientation (when followRotation = 1.0)
			mc.connectAttr(follow_source, f"{blend_mat}.target[0].targetMatrix", force=True)

			# Drive blend weight from followRotation attribute (0.0 = Static, 1.0 = Follow)
			mc.connectAttr(f"{pNode.name}.followRotation", f"{blend_mat}.target[0].weight", force=True)

			# 3. Rewire offsetParentMatrix to the output of blendMatrix
			mc.connectAttr(f"{blend_mat}.outputMatrix", f"{pNode.name}.offsetParentMatrix", force=True)

	# 3. Create Bind Joints (_bJnt) and Hierarchy if parentJntTo is provided
	child_bJnts = []
	if parentJntTo:
		parent_target = str(parentJntTo.name if hasattr(parentJntTo, 'name') else parentJntTo)

		# 3.1 Instantiate bind joints at child controller positions
		for i in range(pCount):
			num = i + 1
			jnt_name = f"{ns_prefix}{side_prefix}{childBaseName}{num:02d}_bJnt"
			core.clearSel()
			b_jnt = core.Joint(name=jnt_name)
			b_jnt.rotateOrder = rotOrder
			b_jnt.maSnap(child_ctrls[i])
			b_jnt.setColor('green')
			child_bJnts.append(b_jnt)

		# 3.2 Establish sequential parenting hierarchy
		for idx, jnt in enumerate(child_bJnts):
			if idx == 0:
				if parent_target and mc.objExists(parent_target):
					jnt.parent(parent_target)
				else:
					mc.warning(f"parentJntTo '{parent_target}' does not exist. Root bind joint '{jnt.name}' remains at world root.")
			else:
				jnt.parent(child_bJnts[idx - 1])

		# 3.3 Freeze rotation and disable segmentScaleCompensate on all bind joints
		for jnt in child_bJnts:
			jnt.freeze(r=True)
			mc.setAttr(f"{jnt.name}.segmentScaleCompensate", False)

		# 3.4 Apply matrix parent constraint from child controllers to bind joints (scale=False allows clean inheritance via joint hierarchy)
		for ctrl_name, jnt in zip(child_ctrls, child_bJnts):
			mtc.parentConMatrixGPT(source=ctrl_name, target=jnt.name, mo=True, translate=True, rotate=True, scale=False)

	misc.makeHeader('DONE Matrix Spine Setup')

	return {
		'mod_grp': mod_grp.name if hasattr(mod_grp, 'name') else str(mod_grp),
		'ctrl_grp': ctrl_grp.name if hasattr(ctrl_grp, 'name') else str(ctrl_grp),
		'detail_grp': detail_grp.name if hasattr(detail_grp, 'name') else str(detail_grp),
		'main_ctrls': main_ctrls,
		'main_zro_grps': main_zro_grps,
		'gimbal_ctrls': gimbal_ctrls,
		'child_ctrls': child_ctrls,
		'child_bJnts': [j.name for j in child_bJnts],
		'bind_joints': [j.name for j in child_bJnts],
		'point_matrix_nodes': point_matrix_nodes,
		'tangent_matrix_nodes': tangent_matrix_nodes,
		'aim_matrix_nodes': aim_matrix_nodes,
		'pick_matrix_nodes': pick_matrix_nodes,
		'offset_matrix_nodes': offset_matrix_nodes
	}


'''
# ------------------------------------------------------------------------------
# Example Execution
# ------------------------------------------------------------------------------

from function.rigging.autoRig.base import core
reload(core)

pattern = 'L_snkAChildCV##'
count = 12
child_list = core.generate_named_pattern(pattern, count)


patternMain = 'L_snkAMainCV##'
count = 4
main_list = core.generate_named_pattern(pattern, count)





if __name__ == '__main__':
	
	spine_result = matrix_spine_setup(
		main_guides = main_list,
		child_guides = child_list,
		pCount=2,
		side='L',
		mainBaseName='snkAMainCV',
		childBaseName='snkAChildCV',
		charScale=10.0,
		mainSize=1.0,
		childSize=0.02,
		mainColor='yellow',
		childColor='softBlue',
		gimbal=True,
		zero_out=True
	)
	
	
'''