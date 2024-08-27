import hou
from pxr import Usd, UsdSkel,UsdGeom

node = hou.pwd()
geo = node.geometry()
mesh_points = geo.points()
usd_file_path = node.parm('file_path').eval()

stage = Usd.Stage.Open(usd_file_path)
mesh_prim = stage.GetPrimAtPath("/Model/Mesh")
skel_prim = stage.GetPrimAtPath("/Model/Skel")
mesh = UsdGeom.Mesh(mesh_prim)

current_node = hou.pwd()


joints_usd_list = [joint_name.split('/')[-1] for joint_name in skel_prim.GetAttribute("joints").Get()]
# print(f"USD joints list: {joints_usd_list}")

## houdini part
skin_node = hou.pwd().input(0)


unpack_node = skin_node.outputs()[0]
geo = unpack_node.geometry()

if geo.findGlobalAttrib('boneCapture_pCaptPath'):
    pCaptPath = geo.attribValue('boneCapture_pCaptPath')

skinBinding = UsdSkel.BindingAPI.Apply(mesh_prim)
joint_weights= skinBinding.GetJointWeightsAttr().Get()
joint_indices_disorder=skinBinding.GetJointIndicesAttr().Get()
# joint_indices_disorder = [float(x) for x in joint_indices_int]
joint_indices=[]
for joint_index in joint_indices_disorder:
    new_index = pCaptPath.index(joints_usd_list[joint_index])
    joint_indices.append(float(new_index))


bone_capture_data = list(zip(joint_indices, joint_weights))
bone_capture_attr_name = 'boneCapture'

pairs_size = len(joint_indices)//len(mesh_points)
tuple_elements_size = pairs_size *2 
# print(f"pair size is : {pairs_size}")

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
    point.setAttribValue(bone_capture_attr_name, tuple(bone_capture_data))
    idx += 1

