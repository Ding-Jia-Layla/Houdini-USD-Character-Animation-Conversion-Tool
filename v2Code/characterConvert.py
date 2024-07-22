from pxr import Usd, UsdGeom, Gf,Sdf,UsdSkel
stage = Usd.Stage.CreateNew("character.usda")
stage.SetMetadata('comment', 'Create a character')
#binding
skel_root = UsdSkel.Root.Define(stage,'/')
# bind the skeleton
binding_api = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())
if binding_api:
    print("SkelBindingAPI applied successfully.")
# { }


# xform
# scope 
# variantSet for rig
    # facebone
    # high: rig hair...
    # reduced
