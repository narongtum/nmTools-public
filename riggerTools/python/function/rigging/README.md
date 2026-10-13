# สารบัญโมดูลและฟังก์ชันระบบ Rigging (`nmTools`)

> เอกสารสารบัญรวบรวมไฟล์สคริปต์ โมดูล คลาส และฟังก์ชันทั้งหมดในโฟลเดอร์ `riggerTools/python/function/rigging`
> เพื่อเป็นคู่มืออ้างอิงโครงสร้าง (Table of Contents / API Index) สำหรับ Pipeline Rigging ใน Autodesk Maya

## 📌 สรุปภาพรวมโครงสร้าง (Directory Overview)

| หมวดหมู่ | คำอธิบาย | จำนวนไฟล์ (.py) |
| :--- | :--- | :---: |
| [1. Core & Base Framework](#core_base) | โมดูลหลักสำหรับจัดการ DAG node, Matrix constraint, Object-Oriented wrapping และ Helper utilities ที่ใช้ร่วมกันทั่วทั้งระบบ | `19` |
| [2. Rig Components: Limbs & Quadruped](#components_limbs) | โมดูลสร้าง Rig ส่วนแขน ขา Biped/Quadruped รวมถึงระบบ Pure Double IK, Stretchy IK, Soft IK และ Knee Lock | `47` |
| [3. Rig Components: Ribbon, Spine, Spline & Dynamic](#components_ribbon_spine) | ระบบ Ribbon Matrix De Boor spline, Matrix Spine, Dynamic IK Tail/Spine และ Curve pinned setups | `37` |
| [4. Rig Components: Fingers & Face/Head](#components_fingers_face) | โมดูลสร้าง Rig นิ้วมือ (FK/IK/Curl/SDK), คอ, ศีรษะ, ขากรรไกร และโครงสร้างใบหน้าเบื้องต้น | `12` |
| [5. Rig Builders, Body Rig & Pipeline Runners](#build_runners) | สคริปต์ Assembly ระดับ Character/Creature, Body rig orchestrator และ Master build execution | `67` |
| [6. Controllers, Shapes & Curve Tools](#controllers_curves) | ระบบคลัง NURBS Shapes, เครื่องมือสร้าง Gimbal/Zero group, ปรับแต่งรูปทรง/สี และจัดการขนาดคอนโทรลเลอร์ | `25` |
| [7. Skeleton & Joint Systems](#skeleton_joints) | เครื่องมือสร้างและจัดการ Joint บน Curve, จัดการ Bind Joints, คำนวณความยาว และการแทนที่ Template Joints | `4` |
| [8. Skinning, Deformers & BlendShapes](#skin_deformers) | เครื่องมือบริหารจัดการ Skin Weights (SkinWrangler, nsSkinClusterIO, brSmoothWeights, Curve skinning) และ BlendShape Inverters | `33` |
| [9. Project-Specific Rigging Modules](#project_specific) | สคริปต์เฉพาะสำหรับโปรเจกต์ เช่น Project_Regulus_Sample และ Project_Sample (Local/World, Texture switch, Facial link) | `9` |
| [10. Features, Tools & Utility Scripts](#tools_features_root) | ชุดเครื่องมือ Utilities ทั่วไป, ทำความสะอาดซีน, สร้าง Shader, Local/World switches, Snap tools และ Legacy scripts | `17` |
| [Root Helper & One-Off Scripts](#root_scripts) | สคริปต์เดี่ยวระดับ Root folder สำหรับฟังก์ชันเฉพาะกิจและ Quick tools | `108` |
| **รวมทั้งหมด** | | **`378`** |

---

<a id="core_base"></a>
## 1. Core & Base Framework (โครงสร้างแกนหลักและเครื่องมือพื้นฐาน)
*โมดูลหลักสำหรับจัดการ DAG node, Matrix constraint, Object-Oriented wrapping และ Helper utilities ที่ใช้ร่วมกันทั่วทั้งระบบ*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `19` ไฟล์

### 📄 `autoRig/base/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/base/core.py`
**คำอธิบาย / รายละเอียด:** :Date: 2021-04-08

**คลาส (Classes):**
- `class CoreLogger`
- `class Node` — *Template Base class for maya*
  - **Methods:** `deleteName`, `getName`, `rename`, `getType`, `getExists`, `attr`, `addAttribute`, `setAttribute`...
- `class MetaRoot` — *create clamp object  *
- `class MetaBlank`
- `class MetaGeneric`
  - **Methods:** `lockAllAttr`
- `class CMuscleSmartConstraint` — *create plusMinusAverage object  *
- `class Clamp` — *create clamp object  *
- `class Reverse` — *create reverse object *
- `class ReverseNam` — *create reverse object *
- `class PlusMinusAverage` — *create plusMinusAverage object  *
- `class LightInfo`
- `class BlendColors` — *create BlendColors object  *
- `class BlendShape` — *create BlendShape   *
- `class MultiplyDivine` — *create MultiplyDivine object  *
- `class MultiplyDivineWithVal` — *create MultiplyDivine object  with regsinate operator *
- `class AddDoubleLinear` — *create AddDoubleLinear object  *
- `class MultiDoubleLinear` — *create multDoubleLinear object  *
- `class MDLWithMul` — *create multDoubleLinear object with multiple val*
- `class Condition` — *create Condition object  *
- `class ConditionWithNum`
- `class Loft`
- `class PointOnCurveInfo`
- `class CurveInfo`
- `class BlendTwoAttr`
- `class DecomposeMatrix`
- `class MultMatrix`
- `class MultMatrixWithValue`
- `class ComposeMatrix`
- `class VectorProduct`
- `class FourByFourMatrix`
- `class AimMatrix`
- `class PickMatrix`
- `class WtAddMatrix`
- `class WtAddMatrixWithVal`
- `class WtAddMatrixWithChannal`
- `class EulerToQuat`
- `class QuatInvert`
- `class QuatProd`
- `class QuatToEuler`
- `class BlendMatrix`
- `class PointMatrixMult`
- `class SkinCluster` — *skinCluster Node Object *
  - **Methods:** `setWeight`
- `class DistanceBetween` — *create DisctanceBetween   *
- `class DistanceDimension`
- `class DistanceNode`
- `class MotionPath`
- `class RemapCurve`
- `class AnimCurveUU` — *create animcurve for connect value to object  *
  - **Methods:** `setKeyValue`, `keyTangent`
- `class AnimCurvePos` — *# find the way to make an arg insted create 2 class*
- `class AnimCurveNeg` — *animCurve for Negative value*
- `class AnimCurveSomeThing` — *animCurve for Negative value Still Fail try it later*
- `class Attribute` — *Template maya attr for class Attributes*
  - **Methods:** `_getExists`, `lockHide`, `editAttrManual`, `getVal`, `setVal`, `getExists`
- `class Dag` — *Template DAG class  *
  - **Methods:** `unParent`, `getShape`, `renameShape`, `setLineWidth`, `getColor`, `setColor`, `setOutlineColor`, `getRotateOrder`...
- `class Follicle`
- `class Null` — *for create Object empty group in maya*
  - **Methods:** `follicle`
- `class Nurb`
  - **Methods:** `sphere`
- `class Locator` — *Create Locator Object *
  - **Methods:** `setLocColor`
- `class Joint` — *WARNING !!! joint object adjust for assign name when create*
  - **Methods:** `setLable`, `setJointColor`, `setJointOutlineColor`, `createJntShape`, `getRotateOrder`, `setRotationOrder`, `getRotateOrderString`, `setJointColor`...
- `class Constraint` — *base class for constraint *
  - **Methods:** `getTargets`
- `class Constr` — *base class for constraint *
  - **Methods:** `psConstr`
- `class ParentConstraint` — *inherit from Constraint *
- `class AimConstraint` — *inherit from Constraint *
- `class PoleVectorConstraint` — *inherit from Constraint *
- `class ScaleConstraint` — *inherit from Constraint *
- `class Ik` — *Template class for IK object*
  - **Methods:** `getName`, `rename`, `getEff`, `setEff`, `getCrv`, `reCrv`
- `class IkRp` — *Class ik rotate plane *
- `class DoIk` — *Newer than IkRp*
- `class DoIkSpline` — *        # Newer than IkRp put the solver in to attr instead*
  - **Methods:** `enableTwistControl`
- `class IkSpring` — *Class ik spring solver  *

**ฟังก์ชันหลัก (Functions - 39 รายการ):**
- `extract_rotationToQuat(baseName, source, target, rotAxis)` — *Extracts a specific rotation axis (twist) from source to target using Quaternions.*
- `read_joint_list_from_file(file_path)` — *Reads a Python-formatted list of joint names from a text file.*
- `findExtensionFullName(name)` — *aaa= core.findExtensionFullName('C_tenTail_squash_deformerHandle')*
- `generate_named_pattern(pattern, count)` — *Replace one or more '#' in a pattern string with zero-padded integers up to count.*
- `list_joints_from_skincluster(skincluster)`
- `parse_node_name(node_input)` — *Decomposes a node name into components (base, side, type, etc.).*
- `check_name_style(name)`
- `findBaseName(name)`
- `shapeName(ctrl)`
- `makeHeader(text)`
- `createGimbal(obj)`
- `nmCreateGimbal(obj)`
- *...และอีก 27 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/base/eh_rigTools.py`
**คำอธิบาย / รายละเอียด:** ... ... DESCRIPTION: Enhanced Rigging Tools (eh_rigTools.py) ... ใช้ฟังก์ชันชื่อเดียวกับ rigTools.py เดิม แต่ปรับปรุงการคืนค่า (Return) ... ให้เป็น Object เพื่อความต่อเนื่องของระบบ ...

**คลาส (Classes):**
- `class RigToolsLogger`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `zroNewGrpWithOffset(obj)`
- `jointAt(obj, orient)`
- `_creControl(nameSpace, name, ctrlShape, rotateOrder, ...)`
- `findCharScale(topJnt)`

### 📄 `autoRig/base/rigTools.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.base import rigTools

**คลาส (Classes):**
- `class RigToolsLogger`

**ฟังก์ชันหลัก (Functions - 30 รายการ):**
- `create_basic_ctrl_on_object(target, baseName, shape, charScale, ...)` — *Creates a controller at the target object's position with standard Zero/Offset groups.*
- `createFollicle(name, uVal, vVal)`
- `_pinToSurface(oNurbs, side, region, uPos, ...)`
- `find_pv(arm, elbow, wrist, poleVector, ...)`
- `distanceNode(name, startPoint, endPoint)`
- `_creControl(nameSpace, name, ctrlShape, rotateOrder, ...)` — *create controller for fk controller autoRig*
- `createFkRig(nameSpace, name, parentTo, tmpJnt, ...)`
- `zeroGroup(obj)` — *create zero group *
- `zeroGroupNam(obj)` — *create zero group *
- `zroNewGrpWithOffset(obj)` — *name naming *
- `offset_locator_grp(obj)`
- `zroDoubleGrp(obj, zroNam, offNam)` — *create double grp *
- *...และอีก 18 ฟังก์ชันภายในโมดูล*

### 📄 `constraint/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `constraint/eh_auto_skirt_rig.py`
**คำอธิบาย / รายละเอียด:** Maya Auto Skirt Rigging System

**คลาส (Classes):**
- `class AutoSkirtUI` — *GUI class to provide an artist-friendly window for *
  - **Methods:** `show`, `create_selection_row`, `load_selected`, `load_selected_pelvis`, `get_selection_pos_and_pelvis`, `on_measure_top_rad`, `on_measure_bot_rad`, `on_measure_height`...

**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `create_collider(joint_name, radius, name_suffix)` — *Creates a collider locator parented to the specified joint.*
- `connect_collision_chain(base_loc, ik_handle, colliders, parent_space_obj)` — *Connects a series of colliders to push the ik_handle away from its base_loc position.*
- `build_auto_skirt(pelvis, left_thigh, right_thigh, left_knee, ...)` — *Main generator for the auto skirt rig.*
- `build_sample_scene()` — *Builds a simple character test rig (hips and two leg chains) *
- `main()` — *Entry point to launch the UI.*

### 📄 `constraint/matrixConstraint.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.constraint import matrixConstraint as mtc

**คลาส (Classes):**
- `class Constraint`

**ฟังก์ชันหลัก (Functions - 26 รายการ):**
- `_getDagPath(node)` — *API 2.0 Helper to get MDagPath*
- `_getLocalOffset(source, target)` — *Calculates Offset Matrix using OpenMaya 2.0 but forces evaluation via mc.xform.*
- `rotateOffset(tgt, dmpMtx, mulMtx)`
- `eh_orientLocalWorldMatrix(ctrl, localObj, worldObj, target, ...)` — *Matrix-based Local/World space switch with optional parent/orient/point behavior.*
- `createMatrixAttr(selected, attrNam)`
- `orientConstraintMatrix(source, target, mo, baseName)` — *Creates a matrix-based Orient Constraint.*
- `_getAimMoOffset(source, target, aimVector, upVector)` — *Compute world-space offset so that the matrix-based aim behaves*
- `aimConstraintMatrix(source, target, aimVector, upVector, ...)` — *Creates a Matrix-based Aim Constraint using the 'aimMatrix' node.*
- `eh_aimMatrixConstraint(aim_object, up_object, target, aimVector, ...)` — *Creates a cycle-free Matrix-based Aim Constraint.*
- `aimBlendMatrixGPT(source1, source2, target, upObject1, ...)` — *Stable Matrix-based Aim Constraint with Up-Vector Blending.*
- `parentConMatrix_forRibbon(source, target, nameSpace, mo, ...)` — *Creates a matrix-based Parent Constraint using MultMatrix and DecomposeMatrix.*
- `parentConMatrixGPT(source, target, nameSpace, mo, ...)` — *Creates a matrix-based Parent Constraint using MultMatrix and DecomposeMatrix.*
- *...และอีก 14 ฟังก์ชันภายในโมดูล*

### 📄 `constraint/normalConstraint.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.constraint import normalConstraint as nmCon

**ฟังก์ชันหลัก (Functions - 20 รายการ):**
- `constraint_pair(pairs, maintainOffset)` — *Create parentConstraint and scaleConstraint for multiple parent-child pairs.*
- `constraint_list(parents, children, mo_parent, mo_scale)` — *Create parentConstraint and scaleConstraint between corresponding items in two lists.*
- `snapPointCon()`
- `snapOrientCon()`
- `snapScaleCon()`
- `snapMat()`
- `snapMatArg(source, target)`
- `normalParentConstr(source, target)`
- `normalScaleConstr(source, target)`
- `normalPointConstr(source, target)`
- `orientConstr(source, target)`
- `orientConstrRe(source, target)`
- *...และอีก 8 ฟังก์ชันภายในโมดูล*

### 📄 `constraint/pinLocatorToSurface.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.constraint import pinLocatorToSurface as pls

**คลาส (Classes):**
- `class PinLogger`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `pin_locator_surface(nurbs, region, side, source_loc, ...)`
- `gen_locator_surface(ribbon_nrb, numJoints, side, region, ...)`
- `_create_ctrl_bJnt_for_glue(loc_list, priorJnt, charScale, ctrlShape, ...)`

### 📄 `constraint/pin_locator_curve.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.constraint import pin_locator_curve as lfc

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `locator_follow_curve_spec_position(locator_param_list, curve_name)`
- `locator_follow_curve_list(locator_list, curve_name)`

### 📄 `constraint/pin_locator_polygon.py`
**คลาส (Classes):**
- `class PinPolyLogger`
- `class PinPolyLogger`
- `class PinPolyLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `pin_locator_polygon(poly_mesh, vtx_list, locator_scale, side, ...)` — *Pin locators to specific vertices using uvPin.*
- `pin_locator_polygon_from_guides(poly_mesh, guide_list, locator_scale, side, ...)` — *Pin locators (or joints) to a mesh using existing Locator Guides to determine position.*

### 📄 `constraint/rivetWithAddMatrix.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.constraint import rivetWithAddMatrix as rwm

**คลาส (Classes):**
- `class riveAddMatrixLog`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `get_dag_path(node_name)` — *Returns MDagPath from node name.*
- `get_matrix(node_name)` — *Returns inclusive matrix of a node.*
- `rivetMatrixWeight(data_list)` — *Create a matrix-based rivet constraint (wtAddMatrix) using explicit weight arguments.*
- `rivetMatrix(skinCluster, vtx, target, thresholdValue)`

### 📄 `constraint/slide_controller_to_pathGPT.py`
**คำอธิบาย / รายละเอียด:** Maya Python (PyMEL) Attach MULTIPLE controllers to one curve + one shared slide_ctrl Each controller gets its own offsetGrp + motionPath + ADL All ADL.input2 connect to ONE shared multiplyDivide (slide_ctrl.pathSlide * pathScale)

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `get_or_create_shared_scale_md(slide_ctrl, slide_attr, scale_attr, md_name)` — *Ensure one shared multiplyDivide exists:*
- `attach_ctrls_with_shared_scale(controllers, curve, slide_ctrl, slide_attr, ...)` — *Attach a LIST of controllers to the curve with one shared slide_ctrl.*

### 📄 `constraint/snakeSlideController.py`
**คำอธิบาย / รายละเอียด:** Maya Python — Snake path "Ghost Follower" rig helper Converted: use maya.cmds (mc) for core rig logic Keep PyMEL (pm) only for UI

**ฟังก์ชันหลัก (Functions - 16 รายการ):**
- `_namespaced(name, namespace)`
- `_ghost_name(node)`
- `getRigNode(namespace)`
- `get_slide_ctrls(namespace)`
- `ensure_slide_attrs(curveField, namespace)` — *Ensure shared slide attributes exist on the path curve specified by UI text field.*
- `get_or_create_shared_md(namespace, curveField)` — *Create or fetch the shared multiplyDivide node and wire it to the path curve's shared attributes.*
- `ensure_ghost_group()`
- `build_path_ghosts(curveField, namespace)` — *Build or update path ghosts using a shared MD driven by attributes on the path curve.*
- `_get_parent_handle(node)`
- `_get_snap_group(node)`
- `attach_all(namespace)`
- `release_all_detach_current_frame(namespace)`
- *...และอีก 4 ฟังก์ชันภายในโมดูล*

### 📄 `util/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `util/boundingBox.py`
**คำอธิบาย / รายละเอียด:** Reference from glTools

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `geoBoundingBox(geometry, worldSpace, noIntermediate, visibleOnly)` — *get bounding box value from geometry *
- `getGeoRatio(select, xVal, yVal)` — *I don't know what is for*

### 📄 `util/cleanup.py`
**คำอธิบาย / รายละเอียด:** .... shift from autorig.util

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `cleanup()`
- `_deleteTemplate()`

### 📄 `util/generic_maya_dict.py`
**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `askColor(side)`
- `getColorPart(part)` — *Returns the color string based on the part or side name from COLOR_part_dict.*
- `select_body_jnt()` — *Selects all joints defined in standardJnt_list if they exist in the scene.*
- `get_short_name(long_name)`
- `rename_joints(standard_dict, nanuq_dict)`

### 📄 `util/misc.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.util import misc

**คลาส (Classes):**
- `class MiscLogger`

**ฟังก์ชันหลัก (Functions - 82 รายการ):**
- `select_hierarchy(root)` — *Select the given root and all its descendants.*
- `check_case_sentitive(group_name)`
- `check_case_manual(name)` — *Check if the given name exists in Maya, either as lowercase or capitalized.*
- `unparent_group(group_name)`
- `make_ctrl_bold(lineWidth)`
- `replace_name()`
- `hide_by_ext(ext)` — *Hide objects in Maya by a specified naming extension.*
- `rename_locator()`
- `select_tip_joint(selected_joints)`
- `_change_color(name_list, color, displayType)`
- `check_name_style(name)`
- `_unparent_if_not_world(obj_name)`
- *...และอีก 70 ฟังก์ชันภายในโมดูล*

---

<a id="components_limbs"></a>
## 2. Rig Components: Limbs & Quadruped (ระบบรยางค์ แขน ขา สัตว์สี่เท้า)
*โมดูลสร้าง Rig ส่วนแขน ขา Biped/Quadruped รวมถึงระบบ Pure Double IK, Stretchy IK, Soft IK และ Knee Lock*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `47` ไฟล์

### 📄 `autoRig/components/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/eh_armRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `eh_armRigExt(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/components/eh_armRigR15.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `eh_armRigExtR15(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/components/eh_bipedLegRig.py`
**คำอธิบาย / รายละเอียด:** log use the same  rotateOrder of both bJnt and ctrl

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `footRollRig(nameSpace, side, region, tmpJnt, ...)`
- `bipedLegRigExt(nameSpace, parentTo, side, region, ...)`

### 📄 `autoRig/components/eh_clavicleRig.py`
**คำอธิบาย / รายละเอียด:** Module: eh_clavicleRig

**คลาส (Classes):**
- `class ClavicleRigLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createClavicleRig(nameSpace, side, parentTo, priorCtrl, ...)`

### 📄 `autoRig/components/eh_headRig.py`
**คำอธิบาย / รายละเอียด:** Module: eh_headRig

**คลาส (Classes):**
- `class HeadRigLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `_createEyeSetup(nameSpace, side, eyeJnt, headJnt, ...)` — *Internal helper to create Eye Rig.*
- `createHeadRig(nameSpace, parentTo, tmpJnt, faceCtrl, ...)`

### 📄 `autoRig/components/eh_hipRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - Pelvis rig module eh_hipRig.py

**คลาส (Classes):**
- `class HipRigLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createHipRig(nameSpace, ctrl_grp, tmpJnt, charScale, ...)`

### 📄 `autoRig/components/eh_ikFkWtMatrixSpineRig.py`
**คำอธิบาย / รายละเอียด:** Module: eh_ikFkWtMatrixSpineRig

**คลาส (Classes):**
- `class spineWtMatrixSpineLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createSpineRig(nameSpace, parentTo, priorJnt, priorCtrl, ...)`

### 📄 `autoRig/components/eh_ikfkSpineRig.py`
**คำอธิบาย / รายละเอียด:** Module: eh_ikfkSpineRig

**คลาส (Classes):**
- `class IkFkSpineLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createIkFkSpineRig(nameSpace, parentTo, priorJnt, priorCtrl, ...)`

### 📄 `autoRig/components/eh_neckRig.py`
**คำอธิบาย / รายละเอียด:** Module: eh_neckRig

**คลาส (Classes):**
- `class NeckRigLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createNeckRig(nameSpace, parentTo, priorCtrl, priorJnt, ...)`

### 📄 `autoRig/components/eh_propRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - prop Rig module

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `propRig(nameSpace, ctrl_grp, tmpJnt, charScale, ...)`

### 📄 `autoRig/components/eh_quadrupedLegRig.py`
**คำอธิบาย / รายละเอียด:** Quadruped Leg Rig Component Module (Digitigrade & Plantigrade)

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `eh_quadrupedLegRig(nameSpace, parentTo, side, tmpJnt, ...)` — *Builds a full 4-joint Digitigrade Quadruped Hind Leg Rig.*
- `plantigradeLegRig(nameSpace, parentTo, side, tmpJnt, ...)` — *Builds a 3-joint Plantigrade / Biped-like Leg Rig (e.g. bear, human-like quadruped limbs).*

### 📄 `autoRig/components/eh_quadrupedLegRig_DoubleIK.py`
**คำอธิบาย / รายละเอียด:** Quadruped Double IK Leg Rig Component (eh_quadrupedLegRig_DoubleIK)

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `eh_quadrupedLegRig_DoubleIK(nameSpace, parentTo, side, tmpJnt, ...)` — *Builds a full 4-joint Digitigrade Quadruped Leg Rig powered by a Double IK*

### 📄 `autoRig/components/eh_quradpedHipRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `quradpedHipRig(nameSpace, parentTo, tmpJnt, charScale)`

### 📄 `autoRig/components/eh_rootRig.py`
**คำอธิบาย / รายละเอียด:** ... ... DESCRIPTION: Core function for creating the root rig groups and master controls. ...

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createMasterGrp(nameSpace, charScale, PROJECT_DICT)` — *# ... Creates the main master control groups and controls for the rig hierarchy.*

### 📄 `autoRig/components/fingerRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/fingerRig/eh_creatureFingerRig.py`
**คำอธิบาย / รายละเอียด:** Procedural Hybrid FK / Single Chain IK Finger Rig for creature paws/hands with ball joint parenting and floor clench behavior.

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `creatureFingerRig(nameSpace, side, fingerNum, fingerName, ...)` — *Construct procedural FK / IK Hybrid Finger Rig for creature paws/hands.*
- `creatureFingerCurlRig(nameSpace, side, fingerName, numCtrl, ...)` — *Connect Procedural Finger Curl & Floor Clench ('clench') math network to offset groups.*

### 📄 `autoRig/components/fingerRig/eh_fingerRig.py`
**คำอธิบาย / รายละเอียด:** FK Five Finger Rig

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `fingerRigExt(nameSpace, side, fingerNum, fingerName, ...)`
- `baseFingerRig(nameSpace, side, fingerNum, fingerName, ...)`
- `connect_finger_value(stickNam, fingerName, side, defaultValue)`

### 📄 `autoRig/components/fingerRig/eh_finger_localCurlExec.py`
**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `creEachFingerGrp(nameSpace, parentTo, side, stickNam)` — *Create Main empty grp with name*
- `creHandStick(nameSpace, fingerName, side, charScale, ...)` — *Create Local small stick controller*
- `creLocalFingerAttr(nameSpace, fingerName, side, ctrlName, ...)`
- `runLocalFingerRig(nameSpace, fingerName, side, charScale, ...)`
- `localFingerAllRig(nameSpace, parentTo, side, fingerName, ...)`

### 📄 `autoRig/components/fingerRig/eh_finger_localCurlRig.py`
**ฟังก์ชันหลัก (Functions - 6 รายการ):**
- `connect_LocOffGrp(nameSpace, fingerName, side, numCtrl, ...)`
- `_creLocStoVal(nameSpace, fingerName, numCtrl, side, ...)`
- `creaeLocalPostStore(nameSpace, side, fingerName, fingerbehavior)`
- `_normalLocalCon(nameSpace, fingerName, side, ctrlName, ...)`
- `connectLocalPma(nameSpace, fingerName, side, nameOfPost, ...)`
- `conLocRollPma(nameSpace, fingerName, side, nameOfPost, ...)`

### 📄 `autoRig/components/fingerRig/eh_finger_mainCurlExec.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `mainFingerCurlRig(nameSpace, fingerbehavior, fingerName, side, ...)`

### 📄 `autoRig/components/fingerRig/eh_finger_mainCurlRig.py`
**คำอธิบาย / รายละเอียด:** from function.rigging import fingerOffsetRig

**ฟังก์ชันหลัก (Functions - 15 รายการ):**
- `defineVariable(fingerbehavior, fingerName, side, numCtrl, ...)`
- `createOffsetGrp(side, fingerName, numCtrl, zroNam, ...)`
- `creaePostStore(nameSpace, side, fingerbehavior)`
- `creRelax(side, finName, amp)`
- `creCup(side, finName, amp)`
- `_creStoVal(fingerName, numCtrl, side, axis, ...)`
- `connectToOffGrp(fingerName, fingerbehavior, numCtrl, side, ...)`
- `doCreateAttr(ctrlName, fingerbehavior)`
- `_normalCon(nameSpace, ctrlName, name, side)`
- `normalConnect(nameSpace, ctrlName, fingerbehavior, side)`
- `conxAdv(ctrlName, side, finger, position)`
- `connectPma(nameSpace, fingerName, side, numCtrl, ...)`
- *...และอีก 3 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/components/fingerRig/fix_orientJntAferRunCode.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/limbRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/limbRig/eh_createIKStretch.py`
**คำอธิบาย / รายละเอียด:** Dode Create IK strerchy

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `mag(v)`
- `iKStretch(ikJnt, ikCtrl, region, side, ...)`

### 📄 `autoRig/components/limbRig/eh_createSoftIk.py`
**คำอธิบาย / รายละเอียด:** ... Core function from nick miller ...Formula  y = { -(x-da)/ dsoft(1 - e^  dsoft  ) + da   (da <= x) }  da = length_AB - dsoft length_AB = sum of bone lengths dsoft = user set soft distance (how far the effector should fall behind) x = distance between root and ik

**คลาส (Classes):**
- `class SoftIkLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `mag(v)`
- `softIK(nameSpace, priorMeta, region, side, ...)`

### 📄 `autoRig/components/limbRig/eh_fkIkTwistGenRig_R15.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `eh_fkIkTwistGenRig_R15(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/components/limbRig/eh_fkIkTwistGenRig_rbnMatrix.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `fkIkTwistGenRig(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/components/limbRig/eh_midLockModule.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.components.limbRig import eh_midLockModule

**คลาส (Classes):**
- `class MidLockLogger`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `createDistance(nameSpace, part, startP, endP, ...)`
- `createBlendColor(nameSpace, uprDistance, lwrDistance, side, ...)` — *Copy shape to a specified target transform.*
- `doAddAttr(povName, region)` — *add attribute to pov*
- `connectIkJnt(stretchNode, upperIKJnt, lowerIKJnt, blendName, ...)` — *Connect node to ik joint*

### 📄 `autoRig/components/limbRig/eh_proc.py`
**คำอธิบาย / รายละเอียด:** Proc from function.rigging.autoRig.components.limbRig import proc as pc reload(pc)

**ฟังก์ชันหลัก (Functions - 16 รายการ):**
- `clearVis(suffix, hide)`
- `QuickProc(giveName, side, switchCtrl)`
- `renameShd(overideName)`
- `piston(masterA, masterB)`
- `resetAllController(reference)`
- `boneCount()`
- `twistNrbRig(nameSpace, stJnt, enJnt, charScale)`
- `twistRig(nameSpace, stJnt, enJnt, charScale)`
- `setupShowArmor(sex, digit, giveName)`
- `setupSelectedArmor()`
- `exportSelArmor()`
- `exportSelOutfit()`
- *...และอีก 4 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/components/limbRig/eh_twistRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `twistRigAuto(nameSpace, parent_jnt, child_jnt, fk_shoulderCtrl, ...)` — *Create single joint at the same position of shoulder or thigh that ignore rotation y (twist)*

### 📄 `autoRig/components/limbRig/quaruped/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/limbRig/quaruped/eh_quradrupedLegRig_V1_default.py`
**คลาส (Classes):**
- `class QuardrupedLogger`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `quradrupedLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `plantigradeLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `add_guide_preferred_angle_attrs()` — *Adds 'guide_preferredAngle' X, Y, Z attributes to the selected joints.*

### 📄 `autoRig/components/limbRig/quaruped/eh_quradrupedLegRig_V2_set_prefferenceAngle.py`
**คลาส (Classes):**
- `class QuardrupedLogger`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `quradrupedLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `plantigradeLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `add_guide_preferred_angle_attrs()` — *Adds 'guide_preferredAngle' X, Y, Z attributes to the selected joints.*

### 📄 `autoRig/components/limbRig/quaruped/eh_quradrupedLegRig_V3_doubleIK.py`
**คำอธิบาย / รายละเอียด:** ... try to run by line

### 📄 `autoRig/components/limbRig/quaruped/eh_quradrupedLegRig_V4_blender.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `create_rear_paw_rig(side, name)` — *Creates a procedural Rear Paw (Digitigrade) rig in Maya.*

### 📄 `autoRig/components/limbRig/quaruped/eh_quradrupedLegRig_V5_anotherIK.py`
**คำอธิบาย / รายละเอียด:** ... Another multi IK method rear pow rig

### 📄 `autoRig/components/ribbonRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/ribbonRig/build_updated_ribbon.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/ribbonRig/eh_hh_matrixRibbonDeBoor.py`
**คลาส (Classes):**
- `class RibbonLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `performMatrixRibbonRig(charScale, jointTop, jointBtm, aim_axis, ...)`
- `makeHigesMover(nameSpace, part, side, topName, ...)`

### 📄 `autoRig/components/ribbonRig/eh_hh_ribbonExt.py`
**คำอธิบาย / รายละเอียด:** ... Updated hhRibbon using matrix de_boor math with autoRig integration

**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `de_boor_ribbon(cvs, baseName, side, nameSpace, ...)` — *AutoRig integrated de_boor_ribbon.*
- `get_consolidated_wts(wts, original_cvs, cvs)`
- `create_wt_add_matrix(matrix_attrs, wts, name, tol)`
- `get_weighted_translation_matrix(matrices, wts)`
- `deDoor_makeHigesMover(nameSpace, part, side, topName, ...)`

### 📄 `autoRig/components/ribbonRig/eh_matrixRibbonDeBoor_raw.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/components/ribbonRig/eh_matrixRibbonDeBoor_raw_v002.py`
**คลาส (Classes):**
- `class RibbonLogger`

### 📄 `autoRig/components/ribbonRig/eh_matrixRibbonDeBoor_raw_v003.py`
**คลาส (Classes):**
- `class RibbonLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `performMatrixRibbonRig(charScale, jointTop, jointBtm, aim_axis, ...)`

### 📄 `autoRig/components/ribbonRig/eh_matrixRibbonRig_bug .py`
**คำอธิบาย / รายละเอียด:** ------------------------------------------------------------------------------ CANCLE FOR NOW IS NOT WORK ------------------------------------------------------------------------------

**คลาส (Classes):**
- `class RibbonLogger`
- `class CurveException` — *Raised to indicate invalid curve parameters. *

**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `defaultKnots(count, degree)`
- `pointOnCurveWeights(cvs, t, degree, knots)`
- `tangentOnCurveWeights(cvs, t, degree, knots)`
- `ribbonRigExt(nameSpace, width, numJoints, side, ...)` — *De Boor Matrix Spline Ribbon AutoRig System.*
- `makeHigesMover(nameSpace, part, side, btmName, ...)`

### 📄 `autoRig/components/ribbonRig/eh_ribbonRigExt.py`
**คำอธิบาย / รายละเอียด:** ... Ribbon rig convert ... uncheck scale segment compensage

**คลาส (Classes):**
- `class RibbonLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `ribbonRigExt(nameSpace, width, numJoints, side, ...)`
- `makeHigesMover(nameSpace, part, side, topName, ...)`

### 📄 `autoRig/components/ribbonSnakeRig/01_matrixspine_Snake_v007.py`
**คำอธิบาย / รายละเอียด:** Functions for generating spline weights by Cole O'Brien

**คลาส (Classes):**
- `class CurveException` — *Raised to indicate invalid curve parameters. *

**ฟังก์ชันหลัก (Functions - 10 รายการ):**
- `defaultKnots(count, degree)` — *Gets a default knot vector for a given number of cvs and degrees.*
- `pointOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve weight values on a spline curve.*
- `tangentOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve tangent weight values.*
- `pointOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface point weight values.*
- `tangentUOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the u axis.*
- `tangentVOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the v axis.*
- `_is2020()` — *Determines whether the current maya version is 2020+ *
- `_testCube(radius, color, name, position)` — *Creates a cube for testing purposes. *
- `_testSphere(radius, color, name, position)` — *Creates a sphere for testing purposes. *
- `_creParentCtrl(size, color, name, ctrlShape)`

### 📄 `autoRig/components/ribbonSnakeRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

---

<a id="components_ribbon_spine"></a>
## 3. Rig Components: Ribbon, Spine, Spline & Dynamic (ระบบริบบอน กระดูกสันหลัง และไดนามิกส์)
*ระบบ Ribbon Matrix De Boor spline, Matrix Spine, Dynamic IK Tail/Spine และ Curve pinned setups*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `37` ไฟล์

### 📄 `autoRig/addRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/addRig/createFkRig.py`
**คำอธิบาย / รายละเอียด:** #... example

**คลาส (Classes):**
- `class createFKRigLogger`

**ฟังก์ชันหลัก (Functions - 14 รายการ):**
- `make_list(letter, leng, pattern, prefix)`
- `fkRig_omni_newCurl(nameSpace, parentCtrlTo, jntLst, charScale, ...)`
- `_is_parent(parent, is_child)`
- `fkRig_omni_matrix(nameSpace, parentCtrlTo, jntLst, charScale, ...)`
- `fkRig_new_curl_ext(nameSpace, parentCtrlTo, jntLst, charScale, ...)`
- `smoothFk(broad_jnt, nurbs, region, side, ...)`
- `fkRig_newCurl(nameSpace, name, parentTo, tmpJnt, ...)`
- `createFkRig_direct(nameSpace, name, parentTo, tmpJnt, ...)`
- `newCreateFkRig(nameSpace, name, parentTo, tmpJnt, ...)` — *priorJnt can be False then it will be parent to world instead *
- `createFkRig(nameSpace, name, parentTo, tmpJnt, ...)` — *priorJnt can be False then it will be parent to world instead *
- `checkUnerScore(name)`
- `fkMulChild(nameSpace, name, parentTo, tmpJnt, ...)`
- *...และอีก 2 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/addRig/creatingDynamicIkSpineRig.py`
**คำอธิบาย / รายละเอียด:** Date: 23.01.Jan.31.Tue.08_

**คลาส (Classes):**
- `class DynLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createDynamicTail(side, baseName, firstJnt, lastJnt, ...)`

### 📄 `autoRig/addRig/eh_createFkRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `create_fk_chain(nameSpace, parentCtrlTo, jntLst, charScale, ...)` — *Creates an FK chain with optional Curl controller and Matrix-based Local/World switch.*

### 📄 `autoRig/addRig/eh_creatingDynamicIkSpineRig.py`
**คำอธิบาย / รายละเอียด:** Date: 23.01.Jan.31.Tue.08_

**คลาส (Classes):**
- `class DynLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createDynamicTail(side, baseName, firstJnt, lastJnt, ...)`

### 📄 `autoRig/addRig/eh_creatingNoneDynamicIkSpineRig.py`
**คำอธิบาย / รายละเอียด:** Date: 23.01.Jan.31.Tue.08_

**คลาส (Classes):**
- `class IkLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createNoneDynamicTail(side, baseName, firstJnt, lastJnt, ...)`

### 📄 `autoRig/addRig/fkSkirtSpine.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.addRig import fkSkirtSpine as fse

**คลาส (Classes):**
- `class DynLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `fkSkirtSpline(side, baseName, firstJnt, lastJnt, ...)`

### 📄 `autoRig/addRig/simpleAutoSkirt.py`
**คำอธิบาย / รายละเอียด:** ... \rigging\autoRig\addRig\simpleAutoSkirt ... todo ... make skirt on/off ... make limit angle condition in case sharing with two side ... must place orientation alone with Y along Z up

### 📄 `autoRig/addRig/tentacle_fkIkDeformedRig.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.addRig import tentacle_fkIkDeformedRig as tenFkIkRig

**คลาส (Classes):**
- `class TentacleRig`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `fkIkDeformed(SIDE, BASE_NAME, SCALE, COUNT_DETAIL, ...)`

### 📄 `autoRig/addRig/tentacle_fkIkSpineReplace.py`
**คลาส (Classes):**
- `class FkIkSpineReplace`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `tentacle_fkIkReplace(nurbs_surface, num_pins, num_fk_joints, region, ...)`

### 📄 `de_boor/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `de_boor/backup/de_boor_core.py`
**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `get_open_uniform_kv(n, d)` — *Get open uniform knot vector*
- `get_periodic_uniform_kv(n, d)` — *Get periodic uniform knot vector.  Append d values to the start and end*
- `knot_vector(kv_type, cvs, d)` — *Convenience function for creating knot vectors and editing cv/joint/controls/etc lists*
- `de_boor(n, d, t, kv, ...)` — *Examples:*

### 📄 `de_boor/backup/hh_de_boor_to_surface.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.de_boor import hh_de_boor_to_surface as srf_deboor

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `list_joints_from_skincluster(skincluster)`
- `split_with_surface_debug(mesh, jnt_grid, surface, d, ...)`
- `split_surface_1D_from_cvs(surface, jnts, direction, d, ...)`

### 📄 `de_boor/backup/skincluster_surface.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `split_with_surface(verts, jnts, srf, d, ...)` — *Procedurally set the skinCluster weights for the joints attached to the skinCluster deforming the verts using the*

### 📄 `de_boor/cb_matrix_spine.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.de_boor import cb_matrix_spine_core as cb

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `defaultKnots(count, degree)` — *Gets a default knot vector for a given number of cvs and degrees.*
- `tangentOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve tangent weight values.*
- `pointOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve weight values on a spline curve.*

### 📄 `de_boor/cb_matrixspline_original.py`
**คำอธิบาย / รายละเอียด:** Functions for generating spline weights.

**คลาส (Classes):**
- `class CurveException` — *Raised to indicate invalid curve parameters. *

**ฟังก์ชันหลัก (Functions - 12 รายการ):**
- `defaultKnots(count, degree)` — *Gets a default knot vector for a given number of cvs and degrees.*
- `pointOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve weight values on a spline curve.*
- `tangentOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve tangent weight values.*
- `pointOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface point weight values.*
- `tangentUOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the u axis.*
- `tangentVOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the v axis.*
- `_is2020()` — *Determines whether the current maya version is 2020+ *
- `_testCube(radius, color, name, position)` — *Creates a cube for testing purposes. *
- `_testSphere(radius, color, name, position)` — *Creates a sphere for testing purposes. *
- `_testMatrixOnCurve(count, pCount, degree)` — *Creates an example curve with the given cv and point counts.*
- `_testMatrixOnCircularCurve(count, pCount, degree)` — *Creates an example circular curve with the given cv and point counts.*
- `_testMatrixOnSurface(uCount, vCount, degree)` — *Tests matrixOnSurface with the given cv counts.*

### 📄 `de_boor/de_boor_skincluster_surface_sample.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `de_boor/hh_blendshape.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `split_with_curve(mesh, base_mesh, crv, output_names, ...)` — *Procedurally create blendShape targets by extracting the offset vectors between the mesh and base mesh; getting the*

### 📄 `de_boor/hh_de_boor_core.py`
**คำอธิบาย / รายละเอียด:** from function.framework.reloadWrapper import reloadWrapper as reload

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `get_open_uniform_kv(n, d)` — *Get open uniform knot vector*
- `get_periodic_uniform_kv(n, d)` — *Get periodic uniform knot vector.  Append d values to the start and end*
- `knot_vector(kv_type, cvs, d)` — *Convenience function for creating knot vectors and editing cv/joint/controls/etc lists*
- `de_boor(n, d, t, kv, ...)` — *Examples:*

### 📄 `de_boor/hh_de_boor_core_sample.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `de_boor/hh_de_boor_to_curve.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.de_boor import hh_de_boor_to_curve

**ฟังก์ชันหลัก (Functions - 11 รายการ):**
- `ramp_style_falloff_A(t_n)` — *Custom falloff to match sculpted ramp curve in lip rig.*
- `ramp_style_falloff(t_n)`
- `ease_in_out_sine(t)`
- `ease_in_cubic(t)`
- `ease_out_cubic(t)`
- `custom_falloff_t(t_n, method)`
- `shape_weights(weights, jnts, shape)`
- `skin_curve_with_de_boor(jnts, crv, d, tol, ...)`
- `split_curve_cvs_with_de_boor_v2(jnts, crv, d, tol)`
- `list_joints_from_skincluster(skincluster)`
- `split_curve_cvs_with_de_boor_v4(joints, curve, degree, falloff_mode, ...)`

### 📄 `de_boor/hh_de_boor_to_mesh.py`
**คำอธิบาย / รายละเอียด:** ... Split weight with curve to mesh ... Request mesh, curve, joint ... verts is mean mesh my friend

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `split_with_curve_to_mesh(verts, jnts, crv, d, ...)`
- `_check_and_fix_joint_order(jnts, crv)`
- `split_with_curve_to_mesh_V2(verts, jnts, crv, d, ...)`
- `list_joints_from_skincluster(skincluster)`

### 📄 `de_boor/hh_de_boor_to_surface.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.de_boor import hh_de_boor_to_surface as srf_deboor

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `list_joints_from_skincluster(skincluster)`
- `split_with_surface_debug(mesh, jnt_grid, surface, d, ...)`
- `split_surface_1D_from_cvs(surface, jnts, direction, d, ...)`
- `split_surface_1D_from_cvs_open_only(surface, jnts, direction, d, ...)`

### 📄 `de_boor/hh_ribbon.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.de_boor import hh_ribbon as ribbon

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `de_boor_ribbon(cvs, aim_axis, up_axis, num_joints, ...)` — *Use controls and de_boor function to get position, tangent and up values for joints.  The param_from_length can*
- `get_consolidated_wts(wts, original_cvs, cvs)`
- `create_wt_add_matrix(matrix_attrs, wts, name, tol)`
- `get_weighted_translation_matrix(matrices, wts)`

### 📄 `de_boor/hh_ribbon_sample.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `de_boor/hh_skincluster_curve.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.de_boor import hh_skincluster_curve as hhskcc

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `split_with_curve(verts, jnts, crv, d, ...)` — *Procedurally set the skinCluster weights for the joints attached to the skinCluster deforming the verts using the*

### 📄 `de_boor/hh_skincluster_curve_sample.py`
**คำอธิบาย / รายละเอียด:** ... Splite weight with curve to mesh ... Request mesh, curve, joint

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `split_with_curve(verts, jnts, crv, d, ...)`

### 📄 `de_boor/hh_skincluster_curve_sample02.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `split_curve_cvs_with_de_boor(jnts, crv, d, tol)`

### 📄 `de_boor/hh_skincluster_curve_sample03.py`
**คำอธิบาย / รายละเอียด:** ... distribute de boor weight value to curve

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `split_curve_cvs_with_de_boor_v2(jnts, crv, d, tol)`
- `list_joints_from_skincluster(skincluster)`

### 📄 `de_boor/hh_skincluster_surface.py`
**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `list_joints_from_skincluster(skincluster)`
- `split_with_surface_debug(mesh, jnt_grid, surface, d, ...)`

### 📄 `de_boor/hh_skincluster_surface_sample.py`
**คำอธิบาย / รายละเอียด:** ... using nrb as a proxy to skin mesh with joint

### 📄 `de_boor/matrixSpine/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `de_boor/matrixSpine/eh_matrixSpine_01_Merge.py`
**คำอธิบาย / รายละเอียด:** ===============================================================================

**คลาส (Classes):**
- `class CurveException` — *Custom exception raised when curve parameters or knot vector lengths are invalid.*

**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `defaultKnots(count, degree)` — *Generate a standard clamped knot vector for a given number of CVs and curve degree.*
- `pointOnCurveWeights(cvs, t, degree, knots)` — *Calculate CV blend weights at parameter $t$ along a B-spline curve using de Boor's algorithm.*
- `tangentOnCurveWeights(cvs, t, degree, knots)` — *Calculate derivative tangent blend weights at parameter $t$ along a B-spline curve.*
- `apply_static_offset(slave_ctrl, guide_loc, spline_output_node)` — *Calculate and apply a static offset matrix to zero out a slave controller transform.*
- `matrix_spine_setup(main_guides, child_guides, pCount, side, ...)` — *Construct a modular De Boor Matrix Spline rig for spine, neck, or tentacle components.*

### 📄 `de_boor/matrixSpine/eh_matrixSpine_03_weightRelationship.py`
**คำอธิบาย / รายละเอียด:** ... Script for matrix weight relationship between main spine controllers ... Based on Cole O'Brien de Boor spline logic and repository standards

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `apply_multi_blend_matrix(target, drivers_and_weights, translate, rotate, ...)` — *Apply a matrix-based parent blend constraint from multiple drivers to a target node.*
- `setup_relationships(relationship_dict, translate, rotate, scale)` — *Setup multiple matrix-based weight relationships using a configuration dictionary.*

### 📄 `de_boor/matrixspine_simple.py`
**คำอธิบาย / รายละเอียด:** Functions for generating spline weights by Cole O'Brien

**คลาส (Classes):**
- `class CurveException` — *Raised to indicate invalid curve parameters. *

**ฟังก์ชันหลัก (Functions - 10 รายการ):**
- `defaultKnots(count, degree)` — *Gets a default knot vector for a given number of cvs and degrees.*
- `pointOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve weight values on a spline curve.*
- `tangentOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve tangent weight values.*
- `pointOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface point weight values.*
- `tangentUOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the u axis.*
- `tangentVOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the v axis.*
- `_is2020()` — *Determines whether the current maya version is 2020+ *
- `_testCube(radius, color, name, position)` — *Creates a cube for testing purposes. *
- `_testSphere(radius, color, name, position)` — *Creates a sphere for testing purposes. *
- `_creParentCtrl(size, color, name, ctrlShape)`

### 📄 `de_boor/matrixspline_original.py`
**คำอธิบาย / รายละเอียด:** Functions for generating spline weights.

**คลาส (Classes):**
- `class CurveException` — *Raised to indicate invalid curve parameters. *

**ฟังก์ชันหลัก (Functions - 12 รายการ):**
- `defaultKnots(count, degree)` — *Gets a default knot vector for a given number of cvs and degrees.*
- `pointOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve weight values on a spline curve.*
- `tangentOnCurveWeights(cvs, t, degree, knots)` — *Creates a mapping of cvs to curve tangent weight values.*
- `pointOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface point weight values.*
- `tangentUOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the u axis.*
- `tangentVOnSurfaceWeights(cvs, u, v, uKnots, ...)` — *Creates a mapping of cvs to surface tangent weight values along the v axis.*
- `_is2020()` — *Determines whether the current maya version is 2020+ *
- `_testCube(radius, color, name, position)` — *Creates a cube for testing purposes. *
- `_testSphere(radius, color, name, position)` — *Creates a sphere for testing purposes. *
- `_testMatrixOnCurve(count, pCount, degree)` — *Creates an example curve with the given cv and point counts.*
- `_testMatrixOnCircularCurve(count, pCount, degree)` — *Creates an example circular curve with the given cv and point counts.*
- `_testMatrixOnSurface(uCount, vCount, degree)` — *Tests matrixOnSurface with the given cv counts.*

### 📄 `de_boor/sample.py`
**คำอธิบาย / รายละเอียด:** .................................... splite weight to curve

---

<a id="components_fingers_face"></a>
## 4. Rig Components: Fingers & Face/Head (ระบบนิ้ว ใบหน้า และส่วนศีรษะ)
*โมดูลสร้าง Rig นิ้วมือ (FK/IK/Curl/SDK), คอ, ศีรษะ, ขากรรไกร และโครงสร้างใบหน้าเบื้องต้น*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `12` ไฟล์

### 📄 `autoRig/bodyRig/facialRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/facialRig/eyeRig_Marco_ext.py`
**คำอธิบาย / รายละเอียด:** # direct run

**คลาส (Classes):**
- `class EyeRigMarco`

**ฟังก์ชันหลัก (Functions - 6 รายการ):**
- `_unparent_if_not_world(obj_name)`
- `createControlEye(group_name, CENTER, SIDE, PART, ...)`
- `makeInbetweener(eye_up_dict, eye_down_dict)`
- `makeSmartBlink(SIDE, CURVE, up_low_crv, down_low_crv, ...)`
- `arrange_eye_grp(eye_up_dict, eye_down_dict, smartBlink, center_loc, ...)`
- `cre_eye_bJnt(eye_up_dict, eye_down_dict, SIDE, region, ...)`

### 📄 `autoRig/bodyRig/facialRig/eyeRig_marco.py`
**คำอธิบาย / รายละเอียด:** # direct run

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `eyeRig_marco(loc_grp, part_dict, CENTER, SIDE, ...)`
- `make_eyeMarco_blink(PART, SIDE, CURVE, up_low_crv, ...)`

### 📄 `autoRig/bodyRig/facialRig/jawRig_gnm.py`
**คำอธิบาย / รายละเอียด:** ... jaw rig using weight distribute ... newest than in git ...source >>> I:\Resource\Tutorial\Rigging The Jaw with Python in Maya\MyFile

**ฟังก์ชันหลัก (Functions - 20 รายการ):**
- `addOffset(dst, suffix)` — *create zero group  *
- `createGuides(number)` — *create locator template guide  *
- `lip_guides()` — *return name template*
- `jaw_guides()`
- `build()`
- `createHierarchy()` — *create template group*
- `createMinorJoints()` — *04 create Main Structre minor joint*
- `createBroadJoints()`
- `createJawBase()`
- `constraintBroadJoints()`
- `getLipParts()`
- `lipPart(part)`
- *...และอีก 8 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/bodyRig/fingerCurlMainRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/headRigExt/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/headRigExt/headRigExtFacial_jh.py`
**คำอธิบาย / รายละเอียด:** ... using this module D:\sysTools\nmTools_github\riggerTools\python\function\rigging\autoRig\bodyRig\headRigExt Neck rig module

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `_eyeCtrl(nameSpace, eyeJntNam, side, headJnt, ...)`
- `headRig(nameSpace, parentTo, tmpJnt, faceCtrl, ...)`

### 📄 `autoRig/bodyRig/headRigExt/headRigExtFacial_v2.py`
**คำอธิบาย / รายละเอียด:** ... Use with for GeNoMon mounth and Marco eye rig ... Neck rig module ... add top, bottom head joint ... add reverse jaw for jaw rig

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `_eyeCtrl(nameSpace, eyeJntNam, side, headJnt, ...)`
- `headRig(nameSpace, parentTo, tmpJnt, faceCtrl, ...)`

### 📄 `autoRig/bodyRig/jawRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/jawRig/jawRig_gnm_core.py`
**คำอธิบาย / รายละเอียด:** ... jaw rig using weight distribute ...source >>> I:\Resource\Tutorial\Rigging The Jaw with Python in Maya\MyFile

**ฟังก์ชันหลัก (Functions - 20 รายการ):**
- `addOffset(dst, suffix)` — *create zero group  *
- `createGuides(number)` — *create locator template guide  *
- `lip_guides()` — *return name template*
- `jaw_guides()`
- `build()`
- `createHierarchy()` — *create template group*
- `createMinorJoints()` — *04 create Main Structre minor joint*
- `createBroadJoints()`
- `createJawBase()`
- `constraintBroadJoints()`
- `getLipParts()`
- `lipPart(part)`
- *...และอีก 8 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/bodyRig/spineRigExt/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/spineRigExt/spineFkRigExt.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.bodyRig.spineRigExt import spineFkRigExt

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `newSpineFkRig(nameSpace, name, parentTo, tmpJnt, ...)` — *priorJnt can be False then it will be parent to world instead *

---

<a id="build_runners"></a>
## 5. Rig Builders, Body Rig & Pipeline Runners (ตัวประกอบริกอัตโนมัติและสคริปต์สร้างริกสำเร็จรูป)
*สคริปต์ Assembly ระดับ Character/Creature, Body rig orchestrator และ Master build execution*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `67` ไฟล์

### 📄 `autoRig/bodyRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/armRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `armRigExt(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/bodyRig/bipedLegRig.py`
**คำอธิบาย / รายละเอียด:** log use the same  rotateOrder of both bJnt and ctrl

**คลาส (Classes):**
- `class BipedLegRig`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `footRollRig(nameSpace, side, region, tmpJnt, ...)`
- `bipedLegRigExt(nameSpace, parentTo, side, region, ...)`

### 📄 `autoRig/bodyRig/clavicleRig.py`
**คำอธิบาย / รายละเอียด:** ... change local/world attatch to shape node

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `clavicleRig(nameSpace, parentTo, side, tmpJnt, ...)`

### 📄 `autoRig/bodyRig/createElbowKneeLock.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/createIKStretch.py`
**คำอธิบาย / รายละเอียด:** Dode Create IK strerchy

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `mag(v)`
- `iKStretch(ikJnt, ikCtrl, region, side, ...)`

### 📄 `autoRig/bodyRig/createSoftIk.py`
**คำอธิบาย / รายละเอียด:** ... Core function from nick miller ...Formula  y = { -(x-da)/ dsoft(1 - e^  dsoft  ) + da   (da <= x) }  da = length_AB - dsoft length_AB = sum of bone lengths dsoft = user set soft distance (how far the effector should fall behind) x = distance between root and ik

**คลาส (Classes):**
- `class SoftIkLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `mag(v)`
- `softIK(nameSpace, priorMeta, region, side, ...)`

### 📄 `autoRig/bodyRig/edeglau_create_ik_stretch.py`
**คำอธิบาย / รายละเอียด:** File: stretchIK.py Project: edeglau/storage Elise edeglau

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `create_ik_stretch(self, alljoints, getbones)`

### 📄 `autoRig/bodyRig/eh_quradrupedLegRig_ext.py`
**คลาส (Classes):**
- `class QuardrupedLogger`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `quradrupedLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `plantigradeLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `add_guide_preferred_angle_attrs()` — *Adds 'guide_preferredAngle' X, Y, Z attributes to the selected joints.*

### 📄 `autoRig/bodyRig/eh_spineFKRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bodyRig/fingerRig.py`
**คำอธิบาย / รายละเอียด:** FK Five Finger Rig

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `fingerRig(nameSpace, side, fingerNum, fingerName, ...)`
- `fingerRigExt(nameSpace, side, fingerNum, fingerName, ...)`
- `baseFingerRig(nameSpace, side, fingerNum, fingerName, ...)`
- `connect_finger_value(stickNam, fingerName, side, defaultValue)`

### 📄 `autoRig/bodyRig/finger_localCurlExec.py`
**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `creEachFingerGrp(nameSpace, parentTo, side, stickNam)` — *Create Main empty grp with name*
- `creHandStick(nameSpace, fingerName, side, charScale, ...)` — *Create Local small stick controller*
- `creLocalFingerAttr(nameSpace, fingerName, side, ctrlName, ...)`
- `runLocalFingerRig(nameSpace, fingerName, side, charScale, ...)`
- `localFingerAllRig(nameSpace, parentTo, side, fingerName, ...)`

### 📄 `autoRig/bodyRig/finger_localCurlRig.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.module import fingerLocalCurlRig as finLocRig

**ฟังก์ชันหลัก (Functions - 7 รายการ):**
- `connect_LocOffGrp(nameSpace, fingerName, side, numCtrl, ...)`
- `_creLocStoVal(nameSpace, fingerName, numCtrl, side, ...)`
- `creaet_LocalPostStore(nameSpace, side, fingerName, fingerbehavior)`
- `_normalLocalCon(nameSpace, fingerName, side, ctrlName, ...)`
- `connectLocalPma(nameSpace, fingerName, side, nameOfPost, ...)`
- `conLocRollPma(nameSpace, fingerName, side, nameOfPost, ...)`
- `creaeLocalPostStore(nameSpace, side, fingerName, fingerbehavior)`

### 📄 `autoRig/bodyRig/finger_mainCurlExec.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `mainFingerCurlRig(nameSpace, fingerbehavior, fingerName, side, ...)`

### 📄 `autoRig/bodyRig/finger_mainCurlRig.py`
**คำอธิบาย / รายละเอียด:** from function.rigging import fingerOffsetRig

**ฟังก์ชันหลัก (Functions - 15 รายการ):**
- `defineVariable(fingerbehavior, fingerName, side, numCtrl, ...)`
- `createOffsetGrp(side, fingerName, numCtrl, zroNam, ...)`
- `creaePostStore(nameSpace, side, fingerbehavior)`
- `creRelax(side, finName, amp)`
- `creCup(side, finName, amp)`
- `_creStoVal(fingerName, numCtrl, side, axis, ...)`
- `connectToOffGrp(fingerName, fingerbehavior, numCtrl, side, ...)`
- `doCreateAttr(ctrlName, fingerbehavior)`
- `_normalCon(nameSpace, ctrlName, name, side)`
- `normalConnect(nameSpace, ctrlName, fingerbehavior, side)`
- `conxAdv(ctrlName, side, finger, position)`
- `connectPma(nameSpace, fingerName, side, numCtrl, ...)`
- *...และอีก 3 ฟังก์ชันภายในโมดูล*

### 📄 `autoRig/bodyRig/fkIkGenRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `fkIkGenRig(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/bodyRig/fkIkTwistGenRig.py`
**คำอธิบาย / รายละเอียด:** ... ... Create FK/IK switch

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `fkIkTwistGenRig(nameSpace, charScale, parentTo, side, ...)`

### 📄 `autoRig/bodyRig/ge_hipRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - Pelvis rig module 02_hipRig

**คลาส (Classes):**
- `class HipRigLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `hipRig(nameSpace, ctrl_grp, tmpJnt, charScale, ...)`
- `quradpedHipRig(nameSpace, parentTo, tmpJnt, charScale)`

### 📄 `autoRig/bodyRig/ge_rootRig.py`
**คำอธิบาย / รายละเอียด:** ... ... DESCRIPTION: Core function for creating the root rig groups and master controls. ...

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createMasterGrp(nameSpace, charScale, PROJECT_DICT)` — *# ... Creates the main master control groups and controls for the rig hierarchy.*

### 📄 `autoRig/bodyRig/headRig.py`
**คำอธิบาย / รายละเอียด:** Neck rig module

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `_eyeCtrl(nameSpace, eyeJntNam, side, headJnt, ...)`
- `headRig(nameSpace, parentTo, tmpJnt, faceCtrl, ...)`

### 📄 `autoRig/bodyRig/headRigExtFacial_jh.py`
**คำอธิบาย / รายละเอียด:** ... using this module instead D:\sysTools\nmTools_github\riggerTools\python\function\rigging\autoRig\bodyRig\headRigExt Neck rig module

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `_eyeCtrl(nameSpace, eyeJntNam, side, headJnt, ...)`
- `headRig(nameSpace, parentTo, tmpJnt, faceCtrl, ...)`

### 📄 `autoRig/bodyRig/hipRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - Pelvis rig module 02_hipRig

**คลาส (Classes):**
- `class HipRigLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `hipRig(nameSpace, ctrl_grp, tmpJnt, charScale, ...)`
- `quradpedHipRig(nameSpace, parentTo, tmpJnt, charScale)`

### 📄 `autoRig/bodyRig/midLockModule.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.bodyRig import midLockModule

**คลาส (Classes):**
- `class MidLockLogger`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `createDistance(nameSpace, part, startP, endP, ...)`
- `createBlendColor(nameSpace, uprDistance, lwrDistance, side, ...)` — *Copy shape to a specified target transform.*
- `doAddAttr(povName, region)` — *add attribute to pov*
- `connectIkJnt(stretchNode, upperIKJnt, lowerIKJnt, blendName, ...)` — *Connect node to ik joint*

### 📄 `autoRig/bodyRig/neckRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 04_Neck rig module

**คลาส (Classes):**
- `class NeckRigLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `neckRig(nameSpace, parentTo, tmpJnt, priorJnt, ...)`
- `quradpedNeckRig(nameSpace, parentTo, tmpJnt, charScale, ...)` — *neck rig for quradruped *

### 📄 `autoRig/bodyRig/propRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - prop Rig module

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `propRig(nameSpace, ctrl_grp, tmpJnt, charScale, ...)`

### 📄 `autoRig/bodyRig/quradrupedLegRig.py`
**คลาส (Classes):**
- `class QuardrupedLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `quradrupedLegRig(nameSpace, parentTo, side, tmpJnt, ...)`
- `plantigradeLegRig(nameSpace, parentTo, side, tmpJnt, ...)`

### 📄 `autoRig/bodyRig/ribbonRig.py`
**คำอธิบาย / รายละเอียด:** Dear future me. Please forgive me.

**คลาส (Classes):**
- `class RibbonLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `ribbonRig(nameSpace, width, numJoints, side, ...)`
- `makeHigesMover(nameSpace, part, side, btmName, ...)`

### 📄 `autoRig/bodyRig/ribbonRigExt.py`
**คำอธิบาย / รายละเอียด:** ... Ribbon rig convert ... uncheck scale segment compensage

**คลาส (Classes):**
- `class RibbonLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `ribbonRigExt(nameSpace, width, numJoints, side, ...)`
- `makeHigesMover(nameSpace, part, side, btmName, ...)`

### 📄 `autoRig/bodyRig/rootRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - Create Master Template group 01_rootRig_cleanup_v008

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createMasterGrp(nameSpace, charScale, PROJECT_DICT)`

### 📄 `autoRig/bodyRig/spineFkRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - Spine rig module 03_hipRig

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `spineRig(nameSpace, parentTo, tmpJnt, priorCtrl, ...)`
- `spineFkChainRig(nameSpace, name, parentTo, tmpJnt, ...)`

### 📄 `autoRig/bodyRig/spineIKRig.py`
**คำอธิบาย / รายละเอียด:** This module is create spine IK hybride with FK

**คลาส (Classes):**
- `class spineHybridLog`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `spineHybridIK(nameSpace, parentTo, tmpJnt, priorCtrl, ...)`

### 📄 `autoRig/bodyRig/spineRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - -  spine ik Rig by Dode need cog_ctrl and hip_bJnt first//

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `spineIK(nameSpace, spineNum, hipJnt, cog_ctrl, ...)`

### 📄 `autoRig/bodyRig/torsoRig.py`
**คำอธิบาย / รายละเอียด:** New Spine Rig

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `torsoRig(nameSpace, ctrl_grp, tmpJnt, charScale)`

### 📄 `autoRig/bodyRig/twistRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `twistRigAuto(nameSpace, parent_jnt, child_jnt, fk_shoulderCtrl, ...)` — *Create single joint at the same position of shoulder or thight that ignore Rotation y (twist)*

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

**คำอธิบาย / รายละเอียด:** ...reference\templateJoint_quaruped_110_default.ma"

**คำอธิบาย / รายละเอียด:** sixth hores rig


**คำอธิบาย / รายละเอียด:** ===============================================================================

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

### 📄 `autoRig/creatureRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/library/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/library/hero/quarduped_autoRig_cmd.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/library/misc.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `connectFkIkVis(attrName, uprNam, footIKGrp)` — *connectFkIkVis( attrName = 'IK_FK_Arm_L' , uprNam = backlegLFTNam[0] , footIKGrp = footIKLFT )*

### 📄 `autoRig/library/quarduped_autoRig_cmd.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/library/spaceSwitch.py`
**คำอธิบาย / รายละเอียด:** Untimate Switch local IK auto create

### 📄 `autoRig/module/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/module/faceSwapNodeBase.py`
**คำอธิบาย / รายละเอียด:** NewfaceSwap

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `faceSwapNodeBase(mainCtrl, faceNum, mat)`

### 📄 `autoRig/module/spineRig.py`
**คำอธิบาย / รายละเอียด:** __________________ - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - -  spine ik Rig by Dode need cog_ctrl and hip_bJnt first//

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `spineRig(spineNum, hipJnt, cog_ctrl)`

### 📄 `autoRig/object/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/reference/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/reference/templateJoint.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.autoRig.reference import templateJoint as tpJnt

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `importTemplate(templatePath)`
- `openTemplete(templatePath)`
- `refTempRemove(REF_PATH)`

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

### 📄 `autoRig/run_autoRig_run/taiBipedAutoRig_000_default.py`
**คำอธิบาย / รายละเอียด:** Standard autorig version 1.05

### 📄 `autoRig/run_autoRig_run/taiBipedAutoRig_010_noJntTwist.py`
**คำอธิบาย / รายละเอียด:** Standard autorig

### 📄 `autoRig/run_autoRig_run/taiBipedAutoRig_020_noKeepBothFkIk.py`
**คำอธิบาย / รายละเอียด:** Standard autorig

### 📄 `autoRig/run_autoRig_run/taiBipedAutoRig_030_fifthJointFingerRig.py`
**คำอธิบาย / รายละเอียด:** autoRig with spineHybridIK ribbon on

---

<a id="controllers_curves"></a>
## 6. Controllers, Shapes & Curve Tools (เครื่องมือสร้างและจัดการคอนโทรลเลอร์)
*ระบบคลัง NURBS Shapes, เครื่องมือสร้าง Gimbal/Zero group, ปรับแต่งรูปทรง/สี และจัดการขนาดคอนโทรลเลอร์*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `25` ไฟล์

### 📄 `Rigbox_Reborn_Curves_Tool/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `Rigbox_Reborn_Curves_Tool/rr_main_curves.py`
**คำอธิบาย / รายละเอียด:** RigBox Reborn - Main: Curves Tool

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `window_creation()`
- `gui_creation()`
- `create_frameLayout(frame_name)`

### 📄 `Rigbox_Reborn_Curves_Tool/rr_sub_curves_addAttributes.py`
**คำอธิบาย / รายละเอียด:** NOTE: This script has been cleaned to use consistent 4-space indentation only.

**ฟังก์ชันหลัก (Functions - 21 รายการ):**
- `window_creation()`
- `gui_creation()`
- `title_creation(title)`
- `preset_options()`
- `custom_options()`
- `field_display()`
- `add_cogAttrs()`
- `add_eyeAttrs()`
- `add_headAttrs()`
- `add_ikFootAttrs()`
- `add_ikHandAttrs()`
- `add_footSwitchAttrs()`
- *...และอีก 9 ฟังก์ชันภายในโมดูล*

### 📄 `Rigbox_Reborn_Curves_Tool/rr_sub_curves_colorOptions.py`
**คำอธิบาย / รายละเอียด:** Rigbox Reborn - Sub: Color Options

**ฟังก์ชันหลัก (Functions - 6 รายการ):**
- `window_creation()`
- `gui_creation()`
- `rr_colorCurves_buttons(color)`
- `rr_template_object()`
- `rr_untemplate()`
- `rr_template_attr()`

### 📄 `Rigbox_Reborn_Curves_Tool/rr_sub_curves_curveCreation.py`
**คำอธิบาย / รายละเอียด:** RigBox Reborn - Sub: Curve Creation

**ฟังก์ชันหลัก (Functions - 65 รายการ):**
- `window_creation()`
- `gui_creation()`
- `rename_gui()`
- `control_options_gui()`
- `group_naming_gui()`
- `group_instructions_gui()`
- `grouping_options_gui()`
- `control_buttons_gui()`
- `create_shapeButtons_gui()`
- `twoD_controls_gui()`
- `twoD_arrows_gui()`
- `threeD_controls_gui()`
- *...และอีก 53 ฟังก์ชันภายในโมดูล*

### 📄 `Rigbox_Reborn_Curves_Tool/rr_sub_curves_lockHide.py`
**คำอธิบาย / รายละเอียด:** RigBox Reborn - Sub: Curve Creation

**ฟังก์ชันหลัก (Functions - 65 รายการ):**
- `window_creation()`
- `gui_creation()`
- `rename_gui()`
- `control_options_gui()`
- `group_naming_gui()`
- `group_instructions_gui()`
- `grouping_options_gui()`
- `control_buttons_gui()`
- `create_shapeButtons_gui()`
- `twoD_controls_gui()`
- `twoD_arrows_gui()`
- `threeD_controls_gui()`
- *...และอีก 53 ฟังก์ชันภายในโมดูล*

### 📄 `controlShapeManager/__init__.py`
**คำอธิบาย / รายละเอียด:** A python package that creates a control shape manager for maya to load, save, copy, paste, mirror, etc. nurbs curves.

### 📄 `controlShapeManager/functions.py`
**คำอธิบาย / รายละเอียด:** This module contains functions to provide a higher level of interaction with the commands in the manager.py file.

**ฟังก์ชันหลัก (Functions - 14 รายการ):**
- `getAvailableControlShapes()` — *Returns a list of the available control shapes in the specified library. Each element*
- `getAvailableColours()` — *Returns a list of the available 32 colours for overrideColor in maya. Each element*
- `assignColour()` — *Assigns args[0] as the overrideColor of the selected curves*
- `assignControlShape()` — *Assigns args[0] as the shape of the selected curves*
- `saveCtlShapeToLib()` — *Saves the selected shape in the defined control shape library*
- `mirrorCtlShapes()` — *Mirrors the selected control's shape to the other control on the other side*
- `copyCtlShape()` — *Copies the selected control's shape to a global variable for pasting*
- `pasteCtlShape()` — *Assigns the control's shape from the ctlShapeClipboard global variable *
- `flipCtlShape()` — *Flips the selected control shapes to the other side in all axis*
- `flipCtlShapeX()` — *Flips the selected control shapes to the other side in X*
- `flipCtlShapeY()` — *Flips the selected control shapes to the other side in Y*
- `flipCtlShapeZ()` — *Flips the selected control shapes to the other side in Z*
- *...และอีก 2 ฟังก์ชันภายในโมดูล*

### 📄 `controlShapeManager/manager.py`
**คำอธิบาย / รายละเอียด:** Contains the core low level functionality of the control shape manager. The functions here work directly

**ฟังก์ชันหลัก (Functions - 7 รายการ):**
- `getShape(crv)` — *Returns a dictionary containing all the necessery information for rebuilding the passed in crv.*
- `setShape(crv, crvShapeList)` — *Creates a new shape on the crv transform, using the properties in the crvShapeDict.*
- `validateCurve(crv)` — *Checks whether the transform we are working with is actually a curve and returns it's shapes*
- `loadFromLib(shape)` — *Loads the shape data from the shape file in the SHAPE_LIBRARY_PATH directory*
- `saveToLib(crv, shapeName)` — *Saves the shape data to a shape file in the SHAPE_LIBRARY_PATH directory*
- `setColour(crv, colour)` — *Sets the overrideColor of a curve*
- `getColour(crv)` — *Returns the overrideColor of a curve*

### 📄 `controlShapeManager/managerUI.py`
**คำอธิบาย / รายละเอียด:** Creates a very simple UI, which is just a button on a specified shelf containing a popup with all the needed

### 📄 `controlShapeManager/utils.py`
**คำอธิบาย / รายละเอียด:** Contains utility commands to help work and I/O nurbsCurve data.

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `validatePath(path)` — *Checks if the file already exists and provides a dialog to overwrite or not*
- `loadData(path)` — *Loads raw JSON data from a file and returns it as a dict*
- `saveData(path, data)` — *Saves a dictionary as JSON in a file*
- `getKnots(crvShape)`

### 📄 `controllerBox/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `controllerBox/adjustController.py`
**คำอธิบาย / รายละเอียด:** Path                            :

**ฟังก์ชันหลัก (Functions - 9 รายการ):**
- `ctrlWidth(Width)`
- `_makeCurveWidth(name, Width)`
- `creControllerFunc(selected, scale, ctrlShape, color, ...)` — *Create Controller at selected object.*
- `createController()`
- `createZroGrpWithFlexName(selected)`
- `createZroGrp(offset)`
- `createGimbal()`
- `createController(shapeName)`
- `assignColor(color, arg)`

### 📄 `controllerBox/createController.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.controllerBox import createController

**คลาส (Classes):**
- `class ControlMaker`
  - **Methods:** `showUI`, `changeButtonLabel`, `checkCurve`, `createController`, `assignColor`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `run()`

### 📄 `controllerBox/eh_controller.py`
**คำอธิบาย / รายละเอียด:** Module: eh_controller

**คลาส (Classes):**
- `class ControllerLogger`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `createZeroGroupWithOffset(obj)` — *Creates a standard Zero Group and Offset Group structure above the object.*
- `createZeroGroup(obj)` — *Simple Zero Group (Single level).*
- `create(nameSpace, name, ctrlShape, rotateOrder, ...)` — *Creates a controller with Zro/Offset groups, Gimbal, and Constraints.*

### 📄 `controllerBox/flipController.py`
**คลาส (Classes):**
- `class buildUI`
  - **Methods:** `show`, `flipCtrlShapeX`, `flipCtrlShapeY`, `flipCtrlShapeZ`, `copyCtrlShape`, `copyShapeToOpposite`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `run()`

### 📄 `controllerBox/mz_ctrlCreator/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `controllerBox/mz_ctrlCreator/mz_ctrlCreator.py`
**คำอธิบาย / รายละเอียด:** mz_ctrlCreator v1.0.0

**ฟังก์ชันหลัก (Functions - 104 รายการ):**
- `mz_ctrlCreator()`
- `mz_ccUI()`
- `mz_hideManipulator()`
- `mz_showManipulator()`
- `mz_setColor()`
- `mz_groups()`
- `mz_makeGroups(self)`
- `mz_unlockAttrs()`
- `mz_mirrorX(self)`
- `mz_mirrorY(self)`
- `mz_mirrorZ(self)`
- `mz_combineShapes(self)`
- *...และอีก 92 ฟังก์ชันภายในโมดูล*

### 📄 `curve/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `curve/create_curve_from_selected.py`
**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `create_curve_from_selected(obj1, obj2)` — *Create a linear degree-1 curve between two objects.*
- `rebuild_curve_to_degree3(curve, degree, spans)` — *Rebuild a curve to be degree 3 with a given number of spans.*

### 📄 `curve/curveShapeTools.py`
**คำอธิบาย / รายละเอียด:** ... stable version it can run ... Add A to B not work ... Substract A to B not work

**คลาส (Classes):**
- `class CurveShapeTools`
  - **Methods:** `getDagPath`, `storeBaseCurve`, `revertToBase`, `mirror_curve_cvs`, `flipCurve`, `add_curve_shape_relative_from_base`, `subtract_curve_shape`, `copy_curve_shape_via_blendShape`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `create_ui()`

### 📄 `curve/curveTools.py`
**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `create_curve_from_selected(obj1, obj2)` — *Create a linear degree-1 curve between two objects.*
- `rebuild_curve_to_degree3(curve, spans)` — *Rebuild a curve to be degree 3 with a given number of spans.*

### 📄 `readWriteCtrlSizeData/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `readWriteCtrlSizeData/run.py`
**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `savingData()`
- `loadingData()`

### 📄 `readWriteCtrlSizeData/writeCtrlData.py`
**คำอธิบาย / รายละเอียด:** // date : 10 aug 2018

**ฟังก์ชันหลัก (Functions - 15 รายการ):**
- `whereAreMe(path)`
- `validCtrlData()`
- `filePath(filename)`
- `validateCurve(crv)` — *Checks whether the transform we are working with is actually a curve and returns it's shapes*
- `getShape(crv)` — *Returns a dictionary containing all the necessery information for rebuilding the passed in crv.*
- `getKnots(crvShape)`
- `saveToLib(crv, shapeName)` — *Saves the shape data to a shape file in the SHAPE_LIBRARY_PATH directory*
- `saveData(path, data)` — *Saves a dictionary as JSON in a file*
- `validatePath(path)` — *Checks if the file already exists and provides a dialog to overwrite or not*
- `loadFromLib(shape)` — *Loads the shape data from the shape file in the SHAPE_LIBRARY_PATH directory*
- `loadData(path)` — *Loads raw JSON data from a file and returns it as a dict*
- `setShape(crv, crvShapeList)` — *Creates a new shape on the crv transform, by using the properties in the crvShapeDict. *
- *...และอีก 3 ฟังก์ชันภายในโมดูล*

---

<a id="skeleton_joints"></a>
## 7. Skeleton & Joint Systems (ระบบโครงสร้างกระดูกและข้อต่อ)
*เครื่องมือสร้างและจัดการ Joint บน Curve, จัดการ Bind Joints, คำนวณความยาว และการแทนที่ Template Joints*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `4` ไฟล์

### 📄 `skeleton/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skeleton/createJointAlongCurve.py`
**คลาส (Classes):**
- `class buildUI`
  - **Methods:** `show`, `_core_along_curve`, `createJntAlongCurve`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `run()`

### 📄 `skeleton/jointTools.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.skeleton import jointTools as jtt

**คลาส (Classes):**
- `class utilLogger`

**ฟังก์ชันหลัก (Functions - 11 รายการ):**
- `change_replace_endJnt(search, replace)`
- `select_body_jnt()`
- `disable_compensate()`
- `select_tip_joint(selected_joints, search, replace)`
- `_replace_change_gray(selectedLst)`
- `change_endJnt_gray()`
- `rename_tip_jnt(root_joint, search, replace)`
- `mirror_joint_chain(root_joint, axis)`
- `list_tip_joints(root_joint)`
- `list_joint_hierarchy(root_joint)`
- `replaceTmpJnt(nameSpace, tmpJnt, side, extName)` — *Replace template joint with new ext name*

### 📄 `skeleton/replaceTmpJnt.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.skeleton import replaceTmpJnt as rtj

**คลาส (Classes):**
- `class utilLogger`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `replaceTmpJnt(nameSpace, tmpJnt, side, extName)` — *Replace template joint with new ext name*

---

<a id="skin_deformers"></a>
## 8. Skinning, Deformers & BlendShapes (ระบบการถ่ายโอนน้ำหนัก Skin และ Deformers)
*เครื่องมือบริหารจัดการ Skin Weights (SkinWrangler, nsSkinClusterIO, brSmoothWeights, Curve skinning) และ BlendShape Inverters*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `33` ไฟล์

### 📄 `blendShape/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape/blendshapeTools.py`
**คำอธิบาย / รายละเอียด:** #... direct run

**ฟังก์ชันหลัก (Functions - 17 รายการ):**
- `extractBlendShapeTargetGeo(blendShape)`
- `createBshToPly(bsh_dict, side)` — *Duplicate base geometry for each facial in dict in the same collum*
- `_duplicateForBsh(bsh_dict, side, nameSpace)` — *Duplicate curve prepare for blendshape*
- `createBshToCurve(bsh_dict, posiBlock)`
- `_singleConnectBsh(singleBsh_dict)` — *connect blendshape from pair dictionary (just copy paste from pair connect blendshape )*
- `_pairConnectBsh(pairBsh_dict)` — *connect blendshape from pair (LFT,RGT) dictionary*
- `create(baseGeo, targetGeo, origin, deformOrder, ...)` — *Create a blendShape deformer for the specified base geometry(reference from glmaster).*
- `addTarget(blendShape, target, base, targetIndex, ...)` — *Add a new target to the specified blendShape*
- `nextAvailableTargetIndex(blendShape)` — *Get the next available blendShape target index*
- `getTargetList(blendShape)` — *Return the target list for the input blendShape*
- `getTargetIndex(blendShape, target)` — *Get the target index of the specified blendShape and target name*
- `addTatgetInbetween(blendShape, targetGeo, targetName, base, ...)` — *Add a new target inbetween to the specified blendShape target*
- *...และอีก 5 ฟังก์ชันภายในโมดูล*

### 📄 `blendShape/cvshapeinverter-master/plug-ins/cvshapeinverter_plugin.py`
**คลาส (Classes):**
- `class cvShapeInverter`
  - **Methods:** `deform`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `creator()`
- `initialize()`
- `initializePlugin(mobject)`
- `uninitializePlugin(mobject)`

### 📄 `blendShape/generate_blendShape.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.blendShape import generate_blendShape as gbs

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `duplicateForBlendshape(blendshapeAtEnd, blendshape_dict, multiplier, blendshapeName)`

### 📄 `blendShape/na_bsCorrectiveSculpt.py`
**คำอธิบาย / รายละเอียด:** Corrective Blendshape Model Sculpt Helper

**ฟังก์ชันหลัก (Functions - 6 รายการ):**
- `gatherInfo()`
- `cbsStart()`
- `cbsTrans()`
- `clearTweaks()`
- `cbsHookup()`
- `cbsMirror(blend, base)`

### 📄 `blendShape/na_bsCorrectiveSculpt/na_bsCorrectiveSculpt.py`
**คำอธิบาย / รายละเอียด:** Corrective Blendshape Model Sculpt Helper

**ฟังก์ชันหลัก (Functions - 6 รายการ):**
- `gatherInfo()`
- `cbsStart()`
- `cbsTrans()`
- `clearTweaks()`
- `cbsHookup()`
- `cbsMirror(blend, base)`

### 📄 `corrective/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `corrective/correctCMuscleJoint.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `createHelperJoint(parentA, parentB, side, axis)` — *return name of help joint*

### 📄 `corrective/correctShoulderJoint.py`
**คำอธิบาย / รายละเอียด:** #... corrective joint for shoulder

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `correctShoulderJoint(tmpJnt, side, priorJnt, belowJnt, ...)`

### 📄 `corrective/correctiveJointChain.py`
**คำอธิบาย / รายละเอียด:** # direct run

**คลาส (Classes):**
- `class correctiveJntLog`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `correctiveJointChain(skinJntA, skinJntB, correctiveJntA, correctiveJntB, ...)`

### 📄 `corrective/valuePreservation.py`
**คำอธิบาย / รายละเอียด:** # Direct run

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `valuePreservation(middleJnt, side, auxPosiWeight, baseName, ...)`

### 📄 `skin/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skin/autoReadWriteSkin.py`
**คำอธิบาย / รายละเอียด:** utils.py [part 3/4] mod from Andrew Glisinski Returns a list of requested object strings

**ฟังก์ชันหลัก (Functions - 10 รายการ):**
- `selectBJntFromSameMesh()` — *select bind joint from the mesh that was skinCluster before *
- `geoInfo(vtx, geo, shape, skinC)`
- `getVertexWeights(vertexList, skinCluster, thresholdValue)`
- `writeJsonFile(dataWrite, filePath, step)`
- `getSkinJntLst()`
- `_processPath()`
- `exportWeightData()`
- `importWeightData()`
- `_jsonGetFileName()`
- `browseWeight()`

### 📄 `skin/brSmoothWeights/userSetup.py`
**คำอธิบาย / รายละเอียด:** ---------------------------------------------------------------------- userSetup.mel  Automatically add the menu items for the smooth weights tool upon Maya startup.  ----------------------------------------------------------------------

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `addMenuItems()`

### 📄 `skin/copyPasteSkinUI.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.skin import copyPasteSkinUI as cpu

**คลาส (Classes):**
- `class BuildUI` — *Class to build a simple UI for copying and pasting skin weights in Maya.*
  - **Methods:** `show`, `click_copySkin`, `click_pasteSkinJ`

### 📄 `skin/copySkinFromRef.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.skin import copySkinFromRef as cpr

**คลาส (Classes):**
- `class CopySkinUI` — *Inherited from MlUi*
  - **Methods:** `copySkin`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `runUi()` — *User interface for copy skin*

### 📄 `skin/copySkinTool.py`
**คำอธิบาย / รายละเอียด:** select skinned mesh, then select mesh to transfer to, and run

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `objectSel()`
- `assignSkc(skc, target)`
- `ncCopySkinWeights(source, target)`

### 📄 `skin/copySkinWeight.py`
**คำอธิบาย / รายละเอียด:** reload module

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `copyWeight()`
- `copyWeightArg(source, destination)`

### 📄 `skin/curve_skinWeight.py`
**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `smooth_curve_weights(curve_name, iterations, pin_ends)` — *Smooth skin weights for a NURBS curve by averaging neighbors (1D Smoothing).*
- `create_proxy_from_curve(curve_name, width)` — *Create a polyPlane proxy aligned to the curve for easier weight painting.*
- `transfer_mesh_to_curve(source_mesh, target_curve)` — *Copy skin weights from Proxy Mesh to Target Curve.*

### 📄 `skin/exportImportMeshGeneralData.py`
**คลาส (Classes):**
- `class buildUI`
  - **Methods:** `show`, `click_writeRigData`, `click_importSkinJntList`, `click_writeVTXselected`

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `run()`

### 📄 `skin/ml_copySkin.py`
**คำอธิบาย / รายละเอียด:** -= ml_copySkin.py =- __   by Morgan Loomis ____ ___  / /  http://morganloomis.com / __ `__ \/ /  Revision 2 / / / / / / /  2018-02-17 /_/ /_/ /_/_/  _________ /_________/  ______________ - -/__ License __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - -  Copyright 2018 Morgan Loomis  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in

**คลาส (Classes):**
- `class CopySkinUI` — *Inherited from MlUi*
  - **Methods:** `copySkin`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `ui()` — *User interface for copy skin*
- `copySkinInfluences(source, dest)`
- `copySkinComponents(source, destinationVerts)`
- `copySkinCluster(source, destination)`

### 📄 `skin/ml_utilities.py`
**คำอธิบาย / รายละเอียด:** -= ml_utilities.py =- __   by Morgan Loomis ____ ___  / /  http://morganloomis.com / __ `__ \/ /  Revision 33 / / / / / / /  2018-07-18 /_/ /_/ /_/_/  _________ /_________/  ______________ - -/__ License __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - -  Copyright 2018 Morgan Loomis  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in

**คลาส (Classes):**
- `class Dragger`
  - **Methods:** `press`, `drag`, `release`, `drawString`, `dragLeft`, `dragMiddle`, `dragControlLeft`, `dragControlMiddle`...
- `class IsolateViews` — *Isolates selection with nothing selected for all viewports*
  - **Methods:** `isolate`
- `class KeySelection` — *        *
  - **Methods:** `curves`, `channels`, `nodes`, `args`, `time`, `times`, `values`, `initialized`...
- `class MlUi` — *Window template for consistency*
  - **Methods:** `buildWindow`, `finish`, `createMenu`, `about`, `buttonWithPopup`, `shelfMenuItem`, `hotkeyMenuItem`, `selectionField`...
- `class SkipUndo` — *Skips adding the encapsulated commands to the undo queue, so that you*
- `class UndoChunk` — *In versions of maya before 2011, python doesn't always undo properly, so in*
- `class Vector`
  - **Methods:** `_isCompatible`, `magnitude`, `normalize`, `normalized`, `dot`, `cross`

**ฟังก์ชันหลัก (Functions - 31 รายการ):**
- `_showHelpCommand(url)` — *This just returns the maya command for launching a web page, since that gets called a few times*
- `main()` — *This just launches the online help and serves as a placeholder for the default function for this script.*
- `upToDateCheck(revision, prompt)` — *This is a check that can be run by scripts that import ml_utilities to make sure they*
- `castToTime(time)` — *Maya's keyframe commands are finnicky about how lists of times or indicies are formatted.*
- `constrain(source, destination, translate, rotate, ...)` — *Constrain two objects, even if they have some locked attributes.*
- `createAnimLayer(nodes, name, namePrefix, override)` — *Create an animation layer, add nodes, and select it.*
- `selectAnimLayer(animLayer)` — *Select only the specified animation layer*
- `getSelectedAnimLayers()` — *Return the names of the layers which are selected*
- `createHotkey(command, name, description, python)` — *Open up the hotkey editor to create a hotkey from the specified command*
- `createShelfButton(command, label, name, description, ...)` — *Create a shelf button for the command on the current shelf*
- `deselectChannels()` — *Deselect selected channels in the channelBox*
- `formLayoutGrid(form, controls, offset)` — *Controls should be a list of lists, and this will arrange them in a grid*
- *...และอีก 19 ฟังก์ชันภายในโมดูล*

### 📄 `skin/nsSkinClusterIO/nsSkinClusterIO.py`
**คำอธิบาย / รายละเอียด:** ... locate --> 22.11.Nov.17.Thu.15_nsSkinClusterIO ... repo --> rigging.skin.nsSkinClusterIO

**คลาส (Classes):**
- `class DataIO`
  - **Methods:** `get_legendArrayFromData`, `get_dataItem`, `set_dataItems`
- `class SkinClusterIO`
  - **Methods:** `get_mesh_components_from_tag_expression`, `get_data`, `set_data`, `save`, `load`, `compress_weightData`

### 📄 `skin/nsSkinClusterIO/nsSkinClusterIO_reFunc.py`
**คำอธิบาย / รายละเอียด:** # direct run

**คลาส (Classes):**
- `class SkinIOLogger`
- `class SkinClusterIO`
  - **Methods:** `get_mesh_components_from_tag_expression`, `get_data`, `set_data`, `compress_weightData`
- `class DataIO`
  - **Methods:** `get_legendArrayFromData`, `get_dataItem`, `set_dataItems`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `_processPath()`
- `saveSkin()`
- `loadSkin()`

### 📄 `skin/roundSkinWeight.py`
**คำอธิบาย / รายละเอียด:** from function.framework.reloadWrapper import reloadWrapper as reload

**คลาส (Classes):**
- `class roundSkinLogger`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `has_skin_cluster(mesh)`
- `roundSkinWeight(digit, selection)`

### 📄 `skin/saveLoadCurveSkinweight.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.skin import saveLoadCurveSkinweight as slk

**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `save_curve_skinweights(curve_name, json_path)`
- `run_save_curve_skinweights()`
- `load_curve_skinweights(curve_name, json_path)`
- `load_curve_skinweights_V2(curve_name, json_path)`
- `run_load_curve_skinweights()`

### 📄 `skin/skinUtil.py`
**คำอธิบาย / รายละเอียด:** # skin utility

**ฟังก์ชันหลัก (Functions - 10 รายการ):**
- `getJntData()`
- `selectBindJnt(naming)`
- `renameSkinCluster()`
- `_renameAllBindpose(ext)`
- `_listJntSkinCluster()` — *get the skin cluster and the joint*
- `writeRigData()`
- `connectProxyJnt(master, slave)`
- `copyWeight()`
- `mulWeight(source)`
- `creJntAtVertex()`

### 📄 `skin/skinWrangler/Qtpy/Qt.py`
**คำอธิบาย / รายละเอียด:** Map all bindings to PySide2

**ฟังก์ชันหลัก (Functions - 11 รายการ):**
- `convert(lines)` — *Convert compiled .ui file from PySide2 to Qt.py*
- `_remap(object, name, value, safe)` — *Prevent accidental assignment of existing members*
- `_add(object, name, value)` — *Append to self, accessible via Qt.QtCompat*
- `_pyqt5()`
- `_pyqt4()`
- `_pyside2()`
- `_pyside()`
- `_log(text, verbose)`
- `cli(args)` — *Qt.py command-line interface*
- `init()` — *Try loading each binding in turn*
- `_maintain_backwards_compatibility(binding)` — *Add members found in prior versions up till the next major release*

### 📄 `skin/skinWrangler/Qtpy/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skin/skinWrangler/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skin/skinWrangler/skinWrangler_2023.py`
**คำอธิบาย / รายละเอียด:** skinWrangler

**คลาส (Classes):**
- `class skinWrangler`
  - **Methods:** `closeEvent`, `closeExistingWindow`, `averageWeights`, `findRelatedSkinCluster`, `removeAnnotations`, `annotateNodes`, `getSelected`, `getAvgVertWeights`...

**ฟังก์ชันหลัก (Functions - 6 รายการ):**
- `show()`
- `load_ui_file(uiFile)`
- `loadUiType(uiFile)`
- `loadUiType(uiFile)` — *Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first*
- `loadUiType(uiFile)`
- `getMayaWindow()`

### 📄 `skin/skinio.py`
**คำอธิบาย / รายละเอียด:** # direct run

**คลาส (Classes):**
- `class SkinCluster`
  - **Methods:** `createAndImport`, `getSkinCluster`, `export`, `removeNamespaceFromString`, `gatherData`, `gatherInfluenceWeights`, `gatherBlendWeights`, `exportSkin`...
- `class WeightRemapDialog`
  - **Methods:** `setInfluences`, `setInfluenceMapping`
- `class SkinIODialog`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `show()`
- `getMayaWindow()`
- `getShape(node, intermediate)` — *get the shape from specified node.*

### 📄 `skin/skinio2023.py`
**คำอธิบาย / รายละเอียด:** # direct run

**คลาส (Classes):**
- `class SkinCluster`
  - **Methods:** `createAndImport`, `getSkinCluster`, `export`, `removeNamespaceFromString`, `gatherData`, `gatherInfluenceWeights`, `gatherBlendWeights`, `exportSkin`...
- `class WeightRemapDialog`
  - **Methods:** `setInfluences`, `setInfluenceMapping`
- `class SkinIODialog`

**ฟังก์ชันหลัก (Functions - 3 รายการ):**
- `show()`
- `getMayaWindow()`
- `getShape(node, intermediate)` — *get the shape from specified node.*

---

<a id="project_specific"></a>
## 9. Project-Specific Rigging Modules (สคริปต์เฉพาะโปรเจกต์)
*สคริปต์เฉพาะสำหรับโปรเจกต์ เช่น Project_Regulus_Sample และ Project_Sample (Local/World, Texture switch, Facial link)*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `9` ไฟล์

### 📄 `Project_Sample/01_make root local or world.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `Project_Regulus_Sample/01_createSwitchTextureOffset_P.py`
**คำอธิบาย / รายละเอียด:** PORTABLE - createSwtichTextureOffset - ctrl must not have "mouth" Attr, if already had it will cancel place2dTexture is node that on the left side of Mouth texture

**ฟังก์ชันหลัก (Functions - 5 รายการ):**
- `createSwtichTextureOffset(ctrl, place2dTexture, attrName, addEnumList)`
- `addEnum(ctrl, name, enum)`
- `connectTo(attrA, objB, attrB)`
- `setAttr(obj, attr, val)`
- `connect(objA, attrA, objB, attrB)`

### 📄 `Project_Regulus_Sample/02_make naming same with The Dode.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `Project_Regulus_Sample/03_linkFacialToJnt.py`
**คำอธิบาย / รายละเอียด:** this will link facial Switch ctrl to facial Offset jnt on the floor you need to link texture 2D first

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `linkFacialToJnt(ctrl, attr, facialJnt)`

### 📄 `Project_Regulus_Sample/04_local world manual.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `check_obj_exists(obj_name)`

### 📄 `Project_Regulus_Sample/05_create_attr.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `Project_Regulus_Sample/06_change color.py`
**คำอธิบาย / รายละเอียด:** ... change color

### 📄 `Project_Regulus_Sample/07_not using namesapce.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `Project_Regulus_Sample/Project_Regulus_Sample_name_data.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

---

<a id="tools_features_root"></a>
## 10. Features, Tools & Utility Scripts (เครื่องมือเสริมและสคริปต์จัดการทั่วไป)
*ชุดเครื่องมือ Utilities ทั่วไป, ทำความสะอาดซีน, สร้าง Shader, Local/World switches, Snap tools และ Legacy scripts*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `17` ไฟล์

### 📄 `_archive/eh_fkIkTwistGenRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `fkIkTwistGenRig(nameSpace, charScale, parentTo, side, ...)`

### 📄 `bd_scripts/rear_paw.py`
**คำอธิบาย / รายละเอียด:** SPDX-FileCopyrightText: 2017-2022 Blender Foundation  SPDX-License-Identifier: GPL-2.0-or-later

**คลาส (Classes):**
- `class Rig` — *Rear paw rig with special IK automation.*
  - **Methods:** `get_middle_ik_controls`, `get_ik_fk_position_chains`, `get_extra_ik_controls`, `get_ik_pole_parents`, `parent_heel_control_bone`, `get_ik2_input_bone`, `make_ik2_mch_stretch`, `make_ik2_mch_target_bone`...

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `create_sample(obj)`

### 📄 `feature/CLOTH_SWAP.py`
**คำอธิบาย / รายละเอียด:** Untimate CLOTH SWAP NAME GIVING

### 📄 `feature/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature/autoSkirtRig.py`
**คำอธิบาย / รายละเอียด:** from function.rigging.feature import autoSkirtRig

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `autoSkirt(name, jointName, attrPlace)`

### 📄 `feature/baseFingerSpread.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `baseFingerSpread(nameSpace, tmpJnt, stick, fingerGrpNam, ...)`

### 📄 `feature/localWorld.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `localWorld(fromSel, giveCtrl, ori, worldCtrl)`

### 📄 `feature/localWorldExt.py`
**คำอธิบาย / รายละเอียด:** ... Update version for local/world not make it cycle with curl rig

### 📄 `feature/propRig.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `propRig(jnt)`

### 📄 `legacy/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `legacy/kneeLockCmds.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `runLock(nameUPR, namePov, nameLWR, stretchNode, ...)`

### 📄 `legacy/resetRotationOrder.py`
**คำอธิบาย / รายละเอียด:** reset the rotation order

### 📄 `legacy/select_addJoint.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `tools/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `tools/colorTool.py`
**คำอธิบาย / รายละเอียด:** >>>>>   Untimate Color Menu   <<<<< Date: 27.May.2020 Author: UI, main function		:	THEDODE

**คลาส (Classes):**
- `class Function`
  - **Methods:** `_toRed`, `_toGreen`, `_toBlue`, `_toYellow`, `_toWhite`
- `class Ui`
  - **Methods:** `createGUI`

### 📄 `tools/dTool.py`
**คำอธิบาย / รายละเอียด:** Dode Rig Tool name as dc import dTool as dc reload dc

**ฟังก์ชันหลัก (Functions - 25 รายการ):**
- `parCon(src, tgt, mo, w)`
- `oriCon(src, tgt, mo, w)`
- `pointCon(src, tgt, mo, w)`
- `sclCon(src, tgt, mo, w)`
- `allMat(tgt, src)`
- `posMat(tgt, src)`
- `rotMat(tgt, src)`
- `cons(mo, type)`
- `chainCtrl()`
- `quickCtrl()`
- `createCtrl(jnt, typ, c, gmbl)`
- `ctrlColor(name, color)`
- *...และอีก 13 ฟังก์ชันภายในโมดูล*

### 📄 `tools/proc.py`
**คำอธิบาย / รายละเอียด:** Proc

**ฟังก์ชันหลัก (Functions - 16 รายการ):**
- `clearVis(suffix, hide)`
- `QuickProc(giveName, side, switchCtrl)`
- `renameShd(overideName)`
- `piston(masterA, masterB)`
- `resetAllController(reference)`
- `boneCount()`
- `twistNrbRig(nameSpace, stJnt, enJnt, charScale)`
- `twistRig(nameSpace, stJnt, enJnt, charScale)`
- `setupShowArmor(sex, digit, giveName)`
- `setupSelectedArmor()`
- `exportSelArmor()`
- `exportSelOutfit()`
- *...และอีก 4 ฟังก์ชันภายในโมดูล*

---

<a id="root_scripts"></a>
## 11. Root Helper & One-Off Scripts (สคริปต์เดี่ยวระดับ Root)
*สคริปต์เครื่องมือเสริมและฟังก์ชันเดี่ยวที่อยู่ใน Root ของ `function/rigging/`*

**จำนวนไฟล์ทั้งหมดในหมวดนี้:** `108` ไฟล์

### 📄 `AutoStretchIK.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `autoStrechIK()`

### 📄 `BoneCount.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `LOCAL_WORLD_Manual.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `check_obj_exists(obj_name)`

### 📄 `LOCAL_WORLD_Orient.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `localWorldOrient(worldCtrl)`

### 📄 `LOCAL_WORLD_POV.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `RESET.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `resetAllController(reference)`

### 📄 `Snap SetUp.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `Snap()`

### 📄 `SnapCreate.V2.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `Snap()`

### 📄 `SnapCreateMessage.V2.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `UKDP_DFKC.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/__init__.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bipedAutoRig_baseFinger.py`
**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

### 📄 `autoRig/bipedAutoRig_default.py`
**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

### 📄 `autoRig/bipedAutoRig_fourHand.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/bipedAutoRig_fourLeg.py`
**คำอธิบาย / รายละเอียด:** Standard autorig version 1.05

### 📄 `autoRig/bipedAutoRig_hi.py`
**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

### 📄 `autoRig/bipedAutoRig_lite.py`
**คำอธิบาย / รายละเอียด:** Standard autorig

### 📄 `autoRig/biped_autoRig_010_default.py`
**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # Autorig with following feature # # # # # # # # # # # # # # # stretchy IK auto upper arm/leg twist Fk/Ik switch kneelock ribbon limb (option) head clavicle local world finger curl arm space snaping foot roll behavior

### 📄 `autoRig/quarupedAutoRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/quaruped_autoRig_110_default.py`
**คำอธิบาย / รายละเอียด:** ...reference\templateJoint_quaruped_110_default.ma"

### 📄 `autoRig/taiBipedAutoRigMatrix.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig/util.py`
**คำอธิบาย / รายละเอียด:** ... THIS MODULE IS WILL REMOVE ... ALL FUNTION IS MOVE TO RIGGING.UTIL.CLEANUP INSTEAD !!!!!

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `cleanup()`
- `_deleteTemplate()`

### 📄 `autoRig\addRig\bRivetReFunction.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\addRig\tentacle_fkIkDeformedRig_GPT.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\bodyRig\armRigMatrix.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\bodyRig\armTwistRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\bodyRig\bipedLegTwistRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\bodyRig\fingerCurlMainRig\fingerCurl_dict.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\bodyRig\ribbonBreakChain\ribbonRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\creatureRig\base.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\backLegRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\bipedLegRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\bipedfootRoll.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\hero\backLegRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\hero\bipedfootRoll.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\hero\localWorldRot.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\hero\spineFkRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\localWorldRot.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\plantigradeLegRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\library\spineFkRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\module\clothSwapWithClick.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\module\fingerCurlRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\module\fingerLocalCurlRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\module\fingerRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\module\ikfkSnap.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\object\createCtrlAtSelected.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\object\createCtrlAtSelectedJoint.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\object\createFkctrl.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\object\createLocalWorldAtSelected.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\simpleQuarupedAutoRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `autoRig\snake_AutoRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `bRivet.py`
**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `bRivet()`
- `bRivet_Build(input, ob, edgeMax, shape, ...)`

### 📄 `blendShape\blendshapeConnectGeo.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\blendshapeTools_010_duplicate_execute.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\blendshapeTools_020_connect_execute.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\blendshapeTools_030_connect_eyelid.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\blendshapeTools_connect_execute_.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\blendshapeTools_duplicate_execute_.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\combineAlot.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\connectGeo\030_connect value from controller to blendshape.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\connectGeo\035_connect value from controller to blendshape_eyebrowRGT.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\connectGeo\036_03_create controller for connect to blendshape_eyeLid_v002.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\connectGeo\037_create controller for connect to blendshape_mouth_v002.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\connectGeo\038_connect value from controller to blendshape_forPly_eyebrowLFT.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\connectGeo\039_connect value from controller to blendshape_forPly_eyelid.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\cvshapeinverter-master\scripts\cvshapeinverter.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\na_bsCorrectiveSculptUI.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `blendShape\na_bsCorrectiveSculpt\na_bsCorrectiveSculptUI.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `copyPivot.py`
**คำอธิบาย / รายละเอียด:** all credits to Serge Scherbakov This script allows you to copy object pivot translation and rotation from one object to another one. How to use: - copy code to the script editor "Python tab" - select target object - select source object - execute script Works on multiple selection. Align all object pivots with last selected.

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `copyPivot()`

### 📄 `corrective\correctHingesJoint.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `creFollicleAtSel.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `de_boor\hh_blendshape_sample.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `example_google.py`
**คำอธิบาย / รายละเอียด:** Example Google style docstrings.

**คลาส (Classes):**
- `class ExampleError` — *Exceptions are documented in the same way as classes.*
- `class ExampleClass` — *The summary line for a class docstring should fit on one line.*
  - **Methods:** `readonly_property`, `readwrite_property`, `readwrite_property`, `example_method`, `_private`, `_private_without_docstring`

**ฟังก์ชันหลัก (Functions - 4 รายการ):**
- `function_with_types_in_docstring(param1, param2)` — *Example function with types documented in the docstring.*
- `function_with_pep484_type_annotations(param1, param2)` — *Example function with PEP 484 type annotations.*
- `module_level_function(param1, param2)` — *This is an example of a module level function.*
- `example_generator(n)` — *Generators have a ``Yields`` section instead of a ``Returns`` section.*

### 📄 `faceSwitch.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\fingerOffsetRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\jointAttatchToCurve.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\kneeLock.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\localWorldPOV.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\ribbonRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\ribbon_jh.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\textureSwitch.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `feature\twist.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `jh_ribbon.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `jo_varFk.py`
**คำอธิบาย / รายละเอียด:** Variable FK Autorigger ######## Version 1.00 Version: 15.02.2014 Author: Julian "fleity" Oberbeck Download at and submit bugs to: http://www.creativecrash.com/maya/downloads/scripts-plugins/character/c/variable-fk-rigger  Variable FK concept based on the video of Jeff Brodsky (https://vimeo.com/72424469). thanks at adeptus from cgsociety.com/forum for a tip on how to orient joint chains  How To Use ##############  put varFk.py into scripts directory, varFk.jpg into documents\maya\<maya version>\prefs\icons  run from python command line / script editor: import jo_varFk

**ฟังก์ชันหลัก (Functions - 11 รายการ):**
- `UI()`
- `insertFirstSelected()`
- `buildVarFkFromUI()`
- `create_jointChain(IdName, inputCurve, orientation)`
- `addPositionOnSurfaceAttr(objects, nurbsSurface)`
- `create_guideSurface(IdName, listOfJnts)`
- `create_VarFkCtrls(IdName, guideSurface, numberOfCtrls)`
- `createBufGrp(sel)`
- `create_follicle(oNurbs, uPos, vPos)`
- `create_ctrlOutput(ctrl, jnt)`
- `buildVarFk(IdName, inputCurve, numberOfCtrls)`

### 📄 `legacy\deleteTransKeys.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `legacy\faceSwitch.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `legacy\fingerOffsetRig.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `legacy\kneeLock.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `legacy\renameJoint.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `legacy\rename_node.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `listTipJnt.py`
**คำอธิบาย / รายละเอียด:** # # # # # # # # # # # # # # # ...  list end joint # # # # # # # # # # # # # # #

### 📄 `mirror_curve_cvs.py`
**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `mirror_curve_cvs(curve, right_to_left)` — *Mirrors CVs on one side of a curve to the opposite side across the center (X-axis).*

### 📄 `openMaya_port.py`
**คำอธิบาย / รายละเอียด:** Check and open Maya Command Port safely

### 📄 `skinWeight.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skin\pk_skinTools.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skin\skinWeight.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `skin\skinWrangler\skinWrangler.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `snapPivot.py`
**คำอธิบาย / รายละเอียด:** Align pivots by Serge Scherbakov.

**ฟังก์ชันหลัก (Functions - 1 รายการ):**
- `copyPivot()`

### 📄 `switchLocalIK.py`
**คำอธิบาย / รายละเอียด:** Untimate Switch local IK auto create

### 📄 `templateUi.py`
**คำอธิบาย / รายละเอียด:** from function.rigging import templateUi

**คลาส (Classes):**
- `class templateUi` — *docstring for templateUi*
  - **Methods:** `buildWindow`, `selectionField`, `_populateSelectionField`, `finish`

### 📄 `textureSwitch.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `tf_smoothSkinWeight.py`
**คำอธิบาย / รายละเอียด:** ----------------------------------------------------------------------------------- AUTHOR:     Tom Ferstl t.ferstl@gmx.net  INSTALL:    copy script to your maya scripts directory (i.e. C:\Users\xx\Documents\maya\2011\scripts )  USAGE:      select a skinned mesh and execute the following python commands (without # and whitespace): import tf_smoothSkinWeight tf_smoothSkinWeight.paint() -----------------------------------------------------------------------------------

**คลาส (Classes):**
- `class smoothPaintClass`
  - **Methods:** `setWeight`

**ฟังก์ชันหลัก (Functions - 2 รายการ):**
- `initPaint()`
- `paint()`

### 📄 `tools\cleantool.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `tools\createShdFromSel.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `tools\rigtool_dode.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `tororo2023.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*

### 📄 `util\copySkinWeight_001.py`
*สคริปต์สำหรับรันคำสั่งโดยตรง (Direct execution script)*
