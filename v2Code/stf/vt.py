def build_joint_hierarchy(joints):
    hierarchy = {}
    for joint in joints:
        parts = joint.split('/')
        for i in range(len(parts)):
            parent = '/'.join(parts[:i])
            child = '/'.join(parts[:i+1])
            if parent not in hierarchy:
                hierarchy[parent] = []
            if child not in hierarchy[parent]:
                hierarchy[parent].append(child)
    return hierarchy

def sort_joints_by_length(joints):
    return sorted(joints, key=lambda joint: len(joint.split('/')))

# 示例关节数据
joints = [
    "Hips/Spine/Spine1/Spine2/Neck/Head", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandPinky1", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandMiddle1", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandRing1", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandThumb1", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandPinky1/LeftHandPinky2", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandRing1/LeftHandRing2", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandPinky1/LeftHandPinky2/LeftHandPinky3", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandMiddle1/LeftHandMiddle2", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandRing1/LeftHandRing2/LeftHandRing3", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandMiddle1/LeftHandMiddle2/LeftHandMiddle3", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandIndex1", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandIndex1/LeftHandIndex2", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandIndex1/LeftHandIndex2/LeftHandIndex3", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandThumb1/LeftHandThumb2/LeftHandThumb3", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder/LeftArm/LeftForeArm/LeftHand/LeftHandThumb1/LeftHandThumb2", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandMiddle1", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandRing1", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandPinky1", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandRing1/RightHandRing2", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandPinky1/RightHandPinky2", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandPinky1/RightHandPinky2/RightHandPinky3", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandRing1/RightHandRing2/RightHandRing3", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandMiddle1/RightHandMiddle2", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandMiddle1/RightHandMiddle2/RightHandMiddle3", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandIndex1", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandIndex1/RightHandIndex2", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandIndex1/RightHandIndex2/RightHandIndex3", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandThumb1", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandThumb1/RightHandThumb2", 
    "Hips/Spine/Spine1/Spine2/RightShoulder/RightArm/RightForeArm/RightHand/RightHandThumb1/RightHandThumb2/RightHandThumb3", 
    "Hips/Spine/Spine1/Spine2/Neck", 
    "Hips/Spine/Spine1/Spine2", 
    "Hips/Spine/Spine1", 
    "Hips/Spine/Spine1/Spine2/LeftShoulder", 
    "Hips/Spine", 
    "Hips", 
    "Hips/LeftUpLeg", 
    "Hips/RightUpLeg", 
    "Hips/LeftUpLeg/LeftLeg", 
    "Hips/LeftUpLeg/LeftLeg/LeftFoot", 
    "Hips/LeftUpLeg/LeftLeg/LeftFoot/LeftToeBase", 
    "Hips/Spine/Spine1/Spine2/RightShoulder", 
    "Hips/RightUpLeg/RightLeg/RightFoot", 
    "Hips/RightUpLeg/RightLeg", 
    "Hips/RightUpLeg/RightLeg/RightFoot/RightToeBase"
]
index_joint = joints.index('Hips/RightUpLeg/RightLeg/RightFoot/RightToeBase')
# 构建层次结构
hierarchy = build_joint_hierarchy(joints)

# 对关节按长度排序
sorted_joints = sort_joints_by_length(joints)


print(index_joint)
