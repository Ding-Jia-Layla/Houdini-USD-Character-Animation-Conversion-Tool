from pxr import Gf

def compute_bind_transforms(joints, rest_transforms):
    bind_transforms = {}
    
    def calculate_bind_transform(joint):
        # 如果bindTransform已经计算过了，直接返回
        if joint in bind_transforms:
            return bind_transforms[joint]
        
        parent = joints[joint]
        
        if parent is None:
            # 根节点，直接使用restTransform作为bindTransform
            bind_transforms[joint] = rest_transforms[joint]
        else:
            # 递归计算父节点的bindTransform
            parent_bind_transform = calculate_bind_transform(parent)
            # 计算子节点的bindTransform
            bind_transforms[joint] = rest_transforms[joint] * parent_bind_transform
        
        return bind_transforms[joint]
    
    # 计算所有关节的bindTransform
    for joint in joints:
        calculate_bind_transform(joint)
    
    return bind_transforms

# 示例数据
joints = {
    "root": None,
    "child1": "root",
    "child2": "child1"
}

rest_transforms = {
    "root": Gf.Matrix4d(((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))),
    "child1": Gf.Matrix4d(((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,2,1))),
    "child2": Gf.Matrix4d(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 2, 1)))
}

bind_transforms = compute_bind_transforms(joints, rest_transforms)
print(bind_transforms)
