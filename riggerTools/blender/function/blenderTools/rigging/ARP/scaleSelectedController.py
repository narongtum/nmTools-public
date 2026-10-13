import bpy
import importlib

class WM_OT_arp_scale_controller(bpy.types.Operator):
    bl_idname = "wm.arp_scale_controller"
    bl_label = "Scale Selected Controller"
    bl_options = {'REGISTER', 'UNDO'}

    # 1. ตัวแปรปรับค่าสเกลที่จะไปโชว์บนหน้าต่าง UI Popup
    scale_factor: bpy.props.FloatProperty(
        name="Scale Factor",
        description="Multiply custom shape scale by this factor",
        default=1.1,
        min=0.01,
        max=100.0
    )

    # 2. ฟังก์ชันเรียกเปิดหน้าต่าง UI Popup ขึ้นมาก่อน (ยังไม่รันคำสั่งทันที)
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # 3. วาดการแสดงผลของค่าปรับระดับในหน้าต่าง UI Popup
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scale_factor") # สร้าง Slider/ช่องพิมพ์ตัวเลขสเกล

    # 4. ทำงานจริงเมื่อผู้ใช้กดปุ่ม OK (Apply) บนหน้าต่าง UI Popup
    def execute(self, context):
        try:
            # ดึงคำสั่งจากไฟล์สคริปต์สเกลของคุณโดยอ้างอิงผ่าน path ที่ append ไว้
            from function.blenderTools.rigging.ARP import scaleSelectedController
            importlib.reload(scaleSelectedController)
            
            # ส่งค่า scale_factor ที่ผู้ใช้ปรับจาก UI เข้าไปรันในฟังก์ชันจริง
            scaleSelectedController.scale_selected(self.scale_factor)
            
            self.report({'INFO'}, f"Applied scale factor: {self.scale_factor}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to execute scale script: {e}")
            
        return {'FINISHED'}
