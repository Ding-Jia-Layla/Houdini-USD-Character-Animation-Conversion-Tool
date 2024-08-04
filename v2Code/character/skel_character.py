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
    hierarchy_list = list(hierarchy.values())
    # return type : list
    return sorted(joints, key=lambda joint: len(joint.split('/')))
def get_skeleton_data(fbx_node):
    joints = []
    bindTransforms = []
    restTransforms = [] 
    capt_parents = fbx_node.node('fbx_skin_import1').geometry().intListAttribValue('capt_parents')
    capt_names = fbx_node.node('fbx_skin_import1').geometry().stringListAttribValue('capt_names')
    capt_xforms_list =  fbx_node.node('fbx_skin_import1').geometry().attribValue('capt_xforms')
    capt_xforms = [tuple(capt_xforms_list[i:i+16]) for i in range(0,len(capt_xforms_list),16)]
    for index, value in enumerate(capt_parents):
        if value == -1:
            root_index = index
    root_name = capt_names[root_index]
    # 父子关系的字典。
    capt_dict={}
    for index, name in enumerate(capt_names):
        parent_index = capt_parents[index]
        if parent_index == -1:
            parent_name = None
        else:
            parent_name = capt_names[parent_index]
        capt_dict[name] = parent_name
    joints_paths={}
    for joint in capt_dict:
        current = joint
        path=[]
        while current:
            path.append(current)
            current = capt_dict[current]
        joints_paths[joint]='/'.join(reversed(path))
    joints = list(joints_paths.values())
    print(joints)
    # bind pose -- capt_xforms 
    bindTransforms = [Gf.Matrix4d(*capt_xform) for capt_xform in capt_xforms]
    # get the transform matrix: {0,0,0}*capt_xforms
    bind_transform_dict={}
    rest_transform_dict={}
    for index, value in enumerate(bindTransforms):
        bind_transform_dict[capt_names[index]] = value
    # resttransform<matrix4d>: compute the local space transform 每一个关节骨骼相对于父节点的矩阵 子-父
    # rest should be local, bind should be world space
    for index, value in enumerate(joints):
        parts = value.split('/')
        if(len(parts)==1):
            rest_transform_dict[root_name] = bind_transform_dict[root_name]
        else:
            child = parts[-1]
            parent = parts[-2]
            M = bind_transform_dict[child] * bind_transform_dict[parent].GetInverse()
            rest_transform_dict[child] = M
    restTransforms = list(rest_transform_dict.values())
    # print(f"restTransforms:{restTransforms}")
    root_bindTransform = bind_transform_dict[root_name]
    root_restTransform = rest_transform_dict[root_name]
    geom_bindTransform = root_bindTransform * root_restTransform
    return joints, bindTransforms, restTransforms,geom_bindTransform, root_name
# 在这里整理所有的 这是正确的最终的顺序的矩阵和关节
def setup_skeleton(_joints, _bindTransforms, _restTransforms, root_name, skel):
    joints = build_joint_hierarchy(_joints)
    bindTransforms = []
    restTransforms = []
    for joint in joints:
        joint_index =  _joints.index(joint)
        bindTransforms.append(_bindTransforms[joint_index])
        restTransforms.append(_restTransforms[joint_index])
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
    skel.GetBindTransformsAttr().Set(bindTransforms)
    # restTransforms 
    if restTransforms and len(restTransforms) == numJoints:
        skel.GetRestTransformsAttr().Set(restTransforms)
    return joints, bindTransforms, restTransforms,root_name

def export_skeleton(stage,fbx_node,skel):
    # structure of skeleton -- get
    joints, bindTransforms, restTransforms,geom_bindTransform, root_name= get_skeleton_data(fbx_node)
    # set up for the skeleton -- set
    joints, bindTransforms, restTransforms,root_name = setup_skeleton(joints, bindTransforms, restTransforms, root_name,skel)
    #return skeleton
    return joints,geom_bindTransform, root_name
    
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
    fbx_node = input_node_name.node('fbxcharacterimport2')
    geometry = fbx_node.geometry()
    joints,geom_bindTransform,root_name = export_skeleton(stage,fbx_node,skel)
    stage.GetRootLayer().Save()

export_usd()

