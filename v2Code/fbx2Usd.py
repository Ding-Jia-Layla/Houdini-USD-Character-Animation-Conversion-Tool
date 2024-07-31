import random
from pxr import Usd, UsdGeom, UsdShade, Gf, Sdf,Kind, UsdSkel,Tf,Vt
import hou

node = hou.pwd()
geo = node.geometry()

def setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices):
    # 0->11
    mesh.GetPointsAttr().Set(points)
    mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
    mesh.GetFaceVertexIndicesAttr().Set(face_vertex_indices)

    if normals:
        mesh.CreateNormalsAttr().Set(normals)
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)

    # Set orientation and subdivisionScheme
    mesh.CreateOrientationAttr().Set(UsdGeom.Tokens.leftHanded)
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

        for vertex in vertices:
            face_vertex_indices.append(vertex.point().number())

            # Get Normals data
            if geometry.findVertexAttrib("N") is not None:
                normal = vertex.attribValue("N")
                normals.append(Gf.Vec3f(normal[0], normal[1], normal[2]))

    return points, normals, face_vertex_counts, face_vertex_indices
def export_skinning(stage,fbx_node,skel,mesh):
    skinBinding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())
    skinBinding.CreateSkeletonRel().SetTargets([skel.GetPath()])
    # geom_bindTransform_attr = skinBinding.CreateGeomBindTransformAttr()
    skin_node = fbx_node.node('fbx_skin_import1').geometry()
    skin_node_points = skin_node.points()
    joint_indices =[]
    joint_weights =[]
    for point in skin_node_points:
        if (point.attribValue('boneCapture')):
            bone_capture = point.attribValue('boneCapture')
            bone_capture_indices = bone_capture[0]
            bone_capture_weights = bone_capture[1]
            joint_indices.append(bone_capture_indices)
            joint_weights.append(bone_capture_weights)
            # jointIndices 数组与顶点的顺序一致，用于确定每个顶点所依赖的骨骼或关节。
        else:
            print("no boneCapture")  
    joint_indices_attr = skinBinding.CreateJointIndicesPrimvar(False, 1).Set(joint_indices)
    joint_weights_attr = skinBinding.CreateJointWeightsPrimvar(False, 1).Set(joint_weights)
    # TODO:primvars:skel:geomBindTransform
    child_nodes = fbx_node.children()
    output_sop_nodes = [node for node in child_nodes if node.type().name() == 'output']
    capture_pose = output_sop_nodes[1]
    capture_pose_points = capture_pose.geometry().points()
    
    
    for point in capture_pose_points:
        if (point.attribValue('transform')):
            geomBindTransform_list = point.attribValue('transform')
    print(geomBindTransform_list)
def stage_setting(stage):
    stage.SetDefaultPrim(stage.DefinePrim('/Model', 'Xform'))
    stage.SetStartTimeCode(1)    
    #stage.SetDefaultPrim(stage.DefinePrim('/Model', 'SkelRoot'))
    stage.SetMetadata('metersPerUnit', 1)
    stage.SetMetadata('upAxis', 'Y')    
    skelRootPath = Sdf.Path("/Model")
    root = UsdGeom.Xform.Define(stage, skelRootPath)
    Usd.ModelAPI(root).SetKind(Kind.Tokens.component)
    skelPath = skelRootPath.AppendChild("Skel")
    return stage,skelPath
def export_geometry(stage, geometry, input_node_name):
    # Get Geometry data
    points, normals, face_vertex_counts, face_vertex_indices = get_geometry_data(geometry)
    mesh = UsdGeom.Mesh.Define(stage, f'/Model/Mesh')
    setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices)
    return mesh
def get_skeleton_data(fbx_node):
    joints = []
    bindTransforms = []
    restTransforms = [] 
    capt_parents = fbx_node.node('fbx_skin_import1').geometry().intListAttribValue('capt_parents')
    capt_names = fbx_node.node('fbx_skin_import1').geometry().stringListAttribValue('capt_names')
    capt_xforms_list =  fbx_node.node('fbx_skin_import1').geometry().attribValue('capt_xforms')
    capt_xforms = [tuple(capt_xforms_list[i:i+16]) for i in range(0,len(capt_xforms_list),16)]
    for index, value in enumerate(capt_parents):
        if value == -1:
            root_index = index
    root_name = capt_names[root_index]
    capt_dict={}
    for index, name in enumerate(capt_names):
        parent_index = capt_parents[index]
        if parent_index == -1:
            parent_name = None
        else:
            parent_name = capt_names[parent_index]
        capt_dict[name] = parent_name
    joints_paths={}
    for joint in capt_dict:
        current = joint
        path=[]
        while current:
            path.append(current)
            current = capt_dict[current]
        joints_paths[joint]='/'.join(reversed(path))
    joints = list(joints_paths.values())

    # bind pose -- capt_xforms 
    bindTransforms = [Gf.Matrix4d(*capt_xform) for capt_xform in capt_xforms]
    # get the transform matrix: {0,0,0}*capt_xforms
    bind_transform_dict={}
    rest_transform_dict={}
    for index, value in enumerate(bindTransforms):
        bind_transform_dict[capt_names[index]] = value
    # resttransform<matrix4d>: compute the local space transform 每一个关节骨骼相对于父节点的矩阵 子-父
    # rest should be local, bind should be world space
    for index, value in enumerate(joints):
        parts = value.split('/')
        if(len(parts)==1):
            rest_transform_dict[root_name] = bind_transform_dict[root_name]
        else:
            child = parts[-1]
            parent = parts[-2]
            rest_transform_dict[child] = bind_transform_dict[child] -  bind_transform_dict[parent]
    restTransforms = list(rest_transform_dict.values())

    return joints, bindTransforms, restTransforms
def export_skeleton(stage,fbx_node,skel):
    # structure of skeleton -- get
    joints, bindTransforms, restTransforms= get_skeleton_data(fbx_node)
    # set up for the skeleton -- set
    setup_skeleton(joints,bindTransforms,restTransforms,skel)
    #return skeleton
    return joints
def setup_skeleton(joints,bindTransforms,restTransforms,skel):
    topo = UsdSkel.Topology(joints)
    valid, reason = topo.Validate()
    if not valid:
        Tf.Warn("Invalid topology: %s" % reason) 
    numJoints = len(joints)
    # if numJoints:
    #     print("Joints number: %s" %numJoints)
    jointTokens = Vt.TokenArray(joints)
    skel.GetJointsAttr().Set(jointTokens)
    topology = UsdSkel.Topology(skel.GetJointsAttr().Get()) 
    #bindTransform world space
    skel.GetBindTransformsAttr().Set(bindTransforms)
    # restTransforms 
    if restTransforms and len(restTransforms) == numJoints:
        skel.GetRestTransformsAttr().Set(restTransforms)

def export_animation(stage,fbx_node,skel,skelAnim,joints):
    skelAnim.CreateJointsAttr().Set(joints)
    anim_node = fbx_node.node('fbxanimimport1').geometry()
    # p[x],p[y],p[z] = V = M·V'= T_reset*R(theta)*T_2original
    # TODO: just get the index-3 joint value
    animRot = skelAnim.CreateRotationsAttr()
    start_frame = hou.playbar.playbackRange()[0]
    end_frame = hou.playbar.playbackRange()[1]
    for frame in range(int(start_frame), int(end_frame) + 1):
        hou.setFrame(frame)
        transformation_matrix_original = anim_node.point(3).floatListAttribValue('transform')
        transformation_matrix = hou.Matrix3(
                (transformation_matrix_original[0], transformation_matrix_original[3], transformation_matrix_original[6],
                transformation_matrix_original[1],transformation_matrix_original[4],transformation_matrix_original[7],
                transformation_matrix_original[2],transformation_matrix_original[5],transformation_matrix_original[8]))
        quaternion= hou.Quaternion(transformation_matrix)
        transforms = [quaternion[3],quaternion[0],quaternion[1],quaternion[2]]
        if frame == 1:
            translations = anim_node.point(3).floatListAttribValue('P')
            translations_vec = Gf.Vec3f(translations[0], translations[1], translations[2])
            translations_array = Vt.Vec3fArray(1, translations_vec)
            skelAnim.CreateTranslationsAttr().Set(translations_array)
        animRot.Set([Gf.Quatf(transforms[0],transforms[1],transforms[2],transforms[3])], Usd.TimeCode(frame))   
    skelAnim.CreateScalesAttr().Set([(1,1,1)])
def export_usd():
    usd_file_path = f'E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/houdini_export_{random.randint(1, 100)}.usda'
    _stage = Usd.Stage.CreateNew(usd_file_path)
    stage,skelPath= stage_setting(_stage)
    skel = UsdSkel.Skeleton.Define(stage, skelPath)
    animPath = skelPath.AppendChild("Anim")
    skelAnim = UsdSkel.Animation.Define(stage, animPath)
    # get the input node
    input_node_name = hou.node('/obj/mixamo_character_animated')
    # get the final node of the input node
    fbx_node = input_node_name.node('fbxcharacterimport2')
    geometry = fbx_node.geometry()
    mesh = export_geometry(stage, geometry, input_node_name)
    joints = export_skeleton(stage,fbx_node,skel)
    export_animation(stage,fbx_node,skel,skelAnim,joints)
    export_skinning(stage,fbx_node,skel,mesh)
    stage.GetRootLayer().Save()

export_usd()

