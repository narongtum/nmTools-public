"""Pole Vector placement utilities for temp-joint chains in Maya.

โมดูลนี้ใช้คำนวณและวางตำแหน่ง Pole Vector (PV) ให้ตรงกับ "ระนาบการงอ"
ของโซ่ joint 3 ตัว (เช่น shoulder-elbow-wrist หรือ thumb02-03-04)
โดยยึดหลักว่า:

	* ทิศของ PV ต้องตั้งฉากกับแกนหลักของโซ่ (p1 -> p3) เสมอ
	* ทิศของ PV ต้องอยู่ในระนาบการงอจริง แม้ระนาบนั้นจะเอียงในแกนใดก็ตาม
	* ระยะห่างคิดแบบสัมพัทธ์กับความยาวโซ่ ไม่ใช่หน่วยสัมบูรณ์
	  เพื่อให้ใช้ได้ทั้งกับนิ้วมือและแขน/ขา โดยไม่ต้องแก้ค่าใหม่

ข้อกำหนดสำคัญ:
	โซ่ joint **ต้องถูกงอมาแล้ว** โดย rigger ก่อนเรียกใช้
	หากโซ่เกือบเป็นเส้นตรง ระนาบการงอจะไม่มีอยู่จริงทางคณิตศาสตร์
	โมดูลนี้จะ raise :class:`PoleVectorError` แทนการเดาค่าให้

Example:
	>>> import pole_vector_utils as pvu
	>>> pvu.place_pv_on_plane(
	...     'thumb02LFT_tmpJnt', 'thumb03LFT_tmpJnt',
	...     'thumb04LFT_tmpJnt', 'thumbPovLFT_tmpJnt', factor=1.0)

Note:
	ใช้ maya.OpenMaya (API 1.0) เพื่อให้ทำงานได้กับ Maya รุ่นเก่า
	หากต้องการย้ายไป API 2.0 ให้เปลี่ยน import เป็น
	``maya.api.OpenMaya`` และแก้ ``*`` (dot product) เป็น ``v1 * v2``
	ซึ่งใช้ syntax เดียวกัน แต่ ``^`` (cross) ยังคงเหมือนเดิม
"""

import math

import maya.cmds as mc
import maya.OpenMaya as om

#: ค่า epsilon สำหรับเทียบความยาวเวกเตอร์กับศูนย์ (หน่วยเดียวกับ scene unit)
EPS = 1e-5


class PoleVectorError(RuntimeError):
	"""ข้อผิดพลาดที่เกิดเมื่อโซ่ joint ไม่ผ่านเงื่อนไขการคำนวณระนาบ.

	ใช้เป็น exception เฉพาะทาง เพื่อให้ผู้เรียกสามารถ catch เฉพาะปัญหา
	ที่เกี่ยวกับ Pole Vector ได้ โดยไม่ไปกลืน error อื่น ๆ ของ Maya

	สาเหตุที่พบบ่อย:
		* ไม่พบ object ตามชื่อที่ระบุ (พิมพ์ชื่อ joint ผิด)
		* joint สองตัวติดกันทับตำแหน่งกันสนิท
		* joint กลางยังไม่ได้ถูกงอ ทำให้โซ่เป็นเส้นตรง

	Example:
		>>> try:
		...     place_pv_on_plane(a, b, c, pv)
		... except PoleVectorError as err:
		...     mc.warning(str(err))
	"""
	pass


def _pos(obj):
	"""คืนตำแหน่ง world-space ของ object ในรูปแบบ MVector.

	Args:
		obj (str): ชื่อ DAG object ใน scene (เช่น ``'thumb02LFT_tmpJnt'``)

	Returns:
		om.MVector: ตำแหน่ง world-space (x, y, z)

	Raises:
		PoleVectorError: เมื่อไม่พบ object ตามชื่อที่ระบุใน scene
	"""
	if not mc.objExists(obj):
		raise PoleVectorError("ไม่พบ object: '%s'" % obj)
	return om.MVector(*mc.xform(obj, q=True, ws=True, t=True))


def get_bend_angle(p1_name, p2_name, p3_name):
	"""คำนวณมุมงอที่ joint กลางของโซ่ 3 ตัว.

	ใช้ตรวจสอบล่วงหน้าว่าโซ่งอพอสำหรับคำนวณระนาบหรือยัง
	โดยไม่ต้องเรียก :func:`place_pv_on_plane` แล้วดัก exception

	Args:
		p1_name (str): joint ต้นโซ่
		p2_name (str): joint กลาง (จุดที่งอ)
		p3_name (str): joint ปลายโซ่

	Returns:
		float: มุมงอในหน่วยองศา โดย ``180.0`` = ตรงสนิท,
			ค่าน้อยลง = งอมากขึ้น (เช่น ``90.0`` = งอฉาก)

	Raises:
		PoleVectorError: เมื่อไม่พบ object หรือมี joint ทับตำแหน่งกัน

	Example:
		>>> get_bend_angle('thumb02LFT_tmpJnt',
		...                'thumb03LFT_tmpJnt',
		...                'thumb04LFT_tmpJnt')
		168.42
	"""
	p1, p2, p3 = _pos(p1_name), _pos(p2_name), _pos(p3_name)
	v1, v2 = p2 - p1, p3 - p2

	if v1.length() < EPS or v2.length() < EPS:
		raise PoleVectorError(
			"Joint ทับกัน: ตรวจ '%s', '%s', '%s'" % (p1_name, p2_name, p3_name))

	cos_a = max(-1.0, min(1.0, v1.normal() * v2.normal()))
	return 180.0 - math.degrees(math.acos(cos_a))


def place_pv_on_plane(p1_name, p2_name, p3_name, pv_name,
					  factor=1.0, dist=None,
					  min_angle=2.0, align=True, flip=False):
	"""วาง Pole Vector บนระนาบการงอจริง เหนือ joint กลางของโซ่.

	ฟังก์ชันคำนวณ normal ของระนาบจาก cross product ของกระดูกทั้งสองท่อน
	แล้วหาทิศของ PV จาก ``normal x chain`` ซึ่งรับประกันว่าได้ทิศที่
	**ตั้งฉากกับแกนหลักของโซ่** และ **อยู่ในระนาบการงอ** เสมอ
	ต่างจากวิธี ``p2 - midpoint`` ที่จะเบี้ยวเมื่อกระดูกสองท่อนยาวไม่เท่ากัน

	ขั้นตอนการทำงาน:
		1. อ่านตำแหน่ง world-space ของ joint ทั้งสาม
		2. ตรวจว่าโซ่งอเกิน ``min_angle`` หรือไม่ (ถ้าไม่ -> raise)
		3. หา normal ของระนาบ แล้ว cross กับแกนโซ่เพื่อได้ทิศ PV
		4. กลับทิศให้ชี้ออกด้านนอกของข้อพับเสมอ
		5. ย้าย PV ไปยังตำแหน่งเป้าหมาย และจัด rotation (ถ้า ``align=True``)

	Args:
		p1_name (str): joint ต้นโซ่ เช่น ``'thumb02LFT_tmpJnt'``
		p2_name (str): joint กลาง จุดอ้างอิงตำแหน่งของ PV
		p3_name (str): joint ปลายโซ่
		pv_name (str): object ที่จะถูกย้าย (locator หรือ temp joint ของ PV)
		factor (float): ตัวคูณระยะแบบสัมพัทธ์กับความยาวเฉลี่ยของกระดูก
			``1.0`` = ระยะเท่าความยาวเฉลี่ยของกระดูกสองท่อน
			ค่าน้อย = PV ชิดข้อพับ, ค่ามาก = PV ห่างออกไป
			ถูกละเว้นเมื่อกำหนด ``dist``
		dist (float, optional): ระยะห่างแบบสัมบูรณ์ (scene unit)
			หากระบุค่านี้ จะ override ``factor`` ทั้งหมด
			เหมาะกับกรณีที่ต้องการระยะเท่ากันเป๊ะทุกนิ้ว
		min_angle (float): มุมงอขั้นต่ำที่ยอมรับได้ (องศา วัดจากแนวตรง)
			ค่าต่ำกว่า ``2.0`` จะทำให้ normal ไวต่อ floating-point error
			หาก rigging guide บังคับงอ 5-10 องศาอยู่แล้ว ปรับขึ้นได้
		align (bool): ``True`` = จัด rotation ของ PV ให้ล็อกกับระนาบด้วย
			(แกน X ชี้ออกจากข้อพับ, แกน Z = normal ของระนาบ)
			``False`` = ย้ายเฉพาะตำแหน่ง คง rotation เดิมไว้
		flip (bool): ``True`` = กลับทิศ PV ไปอีกด้านของโซ่
			ใช้เมื่อ PV ไปอยู่ผิดฝั่ง เช่น ทะลุเข้าในฝ่ามือแทนที่จะออกนอก

	Returns:
		om.MVector: ตำแหน่ง world-space สุดท้ายที่ PV ถูกวางไว้
			นำไปใช้ต่อได้ เช่น สร้าง annotation หรือ curve guide

	Raises:
		PoleVectorError: เมื่อเกิดกรณีใดกรณีหนึ่งต่อไปนี้
			* ไม่พบ object ตามชื่อที่ระบุ
			* joint ทับตำแหน่งกันจนหาทิศกระดูกไม่ได้
			* โซ่ตรงเกินไป (มุมงอน้อยกว่า ``min_angle``)
			  ซึ่งหมายความว่า rigger ยังไม่ได้งอ joint กลาง

	Example:
		การใช้งานพื้นฐาน::

			place_pv_on_plane(
				'thumb02LFT_tmpJnt', 'thumb03LFT_tmpJnt',
				'thumb04LFT_tmpJnt', 'thumbPovLFT_tmpJnt',
				factor=1.0)

		กรณี PV ไปอยู่ผิดด้าน และต้องการระยะตายตัว::

			place_pv_on_plane(
				'thumb02RGT_tmpJnt', 'thumb03RGT_tmpJnt',
				'thumb04RGT_tmpJnt', 'thumbPovRGT_tmpJnt',
				dist=2.5, flip=True)

		พร้อมแจ้งเตือน user เมื่อโซ่ยังไม่งอ::

			try:
				place_pv_on_plane(a, b, c, pv)
			except PoleVectorError as err:
				mc.confirmDialog(title='Pole Vector Error',
								 message=str(err),
								 button=['OK'], icon='critical')

	Note:
		ควรเรียกฟังก์ชันนี้ตอนที่โซ่อยู่ใน bind pose หรือท่าที่ตั้งใจ
		ใช้เป็นระนาบอ้างอิงเท่านั้น หากเรียกตอน joint ถูกหมุนชั่วคราว
		PV จะถูกวางตามระนาบของท่านั้นแทน
	"""
	p1, p2, p3 = _pos(p1_name), _pos(p2_name), _pos(p3_name)

	v1 = p2 - p1        # กระดูกท่อนแรก
	v2 = p3 - p2        # กระดูกท่อนที่สอง
	chain = p3 - p1     # แกนหลักของโซ่

	# --- ตรวจความถูกต้องของโซ่ก่อนคำนวณ ---
	if v1.length() < EPS or v2.length() < EPS:
		raise PoleVectorError(
			"Joint ทับกัน: ตรวจ '%s', '%s', '%s'" % (p1_name, p2_name, p3_name))

	cos_a = max(-1.0, min(1.0, v1.normal() * v2.normal()))
	bend = 180.0 - math.degrees(math.acos(cos_a))

	if bend > (180.0 - min_angle):
		raise PoleVectorError(
			"'%s' ไม่ได้งอ (มุมปัจจุบัน %.3f องศา, ต้องการอย่างน้อย %.1f องศาจากแนวตรง)\n"
			"   -> กรุณางอ joint กลางในระนาบที่ต้องการก่อนรันสคริปต์ "
			"เพราะระนาบ Pole Vector คำนวณจากทิศทางการงอเท่านั้น"
			% (p2_name, bend, min_angle))

	# --- หาทิศ PV: ตั้งฉากกับแกนโซ่ และอยู่ในระนาบการงอ ---
	normal = (v1 ^ v2).normal()
	pv_dir = (normal ^ chain).normal()

	# กลับทิศให้ชี้ออกด้านนอกของข้อพับเสมอ (เทียบกับ bulge ของ joint กลาง)
	proj = p1 + chain * (((p2 - p1) * chain) / (chain * chain))
	bulge = p2 - proj
	if (pv_dir * bulge) < 0:
		pv_dir *= -1.0
	if flip:
		pv_dir *= -1.0

	# --- ระยะแบบสัมพัทธ์กับความยาวโซ่ ---
	if dist is None:
		dist = (v1.length() + v2.length()) * 0.5 * factor

	target = p2 + pv_dir * dist
	mc.xform(pv_name, ws=True, t=(target.x, target.y, target.z))

	# --- จัด rotation ให้ล็อกกับระนาบ ---
	if align:
		x, z = pv_dir, normal
		y = (z ^ x).normal()
		mc.xform(pv_name, ws=True, m=[x.x, x.y, x.z, 0,
									  y.x, y.y, y.z, 0,
									  z.x, z.y, z.z, 0,
									  target.x, target.y, target.z, 1])

	print("# %s -> OK | bend %.2f deg | dist %.3f" % (pv_name, bend, dist))
	return target