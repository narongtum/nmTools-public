"""
create_joints_raycast_mesh.py

Automated tool to create a centered Joint Chain along the internal centerline of a polygon mesh
(e.g. fins, snakes, tentacles, wings, ribbons, blades, straps, tongue, hair, or appendages)
using OpenMaya 2.0 raycasting.

Workflow:
1. Select 2 Edges in order:
   - Click 1: START edge (โคน / Head)
   - Click 2: END edge (ปลาย / Tail)
   (Alternatively, select an edge loop path, 2 vertices, or an entire edge loop).
2. Run create_joints_raycast_mesh() or launch the UI via show_ui().
3. The tool finds the connected edge/vertex path from Start to End, casts inward rays along
   surface normals to calculate the exact midpoint of thickness, and builds a connected, oriented joint chain.

Author: nmTools Rigging Suite
"""

import heapq
import maya.cmds as mc
import maya.api.OpenMaya as om


def get_ordered_vertices_from_edges(sel_edges):
	"""
	Sorts selected polygon edges into a continuous, ordered list of vertices from start to end.

	Args:
		sel_edges (list[str]): List of Maya edge component strings (e.g. ['pMesh.e[0]', 'pMesh.e[1]']).

	Returns:
		list[str]: Ordered list of vertex component strings.
	"""
	if not sel_edges:
		return []

	# Build adjacency dictionary from edges
	adj_map = {}
	all_vertices = set()

	for edge in sel_edges:
		vtxs = mc.polyListComponentConversion(edge, toVertex=True)
		flat_vtxs = mc.ls(vtxs, flatten=True)
		if len(flat_vtxs) == 2:
			v0, v1 = flat_vtxs[0], flat_vtxs[1]
			adj_map.setdefault(v0, set()).add(v1)
			adj_map.setdefault(v1, set()).add(v0)
			all_vertices.update([v0, v1])

	if not all_vertices:
		return []

	# Find start vertex: vertex with degree 1 (endpoint of open strip), or first vertex if closed loop
	start_vtx = None
	for vtx, neighbors in adj_map.items():
		if len(neighbors) == 1:
			start_vtx = vtx
			break

	if not start_vtx:
		start_vtx = list(all_vertices)[0]

	# Traverse adjacency graph
	ordered_vertices = [start_vtx]
	visited = {start_vtx}
	curr = start_vtx

	while len(visited) < len(all_vertices):
		neighbors = adj_map.get(curr, set())
		unvisited = neighbors - visited
		if not unvisited:
			break
		next_vtx = list(unvisited)[0]
		ordered_vertices.append(next_vtx)
		visited.add(next_vtx)
		curr = next_vtx

	return ordered_vertices


def get_ordered_vertices_from_edge_id_path(mesh_node, edge_ids):
	"""
	Converts an ordered list of edge IDs (from polySelect edgeLoopPath) into an ordered list of vertex names.

	Args:
		mesh_node (str): Name of the polygon mesh node.
		edge_ids (list[int]): Ordered edge indices along a contiguous path.

	Returns:
		list[str]: Ordered list of vertex component strings from start to end.
	"""
	if not edge_ids:
		return []

	if len(edge_ids) == 1:
		vtxs = mc.ls(mc.polyListComponentConversion(f"{mesh_node}.e[{edge_ids[0]}]", toVertex=True), flatten=True)
		return vtxs

	edge_vtx_pairs = []
	for eid in edge_ids:
		vtxs = mc.ls(mc.polyListComponentConversion(f"{mesh_node}.e[{eid}]", toVertex=True), flatten=True)
		edge_vtx_pairs.append(vtxs)

	# Find connection between first edge and second edge
	shared_first = set(edge_vtx_pairs[0]).intersection(set(edge_vtx_pairs[1]))
	if not shared_first:
		# Edges not contiguous, fallback to general edge adjacency
		edge_strings = [f"{mesh_node}.e[{eid}]" for eid in edge_ids]
		return get_ordered_vertices_from_edges(edge_strings)

	shared_v = list(shared_first)[0]
	first_v = [v for v in edge_vtx_pairs[0] if v != shared_v][0]

	ordered_vtx = [first_v, shared_v]
	curr_shared = shared_v

	for i in range(1, len(edge_vtx_pairs)):
		curr_pair = edge_vtx_pairs[i]
		next_v = [v for v in curr_pair if v != curr_shared]
		if next_v:
			ordered_vtx.append(next_v[0])
			curr_shared = next_v[0]

	return ordered_vtx


def find_shortest_vertex_path(mesh_node, start_vtx_name, end_vtx_name):
	"""
	Finds the shortest connected vertex path on mesh between start_vtx and end_vtx using Dijkstra.
	Works on ANY topology (triangles, quads, n-gons, poles).

	Args:
		mesh_node (str): Name of the polygon mesh.
		start_vtx_name (str): Starting vertex name (e.g. 'pMesh.vtx[10]').
		end_vtx_name (str): Ending vertex name (e.g. 'pMesh.vtx[85]').

	Returns:
		list[str]: Ordered list of vertex component strings from start_vtx to end_vtx.
	"""
	start_idx = int(start_vtx_name.split('[')[-1].split(']')[0])
	end_idx = int(end_vtx_name.split('[')[-1].split(']')[0])

	if start_idx == end_idx:
		return [start_vtx_name]

	# Build OpenMaya vertex iterator
	sel_list = om.MSelectionList()
	sel_list.add(mesh_node)
	dag_path = sel_list.getDagPath(0)
	vtx_iter = om.MItMeshVertex(dag_path)

	# Priority Queue Dijkstra
	distances = {start_idx: 0.0}
	prev = {}
	pq = [(0.0, start_idx)]

	while pq:
		curr_dist, curr_idx = heapq.heappop(pq)

		if curr_idx == end_idx:
			break

		if curr_dist > distances.get(curr_idx, float('inf')):
			continue

		vtx_iter.setIndex(curr_idx)
		curr_pos = vtx_iter.position(om.MSpace.kWorld)
		connected_vertices = vtx_iter.getConnectedVertices()

		for next_idx in connected_vertices:
			vtx_iter.setIndex(next_idx)
			next_pos = vtx_iter.position(om.MSpace.kWorld)
			edge_len = curr_pos.distanceTo(next_pos)

			new_dist = curr_dist + edge_len
			if new_dist < distances.get(next_idx, float('inf')):
				distances[next_idx] = new_dist
				prev[next_idx] = curr_idx
				heapq.heappush(pq, (new_dist, next_idx))

	# Reconstruct path
	if end_idx not in prev:
		return []

	path_indices = []
	curr = end_idx
	while curr is not None:
		path_indices.append(curr)
		curr = prev.get(curr)

	path_indices.reverse()
	return [f"{mesh_node}.vtx[{i}]" for i in path_indices]


def find_path_between_two_edges(mesh_node, edge1_str, edge2_str):
	"""
	Finds the contiguous vertex path between two selected edges (Head & Tail),
	STRICTLY respecting the direction from edge1_str (Start) to edge2_str (End).

	Args:
		mesh_node (str): Name of the polygon mesh.
		edge1_str (str): First edge component (Start / Head).
		edge2_str (str): Second edge component (End / Tail).

	Returns:
		list[str]: Ordered list of vertex component strings starting at edge1 and ending at edge2.
	"""
	e1_id = int(edge1_str.split('[')[-1].split(']')[0])
	e2_id = int(edge2_str.split('[')[-1].split(']')[0])

	v0_pair = mc.ls(mc.polyListComponentConversion(edge1_str, toVertex=True), flatten=True)
	v1_pair = mc.ls(mc.polyListComponentConversion(edge2_str, toVertex=True), flatten=True)

	ordered_vtx = None

	# 1. Try Maya Native polySelect edgeLoopPath
	try:
		loop_edge_ids = mc.polySelect(mesh_node, edgeLoopPath=(e1_id, e2_id), noSelection=True)
		if loop_edge_ids:
			ordered_vtx = get_ordered_vertices_from_edge_id_path(mesh_node, loop_edge_ids)
	except Exception:
		pass

	# 2. Try Maya Native polySelect edgeRingPath
	if not ordered_vtx:
		try:
			ring_edge_ids = mc.polySelect(mesh_node, edgeRingPath=(e1_id, e2_id), noSelection=True)
			if ring_edge_ids:
				ordered_vtx = get_ordered_vertices_from_edge_id_path(mesh_node, ring_edge_ids)
		except Exception:
			pass

	# 3. Fallback: Dijkstra shortest path between edge endpoint vertex pairs
	if not ordered_vtx:
		best_path = []
		min_length = float('inf')

		for v_start in v0_pair:
			for v_end in v1_pair:
				path = find_shortest_vertex_path(mesh_node, v_start, v_end)
				if path and len(path) > 0:
					# Calculate 3D euclidean distance along path
					total_len = 0.0
					for k in range(len(path) - 1):
						p1 = mc.pointPosition(path[k], world=True)
						p2 = mc.pointPosition(path[k + 1], world=True)
						dist = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5
						total_len += dist
					if total_len < min_length:
						min_length = total_len
						best_path = path

		ordered_vtx = best_path

	# 4. STRICT DIRECTION ENFORCEMENT: Ensure path strictly starts at edge1 and ends at edge2
	if ordered_vtx and len(ordered_vtx) >= 2:
		# If the start vertex belongs to edge2 (or end vertex belongs to edge1), reverse the path!
		if ordered_vtx[0] in v1_pair or ordered_vtx[-1] in v0_pair:
			ordered_vtx.reverse()
		else:
			# Additional 3D spatial verification
			p_first = mc.pointPosition(ordered_vtx[0], world=True)
			p_last = mc.pointPosition(ordered_vtx[-1], world=True)

			e1_positions = [mc.pointPosition(v, world=True) for v in v0_pair]
			e1_center = [sum(p[i] for p in e1_positions) / len(e1_positions) for i in range(3)]

			dist_first_to_e1 = sum((p_first[i] - e1_center[i]) ** 2 for i in range(3))
			dist_last_to_e1 = sum((p_last[i] - e1_center[i]) ** 2 for i in range(3))

			if dist_last_to_e1 < dist_first_to_e1:
				ordered_vtx.reverse()

	return ordered_vtx


def raycast_midpoint_from_vertex(mesh_node, vtx_name, fn_mesh):
	"""
	Casts an inward ray from a front vertex along its negative surface normal to find
	the opposing back surface, returning the exact midpoint.

	Args:
		mesh_node (str): Name of the polygon mesh.
		vtx_name (str): Vertex component name.
		fn_mesh (om.MFnMesh): OpenMaya 2.0 MFnMesh function set for the mesh.

	Returns:
		tuple: (midpoint [x, y, z], normal [nx, ny, nz], hit_distance float)
	"""
	pos = mc.pointPosition(vtx_name, world=True)
	front_point = om.MPoint(pos[0], pos[1], pos[2])

	# Query vertex normal in world space
	vtx_index = int(vtx_name.split('[')[-1].split(']')[0])
	try:
		normal = fn_mesh.getVertexNormal(vtx_index, True, om.MSpace.kWorld)
	except Exception:
		n_vals = mc.polyNormalPerVertex(vtx_name, query=True, normalXYZ=True)
		if n_vals and len(n_vals) >= 3:
			normal = om.MVector(n_vals[0], n_vals[1], n_vals[2]).normal()
		else:
			normal = om.MVector(0, 1, 0)

	# Ray direction: inward into mesh (-Normal)
	ray_dir = om.MVector(-normal.x, -normal.y, -normal.z).normal()

	# Offset ray origin slightly inward to prevent self-intersection
	offset_dist = 0.001
	ray_origin = om.MFloatPoint(
		front_point.x + ray_dir.x * offset_dist,
		front_point.y + ray_dir.y * offset_dist,
		front_point.z + ray_dir.z * offset_dist
	)
	ray_dir_float = om.MFloatVector(ray_dir.x, ray_dir.y, ray_dir.z)

	# 1. Inward raycast
	try:
		hit_info = fn_mesh.closestIntersection(
			ray_origin,
			ray_dir_float,
			om.MSpace.kWorld,
			maxParam=999999.0,
			testBothDirections=False
		)
		if hit_info:
			hit_point = hit_info[0]
			hit_dist = hit_info[1]
			midpoint = [
				(front_point.x + hit_point.x) * 0.5,
				(front_point.y + hit_point.y) * 0.5,
				(front_point.z + hit_point.z) * 0.5
			]
			return midpoint, [normal.x, normal.y, normal.z], hit_dist
	except Exception:
		pass

	# 2. Both directions fallback
	try:
		hit_info = fn_mesh.closestIntersection(
			om.MFloatPoint(front_point.x, front_point.y, front_point.z),
			ray_dir_float,
			om.MSpace.kWorld,
			maxParam=999999.0,
			testBothDirections=True
		)
		if hit_info:
			hit_point = hit_info[0]
			hit_dist = hit_info[1]
			if hit_dist > 0.001:
				midpoint = [
					(front_point.x + hit_point.x) * 0.5,
					(front_point.y + hit_point.y) * 0.5,
					(front_point.z + hit_point.z) * 0.5
				]
				return midpoint, [normal.x, normal.y, normal.z], hit_dist
	except Exception:
		pass

	# 3. Fallback to surface position if ray hits nothing
	return [pos[0], pos[1], pos[2]], [normal.x, normal.y, normal.z], 0.0


def create_joints_raycast_mesh(
	prefix="snk",
	step=1,
	count=None,
	orient_axis="xyz",
	secondary_axis="yup",
	create_curve=False,
	reverse_direction=False,
	auto_radius=True
):
	"""
	Creates a joint chain along the internal centerline of a mesh with front/back surfaces.

	Args:
		prefix (str): Prefix name for the generated joints (e.g. 'snk', 'fin', 'tongue', 'strap'). Defaults to 'snk'.
		step (int): Sampling step (e.g. 1 = every edge loop, 2 = every 2nd edge loop). Defaults to 1.
		count (int, optional): If specified, resamples the total path into exactly N evenly-spaced joints.
		orient_axis (str): Primary joint orientation axis ('xyz', 'yxz', etc.). Defaults to 'xyz'.
		secondary_axis (str): Secondary joint up axis ('yup', 'zup', etc.). Defaults to 'yup'.
		create_curve (bool): If True, also generates a NURBS curve passing through all midpoints. Defaults to False.
		reverse_direction (bool): If True, reverses the joint chain start-to-end direction. Defaults to False.
		auto_radius (bool): If True, dynamically scales joint radius based on mesh thickness. Defaults to True.

	Returns:
		list[str]: Names of generated joint nodes.
	"""
	# 1. Query selection strictly preserving the user's click order (orderedSelection)
	ordered_sel = mc.ls(orderedSelection=True, flatten=True) or []
	if not ordered_sel:
		ordered_sel = mc.ls(selection=True, flatten=True) or []

	if not ordered_sel:
		mc.error("[create_joints_raycast_mesh] Please select 2 Edges (Head & Tail) or an Edge Loop on the mesh.")
		return []

	# Filter edges and vertices in original selection order
	sel_edges = [item for item in ordered_sel if ".e[" in item]
	sel_vtxs = [item for item in ordered_sel if ".vtx[" in item]

	ordered_vtx = []
	mesh_node = ""

	if sel_edges:
		mesh_node = sel_edges[0].split('.')[0]

		# Case A: Exactly 2 edges selected (Click 1 = Start, Click 2 = End)
		if len(sel_edges) == 2:
			ordered_vtx = find_path_between_two_edges(mesh_node, sel_edges[0], sel_edges[1])

		# Case B: Exactly 1 edge selected (Expand full loop)
		elif len(sel_edges) == 1:
			edge_id = int(sel_edges[0].split('[')[-1].split(']')[0])
			loop_indices = mc.polySelect(mesh_node, edgeLoop=edge_id, noSelection=True) or []
			if loop_indices:
				ordered_vtx = get_ordered_vertices_from_edge_id_path(mesh_node, loop_indices)

		# Case C: Multiple edges selected (User selected a contiguous strip/range)
		if not ordered_vtx:
			ordered_vtx = get_ordered_vertices_from_edges(sel_edges)

	elif sel_vtxs:
		mesh_node = sel_vtxs[0].split('.')[0]
		if len(sel_vtxs) == 2:
			# 2 Vertices selected (Click 1 = Start, Click 2 = End)
			ordered_vtx = find_shortest_vertex_path(mesh_node, sel_vtxs[0], sel_vtxs[1])
		else:
			ordered_vtx = sel_vtxs
	else:
		mc.error("[create_joints_raycast_mesh] Please select polygon Edges or Vertices on the mesh.")
		return []

	if not ordered_vtx:
		mc.error("[create_joints_raycast_mesh] Failed to find a valid vertex path on the mesh.")
		return []

	if reverse_direction:
		ordered_vtx.reverse()

	# 2. Initialize OpenMaya MFnMesh for fast raycasting
	sel_list = om.MSelectionList()
	sel_list.add(mesh_node)
	dag_path = sel_list.getDagPath(0)
	fn_mesh = om.MFnMesh(dag_path)

	# 3. Raycast to find midpoints
	raw_midpoints = []
	raw_dists = []

	for vtx in ordered_vtx:
		mid_pos, normal, dist = raycast_midpoint_from_vertex(mesh_node, vtx, fn_mesh)
		raw_midpoints.append(mid_pos)
		raw_dists.append(dist)

	if not raw_midpoints:
		mc.error("[create_joints_raycast_mesh] No midpoint positions could be calculated.")
		return []

	# Smooth gap interpolation if any vertices missed raycast
	valid_dists = [d for d in raw_dists if d > 0.001]
	avg_dist = (sum(valid_dists) / float(len(valid_dists))) if valid_dists else 1.0

	for i, dist in enumerate(raw_dists):
		if dist <= 0.001:
			# Look for nearest valid neighbors to interpolate offset
			prev_d = raw_dists[i - 1] if i > 0 and raw_dists[i - 1] > 0.001 else avg_dist
			next_d = raw_dists[i + 1] if i < len(raw_dists) - 1 and raw_dists[i + 1] > 0.001 else avg_dist
			interp_d = (prev_d + next_d) * 0.5
			# Push inward from surface
			pos = mc.pointPosition(ordered_vtx[i], world=True)
			vtx_idx = int(ordered_vtx[i].split('[')[-1].split(']')[0])
			try:
				n = fn_mesh.getVertexNormal(vtx_idx, True, om.MSpace.kWorld)
				raw_midpoints[i] = [
					pos[0] - n.x * interp_d * 0.5,
					pos[1] - n.y * interp_d * 0.5,
					pos[2] - n.z * interp_d * 0.5
				]
			except Exception:
				pass

	# 4. Resample / Filter points based on count or step
	final_points = []
	if count and count > 1 and len(raw_midpoints) > 1:
		curve_degree = 3 if len(raw_midpoints) >= 4 else 1
		temp_crv = mc.curve(d=curve_degree, p=raw_midpoints)
		final_points = []
		for i in range(count):
			param = float(i) / float(count - 1)
			pos = mc.pointOnCurve(temp_crv, parameter=param, turnOnPercentage=True, position=True)
			final_points.append(pos)
		mc.delete(temp_crv)
	else:
		for idx, pt in enumerate(raw_midpoints):
			if idx % step == 0 or idx == len(raw_midpoints) - 1:
				final_points.append(pt)

	# 5. Create Joint Chain
	mc.select(clear=True)
	created_joints = []

	jnt_radius = max(0.1, round(avg_dist * 0.2, 2)) if auto_radius else 0.5

	for i, pos in enumerate(final_points):
		jnt_name = f"{prefix}_{i+1:02d}_jnt"
		jnt = mc.joint(name=jnt_name, position=pos, radius=jnt_radius)
		created_joints.append(jnt)

	# 6. Orient Joint Chain from root (0) to tip (-1)
	if len(created_joints) > 1:
		mc.joint(
			created_joints[0],
			edit=True,
			orientJoint=orient_axis,
			secondaryAxisOrient=secondary_axis,
			children=True,
			zeroScaleOrient=True
		)
		# Set tip joint orientation to none
		mc.joint(created_joints[-1], edit=True, orientJoint='none', zeroScaleOrient=True)

	# Optional: Create Centerline NURBS Curve
	if create_curve and len(final_points) >= 2:
		curve_degree = 3 if len(final_points) >= 4 else 1
		center_crv = mc.curve(name=f"{prefix}_center_crv", d=curve_degree, p=final_points)
		print(f"[create_joints_raycast_mesh] Created center curve: {center_crv}")

	mc.select(created_joints[0])
	print(f"\n[create_joints_raycast_mesh] Success: Created {len(created_joints)} joints along '{mesh_node}' centerline.")
	return created_joints


def show_ui():
	"""
	Displays an interactive Maya tool UI for creating centered joints between Head and Tail edges.
	"""
	window_name = "nmCreateJointsRaycastWin"

	if mc.window(window_name, exists=True):
		mc.deleteUI(window_name, window=True)

	win = mc.window(window_name, title="Mesh Centerline Joint Creator", widthHeight=(360, 420), resizeToFitChildren=True)
	mc.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 12))

	mc.separator(height=6, style="none")
	mc.text(label="Mesh Centerline Joint Tool", font="boldLabelFont", align="center")
	mc.text(
		label="Select Edge 1 (Start) -> Edge 2 (End) on mesh,\nthen click 'Create Centered Joints'.",
		align="center",
		font="obliqueLabelFont"
	)
	mc.separator(height=10, style="in")

	# Prefix
	prefix_fld = mc.textFieldGrp(label="Joint Prefix:", text="snk", columnWidth2=[100, 200])

	# Mode selection
	mode_rad = mc.radioButtonGrp(
		label="Distribution:",
		labelArray2=["By Count", "By Step"],
		numberOfRadioButtons=2,
		select=1,
		columnWidth3=[100, 100, 100]
	)

	count_slider = mc.intSliderGrp(label="Joint Count:", field=True, minValue=2, maxValue=100, fieldMinValue=2, fieldMaxValue=500, value=15, columnWidth3=[100, 50, 150])
	step_slider = mc.intSliderGrp(label="Loop Step:", field=True, minValue=1, maxValue=20, fieldMinValue=1, fieldMaxValue=50, value=1, columnWidth3=[100, 50, 150], enable=False)

	def on_mode_change(*args):
		is_count = mc.radioButtonGrp(mode_rad, query=True, select=True) == 1
		mc.intSliderGrp(count_slider, edit=True, enable=is_count)
		mc.intSliderGrp(step_slider, edit=True, enable=not is_count)

	mc.radioButtonGrp(mode_rad, edit=True, changeCommand=on_mode_change)

	mc.separator(height=6, style="in")

	# Orientation axes
	orient_menu = mc.optionMenuGrp(label="Primary Axis:", columnWidth2=[100, 200])
	for opt in ["xyz", "yxz", "zxy", "xzy", "yzx", "zyx"]:
		mc.menuItem(label=opt)
	mc.optionMenuGrp(orient_menu, edit=True, value="xyz")

	up_menu = mc.optionMenuGrp(label="Secondary Up:", columnWidth2=[100, 200])
	for opt in ["yup", "zup", "xup", "ydown", "zdown", "xdown"]:
		mc.menuItem(label=opt)
	mc.optionMenuGrp(up_menu, edit=True, value="yup")

	mc.separator(height=6, style="in")

	# Options Checkboxes
	crv_chk = mc.checkBox(label="Create Centerline NURBS Curve", value=False)
	rev_chk = mc.checkBox(label="Reverse Direction (Tail to Head)", value=False)
	rad_chk = mc.checkBox(label="Auto-size Joint Radius to Thickness", value=True)

	mc.separator(height=10, style="in")

	def on_build_clicked(*args):
		prefix_val = mc.textFieldGrp(prefix_fld, query=True, text=True).strip() or "snk"
		is_count_mode = mc.radioButtonGrp(mode_rad, query=True, select=True) == 1
		count_val = mc.intSliderGrp(count_slider, query=True, value=True) if is_count_mode else None
		step_val = mc.intSliderGrp(step_slider, query=True, value=True)
		orient_val = mc.optionMenuGrp(orient_menu, query=True, value=True)
		up_val = mc.optionMenuGrp(up_menu, query=True, value=True)
		crv_val = mc.checkBox(crv_chk, query=True, value=True)
		rev_val = mc.checkBox(rev_chk, query=True, value=True)
		rad_val = mc.checkBox(rad_chk, query=True, value=True)

		try:
			create_joints_raycast_mesh(
				prefix=prefix_val,
				step=step_val,
				count=count_val,
				orient_axis=orient_val,
				secondary_axis=up_val,
				create_curve=crv_val,
				reverse_direction=rev_val,
				auto_radius=rad_val
			)
		except Exception as err:
			mc.warning(f"Error creating joints: {err}")

	mc.button(
		label="Create Centered Joints",
		height=40,
		backgroundColor=[0.25, 0.5, 0.35],
		command=on_build_clicked
	)
	mc.separator(height=6, style="none")

	mc.showWindow(win)
	return win


if __name__ == "__main__":
	show_ui()


