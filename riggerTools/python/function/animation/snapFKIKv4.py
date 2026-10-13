import maya.cmds as mc
import math



try:
	from importlib import reload
except ImportError:
	pass

from function.rigging.autoRig.base import core
from function.rigging.autoRig.base import rigTools
from function.animation import fkIkMatcherUI

def show_ui():
	"""Opens the modern PySide FK/IK Matcher UI Window."""
	reload(fkIkMatcherUI)
	return fkIkMatcherUI.show_ui()

def ikfkSnap():
	reload(fkIkMatcherUI)
	sel = mc.ls(sl=True) or []
	if not sel:
		mc.warning("Please select at least one stick controller.")
		return

	# Query current time
	curr_frame = int(mc.currentTime(query=True))

	# Resolve stick controllers from selection
	sticks = []
	for node in sel:
		if mc.attributeQuery('FK_IK', node=node, exists=True):
			sticks.append(node)
		elif mc.attributeQuery('stick', node=node, exists=True):
			con = mc.listConnections(f"{node}.stick")
			if con:
				sticks.append(con[0])
		elif 'stick' in node.lower() and mc.objExists(node) and mc.attributeQuery('FK_IK', node=node, exists=True):
			sticks.append(node)

	sticks = list(dict.fromkeys(sticks))
	if not sticks:
		mc.warning(f"No valid FK/IK stick controller found in selection: {sel}")
		return

	mc.undoInfo(openChunk=True)
	try:
		for stick in sticks:
			fkIkMatcherUI.FkIkMatcherEngine.snap_and_switch(stick, auto_key=True)
	finally:
		mc.undoInfo(closeChunk=True)

	print(f"// Switched & snapped: {sticks} at frame {curr_frame}")



def listCon( obj, attr = '' ):
	connector = mc.listConnections( '{0}.{1}'.format( obj, attr ) )[0]
	return connector

def getAttr( obj = '', attr = '' ):
	val = mc.getAttr( '{0}.{1}'.format( obj, attr )  )
	return val

def _snap( switch =  '' ):

	# get bJnt
	bJntUp = listCon( switch, 'bJntUp' )
	bJntMid = listCon( switch, 'bJntMid' )
	bJntLow = listCon( switch, 'bJntLow' )

	jntList = [ bJntUp, bJntMid, bJntLow ] # list

	# get fkCtrl
	fkUp = listCon( switch, 'fkUp' )
	fkMid = listCon( switch, 'fkMid' )
	fkLow = listCon( switch, 'fkLow' )
		
	fkCtrlList = [ fkUp, fkMid, fkLow ] # list

	# get IK Ctrl
	ikCtrl = listCon( switch, 'ikCtrl' )
	ikRootCtrl = listCon( switch, 'ikRootCtrl' )
	ikPov = listCon( switch, 'ikPov' )

	# get Special thing
	system = getAttr( switch, 'system' )
	side = getAttr( switch, 'side' )
	ikfkAttr =  switch + '.__FKIK__'
	ikValue = 1
	fkValue = 0
	pvAxisDict = { "arm": "-z", "leg": "z", "frontLeg": "-z", "backLeg": "z" }
	pvAxis = pvAxisDict[ str(system) ]

	if system == 'leg':

		bJntBall = listCon( switch, 'bJntBall' )
		jntList.extend( [bJntBall] )

		bJntToe = listCon( switch, 'bJntToe' )
		jntList.extend( [bJntToe] )

		fkBall = listCon( switch, 'fkBall' )
		fkCtrlList.extend( [fkBall] )
		# fkToe = listCon( switch, 'fkToe' )
		# fkCtrlList.extend( [fkToe] )
		offsetFoot = listCon( switch, 'offsetFoot' ) # offsetIKGrp

		footIK_ctrl = listCon( switch, 'footIKCtrl' )
		ikCtrl = footIK_ctrl

		# now you get extend list which you need

	elif system == 'birdLeg':
		bJntKunck = listCon( switch, 'bJntKunck' )
		jntList.extend( [bJntKunck] )
		fkKunck = listCon( switch, 'fkKunck' )
		fkCtrlList.extend( [fkKunck] )


	# ----------- FUNCTION Fkctrl to Ikctrl -----------
	if mc.getAttr(ikfkAttr) == ikValue: # fk --- [ snap to ] ---> ik

		for i, jnt in enumerate( jntList ):

			oldRO = mc.getAttr( '{0}.ro'.format( jnt ) )
			ctrl = fkCtrlList[i]

			if mc.objExists( ctrl ):
				ro = mc.getAttr( '{0}.ro'.format( ctrl ) )
				# assign the same RO as ctrl
				mc.setAttr( '{0}.ro'.format( jnt ), ro )

				# getAttr
				pos = mc.xform( jnt, q=True, t=True, ws=True)
				ori = mc.xform( jnt, q=True, ro=True, ws=True)
				mc.setAttr( '{0}.ro'.format( jnt ), oldRO )

				# setAttr
				mc.xform( ctrl, t=pos, ro=ori, ws=True, a=True )
		
		#mc.setAttr( ikfkAttr, fkValue) # big Change


	# ----------- FUNCTION Fkctrl to Ikctrl
	# HARD STUFF ------------------------------------------------------------------------------------
	elif mc.getAttr( ikfkAttr ) == fkValue:   # ik --- [ snap to ] ---> fk


		# if have to offset must continue on this

		if system == 'leg':

			ikNewPos = offsetFoot
			ikNewOri = offsetFoot
		else:
			ikNewPos = bJntLow
			ikNewOri = bJntLow

		# get RO
		ro = mc.getAttr( '{0}.ro'.format( ikCtrl ) )
		oldRO = mc.getAttr( '{0}.ro'.format( bJntLow ) )
		# set RO to match value at the ikCtrl
		mc.setAttr( '{0}.ro'.format( bJntLow ), ro )

		ikPos = mc.xform( ikNewPos, q=True, t=True, ws=True) #if alias in ["HindLeg"] else mc.xform(bJntLow, q=True, t=True, ws=True) 
		ikOri = mc.xform( ikNewOri, q=True, ro=True, ws=True) #if alias in ["HindLeg"] else mc.xform(bJntLow, q=True, ro=True, ws=True)
		pvPos = _findPV( bJntUp, bJntMid, bJntLow, pvAxis) 

		# setRO back
		mc.setAttr( '{0}.ro'.format( bJntLow ), oldRO )

		if system in ["leg", "frontLeg", "backLeg"]:

			footMX = mc.xform( bJntBall, q=True, m=True, ws=True)
			upVec = footMX[4:7]
			if side == 'LFT':
				upVec = vMultiply(upVec, -1)

			ballPos = mc.xform( bJntBall, q=True, t=True, ws=True)
			toePos = mc.xform( bJntToe, q=True, t=True, ws=True)

			aimVec = vPlus(ballPos, toePos, "-")
			#toeOri = vectorToAngle(aimVec, upVec=upVec, sideVec=None, aimAxis="z", upAxis="x", sideAxis=None)

		#get foot ik's orientation
		if system in ["backLeg"]:
			lowMX = mc.xform( bJntLow, q=True, m=True, ws=True)
			upVec = lowMX[4:7]
			if side == 'LFT':
				upVec = vMultiply(upVec, -1)
			lowPos = mc.xform( bJntLow, q=True, t=True, ws=True)
			aimVec = vPlus(lowPos, ballPos, "-")
			#footOri = vectorToAngle(aimVec, upVec=upVec, sideVec=None, aimAxis="z", upAxis="x", sideAxis=None)

		#mc.setAttr( ikfkAttr, ikValue) # big change
		
		# ---------- set attr ----------
		mc.xform( ikCtrl, t=ikPos, ro=ikOri, ws=True, a=True)
		mc.xform( ikPov, t=pvPos, ws=True, a=True)

		# if system in ["leg", "frontLeg", "backLeg"]:
		# 	mc.xform( ikCtrl, ro=ikOri, a=True, ws=True)
		# 	mc.xform( toeIkCtrl, ro=toeOri, a=True, ws=True)

			# if system in ["hindLeg"]:
				# print "I'm A DOG"
				#mc.xform( footIkCtrl, ro=footOri, a=True, ws=True)
			# else:
				#mc.xform( footIkCtrl, ro=(0, 0, 0), a=True, os=True)
				# print "I'm A Man"

		if system in ["frontLeg", "backLeg"]:
			if mc.objExists( kunckIKCtrl):
				mc.setAttr("{0}.r".format( kunckIKCtrl), 0, 0, 0, type="double3")

			if mc.objExists(toeSubIKCtrl):
				mc.setAttr("{0}.r".format( toeSubIKCtrl), 0, 0, 0, type="double3")


	return True


def _findPV( obj1, obj2, obj3, axis, scale=10): ### We found Pole Vector for you. NICE !!??
	neg = 1
	if axis[0] == '-':
		neg = -1
		axis = axis[1]

	row = {'x': 0, 'y': 1, 'z': 2}

	P = [mc.xform(obj, q=True, t=True, ws=True) for obj in [obj1, obj2, obj3]]

	V0 = vPlus(P[2], P[0], '-')
	V1 = vPlus(P[1], P[0], '-')
	w = vDot(V0, V1) / vDot(V0, V0)
	Vp = vMultiply(V0, w)
	Pp = vPlus(P[0], Vp, '+') 

	if 1 - vDot(V0, V1)/(vLength(V0)*vLength(V1)) < 0.0001:
		M16 = mc.xform(obj1, q=True, matrix=True, ws=True)
		M3x3 = []
		for i in range(3):
			M3x3.append([M16[i*4], M16[i*4+1], M16[i*4+2]])
		Vperp = vMultiply(M3x3[row[axis]], neg)
	else:
		Vperp = vPlus(P[1], Pp, '-')

	Vperp = vNormal(Vperp)
	Vperp = vMultiply(Vperp, scale)
	V0 = vMultiply(V0, 0.5)
	Pmid = vPlus(P[0], V0, '+')
	pvPos = vPlus(Pmid, Vperp, '+')

	return pvPos




# __  __          _______  __   __
#|  \/  |    /\  |__   __||  | |  |
#| \  / |   /  \    | |   |  |_|  |
#| |\/| |  / /\ \   | |   |   _   |
#| |  | | / ____ \  | |   |  | |  |
#|_|  |_|/_/    \_\ |_|   |__| |__|

def vPlus(vec1, vec2, operator):
	'''operator: +, -'''
	vec = []      
	for i in range(len(vec1)):
		if operator == '+':
			vec.append(vec1[i]+vec2[i])
		elif operator == '-':
			vec.append(vec1[i]-vec2[i])
	return vec

def vCross(vec1, vec2):
	vec = [vec1[1]*vec2[2] - vec1[2]*vec2[1],
		   vec1[2]*vec2[0] - vec1[0]*vec2[2],
		   vec1[0]*vec2[1] - vec1[1]*vec2[0]]
	return vec

def vDot(vec1, vec2):
	return sum([vec1[i]*vec2[i] for i in range(len(vec1))])

def vLength(vec1):
	return math.sqrt(vDot(vec1, vec1))

def vMultiply(vec1, m):
	vec = []
	for i in range(len(vec1)):
		vec.append(vec1[i] * m)
	return vec

def vNormal(vec1):
	vec1L = vLength(vec1)
	nVec1 = vMultiply(vec1, 1.0/vec1L)
	return nVec1

def vSum(vec1):
	return sum([vec1[i] for i in range(len(vec1))])

def vSquare(vec1):
	vec = []
	for i in range(len(vec1)):
		vec.append(vec1[i] * vec1[i])
	return vec


def snapSel():
	ikfkSnap()





###### RUN #####
# snapSel()
# select <=> ctrl and run this