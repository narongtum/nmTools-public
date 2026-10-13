import maya.cmds as mc

class FlipRotationAxisToolUI:
	def __init__(self):
		self.window_name = "nmFlipRotAxisUI"
		# Define patterns as a dictionary for easy maintenance
		self.patterns = {
			'ax1: [-1, 1, 1]': [-1, 1, 1],
			'ax2: [1, -1, 1]': [1, -1, 1],
			'ax3: [1, 1, -1]': [1, 1, -1],
			'ax4: [-1, -1, -1]': [-1, -1, -1],
			'ax5: [-1, -1, 1]': [-1, -1, 1],
			'ax6: [1, -1, -1]': [1, -1, -1],
			'ax7: [-1, 1, -1]': [-1, 1, -1]
		}
		self.build_ui()

	def build_ui(self):
		# Check if window exists and delete it
		if mc.window(self.window_name, exists=True):
			mc.deleteUI(self.window_name)

		# Create tool window
		self.window = mc.window(
			self.window_name, 
			title="Flip Rotation Axis Tool", 
			widthHeight=(300, 220), # Increased height to accommodate more items
			sizeable=False
		)
		
		# Layout Setup
		mc.columnLayout(adjustableColumn=True, rowSpacing=10, columnAttach=('both', 15))
		
		mc.separator(height=10, style="none")
		mc.text(label="Select Rotation Flip Pattern:", align="center", font="boldLabelFont")

		# Create Dropdown (optionMenu)
		self.axis_dropdown = mc.optionMenu(label='Rot Axis Set')
		
		# Automatically generate menu items from patterns dictionary keys
		# Use sorted keys to keep UI consistent (ax1, ax2, ...)
		for label in sorted(self.patterns.keys()):
			mc.menuItem(label=label)

		mc.separator(height=5)

		# Apply Button
		mc.button(
			label="APPLY ROTATION FLIP", 
			height=40, 
			backgroundColor=[0.2, 0.3, 0.4], 
			command=self.execute_flip
		)

		mc.showWindow(self.window)

	def execute_flip(self, *args):
		"""
		Main logic for multiplying rotation values.
		Targets rotateX, rotateY, rotateZ specifically.
		"""
		# 1. Get selection
		selection = mc.ls(selection=True, type='transform')
		if not selection:
			mc.warning("Please select at least one object (transform node).")
			return

		# 2. Query selected pattern from UI
		selected_text = mc.optionMenu(self.axis_dropdown, query=True, value=True)
		multiplier = self.patterns.get(selected_text)

		if not multiplier:
			mc.error("Selected pattern not found in data dictionary.")
			return

		# 3. Execution with Undo Chunk
		mc.undoInfo(openChunk=True)
		try:
			for obj in selection:
				# Get current rotation values
				rx = mc.getAttr(f"{obj}.rotateX")
				ry = mc.getAttr(f"{obj}.rotateY")
				rz = mc.getAttr(f"{obj}.rotateZ")

				# Apply multiplier (Flip logic)
				mc.setAttr(f"{obj}.rotateX", rx * multiplier[0])
				mc.setAttr(f"{obj}.rotateY", ry * multiplier[1])
				mc.setAttr(f"{obj}.rotateZ", rz * multiplier[2])

			print(f"[Flip Tool] Applied {selected_text} to {len(selection)} objects.")
			
		except Exception as e:
			mc.error(f"Error during rotation flip: {e}")
			
		finally:
			mc.undoInfo(closeChunk=True)

# Run Tool
FlipRotationAxisToolUI()