from pxr import Usd, UsdGeom, UsdSkel,Sdf,Kind,Vt, Tf,Gf
# stage setting
stage = Usd.Stage.CreateNew("practiceSkel.usda")
stage.SetDefaultPrim(stage.DefinePrim('/Model', 'SkelRoot'))
stage.SetStartTimeCode(1)
# 第十帧结束
stage.SetEndTimeCode(10)
stage.SetMetadata('metersPerUnit', 0.01)
stage.SetMetadata('upAxis', 'Y')
# root      
# skeleton
# animation
skelRootPath = Sdf.Path("/Model")
skel_root = UsdSkel.Root.Define(stage, skelRootPath)
Usd.ModelAPI(skel_root).SetKind(Kind.Tokens.component)

if not skel_root:
    Tf.Warn("Failed defining a Skeleton at <%s>.", skelRootPath)
skelPath = skelRootPath.AppendChild("Skel")
skel = UsdSkel.Skeleton.Define(stage, skelPath)

jointPaths = ["Shoulder", "Shoulder/Elbow", "Shoulder/Elbow/Hand"]
topo = UsdSkel.Topology(jointPaths)
valid, reason = topo.Validate()
if not valid:
    Tf.Warn("Invalid topology: %s" % reason)
    
numJoints = len(jointPaths)
if numJoints:
    print("Joints number: %s" %numJoints)
    
jointTokens = Vt.TokenArray(jointPaths)
skel.GetJointsAttr().Set(jointTokens)

bindTransforms = [
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1), 
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 2, 1), 
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 2, 1)   
]
skel.GetBindTransformsAttr().Set(bindTransforms)
restTransforms = [
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1), 
    Gf.Matrix4d(1, 0, 0, 0,     
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 2, 1), 
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 4, 1)   
]
if restTransforms and len(restTransforms) == numJoints:
    skel.GetRestTransformsAttr().Set(restTransforms)
#joint
joints = skel.GetJointsAttr().Get()
topology = UsdSkel.Topology(skel.GetJointsAttr().Get())
# print(topology.GetNumJoints())
# print(topology.IsRoot(0))
# print(joints[0])
# parentIndex = topology.GetParent(1)
# print(joints[parentIndex])

animPath = skelPath.AppendChild("Anim")
skelAnim = UsdSkel.Animation.Define(stage, animPath)
animJoints = ["Shoulder/Elbow"]
skelAnim.CreateJointsAttr(animJoints)
skelAnim.CreateTranslationsAttr().Set([(0, 0, 2)])
animRot = skelAnim.CreateRotationsAttr()
animRot.Set([Gf.Quatf(1, 0, 0, 0)], Usd.TimeCode(1))
animRot.Set([Gf.Quatf(0.7071, 0.7071, 0, 0)], Usd.TimeCode(10))
skelAnim.CreateScalesAttr().Set([(1,1,1)])
# skel.GetPrim().CreateRelationship("skel:animationSource").AddTarget(anim.GetPath())

skeleton_skel_binding = UsdSkel.BindingAPI.Apply(skel.GetPrim())
skeleton_root_binding = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())
skeleton_skel_binding.CreateAnimationSourceRel().SetTargets([skelAnim.GetPrim().GetPath()])

# # 定义Mesh
mesh = UsdGeom.Mesh.Define(stage, "/Model/Arm")
geometry_data = {
        'points': [(0.5, -0.5, 4), (-0.5, -0.5, 4), (0.5, 0.5, 4), (-0.5, 0.5, 4),
        (-0.5, -0.5, 0), (0.5, -0.5, 0), (-0.5, 0.5, 0), (0.5, 0.5, 0),
        (-0.5, 0.5, 2), (0.5, 0.5, 2), (0.5, -0.5, 2), (-0.5, -0.5, 2)],
        'face_vertex_counts': [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        'face_vertex_indices': [2, 3, 1, 0,
            6, 7, 5, 4,
            8, 9, 7, 6,
            3, 2, 9, 8,
            10, 11, 4, 5,
            0, 1, 11, 10,
            7, 9, 10, 5,
            9, 2, 0, 10,
            3, 8, 11, 1,
            8, 6, 4, 11]}
# Set mesh attributes
mesh.GetPointsAttr().Set(geometry_data['points'])
mesh.GetFaceVertexCountsAttr().Set(geometry_data['face_vertex_counts'])
mesh.GetFaceVertexIndicesAttr().Set(geometry_data['face_vertex_indices'])

# 设置Mesh与Skeleton的绑定
skinBinding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())
#skinBinding.CreateAnimationSourceRel().AddTarget(skelAnim.GetPath())
skinBinding.CreateSkeletonRel().SetTargets([skel.GetPath()])
joint_indices_attr = skinBinding.CreateJointIndicesPrimvar(False, 1).Set([2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 1, 1])
joint_weights_attr = skinBinding.CreateJointWeightsPrimvar(False,1).Set([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
geom_bindTransform_attr = skinBinding.CreateGeomBindTransformAttr(Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))

# 保存Stage
stage.Save()
