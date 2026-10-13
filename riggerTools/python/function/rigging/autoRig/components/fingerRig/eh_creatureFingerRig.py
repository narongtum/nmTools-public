# ===============================================================================
# Creature Finger Rig Component (FK / Single Chain IK Hybrid + Floor Clench)
# ===============================================================================
"""
Overview:
    Procedural Hybrid FK / IK Finger Rig designed for creature / quadruped paws and hands.
    Supports 5-digit paws/hands (thumb, index, middle, ring, pinky) with 3-tier joint
    hierarchies (FK, IK, Bind) parented under the ball pivot joint (e.g. ballLFT_bJnt).

Key Features:
    1. Ball Pivot Parenting: Base finger joints are parented under ball_bJnt, allowing
       the heel/palm to lift during Ball Roll while fingers remain planted on the ground.
    2. Single Chain IK (ikSCsolver): Lightweight IK handles from joint 01 to joint 04 tip,
       providing clean tip planting controllers ({finger}Ik_ctrl) without pole vector clutter.
    3. Master & Individual FK/IK Switch: Master 'allFkIk' and individual '{finger}FkIk'
       attributes on the Stick controller driving smooth parentConstraint blend weights
       and automated controller visibility toggles.
    4. Full Finger Curl & Floor Clench ('clench'): Math network driving offset groups
       for fist, roll, relax, spread, cup, and iconic beast floor clenching (joint 01
       knuckle arch up, joints 02/03 claw tip dig down).

Author:
    Antigravity / nmTools Pipeline
"""

import maya.cmds as mc
import logging

from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.base import core
reload(core)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

from function.rigging.util import misc
reload(misc)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

from function.rigging.constraint import matrixConstraint as mtc
reload(mtc)

logger = logging.getLogger('debug_text')
logger.setLevel(logging.DEBUG)


from function.rigging.feature import matrixMeshCollision as mmCol
reload(mmCol)


def creatureFingerRig(
	nameSpace='',
	baseName='',
	side='LFT',
	fingerNum=3,
	fingerName=('thumb', 'index', 'middle', 'ring', 'pinky'),
	zroName='Zro_grp',
	offsetName='Offset_grp',
	charScale=1.0,
	priorJnt='ballLFT_bJnt',
	thumbPriorJnt='',
	parentTo='ctrl_grp',
	jntGrp='jnt_grp',
	ankleJnt='',
	stickNam='',
	hasIk=True,
	hasGroundCollision=False,
	collisionMesh='',
	collisionYOnly=True,
	ctrlShape='circle_ctrlShape',
	ikCtrlShape='stick_ctrlShape',
	povShape='plainSphereB_ctrlShape',
	povScale=0.1
):
	"""
	Construct procedural FK / IK Hybrid Finger Rig for creature paws/hands.

	Args:
		nameSpace (str): Global namespace prefix.
		baseName (str): Base limb/foot identifier (e.g. 'frontLeg', 'backLeg01', 'backLeg02').
		side (str): Side identifier ('LFT' or 'RGT').
		fingerNum (int): Number of FK controllers per finger (default: 3).
		fingerName (tuple[str]): Tuple of finger base names.
		zroName (str): Zero group suffix (default: 'Zro_grp').
		offsetName (str): Offset group suffix (default: 'Offset_grp').
		charScale (float): Overall character scale factor.
		priorJnt (str | core.Dag): Parent joint under which base fingers are attached (e.g. 'ballLFT_bJnt').
		thumbPriorJnt (str | core.Dag): Dedicated parent joint for thumb/dewclaw (e.g. 'ankleLFT_bJnt'). Defaults to priorJnt if empty.
		parentTo (str | core.Dag): Parent controller group (e.g. 'ctrl_grp').
		jntGrp (str): Master joint group to hold FK/IK chains (default: 'jnt_grp').
		ankleJnt (str): Ankle joint name for space switching. If empty, auto-detects 'ankle{side}_bJnt'.
		stickNam (str): Name of the stick controller. If empty, auto-names to 'legStick{side}_ctrl'.
		hasIk (bool): Whether to generate Single Chain / Rotate Plane IK handles and controllers.
		hasGroundCollision (bool): Whether to build real-time Matrix Mesh Collision for finger IK tips.
		collisionMesh (str): Target polygon collision mesh in scene (terminates if not found).
		collisionYOnly (bool): When True, only clamps vertical height (Y) to floor while letting X and Z move freely (default: True).
		ctrlShape (str): Controller curve shape for FK controllers.
		ikCtrlShape (str): Controller curve shape for IK controllers.
		povShape (str): Controller curve shape for Pole Vector IK controllers.
		povScale (float): Scale multiplier for POV controllers (default: 0.1).

	Returns:
		dict[str, Any]: Dictionary of created groups, controllers, joints, and handles.
	"""
	core.makeHeader(f"Start of Creature Finger {side} Rig")
	logger.info(f"#### Executing Creature Finger Rig for side: {side} ####")

	prior_jnt_name = priorJnt.name if hasattr(priorJnt, 'name') else str(priorJnt)
	parent_to_name = parentTo.name if hasattr(parentTo, 'name') else str(parentTo)

	side_color = mnd.COLOR_part_dict.get('left' if 'LFT' in side else 'right', 'yellow')

	# Fail-fast validation: priorJnt and parentTo MUST exist
	if not mc.objExists(prior_jnt_name):
		mc.error(f"[eh_creatureFingerRig] Prior joint '{prior_jnt_name}' does not exist in scene! Please build the parent leg/limb rig before running finger rig.")
		return

	if not mc.objExists(parent_to_name):
		mc.error(f"[eh_creatureFingerRig] Parent target '{parent_to_name}' does not exist in scene!")
		return

	# Resolve baseName if not explicitly provided
	if not baseName:
		raw_prior = misc.splitName(prior_jnt_name)[0].replace('ball', '').replace('bJnt', '').replace('tmpJnt', '').replace(side, '').replace('_', '')
		baseName = raw_prior if raw_prior else 'frontLeg'

	# Extract position token (e.g. 'Back01', 'Back02', 'BackA', 'BackB') from baseName
	position = ''
	if baseName and baseName not in ('frontLeg', 'front', 'leg'):
		clean_pos = baseName.replace('Leg', '').replace('leg', '')
		position = clean_pos[0].upper() + clean_pos[1:] if clean_pos else ''
	elif prior_jnt_name:
		clean_pos = misc.splitName(prior_jnt_name)[0].replace('ball', '').replace('bJnt', '').replace('tmpJnt', '').replace(side, '').replace('_', '')
		if clean_pos and clean_pos.lower() not in ('front', 'leg'):
			position = clean_pos[0].upper() + clean_pos[1:]

	# Resolve thumb prior joint
	if thumbPriorJnt:
		thumb_prior_jnt_name = thumbPriorJnt.name if hasattr(thumbPriorJnt, 'name') else str(thumbPriorJnt)
		if not mc.objExists(thumb_prior_jnt_name):
			mc.error(f"[eh_creatureFingerRig] Specified thumbPriorJnt '{thumb_prior_jnt_name}' does not exist in scene!")
			return
	else:
		thumb_prior_jnt_name = prior_jnt_name

	# Resolve ankle joint for space switching
	if not ankleJnt:
		ankle_candidate = f"{nameSpace}ankle{position}{side}_bJnt" if mc.objExists(f"{nameSpace}ankle{position}{side}_bJnt") else f"{nameSpace}ankle{side}_bJnt"
		ankle_jnt_name = ankle_candidate if mc.objExists(ankle_candidate) else prior_jnt_name
	else:
		ankle_jnt_name = ankleJnt.name if hasattr(ankleJnt, 'name') else str(ankleJnt)

	# 1. Master Finger Groups for Main Digits (Index, Middle, Ring, Pinky)
	f_grp_name = f"{nameSpace}{baseName}Finger{side}_grp"
	fk_ctrl_grp_name = f"{nameSpace}{baseName}FingerFkCtls{side}_grp"
	ik_ctrl_grp_name = f"{nameSpace}{baseName}FingerIkCtls{side}_grp"
	jnt_grp_name = f"{nameSpace}{baseName}FingerJnts{side}_grp"

	f_grp = core.Null(f_grp_name)
	fk_ctrl_grp = core.Null(fk_ctrl_grp_name)
	ik_ctrl_grp = core.Null(ik_ctrl_grp_name)
	jnt_grp = core.Null(jnt_grp_name)

	# Snap group origins directly to prior_jnt so scale center is exactly on the foot/wrist joint
	if mc.objExists(prior_jnt_name):
		f_grp.maSnap(prior_jnt_name)
		jnt_grp.maSnap(prior_jnt_name)

	fk_ctrl_grp.parent(f_grp)
	ik_ctrl_grp.parent(f_grp)

	if mc.objExists(jntGrp):
		jnt_grp.parent(jntGrp)
	else:
		jnt_grp.parent(f_grp)

	mc.parentConstraint(prior_jnt_name, f_grp.name, mo=True, name=f"{f_grp_name}_parCons")
	mc.parentConstraint(prior_jnt_name, jnt_grp.name, mo=True, name=f"{jnt_grp_name}_parCons")

	# Hide FK/IK joint group by default (following eh_fkIkTwistGenRig standard)
	jnt_grp.attr('visibility').value = 0

	# 1.1 Master Finger Groups for Isolated Thumb / Dewclaw (if attached to ankle/wrist)
	has_isolated_thumb = (thumb_prior_jnt_name != prior_jnt_name)
	if has_isolated_thumb:
		thumb_f_grp_name = f"{nameSpace}{baseName}ThumbFinger{side}_grp"
		thumb_fk_ctrl_grp_name = f"{nameSpace}{baseName}ThumbFingerFkCtls{side}_grp"
		thumb_ik_ctrl_grp_name = f"{nameSpace}{baseName}ThumbFingerIkCtls{side}_grp"
		thumb_jnt_grp_name = f"{nameSpace}{baseName}ThumbFingerJnts{side}_grp"

		thumb_f_grp = core.Null(thumb_f_grp_name)
		thumb_fk_ctrl_grp = core.Null(thumb_fk_ctrl_grp_name)
		thumb_ik_ctrl_grp = core.Null(thumb_ik_ctrl_grp_name)
		thumb_jnt_grp = core.Null(thumb_jnt_grp_name)

		# Snap thumb group origins directly to thumb_prior_jnt_name (ankle/wrist joint)
		if mc.objExists(thumb_prior_jnt_name):
			thumb_f_grp.maSnap(thumb_prior_jnt_name)
			thumb_jnt_grp.maSnap(thumb_prior_jnt_name)

		thumb_fk_ctrl_grp.parent(thumb_f_grp)
		thumb_ik_ctrl_grp.parent(thumb_f_grp)

		if mc.objExists(jntGrp):
			thumb_jnt_grp.parent(jntGrp)
		else:
			thumb_jnt_grp.parent(thumb_f_grp)

		mc.parentConstraint(thumb_prior_jnt_name, thumb_f_grp.name, mo=True, name=f"{thumb_f_grp_name}_parCons")
		mc.parentConstraint(thumb_prior_jnt_name, thumb_jnt_grp.name, mo=True, name=f"{thumb_jnt_grp_name}_parCons")
		thumb_jnt_grp.attr('visibility').value = 0
	else:
		thumb_f_grp = f_grp
		thumb_fk_ctrl_grp = fk_ctrl_grp
		thumb_ik_ctrl_grp = ik_ctrl_grp
		thumb_jnt_grp = jnt_grp

	# 2. Stick Controller Resolution (Default to legStick{side}_ctrl)
	if not stickNam:
		candidate_leg_stick = f"{nameSpace}legStick{side}_ctrl"
		candidate_front_stick = f"{nameSpace}frontFootStick{side}_ctrl"
		if mc.objExists(candidate_leg_stick):
			stickNam = candidate_leg_stick
		elif mc.objExists(candidate_front_stick):
			stickNam = candidate_front_stick
		else:
			stickNam = candidate_leg_stick

	if not mc.objExists(stickNam):
		logger.info(f"# Creating stick controller '{stickNam}'")
		stick_ctrl = core.Dag(stickNam)
		stick_ctrl.nmCreateController('stick_ctrlShape')
		stick_ctrl.editCtrlShape(axis=charScale * 1.5)
		stick_ctrl.setColor(side_color)
		stick_zro = rigTools.zeroGroupNam(stick_ctrl)
		stick_zro.maSnap(prior_jnt_name)
		mc.move(0, 0, 15 * charScale, stick_zro.name, r=True, os=True, wd=True)
		stick_zro.parent(parent_to_name)
	else:
		stick_ctrl = core.Dag(stickNam)

	# 3. Add FK/IK Attributes to Stick Controller
	if not mc.attributeQuery('fingerSettings', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(longName='fingerSettings', niceName='_', at='enum', en='Fingers', keyable=True)

	if hasIk:
		if not mc.attributeQuery('allFkIk', node=stick_ctrl.name, exists=True):
			stick_ctrl.addAttribute(attributeType='float', ln='allFkIk', niceName='All FK IK', minValue=0.0, maxValue=1.0, k=True, dv=0.0)
		if not mc.attributeQuery('allFingerSpace', node=stick_ctrl.name, exists=True):
			stick_ctrl.addAttribute(longName='allFingerSpace', niceName='All Finger Space', at='enum', en='World:Ankle', keyable=True)
		if hasGroundCollision and collisionMesh and mc.objExists(collisionMesh):
			if not mc.attributeQuery('groundCollision', node=stick_ctrl.name, exists=True):
				stick_ctrl.addAttribute(attributeType='float', ln='groundCollision', niceName='Ground Collision', minValue=0.0, maxValue=1.0, k=True, dv=0.0)

	all_b_jnts = []
	all_fk_jnts = []
	all_ik_jnts = []
	all_fk_ctrls = []
	all_ik_ctrls = []
	all_pov_ctrls = []
	all_ik_handles = []

	# 4. Construct 3-Tier Chains for each Finger
	for finger in fingerName:
		logger.info(f"# Building finger chain: {finger}{side}")

		# Select appropriate target parent groups for this finger
		is_this_isolated_thumb = (finger == 'thumb' and has_isolated_thumb)
		curr_prior_jnt = thumb_prior_jnt_name if is_this_isolated_thumb else prior_jnt_name
		curr_fk_ctrl_grp = thumb_fk_ctrl_grp if is_this_isolated_thumb else fk_ctrl_grp
		curr_ik_ctrl_grp = thumb_ik_ctrl_grp if is_this_isolated_thumb else ik_ctrl_grp
		curr_jnt_grp = thumb_jnt_grp if is_this_isolated_thumb else jnt_grp

		# Add individual finger FkIk attribute
		if hasIk:
			attr_fk_ik = f"{finger}FkIk"
			if not mc.attributeQuery(attr_fk_ik, node=stick_ctrl.name, exists=True):
				stick_ctrl.addAttribute(attributeType='float', ln=attr_fk_ik, niceName=f"{finger.capitalize()} FK IK", minValue=0.0, maxValue=1.0, k=True, dv=0.0)

			# Combine Master allFkIk + Individual fingerFkIk via plusMinusAverage clamped to [0, 1]
			pma_fkik = mc.createNode('plusMinusAverage', name=f"{nameSpace}{baseName}{finger}FkIkSum{side}_pma")
			mc.connectAttr(f"{stick_ctrl.name}.allFkIk", f"{pma_fkik}.input1D[0]", force=True)
			mc.connectAttr(f"{stick_ctrl.name}.{attr_fk_ik}", f"{pma_fkik}.input1D[1]", force=True)

			clamp_fkik = mc.createNode('clamp', name=f"{nameSpace}{baseName}{finger}FkIkClamp{side}_clp")
			mc.setAttr(f"{clamp_fkik}.minR", 0.0)
			mc.setAttr(f"{clamp_fkik}.maxR", 1.0)
			mc.connectAttr(f"{pma_fkik}.output1D", f"{clamp_fkik}.inputR", force=True)

			fk_ik_plug = f"{clamp_fkik}.outputR"
		else:
			fk_ik_plug = None

		# Query total joints for this finger from tmpJnt (strictly fingerNum joints: 01..03)
		finger_tmp_jnts = []
		for n in range(1, fingerNum + 1):
			if position:
				candidate_tmps = [
					f"{nameSpace}{finger}{n:02d}{position}{side}_tmpJnt",
					f"{nameSpace}{finger}{n:02d}{baseName}{side}_tmpJnt"
				]
			else:
				candidate_tmps = [
					f"{nameSpace}{finger}{n:02d}{side}_tmpJnt"
				]

			found_tmp = None
			for c_tmp in candidate_tmps:
				if mc.objExists(c_tmp):
					found_tmp = c_tmp
					break

			if found_tmp:
				finger_tmp_jnts.append(found_tmp)
			else:
				expected_name = f"{nameSpace}{finger}{n:02d}{position}{side}_tmpJnt" if position else f"{nameSpace}{finger}{n:02d}{side}_tmpJnt"
				mc.error(f"Template guide joint '{expected_name}' not found in scene! Aborting finger setup for '{finger}{position}{side}'.")
				return

		total_joints = len(finger_tmp_jnts)
		if total_joints == 0:
			mc.error(f"No template joints found for finger '{finger}{position}{side}'. Aborting.")
			return

		# 4.1 Create Bind Joints (_bJnt) - Default Skeleton Color
		finger_b_jnts = []
		for idx, tmp_jnt in enumerate(finger_tmp_jnts):
			jnt_num = idx + 1
			b_name = f"{nameSpace}{finger}{jnt_num:02d}{position}{side}_bJnt"
			b_jnt = rigTools.jointAt(tmp_jnt)
			b_jnt.rename(b_name)
			b_jnt.attr('overrideEnabled').value = False
			b_jnt.attr('segmentScaleCompensate').value = 0

			# Labeling
			label_map = {
				'thumb': 'thumb',
				'index': 'index finger',
				'middle': 'mid finger',
				'ring': 'ring finger',
				'pinky': 'pinky finger'
			}
			b_jnt.setLable(side, label_map.get(finger, finger))

			if idx == 0:
				if mc.objExists(curr_prior_jnt):
					b_jnt.parent(curr_prior_jnt)
			else:
				b_jnt.parent(finger_b_jnts[idx - 1])

			finger_b_jnts.append(b_jnt)
			all_b_jnts.append(b_jnt.name)

		for b_item in finger_b_jnts:
			b_item.freeze(r=True)

		# Ensure prior joints also have SSC disabled so scale propagates cleanly
		if mc.objExists(curr_prior_jnt) and mc.attributeQuery('segmentScaleCompensate', node=curr_prior_jnt, exists=True):
			mc.setAttr(f"{curr_prior_jnt}.segmentScaleCompensate", 0)
		if mc.objExists(thumb_prior_jnt_name) and mc.attributeQuery('segmentScaleCompensate', node=thumb_prior_jnt_name, exists=True):
			mc.setAttr(f"{thumb_prior_jnt_name}.segmentScaleCompensate", 0)

		# 4.2 Create FK Joints (_fkJnt) inside jnt_grp
		fk_color_id = 6 if 'LFT' in side else 13
		finger_fk_jnts = []
		for idx, tmp_jnt in enumerate(finger_tmp_jnts):
			jnt_num = idx + 1
			fk_name = f"{nameSpace}{finger}{jnt_num:02d}{position}{side}_fkJnt"
			fk_jnt = rigTools.jointAt(tmp_jnt)
			fk_jnt.rename(fk_name)
			fk_jnt.attr('overrideColor').value = fk_color_id
			fk_jnt.attr('overrideEnabled').value = True

			if idx == 0:
				fk_jnt.parent(curr_jnt_grp.name)
			else:
				fk_jnt.parent(finger_fk_jnts[idx - 1])

			finger_fk_jnts.append(fk_jnt)
			all_fk_jnts.append(fk_jnt.name)

		for fk_item in finger_fk_jnts:
			fk_item.freeze(r=True)

		# 4.3 Create IK Joints (_ikJnt) inside jnt_grp if hasIk
		finger_ik_jnts = []
		if hasIk:
			for idx, tmp_jnt in enumerate(finger_tmp_jnts):
				jnt_num = idx + 1
				ik_name = f"{nameSpace}{finger}{jnt_num:02d}{position}{side}_ikJnt"
				ik_jnt = rigTools.jointAt(tmp_jnt)
				ik_jnt.rename(ik_name)
				ik_jnt.attr('overrideColor').value = 17
				ik_jnt.attr('overrideEnabled').value = True

				if idx == 0:
					ik_jnt.parent(curr_jnt_grp.name)
				else:
					ik_jnt.parent(finger_ik_jnts[idx - 1])

				finger_ik_jnts.append(ik_jnt)
				all_ik_jnts.append(ik_jnt.name)

			for ik_item in finger_ik_jnts:
				ik_item.freeze(r=True)

			# Set preferred angles on IK chain to prevent snapping
			for ik_item in finger_ik_jnts:
				mc.joint(ik_item.name, edit=True, setPreferredAngles=True)

		# 4.4 Create FK Controllers with Zro_grp and Offset_grp
		finger_fk_ctrls = []
		for n in range(1, fingerNum + 1):
			ctrl_name = f"{nameSpace}{finger}{n:02d}{position}{side}_ctrl"
			tmp_name = finger_tmp_jnts[n - 1]

			ctrl = core.Dag(ctrl_name)
			ctrl.nmCreateController(ctrlShape)
			ctrl.editCtrlShape(axis=charScale * 0.8)
			ctrl.setColor(side_color)

			# Create Offset group wrapped inside Zero group
			offset_grp = core.Null(f"{nameSpace}{finger}{n:02d}{position}{side}{offsetName}")
			zro_grp = core.Null(f"{nameSpace}{finger}{n:02d}{position}{side}{zroName}")

			ctrl.parent(offset_grp)
			offset_grp.parent(zro_grp)

			zro_grp.matchAll(tmp_name)

			if n == 1:
				zro_grp.parent(curr_fk_ctrl_grp)
			else:
				zro_grp.parent(finger_fk_ctrls[n - 2])

			# Drive FK Joint via Matrix Constraint
			mtc.parentConMatrixGPT(source=ctrl.name, target=finger_fk_jnts[n - 1].name, mo=True)
			finger_fk_ctrls.append(ctrl.name)
			all_fk_ctrls.append(ctrl.name)

		# 4.5 Create IK Handle (RP solver with POV or SC solver fallback) & Tip Controller if hasIk
		if hasIk and len(finger_ik_jnts) >= 2:
			start_ik_jnt = finger_ik_jnts[0].name
			end_ik_jnt = finger_ik_jnts[-1].name
			ikh_name = f"{nameSpace}{finger}{position}{side}_ikh"

			# Check for finger Pole Vector template joint
			candidate_povs = [
				f"{nameSpace}{finger}Pov{position}{side}_tmpJnt",
				f"{nameSpace}{finger}{position}{side}_pov_tmpJnt",
				f"{nameSpace}{finger}01Pov{position}{side}_tmpJnt",
				f"{nameSpace}{finger}Pov{side}_tmpJnt",
				f"{nameSpace}{finger}{side}_pov_tmpJnt",
				f"{nameSpace}{finger}01Pov{side}_tmpJnt"
			]
			pov_tmp_name = None
			for cand in candidate_povs:
				if mc.objExists(cand):
					pov_tmp_name = cand
					break

			solver_type = 'ikRPsolver' if pov_tmp_name else 'ikSCsolver'
			ikh, effector = mc.ikHandle(sj=start_ik_jnt, ee=end_ik_jnt, sol=solver_type, name=ikh_name)
			all_ik_handles.append(ikh)

			# Create IK Tip Controller
			ik_ctrl_name = f"{nameSpace}{finger}Ik{position}{side}_ctrl"
			ik_ctrl = core.Dag(ik_ctrl_name)
			ik_ctrl.nmCreateController(ikCtrlShape)
			ik_ctrl.editCtrlShape(axis=charScale * 0.6)
			ik_ctrl.setColor('yellow')

			ik_zro = rigTools.zeroGroupNam(ik_ctrl)
			ik_zro.matchAll(finger_tmp_jnts[-1])
			ik_zro.parent(curr_ik_ctrl_grp)

			if hasGroundCollision and collisionMesh and mc.objExists(collisionMesh):
				ik_contact_grp = core.Null(f"{nameSpace}{finger}Ik{position}{side}Contact_grp")
				ik_contact_grp.matchAll(finger_tmp_jnts[-1])
				ik_contact_grp.parent(ik_ctrl.name)

				# Setup Matrix Mesh Collision on downstream contact group (probing ik_ctrl to eliminate cycle)
				mmCol.setup_matrix_mesh_collision(
					nameSpace=nameSpace,
					baseName=baseName,
					side=side,
					partName=f"{finger}03",
					probeObj=ik_ctrl.name,
					targetOffsetGrp=ik_contact_grp.name,
					collisionMesh=collisionMesh,
					stickCtrl=stick_ctrl.name,
					blendAttr='groundCollision',
					yOnly=collisionYOnly
				)
				ik_driver = ik_contact_grp.name
			else:
				ik_driver = ik_ctrl.name

			# Space Switch on IK Tip Controller (Master allFingerSpace + Individual Space)
			ik_ctrl.addAttribute(longName='space', niceName='Space', at='enum', en='World:Ankle', keyable=True)
			world_target = parent_to_name
			local_space_target = curr_prior_jnt
			if mc.objExists(world_target) and mc.objExists(local_space_target):
				pma_ik_space = mc.createNode('plusMinusAverage', name=f"{nameSpace}{baseName}{finger}IkSpaceSum{side}_pma")
				mc.connectAttr(f"{stick_ctrl.name}.allFingerSpace", f"{pma_ik_space}.input1D[0]", force=True)
				mc.connectAttr(f"{ik_ctrl.name}.space", f"{pma_ik_space}.input1D[1]", force=True)

				clamp_ik_space = mc.createNode('clamp', name=f"{nameSpace}{baseName}{finger}IkSpaceClamp{side}_clp")
				mc.setAttr(f"{clamp_ik_space}.minR", 0.0)
				mc.setAttr(f"{clamp_ik_space}.maxR", 1.0)
				mc.connectAttr(f"{pma_ik_space}.output1D", f"{clamp_ik_space}.inputR", force=True)
				ik_space_plug = f"{clamp_ik_space}.outputR"

				ik_space_pcon = mc.parentConstraint(world_target, local_space_target, ik_zro.name, mo=True, name=f"{ik_zro.name}_space_parCons")[0]
				ik_w_targets = mc.parentConstraint(ik_space_pcon, q=True, targetList=True)
				ik_rev_space = mc.createNode('reverse', name=f"{nameSpace}{baseName}{finger}IkSpace{side}_rev")
				mc.connectAttr(ik_space_plug, f"{ik_rev_space}.inputX", force=True)
				mc.connectAttr(f"{ik_rev_space}.outputX", f"{ik_space_pcon}.{ik_w_targets[0]}W0", force=True)
				mc.connectAttr(ik_space_plug, f"{ik_space_pcon}.{ik_w_targets[1]}W1", force=True)

			mc.parent(ikh, ik_driver)
			mc.setAttr(f"{ikh}.v", False)

			# Orient tip joint directly to IK Controller
			mc.orientConstraint(ik_ctrl.name, end_ik_jnt, mo=True, name=f"{end_ik_jnt}_oriCons")

			all_ik_ctrls.append(ik_ctrl.name)

			# Create IK Pole Vector Controller if pov_tmp_name exists
			if pov_tmp_name:
				pov_ctrl_name = f"{nameSpace}{finger}Pov{position}{side}_ctrl"
				pov_ctrl = core.Dag(pov_ctrl_name)
				pov_ctrl.nmCreateController(povShape)
				pov_ctrl.editCtrlShape(axis=charScale * povScale)
				pov_ctrl.setColor('yellow')

				pov_zro = rigTools.zeroGroupNam(pov_ctrl)
				pov_zro.matchAll(pov_tmp_name)
				pov_zro.parent(curr_ik_ctrl_grp)

				# Space Switch on POV Controller (Master allFingerSpace + Individual Space)
				pov_ctrl.addAttribute(longName='space', niceName='Space', at='enum', en='World:Ankle', keyable=True)
				if mc.objExists(world_target) and mc.objExists(local_space_target):
					pma_pov_space = mc.createNode('plusMinusAverage', name=f"{nameSpace}{baseName}{finger}PovSpaceSum{side}_pma")
					mc.connectAttr(f"{stick_ctrl.name}.allFingerSpace", f"{pma_pov_space}.input1D[0]", force=True)
					mc.connectAttr(f"{pov_ctrl.name}.space", f"{pma_pov_space}.input1D[1]", force=True)

					clamp_pov_space = mc.createNode('clamp', name=f"{nameSpace}{baseName}{finger}PovSpaceClamp{side}_clp")
					mc.setAttr(f"{clamp_pov_space}.minR", 0.0)
					mc.setAttr(f"{clamp_pov_space}.maxR", 1.0)
					mc.connectAttr(f"{pma_pov_space}.output1D", f"{clamp_pov_space}.inputR", force=True)
					pov_space_plug = f"{clamp_pov_space}.outputR"

					pov_space_pcon = mc.parentConstraint(world_target, local_space_target, pov_zro.name, mo=True, name=f"{pov_zro.name}_space_parCons")[0]
					pov_w_targets = mc.parentConstraint(pov_space_pcon, q=True, targetList=True)
					pov_rev_space = mc.createNode('reverse', name=f"{nameSpace}{baseName}{finger}PovSpace{side}_rev")
					mc.connectAttr(pov_space_plug, f"{pov_rev_space}.inputX", force=True)
					mc.connectAttr(f"{pov_rev_space}.outputX", f"{pov_space_pcon}.{pov_w_targets[0]}W0", force=True)
					mc.connectAttr(pov_space_plug, f"{pov_space_pcon}.{pov_w_targets[1]}W1", force=True)

				mc.poleVectorConstraint(pov_ctrl.name, ikh, name=f"{nameSpace}{finger}Pov{position}{side}_poleVectorCons")
				all_pov_ctrls.append(pov_ctrl.name)

				# Connect POV visibility to FK/IK switch
				if fk_ik_plug:
					mc.connectAttr(fk_ik_plug, f"{pov_zro.name}.v", force=True)

		# 4.6 FK / IK Blending on Bind Joints (_bJnt)
		if hasIk and len(finger_ik_jnts) == len(finger_fk_jnts):
			rev_node = mc.createNode('reverse', name=f"{nameSpace}{baseName}{finger}FkIk{side}_rev")
			mc.connectAttr(fk_ik_plug, f"{rev_node}.inputX", force=True)

			for idx in range(len(finger_b_jnts)):
				b_jnt_name = finger_b_jnts[idx].name
				fk_jnt_name = finger_fk_jnts[idx].name
				ik_jnt_name = finger_ik_jnts[idx].name

				p_con = mc.parentConstraint(fk_jnt_name, ik_jnt_name, b_jnt_name, mo=False, name=f"{b_jnt_name}_parCons")[0]
				# Connect weights: FK is reverse (1 - fkIk), IK is fkIk
				mc.connectAttr(f"{rev_node}.outputX", f"{p_con}.{fk_jnt_name}W0", force=True)
				mc.connectAttr(fk_ik_plug, f"{p_con}.{ik_jnt_name}W1", force=True)

			# Controller Visibility Switching
			# In FK mode (fkIk=0): FK visible, IK hidden
			# In IK mode (fkIk=1): FK hidden, IK visible
			# Connect visibility to respective zero/control groups
			if finger_fk_ctrls and all_ik_ctrls:
				# FK root controller group visibility
				fk_root_zro = f"{nameSpace}{finger}01{position}{side}{zroName}"
				if mc.objExists(fk_root_zro):
					mc.connectAttr(f"{rev_node}.outputX", f"{fk_root_zro}.v", force=True)
				# IK controller zero group visibility
				ik_root_zro = f"{nameSpace}{finger}Ik{position}{side}{zroName}"
				if mc.objExists(ik_root_zro):
					mc.connectAttr(fk_ik_plug, f"{ik_root_zro}.v", force=True)
		else:
			# Direct FK drive if no IK
			for idx in range(min(len(finger_fk_ctrls), len(finger_b_jnts))):
				mtc.parentConMatrixGPT(source=finger_fk_ctrls[idx], target=finger_b_jnts[idx].name, mo=True)

	if mc.objExists(parent_to_name):
		mc.parent(f_grp.name, parent_to_name)
		if has_isolated_thumb and mc.objExists(thumb_f_grp.name):
			mc.parent(thumb_f_grp.name, parent_to_name)

	mc.select(clear=True)

	misc.makeHeader(f"DONE Creature Finger {side} Rig")

	return {
		'finger_grp': f_grp.name,
		'thumb_finger_grp': thumb_f_grp.name if has_isolated_thumb else None,
		'fk_ctrls': all_fk_ctrls,
		'ik_ctrls': all_ik_ctrls,
		'pov_ctrls': all_pov_ctrls,
		'bind_joints': all_b_jnts,
		'fk_joints': all_fk_jnts,
		'ik_joints': all_ik_jnts,
		'ik_handles': all_ik_handles,
		'stick_ctrl': stick_ctrl.name
	}


def creatureFingerCurlRig(
	nameSpace='',
	baseName='',
	side='LFT',
	fingerName=('thumb', 'index', 'middle', 'ring', 'pinky'),
	numCtrl=3,
	offsetName='Offset_grp',
	stickNam='',
	priorJnt='',
	thumbPriorJnt='',
	charScale=1.0
):
	"""
	Construct procedural Curl, Roll, Fist, Clench, Relax, Cup, Spread, and HandScale math network for creature fingers.
	Adds attributes directly onto the specified stick controller (e.g. 'legStickLFT_ctrl').

	Pose behaviors supported:
		- 'fist': Full hand fist curl on X-axis.
		- 'roll': Progressive rolling curl from knuckle to claw tip.
		- 'relax': Relaxed resting hand curl.
		- 'spread': Finger spreading on Z-axis (fanning outwards from middle).
		- 'cup': Palm cupping.
		- 'clench': Creature floor clench (joint 01 knuckle arch up, joints 02/03 claw tip dig down).
		- 'handScale': Uniform finger and hand scale.

	Args:
		nameSpace (str): Global namespace prefix.
		baseName (str): Base limb/foot identifier (e.g. 'frontLeg', 'backLeg01', 'backLeg02').
		side (str): Side identifier ('LFT' or 'RGT').
		fingerName (tuple[str]): Finger base names.
		numCtrl (int): Number of FK controllers per finger.
		offsetName (str): Suffix for offset groups.
		stickNam (str): Target stick controller name. If empty, auto-resolves to 'legStick{side}_ctrl'.
		priorJnt (str): Prior parent bind joint (e.g. 'ballLFT_bJnt') for handScale driving.
		thumbPriorJnt (str): Dedicated root joint for handScale expansion (e.g. 'ankleLFT_bJnt'). Takes priority over priorJnt.
		charScale (float): Character scale.
	"""
	core.makeHeader(f"Creature Finger Curl {side} Rig")

	if not stickNam:
		candidate_leg_stick = f"{nameSpace}legStick{side}_ctrl"
		candidate_front_stick = f"{nameSpace}frontFootStick{side}_ctrl"
		if mc.objExists(candidate_leg_stick):
			stickNam = candidate_leg_stick
		elif mc.objExists(candidate_front_stick):
			stickNam = candidate_front_stick
		else:
			stickNam = candidate_leg_stick

	if not mc.objExists(stickNam):
		mc.error(f"[creatureFingerCurlRig] Stick controller '{stickNam}' does not exist in scene! Please build the parent leg/stick controller before curl setup.")
		return

	stick_ctrl = core.Dag(stickNam)

	# Resolve baseName if not explicitly provided
	if not baseName:
		raw_stick = misc.splitName(stickNam)[0].replace('Stick', '').replace('ctrl', '').replace(side, '').replace('_', '')
		baseName = raw_stick if raw_stick else 'frontLeg'

	# Extract position token (e.g. 'Back01', 'Back02', 'BackA', 'BackB') from baseName
	position = ''
	if baseName and baseName not in ('frontLeg', 'front', 'leg'):
		clean_pos = baseName.replace('Leg', '').replace('leg', '')
		position = clean_pos[0].upper() + clean_pos[1:] if clean_pos else ''

	# 1. Add Attribute Headers & Curl Attributes
	if not mc.attributeQuery('curlSettings', node=stick_ctrl.name, exists=True):
		stick_ctrl.addAttribute(longName='curlSettings', niceName='_', at='enum', en='Curl_Poses', keyable=True)

	curl_attrs = [
		('fist', 0.0),
		('roll', 0.0),
		('relax', 0.0),
		('spread', 0.0),
		('cup', 0.0),
		('clench', 0.0),  # Floor Clench (นิ้วจิกพื้น)
		('handScale', 1.0)
	]

	for attr_name, default_val in curl_attrs:
		if not mc.attributeQuery(attr_name, node=stick_ctrl.name, exists=True):
			stick_ctrl.addAttribute(attributeType='float', ln=attr_name, k=True, dv=default_val)

	# 2. Master FK/IK synchronization if allFkIk exists
	if mc.attributeQuery('allFkIk', node=stick_ctrl.name, exists=True):
		for finger in fingerName:
			f_attr = f"{finger}FkIk"
			if mc.attributeQuery(f_attr, node=stick_ctrl.name, exists=True):
				# When allFkIk changes, users can drive all fingers seamlessly
				pass

	# 3. Create Multipliers & Math Nodes for each behavior (Consistent anatomical curl across LFT and RGT)
	# 3.1 Fist Behavior: Rotates X on all joints (01, 02, 03)
	fist_mdv = mc.createNode('multiplyDivide', name=f"{nameSpace}{baseName}Fist{side}_mdv")
	mc.connectAttr(f"{stick_ctrl.name}.fist", f"{fist_mdv}.input1X", force=True)
	mc.connectAttr(f"{stick_ctrl.name}.fist", f"{fist_mdv}.input1Y", force=True)
	mc.connectAttr(f"{stick_ctrl.name}.fist", f"{fist_mdv}.input1Z", force=True)
	mc.setAttr(f"{fist_mdv}.input2X", -9.0)
	mc.setAttr(f"{fist_mdv}.input2Y", -10.0)
	mc.setAttr(f"{fist_mdv}.input2Z", -11.0)

	# 3.2 Roll Behavior: Progressive curling roll
	roll_mdv = mc.createNode('multiplyDivide', name=f"{nameSpace}{baseName}Roll{side}_mdv")
	mc.connectAttr(f"{stick_ctrl.name}.roll", f"{roll_mdv}.input1X", force=True)
	mc.connectAttr(f"{stick_ctrl.name}.roll", f"{roll_mdv}.input1Y", force=True)
	mc.connectAttr(f"{stick_ctrl.name}.roll", f"{roll_mdv}.input1Z", force=True)
	mc.setAttr(f"{roll_mdv}.input2X", -1.2)
	mc.setAttr(f"{roll_mdv}.input2Y", -1.5)
	mc.setAttr(f"{roll_mdv}.input2Z", -1.8)

	# 3.3 Clench Behavior (นิ้วจิกพื้น / Floor Clench)
	# Joint 01: Arches UP (+), Joints 02/03: Digs DOWN (-)
	clench_mdv = mc.createNode('multiplyDivide', name=f"{nameSpace}{baseName}Clench{side}_mdv")
	mc.connectAttr(f"{stick_ctrl.name}.clench", f"{clench_mdv}.input1X", force=True)
	mc.connectAttr(f"{stick_ctrl.name}.clench", f"{clench_mdv}.input1Y", force=True)
	mc.connectAttr(f"{stick_ctrl.name}.clench", f"{clench_mdv}.input1Z", force=True)
	# Knuckle 01 arches up (+4.0), Joint 02 flexes down (-8.0), Joint 03 claw tips dig hard down (-12.0)
	mc.setAttr(f"{clench_mdv}.input2X", 4.0)
	mc.setAttr(f"{clench_mdv}.input2Y", -8.0)
	mc.setAttr(f"{clench_mdv}.input2Z", -12.0)

	# 4. Connect Behaviors to each Finger's Offset Groups
	spread_angles = {
		'thumb': -3.0,
		'index': -1.5,
		'middle': 0.0,
		'ring': 1.5,
		'pinky': 3.0
	}

	cup_angles = {
		'thumb': 0.5,
		'index': 0.0,
		'middle': 0.0,
		'ring': -0.8,
		'pinky': -1.6
	}

	relax_amps = {
		'thumb': 0.8,
		'index': 1.0,
		'middle': 1.2,
		'ring': 1.4,
		'pinky': 1.6
	}

	# Graduated Floor Clench Profile (Middle peaks at apex, diminishing outward to Index, Ring, Pinky, and Thumb)
	clench_amps = {
		'middle': 1.25,
		'index': 1.05,
		'ring': 0.95,
		'pinky': 0.75,
		'thumb': 0.65
	}

	# Get Stick Controller Shape node to host per-joint tuning multipliers
	stick_shapes = mc.listRelatives(stick_ctrl.name, shapes=True) or []
	stick_shape = stick_shapes[0] if stick_shapes else f"{stick_ctrl.name}Shape"

	for finger in fingerName:
		# 4.1 Spread Connection (Z-axis rotation on joint 01)
		spread_val = spread_angles.get(finger, 0.0)
		if spread_val != 0.0:
			spread_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}{finger}Spread{side}_mdl")
			mc.connectAttr(f"{stick_ctrl.name}.spread", f"{spread_mdl}.input1", force=True)
			mc.setAttr(f"{spread_mdl}.input2", spread_val)

			candidate_off_01 = [
				f"{nameSpace}{finger}01{position}{side}{offsetName}",
				f"{nameSpace}{finger}01{side}{offsetName}"
			]
			off_01 = None
			for c_off in candidate_off_01:
				if mc.objExists(c_off):
					off_01 = c_off
					break

			if off_01:
				# Connect to rotateZ (or rotateY depending on orientation)
				mc.connectAttr(f"{spread_mdl}.output", f"{off_01}.rz", force=True)

		# 4.2 Cup Connection (X/Z tilt on joint 01)
		cup_val = cup_angles.get(finger, 0.0)
		if cup_val != 0.0:
			cup_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}{finger}Cup{side}_mdl")
			mc.connectAttr(f"{stick_ctrl.name}.cup", f"{cup_mdl}.input1", force=True)
			mc.setAttr(f"{cup_mdl}.input2", cup_val)

			candidate_off_01 = [
				f"{nameSpace}{finger}01{position}{side}{offsetName}",
				f"{nameSpace}{finger}01{side}{offsetName}"
			]
			off_01 = None
			for c_off in candidate_off_01:
				if mc.objExists(c_off):
					off_01 = c_off
					break

			if off_01:
				mc.connectAttr(f"{cup_mdl}.output", f"{off_01}.ry", force=True)

		# 4.3 Relax Connection
		r_amp = relax_amps.get(finger, 1.0)
		relax_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}{finger}Relax{side}_mdl")
		mc.connectAttr(f"{stick_ctrl.name}.relax", f"{relax_mdl}.input1", force=True)
		mc.setAttr(f"{relax_mdl}.input2", -2.5 * r_amp)

		# 4.4 Floor Clench Multiplier per finger
		c_amp = clench_amps.get(finger, 1.0)

		# 4.5 Summation & Multiplier Math Network on X-Rotation for Joints 01, 02, 03
		for n in range(1, numCtrl + 1):
			candidate_offsets = [
				f"{nameSpace}{finger}{n:02d}{position}{side}{offsetName}",
				f"{nameSpace}{finger}{n:02d}{side}{offsetName}"
			]
			off_name = None
			for c_off in candidate_offsets:
				if mc.objExists(c_off):
					off_name = c_off
					break

			if not off_name:
				expected_off = f"{nameSpace}{finger}{n:02d}{position}{side}{offsetName}" if position else f"{nameSpace}{finger}{n:02d}{side}{offsetName}"
				mc.error(f"[creatureFingerCurlRig] Controller offset group '{expected_off}' not found in scene! Please run creatureFingerRig first.")
				return

			# Create plusMinusAverage sum node
			pma_node = mc.createNode('plusMinusAverage', name=f"{nameSpace}{baseName}{finger}{n:02d}RotXSum{side}_pma")

			# Input 1: Fist
			channel_xyz = ['outputX', 'outputY', 'outputZ'][n - 1]
			mc.connectAttr(f"{fist_mdv}.{channel_xyz}", f"{pma_node}.input1D[0]", force=True)

			# Input 2: Roll
			mc.connectAttr(f"{roll_mdv}.{channel_xyz}", f"{pma_node}.input1D[1]", force=True)

			# Input 3: Clench (Floor Clench with graduated finger curve multiplier)
			clench_finger_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}{finger}{n:02d}Clench{side}_mdl")
			mc.connectAttr(f"{clench_mdv}.{channel_xyz}", f"{clench_finger_mdl}.input1", force=True)
			mc.setAttr(f"{clench_finger_mdl}.input2", c_amp)
			mc.connectAttr(f"{clench_finger_mdl}.output", f"{pma_node}.input1D[2]", force=True)

			# Input 4: Relax (progressive multiplier per joint level)
			if n == 1:
				mc.connectAttr(f"{relax_mdl}.output", f"{pma_node}.input1D[3]", force=True)
			else:
				relax_sub_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}{finger}{n:02d}RelaxSub{side}_mdl")
				mc.connectAttr(f"{relax_mdl}.output", f"{relax_sub_mdl}.input1", force=True)
				mc.setAttr(f"{relax_sub_mdl}.input2", 1.2 * n)
				mc.connectAttr(f"{relax_sub_mdl}.output", f"{pma_node}.input1D[3]", force=True)

			# 4.6 Shape Node Tuning Multiplier: {finger}{n:02d}Rx (e.g. index02Rx)
			shape_attr = f"{finger}{n:02d}Rx"
			if not mc.attributeQuery(shape_attr, node=stick_shape, exists=True):
				mc.addAttr(stick_shape, longName=shape_attr, attributeType='float', defaultValue=1.0, keyable=True)

			amp_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}{finger}{n:02d}Amp{side}_mdl")
			mc.connectAttr(f"{pma_node}.output1D", f"{amp_mdl}.input1", force=True)
			mc.connectAttr(f"{stick_shape}.{shape_attr}", f"{amp_mdl}.input2", force=True)

			# Connect Amp Multiplier output to Offset group rotateX
			mc.connectAttr(f"{amp_mdl}.output", f"{off_name}.rx", force=True)

	# 5. Hand Scale Connection (Dampened Multiplier: Scale = 1.0 + (handScale - 1.0) * 0.2)
	# 5.1 Math Network
	hs_sub_pma = mc.createNode('plusMinusAverage', name=f"{nameSpace}{baseName}HandScaleSub{side}_pma")
	mc.setAttr(f"{hs_sub_pma}.operation", 2)  # Subtract
	mc.connectAttr(f"{stick_ctrl.name}.handScale", f"{hs_sub_pma}.input1D[0]", force=True)
	mc.setAttr(f"{hs_sub_pma}.input1D[1]", 1.0)

	hs_mult_mdl = mc.createNode('multDoubleLinear', name=f"{nameSpace}{baseName}HandScaleMult{side}_mdl")
	mc.connectAttr(f"{hs_sub_pma}.output1D", f"{hs_mult_mdl}.input1", force=True)
	mc.setAttr(f"{hs_mult_mdl}.input2", 0.2)  # Attenuation factor

	hs_out_pma = mc.createNode('plusMinusAverage', name=f"{nameSpace}{baseName}HandScaleOut{side}_pma")
	mc.setAttr(f"{hs_out_pma}.operation", 1)  # Sum
	mc.connectAttr(f"{hs_mult_mdl}.output", f"{hs_out_pma}.input1D[0]", force=True)
	mc.setAttr(f"{hs_out_pma}.input1D[1]", 1.0)

	scale_plug = f"{hs_out_pma}.output1D"

	# 5.2 Drive Root / Prior Bind Joint (thumbPriorJnt e.g. ankleLFT_bJnt, or priorJnt e.g. ballLFT_bJnt)
	target_prior_jnt = None
	if thumbPriorJnt:
		target_prior_jnt = thumbPriorJnt.name if hasattr(thumbPriorJnt, 'name') else str(thumbPriorJnt)
	elif priorJnt:
		target_prior_jnt = priorJnt.name if hasattr(priorJnt, 'name') else str(priorJnt)
	else:
		candidate_priors = [
			f"{nameSpace}ankle{position}{side}_bJnt",
			f"{nameSpace}ankle{side}_bJnt",
			f"{nameSpace}hand{position}{side}_bJnt",
			f"{nameSpace}ball{position}{side}_bJnt",
			f"{nameSpace}ballRoll{position}{side}_bJnt",
			f"{nameSpace}hand{side}_bJnt",
			f"{nameSpace}ball{side}_bJnt",
			f"{nameSpace}wrist{side}_bJnt"
		]
		for c_prior in candidate_priors:
			if mc.objExists(c_prior):
				target_prior_jnt = c_prior
				break

	if target_prior_jnt and mc.objExists(target_prior_jnt):
		for axis in ('sx', 'sy', 'sz'):
			mc.connectAttr(scale_plug, f"{target_prior_jnt}.{axis}", force=True)

		# Ensure target root joint has segmentScaleCompensate disabled
		if mc.attributeQuery('segmentScaleCompensate', node=target_prior_jnt, exists=True):
			mc.setAttr(f"{target_prior_jnt}.segmentScaleCompensate", 0)

	# Also disable SSC on child ball joint if priorJnt exists so scale cascades down to all fingers
	if priorJnt:
		p_jnt = priorJnt.name if hasattr(priorJnt, 'name') else str(priorJnt)
		if mc.objExists(p_jnt) and mc.attributeQuery('segmentScaleCompensate', node=p_jnt, exists=True):
			mc.setAttr(f"{p_jnt}.segmentScaleCompensate", 0)

	# 5.3 Drive Finger Master Groups (controller position scaling)
	# Architecture matching original armRigMatrix.py + fingerRig.py:
	#   - ball_bJnt scale (5.2): expands mesh/skin via skeletal hierarchy
	#   - f_grp scale (5.3): moves controller positions outward so parentConstraint
	#     drives bind joints to correct scaled positions
	#   - Finger joints have SSC=True (Maya default) which blocks scale inheritance
	#     from ball_bJnt, preventing double-scale. Controllers provide the sole
	#     position authority via parentConstraint.
	f_grp_candidates = [
		f"{nameSpace}{baseName}Finger{side}_grp",
		f"{nameSpace}{baseName}ThumbFinger{side}_grp",
		f"{nameSpace}handFinger{side}_grp",
		f"{nameSpace}ballFinger{side}_grp",
		f"{nameSpace}Finger{side}_grp"
	]
	for grp_candidate in f_grp_candidates:
		if mc.objExists(grp_candidate):
			for axis in ('sx', 'sy', 'sz'):
				mc.connectAttr(scale_plug, f"{grp_candidate}.{axis}", force=True)

	misc.makeHeader(f"DONE Creature Finger Curl {side} Rig")
