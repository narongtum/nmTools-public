# -*- coding: utf-8 -*-
"""
===============================================================================
Bifrost RBF Auto Skirt Rigging System (eh_bifrostRbfSkirt.py)
===============================================================================
A modular, procedural auto-skirt rigging tool for Autodesk Maya using a
Bifrost Graph RBF (Radial Basis Function / Inverse Distance Weighting) Solver.

Dissected & reverse-engineered from:
riggerTools/python/function/rigging/constraint/RBF_bifrost_fakeThight.mb

Architecture & Data Flow:
-------------------------
1. Driver Tracker:
   A guide locator parented under the driver leg joint (e.g. 'thigh01' or
   'upperLegLFT_bJnt'). Tracks the 3D directional swing vector of the leg.
   Its worldMatrix connects into: `bifrostGraphShape.locator_guide`

2. Target Reference Poses (Sample Centers):
   An array of locators (locator_0 to locator_{n-1}) positioned on a spherical
   arc representing key extremity poses:
     - Target 0: Leg Backward / Back-Diagonal
     - Target 1: Leg Forward (Flexion / Front Kick)
     - Target 2: Leg Side (Abduction / Outward Spread)
     - Target 3: Leg Diagonal Backward
     - Target 4: Leg Neutral / Rest Pose
   Their worldMatrices connect into multi-attribute:
   `bifrostGraphShape.input_by_path[i]`

3. Bifrost Graph Inverse Distance Weighting (IDW / RBF):
   - Computes Euclidean distance $d_i = ||\\vec{P}_{guide} - \\vec{P}_i||$
   - Computes inverse squared distance: $w_i^{raw} = 1 / clamp(d_i^2, 1e-6, 1e11)$
   - Normalizes weights across all targets: $w_i = w_i^{raw} / \\sum w_k^{raw}$
   - Applies smooth FCurve shaping
   - Outputs: `bifrostGraphShape.bifrost_out_weights[i]` (sum = 1.0)

4. Skirt Joint Remap Drivers:
   Connects each `bifrost_out_weights[i]` through a `remapValue` node into skirt
   joints (e.g. objectA01.rotateX, objectC01.rotateX, objectE01.rotateX) or
   offset groups. Configurable thresholding via inputMin, inputMax, outputMin,
   and outputMax.

Author: Antigravity AI / nmTools
===============================================================================
"""

import os
import maya.cmds as mc
import maya.mel as mel

from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)


def ensure_bifrost_plugin():
	"""
	Ensures the Autodesk Bifrost Graph plugin is loaded in Maya.
	Raises a fatal error if the plugin is unavailable.
	"""
	plugin_name = "bifrostGraph"
	if not mc.pluginInfo(plugin_name, query=True, loaded=True):
		try:
			mc.loadPlugin(plugin_name)
			print(f"[eh_bifrostRbfSkirt] Successfully loaded plugin: {plugin_name}")
		except Exception as e:
			mc.error(
				f"[eh_bifrostRbfSkirt] Failed to load required plugin '{plugin_name}': {e}. "
				f"Please verify Bifrost is installed with your Maya installation."
			)


def get_template_scene_path():
	"""
	Returns the absolute path to the reference Bifrost RBF template Maya scene.
	"""
	# Navigate from addRig -> autoRig -> rigging -> constraint -> RBF_bifrost_fakeThight.mb
	current_dir = os.path.dirname(os.path.abspath(__file__))
	constraint_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "constraint"))
	template_path = os.path.join(constraint_dir, "RBF_bifrost_fakeThight.mb")
	return template_path


def get_or_import_bifrost_solver(node_name="bifrostGraph1", template_path=None):
	"""
	Finds an existing Bifrost RBF solver in the scene or imports the verified
	template solver from the repository.

	Args:
		node_name (str): Expected name of the bifrostGraph transform node.
		template_path (str, optional): Path to .mb template. Defaults to auto-resolved path.

	Returns:
		str: Name of the active bifrostGraphShape node.
	"""
	ensure_bifrost_plugin()

	# 1. Check if node_name or shape already exists
	if mc.objExists(node_name):
		shapes = mc.listRelatives(node_name, shapes=True, type="bifrostGraphShape") or []
		if shapes:
			return shapes[0]
		if mc.nodeType(node_name) == "bifrostGraphShape":
			return node_name

	# 2. Check for any existing bifrostGraphShape in the scene
	existing_shapes = mc.ls(type="bifrostGraphShape") or []
	for s in existing_shapes:
		if mc.attributeQuery("bifrost_out_weights", node=s, exists=True):
			print(f"[eh_bifrostRbfSkirt] Found existing Bifrost RBF solver shape: '{s}'")
			return s

	# 3. If not found, import the solver template
	if not template_path:
		template_path = get_template_scene_path()

	if not os.path.exists(template_path):
		mc.error(
			f"[eh_bifrostRbfSkirt] Template file '{template_path}' not found on disk. "
			f"Cannot initialize Bifrost RBF solver."
		)

	tmp_ns = "bifrostRbfTmp"
	print(f"[eh_bifrostRbfSkirt] Importing Bifrost RBF template from: {template_path}")
	imported_nodes = mc.file(
		template_path,
		i=True,
		type="mayaBinary",
		ignoreVersion=True,
		namespace=tmp_ns,
		returnNewNodes=True
	) or []

	# Find imported bifrostGraph
	imported_shapes = [n for n in imported_nodes if mc.nodeType(n) == "bifrostGraphShape"]
	if not imported_shapes:
		mc.error(
			f"[eh_bifrostRbfSkirt] Failed to find 'bifrostGraphShape' in imported template: {template_path}"
		)

	bifrost_shape = imported_shapes[0]
	bifrost_transform = mc.listRelatives(bifrost_shape, parent=True)[0]

	# Clean up non-bifrost imported clutter (e.g. test spheres or old locators if any)
	for n in imported_nodes:
		if mc.objExists(n) and n not in [bifrost_transform, bifrost_shape]:
			# Keep shading or internal dependencies, delete transforms/meshes
			if mc.nodeType(n) in ["transform", "mesh"] and not n.startswith(bifrost_transform):
				try:
					mc.delete(n)
				except Exception:
					pass

	# Strip temporary namespace
	try:
		mc.namespace(removeNamespace=f":{tmp_ns}", mergeNamespaceWithRoot=True)
	except Exception:
		pass

	# Re-query shape name after namespace merge
	shapes_after = mc.ls(type="bifrostGraphShape") or []
	target_shape = shapes_after[0] if shapes_after else bifrost_shape
	print(f"[eh_bifrostRbfSkirt] Initialized Bifrost RBF Solver: '{target_shape}'")
	return target_shape


def create_guide_locator(driver_joint, name=None, distance=35.0, axis="Z"):
	"""
	Creates a guide locator parented under the driver joint to track leg swing.

	Args:
		driver_joint (str or core.Dag): Leg joint driving the tracker.
		name (str, optional): Custom name for the locator.
		distance (float): Offset distance along tracking axis. Defaults to 35.0.
		axis (str): Primary tracking axis ('X', 'Y', 'Z', '-X', '-Y', '-Z'). Defaults to 'Z'.

	Returns:
		str: Name of the created guide locator.
	"""
	joint_name = str(driver_joint.name if hasattr(driver_joint, "name") else driver_joint)
	if not mc.objExists(joint_name):
		mc.error(f"[eh_bifrostRbfSkirt] Driver joint '{joint_name}' does not exist.")

	loc_name = name or f"{joint_name}_guideLoc"
	if mc.objExists(loc_name):
		mc.delete(loc_name)

	loc = mc.spaceLocator(name=loc_name)[0]
	mc.parent(loc, joint_name)

	# Zero transformations relative to joint
	mc.setAttr(f"{loc}.translate", 0, 0, 0)
	mc.setAttr(f"{loc}.rotate", 0, 0, 0)
	mc.setAttr(f"{loc}.scale", 1, 1, 1)

	# Apply directional offset
	offset_map = {
		"X": (distance, 0, 0),
		"-X": (-distance, 0, 0),
		"Y": (0, distance, 0),
		"-Y": (0, -distance, 0),
		"Z": (0, 0, distance),
		"-Z": (0, 0, -distance),
	}
	t_offset = offset_map.get(axis.upper(), (0, 0, distance))
	mc.setAttr(f"{loc}.translate", t_offset[0], t_offset[1], t_offset[2])

	# Set viewport display color to bright yellow for visibility
	loc_shape = mc.listRelatives(loc, shapes=True)[0]
	mc.setAttr(f"{loc_shape}.overrideEnabled", 1)
	mc.setAttr(f"{loc_shape}.overrideColor", 17) # 17 = Yellow

	return loc


def create_target_pose_locators(
	parent_group=None,
	positions=None,
	base_name="locator",
	side="LFT",
	reference_joint=None
):
	"""
	Creates the target sample pose locators distributed around the leg swing arc.

	Args:
		parent_group (str, optional): Parent group for target locators.
		positions (list of list of float, optional): 5 target 3D world positions.
		base_name (str): Prefix for locator names.
		side (str): Side identifier ('LFT' or 'RGT').
		reference_joint (str, optional): Reference joint for relative positioning.

	Returns:
		list of str: List of 5 created target locator names.
	"""
	if not positions:
		# Production default 5-pose layout matching RBF_bifrost_fakeThight.mb
		# Target 0: Back-Diagonal, Target 1: Forward, Target 2: Side, Target 3: Diag-Back, Target 4: Rest
		ref_x = 1.0 if side.upper() in ["LFT", "L"] else -1.0
		positions = [
			[-40.21 * ref_x, 9.10, 5.23],     # Target 0: Back-Diagonal
			[0.0, 0.0, 36.68],                 # Target 1: Forward (Flexion)
			[59.83 * ref_x, 9.92, 5.19],      # Target 2: Side (Abduction)
			[-5.92 * ref_x, 17.33, -44.12],   # Target 3: Diagonal
			[-5.92 * ref_x, 17.33, -44.12]    # Target 4: Secondary reference
		]

	grp_name = parent_group or f"grp_{base_name}s_{side}"
	if not mc.objExists(grp_name):
		grp_name = mc.group(empty=True, name=grp_name)

	# If reference joint provided, position grp at reference joint
	if reference_joint and mc.objExists(reference_joint):
		mc.matchTransform(grp_name, reference_joint, pos=True, rot=False)

	created_locs = []
	for i, pos in enumerate(positions):
		loc_name = f"{base_name}_{i}_{side}"
		if mc.objExists(loc_name):
			mc.delete(loc_name)
		loc = mc.spaceLocator(name=loc_name)[0]
		mc.parent(loc, grp_name)
		mc.xform(loc, ws=True, t=pos)

		# Color override (Cyan = 18)
		loc_shape = mc.listRelatives(loc, shapes=True)[0]
		mc.setAttr(f"{loc_shape}.overrideEnabled", 1)
		mc.setAttr(f"{loc_shape}.overrideColor", 18)

		created_locs.append(loc)

	return created_locs


def connect_bifrost_inputs(bifrost_shape, guide_locator, target_locators):
	"""
	Connects guide locator and target locators into the Bifrost RBF solver shape.

	Args:
		bifrost_shape (str): The bifrostGraphShape node.
		guide_locator (str): The guide locator tracking leg swing.
		target_locators (list of str): List of target pose locators.
	"""
	# Connect guide locator worldMatrix -> bifrostGraphShape.locator_guide
	mc.connectAttr(f"{guide_locator}.worldMatrix[0]", f"{bifrost_shape}.locator_guide", force=True)

	# Connect target locators worldMatrix -> bifrostGraphShape.input_by_path[i]
	for i, loc in enumerate(target_locators):
		mc.connectAttr(f"{loc}.worldMatrix[0]", f"{bifrost_shape}.input_by_path[{i}]", force=True)

	print(
		f"[eh_bifrostRbfSkirt] Connected guide '{guide_locator}' and {len(target_locators)} "
		f"targets to '{bifrost_shape}'"
	)


def connect_skirt_joint_driver(
	bifrost_shape,
	weight_index,
	skirt_joint,
	axis="rotateX",
	in_min=0.15,
	in_max=0.65,
	out_min=0.0,
	out_max=75.0,
	node_name=None
):
	"""
	Creates a remapValue node to map a specific RBF output weight to a skirt joint channel.

	Args:
		bifrost_shape (str): The bifrostGraphShape node.
		weight_index (int): Index into bifrost_out_weights (0..4).
		skirt_joint (str or core.Dag): Joint or group to rotate.
		axis (str): Driven channel ('rotateX', 'rotateY', 'rotateZ'). Defaults to 'rotateX'.
		in_min (float): Low activation weight threshold.
		in_max (float): High activation weight threshold.
		out_min (float): Minimum rotation value in degrees.
		out_max (float): Maximum rotation value in degrees.
		node_name (str, optional): Custom name for the remapValue node.

	Returns:
		str: Created remapValue node name.
	"""
	jnt_name = str(skirt_joint.name if hasattr(skirt_joint, "name") else skirt_joint)
	if not mc.objExists(jnt_name):
		mc.error(f"[eh_bifrostRbfSkirt] Target skirt joint '{jnt_name}' does not exist.")

	remap_name = node_name or f"{jnt_name}_w{weight_index}_remap"
	if mc.objExists(remap_name):
		mc.delete(remap_name)

	remap_node = mc.createNode("remapValue", name=remap_name)
	mc.setAttr(f"{remap_node}.inputMin", in_min)
	mc.setAttr(f"{remap_node}.inputMax", in_max)
	mc.setAttr(f"{remap_node}.outputMin", out_min)
	mc.setAttr(f"{remap_node}.outputMax", out_max)

	# Connect RBF weight to remap input
	mc.connectAttr(
		f"{bifrost_shape}.bifrost_out_weights[{weight_index}]",
		f"{remap_node}.inputValue",
		force=True
	)

	# Connect remap output to joint channel
	mc.connectAttr(f"{remap_node}.outValue", f"{jnt_name}.{axis}", force=True)

	print(
		f"[eh_bifrostRbfSkirt] Linked weight[{weight_index}] -> '{remap_node}' -> '{jnt_name}.{axis}' "
		f"(in: {in_min:.2f}..{in_max:.2f}, out: {out_min:.1f}..{out_max:.1f})"
	)
	return remap_node


def setup_bifrost_rbf_skirt(
	driver_leg_joint,
	skirt_joint_configs,
	guide_loc=None,
	target_locators=None,
	bifrost_shape=None,
	side="LFT",
	base_name="bifrostRbfSkirt"
):
	"""
	Primary high-level builder for the Bifrost RBF Auto Skirt System.

	Args:
		driver_leg_joint (str or core.Dag): Leg joint driving the system (e.g. 'thigh01' or 'upperLegLFT_bJnt').
		skirt_joint_configs (list of dict): Configuration list for driven skirt joints.
			Example:
			[
				{'joint': 'skirtFront01_bJnt', 'weight_index': 1, 'axis': 'rotateX', 'in_min': 0.28, 'in_max': 0.81, 'out_max': 75.0},
				{'joint': 'skirtSide01_bJnt',  'weight_index': 2, 'axis': 'rotateX', 'in_min': 0.17, 'in_max': 0.69, 'out_max': 90.0},
				{'joint': 'skirtDiag01_bJnt',  'weight_index': 0, 'axis': 'rotateX', 'in_min': 0.16, 'in_max': 0.52, 'out_max': 90.0},
			]
		guide_loc (str, optional): Custom guide locator. Auto-created under driver_leg_joint if None.
		target_locators (list of str, optional): List of 5 target locators. Auto-created if None.
		bifrost_shape (str, optional): Existing bifrostGraphShape. Auto-resolved/imported if None.
		side (str): Side identifier ('LFT' or 'RGT'). Defaults to 'LFT'.
		base_name (str): Base naming prefix. Defaults to 'bifrostRbfSkirt'.

	Returns:
		dict: Dictionary of all created nodes, locators, and remap nodes.
	"""
	core.makeHeader("Start of Bifrost RBF Auto Skirt Rig")

	# 1. Prerequisite Validation
	leg_name = str(driver_leg_joint.name if hasattr(driver_leg_joint, "name") else driver_leg_joint)
	if not mc.objExists(leg_name):
		mc.error(f"[eh_bifrostRbfSkirt] Specified driver leg joint '{leg_name}' does not exist in scene.")

	if not skirt_joint_configs or not isinstance(skirt_joint_configs, list):
		mc.error(f"[eh_bifrostRbfSkirt] 'skirt_joint_configs' must be a non-empty list of configuration dictionaries.")

	for cfg in skirt_joint_configs:
		jnt = cfg.get("joint")
		if not jnt or not mc.objExists(str(jnt.name if hasattr(jnt, "name") else jnt)):
			mc.error(f"[eh_bifrostRbfSkirt] Configured skirt joint '{jnt}' does not exist.")

	# 2. Get or Import Bifrost Solver
	if not bifrost_shape or not mc.objExists(bifrost_shape):
		bifrost_shape = get_or_import_bifrost_solver(node_name=f"{base_name}_{side}")

	# 3. Create or Validate Guide Locator
	if not guide_loc:
		guide_loc = create_guide_locator(
			driver_joint=leg_name,
			name=f"{leg_name}_rbfGuideLoc",
			distance=35.0,
			axis="Z"
		)

	# 4. Create or Validate Target Pose Locators
	if not target_locators:
		target_locators = create_target_pose_locators(
			parent_group=f"grp_{base_name}Locators_{side}",
			base_name=f"{base_name}Target",
			side=side,
			reference_joint=leg_name
		)

	if len(target_locators) < 5:
		mc.error(
			f"[eh_bifrostRbfSkirt] Expected at least 5 target locators for the RBF solver, "
			f"got {len(target_locators)}."
		)

	# 5. Connect Inputs to Bifrost
	connect_bifrost_inputs(bifrost_shape, guide_loc, target_locators)

	# 6. Build Skirt Remap Drivers
	created_remaps = []
	for cfg in skirt_joint_configs:
		jnt = str(cfg["joint"].name if hasattr(cfg["joint"], "name") else cfg["joint"])
		w_idx = cfg.get("weight_index", 0)
		axis = cfg.get("axis", "rotateX")
		in_min = cfg.get("in_min", 0.15)
		in_max = cfg.get("in_max", 0.65)
		out_min = cfg.get("out_min", 0.0)
		out_max = cfg.get("out_max", 75.0)

		remap = connect_skirt_joint_driver(
			bifrost_shape=bifrost_shape,
			weight_index=w_idx,
			skirt_joint=jnt,
			axis=axis,
			in_min=in_min,
			in_max=in_max,
			out_min=out_min,
			out_max=out_max,
			node_name=f"{jnt}_{axis}_rbfRemap"
		)
		created_remaps.append(remap)

	result = {
		"bifrost_shape": bifrost_shape,
		"guide_locator": guide_loc,
		"target_locators": target_locators,
		"remap_nodes": created_remaps,
		"driver_leg": leg_name,
	}

	core.makeHeader("End of Bifrost RBF Auto Skirt Rig")
	return result
