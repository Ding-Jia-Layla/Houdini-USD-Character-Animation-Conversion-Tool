import numpy as np
import math
from scipy.spatial.transform import Rotation as R
m11, m21, m31, m12, m22, m32, m13, m23, m33 = 1.0, 0.0, 0.0, 0.0, 1.9307546608615667e-05, 0.9999807476997375, 0.0, -0.9999807476997375, 1.9307546608615667e-05
rotation_matrix_np = np.array([[m11, m12, m13],
                            [m21, m22, m23],
                            [m31, m32, m33]])
Rh = hou.Matrix3((m11, m12, m13, m21, m22, m23, m31, m32, m33)

rotation_np = R.from_matrix(rotation_matrix_np)
quaternion_scipy = rotation_np.as_quat()
quaternion_other = [quaternion_scipy[3], quaternion_scipy[0], quaternion_scipy[1], quaternion_scipy[2]]
print(f"quaternion :{quaternion_other}")



# import numpy as np
# from pxr import Gf

# # 假设 bindTransform 和 restTransform 矩阵
# bindTransform = np.array([
#     [1, 0, 0, 2],
#     [0, 1, 0, 3],
#     [0, 0, 1, 4],
#     [0, 0, 0, 1]
# ])

# restTransform = np.array([
#     [1, 0, 0, 0],
#     [0, 1, 0, 0],
#     [0, 0, 1, 0],
#     [0, 0, 0, 1]
# ])


# # 计算 restTransform 的逆矩阵
# restTransform_inv = np.linalg.inv(restTransform)

# # 计算 geomBindTransform
# geomBindTransform = np.dot(bindTransform, restTransform_inv)

# # 将 geomBindTransform 转换为 Gf.Matrix4d 格式
# gf_geomBindTransform = Gf.Matrix4d(geomBindTransform)

# mius_geomBindTransform = np.dot(bindTransform,restTransform)
# print("geomBindTransform:\n", geomBindTransform)
# print("Gf.Matrix4d geomBindTransform:\n", gf_geomBindTransform)
# print(mius_geomBindTransform)


from pxr import Gf

restTransforms = [
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1), 
    Gf.Matrix4d(1, 0, 0, 0,     
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 2, 1), 
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 4, 1)   
]

bindTransforms= [
    Gf.Matrix4d(1, 0, 0, 1,
                0, 1, 0, 2,
                0, 0, 1, 3,
                0, 0, 0, 1), 
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 2, 1), 
    Gf.Matrix4d(1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 2, 1)   
]
mius_geomBindTransform = bindTransforms[0]*restTransforms[0]
print(mius_geomBindTransform)



