# Check and open Maya Command Port safely
import maya.cmds as mc

port_name = ":50007"

try:
	# Check if the command port is already open
	if not mc.commandPort(port_name, query=True):
		mc.commandPort(name=port_name)
		print(f"Maya Command Port {port_name} opened successfully.")
	else:
		print(f"Maya Command Port {port_name} is already open and ready.")
except Exception as err:
	mc.warning(f"Failed to configure command port: {err}")
