from pxr import Usd, UsdGeom
# Root layer: e:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/arm_skel_export.usda
# Prim: /Model
# Prim: /Model/Skel
# Prim: /Model/Skel/Anim
# Prim type: SkelAnimation
# USD文件路径
usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/arm_skel_export.usda"

# 打开USD文件
stage = Usd.Stage.Open(usd_file_path)

# 获取stage的根层
root_layer = stage.GetRootLayer()
print(f"Root layer: {root_layer.identifier}")

# 列出所有的prim路径
for prim in stage.Traverse():
    print(f"Prim: {prim.GetPath()}")

# 获取特定的Prim
prim_path = "/Model/Skel/Anim"
prim = stage.GetPrimAtPath(prim_path)

# 打印Prim的类型
if prim:
    print(f"Prim type: {prim.GetTypeName()}")
else:
    print(f"Prim at path {prim_path} not found.")
