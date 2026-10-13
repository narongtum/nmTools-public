"""
Maya Auto Skirt Rigging System
==============================
A Python script to generate a game-ready, joint-based auto skirt rigging system 
in Autodesk Maya. It creates a procedural collision node network using standard 
Maya utility nodes to push skirt joints away from leg colliders, preventing intersection.

Author: Antigravity AI
Date: 2026-06-02
"""

import math
from typing import List, Optional, Tuple
import maya.cmds as cmds


def create_collider(joint_name: str, radius: float, name_suffix: str) -> str:
	"""
	Creates a collider locator parented to the specified joint.
	
	Args:
		joint_name: The joint to attach the collider to.
		radius: The collision radius.
		name_suffix: Suffix for naming the collider.
		
	Returns:
		The name of the created collider locator.
	"""
	collider_name = f"{joint_name}_{name_suffix}_collider"
	if cmds.objExists(collider_name):
		cmds.delete(collider_name)
		
	# Create a locator to act as the collider center
	locator = cmds.spaceLocator(n=collider_name)[0]
	cmds.setAttr(f"{locator}.visibility", True)
	
	# Add a custom radius attribute to control collision size
	if not cmds.attributeQuery('radius', node=locator, exists=True):
		cmds.addAttr(locator, ln='radius', at='double', dv=radius, k=True)
		
	# Parent and zero transformations
	cmds.parent(locator, joint_name)
	cmds.setAttr(f"{locator}.translate", 0, 0, 0)
	cmds.setAttr(f"{locator}.rotate", 0, 0, 0)
	cmds.setAttr(f"{locator}.scale", 1, 1, 1)
	
	# Draw a wireframe sphere in the viewport using Maya's drawing overrides
	# to represent the collision boundary
	
	# Add visual sphere representation using a simple NURBS sphere (non-renderable)
	visual_sphere = cmds.sphere(r=1.0, n=f"{collider_name}_visual", ch=False)[0]
	cmds.parent(visual_sphere, locator)
	cmds.setAttr(f"{visual_sphere}.translate", 0, 0, 0)
	cmds.setAttr(f"{visual_sphere}.rotate", 0, 0, 0)
	cmds.setAttr(f"{visual_sphere}.scale", 1, 1, 1)
	
	# Set display override to template/reference and draw as wireframe
	cmds.setAttr(f"{visual_sphere}.overrideEnabled", 1)
	cmds.setAttr(f"{visual_sphere}.overrideDisplayType", 2) # Reference (transparent/unselectable)
	
	# Connect visual sphere scale to the radius attribute
	cmds.connectAttr(f"{locator}.radius", f"{visual_sphere}.scaleX")
	cmds.connectAttr(f"{locator}.radius", f"{visual_sphere}.scaleY")
	cmds.connectAttr(f"{locator}.radius", f"{visual_sphere}.scaleZ")
	
	return locator


def connect_collision_chain(
	base_loc: str, 
	ik_handle: str, 
	colliders: List[str], 
	parent_space_obj: Optional[str] = None
) -> None:
	"""
	Connects a series of colliders to push the ik_handle away from its base_loc position.
	Creates a procedural math node network in Maya's Dependency Graph.
	
	Args:
		base_loc: Name of the base locator (resting position in world space).
		ik_handle: Name of the IK handle to drive.
		colliders: List of collider locators.
		parent_space_obj: Parent object of the IK handle to transform the world position back to local space.
	"""
	# 1. Get base world position
	base_decomp = cmds.createNode('decomposeMatrix', n=f"{base_loc}_decomp")
	cmds.connectAttr(f"{base_loc}.worldMatrix[0]", f"{base_decomp}.inputMatrix")
	
	current_pos_attr = f"{base_decomp}.outputTranslate"
	
	# If no parent space object is specified, use the parent of the ik_handle
	if not parent_space_obj:
		parent_space_obj = cmds.listRelatives(ik_handle, parent=True)[0]
		
	for i, collider in enumerate(colliders):
		suffix = f"{ik_handle}_step_{i}"
		
		# Get collider world position
		coll_decomp = cmds.createNode('decomposeMatrix', n=f"{collider}_{suffix}_decomp")
		cmds.connectAttr(f"{collider}.worldMatrix[0]", f"{coll_decomp}.inputMatrix")
		coll_pos_attr = f"{coll_decomp}.outputTranslate"
		
		coll_radius_attr = f"{collider}.radius"
		
		# Subtract vector: current_pos - collider_pos (direction of push)
		sub_node = cmds.createNode('plusMinusAverage', n=f"sub_{suffix}")
		cmds.setAttr(f"{sub_node}.operation", 2)  # Subtract
		cmds.connectAttr(current_pos_attr, f"{sub_node}.input3D[0]")
		cmds.connectAttr(coll_pos_attr, f"{sub_node}.input3D[1]")
		
		# Distance between current_pos and collider_pos
		dist_node = cmds.createNode('distanceBetween', n=f"dist_{suffix}")
		cmds.connectAttr(current_pos_attr, f"{dist_node}.point1")
		cmds.connectAttr(coll_pos_attr, f"{dist_node}.point2")
		
		# Clamp distance to prevent division by zero (min = 0.001)
		clamp_dist = cmds.createNode('clamp', n=f"clampDist_{suffix}")
		cmds.setAttr(f"{clamp_dist}.minR", 0.001)
		cmds.setAttr(f"{clamp_dist}.maxR", 999999.0)
		cmds.connectAttr(f"{dist_node}.distance", f"{clamp_dist}.inputR")
		
		# Divide: radius / distance
		div_node = cmds.createNode('multiplyDivide', n=f"div_{suffix}")
		cmds.setAttr(f"{div_node}.operation", 2)  # Divide
		cmds.connectAttr(coll_radius_attr, f"{div_node}.input1X")
		cmds.connectAttr(f"{clamp_dist}.outputR", f"{div_node}.input2X")
		
		# Multiply: vector * (radius / distance) to project onto sphere surface
		mult_node = cmds.createNode('multiplyDivide', n=f"mult_{suffix}")
		cmds.setAttr(f"{mult_node}.operation", 1)  # Multiply
		cmds.connectAttr(f"{sub_node}.output3D", f"{mult_node}.input1")
		cmds.connectAttr(f"{div_node}.outputX", f"{mult_node}.input2X")
		cmds.connectAttr(f"{div_node}.outputX", f"{mult_node}.input2Y")
		cmds.connectAttr(f"{div_node}.outputX", f"{mult_node}.input2Z")
		
		# Add: collider_pos + scaled_vector
		add_node = cmds.createNode('plusMinusAverage', n=f"add_{suffix}")
		cmds.setAttr(f"{add_node}.operation", 1)  # Sum
		cmds.connectAttr(coll_pos_attr, f"{add_node}.input3D[0]")
		cmds.connectAttr(f"{mult_node}.output", f"{add_node}.input3D[1]")
		
		# Condition: distance < radius
		cond_node = cmds.createNode('condition', n=f"cond_{suffix}")
		cmds.setAttr(f"{cond_node}.operation", 4)  # Less than
		cmds.connectAttr(f"{dist_node}.distance", f"{cond_node}.firstTerm")
		cmds.connectAttr(coll_radius_attr, f"{cond_node}.secondTerm")
		cmds.connectAttr(f"{add_node}.output3D", f"{cond_node}.colorIfTrue")
		cmds.connectAttr(current_pos_attr, f"{cond_node}.colorIfFalse")
		
		current_pos_attr = f"{cond_node}.outColor"
		
	# Transform world position to local space of IK handle's parent
	pt_matrix = cmds.createNode('pointMatrixMult', n=f"{ik_handle}_local_matrix")
	cmds.connectAttr(current_pos_attr, f"{pt_matrix}.inPoint")
	cmds.connectAttr(f"{parent_space_obj}.worldInverseMatrix[0]", f"{pt_matrix}.inMatrix")
	
	# Connect to IK Handle translate
	cmds.connectAttr(f"{pt_matrix}.output", f"{ik_handle}.translate")


def build_auto_skirt(
	pelvis: str,
	left_thigh: str,
	right_thigh: str,
	left_knee: str,
	right_knee: str,
	num_chains: int = 8,
	joints_per_chain: int = 3,
	skirt_radius_top: float = 1.5,
	skirt_radius_bottom: float = 2.2,
	thigh_radius: float = 1.0,
	knee_radius: float = 0.8,
	skirt_height: float = 4.0
) -> None:
	"""
	Main generator for the auto skirt rig.
	
	Args:
		pelvis: Name of the pelvis/hip joint.
		left_thigh: Name of the left thigh joint.
		right_thigh: Name of the right thigh joint.
		left_knee: Name of the left knee joint.
		right_knee: Name of the right knee joint.
		num_chains: Number of skirt chains around the hips.
		joints_per_chain: Joints in each skirt chain (default: 3).
		skirt_radius_top: Top radius of the skirt.
		skirt_radius_bottom: Bottom radius of the skirt.
		thigh_radius: Radius of the thigh colliders.
		knee_radius: Radius of the knee colliders.
		skirt_height: Total height length of the skirt.
	"""
	# 1. Verification
	for node in [pelvis, left_thigh, right_thigh, left_knee, right_knee]:
		if not cmds.objExists(node):
			raise ValueError(f"Required joint '{node}' does not exist.")
			
	# 2. Load required plugins
	if not cmds.pluginInfo('matrixNodes', q=True, loaded=True):
		cmds.loadPlugin('matrixNodes')
		
	# 3. Create Colliders
	colliders = []
	colliders.append(create_collider(left_thigh, thigh_radius, "L_thigh"))
	colliders.append(create_collider(right_thigh, thigh_radius, "R_thigh"))
	colliders.append(create_collider(left_knee, knee_radius, "L_knee"))
	colliders.append(create_collider(right_knee, knee_radius, "R_knee"))
	
	# Create main organization groups
	skirt_system_grp = cmds.group(em=True, n="skirt_system_grp")
	cmds.parent(skirt_system_grp, pelvis)
	cmds.setAttr(f"{skirt_system_grp}.translate", 0, 0, 0)
	cmds.setAttr(f"{skirt_system_grp}.rotate", 0, 0, 0)
	cmds.setAttr(f"{skirt_system_grp}.scale", 1, 1, 1)
	
	skirt_joints_grp = cmds.group(em=True, n="skirt_joints_grp")
	skirt_locators_grp = cmds.group(em=True, n="skirt_base_locators_grp")
	skirt_iks_grp = cmds.group(em=True, n="skirt_iks_grp")
	
	cmds.parent([skirt_joints_grp, skirt_locators_grp, skirt_iks_grp], skirt_system_grp)
	
	# Pelvis translation for height starting point
	pelvis_pos = cmds.xform(pelvis, q=True, ws=True, t=True)
	pelvis_y = pelvis_pos[1]
	
	# 4. Generate Skirt Chains
	for i in range(num_chains):
		angle = (2 * math.pi / num_chains) * i
		cos_a = math.cos(angle)
		sin_a = math.sin(angle)
		
		# Name prefix for this chain
		chain_name = f"skirt_chain_{i:02d}"
		
		# Create joint chain
		cmds.select(cl=True)
		prev_joint = None
		chain_joints = []
		
		for j in range(joints_per_chain):
			t = j / float(joints_per_chain - 1) if joints_per_chain > 1 else 0.0
			
			# Interpolate radius from top to bottom
			r = skirt_radius_top + t * (skirt_radius_bottom - skirt_radius_top)
			
			# Calculate coordinates
			# Move slightly outward to give a preferred bending angle away from the legs
			curvature_offset = 0.1 * math.sin(t * math.pi)  
			r_with_bend = r + curvature_offset
			
			x = pelvis_pos[0] + r_with_bend * cos_a
			z = pelvis_pos[2] + r_with_bend * sin_a
			y = pelvis_y - t * skirt_height
			
			jnt_name = f"{chain_name}_jnt_{j:02d}"
			jnt = cmds.joint(p=(x, y, z), n=jnt_name)
			chain_joints.append(jnt)
			
			if prev_joint:
				# Set preferred angle to bend outward
				cmds.setAttr(f"{prev_joint}.preferredAngleX", 0.0)
				cmds.setAttr(f"{prev_joint}.preferredAngleY", 0.0)
				# Set preferred angle Z or Y depending on orientation to bend outward
				cmds.setAttr(f"{prev_joint}.preferredAngleZ", 5.0)
				
			prev_joint = jnt
			
		# Parent the chain root to the joints group
		cmds.parent(chain_joints[0], skirt_joints_grp)
		
		# Create IK Handle for the chain
		ik_name = f"{chain_name}_ik"
		ik_nodes = cmds.ikHandle(
			sj=chain_joints[0], 
			ee=chain_joints[-1], 
			sol="ikSCsolver", 
			n=ik_name
		)
		ik_h = ik_nodes[0]
		cmds.parent(ik_h, skirt_iks_grp)
		cmds.setAttr(f"{ik_h}.visibility", False) # Hide IK handle
		
		# Create base locator representing the resting position
		base_loc = cmds.spaceLocator(n=f"{chain_name}_base_loc")[0]
		cmds.parent(base_loc, skirt_locators_grp)
		
		# Position base locator at the IK handle's default position
		ik_pos = cmds.xform(ik_h, q=True, ws=True, t=True)
		cmds.xform(base_loc, ws=True, t=ik_pos)
		cmds.setAttr(f"{base_loc}.visibility", True)
		
		# Connect collision math node network to push the IK handle
		connect_collision_chain(
			base_loc=base_loc,
			ik_handle=ik_h,
			colliders=colliders,
			parent_space_obj=skirt_iks_grp
		)
		
	cmds.select(cl=True)
	print("Auto Skirt Rig successfully generated!")


def build_sample_scene() -> Tuple[str, str, str, str, str]:
	"""
	Builds a simple character test rig (hips and two leg chains) 
	and a skirt mesh representation for testing.
	
	Returns:
		A tuple of strings representing the names of:
		(pelvis_joint, L_thigh, R_thigh, L_knee, R_knee)
	"""
	# Clean up existing test scene if exists
	for obj in ["test_rig_grp", "skirt_geometry_grp"]:
		if cmds.objExists(obj):
			cmds.delete(obj)
			
	# Create main group
	test_grp = cmds.group(em=True, n="test_rig_grp")
	
	# 1. Create Skeleton Joints
	cmds.select(cl=True)
	pelvis = cmds.joint(p=(0, 10, 0), n="test_pelvis_jnt")
	
	# Left Leg
	cmds.select(pelvis)
	l_thigh = cmds.joint(p=(1.0, 10.0, 0), n="test_L_thigh_jnt")
	l_knee = cmds.joint(p=(1.0, 5.0, 0.1), n="test_L_knee_jnt") # slight bend forward
	l_foot = cmds.joint(p=(1.0, 0.5, 0), n="test_L_foot_jnt")
	
	# Right Leg
	cmds.select(pelvis)
	r_thigh = cmds.joint(p=(-1.0, 10.0, 0), n="test_R_thigh_jnt")
	r_knee = cmds.joint(p=(-1.0, 5.0, 0.1), n="test_R_knee_jnt")
	r_foot = cmds.joint(p=(-1.0, 0.5, 0), n="test_R_foot_jnt")
	
	cmds.parent(pelvis, test_grp)
	
	# Orient joints cleanly
	for leg_root in [l_thigh, r_thigh]:
		cmds.joint(leg_root, e=True, oj="xyz", sao="yup", ch=True, zso=True)
		
	# Add simple IK handles to legs for easy posing
	l_leg_ik = cmds.ikHandle(sj=l_thigh, ee=l_foot, sol="ikRPsolver", n="test_L_leg_ik")[0]
	r_leg_ik = cmds.ikHandle(sj=r_thigh, ee=r_foot, sol="ikRPsolver", n="test_R_leg_ik")[0]
	cmds.parent([l_leg_ik, r_leg_ik], test_grp)
	
	# Move IK handles to make legs straight
	cmds.setAttr(f"{l_leg_ik}.translateY", 0.5)
	cmds.setAttr(f"{l_leg_ik}.translateZ", 0.0)
	cmds.setAttr(f"{r_leg_ik}.translateY", 0.5)
	cmds.setAttr(f"{r_leg_ik}.translateZ", 0.0)
	
	# 2. Create a mock skirt geometry (NURBS Cylinder) for visualization
	skirt_geom_grp = cmds.group(em=True, n="skirt_geometry_grp")
	skirt_mesh = cmds.nurbsCylinder(ax=(0, 1, 0), r=1.8, hr=2.5, s=8, n="mock_skirt_mesh")[0]
	cmds.setAttr(f"{skirt_mesh}.translate", 0, 7.5, 0)
	cmds.parent(skirt_mesh, skirt_geom_grp)
	
	# Apply soft color to the mock skirt mesh
	shading_grp = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="skirt_shader_SG")
	shader = cmds.shadingNode("lambert", asShader=True, name="skirt_material")
	cmds.setAttr(f"{shader}.color", 0.8, 0.4, 0.5, type="double3")
	cmds.setAttr(f"{shader}.transparency", 0.4, 0.4, 0.4, type="double3")
	cmds.connectAttr(f"{shader}.outColor", f"{shading_grp}.surfaceShader")
	cmds.sets(skirt_mesh, edit=True, forceElement=shading_grp)
	
	# Clear selection
	cmds.select(cl=True)
	
	return pelvis, l_thigh, r_thigh, l_knee, r_knee


class AutoSkirtUI:
	"""
	GUI class to provide an artist-friendly window for 
	generating the auto-skirt rig system.
	"""
	def __init__(self) -> None:
		self.window_name = "AutoSkirtRigGenerator"
		self.window_title = "Auto Skirt Rig Generator"
		
	def show(self) -> None:
		"""Draw and display the UI window."""
		if cmds.window(self.window_name, exists=True):
			cmds.deleteUI(self.window_name)
			
		self.window = cmds.window(
			self.window_name,
			title=self.window_title,
			widthHeight=(470, 580),
			menuBar=True,
			sizeable=True
		)
		
		# Wrap everything in a scroll layout to prevent UI elements from falling off
		scroll_layout = cmds.scrollLayout(childResizable=True)
		
		# Main layout
		main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

		
		# Title Banner
		cmds.text(label="Auto Skirt Rigging System", font="boldLabelFont", height=25)
		cmds.text(label="Procedural distance-based collision rig (Game Engine Friendly)", align="left")
		cmds.separator(height=10, style="double")
		
		# Section 1: Joint Setup Inputs
		cmds.text(label="1. Target Joint Selection", font="boldLabelFont", align="left")
		
		self.pelvis_tf = self.create_selection_row("Pelvis/Hips:", main_layout)
		self.l_thigh_tf = self.create_selection_row("Left Thigh:", main_layout)
		self.r_thigh_tf = self.create_selection_row("Right Thigh:", main_layout)
		self.l_knee_tf = self.create_selection_row("Left Knee:", main_layout)
		self.r_knee_tf = self.create_selection_row("Right Knee:", main_layout)
		
		cmds.separator(height=10, style="single")
		
		# Section 2: Rigging Parameters
		cmds.text(label="2. Rigging Settings", font="boldLabelFont", align="left")
		
		self.chains_if = cmds.intSliderGrp(label="Skirt Chains:", min=4, max=24, value=8, field=True)
		self.jnts_if = cmds.intSliderGrp(label="Joints Per Chain:", min=2, max=5, value=3, field=True)
		
		# Top Radius
		cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(350, 70), columnAttach2=("both", "both"))
		self.rad_top_ff = cmds.floatSliderGrp(label="Top Radius:", min=0.1, max=10.0, value=1.5, field=True, precision=2)
		cmds.button(label="Measure", command=self.on_measure_top_rad, bgc=(0.2, 0.35, 0.45))
		cmds.setParent(main_layout)
		
		# Bottom Radius
		cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(350, 70), columnAttach2=("both", "both"))
		self.rad_bot_ff = cmds.floatSliderGrp(label="Bottom Radius:", min=0.1, max=15.0, value=2.2, field=True, precision=2)
		cmds.button(label="Measure", command=self.on_measure_bot_rad, bgc=(0.2, 0.35, 0.45))
		cmds.setParent(main_layout)
		
		# Skirt Height
		cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(350, 70), columnAttach2=("both", "both"))
		self.height_ff = cmds.floatSliderGrp(label="Skirt Height:", min=0.1, max=20.0, value=4.0, field=True, precision=2)
		cmds.button(label="Measure", command=self.on_measure_height, bgc=(0.2, 0.35, 0.45))
		cmds.setParent(main_layout)
		
		# Thigh Collider Rad
		cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(350, 70), columnAttach2=("both", "both"))
		self.thigh_rad_ff = cmds.floatSliderGrp(label="Thigh Collider Rad:", min=0.1, max=5.0, value=1.0, field=True, precision=2)
		cmds.button(label="Measure", command=self.on_measure_thigh_rad, bgc=(0.2, 0.35, 0.45))
		cmds.setParent(main_layout)
		
		# Knee Collider Rad
		cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(350, 70), columnAttach2=("both", "both"))
		self.knee_rad_ff = cmds.floatSliderGrp(label="Knee Collider Rad:", min=0.1, max=5.0, value=0.8, field=True, precision=2)
		cmds.button(label="Measure", command=self.on_measure_knee_rad, bgc=(0.2, 0.35, 0.45))
		cmds.setParent(main_layout)
		
		cmds.separator(height=15, style="double")
		
		# Action Buttons
		cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnWidth3=(140, 140, 140), columnAttach3=("both", "both", "both"))
		cmds.button(label="Build Test Scene", command=self.on_build_test_scene, bgc=(0.25, 0.45, 0.45))
		cmds.button(label="Generate Rig", command=self.on_generate, bgc=(0.3, 0.5, 0.3))
		cmds.button(label="Close", command=lambda x: cmds.deleteUI(self.window_name))
		
		cmds.showWindow(self.window)
		
	def create_selection_row(self, label: str, parent: str) -> str:
		"""Helper to create a layout row with a textfield and a Selection load button."""
		row = cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnWidth3=(90, 250, 60), columnAttach3=("both", "both", "both"))
		cmds.text(label=label, align="right")
		tf = cmds.textField()
		if label == "Pelvis/Hips:":
			cmds.button(label="Load Sel", command=lambda x: self.load_selected_pelvis(tf))
		else:
			cmds.button(label="Load Sel", command=lambda x: self.load_selected(tf))
		cmds.setParent(parent)
		return tf
		
	def load_selected(self, text_field: str) -> None:
		"""Loads selected node name into the textfield."""
		selection = cmds.ls(sl=True)
		if selection:
			cmds.textField(text_field, edit=True, text=selection[0])
		else:
			cmds.warning("Please select a joint in the scene first.")
			
	def load_selected_pelvis(self, text_field: str) -> None:
		"""Loads selected pelvis joint and tries to auto-detect thighs and knees in its hierarchy."""
		selection = cmds.ls(sl=True)
		if not selection:
			cmds.warning("Please select the Pelvis/Hip joint first.")
			return
			
		pelvis_node = selection[0]
		cmds.textField(text_field, edit=True, text=pelvis_node)
		
		# Traverse hierarchy to find thighs and knees
		all_descendants = cmds.listRelatives(pelvis_node, allDescendents=True, type='joint') or []
		
		# Define keywords for detection
		l_thigh_patterns = ["l_thigh", "l_upleg", "left_thigh", "left_upleg", "l_leg", "left_leg"]
		r_thigh_patterns = ["r_thigh", "r_upleg", "right_thigh", "right_upleg", "r_leg", "right_leg"]
		l_knee_patterns = ["l_knee", "l_lowleg", "left_knee", "left_lowleg", "l_shin", "left_shin"]
		r_knee_patterns = ["r_knee", "r_lowleg", "right_knee", "right_lowleg", "r_shin", "right_shin"]
		
		detected = {}
		
		for joint in all_descendants:
			name_lower = joint.lower()
			
			# Check L Thigh
			if any(pattern in name_lower for pattern in l_thigh_patterns) and not detected.get("l_thigh"):
				detected["l_thigh"] = joint
			# Check R Thigh
			elif any(pattern in name_lower for pattern in r_thigh_patterns) and not detected.get("r_thigh"):
				detected["r_thigh"] = joint
			# Check L Knee
			elif any(pattern in name_lower for pattern in l_knee_patterns) and not detected.get("l_knee"):
				detected["l_knee"] = joint
			# Check R Knee
			elif any(pattern in name_lower for pattern in r_knee_patterns) and not detected.get("r_knee"):
				detected["r_knee"] = joint
				
		# Fill fields if detected
		if detected.get("l_thigh"):
			cmds.textField(self.l_thigh_tf, edit=True, text=detected["l_thigh"])
		if detected.get("r_thigh"):
			cmds.textField(self.r_thigh_tf, edit=True, text=detected["r_thigh"])
		if detected.get("l_knee"):
			cmds.textField(self.l_knee_tf, edit=True, text=detected["l_knee"])
		if detected.get("r_knee"):
			cmds.textField(self.r_knee_tf, edit=True, text=detected["r_knee"])
			
		print("Hierarchy scan completed. Automatically detected leg joints:")
		for k, v in detected.items():
			print(f"  - {k}: {v}")
			
	def get_selection_pos_and_pelvis(self) -> Optional[Tuple[List[float], List[float]]]:
		"""Helper to get positions of selected item and pelvis joint."""
		pelvis = cmds.textField(self.pelvis_tf, q=True, text=True)
		if not pelvis or not cmds.objExists(pelvis):
			cmds.warning("Please specify a valid Pelvis joint first.")
			return None
			
		selection = cmds.ls(sl=True, fl=True)  # fl=True to flatten component selection
		if not selection:
			cmds.warning("Please select a target object or vertex in the scene to measure.")
			return None
			
		# Get pelvis world position
		pelvis_pos = cmds.xform(pelvis, q=True, ws=True, t=True)
		# Get selection world position
		sel_pos = cmds.xform(selection[0], q=True, ws=True, t=True)
		
		return pelvis_pos, sel_pos

	def on_measure_top_rad(self, *args) -> None:
		"""Measure horizontal distance from pelvis to selection and update Top Radius."""
		res = self.get_selection_pos_and_pelvis()
		if not res:
			return
		pelvis_pos, sel_pos = res
		
		# Calculate horizontal distance on XZ plane
		dx = sel_pos[0] - pelvis_pos[0]
		dz = sel_pos[2] - pelvis_pos[2]
		radius = math.sqrt(dx * dx + dz * dz)
		
		# Update slider value
		cmds.floatSliderGrp(self.rad_top_ff, edit=True, value=radius)
		print(f"Top Radius measured: {radius:.3f}")

	def on_measure_bot_rad(self, *args) -> None:
		"""Measure horizontal distance from pelvis to selection and update Bottom Radius."""
		res = self.get_selection_pos_and_pelvis()
		if not res:
			return
		pelvis_pos, sel_pos = res
		
		# Calculate horizontal distance on XZ plane
		dx = sel_pos[0] - pelvis_pos[0]
		dz = sel_pos[2] - pelvis_pos[2]
		radius = math.sqrt(dx * dx + dz * dz)
		
		# Update slider value
		cmds.floatSliderGrp(self.rad_bot_ff, edit=True, value=radius)
		print(f"Bottom Radius measured: {radius:.3f}")

	def on_measure_height(self, *args) -> None:
		"""Measure vertical distance from pelvis to selection and update Skirt Height."""
		res = self.get_selection_pos_and_pelvis()
		if not res:
			return
		pelvis_pos, sel_pos = res
		
		# Calculate vertical distance (Y axis)
		height = pelvis_pos[1] - sel_pos[1]
		
		if height <= 0:
			cmds.warning("The selected point is higher than or equal to the Pelvis joint. Height must be positive.")
			return
			
		# Update slider value
		cmds.floatSliderGrp(self.height_ff, edit=True, value=height)
		print(f"Skirt Height measured: {height:.3f}")
		
	def on_measure_thigh_rad(self, *args) -> None:
		"""Measure 3D distance from thigh joint to selection and update Thigh Collider Rad."""
		thigh = cmds.textField(self.l_thigh_tf, q=True, text=True)
		if not thigh or not cmds.objExists(thigh):
			thigh = cmds.textField(self.r_thigh_tf, q=True, text=True)
			
		if not thigh or not cmds.objExists(thigh):
			cmds.warning("Please specify a valid Left or Right Thigh joint first.")
			return
			
		selection = cmds.ls(sl=True, fl=True)
		if not selection:
			cmds.warning("Please select a vertex on the thigh skin to measure.")
			return
			
		thigh_pos = cmds.xform(thigh, q=True, ws=True, t=True)
		sel_pos = cmds.xform(selection[0], q=True, ws=True, t=True)
		
		# Calculate 3D distance
		dist = math.sqrt(
			(sel_pos[0] - thigh_pos[0])**2 +
			(sel_pos[1] - thigh_pos[1])**2 +
			(sel_pos[2] - thigh_pos[2])**2
		)
		
		cmds.floatSliderGrp(self.thigh_rad_ff, edit=True, value=dist)
		print(f"Thigh Collider Radius measured: {dist:.3f}")

	def on_measure_knee_rad(self, *args) -> None:
		"""Measure 3D distance from knee joint to selection and update Knee Collider Rad."""
		knee = cmds.textField(self.l_knee_tf, q=True, text=True)
		if not knee or not cmds.objExists(knee):
			knee = cmds.textField(self.r_knee_tf, q=True, text=True)
			
		if not knee or not cmds.objExists(knee):
			cmds.warning("Please specify a valid Left or Right Knee joint first.")
			return
			
		selection = cmds.ls(sl=True, fl=True)
		if not selection:
			cmds.warning("Please select a vertex on the knee skin to measure.")
			return
			
		knee_pos = cmds.xform(knee, q=True, ws=True, t=True)
		sel_pos = cmds.xform(selection[0], q=True, ws=True, t=True)
		
		# Calculate 3D distance
		dist = math.sqrt(
			(sel_pos[0] - knee_pos[0])**2 +
			(sel_pos[1] - knee_pos[1])**2 +
			(sel_pos[2] - knee_pos[2])**2
		)
		
		cmds.floatSliderGrp(self.knee_rad_ff, edit=True, value=dist)
		print(f"Knee Collider Radius measured: {dist:.3f}")
		
	def on_build_test_scene(self, *args) -> None:
		"""Creates the test rig and loads names into the UI."""
		pelvis, l_thigh, r_thigh, l_knee, r_knee = build_sample_scene()
		
		cmds.textField(self.pelvis_tf, edit=True, text=pelvis)
		cmds.textField(self.l_thigh_tf, edit=True, text=l_thigh)
		cmds.textField(self.r_thigh_tf, edit=True, text=r_thigh)
		cmds.textField(self.l_knee_tf, edit=True, text=l_knee)
		cmds.textField(self.r_knee_tf, edit=True, text=r_knee)
		
		cmds.viewFit(all=True)
		
	def on_generate(self, *args) -> None:
		"""Handles the rig generation process."""
		# Retrieve values
		pelvis = cmds.textField(self.pelvis_tf, q=True, text=True)
		l_thigh = cmds.textField(self.l_thigh_tf, q=True, text=True)
		r_thigh = cmds.textField(self.r_thigh_tf, q=True, text=True)
		l_knee = cmds.textField(self.l_knee_tf, q=True, text=True)
		r_knee = cmds.textField(self.r_knee_tf, q=True, text=True)
		
		num_chains = cmds.intSliderGrp(self.chains_if, q=True, value=True)
		joints_per_chain = cmds.intSliderGrp(self.jnts_if, q=True, value=True)
		
		rad_top = cmds.floatSliderGrp(self.rad_top_ff, q=True, value=True)
		rad_bot = cmds.floatSliderGrp(self.rad_bot_ff, q=True, value=True)
		height = cmds.floatSliderGrp(self.height_ff, q=True, value=True)
		
		thigh_rad = cmds.floatSliderGrp(self.thigh_rad_ff, q=True, value=True)
		knee_rad = cmds.floatSliderGrp(self.knee_rad_ff, q=True, value=True)
		
		# Verify inputs
		for name, node in [("Pelvis", pelvis), ("Left Thigh", l_thigh), ("Right Thigh", r_thigh), ("Left Knee", l_knee), ("Right Knee", r_knee)]:
			if not node or not cmds.objExists(node):
				cmds.error(f"Please input a valid joint for {name}.")
				return
				
		# Build
		build_auto_skirt(
			pelvis=pelvis,
			left_thigh=l_thigh,
			right_thigh=r_thigh,
			left_knee=l_knee,
			right_knee=r_knee,
			num_chains=num_chains,
			joints_per_chain=joints_per_chain,
			skirt_radius_top=rad_top,
			skirt_radius_bottom=rad_bot,
			thigh_radius=thigh_rad,
			knee_radius=knee_rad,
			skirt_height=height
		)
		
		cmds.confirmDialog(
			title="Success", 
			message="Auto Skirt Rig successfully generated!", 
			button=["OK"]
		)


def main() -> None:
	"""Entry point to launch the UI."""
	ui = AutoSkirtUI()
	ui.show()



if __name__ == "__main__":
	main()
