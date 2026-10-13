# -*- coding: utf-8 -*-
"""
Space Switch Module (spaceSwitch.py)
------------------------------------
Matrix-based multi-space switcher for Maya procedural rigging (nmTools standard).

Features:
- Arbitrary number of spaces (2, 3, 4, ... N spaces).
- Strict fail-fast: Requires 'spaceAttach' (the node to be constrained) and raises fatal error if missing.
- Clean matrix graph: maintains rest offset, blends via wtAddMatrix + condition nodes.
- Zero constraint nodes: avoids DAG cycle risk, lighter evaluation for parallel anim rigs.
- Multi-mode support:
    - 'parent': Drives Translate + Rotate (and Scale optionally).
    - 'orient': Drives Rotate only (keeps translate free/untouched).
    - 'point' / 'translate': Drives Translate only.
- Quaternion stability: Converts rotation via QuatToEuler matching target's rotateOrder.
- Joint Orient compensation: Automatically handles jointOrient if spaceAttach is a joint.
- Smart enum label cleaning: Auto-cleans suffixes (_ctrl, _gmbCtrl, _loc) or accepts custom space_names.

Usage Example:
--------------
from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.constraint import spaceSwitch
reload(spaceSwitch)

res = spaceSwitch.create_space_switch(
    space=['head_ctrl', 'ctrl_ctrl'],
    spaceAttach='handZro_grp',         # Node to be constrained (Mandatory)
    attr_holder='hand_ctrl',          # Controller holding the switch attribute
    attr_name='space',
    defaultVal=0,
    mode='parent'                     # 'parent' (T+R), 'orient' (R only), 'point' (T only)
)
"""

import maya.cmds as mc
import maya.api.OpenMaya as om2
import re

from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.pipeline import logger
reload(logger)


class SpaceSwitchLogger(logger.MayaLogger):
	LOGGER_NAME = "SpaceSwitch"


class Condition(core.Node):
	"""
	Core wrapper for Maya condition node.
	"""
	def __init__(self, name):
		super(Condition, self).__init__(mc.createNode('condition', name=name))
		self.autoSuffix()


def _get_dag_name(node):
	"""
	Helper to extract string name from string or core.Dag / core.Null object.
	"""
	if hasattr(node, 'name'):
		return str(node.name)
	return str(node)


def _get_local_offset(source, target):
	"""
	Calculates Offset Matrix using OpenMaya 2.0.
	Formula: TargetWorld * Inverse(SourceWorld)
	Returns: List of 16 floats (Row-major)
	"""
	source_mat_list = mc.xform(source, q=True, ws=True, m=True)
	target_mat_list = mc.xform(target, q=True, ws=True, m=True)

	source_mat = om2.MMatrix(source_mat_list)
	target_mat = om2.MMatrix(target_mat_list)

	offset_mat = target_mat * source_mat.inverse()
	return [offset_mat[i] for i in range(16)]


def _clean_space_label(space_node):
	"""
	Derives a clean human-readable label for enum attributes from a node name.
	Example:
		'head_ctrl' -> 'head'
		'ctrl_ctrl' -> 'World'
		'chest_gmbCtrl' -> 'chest'
	"""
	name_str = _get_dag_name(space_node)
	raw = name_str.split(':')[-1]

	# Special cases for root / world controllers
	if raw in ('ctrl_ctrl', 'master_ctrl', 'placement_ctrl', 'world_ctrl', 'noTouch_grp'):
		return 'World'

	# Strip common suffixes
	cleaned = re.sub(r'(_ctrl|_gmbCtrl|_gmb|_loc|_grp|_jnt|_bJnt|_tmpJnt)$', '', raw, flags=re.IGNORECASE)
	return cleaned if cleaned else raw


def create_space_switch(
	space,
	spaceAttach=None,
	attr_holder=None,
	space_names=None,
	attr_name='space',
	defaultVal=0,
	mode='parent',
	maintainOffset=True,
	driveScale=True,
	bodyPart=None,
	target=None
):
	"""
	Creates a matrix-based multi-space switch network.

	Args:
		space (list|tuple): List of 2 or more space driver nodes (e.g. ['head_ctrl', 'ctrl_ctrl']).
		spaceAttach (str|core.Dag): Node to be constrained / driven (e.g. 'somethingZro_grp'). Mandatory.
		attr_holder (str|core.Dag): Controller node that holds the switch enum attribute. Mandatory.
		space_names (list|tuple|None): Custom string labels for the enum attribute.
		                               If None, auto-cleans names from the space list.
		attr_name (str): Long name of the enum attribute (default: 'space').
		defaultVal (int): Initial enum index (default: 0).
		mode (str): 'parent' (Translate + Rotate), 'orient' (Rotate only), 'point' (Translate only).
		maintainOffset (bool): If True, preserves relative offset between space and spaceAttach at setup.
		driveScale (bool): If True, also drives spaceAttach scale in 'parent' / 'point' modes.
		bodyPart (str|None): Optional naming prefix. If None, derived from spaceAttach node.
		target (str|core.Dag|None): Backwards-compatible alias for spaceAttach.

	Returns:
		dict: Node dictionary containing references to created nodes.
	"""
	# --------------------------------------------------------------------------
	# 1. Validation (Fail-Fast)
	# --------------------------------------------------------------------------
	# 1.1 Check spaceAttach (Mandatory)
	actual_space_attach = spaceAttach if spaceAttach is not None else target
	if not actual_space_attach:
		mc.error(
			"[SpaceSwitch] Fatal Error: Parameter 'spaceAttach' is required (e.g. spaceAttach='somethingZro_grp'). "
			"Please specify the node to be constrained."
		)

	space_attach_str = _get_dag_name(actual_space_attach)
	if not mc.objExists(space_attach_str):
		mc.error(
			f"[SpaceSwitch] Fatal Error: Specified 'spaceAttach' does not exist in scene: '{space_attach_str}'"
		)

	# 1.2 Check attr_holder (Mandatory)
	if not attr_holder:
		mc.error(
			"[SpaceSwitch] Fatal Error: Parameter 'attr_holder' is required (e.g. attr_holder='some_ctrl'). "
			"Please specify the controller holding the switch attribute."
		)

	attr_holder_str = _get_dag_name(attr_holder)
	if not mc.objExists(attr_holder_str):
		mc.error(
			f"[SpaceSwitch] Fatal Error: Specified 'attr_holder' does not exist in scene: '{attr_holder_str}'"
		)

	# 1.3 Check space drivers
	if not space or len(space) < 2:
		mc.error(
			f"[SpaceSwitch] Fatal Error: 'space' must contain at least 2 driver objects. "
			f"Received: {space}"
		)

	missing_spaces = [ _get_dag_name(s) for s in space if not mc.objExists(_get_dag_name(s)) ]
	if missing_spaces:
		mc.error(
			f"[SpaceSwitch] Fatal Error: The following space drivers do not exist in scene:\n"
			f"{', '.join(missing_spaces)}"
		)

	# 1.4 Validate mode
	valid_modes = ('parent', 'orient', 'point', 'translate', 'rotate')
	if mode.lower() not in valid_modes:
		SpaceSwitchLogger.warning(f"Invalid mode '{mode}'. Falling back to 'parent'.")
		mode = 'parent'
	mode = mode.lower()
	if mode == 'translate':
		mode = 'point'
	elif mode == 'rotate':
		mode = 'orient'

	# 1.5 Validate defaultVal
	num_spaces = len(space)
	if not (0 <= defaultVal < num_spaces):
		SpaceSwitchLogger.warning(
			f"defaultVal '{defaultVal}' is out of bounds [0..{num_spaces-1}]. Resetting to 0."
		)
		defaultVal = 0

	# --------------------------------------------------------------------------
	# 2. Setup Naming & Labels
	# --------------------------------------------------------------------------
	if bodyPart:
		base_name = f"{bodyPart}_SpaceSwitch"
	else:
		attach_info = core.check_name_style(name=space_attach_str)
		base_name = f"{attach_info[0]}_SpaceSwitch"

	if space_names and len(space_names) == num_spaces:
		enum_labels = [str(lbl) for lbl in space_names]
	else:
		enum_labels = [_clean_space_label(s) for s in space]

	enum_str = ":".join(enum_labels)

	SpaceSwitchLogger.info(
		f"Building Space Switch: '{base_name}' for spaceAttach '{space_attach_str}' "
		f"driven by {num_spaces} spaces: [{', '.join(enum_labels)}]"
	)

	# --------------------------------------------------------------------------
	# 3. Add / Configure Enum Attribute on attr_holder
	# --------------------------------------------------------------------------
	attr_full_path = f"{attr_holder_str}.{attr_name}"
	if not mc.attributeQuery(attr_name, node=attr_holder_str, exists=True):
		mc.addAttr(attr_holder_str, ln=attr_name, at='enum', en=enum_str, k=True)
	else:
		# If attribute exists as enum, update enum strings
		try:
			mc.addAttr(attr_full_path, edit=True, at='enum', en=enum_str)
		except:
			pass

	mc.setAttr(attr_full_path, defaultVal)

	# --------------------------------------------------------------------------
	# 4. Matrix Network Construction
	# --------------------------------------------------------------------------
	# WtAddMatrix node to combine all active spaces
	wt_add = core.WtAddMatrix(f"{base_name}_Blend_wtAdd")

	space_mmx_nodes = []
	condition_nodes = []

	for i, sp in enumerate(space):
		sp_str = _get_dag_name(sp)
		sp_label = enum_labels[i]

		# 4.1 Maintain Offset Matrix
		if maintainOffset:
			offset_val = _get_local_offset(sp_str, space_attach_str)
		else:
			# Identity matrix 4x4
			offset_val = [1.0, 0.0, 0.0, 0.0,
			              0.0, 1.0, 0.0, 0.0,
			              0.0, 0.0, 1.0, 0.0,
			              0.0, 0.0, 0.0, 1.0]

		# 4.2 MultMatrix for Space i
		sp_mmx = core.MultMatrix(f"{base_name}_{sp_label}_mmx")
		mc.setAttr(f"{sp_mmx.name}.matrixIn[0]", offset_val, type="matrix")
		mc.connectAttr(f"{sp_str}.worldMatrix[0]", f"{sp_mmx.name}.matrixIn[1]", f=True)
		space_mmx_nodes.append(sp_mmx)

		# Connect space matrixSum to wtAddMatrix slot i
		mc.connectAttr(f"{sp_mmx.name}.matrixSum", f"{wt_add.name}.wtMatrix[{i}].matrixIn", f=True)

		# 4.3 Condition Node for Space i (Weight selector)
		cnd = Condition(f"{base_name}_{sp_label}_cnd")
		mc.connectAttr(attr_full_path, f"{cnd.name}.firstTerm", f=True)
		cnd.attr('secondTerm').value = i
		cnd.attr('operation').value = 0  # Equal
		cnd.attr('colorIfTrueR').value = 1.0
		cnd.attr('colorIfFalseR').value = 0.0
		condition_nodes.append(cnd)

		# Drive wtMatrix weight
		mc.connectAttr(f"{cnd.name}.outColorR", f"{wt_add.name}.wtMatrix[{i}].weightIn", f=True)

	# --------------------------------------------------------------------------
	# 5. Target Parent Inverse Matrix Conversion
	# --------------------------------------------------------------------------
	# Multiply blended World Matrix by spaceAttach's parentInverseMatrix to get Local Matrix
	mat_final = core.MultMatrix(f"{base_name}_Final_mmx")
	mc.connectAttr(f"{wt_add.name}.matrixSum", f"{mat_final.name}.matrixIn[0]", f=True)
	mc.connectAttr(f"{space_attach_str}.parentInverseMatrix[0]", f"{mat_final.name}.matrixIn[1]", f=True)

	# --------------------------------------------------------------------------
	# 6. Decompose Final Matrix
	# --------------------------------------------------------------------------
	decomp = core.DecomposeMatrix(f"{base_name}_Result_dcmp")
	mc.connectAttr(f"{mat_final.name}.matrixSum", f"{decomp.name}.inputMatrix", f=True)

	# --------------------------------------------------------------------------
	# 7. Output Connections to spaceAttach
	# --------------------------------------------------------------------------
	# 7.1 Translate & Scale
	if mode in ('parent', 'point'):
		mc.connectAttr(f"{decomp.name}.outputTranslate", f"{space_attach_str}.translate", f=True)
		if driveScale:
			mc.connectAttr(f"{decomp.name}.outputScale", f"{space_attach_str}.scale", f=True)
		SpaceSwitchLogger.info(f"[{base_name}] Driving Translate and Scale on '{space_attach_str}'.")

	# 7.2 Rotate via QuatToEuler (with Joint Orient compensation if joint)
	quat_to_euler = None
	if mode in ('parent', 'orient'):
		quat_to_euler = core.QuatToEuler(f"{base_name}_Result_q2e")
		attach_type = mc.nodeType(space_attach_str)

		if attach_type == 'joint':
			SpaceSwitchLogger.info(f"spaceAttach '{space_attach_str}' is a Joint. Adding Joint Orient compensation.")
			q_e2q = core.EulerToQuat(f"{base_name}_JO_e2q")
			q_inv = core.QuatInvert(f"{base_name}_JO_inv")
			q_prod = core.QuatProd(f"{base_name}_JO_prod")

			mc.connectAttr(f"{space_attach_str}.jointOrient", f"{q_e2q.name}.inputRotate", f=True)
			mc.connectAttr(f"{q_e2q.name}.outputQuat", f"{q_inv.name}.inputQuat", f=True)
			mc.connectAttr(f"{decomp.name}.outputQuat", f"{q_prod.name}.input1Quat", f=True)
			mc.connectAttr(f"{q_inv.name}.outputQuat", f"{q_prod.name}.input2Quat", f=True)
			mc.connectAttr(f"{q_prod.name}.outputQuat", f"{quat_to_euler.name}.inputQuat", f=True)
		else:
			# Transform node or group
			mc.connectAttr(f"{decomp.name}.outputQuat", f"{quat_to_euler.name}.inputQuat", f=True)

		# Match target rotate order
		mc.connectAttr(f"{space_attach_str}.rotateOrder", f"{quat_to_euler.name}.inputRotateOrder", f=True)
		mc.connectAttr(f"{quat_to_euler.name}.outputRotate", f"{space_attach_str}.rotate", f=True)
		SpaceSwitchLogger.info(f"[{base_name}] Driving Rotate on '{space_attach_str}'.")

	return {
		'spaceAttach': space_attach_str,
		'target': space_attach_str,
		'attr_holder': attr_holder_str,
		'attr': attr_full_path,
		'spaces': [ _get_dag_name(s) for s in space ],
		'enum_labels': enum_labels,
		'wtAddMatrix': wt_add,
		'decomp': decomp,
		'final_mmx': mat_final,
		'conditions': condition_nodes,
		'space_mmx': space_mmx_nodes,
		'quat_to_euler': quat_to_euler
	}


# Convenient alias
space_switch = create_space_switch
