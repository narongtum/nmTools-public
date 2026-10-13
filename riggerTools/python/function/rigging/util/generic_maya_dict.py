import maya.cmds as mc

'''




from function.rigging.util import generic_maya_dict as mnd
reload(mnd)



mnd.select_body_jnt()

'''



'''
#... How to use

nodeDict = mnd.NODE_dict

for each in nodeDict:
	if each["longName"] == 'joint':
		node_exp = each["shortName"]







#... select body bind joint

from function.rigging.util import generic_maya_dict as mnd
reload(mnd)

nodeDict = mnd.standardJnt_list

for each in nodeDict:
	mc.select(each, add=True)

		
'''


'''
from function.rigging.util import generic_maya_dict as mnd
reload(mnd)
mnd.COLOR_part_dict['right']
'''







# ==============================================================================
# 1. PROCEDURAL RIGGING PARAMETERS (DUAL ARCHITECTURE)
# ==============================================================================
# Canonical catalog of arguments/kwargs used in nmTools procedural auto-rig functions.
# Organized by category with strict type, default, intent, and anti-pattern constraints.

PARAMETER_BY_CATEGORY = {
	'Hierarchy & DAG Attachment': {
		'parentCtrlTo': {
			'type': 'str',
			'default': None,
			'desc': 'Target controller, group, or transform under which the module controller zero group is parented (e.g. "head01_gmbCtrl", "ctrl_grp").',
			'never_use': ['parentCtrl', 'parent_to', 'targetCtrl', 'parentToCtrl']
		},
		'parentCtrlToPriorJnt': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag determining controller follow mode. True = parent controller group under parentCtrlTo and parentConstraint to priorJnt; False = direct DAG parenting.',
			'never_use': ['parentCtrlFollow', 'constraintCtrlToPrior', 'parentCtrlPrior']
		},
		'priorJnt': {
			'type': 'str',
			'default': None,
			'desc': 'Preceding parent joint name (e.g. "head01_bJnt", "clavLFT_bJnt") where this module connects or parents its root joint.',
			'never_use': ['parentJnt', 'previousJnt', 'prevJnt', 'baseJnt']
		},
		'parentToPriorJnt': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag. If True, automatically DAG-parents the root bind joint (_bJnt) under priorJnt.',
			'never_use': ['parentPrior', 'parentToParent', 'connectToPrior']
		},
		'parentTo': {
			'type': 'str',
			'default': None,
			'desc': 'Explicit target DAG parent node (group, joint, or controller) to parent newly created nodes or groups under.',
			'never_use': ['parentTarget', 'dagParent']
		},
		'useRigGrp': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag. If True, encapsulates all module components inside a dedicated {part}Rig_grp; if False, parents top zero group directly under parentCtrlTo.',
			'never_use': ['createRigGrp', 'makeRigGrp']
		},
		'chainHierarchy': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag for FK chains. If True, controllers form a sequential parent-child chain (01 -> 02 -> 03); if False, controllers are arranged in parallel (flat FK).',
			'never_use': ['sequential', 'hierarchyMode']
		},
		'noTouchGrp': {
			'type': 'str',
			'default': None,
			'desc': 'Internal calculation group name for constraints, curves, and non-keyable utility nodes (hidden from animators).',
			'never_use': ['hiddenGrp', 'dontTouchGrp', 'calcGrp']
		},
		'nullGrp': {
			'type': 'str',
			'default': None,
			'desc': 'Buffer/zero group name for controllers or joints.',
			'never_use': ['zeroGrp', 'zroGrp']
		},
		'ikhGrp': {
			'type': 'str',
			'default': None,
			'desc': 'Dedicated group name housing IK handles.',
			'never_use': ['ikHandleGrp', 'ikGrp']
		},
		'ctrl_grp': {
			'type': 'str',
			'default': 'ctrl_grp',
			'desc': 'Master controller group in the rig hierarchy.',
			'never_use': ['controlGrp', 'controllers_grp']
		},
		'jnt_grp': {
			'type': 'str',
			'default': 'jnt_grp',
			'desc': 'Master joint group housing bind joints and procedural driver chains.',
			'never_use': ['jointGrp', 'joints_grp']
		}
	},

	'Joint & Guide Inputs': {
		'jntLst': {
			'type': 'list|tuple',
			'default': (),
			'desc': 'List or tuple of joint names to process or rig (supports single flat list or nested lists for multi-chain setups).',
			'never_use': ['jointList', 'joints', 'jnts', 'jntList']
		},
		'tmpJnt': {
			'type': 'str|list',
			'default': None,
			'desc': 'Guide/template joint name or list used as geometric reference for joint placement, orientation, and rotateOrder.',
			'never_use': ['guideJnt', 'templateJoint', 'guide', 'tempJnt']
		},
		'isTmpJnt': {
			'type': 'bool|None',
			'default': None,
			'desc': 'Boolean flag or None. If True, procedurally clones template joints (_tmpJnt -> _bJnt) via rigTools.jointAt; if False, uses existing bind joints directly.',
			'never_use': ['fromTemplate', 'cloneGuide']
		},
		'suffix': {
			'type': 'str',
			'default': '_bJnt',
			'desc': 'Suffix token appended to newly created bind joints or nodes (default: "_bJnt").',
			'never_use': ['jointSuffix', 'endSuffix']
		},
		'prefix': {
			'type': 'str',
			'default': '',
			'desc': 'Prefix token prepended to newly created nodes (e.g. "L_", "R_").',
			'never_use': ['pre', 'startPrefix']
		},
		'baseName': {
			'type': 'str',
			'default': None,
			'desc': 'Sanitized base name string used for prefixing utility nodes, groups, and controllers.',
			'never_use': ['coreName', 'rawName']
		},
		'name': {
			'type': 'str',
			'default': None,
			'desc': 'Primary base name of the module, component, or controller (e.g. "arm", "leg", "skirt", "hair").',
			'never_use': ['partName', 'moduleName']
		}
	},

	'Controller Shapes & Transformation': {
		'ctrlShape': {
			'type': 'str',
			'default': 'circle_ctrlShape',
			'desc': 'Curve shape identifier for controllers (e.g. "circle_ctrlShape", "cube_ctrlShape", "sphere_ctrlShape", "stick_ctrlShape").',
			'never_use': ['shape', 'curveShape', 'controllerShape']
		},
		'charScale': {
			'type': 'float',
			'default': 1.0,
			'desc': 'Global character scale multiplier (float, default 1.0) used to size controllers, locators, and offset distances proportionally.',
			'never_use': ['globalScale', 'scaleMult', 'characterScale']
		},
		'color': {
			'type': 'str|None',
			'default': None,
			'desc': 'Controller color override (e.g. "blue", "red", "yellow", "softBlue", "white"). If None, auto-detected from side.',
			'never_use': ['ctrlColor', 'colour']
		},
		'side': {
			'type': 'str',
			'default': 'LFT',
			'desc': 'Rig side token ("LFT", "RGT", "CEN", "L", "R", "C"). Used for symmetry, naming, and color coding.',
			'never_use': ['sideName', 'sideToken']
		},
		'rotateOrder': {
			'type': 'str',
			'default': 'zxy',
			'desc': 'Maya rotation order string (e.g. "zxy", "xyz", "xzy", "yxz") applied to controllers and joints to mitigate gimbal lock.',
			'never_use': ['rotOrder', 'ro', 'rotationOrder']
		},
		'linkRotOrder': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag. If True, dynamically connects controller rotateOrder to drive target joint rotateOrder.',
			'never_use': ['syncRotOrder', 'connectRotateOrder']
		},
		'segmentScaleCompensate': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag (or "ssc"). If False (pipeline standard), disables SSC on bind joints to ensure proper uniform scaling without shearing.',
			'never_use': ['compensateScale', 'disableSSC']
		},
		'ssc': {
			'type': 'bool',
			'default': False,
			'desc': 'Alias for segmentScaleCompensate. Disables joint Segment Scale Compensate when False.',
			'never_use': []
		}
	},

	'Kinematics & Constraints': {
		'parentMatrix': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag. If True, drives joints via matrixConstraint.parentConMatrix; if False, uses standard Maya parent/scale constraints.',
			'never_use': ['matrixParent', 'useMatrix']
		},
		'localWorld': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag or mode. If True, builds a dynamic Orient Local/World space switch network on the controller.',
			'never_use': ['worldOrient', 'localOrient']
		},
		'mo': {
			'type': 'bool',
			'default': True,
			'desc': 'Maintain offset boolean flag (maintainOffset). If True, preserves initial transformation offset between driver and driven.',
			'never_use': ['maintainOffset', 'keepOffset']
		},
		'alongAxis': {
			'type': 'str',
			'default': 'y',
			'desc': 'Primary anatomical axis along the bone or chain (e.g. "y", "x", "z").',
			'never_use': ['boneAxis', 'aimAxis']
		},
		'axis': {
			'type': 'str|tuple',
			'default': 'y+',
			'desc': 'Vector axis string or tuple for constraint aiming, flipping, or projection (e.g. "x+", "y-", "z+").',
			'never_use': ['upAxis', 'targetAxis']
		}
	},

	'Secondary & Poses': {
		'curlCtrl': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag. If True, builds an overall Curl/Master controller driving secondary rotational offsets across the chain.',
			'never_use': ['poseCtrl', 'masterCurl']
		},
		'curlPosiAtFirst': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag for Curl controller placement. True = snaps to the root joint; False = snaps to the tip joint.',
			'never_use': ['curlAtRoot', 'firstCurlPos']
		},
		'curlCtrlShape': {
			'type': 'str',
			'default': 'stick_ctrlShape',
			'desc': 'Curve shape identifier for the Curl controller (e.g. "stick_ctrlShape").',
			'never_use': ['curlShape', 'stickCurve']
		},
		'constraintCurl': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag. If True, parent-constrains the Curl zero group to follow the snap joint.',
			'never_use': ['followCurl', 'stickFollow']
		},
		'stickNam': {
			'type': 'str',
			'default': None,
			'desc': 'Name identifier for stick/curl pose controllers.',
			'never_use': ['stickName', 'poseCtrlName']
		},
		'fingerName': {
			'type': 'str',
			'default': None,
			'desc': 'Name identifier for finger chain components (e.g. "thumb", "index", "middle", "ring", "pinky").',
			'never_use': ['digitName']
		}
	},

	'Limb & IK Systems': {
		'povShape': {
			'type': 'str',
			'default': 'sphere_ctrlShape',
			'desc': 'Curve shape identifier for Pole Vector controllers (e.g. "sphere_ctrlShape", "cross_ctrlShape").',
			'never_use': ['pvShape', 'poleVectorShape']
		},
		'povPosi': {
			'type': 'float|tuple',
			'default': None,
			'desc': 'Vector or distance multiplier controlling Pole Vector controller standoff distance from the knee/elbow.',
			'never_use': ['pvPos', 'poleVectorPos']
		},
		'ikPosi': {
			'type': 'str|tuple',
			'default': None,
			'desc': 'Snapping target, guide, or position offset for IK handle and IK controller placement.',
			'never_use': ['ikPos', 'ikTarget']
		},
		'keepFkIkBoth': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag. If True, keeps both FK and IK controllers visible simultaneously; if False, toggles visibility via FK_IK switch.',
			'never_use': ['showBothFkIk', 'alwaysVisFkIk']
		},
		'creTwistJnt': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag. If True, procedurally creates roll/twist joints along the limb segments to preserve volume.',
			'never_use': ['buildTwist', 'createTwist']
		}
	},

	'Ribbon & Spline': {
		'ribbon': {
			'type': 'bool',
			'default': False,
			'desc': 'Boolean flag. If True, builds a NURBS surface ribbon deformation network.',
			'never_use': ['useRibbon', 'createRibbon']
		},
		'ribbonRes': {
			'type': 'int',
			'default': 5,
			'desc': 'Integer resolution determining the number of follicle driver joints along the ribbon surface.',
			'never_use': ['ribbonJoints', 'numRibbonJnt']
		},
		'ribbonName': {
			'type': 'str',
			'default': None,
			'desc': 'Base name string for generated ribbon surface and follicle nodes.',
			'never_use': ['ribbonBase']
		},
		'pinMethod': {
			'type': 'str',
			'default': 'both',
			'desc': 'Pinning method for ribbon endpoints (e.g. "both", "start", "end", "none").',
			'never_use': ['ribbonPin']
		}
	},

	'Space Switch & Drivers': {
		'space': {
			'type': 'list',
			'default': None,
			'desc': 'List of driver space target objects for dynamic space switching (e.g. ["world", "head", "chest", "cog"]).',
			'never_use': ['spaces', 'targetSpaces', 'driverList']
		},
		'spaceAttach': {
			'type': 'str',
			'default': None,
			'desc': 'Driven node or zero group controlled by the space switch network (e.g. "handIkZro_grp"). Mandatory fail-fast parameter.',
			'never_use': ['drivenTarget', 'spaceTarget', 'attachTo']
		},
		'attr_holder': {
			'type': 'str',
			'default': None,
			'desc': 'Controller or node that hosts custom animator Channel Box attributes (e.g. space switch, follow weights, FK_IK).',
			'never_use': ['attrHost', 'holder', 'attrNode']
		},
		'attr_occur': {
			'type': 'str',
			'default': None,
			'desc': 'Controller or shape hosting dynamic follow attributes (alias/equivalent to attr_holder in skirt/follow modules).',
			'never_use': ['occurHost']
		},
		'priorCtrl': {
			'type': 'str',
			'default': None,
			'desc': 'Preceding parent controller for hierarchical controller connection.',
			'never_use': ['parentControl', 'prevCtrl']
		}
	},

	'Diagnostics & Pipeline': {
		'showInfo': {
			'type': 'bool',
			'default': True,
			'desc': 'Boolean flag. If True, prints verbose build diagnostics and node creation breadcrumbs to the Maya Script Editor.',
			'never_use': ['verbose', 'debug', 'printInfo']
		},
		'nameSpace': {
			'type': 'str',
			'default': '',
			'desc': 'Namespace prefix string for handling referenced assets or multi-character scene setups.',
			'never_use': ['ns', 'namespacePrefix']
		}
	}
}

# Auto-flattened parameter dictionary (100% backwards-compatible string description)
parameter_name_dict = {
	param: data['desc']
	for cat in PARAMETER_BY_CATEGORY.values()
	for param, data in cat.items()
}

# Auto-flattened parameter catalog containing full metadata
parameter_catalog_dict = {
	param: dict(category=cat_name, **data)
	for cat_name, cat in PARAMETER_BY_CATEGORY.items()
	for param, data in cat.items()
}


# ==============================================================================
# 2. MAYA CONTROLLER CUSTOM ATTRIBUTES (DUAL ARCHITECTURE)
# ==============================================================================
# Canonical catalog of custom attributes added via mc.addAttr / core.Dag.addAttribute
# on Maya controllers in Channel Box. Organized by category with strict standards.

CTRL_ATTR_BY_CATEGORY = {
	'FK / IK & Space Switching': {
		'FK_IK': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Master mode switch between Forward Kinematics (FK) and Inverse Kinematics (IK). Usually float 0.0 (FK) to 1.0 (IK) or 0 to 10.',
			'never_use': ['fkik', 'ik_fk', 'fk_to_ik']
		},
		'allFkIk': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Global FK/IK switch driving all finger or limb sub-switches simultaneously.',
			'never_use': ['masterFkIk', 'all_fk_ik']
		},
		'fkVis': {
			'type': 'bool',
			'default': 1,
			'desc': 'Visibility toggle for FK controllers (0 = hidden, 1 = visible). Driven dynamically by FK_IK switch.',
			'never_use': ['fkVisibility', 'visFk']
		},
		'ikVis': {
			'type': 'bool',
			'default': 0,
			'desc': 'Visibility toggle for IK controllers and Pole Vector controls (0 = hidden, 1 = visible). Driven dynamically by FK_IK switch.',
			'never_use': ['ikVisibility', 'visIk']
		},
		'space': {
			'type': 'enum',
			'default': 0,
			'desc': 'Enum attribute providing dynamic coordinate space switching (e.g. 0:World, 1:COG, 2:Chest, 3:Head).',
			'never_use': ['spaceSwitch', 'parentSpace']
		},
		'localWorld': {
			'type': 'float|enum',
			'default': 0.0,
			'desc': 'Float (0.0 to 1.0) or Enum switch blending controller orientation between World space (0) and Local parent space (1).',
			'never_use': ['worldLocal', 'local_world']
		},
		'kneeLock': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Snaps the IK knee joint directly to the Pole Vector controller position when set to 1.0 (0.0 = normal IK).',
			'never_use': ['lockKnee', 'knee_lock']
		},
		'elbowLock': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Snaps the IK elbow joint directly to the Pole Vector controller position when set to 1.0 (0.0 = normal IK).',
			'never_use': ['lockElbow', 'elbow_lock']
		}
	},

	'Stretchy Limbs & Soft IK': {
		'autoStretch': {
			'type': 'float',
			'default': 1.0,
			'desc': 'Enables procedural automatic limb stretching when the IK controller distance exceeds natural bone length (0 = off, 1 = on).',
			'never_use': ['stretchy', 'auto_stretch']
		},
		'upStretch': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Manual stretch multiplier or length offset for the upper limb bone segment.',
			'never_use': ['upperStretch', 'up_stretch']
		},
		'lowStretch': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Manual stretch multiplier or length offset for the lower limb bone segment.',
			'never_use': ['lowerStretch', 'low_stretch']
		},
		'softIK': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Damping distance threshold that gradually decelerates the IK chain as it straightens to prevent snapping/popping.',
			'never_use': ['soft_ik', 'dampIK']
		},
		'dSoft': {
			'type': 'float',
			'default': 0.001,
			'desc': 'Soft IK exponential falloff rate parameter controlling the softness curve.',
			'never_use': ['softRate']
		},
		'squash': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Volume preservation factor that expands cross-sectional scale when a limb or spine is compressed.',
			'never_use': ['squashMult', 'autoSquash']
		},
		'stretch': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Volume preservation factor that compresses cross-sectional scale when a limb or spine is elongated.',
			'never_use': ['stretchMult', 'autoStretchScale']
		}
	},

	'Foot Roll & Ankle Mechanics': {
		'ballRoll': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Rotates the foot upward pivoting on the ball/metatarsal joint, lifting the heel off the ground.',
			'never_use': ['ball_roll', 'rollBall']
		},
		'toeRoll': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Rotates the foot upward pivoting on the tip of the toe after ball roll reaches its limit.',
			'never_use': ['toe_roll', 'rollToe']
		},
		'heelRoll': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Rotates the foot upward pivoting on the back of the heel, lifting the toes off the ground.',
			'never_use': ['heel_roll', 'rollHeel']
		},
		'heelTwist': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Twists the foot yaw angle pivoting about the heel.',
			'never_use': ['heel_twist', 'twistHeel']
		},
		'toeTwist': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Twists the foot yaw angle pivoting about the toe tip.',
			'never_use': ['toe_twist', 'twistToe']
		},
		'footRock': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Banks the foot laterally side-to-side pivoting along the outer and inner foot edges.',
			'never_use': ['foot_rock', 'bank']
		},
		'ballRise': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Raises the heel vertically while keeping the toe and ball flat on the ground plane.',
			'never_use': ['riseBall', 'heelLift']
		},
		'toeBend': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Independent secondary bend angle for the toe joints.',
			'never_use': ['bendToe']
		},
		'ankleRoll': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Direct roll/twist rotation applied directly to the ankle joint.',
			'never_use': ['rollAnkle']
		},
		'footIn': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Inward banking rotation limit or angle.',
			'never_use': ['bankIn']
		},
		'footOut': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Outward banking rotation limit or angle.',
			'never_use': ['bankOut']
		},
		'pivotChoice': {
			'type': 'enum',
			'default': 0,
			'desc': 'Enum attribute selecting the active foot pivot location (Heel, Ball, Toe, Outer, Inner).',
			'never_use': ['pivotSelect', 'footPivot']
		}
	},

	'Hand & Finger Poses': {
		'fist': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute curling all fingers and thumb simultaneously into a closed fist.',
			'never_use': ['makeFist', 'fistPose']
		},
		'roll': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute driving progressive sequential curl along finger phalanges.',
			'never_use': ['fingerRoll']
		},
		'relax': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute driving natural rest/relaxed finger curl.',
			'never_use': ['relaxedPose']
		},
		'spread': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute fanning fingers outward away from the hand center axis.',
			'never_use': ['fingerSpread']
		},
		'cup': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute curling the palm/metacarpals inward to cup the hand.',
			'never_use': ['cupHand']
		},
		'wide': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute spreading fingers outward to maximum extension.',
			'never_use': ['fingerWide']
		},
		'clench': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Pose attribute compressing knuckles into a tight grasping pose.',
			'never_use': ['fingerClench']
		},
		'handScale': {
			'type': 'float',
			'default': 1.0,
			'desc': 'Uniform scale multiplier for the entire hand controller and finger bones.',
			'never_use': ['hand_scale']
		}
	},

	'Twist & Volume Deformation': {
		'Upper_Twist': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Manual rotational twist offset applied to upper limb twist/roll joints.',
			'never_use': ['upperTwist', 'upTwist']
		},
		'Lower_Twist': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Manual rotational twist offset applied to lower limb twist/roll joints.',
			'never_use': ['lowerTwist', 'lowTwist']
		},
		'Auto_Twist': {
			'type': 'short',
			'default': 1,
			'desc': 'Toggles automatic procedural twist distribution driven by wrist/ankle orientation (0 = off, 1 = on).',
			'never_use': ['autoTwist', 'twistAuto']
		},
		'Detail': {
			'type': 'bool',
			'default': 0,
			'desc': 'Visibility toggle for secondary micro-controllers, twist controls, or ribbon tweaks (0 = hidden, 1 = visible).',
			'never_use': ['detailVis', 'tweakVis']
		},
		'offset': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Positional or rotational offset along a spline IK or tentacle chain.',
			'never_use': ['chainOffset']
		}
	},

	'Dynamic Simulation & Correctives': {
		'dynamic': {
			'type': 'bool|enum',
			'default': 1,
			'desc': 'Toggles dynamic hair/spine/cloth physics simulation on or off (0 = off, 1 = on).',
			'never_use': ['enableDynamic', 'simOn']
		},
		'dynamic_blend': {
			'type': 'float',
			'default': 1.0,
			'desc': 'Blend slider between keyframed animation (0.0) and dynamic physics simulation (1.0).',
			'never_use': ['dynBlend', 'simBlend']
		},
		'startFrame': {
			'type': 'int',
			'default': 1,
			'desc': 'Initial simulation start frame for physics solver cache initialization.',
			'never_use': ['simStart']
		},
		'groundCollision': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Toggle or height threshold for real-time mesh ground collision detection.',
			'never_use': ['floorCollide']
		},
		'currentPush': {
			'type': 'float',
			'default': 0.0,
			'desc': 'Read-only display attribute showing real-time computed translation offset for volume-bulge helper joints.',
			'never_use': ['pushValue']
		},
		'restraintWeight': {
			'type': 'float',
			'default': 0.1,
			'desc': 'Blend weight damping helper joint motion back towards restraint space (0.0 to 1.0).',
			'never_use': ['restraint_weight', 'dampWeight']
		},
		'positionWeight': {
			'type': 'float',
			'default': 0.5,
			'desc': 'Blend weight slider determining helper joint position between parent joint (0.0) and driver joint (1.0).',
			'never_use': ['posWeight', 'position_weight']
		},
		'rotationWeight': {
			'type': 'float',
			'default': 0.5,
			'desc': 'Blend weight slider determining helper joint rotation between parent joint (0.0) and driver joint (1.0).',
			'never_use': ['rotWeight', 'rotation_weight']
		}
	}
}

# Auto-flattened controller attributes dictionary (100% backwards-compatible string description)
ctrl_attribute_dict = {
	attr: data['desc']
	for cat in CTRL_ATTR_BY_CATEGORY.values()
	for attr, data in cat.items()
}

# Auto-flattened controller attributes catalog containing full metadata
ctrl_attribute_catalog_dict = {
	attr: dict(category=cat_name, **data)
	for cat_name, cat in CTRL_ATTR_BY_CATEGORY.items()
	for attr, data in cat.items()
}


# ==============================================================================
# 3. HELPER QUERY & VALIDATION FUNCTIONS
# ==============================================================================

def get_param_info(param_name):
	"""
	Retrieves detailed metadata for a procedural auto-rig function parameter.

	Args:
		param_name (str): The canonical name of the function parameter (e.g. 'priorJnt', 'parentCtrlTo').

	Returns:
		dict or None: Dictionary containing 'category', 'type', 'default', 'desc', and 'never_use'
		              if found, or None if the parameter is not registered in the catalog.

	Example:
		>>> from function.rigging.util import generic_maya_dict as mnd
		>>> info = mnd.get_param_info('priorJnt')
		>>> print(info['category'], info['desc'])
	"""
	return parameter_catalog_dict.get(param_name, None)


def get_ctrl_attr_info(attr_name):
	"""
	Retrieves detailed metadata for a Maya controller Channel Box custom attribute.

	Args:
		attr_name (str): The canonical name of the custom attribute (e.g. 'FK_IK', 'ballRoll').

	Returns:
		dict or None: Dictionary containing 'category', 'type', 'default', 'desc', and 'never_use'
		              if found, or None if the attribute is not registered in the catalog.

	Example:
		>>> from function.rigging.util import generic_maya_dict as mnd
		>>> info = mnd.get_ctrl_attr_info('FK_IK')
		>>> print(info['type'], info['desc'])
	"""
	return ctrl_attribute_catalog_dict.get(attr_name, None)


def get_params_by_category(category_name=None):
	"""
	Retrieves procedural function parameters grouped by category, or filters by a specific category.

	Args:
		category_name (str, optional): Target category name (e.g. 'Hierarchy & DAG Attachment').
		                               If None, returns a list of all available parameter categories.

	Returns:
		dict or list: If category_name is provided, returns the dictionary of parameters in that category.
		              If category_name is None, returns a list of all category name strings.

	Example:
		>>> from function.rigging.util import generic_maya_dict as mnd
		>>> categories = mnd.get_params_by_category()
		>>> hierarchy_params = mnd.get_params_by_category('Hierarchy & DAG Attachment')
	"""
	if category_name is None:
		return list(PARAMETER_BY_CATEGORY.keys())
	return PARAMETER_BY_CATEGORY.get(category_name, {})


def get_ctrl_attrs_by_category(category_name=None):
	"""
	Retrieves Maya controller custom attributes grouped by category, or filters by a specific category.

	Args:
		category_name (str, optional): Target category name (e.g. 'Foot Roll & Ankle Mechanics').
		                               If None, returns a list of all available attribute categories.

	Returns:
		dict or list: If category_name is provided, returns the dictionary of attributes in that category.
		              If category_name is None, returns a list of all category name strings.

	Example:
		>>> from function.rigging.util import generic_maya_dict as mnd
		>>> categories = mnd.get_ctrl_attrs_by_category()
		>>> foot_attrs = mnd.get_ctrl_attrs_by_category('Foot Roll & Ankle Mechanics')
	"""
	if category_name is None:
		return list(CTRL_ATTR_BY_CATEGORY.keys())
	return CTRL_ATTR_BY_CATEGORY.get(category_name, {})


def search_rig_parameter(query):
	"""
	Searches both procedural function parameters and controller custom attributes for a query string.
	Performs a case-insensitive search across parameter names, descriptions, and anti-pattern aliases.

	Args:
		query (str): Search keyword (e.g. 'prior', 'stretch', 'roll', 'fk').

	Returns:
		dict: Dictionary with 'parameters' and 'controller_attributes' lists containing matching entries.

	Example:
		>>> from function.rigging.util import generic_maya_dict as mnd
		>>> results = mnd.search_rig_parameter('stretch')
		>>> print(results['controller_attributes'])
	"""
	q = query.lower()
	matched_params = []
	matched_ctrl_attrs = []

	for name, info in parameter_catalog_dict.items():
		never_hit = any(q in alias.lower() for alias in info.get('never_use', []))
		if q in name.lower() or q in info['desc'].lower() or never_hit:
			matched_params.append({
				'name': name,
				'category': info['category'],
				'type': info['type'],
				'desc': info['desc']
			})

	for name, info in ctrl_attribute_catalog_dict.items():
		never_hit = any(q in alias.lower() for alias in info.get('never_use', []))
		if q in name.lower() or q in info['desc'].lower() or never_hit:
			matched_ctrl_attrs.append({
				'name': name,
				'category': info['category'],
				'type': info['type'],
				'desc': info['desc']
			})

	return {
		'parameters': matched_params,
		'controller_attributes': matched_ctrl_attrs
	}


def validate_param_name(param_name):
	"""
	Validates whether a parameter name conforms to the canonical nmTools rigging standard.
	Detects if the name matches a known prohibited alias (anti-pattern).

	Args:
		param_name (str): Parameter or attribute name string to test.

	Returns:
		tuple: (is_valid: bool, canonical_name: str or None, warning_message: str or None)

	Example:
		>>> from function.rigging.util import generic_maya_dict as mnd
		>>> is_valid, canonical, msg = mnd.validate_param_name('parentJnt')
		>>> # returns (False, 'priorJnt', "Prohibited alias 'parentJnt' detected! Use 'priorJnt' instead.")
	"""
	if param_name in parameter_catalog_dict:
		return (True, param_name, None)

	# Check if it is a prohibited alias across function parameters
	for canonical, info in parameter_catalog_dict.items():
		if param_name in info.get('never_use', []):
			msg = f"Prohibited alias '{param_name}' detected! Use canonical standard '{canonical}' instead."
			return (False, canonical, msg)

	# Check if it is a prohibited alias across controller attributes
	if param_name in ctrl_attribute_catalog_dict:
		return (True, param_name, None)

	for canonical, info in ctrl_attribute_catalog_dict.items():
		if param_name in info.get('never_use', []):
			msg = f"Prohibited controller attribute alias '{param_name}' detected! Use canonical standard '{canonical}' instead."
			return (False, canonical, msg)

	return (False, None, f"Unknown parameter or attribute name '{param_name}' not found in canonical catalog.")







aim_axis_dict = {
    'x+': (1, 0, 0),  'x-': (-1, 0, 0),
    'y+': (0, 1, 0),  'y-': (0, -1, 0),
    'z+': (0, 0, 1),  'z-': (0, 0, -1)}






COLOR_part_dict = { 	'right': 'red', 
						'left': 'blue', 
						'dynamic': 'white',
						'primary': 'yellow',
						'secondary': 'white',
						'tertiary': 'softBlue',
						'offset':'white',
						'gimbal': 'white'}


def askColor(side):
	if side == 'LFT':
		return 'red'
	elif side == 'RGT':
		return 'blue'
	elif side == 'MID':
		return 'yellow'
	else:
		return 'white'


def getColorPart(part):
	"""
	Returns the color string based on the part or side name from COLOR_part_dict.
	Supports right (R, RGT, right), left (L, LFT, left) case-insensitively, 
	and other keys in COLOR_part_dict.
	"""
	if not part:
		return 'white'
	
	part_lower = str(part).lower()
	
	if part_lower in ('r', 'rgt', 'right'):
		key = 'right'
	elif part_lower in ('l', 'lft', 'left'):
		key = 'left'
	else:
		key = part_lower
		
	return COLOR_part_dict.get(key, 'yellow')


# Alias for compatibility / naming convenience
askColorPart = getColorPart





dForwardAxis_dict = {	'x+':'0',
						'x-':'1',
						'y+':'2',
						'y-':'3',
						'z+':'4',
						'z-':'5',	}

dWorldUpAxis_dict = {	'y+':'0',
						'y-':'1',
						'yc':'2',
						'z+':'3',
						'z-':'4',
						'zc':'5',
						'x+':'6',
						'x-':'7',
						'xc':'8'	}





alphabet = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')

#... newr version using this instead
NODE_short_dict = {
	'nurbsSurface': 'nrb',
	'nurbsCurve': 'ctrl',
	'condition': 'cnd',
	'blendColors': 'blc',
	'distanceBetween': 'dtw',
	'expression': 'exp',
	'file': 'file',
	'lambert': 'lambert',
	'place2dTexture': 'place2d',
	'plusMinusAverage': 'pma',
	'skinCluster': 'skc',
	'multiplyDivide': 'mdv',
	'reverse': 'rev',
	'mesh': 'ply',
	'cluster': 'clus',
	'parentConstraint': 'parCons',
	'scaleConstraint': 'scaleCons',
	'orientConstraint': 'orienCons',
	'pointConstraint': 'poinCons',
	'ikHandle': 'ikh',
	'ikEffector': 'ike',
	'poleVectorConstraint': 'poleCons',
	'joint': 'jnt',
	'group': 'grp',
	'locator': 'loc',
	'clamp': 'cmp',
	'pointOnCurveInfo': 'poci',
	'decomposeMatrix': 'deComp',
	'animCurveU': 'animCrv',
	'multDoubleLinear': 'mdl',
	'phong': 'phong',
	'shadingEngine': 'sg',
	'motionPath': 'mp',
	'cMuscleSmartConstraint': 'musleCons',
	'addDoubleLinear': 'adl',
	'aimConstraint': 'aimCons',
	'animCurveUU': 'animUU',
	'curveInfo': 'crvInfo',
	'follicle': 'flc',
	'remapValue': 'remap',
	'composeMatrix': 'composeMatrix',
	'vectorProduct': 'vecProd',
	'fourByFourMatrix': 'fBFMat',
	'multMatrix': 'multMatrix',
	'aimMatrix': 'aimMatrix',
	'wtAddMatrix': 'wtAddMat',
	'eulerToQuat': 'eulToQuat',
	'quatInvert': 'quatInv',
	'quatProd': 'quatProd',
	'quatToEuler': 'quatToEul',
	'blendMatrix': 'blendMat',
	'blendShape': 'bsh',
	'network': 'meta',
	'setRange': 'setRange',
	'deformSquash': 'defSquash' ,
	'blendWeighted':'blendWeighted',
	'animCurveUL':'animCurveUL',
	'deformSine':'defSine',
	'blendTwoAttr':'bta',
	'pickMatrix':'pickMat'

}

#... Example usage
# ext = mnd.NODE_short_dict.get('parentConstraint', 'Unknown') # Output: parCons









# same as the mayaNodeDict not sure which dict to put
NODE_dict = [
	
	{	'longName': 'nurbsSurface'		, 		'shortName': 'nrb'					},
	{	'longName': 'nurbsCurve'			, 	'shortName': 'ctrl'					},
	{	'longName': 'condition'				, 	'shortName': 'cnd'					},
	{	'longName': 'blendColors'			, 	'shortName': 'blc'					},
	{	'longName': 'distanceBetween'		, 	'shortName': 'dtw'					},
	{	'longName': 'expression'			, 	'shortName': 'exp'					},
	{	'longName': 'file'					, 	'shortName': 'file'					},
	{	'longName': 'lambert'				, 	'shortName': 'lambert'				},					
	{	'longName': 'place2dTexture'		, 	'shortName': 'place2d'				},
	{	'longName': 'plusMinusAverage'		, 	'shortName': 'pma'					},
	{	'longName': 'skinCluster'			, 	'shortName': 'skc'					},
	{	'longName': 'multiplyDivide'		, 	'shortName': 'mdv'					},
	{	'longName': 'reverse'				, 	'shortName': 'rev'					},
	{	'longName': 'mesh'					, 	'shortName': 'ply'					},
	{	'longName': 'cluster'				, 	'shortName': 'clus'					},
	{	'longName': 'parentConstraint'		, 	'shortName': 'parCons'				},
	{	'longName': 'scaleConstraint'		, 	'shortName': 'scaleCons'			},
	{	'longName': 'orientConstraint'		, 	'shortName': 'orienCons'			},
	{	'longName': 'pointConstraint'		, 	'shortName': 'poinCons'				},
	{	'longName': 'ikHandle'				, 	'shortName': 'ikh'					},
	{	'longName': 'ikEffector'			, 	'shortName': 'ike'					},
	{	'longName': 'poleVectorConstraint'	, 	'shortName': 'poleCons'				},
	{	'longName': 'joint'					, 	'shortName': 'jnt'					},
	{	'longName': 'group'					, 	'shortName': 'grp'					},
	{	'longName': 'locator'				, 	'shortName': 'loc'					},
	{	'longName': 'clamp'					, 	'shortName': 'cmp'					},
	{	'longName': 'pointOnCurveInfo'		, 	'shortName': 'poci'					},
	{	'longName': 'decomposeMatrix'		, 	'shortName': 'deComp'				},
	{	'longName': 'animCurveU'			, 	'shortName': 'animCrv'				},
	{	'longName': 'multDoubleLinear'		, 	'shortName': 'mdl'					},
	{	'longName': 'phong'					, 	'shortName': 'phong'				},
	{	'longName': 'shadingEngine'			, 	'shortName': 'sg'					},
	{	'longName': 'motionPath'							, 	'shortName': 'mp'						},
	{	'longName': 'cMuscleSmartConstraint'				, 	'shortName': 'musleCons'				},
	{	'longName': 'addDoubleLinear'						, 	'shortName': 'adl'						},
	{	'longName': 'aimConstraint'							, 	'shortName': 'aimCons'					},
	{	'longName': 'aimConstraint'							, 	'shortName': 'aimCons'					},
	{	'longName': 'animCurveUU'							, 	'shortName': 'animUU'					},
	{	'longName': 'curveInfo'								,	'shortName': 'crvInfo'					},
	{	'longName': 'follicle'								,	'shortName': 'flc'						},
	{	'longName': 'remapValue'							,	'shortName': 'remap'					},
	{	'longName': 'composeMatrix'							,	'shortName': 'composeMat'			},
	{	'longName': 'vectorProduct'							,	'shortName': 'vectorProd'					},
	{	'longName': 'fourByFourMatrix'						,	'shortName': 'fourByFourMat'				},
	{	'longName': 'multMatrix'							,	'shortName': 'multMat'					},
	{	'longName': 'aimMatrix'								,	'shortName': 'aimMat'					},
	{	'longName': 'wtAddMatrix'							,	'shortName': 'wtAddMat'					},
	{	'longName': 'eulerToQuat'							,	'shortName': 'eulerToQuat'					},
	{	'longName': 'quatInvert'							,	'shortName': 'quatInvert'					},
	{	'longName': 'quatProd'								,	'shortName': 'quatProd'						},
	{	'longName': 'quatToEuler'							,	'shortName': 'quatToEuler'					},
	{	'longName': 'blendMatrix'							,	'shortName': 'blendMat'					},
	{	'longName': 'blendShape'							,	'shortName': 'bsh'					},
	{	'longName': 'network'							,	'shortName': 'meta'						},
	{	'longName': 'setRange'							,	'shortName': 'setRange'					},
	{	'longName': 'blendWeighted'							,	'shortName': 'blendWeighted'		},	
	{	'longName': 'animCurveUL'							,	'shortName': 'animCurveUL'}	,
	{	'longName': 'deformSine'							,	'shortName': 'defSine'}	,
	{	'longName': 'blendTwoAttr'							,	'shortName': 'bta'},
	{	'longName': 'pickMatrix'							,	'shortName': 'pickMat'}
]



#... naming for auto name in meta data
auto_name_variation = ('01','02')
auto_name_used = ('Gameplay_Model','Charactor_Model','Other')




#... finger dict
FINGER_dict = {		'fingerName':		('thumb','index','middle','ring','pinky'),
					'fingerbehavior':	('fist','roll','relax','cup','spread','wide')
					 }



#... foot dict
FOOT_dict = {	
					'footbehavior':	('ballRoll','toeRoll','heelTwist','toeTwist','footRock','ballRise')
					 }



def select_body_jnt():
	"""
	Selects all joints defined in standardJnt_list if they exist in the scene.
	"""
	mc.select(cl = True)
	for each in standardJnt_list:
		if mc.objExists(each):
			mc.select(each, add = True)
		else:
			# print(f"Joint {each} not found, skipping.")
			pass
	print('DONE: Bind joints selected.')




def get_short_name(long_name):
	for node in NODE_dict:
		if node['longName'] == long_name:
			return node['shortName']
	return long_name



# color dictionary calling in core
COLOR_dict = {   'yellow'    : 17 ,          'red'           : 13 ,
				'softBlue'  : 18 ,          'blue'          : 6 ,
				'white'     : 16 ,          'brown'         : 11 ,
				'black'     : 1 ,           'gray'          : 3 ,
				'softGray'  : 3 ,           'darkRed'       : 4 ,
				'darkBlue'  : 5 ,           'darkGreen'     : 7 ,
				'green'     : 14 ,          'softBlue'      : 18 ,
				'none'      : 0     }




# for arg message in arm and leg function
MESSAGE_dict = { 	'listString':	('region' , 'location'), # location get foot or angle only
					'listbJnt' 	:	('stick' , 'upJnt' , 'midJnt' , 'lowJnt'), 
					'listCtrl' 	:	('upFkCtrl' , 'midFkCtrl' , 'lowFkCtrl' , 'offset'), 
					'listPov'  	:	('pov' , 'ikCtrl' ),
					'listIkRoot':	('ikRootCtrl',),
					'meta'		:	['metaNode']							}


rotOrder_dict = {		'xyz'  : 0   ,
						'yzx'  : 1   ,
						'zxy'  : 2   ,
						'xzy'  : 3   ,
						'yxz'  : 4   ,
						'zyx'  : 5		}

rgbCode = {		'black':	(0,0,0)		,
				'red':		(1,0,0)		,
				'green':	(0,1,0)		,
				'blue':		(0,0,1)		,
				'yellow':	(1,1,0)		,
				'white':	(1,1,1)			}


make_bigger_list = (		'head01_ctrl','eyeCenter_ctrl',

					'hip_ctrl','spine01FK_ctrl','spine02FK_ctrl','spine03FK_ctrl',

					'upperArmFkLFT_ctrl','lowerArmFkLFT_ctrl','handFkLFT_ctrl',
					'ballLegFkLFT_ctrl','ankleFkLFT_ctrl','lowerLegFkLFT_ctrl','upperLegFkLFT_ctrl'

					'upperArmFkRGT_ctrl','lowerArmFkRGT_ctrl','handFkRGT_ctrl',
					'ballLegFkRGT_ctrl','ankleFkRGT_ctrl','lowerLegFkRGT_ctrl','upperLegFkRGT_ctrl'	,

					'upperArmIkRootLFT_ctrl','upperLegIkRootLFT_ctrl','footIkLFT_ctrl','handIkLFT_ctrl',
					'upperArmIkRootRGT_ctrl','upperLegIkRootRGT_ctrl','footIkRGT_ctrl','handIkRGT_ctrl'
)
					







controller_thicker_list = (		'head01_ctrl','eyeCenter_ctrl','upperArmLFTFK_ctrl',
								'lowerArmLFTFK_ctrl','handLFTFK_ctrl','upperLegLFTFK_ctrl','lowerLegLFTFK_ctrl','footLFTFK_ctrl','upperArmLFTFK_ctrl','handLFTFK_ctrl'
								'lowerArmRGTFK_ctrl','handRGTFK_ctrl','upperLegRGTFK_ctrl','lowerLegRGTFK_ctrl','footRGTFK_ctrl','upperArmRGTFK_ctrl','handRGTFK_ctrl'
								'hip_ctrl','spine01FK_ctrl','spine02FK_ctrl','spine03FK_ctrl',
								'upperArmFkLFT_ctrl','lowerArmFkLFT_ctrl','handFkLFT_ctrl',
								'upperArmFkRGT_ctrl','lowerArmFkRGT_ctrl','handFkRGT_ctrl',
								'handIkLFT_ctrl','handIkRGT_ctrl','hip_ctrl','handStickLFT_ctrl','handStickRGT_ctrl',
								'cog_ctrl','clavLFT_ctrl','clavRGT_ctrl','footIkRGT_ctrl','footIkLFT_ctrl',
								'ballLegFkLFT_ctrl','ankleFkLFT_ctrl','lowerLegFkLFT_ctrl','upperLegFkLFT_ctrl',
								'ballLegFkRGT_ctrl','ankleFkRGT_ctrl','lowerLegFkRGT_ctrl','upperLegFkRGT_ctrl')


"""standardJnt_list = [		'ankleLFT_bJnt','ankleRGT_bJnt','ballLFT_bJnt','ballRGT_bJnt',
		'clavLFT_bJnt','clavRGT_bJnt','handLFT_bJnt','handRGT_bJnt','head01_bJnt',
		'hip_bJnt','index01LFT_bJnt','index01RGT_bJnt','index02LFT_bJnt','index02RGT_bJnt',
		'index03LFT_bJnt','index03RGT_bJnt','lowerArmLFT_bJnt',
		'lowerArmRGT_bJnt','lowerLegLFT_bJnt','lowerLegRGT_bJnt','neck_bJnt',
		'ring01LFT_bJnt','ring01RGT_bJnt','ring02LFT_bJnt',
		'ring02RGT_bJnt','ring03LFT_bJnt','ring03RGT_bJnt',
		'spine01_bJnt','spine02_bJnt','spine03_bJnt','spine04_bJnt',
		'thumb01LFT_bJnt','thumb01RGT_bJnt','thumb02LFT_bJnt',
		'thumb02RGT_bJnt','thumb03LFT_bJnt','thumb03RGT_bJnt',
		'upperArmLFT_bJnt','upperArmRGT_bJnt','upperLegLFT_bJnt','upperLegRGT_bJnt'	]"""


standardJnt_list = ('ankleLFT_bJnt',
'ankleRGT_bJnt',
'ballLFT_bJnt',
'ballRGT_bJnt',
'clavLFT_bJnt',
'clavRGT_bJnt',
'handLFT_bJnt',
'handRGT_bJnt',
'hip_bJnt',
'index01LFT_bJnt',
'index01RGT_bJnt',
'index02LFT_bJnt',
'index02RGT_bJnt',
'index03LFT_bJnt',
'index03RGT_bJnt',
'lowerArmLFT_bJnt',
'lowerArmRGT_bJnt',
'lowerLegLFT_bJnt',
'lowerLegRGT_bJnt',
'ring01LFT_bJnt',
'ring01RGT_bJnt',
'ring02LFT_bJnt',
'ring02RGT_bJnt',
'ring03LFT_bJnt',
'ring03RGT_bJnt',
'spine01_bJnt',
'spine02_bJnt',
'spine03_bJnt','thumb01LFT_bJnt',
'thumb01RGT_bJnt','thumb02LFT_bJnt',
'thumb02RGT_bJnt','thumb03LFT_bJnt',
'thumb03RGT_bJnt',
'upperArmLFT_bJnt',
'upperArmRGT_bJnt',
'upperLegLFT_bJnt',
'upperLegRGT_bJnt','neck_bJnt',
'middle03LFT_bJnt',
'middle02LFT_bJnt',
'middle01LFT_bJnt',
'middle03RGT_bJnt',
'middle02RGT_bJnt',
'middle01RGT_bJnt',
'pinky01LFT_bJnt',
'pinky02LFT_bJnt',
'pinky03LFT_bJnt',
'pinky01RGT_bJnt',
'pinky02RGT_bJnt',
'pinky03RGT_bJnt',
'head01_bJnt',
'eyeLFT_bJnt',
'eyeRGT_bJnt')






standard_jnt_dict = {
	'root': ['root','L_weapon_bJnt','R_weapon_bJnt'],
	'L_arm': ['clavLFT_bJnt', 'upperArmLFT_bJnt', 'lowerArmLFT_bJnt', 'handLFT_bJnt',
			  'thumb01LFT_bJnt', 'thumb02LFT_bJnt', 'thumb03LFT_bJnt',
			  'index01LFT_bJnt', 'index02LFT_bJnt', 'index03LFT_bJnt',
			  'middle01LFT_bJnt', 'middle02LFT_bJnt', 'middle03LFT_bJnt',
			  'ring01LFT_bJnt', 'ring02LFT_bJnt', 'ring03LFT_bJnt',
			  'pinky01LFT_bJnt', 'pinky02LFT_bJnt', 'pinky03LFT_bJnt'],

	'R_arm': ['clavRGT_bJnt', 'upperArmRGT_bJnt', 'lowerArmRGT_bJnt', 'handRGT_bJnt',
			  'thumb01RGT_bJnt', 'thumb02RGT_bJnt', 'thumb03RGT_bJnt',
			  'index01RGT_bJnt', 'index02RGT_bJnt', 'index03RGT_bJnt',
			  'middle01RGT_bJnt', 'middle02RGT_bJnt', 'middle03RGT_bJnt',
			  'ring01RGT_bJnt', 'ring02RGT_bJnt', 'ring03RGT_bJnt',
			  'pinky01RGT_bJnt', 'pinky02RGT_bJnt', 'pinky03RGT_bJnt'],

	'L_leg': ['upperLegLFT_bJnt', 'lowerLegLFT_bJnt', 'ankleLFT_bJnt', 'ballLFT_bJnt'],

	'R_leg': ['upperLegRGT_bJnt', 'lowerLegRGT_bJnt', 'ankleRGT_bJnt', 'ballRGT_bJnt'],

	'spine': ['hip_bJnt', 'spine01_bJnt', 'spine02_bJnt', 'spine03_bJnt'],

	'head': ['neck_bJnt', 'head01_bJnt', 'eyeLFT_bJnt', 'eyeRGT_bJnt']
}


ue_jnt_dict = {
	'root': ['root', 'weapon_l', 'weapon_r'],
	'spine': ['pelvis', 'spine_01', 'spine_02', 'spine_03'],
	'head': ['neck_01', 'head', 'eye_l', 'eye_r'],
	'L_arm': ['clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l',
			  'thumb_01_l', 'thumb_02_l', 'thumb_03_l',
			  'index_01_l', 'index_02_l', 'index_03_l',
			  'middle_01_l', 'middle_02_l', 'middle_03_l',
			  'ring_01_l', 'ring_02_l', 'ring_03_l',
			  'pinky_01_l', 'pinky_02_l', 'pinky_03_l'],
	'R_arm': ['clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r',
			  'thumb_01_r', 'thumb_02_r', 'thumb_03_r',
			  'index_01_r', 'index_02_r', 'index_03_r',
			  'middle_01_r', 'middle_02_r', 'middle_03_r',
			  'ring_01_r', 'ring_02_r', 'ring_03_r',
			  'pinky_01_r', 'pinky_02_r', 'pinky_03_r'],
	'L_leg': ['thigh_l', 'calf_l', 'foot_l', 'ball_l'],
	'R_leg': ['thigh_r', 'calf_r', 'foot_r', 'ball_r']
}





nanuq_jnt_dict = {
	'root': ['Root_JNT','L_HandSlot_JNT','R_HandSlot_JNT'],
	'L_arm': ['L_Clav_JNT', 'L_Shoulder_JNT', 'L_Elbow_JNT', 'L_Wrist_JNT',
			  'L_Thumb1_JNT', 'L_Thumb2_JNT', 'L_Thumb3_JNT',
			  'L_Index1_JNT', 'L_Index2_JNT', 'L_Index3_JNT',
			  'L_Middle1_JNT', 'L_Middle2_JNT', 'L_Middle3_JNT',
			  'L_Ring1_JNT', 'L_Ring2_JNT', 'L_Ring3_JNT',
			  'L_Pinky1_JNT', 'L_Pinky2_JNT', 'L_Pinky3_JNT'],

	'R_arm': ['R_Clav_JNT', 'R_Shoulder_JNT', 'R_Elbow_JNT', 'R_Wrist_JNT',
			  'R_Thumb1_JNT', 'R_Thumb2_JNT', 'R_Thumb3_JNT',
			  'R_Index1_JNT', 'R_Index2_JNT', 'R_Index3_JNT',
			  'R_Middle1_JNT', 'R_Middle2_JNT', 'R_Middle3_JNT',
			  'R_Ring1_JNT', 'R_Ring2_JNT', 'R_Ring3_JNT',
			  'R_Pinky1_JNT', 'R_Pinky2_JNT', 'R_Pinky3_JNT'],

	'L_leg': ['L_Hip_JNT', 'L_Knee_JNT', 'L_Ankle_JNT', 'L_Ball_JNT'],

	'R_leg': ['R_Hip_JNT', 'R_Knee_JNT', 'R_Ankle_JNT', 'R_Ball_JNT'],

	'spine': ['Hip_JNT', 'Back_JNT', 'Spine1_JNT', 'Chest_JNT'],

	'head': ['Neck_JNT', 'Head_JNT', 'L_Eye_JNT', 'R_Eye_JNT']
}



import maya.cmds as mc

# Rename function
def rename_joints(standard_dict, nanuq_dict):
	for body_part in standard_dict:
		# Iterate over joints in each part
		for i, standard_jnt in enumerate(standard_dict[body_part]):
			if i < len(nanuq_dict[body_part]):  # Ensure there is a corresponding nanuq joint
				nanuq_jnt = nanuq_dict[body_part][i]
				
				# Check if the standard joint exists in the scene
				if mc.objExists(standard_jnt):
					# Rename to the corresponding nanuq joint
					mc.rename(standard_jnt, nanuq_jnt)
					print(f"Renamed {standard_jnt} to {nanuq_jnt}")
				else:
					print(f"{standard_jnt} does not exist.")
















regulus_facial_dict = {'facialRegion': 'facial'    ,
							   'posiBlock' : (1,1)         	,

							   'name_all':['eyeWondering_L',
										   'eyeWondering_R',
										   'eyeBlink_L',
										   'eyeBlink_R',
										   'eyeAngry_L',
										   'eyeAngry_R'] ,

							   'name_exclude':[]}










facial_dict_ARKit =   {   'facialRegion'  :   'facial'    	,
							'posiBlock' : (1,1)         	,
						
						'name_all':['eyeBlinkLeft',
								'eyeLookDownLeft',
								'eyeLookInLeft',
								'eyeLookOutLeft',
								'eyeLookUpLeft',
								'eyeSquintLeft',
								'eyeWideLeft',
								'eyeBlinkRight',
								'eyeLookDownRight',
								'eyeLookInRight',
								'eyeLookOutRight',
								'eyeLookUpRight',
								'eyeSquintRight',
								'eyeWideRight',
								'jawForward',
								'jawLeft',
								'jawRight',
								'jawOpen',
								'mouthClose',
								'mouthFunnel',
								'mouthPucker',
								'mouthRight',
								'mouthLeft',
								'mouthSmileLeft',
								'mouthSmileRight',
								'mouthFrownRight',
								'mouthFrownLeft',
								'mouthDimpleLeft',
								'mouthDimpleRight',
								'mouthStretchLeft',
								'mouthStretchRight',
								'mouthRollLower',
								'mouthRollUpper',
								'mouthShrugLower',
								'mouthShrugUpper',
								'mouthPressLeft',
								'mouthPressRight',
								'mouthLowerDownLeft',
								'mouthLowerDownRight',
								'mouthUpperUpLeft',
								'mouthUpperUpRight',
								'browDownLeft',
								'browDownRight',
								'browInnerUp',
								'browOuterUpLeft',
								'browOuterUpRight',
								'cheekPuff',
								'cheekSquintLeft',
								'cheekSquintRight',
								'noseSneerLeft',
								'noseSneerRight',
								'tongueOut',
								'uniqueFace']                 ,

						'name_exclude':[	'jawForward','jawLeft','jawRight','mouthLeft',
											'mouthRight','mouthFrownLeft','mouthFrownRight',
											'mouthDimpleLeft','mouthDimpleRight','mouthStretchLeft',
											'mouthStretchRight','mouthShrugLower','mouthShrugUpper',
											'mouthPressLeft','mouthPressRight','mouthLowerDownLeft',
											'mouthLowerDownRight','mouthUpperUpLeft','mouthUpperUpRight',
											'cheekPuff','cheekSquintLeft','cheekSquintRight','noseSneerLeft',
											'noseSneerRight'] ,

						'kite_additional':[			 u'eyeBlinkLookDownLeft',
													 u'eyeBlinkLookDownRight',
													 u'eyeBlinkLookUpLeft',
													 u'eyeBlinkLookUpRight',
													 u'eyeBlinkLookOutLeft',
													 u'eyeBlinkLookInRight',
													 u'eyeBlinkLookInLeft',
													 u'eyeBlinkLookOutRight',
													 u'eyeBlinkSquintLeft',
													 u'eyeBlinkSquintRight',
													 u'eyeBlinkCheekSquintLeft',
													 u'eyeBlinkCheekSquintRight']	,
						'mouth_oUU':[]

						}


# facial full
facial_dict_ARKit_full =   {   'facialRegion'  :   'facial'    	,
							'posiBlock' : (1,1)         	,
						
						'name_all':['eyeBlinkLeft',
								'eyeLookDownLeft',
								'eyeLookInLeft',
								'eyeLookOutLeft',
								'eyeLookUpLeft',
								'eyeSquintLeft',
								'eyeWideLeft',
								'eyeBlinkRight',
								'eyeLookDownRight',
								'eyeLookInRight',
								'eyeLookOutRight',
								'eyeLookUpRight',
								'eyeSquintRight',
								'eyeWideRight',
								'jawForward',
								'jawLeft',
								'jawRight',
								'jawOpen',
								'mouthClose',
								'mouthFunnel',
								'mouthPucker',
								'mouthRight',
								'mouthLeft',
								'mouthSmileLeft',
								'mouthSmileRight',
								'mouthFrownRight',
								'mouthFrownLeft',
								'mouthDimpleLeft',
								'mouthDimpleRight',
								'mouthStretchLeft',
								'mouthStretchRight',
								'mouthRollLower',
								'mouthRollUpper',
								'mouthShrugLower',
								'mouthShrugUpper',
								'mouthPressLeft',
								'mouthPressRight',
								'mouthLowerDownLeft',
								'mouthLowerDownRight',
								'mouthUpperUpLeft',
								'mouthUpperUpRight',
								'browDownLeft',
								'browDownRight',
								'browInnerUp',
								'browOuterUpLeft',
								'browOuterUpRight',
								'cheekPuff',
								'cheekSquintLeft',
								'cheekSquintRight',
								'noseSneerLeft',
								'noseSneerRight',
								'tongueOut',
								'jawForward','jawLeft','jawRight','mouthLeft',
								'mouthRight','mouthFrownLeft','mouthFrownRight',
								'mouthDimpleLeft','mouthDimpleRight','mouthStretchLeft',
								'mouthStretchRight','mouthShrugLower','mouthShrugUpper',
								'mouthPressLeft','mouthPressRight','mouthLowerDownLeft',
								'mouthLowerDownRight','mouthUpperUpLeft','mouthUpperUpRight',
								'cheekPuff','cheekSquintLeft','cheekSquintRight','noseSneerLeft',
								'noseSneerRight'] ,

						'kite_additional':[			 u'eyeBlinkLookDownLeft',
													 u'eyeBlinkLookDownRight',
													 u'eyeBlinkLookUpLeft',
													 u'eyeBlinkLookUpRight',
													 u'eyeBlinkLookOutLeft',
													 u'eyeBlinkLookInRight',
													 u'eyeBlinkLookInLeft',
													 u'eyeBlinkLookOutRight',
													 u'eyeBlinkSquintLeft',
													 u'eyeBlinkSquintRight',
													 u'eyeBlinkCheekSquintLeft',
													 u'eyeBlinkCheekSquintRight']	,


						}





ribbon_joint =   {   'arm_rbn'  :	[	u'lwrArmRbn01RGT_rbnBJnt',
										 u'lwrArmRbn02RGT_rbnBJnt',
										 u'lwrArmRbn03RGT_rbnBJnt',
										 u'armHingesRbnRGT_rbnBJnt',
										 u'upArmRbn01RGT_rbnBJnt',
										 u'upArmRbn02RGT_rbnBJnt',
										 u'upArmRbn03RGT_rbnBJnt',
										 u'lwrArmRbn01LFT_rbnBJnt',
										 u'lwrArmRbn02LFT_rbnBJnt',
										 u'lwrArmRbn03LFT_rbnBJnt',
										 u'armHingesRbnLFT_rbnBJnt',
										 u'upArmRbn01LFT_rbnBJnt',
										 u'upArmRbn02LFT_rbnBJnt',
										 u'upArmRbn03LFT_rbnBJnt'],




					'leg_rbn'  :   					[		u'legHingesRbnLFT_rbnBJnt',
															u'legHingesRbnRGT_rbnBJnt',
															u'lwrLegRbn01LFT_rbnBJnt',
															u'lwrLegRbn01RGT_rbnBJnt',
															u'lwrLegRbn02LFT_rbnBJnt',
															u'lwrLegRbn02RGT_rbnBJnt',
															u'lwrLegRbn03LFT_rbnBJnt',
															u'lwrLegRbn03RGT_rbnBJnt',
															u'upLegRbn01LFT_rbnBJnt',
															u'upLegRbn01RGT_rbnBJnt',
															u'upLegRbn02LFT_rbnBJnt',
															u'upLegRbn02RGT_rbnBJnt',
															u'upLegRbn03LFT_rbnBJnt',
															u'upLegRbn03RGT_rbnBJnt']    	}





noman_arm_leg_FK = ['ballLegFkLFT_ctrl',
'ankleFkLFT_ctrl',
'lowerLegFkLFT_ctrl',
'upperLegFkLFT_ctrl',
'ballLegFkRGT_ctrl',
'ankleFkRGT_ctrl',
'lowerLegFkRGT_ctrl',
'upperLegFkRGT_ctrl',
'handFkLFT_ctrl',
'lowerArmFkLFT_ctrl',
'upperArmFkLFT_ctrl',
'handFkRGT_ctrl',
'lowerArmFkRGT_ctrl',
'upperArmFkRGT_ctrl']

noman_arm_leg_IK = ['footIkLFT_ctrl',
'kneePovLFT_ctrl',
'footIkRGT_ctrl',
'kneePovRGT_ctrl',
'handIkLFT_ctrl',
'elbowPovLFT_ctrl',
'handIkRGT_ctrl',
'elbowPovRGT_ctrl',
'upperLegIkRootLFT_ctrl',
'upperLegIkRootRGT_ctrl',
'upperArmIkRootLFT_ctrl',
'upperArmIkRootRGT_ctrl'
]


noman_spine=['spineCurl_ctrl',
'spine01_ctrl',
'spine02_ctrl',
'clavLFT_ctrl',
'clavRGT_ctrl']

dode_spine = ['spineCurl_ctrl',
'spine01FK_ctrl',
'spine02FK_ctrl',
'clvLFT_ctrl',
'clvRGT_ctrl']



dode_arm_leg_FK = ['ballLFT_ctrl',
'footLFTFK_ctrl',
'lowerLegLFTFK_ctrl',
'upperLegLFTFK_ctrl',
'ballRGT_ctrl',
'footRGTFK_ctrl',
'lowerLegRGTFK_ctrl',
'upperLegRGTFK_ctrl',
'handLFTFK_ctrl',
'lowerArmLFTFK_ctrl',
'upperArmLFTFK_ctrl',
'handRGTFK_ctrl',
'lowerArmRGTFK_ctrl',
'upperArmRGTFK_ctrl']


dode_arm_leg_IK = ['footLFTIK_ctrl',
'legLFTPov_ctrl',
'footRGTIK_ctrl',
'legRGTPov_ctrl',
'armLFTIK_ctrl',
'armLFTPov_ctrl',
'armRGTIK_ctrl',
'armRGTPov_ctrl',
'upperLegLFTIK_ctrl',
'upperLegRGTIK_ctrl',
'upperArmLFTIK_ctrl',
'upperArmRGTIK_ctrl']





match_naming_dict = {
	"noman": {
		"arm_leg_FK": [
			'ballLegFkLFT_ctrl', 'ankleFkLFT_ctrl', 'lowerLegFkLFT_ctrl', 'upperLegFkLFT_ctrl',
			'ballLegFkRGT_ctrl', 'ankleFkRGT_ctrl', 'lowerLegFkRGT_ctrl', 'upperLegFkRGT_ctrl',
			'handFkLFT_ctrl', 'lowerArmFkLFT_ctrl', 'upperArmFkLFT_ctrl',
			'handFkRGT_ctrl', 'lowerArmFkRGT_ctrl', 'upperArmFkRGT_ctrl'
		],
		"arm_leg_IK": [
			'footIkLFT_ctrl', 'kneePovLFT_ctrl', 'footIkRGT_ctrl', 'kneePovRGT_ctrl',
			'handIkLFT_ctrl', 'elbowPovLFT_ctrl', 'handIkRGT_ctrl', 'elbowPovRGT_ctrl',
			'upperLegIkRootLFT_ctrl', 'upperLegIkRootRGT_ctrl',
			'upperArmIkRootLFT_ctrl', 'upperArmIkRootRGT_ctrl'
		],
		"spine": [
			'spineCurl_ctrl', 'spine01_ctrl', 'spine02_ctrl', 'clavLFT_ctrl', 'clavRGT_ctrl'
		]
	},
	"dode": {
		"spine": [
			'spineCurl_ctrl', 'spine01FK_ctrl', 'spine02FK_ctrl', 'clvLFT_ctrl', 'clvRGT_ctrl'
		],
		"arm_leg_FK": [
			'ballLFT_ctrl', 'footLFTFK_ctrl', 'lowerLegLFTFK_ctrl', 'upperLegLFTFK_ctrl',
			'ballRGT_ctrl', 'footRGTFK_ctrl', 'lowerLegRGTFK_ctrl', 'upperLegRGTFK_ctrl',
			'handLFTFK_ctrl', 'lowerArmLFTFK_ctrl', 'upperArmLFTFK_ctrl',
			'handRGTFK_ctrl', 'lowerArmRGTFK_ctrl', 'upperArmRGTFK_ctrl'
		],
		"arm_leg_IK": [
			'footLFTIK_ctrl', 'legLFTPov_ctrl', 'footRGTIK_ctrl', 'legRGTPov_ctrl',
			'armLFTIK_ctrl', 'armLFTPov_ctrl', 'armRGTIK_ctrl', 'armRGTPov_ctrl',
			'upperLegLFTIK_ctrl', 'upperLegRGTIK_ctrl', 'upperArmLFTIK_ctrl', 'upperArmRGTIK_ctrl'
		]
	}
}



handle_behavior_dict = {
	'finger': {
		'stick_name': ['handStickLFT_ctrl', 'legStickLFT_ctrl', 'frontFootStickLFT_ctrl'],
		'behavior_name': ['fist', 'roll', 'relax', 'cup', 'spread', 'wide', 'clench', 'handScale', 'allFkIk', 'allFingerSpace', 'thumbFkIk', 'indexFkIk', 'middleFkIk', 'ringFkIk', 'pinkyFkIk'],
		'side': ['LFT', 'RGT']
	},
	'foot': {
		'stick_name': ['footIkLFT_ctrl', 'ankleIkLFT_ctrl', 'ankleLFTIK_ctrl', 'legStickLFT_ctrl'],
		'behavior_name': ['ballRoll', 'toeRoll', 'heelRoll', 'heelTwist', 'toeTwist', 'footRock', 'ballRise', 'kneeLock', 'elbowLock'],
		'side': ['LFT', 'RGT']
	}
}

FINGER_dict = {
	'fingerbehavior': ('fist', 'roll', 'relax', 'cup', 'spread', 'wide', 'clench'),
	'finger_behavior': ('fist', 'roll', 'relax', 'cup', 'spread', 'wide', 'clench')
}

MESSAGE_dict = {
	'meta': ('meta',),
	'listString': ('region', 'location'),
	'listbJnt': ('stick', 'upJnt', 'midJnt', 'lowJnt'),
	'listCtrl': ('upFkCtrl', 'midFkCtrl', 'lowFkCtrl', 'offset', 'ikRootCtrl', 'midIkCtrl'),
	'listPov': ('pov', 'ikCtrl')
}


eachFinger_behavior_dict = {
	'finger': {
		'stick_name': ['thumblocalLFT_ctrl', 'indexlocalLFT_ctrl', 'middlelocalLFT_ctrl', 'ringlocalLFT_ctrl', 'pinkylocalLFT_ctrl'],
		'behavior_name': ['roll', 'stretch'],
		'side': ['LFT', 'RGT']
	}
}


# ==============================================================================
# 4. IK SPLINE ADVANCED TWIST ENUMS & RESOLVERS
# ==============================================================================

IK_SPLINE_WORLD_UP_TYPE = {
	# Standard Maya UI labels
	'Scene Up': 0,
	'Object Up': 1,
	'Object Up (Start/End)': 2,
	'Object Rotation Up': 3,
	'Object Rotation Up (Start/End)': 4,
	'Vector': 5,
	'Vector (Start/End)': 6,
	'Relative': 7,
	# Lowercase & normalized aliases
	'scene up': 0,
	'scene_up': 0,
	'object up': 1,
	'object_up': 1,
	'object up (start/end)': 2,
	'object up start/end': 2,
	'object_up_start_end': 2,
	'object rotation up': 3,
	'object_rotation_up': 3,
	'object rotation up (start/end)': 4,
	'object rotation up start/end': 4,
	'object_rotation_up_start_end': 4,
	'vector': 5,
	'vector (start/end)': 6,
	'vector start/end': 6,
	'vector_start_end': 6,
	'relative': 7,
}

IK_SPLINE_TWIST_VALUE_TYPE = {
	# Standard Maya UI labels
	'Total': 0,
	'Start/End': 1,
	'Ramp': 2,
	# Lowercase & normalized aliases
	'total': 0,
	'start/end': 1,
	'start_end': 1,
	'startend': 1,
	'ramp': 2,
}

IK_SPLINE_FORWARD_AXIS = {
	'Positive X': 0, 'x+': 0, '+x': 0,
	'Negative X': 1, 'x-': 1, '-x': 1,
	'Positive Y': 2, 'y+': 2, '+y': 2,
	'Negative Y': 3, 'y-': 3, '-y': 3,
	'Positive Z': 4, 'z+': 4, '+z': 4,
	'Negative Z': 5, 'z-': 5, '-z': 5,
}

IK_SPLINE_UP_AXIS = {
	'Positive Y': 0, 'y+': 0, '+y': 0,
	'Negative Y': 1, 'y-': 1, '-y': 1,
	'Positive Z': 2, 'z+': 2, '+z': 2,
	'Negative Z': 3, 'z-': 3, '-z': 3,
	'Positive X': 4, 'x+': 4, '+x': 4,
	'Negative X': 5, 'x-': 5, '-x': 5,
}


def get_ik_world_up_type(val, default=1):
	"""
	Resolves Maya Spline IK dWorldUpType enum integer from string or int.
	Supports standard Maya labels like 'Object Up' -> 1, 'Object Rotation Up (Start/End)' -> 4.
	"""
	if isinstance(val, int):
		return val
	if isinstance(val, str):
		if val in IK_SPLINE_WORLD_UP_TYPE:
			return IK_SPLINE_WORLD_UP_TYPE[val]
		clean_val = val.strip().lower().replace('/', '_').replace(' ', '_').replace('(', '').replace(')', '')
		return IK_SPLINE_WORLD_UP_TYPE.get(clean_val, default)
	return default


def get_ik_twist_value_type(val, default=1):
	"""
	Resolves Maya Spline IK dTwistValueType enum integer from string or int.
	Supports standard Maya labels like 'Start/End' -> 1, 'Total' -> 0, 'Ramp' -> 2.
	"""
	if isinstance(val, int):
		return val
	if isinstance(val, str):
		if val in IK_SPLINE_TWIST_VALUE_TYPE:
			return IK_SPLINE_TWIST_VALUE_TYPE[val]
		clean_val = val.strip().lower().replace('/', '_').replace(' ', '_')
		return IK_SPLINE_TWIST_VALUE_TYPE.get(clean_val, default)
	return default


def get_ik_forward_axis(val, default=5):
	"""
	Resolves Maya Spline IK dForwardAxis enum integer from string or int.
	Supports 'z-', 'Negative Z' -> 5, 'y+' -> 2, etc.
	"""
	if isinstance(val, int):
		return val
	if isinstance(val, str):
		if val in IK_SPLINE_FORWARD_AXIS:
			return IK_SPLINE_FORWARD_AXIS[val]
		clean_val = val.strip().lower()
		return IK_SPLINE_FORWARD_AXIS.get(clean_val, default)
	return default


def get_ik_up_axis(val, default=0):
	"""
	Resolves Maya Spline IK dWorldUpAxis enum integer from string or int.
	Supports 'y+', 'Positive Y' -> 0, 'Negative Y' -> 1, etc.
	"""
	if isinstance(val, int):
		return val
	if isinstance(val, str):
		if val in IK_SPLINE_UP_AXIS:
			return IK_SPLINE_UP_AXIS[val]
		clean_val = val.strip().lower()
		return IK_SPLINE_UP_AXIS.get(clean_val, default)
	return default










