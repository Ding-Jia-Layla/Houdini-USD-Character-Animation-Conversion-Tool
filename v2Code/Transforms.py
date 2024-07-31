import numpy as np
import math
from scipy.spatial.transform import Rotation as R
m11, m21, m31, m12, m22, m32, m13, m23, m33 = 1.0, 0.0, 0.0, 0.0, 1.9307546608615667e-05, 0.9999807476997375, 0.0, -0.9999807476997375, 1.9307546608615667e-05
rotation_matrix_np = np.array([[m11, m12, m13],
                            [m21, m22, m23],
                            [m31, m32, m33]])
Rq=[0.7071, 0.7071, 0, 0]
rotation_np = R.from_matrix(rotation_matrix_np)
quaternion_scipy = rotation_np.as_quat()
quaternion_other = [quaternion_scipy[3], quaternion_scipy[0], quaternion_scipy[1], quaternion_scipy[2]]
print(f"quaternion :{quaternion_other}")



import hou
node = hou.pwd()
geo = node.geometry()

# 90 degree
rotation_matrix = hou.Matrix3((1, 0, 0,
                               0, 0, -1,
                               0, 1, 0))


quaternion_s= hou.Quaternion(rotation_matrix)

quaternion =quaternion_s[3]

print("Quaternion from rotation matrix:", quaternion)



