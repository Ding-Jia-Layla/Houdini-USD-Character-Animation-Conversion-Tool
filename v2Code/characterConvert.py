from pxr import Usd, UsdGeom, Gf,Sdf,UsdSkel
stage = Usd.Stage.CreateNew("character.usda")
stage.SetMetadata('comment', 'Create a character')

