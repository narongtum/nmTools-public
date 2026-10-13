import bpy

# 1. สร้าง Operator
class MainMenuCustomAction(bpy.types.Operator):
	bl_idname = "wm.main_menu_custom_action"
	bl_label = "My Main Menu Action"

	def execute(self, context):
		self.report({'INFO'}, "ทำงานผ่านเมนูหลักด้านบนสุดแล้ว!")
		return {'FINISHED'}

# 2. สร้างตัว Menu
class TOPBAR_MT_my_custom_main_menu(bpy.types.Menu):
	bl_label = "My Tools"
	bl_idname = "TOPBAR_MT_my_custom_main_menu"

	def draw(self, context):
		layout = self.layout
		layout.operator("wm.main_menu_custom_action", text="Rigging Tool A", icon='ARMATURE_DATA')
		layout.operator("wm.main_menu_custom_action", text="Rigging Tool B", icon='CONSTRAINT')

# 3. ฟังก์ชันสำหรับวาดเมนู
def draw_main_menu(self, context):
	self.layout.menu(TOPBAR_MT_my_custom_main_menu.bl_idname)

classes = (
	MainMenuCustomAction,
	TOPBAR_MT_my_custom_main_menu,
)

def register():
	# --- [ตรวจสอบและลบเมนูเก่าที่ชื่อซ้ำ] ---
	# ค้นหาใน _draw_funcs ของ Topbar
	if hasattr(bpy.types.TOPBAR_MT_editor_menus, "_draw_funcs"):
		for func in list(bpy.types.TOPBAR_MT_editor_menus._draw_funcs):
			# ถ้าเจอชื่อฟังก์ชันวาดเมนูตัวเดิม ให้ลบออกทันที
			if func.__name__ == "draw_main_menu":
				try:
					bpy.types.TOPBAR_MT_editor_menus.remove(func)
				except Exception as e:
					print(f"Error removing old menu callback: {e}")

	# --- [ตรวจสอบและ Unregister Class เก่าเพื่อกัน Error] ---
	for cls in classes:
		try:
			bpy.utils.unregister_class(cls)
		except Exception:
			# ถ้าไม่มี Class นี้ค้างอยู่ในระบบอยู่แล้ว ให้ข้ามไปได้เลย
			pass
			
	# --- [ลงทะเบียนใหม่ทั้งหมด] ---
	for cls in classes:
		bpy.utils.register_class(cls)
	
	# เพิ่มเมนูใหม่เข้าไป
	bpy.types.TOPBAR_MT_editor_menus.append(draw_main_menu)

def unregister():
	for cls in classes:
		try:
			bpy.utils.unregister_class(cls)
		except Exception:
			pass
			
	if hasattr(bpy.types.TOPBAR_MT_editor_menus, "_draw_funcs"):
		for func in list(bpy.types.TOPBAR_MT_editor_menus._draw_funcs):
			if func.__name__ == "draw_main_menu":
				bpy.types.TOPBAR_MT_editor_menus.remove(func)

if __name__ == "__main__":
	register()
