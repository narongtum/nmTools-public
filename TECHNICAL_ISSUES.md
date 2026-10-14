# Technical Issues & Rigging Case Studies (Knowledge Base)

This document is the centralized knowledge base and troubleshooting reference for technical anomalies, mathematical flaws in Maya solvers/nodes, and production-tested solutions in the **nmTools** pipeline.

---

## 📑 Table of Contents
1. [Issue #001: Maya `ikSpringSolver` World Rotation Planar Twist Anomaly & Hotfix](#issue-001-maya-ikspringsolver-world-rotation-planar-twist-anomaly--hotfix)
2. [Issue #002: Joint Orientation & IK Popping Prevention (`rigTools.jointAt` + `freeze(r=True)`)](#issue-002-joint-orientation--ik-popping-prevention-rigtoolsjointat--freezertrue)
3. [Issue #003: Global Scaling Double Translation Distortion in Matrix Offset Systems](#issue-003-global-scaling-double-translation-distortion-in-matrix-offset-systems)
4. [Issue #004: Maya Component Selection Order Sorting Bug (`filterExpand` vs `orderedSelection`)](#issue-004-maya-component-selection-order-sorting-bug-filterexpand-vs-orderedselection)
5. [Issue #005: Duplicate DAG Path String Evaluation in Maya Commands](#issue-005-duplicate-dag-path-string-evaluation-in-maya-commands)

---

## Issue #001: Maya `ikSpringSolver` World Rotation Planar Twist Anomaly & Hotfix

### 1. Symptom & Context
On 4-joint quadruped hind legs (`upLeg_ikJnt` $\rightarrow$ `midLeg_ikJnt` $\rightarrow$ `lowLeg_ikJnt` $\rightarrow$ `ankle_ikJnt`) driven by Maya's native `ikSpringSolver`, rotating the character/root in World Space (`placement_ctrl.rotateY` or `master_ctrl.rotateY` e.g. $90^\circ$) causes the intermediate joints (`midLeg_ikJnt` and `lowLeg_ikJnt`) to twist axially around the bone shaft, flipping the knee and hock sideways unnaturally.

### 2. Root Cause & Mathematical Breakdown
* **Static Reference Vector Baking (`springRestPoleVector`)**: When `ikSpringSolver` initializes, it bakes an internal reference vector `springRestPoleVector` in local coordinate space. Unlike 2-bone `ikRPsolver` (which calculates the bending plane dynamically from 3 world points: $(\vec{v}_2 - \vec{v}_1) \times (\vec{v}_3 - \vec{v}_1)$), `ikSpringSolver` measures the angular difference between the active pole vector and its static rest vector.
* **Coaxial Alignment on $R_Y$**: The quadruped hind leg stretches vertically along the Y-axis. Rotating $R_Y$ (Yaw) is coaxial (parallel) to the primary limb vector. The solver misinterprets the world rotation of the pole vector as an intentional **axial twist command** from the animator, causing full axial bone twisting.
* **Why $R_X$ and $R_Z$ are unaffected**: $R_X$ (Pitch) and $R_Z$ (Roll) are perpendicular to the vertical limb axis, swinging the entire limb through space as a rigid arc without changing the pole vector's angular phase around the bone shaft.

### 3. Permanent Pipeline Architecture (`eh_quadrupedLegRig_DoubleIK.py`)
All new 4-joint quadruped hind legs must strictly use the **Pure Double IK (V3)** architecture:
1. **Upper Main Chain (Hip $\rightarrow$ Knee $\rightarrow$ Hock)**: Standard 2-bone `ikRPsolver` (`upperIk_ikh`).
2. **Lower Main Chain (Hock $\rightarrow$ Ankle)**: Single-Chain `ikSCsolver` (`ankleIk_ikh`).
3. **Guide Kinematic Chain**: 2-bone driver chain with `ikRPsolver`.
* Eliminates `ikSpringSolver.mll` plugin dependency and resolves world rotation flipping completely.

### 4. Production In-Scene Hotfix (Twist Compensation Network)
For existing production rigs that cannot replace `ikSpringSolver`, route total world yaw rotation into `ikSpring_handle.twist` via `plusMinusAverage`:

```python
import maya.cmds as mc

def fix_quadruped_spring_ik_twist():
    """
    Hotfix for Maya ikSpringSolver planar twist anomaly during world/placement rotation.
    Connects master/placement rotateY and controller twist attributes into ikSpring_handle.twist
    via plusMinusAverage nodes.
    """
    legs = [
        {'side': 'LFT', 'handle': 'lowLegBackLFT_ikSpring_handle', 'ctrl': 'anklebackLegIKLFT_ctrl'},
        {'side': 'RGT', 'handle': 'lowLegBackRGT_ikSpring_handle', 'ctrl': 'anklebackLegIKRGT_ctrl'}
    ]
    
    placement_ctrl = 'placement_ctrl'
    master_ctrl = 'master_ctrl'
    
    for leg in legs:
        side, handle, ctrl = leg['side'], leg['handle'], leg['ctrl']
        if not mc.objExists(handle):
            continue
            
        # 1. Add animator manual twist channel on ankle IK controller
        if mc.objExists(ctrl) and not mc.attributeQuery('twist', node=ctrl, exists=True):
            mc.addAttr(ctrl, ln='twist', at='float', k=True, dv=0.0)
            
        # 2. Create plusMinusAverage node for twist sum
        pma = mc.createNode('plusMinusAverage', name=f"backLeg{side}_twist_pma") if not mc.objExists(f"backLeg{side}_twist_pma") else f"backLeg{side}_twist_pma"
            
        # 3. Route placement rotateY, master rotateY, and manual twist
        if mc.objExists(placement_ctrl):
            mc.connectAttr(f"{placement_ctrl}.rotateY", f"{pma}.input1D[0]", force=True)
        if mc.objExists(master_ctrl):
            mc.connectAttr(f"{master_ctrl}.rotateY", f"{pma}.input1D[1]", force=True)
        if mc.objExists(ctrl):
            mc.connectAttr(f"{ctrl}.twist", f"{pma}.input1D[2]", force=True)
            
        # 4. Drive ikSpring handle twist
        mc.connectAttr(f"{pma}.output1D", f"{handle}.twist", force=True)
        print(f"Twist Compensation connected on {handle}")

fix_quadruped_spring_ik_twist()
```

---

## Issue #002: Joint Orientation & IK Popping Prevention (`rigTools.jointAt` + `freeze(r=True)`)

### 1. Symptom & Context
Procedural joint chains created from guide templates snap, twist, or pop out of position the instant an IK Handle (`ikRPsolver` / `ikSCsolver`) is created.

### 2. Root Cause & Mathematical Breakdown
* Maya IK Solvers calculate inverse kinematics exclusively from the joint's **`jointOrient`** and rest angles, and **forcefully reset non-zero Euler `rotate` channels to $[0, 0, 0]$** at solver initialization.
* Creating joints with raw `core.Joint()` and `maSnap()` leaves parent-relative Euler rotations in the `rotate` channels. When `mc.ikHandle()` is executed, Maya clears `rotate`, causing the joint chain to pop out of alignment with the guide template.

### 3. Mandatory Pipeline Standard
1. **Always use `rigTools.jointAt(tmpJnt)`**: Clones orientation, matches `rotateOrder`, and zeroes channels.
2. **Freeze Rotations after Hierarchy Construction (`jnt.freeze(r=True)`)**: Transfers parent-relative rotations into `jointOrient` and resets default `rotate` to $[0, 0, 0]$.
3. **Set Preferred Angles (`setPreferredAngles = True`)**: Run `mc.joint(jnt, edit=True, setPreferredAngles=True)` immediately after freezing rotations so the IK solver knows the natural bending plane.

---

## Issue #003: Global Scaling Double Translation Distortion in Matrix Offset Systems

### 1. Symptom & Context
Scaling the master controller (`placement_ctrl` e.g. $\times 2$ or $\times 0.5$) causes bind joints or child controllers in matrix-driven spines to stretch out by scale factor squared ($S^2$) or collapse.

### 2. Root Cause & Mathematical Breakdown
* In `multMatrix` offset networks (`apply_static_offset`), the static offset is multiplied by the target's parent inverse matrix:
  $$\text{LocalMatrix} = \text{WorldTargetMatrix} \times \text{StaticOffset} \times \text{ParentWorldInverseMatrix}$$
* If `parent.worldInverseMatrix[0]` is stripped of scale or bypassed, the local coordinate normalization $(1/S)$ is lost, resulting in translation scaling $S \times S = S^2$.

### 3. Mandatory Pipeline Standard
1. **Direct Parent Inverse Connection**: Always connect full `parent.worldInverseMatrix[0]` directly to `offset_node.matrixIn[2]`.
2. **Disable Segment Scale Compensate**: Always execute `mc.setAttr(f"{jnt}.segmentScaleCompensate", 0)` on procedural bind joints to prevent counter-scaling and shear distortion.
3. **Decouple Sequential Bind Joint Constraints**: Use `scale=False` on `parentConMatrixGPT` for sequential bind joint chains (`_bJnt01` $\rightarrow$ `_bJnt02`), letting scale inherit cleanly through the joint skeletal hierarchy.

---

## Issue #004: Maya Component Selection Order Sorting Bug (`filterExpand` vs `orderedSelection`)

### 1. Symptom & Context
Interactive tools relying on sequential component selection (e.g. `create_joints_raycast_mesh.py` selecting Start Edge $\rightarrow$ End Edge) generate joint chains in reversed direction (bottom-to-top or sky-facing) regardless of user click order.

### 2. Root Cause & Mathematical Breakdown
* Maya native commands `mc.filterExpand()` and `mc.ls(selection=True)` automatically sort components alphabetically and numerically by index ID (e.g. `e[12]`, `e[45]`, `e[108]`), completely destroying the user's sequential click order.

### 3. Mandatory Pipeline Standard
* Always query selection order using:
  ```python
  mc.ls(orderedSelection=True, flatten=True)
  ```
  with explicit start-to-end vertex/edge ownership verification (`find_path_between_two_edges`).

---

## Issue #005: Duplicate DAG Path String Evaluation in Maya Commands

### 1. Symptom & Context
Maya Python commands fail with errors like:
`Error reading data element number 1: [0, 0]` or `RuntimeError: More than one object matches name`.

### 2. Root Cause & Mathematical Breakdown
* If duplicate short node names exist in the scene DAG (e.g. `|L_snkBChildCV12` and `L_snkBChildCV11|L_snkBChildCV12`), Maya commands like `mc.getAttr(f"{node}.rotateOrder")` return a list of values `[0, 0]` instead of a single integer `0`, causing `mc.setAttr` to fail.

### 3. Mandatory Pipeline Standard
1. **Pre-flight Guide Validation**: Always scan guide templates and reject scenes with duplicate DAG short names before building rigs.
2. **Auto BaseName Isolation**: Use dynamic `baseName` prefixing on all procedural groups and math nodes (`L_snkAMod_grp`, `L_snkBMod_grp`) to guarantee 100% DAG uniqueness.
