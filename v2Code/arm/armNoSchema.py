from pxr import Usd, UsdGeom, UsdSkel, Sdf, Kind, Vt, Tf, Gf

# Stage setting
stage = Usd.Stage.CreateNew("noSchema.usda")
stage.SetDefaultPrim(stage.DefinePrim('/Model', 'SkelRoot'))
stage.SetStartTimeCode(1)
stage.SetEndTimeCode(10)
stage.SetMetadata('metersPerUnit', 0.01)
stage.SetMetadata('upAxis', 'Y')

# Root and Skeleton
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
    print("Joints number: %s" % numJoints)

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
                0, 0, 4, 1)   
]
skel.CreateBindTransformsAttr().Set(bindTransforms)
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

# Joint
joints = skel.GetJointsAttr().Get()
topology = UsdSkel.Topology(skel.GetJointsAttr().Get())

# Animation
animPath = skelPath.AppendChild("Anim")
skelAnim = UsdSkel.Animation.Define(stage, animPath)
animJoints = ["Shoulder", "Shoulder/Elbow", "Shoulder/Elbow/Hand"]
skelAnim.CreateJointsAttr().Set(animJoints)
skelAnim.CreateTranslationsAttr().Set([(0, 0, 2), (0, 0, 2), (0, 0, 4)])
animRot = skelAnim.CreateRotationsAttr()
animRot.Set([Gf.Quatf(1, 0, 0, 0), Gf.Quatf(1, 0, 0, 0), Gf.Quatf(1, 0, 0, 0)], Usd.TimeCode(1))
animRot.Set([Gf.Quatf(0.7071, 0.7071, 0, 0), Gf.Quatf(0.7071, 0.7071, 0, 0), Gf.Quatf(0.7071, 0.7071, 0, 0)], Usd.TimeCode(10))
skelAnim.CreateScalesAttr().Set([(1, 1, 1), (1, 1, 1), (1, 1, 1)])

# Bind Skeleton to Mesh
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

# Set joint indices and weights
jointIndices = Vt.IntArray([2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 1, 1])
jointWeights = Vt.FloatArray([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
primvarsAPI = UsdGeom.PrimvarsAPI(mesh.GetPrim())
jointIndicesPrimvar = primvarsAPI.CreatePrimvar('skel:jointIndices', Sdf.ValueTypeNames.IntArray)
jointIndicesPrimvar.Set(jointIndices)
jointIndicesPrimvar.SetInterpolation('vertex')

jointWeightsPrimvar = primvarsAPI.CreatePrimvar('skel:jointWeights', Sdf.ValueTypeNames.FloatArray)
jointWeightsPrimvar.Set(jointWeights)
jointWeightsPrimvar.SetInterpolation('vertex')
geomBindTransform = Gf.Matrix4d(1.0)  
mesh.GetPrim().CreateAttribute('skel:geomBindTransform', Sdf.ValueTypeNames.Matrix4d).Set(geomBindTransform)

# 保存Stage
stage.Save()
