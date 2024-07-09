import maya.cmds as cmds


def __init__(self):
    self.character = None
    
def export_rigging(self,export_file_path,start_frame, end_frame):
    cmds.select(clear=True)
    cmds.select(["cylinder1", "joint1", "joint2", "joint3"])
    export_args = {
        "file": export_file_path,
        "selection": True,
        "exportSkels":"auto",
        "exportSkin":"auto",   
        "frameRange": (start_frame, end_frame),         
    }
    cmds.mayaUSDExport(**export_args)
def main():
    export_rigging("E:CAVE/final/SkelTest.usda", 1, 24)
if __name__ == "__main__":
    main()