import hou
from pxr import Usd, UsdGeom, Gf
# four joints arm

def get_skel_data(stage):
    skel_bind_dict = {}
    positions_dict = {}
    point_positions_list = []
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
    print(joints_relationship_dict)
    # print(joints_children)
    bind_transforms = prim.GetAttribute("bindTransforms").Get()
    # 顺序是bindTransform的顺序
    for index, bind_transform in enumerate(bind_transforms):
        skel_bind_dict[joints_children[index]] = bind_transform
        positions_dict[joints_children[index]] = bind_transform.ExtractTranslation()
    for key, value in positions_dict.items():
        point_positions_list.append((value[0],value[1],value[2]))
    point_positions = tuple(point_positions_list)
    #print(point_positions)
    line_list = [(key, value) for key, value in list(joints_relationship_dict.items())][1:]
    poly_point_indices = tuple(line_list)
    return point_positions,poly_point_indices

def set_up_skel(point_positions,poly_point_indices):
    geo = hou.pwd().geometry()
    points = []
    for position in point_positions:
        pt = geo.createPoint()
        pt.setPosition(position)
        points.append(pt)
    # 创建多条线段
    for point_indices in poly_point_indices:
        polyline = geo.createPolygon(is_closed=False)  # 创建一个新的多边形（线段）
        for point_index in point_indices:
            polyline.addVertex(points[point_index])
            
def import_skel(stage):
    point_positions,poly_point_indices = get_skel_data(stage)
    set_up_skel(point_positions,poly_point_indices)
    
def import_usd():
    usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/arm_skel_export.usda"
    stage = Usd.Stage.Open(usd_file_path)
    import_skel(stage)
    # import_mesh()
    # import_animation()
    # import_skinning()
    

import_usd()