"""
# Module for batch scaling Auto-Rig Pro controller shapes in Blender.

# Usage: Select obj first


from function.blenderTools.rigging.controller import scale_controller_list as scl

hand_main_ctrl = [
	'c_pinky1.l', 'c_pinky2.l',  'c_ring1.l', 'c_ring2.l', 
	'c_middle1.l', 'c_middle2.l', 'c_index1.l', 'c_index2.l', 
	'c_thumb1.l', 'c_thumb2.l', 'c_pinky1.r', 'c_pinky2.r', 
	'c_ring1.r', 'c_ring2.r', 'c_middle1.r', 'c_middle2.r', 
	'c_index1.r', 'c_index2.r', 'c_thumb1.r', 'c_thumb2.r' ]

   
hand_tip_ctrl = ['c_pinky3.l' ,'c_ring3.l', 'c_middle3.l', 'c_index3.l', 'c_thumb3.l',
'c_pinky3.r' ,'c_ring3.r', 'c_middle3.r', 'c_index3.r', 'c_thumb3.r']


handBase_ctrl = [	'c_thumb1_base.l', 'c_index1_base.l', 'c_middle1_base.l', 'c_ring1_base.l',
					'c_thumb1_base.r', 'c_index1_base.r', 'c_middle1_base.r', 'c_ring1_base.r']

pelvis_ctrl=['c_root_master.x']

scl.scale_controllers_xy(hand_main_ctrl, 2.0)
scl.scale_controllers_xy(hand_tip_ctrl, 1.5)
scl.scale_controllers_xy(handBase_ctrl, 0.35)
scl.scale_controllers_xy(pelvis_ctrl, 1.25)

"""
import bpy


hand_ctrl = [
	'c_pinky1.l', 'c_pinky2.l', 'c_pinky3.l', 'c_ring1.l', 'c_ring2.l', 'c_ring3.l', 
	'c_middle1.l', 'c_middle2.l', 'c_middle3.l', 'c_index1.l', 'c_index2.l', 'c_index3.l', 
	'c_thumb1.l', 'c_thumb2.l', 'c_thumb3.l', 'c_pinky1.r', 'c_pinky2.r', 'c_pinky3.r', 
	'c_ring1.r', 'c_ring2.r', 'c_ring3.r', 'c_middle1.r', 'c_middle2.r', 'c_middle3.r', 
	'c_index1.r', 'c_index2.r', 'c_index3.r', 'c_thumb1.r', 'c_thumb2.r', 'c_thumb3.r'
]

SCALE = 3.0

def show_message_box(message="", title="CNI Scale Controller", icon='INFO'):
	def draw(self, context):
		self.layout.label(text=message)
	bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def scale_controllers_xy(bone_names, scale_xy):
	obj = bpy.context.active_object
	if not obj or obj.type != 'ARMATURE':
		show_message_box("Error: Active object must be an Armature!", "Error", 'ERROR')
		return

	# Automatically switch to Pose Mode if not already in it
	if bpy.context.mode != 'POSE':
		bpy.ops.object.mode_set(mode='POSE')

	scaled_count = 0
	not_found = []

	for name in bone_names:
		bone = obj.pose.bones.get(name)
		# Flexible lookup: fallback to _base for the first knuckle joints if not found directly
		if not bone and "1." in name:
			fallback_name = name.replace("1.", "1_base.")
			bone = obj.pose.bones.get(fallback_name)

		if bone:
			current_z = bone.custom_shape_scale_xyz[2]
			bone.custom_shape_scale_xyz = (scale_xy, scale_xy, scale_xy)
			scaled_count += 1
		else:
			not_found.append(name)

	show_message_box(f"Scaled {scaled_count} controllers to {scale_xy}. (Missing: {len(not_found)})", "Result")
	if not_found:
		print("Missing bones in armature:", not_found)

if __name__ == "__main__":
	scale_controllers_xy(hand_ctrl, SCALE)
