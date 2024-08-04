import random
from pxr import Usd, UsdGeom, UsdShade, Gf, Sdf,Kind, UsdSkel,Tf,Vt
import hou

node = hou.pwd()
geo = node.geometry()
def stage_setting(stage):
    stage.SetDefaultPrim(stage.DefinePrim('/Model', 'SkelRoot'))
    stage.SetStartTimeCode(1)    
    stage.SetMetadata('metersPerUnit', 0.01)
    stage.SetEndTimeCode(10)
    stage.SetMetadata('upAxis', 'Y')    
    skelRootPath = Sdf.Path("/Model")
    skel_root = UsdSkel.Root.Define(stage, skelRootPath)
    Usd.ModelAPI(skel_root).SetKind(Kind.Tokens.component)
    skelPath = skelRootPath.AppendChild("Skel")
    return stage,skelPath,skel_root
def export_skeleton(stage,fbx_skel_node,skel):
    # structure of skeleton -- get
    # joints, bindTransforms, restTransforms,geom_bindTransform, root_name
    joints, bindTransforms, restTransforms,geom_bindTransform, root_name= get_skeleton_data(fbx_skel_node)
    # set up for the skeleton -- set
    setup_skeleton(joints,bindTransforms,restTransforms,skel)
    
def setup_skeleton(joints,bindTransforms,restTransforms,skel):
    topo = UsdSkel.Topology(Vt.TokenArray([joint.replace(":", "_")for joint in joints]))
    valid, reason = topo.Validate()
    if not valid:
        Tf.Warn("Invalid topology: %s" % reason) 
    numJoints = len(joints)
    # if numJoints:
    #     print("Joints number: %s" %numJoints)
    jointTokens = Vt.TokenArray([joint.replace(":", "_") for joint in joints])
    skel.GetJointsAttr().Set(jointTokens)
    topology = UsdSkel.Topology(skel.GetJointsAttr().Get())    
    # bindTransforms 
    # skel.GetRestTransformsAttr().Set(Vt.Matrix4dArray([rest_transforms_dict[joint.split('/')[-1]] for joint in joints]))
    skel.GetBindTransformsAttr().Set(bindTransforms)
    if restTransforms and len(restTransforms) == numJoints:
        skel.GetRestTransformsAttr().Set(restTransforms)
        
def get_skeleton_data(fbx_skel_node):
    joints = []
    bind_transform_dict = {}
    points_original = fbx_skel_node.geometry().points()
    # TODO:还是得找根节点： 找路径里最长的然后获取它的第一个就是根节点
    max_path_length = 0
    root_name = None
    mesh_index = None 
    joints_relationship_dict = {}
    for point_original in points_original:
        point_path = point_original.stringAttribValue('path')
        parts = point_path.split('/')
        if len(parts)> max_path_length:
            max_path_length = len(parts)
            root_name = parts[1]
    # print(joints_relationship_dict)  
    for index,point_original in enumerate(points_original):
        point_path = point_original.stringAttribValue('path')
        parts = point_path.split('/')
        if(len(parts)==2)and(parts[1]!=root_name):
            mesh_index = index
    for index,point_original in enumerate(points_original):
        point_path = point_original.stringAttribValue('path')
        parts = point_path.split('/')
        if index != mesh_index:
            current_name = parts[-1]
            parent_name = parts[-2]
            joints_relationship_dict[current_name] = parent_name
    # print(f"root_name is : {root_name}, mesh_index: {mesh_index}")
    for index, point in enumerate(points_original):
        if index != mesh_index:
            joints.append(point.stringAttribValue('path'))
            # joints_names：不是_而是：
            transformation_matrix_original = point.floatListAttribValue('transform')
            translations = point.floatListAttribValue('P')
            bindTransform =Gf.Matrix4d(
            transformation_matrix_original[0], transformation_matrix_original[1], transformation_matrix_original[2], 0,
            transformation_matrix_original[3], transformation_matrix_original[4], transformation_matrix_original[5], 0,
            transformation_matrix_original[6], transformation_matrix_original[7], transformation_matrix_original[8], 0,
            translations[0], translations[1], translations[2], 1)
            # print(f"point name: {point.stringAttribValue('name')}, matrix is :{bindTransform}")
            bind_transform_dict[point.stringAttribValue('name')] = bindTransform
    bindTransforms = list(bind_transform_dict.values())
    rest_transform_dict = {}
    for key in joints_relationship_dict:
        if key == root_name:
            rest_transform_dict[root_name] = bind_transform_dict[root_name]
        else: 
            M = bind_transform_dict[key] * bind_transform_dict[joints_relationship_dict[key]].GetInverse()
            rest_transform_dict[key] = M
    restTransforms = list(rest_transform_dict.values())
    root_bindTransform = bind_transform_dict[root_name]
    root_restTransform = rest_transform_dict[root_name]
    geom_bindTransform = root_bindTransform * root_restTransform
    # print(f"restTransformdict:{restTransforms_dict}")
    return joints, bindTransforms, restTransforms,geom_bindTransform, root_name

def setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices):
    # 0->11
    mesh.GetPointsAttr().Set(points)
    mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
    mesh.GetFaceVertexIndicesAttr().Set(face_vertex_indices)

    if normals:
        mesh.CreateNormalsAttr().Set(normals)
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)

    # Set orientation and subdivisionScheme
    mesh.CreateOrientationAttr().Set(UsdGeom.Tokens.rightHanded)
    mesh.CreateSubdivisionSchemeAttr().Set("none")
def get_geometry_data(geometry):
    #Get mesh geometry data including normals
    points = []  # List of point positions (point3f[] points)
    normals = []  # List of normals (normal3f[] normals)
    face_vertex_counts = []  # List of vertex count per face (int[] faceVertexCounts)
    face_vertex_indices = []  # List of vertex indices (int[] faceVertexIndices)

    # Collect points and normals
    for point in geometry.points():
        position = point.position()
        points.append(Gf.Vec3f(position[0], position[1], position[2]))
        
    # Collect face data
    for primitive in geometry.prims():
        vertices = primitive.vertices()
        face_vertex_counts.append(len(vertices))

        for vertex in reversed(vertices):
            face_vertex_indices.append(vertex.point().number())

            # Get Normals data
            if geometry.findVertexAttrib("N") is not None:
                normal = vertex.attribValue("N")
                normals.append(Gf.Vec3f(normal[0], normal[1], normal[2]))
    return points,normals,face_vertex_counts,face_vertex_indices

def export_geometry(stage, geometry):
    # Get Geometry data
    points, normals, face_vertex_counts, face_vertex_indices = get_geometry_data(geometry)
    mesh = UsdGeom.Mesh.Define(stage, f'/Model/Arm')
    setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices)
    return mesh

def export_usd():
    usd_file_path = f'E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/houdini_export_{random.randint(1, 100)}.usda'
    _stage = Usd.Stage.CreateNew(usd_file_path)
    stage,skelPath,skel_root= stage_setting(_stage)
    skel = UsdSkel.Skeleton.Define(stage, skelPath)
    skeleton_skel_binding = UsdSkel.BindingAPI.Apply(skel.GetPrim())
    skeleton_root_binding = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())
    animPath = skelPath.AppendChild("Anim")
    skelAnim = UsdSkel.Animation.Define(stage, animPath)
    skeleton_skel_binding.CreateAnimationSourceRel().SetTargets([skelAnim.GetPrim().GetPath()])
    # get the input node
    input_node_name = hou.node('/obj/mixamo_character_animated')
    # get the final node of the input node
    fbx_skel_node = input_node_name.node('fbxanimimport1')
    fbx_anim_node = input_node_name.node('fbxanimimport2')
    fbx_skin_node = input_node_name.node('fbxskinimport1')
    geometry = fbx_skin_node.geometry()
    export_skeleton(stage,fbx_skel_node,skel)
    mesh = export_geometry(stage, geometry)
    stage.GetRootLayer().Save()

export_usd()