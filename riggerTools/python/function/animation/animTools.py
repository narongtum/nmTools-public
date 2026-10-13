'''
from function.animation import animTools 
reload( animTools )
'''
from function.framework.reloadWrapper import reloadWrapper as reload

import maya.cmds as mc

from function.rigging.util import misc
reload(misc)

def selectAllCtrl():
	selected = mc.ls( sl = True )
	nameSpace = misc.findNameSpace()

	if nameSpace:
		# If selection is reference
		mc.select('%s*_ctrl' %nameSpace,r=True)
		mc.select('%s*_gmbCtrl' %nameSpace, add=True)
	elif selected:
		# If selection is controller
		mc.select( '*_ctrl' ,r=True)
		mc.select( '*_gmbCtrl' , add=True)
	else:
		# Nothing select 
		mc.warning( "No controller selected" )