# Naming Convention Documentation

This document outlines the naming conventions used in the auto-rigging system, based on the analysis of `core.py` and `generic_maya_dict.py`.

## 1. General Structure

The system supports two primary naming styles. The `core.parse_node_name` and `core.check_name_style` functions are used to detect and handle these styles.

### Style A: Prefix Style (Capital Lead)
Used when the side indicator is at the beginning of the name.
*   **Format**: `[Side]_[BaseName]_[Type]`
*   **Examples**: `L_arm_jnt`, `R_leg_ctrl`, `C_spine_grp`
*   **Side Indicators**: `L`, `R`, `C`, `M`

### Style B: Suffix Style (Side Follows)
Used when the side indicator follows the name but precedes the type.
*   **Format**: `[BaseName][Side]_[Type]`
*   **Examples**: `armLFT_jnt`, `legRGT_ctrl`, `spineCEN_grp`
*   **Side Indicators**: `LFT`, `RGT`, `CEN`

## 2. Side Indicators

| Side | Prefix Style | Suffix Style | Color Code |
| :--- | :--- | :--- | :--- |
| **Left** | `L` | `LFT` | Blue / SoftBlue |
| **Right** | `R` | `RGT` | Red |
| **Center** | `C`, `M` | `CEN` | Yellow / Primary |

## 3. Node Type Suffixes

Standard suffixes are defined in `generic_maya_dict.py` (`NODE_short_dict` and `NODE_dict`).

### Node Type Shortcuts

| Node Type | Suffix |
| :--- | :--- |
| **addDoubleLinear** | `adl` |
| **aimConstraint** | `aimCons` |
| **aimMatrix** | `aimMat` |
| **animCurveU** | `animCrv` |
| **animCurveUL** | `animCurveUL` |
| **animCurveUU** | `animUU` |
| **blendColors** | `blc` |
| **blendMatrix** | `blendMat` |
| **blendShape** | `bsh` |
| **blendTwoAttr** | `bta` |
| **blendWeighted** | `blendWeighted` |
| **cMuscleSmartConstraint** | `musleCons` |
| **clamp** | `cmp` |
| **cluster** | `clus` |
| **composeMatrix** | `composeMatrix` |
| **condition** | `cnd` |
| **curveInfo** | `crvInfo` |
| **decomposeMatrix** | `deComp` |
| **deformSine** | `defSine` |
| **deformSquash** | `defSquash` |
| **distanceBetween** | `dtw` |
| **eulerToQuat** | `eulToQuat` |
| **expression** | `exp` |
| **file** | `file` |
| **follicle** | `flc` |
| **fourByFourMatrix** | `fBFMat` |
| **group** | `grp` |
| **ikEffector** | `ike` |
| **ikHandle** | `ikh` |
| **joint** | `jnt` |
| **lambert** | `lambert` |
| **locator** | `loc` |
| **mesh** | `ply` |
| **motionPath** | `mp` |
| **multDoubleLinear** | `mdl` |
| **multMatrix** | `multMatrix` |
| **multiplyDivide** | `mdv` |
| **network** | `meta` |
| **nurbsCurve** | `ctrl` |
| **nurbsSurface** | `nrb` |
| **orientConstraint** | `orienCons` |
| **parentConstraint** | `parCons` |
| **phong** | `phong` |
| **pickMatrix** | `pickMat` |
| **place2dTexture** | `place2d` |
| **plusMinusAverage** | `pma` |
| **pointConstraint** | `poinCons` |
| **pointOnCurveInfo** | `poci` |
| **poleVectorConstraint** | `poleCons` |
| **quatInvert** | `quatInv` |
| **quatProd** | `quatProd` |
| **quatToEuler** | `quatToEul` |
| **remapValue** | `remap` |
| **reverse** | `rev` |
| **scaleConstraint** | `scaleCons` |
| **setRange** | `setRange` |
| **shadingEngine** | `sg` |
| **skinCluster** | `skc` |
| **vectorProduct** | `vecProd` |
| **wtAddMatrix** | `wtAddMat` |

## 4. Specific Rigging Suffixes

*   **Zero Group**: `[Name]_Zro` or `[Name]Zro_grp` (Hierarchy root for a controller)
*   **Offset Group**: `[Name]_Offset` (Secondary group under Zero)
*   **Gimbal Controller**: `[Name]_Gmbl` (Gimbal correction controller)

## 5. Color Coding Standards

Defined in `generic_maya_dict.COLOR_part_dict`:
*   **Left (`LFT`/`L`)**: Blue
*   **Right (`RGT`/`R`)**: Red
*   **Center / Primary**: Yellow
*   **Dynamic**: White
*   **Secondary**: White
*   **Tertiary**: SoftBlue

## 6. Joint Naming Standards
Standard joint lists are pre-defined for auto-rigging purposes:
*   **Standard List**: `ankleLFT_bJnt`, `wristRGT_bJnt`, etc.
*   **Binder Joint Suffix**: `_bJnt` (commonly used for skinning joints)

## 7. Procedural Rigging Function Parameter Standards (`generic_maya_dict.py`)

All procedural rigging functions in `nmTools` (e.g. `eh_universalFkRig`, `eh_armRig`, `eh_bipedLegRig`, `spaceSwitch`, `eh_weightedHelperJnt`) must strictly adhere to the canonical parameter names defined in `generic_maya_dict.PARAMETER_BY_CATEGORY` / `parameter_name_dict`.

### Core Rigging Parameters & Anti-Pattern Rules

| Canonical Parameter | Type | Purpose / Description | Prohibited Aliases (NEVER USE) |
| :--- | :--- | :--- | :--- |
| **`parentCtrlTo`** | `str` | Target controller/group for top zero group | `parentCtrl`, `parent_to`, `targetCtrl`, `parentToCtrl` |
| **`parentCtrlToPriorJnt`** | `bool` | True = parent under `parentCtrlTo` + constraint to `priorJnt` | `parentCtrlFollow`, `constraintCtrlToPrior` |
| **`priorJnt`** | `str` | Preceding parent joint for root attachment | `parentJnt`, `previousJnt`, `prevJnt`, `baseJnt` |
| **`parentToPriorJnt`** | `bool` | True = DAG-parents root bind joint under `priorJnt` | `parentPrior`, `parentToParent`, `connectToPrior` |
| **`parentTo`** | `str` | Explicit target DAG parent node | `parentTarget`, `dagParent` |
| **`useRigGrp`** | `bool` | True = wraps module inside dedicated `{part}Rig_grp` | `createRigGrp`, `makeRigGrp` |
| **`chainHierarchy`** | `bool` | True = sequential 01->02->03 FK; False = flat parallel FK | `sequential`, `hierarchyMode` |
| **`jntLst`** | `list` | Joint names to rig (flat list or nested multi-chain) | `jointList`, `joints`, `jnts`, `jntList` |
| **`tmpJnt`** | `str\|list` | Guide/template joint name for transform reference | `guideJnt`, `templateJoint`, `guide`, `tempJnt` |
| **`isTmpJnt`** | `bool\|None`| True = clones template joints via `rigTools.jointAt` | `fromTemplate`, `cloneGuide` |
| **`ctrlShape`** | `str` | Curve shape identifier for controllers | `shape`, `curveShape`, `controllerShape` |
| **`charScale`** | `float` | Global character scale multiplier (default 1.0) | `globalScale`, `scaleMult`, `characterScale` |
| **`rotateOrder`** | `str` | Maya rotation order string (e.g. `'zxy'`) | `rotOrder`, `ro`, `rotationOrder` |
| **`linkRotOrder`** | `bool` | True = dynamically links ctrl rotateOrder to joint | `syncRotOrder`, `connectRotateOrder` |
| **`parentMatrix`** | `bool` | True = uses `mtc.parentConMatrix`; False = legacy constraints | `matrixParent`, `useMatrix` |
| **`localWorld`** | `bool` | True = builds dynamic Orient Local/World switch network | `worldOrient`, `localOrient` |
| **`curlCtrl`** | `bool` | True = builds master Curl controller with `'Detail'` toggle | `poseCtrl`, `masterCurl` |
| **`space`** | `list` | Target space objects for space switching | `spaces`, `targetSpaces`, `driverList` |
| **`spaceAttach`** | `str` | Driven target node/group (Fail-Fast required) | `drivenTarget`, `spaceTarget`, `attachTo` |
| **`attr_holder`** | `str` | Controller hosting custom animator Channel Box attributes | `attrHost`, `holder`, `attrNode` |
| **`attr_occur`** | `str` | Alias/equivalent to `attr_holder` in follow/skirt modules | `occurHost` |
| **`segmentScaleCompensate`** / **`ssc`** | `bool` | Must be `False` on bind joints to prevent shearing | `compensateScale`, `disableSSC` |

## 8. Maya Controller Custom Attribute Standards (`generic_maya_dict.py`)

Custom attributes added to Maya controllers via `mc.addAttr` / `core.Dag.addAttribute` for animators in Channel Box must strictly adhere to the canonical attribute names defined in `generic_maya_dict.CTRL_ATTR_BY_CATEGORY` / `ctrl_attribute_dict`.

| Category | Canonical Attribute | Type | Default | Description / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **FK/IK & Space** | **`FK_IK`** | `float` | `0.0` | Master mode switch (0.0 = FK, 1.0 = IK or 0-10) |
| | **`allFkIk`** | `float` | `0.0` | Global FK/IK switch for all finger or limb chains |
| | **`fkVis`** / **`ikVis`** | `bool` | `1` / `0` | Visibility toggles driven dynamically by FK_IK switch |
| | **`space`** | `enum` | `0` | Coordinate space switcher (0:World, 1:COG, 2:Chest, etc.) |
| | **`localWorld`** | `float` | `0.0` | Blends rotation between World (0.0) and Local parent (1.0) |
| | **`kneeLock`** / **`elbowLock`** | `float` | `0.0` | Snaps mid-limb joint directly to Pole Vector locator |
| **Stretchy Limbs**| **`autoStretch`** | `float` | `1.0` | Enables procedural automatic limb stretch |
| | **`upStretch`** / **`lowStretch`** | `float` | `0.0` | Manual stretch multipliers for limb segments |
| | **`softIK`** / **`dSoft`** | `float` | `0.0` / `0.001` | Anti-popping deceleration before full extension |
| | **`squash`** / **`stretch`** | `float` | `0.0` | Volume preservation scale factors |
| **Foot Roll** | **`ballRoll`** | `float` | `0.0` | Metatarsal roll lifting heel off ground |
| | **`toeRoll`** | `float` | `0.0` | Tip of toe roll after ball roll limit |
| | **`heelRoll`** | `float` | `0.0` | Back of heel roll lifting toe off ground |
| | **`heelTwist`** / **`toeTwist`** | `float` | `0.0` | Yaw twisting pivoting about heel / toe |
| | **`footRock`** | `float` | `0.0` | Lateral side-to-side banking along foot edges |
| | **`ballRise`** | `float` | `0.0` | Vertical heel raise keeping toe flat |
| **Hand Poses** | **`fist`**, **`roll`**, **`relax`** | `float` | `0.0` | Closed fist, sequential curl, relaxed pose |
| | **`spread`**, **`cup`**, **`wide`** | `float` | `0.0` | Finger abduction, palm cup, wide fan out |
| **Twist & Tweak** | **`Upper_Twist`**, **`Lower_Twist`**| `float` | `0.0` | Manual rotation offsets for roll joints |
| | **`Auto_Twist`** | `short` | `1` | Procedural twist distribution from wrist/ankle |
| | **`Detail`** | `bool` | `0` | Secondary micro-controller / tweak visibility |
| **Dynamics** | **`dynamic`** / **`dynamic_blend`** | `bool`/`float` | `1` / `1.0` | Physics simulation toggle and keyframe blend slider |
| | **`currentPush`** | `float` | `0.0` | Read-only live computed translation offset for volume helpers |
| | **`positionWeight`** / **`rotationWeight`** | `float` | `0.5` | Helper joint parent (0.0) <-> driver (1.0) blend weights |
| | **`restraintWeight`** | `float` | `0.1` | Damping weight back towards restraint space |
