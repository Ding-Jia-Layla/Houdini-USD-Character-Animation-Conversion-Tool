import hou
from pxr import Usd, UsdGeom, Gf, UsdSkel
# four joints arm

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
    # print(joints_relationship_dict)
    # print(joints_children)
    bind_transforms = prim.GetAttribute("bindTransforms").Get()
    # 顺序是bindTransform的顺序
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
    
    
    
    return point_positions_list,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict

def set_up_skel_anim(point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict):
    transforms = []
    for point_transform in point_transforms_list:
        # print(tuple(point_transform))
        transforms.append(tuple(point_transform))
        
    geo = hou.pwd().geometry()
    
    transform_attr_name = 'transform'
    name_attr_name = 'name'
    path_attr_name = 'path'
    default_identity_transform = (1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0)
    
    geo.addAttrib(hou.attribType.Point,transform_attr_name,default_identity_transform,transform_as_normal=False, create_local_variable=True)
    geo.addAttrib(hou.attribType.Point,name_attr_name,'jointName',transform_as_normal=False, create_local_variable=True)
    geo.addAttrib(hou.attribType.Point,path_attr_name,'parent/child',transform_as_normal=False, create_local_variable=True)
    
    points = []
    
    for position in point_positions:
        pt = geo.createPoint()
        pt.setPosition(position)
        points.append(pt)
    # 创建多条线段
    for point_indices in poly_point_indices:
        polyline = geo.createPolygon(is_closed=False)  
        for point_index in point_indices:
            polyline.addVertex(points[point_index])

    joints_path={}
    
    # print(f"joint relationship: {joints_relationship_dict}")#{0:-1,1:0,2:1,3:2}
    
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
        point.setAttribValue(transform_attr_name, transforms[i])
        point.setAttribValue(path_attr_name,joints_path[i])
        
    all_frames_matrice = get_animation_data(joints_path,anim_prim,joints_children,joints_relationship_dict)
    
        # print(f"joint path: {joints_path[i]}")
    return joints_path,points



def get_animation_data(joints_path,anim_prim,joints_children,joints_relationship_dict):
    
    joints_anims_list = anim_prim.GetAttribute("joints").Get()
    # print(f"joint list: {joints_anims_list}")
    all_attributes_strong = anim_prim.GetProperties()
    all_attributes_space = anim_prim.GetAuthoredProperties()
    all_frames_rotation = anim_prim.GetAttribute('rotations')
    all_frames_scale = anim_prim.GetAttribute('scales')
    all_frames_translations = anim_prim.GetAttribute('translations')
    all_frames_matrice = {}
    # num_frames_rotation = all_frames_rotation.GetNumTimeSamples()
    # 1 frame : M(each joint matrix)* numJoint
    time_samples = all_frames_rotation.GetTimeSamples()
    for time in time_samples:
        each_frames_matrice=[]
        # hou: (x, y, z, and w)
        # Gf:(w and x, y, z)
        #rotation_quat_hou_values = [hou.Quaternion(hou_quaf.GetImaginary()[0],hou_quaf.GetImaginary()[1],hou_quaf.GetImaginary()[2],hou_quaf.GetReal()) for hou_quaf in all_frames_rotation.Get(time) ]
        rotation_quaf_values = all_frames_rotation.Get(time)
        scale_values = all_frames_scale.Get(time)
        translations_values = all_frames_translations.Get(time)
        L = Gf.Matrix4f()
        # Vec3f 每一个关节
        for index, rotate in enumerate(rotation_quaf_values):
            L.SetScale(Gf.Vec3f(scale_values[index]))
            L.SetRotate(rotate)
            L.SetTranslateOnly(translations_values[index])
            local_matrix = hou.Matrix4(
                [[L[0][0],L[0][1],L[0][2],L[0][3]],
                [L[1][0],L[1][1],L[1][2],L[1][3]],
                [L[2][0],L[2][1],L[2][2],L[2][3]],
                [L[3][0],L[3][1],L[3][2],L[3][3]]])
            if time ==1 and index == 0:
                print(f"{joints_children[0]} local transform: {local_matrix}")
            # index自动是这个序列对应骨架的列表
            each_frames_matrice.append(local_matrix)
        bind_transforms = [None] * len(each_frames_matrice)
        for joint_index in range(len(each_frames_matrice)):
            if joints_relationship_dict[joint_index] == -1:
                bind_transforms[joint_index] = each_frames_matrice[joint_index]
            else:
                parent_global_transform = bind_transforms[joints_relationship_dict[joint_index]]
                bind_transforms[joint_index] = parent_global_transform * each_frames_matrice[joint_index]
        # bind transform上是某一帧的所有骨骼的矩阵数据
        # 存好所有帧的字典：{1：{matrices...}}
        all_frames_matrice[time] = bind_transforms
    return all_frames_matrice
        # 每当在播放，能找到目前的关键帧，根据当前的序号就当作key来用，把这些点赋值set
    
def set_animation_data(all_frames_matrice):
    current_frame = int(hou.frame())
    pass


def import_usd():
    usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/arm_skel_export.usda"
    stage = Usd.Stage.Open(usd_file_path)
    
    skeleton = "/Model/Skel"
    anim = "/Model/Skel/Anim"
    anim_prim = stage.GetPrimAtPath(anim)
    anim = UsdSkel.Animation(anim_prim)
    joints_path, points,joints_relationship_dict,joints_children= import_skel(stage,skeleton)
    # import_skinning()

def import_skel(stage,skeleton):
    # skeleton prim:
    # get the skeleton data
    point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict= get_skel_anim_data(stage,skeleton)
    # set the skeleton data
    joints_path, points = set_up_skel_anim(point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict)
    # print(joints_relationship_dict)
    # {0: -1, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 3, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11, 13: 12, 14: 13, 15: 10, 16: 15, 17: 16, 18: 17, 19: 10, 20: 19, 21: 20, 22: 21, 23: 10, 24: 23, 25: 24, 26: 25, 27: 10, 28: 27, 29: 28, 30: 29, 31: 3, 32: 31, 33: 32, 34: 33, 35: 34, 36: 35, 37: 36, 38: 37, 39: 34, 40: 39, 41: 40, 42: 41, 43: 34, 44: 43, 45: 44, 46: 45, 47: 34, 48: 47, 49: 48, 50: 49, 51: 34, 52: 51, 53: 52, 54: 53, 55: 0, 56: 55, 57: 56, 58: 57, 59: 58, 60: 0, 61: 60, 62: 61, 63: 62, 64: 63}
    return joints_path, points,joints_relationship_dict, joints_children
 

import_usd()