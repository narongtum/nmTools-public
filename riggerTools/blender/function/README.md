# Blender File Manager Setup

คู่มือการติดตั้งระบบเครื่องมือจัดการไฟล์ (File Manager) สำหรับ Blender ในโครงสร้างโปรเจกต์ของทีม

## ขั้นตอนการติดตั้ง (Installation Steps)

เพื่อให้ระบบเครื่องมือทำงานร่วมกับ Blender ได้อย่างถูกต้อง กรุณาดำเนินการคัดลอกไฟล์ตามขั้นตอนดังนี้:

### 1. ติดตั้งไฟล์คำสั่งเปิดใช้งานอัตโนมัติ (Startup Script)
ให้นำไฟล์สคริปต์สตาร์ทอัพไปวางไว้ในโฟลเดอร์ Startup ของ Blender เพื่อให้โหลดเมนูทำงานโดยอัตโนมัติทุกครั้งเมื่อเปิดโปรแกรม:
*   **ไฟล์ต้นทาง:** `D:\sysTools\nmTools_github\riggerTools\blender\function\blender_startup\blenderUserStartup.py`
*   **โฟลเดอร์ปลายทาง:**
    `C:\Users\<ชื่อผู้ใช้งาน Windows>\AppData\Roaming\Blender Foundation\Blender\<เวอร์ชันของ Blender>\scripts\startup\blenderUserStartup.py`

*(หมายเหตุ: หากไม่มีโฟลเดอร์ `startup` ภายใต้ไดเรกทอรีดังกล่าว ให้สร้างโฟลเดอร์ขึ้นมาใหม่)*

---

### 2. ติดตั้งไฟล์ตั้งค่า (Configuration File)
นำไฟล์ตั้งค่าโครงสร้างโฟลเดอร์โปรเจกต์ไปวางไว้ในโฟลเดอร์ Documents (My Documents) ของคุณ เพื่อเปิดให้ตัวเครื่องมือดึงค่าคอนฟิกได้ถูกต้อง:
*   **ไฟล์ต้นทาง:** `D:\sysTools\nmTools_github\riggerTools\blender\function\blender_startup\blender_fileManager_config.py`
*   **โฟลเดอร์ปลายทาง:**
    `C:\Users\<ชื่อผู้ใช้งาน Windows>\Documents\blender\scripts\blender_fileManager_config.py`

*(หมายเหตุ: หากไม่มีโฟลเดอร์ `blender\scripts` ภายใต้ Documents ให้ทำการสร้างโฟลเดอร์ขึ้นมาใหม่)*

---

## การปรับแต่งและการแก้ไขข้อมูลเพิ่มเติม
คุณสามารถแก้ไขไฟล์ตั้งค่า `blender_fileManager_config.py` ใน Documents เพื่อปรับแต่งข้อมูลโปรเจกต์ เช่น:
*   **DRIVES**: กำหนดไดรฟ์ที่ใช้จัดเก็บไฟล์งาน (เช่น `"D:\\"`, `"E:\\"`)
*   **PROJECT_NAME**: รายชื่อโฟลเดอร์โปรเจกต์ในระบบงาน
*   **BASE_FOLDER**: ชื่อโฟลเดอร์จัดเก็บหลักของ SVN (เริ่มต้นคือ `"svn_repo"`)
