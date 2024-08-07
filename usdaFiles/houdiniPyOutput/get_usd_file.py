from pxr import Usd, UsdGeom, Gf

def compute_global_transforms(stage, skeleton_path):
    # Open the USD scene
    prim = stage.GetPrimAtPath(skeleton_path)
    if not prim:
        raise ValueError(f"Prim not found: {skeleton_path}")

    # Get the animation source
    anim_path = prim.GetRelationship('skel:animationSource').GetTargets()[0]
    anim_prim = stage.GetPrimAtPath(anim_path)

    # Get joints and transformation attributes
    joints_attr = prim.GetAttribute('joints').Get()
    joints = list(joints_attr)  # Convert TokenArray to Python list

    rotation_attr = anim_prim.GetAttribute('rotations')
    # print(rotation_attr)
    scale_attr = anim_prim.GetAttribute('scales')
    translation_attr = anim_prim.GetAttribute('translations')

    # Initialize global matrix storage
    global_matrices = {}

    # Process each sampled time
    time_samples = rotation_attr.GetTimeSamples()
    for time in time_samples:
        rotations = rotation_attr.Get(time)
        scales = scale_attr.Get(time)
        translations = translation_attr.Get(time)
        # if time ==10:
        #     print(f"rotations:{rotations},translations:{translations}")
        local_matrices = []
        for j, joint in enumerate(joints):
            rotation = rotations[j]
            scale = scales[j]
            translation = translations[j]

            # Create local transformation matrix
            _matrix = Gf.Matrix4f().SetIdentity()
            _matrix.SetScale(Gf.Vec3f(scale))
            _matrix.SetRotateOnly(rotation)
            _matrix.SetTranslateOnly(Gf.Vec3f(translation))
            # rotation is directly used here
            # if j == 1 and time ==10:
            #     # col0: ( (1, 0, 0, 0), col1: (0, 0.053860843, 0.99854845, 0), col2: (0, -0.99854845, 0.053860843, 0), (0, 0, 2, 1) )
            #     print(f"elbow joint local matrix: {matrix}")
            matrix = Gf.Matrix4f(_matrix[0][0],_matrix[1][0],_matrix[2][0],_matrix[3][0],
                                _matrix[0][1],_matrix[1][1],_matrix[2][1],_matrix[3][1],
                                _matrix[0][2],_matrix[1][2],_matrix[2][2],_matrix[3][2],
                                _matrix[0][3],_matrix[1][3],_matrix[2][3],_matrix[3][3])
            # if j == 1 and time ==10:
            #     # col0: ( (1, 0, 0, 0), col1: (0, 0.053860843, 0.99854845, 0), col2: (0, -0.99854845, 0.053860843, 0), (0, 0, 2, 1) )
            #     print(f"elbow joint local matrix: {matrix}")
            # Accumulate to the global matrix
            if j == 0:
                # Root joint
                local_matrices.append(matrix)
            else:
                # Find parent joint index
                parent_index = find_parent_index(joint, joints)
                parent_matrix = local_matrices[parent_index]
                global_matrix = parent_matrix * matrix
                # if time ==10 and j ==1:
                #     print(global_matrix)
                local_matrices.append(global_matrix)

        global_matrices[time] = local_matrices

    return global_matrices

def find_parent_index(joint, joints):
    # Implement logic to find the parent joint index
    parent_name = '/'.join(joint.split('/')[:-1])
    try:
        return joints.index(parent_name)
    except ValueError:
        return -1  # Return -1 if the parent joint is not found in the list

# Usage example
stage = Usd.Stage.Open("export_character_anim.usda")
global_transforms = compute_global_transforms(stage, "/Model/Skel")
print(global_transforms[1])
