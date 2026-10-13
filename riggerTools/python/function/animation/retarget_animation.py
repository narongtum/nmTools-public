
retarget_ctrl_data = {
	# ตำแหน่ง : [Source_Joint, Target_Controller]
	'hips':      ['Hips', 'hip_ctrl'],
	'spine01':   ['Spine', 'spine01_ctrl'],
	'spine02':   ['Spine1', 'spine02_ctrl'],
	'spine03':   ['Spine2', 'spine03_ctrl'],
	'neck':      ['Neck', 'neck_ctrl'],
	'head':      ['Head', 'head01_ctrl'],

	# --- Left Arm (FK) ---
	'clav_L':    ['LeftShoulder', 'clavLFT_ctrl'],
	'arm_L':     ['LeftArm', 'upperArmFkLFT_ctrl'],
	'forearm_L': ['LeftForeArm', 'lowerArmFkLFT_ctrl'],
	'hand_L':    ['LeftHand', 'handFkLFT_ctrl'],

	# Left Fingers
	'thumb_01_L':  ['LeftHandThumb1', 'thumb01LFT_ctrl'],
	'thumb_02_L':  ['LeftHandThumb2', 'thumb02LFT_ctrl'],
	'thumb_03_L':  ['LeftHandThumb3', 'thumb03LFT_ctrl'],
	'index_01_L':  ['LeftHandIndex1', 'index01LFT_ctrl'],
	'index_02_L':  ['LeftHandIndex2', 'index02LFT_ctrl'],
	'index_03_L':  ['LeftHandIndex3', 'index03LFT_ctrl'],
	'middle_01_L': ['LeftHandMiddle1', 'middle01LFT_ctrl'],
	'middle_02_L': ['LeftHandMiddle2', 'middle02LFT_ctrl'],
	'middle_03_L': ['LeftHandMiddle3', 'middle03LFT_ctrl'],
	'ring_01_L':   ['LeftHandRing1', 'ring01LFT_ctrl'],
	'ring_02_L':   ['LeftHandRing2', 'ring02LFT_ctrl'],
	'ring_03_L':   ['LeftHandRing3', 'ring03LFT_ctrl'],
	'pinky_01_L':  ['LeftHandPinky1', 'pinky01LFT_ctrl'],
	'pinky_02_L':  ['LeftHandPinky2', 'pinky02LFT_ctrl'],
	'pinky_03_L':  ['LeftHandPinky3', 'pinky03LFT_ctrl'],

	# --- Right Arm (FK) ---
	'clav_R':    ['RightShoulder', 'clavRGT_ctrl'],
	'arm_R':     ['RightArm', 'upperArmFkRGT_ctrl'],
	'forearm_R': ['RightForeArm', 'lowerArmFkRGT_ctrl'],
	'hand_R':    ['RightHand', 'handFkRGT_ctrl'],

	# Right Fingers
	'thumb_01_R':  ['RightHandThumb1', 'thumb01RGT_ctrl'],
	'thumb_02_R':  ['RightHandThumb2', 'thumb02RGT_ctrl'],
	'thumb_03_R':  ['RightHandThumb3', 'thumb03RGT_ctrl'],
	'index_01_R':  ['RightHandIndex1', 'index01RGT_ctrl'],
	'index_02_R':  ['RightHandIndex2', 'index02RGT_ctrl'],
	'index_03_R':  ['RightHandIndex3', 'index03RGT_ctrl'],
	'middle_01_R': ['RightHandMiddle1', 'middle01RGT_ctrl'],
	'middle_02_R': ['RightHandMiddle2', 'middle02RGT_ctrl'],
	'middle_03_R': ['RightHandMiddle3', 'middle03RGT_ctrl'],
	'ring_01_R':   ['RightHandRing1', 'ring01RGT_ctrl'],
	'ring_02_R':   ['RightHandRing2', 'ring02RGT_ctrl'],
	'ring_03_R':   ['RightHandRing3', 'ring03RGT_ctrl'],
	'pinky_01_R':  ['RightHandPinky1', 'pinky01RGT_ctrl'],
	'pinky_02_R':  ['RightHandPinky2', 'pinky02RGT_ctrl'],
	'pinky_03_R':  ['RightHandPinky3', 'pinky03RGT_ctrl'],

	# --- Legs (FK) ---
	'upLeg_L':   ['LeftUpLeg', 'upperLegFkLFT_ctrl'],
	'leg_L':     ['LeftLeg', 'lowerLegFkLFT_ctrl'],
	'foot_L':    ['LeftFoot', 'ankleFkLFT_ctrl'],
	'toe_L':     ['LeftToeBase', 'ballLegFkLFT_ctrl'],

	'upLeg_R':   ['RightUpLeg', 'upperLegFkRGT_ctrl'],
	'leg_R':     ['RightLeg', 'lowerLegFkRGT_ctrl'],
	'foot_R':    ['RightFoot', 'ankleFkRGT_ctrl'],
	'toe_R':     ['RightToeBase', 'ballLegFkRGT_ctrl'],
}

import maya.cmds as mc
from function.rigging.constraint import matrixConstraint as mtc

def create_retarget_orient_matrix(joint_dict, source_ns="", target_ns="", mo=True):
	"""
	Retarget โดยใช้ Orient Matrix Constraint (คุมเฉพาะ Rotation)
	
	Args:
		joint_dict (dict): { 'label': [source, target] }
		source_ns (str): Namespace ของฝั่ง Mocap
		target_ns (str): Namespace ของฝั่ง Rig Controller
		mo (bool): Maintain Offset
	"""
	print(f"\n# --- Start Orient Matrix Retargeting (MO: {mo}) --- #")
	
	for label, joints in joint_dict.items():
		src_name = f"{source_ns}:{joints[0]}" if source_ns else joints[0]
		tgt_name = f"{target_ns}:{joints[1]}" if target_ns else joints[1]
		
		if mc.objExists(src_name) and mc.objExists(tgt_name):
			print(f"Orient Constraining [{label}]: {src_name} -> {tgt_name}")
			
			# เปลี่ยนมาใช้ฟังก์ชัน orientConstraintMatrix โดยตรง
			mtc.orientConstraintMatrix(
				src_name, 
				tgt_name, 
				mo=mo
			)
		else:
			if not mc.objExists(src_name): print(f"Missing Source: {src_name}")
			if not mc.objExists(tgt_name): print(f"Missing Target: {tgt_name}")

# ==========================================
# วิธีเรียกใช้งาน
# ==========================================

# รันด้วยชุดข้อมูล Controller ที่เราสกัดมาใหม่
create_retarget_orient_matrix(
	retarget_ctrl_data, 
	source_ns="", 
	target_ns="EM004_PhiTaKhon_Rig", 
	mo=True
)

