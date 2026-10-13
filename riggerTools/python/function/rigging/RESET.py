import maya.cmds as mc

from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.util import misc as misc
reload(misc)

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

# Determine namespace and reference string

SPECIAL_ATTR_DEFAULTS = {
	# Foot Roll & Leg Attributes
	'ballRoll': 0.0,
	'toeRoll': 0.0,
	'heelRoll': 0.0,
	'heelTwist': 0.0,
	'toeTwist': 0.0,
	'footRock': 0.0,
	'ballRise': 0.0,
	'kneeLock': 0.0,
	'elbowLock': 0.0,
	'ankleRoll': 0.0,
	'toeBend': 0.0,
	'heelBend': 0.0,
	'footIn': 0.0,
	'footOut': 0.0,

	# Finger Poses & Curl Attributes
	'fist': 0.0,
	'roll': 0.0,
	'relax': 0.0,
	'spread': 0.0,
	'cup': 0.0,
	'wide': 0.0,
	'clench': 0.0,
	'handScale': 1.0,

	# Finger FK/IK, Space & Collision Switches
	'allFkIk': 0.0,
	'allFingerSpace': 0,
	'space': 0,
	'groundCollision': 0.0,
	'thumbFkIk': 0.0,
	'indexFkIk': 0.0,
	'middleFkIk': 0.0,
	'ringFkIk': 0.0,
	'pinkyFkIk': 0.0,
}


# Attributes to explicitly skip (preserve current animation/mode state)
SKIP_ATTRS = {'FK_IK', 'fk_ik', 'FKIK', 'fkIk'}


def resetControllerList(ctrl_list, resetCustomAttributes=False):
	"""
	Reset transforms and optionally special/custom rigging attributes on a given list of controllers.

	:param ctrl_list: List of controller names to reset.
	:param resetCustomAttributes: If True, reset custom and special rigging attributes (foot roll, finger curl, user-defined attrs).
	                              Defaults to False (resets transformation channels only).
	"""
	if not ctrl_list:
		return

	transform_attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

	for name in ctrl_list:
		if not mc.objExists(name):
			continue

		# 1. Reset standard transformation attributes
		for attr in transform_attrs:
			attr_name = f"{name}.{attr}"
			if not mc.objExists(attr_name) or mc.getAttr(attr_name, lock=True):
				continue

			default_value = 1.0 if attr in ['sx', 'sy', 'sz'] else 0.0
			try:
				if mc.getAttr(attr_name) != default_value:
					mc.setAttr(attr_name, default_value)
			except Exception:
				continue

		# 2. Reset custom / special rigging attributes if enabled
		if resetCustomAttributes:
			# 2a. Reset known special rigging attributes (Foot, Finger, Curl, Space)
			for attr, default_value in SPECIAL_ATTR_DEFAULTS.items():
				if attr in SKIP_ATTRS or attr.upper() == 'FK_IK':
					continue

				attr_name = f"{name}.{attr}"
				if mc.attributeQuery(attr, node=name, exists=True):
					if mc.getAttr(attr_name, lock=True):
						continue
					try:
						if mc.getAttr(attr_name) != default_value:
							mc.setAttr(attr_name, default_value)
							print(f"Reset {attr_name} -> {default_value}")
					except Exception:
						continue

			# 2b. Dynamic User-Defined Keyable Attributes Reset
			user_attrs = mc.listAttr(name, userDefined=True, keyable=True) or []
			for u_attr in user_attrs:
				if u_attr in SPECIAL_ATTR_DEFAULTS or u_attr in transform_attrs or u_attr in SKIP_ATTRS or u_attr.upper() == 'FK_IK':
					continue

				attr_name = f"{name}.{u_attr}"
				if mc.getAttr(attr_name, lock=True):
					continue

				# Skip separator/header enums
				nice_name = mc.attributeQuery(u_attr, node=name, niceName=True) or ''
				if nice_name == '_' or 'Settings' in u_attr or 'Bar' in u_attr or 'header' in u_attr.lower():
					continue

				# Try to query default value, fallback to 0.0
				try:
					dv = mc.addAttr(attr_name, query=True, defaultValue=True)
					if dv is None:
						dv = 0.0
					if mc.getAttr(attr_name) != dv:
						mc.setAttr(attr_name, dv)
						print(f"Reset userDefined {attr_name} -> {dv}")
				except Exception:
					continue


def resetAllController(reference=False, resetCustomAttributes=False):
	"""
	Reset all controllers in the scene.

	:param reference: If True, searches within namespaces ('*:*').
	:param resetCustomAttributes: If True, resets custom and special rigging attributes in addition to TRS. Defaults to False.
	"""
	refStr = '*:*' if reference else '*'
	sel = mc.ls(f'{refStr}_ctrl', f'{refStr}_gmbCtrl')

	resetControllerList(sel, resetCustomAttributes=resetCustomAttributes)

	mc.select(cl=True)
	print("### RESET ALL CTRL VALUES COMPLETE ###")


def resetSelectedController(resetCustomAttributes=False):
	"""
	Reset only currently selected controllers.

	:param resetCustomAttributes: If True, resets custom and special rigging attributes in addition to TRS. Defaults to False.
	"""
	sel = mc.ls(sl=True)
	if not sel:
		mc.warning("Please select at least one controller to reset.")
		return

	resetControllerList(sel, resetCustomAttributes=resetCustomAttributes)
	print("### RESET SELECTED CTRL VALUES COMPLETE ###")




