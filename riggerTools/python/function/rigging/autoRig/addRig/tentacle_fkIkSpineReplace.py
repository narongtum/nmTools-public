import maya.cmds as mc
import pymel.core as pm

from function.rigging.autoRig.base import core
from function.rigging.autoRig.base import rigTools
from function.rigging.constraint import pinLocatorToSurface as pls
from function.rigging.controllerBox import adjustController as adjust
from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.constraint import matrixConstraint as mtc


# Reload dependencies to ensure we are using the latest code
reload(core)
reload(rigTools)
reload(pls)
reload(adjust)
reload(mtc)


# ==============================================================================
# USER Import
# ==============================================================================
from function.pipeline import logger 
reload(logger)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

class FkIkSpineReplace(logger.MayaLogger):
	LOGGER_NAME = "tentacle_fkIkSpineReplace"



'''
# ==============================================================================
# USER INPUTS: Define parameters here
# ==============================================================================
nurbs_surface = 'C_legPlane_nrb'         # Name of the NURBS surface (user must create this first)
num_pins = 16                       # Number of detail locators to pin along the surface
num_fk_joints = 6                  # Number of FK driver joints (Step 3)
region = 'leg'                   # Name prefix for the rig components
side = 'C'                         # Side code (e.g., LFT, RGT, C, L, R)
ctrl_shape = 'circle_Y_along_ctrlShape'    # Shape library name for the controller
scale = 1.0                        # Global scale factor for locators and controllers
joint_orient = 'yxz'               # Orientation for all joints (e.g. 'yxz', 'xyz')
secondary_orient = 'zup'           # Secondary axis orientation (e.g. 'zup', 'yup')
fk_ctrlShape = 'circle_ctrlShape'  # Shape library name for FK controllers
ik_ctrlShape = 'cube_ctrlShape'    # Shape library name for IK controllers
rotate_order = 'xzy'               # Rotation order for controllers
prior_joint = 'hip_bJnt'                   # Prior joint to parent the bind joint chain (leave empty to keep under world)
stickShape = 'stickCircle_Y_long_ctrlShape' # Shape library name for the stick/end controller
parentMatrix = True                 # If True, use parentConMatrixGPT for bJnt to jnt. If False, use parentConstraint/scaleConstraint.

# Note: Color and rotate order for step 1 & 2 controllers are determined by the default
# settings inside pls.pin_locator_surface ('yellow' and 'xzy').

'''



# ==============================================================================
# RIG CREATION STEP 1 & 2
# ==============================================================================



def tentacle_fkIkReplace(   nurbs_surface = 'C_legPlane_nrb',         # Name of the NURBS surface (user must create this first)
							num_pins = 16  ,                     # Number of detail locators to pin along the surface
							num_fk_joints = 6  ,                # Number of FK driver joints (Step 3)
							region = 'leg' ,                  # Name prefix for the rig components
							side = 'C'    ,                     # Side code (e.g., LFT, RGT, C, L, R)
							ctrl_shape = 'circle_Y_along_ctrlShape' ,   # Shape library name for the controller
							scale = 1.0       ,                 # Global scale factor for locators and controllers
							joint_orient = 'yxz'   ,            # Orientation for all joints (e.g. 'yxz', 'xyz')
							secondary_orient = 'zup'    ,       # Secondary axis orientation (e.g. 'zup', 'yup')
							fk_ctrlShape = 'circle_ctrlShape' , # Shape library name for FK controllers
							ik_ctrlShape = 'cube_ctrlShape'  ,  # Shape library name for IK controllers
							rotate_order = 'xzy' ,              # Rotation order for controllers
							prior_joint = 'hip_bJnt'   ,     # Prior joint to parent the bind joint chain (leave empty to keep under world)
							priorCtrl = '' ,             
							stickShape = 'stickCircle_Y_long_ctrlShape', # Shape library name for the stick/end controller
							jnt_grp = 'jnt_grp',
							noTouch = 'noTouch_grp',
							parentMatrix = True ):


	core.makeHeader("Start of Tentacle FkIk Spine Replace")

	color_side = mnd.getColorPart(side)


	# 1. Validate the NURBS surface
	if not pm.objExists(nurbs_surface):
		mc.error(f"NURBS surface '{nurbs_surface}' does not exist. Please create it first.")

	oNurbs = pm.PyNode(nurbs_surface)
	if isinstance(oNurbs, pm.nodetypes.Transform):
		pass
	elif isinstance(oNurbs, pm.nodetypes.NurbsSurface):
		oNurbs = oNurbs.getTransform()

	nurbs_shape = oNurbs.getShape()

	# Get the min/max range of U and V coordinates
	paramLengthU = nurbs_shape.minMaxRangeU.get()
	paramLengthV = nurbs_shape.minMaxRangeV.get()

	u_min, u_max = paramLengthU[0], paramLengthU[1]
	v_min, v_max = paramLengthV[0], paramLengthV[1]
	v_pos = (v_min + v_max) * 0.5  # Position V at the center of the surface

	# Calculate evenly distributed U coordinate values along the surface
	if num_pins > 1:
		step = (u_max - u_min) / float(num_pins - 1)
		u_values = [u_min + step * i for i in range(num_pins)]
	else:
		u_values = [(u_min + u_max) * 0.5]

	# Create root groups for clean organization
	main_grp_name = f'{side}_{region}_Rig_grp'
	loc_grp_name = f'{side}_{region}_loc_grp'

	main_grp = pm.group(em=True, name=main_grp_name)
	loc_grp = pm.group(em=True, name=loc_grp_name)
	pm.parent(loc_grp, main_grp)

	print(f"Generating {num_pins} temporary locators along {nurbs_surface}...")

	temp_locs = []
	for i, u_val in enumerate(u_values):
		num = i + 1
		loc_name = f'{side}_{region}{num:02d}_loc'
		
		# Calculate 3D position on the NURBS surface at UV coordinates
		pos = mc.pointOnSurface(nurbs_surface, u=u_val, v=v_pos, position=True)
		
		# Create temp locator and position it
		loc = mc.spaceLocator(name=loc_name)[0]
		mc.xform(loc, translation=pos, worldSpace=True)
		temp_locs.append(loc)

	# 1. & 1.1 Pin locators to surface and create controllers using the function in the repo
	# This replaces the temp locators with matrix-pinned locators.
	pinned_locs = pls.pin_locator_surface(
		nurbs=nurbs_surface,
		region=region,
		side=side,
		source_loc=temp_locs,
		locator_scale=scale,
		creJnt=True,
		suffixJnt='jnt',
		creCtrl=True,
		ctrlShape=ctrl_shape,
		snapAtEnd=False,
		priorJnt='',
		scale=scale
	)

	# Parent the pinned locators to the locator group to keep Outliner clean
	for loc in pinned_locs:
		pm.parent(loc, loc_grp)

	# 2. Orient and parent each detail joint under its respective gimbal controller
	print("Orienting and parenting detail joints under gimbal controllers...")
	# Temporarily chain the detail joints to orient them
	for i in range(num_pins):
		num = i + 1
		base_name = f'{side}_{region}{num:02d}'
		joint_name = f'{base_name}_jnt'
		
		if i > 0:
			prev_joint = f'{side}_{region}{i:02d}_jnt'
			if mc.objExists(joint_name) and mc.objExists(prev_joint):
				mc.parent(joint_name, prev_joint)

	# Orient the temporary joint chain
	if num_pins > 0:
		root_joint = f'{side}_{region}01_jnt'
		if mc.objExists(root_joint):
			mc.joint(root_joint, e=True, oj=joint_orient, sao=secondary_orient, ch=True, zso=True)
			
			# Zero out orient of the last joint in the chain
			last_joint = f'{side}_{region}{num_pins:02d}_jnt'
			if mc.objExists(last_joint):
				mc.setAttr(f'{last_joint}.jointOrientX', 0)
				mc.setAttr(f'{last_joint}.jointOrientY', 0)
				mc.setAttr(f'{last_joint}.jointOrientZ', 0)

	# Parent each joint back under its respective gimbal controller
	for i in range(num_pins):
		num = i + 1
		base_name = f'{side}_{region}{num:02d}'
		
		joint_name = f'{base_name}_jnt'
		gimbal_ctrl = f'{base_name}_gmbCtrl'
		
		if mc.objExists(joint_name) and mc.objExists(gimbal_ctrl):
			mc.parent(joint_name, gimbal_ctrl)

	print("Rig Setup Step 1 & 2 completed successfully!")

	# ==============================================================================
	# RIG CREATION STEP 3: Create FK Driver Joint Chain
	# ==============================================================================

	# Calculate evenly distributed U coordinate values for the FK joints
	if num_fk_joints > 1:
		step_fk = (u_max - u_min) / float(num_fk_joints - 1)
		u_values_fk = [u_min + step_fk * i for i in range(num_fk_joints)]
	else:
		u_values_fk = [(u_min + u_max) * 0.5]

	# Create an FK driver joints group for organization
	fk_jnt_grp_name = f'{side}_{region}_fkJnt_grp'
	fk_jnt_grp = pm.group(em=True, name=fk_jnt_grp_name)
	pm.parent(fk_jnt_grp, world=True)

	print(f"Generating {num_fk_joints} FK driver joints along {nurbs_surface}...")

	fk_joints = []
	for i, u_val in enumerate(u_values_fk):
		num = i + 1
		fk_jnt_name = f'{side}_{region}_fk{num:02d}_fkJnt'
		
		# Calculate 3D position on the surface
		pos = mc.pointOnSurface(nurbs_surface, u=u_val, v=v_pos, position=True)
		
		# Create the joint (larger radius for easy selection, colored red)
		jnt = core.Joint(name=fk_jnt_name, radius=scale * 1.5, scaleCompensate=False)
		# jnt.setJointColor('red')
		
		# Position joint in world space
		mc.xform(jnt.name, translation=pos, worldSpace=True)
		
		fk_joints.append(jnt)
		
		if i > 0:
			# Parent to the previous joint to form the chain
			mc.parent(jnt.name, fk_joints[i-1].name)
		else:
			# Parent the root of the chain to the FK group
			mc.parent(jnt.name, fk_jnt_grp.name())

	# Orient the joint chain down the bone
	if len(fk_joints) > 0:
		root_fk = fk_joints[0].name
		mc.joint(root_fk, e=True, oj=joint_orient, sao=secondary_orient, ch=True, zso=True)
		
		# Zero out orient of the last joint in the chain
		last_fk = fk_joints[-1].name
		mc.setAttr(f'{last_fk}.jointOrientX', 0)
		mc.setAttr(f'{last_fk}.jointOrientY', 0)
		mc.setAttr(f'{last_fk}.jointOrientZ', 0)

	# Create an FK controllers group for organization
	fk_ctrl_grp_name = f'{side}_{region}_fkCtrl_grp'
	fk_ctrl_grp = pm.group(em=True, name=fk_ctrl_grp_name)
	pm.parent(fk_ctrl_grp, main_grp)

	print("Creating FK controllers and parenting them in hierarchy...")
	# Call creControllerFunc on all FK joints
	fk_ctrl_names = [jnt.name for jnt in fk_joints]
	fk_ctrls = adjust.creControllerFunc(
		selected=fk_ctrl_names,
		scale=scale * 4.5,
		ctrlShape=fk_ctrlShape,
		color=color_side,
		constraint=True,
		matrixConst=True,
		rotateOrder=rotate_order,
		parentUnder=False
	)

	# Parent the FK controllers in hierarchy: Zero group of current under Gimbal of previous
	for i in range(1, num_fk_joints):
		current_zro = fk_ctrls[3 * i]
		prev_gmb = fk_ctrls[3 * (i - 1) + 2]
		mc.parent(current_zro, prev_gmb)

	# Parent the root FK controller's Zero group to the FK controllers group
	if len(fk_ctrls) > 0:
		mc.parent(fk_ctrls[0], fk_ctrl_grp_name)

	print("Rig Setup Step 3 completed successfully!")

	# ==============================================================================
	# RIG CREATION STEP 4: Create IK Driver Joints and Controllers
	# ==============================================================================

	# Create an IK driver joints group for organization
	ik_jnt_grp_name = f'{side}_{region}_ikJnt_grp'
	ik_jnt_grp = pm.group(em=True, name=ik_jnt_grp_name)
	pm.parent(ik_jnt_grp, world = True)

	# Create an IK controllers group for organization
	ik_ctrl_grp_name = f'{side}_{region}_ikCtrl_grp'
	ik_ctrl_grp = pm.group(em=True, name=ik_ctrl_grp_name)
	pm.parent(ik_ctrl_grp, main_grp)

	print(f"Generating {num_fk_joints} IK driver joints along {nurbs_surface}...")

	ik_joints = []


	for i, u_val in enumerate(u_values_fk):
		num = i + 1
		ik_jnt_name = f'{side}_{region}_ik{num:02d}_ikJnt'
		fk_jnt_name = f'{side}_{region}_fk{num:02d}_fkJnt'
		
		# Create the joint (larger radius, colored blue for IK)
		jnt = core.Joint(name=ik_jnt_name, radius=scale * 1.5, scaleCompensate=False)
		jnt.setJointColor('blue')
		
		# Parent directly to the IK joint group (independent/no hierarchy chain)
		mc.parent(jnt.name, ik_jnt_grp_name)
		
		# Snap position and orientation of the corresponding FK joint
		if mc.objExists(fk_jnt_name):
			mc.matchTransform(jnt.name, fk_jnt_name, pos=True, rot=True)
		
		ik_joints.append(jnt)


	print("Creating IK controllers and linking them via matrix constraint...")
	# Call creControllerFunc on all IK joints
	ik_ctrl_names = [jnt.name for jnt in ik_joints]
	ik_ctrls = adjust.creControllerFunc(
		selected=ik_ctrl_names,
		scale=scale * 4.5,
		ctrlShape=ik_ctrlShape,
		color=color_side,
		constraint=True,
		matrixConst=True,
		rotateOrder=rotate_order,
		parentUnder=False
	)

	# Parent all IK controller Zero groups to the IK controllers group (independent/no hierarchy chain)
	for i in range(num_fk_joints):
		zro_grp = ik_ctrls[3 * i]
		if mc.objExists(zro_grp):
			mc.parent(zro_grp, ik_ctrl_grp_name)

	print("Rig Setup Step 4 completed successfully!")

	# ==============================================================================
	# RIG CREATION STEP 5: Duplicate NURBS Surfaces and Auto-Skin
	# ==============================================================================

	def auto_skin_nurbs_ribbon(nurbs_name, joints, skin_cluster_name, smooth_method='smoothstep'):
		"""
		Automatically calculates and sets weights for a NURBS ribbon based on UV coordinate interpolation.
		
		Supported smooth_methods:
		- 'smoothstep': Standard smooth blending (ideal for IK)
		- 'linear': Straight linear interpolation (medium blend)
		- 'sharp': High-contrast transition (less diffuse, ideal for FK)
		- 'rigid': 100% influence from the closest joint (no blend)
		"""
		# Get the number of CVs in U and V directions
		num_cvs_u = mc.getAttr(f'{nurbs_name}.spansU') + mc.getAttr(f'{nurbs_name}.degreeU')
		num_cvs_v = mc.getAttr(f'{nurbs_name}.spansV') + mc.getAttr(f'{nurbs_name}.degreeV')
		
		num_joints = len(joints)
		
		print(f"Calculating smooth skin weights ({smooth_method}) mathematically for {nurbs_name} with {num_joints} joints...")
		
		for u in range(num_cvs_u):
			pos_u = float(u) / float(num_cvs_u - 1) if num_cvs_u > 1 else 0.5
			
			# Find which two joints this U position lies between
			joint_float_idx = pos_u * (num_joints - 1)
			idx_lower = int(joint_float_idx)
			idx_upper = min(idx_lower + 1, num_joints - 1)
			
			if idx_lower == idx_upper:
				weight_lower = 1.0
				weight_upper = 0.0
			else:
				t = joint_float_idx - idx_lower
				
				# Select interpolation method
				if smooth_method == 'linear':
					t_val = t
				elif smooth_method == 'sharp':
					# Contrast function (exponent 3) to keep weights sharper near joint centers
					if t < 0.5:
						t_val = 4.0 * (t ** 3)
					else:
						t_val = 1.0 - 4.0 * ((1.0 - t) ** 3)
				elif smooth_method == 'rigid':
					t_val = 1.0 if t >= 0.5 else 0.0
				else:  # smoothstep
					t_val = t * t * (3.0 - 2.0 * t)
					
				weight_upper = t_val
				weight_lower = 1.0 - t_val
				
			# Build the weight list for skinPercent
			weight_list = []
			for j_idx, jnt in enumerate(joints):
				if j_idx == idx_lower:
					weight_list.append((jnt, weight_lower))
				elif j_idx == idx_upper:
					weight_list.append((jnt, weight_upper))
				else:
					weight_list.append((jnt, 0.0))
					
			# Set weights for all V CVs at this U index
			for v in range(num_cvs_v):
				cv_name = f'{nurbs_name}.cv[{u}][{v}]'
				mc.skinPercent(skin_cluster_name, cv_name, transformValue=weight_list, normalize=True)

	# 1. Duplicate the NURBS surface
	fk_nurbs_name = f'{side}_{region}_fkNrb'
	ik_nurbs_name = f'{side}_{region}_ikNrb'

	# Remove if they already exist to prevent duplicate suffix issues
	if mc.objExists(fk_nurbs_name):
		mc.delete(fk_nurbs_name)
	if mc.objExists(ik_nurbs_name):
		mc.delete(ik_nurbs_name)

	fk_nurbs = mc.duplicate(nurbs_surface, name=fk_nurbs_name)[0]
	ik_nurbs = mc.duplicate(nurbs_surface, name=ik_nurbs_name)[0]

	# Parent them under world
	pm.parent(fk_nurbs, world=True)
	pm.parent(ik_nurbs, world=True)

	print(f"Duplicated {nurbs_surface} into {fk_nurbs} and {ik_nurbs}.")

	# 2. SkinWeight the FK NURBS surface to FK driver joints (using 'sharp' weight curve to prevent diffuse weighting)
	fk_jnt_names = [jnt.name for jnt in fk_joints]
	fk_skin_cluster = mc.skinCluster(fk_jnt_names, fk_nurbs, toSelectedBones=True, maximumInfluences=2, dropoffRate=1.5, bindMethod=0)[0]
	auto_skin_nurbs_ribbon(fk_nurbs, fk_jnt_names, fk_skin_cluster, smooth_method='sharp')

	# 3. SkinWeight the IK NURBS surface to IK driver joints (using standard 'smoothstep')
	ik_jnt_names = [jnt.name for jnt in ik_joints]
	ik_skin_cluster = mc.skinCluster(ik_jnt_names, ik_nurbs, toSelectedBones=True, maximumInfluences=2, dropoffRate=1.5, bindMethod=0)[0]
	auto_skin_nurbs_ribbon(ik_nurbs, ik_jnt_names, ik_skin_cluster, smooth_method='smoothstep')

	print("Rig Setup Step 5 completed successfully!")

	# ==============================================================================
	# RIG CREATION STEP 6: Create Blendshape and Bind Joint Chain
	# ==============================================================================

	print("Creating blendshape to connect FK/IK NURBS to the primary surface...")
	bsh_name = f'{side}_{region}_nrb_bsh'
	if mc.objExists(bsh_name):
		mc.delete(bsh_name)

	bsh_node = mc.blendShape(fk_nurbs, ik_nurbs, nurbs_surface, name=bsh_name)[0]

	print("Creating bind joint chain (_bJnt) by duplicating detail joints...")
	b_joints = []
	for i in range(num_pins):
		num = i + 1
		jnt_name = f'{side}_{region}{num:02d}_jnt'
		b_jnt_name = f'{side}_{region}{num:02d}_bJnt'
		
		# Clean up old duplicate if exists
		if mc.objExists(b_jnt_name):
			mc.delete(b_jnt_name)
			
		if mc.objExists(jnt_name):
			# Duplicate only the joint itself (no children/shapes)
			dup_jnt = mc.duplicate(jnt_name, name=b_jnt_name, parentOnly=True)[0]
			
			# Enable override color and set color to green (ID 14) for bind joints
			mc.setAttr(f"{dup_jnt}.overrideEnabled", True)
			mc.setAttr(f"{dup_jnt}.overrideColor", 14)
			
			# Ensure segmentScaleCompensate is False per RULE.md standards
			mc.setAttr(f"{dup_jnt}.segmentScaleCompensate", False)
			
			b_joints.append(dup_jnt)

	# Parent the duplicated bind joints hierarchically from low to high
	print("Parenting bind joints in a hierarchical chain...")
	for i in range(1, len(b_joints)):
		mc.parent(b_joints[i], b_joints[i-1])

	# Parent the root of the bind joint chain under prior_joint if specified
	if len(b_joints) > 0:
		root_b_joint = b_joints[0]
		if prior_joint and mc.objExists(prior_joint):
			print(f"Parenting root bind joint '{root_b_joint}' under prior joint '{prior_joint}'...")
			mc.parent(root_b_joint, prior_joint)
		else:
			print(f"No valid prior joint specified. Root bind joint '{root_b_joint}' will reside under world.")
			mc.parent(root_b_joint, world=True)

	print("Rig Setup Step 6 completed successfully!")

	# Constraint bJnt to follow jnt
	print("Constraining bind joints to follow detail joints...")
	for i in range(num_pins):
		num = i + 1
		jnt_name = f'{side}_{region}{num:02d}_jnt'
		b_jnt_name = f'{side}_{region}{num:02d}_bJnt'
		
		if mc.objExists(jnt_name) and mc.objExists(b_jnt_name):
			if parentMatrix:
				print(f"Matrix constraining '{b_jnt_name}' to follow '{jnt_name}'...")
				mtc.parentConMatrixGPT(source=jnt_name, target=b_jnt_name, mo=True, translate=True, rotate=True, scale=True)
			else:
				print(f"Parent constraining '{b_jnt_name}' to follow '{jnt_name}'...")
				mc.parentConstraint(jnt_name, b_jnt_name, mo=True)
				mc.scaleConstraint(jnt_name, b_jnt_name, mo=True)

	# ==============================================================================
	# RIG CREATION STEP 7: Create Stick Controller & FK/IK Space Blending
	# ==============================================================================

	if len(b_joints) > 0:
		tip_joint = b_joints[-1]
		
		# Create Stick controller
		stick_ctrl_name = f'{side}_{region}Stick_ctrl'
		print(f"Creating stick controller '{stick_ctrl_name}' at the tip of bind joint chain...")
		
		if mc.objExists(stick_ctrl_name):
			mc.delete(stick_ctrl_name)
			
		stick_ctrl = core.Dag(stick_ctrl_name)
		stick_ctrl.nmCreateController(stickShape)
		stick_ctrl.editCtrlShape(axis=scale * 2.0)
		stick_ctrl.color = 'yellow'
		stick_ctrl.rotateOrder = rotate_order
		stick_ctrl.lockHideAttrLst( 'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')

		
		# Create zero group for the stick controller (already auto-named as side_regionStickZro_grp)
		stick_zro = rigTools.zroGrpWithOffset(stick_ctrl)
		
		# Align Zero group to the tip joint
		stick_zro.matchPosition(tip_joint)
		stick_zro.matchRotation(tip_joint)
		
		# Parent the Zero group to the main group for clean organization
		pm.parent(stick_zro, main_grp)
		
		# Matrix constraint: stick controller's Zero group follows the tip joint
		print(f"Applying matrixConstraint from '{tip_joint}' to follow target '{stick_zro.name}'...")
		mtc.parentConMatrixGPT(source=tip_joint, target=stick_zro.name, mo=True, translate=True, rotate=True, scale=True)
		
		# Add FK_IK attribute to stick_ctrl
		print(f"Adding attribute 'FK_IK' (niceName='FK IK') to controller '{stick_ctrl_name}'...")
		mc.addAttr(stick_ctrl.name, ln='FK_IK', nn='FK IK', at='double', min=0.0, max=1.0, dv=0.0, k=True)
		
		# Hook up attribute to blendshape targets using a reverse node
		print("Setting up reverse logic node for blendshape FK/IK blending...")
		rev_node_name = f'{side}_{region}_fkIk_rev'
		if mc.objExists(rev_node_name):
			mc.delete(rev_node_name)
			
		rev_node = mc.createNode('reverse', name=rev_node_name)
		
		# Connect stick_ctrl.FK_IK -> reverse.inputX
		mc.connectAttr(f'{stick_ctrl.name}.FK_IK', f'{rev_node}.inputX')
		
		# Connect reverse.outputX -> fkNrb target on blendshape (0.0 = FK, reverse output = 1.0)
		mc.connectAttr(f'{rev_node}.outputX', f'{bsh_node}.{fk_nurbs_name}')
		
		# Connect stick_ctrl.FK_IK -> ikNrb target on blendshape (1.0 = IK)
		mc.connectAttr(f'{stick_ctrl.name}.FK_IK', f'{bsh_node}.{ik_nurbs_name}')

		# Connect visibility of FK/IK controller groups to toggle them based on FK_IK value
		print("Connecting FK/IK controller group visibilities to the FK_IK space switch...")
		# Connect stick_ctrl.FK_IK -> ikCtrl_grp.visibility (shows IK when FK_IK = 1)
		mc.connectAttr(f'{stick_ctrl.name}.FK_IK', f'{ik_ctrl_grp_name}.visibility')
		# Connect reverse.outputX -> fkCtrl_grp.visibility (shows FK when FK_IK = 0)
		mc.connectAttr(f'{rev_node}.outputX', f'{fk_ctrl_grp_name}.visibility')

		# Add detail visibility toggle attribute
		print(f"Adding attribute 'detail' (niceName='Detail') to controller '{stick_ctrl_name}'...")
		mc.addAttr(stick_ctrl.name, ln='detail', nn='Detail', at='long', min=0, max=1, dv=0, k=True)
		# Connect stick_ctrl.detail -> loc_grp.visibility (default 0 hides locator group)
		mc.connectAttr(f'{stick_ctrl.name}.detail', f'{loc_grp_name}.visibility')

	#... Parenting




	#... parent fk control to controller
	if priorCtrl != '':
		mc.parent(fk_ctrl_grp.name(), priorCtrl)
		mc.parent(ik_ctrl_grp.name(), priorCtrl)

	if jnt_grp != '' or noTouch != '':
		mc.parent(fk_jnt_grp.name(), jnt_grp)
		mc.parent(ik_jnt_grp.name(), jnt_grp)
		mc.parent(fk_nurbs, noTouch)
		mc.parent(ik_nurbs, noTouch)


	mc.parent(main_grp.name(), noTouch)
	


	FkIkSpineReplace.info(f'return: {fk_jnt_grp}, {ik_jnt_grp}, {fk_nurbs}, {ik_nurbs}, {fk_ctrl_grp}, {ik_ctrl_grp}')
	core.makeHeader("Rig Setup completed successfullye!")

	return fk_jnt_grp, ik_jnt_grp, fk_nurbs, ik_nurbs, fk_ctrl_grp, ik_ctrl_grp


fk_jnt_grp, ik_jnt_grp, fk_nurbs, ik_nurbs, fk_ctrl_grp, ik_ctrl_grp = tentacle_fkIkReplace(   
							nurbs_surface = 'C_legPlane_nrb',         
							num_pins = 16  		,                     
							num_fk_joints = 6  	,                
							region = 'leg' 		,                 
							side = 'C'    		,                    
							ctrl_shape = 'circle_Y_along_ctrlShape' ,   
							joint_orient = 'yxz'   ,           
							secondary_orient = 'zup'    ,  
							scale = 1.0       			,                         
							prior_joint = 'hip_bJnt'   ,
							priorCtrl = 'hip_gmbCtrl' ,           
							parentMatrix = True )






fk_jnt_grp, ik_jnt_grp, fk_nurbs, ik_nurbs, fk_ctrl_grp, ik_ctrl_grp = tentacle_fkIkReplace(   
							nurbs_surface = 'L_legPlane_nrb',         
							num_pins = 16  		,                     
							num_fk_joints = 6  	,                
							region = 'leg' 		,                 
							side = 'L'    		,                    
							ctrl_shape = 'circle_Y_along_ctrlShape' ,   
							joint_orient = 'yxz'   ,           
							secondary_orient = 'zup'    ,  
							scale = 1.0       			,                         
							prior_joint = 'hip_bJnt'   ,
							priorCtrl = 'hip_gmbCtrl' ,           
							parentMatrix = True )






fk_jnt_grp, ik_jnt_grp, fk_nurbs, ik_nurbs, fk_ctrl_grp, ik_ctrl_grp = tentacle_fkIkReplace(   
							nurbs_surface = 'R_legPlane_nrb',         
							num_pins = 16  		,                     
							num_fk_joints = 6  	,                
							region = 'leg' 		,                 
							side = 'R'    		,                    
							ctrl_shape = 'circle_Y_along_ctrlShape' ,   
							joint_orient = 'yxz'   ,           
							secondary_orient = 'zup'    ,  
							scale = 1.0       			,                         
							prior_joint = 'hip_bJnt'   ,
							priorCtrl = 'hip_gmbCtrl' ,           
							parentMatrix = True )







fk_jnt_grp, ik_jnt_grp, fk_nurbs, ik_nurbs, fk_ctrl_grp, ik_ctrl_grp = tentacle_fkIkReplace(   
							nurbs_surface = 'L_armPlane_nrb',         
							num_pins = 16  		,                     
							num_fk_joints = 6  	,                
							region = 'arm' 		,                 
							side = 'L'    		,                    
							ctrl_shape = 'circle_Y_along_ctrlShape' ,   
							joint_orient = 'yxz'   ,           
							secondary_orient = 'zup'    ,  
							scale = 1.0       			,                         
							prior_joint = 'clavLFT_bJnt'   ,
							priorCtrl = 'clavLFT_gmbCtrl' ,           
							parentMatrix = True )







fk_jnt_grp, ik_jnt_grp, fk_nurbs, ik_nurbs, fk_ctrl_grp, ik_ctrl_grp = tentacle_fkIkReplace(   
							nurbs_surface = 'R_armPlane_nrb',         
							num_pins = 16  		,                     
							num_fk_joints = 6  	,                
							region = 'arm' 		,                 
							side = 'R'    		,                    
							ctrl_shape = 'circle_Y_along_ctrlShape' ,   
							joint_orient = 'yxz'   ,           
							secondary_orient = 'zup'    ,  
							scale = 1.0       			,                         
							prior_joint = 'clavLFT_bJnt'   ,
							priorCtrl = 'clavLFT_gmbCtrl' ,           
							parentMatrix = True )

