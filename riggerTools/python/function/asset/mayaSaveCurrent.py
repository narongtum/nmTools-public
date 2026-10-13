import maya.cmds as mc
import os

def mayaSaveCurrent():
    """
    Opens a 'Save As' dialog that defaults to the directory of the current Maya file.
    If the file has not been saved, it defaults to the Maya workspace root.
    Usage: mayaSaveCurrent()
    """
    # Get current scene path
    current_scene = mc.file(q=True, sn=True)
    
    if current_scene:
        # Use the directory of the current file
        starting_dir = os.path.dirname(current_scene)
    else:
        # Fallback to workspace root if scene is unsaved
        starting_dir = mc.workspace(q=True, rd=True)

    # Define file filters
    file_filter = "Maya ASCII (*.ma);;Maya Binary (*.mb)"
    
    # Open the Save As dialog
    result = mc.fileDialog2(
        fileFilter=file_filter,
        dialogStyle=2,
        startingDirectory=starting_dir,
        fileMode=0,
        okCaption="Save As",
        caption="Save As"
    )
    
    if result:
        file_path = result[0]
        
        # Determine file type based on extension
        if file_path.lower().endswith(".ma"):
            file_type = "mayaAscii"
        elif file_path.lower().endswith(".mb"):
            file_type = "mayaBinary"
        else:
            # Default to mayaAscii if no extension or unknown
            file_type = "mayaAscii"
            if not os.path.splitext(file_path)[1]:
                file_path += ".ma"

        try:
            # Rename and save the file
            mc.file(rename=file_path)
            mc.file(save=True, type=file_type)
            
            # Print status to script editor
            print("Maya file saved successfully: {}".format(file_path))
        except Exception as e:
            mc.warning("Failed to save file: {}".format(str(e)))
    else:
        print("Save As operation cancelled.")
