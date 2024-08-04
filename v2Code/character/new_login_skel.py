import random
from pxr import Usd, UsdGeom, UsdShade, Gf, Sdf,Kind, UsdSkel,Tf,Vt
import hou

node = hou.pwd()
geo = node.geometry()
def stage_setting(stage):
    stage.SetDefaultPrim(stage.DefinePrim('/Model', 'SkelRoot'))
    stage.SetStartTimeCode(1)    
    stage.SetMetadata('metersPerUnit', 0.01)
    stage.SetEndTimeCode(10)
    stage.SetMetadata('upAxis', 'Y')    
    skelRootPath = Sdf.Path("/Model")
    skel_root = UsdSkel.Root.Define(stage, skelRootPath)
    Usd.ModelAPI(skel_root).SetKind(Kind.Tokens.component)
    skelPath = skelRootPath.AppendChild("Skel")
    return stage,skelPath,skel_root
def export_skeleton(stage,fbx_skel_node,skel):
    # structure of skeleton -- get
    joints, restTransforms = get_skeleton_data(fbx_skel_node)
    # set up for the skeleton -- set
    setup_skeleton(joints,restTransforms,skel)


def get_skeleton_data(fbx_skel_node):
    joints = []
    restTransforms = []
    restTransforms_dict = {}
    points_original = fbx_skel_node.geometry().points()
    # TODO:还是得找根节点： 找路径里最长的然后获取它的第一个就是根节点
    max_path_length = 0
    root_name = None
    mesh_index = None 
    joints_relationship_dict = {}
    for point_original in points_original:
        point_path = point_original.stringAttribValue('path')
        parts = point_path.split('/')
        if len(parts)> max_path_length:
            max_path_length = len(parts)
            root_name = parts[1]
    print(joints_relationship_dict)  
    for index,point_original in enumerate(points_original):
        point_path = point_original.stringAttribValue('path')
        parts = point_path.split('/')
        if(len(parts)==2)and(parts[1]!=root_name):
            mesh_index = index 
        current_name = parts[-1]
        parent_name = parts[-2]
        joints_relationship_dict[current_name] = parent_name
    # print(f"root_name is : {root_name}, mesh_index: {mesh_index}")
    # TODO: 先拿到每个关节的restTransform并且塞入字典
    joints_names=[]
    for index, point in enumerate(points_original):
        if index != mesh_index:
            joints.append(point.stringAttribValue('path'))
            joints_names.append(point.stringAttribValue('name'))
            transformation_matrix_original = point.floatListAttribValue('transform')
            translations = point.floatListAttribValue('P')
            restTransform = Gf.Matrix4d([
                [transformation_matrix_original[0], transformation_matrix_original[1], transformation_matrix_original[2], translations[0]],
                [transformation_matrix_original[3], transformation_matrix_original[4], transformation_matrix_original[5], translations[1]],
                [transformation_matrix_original[6], transformation_matrix_original[7], transformation_matrix_original[8], translations[2]],
                [0, 0, 0, 1]
                ])
            restTransforms_dict[point.stringAttribValue('name')] = restTransform
    restTransforms = [restTransforms_dict[joint] for joint in joints_names]
    return joints,restTransforms
def setup_skeleton(joints, restTransforms, skel):
    topo = UsdSkel.Topology(Vt.TokenArray([joint.replace(":", "_")for joint in joints]))
    valid, reason = topo.Validate()
    if not valid:
        Tf.Warn("Invalid topology: %s" % reason) 
    numJoints = len(joints)
    # if numJoints:
    #     print("Joints number: %s" %numJoints)
    jointTokens = Vt.TokenArray([joint.replace(":", "_") for joint in joints])
    skel.GetJointsAttr().Set(jointTokens)
    topology = UsdSkel.Topology(skel.GetJointsAttr().Get())    
    # bindTransforms 
    skel.GetRestTransformsAttr().Set(Vt.Matrix4dArray(restTransforms))

def export_usd():
    usd_file_path = f'E:/CAVE/final/mscProject/usdaFiles/houdiniPyOutput/houdini_export_{random.randint(1, 100)}.usda'
    _stage = Usd.Stage.CreateNew(usd_file_path)
    stage,skelPath,skel_root= stage_setting(_stage)
    skel = UsdSkel.Skeleton.Define(stage, skelPath)
    skeleton_skel_binding = UsdSkel.BindingAPI.Apply(skel.GetPrim())
    skeleton_root_binding = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())
    animPath = skelPath.AppendChild("Anim")
    skelAnim = UsdSkel.Animation.Define(stage, animPath)
    skeleton_skel_binding.CreateAnimationSourceRel().SetTargets([skelAnim.GetPrim().GetPath()])
    # get the input node
    input_node_name = hou.node('/obj/mixamo_character_animated')
    # get the final node of the input node
    fbx_skel_node = input_node_name.node('fbxanimimport1')
    fbx_anim_node = input_node_name.node('fbxanimimport2')
    fbx_skin_node = input_node_name.node('fbxskinimport1')
    geometry = fbx_skin_node.geometry()
    export_skeleton(stage,fbx_skel_node,skel)
    stage.GetRootLayer().Save()

export_usd()