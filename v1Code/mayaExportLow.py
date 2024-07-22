from pxr import Usd, UsdGeom, UsdSkel, Gf

# 创建一个新的USD文件
stage = Usd.Stage.CreateNew("model.usda")

# 创建SkelRoot，这是Skeleton和Animation的根节点
skelRoot = UsdSkel.Root.Define(stage, "/Model")

# 创建Skeleton
skeleton = UsdSkel.Skeleton.Define(stage, "/Model/Skel")
skeleton.CreateJointsAttr(["Shoulder", "Shoulder/Elbow", "Shoulder/Elbow/Hand"])
skeleton.CreateBindTransformsAttr([
    Gf.Matrix4d(1.0),  # 默认矩阵，示例中未具体定义
    Gf.Matrix4d(1.0),
    Gf.Matrix4d(1.0)
])
skeleton.CreateRestTransformsAttr([
    Gf.Matrix4d(1.0),
    Gf.Matrix4d(1.0),
    Gf.Matrix4d(1.0)
])

# 创建Animation
animation = UsdSkel.Animation.Define(stage, "/Model/Skel/Anim")
animation.CreateJointsAttr(["Shoulder/Elbow"])
animation.CreateRotationsAttr().Set(time=1, value=[
    Gf.Quatf(1, 0, 0, 0),  # 默认无旋转
])
animation.CreateRotationsAttr().Set(time=10, value=[
    Gf.Quatf(0.7071, 0.7071, 0, 0)  # 90度旋转
])
animation.CreateTranslationsAttr().Set([
    Gf.Vec3f(0, 0, 2)  # 位置变化
])

# 将动画关联到Skeleton
rel = skeleton.GetPrim().CreateRelationship("skel:animationSource")
rel.AddTarget(animation.GetPath())

# 创建一个Mesh并将其绑定到Skeleton
mesh = UsdGeom.Mesh.Define(stage, "/Model/Arm")
mesh.CreatePointsAttr([
    (0.5, -0.5, 4), (-0.5, -0.5, 4), (0.5, 0.5, 4), (-0.5, 0.5, 4),
    (-0.5, -0.5, 0), (0.5, -0.5, 0), (-0.5, 0.5, 0), (0.5, 0.5, 0),
    (-0.5, 0.5, 2), (0.5, 0.5, 2), (0.5, -0.5, 2), (-0.5, -0.5, 2)
])

# 保存文件
stage.GetRootLayer().Save()

print("USD file created and saved as 'model.usda'")
