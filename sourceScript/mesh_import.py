
from pxr import Usd, UsdGeom,UsdSkel
import hou


node = hou.pwd()
geo = node.geometry()

usd_file_path = node.parm('file_path').eval()


stage = Usd.Stage.Open(usd_file_path)

# get Mesh
mesh_prim = stage.GetPrimAtPath("/Model/Mesh")
mesh = UsdGeom.Mesh(mesh_prim)

# get faceVertexCounts
face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()

# get faceVertexIndices
face_vertex_indices = mesh.GetFaceVertexIndicesAttr().Get()

# get points
point_positions = mesh.GetPointsAttr().Get()

skinBinding = UsdSkel.BindingAPI.Apply(mesh_prim)

joint_weights= skinBinding.GetJointWeightsAttr().Get()
joint_indices_int=skinBinding.GetJointIndicesAttr().Get()
joint_indices = [float(x) for x in joint_indices_int]

bone_capture_data = list(zip(joint_indices, joint_weights))

bone_capture_attr_name = 'boneCapture'

pairs_size = len(joint_indices)//len(point_positions)
tuple_elements_size = pairs_size *2 


points = []

for position in point_positions:
    pt = geo.createPoint()
    pt.setPosition(position)
    points.append(pt)



start_index = 0
for count in face_vertex_counts:
    vertices = face_vertex_indices[start_index:start_index + count]
    poly = geo.createPolygon()
    for vertex in reversed(vertices):
        poly.addVertex(points[vertex])
    start_index += count


