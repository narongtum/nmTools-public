from function.framework.reloadWrapper import reloadWrapper as reload


'''
from function.rigging.readWriteCtrlSizeData import flipController as fip
reload(fip)
'''
import maya.cmds as mc
from function.rigging.readWriteCtrlSizeData import writeCtrlData as wcd
reload(wcd)


from function.rigging.util import misc
reload(misc)

from function.rigging.autoRig.base import core
reload(core)

import maya.OpenMaya as om



def run():
	ui = buildUI()
	ui.show()



class buildUI():
	def __init__(self):
		print ('initiation building UI')
		self.widt = 750
		self.ui = 'TAI shapeTools'
		self.win = '%sWin' % self.ui

	def show(self):

		if mc.window(self.win, exists=True):
			mc.deleteUI(self.win)
		  
		mc.window( self.win, width = self.widt , widthHeight=(200, 140) )
		mc.columnLayout( adjustableColumn = True )
		mc.button( label = 'Copy ControllerShape ' , command = self.copyCtrlShape , ann = "Select source and destination.")
		mc.button( label = 'Flip ControllerX'   	,	command = self.flipCtrlShapeX , ann = "click object and click the button")
		mc.button( label = 'Flip ControllerY'   	,	command = self.flipCtrlShapeY , ann = "click object and click the button")
		mc.button( label = 'Flip ControllerZ'   	,	command = self.flipCtrlShapeZ , ann = "click object and click the button")
		mc.button( label = 'Copy to Opposite'   	,	command = self.copyShapeToOpposite , ann = "click object and click the button")
		mc.separator( height = 10, style = 'shelf' )
		mc.button( label = 'Mirror L -> R (Selected)' , command = self.mirrorSelectedLtoR , bgc = (0.2, 0.4, 0.6) , ann = "Mirror selected Left controller shape to Right in World Space.")
		mc.button( label = 'Mirror ALL (Scan Scene L -> R)' , command = self.mirrorAllSceneLtoR , bgc = (0.15, 0.35, 0.55) , ann = "Scan scene for all Left controllers and mirror to Right in World Space.")



		mc.showWindow()





	def flipCtrlShapeX( self , sel , axis = [ 1, -1, -1 ] ):
		sel = mc.ls(sl=True)
		print ('flip axis is %s' %axis)
		shapes = wcd.getShape(sel[0])	
		newShapes = []

		for i, each in enumerate(shapes["points"]):
			shapes["points"][i] = [each[0] * axis[0], each[1] * axis[1], each[2] * axis[2]]
		newShapes.append(shapes)

		mc.curve( sel , replace = True,p=newShapes[0]["points"], k=newShapes[0]["knots"], d=newShapes[0]["degree"], per=bool(newShapes[0]["form"]) )




	# flip controller

	def flipCtrlShapeY( self , sel , axis = [-1, -1, 1] ):
		sel = mc.ls(sl=True)
		print ('flip axis is %s' %axis)
		shapes = wcd.getShape(sel[0])	
		newShapes = []


		for i, each in enumerate(shapes["points"]):
			shapes["points"][i] = [each[0] * axis[0], each[1] * axis[1], each[2] * axis[2]]
		newShapes.append(shapes)
		# this is mean
		# for each number of joint [i] 1,2,3,4,5,..... number of point
		# for each is value ( -0.12 3.93, 12.53 )
		# that mean make this multiply with -1
		# and append that to new shape

		# specifiy the shape that u went to make
		# wcd.setShape(sel[0], newShapes)

		mc.curve( sel , replace = True,p=newShapes[0]["points"], k=newShapes[0]["knots"], d=newShapes[0]["degree"], per=bool(newShapes[0]["form"]) )


	

	def flipCtrlShapeZ( self , sel , axis = [ -1, 1, -1 ] ):
		sel = mc.ls(sl=True)
		print ('flip axis is %s' %axis)
		shapes = wcd.getShape(sel[0])	
		newShapes = []


		for i, each in enumerate(shapes["points"]):
			shapes["points"][i] = [each[0] * axis[0], each[1] * axis[1], each[2] * axis[2]]
		newShapes.append(shapes)

		# wcd.setShape(sel[0], newShapes)

		# try to use cleaner metod
		mc.curve( sel , replace = True,p=newShapes[0]["points"], k=newShapes[0]["knots"], d=newShapes[0]["degree"], per=bool(newShapes[0]["form"]) )



	# copy controller
	def copyCtrlShape(self,sel = None):
		sel = mc.ls(sl=True)
		print ('##### copyCtrlShape #####')
		try:
			data = wcd.getShape(sel[0])	
			mc.curve( sel[1], replace = True,p=data["points"], k=data["knots"], d=data["degree"], per=bool(data["form"]) )
		except:
			print ('Error occured: Maybe you should delete curve history.')




	def copyShapeToOpposite(self, sel = None):
		#.... copy shape control
		sel = mc.ls(sl=True)[0]

		if sel:

			check = misc.check_name_style(sel)

			#... get another side
			opposite = sel.replace(check[1],check[2])
			try:
				data = wcd.getShape(sel)	
				mc.curve( opposite, replace = True,p=data["points"], k=data["knots"], d=data["degree"], per=bool(data["form"]) )
			except:
				print ('Error occured: Maybe you should delete curve history.')
		else:
			print('There are no selection.')

	# =========================================================================
	# NEW: World-Space Mirror UI Callbacks (Non-destructive addition)
	# =========================================================================
	def mirrorSelectedLtoR(self, *args):
		"""UI Callback: Mirrors selected Left controller(s) to Right in World Space."""
		return mirror_controllers_l_to_r(mode='selected')

	def mirrorAllSceneLtoR(self, *args):
		"""UI Callback: Scans scene for all Left controllers and mirrors to Right in World Space."""
		return mirror_controllers_l_to_r(mode='all')


# -----------------------------------------------------------------------------
# Standalone Helper Functions for World-Space Controller Mirroring
# -----------------------------------------------------------------------------

def get_world_matrix(node):
	"""Returns the 4x4 inclusive world matrix of a DAG node using OpenMaya."""
	sel = om.MSelectionList()
	sel.add(node)
	dag_path = om.MDagPath()
	sel.getDagPath(0, dag_path)
	return dag_path.inclusiveMatrix()


def get_opposite_ctrl_name(ctrl_name):
	"""
	Finds the opposite side name for a given controller name.
	Supports 'LFT' <-> 'RGT', 'L_' <-> 'R_', '_LFT' <-> '_RGT', 'Left' <-> 'Right'.
	"""
	try:
		check = misc.check_name_style(ctrl_name)
		side = check[1]
		reverse_side = check[2]
		if side and reverse_side:
			if not check[3]:  # Prefix style e.g. L_spineMain01_ctrl -> R_spineMain01_ctrl
				if ctrl_name.startswith(f"{side}_"):
					return f"{reverse_side}_{ctrl_name[len(side)+1:]}"
			else:  # Suffix style e.g. ankleLFT_ctrl -> ankleRGT_ctrl
				return ctrl_name.replace(side, reverse_side)
	except:
		pass

	# Fallback checks
	if 'LFT' in ctrl_name:
		return ctrl_name.replace('LFT', 'RGT')
	elif ctrl_name.startswith('L_'):
		return 'R_' + ctrl_name[2:]
	elif '_LFT' in ctrl_name:
		return ctrl_name.replace('_LFT', '_RGT')
	elif 'Left' in ctrl_name:
		return ctrl_name.replace('Left', 'Right')
	elif 'left' in ctrl_name:
		return ctrl_name.replace('left', 'right')
	return None


def mirror_ctrl_shape_world(src_ctrl, dst_ctrl=None, axis_mirror='X', assign_color=False):
	"""
	Mirrors the CV points of src_ctrl to dst_ctrl in 3D World Space across the specified axis plane (default X=0).
	Converts mirrored world points into dst_ctrl's local coordinate space and updates its curve shape.
	
	Args:
		src_ctrl (str): Source controller (e.g. Left controller).
		dst_ctrl (str, optional): Target controller (e.g. Right controller). If None, auto-detected.
		axis_mirror (str): Symmetry mirror axis ('X', 'Y', or 'Z'). Default is 'X'.
		assign_color (bool): If True, sets the target controller color to blue. Default is False (preserves original color).
	"""
	if not dst_ctrl:
		dst_ctrl = get_opposite_ctrl_name(src_ctrl)

	if not dst_ctrl or not mc.objExists(dst_ctrl):
		print(f"Target opposite controller not found for: {src_ctrl}")
		return False

	if not mc.objExists(src_ctrl):
		print(f"Source controller does not exist: {src_ctrl}")
		return False

	# 1. Get shape data from source
	try:
		data = wcd.getShape(src_ctrl)
	except Exception as err:
		print(f"Error getting shape from {src_ctrl}: {err}")
		return False

	if not data or "points" not in data:
		print(f"No valid curve shape data found on {src_ctrl}")
		return False

	# 2. Get World Matrices
	try:
		src_mat = get_world_matrix(src_ctrl)
		dst_mat = get_world_matrix(dst_ctrl)
		dst_mat_inv = dst_mat.inverse()
	except Exception as err:
		print(f"Error computing matrices for {src_ctrl} -> {dst_ctrl}: {err}")
		return False

	# 3. Transform CVs: Local(src) -> World -> Mirror -> Local(dst)
	mirrored_points = []
	for pt in data["points"]:
		p_local = om.MPoint(pt[0], pt[1], pt[2], 1.0)
		p_world = p_local * src_mat

		if axis_mirror.upper() == 'X':
			p_world_mirrored = om.MPoint(-p_world.x, p_world.y, p_world.z, 1.0)
		elif axis_mirror.upper() == 'Y':
			p_world_mirrored = om.MPoint(p_world.x, -p_world.y, p_world.z, 1.0)
		elif axis_mirror.upper() == 'Z':
			p_world_mirrored = om.MPoint(p_world.x, p_world.y, -p_world.z, 1.0)
		else:
			p_world_mirrored = om.MPoint(-p_world.x, p_world.y, p_world.z, 1.0)

		p_dst_local = p_world_mirrored * dst_mat_inv
		mirrored_points.append([p_dst_local.x, p_dst_local.y, p_dst_local.z])

	# 4. Replace curve shape on destination controller
	try:
		mc.curve(
			dst_ctrl,
			replace=True,
			p=mirrored_points,
			k=data["knots"],
			d=data["degree"],
			per=bool(data["form"])
		)
	except Exception as err:
		print(f"Error updating curve on {dst_ctrl}: {err}")
		return False

	# 5. Assign Right Side Color (Optional, default False to preserve original color)
	if assign_color:
		try:
			misc.setColor(dst_ctrl, 'blue')
		except:
			try:
				core.Dag(dst_ctrl).color = 'blue'
			except:
				pass

	print(f"Successfully mirrored shape (World Space): {src_ctrl} -> {dst_ctrl}")
	return True


def mirror_controllers_l_to_r(mode='selected', axis_mirror='X', assign_color=False):
	"""
	Main execution function to mirror Left controllers to Right counterparts.
	
	Args:
		mode (str): 'selected' to mirror currently selected Left controllers,
		            'all' to scan the entire scene for all Left controllers.
		axis_mirror (str): Mirror axis plane ('X', 'Y', or 'Z').
		assign_color (bool): If True, sets Right controllers to Blue.
	
	Returns:
		int: Number of successfully mirrored controllers.
	"""
	sel = mc.ls(sl=True) or []
	pairs = []

	if mode == 'selected' and sel:
		if len(sel) == 2 and not get_opposite_ctrl_name(sel[0]) == sel[1]:
			# Explicit pair selection (Source -> Target)
			pairs.append((sel[0], sel[1]))
		else:
			for obj in sel:
				opp = get_opposite_ctrl_name(obj)
				if opp and mc.objExists(opp):
					pairs.append((obj, opp))
				else:
					print(f"Opposite controller not found for: {obj}")
	else:
		# Scan Scene Mode: Find all Left controllers with curve shapes
		patterns = ['*LFT*_ctrl', 'L_*_ctrl', '*_LFT_ctrl', '*Left*_ctrl', '*left*_ctrl']
		candidate_nodes = []
		for pat in patterns:
			candidate_nodes.extend(mc.ls(pat, type='transform') or [])

		valid_left = []
		for node in set(candidate_nodes):
			shapes = mc.listRelatives(node, shapes=True, type='nurbsCurve') or []
			if shapes:
				valid_left.append(node)

		for obj in sorted(valid_left):
			opp = get_opposite_ctrl_name(obj)
			if opp and mc.objExists(opp):
				pairs.append((obj, opp))

	if not pairs:
		print("No valid Left -> Right controller pairs found to mirror.")
		return 0

	success_count = 0
	for src, dst in pairs:
		if mirror_ctrl_shape_world(src, dst, axis_mirror=axis_mirror, assign_color=assign_color):
			success_count += 1

	print(f"### Mirrored {success_count} controllers from Left to Right successfully! ###")
	return success_count







