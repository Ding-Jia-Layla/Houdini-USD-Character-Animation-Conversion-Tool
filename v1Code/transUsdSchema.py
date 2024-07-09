from pxr import Usd, UsdGeom, Gf,Sdf
# create a new stage
stage = Usd.Stage.CreateNew("TestTransform.usda")
# Add a comment to the stage
stage.SetMetadata('comment', 'Create a locator')

# set the start and end time codes (basically the frame range) but float
frames=10 
stage.SetStartTimeCode(0)
stage.SetEndTimeCode(frames)

# Create a new prim at the root called /Loc1 and set its type to Locator
# This is what your would call your things when you make them.
locator = stage.DefinePrim('/Loc1', 'Locator')
# I'm going to add some attributes to my prim scale, name and position
locator.CreateAttribute("scale",Sdf.ValueTypeNames.Float ).Set(2.0)
locator.CreateAttribute("name",Sdf.ValueTypeNames.String ).Set("hello")
locator.CreateAttribute("position",Sdf.ValueTypeNames.Point3d ).Set((0,0,0))

# Then set them at various times
offset=0.1
for t in range(0,frames) :
    offset += 0.1 
    pos = locator.GetAttribute('position')
    pos.Set(time=t, value=(offset,0,0))
    scale = locator.GetAttribute('scale')
    scale.Set(time=t, value=scale.Get(time=t-1)*1.1)

# Save the file (look at it in the text editor)
stage.Save()
