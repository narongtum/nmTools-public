import maya.cmds as mc

def create_joints_along_tube(prefix="tube", step=1, orient_axis="xyz", secondary_axis="yup"):
	"""
	สร้าง Joint Chain วิ่งตามความยาวของท่อโดยอัตโนมัติ
	:param prefix: ชื่อนำหน้าของ Joint (เช่น 'tube', 'hose', 'cable')
	:param step: ข้ามทีละกี่ Edge Loop (ค่าเริ่มต้น 1 = วางทุกวง, 2 = วางวงเว้นวง)
	:param orient_axis: แกนหลักที่ชี้ไปยัง Joint ลูก (default: 'xyz')
	:param secondary_axis: แกนรองสำหรับ Up Vector (default: 'yup')
	"""
	# 1. ตรวจสอบ Selection
	sel_edges = mc.filterExpand(sm=32)  # 32 = Polygon Edge
	if not sel_edges:
		mc.warning("กรุณาเลือก Edge หรือ Edge Loop วงเริ่มต้นของท่ออย่างน้อย 1 เส้น")
		return

	# กรณีผู้ใช้เลือกเพียง Edge เดียว ให้ขยายเป็นทั้ง Loop อัตโนมัติ
	if len(sel_edges) == 1:
		mesh_node = sel_edges[0].split('.')[0]
		edge_id = int(sel_edges[0].split('[')[1].split(']')[0])
		loop_indices = mc.polySelect(mesh_node, edgeLoop=edge_id, noSelection=True) or []
		sel_edges = [f"{mesh_node}.e[{i}]" for i in loop_indices]

	# ดึง Vertices ของ Loop เริ่มต้น
	init_vtx = mc.polyListComponentConversion(sel_edges, toVertex=True)
	v_curr = set(mc.ls(init_vtx, flatten=True))

	if not v_curr:
		mc.warning("ไม่สามารถแปลง Edge เป็น Vertex ได้")
		return

	visited_faces = set()
	visited_vertices = set(v_curr)
	all_loop_centers = []

	# 2. วิ่ง Traverse ตามแนวหน้าตัดไปจนสุดท่อ
	while True:
		# คำนวณหา Centroid ของ Loop ปัจจุบัน
		x_sum = y_sum = z_sum = 0.0
		for v in v_curr:
			pos = mc.pointPosition(v, world=True)
			x_sum += pos[0]
			y_sum += pos[1]
			z_sum += pos[2]

		count = float(len(v_curr))
		centroid = [x_sum / count, y_sum / count, z_sum / count]
		all_loop_centers.append(centroid)

		# หาขอบ Edge ภายใน Loop เพื่อหา Face แถวถัดไป
		e_curr = mc.polyListComponentConversion(list(v_curr), toEdge=True, internal=True)
		adj_faces = set(mc.ls(mc.polyListComponentConversion(e_curr, toFace=True), flatten=True))

		# กรองเฉพาะ Face ที่ยังไม่เคยวิ่งผ่าน
		unvisited_faces = adj_faces - visited_faces
		if not unvisited_faces:
			break  # ถึงปลายท่อแล้ว

		visited_faces.update(unvisited_faces)

		# ดึง Vertices ของ Face แถวใหม่ แล้วตัด Vertices เดิมออก จะได้ Loop ถัดไป
		face_vtx = set(mc.ls(mc.polyListComponentConversion(list(unvisited_faces), toVertex=True), flatten=True))
		v_next = face_vtx - visited_vertices

		if not v_next:
			break

		visited_vertices.update(v_next)
		v_curr = v_next

	# 3. จัดการ Step (กรณีต้องการวาง Joint เว้นระยะ)
	selected_centers = []
	for idx, c in enumerate(all_loop_centers):
		if idx % step == 0 or idx == len(all_loop_centers) - 1:
			selected_centers.append(c)

	if not selected_centers:
		return

	# 4. สร้าง Joint Chain และ Orient กระดูก
	mc.select(clear=True)
	created_joints = []

	for i, pos in enumerate(selected_centers):
		jnt_name = f"{prefix}_{i+1:02d}_jnt"
		jnt = mc.joint(name=jnt_name, position=pos)
		created_joints.append(jnt)

	# Orient Joint จากโคนไปปลาย
	if len(created_joints) > 1:
		mc.joint(created_joints[0], edit=True, orientJoint=orient_axis,
				 secondaryAxisOrient=secondary_axis, children=True, zeroScaleOrient=True)
		# ตั้งค่า Tip Joint ตัวสุดท้ายให้เป็น 0
		mc.joint(created_joints[-1], edit=True, orientJoint='none', zeroScaleOrient=True)

	mc.select(created_joints[0])
	print(f"สร้าง Joint Chain สำเร็จ: ทั้งหมด {len(created_joints)} ตัว")
	return created_joints


# --- คำสั่งรัน ---
# วางทุก Loop:
create_joints_along_tube(prefix="hose", step=1)

# หรือถ้ารูปทรงท่อมี Edge ถี่เกินไป ให้วางแบบเว้นทุกๆ 2 หรือ 3 Loop:
# create_joints_along_tube(prefix="hose", step=2)