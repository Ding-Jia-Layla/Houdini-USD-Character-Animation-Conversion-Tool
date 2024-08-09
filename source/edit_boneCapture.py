import hou
from pxr import Usd, UsdSkel,UsdGeom

node = hou.pwd()
geo = node.geometry()
mesh_points = geo.points()
usd_file_path = "E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/export_character_anim.usda"
stage = Usd.Stage.Open(usd_file_path)
mesh_prim = stage.GetPrimAtPath("/Model/Mesh")
skel_prim = stage.GetPrimAtPath("/Model/Skel")
mesh = UsdGeom.Mesh(mesh_prim)


# TODO: 拿到序号和名字的对应关系，直接拿到关节列表就好
joints_usd_list = [joint_name.split('/')[-1] for joint_name in skel_prim.GetAttribute("joints").Get()]
# print(f"USD joints list: {joints_usd_list}")

## houdini part
skin_node = hou.node('/obj/anim_import/character_captureproximity')


# TODO: 拿到boneCapture_pCaptPath的顺序
unpack_node = hou.node('/obj/anim_import/captureattribunpack1')
geo = unpack_node.geometry()

if geo.findGlobalAttrib('boneCapture_pCaptPath'):
    pCaptPath = geo.attribValue('boneCapture_pCaptPath')
    # print(f"pack joint list: {list(pCaptPath)}")# ('arm_Elbow', 'arm_Hand', 'arm_Shoulder')


# TODO: 将joint_indices_int里的所有的点对应找到名字 找到名字之后对应找到boneCapture_pCaptPath的序号，调整整体的顺序
skinBinding = UsdSkel.BindingAPI.Apply(mesh_prim)
joint_weights= skinBinding.GetJointWeightsAttr().Get()
joint_indices_disorder=skinBinding.GetJointIndicesAttr().Get()
# joint_indices_disorder = [float(x) for x in joint_indices_int]
joint_indices=[]
for joint_index in joint_indices_disorder:
    # capture中实际的序号
    new_index = pCaptPath.index(joints_usd_list[joint_index])
    joint_indices.append(float(new_index))
# print(f"right skinning order: {joint_indices}")# except: 1,1,1,1, 2,2,2,2, 0,0,0,0 # right skinning order: [1, 1, 1, 1, 2, 2, 2, 2, 0, 0, 0, 0]

bone_capture_data = list(zip(joint_indices, joint_weights))
bone_capture_attr_name = 'boneCapture'

pairs_size = len(joint_indices)//len(mesh_points)
tuple_elements_size = pairs_size *2 
print(f"pair size is : {pairs_size}")

idx = 0
for point in mesh_points:
    start_index = idx * pairs_size
    end_index = start_index + pairs_size
    if end_index > len(joint_weights) or end_index > len(joint_indices):
        break
    weights = joint_weights[start_index:end_index]
    indices = joint_indices[start_index:end_index]
    # tuple 
    # (31.0, 0.0005515387165360153, 30.0, 0.005704548675566912, 7.0, 0.0041468022391200066, 6.0, 0.016468079760670662, 3.0, 0.025992322713136673, 4.0, 0.014713943004608154, 5.0, 0.9324227571487427)
    bone_capture_data = [val for pair in zip(indices, weights) for val in pair]
    if idx == 0:
        print(f"point 0 bone Capture value is : {bone_capture_data}")
        
    point.setAttribValue(bone_capture_attr_name, tuple(bone_capture_data))
    idx += 1

print(f"houdini node output boneCapture value of point 0: {mesh_points[0].floatListAttribValue(bone_capture_attr_name)}")# tuple of float







