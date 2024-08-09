#Import Houdini's Command Module
import hou

'''
This Python script will create a Subnetwork, along with with 2 Bone objects parented to a Null...
Instructions: simply run the script in the Python Source Editor :)
'''

#Create Subnet
subnet = hou.node("/obj").createNode("subnet", "%s_Skeleton" % "Cool")
#Prevent Overlapping Nodes
subnet.moveToGoodPosition()
#Create Root Null and Use Name of Subnet as Prefix
root = subnet.createNode("null", "%s_Root" % subnet)
#Offset Root Null in the Translate Y axis
root.parm("ty").set(2)
#Clean Transforms of Null

#Create First Bone
bone_0 = subnet.createNode("bone", "%s_Bone_0" % root)
#Parent First Bone to Root Null
bone_0.setNextInput(root)
bone_0.moveToGoodPosition()
bone_0.parm("rx").set(-120)

#Enable Xray on Bone
bone_0.useXray(True)
#Create Second Bone
bone_1 = subnet.createNode("bone", "%s_Bone_1" % root)
bone_1.setNextInput(bone_0)
bone_1.moveToGoodPosition()
bone_1.parm("rx").set(60)

bone_1.useXray(True)