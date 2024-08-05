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

def setup_skeleton(joints,bindTransforms,restTransforms,skel):
    
    topo = UsdSkel.Topology(Vt.TokenArray([joint.lstrip('/').replace(":", "_") for joint in joints]))
    valid, reason = topo.Validate()
    if not valid:
        Tf.Warn("Invalid topology: %s" % reason) 
    numJoints = len(joints)
    # if numJoints:
    #     print("Joints number: %s" %numJoints)
    jointTokens = Vt.TokenArray([joint.lstrip('/').replace(":", "_") for joint in joints])
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
    geom_bindTransform = root_bindTransform * root_restTransform.GetInverse()
    return joints, bindTransforms, restTransforms,geom_bindTransform, root_name,mesh_index,joints_relationship_dict

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
def export_skinning(geometry,skel,mesh,geom_bindTransform,joints_list):
    skinBinding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())
    skinBinding.CreateSkeletonRel().SetTargets([skel.GetPath()])
    skin_node_points = geometry.points()
    joint_indices =[]
    joint_weights =[]
    len_bone_capture = len(skin_node_points[0].attribValue('boneCapture'))//2
    # capt_joints
    # 这个获取到的对象是capt_name里的顺序
    # print(skin_node_points[3078].attribValue('boneCapture'))
    # if skin_node_points[0].attribValue('boneCapture_regn[0]'):
    #     print(skin_node_points[0].attribValue('boneCapture_regn[0]'))
    # else:
    #     print("no this attr")
    capt_names = geometry.stringListAttribValue('capt_names')
    for point in skin_node_points:
        if (point.attribValue('boneCapture')):
            bone_capture = point.attribValue('boneCapture')
            
            for i in range(0,len(bone_capture),2):
                index_capt = bone_capture[i]
                joint_name_capt = capt_names[int(index_capt)]
                joint_index = joints_list.index(joint_name_capt)
                joint_weight = bone_capture[i+1]
                if  index_capt == -1.0 and joint_weight == -1.0:
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

def export_skeleton(stage,fbx_skel_node,skel):
    # structure of skeleton -- get
    # joints, bindTransforms, restTransforms,geom_bindTransform, root_name
    joints, bindTransforms, restTransforms,geom_bindTransform, root_name,mesh_index,joints_relationship_dict= get_skeleton_data(fbx_skel_node)
    # set up for the skeleton -- set
    setup_skeleton(joints,bindTransforms,restTransforms,skel)
    return joints,geom_bindTransform,mesh_index,joints_relationship_dict

def export_animation(stage,fbx_anim_node,skel,skelAnim,joints,mesh_index,joints_relationship_dict):
    joints_anim = Vt.TokenArray([joint.lstrip('/').replace(":", "_") for joint in joints])
    skelAnim.CreateJointsAttr().Set(joints_anim)
    anim_node = fbx_anim_node.geometry()
    start_frame = hou.playbar.playbackRange()[0]
    end_frame = hou.playbar.playbackRange()[1]
    points = anim_node.points()
    len_points = len(points) # 66
    len_joints = len(joints) # 65
    # ok
    joints_list = [joint.split('/')[-1] for joint in joints]
    # ok 'mixamorig:Hips': 0, 'mixamorig:Spine': 1, 'mixamorig:Spine1': 2...
    name_to_index = {name: idx for idx, name in enumerate(joints_list)}
    parent_indices = []
    # print(joints_relationship_dict)
    for joint in joints_list:
        # print(f"current joint : {joint}")
        parent_name = joints_relationship_dict[joint]  # 获取父关节名，如果不存在则返回None
        if parent_name =='':
            parent_indices.append(-1)
        else:
            parent_indices.append(name_to_index.get(parent_name, -1))
    # 每一帧
    for frame in range(int(start_frame), int(end_frame) + 1):
        hou.setFrame(frame)
        translations_frame = [Gf.Vec3f(0, 0, 0)] * len(joints)
        rotations_frame = [Gf.Quatf(1, 0, 0, 0)] * len(joints)
        scales_frame = [Gf.Vec3f(1, 1, 1)] * len(joints)
        matrix_joints_frame = [hou.Matrix4([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])] * len(joints)
        # 每一个关节
        joint_index =0 
        for index, point in enumerate(points):
            if index != mesh_index:
                transformation_matrix_original = point.floatListAttribValue('transform')
                translations = point.floatListAttribValue('P')
                joint_name = point.stringAttribValue('name')
                # 
                matrix4 = hou.Matrix4(
                [[transformation_matrix_original[0], transformation_matrix_original[1], transformation_matrix_original[2], 0],
                [transformation_matrix_original[3], transformation_matrix_original[4], transformation_matrix_original[5], 0],
                [transformation_matrix_original[6], transformation_matrix_original[7], transformation_matrix_original[8], 0],
                [translations[0], translations[1], translations[2], 1]])
                # 这里joint_index的顺序和本来的关节顺序不一致 似乎
                matrix_joints_frame[joint_index] = matrix4
                joint_index+=1
        # print(f"length of matrix: {len(matrix_joints_frame)} ") 65
        for index, global_matrix in enumerate(matrix_joints_frame):
            if parent_indices[index] == -1:
                local_matrix = global_matrix
            else:
                # print(index,parent_indices[index])
                parent_global_matrix = matrix_joints_frame[parent_indices[index]]
                local_matrix = global_matrix* parent_global_matrix.inverted() 
            quaternion = hou.Quaternion(local_matrix.extractRotationMatrix3())
            rotations_frame[index] = Gf.Quatf(quaternion[3], quaternion[0], quaternion[1], quaternion[2])
            scale =local_matrix.extractScales()
            scales_frame[index] = Gf.Vec3f(scale[0], scale[1], scale[2])
            translation = local_matrix.extractTranslates()
            translations_frame[index] = Gf.Vec3f(translation[0], translation[1], translation[2])
            # if frame == 1 and index == 0:
            #     print(f"rotation:{local_matrix.extractRotationMatrix3()}")
            #     print(f"Quatrotation:{Gf.Quatf(quaternion[3], quaternion[0], quaternion[1], quaternion[2])}")
            #     print(f"the frame 1 root matrix: {local_matrix}, translation: {translation}")
        skelAnim.CreateRotationsAttr().Set(Vt.QuatfArray(rotations_frame), Usd.TimeCode(frame))  
        skelAnim.CreateScalesAttr().Set(Vt.Vec3fArray(scales_frame),Usd.TimeCode(frame))
        skelAnim.CreateTranslationsAttr().Set(Vt.Vec3fArray(translations_frame),Usd.TimeCode(frame)) 
    return joints_list         
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
    joints, geom_bindTransform, mesh_index,joints_relationship_dict = export_skeleton(stage,fbx_skel_node,skel)
    mesh = export_geometry(stage, geometry)
    joints_list = export_animation(stage,fbx_anim_node,skel,skelAnim,joints, mesh_index,joints_relationship_dict)
    export_skinning(geometry,skel,mesh,geom_bindTransform,joints_list)
    stage.GetRootLayer().Save()

export_usd()