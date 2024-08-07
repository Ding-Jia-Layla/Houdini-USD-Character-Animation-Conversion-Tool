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
    
    all_frames_matrice = get_anim_data(anim_prim,joints_children,joints_relationship_dict)
    # return point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict
    return point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict,all_frames_matrice

def set_up_skel_anim(all_frames_matrix,point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict):
    
    geo = hou.pwd().geometry()
    # transform_attr_name = 'transform'
    name_attr_name = 'name'
    path_attr_name = 'path'
    
    geo.addAttrib(hou.attribType.Point,name_attr_name,'jointName',transform_as_normal=False, create_local_variable=True)
    geo.addAttrib(hou.attribType.Point,path_attr_name,'parent/child',transform_as_normal=False, create_local_variable=True)
    
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

# point_positions = ((0, 0, 0), (1, 0, 0), (2, 0, 0))
# poly_point_indices = ((0,1,2))
# frame_positions = {
#     1: [(0, 0, 0), (1, 0, 0), (2, 0, 0)],
#     2: [(0, 1, 0), (1, 1, 0), (2, 1, 0)],
#     3: [(0, 2, 0), (1, 2, 0), (2, 2, 0)],
#     4: [(0, 3, 0), (1, 3, 0), (2, 3, 0)],
#     5: [(0, 4, 0), (1, 4, 0), (2, 4, 0)]
# }
    # print(f"joint relationship: {joints_relationship_dict}")#{0:-1,1:0,2:1,3:2}
    # 全局转换似乎是错的
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
    # print(all_frames_matrice)
    current_frame = int(hou.frame())
    # TODO: 
    if current_frame in all_frames_matrix:
        joints_positions_this_frame = [matrix for matrix in all_frames_matrix[current_frame]]
        print(f"final 10 frame is: {joints_positions_this_frame}")
        # for idx, pt in enumerate(geo.points()):
        #     pt.setPosition()
        #     if idx < len(joints_positions_this_frame):
        #         pt.setPosition(hou.Vector3(*joints_positions_this_frame[idx]))
        
def get_anim_data(anim_prim, joints_children, joints_relationship_dict):
    all_frames_rotation = anim_prim.GetAttribute('rotations')
    # print(f"all_frames_rotation: {all_frames_rotation.Get(10)}")
    all_frames_scale = anim_prim.GetAttribute('scales')
    all_frames_translations = anim_prim.GetAttribute('translations')
    all_frames_matrix = {}
    time_samples = all_frames_rotation.GetTimeSamples()
    # print(f"num of frames: {time_samples}")
    # 避免在循环内部重复创建Matrix对象
    L = Gf.Matrix4f()

    for time in time_samples:
        each_frames_matrix = []
        rotation_quaf_values = all_frames_rotation.Get(time)
        scale_values = all_frames_scale.Get(time)
        translations_values = all_frames_translations.Get(time)

        for rotate, scale, translate in zip(rotation_quaf_values, scale_values, translations_values):
            # 重设矩阵而不是创建新的
            L.SetIdentity()
            L.SetTranslateOnly(translate)
            L.SetScale(Gf.Vec3f(scale))
            L.SetRotateOnly(rotate)
            # if time ==10:
            #     print(f" local rotate matrix is : {L}")
                # local rotate matrix is : ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
                #  local rotate matrix is : ( (1, 0, 0, 0), (0, 0.053860843, 0.99854845, 0), (0, -0.99854845, 0.053860843, 0), (0, 0, 2, 1) )
                #  local rotate matrix is : ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, -5.207933e-8, 2, 1) )
            houdini_matrix = hou.Matrix4(
                [[L[i][j] for j in range(4)] for i in range(4)]
            )
            each_frames_matrix.append(houdini_matrix)
        # print(len(each_frames_matrix)) # 3

        global_transforms = [None] * len(each_frames_matrix)
        for joint_index, local_matrix in enumerate(each_frames_matrix):
            if joints_relationship_dict[joint_index] == -1:
                global_transforms[joint_index] = local_matrix
            else:
                parent_index = joints_relationship_dict[joint_index]
                global_transforms[joint_index] = global_transforms[parent_index] * local_matrix

        all_frames_matrix[time] = global_transforms
    print(f"middle matrix 10 frame: {all_frames_matrix[10]}")
    # [<hou.Matrix4 [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]>, <hou.Matrix4 [[1, 0, 0, 0], [0, 0.0538608, 0.998548, 0], [0, -0.998548, 0.0538608, 0], [0, 0, 2, 1]]>, <hou.Matrix4 [[1, 0, 0, 0], [0, 0.0538608, 0.998548, 0], [0, -0.998548, 0.0538608, 0], [0, -5.20793e-08, 4, 1]]>]
    return all_frames_matrix

def import_skel_anim(stage,skeleton,anim_prim):
    
    point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict,all_frames_matrice = get_skel_anim_data(stage,skeleton,anim_prim)
    
    set_up_skel_anim(all_frames_matrice,point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict)

def import_usd():
    usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/houdini_export_81.usda"
    stage = Usd.Stage.Open(usd_file_path)
    skeleton = "/Model/Skel"
    anim = "/Model/Skel/Anim"
    anim_prim = stage.GetPrimAtPath(anim)
    import_skel_anim(stage,skeleton,anim_prim)
import_usd()