"""
Universal FK Chain Rigging Module (eh_universalFkRig.py)
--------------------------------------------------------
A unified, modular FK chain generator combining all production-proven features from:
- createFkRig.fkRig_omni_newCurl
- createFkRig.fkRig_omni_matrix
- createFkRig.fkRig_new_curl_ext
- createFkRig.fkMulChild
- eh_createFkRig.create_fk_chain

Key Capabilities:
1. Smart Input: Supports Single Chain (flat list) or Multi-Chain (nested list e.g. multiple tentacles/hair/fingers).
2. Auto-Detection: Automatically clones _tmpJnt -> _bJnt with rigTools.jointAt & freeze, or uses existing _bJnt directly.
3. Hierarchy Flexibility: Sequential FK (chainHierarchy=True) or Parallel/Broad FK (chainHierarchy=False).
4. External Space Modes:
   - Case 1 (Direct DAG): parentCtrlTo='head01_gmbCtrl', parentCtrlToPriorJnt=False
   - Case 2 (Container + Constraint): parentCtrlTo='ctrl_grp', parentCtrlToPriorJnt=True (psCon to priorJnt)
   - Direct Controller: useRigGrp=False (placing top zero group directly under parentCtrlTo)
5. Kinematics: Matrix Constraint (parentConMatrix, mo=True) or Standard Constraints (parentConstraint + scaleConstraint).
6. Local/World Switch: Dynamic Matrix Orient Local/World switch (localWorld=True).
7. Pose/Curl Control: Optional master Curl controller driving rotation offsets (curlCtrl=True) with 'Detail' toggle.
8. SSC Standard: Segment Scale Compensate cleanly disabled on bind joints for proper scaling.
9. Naming & Symmetry: Full support for Prefix style (L_...) and Suffix style (...LFT).
"""

from function.framework.reloadWrapper import reloadWrapper as reload
import maya.cmds as mc
import re

from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

from function.rigging.util import misc
reload(misc)


class RigResult(dict):
	"""
	Dictionary container allowing both dict lookup ['key'] and attribute access .key
	"""
	def __getattr__(self, name):
		if name in self:
			return self[name]
		raise AttributeError(f"'RigResult' object has no attribute '{name}'")

	def __setattr__(self, name, value):
		self[name] = value


def create_universal_fk_chain(
	jntLst=(),
	name=None,
	nameSpace='',
	parentCtrlTo=None,
	parentCtrlToPriorJnt=False,
	priorJnt=None,
	parentToPriorJnt=True,
	isTmpJnt=None,
	chainHierarchy=True,
	useRigGrp=True,
	parentMatrix=True,
	ctrlShape='circle_ctrlShape',
	charScale=1.0,
	color=None,
	side=None,
	rotateOrder='zxy',
	localWorld=False,
	curlCtrl=False,
	curlPosiAtFirst=True,
	curlCtrlShape='stick_ctrlShape',
	constraintCurl=False,
	segmentScaleCompensate=False,
	suffix='_bJnt'
):
	"""
	Creates a unified procedural FK chain (Single Chain or Multi-Chain).

	CRITICAL PIPELINE EXECUTION ORDER (Matrix Constraint Standard):
	---------------------------------------------------------------
	Why joint driving is strictly separated and executed LAST:
	1. `mtc.parentConMatrix()` dynamically queries the target joint's live DAG parent
	   via `mc.pickWalk(target, d='up')[0]` to connect `parent.worldInverseMatrix[0]`
	   into `multMatrix.matrixIn[3]`.
	2. If `parentConMatrix()` is called BEFORE the joint chain is parented to `priorJnt`
	   or before the controller group is parented to `parentCtrlTo`:
	   - The measured rest offset matrix will be evaluated against World or temporary space.
	   - When the joint is subsequently parented to `priorJnt`, its DAG parent space changes.
	   - Maya's matrix calculation multiplies against the wrong inverse parent matrix,
	     causing the entire joint chain to instantly POP, TWIST, or FLOAT AWAY!
	3. Strict Execution Sequence Followed By This Engine:
	   - Step 1: Input Normalization (Single flat chain or Multi-chain nested list).
	   - Step 2: Naming, side detection, and color assignment.
	   - Step 3: Master Rig Group creation and snapping.
	   - Step 4: Joint preparation (jointAt, freeze into jointOrient, preferred angles, SSC).
	   - Step 5: SKELETON DAG ATTACHMENT: `bJnts[0].parent(priorJnt)` (Finalize skeleton DAG FIRST).
	   - Step 6: CONTROLLER DAG ATTACHMENT: `rigGrp.parent(parentCtrlTo)` (Finalize controller DAG FIRST).
	   - Step 7: Extras (Curl controller with PMA/MDV, Matrix Local/World switch).
	   - Step 8 (FINAL): DRIVE BIND JOINTS via `mtc.parentConMatrix` only when both hierarchies
	                     are 100% frozen in their true neutral Rest Pose.

	Args:
		jntLst (list|tuple): List of joints (e.g. ['A01_bJnt', 'A02_bJnt']) for single chain,
		                     OR nested list (e.g. [['A01_bJnt', 'A02_bJnt'], ['B01_bJnt', 'B02_bJnt']]) for multi-chain.
		name (str): Optional base name. If omitted, inferred from the first joint name.
		nameSpace (str): Optional namespace prefix.
		parentCtrlTo (str): Controller or group to parent under (e.g. 'head01_gmbCtrl' or 'ctrl_grp').
		parentCtrlToPriorJnt (bool): If True, parents rigGrp to parentCtrlTo and applies parentConstraint to priorJnt (Case 2).
		                             If False, performs pure DAG parenting to parentCtrlTo (Case 1).
		priorJnt (str): Main joint of the previous part (e.g. 'head01_bJnt').
		parentToPriorJnt (bool): If True, parents the root bind joint under priorJnt.
		isTmpJnt (bool|None): If True, clones guide joints to bind joints. If None, auto-detects based on '_tmpJnt' in name.
		chainHierarchy (bool): If True, controllers form a sequential parent chain (01 -> 02 -> 03).
		                       If False, all controllers are placed in parallel under rigGrp (flat FK).
		useRigGrp (bool): If True, encapsulates chain in {part}Rig_grp. If False, parents top zero group directly to parentCtrlTo.
		parentMatrix (bool): If True, drives joints via matrixConstraint.parentConMatrix. If False, uses standard parent/scale constraints.
		ctrlShape (str): Controller curve shape name.
		charScale (float): Overall controller scale multiplier.
		color (str): Controller color. If None, auto-detects side color (Blue for LFT, Red for RGT, Yellow for CEN).
		side (str): Explicit side ('LFT', 'RGT', 'L', 'R', 'C'). If None, auto-detected from joint naming.
		rotateOrder (str): Rotate order for controllers and gimbals (default: 'zxy').
		localWorld (bool): If True, builds a matrix-based Orient Local/World switch on the root controller.
		curlCtrl (bool): If True, builds an overall Curl controller with 'Detail' attribute driving offset rotations.
		curlPosiAtFirst (bool): If True, snaps Curl controller to the root joint; if False, to the tip joint.
		curlCtrlShape (str): Curve shape for the Curl controller.
		constraintCurl (bool): If True, parent-constrains Curl zero group to the snap joint.
		segmentScaleCompensate (bool): If False (default), disables SSC on all bind joints for proper scale propagation.
		suffix (str): Suffix used when generating new bind joints from template joints (default: '_bJnt').

	Returns:
		RigResult: Dictionary-like object containing:
			- ctrls: List of core.Dag controllers
			- gmbls: List of gimbal controllers
			- zroGrps: List of zero groups
			- offsetGrps: List of offset groups
			- bJnts: List of bind joints
			- rigGrp: Rig group object (or None)
			- topCtrl_grp: Name of the top group
			- topZroGrp: First zero group object
			- curlCtrl: Curl controller (if curlCtrl=True)
			- metaNode: Meta node (if curlCtrl=True)
			- localWorld: Local/World node dict (if localWorld=True)
			- chains: List of individual chain data dicts (if multi-chain)
	"""
	core.makeHeader('Start of Universal FK Chain')

	# --------------------------------------------------------------------------
	# 1. Input Normalization & Fail-Fast Validation
	# --------------------------------------------------------------------------
	if not jntLst:
		mc.error("[UniversalFK] Fatal Error: 'jntLst' cannot be empty. Please provide joint names.")

	raw_input = list(jntLst) if isinstance(jntLst, tuple) else jntLst

	# Detect if first element is a list or tuple -> Multi-Chain mode
	if isinstance(raw_input[0], (list, tuple)):
		chains = [list(c) for c in raw_input]
		is_multi_chain = True
	else:
		chains = [raw_input]
		is_multi_chain = False

	# 1.1 Strict Validation: Check all joints in jntLst exist in Maya scene
	missing_jnts = []
	for c in chains:
		for j in c:
			j_str = str(j.name if hasattr(j, 'name') else j)
			if not mc.objExists(j_str):
				missing_jnts.append(j_str)
	if missing_jnts:
		mc.error(
			f"[UniversalFK] Fatal Error: The following joints in 'jntLst' do not exist in the scene:\n"
			f"{', '.join(missing_jnts)}\n"
			f"Action Required: Please ensure all guide or bind joints exist before building."
		)

	# 1.2 Strict Validation: Check parentCtrlTo exists if specified
	if parentCtrlTo and not mc.objExists(str(parentCtrlTo)):
		mc.error(
			f"[UniversalFK] Fatal Error: Specified 'parentCtrlTo' does not exist in the scene: '{parentCtrlTo}'.\n"
			f"Action Required: Please verify the controller/group name or build the parent hierarchy first."
		)

	# 1.3 Strict Validation: Check priorJnt exists if specified
	if priorJnt and not mc.objExists(str(priorJnt)):
		mc.error(
			f"[UniversalFK] Fatal Error: Specified 'priorJnt' does not exist in the scene: '{priorJnt}'.\n"
			f"Action Required: Please verify the skeleton hierarchy or joint name before attaching."
		)

	# --------------------------------------------------------------------------
	# 2. Naming & Side Analysis
	# --------------------------------------------------------------------------
	first_jnt_str = str(chains[0][0].name if hasattr(chains[0][0], 'name') else chains[0][0])
	name_info = core.check_name_style(name=first_jnt_str)
	# name_info: [base_name, side, pos, is_default_style, name_no_side]
	detected_side = name_info[1] if (len(name_info) > 1 and name_info[1]) else ''
	is_default_style = name_info[3]  # True if suffix style (ear01LFT)
	name_no_side = name_info[4]      # Base token without side (ear01)

	final_side = side if side is not None else detected_side

	# Determine Part Base Name
	if name:
		base_part = name
	else:
		# Strip trailing digits from name_no_side (e.g. 'tenFaceA01' -> 'tenFaceA' or 'tenFace')
		base_part = re.sub(r'\d+$', '', name_no_side) if name_no_side else 'fkPart'

	# Determine if using Prefix Style (L_, R_, C_) vs Suffix Style (LFT, RGT)
	use_prefix_style = (final_side in ('L', 'R', 'C', 'M')) or (not is_default_style)

	# Determine Master Rig Group Name
	if use_prefix_style:
		prefix = f"{final_side}_" if final_side else ""
		rig_grp_name = f"{prefix}{nameSpace}{base_part}Rig_grp"
	else:
		rig_grp_name = f"{nameSpace}{base_part}Rig{final_side}_grp"

	# Auto-detect side color if not specified
	if color is None:
		clean_side = str(final_side).upper()
		if clean_side in ('LFT', 'L'):
			chain_color = 'blue'
		elif clean_side in ('RGT', 'R'):
			chain_color = 'red'
		elif clean_side in ('CEN', 'C', 'M'):
			chain_color = 'yellow'
		else:
			chain_color = 'red'
	else:
		chain_color = color

	# --------------------------------------------------------------------------
	# 3. Master Rig Group Creation & External Parenting
	# --------------------------------------------------------------------------
	rigGrp = None
	if useRigGrp:
		rigGrp = core.Null(rig_grp_name)
		first_snap_target = chains[0][0]
		if mc.objExists(str(first_snap_target)):
			rigGrp.maSnap(first_snap_target)

		# External Parenting
		if parentCtrlTo:
			rigGrp.parent(parentCtrlTo)

		# Case 2: Parent group placed at parentCtrlTo, and parentConstrained to priorJnt
		if parentCtrlToPriorJnt and priorJnt:
			core.parentConstraint(priorJnt, rigGrp.name, mo=True)

	# --------------------------------------------------------------------------
	# 4. Chain Processing Loop
	# --------------------------------------------------------------------------
	all_ctrls = []
	all_gmbls = []
	all_zroGrps = []
	all_offsetGrps = []
	all_bJnts = []
	chain_data_list = []

	for chain_idx, chain_jnts in enumerate(chains):
		c_ctrls = []
		c_gmbls = []
		c_zroGrps = []
		c_offsetGrps = []
		c_bJnts = []

		chain_root_parent = rigGrp if useRigGrp else parentCtrlTo

		# Process each joint in this chain
		for num, jnt_raw in enumerate(chain_jnts):
			jnt_str = str(jnt_raw.name if hasattr(jnt_raw, 'name') else jnt_raw)
			if not mc.objExists(jnt_str):
				mc.error(f"[UniversalFK] Joint does not exist in Maya scene: '{jnt_str}'")

			jnt_info = core.check_name_style(name=jnt_str)
			jnt_base = jnt_info[0]

			# Determine if this joint is a template joint
			is_tmp = isTmpJnt
			if is_tmp is None:
				is_tmp = jnt_str.endswith('_tmpJnt') or '_tmp' in jnt_str

			# Bind Joint Preparation
			if is_tmp:
				# Clone guide joint using rigTools.jointAt
				tmp_dag = core.Dag(jnt_str)
				b_jnt = rigTools.jointAt(tmp_dag.name)
				b_jnt.name = f"{jnt_base}{suffix}"

				# Freeze rotation into jointOrient
				b_jnt.freeze(r=True)

				# Set preferred angles
				try:
					mc.joint(b_jnt.name, edit=True, setPreferredAngles=True)
				except:
					pass

				# Disable Segment Scale Compensate
				if not segmentScaleCompensate:
					if mc.attributeQuery('segmentScaleCompensate', node=b_jnt.name, exists=True):
						b_jnt.attr('segmentScaleCompensate').value = 0

				# Sequential parenting of generated bind joints
				if num > 0:
					b_jnt.parent(c_bJnts[num - 1])
			else:
				b_jnt = core.Dag(jnt_str)
				if not segmentScaleCompensate:
					if mc.attributeQuery('segmentScaleCompensate', node=b_jnt.name, exists=True):
						b_jnt.attr('segmentScaleCompensate').value = 0

			c_bJnts.append(b_jnt)
			all_bJnts.append(b_jnt)

			# Controller Creation
			ctrl = core.Dag(f"{jnt_base}_ctrl")
			ctrl.nmCreateController(ctrlShape)
			ctrl.editCtrlShape(axis=charScale * 6.4)
			ctrl.color = chain_color
			ctrl.rotateOrder = rotateOrder

			gimbal = core.createGimbal(ctrl)
			gimbal.rotateOrder = rotateOrder

			zroGrp, offsetGrp = rigTools.zroNewGrpWithOffset(ctrl)
			zroGrp.snap(b_jnt)
			zroGrp.name = f"{jnt_base}Zro_grp"
			offsetGrp.name = f"{jnt_base}Offset_grp"

			c_ctrls.append(ctrl)
			c_gmbls.append(gimbal)
			c_zroGrps.append(zroGrp)
			c_offsetGrps.append(offsetGrp)

			all_ctrls.append(ctrl)
			all_gmbls.append(gimbal)
			all_zroGrps.append(zroGrp)
			all_offsetGrps.append(offsetGrp)

			# Hierarchy Parenting
			if num > 0:
				if chainHierarchy:
					# Sequential FK: Parent to previous gimbal
					zroGrp.parent(c_gmbls[num - 1])
				else:
					# Parallel/Flat FK: Parent directly under chain root
					if chain_root_parent and mc.objExists(str(chain_root_parent)):
						zroGrp.parent(chain_root_parent)
			else:
				# Root of this chain
				if chain_root_parent and mc.objExists(str(chain_root_parent)):
					zroGrp.parent(chain_root_parent)

		# Prior Joint Skeleton Parenting (attach root joint to skeleton hierarchy FIRST)
		if priorJnt and parentToPriorJnt:
			c_bJnts[0].parent(priorJnt)

		chain_data_list.append({
			'ctrls': c_ctrls,
			'gmbls': c_gmbls,
			'zroGrps': c_zroGrps,
			'offsetGrps': c_offsetGrps,
			'bJnts': c_bJnts,
			'topZroGrp': c_zroGrps[0] if c_zroGrps else None
		})

	# --------------------------------------------------------------------------
	# 5. Optional Curl Controller
	# --------------------------------------------------------------------------
	curl_ctrl_obj = None
	meta_node_obj = None

	if curlCtrl:
		if use_prefix_style:
			prefix = f"{final_side}_" if final_side else ""
			curl_base_name = f"{prefix}{nameSpace}{base_part}Curl"
		else:
			curl_base_name = f"{nameSpace}{base_part}Curl{final_side}"

		curl_ctrl = core.Dag(f"{curl_base_name}_ctrl")
		curl_ctrl.nmCreateController(curlCtrlShape)
		curl_ctrl.editCtrlShape(axis=charScale * 7.4)
		curl_ctrl.color = chain_color
		curl_ctrl.rotateOrder = rotateOrder

		zroGrpCurl, offsetCurl = rigTools.zroNewGrpWithOffset(curl_ctrl)
		target_snap = all_bJnts[0] if curlPosiAtFirst else all_bJnts[-1]
		zroGrpCurl.maSnap(target_snap)

		curl_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

		# Detail attribute to toggle FK chain visibility
		curlShape = core.Dag(curl_ctrl.shape)
		curlShape.addAttribute(at='long', min=0, max=1, longName='Detail', keyable=True, defaultValue=0)

		# Connect Detail -> root zero group visibility of each chain
		for c_data in chain_data_list:
			if c_data['zroGrps']:
				try:
					mc.connectAttr(f"{curlShape.name}.Detail", f"{c_data['zroGrps'][0].name}.visibility", f=True)
				except:
					pass

		# Rotation distribution network (PMA -> MDV -> Offset.rotate)
		pma_node = core.PlusMinusAverage(f"{curl_base_name}_pma")
		mdv_node = core.MultiplyDivine(f"{curl_base_name}_mdv")

		curl_ctrl.attr('rotate') >> pma_node.attr('input3D[0]')
		pma_node.attr('output3D') >> mdv_node.attr('input1')

		for off_grp in all_offsetGrps:
			mdv_node.attr('output') >> off_grp.attr('rotate')

		# Parent Curl Zero Group
		if rigGrp:
			zroGrpCurl.parent(rigGrp)
		elif parentCtrlTo and mc.objExists(parentCtrlTo):
			zroGrpCurl.parent(parentCtrlTo)

		if constraintCurl:
			curl_ps = core.parentConstraint(target_snap, zroGrpCurl, mo=False)
			curl_ps.name = f"{curl_base_name}_psCon"

		curl_ctrl_obj = curl_ctrl

		# Meta Node
		meta_name = f"{curl_base_name}_meta"
		meta_node = core.MetaGeneric(meta_name)
		meta_node.addAttribute(attributeType='message', longName='baseName')
		curl_ctrl.attr('message') >> meta_node.attr('Rig_Prior')
		pma_node.attr('message') >> meta_node.attr('passValue')
		meta_node.setAttribute('Color', chain_color, type='string')
		meta_node.setAttribute('Side', str(final_side), type='string')
		meta_node.setAttribute('Base_Name', rigGrp.name if rigGrp else curl_base_name, type='string')
		meta_node_obj = meta_node

	# --------------------------------------------------------------------------
	# 6. Optional Local / World Matrix Switch
	# --------------------------------------------------------------------------
	lw_nodes = None
	if localWorld and all_zroGrps:
		target_lw_ctrl = curl_ctrl_obj if curlCtrl else all_ctrls[0]
		local_space_obj = priorJnt if (parentCtrlTo in ('ctrl_grp', 'noTouch_grp', None, '') and priorJnt and mc.objExists(priorJnt)) else parentCtrlTo

		if local_space_obj and mc.objExists(local_space_obj):
			world_space_obj = 'ctrl_grp' if mc.objExists('ctrl_grp') else 'noTouch_grp'

			# Collect target zero groups that must follow Local/World
			target_lw_groups = []

			# 1. FK Chain Root(s): In sequential FK, driving the root zero group carries the chain.
			# In flat parallel FK (chainHierarchy=False), all zero groups are direct siblings under root.
			for c_data in chain_data_list:
				if chainHierarchy:
					if c_data.get('topZroGrp'):
						target_lw_groups.append(c_data['topZroGrp'])
					elif c_data.get('zroGrps'):
						target_lw_groups.append(c_data['zroGrps'][0])
				else:
					for z_grp in c_data.get('zroGrps', []):
						target_lw_groups.append(z_grp)

			if not target_lw_groups and all_zroGrps:
				target_lw_groups.append(all_zroGrps[0])

			# 2. Curl Controller: If curl controller exists and is not already constrained to a joint,
			# also drive it so stick_ctrl stays in sync with World orient.
			if curlCtrl and zroGrpCurl and not constraintCurl:
				if zroGrpCurl not in target_lw_groups:
					target_lw_groups.append(zroGrpCurl)

			lw_results = []
			for t_grp in target_lw_groups:
				t_name = t_grp.name if hasattr(t_grp, 'name') else str(t_grp)
				t_base = core.check_name_style(name=t_name)[0]
				res = mtc.eh_orientLocalWorldMatrix(
					ctrl=target_lw_ctrl.name,
					localObj=local_space_obj,
					worldObj=world_space_obj,
					target=t_name,
					attrName='localWorld',
					parentMode='orient',
					bodyPart=t_base
				)
				lw_results.append(res)

			lw_nodes = lw_results[0] if len(lw_results) == 1 else lw_results

	# --------------------------------------------------------------------------
	# 7. Drive Bind Joints (Matrix or Standard Constraint)
	# --------------------------------------------------------------------------
	# [CRITICAL STEP ORDER - THE MATRIX CONSTRAINT GOLDEN RULE]:
	# This loop MUST execute strictly AFTER all DAG parenting has concluded:
	#   1. Skeletons: bJnts[0] is already parented under priorJnt (e.g. head01_bJnt).
	#   2. Controllers: rigGrp is already parented under parentCtrlTo (e.g. head01_gmbCtrl).
	#
	# Rationale:
	# `mtc.parentConMatrix` uses `_getLocalOffset(driver, driven)` and wires
	# `driven.parent.worldInverseMatrix[0]` into `multMatrix.matrixIn[3]`.
	# If called before parenting is finalized, the offset is computed against World,
	# and subsequent reparenting will corrupt the inverse matrix, causing the entire
	# limb / tentacle chain to POP and FLOAT AWAY in 3D space!
	# --------------------------------------------------------------------------
	for i in range(len(all_bJnts)):
		driver = all_gmbls[i]
		driven = all_bJnts[i]
		jnt_base = core.check_name_style(name=driven.name)[0]

		if parentMatrix:
			mtc.parentConMatrix(
				driver.name,
				driven.name,
				mo=True,
				translate=True,
				rotate=True,
				scale=True
			)
		else:
			ps_con = core.parentConstraint(driver, driven)
			ps_con.name = f"{jnt_base}_psCons"
			sc_con = core.scaleConstraint(driver, driven)
			sc_con.name = f"{jnt_base}_scalCons"

	# --------------------------------------------------------------------------
	# 8. Package and Return Results
	# --------------------------------------------------------------------------
	top_zro = all_zroGrps[0] if all_zroGrps else None
	top_grp_name = rigGrp.name if rigGrp else (top_zro.name if top_zro else '')

	result = RigResult({
		'ctrls': all_ctrls,
		'gmbls': all_gmbls,
		'zroGrps': all_zroGrps,
		'offsetGrps': all_offsetGrps,
		'bJnts': all_bJnts,
		'rigGrp': rigGrp,
		'topCtrl_grp': top_grp_name,
		'topZroGrp': top_zro,
		'topZro_grp': top_zro.name if top_zro else '',
		'curlCtrl': curl_ctrl_obj,
		'metaNode': meta_node_obj,
		'localWorld': lw_nodes,
		'chains': chain_data_list if is_multi_chain else []
	})

	print(f"\n# Universal FK Rig Build Complete: {base_part} ({len(all_ctrls)} controllers across {len(chains)} chain(s))")

	core.makeHeader('End of Universal FK Chain')
	return result


# Shorthand alias for seamless drop-in compatibility
create_fk_chain = create_universal_fk_chain
