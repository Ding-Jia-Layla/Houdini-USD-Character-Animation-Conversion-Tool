from pxr import Gf
capt_names = ["hip", "spine", "chest", "neck", "head"]
capt_parents = [-1, 0, 1, 2, 3]

skeleton_hierarchy = {}

for index, name in enumerate(capt_names):
    parent_index = capt_parents[index]
    if parent_index == -1:
        parent_name = None  
    else:
        parent_name = capt_names[parent_index]
    skeleton_hierarchy[name] = parent_name

joints_path={}
for joint in skeleton_hierarchy:
    path = []
    current = joint
    while current:
        path.append(current)
        current = skeleton_hierarchy[current]
#当列表中有多于一个元素时，'/' 才会出现在元素之间。str.join(iterable)只有>1的时候才会起效。
    joints_path[joint]='/'.join(reversed(path))
for joint,path in joints_path.items():
    print(f"{path}")
# Gf.Matrix4d 的构造函数期望接收 16 个单独的浮点数作为参数，而不是一个包含这些浮点数的元组。    
example = [ (0.01, -0.0, 0.0, 0.0, 0.0, 0.01, -1.45519e-11, 0.0, -0.0, -8.67365e-21, 0.01, 0.0, 0.0, 1.36853, -0.0183984, 1.0), (-0.00103434, 0.00108028, -0.00988753, 0.0, 0.00994398, 0.000330021, -0.00100418, 0.0, 0.000217828, -0.009936, -0.00110837, 0.0, 0.633132, 1.27577, -0.0244756, 1.0)]
matrix =[Gf.Matrix4d(A) for A in example]
print(matrix)
# get path
# get each key, then add the value,
# use the value as key, then get the value
# until the value is None
print(skeleton_hierarchy)