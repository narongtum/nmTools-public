import os
import json
import maya.cmds as mc
from function.animation.studiolibrary_mirrortable import MirrorTable, MirrorOption, KeysOption

# Path ไปที่ไฟล์ mirrortable.json ของคุณ
MIRROR_TABLE_PATH = r"D:\Studio Library\Noman\Dagon_mirror_02.mirror\mirrortable.json"


def mirror_anim_from_table(json_path=MIRROR_TABLE_PATH):
    """
    Mirror animation for selected controllers using a Studio Library mirror table.
    1. Load mirrorAxis and mapping from mirrortable.json
    2. Swap animation curves (All Keys)
    3. Swap custom attributes (with keyframes) if they exist on both sides
    """

    if not os.path.isfile(json_path):
        mc.error("Mirror table JSON not found: " + json_path)

    sel = mc.ls(sl=True, type='transform') or []
    if not sel:
        mc.error("Please select one or more controllers.")

    # --- Step 1: Mirror transforms (Studio Library logic) ---
    mt = MirrorTable.fromPath(json_path)
    mt.load(objects=sel,
            option=MirrorOption.Swap,
            keysOption=KeysOption.All,
            namespaces=[])

    print("[Mirror] Transforms mirrored using:", json_path)

    # --- Step 2: Swap custom attribute keyframes ---
    with open(json_path, "r") as f:
        table_data = json.load(f)

    objects_data = table_data.get("objects", {})

    for obj_name, data in objects_data.items():
        other = data.get("opposite")
        if not other or other not in objects_data:
            continue
        if not (mc.objExists(obj_name) and mc.objExists(other)):
            continue

        # หา custom attrs ของแต่ละ object
        attrs_left = mc.listAttr(obj_name, ud=True, k=True) or []
        attrs_right = mc.listAttr(other, ud=True, k=True) or []

        # หา common attr ที่มีทั้งสองฝั่ง
        common = set(attrs_left).intersection(set(attrs_right))

        for attr in common:
            left_attr = f"{obj_name}.{attr}"
            right_attr = f"{other}.{attr}"

            # query keyframes
            left_keys = mc.keyframe(left_attr, q=True, tc=True) or []
            right_keys = mc.keyframe(right_attr, q=True, tc=True) or []

            # backup ค่า keyframes ทั้งหมด
            left_anim = mc.keyframe(left_attr, q=True, vc=True, tc=True) or []
            right_anim = mc.keyframe(right_attr, q=True, vc=True, tc=True) or []

            # clear keyframes ก่อน
            if left_keys:
                mc.cutKey(left_attr, time=(min(left_keys), max(left_keys)), cl=True)
            if right_keys:
                mc.cutKey(right_attr, time=(min(right_keys), max(right_keys)), cl=True)

            # ใส่ค่าใหม่: swap L ↔ R
            if right_anim:
                for t, v in zip(right_anim[::2], right_anim[1::2]):
                    mc.setKeyframe(left_attr, time=t, value=v)
            if left_anim:
                for t, v in zip(left_anim[::2], left_anim[1::2]):
                    mc.setKeyframe(right_attr, time=t, value=v)

            print(f"[Mirror] Swapped keyframes for attr {attr}: {obj_name} <-> {other}")


# === ตัวอย่างการใช้งาน ===
# 1. เลือก controllers ของ character
# 2. รันฟังก์ชันนี้
mirror_anim_from_table()
