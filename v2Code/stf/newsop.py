import hou

class MyImportSOP(hou.SopNode):
    def __init__(self, node):
        super(MyImportSOP, self).__init__(node)

    def cookMySop(self, context):
        geo = self.geometry()
        self.import_fbx(geo)

    def import_fbx(self, geo):
        fbx_file = self.evalParm("fbxfile")
        # Your FBX import logic here
        # Example: Load the FBX file and convert it to Houdini geometry
        # For demonstration, we'll just create a simple point
        pt = geo.createPoint()
        pt.setPosition((0, 0, 0))

# Register the SOP
def register_my_import():
    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "myimport")
    if node_type:
        return  # Already registered

    definition = hou.sopNodeTypeCategory().addNodeType(
        name="myimport",
        label="My Import",
        pythonModule=__name__
    )
    definition.addParmTemplate(hou.StringParmTemplate(name="fbxfile", label="FBX File", num_components=1))
    definition.setDefaultNodeColor(hou.Color((0.4, 0.8, 0.4)))  # Set a default color, optional

# Register the custom SOP node when this module is imported
register_my_import()
