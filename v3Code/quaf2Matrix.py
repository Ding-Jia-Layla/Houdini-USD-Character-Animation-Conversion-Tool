import numpy as np
import math
from pxr import Gf
from scipy.spatial.transform import Rotation as R
#  10: [(1, 0, 0, 0), (0.72589976, 0.6878005, 0, 0), (1, 0, 0, 0)],
# source file: q0->q3

Rq=[0.6878005, 0, 0,0.72589976]
#   t0           t3          t6
# [[ 1.          0.          0.        ]
#  [ 0.          0.05386093 -0.99854845]
#  [ 0.          0.99854845  0.05386093]]



# 四元数到旋转矩阵
r = R.from_quat(Rq)
Rm = r.as_matrix()
# print(Rm)
# 10 frame
# 父关节的全局变换矩阵
M2 = Gf.Matrix4f(1,0,0,0,
                0,0.05386093,-0.99854845, 0,
                0,0.99854845,0.05386093,2,
                0,0,0,1)
print(M2[1][1])
# 子关节的局部变换矩阵
M3 = Gf.Matrix4f(1,0,0,0,
                0,1,0,0,
                0,0,1,2,
                0,0,0,1)
M=M2*M3
# print(M)

######houdini##############
# import hou

#t0
#t3
#t6

# M2 = hou.Matrix4([1,0,0,0,
#                 0,0.05386093,-0.99854845, 0,
#                 0,0.99854845,0.05386093,2,
#                 0,0,0,1])
# M3 = hou.Matrix4([1,0,0,0,
#                 0,1,0,0,
#                 0,0,1,2,
#                 0,0,0,1])
# print(M2*M3)
# # parentW* childL

#######houdini2#######
# import hou


# q = hou.Quaternion([0.6878005, 0, 0,0.72589976]).extractRotationMatrix3()


# joint2 = hou.Matrix4([q.at(0, 0),q.at(1,0),q.at(2,0),0,
# q.at(0, 1),q.at(1,1),q.at(2,1),0,
# q.at(0, 2),q.at(1,2),q.at(2,2),2,
# 0,0,0,1])

# joint3 = hou.Matrix4([1,0,0,0,
#                  0,1,0,0,
#                  0,0,1,2,
#                  0,0,0,1])

# print(joint2* joint3)
