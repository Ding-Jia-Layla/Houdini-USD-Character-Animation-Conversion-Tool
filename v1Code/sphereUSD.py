from pxr import Usd, UsdGeom

# Create a temporary stage in memory
stage = Usd.Stage.CreateInMemory("SampleLayer.usda")

# Create a transform and add a sphere as mesh data
xformPrim = UsdGeom.Xform.Define(stage, "/MySphere")

# Set a translation
UsdGeom.XformCommonAPI(xformPrim).SetTranslate((7, 8, 9))

spherePrim = UsdGeom.Sphere.Define(stage, "/MySphere/MeshData")

# Get the sphere as a generic prim
sphere = stage.GetPrimAtPath("/MySphere/MeshData")

# Get the extent and radius parameters for the prim
radiusAttr = sphere.GetAttribute("radius")
extentAttr = sphere.GetAttribute("extent")

# Access the sphere schema to set the color
colorAttr = spherePrim.GetDisplayColorAttr()

# Set the radius to 2
radiusAttr.Set(2)

# Expand the extents to match the new radius
extentAttr.Set(extentAttr.Get() * 2)

# Make the sphere blue
colorAttr.Set([(0.0, 0.0, 1.0)])

# Print out the stage
print(stage.GetRootLayer().ExportToString())

# Save the resulting layer
stage.Export(path + "SampleLayer.usda", addSourceFileComment=False)