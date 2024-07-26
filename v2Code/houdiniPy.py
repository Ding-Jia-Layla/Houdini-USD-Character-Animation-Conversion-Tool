import random
from pxr import Usd, UsdGeom, UsdShade, Gf, Sdf,Kind, UsdSkel
import hou

node = hou.pwd()
geo = node.geometry()

def setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices):
    mesh.GetPointsAttr().Set(points)
    mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
    mesh.GetFaceVertexIndicesAttr().Set(face_vertex_indices)

    if normals:
        mesh.CreateNormalsAttr().Set(normals)
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)

    # Set orientation and subdivisionScheme
    mesh.CreateOrientationAttr().Set(UsdGeom.Tokens.leftHanded)
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

        for vertex in vertices:
            face_vertex_indices.append(vertex.point().number())

            # Get Normals data
            if geometry.findVertexAttrib("N") is not None:
                normal = vertex.attribValue("N")
                normals.append(Gf.Vec3f(normal[0], normal[1], normal[2]))

    return points, normals, face_vertex_counts, face_vertex_indices
    
def stage_setting(stage):
    stage.SetDefaultPrim(stage.DefinePrim('/Model', 'Xform'))
    stage.SetStartTimeCode(1)    
    #stage.SetDefaultPrim(stage.DefinePrim('/Model', 'SkelRoot'))
    #stage.SetEndTimeCode(10)
    stage.SetMetadata('metersPerUnit', 1)
    stage.SetMetadata('upAxis', 'Y')    
    skelRootPath = Sdf.Path("/Model")
    #root = UsdSkel.Root.Define(stage, skelRootPath)
    root = UsdGeom.Xform.Define(stage, skelRootPath)
    Usd.ModelAPI(root).SetKind(Kind.Tokens.component)
    return stage
def export_geometry(stage, geometry, input_node_name):
    # Get Geometry data
    points, normals, face_vertex_counts, face_vertex_indices = get_geometry_data(geometry)

    mesh = UsdGeom.Mesh.Define(stage, f'/Model/Mesh')
    setup_mesh(mesh, points, normals, face_vertex_counts, face_vertex_indices)
def get_skeleton_data(fbx_node):
    joints = []
    bindTransforms = []
    restTransforms = [] 
    
    # skeleton_capture_name = deform_node.inputs()[0] .type().name()
    child_nodes = fbx_node.children()
    output_sop_nodes = [node for node in child_nodes if node.type().name() == 'output']
    rest_geometry = output_sop_nodes[0]
    capture_pose = output_sop_nodes[1]
    animated_pose = output_sop_nodes[2]
    capture_pose_geo = capture_pose.geometry()
    
    skeleton= capture_pose_geo.points()
    # 每读一个点就把关节上的属性都塞进结构里
    # joints<path>
    # get the topo (structure)
    
    # bindtransform<matrix4d>
    # resttransform<matrix4d>
    
    # test to get one attr of one point
    joint_name = skeleton[2].attribValue('name')
    joint_transform = skeleton[2].floatListAttribValue('transform')
    print(f"joint name is : {joint_name}")
    print(f"transform should be found: {joint_transform}")
    
    return joints
def export_skeleton(stage,fbx_node):
    # structure of skeleton -- get
    joints= get_skeleton_data(fbx_node)
    # set up for the skeleton -- set
    #return skeleton
def export_usd():
    usd_file_path = f'E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/houdini_export_{random.randint(1, 100)}.usda'
    _stage = Usd.Stage.CreateNew(usd_file_path)
    stage = stage_setting(_stage)
    # get the input node
    input_node_name = hou.node('/obj/mixamo_character_animated')
    # get the final node of the input node
    fbx_node = input_node_name.node('fbxcharacterimport1')
    #deform_node = input_node_name.node('bonedeform1')
    geometry = fbx_node.geometry()
    mesh = export_geometry(stage, geometry, input_node_name)
    export_skeleton(stage,fbx_node)
    stage.GetRootLayer().Save()

export_usd()

