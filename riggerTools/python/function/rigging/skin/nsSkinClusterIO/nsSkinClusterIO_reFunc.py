#... Warning... INSTALL NUMPY FIRST
#... This is approve for my pipeline

###########################
'''
# direct run
from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.skin.nsSkinClusterIO import nsSkinClusterIO_reFunc as skinIO
reload(skinIO)
skinIO.saveSkin()
skinIO.loadSkin()
'''

###########################

#Title: skinClusterIO.py
#Author: Noah Schnapp
#LinkedIn: https://www.linkedin.com/in/wnschnapp/
#22.11.Nov.17.Thu.15_nsSkinClusterIO\version







from function.framework.reloadWrapper import reloadWrapper as reload


###########################
####### IMPORTS ###########
###########################

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as OpenMayaAPI
import maya.api.OpenMayaAnim as OpenMayaAnimAPI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMaya as OpenMaya
import os
import imp
import numpy as np
import json
import time










####################################################################
#...CODE START

from function.pipeline import logger 
reload(logger)

class SkinIOLogger(logger.MayaLogger):
	LOGGER_NAME = "SkinIO"





SkinIOLogger.info('Run function at:{0}'.format(__name__))


class SkinClusterIO(object):

	def __init__(self):

		#...class init
		self.cDataIO 			    = DataIO()

		#...vars
		self.name                   = ''
		self.type                  	= 'skinCluster'
		self.weightsNonZero_Array   = []
		self.weights_Array          = []
		self.infMap_Array 			= []
		self.vertSplit_Array        = []
		self.inf_Array              = []
		self.skinningMethod         = 1
		self.normalizeWeights       = 1
		self.geometry               = None
		self.blendWeights           = []
		self.vtxCount               = 0
		self.envelope        		= 1
		self.skinningMethod         = 1
		self.useComponents         	= 0
		self.normalizeWeights       = 1
		self.deformUserNormals      = 1

		pass

	def get_mesh_components_from_tag_expression(self, skinPy, tag='*'):
		geo_types = ["mesh", "nurbsSurface", "nurbsCurve"]
		for t in geo_types:
			obj = skinPy.listConnections(et=True, t=t)
			if obj:
				geo = obj[0].getShape().name()
		# Get attr out of shape
		attr_out = cmds.deformableShape(geo, localShapeOutAttr=True)[0]
		# Get the output geometry data as MObject
		sel = OpenMaya.MSelectionList()
		sel.add(geo)
		dep = OpenMaya.MObject()
		sel.getDependNode(0, dep)
		fn_dep = OpenMaya.MFnDependencyNode(dep)
		plug = fn_dep.findPlug(attr_out, True)
		obj = plug.asMObject()
		# Use the MFnGeometryData class to query the components for a tag expression
		fn_geodata = OpenMaya.MFnGeometryData(obj)
		# Components MObject
		components = fn_geodata.resolveComponentTagExpression(tag)
		dagPath = OpenMaya.MDagPath.getAPathTo(dep)
		return dagPath, components
		
	def get_data(self, skinCluster):

		#...get PyNode skinCluster
		skinPy = pm.PyNode(skinCluster)

		#...Pre Maya 2022 or new compoent tag expression
		try:
			fnSet = OpenMaya.MFnSet(skinPy.__apimfn__().deformerSet())
			members = OpenMaya.MSelectionList()
			fnSet.getMembers(members, False)
			dagPath = OpenMaya.MDagPath()
			components = OpenMaya.MObject()
			members.getDagPath(0, dagPath, components)
		except:
			dagPath, components = self.get_mesh_components_from_tag_expression(skinPy)


		#...get mesh
		geometry = cmds.skinCluster(skinCluster, query = True, geometry = True)[0]

		#...get vtxID_Array
		vtxID_Array = list(range(0,len(cmds.ls('%s.vtx[*]'%geometry,fl=1))))

		#...get skin
		selList = OpenMayaAPI.MSelectionList()
		selList.add(mel.eval('findRelatedSkinCluster %s' % geometry))
		skinPath = selList.getDependNode(0)

		#...get mesh
		selList = OpenMayaAPI.MSelectionList()
		selList.add(geometry)
		meshPath = selList.getDagPath(0)

		#...get vtxs
		fnSkinCluster = OpenMayaAnimAPI.MFnSkinCluster(skinPath);
		fnVtxComp = OpenMayaAPI.MFnSingleIndexedComponent()
		vtxComponents = fnVtxComp.create( OpenMayaAPI.MFn.kMeshVertComponent )
		fnVtxComp.addElements(vtxID_Array);

		#...get weights/infs
		dWeights, infCount = fnSkinCluster.getWeights(meshPath, vtxComponents)
		# weights_Array = np.array(list(dWeights), dtype='float64')
		#... change this due to warning 
		weights_Array = np.array(list(dWeights), dtype='object')
		inf_Array = [dp.partialPathName() for dp in fnSkinCluster.influenceObjects()]
		
		#...convert to weightsNonZero_Array
		weightsNonZero_Array, infMap_Array, vertSplit_Array = self.compress_weightData(weights_Array, infCount)

		#...gatherBlendWeights
		blendWeights_mArray = OpenMaya.MDoubleArray()
		skinPy.__apimfn__().getBlendWeights(dagPath, components, blendWeights_mArray)
		
		#...set data to self vars
		self.name 					= skinCluster
		self.weightsNonZero_Array   = np.array(weightsNonZero_Array)
		self.infMap_Array       	= np.array(infMap_Array)
		self.vertSplit_Array       	= np.array(vertSplit_Array)
		self.inf_Array              = np.array(inf_Array)
		self.geometry               = geometry
		self.blendWeights           = np.array(blendWeights_mArray)
		self.vtxCount               = len(vertSplit_Array)-1

		#...get attrs
		self.envelope         		= cmds.getAttr(skinCluster + ".envelope")
		self.skinningMethod         = cmds.getAttr(skinCluster + ".skinningMethod")
		self.useComponents       	= cmds.getAttr(skinCluster + ".useComponents")
		self.normalizeWeights       = cmds.getAttr(skinCluster + ".normalizeWeights")
		self.deformUserNormals      = cmds.getAttr(skinCluster + ".deformUserNormals")
	
		return True

	def set_data(self, skinCluster):

		#...get PyNode skinCluster
		skinPy = pm.PyNode(skinCluster)

		#...Pre Maya 2022 or new compoent tag expression
		try:
			fnSet = OpenMaya.MFnSet(skinPy.__apimfn__().deformerSet())
			members = OpenMaya.MSelectionList()
			fnSet.getMembers(members, False)
			dagPath = OpenMaya.MDagPath()
			components = OpenMaya.MObject()
			members.getDagPath(0, dagPath, components)
		except:
			dagPath, components = self.get_mesh_components_from_tag_expression(skinPy)

		###################################################

		#...set infs
		influencePaths = OpenMaya.MDagPathArray()
		infCount = skinPy.__apimfn__().influenceObjects(influencePaths)
		influences_Array = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]

		#...change the order in set(i,i)
		influenceIndices = OpenMaya.MIntArray(infCount)
		[influenceIndices.set(i,i) for i in range(infCount)]

		###################################################

		#...construct mArrays from normal/numpy arrays
		infCount = len(influences_Array)
		weightCounter = 0
		weights_Array = []
		weights_mArray = OpenMaya.MDoubleArray()
		length = len(self.vertSplit_Array)
		for vtxId, splitStart in enumerate(self.vertSplit_Array):
			if vtxId < length-1:
				vertChunk_Array = [0]*infCount
				splitEnd = self.vertSplit_Array[vtxId+1]

				#...unpack data and replace zeros with nonzero weight vals
				for i in range(splitStart, splitEnd):
					infMap = self.infMap_Array[i]
					val = self.weightsNonZero_Array[i]
					vertChunk_Array[infMap] = val

				#...append to raw data array
				for vert in vertChunk_Array:
					weights_mArray.append(vert)

		blendWeights_mArray = OpenMaya.MDoubleArray()
		for i in self.blendWeights:
			blendWeights_mArray.append(i)
		
		###################################################
		#...set data
		# skinPy.setWeights(dagPath, components, influenceIndices, weights_mArray, False)
		SkinIOLogger.info('ERROR HERE WHY')
		skinPy.__apimfn__().setWeights(dagPath, components, influenceIndices, weights_mArray, False)
		SkinIOLogger.info('ERROR HERE WHY')
		#skinPy.setBlendWeights(dagPath, components, blendWeights_mArray)
		skinPy.__apimfn__().setBlendWeights(dagPath, components, blendWeights_mArray)
		###################################################
		#...set attrs of skinCluster
		cmds.setAttr('%s.envelope'%skinCluster, self.envelope)
		cmds.setAttr('%s.skinningMethod'%skinCluster, self.skinningMethod)
		cmds.setAttr('%s.useComponents'%skinCluster, self.useComponents)
		cmds.setAttr('%s.normalizeWeights'%skinCluster, self.normalizeWeights)
		cmds.setAttr('%s.deformUserNormals'%skinCluster, self.deformUserNormals)

		#...name
		cmds.rename(skinCluster, self.name)

		return True
	'''
	def save(self, node=None, dirpath=None):
		
		#...get selection
		if node == None:
			node = cmds.ls(sl=1)
			if node == None:
				print('ERROR: Select Something!')
				return False
			else:
				node = node[0]

		#...get skinCluster
		skinCluster = mel.eval('findRelatedSkinCluster ' + node)
		if not cmds.objExists(skinCluster):
			print('ERROR: Node has no skinCluster!')
			return False



		#...get dirpath
		if dirpath == None:
			startDir = cmds.workspace(q=True, rootDirectory=True)
			dirpath = cmds.fileDialog2(caption='Save Skinweights', dialogStyle=2, fileMode=3, startingDirectory=startDir, fileFilter='*.npy', okCaption = "Select")

		#...get filepath
		skinCluster = 'skinCluster_%s'%node
		filepath = '%s/%s.npy'%(dirpath, skinCluster)

		#...timeStart
		timeStart = time.time()

		#...get data
		self.get_data(skinCluster)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('GetData Elapsed: %s'%timeElapsed)

		#...construct data_array
		legend =            (   'legend',
								'weightsNonZero_Array', 
								'vertSplit_Array',
								'infMap_Array',

								'inf_Array',
								'geometry',
								'blendWeights', 
								'vtxCount',

								'name',
								'envelope',
								'skinningMethod',
								'useComponents',

								'normalizeWeights',
								'deformUserNormals',

								'type',
								)

		data =              [   legend,
								self.weightsNonZero_Array, 
								self.vertSplit_Array,
								self.infMap_Array,

								self.inf_Array,
								self.geometry,
								self.blendWeights, 
								self.vtxCount,

								self.name,
								self.envelope,
								self.skinningMethod,
								self.useComponents,

								self.normalizeWeights,
								self.deformUserNormals,

								self.type,
								]

		#...timeStart
		timeStart = time.time()

		#...write data 
		np.save(filepath, np.array(data, dtype=object))

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('SaveData Elapsed: %s'%timeElapsed)

		return True	

	def load(self, node=None, dirpath=None):

		#...get selection
		if node == None:
			node = cmds.ls(sl=1)
			if node == None:
				print('ERROR: Select Something!')
				return False
			else:
				node = node[0]



		#...get dirpath
		if dirpath == None:
			startDir = cmds.workspace(q=True, rootDirectory=True)
			dirpath = cmds.fileDialog2(caption='Load Skinweights', dialogStyle=2, fileMode=1, startingDirectory=startDir, fileFilter='*.npy', okCaption = "Select")

		#...get filepath
		skinCluster = 'skinCluster_%s'%node
		filepath = '%s/%s.npy'%(dirpath, skinCluster)

		#...check if skinCluster exists
		if not os.path.exists(filepath):
			print('ERROR: SkinCluster for node "%s" not found on disk!'%node)
			return False

		#...unbind current skinCluster
		skinCluster = mel.eval('findRelatedSkinCluster ' + node)
		if cmds.objExists(skinCluster):
			mel.eval('skinCluster -e  -ub ' + skinCluster)

		#...timeStart
		timeStart = time.time()

		#...read data
		data = np.load(filepath, allow_pickle=True)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('ReadData Elapsed: %s'%timeElapsed)

		#...get item data from numpy array
		self.legend_Array = self.cDataIO.get_legendArrayFromData(data)
		self.weightsNonZero_Array = self.cDataIO.get_dataItem(data, 'weightsNonZero_Array', self.legend_Array)
		self.infMap_Array = self.cDataIO.get_dataItem(data, 'infMap_Array', self.legend_Array)
		self.vertSplit_Array = self.cDataIO.get_dataItem(data, 'vertSplit_Array', self.legend_Array)
		self.inf_Array = self.cDataIO.get_dataItem(data, 'inf_Array', self.legend_Array)
		self.blendWeights = self.cDataIO.get_dataItem(data, 'blendWeights', self.legend_Array)
		self.vtxCount = self.cDataIO.get_dataItem(data, 'vtxCount', self.legend_Array)
		self.geometry = self.cDataIO.get_dataItem(data, 'geometry', self.legend_Array)
		self.name = self.cDataIO.get_dataItem(data, 'name', self.legend_Array)
		self.envelope = self.cDataIO.get_dataItem(data, 'envelope', self.legend_Array)
		self.skinningMethod = self.cDataIO.get_dataItem(data, 'skinningMethod', self.legend_Array)
		self.useComponents = self.cDataIO.get_dataItem(data, 'useComponents', self.legend_Array)
		self.normalizeWeights = self.cDataIO.get_dataItem(data, 'normalizeWeights', self.legend_Array)
		self.deformUserNormals = self.cDataIO.get_dataItem(data, 'deformUserNormals', self.legend_Array)

		#...bind skin
		for inf in self.inf_Array:
			if not cmds.objExists(inf):
				cmds.select(cl=True)
				cmds.joint(n=inf)
		skinCluster = 'skinCluster_%s'%node
		skinCluster = cmds.skinCluster(self.inf_Array, node, n=skinCluster, tsb = True)[0]

		#...timeStart
		timeStart = time.time()

		#...set data
		self.set_data(skinCluster)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('SetData Elapsed: %s'%timeElapsed)

		return True	
	'''
	###################################
	def compress_weightData(self, weights_Array, infCount):

		#...convert to weightsNonZero_Array
		weightsNonZero_Array = []
		infCounter = 0
		infMap_Chunk = []
		infMap_ChunkCount = 0
		vertSplit_Array = [infMap_ChunkCount]
		infMap_Array = []

		for w in weights_Array:
			if w != 0.0:
				weightsNonZero_Array.append(w)
				infMap_Chunk.append(infCounter)

			#...update inf counter
			infCounter += 1
			if infCounter ==  infCount:
				infCounter = 0
				
				#...update vertSplit_Array
				infMap_Array.extend(infMap_Chunk)
				infMap_ChunkCount = len(infMap_Chunk)+infMap_ChunkCount
				vertSplit_Array.append(infMap_ChunkCount)
				infMap_Chunk = []

		return weightsNonZero_Array, infMap_Array, vertSplit_Array

class DataIO(object):

	def __init__(self):

		pass

	@staticmethod
	def get_legendArrayFromData(data):

		return data[0]

	@staticmethod
	def get_dataItem(data, item, legend_Array=None):
		if item not in data[0]:
			print('ERROR: "%s" Not Found in data!'%item)
			return False
		#...no legend_Array
		if legend_Array is None:
			legend_Array = [key for key in data[0]]	
		#...with legend_Array
		return data[legend_Array.index(item)]

	@staticmethod
	def set_dataItems(data, itemData_Array):

		return data









from function.pipeline import fileTools as fileTools 
reload (fileTools)

def get_skin_paths():
	"""
	Analyzes current Maya scene path to determine pipeline status and skinData paths.
	Returns:
		(is_pipeline, rig_skin_dir, local_skin_dir)
	"""
	where = fileTools.whereAreMe()
	if not where:
		return False, None, None

	clean_path = os.path.normpath(where)
	parts = clean_path.split(os.sep)
	current_dir = os.path.dirname(clean_path)
	local_skin_dir = os.path.normpath(os.path.join(current_dir, 'Data', 'skinData'))

	# Check pipeline state
	state = fileTools.fileState()

	# Find asset root directory by inspecting path structure
	asset_dir = None

	# Case 1: If any segment is 'rig' (case-insensitive)
	for i, part in enumerate(parts[:-1]):
		if part.lower() == 'rig':
			asset_dir = os.sep.join(parts[:i])
			break

	# Case 2: If scene is in another department e.g. Model, Anim, Texture, FBX
	if not asset_dir:
		known_depts = ['model', 'anim', 'texture', 'fbx', 'conceptart', 'vfx']
		for i, part in enumerate(parts[:-1]):
			if part.lower() in known_depts:
				candidate = os.sep.join(parts[:i])
				if (os.path.exists(os.path.join(candidate, 'Rig')) or 
					os.path.exists(os.path.join(candidate, 'data.json')) or
					(i >= 2 and parts[i-2].lower() in ['content', 'sequence'])):
					asset_dir = candidate
					break

	# Case 3: Global hero / commit folder directly under asset (e.g. .../Asset/Commit/file.ma)
	if not asset_dir and len(parts) >= 3:
		parent_folder = parts[-2].lower()
		if parent_folder in ['commit', 'hero']:
			candidate = os.sep.join(parts[:-2])
			if (os.path.exists(os.path.join(candidate, 'Rig')) or 
				os.path.exists(os.path.join(candidate, 'data.json')) or
				state == 'global_hero'):
				asset_dir = candidate

	# Case 4: Traverse upwards looking for data.json (defining asset root in pipeline)
	if not asset_dir:
		cur = current_dir
		for _ in range(4):
			if os.path.exists(os.path.join(cur, 'data.json')):
				asset_dir = cur
				break
			parent = os.path.dirname(cur)
			if parent == cur:
				break
			cur = parent

	# If asset_dir found, we are in pipeline!
	if asset_dir:
		rig_skin_dir = os.path.normpath(os.path.join(asset_dir, 'Rig', 'Data', 'skinData'))
		return True, rig_skin_dir, local_skin_dir
	else:
		return False, None, local_skin_dir


def _processPath():
	is_pipeline, rig_skin_dir, local_skin_dir = get_skin_paths()
	if is_pipeline and rig_skin_dir:
		filePath = rig_skin_dir
		SkinIOLogger.info('Pipeline scene: target path is %s' % filePath)
	else:
		filePath = local_skin_dir
		SkinIOLogger.info('Non-pipeline scene: target path is local %s' % filePath)

	fileTools.currentFilePath(filePath)
	return filePath


def saveSkin():
	where = fileTools.whereAreMe()
	if not where:
		cmds.warning("Please save your Maya scene file before saving skinCluster data.")
		return False

	sel = cmds.ls(sl=True)
	if not sel:
		cmds.warning('Please select something!')
		return False

	node = sel[0]

	# get skinCluster
	skinCluster_name = mel.eval('findRelatedSkinCluster ' + node)
	if not cmds.objExists(skinCluster_name):
		cmds.warning('Node "%s" has no skinCluster!' % node)
		return False

	is_pipeline, rig_skin_dir, local_skin_dir = get_skin_paths()

	if is_pipeline and rig_skin_dir:
		dirpath = rig_skin_dir
		SkinIOLogger.info('Pipeline scene detected: saving skin to %s' % dirpath)
	else:
		dirpath = local_skin_dir
		SkinIOLogger.info('Non-pipeline scene detected: saving skin to local %s' % dirpath)

	# Ensure target directory exists (auto-create as confirmed by user)
	if not os.path.exists(dirpath):
		try:
			os.makedirs(dirpath)
			SkinIOLogger.info('Created directory: %s' % dirpath)
		except Exception as e:
			SkinIOLogger.error('Failed to create directory %s: %s' % (dirpath, e))

	# get file path
	skinCluster = '%s_skinCluster' % node
	filepath = os.path.normpath(os.path.join(dirpath, f"{skinCluster}.npy"))

	#... time start
	timeStart = time.time()

	SkinClusterExport = SkinClusterIO()
	SkinClusterExport.get_data(skinCluster_name)

	#... time end
	timeEnd = time.time()
	timeElapsed = timeEnd-timeStart
	print('Get data Elapsed: %s'%timeElapsed)

	#...construct data_array
	legend =            (   'legend',
							'weightsNonZero_Array', 
							'vertSplit_Array',
							'infMap_Array',

							'inf_Array',
							'geometry',
							'blendWeights', 
							'vtxCount',

							'name',
							'envelope',
							'skinningMethod',
							'useComponents',

							'normalizeWeights',
							'deformUserNormals',

							'type',
							)

	data =              [   legend,
							SkinClusterExport.weightsNonZero_Array, 
							SkinClusterExport.vertSplit_Array,
							SkinClusterExport.infMap_Array,

							SkinClusterExport.inf_Array,
							SkinClusterExport.geometry,
							SkinClusterExport.blendWeights, 
							SkinClusterExport.vtxCount,

							SkinClusterExport.name,
							SkinClusterExport.envelope,
							SkinClusterExport.skinningMethod,
							SkinClusterExport.useComponents,

							SkinClusterExport.normalizeWeights,
							SkinClusterExport.deformUserNormals,

							SkinClusterExport.type,
							]

	timeStart = time.time()

	np.save(filepath, np.array(data, dtype=object))
	cmds.select(deselect=True)
	timeEnd = time.time()
	timeElapsed = timeEnd-timeStart
	print('Saved data Elapsed: %s'%timeElapsed)

	print('File save at: ---> %s' %filepath)
	
	return True











def loadSkin():
	where = fileTools.whereAreMe()
	if not where:
		cmds.warning("Please save your Maya scene file before loading skinCluster data.")
		return False

	sel = cmds.ls(sl=True)
	if not sel:
		cmds.warning('Please select something!')
		return False

	node = sel[0]
	print('selected name is ---> %s' % node)

	skinCluster_name = '%s_skinCluster' % node
	file_name = f"{skinCluster_name}.npy"

	is_pipeline, rig_skin_dir, local_skin_dir = get_skin_paths()

	filepath = None

	if is_pipeline and rig_skin_dir:
		candidate = os.path.normpath(os.path.join(rig_skin_dir, file_name))
		SkinIOLogger.info('Checking Rig/Data/skinData: %s' % candidate)
		if os.path.exists(candidate):
			filepath = candidate
			SkinIOLogger.info('Found skinCluster in Rig/Data/skinData: %s' % filepath)
		else:
			# Fallback to local Data/skinData in current directory as confirmed by user
			local_candidate = os.path.normpath(os.path.join(local_skin_dir, file_name))
			SkinIOLogger.info('Not found in Rig/Data/skinData, checking local fallback: %s' % local_candidate)
			if os.path.exists(local_candidate):
				filepath = local_candidate
				SkinIOLogger.info('Found skinCluster in local fallback: %s' % filepath)
			else:
				msg = f'SkinCluster for node "{node}" not found in Rig/Data/skinData ({candidate}) nor local fallback ({local_candidate})!'
				cmds.warning(msg)
				print('ERROR: ' + msg)
				return False
	else:
		# Non-pipeline: check local_skin_dir
		local_candidate = os.path.normpath(os.path.join(local_skin_dir, file_name))
		if os.path.exists(local_candidate):
			filepath = local_candidate
			SkinIOLogger.info('Found skinCluster in: %s' % filepath)
		else:
			msg = f'SkinCluster for node "{node}" not found on disk: {local_candidate}'
			cmds.warning(msg)
			print('ERROR: ' + msg)
			return False

	#...unbind current skinCluster
	skinCluster = mel.eval('findRelatedSkinCluster ' + node)
	if cmds.objExists(skinCluster):
		mel.eval('skinCluster -e  -ub ' + skinCluster)

	#...timeStart
	timeStart = time.time()

	SkinIOLogger.info('This is filepath: {0}'.format(filepath))

	#...read data
	data = np.load(filepath, allow_pickle=True)



	SkinClusterImport = SkinClusterIO()

	#...get item data from numpy array
	legend_Array = SkinClusterImport.cDataIO.get_legendArrayFromData(data)
	weightsNonZero_Array = SkinClusterImport.cDataIO.get_dataItem(data, 'weightsNonZero_Array',legend_Array)
	infMap_Array = SkinClusterImport.cDataIO.get_dataItem(data, 'infMap_Array',legend_Array)
	vertSplit_Array = SkinClusterImport.cDataIO.get_dataItem(data, 'vertSplit_Array',legend_Array)
	inf_Array = SkinClusterImport.cDataIO.get_dataItem(data, 'inf_Array',legend_Array)
	blendWeights = SkinClusterImport.cDataIO.get_dataItem(data, 'blendWeights',legend_Array)
	vtxCount = SkinClusterImport.cDataIO.get_dataItem(data, 'vtxCount',legend_Array)
	geometry = SkinClusterImport.cDataIO.get_dataItem(data, 'geometry',legend_Array)
	name = SkinClusterImport.cDataIO.get_dataItem(data, 'name',legend_Array)
	envelope = SkinClusterImport.cDataIO.get_dataItem(data, 'envelope',legend_Array)
	skinningMethod = SkinClusterImport.cDataIO.get_dataItem(data, 'skinningMethod',legend_Array)
	useComponents = SkinClusterImport.cDataIO.get_dataItem(data, 'useComponents',legend_Array)
	normalizeWeights = SkinClusterImport.cDataIO.get_dataItem(data, 'normalizeWeights',legend_Array)
	deformUserNormals = SkinClusterImport.cDataIO.get_dataItem(data, 'deformUserNormals',legend_Array)

	#...bind skin
	for inf in inf_Array:
		if not cmds.objExists(inf):
			cmds.select(cl=True)
			cmds.joint(n=inf)
	skinCluster = '%s_skinCluster'%node
	skinCluster_name = cmds.skinCluster(inf_Array, node, n=skinCluster, tsb = True)[0]

	#...timeStart
	timeStart = time.time()

	#...set data
	# not work breakdown the code
	#SkinClusterImport.set_data(skinCluster)

	#...timeEnd

	#...get PyNode skinCluster


	#skinCluster_name = skinCluster
	skinPy = pm.PyNode(skinCluster_name)

	#...Pre Maya 2022 or new compoent tag expression
	try:
		fnSet = OpenMaya.MFnSet(skinPy.__apimfn__().deformerSet())
		members = OpenMaya.MSelectionList()
		fnSet.getMembers(members, False)
		dagPath = OpenMaya.MDagPath()
		components = OpenMaya.MObject()
		members.getDagPath(0, dagPath, components)
	except:
		dagPath, components = SkinClusterImport.get_mesh_components_from_tag_expression(skinPy)

	###################################################

	#...set infs
	influencePaths = OpenMaya.MDagPathArray()
	infCount = skinPy.__apimfn__().influenceObjects(influencePaths)
	influences_Array = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]

	#...change the order in set(i,i)
	influenceIndices = OpenMaya.MIntArray(infCount)
	[influenceIndices.set(i,i) for i in range(infCount)]

	###################################################

	#...construct mArrays from normal/numpy arrays
	infCount = len(influences_Array)
	weightCounter = 0
	weights_Array = []
	weights_mArray = OpenMaya.MDoubleArray()
	length = len(vertSplit_Array)
	for vtxId, splitStart in enumerate(vertSplit_Array):
		if vtxId < length-1:
			vertChunk_Array = [0]*infCount
			splitEnd = vertSplit_Array[vtxId+1]

			#...unpack data and replace zeros with nonzero weight vals
			for i in range(splitStart, splitEnd):
				infMap = infMap_Array[i]
				val = weightsNonZero_Array[i]
				vertChunk_Array[infMap] = val

			#...append to raw data array
			for vert in vertChunk_Array:
				weights_mArray.append(vert)

	blendWeights_mArray = OpenMaya.MDoubleArray()
	for i in blendWeights:
		blendWeights_mArray.append(i)

	###################################################
	#...set data
	# skinPy.setWeights(dagPath, components, influenceIndices, weights_mArray, False)

	skinPy.__apimfn__().setWeights(dagPath, components, influenceIndices, weights_mArray, False)
	#skinPy.setBlendWeights(dagPath, components, blendWeights_mArray)
	skinPy.__apimfn__().setBlendWeights(dagPath, components, blendWeights_mArray)
	###################################################
	#...set attrs of skinCluster
	cmds.setAttr('%s.envelope'%skinCluster_name, envelope)
	cmds.setAttr('%s.skinningMethod'%skinCluster_name, skinningMethod)
	cmds.setAttr('%s.useComponents'%skinCluster_name, useComponents)
	cmds.setAttr('%s.normalizeWeights'%skinCluster_name, normalizeWeights)
	cmds.setAttr('%s.deformUserNormals'%skinCluster_name, deformUserNormals)


	#...timeEnd
	timeEnd = time.time()
	timeElapsed = timeEnd-timeStart
	#...print time
	print('ReadData Elapsed: %s'%timeElapsed)

	#...name
	cmds.rename(skinCluster_name, name)
	print('File load at: ---> %s' %filepath)

	cmds.select(deselect=True)
	return True
	
'''	
saveSkin()
loadSkin()
'''