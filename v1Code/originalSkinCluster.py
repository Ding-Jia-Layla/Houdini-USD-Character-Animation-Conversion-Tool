import maya.cmds as cmds

cylinder = cmds.polyCylinder(r=1, h=5, sy=20, name="cylinder")[0]
mesh = cmds.ls(type='mesh')
shoulder = cmds.joint(p=(0, -2.5, 0))
elbow = cmds.joint(p=(0, 0, 0))
wrist = cmds.joint(p=(0, 2.5, 0))

shape = cmds.listRelatives(cylinder, shapes=True)[0]
joints = cmds.ls(type='joint')
print(joints)
skin_cluster = cmds.skinCluster(joints, mesh, toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1, weightDistribution=0)[0]

# select the polygon first, then run this line to check vertices count:
cmds.polyEvaluate(v=True)