
from pxr import Usd, UsdGeom,UsdSkel
import hou

# 获取当前节点
node = hou.pwd()
geo = node.geometry()
# E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/export_character_anim.usda
# E:/CAVE/final/mscProject/v2Code/arm/armSelf.usda
usd_file_path = "E:/CAVE/final/mscProject/v2Code/arm/armSelf.usda"

# 打开 USD Stage
stage = Usd.Stage.Open(usd_file_path)

# 获取 Mesh
mesh_prim = stage.GetPrimAtPath("/Model/Mesh")
mesh = UsdGeom.Mesh(mesh_prim)

# 获取 faceVertexCounts
face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()

# 获取 faceVertexIndices
face_vertex_indices = mesh.GetFaceVertexIndicesAttr().Get()

# 获取 points
point_positions = mesh.GetPointsAttr().Get()

skinBinding = UsdSkel.BindingAPI.Apply(mesh_prim)
        # GetJointWeightsAttr() GetJointWeightsPrimvar()
joint_weights= skinBinding.GetJointWeightsAttr().Get()
joint_indices_int=skinBinding.GetJointIndicesAttr().Get()
joint_indices = [float(x) for x in joint_indices_int]
# TODO: 拿到序号和名字的对应关系，直接拿到关节列表就好
print(joint_weights)
# TODO: 拿到
# TODO:需要调整整体的顺序，将joint_indices_int里的顺序
bone_capture_data = list(zip(joint_indices, joint_weights))

bone_capture_attr_name = 'boneCapture'

pairs_size = len(joint_indices)//len(point_positions)
tuple_elements_size = pairs_size *2 
geo = hou.node()
#print(f"element size of one joint: {tuple_elements_size}") # arm:1 character: 7

# 每个点有一个boneCapture有14个位置，获得的是两种属性的int[] float[]
# 每七个交替出现
# 创建点并设置它们的位置必须是序号，权重交替出现7次。两者似乎都是float
points = []
idx = 0
for position in point_positions:
    pt = geo.createPoint()
    pt.setPosition(position)
    start_index = idx * pairs_size
    end_index = start_index + pairs_size
    if end_index > len(joint_weights) or end_index > len(joint_indices):
        break
    weights = joint_weights[start_index:end_index]
    indices = joint_indices[start_index:end_index]
    bone_capture_data = [val for pair in zip(indices, weights) for val in pair]
    # pt.setAttributeValue(bone_capture_attr_name,newValue)
    pt.setAttribValue(bone_capture_attr_name, bone_capture_data)
    points.append(pt)
    idx += 1
# TODO: usd的index->joint name->现在的index->set上去
# 创建多边形面
start_index = 0
for count in face_vertex_counts:
    vertices = face_vertex_indices[start_index:start_index + count]
    poly = geo.createPolygon()
    for vertex in reversed(vertices):
        poly.addVertex(points[vertex])
    start_index += count



