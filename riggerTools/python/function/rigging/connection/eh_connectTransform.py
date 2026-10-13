"""
Module: eh_connectTransform.py
Author: Senior Pipeline Advisor (AI Assistant)
Description:
    Procedural transform connection utility between source and target nodes (e.g. joints).
    Connects translation directly and bridges rotation through intermediate Quaternion nodes
    (eulerToQuat -> quatToEuler) to eliminate Gimbal lock, axis flipping, and Rotate Order
    mismatch across disparate hierarchies.

Usage:
    from function.rigging.connection import eh_connectTransform as conn
    reload(conn)

    pairs = [
        ('spine03_bJnt', 'spineNm03_bJnt'),
        ('clavLFT_bJnt', 'clavNmLFT_bJnt')
    ]
    conn.connectTranslateAndRotate(pairs, translate=True, rotate=True, scale=False)

    # To disconnect:
    conn.disconnectTranslateAndRotate(pairs, translate=True, rotate=True, scale=False)
"""

import maya.cmds as mc
from function.framework.reloadWrapper import reloadWrapper as reload
from function.rigging.autoRig.base import core
reload(core)


def _normalize_pairs(pairs):
    """
    Normalizes input pairs into a list of (source, target) tuples.
    Supports a single pair ('src', 'tgt') or a list of pairs [('src1', 'tgt1'), ...].
    """
    if not pairs:
        return []

    # Check if single pair passed as tuple/list of two strings
    if len(pairs) == 2 and isinstance(pairs[0], str) and isinstance(pairs[1], str):
        return [(str(pairs[0]), str(pairs[1]))]

    normalized = []
    for item in pairs:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            normalized.append((str(item[0]), str(item[1])))
        else:
            mc.error(f"[eh_connectTransform] Invalid pair item format: {item}. Expected (source, target) tuple.")
    return normalized


def connectTranslateAndRotate(pairs, translate=True, rotate=True, scale=False, match_rotate_order=True):
    """
    Connects translation and rotation from source to target nodes across a list of pairs.
    Rotation is bridged via Quaternion nodes (eulerToQuat -> quatToEuler) to guarantee
    zero rotation pop or Gimbal lock, honoring each node's rotateOrder dynamically.

    Args:
        pairs (list of tuple/list, or single tuple):
            Pairs of (source, target) nodes.
            e.g. [('spine03_bJnt', 'spineNm03_bJnt'), ('clavLFT_bJnt', 'clavNmLFT_bJnt')]
        translate (bool): Connect source.translate -> target.translate. Default is True.
        rotate (bool): Connect source.rotate -> target.rotate via Quaternion Bridge. Default is True.
        scale (bool): Connect source.scale -> target.scale. Default is False.
        match_rotate_order (bool): Copy and place source.rotateOrder onto target.rotateOrder. Default is True.

    Returns:
        dict: Mapping of target nodes to created connection data and utility nodes.
    """
    pair_list = _normalize_pairs(pairs)
    if not pair_list:
        mc.warning("[eh_connectTransform] No pairs provided to connect.")
        return {}

    # Strict Fail-Fast Validation: verify all nodes exist before making any connections
    missing_nodes = []
    for src, tgt in pair_list:
        if not mc.objExists(src):
            missing_nodes.append(src)
        if not mc.objExists(tgt):
            missing_nodes.append(tgt)

    if missing_nodes:
        mc.error(
            f"[eh_connectTransform] Fatal Error: The following nodes do not exist in the scene:\n"
            f"{', '.join(missing_nodes)}\n"
            f"Action Required: Please ensure all guide/bind joints exist before connecting."
        )

    core.makeHeader('Start of connectTranslateAndRotate')

    results = {}

    for src, tgt in pair_list:
        #... Extract base name for clean node naming
        base_name = core.check_name_style(tgt)[0] if tgt else tgt
        if not base_name:
            base_name = tgt.replace('_bJnt', '').replace('_jnt', '')

        pair_data = {
            'source': src,
            'target': tgt,
            'translate_connected': False,
            'rotate_connected': False,
            'scale_connected': False,
            'e2q_node': None,
            'q2e_node': None
        }

        # ------------------------------------------------------------------
        # 1. Translate Connection
        # ------------------------------------------------------------------
        if translate:
            src_attr = f"{src}.translate"
            tgt_attr = f"{tgt}.translate"
            mc.connectAttr(src_attr, tgt_attr, force=True)
            pair_data['translate_connected'] = True

        # ------------------------------------------------------------------
        # 2. Rotate Connection via Quaternion Bridge (Order-Independent)
        # ------------------------------------------------------------------
        if rotate:
            # 2.1 Copy & Place rotateOrder from source to target
            if match_rotate_order and mc.attributeQuery('rotateOrder', node=src, exists=True) and mc.attributeQuery('rotateOrder', node=tgt, exists=True):
                src_ro = mc.getAttr(f"{src}.rotateOrder")
                # Ensure target rotateOrder is updated if not driven by an external source
                if not mc.listConnections(f"{tgt}.rotateOrder", source=True, destination=False):
                    is_locked = mc.getAttr(f"{tgt}.rotateOrder", lock=True)
                    if is_locked:
                        mc.setAttr(f"{tgt}.rotateOrder", lock=False)
                    mc.setAttr(f"{tgt}.rotateOrder", src_ro)
                    if is_locked:
                        mc.setAttr(f"{tgt}.rotateOrder", lock=True)
                pair_data['source_rotate_order'] = src_ro
                pair_data['target_rotate_order'] = mc.getAttr(f"{tgt}.rotateOrder")

            e2q_name = f"{base_name}_rot_eulToQuat"
            q2e_name = f"{base_name}_rot_quatToEul"

            # Check if matching utility nodes already exist; reuse or create net-new
            if mc.objExists(e2q_name):
                e2q = e2q_name
            else:
                e2q = mc.createNode('eulerToQuat', name=e2q_name)

            if mc.objExists(q2e_name):
                q2e = q2e_name
            else:
                q2e = mc.createNode('quatToEuler', name=q2e_name)

            # Connect Driver -> eulerToQuat (reads driver Euler respecting its rotateOrder)
            mc.connectAttr(f"{src}.rotate", f"{e2q}.inputRotate", force=True)
            mc.connectAttr(f"{src}.rotateOrder", f"{e2q}.inputRotateOrder", force=True)

            # Bridge Quaternions (4D space, order-free)
            mc.connectAttr(f"{e2q}.outputQuat", f"{q2e}.inputQuat", force=True)

            # Connect quatToEuler -> Driven (evaluates back to Euler respecting driven rotateOrder)
            mc.connectAttr(f"{tgt}.rotateOrder", f"{q2e}.inputRotateOrder", force=True)
            mc.connectAttr(f"{q2e}.outputRotate", f"{tgt}.rotate", force=True)

            pair_data['rotate_connected'] = True
            pair_data['e2q_node'] = e2q
            pair_data['q2e_node'] = q2e

        # ------------------------------------------------------------------
        # 3. Scale Connection (Optional)
        # ------------------------------------------------------------------
        if scale:
            src_attr = f"{src}.scale"
            tgt_attr = f"{tgt}.scale"
            mc.connectAttr(src_attr, tgt_attr, force=True)
            pair_data['scale_connected'] = True

        results[tgt] = pair_data
        print(f"[eh_connectTransform] Successfully connected: {src} -> {tgt} (T={translate}, R={rotate}, S={scale})")

    core.makeHeader('End of connectTranslateAndRotate')
    return results


def disconnectTranslateAndRotate(pairs, translate=True, rotate=True, scale=False, delete_nodes=True):
    """
    Disconnects transform connections from target nodes across a list of pairs.
    Optionally deletes intermediate Quaternion nodes created during connection.

    Args:
        pairs (list of tuple/list, or single tuple):
            Pairs of (source, target) nodes.
        translate (bool): Break target.translate connections. Default is True.
        rotate (bool): Break target.rotate connections. Default is True.
        scale (bool): Break target.scale connections. Default is False.
        delete_nodes (bool): Delete associated eulerToQuat / quatToEuler utility nodes. Default is True.

    Returns:
        list: List of targets successfully disconnected.
    """
    pair_list = _normalize_pairs(pairs)
    core.makeHeader('Start of disconnectTranslateAndRotate')
    disconnected = []

    for src, tgt in pair_list:
        if not mc.objExists(tgt):
            continue

        # 1. Disconnect Translate
        if translate:
            for axis in ('X', 'Y', 'Z'):
                attr = f"{tgt}.translate{axis}"
                source_conn = mc.listConnections(attr, source=True, destination=False, plugs=True)
                if source_conn:
                    mc.disconnectAttr(source_conn[0], attr)

            full_attr = f"{tgt}.translate"
            source_conn_full = mc.listConnections(full_attr, source=True, destination=False, plugs=True)
            if source_conn_full:
                mc.disconnectAttr(source_conn_full[0], full_attr)

        # 2. Disconnect Rotate & Clean Quaternion Nodes
        if rotate:
            nodes_to_delete = set()
            for axis in ('X', 'Y', 'Z'):
                attr = f"{tgt}.rotate{axis}"
                source_conn = mc.listConnections(attr, source=True, destination=False, plugs=True)
                if source_conn:
                    node = source_conn[0].split('.')[0]
                    if mc.nodeType(node) == 'quatToEuler':
                        nodes_to_delete.add(node)
                    mc.disconnectAttr(source_conn[0], attr)

            full_attr = f"{tgt}.rotate"
            source_conn_full = mc.listConnections(full_attr, source=True, destination=False, plugs=True)
            if source_conn_full:
                node = source_conn_full[0].split('.')[0]
                if mc.nodeType(node) == 'quatToEuler':
                    nodes_to_delete.add(node)
                mc.disconnectAttr(source_conn_full[0], full_attr)

            # Disconnect rotateOrder on target if fed by quatToEuler
            ro_conn = mc.listConnections(f"{tgt}.rotateOrder", source=False, destination=True, plugs=True)
            if ro_conn:
                for dest_plug in ro_conn:
                    dest_node = dest_plug.split('.')[0]
                    if mc.nodeType(dest_node) == 'quatToEuler':
                        nodes_to_delete.add(dest_node)
                        mc.disconnectAttr(f"{tgt}.rotateOrder", dest_plug)

            # Trace upstream eulerToQuat and delete both
            if delete_nodes:
                for q2e in list(nodes_to_delete):
                    if mc.objExists(q2e):
                        # Find input eulerToQuat
                        e2q_conns = mc.listConnections(f"{q2e}.inputQuat", source=True, destination=False)
                        if e2q_conns:
                            for e2q in e2q_conns:
                                if mc.nodeType(e2q) == 'eulerToQuat' and mc.objExists(e2q):
                                    mc.delete(e2q)
                        mc.delete(q2e)

        # 3. Disconnect Scale
        if scale:
            for axis in ('X', 'Y', 'Z'):
                attr = f"{tgt}.scale{axis}"
                source_conn = mc.listConnections(attr, source=True, destination=False, plugs=True)
                if source_conn:
                    mc.disconnectAttr(source_conn[0], attr)

            full_attr = f"{tgt}.scale"
            source_conn_full = mc.listConnections(full_attr, source=True, destination=False, plugs=True)
            if source_conn_full:
                mc.disconnectAttr(source_conn_full[0], full_attr)

        disconnected.append(tgt)
        print(f"[eh_connectTransform] Disconnected transforms for target: {tgt}")

    core.makeHeader('End of disconnectTranslateAndRotate')
    return disconnected
