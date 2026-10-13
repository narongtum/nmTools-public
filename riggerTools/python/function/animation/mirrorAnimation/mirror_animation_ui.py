import os
import json
import maya.cmds as mc

# Import Studio Library Modules (Ensure this path is correct in your pipeline)
try:
	from function.animation.studiolibrary_mirrortable import MirrorTable, MirrorOption, KeysOption
except ImportError:
	mc.warning("Studio Library mirror modules not found in current path.")

try:
	from function.animation import animTools
except ImportError:
	animTools = None


# List of non-user-defined attributes to include in the swap (e.g., system or proxy attributes)
EXTRA_ATTRS = ['FK_IK']

# Debug Settings
DEBUG_MODE = False
TARGET_DEBUG_CTRL = ''


def get_custom_attr_dict(node, extra_attrs=None):
	"""
	Scan and return all user-defined keyable attributes on the given transform AND its shape nodes.
	Also includes attributes specified in EXTRA_ATTRS.
	Returns:
		dict: { 'attributeShortName': ('node_name', 'attributeShortName') }
	"""
	attr_dict = {}
	
	# 1. Scan Transform Node
	t_attrs = mc.listAttr(node, userDefined=True, keyable=True) or []
	for attr in t_attrs:
		attr_dict[attr] = (node, attr)
	
	# 2. Add Extra Attributes (if they exist on the transform node)
	if extra_attrs:
		for attr in extra_attrs:
			if mc.attributeQuery(attr, node=node, exists=True):
				attr_dict[attr] = (node, attr)
		
	# 3. Scan Shape Nodes (Use short names to avoid pipe '|' parsing issues in setKeyframe)
	shapes = mc.listRelatives(node, shapes=True, fullPath=False) or []
	for shape in shapes:
		s_attrs = mc.listAttr(shape, userDefined=True, keyable=True) or []
		for attr in s_attrs:
			attr_dict[attr] = (shape, attr)
	
	return attr_dict

def mirror_animation_core(json_path):
	"""
	Core logic to validate data, mirror transforms using Studio Library, 
	and safely swap/restore custom animCurves using a Pre-Backup Snapshot System 
	with Hierarchical Debug Logging.
	"""
	if not json_path or not os.path.isfile(json_path):
		mc.error(f"Invalid or missing JSON file: {json_path}")

	sel = mc.ls(selection=True, type='transform') or []

	if not sel:
		mc.error("Please select one or more controllers before applying.")

	with open(json_path, "r") as f:
		table_data = json.load(f)
	
	objects_data = table_data.get("objects", {})
	
	matched_controllers = []
	for obj in sel:
		short_name = obj.split(':')[-1]
		if short_name in objects_data or obj in objects_data:
			matched_controllers.append(obj)
			
	metadata = table_data.get("metadata", {})
	left_str = metadata.get("left", "L_").replace('*', '')
	right_str = metadata.get("right", "R_").replace('*', '')
			
	if not matched_controllers:
		mc.error("Selection mismatch: None of the selected controllers exist in the provided Mirror Table.")

	mc.undoInfo(openChunk=True)
	dummy_backup = "nmMirrorBackupLoc_TEMP"
	
	try:
		if mc.objExists(dummy_backup):
			mc.delete(dummy_backup)
		dummy_backup = mc.spaceLocator(name=dummy_backup)[0]

		processed = set()
		pairs = []
		centers = []
		backup_list = []
		attr_states = {}
		backup_index = 0

		# ==============================================================
		# PASS 1: จัดกลุ่ม Controllers และเตรียมรายการ Backup
		# ==============================================================
		for obj_name in matched_controllers:
			obj_long = mc.ls(obj_name, long=True)
			if not obj_long: continue
			obj_long = obj_long[0]

			if obj_long in processed: continue

			opposite_obj = None
			if left_str and left_str in obj_name:
				opposite_obj = obj_name.replace(left_str, right_str)
			elif right_str and right_str in obj_name:
				opposite_obj = obj_name.replace(right_str, left_str)

			if opposite_obj and mc.objExists(opposite_obj):
				opp_long = mc.ls(opposite_obj, long=True)[0]
				pairs.append((obj_long, opp_long))
				backup_list.append((obj_long, obj_name))
				backup_list.append((opp_long, opposite_obj))
				processed.add(obj_long)
				processed.add(opp_long)
			else:
				centers.append(obj_long)
				backup_list.append((obj_long, obj_name))
				processed.add(obj_long)

		# ==============================================================
		# PASS 2: ดึงคีย์เฟรมและค่าจาก Custom Attributes ไปฝาก Backup
		# ==============================================================
		for node_long, base_name in backup_list:
			short_name = base_name.split(':')[-1]
			data = objects_data.get(short_name, objects_data.get(base_name, {}))
			attr_dict = get_custom_attr_dict(node_long, extra_attrs=EXTRA_ATTRS)

			for attr in attr_dict:
				if attr in data and attr not in EXTRA_ATTRS:
					continue

				node_name, attr_name = attr_dict[attr]
				plug = f"{node_name}.{attr_name}"
				
				l_curves = mc.listConnections(plug, type="animCurve", source=True, destination=False) or []
				
				# เก็บจำนวน Keyframe ของแต่ละ Attribute เพื่อนำไปใช้ Report
				key_count = mc.keyframe(node_name, attribute=attr_name, query=True, keyframeCount=True) or 0
				
				if l_curves:
					b_attr = f"bck_{backup_index}"
					mc.addAttr(dummy_backup, ln=b_attr, keyable=True)
					mc.copyKey(node_name, attribute=attr_name)
					mc.pasteKey(dummy_backup, attribute=b_attr, option="replaceCompletely")
					
					attr_states[plug] = {'type': 'anim', 'backup_attr': b_attr, 'curve': l_curves[0], 'keys': key_count}
					backup_index += 1
				else:
					val = mc.getAttr(plug)
					attr_states[plug] = {'type': 'static', 'value': val, 'keys': 0}

		# ==============================================================
		# PASS 3: ให้ Studio Library ทำงานหลัก
		# ==============================================================
		mt = MirrorTable.fromPath(json_path)
		mt.load(objects=sel,
				option=MirrorOption.Swap,
				keysOption=KeysOption.All,
				namespaces=[])
		print("\n[Mirror] Transforms mirrored using Studio Library.")

		# ==============================================================
		# PASS 4: สลับคีย์กลับที่เดิม (Swap) พร้อม Debug Logger
		# ==============================================================
		processed_curves = set()

		# 4.1: Restore ศูนย์กลาง (Center Controllers)
		for c_obj in centers:
			print(f"\n[Debug] ==========================================================")
			print(f"[Debug] CENTER CTRL: {c_obj} (Restore Only)")
			attr_dict = get_custom_attr_dict(c_obj, extra_attrs=EXTRA_ATTRS)
			for attr in attr_dict:
				node_name, attr_name = attr_dict[attr]
				plug = f"{node_name}.{attr_name}"
				state = attr_states.get(plug)
				
				if not state: continue
				
				c_keys = state.get('keys', 0)
				print(f"[Debug]   |-- Attr: {attr} [Keys: {c_keys}]")

				if state['type'] == 'anim':
					curve = state['curve']
					if curve in processed_curves: 
						print(f"[Debug]   |   `-- Action: SKIPPED (ป้องกัน Proxy Double Process)")
						continue
					processed_curves.add(curve)

					mc.cutKey(node_name, attribute=attr_name, clear=True)
					mc.copyKey(dummy_backup, attribute=state['backup_attr'])
					mc.pasteKey(node_name, attribute=attr_name, option="replaceCompletely")
					print(f"[Debug]   |   `-- Action: RESTORE (กู้คืนคีย์เฟรมจาก Backup)")
				else:
					try: mc.setAttr(plug, state['value'])
					except: pass
					print(f"[Debug]   |   `-- Action: STATIC restore (คืนค่าคงที่)")

			# --- [DEBUG BREAK] หยุดการทำงานทันทีหากเจอเป้าหมาย (Center) ---
			if DEBUG_MODE and c_obj == TARGET_DEBUG_CTRL:
				mc.error(f"[Debug Break] Processed Center Ctrl: {TARGET_DEBUG_CTRL}. Stopping now.")

		# 4.2: Swap ซ้ายและขวา (Paired Controllers)
		for l_obj, r_obj in pairs:
			print(f"\n[Debug] ==========================================================")
			print(f"[Debug] PAIR: {l_obj}  <-->  {r_obj}")
			
			attr_dict_l = get_custom_attr_dict(l_obj, extra_attrs=EXTRA_ATTRS)
			attr_dict_r = get_custom_attr_dict(r_obj, extra_attrs=EXTRA_ATTRS)
			common_attrs = set(attr_dict_l.keys()).intersection(set(attr_dict_r.keys()))

			for attr in common_attrs:
				l_node, l_attr = attr_dict_l[attr]
				r_node, r_attr = attr_dict_r[attr]
				l_plug = f"{l_node}.{l_attr}"
				r_plug = f"{r_node}.{r_attr}"

				l_state = attr_states.get(l_plug)
				r_state = attr_states.get(r_plug)
				
				if not l_state or not r_state: continue

				l_keys = l_state.get('keys', 0)
				r_keys = r_state.get('keys', 0)

				# >>> แสดงชื่อ Attribute และจำนวนคีย์ของ L และ R <<<
				print(f"[Debug]   |-- Attr: {attr} | Keys -> [L: {l_keys}, R: {r_keys}]")

				l_curve = l_state.get('curve')
				r_curve = r_state.get('curve')

				if (l_curve and l_curve in processed_curves) or (r_curve and r_curve in processed_curves):
					print(f"[Debug]   |   `-- Action: SKIPPED (ป้องกัน Double Swap บน Proxy/Shared Curve)")
					continue
					
				if l_curve: processed_curves.add(l_curve)
				if r_curve: processed_curves.add(r_curve)

				# >>> ระบุ Action ตามจำนวนคีย์อย่างชัดเจน <<<
				if not l_curve and not r_curve:
					print(f"[Debug]   |   `-- Action: STATIC swap: ไม่มีคีย์ทั้งคู่ สลับแค่ค่าตัวเลข")
				elif l_curve and r_curve:
					print(f"[Debug]   |   `-- Action: BOTH sides animated: มีคีย์ทั้งคู่ ใช้ลอจิกดึงกราฟจาก Dummy สลับกัน")
				elif r_curve and not l_curve:
					print(f"[Debug]   |   `-- Action: RIGHT side only: มีคีย์แค่ฝั่งขวา ย้ายไปซ้ายแล้วล้างฝั่งขวา")
				elif l_curve and not r_curve:
					print(f"[Debug]   |   `-- Action: LEFT side only: มีคีย์แค่ฝั่งซ้าย ย้ายไปขวาแล้วล้างฝั่งซ้าย")

				mc.cutKey(l_node, attribute=l_attr, clear=True)
				mc.cutKey(r_node, attribute=r_attr, clear=True)

				# วางข้อมูลจากฝั่งขวา -> ลงซ้าย
				if r_state['type'] == 'anim':
					mc.copyKey(dummy_backup, attribute=r_state['backup_attr'])
					mc.pasteKey(l_node, attribute=l_attr, option="replaceCompletely")
				else:
					try: mc.setAttr(l_plug, r_state['value'])
					except: pass

				# วางข้อมูลจากฝั่งซ้าย -> ลงขวา
				if l_state['type'] == 'anim':
					mc.copyKey(dummy_backup, attribute=l_state['backup_attr'])
					mc.pasteKey(r_node, attribute=r_attr, option="replaceCompletely")
				else:
					try: mc.setAttr(r_plug, l_state['value'])
					except: pass

			# --- [DEBUG BREAK] หยุดการทำงานทันทีหากเจอเป้าหมาย (Pair) ---
			if DEBUG_MODE and (l_obj == TARGET_DEBUG_CTRL or r_obj == TARGET_DEBUG_CTRL):
				mc.error(f"[Debug Break] Processed Pair Ctrl: {TARGET_DEBUG_CTRL}. Stopping now.")

		print("\nMirror Animation Process Completed Successfully.")
		
	except Exception as e:
		mc.error(f"Mirror Operation Failed: {str(e)}")
		
	finally:
		if mc.objExists(dummy_backup):
			mc.delete(dummy_backup)
		mc.undoInfo(closeChunk=True)


class MirrorAnimUI(object):
	"""Simple Maya Cmds UI for the Mirror Animation Tool."""
	
	def __init__(self):
		self.window_name = "nmMirrorAnimWindow"
		self.option_var_name = "nmMirrorAnim_lastJsonPath"
		self.build_ui()

	def build_ui(self):
		if mc.window(self.window_name, exists=True):
			mc.deleteUI(self.window_name)

		# Check for saved path in optionVar
		last_path = ""
		if mc.optionVar(exists=self.option_var_name):
			last_path = mc.optionVar(query=self.option_var_name)

		self.window = mc.window(self.window_name, title="Anim Mirror Tool v0.87", widthHeight=(450, 180), sizeable=True)
		mc.columnLayout(adjustableColumn=True, rowSpacing=10, columnAttach=('both', 15))

		mc.separator(height=10, style="none")
		mc.text(label="Studio Library Mirror Table (.json)", align="left", font="boldLabelFont")

		self.path_field = mc.textFieldButtonGrp(
			label="File Path: ",
			text=last_path, 
			buttonLabel="Browse...",
			columnWidth3=[60, 290, 70],
			buttonCommand=self.browse_file
		)

		mc.separator(height=5, style="in")

		mc.button(
			label="Select All Controllers", 
			height=30, 
			backgroundColor=[0.3, 0.3, 0.3], 
			command=self.select_all_ctrl
		)

		mc.button(
			label="APPLY MIRROR (Swap)", 
			height=40, 
			backgroundColor=[0.2, 0.2, 0.2], 
			command=self.apply_mirror
		)

		mc.showWindow(self.window)

	def browse_file(self):
		# Try to get start directory from current path if it exists
		current_path = mc.textFieldButtonGrp(self.path_field, query=True, text=True)
		start_dir = os.path.dirname(current_path) if current_path and os.path.isdir(os.path.dirname(current_path)) else None

		file_path = mc.fileDialog2(
			fileFilter="JSON Files (*.json)", 
			dialogStyle=2, 
			fileMode=1, 
			caption="Select Mirror Table",
			startingDirectory=start_dir
		)
		if file_path:
			selected_path = file_path[0]
			mc.textFieldButtonGrp(self.path_field, edit=True, text=selected_path)
			# Save to optionVar immediately after browsing
			mc.optionVar(sv=(self.option_var_name, selected_path))

	def select_all_ctrl(self, *args):
		if animTools:
			animTools.selectAllCtrl()
		else:
			mc.warning("animTools module not found.")

	def apply_mirror(self, *args):
		path = mc.textFieldButtonGrp(self.path_field, query=True, text=True)
		if not path or not os.path.isfile(path):
			mc.error("Please select a valid Studio Library JSON file first.")
		
		# --- [NEW] Selection Check before applying ---
		sel = mc.ls(selection=True, type='transform') or []
		if not sel:
			mc.error("No controllers selected! Please select one or more controllers (transform nodes) to mirror.")

		# Save path to optionVar for persistence
		mc.optionVar(sv=(self.option_var_name, path))

		mirror_animation_core(path)

# # ==========================================
# # Run the UI
# # ==========================================
# MirrorAnimUI()