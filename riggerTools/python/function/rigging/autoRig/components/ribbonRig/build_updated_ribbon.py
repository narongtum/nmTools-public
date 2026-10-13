import os

target_path = r"D:\sysTools\nmTools_github\riggerTools\python\function\rigging\autoRig\components\ribbonRig\eh_hh_ribbonExt.py"

content = '''#... Updated hhRibbon using matrix de_boor math with autoRig integration
import maya.cmds as mc
from maya.api import OpenMaya as om
from function.framework.reloadWrapper import reloadWrapper as reload

from function.rigging.de_boor import hh_de_boor_core as core
reload(core)

from function.rigging.autoRig.base import core as autoRigCore
reload(autoRigCore)

from function.rigging.autoRig.base import rigTools
reload(rigTools)

OPEN = 'open'
PERIODIC = 'periodic'
AXIS_VECTOR = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}
KNOT_TO_FORM_INDEX = {OPEN: om.MFnNurbsCurve.kOpen, PERIODIC: om.MFnNurbsCurve.kPeriodic}


def de_boor_ribbon(cvs, baseName='ribbon', side='LFT', nameSpace='', charScale=1, aim_axis='x', up_axis='y', num_joints=5, tangent_offset=0.001, d=None, kv_type=OPEN,
                   param_from_length=True, tol=0.000001, use_position=True, use_tangent=True,
                   use_up=True, use_scale=False):
    """
    AutoRig integrated de_boor_ribbon.
    """

    partElem = nameSpace + baseName

    mod_grp = autoRigCore.Null(f'{partElem}Mod{side}_grp')
    ctls_grp = autoRigCore.Null(f'{partElem}Ctls{side}_grp')
    jnts_grp = autoRigCore.Null(f'{partElem}Jnts{side}_grp')
    
    ctls_grp.parent(mod_grp)
    jnts_grp.parent(mod_grp)
    
    mc.matchTransform(mod_grp.name, cvs[0])

    ctls = []

    for i, cv in enumerate(cvs):
        ctl_name = f'{partElem}Cv{i+1:02d}{side}_ctrl'
        ctl = autoRigCore.Dag(ctl_name)
        ctl.nmCreateController('plus_ctrlShape')
        ctl.editCtrlShape(axis=charScale * 2.0)
        ctl.color = 'yellow'
        
        ctl.maSnap(cv)
        
        ctlZro_grp = rigTools.zroNewGrpWithOffset(ctl)
        mc.parent(ctlZro_grp[0], ctls_grp.name)
        
        ctls.append(ctl.name)

    num_cvs = len(cvs)
    original_cvs = cvs[:]

    d = num_cvs - 1 if d is None else d

    if kv_type == OPEN:
        kv, _ = core.knot_vector(OPEN, cvs, d)
        m_kv = kv[1:-1]
        m_cvs = cvs[:]
    else:
        m_cvs = [cvs[i - 1 % len(cvs)] for i in range(len(cvs))]
        for i in range(d):
            m_cvs.append(m_cvs[i])

        m_kv_len = len(m_cvs) + d - 1
        m_kv_interval = 1 / (m_kv_len - 2 * (d - 1) - 1)
        m_kv = [-m_kv_interval * (d - 1) * (1 - t / (m_kv_len - 1)) +
                (1 + m_kv_interval * (d - 1)) * t / (m_kv_len - 1) for t in range(m_kv_len)]

        kv, cvs = core.knot_vector(PERIODIC, cvs, d)

    m_cv_poss = om.MPointArray([mc.xform(obj, q=True, ws=True, t=True) for obj in m_cvs])
    form = KNOT_TO_FORM_INDEX[kv_type]
    is_2d = False
    rational = True
    data_creator = om.MFnNurbsCurveData()
    parent = data_creator.create()

    crv_fn = om.MFnNurbsCurve()
    crv_fn.create(m_cv_poss, m_kv, d, form, is_2d, rational, parent)

    if param_from_length:
        crv_len = crv_fn.length()
        params = []
        for i in range(num_joints):
            sample_len = crv_len * i / (num_joints - 1)
            if kv_type == PERIODIC:
                t = crv_fn.findParamFromLength((sample_len + crv_len * m_kv[2] * 0.5) % crv_len)
                params.append(t - m_kv[2] * 0.5)
            else:
                t = crv_fn.findParamFromLength(sample_len)
                params.append(t)
    else:
        params = [i / (num_joints - 1) for i in range(num_joints)]

    if kv_type == PERIODIC:
        params = [(kv[d + 1] * (d * 0.5 + 0.5)) * (1 - t) + t * (1 - kv[d + 1] * (d * 0.5 - 0.5))
                  for i, t in enumerate(params)]

    par_off_plugs = []
    trans_off_plugs = []
    sca_off_plugs = []

    for i, ctl in enumerate(ctls):
        par_off = mc.createNode('multMatrix', n=f'{partElem}ParOff{i+1:02d}{side}_mm')
        mc.connectAttr(f'{ctl}.worldMatrix[0]', f'{par_off}.matrixIn[0]')
        mc.connectAttr(f'{mod_grp.name}.worldInverseMatrix[0]', f'{par_off}.matrixIn[1]')

        par_off_plugs.append(f'{par_off}.matrixSum')

        trans_off = mc.createNode('pickMatrix', n=f'{partElem}Trans{i+1:02d}{side}_pm')
        mc.connectAttr(f'{par_off}.matrixSum', f'{trans_off}.inputMatrix')
        for attr in 'useRotate', 'useScale', 'useShear':
            mc.setAttr(f'{trans_off}.{attr}', False)

        trans_off_plugs.append(f'{trans_off}.outputMatrix')

        if use_scale and use_tangent or use_up:
            sca_off = mc.createNode('pickMatrix', n=f'{partElem}ScaleOff{i+1:02d}{side}_pm')
            mc.connectAttr(f'{par_off}.matrixSum', f'{sca_off}.inputMatrix')
            for attr in 'useRotate', 'useShear', 'useTranslate':
                mc.setAttr(f'{sca_off}.{attr}', False)

            sca_off_plugs.append(f'{sca_off}.outputMatrix')

    jnts = []

    for i, param in enumerate(params):
        num = i + 1
        detail_name = f'{partElem}{num:02d}{side}'
        
        wts = core.de_boor(len(cvs), d, param, kv, tol=tol)
        if kv_type == PERIODIC:
            wts = get_consolidated_wts(wts, original_cvs, cvs)

        tangent_param = param + tangent_offset
        aim_vector = om.MVector(AXIS_VECTOR[aim_axis])
        if tangent_param > 1:
            tangent_param = param - 2 * tangent_offset
            aim_vector *= -1

        tangent_wts = core.de_boor(len(cvs), d, tangent_param, kv, tol=tol)
        if kv_type == PERIODIC:
            tangent_wts = get_consolidated_wts(tangent_wts, original_cvs, cvs)

        position_plug = None
        tangent_plug = None

        if use_position:
            position = create_wt_add_matrix(trans_off_plugs, wts, f'{detail_name}Pos_wam', tol=tol)
            position_plug = f'{position}.matrixSum'

            if not use_tangent and not use_up:
                pass 
            if use_tangent:
                tangent = create_wt_add_matrix(trans_off_plugs, tangent_wts, f'{detail_name}Tan_wam', tol=tol)
                tangent_plug = f'{tangent}.matrixSum'

        up_plug = f'{mod_grp.name}.worldMatrix[0]'

        if use_up:
            temp = mc.createNode('transform')
            mc.parent(temp, mod_grp.name)
            ori_con = mc.orientConstraint(original_cvs, temp, mo=False)[0]
            mc.setAttr(f'{ori_con}.interpType', 2)
            for j, wt in enumerate(wts):
                mc.setAttr(f'{ori_con}.{original_cvs[j]}W{j}', wt)

            up = create_wt_add_matrix(par_off_plugs, wts, f'{detail_name}Up_wam', tol=tol)

            temp_mat = om.MMatrix(mc.getAttr(f'{temp}.matrix'))
            up_inverse = om.MMatrix(mc.getAttr(f'{up}.matrixSum')).inverse()
            up_off_val = temp_mat * up_inverse

            up_off = mc.createNode('multMatrix', n=f'{detail_name}UpOff_mm')
            mc.setAttr(f'{up_off}.matrixIn[0]', list(up_off_val), type='matrix')
            mc.connectAttr(f'{up}.matrixSum', f'{up_off}.matrixIn[1]')

            up_plug = f'{up_off}.matrixSum'
            mc.delete(temp)

        aim = mc.createNode('aimMatrix', n=f'{detail_name}Aim_am')

        if position_plug:
            mc.connectAttr(position_plug, f'{aim}.inputMatrix')
        else:
            matrices = [om.MMatrix(mc.getAttr(top)) for top in trans_off_plugs]
            trans_wt_mat = get_weighted_translation_matrix(matrices, wts)
            mc.setAttr(f'{aim}.inputMatrix', trans_wt_mat, type='matrix')

        if tangent_plug:
            mc.connectAttr(f'{tangent}.matrixSum', f'{aim}.primaryTargetMatrix')
        else:
            matrices = [om.MMatrix(mc.getAttr(top)) for top in trans_off_plugs]
            trans_wt_mat = get_weighted_translation_matrix(matrices, tangent_wts)

            if position_plug:
                position_m = om.MMatrix(mc.getAttr(position_plug))
                tangent_offset_val = trans_wt_mat * position_m.inverse()
                tangent_off = mc.createNode('multMatrix', n=f'{detail_name}TanOff_mm')
                mc.setAttr(f'{tangent_off}.matrixIn[0]', tangent_offset_val, type='matrix')
                mc.connectAttr(position_plug, f'{tangent_off}.matrixIn[1]')
                mc.connectAttr(f'{tangent_off}.matrixSum', f'{aim}.primaryTargetMatrix')
            else:
                mc.setAttr(f'{aim}.primaryTargetMatrix', trans_wt_mat, type='matrix')

        if up_plug == f'{mod_grp.name}.worldMatrix[0]':
            mod_mat = mc.getAttr(up_plug)
            mc.setAttr(f'{aim}.secondaryTargetMatrix', mod_mat, type='matrix')
        else:
            mc.connectAttr(up_plug, f'{aim}.secondaryTargetMatrix')

        output_plug = f'{aim}.outputMatrix'
        mc.setAttr(f'{aim}.primaryInputAxis', *aim_vector)
        mc.setAttr(f'{aim}.secondaryInputAxis', *AXIS_VECTOR[up_axis])
        mc.setAttr(f'{aim}.secondaryMode', 2)
        mc.setAttr(f'{aim}.secondaryTargetVector', *AXIS_VECTOR[up_axis])

        if use_scale:
            scale_wam = create_wt_add_matrix(sca_off_plugs, wts, f'{detail_name}Scale_wam', tol=tol)
            scale_mm = mc.createNode('multMatrix', n=f'{detail_name}Scale_mm')
            mc.connectAttr(f'{scale_wam}.matrixSum', f'{scale_mm}.matrixIn[0]')
            mc.connectAttr(output_plug, f'{scale_mm}.matrixIn[1]')
            output_plug = f'{scale_mm}.matrixSum'

        # CREATE DETAIL CONTROL
        ribbon_ctrl = autoRigCore.Dag(f'{detail_name}_ctrl')
        ribbon_ctrl.nmCreateController('circle_ctrlShape')
        ribbonZro_grp = rigTools.zeroGroupNam(ribbon_ctrl)
        ribbon_ctrl.editCtrlShape(axis=charScale * 1.8)
        ribbon_ctrl.color = 'softBlue'
        
        # Apply aimMatrix to the detail ctrl's Zero Group Offset Parent Matrix
        mc.connectAttr(output_plug, f'{ribbonZro_grp.name}.offsetParentMatrix')
        mc.parent(ribbonZro_grp.name, jnts_grp.name)
        
        # Reset Zero Group transforms
        mc.setAttr(f'{ribbonZro_grp.name}.translate', 0, 0, 0)
        mc.setAttr(f'{ribbonZro_grp.name}.rotate', 0, 0, 0)
        
        # CREATE JOINT
        mc.select(cl=True)
        jnt = autoRigCore.Joint(f'{detail_name}_pxyJnt')
        jnt.parent(ribbon_ctrl.name)
        mc.setAttr(f'{jnt.name}.translate', 0, 0, 0)
        mc.setAttr(f'{jnt.name}.rotate', 0, 0, 0)
        mc.setAttr(f'{jnt.name}.jointOrient', 0, 0, 0)
        
        jnt.attr('displayLocalAxis').value = 1
        jnt.attr('radius').value = charScale * 0.25
        jnt.attr('overrideEnabled').value = 1
        jnt.attr('overrideColor').value = 3
        
        ribbon_ctrl.lockHideAttrLst('v')
        
        jnts.append(jnt.name)

    return jnts


def get_consolidated_wts(wts, original_cvs, cvs):
    consolidated_wts = {cv: 0 for cv in original_cvs}
    for j, wt in enumerate(wts):
        consolidated_wts[cvs[j]] += wt
    return [consolidated_wts[cv] for cv in original_cvs]


def create_wt_add_matrix(matrix_attrs, wts, name, tol=0.000001):
    wam = mc.createNode('wtAddMatrix', n=name)
    for matrix_attr, wt, i in zip(matrix_attrs, wts, range(len(matrix_attrs))):
        if wt < tol:
            continue
        mc.connectAttr(matrix_attr, f'{wam}.wtMatrix[{i}].matrixIn')
        mc.setAttr(f'{wam}.wtMatrix[{i}].weightIn', wt)
    return wam

def get_weighted_translation_matrix(matrices, wts):
    translation_m = om.MMatrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    for m, wt in zip(matrices, wts):
        for i in 12, 13, 14:
            translation_m[i] += m[i] * wt
    return translation_m

'''

with open(target_path, 'w') as f:
    f.write(content)
print(f"Created {target_path}")
