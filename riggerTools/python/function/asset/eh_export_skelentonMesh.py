# -*- coding: utf-8 -*-
import maya.cmds as mc
import maya.mel as mel
import os
import sys

from function.pipeline import fileTools



'''
from function.asset import eh_export_skelentonMesh
import importlib
importlib.reload(eh_export_skelentonMesh)

eh_export_skelentonMesh.eh_export_skelentonMesh(
	rootJnt_name = 'root', 
	rootMesh_name = 'EM004_PhiTaKhon', 
	fileName = 'EM004_PhiTaKhon_Rig', 
	save_location = '')
'''







def eh_export_skelentonMesh(rootJnt_name='root', rootMesh_name='EM004_PhiTaKhon', fileName='EM004_PhiTaKhon_Rig', save_location=''):
	"""
	Exports a skeleton mesh (joints + geometries) to FBX format.
	
	Args:
		rootJnt_name (str): The name of the root joint of the skeleton.
		rootMesh_name (str): The name of the root mesh group/geometry.
		fileName (str): The name of the output FBX file (without .fbx).
		save_location (str): Directory where the fbx file will be saved.
							If None, False, or '', it will save to the same folder
							where the currently open Maya scene file is located.
	"""
	# 1. Validate targets exist in scene
	found_targets = []
	for name in [rootJnt_name, rootMesh_name]:
		if mc.objExists(name):
			found_targets.append(name)
		else:
			mc.error(f"Required export target '{name}' does not exist in the scene.")

	# 2. Determine save location
	if not save_location:
		scene_name = mc.file(query=True, sceneName=True)
		if not scene_name:
			mc.error("Scene is not saved. Please save the scene first or specify a valid 'save_location'.")
		save_location = os.path.dirname(scene_name)

	# Normalize folder path to use forward slashes and ensure it ends with '/'
	save_location = save_location.replace('\\', '/')
	if not save_location.endswith('/'):
		save_location += '/'

	# Strip .fbx suffix from fileName if present to avoid doubling it
	if fileName.lower().endswith('.fbx'):
		fileName = fileName[:-4]

	folder = f"{save_location}{fileName}.fbx"

	# 3. Handle hierarchy unparenting for clean export at root level
	parent_map = {}
	for node in found_targets:
		parent = mc.listRelatives(node, parent=True)
		if parent:
			parent_map[node] = parent[0]
			mc.parent(node, world=True)

	# 4. Perform selection & export
	mc.select(clear=True)
	mc.select(found_targets)

	try:
		# Ensure FBX plugin is loaded
		if not mc.pluginInfo("fbxmaya", query=True, loaded=True):
			mc.loadPlugin("fbxmaya")

		sys.stdout.write(f'# Preparing to write FBX file: {folder}...\n')
		
		# Disable input connections (ensures constraint/rig connections are baked cleanly)
		mel.eval('FBXExportInputConnections -v 0')
		
		# Configure FBX animation clip name to match fileName instead of clip001/Take 001
		mel.eval('FBXExportSplitAnimationIntoTakes -c')
		mel.eval('FBXExportDeleteOriginalTakeOnSplitAnimation -v true')
		start_time = mc.playbackOptions(query=True, minTime=True)
		end_time = mc.playbackOptions(query=True, maxTime=True)
		mel.eval(f'FBXExportSplitAnimationIntoTakes -v "{fileName}" {start_time} {end_time}')
		
		# Export selected nodes
		mel.eval(f'FBXExport -f "{folder}" -s')
		sys.stdout.write(f'# Skeleton mesh successfully exported to: {folder}\n')

	finally:
		# 5. Restore the original hierarchy
		for node, parent in parent_map.items():
			if mc.objExists(node) and mc.objExists(parent):
				mc.parent(node, parent)
		
		# Clear selection to leave the scene clean
		mc.select(clear=True)

	# 6. Open the container folder
	if os.path.exists(save_location):
		fileTools.openContainerFile(path=save_location)

	return folder
