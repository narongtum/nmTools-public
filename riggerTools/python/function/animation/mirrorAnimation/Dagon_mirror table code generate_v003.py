import re
import os
import maya.cmds as mc
from function.animation.studiolibrary2023.src import mutils


# ----------------------------------------------------------------
# Helper : join multiple regex safely
# ----------------------------------------------------------------
def join_regex(patterns):
	"""
	Combine a list of regex patterns into one alternation group.
	e.g. ["L_*", "*LFT*"] -> "(?:L_.*|.*LFT.*)"
	"""
	if not patterns:
		return ""
	if len(patterns) == 1:
		return patterns[0]
	return "(?:" + "|".join(patterns) + ")"


# ----------------------------------------------------------------
# Patch function: allow full regex (disable fnmatch.translate)
# ----------------------------------------------------------------
def regexFromString_override(pattern):
	"""
	Custom override for Studio Library utils.regexFromString
	that allows full native Python regex.
	Falls back to fnmatch if invalid regex.
	"""
	import fnmatch
	if not pattern:
		return None
	try:
		# Compile directly (real regex)
		return re.compile(pattern)
	except re.error:
		# Fallback to fnmatch if pattern invalid
		return re.compile(fnmatch.translate(pattern))


# ----------------------------------------------------------------
# Create mirror table from selection (multi-regex aware)
# ----------------------------------------------------------------
def create_mirror_table_from_selection(left_patterns,
									   right_patterns,
									   mirror_plane="YZ",
									   save_path=None,
									   ignore_case=False,
									   verbose=True):
	"""
	Build and save a Studio Library MirrorTable from the current Maya selection
	using multiple regex patterns (prefix/suffix).
	Automatically patches mutils to support real regex syntax.
	"""
	#... Validate selection
	sel = mc.ls(selection=True, type="transform") or []
	if not sel:
		raise RuntimeError("Please select controllers before running create_mirror_table_from_selection().")

	# 2️⃣ Join regex pattern lists
	left_regex = join_regex(left_patterns)
	right_regex = join_regex(right_patterns)

	if verbose:
		print("\n# Create MirrorTable From Selection (regex supported)")
		print(" Mirror plane :", mirror_plane)
		print(" Left regex   :", left_regex)
		print(" Right regex  :", right_regex)
		print(" Object count :", len(sel))

	# 3️⃣ Patch utils.regexFromString temporarily
	import inspect
	utils_module = mutils.utils
	if not hasattr(utils_module, "_regexFromString_original"):
		utils_module._regexFromString_original = utils_module.regexFromString
	utils_module.regexFromString = regexFromString_override

	# 4️⃣ Create mirror table
	mt = mutils.MirrorTable.fromObjects(
		sel,
		leftSide=left_regex,
		rightSide=right_regex,
		mirrorPlane=mirror_plane
	)

	# 5️⃣ Restore original function to avoid side effects
	utils_module.regexFromString = utils_module._regexFromString_original

	# 6️⃣ Save table if path given
	if save_path:
		folder = os.path.dirname(save_path)
		if not os.path.exists(folder):
			os.makedirs(folder)
		mt.save(save_path)
		if verbose:
			print(" Saved mirror table to:", save_path)

	return mt
