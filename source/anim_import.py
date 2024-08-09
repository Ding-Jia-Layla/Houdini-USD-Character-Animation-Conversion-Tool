import hou
from pxr import Usd, UsdGeom, Gf, UsdSkel
def get_skel_anim_data(stage,skeleton,anim_prim):
    skel_bind_dict = {}
    positions_dict = {}
    point_positions_list = []
    point_transforms_list = []
    prim = stage.GetPrimAtPath(skeleton)
    joints_paths_list = prim.GetAttribute("joints").Get()
    joints_relationship_dict = {}
    joints_children = [joint.split('/')[-1] for joint in joints_paths_list]
    joints_parents=[]
    
    for index,joint in enumerate(joints_paths_list):
        if index == 0:
            joints_parents.append('None')
        else:
            joints_parents.append(joint.split('/')[-2])
            
    for index, joint in enumerate(joints_children):
        if index ==0:
            joints_relationship_dict[index] = -1
        else:
            joints_relationship_dict[index] = joints_children.index(joints_parents[index])   
    
    bind_transforms = prim.GetAttribute("bindTransforms").Get()
    
    for index, bind_transform in enumerate(bind_transforms):
        
        skel_bind_dict[joints_children[index]] = bind_transform
        
        positions_dict[joints_children[index]] = bind_transform.ExtractTranslation()
        
    for key, value in positions_dict.items():
        
        point_positions_list.append((value[0],value[1],value[2]))
        
    for key, value in skel_bind_dict.items():
        
        point_transform = []
        # print(f"value is : {value}")
        
        for i in range(0,3):
            point_transform.append(value.GetRow(i)[0])
            point_transform.append(value.GetRow(i)[1])
            point_transform.append(value.GetRow(i)[2])
            
        point_transforms_list.append(point_transform)
        # if key  == 'arm_End':
        #     print(point_transforms_list[0])
    # print(point_transforms_list)
    line_list = [(key, value) for key, value in list(joints_relationship_dict.items())][1:]
    poly_point_indices = tuple(line_list)  
    
    all_frames_matrice = get_anim_data(anim_prim)
    # return point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict
    return point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict,all_frames_matrice

def set_up_skel_anim(all_frames_matrix,point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict):
    
    geo = hou.pwd().geometry()
    # transform_attr_name = 'transform'
    name_attr_name = 'name'
    path_attr_name = 'path'
    transform_attr_name = 'transform'
    default_matrix4 = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]
    geo.addAttrib(hou.attribType.Point,name_attr_name,'jointName',transform_as_normal=False, create_local_variable=True)
    geo.addAttrib(hou.attribType.Point,path_attr_name,'parent/child',transform_as_normal=False, create_local_variable=True)
    transform_point_attr = geo.addAttrib(hou.attribType.Point,transform_attr_name,default_matrix4,transform_as_normal=False, create_local_variable=True)
    points = []
    
    for position in point_positions:
        point = geo.createPoint()
        point.setPosition(position)
        points.append(point)
        
        
    for point_indices in poly_point_indices:
        polyline = geo.createPolygon(is_closed=False)  
        for point_index in point_indices:
            polyline.addVertex(points[point_index])

    joints_path={}

# # point_positions = ((0, 0, 0), (1, 0, 0), (2, 0, 0))
# # poly_point_indices = ((0,1,2))
# # frame_positions = {
# #     1: [(0, 0, 0), (1, 0, 0), (2, 0, 0)],
# #     2: [(0, 1, 0), (1, 1, 0), (2, 1, 0)],
# #     3: [(0, 2, 0), (1, 2, 0), (2, 2, 0)],
# #     4: [(0, 3, 0), (1, 3, 0), (2, 3, 0)],
# #     5: [(0, 4, 0), (1, 4, 0), (2, 4, 0)]
# # }

    for joint, value in joints_relationship_dict.items():
        # print(f"each key: {joint}")
        path = []
        current = joint
        while current != -1:
            path.append(joints_children[current])
            current = joints_relationship_dict.get(current, -1)
        joints_path[joint] = '/'.join(reversed(path))
        
    for i, point in enumerate(points):
        point.setAttribValue(name_attr_name, joints_children[i])
        point.setAttribValue(path_attr_name,joints_path[i])
        
    # print(all_frames_matrix)
    current_frame = int(hou.frame())
# #     # TODO: 
    if current_frame in all_frames_matrix:
        # print(f"translation info: {hou.Vector3(matrix.at(0,3),matrix.at(1,3),matrix.at(2,3))}")
        joints_positions_this_frame = [matrix for matrix in all_frames_matrix[current_frame]]
        # print(f"final 10 frame is: {joints_positions_this_frame}")
        # 更新每个点的位置
        for idx, point in enumerate(points):
            if idx < len(joints_positions_this_frame):
                matrix = joints_positions_this_frame[idx]
                # 提取矩阵的平移分量
                translation = hou.Vector3(matrix.at(0,3),matrix.at(1,3),matrix.at(2,3))

                transform = (matrix.at(0,0),matrix.at(1,0),matrix.at(2,0),matrix.at(0,1),matrix.at(1,1),matrix.at(2,1),matrix.at(0,2),matrix.at(1,2),matrix.at(2,2))

                point.setAttribValue(transform_point_attr,transform)
                # 设置点的位置
                # print(translation)
                point.setPosition(translation)
        
def get_anim_data(anim_prim):
    # Get joints and transformation attributes
    joints_attr = anim_prim.GetAttribute('joints').Get()
    joints = list(joints_attr)  # Convert TokenArray to Python list
    rotation_attr = anim_prim.GetAttribute('rotations')

    scale_attr = anim_prim.GetAttribute('scales')
    translation_attr = anim_prim.GetAttribute('translations')
    global_matrices = {}
    # Process each sampled time
    time_samples = rotation_attr.GetTimeSamples()
    for time in time_samples:
        rotations = rotation_attr.Get(time)
        scales = scale_attr.Get(time)
        translations = translation_attr.Get(time)
        # if time ==10:
        #     print(f"rotations:{rotations},translations:{translations}")
        local_matrices = []
        for j, joint in enumerate(joints):
            rotation = rotations[j]
            scale = scales[j]
            translation = translations[j]
            # if j == 2 and time == 10:
            #     print(f"10 frame translation:{translation}")
            # Create local transformation matrix
            _matrix = Gf.Matrix4d().SetIdentity()
            _matrix.SetScale(Gf.Vec3d(scale))
            # if j == 2 and time == 10:
            #     print(f"after scale:{_matrix}")
            _matrix.SetRotateOnly(rotation)
            # if j == 2 and time == 10:
            #     print(f"after rotate:{_matrix}")            
            _matrix.SetTranslateOnly(Gf.Vec3d(translation))
            # if j == 2 and time == 10:
            #     print(f"after translate:{_matrix}")               
            # if j == 2 and time == 10:
            # # #     # col0: ( (1, 0, 0, 0), col1: (0, 0.053860843, 0.99854845, 0), col2: (0, -0.99854845, 0.053860843, 0), (0, 0, 2, 1) )
            #     print(f"old matrix of time 10 and joint 2: {_matrix}")
            # rotation is directly used here
            # if j == 1 and time ==10:
            #     # col0: ( (1, 0, 0, 0), col1: (0, 0.053860843, 0.99854845, 0), col2: (0, -0.99854845, 0.053860843, 0), (0, 0, 2, 1) )
            #     print(f"elbow joint local matrix: {matrix}")
            matrix = hou.Matrix4([_matrix[0][0],_matrix[1][0],_matrix[2][0],_matrix[3][0],
                                _matrix[0][1],_matrix[1][1],_matrix[2][1],_matrix[3][1],
                                _matrix[0][2],_matrix[1][2],_matrix[2][2],_matrix[3][2],
                                _matrix[0][3],_matrix[1][3],_matrix[2][3],_matrix[3][3]])
            # if j == 2 and time == 10:
            # # #     # col0: ( (1, 0, 0, 0), col1: (0, 0.053860843, 0.99854845, 0), col2: (0, -0.99854845, 0.053860843, 0), (0, 0, 2, 1) )
            #     print(f"new matrix of time 10 and joint 2: {matrix}")
            # Accumulate to the global matrix
            if j == 0:
                # Root joint
                local_matrices.append(matrix)
            else:
                # Find parent joint index
                parent_index = find_parent_index(joint, joints)
                parent_matrix = local_matrices[parent_index]
                global_matrix = parent_matrix * matrix
                # if time ==10 and j ==1:
                #     print(f"global matrix joint 1 in 10 frame: {global_matrix}")
                local_matrices.append(global_matrix)

        global_matrices[time] = local_matrices
    # print(global_matrices[10])
    #       [Gf.Matrix4f(1.0, 0.0, 0.0, 0.0,
    #       0.0, 1.0, 0.0, 0.0,
    #        0.0, 0.0, 1.0, 0.0,
    #        0.0, 0.0, 0.0, 1.0), Gf.Matrix4f(1.0, 0.0, 0.0, 0.0,
    #        0.0, 0.05386084318161011, -0.9985484480857849, 0.0,
    #        0.0, 0.9985484480857849, 0.05386084318161011, 2.0,
    #        0.0, 0.0, 0.0, 1.0), Gf.Matrix4f(1.0, 0.0, 0.0, 0.0,
    #        0.0, 0.05386084318161011, -0.9985484480857849, -1.9970968961715698,
    #        0.0, 0.9985484480857849, 0.05386084318161011, 2.1077215671539307,
    #        0.0, 0.0, 0.0, 1.0)]
    
    return global_matrices

def find_parent_index(joint, joints):
    # Implement logic to find the parent joint index
    parent_name = '/'.join(joint.split('/')[:-1])
    try:
        return joints.index(parent_name)
    except ValueError:
        return -1  # Return -1 if the parent joint is not found in the list

def import_skel_anim(stage,skeleton,anim_prim):
    point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict,all_frames_matrice = get_skel_anim_data(stage,skeleton,anim_prim)
    
    set_up_skel_anim(all_frames_matrice,point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict)

def import_usd():
    usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/export_character_anim.usda"
    stage = Usd.Stage.Open(usd_file_path)
    skeleton = "/Model/Skel"
    anim = "/Model/Skel/Anim"
    anim_prim = stage.GetPrimAtPath(anim)
    import_skel_anim(stage,skeleton,anim_prim)
    
import_usd()