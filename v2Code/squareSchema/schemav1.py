from pxr import Usd, UsdGeom, UsdSkel, Gf, Vt

# 创建一个新的USD Stage
stage = Usd.Stage.CreateNew('example.usda')

# 创建一个SkelRoot，并在其中创建一个Skeleton
skelRoot = UsdSkel.Root.Define(stage, '/Model')
skeleton = UsdSkel.Skeleton.Define(stage, '/Model/Skeleton')

# 定义关节名称和拓扑
joints = ["root", "spine", "chest", "head"]
skeleton.GetJointsAttr().Set(joints)

# 定义绑定变换
bindTransforms = [
    Gf.Matrix4d(1.0),  # root
    Gf.Matrix4d(1.0).SetTranslate(Gf.Vec3d(0, 1, 0)),  # spine
    Gf.Matrix4d(1.0).SetTranslate(Gf.Vec3d(0, 2, 0)),  # chest
    Gf.Matrix4d(1.0).SetTranslate(Gf.Vec3d(0, 3, 0))   # head
]
skeleton.CreateBindTransformsAttr().Set(bindTransforms)

# 创建一个网格
mesh = UsdGeom.Mesh.Define(stage, '/Model/CharacterMesh')

# 定义一些简单的顶点和面
mesh.GetPointsAttr().Set([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 1, 0), Gf.Vec3f(0, 1, 0)])
mesh.GetFaceVertexCountsAttr().Set([4])
mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2, 3])

# 使用SkelBindingAPI绑定网格到骨架
bindingAPI = UsdSkel.BindingAPI.Apply(mesh.GetPrim())

# 设置骨架关系
bindingAPI.CreateSkeletonRel().SetTargets([skeleton.GetPath()])

# 设置关节索引和权重
jointIndices = Vt.IntArray([0, 1, 2, 3])
jointWeights = Vt.FloatArray([1.0, 1.0, 1.0, 1.0])
bindingAPI.CreateJointIndicesPrimvar(False, 1).Set(jointIndices)
bindingAPI.CreateJointWeightsPrimvar(False, 1).Set(jointWeights)

# 设置几何体绑定变换
geomBindTransform = Gf.Matrix4d(1.0)  # 例如：单位矩阵
bindingAPI.CreateGeomBindTransformAttr().Set(geomBindTransform)

# 保存Stage
stage.GetRootLayer().Save()
