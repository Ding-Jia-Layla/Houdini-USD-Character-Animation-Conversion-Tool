import hou

def create_matrix4(rotations, position):
    """
    创建一个 hou.Matrix4 对象
    :param rotations: 长度为 9 的列表，包含旋转矩阵的数据。
    :param position: 长度为 3 的列表，包含位置的数据。
    :return: hou.Matrix4 对象
    """
    # 确保输入的数据长度正确
    assert len(rotations) == 9, "Rotations should have 9 elements."
    assert len(position) == 3, "Position should have 3 elements."

    # 创建 Matrix4 对象，直接初始化所有 16 个元素
    matrix4 = hou.Matrix4(
        [rotations[0], rotations[1], rotations[2], position[0],
         rotations[3], rotations[4], rotations[5], position[1],
         rotations[6], rotations[7], rotations[8], position[2],
         0, 0, 0, 1]
    )

    return matrix4

# 示例数据
rotations = [
    1, 0, 0,  # 第一行
    0, 1, 0,  # 第二行
    0, 0, 1   # 第三行
]
position = [2, 3, 4]

# 创建 Matrix4 对象
matrix4 = create_matrix4(rotations, position)
print("Constructed Matrix4:\n", matrix4)
