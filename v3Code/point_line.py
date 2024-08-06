import hou
from pxr import Usd, UsdGeom, Gf
# four joints arm

def get_skel_data(stage):
    skel_bind_dict = {}
    positions_dict = {}
    point_positions_list = []
    point_transforms_list = []
    prim_path = "/Model/Skel"
    prim = stage.GetPrimAtPath(prim_path)
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

def set_up_skel(point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict):
    transforms = []
    print(f"joints children list: {joints_children}") # joints list: ['arm_Shoulder', 'arm_Elbow', 'arm_Hand', 'arm_End']
    #  print(f"parent and child relationship: {joints_relationship_dict}")
    
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
    # add attr: transform , name
    # joint is index
    # TODO: path
    joints_path={}
    #{0:-1,1:0,2:1,3:2}
    print(f"joint relationship: {joints_relationship_dict}")
    
    for joint, value in joints_relationship_dict.items():
        print(f"each key: {joint}")
        path = []
        current = joint
        while current != -1:  # Continue until reaching the root (which has -1)
            path.append(joints_children[current])
            current = joints_relationship_dict.get(current, -1)  # Move to parent, default to -1 if not found
        joints_path[joint] = '/'.join(reversed(path))
    # get all path
    for joint,path in joints_path.items():
        print(f"{path}")
    
    for i, point in enumerate(points):
        point.setAttribValue(name_attr_name, joints_children[i])
        point.setAttribValue(transform_attr_name, transforms[i])
        # TODO: 直到没有父亲关节
        

def import_skel(stage):
    # get the skeleton data
    point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict= get_skel_data(stage)
    # set the skeleton data
    set_up_skel(point_positions,poly_point_indices,point_transforms_list,joints_children,joints_relationship_dict)
    
def import_usd():
    usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/arm_skel_export.usda"
    stage = Usd.Stage.Open(usd_file_path)
    import_skel(stage)
    # import_mesh()
    # import_animation()
    # import_skinning()
    

import_usd()