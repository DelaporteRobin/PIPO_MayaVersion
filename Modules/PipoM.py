#coding: utf-8

#Copyright 2023, Robin Delaporte AKA Quazar, All rights reserved.


import maya.cmds as mc
import pymel.core as pm
import os
import ctypes
import sys
import pickle
import json 
import yaml
import zipfile
import shutil
import webbrowser
import threading
import subprocess

from random import randrange
from time import sleep
from tqdm import tqdm
from datetime import datetime
from functools import partial
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

"""
	[Origin]
	[key]
	[name]
	[mayaProjectName]
	[type]
	[editPublishFolder]
"""


"""
publish export tasklist
	removing the references (import them or break them)
	delete all the namespaces in namespace editor
	export the selection in the scene under a new scene (publish scene)

	rigging scene:
		delete unused nodes
		reset controllers position
		hide sks (check gesse document)
		delete renderman volume aggregate if present in the scene
"""






class PipelineApplication:







	def load_settings_function(self):
		if (self.project_path == None) or (self.project_path == "None"):
			mc.warning("Impossible to load settings!")
			return None, None, None, None, None
		else:
			
			if type(self.project_path)==list:	
				self.project_path = self.project_path[0]



			#try to load settings files from pipeline
			#if file are missing call creation
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.json"), "r") as read_file:
					load_data = json.load(read_file)
				self.settings = load_data["dict1"]
				self.settings_dictionnary = load_data["dict2"]
				self.additionnal_settings = load_data["dict3"]
				self.texture_settings = load_data["dict4"]
			except:
				mc.warning("Impossible to load pipeline settings!")
				self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings = self.create_pipeline_settings_function("pipeline_settings")
			else:
				print("Pipeline settings loaded!")



			try:
				with open(os.path.join(self.program_folder, "Data/PipoUserSettings.json"), "r") as read_file:
					user_settings = json.load(read_file)

				self.user_settings = user_settings["dict1"]
			except:
				mc.warning("Impossible to load user settings!")
				self.user_settings = self.create_pipeline_settings_function("user_settings")
			else:
				print("User settings loaded!")
			
		
		
			"""
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.json"), "r") as read_file:
					load_data = json.load(read_file)
				with open(os.path.join(self.program_folder, "Data/PipoUserSettings.json"), "r") as read_file:
					user_settings = json.load(read_file)
				
				self.user_settings = user_settings["dict1"]
				self.settings = load_data["dict1"]
				self.settings_dictionnary = load_data["dict2"]
				self.additionnal_settings = load_data["dict3"]
				self.texture_settings = load_data["dict4"]

				
				print("Settings loaded successfully!")
			
			except:
				self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings, self.user_settings = self.create_pipeline_settings_function()
				print("Settings file created in your project!")
			"""
			
			
				
		return self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings, self.user_settings






	def letter_verification_function(self, content):
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		list_letter = list(letter)
		list_capital = list(letter.upper())
		list_figure = list(figure)

		list_content = list(content)
		if list_content == None:
			return False

		valid = False
		for i in range(0, len(list_content)):
			if (list_content[i] in list_letter)==True or (list_content[i] in list_capital)==True or (list_content[i] in list_figure)==True:
				valid=True
		return valid
		#OLD SYSTEM
		"""
		for i in range(0, len(list_content)):
			if (list_content[i] in list_letter)==True or (list_content[i] in list_capital)==True or (list_content[i] in list_figure)==True:
				return True
			else:
				if (i == len(list_content) - 1):
					return False
		"""




	def define_project_path_ui_function(self, type,event):
		
		if type == "project":
			mc.textField(self.project_label, edit=True, text=mc.workspace(query=True, active=True))
			folder = mc.workspace(query=True, active=True)
		else:
			#open a file explorer to define a folder
			folder = mc.fileDialog2(fm=3)
			if folder == None:
				mc.error("You have to define one folder!")
				return
			else:
				mc.textField(self.project_label, edit=True, text=folder[0])
				#folder = mc.workspace(query=True, active=True)


		with open(os.path.join(self.program_folder, "Data/PipelineData.dll"), "wb") as read_file:
			pickle.dump(folder, read_file)

		self.project_path = folder 
		self.reload_settings_function()

		#self.load_shading_settings_function()
		
		
		self.save_settings_file()
		





	def reload_settings_function(self):
		self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings, self.user_settings = self.load_settings_function()



		self.type_list_value = []
		for key, value in self.settings_dictionnary.items():
			self.type_list_value.append(key)

		setting_key_list = []
		setting_value_list = []
		setting_default_folder_list = []
		setting_keyword_list = []

		for setting_key, setting_value in self.settings.items():

			#create the default folder buttons
			setting_key_list.append(setting_key)
			setting_value_list.append(setting_value[0])
			setting_keyword_list.append(setting_value[1])

			if setting_value[2] == None:
				setting_default_folder_list.append("None")
			else:
				setting_default_folder_list.append(setting_value[2])



		mc.textScrollList(self.type_list, edit=True, removeAll=True, append=self.type_list_value)
		#mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=setting_key_list)
		#mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=setting_value_list)
		#mc.textScrollList(self.setting_keyword_list, edit=True, removeAll=True, append=setting_keyword_list)
		#mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=setting_default_folder_list)

		




	def save_settings_file(self):

		if self.project_path == "None":
			mc.error("Impossible to save the settings file\nYou have to set the pipeline folder first!")
		else:
			#get content of the pipeline path
			try:
				path = mc.textField(self.project_label, query=True, text=True)
			except:
				path = self.project_path
			if os.path.isdir(path)==False:
				mc.error("You have to define a valid pipeline folder first!")
				return
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			if os.path.isdir(os.path.join(path, "PipelineManagerData"))==False:
				os.mkdir(os.path.join(path, "PipelineManagerData"))
			
			try:
				print(self.user_settings)
				user_dictionnary = {
					"dict1": self.user_settings,
				}
				print("SAVING USER DICTIONNARY")
				print(user_dictionnary)
				saving_dictionnary = {
					"dict1":self.settings,
					"dict2":self.settings_dictionnary,
					"dict3":self.additionnal_settings,
					"dict4":self.texture_settings,
				}

				#save the pipeline file
				with open(os.path.join(path, "PipelineManagerData/PipelineSettings.json"), "w") as save_file:
					save_file.write(json.dumps(saving_dictionnary,indent=4))
				#save the user settings file
				with open(os.path.join(self.program_folder, "Data/PipoUserSettings.json"), "w") as save_file:
					save_file.write(json.dumps(user_dictionnary,indent=4))
			except AttributeError:
				print("Impossible to save!")
				self.create_pipeline_settings_function()
			self.add_log_content_function("Settings file saved successfully")




	



	
	def create_pipeline_settings_function(self, info):
		print("Settings file created!")
		basic_file_type_list = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]

		if info == "pipeline_settings":
			#TYPE OF DATA
			#DETECTION OF FILES
			self.settings_dictionnary = {
				"character": basic_file_type_list,
				"prop": basic_file_type_list, 
				"set": basic_file_type_list,
				"fx": "unknown",
				"shots": ["layout", "camera", "anim", "render", "compositing"],
			}
			self.settings = {
				"character":["[project]_[key]_[name]_[type]", "char", None],
				"prop":["[project]_[key]_[name]_[type]", "prop", None],
				"set":["[project]_[key]_[name]_[type]", "set", None],
				"fx":["[project]_[key]_[name]_[type]","fx", None],
				"shots":["[project]_[key]_[sqversion]_[shversion]", "shots", {"folder1":"folder1", "folder2":"folder2"},]
			}
			self.additionnal_settings = {
				#"checkboxValues":[False, False, True, False, False, False],
				"3dSceneExtension":[".ma",".mb"],
				"3dItemExtension":[".obj", ".fbx"],
				"texturesExtension":[".png", ".tif",".tiff",".tex", ".exr", ".jpg"],
				"lodInterval":[1,3],
				"dodgeList":["RND"],
				"mayaProjectName":"maya",
				"exportSelectionTypeList":["character","prop"],
				"editPublishFolder":["edit", "publish"],
				"renderFolderInProject":"images",
				"renderFrameSyntax":["[content].[frame]", "[content]_[frame]"],
				"textureFolderInProject": "3dPaintTextures",
				"discordBotToken":None,
				"discordChannelId":None,
				"renderEngine":"Renderman",
				"renderShaderNodeList":["lambert"]
			}
			self.texture_settings = {
				"Renderman": {
					"textureNodes": {
						"PxrTexture":"filename",
						"PxrNormalMap":"filename"
					},
					"shadingNodes": ["PxrSurface", "PxrLayerSurface", "PxrDisplace"],
					"channelData": {
						"DIFFUSE": {
							"keywordList":["diffuse", "diff", "Diff", "Diffuse", "Albedo"],
							"textureNode":"PxrTexture",
							},
						"ROUGHNESS": {
							"keywordList":["roughness", "Rough", "Roughness"],
							"textureNode":"PxrTexture",
							},
						"NORMAL": {
							"keywordList":["normal", "Normal"],
							"textureNode":"PxrNormalMap",
							},
					},
				},

			}
			self.save_settings_file()
			return self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings

		if info == "user_settings":
			self.user_settings = {
				"CheckboxValues": {
					"lastsyntax_checkbox":True,
					"index_checkbox":True,
					"projectcontent_checkbox":False,
					"searchbar_checkbox":False,
					"folder_checkbox":True,
					"scenes_checkbox":True,
					"items_checkbox":True,
					"textures_checkbox":False,

					"archivemenu_projectcheckbox":False,
					"archivemenu_pipelinecheckbox":False,

					"render_texture_manual_checkbox":True,
					"render_texture_automatic_checkbox":False,
					"render_texture_limit_project":False,
					"render_texture_udim_checking":True,

					"export_current_folder_checkbox":False,
					"export_custom_folder_checkbox":False,
					"export_assist_folder_checkbox":False,
					"export_projectassist_folder_checkbox":True,
					"export_item_checkbox":True,
					"export_edit_name_checkbox":False,
					"export_backup_publish_checkbox":True,
				},
				"AdditionalData": {
					"FavoriteFiles":{},
					"ExportRaimbow":True,
					"ExportWebsite":True,
					"Notification":False,
					"TagKind":["character", "item"],
					"TagState":["publish"],
					"TagType":["mod", "lookdev", "lookdevProxy"]
				}
			}
			self.save_settings_file()
			return self.user_settings
		


	
	def reset_default_syntax_function(self,event):
		self.default_settings = {
			"character":["[project]_[key]_[name]_[type]", "char", None],
			"prop":["[project]_[key]_[name]_[type]", "prop", None],
			"set":["[project]_[key]_[name]_[type]", "set", None,],
			"fx":["[project]_[key]_[name]_[type]","fx", None,],
			"shots":["[project]_[key]_[sqversion]_[shversion]", "shots", {"folder1":"folder1", "folder2":"folder2"},]
		}
		basic_file_type_list = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]

		#TYPE OF DATA
		#DETECTION OF FILES
		self.default_settings_dictionnary = {
			"character": basic_file_type_list,
			"prop": basic_file_type_list, 
			"set": basic_file_type_list,
			"fx": "unknown",
			"shots": ["layout", "camera", "anim", "render", "compositing"],
		}

		self.default_additional_settings = {
			#"checkboxValues":[False, False, True, False, False, False],
			"3dSceneExtension":[".ma",".mb"],
			"3dItemExtension":[".obj"],
			"texturesExtension":[".png", ".tif",".tiff",".tex", ".exr", ".jpg"],
			"dodgeList":["RND"],
			"lodInterval":[1,3],
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"],
			"renderFolderInProject":"images",
			"exportSelectionTypeList":["character","prop"],
			"renderFrameSyntax":["[content].[frame]", "[content]_[frame]"],
			"textureFolderInProject":"sourceimages",
			"discordBotToken":None,
			"discordChannelId":None,
			"renderEngine":"Renderman",
			"renderShaderNodeList":["lambert"],
		}
		self.default_user_settings = {
			"CheckboxValues": {
				"lastsyntax_checkbox":True,
				"index_checkbox":True,
				"projectcontent_checkbox":False,
				"searchbar_checkbox":False,
				"folder_checkbox":True,
				"scenes_checkbox":True,
				"items_checkbox":True,
				"textures_checkbox":False,

				"archivemenu_projectcheckbox":False,
				"archivemenu_pipelinecheckbox":False,

				"render_texture_manual_checkbox":True,
				"render_texture_automatic_checkbox":False,
				"render_texture_limit_project":False,
				"render_texture_udim_checking":True,

				"export_current_folder_checkbox":False,
				"export_custom_folder_checkbox":False,
				"export_assist_folder_checkbox":False,
				"export_projectassist_folder_checkbox":True,
				"export_item_checkbox":True,
				"export_edit_name_checkbox":False,
				"export_backup_publish_checkbox":True,
			},
			"AdditionalData": {
					"FavoriteFiles":{},
					"ExportRaimbow":True,
					"ExportWebsite":True,
					"Notification":False,
					"TagKind":["character", "item"],
					"TagState":["publish"],
					"TagType":["mod", "lookdev", "lookdevProxy"]
			}
		}
		
		self.default_texture_settings = {

			"Renderman": {
				"textureNodes": {
					"PxrTexture":"filename",
					"PxrNormalMap":"filename"
				},
				"shadingNodes": ["PxrSurface", "PxrLayerSurface", "PxrDisplace"],
				"channelData": {
					"DIFFUSE": {
						"keywordList":["diffuse", "diff", "Diff", "Diffuse", "Albedo"],
						"textureNode":"PxrTexture",
						},
						"ROUGHNESS": {
						"keywordList":["roughness", "Rough", "Roughness"],
						"textureNode":"PxrTexture",
						},
					"NORMAL": {
						"keywordList":["normal", "Normal"],
						"textureNode":"PxrNormalMap",
						},
				},
			},

		}
		

		
		
		self.settings = self.default_settings
		self.settings_dictionnary = self.default_settings_dictionnary
		self.additionnal_settings = self.default_additional_settings
		self.texture_settings = self.default_texture_settings
		self.user_settings = self.default_user_settings
		self.save_settings_file()




	def add_log_content_function(self, log_new_content):
		now = datetime.now()
		new_content = "[%s/%s/%s:%s:%s] %s" % (now.year, now.month, now.day, now.hour, now.minute, log_new_content)
		self.log_list_content.append(new_content)

		try:
			mc.textScrollList(self.log_list, edit=True, removeAll=True, append=self.log_list_content)
		except:
			pass




	def add_team_log_content_function(self, log_new_content):
		#get project path
		folder_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isfile(os.path.join(folder_path, "PipelineManagerData/PipelineManagerTeamLog.dll"))==True:
			#get the content of this file
			try:
				with open(os.path.join(folder_path, "PipelineManagerData/PipelineManagerTeamLog.dll"), "rb") as read_file:
					team_content = pickle.load(read_file)
				#get the old content
			except:
				mc.error("Impossible to change the team log file!")
				return 
			else:
				if type(team_content)==list:
					
					
					team_content.append(log_new_content)
					with open(os.path.join(folder_path, "PIpelineManagerData/PipelineManagerTeamLog.dll"), "wb") as save_file:
						pickle.dump(team_content, save_file)





	def display_new_list_function(self):

		"""
		check the selection of all list to create the content of the next one
		if you change the previous one check if the content of the next list need to change
		if it does, change it (obvious bro)
		"""
		type_selection = mc.textScrollList(self.type_list, query=True, si=True)
		kind_selection = mc.textScrollList(self.kind_list, query=True, si=True)
		name_selection = mc.textScrollList(self.name_list, query=True, si=True)
		seq_selection = mc.textScrollList(self.seq_list, query=True, si=True)
		shot_selection = mc.textScrollList(self.shot_list, query=True, si=True)


		if name_selection != None:
			if self.current_name != name_selection[0]:
				self.current_name = name_selection[0]

		
		
		if type_selection != None:
			past_type_list = self.new_type_list 
			self.new_type_list = []

			for element in type_selection:
				for key, value in self.settings_dictionnary.items():
					if key == element:
						if type(value) != list:
							value = [value]
						for item in value:
							if (item in self.new_type_list)==False:
								self.new_type_list.append(item)

								


			if (past_type_list != self.new_type_list):
				mc.textScrollList(self.kind_list, edit=True, removeAll=True, append=self.new_type_list)


			
		if (type_selection != None) or (kind_selection != None) or (name_selection != None):

			#CREATION OF A THREAD TO CREATE A PARALLEL PROCESSING
			self.searching_thread = threading.Thread(target=partial(self.search_files_function, type_selection, kind_selection, name_selection, seq_selection, shot_selection))
			self.searching_thread.start()
			self.searching_thread.join()

			#LOCAL LAUNCHING OF THE SEARCHING FUNCTION
			#self.search_files_function(type_selection, kind_selection, name_selection)






	def search_files_function(self, type_selection, kind_selection, name_selection, seq_selection, shot_selection):
		#get the content of all checkbox
		#to define the searching field
		index_checkbox_value = mc.checkBox(self.index_checkbox, query=True, value=True)
		project_limit = mc.checkBox(self.searchbar_checkbox, query=True, value=True)
		folder_limit = mc.checkBox(self.folder_checkbox, query=True, value=True)

		scenes_limit = mc.checkBox(self.scenes_checkbox, query=True, value=True)
		items_limit = mc.checkBox(self.items_checkbox, query=True, value=True)
		textures_limit = mc.checkBox(self.textures_checkbox, query=True, value=True)
		#default_folder = mc.checkBox(self.folder_checkbox, query=True, value=True)

		project_name = os.path.basename(os.path.normpath(mc.textField(self.project_label, query=True, text=True)))

		starting_folder = []

		#define the starting folder of the research
		

		if project_limit == True:
			if mc.workspace(query=True, active=True) != None:
				starting_folder = [mc.workspace(query=True, active=True)]
			else:
				starting_folder = None
				mc.warning("No project defined!")
		elif folder_limit == True:
			#get the default folder for the type selected
			type_selection = mc.textScrollList(self.type_list, query=True, si=True)
			if (type_selection)==None:
				mc.error("Impossible to get the default folder!")
				return
			else:
				default_folder = self.settings[type_selection[0]][2]
			
				if (default_folder == None):
					mc.error("Default folder undefined!")
					return


				#create a list of default folder path variables
				default_folder_variable_list = ["[Origin]","[key]","[name]","[mayaProjectName]","[type]","[editPublishFolder]","[sqversion]","[shversion]"]

				#get informations to replace in the default folder
				project_path = mc.textField(self.project_label, query=True, text=True)
				maya_project_name = self.additionnal_settings["mayaProjectName"]
				#edit_publish_folder = self.additionnal_settings["editPublishFolder"]
				name_selection = mc.textScrollList(self.name_list, query=True, si=True)
				kind_selection = mc.textScrollList(self.kind_list, query=True, si=True)


				default_folder = default_folder.replace("[Origin]", str(project_path))
				default_folder = default_folder.replace("[mayaProjectName]", str(maya_project_name))
				#default_folder = default_folder.replace("[editPublishFolder]", str(edit_publish_folder))
				if name_selection != None:
					default_folder = default_folder.replace("[name]", name_selection[0])
				if kind_selection != None:
					default_folder = default_folder.replace("[type]", kind_selection[0])
				default_folder = default_folder.replace("[key]", type_selection[0])

				#split the path and create the default folder path until a variable is default folder variable is detected!
				default_folder_splited = default_folder.split("/")
				#print(default_folder_splited)
				final_default_folder = []

				#print(default_folder_splited)
				for item in default_folder_splited:
					if item in default_folder_variable_list:
						break
					else:
						final_default_folder.append(item)
				print("Default Folder defined")
				#print(final_default_folder)
				starting_folder = ["/".join(final_default_folder)]
				#print(starting_folder)
		else:
			#define the project folder as starting folder
			starting_folder = mc.textField(self.project_label, query=True, text=True)
			if (starting_folder == None) or (os.path.isdir(starting_folder)==False):
				mc.error("Invalid project folder!")
				return
			starting_folder = [starting_folder]

		





				




	
		#define the extension list according to checkbox
		extension_list = []
		if mc.checkBox(self.scenes_checkbox, query=True, value=True)== True:
			extension_list += self.additionnal_settings["3dSceneExtension"]
		if mc.checkBox(self.textures_checkbox, query=True, value=True)==True:
			extension_list += self.additionnal_settings["texturesExtension"]
		if mc.checkBox(self.items_checkbox, query=True, value=True)==True:
			extension_list += self.additionnal_settings["3dItemExtension"]
		#define the number of files from the starting folder
		total_files = 0
		if index_checkbox_value == False:
			for folder in starting_folder:
				total_files += int(sum([len(files) for root, dirs, files in os.walk(folder)]))
		else:
			total_files = len(list(self.pipeline_index.keys()))
		i = 0



		#self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting",min=0, max=total_files)
	
		print("Searching...")
		print("Starting folder : %s"%starting_folder)


		
		final_file_list = []
		final_name_list = []
		final_seq_list = []
		final_shot_list = []
		
		for folder in starting_folder:
			print("searching in [%s]"%folder)
			#p = 0 

			#total_files = int(sum([len(files) for root, dirs, files in os.walk(folder)]))
		
			if index_checkbox_value == False:
				print("PIPELINE CHECKING")
				for r, d, f in os.walk(folder):
					if ("PipelineManagerData" in d)==True:
						d.remove("PipelineManagerData")
					for file in f:
						value = self.parse_file_function(file)

						
						#print("CHECKING %s"%file)
						if value != False:


							filename = value["file_name"]
							key = value["key"]
							saved_type = value["saved_type"]




							#split the checked filename and check if the keyword name and type are the right ones
							splited_filename = file.split("_")
							splited_syntax = self.settings[key][0].split("_")
							
							#print(key in type_selection, key, type_selection)
							if key not in type_selection:
								continue

							if name_selection != None:
								if "[name]" in splited_syntax:
									name_index = splited_syntax.index("[name]")
									if splited_filename[name_index] not in name_selection:
										#print("name error %s %s"%(splited_filename[name_index], name_selection))
										continue
							
							if kind_selection != None:
								if "[type]" in splited_syntax:
									kind_index = splited_syntax.index("[type]")
									if splited_filename[kind_index] not in kind_selection:
										#print("type error %s %s"%(splited_filename[kind_index], kind_selection))
										continue
							
							if seq_selection != None:
								if "[sqversion]" in splited_syntax:
									seq_index = splited_syntax.index("[sqversion]")
									if splited_filename[seq_index] not in seq_selection:
										continue
							if shot_selection != None:
								if "[shversion]" in splited_syntax:
									shot_index = splited_syntax.index("[shversion]")
									if splited_filename[shot_index] not in shot_selection:
										continue
							
							
							#print("no error detected for %s"%filename)
							
							if file not in final_file_list:
								final_file_list.append(file)

							if mc.checkBox(self.projectcontent_checkbox, query=True, value=True)==False:
								if filename not in final_name_list:
									final_name_list.append(filename)
							else:
							
								default_folder = self.settings[key][2]
								splited_default_folder = default_folder.split("/")
								splited_file_path = r.replace("\\", "/").split("/")
								
								
								if "[name]" not in splited_default_folder:
									print("Impossible to get the name in the default folder path!")
									 
								else:
									"""
									if the name selection isn't empty add all the files contained in the right maya project
									"""
									splited_file_path = splited_file_path[splited_file_path.index(project_name):]

									file_project_name_index = len(splited_default_folder) - splited_default_folder.index("[name]")
									
									
									if len(splited_file_path)== len(splited_default_folder):
										if splited_file_path[-file_project_name_index] not in final_name_list:
											
											final_name_list.append(splited_file_path[-file_project_name_index])


							
							

			else:
				"""
				check all the files in the index
				check that theses files are matching 
				with the selection in the textscrolllist
				"""
				file_pipeline_index = list(self.pipeline_index.keys())
				for file in file_pipeline_index:
					result = self.check_syntax_from_selection_function(file, type_selection, kind_selection, name_selection, seq_selection, shot_selection)
					
					if result != None:
						value, value_key, sqversion, shversion = result
					try:
						value, value_key, sqversion, shversion = self.check_syntax_from_selection_function(file, type_selection, kind_selection, name_selection, seq_selection, shot_selection)
					except:
						value, value_key, sqversion, shversion = [False, False, False, False] 
					else:
						pass


					#print(file, value, value_key, sqversion, shversion)
					
					if value != False:
						if (sqversion != False) and (sqversion != "None") and (shversion != None):
							if sqversion not in final_seq_list:
								final_seq_list.append(sqversion)

						if (shversion != False) and (shversion != "None") and (shversion != None):
							if shversion not in final_shot_list:
								final_shot_list.append(shversion)
						#check if the path of the file is in the starting path
						file_path = self.pipeline_index[file]["path"]

						#print(file, value)
						
						
						display = True
						#check if the project folder is checked
						#process the verification to check that only the project files are displayed
						if project_limit==True:
							#print("project limit detected!")
							
							try:
								common_path = os.path.commonpath([starting_folder[0], file_path])
								#print(os.path.normpath(common_path) == os.path.normpath(starting_folder[0]), os.path.normpath(common_path), os.path.normpath(starting_folder[0]))
								if os.path.normpath(common_path)!= os.path.normpath(starting_folder[0]):
									display = False
								
							except ValueError:
								display=False


							
							
							

						if display == True:	
							#print("file matching [%s]"%file)
							#print("checking for the file %s"%file)

							if mc.checkBox(self.projectcontent_checkbox, query=True, value=True)==False:
								if file not in final_file_list:
									final_file_list.append(file)
								if value not in final_name_list:
									final_name_list.append(value)
							else:
							
								#get the default folder for the path
								try:
									default_folder = self.settings[value_key][2]
								except:
									print("Impossible to find default folder for %s"%file)
									continue
								splited_default_folder = default_folder.split("/")
								splited_file_path = file_path.split("/")
								"""
								if (sqversion != False) and (sqversion != None):
									if sqversion not in final_seq_list:
										final_seq_list.append(sqversion)
										final_file_list.append(file)
								"""
								if (shversion != False) and (shversion != None):
									if shversion not in final_shot_list:
										final_shot_list.append(shversion)
										final_file_list.append(file)
								
								if "[name]" not in splited_default_folder:
									print("Impossible to get the name in the filepath!\n")

								else:
									#print("INFORMATIONS")
									#name_index = splited_default_folder.index("[name]")
									splited_file_path = splited_file_path[splited_file_path.index(project_name):]
									#print(splited_file_path)
									#print(splited_default_folder)
									file_project_name_index = len(splited_default_folder) - splited_default_folder.index("[name]")

									
									if name_selection == None:
										final_file_list.append(file)


									

									

										
									
									if len(splited_file_path)== len(splited_default_folder):
										if splited_file_path[-file_project_name_index] not in final_name_list:

											if name_selection == None:
												final_name_list.append(splited_file_path[-file_project_name_index])
											else:
												"""
												print("checking for ")
												print(file)
												print(splited_file_path)
												print(name_selection)
												print(splited_file_path[-file_project_name_index])
												"""

												if splited_file_path[-file_project_name_index] in name_selection:
													final_file_list.append(file)


					
				
					


		
		print("\nSEARCHING DONE!!!\n")
		mc.progressWindow(endProgress=True)

		final_name_list.sort(key=lambda x: x.lower())
		final_file_list.sort(key=lambda x: x.lower())

		
		mc.textScrollList(self.result_list, edit=True,removeAll=True, append=final_file_list)

		mc.textScrollList(self.seq_list, edit=True, removeAll=True, append=final_seq_list)
		mc.textScrollList(self.shot_list, edit=True, removeAll=True, append=final_shot_list)
	


		#each time you select a new name change the value of current_name variable
		#if the name selected each time that function is called is different from the current name
		#update the name list!!!
		#print(name_selection, self.current_name)
		#print(type_selection, self.current_type)

		 

		try:
			if (type_selection[0] != self.current_type):
				self.current_type = type_selection[0]
				mc.textScrollList(self.name_list, edit=True, removeAll=True, append=final_name_list)
			else:
				try:
					if (name_selection[0] != self.current_name):
						self.current_name = name_selection[0]
						mc.textScrollList(self.name_list, edit=True, removeAll=True, append=final_name_list)				
				except:
					mc.textScrollList(self.name_list, edit=True, removeAll=True, append=final_name_list)

				
				try:
					print(self.current_seq, seq_selection[0])
					if (seq_selection[0] != self.current_seq):

						self.current_seq = seq_selection[0]
						mc.textScrollList(self.seq_list, edit=True, removeAll=True, append=final_seq_list)
				except:
					mc.textScrollList(self.seq_list, edit=True, removeAll=True, append=final_seq_list)
		except:
			pass






	def check_syntax_from_selection_function(self, file, type_selection, kind_selection, name_selection, seq_selection, shot_selection):
		file, extension = os.path.splitext(file)
		#get the selection in textscrolllist
		
		final_name = "None"
		splited_file = file.split("_")
		current_type = "None"
		final_seq = "None" 
		final_shot = "None"
		final_lod = "None"
		
		if type_selection != None:
			for t in type_selection:
				#get the syntax for the given type
				type_syntax_data = self.settings[t][0]
				#print(type_syntax_data)

				#check if the syntaix already a list => several syntax
				"""
				if type(type_syntax_data)!= list:
					type_syntax_data = [type_syntax_data]
				"""
				if type(type_syntax_data) != list:
					type_syntax_data = [type_syntax_data]
				else:

					pass 
					
					if mc.checkBox(self.displayonlylastsyntax_checkbox, query=True, value=True)==True:
						if len(self.settings[t][0]) > 1:
							type_syntax_data = [self.settings[t][0][-1]]
						else:
							type_syntax_data = self.settings[t][0]
					else:
						pass
					

				#print(type_syntax_data)

				for type_syntax in type_syntax_data:
					error=False
					splited_type_syntax = type_syntax.split("_")

					#print(splited_type_syntax, splited_file)

					if len(splited_type_syntax) != len(splited_file):
						error=True
						continue

					#get the index of the keyword in the syntax
					#print(splited_type_syntax)
					type_index = splited_type_syntax.index('[key]')
					"""
					except:
						mc.warning("No key in syntax!")
						error=True
						continue
					"""
					

					#print(splited_file[type_index], self.settings[t][1])
					if splited_file[type_index] != self.settings[t][1]:
						#print("type error! %s"%splited_file)
						error=True 
					else:
						current_type = splited_file[type_index]
						#detect the filename of the current file
					
						#print("[sqversion]" in splited_type_syntax, "[shversion]" in splited_type_syntax)
						if '[sqversion]' in splited_type_syntax:
							final_seq = splited_file[splited_type_syntax.index('[sqversion]')]
						if '[shversion]' in splited_type_syntax:
							final_shot = splited_file[splited_type_syntax.index('[shversion]')]
						if '[name]' in splited_type_syntax:
							final_name = splited_file[splited_type_syntax.index('[name]')]
							#print("FOUND A NAME %s"%final_name)
						if '[lod]' in splited_type_syntax:
							final_lod = splited_file[splited_type_syntax.index("[lod]")]


					if "[lod]" in splited_type_syntax:
						#get min and maximum value
						min_value = self.additionnal_settings["lodInterval"][0]
						max_value = self.additionnal_settings["lodInterval"][1]

						#split the lod item in the filename
						splited_item = splited_file[splited_type_syntax.index("[lod]")].split("lod")
						if len(splited_item) != 2:
							error=True 
						if (splited_item[0] != "") or (splited_item[1].isdigit() == False):
							error=True 
						else:
							index = int(splited_item[1])

							if (index < min_value) or (index > max_value):
								error=True
					if kind_selection != None:
						for kind in kind_selection:
							
							try:
								kind_index = splited_type_syntax.index('[type]')
							except:
								mc.error("No kind in the syntax!")
								return
							if splited_file[kind_index] != kind:

								error=True


					if seq_selection != None:
						for seq in seq_selection:
							try:
								seq_index = splited_type_syntax.index("[sqversion]")
							except:
								mc.error("No sequence in the syntax!")
								return 

							if splited_file[seq_index] != seq:
								error = True 

					if shot_selection != None:
						for shot in shot_selection:
							try:
								shot_index = splited_type_syntax.index('[shversion]')
							except:
								mc.error("No shot in the syntax!")
								return 
							if splited_file[shot_index] != shot:

								error=True

					if mc.checkBox(self.projectcontent_checkbox, query=True, value=True)==False:
						if name_selection != None:
							for name in name_selection:
								try:
									name_index = splited_type_syntax.index("[name]")
								except:
									mc.error("No name in the syntax!")
									return

								if len(splited_file) == len(splited_type_syntax):
									if splited_file[name_index] != name:
										error=True



		




					if error==True:
						return False, False, False, False
					else:
						#print(final_name, current_type, final_seq, final_shot)
						return final_name, current_type, final_seq, final_shot



		




		
				





	def save_syntax_function(self, event):
		#check selection of the textscrolllist
		selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		new_content = mc.textField(self.setting_syntax_textfield, query=True, text=True)

		if (self.letter_verification_function(new_content)==None) or (self.letter_verification_function(new_content)==False):
			mc.error("You have to write a new syntax to replace the old one!")
			return
		if selection == None:
			mc.error("You have at least one setting to change!")
			return 
		else:
			selection = selection[0]
			#get list of informations from settings dictionnary
			keys = list(self.settings.keys())
			values = list(self.settings.values())


			self.settings[selection][0] = new_content

			"""

			for rank in selection:
				for i in range(0, len(keys)):
					#check if at the specified rank
					if (int(rank)-1) == i:
						self.add_log_content_function("[%s] New syntax has been saved" % keys[i])
						values[i][0] = new_content
			for i in range(0, len(keys)):
				self.settings[keys[i]] = values[i]

			"""

			self.save_settings_file()
			self.deselect_all_lists()
			mc.warning("Nomenclature saved successfully for [%s]" % selection)



	def deselect_all_lists(self):
		mc.textScrollList(self.type_list, edit=True, deselectAll=True)
		mc.textScrollList(self.name_list, edit=True, deselectAll=True)
		mc.textScrollList(self.kind_list, edit=True, deselectAll=True)
		mc.textScrollList(self.result_list, edit=True, deselectAll=True)











	def define_default_folder_function(self, event):
		#get pipeline folder
		project_name = mc.textField(self.project_label, query=True, text=True)
		#get selection in textscrolllist
		selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		if (selection == None):
			mc.error("You have to select a type to define a new default folder!")
			return
		else:
			#open a file dialogue interface
			if os.path.isdir(project_name)==False:
				new_default_folder = mc.fileDialog2(ds=1, fm=3)
			else:
				new_default_folder = mc.fileDialog2(ds=1, fm=3, dir=project_name)

			if new_default_folder == None:
				mc.warning("No default folder saved!")
				return
			else:
				for key, value in self.settings.items():
					if key == selection[0]:
						value[2] = new_default_folder[0]
						self.settings[key] = value
						self.save_settings_file()

						mc.button(self.setting_default_folder_button, edit=True, label=new_default_folder[0])
		

		



	def import_in_scene_function(self, command, event):
		#get the selection in the file list
		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		folder_name = (mc.textField(self.project_label, query=True, text=True))
		#project_name = os.path.basename(os.path.normpath(folder_name))

		if favorite_selection != None:
			#get the filepath in the user settings
			filepath = self.user_settings["FavoriteFiles"][favorite_selection[0]]
			try:
				if command == False:
					mc.file(filepath, i=True, uns=True)
				if command == True:
					mc.file(filepath, r=True, uns=True, ns="")
				mc.warning("File imported successfully [%s]!"%filepath)
				return 
			except:
				mc.error("Impossible to import this file [%s]!"%filepath)
				return
		if file_selection == None:
			mc.error("You have to select at least one file!")
			return 


		if mc.checkBox(self.index_checkbox, query=True, value=True)==False:
			#try to find file in the folder
			for item in file_selection:
				for r, d, f in os.walk(folder_name):
					for file in f:
						if file == item:
							self.add_log_content_function("[%s] File found in project" % item)
							if os.path.isfile(os.path.join(r, item))==True:
								try:
									if command==False:
										mc.file(os.path.join(r, item), i=True, uns=True, ns="")
									if command==True:
										mc.file(os.path.join(r, item), r=True, uns=True, ns="")
									#self.add_log_content_function("[%s] File imported successfully"%item)
								except:
									mc.error("Impossible to import file!")
									return
		else:
			"""
			check the name of the file in the pipeline index and get the path
			then import the file
			"""
			for file, file_data in self.pipeline_index.items():
				if file in file_selection:
					if os.path.isfile(os.path.join(file_data["path"], file))==True:
						try:
							if command==False:
								mc.file(os.path.join(file_data["path"],file),i=True, uns=True, ns="")
							else:
								mc.file(os.path.join(file_data["path"],file),r=True, uns=True, ns="")
						except:
							mc.error("Impossible to import file!")
							return
				



	def clean_function(self, event):
		nodes_list = mc.ls(st=True)
		node_name = []
		node_type = []

		for i in range(0, len(nodes_list)):
			if i%2 == 0:
				node_name.append(nodes_list[i])
			else:
				node_type.append(nodes_list[i])
		#for each node check its connection
		for item in node_name:
			print(mc.listConnections(item))




	def delete_type_function(self, event):
		#get the value in the type textscrolllist
		type_list = mc.textScrollList(self.settings_type_list, query=True, si=True)

		if type_list == None:
			mc.error("You have to select at least one type to delete!")
			return

		else:
			
			for item in type_list:
				#delete the corresponding key in the dictionnary
				self.settings.pop(item)
				self.settings_dictionnary.pop(item)

		
			
			self.save_settings_file()
			keys = list(self.settings.keys())
			mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=keys)
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True)


	def save_project_name_function(self, event):
		#check the content of the textfield
		content = mc.textField(self.settings_project_folder_textfield, query=True, text=True)
		if self.letter_verification_function(content)==False:
			mc.error("You have to write a name to save!")
			return
		for key, value in self.settings.items():
			value[4] = content
			self.settings[key] = value
		mc.warning("Maya project name saved successfully!")
		return
			

	def create_type_function(self, event):
		"""
		take the content of the type name textfield / setting syntax textfield
		and create a new setting

		if there is no content in the syntax field put "" in the syntax
		#so the program will detect that it's impossible to search for file
		"""
		setting_name_content = mc.textField(self.setting_type_textfield, query=True, text=True)
		setting_syntax_content = mc.textField(self.setting_syntax_textfield, query=True, text=True)
		setting_keyword_content = mc.textField(self.setting_keyword_textfield, query=True, text=True)

		print(setting_name_content)
		if (self.letter_verification_function(setting_name_content)==False) or (self.letter_verification_function(setting_name_content)==None):
			mc.error("You have to define a name!")
			return

		if (self.letter_verification_function(setting_syntax_content)==False) or (self.letter_verification_function(setting_syntax_content)==None):
			mc.warning("No nomenclature saved with the new Kind!")
			setting_syntax_content = "NoSyntaxDefined"
		if (self.letter_verification_function(setting_keyword_content) == False) or (self.letter_verification_function(setting_keyword_content)==None):
			mc.warning("No keyword saved with the new Kind!")
			setting_keyword_content = "NoKeywordDefined"

		if (setting_name_content in self.settings)==True:
			mc.error("An existing type with the same name already exist!")
			return
		else:
			#delete all the buttons on the GUI
			#self.delete_button_function()
			#create the new key in the dictionnary
			
			self.settings[setting_name_content] = [setting_syntax_content, setting_keyword_content, None, [None, None], "maya"]
			self.settings_dictionnary[setting_name_content] = self.file_type
			self.save_settings_file()
			keys = list(self.settings.keys())
			mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=keys)
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True)
			

		

	def save_keyword_function(self, event):
		try:
			selection = mc.textScrollList(self.settings_type_list, query=True, sii=True)[0]
		except TypeError:
			mc.error("You have to select one Kind to change in the list!")
			return
		content = mc.textField(self.setting_keyword_textfield, query=True, text=True)

		#check if the content contain something
		if (self.letter_verification_function(content)==False) or (self.letter_verification_function(content)==None):
			mc.error("You have to define a new keyword!")
			return
		keyword_exist = False
		for key, value in self.settings.items():
			if value[1] == content:
				keyword_exist = True
		if keyword_exist == True:
			mc.error("This keyword is already taken!")
			return
		else:
			
			#change the value in the dictionnary
			keys = list(self.settings.keys())
			values = list(self.settings.values())

			for i in range(0, len(keys)):
				if i == (int(selection) - 1):
					self.settings[keys[i]] = [values[i][0], content, values[i][2]]	
			#save the new dictionnary
			self.save_settings_file()
			self.refresh_export_type_list_function()
			mc.warning("Keyword saved successfully!")
			




	def create_file_kind_function(self, event):
		type_selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		if type_selection == None:
			mc.error("You have to select at least one Type Name!")
			return
		new_kind_name = mc.textField(self.create_file_kind_textfield, query=True, text=True)
		if (self.letter_verification_function(new_kind_name)==False) or (self.letter_verification_function(new_kind_name)==None):
			mc.error("You have to define a name for the new type!")
			return
		else:
			for item in type_selection:
				settings_list = list(self.settings_dictionnary[item])
				settings_list.append(new_kind_name)
				self.settings_dictionnary[item] = settings_list
			self.save_settings_file()
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[item])
			mc.warning("Item created successfully!")
			return

	def delete_file_kind_function(self, event):
		type_selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		kind_selection = mc.textScrollList(self.settings_type_textscrolllist, query=True, si=True)
		try:
			if len(type_selection)==None or len(kind_selection)==None:
				mc.error("You have to select a Type Name and a type to delete!")
				return
		except:
			mc.error("You have to select a Type Name and a type to delete!")
		else:
			settings_list = list(self.settings_dictionnary[type_selection[0]])
			for item in kind_selection:
				settings_list.remove(item)

			self.settings_dictionnary[type_selection[0]] = settings_list
			self.save_settings_file()
			mc.warning("Item removed successfully!")
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[type_selection[0]])
			return

	def rename_file_kind_function(self, event):
		#take the content in textfield
		textfield_content = mc.textField(self.create_file_kind_textfield, query=True, text=True)

		if (self.letter_verification_function(textfield_content))==False or (self.letter_verification_function(textfield_content))==None:
			mc.error("You have to define a new name!")
			return
		else:
			type_selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
			kind_selection = mc.textScrollList(self.settings_type_textscrolllist, query=True, si=True)

			if (type_selection==None) or (kind_selection==None):
				mc.error("You have to select a file type to rename!")
				return
			else:
				#rename in the dictionnary
				settings_list = list(self.settings_dictionnary[type_selection[0]])

				for i in range(0, len(settings_list)):
					if (settings_list[i] in kind_selection)==True:
						settings_list[i] = textfield_content
				self.settings_dictionnary[type_selection[0]] = settings_list
				self.save_settings_file()
				mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=settings_list)
				mc.warning("Item renamed successfully!")
				return

	






	def open_website_for_edit_function(self):
		
		sites_web = [
			"https://tinder.com",
		    "https://bumble.com",
		    "https://www.match.com",
		    "https://www.eharmony.com",
		    "https://www.okcupid.com",
		    "https://www.pof.com",
		    "https://pornhub.com",
		    "https://www.zoosk.com",
		    "https://www.elitesingles.com",
		    "https://hinge.co",
		    "https://coffeemeetsbagel.com",
		    "http://www.theuselessweb.com",
		    "http://www.pointerpointer.com",
		    "https://www.boredpanda.com",
		    "http://www.iamawesome.com",
		    "http://www.zombo.com",
		    "http://www.theuselesswebindex.com",
		    "https://thisissand.com",
		    "http://app.thefacesoffacebook.com",
		    "http://koalastothemax.com",
		    "http://cat-bounce.com",
		    "http://thenicestplaceontheinter.net",
		    "https://littlealchemy2.com",
		    "http://findtheinvisiblecow.com",
		    "http://www.fallingfalling.com",
		    "http://www.theuselessweb.com",
		    "http://www.pointerpointer.com",
		    "https://www.boredpanda.com",
		    "http://www.iamawesome.com",
		    "http://www.zombo.com",
		    "http://www.theuselesswebindex.com",
		    "https://thisissand.com",
		    "http://app.thefacesoffacebook.com",
		    "http://koalastothemax.com",
		    "http://cat-bounce.com",
		    "http://thenicestplaceontheinter.net",
		    "https://littlealchemy2.com",
		    "http://findtheinvisiblecow.com",
		    "http://www.fallingfalling.com",
		    "http://www.sanger.dk",
		    "http://www.thesecretdoor.com",
		    "http://www.theuselesswebbutton.com",
		    "https://www.mapcrunch.com",
		    "http://www.instant-no-button.com",
		    "http://www.baekdal.com/fun/passwords",
		    "https://www.asciiart.eu",
		    "http://heeeeeeeey.com",
		    "https://www.donothingfor2minutes.com",
		    "http://www.staggeringbeauty.com",
		    "https://www.burstuniverse.com",
		    "http://www.patience-is-a-virtue.org",
		    "https://www.pointerpointer.com",
		    "https://www.koalastothemax.com",
		    "https://www.windows93.net",
		    "http://www.sadforjapan.com",
		    "http://weirdorconfusing.com",
		    "http://randomcolour.com",
		    "https://pleasetouchme.herokuapp.com",
		    "https://corgiorgy.com",
		    "https://www.rainymood.com",
		    "https://pointerpointer.com",
		    "https://partridgegetslucky.com",
		    "https://www.eel-slap.com",
		    "http://www.secretsfornicotine.com",
		    "http://whitetrash.nl",
		    "http://www.yesnoif.com",
		    "http://www.isitchristmas.com",
		    "https://nooooooooooooooo.com",
		    "http://www.donothingfor2minutes.com",
		    "https://www.arkive.org",
		    "https://thequietplaceproject.com",
		    "http://www.lingscars.com",
		    "https://www.rockpaperweight.com",
		    "http://www.muchbetterthanthis.com",
		    "https://www.nobodyhere.com",
		    "http://www.incredibox.com",
		    "http://www.fallingfalling.com",
		    "http://www.trypap.com",
		    "http://www.drawastickman.com",
		    "http://www.bury.me",
		    "https://www.tane.us",
		    "http://www.koalastothemax.com",
		    "https://endless.horse",
		    "https://findtheinvisiblecow.com",
		    "https://alwaysjudgeabookbyitscover.com",
		    "https://www.theuselessweb.com",
		    "http://iloveyoulikeafatladylovesapples.com",
		    "https://www.boredpanda.com",
		    "https://chihuahuaspin.com",
		    "https://partridgegetslucky.com",
		    "http://www.hackertyper.com",
		    "https://www.haneke.net",
		    "http://ninjaflex.com",
		    "https://www.hristu.net",
		    "https://www.thepixelgarden.net",
		    "http://www.taghua.com",
		    "https://www.rainymood.com",
		    "http://r33b.net",
		    "https://chickenonaraft.com",
		    "http://nooooooooooooooo.com",
		    "http://www.unicodesnowmanforyou.com",
		    "https://wutdafuk.com",
		    "https://www.pointerpointer.com",
		    "http://iloveyoulikeafatladylovesapples.com",
		    "http://heeeeeeeey.com",
		    "https://www.zoomquilt.org",
		    "https://eelslap.com",
		    "https://strobe.cool",
		    "https://www.burstuniverse.com",
		    "https://www.patience-is-a-virtue.org",
		    "https://ducksarethebest.com",
		    "https://omfgdogs.com",
		    "https://papertoilet.com",
		    # Ajoutez les sites supplémentaires ici
		]
		
		website = sites_web[randrange(0, len(sites_web)-1)]
		webbrowser.open(website)
		


	def print_color_for_publish_function(self):
		
		
		rainbow_colors = [(1, 0, 0), (1, 0.5, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (0.5, 0, 1), (1, 0, 1)]

	
		frame_duration = 10

		mc.inViewMessage( amg='<hl>CONGRATS FOR PUBLISHING\nA NEW FILE</hl>.', pos='midCenter', fade=True )
		for color in rainbow_colors:
		    # Change la couleur de fond du viewport
		    mc.displayRGBColor("background", *color)
		    # Attend le temps spécifié pour chaque couleur
		    mc.currentTime(mc.currentTime(q=True) + frame_duration)
		    sleep(0.2)

		mc.displayRGBColor("background", *(0.3,0.3,0.3))
		congrats_rank = randrange(0,8)
		if os.path.isfile("Data/icons/congrats%s.gif"%congrats_rank)==True:
		
			if os.path.isdir(self.program_folder)==True:

				webbrowser.open(os.path.join(self.program_folder, "Data/icons/congrats%s.gif"%congrats_rank))



			
			



						










	def archive_in_project_function(self, event):
		#check the content of the selection
		selection = mc.textScrollList(self.result_list, query=True, si=True)
		if (len(selection) == 0) or (selection == None):
			mc.error("You have to select something to create put it in the project archive!")
			return
		folder = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(os.path.join(folder, "PipelineManagerData"))==False:
			mc.error("You have to set the pipeline folder first!")
			return
		#find the path of the selection files
		for i in range(0, len(selection)):
			for r, d, f in os.walk(folder):
				for file in f:
					if file == selection[i]:
						selection[i] = os.path.join(r, file)
						

		if os.path.isfile(os.path.join(folder, "PipelineManagerData/PipelineArchive.zip"))==False:
			with ZipFile(os.path.join(folder, "PipelineManagerData/PipelineArchive.zip"), "w", ZIP_DEFLATED) as zip_archive:
				for i in range(0, len(selection)):
					zip_archive.write(selection[i], os.path.basename(selection[i]))
					print("[%s/%s]"%(i+1, len(selection)),os.path.basename(selection[i]), " - ARCHIVED")
			mc.warning("Project archive created")

		mc.warning("Files successfully added to the archive!")
		return







	def save_folder_preset_function(self, event):
		#check the content of textfields
		content1 = mc.textField(self.settings_editfolder_textfield, query=True, text=True)
		content2 = mc.textField(self.settings_publishfolder_textfield, query=True, text=True)
		
		value1 = self.letter_verification_function(content1)
		value2 = self.letter_verification_function(content2)

		print(content1, content2, value1, value2)
				
		if (value1 == False) or (value1 == None):
			content1 = None 
		if (value2 == False) or (value2 == None):
			content2 = None
		for key, value in self.settings.items():
			value[3] = [content1, content2]
			self.settings[key] = value 
			print(self.settings[key])
		self.save_settings_file()






	def searchbar_function(self, event):
		#or limit to the project?
		#search for files in the whole pipeline?
		final_extension_list = []

		project_limit = mc.checkBox(self.searchbar_checkbox, query=True, value=True)
		scenes_limit = mc.checkBox(self.scenes_checkbox, query=True, value=True)
		items_limit = mc.checkBox(self.items_checkbox, query=True, value=True)
		textures_limit = mc.checkBox(self.textures_checkbox, query=True, value=True)
		searchbar_content = mc.textField(self.main_assets_searchbar, query=True, text=True)

		if scenes_limit == True:
			final_extension_list = final_extension_list + self.additionnal_settings["3dSceneExtension"]
		if items_limit == True:
			final_extension_list = final_extension_list + self.additionnal_settings["3dItemExtension"]
		if textures_limit ==True:
			final_extension_list = final_extension_list + self.additionnal_settings["texturesExtension"]


		

		if (self.letter_verification_function(searchbar_content)==False) or (self.letter_verification_function(searchbar_content)==None):
			mc.error("Nothing to search!")
			return
		searchbar_content = searchbar_content.split(";")
		for i in range(len(searchbar_content)):
			searchbar_content[i] = searchbar_content[i].lower()

		if project_limit == True:
			starting_folder = mc.workspace(query=True, active=True)
			if starting_folder == None:
				mc.error("Impossible to search in project!")
				return

		else:
			starting_folder = mc.textField(self.project_label, query=True, text=True)
			if os.path.isdir(starting_folder)==False:
				mc.error("Impossible to search!")
				return

		
        
		if mc.checkBox(self.index_checkbox, query=True, value=True)==False:
			#list all the files in defined directory
			file_list = []
			total_files = int(sum([len(files) for root, dirs, files in os.walk(starting_folder)]))
			i=0
			self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting", min=0, max=total_files)

			print("Searching...")
			for r,d,f in (os.walk(starting_folder)):

				print("Checking folder [%s]" % r)
				mc.progressWindow(edit=True, progress=i, status="Processing...")

				if ("PipelineManagerData" in d)==True:
					d.remove("PipelineManagerData")

				for file in f:
					i+=1
					print("[%s | %s]		checking - %s"%(i,total_files,file))
					valid=True

					if len(final_extension_list) != 0:
						if (os.path.splitext(file)[1] in final_extension_list) != True:
							continue

					error = False
					for keyword in searchbar_content:
						if (keyword in file.lower()) == False:
							error=True 

					if error == False:
						file_list.append(file)
				
			mc.progressWindow(endProgress=True)
		else:
			file_list = []
			for file, file_data in self.pipeline_index.items():
				error=False
				for keyword in searchbar_content:
					if keyword not in file.lower():
						error=True 
				if error==False:
					file_list.append(file)

                
     	
        
		mc.textScrollList(self.result_list, edit=True, removeAll=True, append=file_list)



	def delete_favorite_file_function(self, event):
		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		if favorite_selection == None:
			mc.error("Nothing to delete!")
			return
		favorite_data = self.user_settings["AdditionalData"]["FavoriteFiles"]
		favorite_data.pop(favorite_selection[0])
		self.user_settings["FavoriteFiles"] = favorite_data 
		self.save_settings_file()
		self.apply_user_settings_function()




	def open_location_function(self, data, event):

		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		if favorite_selection != None:
			#get the user settings
			file_to_open = self.user_settings["AdditionalData"]["FavoriteFiles"][favorite_selection[0]]

			if data == "folder":
				#get the folder in user settings
				folder_path = os.path.dirname(self.user_settings["AdditionalData"]["FavoriteFiles"][favorite_selection[0]])
				mc.fileDialog2(ds=1, fm=1, dir=folder_path)
				return
			else:

				
				try:
					mc.file(file_to_open, force=True, o=True)
				except:
					mc.error("Impossible to open the file")
				return

		#check selection in result textscrolllist
		selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
		#check the location of the file in the pipeline
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		#go through all the files
		if mc.checkBox(self.index_checkbox, query=True, value=True)==False:
			for r, d, f in os.walk(pipeline_path):
				for file in f:
					if os.path.basename(file) == selection:
						#open a browser with the location of that file
						if data == "folder":
							mc.fileDialog2(ds=1, fm=1, dir=r)
						else:
							#open the file
							try:
								mc.file(save=True,type="mayaAscii")
							except:
								mc.warning("Impossible to save the current scene!")
								pass

							try:
								print(os.path.join(r, file))
								print(os.path.isfile(os.path.join(r, file)))	
								mc.file(os.path.join(r, file), force=True,o=True)
							except:
								mc.error("Impossible to open the file!")
								return
						break
		else:
			#go through the index settings and check each file in it
			try:
				path = self.pipeline_index[selection]["path"]
			except:
				mc.error("Impossible to find the file in the pipeline index!")
				return
			subprocess.Popen("explorer %s"%os.path.normpath(path))
			








	def set_project_function(self, event):
		#check the first item of the selection
		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		if favorite_selection == None:
			try:
				
				selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
			except:
				mc.error("You have to select an item first!")
				return
		#get the path of the file
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		pipeline_name = os.path.basename(pipeline_path)
		#get project keyword
		project_name = self.additionnal_settings["mayaProjectName"]


		print(pipeline_path)
		print(pipeline_name)

		"""
		if favorite_selection != None:
			#get the path of the file
			index = False
			favorite_filepath = self.user_settings["FavoriteFiles"][favorite_selection[0]]
			splited_filepath = favorite_filepath.split("/")

			for i in range(0, len(splited_filepath)):
				print(splited_filepath[i], project_name)
				if splited_filepath[i] == project_name:
					index = i
			
			if index == False:
				mc.error("Impossible to find maya project in the favorite filepath!")
				return 
			else:
				splited_filepath = splited_filepath[0:index]
				splited_filepath.append(project_name)
				filepath = "/".join(splited_filepath)
				try:
					mc.workspace(filepath, n=True)
				except:
					mc.warning("Impossible to create maya default folder!")
					try:
						mc.workspace(filepath, o=True)
					except:
						mc.error("Impossible to set the project!")
						return 
				os.chdir(filepath)
				mc.warning("Project path set to : %s"%filepath)
			return"""

		
		print("TRYING TO SET THE PROJECT FDP!")
		index_checkbox = mc.checkBox(self.index_checkbox, query=True, value=True)
		if index_checkbox == True :
			for file, data in self.pipeline_index.items():
				if file == selection:
					#get the path of the file
					#get the maya keyword inside
					path = data["path"]
					splited_path = path.split("/")
					#get maya project index
					if project_name not in splited_path:
						mc.error("Impossible to find maya project keyword in path!")
						return 
					else:
						
						maya_project_index = splited_path.index(project_name)
						project_path = "/".join(splited_path[:maya_project_index+1])
						print("Project path [%s]"%project_path)
						try:

							#print("set project to %s"%project_path)
							mc.workspace(project_path, n=True)
							print("Project created!")
						except:
							try:
								mc.workspace(project_path, o=True)
								print("Project opened!")
							except:
								mc.warning("Impossible to set the project!")
		else:
			for r, d, f in os.walk(pipeline_path):
				for file in f:
					if os.path.basename(file) == selection:
						original_path = os.getcwd()

						"""
						go to path of the file
						"""
						os.chdir(r)
						path = os.getcwd()
						defined = False
						for i in range(0, len(r.split("/"))+1):
							#print(os.getcwd(), os.path.basename(path), project_name)
							if os.path.basename(path) == project_name:
								#set project here!!!
								print("Project path [%s]"%path)
								try:
									mc.workspace(path, n=True)
									print("Project created!")
								except:
									try:
										mc.workspace(path, o=True)
										print("Project opened!")
									except:
										mc.warning("Impossible to set the project!")
								defined=True
								

							
							path = os.path.normpath(path+os.sep+os.pardir)
							os.chdir(path)

						if defined==False:
							mc.error("Impossible to find a project folder for that file!")
							return

















	def open_file_function(self, event):
		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		if favorite_selection != None:
			data_favorite = self.user_settings["FavoriteFiles"]
			try:
				mc.file(save=True)
			except RuntimeError:
				mc.warning("Impossible to save current file!")
			mc.file(new=True, force=True)
			mc.file(data_favorite[favorite_selection[0]],o=True)
			mc.warning("File opened successfully")
			self.take_picture_function("test")
		else:
			try:
				selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
			except:
				mc.error("You have to select a file to open!")
				return

		#get path of the scene
		current_scene = mc.file()
		pipeline_path = mc.textField(self.project_label, query=True, text=True)

		if mc.checkBox(self.index_checkbox, query=True, value=True)==True:
			#dig into the pipeline index to search the file if possible
			print(selection, selection in list(self.pipeline_index.keys()))
			if selection in list(self.pipeline_index.keys()):
				#try to open the file
				#get the path of the file to open in the dictionnary
				fullpath = os.path.join(self.pipeline_index[selection]["path"], selection)
				if os.path.isfile(fullpath) == False:
					mc.error("That file doesn't exists anymore in the pipeline!")
					return 
				else:
					try:
						mc.file(save=True)
					except RuntimeError:
						mc.warning("This file doesn't have any name!")
					mc.file(new=True, force=True)
					mc.file(fullpath, o=True)
					mc.warning("File opened successfully")
					self.take_picture_function("test")
			else:
				mc.error("Impossible to find that file in the current pipeline index!")
				return

		else:
			for r, d, f in os.walk(pipeline_path):
				for file in f:
					if os.path.basename(file) == selection:
						#save current file
						try:
							mc.file(save=True)
						except RuntimeError:
							mc.warning("This file doesn't have any name!")
							
						mc.file(new=True, force=True)
						mc.file(os.path.join(r, file), o=True)
						mc.warning("File opened successfully")
						self.take_picture_function("test")






	def take_picture_function(self, event):
		#get current frame 
		current_frame = int(pm.currentTime(query=True))
		#get the name of the current filename
		current_file = mc.file(query=True, sn=True)
		#check if the file exist in the pipeline
		if os.path.isfile(current_file) == False:
			mc.error("This file isn't saved in your pipeline yet!\nSave it first!")
			return
		current_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0]

		#define the path of the image folder
		#query the value of the pipeline textfield
		pipeline_path = mc.textField(self.project_label, query=True, text=True)

		if os.path.isdir(os.path.join(pipeline_path, "PipelineManagerData/ThumbnailsData"))==False:
			try:
				os.mkdir(os.path.join(pipeline_path, "PipelineManagerData/ThumbnailsData"))
			except:
				mc.error("Impossible to create thumbnail folder in the current pipeline!")
				return
		else:
			path = os.path.join(pipeline_path, "PipelineManagerData/ThumbnailsData/Thumbnail_%s.jpg"%current_filename)
			mc.playblast(fr=current_frame, v=False, format="image", c="jpg", orn=False, wh=[300,300],cf=path)

			mc.warning("Picture saved!\n%s"%path)
			return





	def search_for_thumbnail_function(self):
		self.search_for_note_function()
		#get the name of the selected item
		selection = os.path.splitext(mc.textScrollList(self.result_list, query=True, si=True)[0])[0]
		#get the name of the current project
		current_project = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(os.path.join(current_project, "PipelineManagerData/ThumbnailsData"))==False:
			mc.error("Thumbnails folder doesn't exist in that pipeline!")
			return 
		if os.path.isfile(os.path.join(current_project, "PipelineManagerData/ThumbnailsData/Thumbnail_%s.jpg"%selection))==False:
			print(os.path.join(current_project, "PipelineManagerData/ThumbnailsData/Thumbnail_%s"%selection))
			mc.warning("image not found!")
			return
		else:
			mc.image(self.image_box, edit=True,image=os.path.join(current_project,"PipelineManagerData/ThumbnailsData/Thumbnail_%s.jpg"%selection))
			mc.warning("image set!")
			return



	def save_current_scene_function(self, event):
		try:
			mc.file(save=True)
		except RuntimeError:
			return
		else:	
			#save new picture of that scene
			self.take_picture_function("test")	



	def save_additionnal_settings_function(self, command, event):
		#get value of each checkbox
		searchbar_limit = mc.checkBox(self.searchbar_checkbox, query=True, value=True)
		folder_limit = mc.checkBox(self.folder_checkbox, query=True, value=True)
		scenes = mc.checkBox(self.scenes_checkbox, query=True, value=True)
		items = mc.checkBox(self.items_checkbox, query=True, value=True)
		textures = mc.checkBox(self.textures_checkbox, query=True, value=True)
		folder = mc.checkBox(self.folder_checkbox, query=True, value=True)

		if command == "folder":
			if folder_limit == True:
				mc.checkBox(self.searchbar_checkbox, edit=True, value=False)
			else:
				mc.checkBox(self.searchbar_checkbox, edit=True, value=True)
		if command == "project":
			if searchbar_limit == True:
				mc.checkBox(self.folder_checkbox, edit=True, value=False)
			else:
				mc.checkBox(self.folder_checkbox, edit=True, value=True)

		#get each extension list
		scenes_extension_list = mc.textField(self.assets_scene_extension_textfield, query=True, text=True).split(";")
		items_extension_list = mc.textField(self.assets_items_extension_textfield, query=True, text=True).split(";")
		textures_extension_list = mc.textField(self.assets_textures_extension_textfield, query=True, text=True).split(";")

		#get new lod values in intfield
		#check that values are usable
		lod_minimum_value = mc.intField(self.lodminimumvalue_intfield, query=True, value=True)
		lod_maximum_value = mc.intField(self.lodmaximumvalue_intfield, query=True, value=True)

		if command == "lod_minimum":
			if lod_minimum_value >= lod_maximum_value:
				mc.warning("Invalid minimum lod value!\nOld value restored")

				lod_minimum_value = self.additionnal_settings["lodInterval"][0]
				mc.intField(self.lodminimumvalue_intfield, edit=True, value=self.additionnal_settings["lodInterval"][0])

		if command == "lod_maximum":
			if lod_maximum_value <= lod_minimum_value:
				mc.warning("Invalid maximum lod value!\nOld value restored")

				lod_maximum_value = self.additionnal_settings["lodInterval"][1]
				#change the new value by the old value in the intfield!
				mc.intField(self.lodmaximumvalue_intfield, edit=True, value=self.additionnal_settings["lodInterval"][1])




		#print(mc.checkBox(self.searchbar_checkbox, query=True, value=True), mc.checkBox(self.folder_checkbox, query=True, value=True))

		#self.additionnal_settings["checkboxValues"] = [mc.checkBox(self.searchbar_checkbox, query=True, value=True), mc.checkBox(self.folder_checkbox, query=True, value=True), scenes, items, textures, folder]
		self.additionnal_settings["3dSceneExtension"] = scenes_extension_list
		self.additionnal_settings["3dItemExtension"] = items_extension_list
		self.additionnal_settings["texturesExtension"] = textures_extension_list
		self.additionnal_settings["lodInterval"] = [lod_minimum_value, lod_maximum_value]

		
		self.user_settings = {
			"CheckboxValues": {
				"lastsyntax_checkbox":mc.checkBox(self.displayonlylastsyntax_checkbox, query=True, value=True),
				"index_checkbox": mc.checkBox(self.index_checkbox, query=True, value=True),
				"projectcontent_checkbox":mc.checkBox(self.projectcontent_checkbox, query=True, value=True),
				"searchbar_checkbox":mc.checkBox(self.searchbar_checkbox, query=True, value=True),
				"folder_checkbox":mc.checkBox(self.folder_checkbox, query=True, value=True),
				"scenes_checkbox":mc.checkBox(self.scenes_checkbox, query=True, value=True),
				"items_checkbox":mc.checkBox(self.items_checkbox, query=True, value=True),
				"textures_checkbox":mc.checkBox(self.textures_checkbox, query=True, value=True),

				"archivemenu_projectcheckbox":mc.checkBox(self.archivemenu_projectcheckbox, query=True, value=True),
				"archivemenu_pipelinecheckbox":mc.checkBox(self.archivemenu_pipelinecheckbox, query=True, value=True),

				#"render_texture_manual_checkbox":mc.checkBox(self.render_texture_manual_checkbox, query=True, value=True),
				#"render_texture_automatic_checkbox":mc.checkBox(self.render_texture_automatic_checkbox, query=True, value=True),
				#"render_texture_limit_project":mc.checkBox(self.render_texture_limit_project, query=True, value=True),
				#"render_texture_udim_checking":mc.checkBox(self.render_texture_udim_checking, query=True, value=True),

				"export_current_folder_checkbox":mc.checkBox(self.export_current_folder_checkbox, query=True, value=True),
				"export_custom_folder_checkbox":mc.checkBox(self.export_custom_folder_checkbox, query=True, value=True),
				"export_assist_folder_checkbox":mc.checkBox(self.export_assist_folder_checkbox, query=True, value=True),
				"export_projectassist_folder_checkbox":mc.checkBox(self.export_projectassist_folder_checkbox, query=True, value=True),
				"export_item_checkbox":mc.checkBox(self.export_item_checkbox, query=True, value=True),
				"export_edit_name_checkbox":mc.checkBox(self.export_edit_name_checkbox, query=True, value=True),
				"export_backup_publish_checkbox":mc.checkBox(self.export_backup_publish_checkbox, query=True, value=True),
				"export_shader_checkbox":mc.checkBox(self.export_shader_checkbox, query=True, value=True),
			},
			"AdditionalData": {
				"FavoriteFiles": self.user_settings["AdditionalData"]["FavoriteFiles"],
				"ExportRaimbow": self.user_settings["AdditionalData"]["ExportRaimbow"],
				"ExportWebsite": self.user_settings["AdditionalData"]["ExportWebsite"],
			}
		}


		"""
		self.default_additional_settings = {
			"checkboxValues":[False, True, False, False],
			"3dSceneExtension":["ma","mb"],
			"3dItemExtension":["obj", "fbx"],
			"texturesExtension":["png", "tif","tiff","tex", "exr", "jpg"],
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"]
		}
		"""
		self.save_settings_file()



		
	def define_export_nomenclature_function(self, status):
		type_selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)
		kind_selection = mc.textScrollList(self.export_kind_textscrolllist, query=True, si=True)

		#print(type_selection)
		#print(kind_selection)


		if type_selection == None:
			mc.error("You have to select a type!")
			return
		nomenclature = self.settings[type_selection[0]]
		if ("[type]" in nomenclature) and (kind_selection == None):
			mc.error("You have also to select a kind!")
			return
		else:
			#get the nomenclature of the current type
			nomenclature_data = self.settings[type_selection[0]][0]
			keyword = self.settings[type_selection[0]][1]
			defaultfolder = self.settings[type_selection[0]][2]

			if type(nomenclature_data) != list:
				nomenclature_data = [nomenclature_data]


			splited_nomenclature = nomenclature_data[-1].split("_")
			splited_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0].split("_")
			"""
			print(type_selection[0])
			print(splited_nomenclature)
			print(splited_filename)"""

			final_filename = []

			for i in range(0, len(splited_nomenclature)):
				if splited_nomenclature[i] == "[type]":
					final_filename.append(kind_selection[0])
				#print(splited_nomenclature[i])
				if splited_nomenclature[i] == "[key]":
					#print("nique tes grands morts maya!")
					#print(type_selection[0])
					final_filename.append(keyword)
					#final_filename.append(type_selection[0])

				if splited_nomenclature[i] == "[lod]":
					print("LOD DETECTED!")
					#get the content of the intfield for the level of detail
					lod_value = mc.intField(self.export_lod_intfield, query=True, value=True)

					final_filename.append("lod%s"%lod_value)

				if splited_nomenclature[i] == "[artist]":
					artist_name = mc.textField(self.export_artist_name_textfield, query=True, text=True)
					if self.letter_verification_function(artist_name) != True:
						mc.error("Impossible to get the artist name!")
						return
					else:
						final_filename.append(artist_name)

				if splited_nomenclature[i] == "[name]":
					if mc.checkBox(self.export_edit_name_checkbox, query=True, value=True)==True:
						#go through the actual filename and try to get the keyword to get the nomenclature
						#print(list(self.settings.keys()))
						actual_keyword = None
						actual_name = None

						if len(splited_filename)==0:
							mc.error("Impossible to get the name in the current filename!")
							return
						for word in splited_filename:
							for setting_name, setting_content in self.settings.items():
								setting_syntax_list = setting_content[1]
								if word == setting_content[1]:
									for setting_syntax in setting_syntax_list:
										actual_keyword = setting_content[1]
										if ("[name]" in setting_syntax.split("_")) == False:
											mc.error("Impossible to get the name from the actual filename!")
											return
										else:
											actual_name = splited_filename[setting_content[0].split("_").index("[name]")]
											break
						if( actual_keyword == None) or (actual_name == None):
							mc.error("Impossible to get the actual name of the file to create the filename!")
							return
						else:
							#print(actual_name)
							final_filename.append(actual_name)
					else:
						#try to get the content of the textfield
						content = mc.textField(self.export_edit_name_textfield, query=True, text=True)
						if (self.letter_verification_function(content)==True):
							#print(content)
							final_filename.append(content)
						else:
							mc.error("Impossible to get the name in textfield!")
							return


				if splited_nomenclature[i] == "[version]":
					#if mc.checkBox(self.export_edit_version_checkbox, query=True, value=True) == False:
						#try to get the version in textfield
					if status == "publish":
						content = "publish"
					else:
						content = mc.intField(self.export_edit_version_intfield, query=True, value=True)
						if len(list(str(content))) == 1:
							content = "v00%s"%content 
						else:
							content = "v0%s"%content 

					final_filename.append(content)

				if splited_nomenclature[i] == "[sqversion]":
					content = str(mc.intField(self.export_edit_sequence_intfield, query=True, value=True))
					if len(list(content))==1:
						value = "sq00%s"%content 
					else:
						value = "sq0%s"%content
					final_filename.append(value)

				if splited_nomenclature[i] == "[shversion]":
					content = str(mc.intField(self.export_edit_shot_intfield, query=True, value=True))
					if len(list(content))==1:
						value = "sh00%s"%content 
					else:
						value = "sh0%s"%content
					final_filename.append(value)

				if splited_nomenclature[i] == "[project]":
					if self.project_path == None:
						mc.error("Impossible to get project name because project isn't defined!")
						return
					else:
						final_filename.append(os.path.basename(self.project_path))

				
			
			#print(final_filename)
			return "_".join(final_filename)+".ma"





	def define_export_path_function(self, filename, statut):
		"""
		--> export in current folder
		--> export in same folder
		--> default folder assist
			DEFINE PATH FROM VARIABLES
		"""

		"""
		list of variables for path
		"""
		type_selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)
		kind_selection = mc.textScrollList(self.export_kind_textscrolllist, query=True, si=True)
		splited_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0].split("_")

		if (mc.checkBox(self.export_projectassist_folder_checkbox, query=True, value=True)==False):
			if type_selection == None:
				mc.error("You have to select a type!")
				return

		nomenclature = self.settings[type_selection[0]]
		if (("[type]") in nomenclature) and (kind_selection == None):
			mc.error("You have to select a kind for that nomenclature!")
			return

		if mc.checkBox(self.export_current_folder_checkbox, query=True, value=True)==True:
			#get the path of the current file
			path = os.path.dirname(mc.file(query=True, sn=True))
			if (self.letter_verification_function(path)==True) and (path != None):
				return path
			else:
				mc.error("Impossible to get current filepath!")
				return
		if mc.checkBox(self.export_custom_folder_checkbox, query=True, value=True)==True:
			folder = mc.fileDialog2(fm=3)
			if folder == None:
				mc.error("You have to define one folder!")
				return
			else:
				return folder
				#folder = mc.workspace(query=True, active=True)
		if (mc.checkBox(self.export_assist_folder_checkbox, query=True, value=True)==True) or (mc.checkBox(self.export_projectassist_folder_checkbox, query=True, value=True)==True):
			final_filepath = []
			#check the value of the default folder
			default_folder_path = self.settings[type_selection[0]][2]
			if default_folder_path == None:
				mc.error("Impossible to detect a default folder in settings!")
				return
			splited_default_folder = default_folder_path.split("/")
			print("\nDefault folder found in the settings:")
			print(splited_default_folder)
			for i in range(0, len(splited_default_folder)):
				#KEYWORD CONDITIONS
				#print(type(splited_default_folder[i][0]), type(splited_default_folder[i][-1]))

				if (splited_default_folder[i][0] == "[") and (splited_default_folder[i][-1] == "]"):
					if splited_default_folder[i] == "[Origin]":
						final_filepath.append(self.project_path)



					if splited_default_folder[i] =="[key]":
						final_filepath.append(type_selection[0])

					if splited_default_folder[i] == "[name]":
						if mc.checkBox(self.export_edit_name_checkbox, query=True, value=True)==True:
							#go through the actual filename and try to get the keyword to get the nomenclature
							#print(list(self.settings.keys()))
							actual_keyword = None
							actual_name = None
							for word in splited_filename:
								for setting_name, setting_content in self.settings.items():
									if word == setting_content[1]:
										actual_keyword = setting_content[1]
										if ("[name]" in setting_content[0].split("_")) == False:
											mc.error("Impossible to get the name from the actual filename to create the path!")
											return
										else:
											actual_name = splited_filename[setting_content[0].split("_").index("[name]")]
							if( actual_keyword == None) or (actual_name == None):
								mc.error("Impossible to get the actual name of the file!")
								return
							else:
								final_filepath.append(actual_name)
						else:
							#try to get the content of the textfield
							content = mc.textField(self.export_edit_name_textfield, query=True, text=True)
							if (self.letter_verification_function(content)==True):
								final_filepath.append(content)
							else:
								mc.error("Impossible to get the name in textfield!")
								return


					if splited_default_folder[i] == "[mayaProjectName]":
						final_filepath.append(self.additionnal_settings["mayaProjectName"])
					

					if splited_default_folder[i] == "[type]":
						final_filepath.append(kind_selection[0])


					if splited_default_folder[i] == "[editPublishFolder]":
						if statut=="publish":
							final_filepath.append(self.additionnal_settings["editPublishFolder"][1])
						else:
							final_filepath.append(self.additionnal_settings["editPublishFolder"][0])

					
					if splited_default_folder[i] == "[sqversion]":
						sequence = str(mc.intField(self.export_edit_sequence_intfield, query=True, value=True))
						if len(list(sequence)) == 1:
							sequence = "sq00%s"%sequence 
						else:
							sequence = "sq0%s"%sequence 
						final_filepath.append(sequence)

					if splited_default_folder[i] == "[shversion]":
						sequence = str(mc.intField(self.export_edit_shot_intfield, query=True, value=True))
						if len(list(sequence)) == 1:
							sequence = "sh00%s"%sequence 
						else:
							sequence = "sh0%s"%sequence 
						final_filepath.append(sequence)
					


						
				

				#PROPER VALUES
				else:
					final_filepath.append(splited_default_folder[i])

			if mc.checkBox(self.export_projectassist_folder_checkbox, query=True, value=True)==True:
				#check the current path of the scene
				#get the maya project
				maya_project_name = mc.workspace(query=True, active=True)
				if os.path.isdir(maya_project_name)==False:
					mc.error("Impossible to get current maya project folder!")
					return
				#get project index
				maya_project_index = final_filepath.index(self.additionnal_settings["mayaProjectName"])
				end_of_path = final_filepath[maya_project_index:]
				end_of_path.pop(0)

				final_filepath = "%s/"%maya_project_name + "/".join(end_of_path)
				
				print("RESULT INFORMATIONS")
				print(final_filepath)	
				
			
				return final_filepath

			return "/".join(final_filepath)



		


				



	def export_edit_function(self, info, event):
		filename = self.define_export_nomenclature_function("edit")
		filepath = self.define_export_path_function(filename, "edit")
		include_shader = mc.checkBox(self.export_shader_checkbox, query=True, value=True)
		print("Included shaders ? %s"%include_shader)

		extension = "mayaAscii"
		if (mc.checkBox(self.export_item_checkbox, query=True, value=True)==True):
			extension = "OBJexport"
			filename = os.path.splitext(filename)[0]+".obj"
			print("New extension for the file [OBJexport]")

		final_path = os.path.join(filepath, filename)
		print("Returned filename : [%s]"%filename)
		print("Returned filepath : [%s]"%filepath)
		
		#save the current scene with current filename
		#ask for confirmation
		confirm_saving = mc.confirmDialog( title='Confirm saving', message='Are you sure you want to save / export?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
		if confirm_saving == "No":
			return



		
		

		
		if info == "standard":
			#save the new scene with the new name
			#try to create all folder and save the file
			
			try:
				mc.file(save=True, type=extension)
			except:
				mc.warning("Impossible to save the current file before creating edit!")
			try:
				os.makedirs(filepath, exist_ok=True)
				mc.file(rename=final_path)
				mc.file(save=True, type=extension, f=True, sh=include_shader)

				mc.warning("File saved successfully!")
				print(final_path)
				
			except:
				mc.error("Impossible to save the file!")
				return
		else:
			print("export selection")
			#get maya selection
			selection = mc.ls(sl=True)
			if (len(selection))==0:
				mc.error("No item selected to export!")
				return
			
			os.makedirs(filepath, exist_ok=True)
			mc.file(final_path, es=True, pr=True, f=True, type="mayaAscii", sh=include_shader)
			mc.warning("Selection exported successfully!")
			print(final_path)
	
		

	def create_path_function(self, event):
		os.makedirs(path, exist_ok=True)




	def export_publish_function(self, info, event):

		if (self.letter_verification_function(mc.file(query=True, sn=True)) !=True):
			mc.error("Impossible to publish a scene that is not saved before as edit file!")
			return
		#go through the current filename and try to find keyword to then define version position
		splited_filename = os.path.basename(os.path.splitext(mc.file(query=True, sn=True))[0]).split("_")
		"""
		if mc.file(query=True, sn=True) == None:
			mc.error("You can't publish a scene that is not saved before!")
			return"""
		"""
		for i in range(0, len(splited_filename)):
			for key, value in self.settings.items():
				if value[1] == splited_filename[i]:
					splited_nomenclature = value[0].split("_")

					if "[version]" in splited_nomenclature:
						index = splited_nomenclature.index("[version]")
						#print(splited_filename, len(splited_filename), index)
						splited_filename[index] = self.additionnal_settings["editPublishFolder"][1]

					elif "[name]" in splited_nomenclature:
						index = splited_nomenclature.index("[name]")
						splited_filename[index] = splited_filename[index]+"Publish"
					else:
						mc.error("Impossible to create the publish keyword in the nomenclature!")
						return

		filename = "_".join(splited_filename) + ".ma"
		"""
		filename = self.define_export_nomenclature_function("publish")
		filepath = self.define_export_path_function(filename, "publish")
		final_path = os.path.join(filepath, filename)
		include_shader= mc.checkBox(self.export_shader_checkbox, query=True, value=True)
		print("Shaders included ? %s"%include_shader)

		extension = "mayaAscii"
		if (mc.checkBox(self.export_item_checkbox, query=True, value=True)==True):
			filename = "_".join(splited_filename) + ".obj"
			extension = "OBJexport"
			print("New extension for the file [OBJexport]")

		print("Returned filename : [%s]"%filename)
		print("Returned filepath : [%s]"%filepath)
		#print(final_path)


		#check the value of the overwrite publish or create publish backup if publish is existing
		#if the publish already exists rename it under a new name (file_publish.ma.backup)
		if mc.checkBox(self.export_backup_publish_checkbox, query=True, value=True)==True:
			#check if the publish already exists
			if os.path.isfile(final_path)==True:
				#change the name of the current publish
				try:
					os.rename(final_path, "%s.backup"%final_path)
				except:
					mc.warning("Impossible to create the backup file for the publish!")
					

		#ASK FOR CONFIRMATION
		confirm_saving = mc.confirmDialog( title='Confirm saving', message='Are you sure you want to save / export?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
		if confirm_saving == "No":
			return




		if info == "standard":
			"""
			for each folder that does not exist, 
			create it if it's possible
			"""
			os.makedirs(filepath, exist_ok=True)
			#save the file inside the new path
			#mc.file(save=True, type="mayaAscii")
			mc.file(rename=final_path)
			mc.file(save=True, type=extension)
			
			if self.user_settings["ExportRaimbow"]==True:
				self.print_color_for_publish_function()


		
		#get maya selection
		if info == "selection":
			selection = mc.ls(sl=True)
			if (len(selection))==0:
				mc.error("No item selected to export!")
				return
			
			os.makedirs(filepath, exist_ok=True)
			#mc.file(final_path,force=True, pr=True, es=True, type=extension, sh=include_shader)
			mc.file(final_path, es=True, pr=True, f=True, type="mayaAscii", sh=include_shader)
			mc.warning("Selection exported successfully!")
			"""
			if self.user_settings["ExportRaimbow"]==True:
				self.print_color_for_publish_function()
			"""
			print(final_path)
			return
			


	def save_note_function(self, event):
		#check the selection in file list
		selection = mc.textScrollList(self.result_list, query=True, si=True)
		if selection == None:
			return
		else:
			#save a note for each file selected!
			pipeline_path = mc.textField(self.project_label, query=True, text=True)
			if (pipeline_path==None) or (pipeline_path == "None"):
				mc.error("Impossible to save note!")
				return
			else:
				#take the content of the scrollfield
				note_content = mc.scrollField(self.note_textfield, query=True, text=True)
				try:
					with open(os.path.join(pipeline_path, "PipelineManagerData/NoteData.dll"), "rb") as read_file:
						content = pickle.load(read_file)
				except:
					mc.warning("Note file corrupted or doesn't exists!")
					content = {}

				for file in selection:
					content[file] = note_content

				try:
					with open(os.path.join(pipeline_path, "PipelineManagerData/NoteData.dll"), "wb") as save_file:
						pickle.dump(content, save_file)
				except:
					mc.error("Impossible to save note file!")
					return
				else:
					mc.warning("Note saved successfully!")
					return


	def search_for_note_function(self):
		#try to open the note data
		project_path = mc.textField(self.project_label, query=True, text=True)

		try:
			with open(os.path.join(project_path, "PipelineManagerData/NoteData.dll"), "rb") as read_file:
				note_content = pickle.load(read_file)
		except:
			mc.warning("Impossible to read note file!")
			return
		else:
			selection = mc.textScrollList(self.result_list, query=True, si=True)
			if (selection == None):
				return
			selection = selection[0]
			"""
			print(note_content)
			print(selection in note_content)
			"""
			if selection in note_content:
				note = note_content[selection]
				#replace the note in textfield
				mc.scrollField(self.note_textfield, edit=True, clear=True)
				mc.scrollField(self.note_textfield, edit=True, text=note)

			else:
				print("No note found!")



	def create_template_function(self, event):
		#get the name
		template_name = mc.textField(self.template_textfield, query=True, text=True)
		if (self.letter_verification_function(template_name) != True):
			mc.error("You have to define a name for the new template!")
			return

		#get a folder
		root_folder = mc.fileDialog2(fm=3, ds=1)	
		if root_folder == None:
			mc.error("You have to define a folder architecture to copy!")
			return

		#copy folders inside
		folder_list = []
		past_origin = os.getcwd()
		root_folder = root_folder[0]
		


		root_folder_name = os.path.basename(root_folder)
		for root, dirs, files in os.walk(root_folder):
			for dir_name in dirs:
				
				path =(os.path.join(root, dir_name))
				index = path.index(root_folder_name)

				folder_list.append(path[index:].replace(root_folder_name, ""))
		
		#try to get the dictionnary from the template file in the pipeline
		project_name = mc.textField(self.project_label, query=True, text=True)
		if (project_name == None) or (project_name == "NOne"):
			mc.error("Impossible to get project name!")
			return
		try:
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "rb") as read_file:
				template_dictionnary = pickle.load(read_file)
			#add the new template in the dictionnary
			template_dictionnary[template_name] = folder_list
		except:
			#create the new dictionnary instead
			template_dictionnary = {
				template_name : folder_list
			}
		#save the new dictionnary
		try:
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "wb") as save_file:
				pickle.dump(template_dictionnary, save_file)
			print("New template saved!")
			self.reload_template_function()
			return
		except:
			mc.error("Impossible to save the new template!")
			return



	def reload_template_function(self):

		try:
			project_name = mc.textField(self.project_label, query=True, text=True)
			if (project_name == None) or (project_name == "NOne"):
				mc.error("Impossible to get project name!")
				return
		except:
			project_name = self.project_path
		try:
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "rb") as read_file:
				template_dictionnary = pickle.load(read_file)
		

			mc.textScrollList(self.template_textscrolllist, edit=True, removeAll=True, append=list(template_dictionnary.keys()))
		except:
			mc.warning("Impossible to read template file!")
			return


	def delete_template_function(self, event):

		template_selection = mc.textScrollList(self.template_textscrolllist, query=True, si=True)
		if (template_selection == None) or (len(template_selection) == 0):
			mc.error("You have to select a template to delete!")
			return
		else:
			#open template file
			
			try:
				project_name = mc.textField(self.project_label, query=True, text=True)
				if (project_name == None) or (project_name == "NOne"):
					mc.error("Impossible to get project name!")
					return
			except:
				project_name = self.project_path

			try:
				with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "rb") as read_file:
					template_dictionnary = pickle.load(read_file)
				#mc.textScrollList(self.template_textscrolllist, edit=True, removeAll=True, append=list(template_dictionnary.keys()))
			except:
				mc.warning("Impossible to read template file!")
				return

			for template in template_selection:
				#print(template)
				template_dictionnary.pop(template)
			#save the new dictionnary
			#update the textscrolllist
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"),"wb") as save_file:
				pickle.dump(template_dictionnary, save_file)
			mc.textScrollList(self.template_textscrolllist, edit=True, removeAll=True, append=list(template_dictionnary.keys()))
			mc.warning("Template list updated successfully!")
			return





	def create_new_item_template_function(self, command, event):
		
		item_name = [mc.textField(self.export_edit_name_textfield, query=True, text=True)]
		item_seq = mc.intField(self.export_edit_sequence_intfield, query=True, value=True)
		item_shot = mc.intField(self.export_edit_shot_intfield, query=True, value=True)

		"""
		if (self.letter_verification_function(item_name) == False) or (self.letter_verification_function(item_name) == None):
			item_name = """


		#get informations to create new item architecture
		
		template_name = mc.textScrollList(self.template_textscrolllist, query=True, si=True)
		template_type = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)
		#template_version = mc.intField(self.export_edit_version_intfield, query=True, value=True)
		

		
		if template_name == None:
			mc.error("You have to pick a template!")
			return
		template_name = template_name[0]
		if template_type == None:
			mc.error("You have to pick a type!")
			return

		print(item_name, len(item_name))

		for i in range(0, len(item_name)):
			starting_folder = self.settings[template_type[0]][2]
			print(starting_folder)


			if '[key]' in starting_folder:
				dodge = "[key]"
			if '[sqversion]' in starting_folder:
				dodge = "[sqversion]"
			if '[shversion]' in starting_folder:
				dodge = '[shversion]'
			while os.path.basename(starting_folder) != dodge:
				starting_folder = os.path.dirname(starting_folder)

		
			if ("[Origin]" in starting_folder):
				starting_folder = starting_folder.replace("[Origin]",self.project_path)
				
			if ("[key]" in starting_folder):
				starting_folder = starting_folder.replace("[key]",template_type[0])

			#print(starting_folder, "[name]" in starting_folder)
			if ("[name]" in starting_folder):
				print(self.letter_verification_function(item_name[i]), item_name[i])
				if self.letter_verification_function(item_name[i]) ==True:
					starting_folder = starting_folder.replace("[name]", item_name[i])
				else:
					mc.error("[name] folder impossible to create!")
					return 

			if ("[mayaProjectName]" in starting_folder):
				starting_folder = starting_folder.replace("[mayaProjectName]", self.additionnal_settings["mayaProjectName"])

			if ("[type]" in starting_folder) or ("[editPublishFolder]" in starting_folder):
				mc.error("Impossible to create new item with that default folder architecture!")
				return

			
			if ("[sqversion]" in starting_folder):
				print("sequence detected!")
				if len(list(str(item_seq))) == 1:
					item_seq = "sq00%s"%str(item_seq)
				else:
					item_seq = "sq0%s"%str(item_seq)
				starting_folder = starting_folder.replace("[sqversion]", item_seq)

			if ("[shversion]" in starting_folder):
				print("shot detected!")
				if len(list(str(item_shot))) == 1:
					item_shot = "sh00%s"%str(item_shot)
				else:
					item_shot = "sh0%s"%str(item_shot)
				starting_folder = starting_folder.replace("[shversion]", item_shot)




			#add the name of the new folder to the starting path
			
			if self.letter_verification_function(item_name[i]) ==True:
				starting_folder = os.path.join(starting_folder, item_name[i])
			#check and create all folders of the starting folder
			os.makedirs(starting_folder, exist_ok=True)

			#get the template folder list
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/Template.dll"), "rb") as read_file:
					template_dictionnary = pickle.load(read_file)
			except:
				mc.error("Impossible to read template data!")
				return

			#print(template_name)
			#print(template_dictionnary)
			for key, value in template_dictionnary.items():
				print(key, value)


			if (template_name in template_dictionnary) == False:
				mc.error("Impossible to get template informations!")
				return
			else:
				template_folder_list = template_dictionnary[template_name]

				folder_to_create = []
				for folder in template_folder_list:
					folder_full_path = starting_folder+folder
					folder_to_create.append(folder_full_path.replace('\\', '/'))

				
				#create the folder list
				for folder in folder_to_create:
					try:
						os.mkdir(folder)
						print("Folder created [%s]"%folder)
					except:
						mc.warning("Failed to create folder [%s]"%folder)
						continue

				

			
			




	def hard_rename_function(self, event):
		#get values of checkboxes
		files_rename = mc.checkBox(self.hardrename_checkbox_file, query=True, value=True)
		folders_rename = mc.checkBox(self.hardrename_checkbox_folder, query=True, value=True)

		files_to_rename = []
		folders_to_rename = []

		#check the content to rename
		content_to_replace = mc.textField(self.rename_oldcontent_textfield, query=True, text=True)
		new_content = mc.textField(self.rename_newcontent_textfield, query=True, text=True)

		#define the starting folder of the pipeline
		project_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(project_path) == False:
			mc.error("Impossible to define the starting folder of the pipeline!")
			return 




	def rename_filename_function(self, command, event):
		print(command)
		#get all informations required
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		final_file_list = []
		#steps
		#	- replace content
		#	- put prefix
		#	- put suffix
		old_content = mc.textField(self.rename_oldcontent_textfield, query=True, text=True)
		new_content = mc.textField(self.rename_newcontent_textfield, query=True, text=True)
		prefix_content = mc.textField(self.rename_prefix_textfield, query=True, text=True)
		suffix_content = mc.textField(self.rename_suffix_textfield, query=True, text=True)

		if (command == "RENAME") and (file_selection == None):
			mc.error("You have to select files to rename!")
			return
		else:
			
			if mc.checkBox(self.index_checkbox, query=True, value=True) == True:
				#search the file selected in the index
				for file in file_selection:
					print(file in list(self.pipeline_index.keys()))

					if file in list(self.pipeline_index.keys()):

						#get the fullpath of the file in the index
						fullpath = self.pipeline_index[file]["fullpath"]
						path = self.pipeline_index[file]["path"]
						filename = self.pipeline_index[file]["filename"]

						#rename all elements of the path
						new_filename = filename.replace(old_content, new_content)
						if (self.letter_verification_function(prefix_content)==True):
							new_filename = prefix_content+new_filename
						if (self.letter_verification_function(suffix_content)==True):
							new_filename = new_filename+suffix_content

						print("FINAL FILENAME DEFINED : %s"%new_filename)
						print("full path : %s"%(os.path.join(path, new_filename)))

						try:
							os.rename(os.path.join(path, file), os.path.join(path, new_filename))
							print("File renamed successfully")
						except Exception as error:
							mc.warning("Impossible to rename the file!\n%s"%error)
			
			else:
			
				#create the list with final filepath
				#get the path of the pipeline
				for root, dirs, files in os.walk(mc.textField(self.project_label, query=True, text=True)):
					for f in files:
						if (f in file_selection)==True:
							final_file_list.append(os.path.join(root,f))

				if len(final_file_list) == 0:
					mc.error("No matching elements to rename!")
					return
				#print(old_content, type(old_content), self.letter_verification_function(old_content))
				#print(new_content, type(new_content), self.letter_verification_function(new_content))

				for file in final_file_list:
					root = os.path.dirname(file)
					filename = os.path.splitext(os.path.basename(file))[0]
					old_filename = filename
					extension = os.path.splitext(os.path.basename(file))[1]

					filename = filename.replace(old_content, new_content)
					if (self.letter_verification_function(old_content)!=True) and (self.letter_verification_function(new_content)==True):
						mc.error("You need something to replace!")
						return

					if (self.letter_verification_function(prefix_content)==True):
						filename = prefix_content+filename 
					if (self.letter_verification_function(suffix_content)==True):
						filename = filename+suffix_content 
					final_filename = os.path.join(root,filename+extension)
					
					os.rename(file, final_filename)
					print("%s renamed as %s"%(file, final_filename))
			





	def add_script_to_shelf_function(self, event):
		#open 2 file explorer to define the Script and the icon
		selection = mc.fileDialog2(caption="Select a python script and an Icon",fm=4)
		print(selection, len(selection))
		if (selection == None) or (len(selection) != 2):
			mc.error("You have to select two elements!")
		icon = False 
		program = False 

		for element in selection:
			if os.path.splitext(element)[1] in [".jpg",".png"]:
				icon=True 
			if os.path.splitext(element)[1] == ".py":
				program = True 
		if (icon == False) or (program == False):
			mc.error("You have to select a python script and an icon!")
			return 
		#copy the python script and the icon in the right folder
		project_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(project_path)==True:
			#get the python script name
			python_script_name = None 
			for element in selection:
				if os.path.splitext(element)[1] == ".py":
					python_script_name = os.path.splitext(os.path.basename(element))[0]
			if python_script_name == None:
				mc.error("Impossible to find the script name!")
				return 

			for element in selection:
				if os.path.splitext(element)[1] == ".py":
					destination = os.path.join(project_path, "PipelineManagerData/scripts/%s.py"%python_script_name)
				else:
					destination = os.path.join(project_path, "PipelineManagerData/scripts/icons/%s.png"%python_script_name)
				#create all required folders to save scripts
				os.makedirs(os.path.dirname(destination), exist_ok=True)
				print("\nScript saved:\n%s\n%s"%(element, destination))
				shutil.copy(element, destination)
			"""
				print("\nSkipped!\n%s"%element)
				return"""
			print("SCRIPTS SAVED IN YOUR PROJECT!")
			print("Relaunch Pipo to load them in your shelf!")
		else:
			mc.error("Impossible to save scripts, define a Project first!")
			return






	def create_archive_from_files_function(self, event):
		#get file selection
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		#get name 
		archive_name = mc.textField(self.archivemenu_textfield, query=True, text=True)
		if (len(file_selection)==0) or (file_selection==None):
			mc.error("You have to select files to put inside your archive!")
			return
		if self.letter_verification_function(archive_name)!=True:
			mc.error("You have to define a name for the new archive!")
			return
		archive_name = "PipoArchive_%s"%archive_name




		"""
		archive location
			root of the project
			root of the pipeline
		"""
		project_value = mc.checkBox(self.archivemenu_projectcheckbox, query=True, value=True)
		if project_value == True:
			archive_path = mc.workspace(query=True, active=True)
		else:
			archive_path = mc.textField(self.project_label,query=True, text=True)

		if (archive_path == None) or (os.path.isdir(archive_path) == False):
			mc.error("Impossible to define the creation path of the archive!")
			return

		if project_value == True:
			#create the archive before the maya project
			project_key = self.additionnal_settings["mayaProjectName"]
			if (project_key == None) or (self.letter_verification_function(project_key)!=True):
				mc.warning("Impossible to detect maya project name in settings!")
				return
			archive_path = archive_path.split(project_key)[0]
		os.makedirs(archive_path, exist_ok=True)
		archive_path = os.path.join(archive_path,"%s.zip"%archive_name)
		final_file_list = []
		#create final file list



		#check file in index
		#or get the file in the pipeline
		if mc.checkBox(self.index_checkbox, query=True, value=True)==True:
			for f in file_selection:
				try:
					filepath = self.pipeline_index[f]["fullpath"]
					print(filepath)
					if os.path.isfile(filepath)==False:
						mc.warning("That file doesn't exist anymore in the pipeline!\n[%s]"%f)
						continue
					final_file_list.append(filepath)
					print("File located in index [%s]"%f)
				except:
					mc.warning("File skipped, Impossible to find the file in the pipeline index!\n[%s]"%f)

		else:
			for root, dirs, files in os.walk(mc.textField(self.project_label, query=True, text=True)):
				for f in files:
					if f in file_selection:
						final_file_list.append(os.path.join(root, f))

		if len(final_file_list)==0:
			mc.error("No files to add!")
			return
		project_path = mc.textField(self.project_label, query=True, text=True)

		#check if archive already exist on the pipeline
		try:
			with open(os.path.join(project_path, "PipelineManagerData/ArchiveData.dll"), "rb") as read_file:
				self.archive_data = pickle.load(read_file)
			key_list = list(self.archive_data.keys())
			if (archive_name in key_list)==True:
				mc.error("An archive with that name already exist!")
				return
			else:
				self.archive_data[archive_name] = {
					"archive_path":archive_path,
					"origin_filepath":final_file_list
					}
				with open(os.path.join(self.project_path, "PipelineManagerData/ArchiveData.dll"), "wb") as save_file:
					pickle.dump(self.archive_data, save_file)
		except:
			#create the archive file with the new archive
			self.archive_data = {
				archive_name: {
					"archive_path":archive_path,
					"origin_filepath":final_file_list,
					}
			}
			os.makedirs(os.path.join(project_path, "PipelineManagerData"), exist_ok=True)
			with open(os.path.join(project_path, "PipelineManagerData/ArchiveData.dll"), "wb") as save_file:
				pickle.dump(self.archive_data, save_file)

		self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting", min=0, max=len(final_file_list))
		p = 0
		size = 0
		
		with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_LZMA, compresslevel=9) as create_archive:
			for file in final_file_list:
				p +=1
				mc.progressWindow(self.progress_bar, edit=True, progress=p)
				size += os.path.getsize(file)
				try:
					create_archive.write(file, arcname=os.path.basename(file))
				except:
					mc.warning("Impossible to add the file : %s"%file)

		mc.progressWindow(self.progress_bar, endProgress=True)


		#check if the archive data file exists on the pipeline
		project_path = mc.textField(self.project_label, query=True, text=True)


		print("Archive created successfully!\n%s"%archive_path)
		

		archive_size = os.path.getsize(archive_path)

		print("Files total size : %s"%size)
		print("Archive size : %s"%archive_size)

		#increment the archive list dictionnary
		#self.archive_data[archive_name] = archive_path

		mc.textScrollList(self.archivemenu_textscrolllist, edit=True, removeAll=True, append=list(self.archive_data.keys()))
		mc.textScrollList(self.archive_archivelist_textscrolllist, edit=True, removeAll=True, append=list(self.archive_data.keys()))


	


	def display_archive_content_function(self):
		#get archive selection
		for key,value in self.archive_data.items():
			print(key, value)
		archive_selection = mc.textScrollList(self.archive_archivelist_textscrolllist, query=True, si=True)
		if archive_selection == None:
			mc.error("You have to select an archive!")
			return
		#archive_selection = "PipoArchive_%s"%archive_selection[0]
		archive_selection = archive_selection[0]
		archive_keys = list(self.archive_data.keys())
		archive_values = list(self.archive_data.values())
		
		print("content")
		print(archive_selection)
		print(archive_keys)
		print(archive_values)
		print("\n")
		if archive_selection not in archive_keys:
			mc.error("Impossible to find the archive in the index!")
			return 
		#print(archive_keys.index(archive_selection))

		archive_index = archive_keys.index(archive_selection)
		archive_values = archive_values[archive_index]
		if type(archive_values)==dict:
			archive_path = archive_values["archive_path"]
		else:
			archive_path = archive_values
		print(archive_path)

		


		if os.path.isfile(archive_path)==False:
			mc.error("This archive doesn't exist : %s"%archive_path)
			return
		else:
			#get the content of the archive:
			try:
				with zipfile.ZipFile(archive_path) as archive:
					content = archive.namelist()
				mc.textScrollList(self.archive_archivecontent_textscrolllist, edit=True, removeAll=True, append=content)
			except:
				mc.error("Impossible to read the archive!")
				return







	def refresh_archive_list_function(self, event):
		project_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(project_path)==False:
			mc.error("No project defined or existing, Impossible to refresh archive!")
			return

		#go through the archive data file and check if all archives exists
		#if no, remove from the list and the file
		new_archive_dictionnary = {}
		for archive_name, archive_data in self.archive_data.items():
			if os.path.isfile(archive_data["archive_path"])==True:
				new_archive_dictionnary[archive_name] = {
					"archive_path":archive_data["archive_path"],
					"origin_filepath":archive_data["origin_filepath"],
					}
		archive_key_list = list(new_archive_dictionnary.keys())
		#for i in range(0, len(archive_key_list)):
		#	archive_key_list[i] = archive_key_list[i].replace("PipoArchive_", "")
		mc.textScrollList(self.archivemenu_textscrolllist, edit=True, removeAll=True, append=archive_key_list)
		mc.textScrollList(self.archive_archivelist_textscrolllist, edit=True, removeAll=True, append=archive_key_list)

		os.makedirs(os.path.join(project_path, "PipelineManagerData"), exist_ok=True)
		with open(os.path.join(project_path, "PipelineManagerData/ArchiveData.dll"), "wb") as save_file:
			pickle.dump(new_archive_dictionnary, save_file)	
		print("Archive data refreshed!")
		return




		

		
	def add_files_to_archive_function(self, event):
		#get selection in the textscrolllist
		archive_selection = mc.textScrollList(self.archivemenu_textscrolllist, query=True, si=True)
		if (archive_selection == None) or (len(archive_selection) == 0):
			mc.error("You have to select an archive!")
			return
		archive_key_list = list(self.archive_data.keys())
		#try to find the archive in the archive data
		#take the path corresponding in the dictionnary
		#if it doesn't exist advice to scan the pipeline to find back the archive
		for element in archive_selection:
			full_archive_name = "PipoArchive_"+element

			if (full_archive_name in archive_key_list)==False:
				mc.error("Impossible to find the archive!\nPlease scan your Pipeline!")
				return
			else:
				#get the full path of the archive
				archive_path = self.archive_data[full_archive_name]
				file_selection = mc.textScrollList(self.result_list, query=True, si=True)
				if (file_selection == None) or (len(file_selection) == 0):
					mc.error("You have to select files to add to the archive!")
					return
				else:
					starting_folder = mc.textField(self.project_label, query=True, text=True)
					if os.path.isdir(starting_folder)==False:
						mc.error("Impossible to find files to add to the archive!")
						return
					#get the real path of the file to add
					final_file_list = []
					for root, dirs, files in os.walk(starting_folder):
						for f in files:
							if f in file_selection:
								if os.path.isfile(os.path.join(root, f))==True:
									final_file_list.append(os.path.join(root, f))
								else:
									mc.warning("File skipped : %s"%f)

					self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting", min=0, max=len(final_file_list))

					p = 0
					size = 0
					archive_size_before = os.path.getsize(archive_path)
					#add files to archive
					print("Modification of the archive : %s"%archive_path)
					with zipfile.ZipFile(archive_path, "a", zipfile.ZIP_LZMA, compresslevel=9) as create_archive:
						for file in final_file_list:
							p +=1
							mc.progressWindow(self.progress_bar, edit=True, progress=p)
							size += os.path.getsize(file)
							try:
								create_archive.write(file, arcname=os.path.basename(file))
								print("File added to the archive : %s"%file)
							except:
								mc.warning("Impossible to add the file : %s"%file)
					mc.progressWindow(self.progress_bar, endProgress=True)
					archive_size_after = os.path.getsize(archive_path)

					print("Archive size before : %s"%archive_size_before)
					print("Archive size after : %s\n"%archive_size_after)





	def delete_archive_function(self, event):
		#detect the archive in the index
		#get the path
		#remove the file and delete the key from the dictionnary
		#in the end update the textscrolllist
		#
		#simple and efficient
		try:
			archive_selection = mc.textScrollList(self.archive_archivelist_textscrolllist, query=True, si=True)[0]
		except:
			mc.error("You have to select an archive to remove!")
			return
		archive_keys = list(self.archive_data.keys())
		archive_values = list(self.archive_data.values())
		
		#get the path
		try:
			archive_path = archive_values[archive_keys.index(archive_selection)]["archive_path"]
		except:
			mc.error("Impossible to find the archive in data!")
			return
		#remove the file
		#remove the key in the dictionnary
		print("Archive to delete : %s"%archive_path)
		if os.path.isfile(archive_path)==True:
			os.remove(archive_path)
			print("Archive removed!")
		else:
			mc.warning("Impossible to remove the archive!")

		project_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(project_path)==False:
			mc.error("No project defined, Impossible to refresh archive data!")
			return
		self.archive_data.pop(archive_selection)
		with open(os.path.join(project_path, "PipelineManagerData/ArchiveData.dll"), "wb") as save_content:
			pickle.dump(self.archive_data, save_content)
		print("Archive data updated!")

		mc.textScrollList(self.archive_archivelist_textscrolllist, edit=True, removeAll=True, append=list(self.archive_data.keys()))
		mc.textScrollList(self.archivemenu_textscrolllist, edit=True, removeAll=True, append=list(self.archive_data.keys())) 
		mc.textScrollList(self.archive_archivecontent_textscrolllist, edit=True, removeAll=True)




	def archive_tidy_files_function(self, event):
		"""
		take the file selected
		the name of the archive
		get the path of the selected archive

		extract files from the archive
		parse their nomenclature
		get the default folder path if possible
		else tidy them at the root of the pipeline
		"""
		try:
			archive_name_selected = mc.textScrollList(self.archive_archivelist_textscrolllist, query=True, si=True)[0]
		except:
			mc.error("You have to select an archive!")
			return 

		archive_content_selected = mc.textScrollList(self.archive_archivecontent_textscrolllist, query=True, si=True)

		if (archive_content_selected == None) or (len(archive_content_selected) == 0):
			mc.error("You have to select at least one file to extract!")
			return 
		
		archive_keys = list(self.archive_data.keys())
		archive_values = list(self.archive_data.values())

		archive_path = archive_values[archive_keys.index(archive_name_selected)]
	

		#print("ARCHIVE PATH\n%s"%archive_path)
		print("Files to extract:")
		for file in archive_content_selected:
			print(file)

			value = self.parse_file_function(file)
			
			"""
			IF THE VALUE IS DIFFERENT FROM FALSE PUT THE FILES AT THE RIGHT LOCATION IN THE PIPELINE
			ELSE PUT THE FILES AT THE ROOT OF THE PIPELINE
			"""

			if value != False:
				print(self.archive_data)
				origin_path = self.archive_data[archive_name_selected]["origin_filepath"]
				#try to find the origin location in the archive data
				if type(self.archive_data[archive_name_selected]) == dict:
					#print(self.archive_data[archive_name_selected])
					archive_path = self.archive_data[archive_name_selected]["archive_path"]
					
				else:
					archive_path = self.archive_data[archive_name_selected]
				
				for path in origin_path:
					#print(file, os.path.basename(path), path)
					if os.path.basename(path) == file:
						#extract that file at that location
						"""
						print("\nExtraction ready:")
						print(file)
						print(os.path.dirname(path))
						print("archive path")
						print(archive_path)
						"""
						if os.path.isdir(os.path.dirname(path))==False:
							os.makedirs(os.path.dirname(path), exist_ok=True)
						if os.path.isfile(path)==True:
							mc.warning("File skipped, the file already exists at that location!")
							return 
						with zipfile.ZipFile(archive_path, mode="r") as read_archive:
							try:	
								read_archive.extract(file, os.path.dirname(path))
								print("File extracted %s"%file)
								print("New location : %s"%os.path.dirname(path))
							except:
								mc.warning("Impossible to extract the file at that location : %s"%file)
							
			else:
				mc.warning("Impossible to extract the file!")
				return



		#for each file in the selection parse the file and get the extraction path






	def add_to_favorite_scene_function(self, event):

		#get the file selection
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		final_file_list = []

		if mc.checkBox(self.index_checkbox, query=True, value=True)==True:
			#get the file in the pipeline index
			for file in file_selection:
				if file in self.pipeline_index:
					#get the path of the file
					fullpath = os.path.join(self.pipeline_index[file]["path"], file)
					print("File found in pipeline index : %s"%fullpath)

					if os.path.isfile(fullpath) == False:
						mc.warning("Warning : the file defined as favorite doesn't exists anymore in the project\n%s"%fullpath)
					else:
						final_file_list.append(fullpath)
						print("File defined as favorite : %s"%fullpath)
				else:
					mc.warning("Impossible to find the file in the pipeline index : %s"%file)


		if mc.checkBox(self.index_checkbox, query=True, value=True)==False:
			if file_selection == None:
				mc.error("You have to select at least one file!")
				return
			#get the path of the file
			if mc.checkBox(self.searchbar_checkbox, query=True, value=True)==True:
				#get the maya project path
				path = mc.workspace(query=True, active=True)
				if os.path.isdir(path)==False:
					mc.error("You have to define a correct maya project first!")
					return 
			else:
				if os.path.isdir(mc.textField(self.project_label, query=True, text=True))==False:
					mc.error("Impossible to define the root folder!")
					return
				path = mc.textField(self.project_label, query=True, text=True)
			print(file_selection)
			
			for root, dirs, files in os.walk(path):
				#print(root)
				for f in files:
					#print(f in file_selection, f in final_file_list, f)
					if (f in file_selection) and (f in final_file_list)==False:
						final_file_list.append(os.path.join(root, f))


		favorite_file_data = self.user_settings["AdditionalData"]["FavoriteFiles"]

		if len(final_file_list) != 0:
			for file in final_file_list:
				file = file.replace(os.sep, '/')
				favorite_file_data[os.path.basename(file)] = file


		self.user_settings["AdditionalData"]["FavoriteFiles"] = favorite_file_data
		self.save_settings_file()
		self.apply_user_settings_function()
		"""
		self.user_settings["FavoriteFiles"] = favorite_file_data
		self.save_settings_file()
		self.apply_user_settings_function()
		"""




	def get_current_scene_name_function(self, event):
		"""
		get the current path of the scene
		get the current filename
		parse the filename thanks to syntax settings

		get the item name from the filename
		"""
		current_filepath = mc.file(sceneName=True, query=True)
		if os.path.isfile(current_filepath) != True:
			mc.warning("Impossible to get the current name!")
			return
		path = os.path.dirname(current_filepath)
		filename = os.path.basename(current_filepath)
		filename, extension = os.path.splitext(filename)

		#go through the settings
		splited_file = filename.split("_")
		
		for key, value in self.settings.items():
			syntax = value[0]

			if type(syntax) != list:
				syntax_data = [syntax]
			else:
				syntax_data = syntax
			
			for syntax in syntax_data:
				splited_syntax = syntax.split("_")

				if len(splited_syntax) == len(splited_file):
					for i in range(0,len(splited_syntax)):
						if (splited_syntax[i] == "[key]") and (splited_file[i] == value[1]):
							print("key found %s"%splited_file[i])

							#try to find the name index in that nomenclature
							if "[name]" in splited_syntax:
								name_index = splited_syntax.index("[name]")

								scene_name = splited_file[name_index]
								print("Name found : %s"%scene_name)
								mc.textField(self.export_edit_name_textfield, edit=True, text=scene_name)
							else:
								mc.warning("Impossible to find [name] keyword in syntax!")






	def get_children_function(self, element):
		#get the list of children for that element
		if element not in self.children_list:
			self.children_list.append(element)
		
		try:
			children_list = mc.listRelatives(element, children=True, fullPath=True) or []
		except:
			mc.warning("Impossible to get the children list for %s"%element)
		else:
			
			if len(children_list) != 0:
				for children in children_list:
					self.get_children_function(children)










	def export_selection_in_project_function(self, event):
		#get the selection in the outliner
		selection = mc.ls(sl=True)




		"""
		for each element of the selection
			-> parse the nomenclature of the element to get the name, and the type of scene
			-> get the nomenclature of the file to export
			-> get the export path of the file to export
			-> export selection
		"""

		for element in selection:


			#parse the nomenclature
			#nomenclature to respect
			#	grpexport_name_type
			#	mshexport_name_type
			splited_element_name = element.split("_")
			if len(splited_element_name) != 3:
				mc.warning("Element skipped, wrong syntax : %s"%element)
				continue 
			else:
				if splited_element_name[0] not in ["export", "|export"]:
					mc.warning("Element skipped, wrong syntax : %s"%element)
					continue
				else:
					if splited_element_name[2] not in self.additionnal_settings["exportSelectionTypeList"]:
						mc.warning("Element skipped, wrong kind : %s"%element)
						continue

					element_name = splited_element_name[1]
					element_kind = splited_element_name[2]
					version= "publish"
					lod = "lod3"


					#define the export filename
					#get the syntax of that type of scene
					nomenclature_data = self.settings[element_kind][0]
					if type(nomenclature_data) != list:
						nomenclature_data = [nomenclature_data]

					nomenclature = nomenclature_data[-1]
					splited_nomenclature = nomenclature.split("_")


					#get the default folder
					default_folder = self.settings[element_kind][2]
					splited_default_folder = default_folder.split("/")

					final_filepath = []
					final_filename = []


					#save the real element name in a variable to export an item 
					#with a right nomenclature
					old_name = element
					


					
					data_dictionnary = {
						"[name]": element_name,
						"[version]": self.additionnal_settings["editPublishFolder"][1],
						"[type]": "mod",
						"[key]": element_kind,
						"[lod]": "lod3",
						"[Origin]":self.project_path,
						"[mayaProjectName]":self.additionnal_settings["mayaProjectName"],
						"[editPublishFolder]":self.additionnal_settings["editPublishFolder"][1]
					}


					for i in range(len(splited_nomenclature)):
						if splited_nomenclature[i] in data_dictionnary:
							splited_nomenclature[i] = data_dictionnary[splited_nomenclature[i]]

					for i in range(len(splited_default_folder)):
						if splited_default_folder[i] in data_dictionnary:
							splited_default_folder[i] = data_dictionnary[splited_default_folder[i]]

					#print(splited_default_folder)
					final_filename = "_".join(splited_nomenclature)+".ma"
					final_filepath = "/".join(splited_default_folder)


					final_fullpath = os.path.join(final_filepath, final_filename)


					print("Destination path : %s"%final_fullpath)


					"""
					import maya.cmds as mc
					test_loc=cmds.spaceLocator()
					mc.setAttr("%s.visibility"%test_loc[0], True)

					mc.matchTransform('grpexport_testgroup2_item','locator1', pos=True, rot=False, scl=False)

					mc.xform("grpexport_testgroup2_item", t=True,t=(0,0,0), ws=True)
					"""


					#CENTER THE PIVOT OF THE OBJECT
					mc.xform(element, cp=True)
					#mc.makeIdentity(element, apply=True, t=1, r=1, s=1, n=0, pn=1)
					print(element)
					
					self.children_list = []
					self.get_children_function(element)

					for children in self.children_list:
						print(children)

						#freeze trnansform and reset pivot
						#makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;
						
						mc.xform(children, cp=True)
					print("All pivots centered")


					


					if mc.checkBox(self.exportselectionmove_checkbox, query=True, value=True)==True:
						#create a locator at the center of the world
						#create a locator at the current position of the group
						locator_worldcenter = mc.spaceLocator()
						locator_oldposition = mc.spaceLocator()

						#match the locator old position with the element to save the old position
						mc.matchTransform(locator_oldposition, element, pos=True, rot=False, scl=False)
						#match the element with the locator at the center of the world
						mc.matchTransform(element, locator_worldcenter, pos=True, rot=False, scl=False)
						print("Item centered")



					#create required folders of the path to save the file
					os.makedirs(final_filepath, exist_ok=True)
					old_name = element 
					mc.rename(element, element_name)

					#DONT FORGET TO SELECT THE ITEM TO EXPORT
					mc.makeIdentity(element_name, apply=True, t=1, r=1, s=1, n=0, pn=1)
					mc.select(element_name, r=True)
					mc.file(final_fullpath, force=True, options="", type="mayaAscii", pr=True, es=True)

					print("%s exported successfully : \n%s"%(element_kind, final_fullpath))
					mc.rename(element_name, element)


					#return the object at his origin position
					if mc.checkBox(self.exportselectionmove_checkbox, query=True, value=True)==True:
						mc.matchTransform(element, locator_oldposition, pos=True, scl=False, rot=False)
						print("Old position of the item restored!")


					if mc.checkBox(self.exportselectionreplace_checkbox, query=True, value=True)==True:
						#import the new exported item as reference
						try:
							imported_asset = mc.file(final_fullpath, r=True, returnNewNodes=True)
						except:
							mc.warning("Impossible to reimport the exported asset\n"%final_fullpath)
						
						else:
							if mc.checkBox(self.exportselectionmove_checkbox, query=True, value=True)==True:
								#try to match the imported asset with the location of the old asset

								#go through the list of imported elements and get the first node with | at the beginning
								#try to split the node name, if there is several | in the name, it's not the first one!
								found_parent=False
								for item in imported_asset:
									splited_item = item.split("|")

									if (len(splited_item) == 2) and (splited_item[0] == ""):
										print("PARENT OF THE REFERENCE FOUND : %s"%item)
										found_parent=True 
										break

								if found_parent == False:
									mc.warning("Impossible to match the reference with its old location")
								else:
									mc.matchTransform(item, locator_oldposition, pos=True, rot=False, scl=False)
									print("Old location restored on imported asset : %s"%element)

					
					#delete all locators at the end of the process
					try:
						mc.delete(locator_oldposition)
						mc.delete(locator_worldcenter)
					except:
						mc.warning("Impossible to clean locators!")
					#delete the old item if the checkbox is checked
					try:
						mc.delete(element)
					except:
						mc.warning("Impossible to delete old item : %s"%element)










