#coding: utf-8


import os
import maya.cmds as mc
import pymel.core as pm

from functools import partial

"""
import maya.cmds as mc
selection = mc.ls(sl=True)

for item in selection:
    #get uv set list
    uv_set_list = mc.polyUVSet(item, query=True, allUVSets=True)
    old_uv_set = uv_set_list[0]
    print(uv_set_list)
    #create a new uv set
    #copy the scatter uv set on the second uv set
    #create an automatic and stacked uv for the first uv set
    #rename the first uv_set
    
    mc.polyUVSet(item, create=True, uvSet="alpha_uv_set")
    mc.polyCopyUV("%s.f[*]"%item, uvSetNameInput=old_uv_set, uvSetName="alpha_uv_set")
    mc.polyUVSet(item, rename=True, newUVSet="scatter_uv_set", uvSet=old_uv_set)
    mel.eval("texStackShells {};")
    mel.eval("texOrientShells;")
"""



class UvScriptApplication:
	def __init__(self):

		self.main_interface_function()




	def main_interface_function(self):
		self.uv_window = mc.window(title="UvScriptWindow - By Quazar", width=300, height=350)

		self.uv_column = mc.columnLayout(adjustableColumn=True, parent=self.uv_window)
		self.uv_world_position_checkbox = mc.checkBox(label="On : World Position\nOff : Local Position", value=False, parent=self.uv_column)
		self.uv_center = mc.checkBox(label="Center uv tile", enable=False, value=False, parent=self.uv_column)
		self.uv_scale = mc.checkBox(label="Full size uv tile", enable=False, value=False, parent=self.uv_column)

		mc.button(label="Create UV Set For Scattering", parent=self.uv_column, command=self.create_uv_set_function)

		mc.showWindow()




	def create_uv_set_function(self, event):
		#get maya selection
		selection = mc.ls(sl=True)

		#get checkboxes values
		world_position = mc.checkBox(self.uv_world_position_checkbox, query=True, value=True)
		
		for item in selection:
			uv_set_list = mc.polyUVSet(item, query=True, allUVSets=True)
			old_uv_set = uv_set_list[0]

			mc.polyUVSet(item, create=True, uvSet="alpha_uv_set")
			mc.polyCopyUV("%s.f[*]"%item, uvSetNameInput=old_uv_set, uvSetName="alpha_uv_set")
			mc.polyUVSet(item, rename=True, newUVSet="scatter_uv_set", uvSet=old_uv_set)
			mc.polyAutoProjection("%s.f[*]"%item, ws=world_position, uvs="alpha_uv_set")
			print("Automatic UV set for %s"%item)
			mel.eval("texStackShells {};")
			mel.eval("texOrientShells;")
			print("UV Set defined for %s\n"%item)



		
		
		


UvScriptApplication()