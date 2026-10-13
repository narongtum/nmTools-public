# ==============================================================================
# Tentacle FK/IK Deformed Rig - Standalone Portable Module
# ==============================================================================
# Description:
#   Self-contained standalone procedural tentacle / tail rig for Autodesk Maya.
#   Includes FK controls, IK Spline with advanced twist, De Boor curve-to-mesh
#   skinning distribution, squash/stretch volume preservation, and sine wave deformer.
#
#   All external dependencies (core nodes, rigTools, de_boor, controller shapes,
#   matrix constraints, pin-to-surface) are fully inlined.
#   This file can be copied and executed in ANY Maya environment without requiring
#   nmTools repository in sys.path.
#
# Usage:
#   import tentacle_fkIkDeformedRig_standalone as tenRig
#   tenRig.fkIkDeformed(
#       SIDE='C',
#       BASE_NAME='tenTail',
#       SCALE=20,
#       COUNT_DETAIL=24,
#       COUNT_MAIN=9,
#       stickShape='stickCircle_Y_long_ctrlShape',
#       mesh='tailSpike_ply',
#       smoothweight=True,
#       sineDef=True,
#       squashDef=True,
#       priorJnt='root',
#       parentTo='ctrl_grp',
#       place_ctrl='placement_ctrl',
#       enableTwist=True,
#       worldUpType=4,
#       forwardAxis='y+',
#       worldUpAxis='z+',
#       worldUpVector=(0, 0, 1),
#       worldUpVectorEnd=(0, 0, 1),
#       upObject='placement_ctrl',
#       upObjectEnd='C_tenTail08_masterIk_ctrl'
#   )
# ==============================================================================

import re
import math
import logging
import maya.cmds as mc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------
logger = logging.getLogger("TentacleRig")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
logger.setLevel(logging.DEBUG)


# ------------------------------------------------------------------------------
# Embedded Controller Shapes Library (Offline Portable Fallback)
# ------------------------------------------------------------------------------
EMBEDDED_SHAPES = {
    "ring_ctrlShape": {
        "degree": 1,
        "form": 0,
        "knots": [float(i) for i in range(34)],
        "points": [
            [-0.707107, 0.0916408, 0.707107], [0.0, 0.0916408, 1.0], [0.0, -0.0916408, 1.0],
            [-0.707107, -0.0916408, 0.707107], [-0.707107, 0.0916408, 0.707107], [-1.0, 0.0916408, 0.0],
            [-1.0, -0.0916408, 0.0], [-0.707107, -0.0916408, 0.707107], [-1.0, -0.0916408, 0.0],
            [-0.707107, -0.0916408, -0.707107], [-0.707107, 0.0916408, -0.707107], [-1.0, 0.0916408, 0.0],
            [-0.707107, 0.0916408, -0.707107], [0.0, 0.0916408, -1.0], [0.0, -0.0916408, -1.0],
            [-0.707107, -0.0916408, -0.707107], [-0.707107, 0.0916408, -0.707107], [-0.707107, -0.0916408, -0.707107],
            [0.0, -0.0916408, -1.0], [0.707107, -0.0916408, -0.707107], [0.707107, 0.0916408, -0.707107],
            [0.0, 0.0916408, -1.0], [0.707107, 0.0916408, -0.707107], [1.0, 0.0916408, 0.0],
            [1.0, -0.0916408, 0.0], [0.707107, -0.0916408, -0.707107], [1.0, -0.0916408, 0.0],
            [0.707107, -0.0916408, 0.707107], [0.707107, 0.0916408, 0.707107], [1.0, 0.0916408, 0.0],
            [0.707107, 0.0916408, 0.707107], [0.0, 0.0916408, 1.0], [0.0, -0.0916408, 1.0],
            [0.707107, -0.0916408, 0.707107]
        ]
    },
    "cube_ctrlShape": {
        "degree": 1,
        "form": 0,
        "knots": [float(i) for i in range(16)],
        "points": [
            [-0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
            [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5],
            [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5],
            [0.5, 0.5, -0.5], [0.5, -0.5, -0.5], [-0.5, -0.5, -0.5], [-0.5, 0.5, -0.5]
        ]
    },
    "stickCircle_Y_long_ctrlShape": {
        "degree": 1,
        "form": 0,
        "knots": [float(i) for i in range(62)],
        "points": [
            [0.0, 0.0, 0.0], [0.0, 5.499085, 0.0], [0.0523598, 5.501829, 0.0], [0.104146, 5.510032, 0.0],
            [0.154791, 5.523602, 0.0], [0.20374, 5.542392, 0.0], [0.250457, 5.566195, 0.0], [0.29443, 5.594752, 0.0],
            [0.335177, 5.627748, 0.0], [0.372252, 5.664823, 0.0], [0.405248, 5.70557, 0.0], [0.433805, 5.749543, 0.0],
            [0.457608, 5.79626, 0.0], [0.476398, 5.845209, 0.0], [0.489968, 5.895854, 0.0], [0.498171, 5.94764, 0.0],
            [0.500915, 6.0, 0.0], [0.498171, 6.05236, 0.0], [0.489968, 6.104146, 0.0], [0.476398, 6.154791, 0.0],
            [0.457608, 6.20374, 0.0], [0.433805, 6.250457, 0.0], [0.405248, 6.29443, 0.0], [0.372252, 6.335177, 0.0],
            [0.335177, 6.372252, 0.0], [0.29443, 6.405248, 0.0], [0.250457, 6.433805, 0.0], [0.20374, 6.457608, 0.0],
            [0.154791, 6.476398, 0.0], [0.104146, 6.489968, 0.0], [0.0523598, 6.498171, 0.0], [0.0, 6.500915, 0.0],
            [-0.0523598, 6.498171, 0.0], [-0.104146, 6.489968, 0.0], [-0.154791, 6.476398, 0.0], [-0.20374, 6.457608, 0.0],
            [-0.250457, 6.433805, 0.0], [-0.29443, 6.405248, 0.0], [-0.335177, 6.372252, 0.0], [-0.372252, 6.335177, 0.0],
            [-0.405248, 6.29443, 0.0], [-0.433805, 6.250457, 0.0], [-0.457608, 6.20374, 0.0], [-0.476398, 6.154791, 0.0],
            [-0.489968, 6.104146, 0.0], [-0.498171, 6.05236, 0.0], [-0.500915, 6.0, 0.0], [-0.498171, 5.94764, 0.0],
            [-0.489968, 5.895854, 0.0], [-0.476398, 5.845209, 0.0], [-0.457608, 5.79626, 0.0], [-0.433805, 5.749543, 0.0],
            [-0.405248, 5.70557, 0.0], [-0.372252, 5.664823, 0.0], [-0.335177, 5.627748, 0.0], [-0.29443, 5.594752, 0.0],
            [-0.250457, 5.566195, 0.0], [-0.20374, 5.542392, 0.0], [-0.154791, 5.523602, 0.0], [-0.104146, 5.510032, 0.0],
            [-0.0523598, 5.501829, 0.0], [0.0, 5.499085, 0.0]
        ]
    },
    "circle_Y_along_ctrlShape": {
        "degree": 1,
        "form": 0,
        "knots": [float(i) for i in range(48)],
        "points": [
            [0.0, -1.35, 0.0], [0.0, -1.204945, 0.0], [0.0, -1.19011, -0.188495], [0.0, -1.145971, -0.372348],
            [0.0, -1.073614, -0.547033], [0.0, -0.974821, -0.708248], [0.0, -0.852025, -0.852025], [0.0, -0.708248, -0.974821],
            [0.0, -0.547033, -1.073614], [0.0, -0.372348, -1.145971], [0.0, -0.188495, -1.19011], [0.0, 0.0, -1.204945],
            [0.0, 0.0, -1.35], [0.0, 0.0, -1.204945], [0.0, 0.188495, -1.19011], [0.0, 0.372348, -1.145971],
            [0.0, 0.547033, -1.073614], [0.0, 0.708248, -0.974821], [0.0, 0.852025, -0.852025], [0.0, 0.974821, -0.708248],
            [0.0, 1.073614, -0.547033], [0.0, 1.145971, -0.372348], [0.0, 1.19011, -0.188495], [0.0, 1.204945, 0.0],
            [0.0, 1.35, 0.0], [0.0, 1.204945, 0.0], [0.0, 1.19011, 0.188495], [0.0, 1.145971, 0.372348],
            [0.0, 1.073614, 0.547033], [0.0, 0.974821, 0.708248], [0.0, 0.852025, 0.852025], [0.0, 0.708248, 0.974821],
            [0.0, 0.547033, 1.073614], [0.0, 0.372348, 1.145971], [0.0, 0.188495, 1.19011], [0.0, 0.0, 1.204945],
            [0.0, 0.0, 1.35], [0.0, 0.0, 1.204945], [0.0, -0.188495, 1.19011], [0.0, -0.372348, 1.145971],
            [0.0, -0.547033, 1.073614], [0.0, -0.708248, 0.974821], [0.0, -0.852025, 0.852025], [0.0, -0.974821, 0.708248],
            [0.0, -1.073614, 0.547033], [0.0, -1.145971, 0.372348], [0.0, -1.19011, 0.188495], [0.0, -1.204945, 0.0]
        ]
    },
    "circle_ctrlShape": {
        "degree": 1,
        "form": 0,
        "knots": [float(i) for i in range(48)],
        "points": [
            [1.125, 0.0, 0.0], [1.004121, 0.0, 0.0], [0.991758, 0.0, -0.157079], [0.954976, 0.0, -0.31029],
            [0.894678, 0.0, -0.455861], [0.812351, 0.0, -0.590207], [0.710021, 0.0, -0.710021], [0.590207, 0.0, -0.812351],
            [0.455861, 0.0, -0.894678], [0.31029, 0.0, -0.954976], [0.157079, 0.0, -0.991758], [0.0, 0.0, -1.004121],
            [0.0, 0.0, -1.125], [0.0, 0.0, -1.004121], [-0.157079, 0.0, -0.991758], [-0.31029, 0.0, -0.954976],
            [-0.455861, 0.0, -0.894678], [-0.590207, 0.0, -0.812351], [-0.710021, 0.0, -0.710021], [-0.812351, 0.0, -0.590207],
            [-0.894678, 0.0, -0.455861], [-0.954976, 0.0, -0.31029], [-0.991758, 0.0, -0.157079], [-1.004121, 0.0, 0.0],
            [-1.125, 0.0, 0.0], [-1.004121, 0.0, 0.0], [-0.991758, 0.0, 0.157079], [-0.954976, 0.0, 0.31029],
            [-0.894678, 0.0, 0.455861], [-0.812351, 0.0, 0.590207], [-0.710021, 0.0, 0.710021], [-0.590207, 0.0, 0.812351],
            [-0.455861, 0.0, 0.894678], [-0.31029, 0.0, 0.954976], [-0.157079, 0.0, 0.991758], [0.0, 0.0, 1.004121],
            [0.0, 0.0, 1.125], [0.0, 0.0, 1.004121], [0.157079, 0.0, 0.991758], [0.31029, 0.0, 0.954976],
            [0.455861, 0.0, 0.894678], [0.590207, 0.0, 0.812351], [0.710021, 0.0, 0.710021], [0.812351, 0.0, 0.590207],
            [0.894678, 0.0, 0.455861], [0.954976, 0.0, 0.31029], [0.991758, 0.0, 0.157079], [1.004121, 0.0, 0.0]
        ]
    }
}


def _create_curve_from_shape(target_name, shape_name):
    """Creates a NURBS curve using embedded shapes, with fallback to circle."""
    shape_data = EMBEDDED_SHAPES.get(shape_name)
    if not shape_data:
        # Fallback to standard NURBS circle if shape is not in dictionary
        crv = mc.circle(name=target_name, ch=False, normal=(0, 1, 0), radius=1.0)[0]
        return crv

    pts = shape_data["points"]
    knots = shape_data["knots"]
    degree = shape_data["degree"]
    per = bool(shape_data.get("form", 0))

    crv = mc.curve(name=target_name, p=pts, k=knots, d=degree, per=per)
    return crv


# ------------------------------------------------------------------------------
# Core OOP Wrapper & Maya Utility Classes (Self-Contained)
# ------------------------------------------------------------------------------
class Attr(object):
    """Wrapper for Maya attributes supporting mathematical and connection operators."""
    def __init__(self, node_name, attr_name):
        self.node = str(node_name)
        self.attr_name = str(attr_name)
        self.name = f"{self.node}.{self.attr_name}"

    def __rshift__(self, other):
        target = str(other.name) if hasattr(other, 'name') else str(other)
        mc.connectAttr(self.name, target, force=True)
        return other

    def __floordiv__(self, other):
        target = str(other.name) if hasattr(other, 'name') else str(other)
        mc.disconnectAttr(self.name, target)
        return other

    def get(self):
        return mc.getAttr(self.name)

    def set(self, val):
        if isinstance(val, (list, tuple)):
            mc.setAttr(self.name, *val)
        elif isinstance(val, str):
            mc.setAttr(self.name, val, type='string')
        else:
            mc.setAttr(self.name, val)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, val):
        self.set(val)

    def lockHide(self):
        mc.setAttr(self.name, lock=True, keyable=False, channelBox=False)

    def setLocked(self, lock=True):
        mc.setAttr(self.name, lock=lock)

    def setMin(self, val):
        mc.addAttr(self.name, edit=True, minValue=val)

    def setMax(self, val):
        mc.addAttr(self.name, edit=True, maxValue=val)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Dag(object):
    """Lightweight DAG Node Wrapper replacing external core.Dag."""
    def __init__(self, node_name):
        self._name = str(node_name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_val):
        if mc.objExists(self._name) and self._name != str(new_val):
            self._name = mc.rename(self._name, str(new_val))
        else:
            self._name = str(new_val)

    @property
    def shape(self):
        shapes = mc.listRelatives(self.name, shapes=True) or []
        return shapes[0] if shapes else self.name

    @property
    def type(self):
        return mc.nodeType(self.name) if mc.objExists(self.name) else ""

    def attr(self, attr_name):
        return Attr(self.name, attr_name)

    def addAttribute(self, **kwargs):
        attr_name = kwargs.get('longName') or kwargs.get('ln') or kwargs.get('shortName') or kwargs.get('sn')
        if attr_name and mc.objExists(self.name) and mc.attributeQuery(attr_name, node=self.name, exists=True):
            return
        mc.addAttr(self.name, **kwargs)

    def deleteAttribute(self, attr_name):
        if mc.attributeQuery(attr_name, node=self.name, exists=True):
            mc.deleteAttr(f"{self.name}.{attr_name}")

    def disconnectAttr(self, attr_name):
        plug = f"{self.name}.{attr_name}"
        conns = mc.listConnections(plug, plugs=True, source=True, destination=False) or []
        for src in conns:
            mc.disconnectAttr(src, plug)

    def maSnap(self, target, pos=True, rot=True, scl=False):
        tgt_name = str(target.name) if hasattr(target, 'name') else str(target)
        if pos and rot:
            mc.delete(mc.parentConstraint(tgt_name, self.name, mo=False))
        elif pos:
            mc.delete(mc.pointConstraint(tgt_name, self.name, mo=False))
        elif rot:
            mc.delete(mc.orientConstraint(tgt_name, self.name, mo=False))
        if scl:
            mc.delete(mc.scaleConstraint(tgt_name, self.name, mo=False))

    def snap(self, target):
        self.maSnap(target, pos=True, rot=True)

    def matchPosition(self, target):
        self.maSnap(target, pos=True, rot=False)

    def matchRotation(self, target):
        self.maSnap(target, pos=False, rot=True)

    def freeze(self, t=False, r=True, s=False):
        mc.makeIdentity(self.name, apply=True, translate=t, rotate=r, scale=s, normal=False, preserveNormals=True)

    def lockAllAttr(self, attrs=('t', 'r', 's')):
        for a in attrs:
            for axis in ('x', 'y', 'z'):
                mc.setAttr(f"{self.name}.{a}{axis}", lock=True)

    def lockHideAttrLst(self, *attrs):
        for a in attrs:
            if mc.attributeQuery(a, node=self.name, exists=True):
                mc.setAttr(f"{self.name}.{a}", lock=True, keyable=False, channelBox=False)

    def setLocked(self, attr_name, lock=True):
        mc.setAttr(f"{self.name}.{attr_name}", lock=lock)

    def parent(self, parent_target):
        pt = str(parent_target.name) if hasattr(parent_target, 'name') else str(parent_target)
        mc.parent(self.name, pt)

    def nmCreateController(self, shape_name, lineWidth=-1):
        if not mc.objExists(self.name):
            mc.createNode('transform', name=self.name)
        tmp_crv = _create_curve_from_shape(f"{self.name}_tmpCrv", shape_name)
        shapes = mc.listRelatives(tmp_crv, shapes=True) or []
        for s in shapes:
            mc.parent(s, self.name, relative=True, shape=True)
            mc.rename(s, f"{self.name}Shape")
        if mc.objExists(tmp_crv):
            mc.delete(tmp_crv)
        if lineWidth > 0 and mc.objExists(self.shape):
            if mc.attributeQuery('lineWidth', node=self.shape, exists=True):
                mc.setAttr(f"{self.shape}.lineWidth", lineWidth)

    def editCtrlShape(self, axis=1.0):
        shapes = mc.listRelatives(self.name, shapes=True) or []
        for shape in shapes:
            if mc.nodeType(shape) == 'nurbsCurve':
                s_val = (axis, axis, axis) if isinstance(axis, (int, float)) else axis
                mc.scale(s_val[0], s_val[1], s_val[2], f"{shape}.cv[*]", r=True)

    def setJointColor(self, color):
        color_map = {
            'gray': 3, 'blue': 6, 'red': 13, 'green': 14,
            'white': 16, 'yellow': 17, 'softBlue': 18
        }
        idx = color_map.get(color, 17 if not isinstance(color, int) else color)
        mc.setAttr(f"{self.name}.overrideEnabled", 1)
        mc.setAttr(f"{self.name}.overrideColor", idx)

    @property
    def color(self):
        return mc.getAttr(f"{self.name}.overrideColor")

    @color.setter
    def color(self, color_val):
        self.setJointColor(color_val)

    @property
    def rotateOrder(self):
        order_map = {0: 'xyz', 1: 'yzx', 2: 'zxy', 3: 'xzy', 4: 'yxz', 5: 'zyx'}
        val = mc.getAttr(f"{self.name}.rotateOrder")
        return order_map.get(val, 'xyz')

    @rotateOrder.setter
    def rotateOrder(self, order_val):
        order_map = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}
        idx = order_map.get(order_val, order_val if isinstance(order_val, int) else 0)
        mc.setAttr(f"{self.name}.rotateOrder", idx)

    def hideArnoldNode(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Joint(Dag):
    def __init__(self, node_name=None, scaleCompensate=False):
        if node_name and mc.objExists(node_name):
            super().__init__(node_name)
        else:
            name_to_use = node_name or "joint1"
            jnt = mc.createNode("joint", name=name_to_use)
            super().__init__(jnt)
        if not scaleCompensate:
            mc.setAttr(f"{self.name}.segmentScaleCompensate", 0)


class Null(Dag):
    def __init__(self, node_name=None):
        if node_name and mc.objExists(node_name):
            super().__init__(node_name)
        else:
            name_to_use = node_name or "group1"
            grp = mc.group(em=True, name=name_to_use)
            super().__init__(grp)


class Locator(Dag):
    def __init__(self, node_name=None):
        if node_name and mc.objExists(node_name):
            super().__init__(node_name)
        else:
            name_to_use = node_name or "locator1"
            loc = mc.spaceLocator(name=name_to_use)[0]
            super().__init__(loc)


class DoIkSpline(Dag):
    """Wrapper for Maya ikSplineHandle with twist control."""
    def __init__(self, startJoint='', endEffector='', solverType='ikSplineSolver',
                 createCurve=False, curveName='', parentCurve=False):
        res = mc.ikHandle(startJoint=startJoint, endEffector=endEffector,
                          solver=solverType, createCurve=createCurve,
                          curve=curveName, parentCurve=parentCurve)
        super().__init__(res[0])
        self.eff = res[1]

    def enableTwistControl(self, forwardAxis='z+', worldUpAxis='y+', worldUpVector=(0, 0, 1),
                           worldUpVectorEnd=(0, 0, 1), worldUpType=4, upObject=None, upObjectEnd=None):
        d_forward = {'x+': 0, 'x-': 1, 'y+': 2, 'y-': 3, 'z+': 4, 'z-': 5}
        d_world_up = {'y+': 0, 'y-': 1, 'yc': 2, 'z+': 3, 'z-': 4, 'zc': 5, 'x+': 6, 'x-': 7, 'xc': 8}

        f_idx = d_forward.get(forwardAxis, 4) if isinstance(forwardAxis, str) else forwardAxis
        w_idx = d_world_up.get(worldUpAxis, 0) if isinstance(worldUpAxis, str) else worldUpAxis

        mc.setAttr(f"{self.name}.dTwistControlEnable", 1)
        mc.setAttr(f"{self.name}.dForwardAxis", f_idx)
        mc.setAttr(f"{self.name}.dWorldUpAxis", w_idx)
        mc.setAttr(f"{self.name}.dWorldUpType", worldUpType)
        mc.setAttr(f"{self.name}.dWorldUpVectorX", worldUpVector[0])
        mc.setAttr(f"{self.name}.dWorldUpVectorY", worldUpVector[1])
        mc.setAttr(f"{self.name}.dWorldUpVectorZ", worldUpVector[2])
        mc.setAttr(f"{self.name}.dWorldUpVectorEndX", worldUpVectorEnd[0])
        mc.setAttr(f"{self.name}.dWorldUpVectorEndY", worldUpVectorEnd[1])
        mc.setAttr(f"{self.name}.dWorldUpVectorEndZ", worldUpVectorEnd[2])

        if upObject and mc.objExists(upObject):
            mc.connectAttr(f"{upObject}.worldMatrix[0]", f"{self.name}.dWorldUpMatrix", force=True)
        if upObjectEnd and mc.objExists(upObjectEnd):
            mc.connectAttr(f"{upObjectEnd}.worldMatrix[0]", f"{self.name}.dWorldUpMatrixEnd", force=True)


# DG Utility Node Wrappers
def CurveInfo(name):
    node = mc.createNode("curveInfo", name=f"{name}_crvInfo") if not mc.objExists(f"{name}_crvInfo") else f"{name}_crvInfo"
    return Dag(node)

def MultiplyDivineWithVal(name, operation=2):
    node = mc.createNode("multiplyDivide", name=name) if not mc.objExists(name) else name
    mc.setAttr(f"{node}.operation", operation)
    return Dag(node)

def MultiplyDivine(name):
    node = mc.createNode("multiplyDivide", name=name) if not mc.objExists(name) else name
    return Dag(node)

def MultiDoubleLinear(name):
    node = mc.createNode("multDoubleLinear", name=name) if not mc.objExists(name) else name
    return Dag(node)

def MDLWithMul(name, dv=1.0):
    node = mc.createNode("multDoubleLinear", name=name) if not mc.objExists(name) else name
    mc.setAttr(f"{node}.input2", dv)
    return Dag(node)

def AddDoubleLinear(name, input2=1.0):
    node = mc.createNode("addDoubleLinear", name=name) if not mc.objExists(name) else name
    mc.setAttr(f"{node}.input2", input2)
    return Dag(node)

def BlendTwoAttr(name):
    node = mc.createNode("blendTwoAttr", name=f"{name}_bta") if not mc.objExists(f"{name}_bta") else f"{name}_bta"
    return Dag(node)

def PlusMinusAverage(name):
    node = mc.createNode("plusMinusAverage", name=name) if not mc.objExists(name) else name
    return Dag(node)

def DecomposeMatrix(name):
    node = mc.createNode("decomposeMatrix", name=f"{name}_deComp") if not mc.objExists(f"{name}_deComp") else f"{name}_deComp"
    return Dag(node)

def MultMatrix(name):
    node = mc.createNode("multMatrix", name=f"{name}_multMat") if not mc.objExists(f"{name}_multMat") else f"{name}_multMat"
    return Dag(node)

def PickMatrix(name):
    node = mc.createNode("pickMatrix", name=f"{name}_pickMat") if not mc.objExists(f"{name}_pickMat") else f"{name}_pickMat"
    return Dag(node)

def EulerToQuat(name):
    node = mc.createNode("eulerToQuat", name=f"{name}_eulerToQuat") if not mc.objExists(f"{name}_eulerToQuat") else f"{name}_eulerToQuat"
    return Dag(node)

def QuatInvert(name):
    node = mc.createNode("quatInvert", name=f"{name}_quatInv") if not mc.objExists(f"{name}_quatInv") else f"{name}_quatInv"
    return Dag(node)

def QuatProd(name):
    node = mc.createNode("quatProd", name=f"{name}_quatProd") if not mc.objExists(f"{name}_quatProd") else f"{name}_quatProd"
    return Dag(node)

def QuatToEuler(name):
    node = mc.createNode("quatToEuler", name=f"{name}_quatToEul") if not mc.objExists(f"{name}_quatToEul") else f"{name}_quatToEul"
    return Dag(node)

def MetaBlank(name):
    node = mc.createNode("network", name=name) if not mc.objExists(name) else name
    return Dag(node)

def MetaGeneric(name):
    node = mc.createNode("network", name=name) if not mc.objExists(name) else name
    return Dag(node)

def parentConstraint(source, target, mo=True):
    con = mc.parentConstraint(str(source), str(target), mo=mo)[0]
    return Dag(con)

def scaleConstraint(source, target, mo=True):
    con = mc.scaleConstraint(str(source), str(target), mo=mo)[0]
    return Dag(con)


# ------------------------------------------------------------------------------
# String & Naming Utilities
# ------------------------------------------------------------------------------
def makeHeader(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65 + "\n")

def shapeName(node):
    node_str = str(node)
    shapes = mc.listRelatives(node_str, shapes=True) or []
    return shapes[0] if shapes else node_str

def generate_named_pattern(pattern, count):
    match = re.search(r'(#+)', pattern)
    if not match:
        raise ValueError("Pattern must contain at least one '#' as a placeholder.")
    placeholder = match.group(1)
    width = len(placeholder)
    return tuple(pattern.replace(placeholder, str(i).zfill(width)) for i in range(1, count + 1))

def check_name_style(name):
    name_str = str(name)
    parts = name_str.split('_')
    if len(parts) == 1:
        return name_str, None, None, True, name_str, None

    if len(parts[0]) == 1:
        side = parts[0]
        base_name = '_'.join(parts[:-1])
        name_no_side = base_name[2:] if len(base_name) > 2 else base_name
        is_default = False
    else:
        base_name = '_'.join(parts[:-1])
        side = None
        for s in ('LFT', 'RGT'):
            if s in base_name:
                side = s
                break
        name_no_side = base_name.replace(side, '') if side else base_name
        name_no_side = re.sub(r'\d+$', '', name_no_side)
        is_default = True

    rev_map = {'LFT': 'RGT', 'RGT': 'LFT', 'L': 'R', 'R': 'L', 'C': 'C'}
    rev_side = rev_map.get(side, None)
    name_rev = base_name.replace(side, rev_side) if (side and rev_side) else None
    return base_name, side, rev_side, is_default, name_no_side, name_rev


# ------------------------------------------------------------------------------
# Hierarchy & Controller Helpers
# ------------------------------------------------------------------------------
def parentShape(source, target):
    shapes = mc.listRelatives(str(source), shapes=True) or []
    for s in shapes:
        mc.parent(s, str(target), relative=True, shape=True)
    if mc.objExists(str(source)):
        mc.delete(str(source))

def createGimbal(ctrl):
    ctrl_obj = Dag(ctrl)
    sp_name = check_name_style(ctrl_obj.name)
    gmbl_name = f"{sp_name[0]}_gmbCtrl"
    tmp_ctrl = mc.duplicate(ctrl_obj.name, rr=True)[0]

    ctrl_obj.addAttribute(ln='gimbal', min=0, max=1, k=True)
    gmbl_ctrl = Null(gmbl_name)
    parentShape(tmp_ctrl, gmbl_ctrl.name)

    gmbl_ctrl.snap(ctrl_obj)
    gmbl_ctrl.parent(ctrl_obj)
    gmbl_ctrl.editCtrlShape(axis=0.75)
    gmbl_ctrl.color = 'white'

    gmbl_shape = Dag(gmbl_ctrl.shape)
    ctrl_obj.attr('gimbal') >> gmbl_shape.attr('v')
    gmbl_ctrl.attr('v').lockHide()
    return gmbl_ctrl

def zroNewGrpWithOffset(child):
    child_dag = Dag(child)
    base_name = check_name_style(child_dag.name)[0]
    zro_grp = Null(f"{base_name}Zro_grp")
    offset_grp = Null(f"{base_name}Offset_grp")

    zro_grp.rotateOrder = child_dag.rotateOrder
    offset_grp.rotateOrder = child_dag.rotateOrder

    offset_grp.parent(zro_grp)
    zro_grp.snap(child_dag)
    child_dag.parent(offset_grp)
    return zro_grp, offset_grp

def zroGrpWithOffset(child):
    child_dag = Dag(child)
    base_name = check_name_style(child_dag.name)[0]
    zro_grp = Null(f"{base_name}Zro_grp")
    offset_grp = Null(f"{base_name}Offset_grp")

    offset_grp.parent(zro_grp)
    zro_grp.snap(child_dag)
    child_dag.parent(offset_grp)
    return zro_grp

def jointAt(obj, orient=True):
    target = Dag(obj)
    jnt = Joint(scaleCompensate=False)
    if orient:
        jnt.maSnap(target)
    else:
        jnt.maSnap(target, pos=True, rot=False, scl=True)
    jnt.freeze(r=True, s=True)
    jnt.rotateOrder = target.rotateOrder
    jnt.attr('segmentScaleCompensate').value = 0
    return jnt


# ------------------------------------------------------------------------------
# Matrix Constraints
# ------------------------------------------------------------------------------
def _getLocalOffset(source, target):
    source_mat_list = mc.xform(str(source), q=True, ws=True, m=True)
    target_mat_list = mc.xform(str(target), q=True, ws=True, m=True)
    source_mat = om.MMatrix(source_mat_list)
    target_mat = om.MMatrix(target_mat_list)
    offset_mat = target_mat * source_mat.inverse()
    return list(offset_mat)

def parentConMatrixGPT(source, target, mo=True, translate=True, rotate=True, scale=True, baseName=None):
    if not source or not target:
        return False

    obj_target = Dag(target)
    obj_source = Dag(source)
    base_name = baseName or check_name_style(obj_target.name)[0]
    off_mat = _getLocalOffset(source, target)

    decompose_mat = DecomposeMatrix(base_name)
    mult_mat = MultMatrix(base_name)
    pick_mat = PickMatrix(base_name)

    if mo:
        mc.setAttr(f"{mult_mat.name}.matrixIn[0]", off_mat, type='matrix')

    if rotate:
        target_euler_to_quat = EulerToQuat(base_name)
        target_quat_invert = QuatInvert(base_name)
        target_quat_prod = QuatProd(base_name)
        target_quat_to_euler = QuatToEuler(base_name)

        if obj_target.type == 'joint':
            mc.connectAttr(f"{obj_target.name}.jointOrient", f"{target_euler_to_quat.name}.inputRotate")
            target_euler_to_quat.attr('outputQuat') >> target_quat_invert.attr('inputQuat')
            decompose_mat.attr('outputQuat') >> target_quat_prod.attr('input1Quat')
            target_quat_invert.attr('outputQuat') >> target_quat_prod.attr('input2Quat')
            target_quat_prod.attr('outputQuat') >> target_quat_to_euler.attr('inputQuat')
            target_quat_to_euler.attr('outputRotate') >> obj_target.attr('rotate')
        else:
            decompose_mat.attr('outputRotate') >> obj_target.attr('rotate')

        source_rot_order = mc.getAttr(f"{obj_source.name}.rotateOrder")
        obj_target.attr('rotateOrder').value = source_rot_order
        if obj_target.type == 'joint':
            obj_target.attr('rotateOrder') >> target_quat_to_euler.attr('inputRotateOrder')

    obj_source.attr('worldMatrix[0]') >> mult_mat.attr('matrixIn[2]')

    parent_nodes = mc.listRelatives(obj_target.name, parent=True)
    if parent_nodes:
        parent = parent_nodes[0]
        mc.connectAttr(f"{parent}.worldInverseMatrix[0]", f"{mult_mat.name}.matrixIn[3]", force=True)

    mult_mat.attr('matrixSum') >> pick_mat.attr('inputMatrix')
    pick_mat.attr('outputMatrix') >> decompose_mat.attr('inputMatrix')

    if not translate:
        pick_mat.attr('useTranslate').value = 0
    if not rotate:
        pick_mat.attr('useRotate').value = 0
    if not scale:
        pick_mat.attr('useScale').value = 0

    if translate:
        decompose_mat.attr('outputTranslate') >> obj_target.attr('translate')
    if scale:
        decompose_mat.attr('outputScale') >> obj_target.attr('scale')

    return obj_target, obj_source


# ------------------------------------------------------------------------------
# Controller Box Generator
# ------------------------------------------------------------------------------
def creControllerFunc(selected=[], scale=1, ctrlShape='circle_ctrlShape', color='yellow',
                      constraint=True, matrixConst=False, mo=False, translate=True,
                      rotate=True, scaleConstraint=True, rotateOrder='xzy', parentUnder=False,
                      parentTo=False, priorJnt=False, baseName=None):
    if not selected:
        mc.warning("creControllerFunc: Please select or pass targets.")
        return []

    if isinstance(selected, str):
        selected = [selected]

    if priorJnt and mc.objExists(priorJnt):
        mc.parent(selected[0], priorJnt)

    return_list = []
    for i, each in enumerate(selected):
        if baseName:
            if isinstance(baseName, (list, tuple)):
                raw_name = baseName[i] if i < len(baseName) else baseName[-1]
            elif len(selected) > 1:
                raw_name = f"{baseName}{i+1:02d}"
            else:
                raw_name = str(baseName)
            if raw_name.endswith('_ctrl'):
                raw_name = raw_name[:-5]
        else:
            raw_name = check_name_style(each)[0]

        child_ctrl = Dag(f"{raw_name}_ctrl")
        child_ctrl.nmCreateController(ctrlShape)
        child_ctrl.editCtrlShape(axis=scale * 1.2)
        child_ctrl.color = color
        child_ctrl.rotateOrder = rotateOrder

        gimbal_ctrl = createGimbal(child_ctrl)

        child_zro_grp = zroGrpWithOffset(child_ctrl)
        child_zro_grp.matchPosition(each)
        child_zro_grp.matchRotation(each)

        return_list.append(child_zro_grp.name)
        return_list.append(child_ctrl.name)
        return_list.append(gimbal_ctrl.name)

        child_ctrl.rotateOrder = rotateOrder
        gimbal_ctrl.rotateOrder = rotateOrder

        if constraint:
            if not matrixConst:
                par_con = mc.parentConstraint(gimbal_ctrl.name, each, mo=mo)[0]
                mc.rename(par_con, f"{raw_name}_parCons")
                scl_con = mc.scaleConstraint(gimbal_ctrl.name, each, mo=mo)[0]
                mc.rename(scl_con, f"{raw_name}_scalCons")
            else:
                parentConMatrixGPT(gimbal_ctrl.name, each, mo=mo, translate=translate,
                                   rotate=rotate, scale=scaleConstraint)

        if parentUnder:
            mc.parent(child_zro_grp.name, each)
        if parentTo and mc.objExists(parentTo):
            mc.parent(child_zro_grp.name, parentTo)

    return return_list


# ------------------------------------------------------------------------------
# FK Omni Rig with Master Curl Controller
# ------------------------------------------------------------------------------
def fkRig_omni_newCurl(nameSpace='', parentCtrlTo='', jntLst=(), charScale=1.0,
                       priorJnt='', side='LFT', ctrlShape='circle_ctrlShape',
                       localWorld=False, color='yellow', curlCtrl=True,
                       curlPosiAtFirst=False, rotateOrder='zxy', parentToPriorJnt=False,
                       parentMatrix=False, curlCtrlShape='stick_ctrlShape',
                       constraintCurl=True, isTmpJnt=False, suffix='_bJnt'):
    naming_style = check_name_style(name=jntLst[0])
    name = naming_style[0]
    name_no_side = naming_style[4]
    old_name_style = naming_style[3]

    part = f"{nameSpace}{name_no_side}{side}" if old_name_style else f"{nameSpace}{name}"
    rig_grp = Null(f"{part}Rig_grp")

    ctrls, jnts, gmbls, z_grps, b_jnts, of_grps = [], [], [], [], [], []

    for num in range(len(jntLst)):
        base_name = check_name_style(name=jntLst[num])[0]
        ctrl = Dag(f"{base_name}_ctrl")
        ctrl.nmCreateController(ctrlShape)
        ctrl.editCtrlShape(axis=charScale * 6.4)

        gimbal = createGimbal(ctrl)

        if isTmpJnt:
            tmp = Dag(jntLst[num])
            b_jnt = jointAt(tmp.name)
            b_jnt.name = f"{base_name}{suffix}"
        else:
            b_jnt = Dag(jntLst[num])

        zro_grp, offset_grp = zroNewGrpWithOffset(ctrl)
        zro_grp.snap(b_jnt)
        zro_grp.name = f"{base_name}Zro_grp"
        offset_grp.name = f"{base_name}Offset_grp"

        ctrl.rotateOrder = rotateOrder
        gimbal.rotateOrder = rotateOrder
        ctrl.color = color

        ctrls.append(ctrl)
        jnts.append(jntLst[num])
        gmbls.append(gimbal)
        z_grps.append(zro_grp)
        b_jnts.append(b_jnt)
        of_grps.append(offset_grp)

        if num != 0:
            zro_grp.parent(gmbls[num - 1])
            if isTmpJnt:
                b_jnt.parent(b_jnts[num - 1])
        else:
            rig_grp.maSnap(b_jnts[0])
            zro_grp.parent(rig_grp)

    if parentCtrlTo and mc.objExists(parentCtrlTo):
        rig_grp.parent(parentCtrlTo)
    if priorJnt and mc.objExists(priorJnt):
        b_jnts[0].parent(priorJnt)

    if curlCtrl:
        if old_name_style:
            curl_base_name = f"{nameSpace}{name_no_side}Curl{side}"
        else:
            curl_base_name = f"{side}_{nameSpace}{name_no_side}Curl" if side else f"{nameSpace}{name_no_side}Curl"

        curl_ctrl = Dag(f"{curl_base_name}_ctrl")
        curl_ctrl.nmCreateController(curlCtrlShape)
        curl_ctrl.editCtrlShape(axis=charScale * 7.4)
        curl_ctrl.color = color
        zro_grp_curl, offset_curl = zroNewGrpWithOffset(curl_ctrl)
        curl_ctrl.rotateOrder = rotateOrder

        bjnt_to_snap = b_jnts[0] if curlPosiAtFirst else b_jnts[-1]
        zro_grp_curl.maSnap(bjnt_to_snap)

        curl_shape_ctrl = Dag(curl_ctrl.shape)
        curl_shape_ctrl.addAttribute(at='long', min=0, max=1, longName='Detail', keyable=True, defaultValue=0)
        mc.connectAttr(f"{curl_shape_ctrl.name}.Detail", f"{z_grps[0].name}.visibility", f=True)
        curl_ctrl.lockHideAttrLst('tx', 'ty', 'tz', 'sx', 'sy', 'sz')

        pass_val_pma = PlusMinusAverage(f"{curl_base_name}_pma")
        mul_val_mdv = MultiplyDivine(f"{curl_base_name}_mdv")

        curl_ctrl.attr('rotate') >> pass_val_pma.attr('input3D[0]')
        pass_val_pma.attr('output3D') >> mul_val_mdv.attr('input1')

        fk_meta = MetaGeneric(f"{curl_base_name}_meta")
        fk_meta.addAttribute(attributeType='message', longName=curl_base_name)
        fk_meta.addAttribute(attributeType='message', longName='passValue')
        fk_meta.addAttribute(attributeType='message', longName='Rig_Prior')
        pass_val_pma.attr('message') >> fk_meta.attr('passValue')
        curl_ctrl.attr('message') >> fk_meta.attr('Rig_Prior')

        for each_of_grp in of_grps:
            mul_val_mdv.attr('output') >> each_of_grp.attr('rotate')

        zro_grp_curl.parent(rig_grp)

        if constraintCurl:
            curl_par_con = mc.parentConstraint(bjnt_to_snap.name, zro_grp_curl.name, mo=False)[0]
            mc.rename(curl_par_con, f"{curl_base_name}_parCons")

    if parentMatrix:
        for num in range(len(jntLst)):
            parentConMatrixGPT(gmbls[num].name, b_jnts[num].name, mo=True, translate=True, rotate=True, scale=True)
    else:
        for num in range(len(jntLst)):
            mc.parentConstraint(gmbls[num].name, b_jnts[num].name, mo=True)

    if curlCtrl:
        return gmbls[0], rig_grp.name, b_jnts, zro_grp_curl.name, ctrls, curl_ctrl.name, z_grps, fk_meta.name
    else:
        return gmbls[0], rig_grp.name, b_jnts, ctrls


# ------------------------------------------------------------------------------
# Pin Locator to Surface (Pure Maya Native - Zero PyMEL Dependency)
# ------------------------------------------------------------------------------
def pin_locator_surface(nurbs='glue_nrb', region='ribCage', side='', source_loc=(),
                        locator_scale=1.0, creJnt=False, suffixJnt='pxyJnt',
                        creCtrl=False, ctrlShape='circle_ctrlShape', snapAtEnd=False,
                        priorJnt='', scale=20):
    if not source_loc:
        mc.error("pin_locator_surface: Need source locators to pinpoint locations.")

    shapes = mc.listRelatives(nurbs, shapes=True) or []
    nurb_shape = shapes[0] if shapes else nurbs

    min_u = mc.getAttr(f"{nurb_shape}.minValueU")
    max_u = mc.getAttr(f"{nurb_shape}.maxValueU")
    min_v = mc.getAttr(f"{nurb_shape}.minValueV")
    max_v = mc.getAttr(f"{nurb_shape}.maxValueV")

    meta_node = MetaBlank(f"{region}_driveAllValue_meta")
    meta_node.addAttribute(attributeType='float', longName='slide_path', minValue=0, maxValue=1, defaultValue=1, keyable=True)

    locator_list = []
    jnt_list = []
    ctrl_list = []

    for each in source_loc:
        base_name = check_name_style(each)[0]

        source_pos = mc.xform(each, q=True, ws=True, t=True)
        cp_node = mc.createNode('closestPointOnSurface')
        mc.connectAttr(f"{nurb_shape}.worldSpace[0]", f"{cp_node}.inputSurface", force=True)
        mc.setAttr(f"{cp_node}.inPositionX", source_pos[0])
        mc.setAttr(f"{cp_node}.inPositionY", source_pos[1])
        mc.setAttr(f"{cp_node}.inPositionZ", source_pos[2])

        u_pos = mc.getAttr(f"{cp_node}.parameterU")
        v_pos = mc.getAttr(f"{cp_node}.parameterV")
        mc.delete(cp_node)

        p_name = each
        mc.delete(each)
        loc = mc.spaceLocator(n=p_name)[0]
        loc_shape = mc.listRelatives(loc, shapes=True)[0]

        mc.addAttr(loc_shape, ln='parameterU', at='double', k=True, dv=u_pos)
        mc.addAttr(loc_shape, ln='parameterV', at='double', k=True, dv=v_pos)
        mc.setAttr(f"{loc_shape}.localScaleX", locator_scale)
        mc.setAttr(f"{loc_shape}.localScaleY", locator_scale)
        mc.setAttr(f"{loc_shape}.localScaleZ", locator_scale)

        mc.addAttr(f"{loc_shape}.parameterU", edit=True, min=min_u, max=max_u)
        mc.addAttr(f"{loc_shape}.parameterV", edit=True, min=min_v, max=max_v)

        point_on_surface = mc.createNode('pointOnSurfaceInfo', name=f"{base_name}_poiInfo")
        mc.connectAttr(f"{nurb_shape}.worldSpace[0]", f"{point_on_surface}.inputSurface", force=True)
        mc.connectAttr(f"{loc_shape}.parameterU", f"{point_on_surface}.parameterU", force=True)
        mc.connectAttr(f"{loc_shape}.parameterV", f"{point_on_surface}.parameterV", force=True)

        mc.setAttr(f"{loc_shape}.overrideEnabled", 1)
        mc.setAttr(f"{loc_shape}.overrideColor", 16)

        mtx = mc.createNode('fourByFourMatrix', name=f"{base_name}_fbfMat")
        out_matrix = mc.createNode('decomposeMatrix', name=f"{base_name}_deCom")
        mc.connectAttr(f"{mtx}.output", f"{out_matrix}.inputMatrix", force=True)
        mc.connectAttr(f"{out_matrix}.outputTranslate", f"{loc}.translate", force=True)
        mc.connectAttr(f"{out_matrix}.outputRotate", f"{loc}.rotate", force=True)

        mc.connectAttr(f"{point_on_surface}.normalizedTangentUX", f"{mtx}.in00", force=True)
        mc.connectAttr(f"{point_on_surface}.normalizedTangentUY", f"{mtx}.in01", force=True)
        mc.connectAttr(f"{point_on_surface}.normalizedTangentUZ", f"{mtx}.in02", force=True)
        mc.setAttr(f"{mtx}.in03", 0.0)

        mc.connectAttr(f"{point_on_surface}.normalizedNormalX", f"{mtx}.in10", force=True)
        mc.connectAttr(f"{point_on_surface}.normalizedNormalY", f"{mtx}.in11", force=True)
        mc.connectAttr(f"{point_on_surface}.normalizedNormalZ", f"{mtx}.in12", force=True)
        mc.setAttr(f"{mtx}.in13", 0.0)

        mc.connectAttr(f"{point_on_surface}.normalizedTangentVX", f"{mtx}.in20", force=True)
        mc.connectAttr(f"{point_on_surface}.normalizedTangentVY", f"{mtx}.in21", force=True)
        mc.connectAttr(f"{point_on_surface}.normalizedTangentVZ", f"{mtx}.in22", force=True)
        mc.setAttr(f"{mtx}.in23", 0.0)

        mc.connectAttr(f"{point_on_surface}.positionX", f"{mtx}.in30", force=True)
        mc.connectAttr(f"{point_on_surface}.positionY", f"{mtx}.in31", force=True)
        mc.connectAttr(f"{point_on_surface}.positionZ", f"{mtx}.in32", force=True)
        mc.setAttr(f"{mtx}.in33", 1.0)

        locator_list.append(p_name)

        add_val_mdl = MultiDoubleLinear(f"{base_name}_mdl")
        meta_node.attr('slide_path') >> add_val_mdl.attr('input1')
        add_val_mdl.attr('input2').value = u_pos
        mc.connectAttr(f"{add_val_mdl.name}.output", f"{loc_shape}.parameterU", force=True)

        if creJnt:
            child_joint = Joint(scaleCompensate=False)
            child_joint.name = f"{base_name}_{suffixJnt}"
            child_joint.maSnap(p_name)
            child_joint.freeze()
            child_joint.attr('segmentScaleCompensate').value = 0
            jnt_list.append(child_joint.name)

            if creCtrl:
                gmb_ctrl = creControllerFunc(selected=[each], scale=scale, ctrlShape=ctrlShape, color='yellow',
                                             constraint=False, matrixConst=False, mo=False, translate=True,
                                             rotate=True, scaleConstraint=True, rotateOrder='xzy', parentUnder=True)[2]
                ctrl_list.append(gmb_ctrl)

    if creJnt and snapAtEnd:
        if not priorJnt or not mc.objExists(priorJnt):
            logger.warning("Snap and parent joint requires an existing priorJoint.")
            return False
        for num in range(1, len(jnt_list)):
            mc.parent(jnt_list[num], jnt_list[num - 1])
        mc.parent(jnt_list[0], priorJnt)

        for num in range(len(jnt_list)):
            par_con = mc.parentConstraint(ctrl_list[num], jnt_list[num])[0]
            base_name = check_name_style(source_loc[num])[0]
            mc.rename(par_con, f"{base_name}_parCons")

    return locator_list


# ------------------------------------------------------------------------------
# De Boor Spline & Smooth Weight Distribution to Mesh
# ------------------------------------------------------------------------------
def get_open_uniform_kv(n, d):
    return [0.0] * (d + 1) + [(i - d) / float(n - d) for i in range(d + 1, n)] + [1.0] * (d + 1)

def get_periodic_uniform_kv(n, d):
    inv = 1.0 / float(n + d)
    return [-inv * a for a in range(d, 0, -1)] + [inv * a for a in range(n + d + 1)] + [inv * a + 1.0 for a in range(1, d + 1)]

def knot_vector(kv_type, cvs, d):
    cvs_copy = list(cvs)
    if kv_type == 'open':
        kv = get_open_uniform_kv(len(cvs), d)
    else:
        kv = get_periodic_uniform_kv(len(cvs), d)
        for i in range(d):
            cvs_copy.insert(0, cvs[len(cvs) - i - 1])
            cvs_copy.append(cvs[i])
    return kv, cvs_copy

def de_boor(n, d, t, kv, tol=0.000001):
    if t + tol >= 1.0:
        return [0.0 if i != n - 1 else 1.0 for i in range(n)]

    weights = [1.0 if kv[i] <= t < kv[i + 1] else 0.0 for i in range(n + d)]
    basis_width = n + d - 1

    for degree in range(1, d + 1):
        for i in range(basis_width):
            if weights[i] == 0.0 and weights[i + 1] == 0.0:
                continue
            a_denom = kv[i + degree] - kv[i]
            b_denom = kv[i + degree + 1] - kv[i + 1]
            a = (t - kv[i]) * weights[i] / a_denom if a_denom != 0.0 else 0.0
            b = (kv[i + degree + 1] - t) * weights[i + 1] / b_denom if b_denom != 0.0 else 0.0
            weights[i] = a + b
        basis_width -= 1

    return weights[:n]

def _check_and_fix_joint_order(jnts, crv):
    if not jnts or not crv:
        return jnts
    jnt_start = mc.xform(jnts[0], q=True, ws=True, t=True)
    cv_start = mc.pointPosition(f"{crv}.cv[0]", w=True)
    cv_end = mc.pointPosition(f"{crv}.cv[-1]", w=True)

    def dist(a, b):
        return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5

    dist_start = dist(cv_start, jnt_start)
    dist_end = dist(cv_end, jnt_start)
    if dist_end < dist_start:
        logger.info("[DeBoor] Auto-reversing joint list to match curve direction.")
        return jnts[::-1]
    return jnts

def list_joints_from_skincluster(skincluster):
    if not mc.objExists(skincluster):
        raise RuntimeError(f"SkinCluster '{skincluster}' does not exist.")
    return mc.skinCluster(skincluster, q=True, inf=True)

def split_with_curve_to_mesh_V2(verts, jnts, crv, d=3, tol=0.1):
    original_sel = om.MGlobal.getActiveSelectionList()
    verts = mc.ls(mc.polyListComponentConversion(verts, toVertex=True), fl=True)
    if not verts:
        return

    d = len(jnts) - 1 if d is None else d
    jnts = _check_and_fix_joint_order(jnts, crv)

    curve_degree = mc.getAttr(f"{crv}.degree")
    crv_spans = mc.getAttr(f"{crv}.spans")
    form_val = mc.getAttr(f"{crv}.form")
    kv_type = 'periodic' if form_val == 2 else 'open'

    kv, modified_jnts = knot_vector(kv_type, jnts, d)

    vert_pa = om.MPointArray([om.MPoint(mc.xform(v, q=True, ws=True, t=True)) for v in verts])

    mc.select(verts)
    vert_sl = om.MGlobal.getActiveSelectionList()
    dag, components = vert_sl.getComponent(0)

    hist_nodes = mc.listHistory(dag.fullPathName()) or []
    history = mc.ls(hist_nodes, type='skinCluster') or []
    if not history:
        return
    skin_cluster = history[0]
    mc.skinPercent(skin_cluster, pruneWeights=tol)

    skin_cluster_sl = om.MGlobal.getSelectionListByName(skin_cluster)
    skin_cluster_obj = skin_cluster_sl.getDependNode(0)
    skin_cluster_fn = oma.MFnSkinCluster(skin_cluster_obj)

    influence_dpa = skin_cluster_fn.influenceObjects()
    influences_names = [i.partialPathName() for i in influence_dpa]
    influences_ia = om.MIntArray(range(len(influence_dpa)))
    jnt_indices = [influences_names.index(jnt) for jnt in jnts if jnt in influences_names]

    skin_wts = skin_cluster_fn.getWeights(dag, components, influences_ia)
    jnts_total_wts = [sum(skin_wts[jnt_index + i * len(influence_dpa)] for jnt_index in jnt_indices)
                      for i in range(len(verts))]

    crv_sl = om.MGlobal.getSelectionListByName(crv)
    crv_dp = crv_sl.getDagPath(0)
    crv_fn = om.MFnNurbsCurve(crv_dp)
    curve_length = crv_fn.length()

    for vert_p, jnts_total_wt, i in zip(vert_pa, jnts_total_wts, range(len(verts))):
        if jnts_total_wt < tol:
            continue

        _, t = crv_fn.closestPoint(vert_p)
        if curve_degree == 1:
            t_n = t / float(crv_spans)
        else:
            arc_len_at_t = crv_fn.findLengthFromParam(t)
            t_n = arc_len_at_t / float(curve_length)

        if kv_type == 'periodic':
            t_n = (kv[d + 1] * (d * 0.5 + 0.5)) * (1.0 - t_n) + t_n * (1.0 - kv[d + 1] * (d * 0.5 - 0.5))

        wts = de_boor(len(modified_jnts), d, t_n, kv, tol=tol)

        if kv_type == 'periodic':
            consolidated_wts = {jnt: 0.0 for jnt in jnts}
            for j_idx, wt in enumerate(wts):
                consolidated_wts[modified_jnts[j_idx]] += wt
            wts = list(consolidated_wts.values())

        jnts_wts = [wt * jnts_total_wt for wt in wts]

        for j_idx, jnt_index in enumerate(jnt_indices):
            skin_wts[jnt_index + i * len(influence_dpa)] = jnts_wts[j_idx]

    skin_cluster_fn.setWeights(dag, components, influences_ia, skin_wts)
    om.MGlobal.setActiveSelectionList(original_sel)


# ==============================================================================
# Main Builder Function: fkIkDeformed
# ==============================================================================
def fkIkDeformed(SIDE='C',
                 BASE_NAME='tenTail',
                 SCALE=20,
                 COUNT_DETAIL=24,
                 COUNT_MAIN=9,
                 stickShape='stickCircle_Y_long_ctrlShape',
                 mesh='Body',
                 smoothweight=True,
                 squashDef=True,
                 sineDef=False,
                 makeTwistDef=False,
                 priorJnt='',
                 parentTo='',
                 place_ctrl='',
                 enableTwist=False,
                 forwardAxis='z+',
                 worldUpAxis='y+',
                 worldUpVector=(0, 1, 0),
                 worldUpVectorEnd=(0, 1, 0),
                 worldUpType=4,
                 upObject='C_tenTailStart_ctrl',
                 upObjectEnd='C_tenTailEnd_ctrl'):
    """
    Main Procedural Builder for FK/IK Deformed Tentacle & Tail Rig.
    """
    makeHeader(f"Start Building Tentacle Rig: {SIDE}_{BASE_NAME}")

    # 1. Root Null Groups
    nurbAll_grp = Null(f"{SIDE}_{BASE_NAME}AllNurbe_grp")
    nurbAll_grp.lockAllAttr(attrs=['t', 'r', 's'])

    ik_detail_joints = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_ikJnt", COUNT_DETAIL)
    spine_crv = f"{SIDE}_{BASE_NAME}_ikSpine_crv"
    ik_nrb = f"{SIDE}_{BASE_NAME}_ik_nrb"

    if not mc.objExists(ik_nrb):
        mc.error(f"[TentacleRig] Guide surface '{ik_nrb}' not found in scene!")
        return False

    shapes = mc.listRelatives(ik_nrb, shapes=True) or []
    if not shapes:
        mc.error(f"[TentacleRig] {ik_nrb} has no shapes.")
        return False

    # 2. Make FK controller chain
    makeHeader('Make FK controller')
    ik_joints = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_masterIk_ikJnt", COUNT_DETAIL)
    bJnts_list = []

    for num in range(COUNT_MAIN):
        ik_jnt = Dag(ik_joints[num])
        fk_jnt = Joint(ik_joints[num].replace('masterIk_ikJnt', 'masterFk_fkJnt'))
        fk_jnt.maSnap(ik_jnt)
        fk_jnt.attr('radius').value = 2
        fk_jnt.setJointColor('gray')
        bJnts_list.append(fk_jnt.name)

    for num in range(1, COUNT_MAIN):
        mc.parent(bJnts_list[num], bJnts_list[num - 1])

    fk_rig = fkRig_omni_newCurl(
        nameSpace='', parentCtrlTo='',
        jntLst=bJnts_list,
        charScale=1 * SCALE, priorJnt='', side=SIDE,
        ctrlShape='ring_ctrlShape', localWorld=False,
        color='yellow', curlCtrl=True, curlPosiAtFirst=False, rotateOrder='zxy',
        parentToPriorJnt=False, parentMatrix=False,
        curlCtrlShape=stickShape
    )

    logger.debug(f"FK Master Curl Control: {fk_rig[5]}")

    # 3. Create IK Spine Controllers
    pattern_ik = f"{SIDE}_{BASE_NAME}{{index}}_masterIk_ikJnt"
    joints_main = [pattern_ik.format(index=str(i).zfill(2)) for i in range(1, COUNT_MAIN + 1)]

    creControllerFunc(
        selected=joints_main, scale=5 * SCALE, ctrlShape='cube_ctrlShape', color='yellow',
        constraint=True, matrixConst=False, mo=False, translate=True,
        rotate=True, scaleConstraint=True, rotateOrder='xzy', parentUnder=False
    )

    master_ik_zroGrp = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_masterIkZro_grp", COUNT_MAIN)
    master_fk_gmbl = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_masterFk_gmbCtrl", COUNT_MAIN)
    for index, each in enumerate(master_fk_gmbl):
        if mc.objExists(master_ik_zroGrp[index]) and mc.objExists(each):
            mc.parent(master_ik_zroGrp[index], each)

    # 4. Create IK Handle
    ik_detail_jnt = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_ikJnt", COUNT_DETAIL)

    ikHandle = DoIkSpline(
        startJoint=ik_detail_jnt[0],
        endEffector=ik_detail_jnt[-1],
        solverType='ikSplineSolver',
        createCurve=False,
        curveName=spine_crv,
        parentCurve=False
    )
    ikHandle.name = f"{SIDE}_{BASE_NAME}_ikh"
    ikHandle.eff = mc.rename(ikHandle.eff, f"{SIDE}_{BASE_NAME}_eff")

    # 5. Skinweight joint to curve & guide nurbs
    logger.info("Skinweight joint to curve")
    skin_crv_name = f"{SIDE}_{BASE_NAME}_ikCrv_skc"
    mc.skinCluster(joints_main, spine_crv, toSelectedBones=True, name=skin_crv_name)

    logger.info("Skinweight joint to ik_nrb curve for match blendshape")
    pattern_detail = f"{SIDE}_{BASE_NAME}{{index}}_ikJnt"
    joints_detail = [pattern_detail.format(index=str(i).zfill(2)) for i in range(1, COUNT_DETAIL + 1)]

    skin_nrb_name = f"{SIDE}_{BASE_NAME}_ikNrb_skc"
    mc.skinCluster(joints_detail, ik_nrb, toSelectedBones=True, name=skin_nrb_name)

    # 6. BlendShape ik nurbs to combine nurbs
    combineFkIk_nrb = mc.duplicate(ik_nrb, n=ik_nrb.replace('ik', 'combineFkIk'))[0]
    mc.blendShape(ik_nrb, combineFkIk_nrb, frontOfChain=True, name=f"{SIDE}_{BASE_NAME}_bsh", w=[(0, 1)])

    # 7. Create Detail Joint & Pin to Surface
    makeHeader('Create Detail Joint')
    locs = generate_named_pattern(f"{SIDE}_{BASE_NAME}_detail##_loc", COUNT_DETAIL)

    for num in range(COUNT_DETAIL):
        locator = Locator(locs[num])
        ik_j = Dag(ik_detail_jnt[num])
        locator.maSnap(ik_j)

    pin_locator_surface(
        nurbs=combineFkIk_nrb,
        region=f"{BASE_NAME}_combineFkik",
        side=SIDE,
        source_loc=locs,
        locator_scale=1 * SCALE,
        creJnt=True, suffixJnt='pxyJnt',
        creCtrl=True, ctrlShape='circle_Y_along_ctrlShape',
        snapAtEnd=False,
        priorJnt='',
        scale=20
    )

    detail_gmbl_ctrl = generate_named_pattern(f"{SIDE}_{BASE_NAME}_detail##_gmbCtrl", COUNT_DETAIL)
    detail_jnt = generate_named_pattern(f"{SIDE}_{BASE_NAME}_detail##_pxyJnt", COUNT_DETAIL)

    for num in range(COUNT_DETAIL):
        if mc.objExists(detail_jnt[num]) and mc.objExists(detail_gmbl_ctrl[num]):
            mc.parent(detail_jnt[num], detail_gmbl_ctrl[num])

    # 8. Create Bind Joint from Detail Joint
    bind_jnt_list = generate_named_pattern(f"{SIDE}_{BASE_NAME}_detail##_bJnt", COUNT_DETAIL)
    for index, each in enumerate(bind_jnt_list):
        pxy_jnt = Dag(detail_jnt[index])
        bind_jnt = jointAt(pxy_jnt)
        bind_jnt.attr('radius').value = 0.5
        bind_jnt.name = each

    for i in range(1, len(bind_jnt_list)):
        mc.parent(bind_jnt_list[i], bind_jnt_list[i - 1])

    if mc.objExists(mesh):
        skin_cluster = mc.skinCluster(bind_jnt_list, mesh, toSelectedBones=True, name=f"{SIDE}_{BASE_NAME}{mesh}_skc")[0]
    else:
        skin_cluster = None
        logger.warning(f"Target mesh '{mesh}' does not exist in scene, skipping skinCluster.")

    jntPxy_list = generate_named_pattern(f"{SIDE}_{BASE_NAME}_detail##_pxyJnt", COUNT_DETAIL)

    if priorJnt and mc.objExists(priorJnt):
        mc.parent(bind_jnt_list[0], priorJnt)
        for index, each in enumerate(bind_jnt_list):
            parentConMatrixGPT(jntPxy_list[index], each, mo=True, translate=True, rotate=True, scale=True)

    detail_grp = Null(f"{SIDE}_{BASE_NAME}_detailJnt_grp")
    detail_grp.lockAllAttr(attrs=['t', 'r', 's'])
    detail_loc = generate_named_pattern(f"{SIDE}_{BASE_NAME}_detail##_loc", COUNT_DETAIL)

    for each in detail_loc:
        if mc.objExists(each):
            mc.parent(each, detail_grp.name)

    # 9. Split Weight to Mesh via De Boor
    if skin_cluster and mc.objExists(mesh):
        if smoothweight is True:
            jnts = list_joints_from_skincluster(skin_cluster)
            split_with_curve_to_mesh_V2(mesh, jnts, spine_crv, d=3, tol=0.1)
        elif smoothweight == 'reverse':
            jnts = list_joints_from_skincluster(skin_cluster)[::-1]
            split_with_curve_to_mesh_V2(mesh, jnts, spine_crv, d=3, tol=0.1)

    # 10. Make Stretchy using ArcLength
    stick_ctrl = Dag(fk_rig[5])
    stick_ctrlShape = Dag(stick_ctrl.shape)
    stick_ctrlShape.addAttribute(attributeType='float', longName='stretchy', minValue=0, maxValue=1, defaultValue=1, keyable=True)

    curveInfo = CurveInfo(f"{SIDE}_{BASE_NAME}")
    spine_crv_dag = Dag(spine_crv)
    spine_crv_dag.attr('worldSpace[0]') >> curveInfo.attr('inputCurve')

    crv_length = curveInfo.attr('arcLength').value
    length_ratio_mdv = MultiplyDivineWithVal(f"{SIDE}_{BASE_NAME}_length_ratio_mdv", 2)
    curveInfo.attr('arcLength') >> length_ratio_mdv.attr('input1X')
    length_ratio_mdv.attr('input2X').value = crv_length
    length_ratio_mdv.attr('input1Y').value = 1
    length_ratio_mdv.setLocked('input2X')
    length_ratio_mdv.setLocked('input1Y')
    length_ratio_mdv.setLocked('input2Y')

    length_store = MultiDoubleLinear(f"{SIDE}_{BASE_NAME}_length_store")
    length_store.attr('input2').value = 1
    envelope_bta = BlendTwoAttr(f"{SIDE}_{BASE_NAME}_length_store")
    length_ratio_mdv.attr('outputY') >> envelope_bta.attr('input[0]')
    length_ratio_mdv.attr('outputX') >> envelope_bta.attr('input[1]')
    envelope_bta.attr('output') >> length_store.attr('input1')

    minorIK_jnt_list = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_ikJnt", COUNT_DETAIL)

    for index, each in enumerate(minorIK_jnt_list):
        minorIK_jnt = Dag(each)
        baseName = check_name_style(each)[0]
        
        # Root joint should not stretch along its translate (it moves the whole chain in space)
        if index == 0:
            continue
            
        tx = mc.getAttr(f"{each}.translateX")
        ty = mc.getAttr(f"{each}.translateY")
        tz = mc.getAttr(f"{each}.translateZ")
        
        axes = {'X': tx, 'Y': ty, 'Z': tz}
        primary_axis = max(axes, key=lambda k: abs(axes[k]))
        axis_val = axes[primary_axis]
        
        multiStartVal_adl = MDLWithMul(f"{baseName}_stretch", dv=axis_val)
        length_store.attr('output') >> multiStartVal_adl.attr('input1')
        multiStartVal_adl.attr('output') >> minorIK_jnt.attr(f'translate{primary_axis}')

    stick_ctrl.attr('stretchy') >> envelope_bta.attr('attributesBlender')

    # 11. Make Squash Tentacle (Optional)
    if squashDef:
        squash_nrb = mc.duplicate(ik_nrb, n=ik_nrb.replace('ik', 'squash'))[0]
        squash_loc_list = generate_named_pattern(f"{SIDE}_{BASE_NAME}Squash##_loc", COUNT_DETAIL)

        mc.parent(squash_nrb, nurbAll_grp.name)

        for num in range(COUNT_DETAIL):
            locator = Locator(squash_loc_list[num])
            ik_j = Dag(ik_detail_jnt[num])
            locator.maSnap(ik_j)

        pin_locator_surface(
            nurbs=squash_nrb,
            region=f"{BASE_NAME}Squash",
            side=SIDE,
            source_loc=squash_loc_list,
            locator_scale=1 * SCALE,
            creJnt=False, suffixJnt='pxyJnt',
            creCtrl=False, ctrlShape='circle_Y_along_ctrlShape',
            snapAtEnd=False,
            priorJnt='',
            scale=20
        )

        for ch in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
            mc.setAttr(f"{SIDE}_{BASE_NAME}_squash_nrb.{ch}", lock=False)

        mc.setAttr(f"{squash_nrb}.rotateX", 90)
        mc.setAttr(f"{squash_nrb}.rotateZ", 180)
        mc.setAttr(f"{squash_nrb}.rotateY", 0)
        mc.setAttr(f"{squash_nrb}.translateX", 0)
        mc.setAttr(f"{squash_nrb}.translateY", 0)
        mc.setAttr(f"{squash_nrb}.translateZ", 0)

        squash_meta = MetaBlank(f"{SIDE}_{BASE_NAME}_squash_xVal")
        squash_deformer, squash_handle = mc.nonLinear(squash_nrb, type='squash', name=f"{SIDE}_{BASE_NAME}_squash_deformer")

        for index, each in enumerate(squash_loc_list):
            mc.setAttr(f"{each}Shape.parameterV", 1)
            baseName = check_name_style(squash_loc_list[index])[0]
            multi01 = MDLWithMul(f"{baseName}_multiply", dv=0.1)
            plus01 = AddDoubleLinear(f"{baseName}_plus01", input2=1)

            multi01.attr('output') >> plus01.attr('input1')
            squash_meta.addAttribute(attributeType='float', longName=f"squash_{index+1:02}",
                                     minValue=-100, maxValue=100, defaultValue=0, keyable=True)
            squash_loc = Dag(each)
            squash_loc.attr('translateX') >> multi01.attr('input1')
            plus01.attr('output') >> squash_meta.attr(f"squash_{index+1:02}")

            if not place_ctrl or not mc.objExists(place_ctrl):
                pxy_j = Dag(jntPxy_list[index])
                squash_meta.attr(f"squash_{index+1:02}") >> pxy_j.attr('scaleX')
                squash_meta.attr(f"squash_{index+1:02}") >> pxy_j.attr('scaleZ')

        if place_ctrl and mc.objExists(place_ctrl):
            placeObj_ctrl = Dag(place_ctrl)
            minusOne_pma = PlusMinusAverage(f"{SIDE}_{BASE_NAME}_minusOne")
            minusOne_pma.attr('operation').value = 2
            placeObj_ctrl.attr('scaleX') >> minusOne_pma.attr('input3D[0].input3Dx')
            placeObj_ctrl.attr('scaleY') >> minusOne_pma.attr('input3D[0].input3Dy')
            placeObj_ctrl.attr('scaleZ') >> minusOne_pma.attr('input3D[0].input3Dz')

            minusOne_pma.attr('input3D[1].input3Dx').value = 1
            minusOne_pma.attr('input3D[1].input3Dy').value = 1
            minusOne_pma.attr('input3D[1].input3Dz').value = 1

            for index, each in enumerate(squash_loc_list):
                storeValue = PlusMinusAverage(f"{SIDE}_{BASE_NAME}_storeValue{index+1:02}")
                storeValue.attr('input3D[1].input3Dy').value = 1

                minusOne_pma.attr('output3Dx') >> storeValue.attr('input3D[0].input3Dx')
                minusOne_pma.attr('output3Dy') >> storeValue.attr('input3D[0].input3Dy')
                minusOne_pma.attr('output3Dz') >> storeValue.attr('input3D[0].input3Dz')

                squash_meta.attr(f"squash_{index+1:02}") >> storeValue.attr('input3D[1].input3Dx')
                squash_meta.attr(f"squash_{index+1:02}") >> storeValue.attr('input3D[1].input3Dz')

                detailObj_loc = Dag(detail_loc[index])
                storeValue.attr('output3Dx') >> detailObj_loc.attr('scaleX')
                storeValue.attr('output3Dy') >> detailObj_loc.attr('scaleY')
                storeValue.attr('output3Dz') >> detailObj_loc.attr('scaleZ')

        offset_X = squash_loc.attr('translateX').value
        mc.setAttr(f"{squash_handle}.translateX", offset_X * -2)
        mc.setAttr(f"{squash_nrb}.translateX", offset_X * -1)

        squashLoc_list = generate_named_pattern(f"{SIDE}_{BASE_NAME}Squash##_loc", COUNT_DETAIL)
        squash_grp = Null(f"{SIDE}_{BASE_NAME}_squashLoc_grp")
        squash_grp.lockAllAttr(attrs=['t', 'r', 's'])

        for each in squashLoc_list:
            if mc.objExists(each):
                mc.parent(each, squash_grp.name)
        mc.parent(squash_handle, squash_grp.name)

        stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_Squash:", longName='Squash')
        stick_ctrlShape.addAttribute(attributeType='float', longName='factor', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='expan', minValue=-1, maxValue=2, defaultValue=1, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='expan_pos', minValue=0.02, maxValue=0.90, defaultValue=0.8, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='start_smooth', defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='end_smooth', defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='low_bound', minValue=-10, maxValue=0, defaultValue=-1, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='high_bound', minValue=0, maxValue=10, defaultValue=1, keyable=True)

        squash_deformer_dag = Dag(squash_deformer)
        inv_value_mdl = MDLWithMul(f"{SIDE}_{BASE_NAME}_squash_invValue", dv=-1)

        stick_ctrlShape.attr('factor') >> inv_value_mdl.attr('input1')
        inv_value_mdl.attr('output') >> squash_deformer_dag.attr('factor')
        stick_ctrlShape.attr('expan_pos') >> squash_deformer_dag.attr('maxExpandPos')
        stick_ctrlShape.attr('start_smooth') >> squash_deformer_dag.attr('startSmoothness')
        stick_ctrlShape.attr('end_smooth') >> squash_deformer_dag.attr('endSmoothness')
        stick_ctrlShape.attr('expan') >> squash_deformer_dag.attr('expand')
        stick_ctrlShape.attr('low_bound') >> squash_deformer_dag.attr('lowBound')
        stick_ctrlShape.attr('high_bound') >> squash_deformer_dag.attr('highBound')

        mc.setAttr(f"{squash_nrb}.visibility", 0)
        squash_grp.attr('visibility').value = 0

    # 12. Create Sine Wave Deformer (Optional)
    if sineDef:
        sine_def_nrb = mc.duplicate(ik_nrb, n=ik_nrb.replace('ik', 'sine'))[0]
        sine_deformer, sine_handle = mc.nonLinear(sine_def_nrb, type='sine', name=f"{SIDE}_{BASE_NAME}_sineDef")
        sine_zro_grp = Null(f"{SIDE}_{BASE_NAME}_sineDefZroGrp")
        mc.parent(sine_handle, sine_zro_grp.name)
        sine_zro_grp.attr('visibility').value = 0
        sine_zro_grp.lockAllAttr(attrs=['t', 'r', 's'])

        mc.blendShape(f"{SIDE}_{BASE_NAME}_bsh", e=True, t=(f"{SIDE}_{BASE_NAME}_combineFkIk_nrb", 2, sine_def_nrb, 1.0))
        mc.setAttr(f"{SIDE}_{BASE_NAME}_bsh.{sine_def_nrb}", 1)

        stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_SINE:", longName='SINE')
        stick_ctrlShape.addAttribute(attributeType='float', longName='envelope', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='amplitude', defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='wavelength', defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='offset', defaultValue=0, keyable=True)
        stick_ctrlShape.addAttribute(attributeType='float', longName='orientation', defaultValue=0, keyable=True)

        sine_deformer_dag = Dag(sine_deformer)
        stick_ctrlShape.attr('envelope').value = 0
        stick_ctrlShape.attr('amplitude').value = 0.3
        stick_ctrlShape.attr('wavelength').value = 1.5

        offset_store_val = PlusMinusAverage(f"{SIDE}_{BASE_NAME}_offsetStoreVal_pma")
        amp_store_val = PlusMinusAverage(f"{SIDE}_{BASE_NAME}_ampStoreVal_pma")
        length_store_val = PlusMinusAverage(f"{SIDE}_{BASE_NAME}_lengthStoreVal_pma")

        stick_ctrlShape.attr('offset') >> offset_store_val.attr('input1D[0]')
        stick_ctrlShape.attr('amplitude') >> amp_store_val.attr('input1D[0]')
        stick_ctrlShape.attr('wavelength') >> length_store_val.attr('input1D[0]')

        offset_store_val.attr('output1D') >> sine_deformer_dag.attr('offset')
        sine_handle_dag = Dag(sine_handle)
        stick_ctrlShape.attr('orientation') >> sine_handle_dag.attr('rotateY')

        stick_ctrlShape.attr('envelope') >> sine_deformer_dag.attr('envelope')
        amp_store_val.attr('output1D') >> sine_deformer_dag.attr('amplitude')
        length_store_val.attr('output1D') >> sine_deformer_dag.attr('wavelength')

    # 13. Channel Box Cleanup & Master Switches
    stick_ctrlShape.deleteAttribute('Detail')
    stick_ctrlShape.addAttribute(at='enum', keyable=True, en="_MAIN:", longName='MAIN_CTRL')
    stick_ctrlShape.addAttribute(attributeType='float', longName='ten_FKIK', minValue=0, maxValue=1, defaultValue=0, keyable=True)
    stick_ctrlShape.addAttribute(attributeType='float', longName='ten_IK', minValue=0, maxValue=1, defaultValue=0, keyable=True)
    stick_ctrlShape.addAttribute(attributeType='float', longName='ten_Detail', minValue=0, maxValue=1, defaultValue=0, keyable=True)

    masterFk_zrpGrp = Dag(f"{SIDE}_{BASE_NAME}01_masterFkZro_grp")
    masterFk_zrpGrp.disconnectAttr('visibility')
    stick_ctrlShape.attr('ten_FKIK') >> masterFk_zrpGrp.attr('visibility')
    stick_ctrlShape.attr('ten_Detail') >> detail_grp.attr('visibility')
    stick_ctrlShape.attr('ten_FKIK').value = 1

    if sineDef:
        mc.setAttr(f"{sine_def_nrb}.visibility", 0)
        mc.parent(sine_def_nrb, nurbAll_grp.name)

    mc.setAttr(f"{ik_nrb}.visibility", 0)
    mc.parent(ik_nrb, nurbAll_grp.name)
    mc.parent(combineFkIk_nrb, nurbAll_grp.name)

    # 14. Create Meta Node Links
    if sineDef:
        chain_meta = Dag(fk_rig[-1])
        chain_meta.addAttribute(dataType='string', longName='storeValue')
        chain_meta.attr('storeValue').value = f"{offset_store_val.name}, {amp_store_val.name}, {length_store_val.name}"
        chain_meta.setLocked('storeValue')
        chain_meta.addAttribute(dataType='string', longName='stickName')
        chain_meta.attr('stickName').value = stick_ctrl.name
        chain_meta.setLocked('stickName')

    # 15. Hide IK Ctrl Visibility
    master_ik_ctrls = generate_named_pattern(f"{SIDE}_{BASE_NAME}##_masterIk_ctrl", COUNT_MAIN)
    for each in master_ik_ctrls:
        if mc.objExists(each):
            master_ik_ctrlShape = Dag(shapeName(each))
            stick_ctrlShape.attr('ten_IK') >> master_ik_ctrlShape.attr('visibility')

    # 16. Scalable Setup
    if not sineDef or not squashDef:
        if place_ctrl and mc.objExists(place_ctrl):
            placeObj_ctrl = Dag(place_ctrl)
            for each in detail_loc:
                if mc.objExists(each):
                    d_loc = Dag(each)
                    placeObj_ctrl.attr('scaleX') >> d_loc.attr('scaleX')
                    placeObj_ctrl.attr('scaleY') >> d_loc.attr('scaleY')
                    placeObj_ctrl.attr('scaleZ') >> d_loc.attr('scaleZ')

    # 17. Hierarchy Parenting
    tenStillStore_grp = Null('tentacleStill_grp') if not mc.objExists('tentacleStill_grp') else Dag('tentacleStill_grp')
    mc.parent(nurbAll_grp.name, tenStillStore_grp.name)
    mc.parent(detail_grp.name, tenStillStore_grp.name)

    tenIkhStore_grp = Null('tentacleIkh_grp') if not mc.objExists('tentacleIkh_grp') else Dag('tentacleIkh_grp')
    mc.parent(ikHandle.name, tenIkhStore_grp.name)

    if sineDef:
        mc.parent(sine_zro_grp.name, tenStillStore_grp.name)
    if squashDef:
        mc.parent(squash_grp.name, tenStillStore_grp.name)

    tenFkJnt_grp = Null('tentacleFkJnt_grp') if not mc.objExists('tentacleFkJnt_grp') else Dag('tentacleFkJnt_grp')
    mc.parent(f"{SIDE}_{BASE_NAME}01_masterFk_fkJnt", tenFkJnt_grp.name)

    if parentTo and mc.objExists(parentTo):
        master_fk_zroGrp_top = Dag(f"{SIDE}_{BASE_NAME}01_masterFkRig_grp")
        if mc.objExists(master_fk_zroGrp_top.name):
            mc.parent(master_fk_zroGrp_top.name, parentTo)

    stick_ctrl.addAttribute(attributeType='message', longName='ikh_msg')
    ikHandle.attr('message') >> stick_ctrl.attr('ikh_msg')

    # 18. Advanced Twist Setup
    if enableTwist:
        ikHandle.enableTwistControl(
            forwardAxis=forwardAxis,
            worldUpAxis=worldUpAxis,
            worldUpVector=worldUpVector,
            worldUpVectorEnd=worldUpVectorEnd,
            worldUpType=worldUpType,
            upObject=upObject,
            upObjectEnd=upObjectEnd
        )

    makeHeader(f"DONE Tentacle Rig: {SIDE}_{BASE_NAME}")
    return True


















#------- USE --------
#import tentacle_fkIkDeformedRig_standalone as tenRig
fkIkDeformed(
    SIDE='A',
    BASE_NAME='tenTail',
    SCALE=20,
    COUNT_DETAIL=13,
    COUNT_MAIN=5,
    stickShape='stickCircle_Y_long_ctrlShape',
    mesh='A_tenTail_ply',
    smoothweight=True,
    sineDef=True,
    squashDef=True,
    priorJnt='root',
    parentTo='ctrl_grp',
    place_ctrl='placement_ctrl',
    enableTwist=True,
    worldUpType=4,
    forwardAxis='y+',
    worldUpAxis='z+',
    worldUpVector=(0, 0, 1),
    worldUpVectorEnd=(0, 0, 1),
    upObject='placement_ctrl',
    upObjectEnd='worldUp_loc' )

fkIkDeformed(
    SIDE='B',
    BASE_NAME='tenTail',
    SCALE=20,
    COUNT_DETAIL=13,
    COUNT_MAIN=5,
    stickShape='stickCircle_Y_long_ctrlShape',
    mesh='B_tenTail_ply',
    smoothweight=True,
    sineDef=True,
    squashDef=True,
    priorJnt='root',
    parentTo='ctrl_grp',
    place_ctrl='placement_ctrl',
    enableTwist=True,
    worldUpType=4,
    forwardAxis='y+',
    worldUpAxis='z+',
    worldUpVector=(0, 0, 1),
    worldUpVectorEnd=(0, 0, 1),
    upObject='placement_ctrl',
    upObjectEnd='worldUp_loc' )

fkIkDeformed(
    SIDE='C',
    BASE_NAME='tenTail',
    SCALE=20,
    COUNT_DETAIL=13,
    COUNT_MAIN=5,
    stickShape='stickCircle_Y_long_ctrlShape',
    mesh='C_tenTail_ply',
    smoothweight=True,
    sineDef=True,
    squashDef=True,
    priorJnt='root',
    parentTo='ctrl_grp',
    place_ctrl='placement_ctrl',
    enableTwist=True,
    worldUpType=4,
    forwardAxis='y+',
    worldUpAxis='z+',
    worldUpVector=(0, 0, 1),
    worldUpVectorEnd=(0, 0, 1),
    upObject='placement_ctrl',
    upObjectEnd='worldUp_loc' )

fkIkDeformed(
    SIDE='D',
    BASE_NAME='tenTail',
    SCALE=20,
    COUNT_DETAIL=13,
    COUNT_MAIN=5,
    stickShape='stickCircle_Y_long_ctrlShape',
    mesh='D_tenTail_ply',
    smoothweight=True,
    sineDef=True,
    squashDef=True,
    priorJnt='root',
    parentTo='ctrl_grp',
    place_ctrl='placement_ctrl',
    enableTwist=True,
    worldUpType=4,
    forwardAxis='y+',
    worldUpAxis='z+',
    worldUpVector=(0, 0, 1),
    worldUpVectorEnd=(0, 0, 1),
    upObject='placement_ctrl',
    upObjectEnd='worldUp_loc' )

fkIkDeformed(
    SIDE='E',
    BASE_NAME='tenTail',
    SCALE=20,
    COUNT_DETAIL=13,
    COUNT_MAIN=5,
    stickShape='stickCircle_Y_long_ctrlShape',
    mesh='E_tenTail_ply',
    smoothweight=True,
    sineDef=True,
    squashDef=True,
    priorJnt='root',
    parentTo='ctrl_grp',
    place_ctrl='placement_ctrl',
    enableTwist=True,
    worldUpType=4,
    forwardAxis='y+',
    worldUpAxis='z+',
    worldUpVector=(0, 0, 1),
    worldUpVectorEnd=(0, 0, 1),
    upObject='placement_ctrl',
    upObjectEnd='worldUp_loc' )