import bpy

# ดึงอ็อบเจกต์ทั้งหมดที่กำลังเลือกอยู่ (Selected Objects)
selected_objs = bpy.context.selected_objects

if not selected_objs:
    print("No object selected")
else:
    print("--- Selected Objects Types ---")
    for obj in selected_objs:
        # obj.type จะส่งกลับค่าตัวใหญ่ เช่น 'MESH', 'ARMATURE', 'EMPTY', 'CAMERA', 'CURVE'
        print(f"Name: {obj.name} | Type: {obj.type}")