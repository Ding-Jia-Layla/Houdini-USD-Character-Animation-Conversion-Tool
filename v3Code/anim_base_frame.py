import hou
point_positions = ((0, 0, 0), (1, 0, 0), (2, 0, 0))
poly_point_indices = ((0,1,2))
frame_positions = {
    1: [(0, 0, 0), (1, 0, 0), (2, 0, 0)],
    2: [(0, 1, 0), (1, 1, 0), (2, 1, 0)],
    3: [(0, 2, 0), (1, 2, 0), (2, 2, 0)],
    4: [(0, 3, 0), (1, 3, 0), (2, 3, 0)],
    5: [(0, 4, 0), (1, 4, 0), (2, 4, 0)]
}
current_frame = int(hou.frame())

geo = hou.pwd().geometry()
points = []
for position in point_positions:
    point = geo.createPoint()
    point.setPosition(position)
    points.append(point)
    
# for point_indices in poly_point_indices:
#     polyline = geo.createPolygon(is_closed=False)  
#     for point_index in point_indices:
#         polyline.addVertex(point_indices)
for point_indices in poly_point_indices:
    polyline = geo.createPolygon(is_closed=False)
    for idx in point_indices:
        polyline.addVertex(points[idx])
print(current_frame)
# 根据当前帧号更新点的位置
if current_frame in frame_positions:
    positions = frame_positions[current_frame]
    for idx, pt in enumerate(geo.points()):
        if idx < len(positions):
            pt.setPosition(hou.Vector3(*positions[idx]))