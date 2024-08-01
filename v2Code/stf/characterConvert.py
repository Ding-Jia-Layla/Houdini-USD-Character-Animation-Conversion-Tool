from pxr import Usd, UsdGeom, Gf,Sdf,UsdSkel
# stage
stage = Usd.Stage.CreateNew("character.usda")
stage.SetDefaultPrim(stage.DefinePrim('/HumanFemale_Group', 'SkelRoot'))
stage.SetMetadata('upAxis', 'Z')

skel_root = UsdSkel.Root.Define(stage,'/HumanFemale_Group')
skeleton_root_binding = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())

if skeleton_root_binding:
    print("SkelBindingAPI applied successfully.")
stage.Save()


# xform
# scope 
# variantSet for rig
    # facebone
    # high: rig hair...
    # reduced
