from pxr import Usd, UsdGeom

def crate_geometry():
    """
    Procedurally create geometry and save it to the USDA file
    """

    # Create USD
    stage = Usd.Stage.CreateNew('hello_world_value.usda')

    # Build mesh object
    root_xform = UsdGeom.Xform.Define(stage, '/Root')
    mesh = UsdGeom.Mesh.Define(stage, '/Root/Mesh')

    # Build mesh geometry. Here polygon creation magic should happen
    geometry_data = {'points': [(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1)],
                     'face_vertex_counts': [4],
                     'face_vertex_indices': [0, 1, 2, 3]}

    # Set mesh attributes
    mesh.GetPointsAttr().Set(geometry_data['points'])
    mesh.GetFaceVertexCountsAttr().Set(geometry_data['face_vertex_counts'])
    mesh.GetFaceVertexIndicesAttr().Set(geometry_data['face_vertex_indices'])

    # Save USD
    stage.GetRootLayer().Save()


crate_geometry()

