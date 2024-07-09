from pxr import Usd, UsdGeom, Gf,Sdf

# Open the stage we created in writeLocator.py
stage = Usd.Stage.Open('TestTransform.usda')

# Get a reference to the root prim
prim_ref = stage.GetPrimAtPath('/')
# get start and end (convert to int for looping ease)
start_frame=int(stage.GetStartTimeCode())
end_frame=int(stage.GetEndTimeCode())

for frame in range(start_frame,end_frame+1):
    # If the print is a Locator process and print the values
    for prim in prim_ref.GetChildren():
        if prim.GetTypeName() == 'Locator':
            p=prim.GetAttribute('position').Get(time=frame)
            s=prim.GetAttribute('scale').Get(time=frame)
            print(f"{frame}  {prim.GetPath()} pos={p} scale={s}")