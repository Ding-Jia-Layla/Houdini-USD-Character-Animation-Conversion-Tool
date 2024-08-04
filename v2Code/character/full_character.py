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
def export_geometry(stage, geometry, input_node_name):
    # Get Geometry data
    points, normals, face_vertex_counts, face_vertex_indices = get_geometry_data(geometry)
    mesh = UsdGeom.Mesh.Define(stage, f'/Model/Arm')
    setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices)
    return mesh,face_vertex_indices

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
def build_joint_hierarchy(joints):
    hierarchy = {}
    for joint in joints:
        parts = joint.split('/')
        for i in range(len(parts)):
            parent = '/'.join(parts[:i])
            child = '/'.join(parts[:i+1])
            if parent not in hierarchy:
                hierarchy[parent] = []
            if child not in hierarchy[parent]:
                hierarchy[parent].append(child)
    hierarchy_list = list(hierarchy.values())
    # return type : list
    return sorted(joints, key=lambda joint: len(joint.split('/')))
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
    # 父子关系的字典。
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
    # print(joints)
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
            M = bind_transform_dict[child] * bind_transform_dict[parent].GetInverse()
            rest_transform_dict[child] = M
    restTransforms = list(rest_transform_dict.values())
    # print(f"restTransforms:{restTransforms}")
    root_bindTransform = bind_transform_dict[root_name]
    root_restTransform = rest_transform_dict[root_name]
    geom_bindTransform = root_bindTransform * root_restTransform
    return joints, bindTransforms, restTransforms,geom_bindTransform, root_name
def setup_skeleton(_joints, _bindTransforms, _restTransforms, root_name, skel):
    joints = build_joint_hierarchy(_joints)
    # print(f"head index is : {joints[15]}")
    bindTransforms = []
    restTransforms = []
    for joint in joints:
        joint_index =  _joints.index(joint)
        bindTransforms.append(_bindTransforms[joint_index])
        restTransforms.append(_restTransforms[joint_index])
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
    skel.GetBindTransformsAttr().Set(bindTransforms)
    # restTransforms 
    if restTransforms and len(restTransforms) == numJoints:
        skel.GetRestTransformsAttr().Set(restTransforms)
    return joints, bindTransforms, restTransforms,root_name

def export_skeleton(stage,fbx_node,skel):
    # structure of skeleton -- get
    _joints, bindTransforms, restTransforms,geom_bindTransform, root_name= get_skeleton_data(fbx_node)
    # set up for the skeleton -- set
    joints, bindTransforms, restTransforms,root_name = setup_skeleton(_joints, bindTransforms, restTransforms, root_name,skel)
    #return skeleton
    return joints,_joints,geom_bindTransform, root_name

def export_skinning(_joints,joints,fbx_node,skel,mesh,geom_bindTransform):
    skinBinding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())
    skinBinding.CreateSkeletonRel().SetTargets([skel.GetPath()])
    skin_node = fbx_node.node('fbx_skin_import1').geometry()
    skin_node_points = skin_node.points()
    joint_indices =[]
    joint_weights =[]
    len_bone_capture = len(skin_node_points[0].attribValue('boneCapture'))//2
    head_original_point = skin_node_points[0].attribValue('boneCapture')[0]
    # print(f"point 0's bone new index is : {joints.index(_joints[int(head_original_point)])}")
    for point in skin_node_points:
        if (point.attribValue('boneCapture')):
            bone_capture = point.attribValue('boneCapture')
            
            for i in range(0,len(bone_capture),2):
                joint_index = bone_capture[i]
                joint_weight = bone_capture[i+1]
                joint_index = joints.index(_joints[int(joint_index)])
                if joint_weight == -1.0 and joint_weight == -1.0:
                    joint_indices.append(0)
                    joint_weights.append(0.0)
                else:
                    joint_weights.append(joint_weight)
                    joint_indices.append(joint_index)
        else:
            print("no boneCapture")  
    joint_indices_attr = skinBinding.CreateJointIndicesPrimvar(False, len_bone_capture).Set(joint_indices)
    joint_weights_attr = skinBinding.CreateJointWeightsPrimvar(False, len_bone_capture).Set(joint_weights)
    geom_bindTransform_attr = skinBinding.CreateGeomBindTransformAttr(geom_bindTransform)
def export_animation(stage,fbx_node,skel,skelAnim,joints,_joints,root_name):
    # print(f"length of old: {len(_joints)}, length of new: {len(joints)}") 52 52
    joints_anim = Vt.TokenArray([joint for joint in joints])
    skelAnim.CreateJointsAttr().Set(joints_anim)
    anim_node = fbx_node.node('fbxanimimport1').geometry()
    # p[x],p[y],p[z] = V = M·V'= T_reset*R(theta)*T_2original
    start_frame = hou.playbar.playbackRange()[0]
    end_frame = hou.playbar.playbackRange()[1]
    points_original = anim_node.points()
    points = anim_node.points()
    mesh_index = None 
    for index,point_original in enumerate(points_original):
        point_path = point_original.stringAttribValue('path')
        parts = point_path.split('/')
        # print(f"parts:{parts}")
        if(len(parts)==2)and(parts[1]!=root_name):
            # print("find mesh")
            mesh_index = index
    for frame in range(int(start_frame), int(end_frame) + 1):
        hou.setFrame(frame)
        translations_frame = [Gf.Vec3f(0, 0, 0)] * len(joints)
        rotations_frame = [Gf.Quatf(1, 0, 0, 0)] * len(joints)
        scales_frame = [Gf.Vec3f(1, 1, 1)] * len(joints)
        # 这一帧的顺序是基于旧的关节点_points的顺序的 最后得到的是这一帧的这个旧关节位移信息
        
        for index, point in enumerate(points):
            if index != mesh_index:
                transformation_matrix_original = point.floatListAttribValue('transform')
                translations = point.floatListAttribValue('P')
                translations_vec = Gf.Vec3f(translations[0], translations[1], translations[2])
                # transform 9数据直接按行走
                matrix4 = hou.Matrix4(
                [transformation_matrix_original[0], transformation_matrix_original[1], transformation_matrix_original[2], translations[0],
                transformation_matrix_original[3], transformation_matrix_original[4], transformation_matrix_original[5], translations[1],
                transformation_matrix_original[6], transformation_matrix_original[7], transformation_matrix_original[8], translations[2],
                0, 0, 0, 1])
                # rotation
                transformation_matrix = hou.Matrix3(
                        (transformation_matrix_original[0], transformation_matrix_original[1], transformation_matrix_original[2],
                        transformation_matrix_original[3],transformation_matrix_original[4],transformation_matrix_original[5],
                        transformation_matrix_original[6],transformation_matrix_original[7],transformation_matrix_original[8]))
                quaternion= hou.Quaternion(transformation_matrix)
                # 应该是66关节
                # print(f"index of old: {index}, index of new: {joints.index(_joints[index])}") 
                # new_index = joints.index(_joints[index])
                # rotations_frame[new_index] = Gf.Quatf(quaternion[3], quaternion[0], quaternion[1], quaternion[2])
                # # scale
                # scale =matrix4.extractScales()
                # scales_frame[new_index] = Gf.Vec3f(scale[0], scale[1], scale[2])
                # translations_frame[new_index] = Gf.Vec3f(translations_vec[0], translations_vec[1], translations_vec[2])
            # print(f"length of rotations_frame: {len(rotations_frame)}, length of scales: {len(scales_frame)}, length of translation: {len(translations_frame)}")
        # skelAnim.CreateRotationsAttr().Set(Vt.QuatfArray(rotations_frame), Usd.TimeCode(frame))  
        # skelAnim.CreateScalesAttr().Set(Vt.Vec3fArray(scales_frame),Usd.TimeCode(frame))
        # skelAnim.CreateTranslationsAttr().Set(Vt.Vec3fArray(translations_frame),Usd.TimeCode(frame)) 
            
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
    fbx_node = input_node_name.node('fbxcharacterimport2')
    geometry = fbx_node.geometry()
    mesh,face_vertex_indices = export_geometry(stage, geometry, input_node_name)
    joints,_joints,geom_bindTransform,root_name = export_skeleton(stage,fbx_node,skel)
    export_skinning(_joints,joints,fbx_node,skel,mesh,geom_bindTransform)
    export_animation(stage,fbx_node,skel,skelAnim,joints,_joints,root_name)
    stage.GetRootLayer().Save()

export_usd()