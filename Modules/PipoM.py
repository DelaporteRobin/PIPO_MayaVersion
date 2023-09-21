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
			return None, None, None, None
		else:
			
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			
		
		
		
			try:	
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.yaml"), "r") as read_file:
					load_data = yaml.load(read_file,Loader=yaml.Loader)
				with open(os.path.join(self.program_folder, "Data/PipoUserSettings.yaml"), "r") as read_file:
					user_settings = yaml.load(read_file, Loader=yaml.Loader)
				
				self.user_settings = user_settings["dict1"]
				self.settings = load_data["dict1"]
				self.settings_dictionnary = load_data["dict2"]
				self.additionnal_settings = load_data["dict3"]
				self.texture_settings = load_data["dict4"]

				
				print("Settings loaded successfully!")
			
			except:
				self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings, self.user_settings = self.create_pipeline_settings_function()
				print("Settings file created in your project!")
				
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
				user_dictionnary = {
					"dict1": self.user_settings,
				}
				saving_dictionnary = {
					"dict1":self.settings,
					"dict2":self.settings_dictionnary,
					"dict3":self.additionnal_settings,
					"dict4":self.texture_settings,
				}

				#save the pipeline file
				with open(os.path.join(path, "PipelineManagerData/PipelineSettings.yaml"), "w") as save_file:
					yaml.dump(saving_dictionnary, save_file, indent=4)
				#save the user settings file
				with open(os.path.join(self.program_folder, "Data/PipoUserSettings.yaml"), "w") as save_file:
					yaml.dump(user_dictionnary, save_file, indent=4)
			except AttributeError:
				print("Impossible to save!")
				self.create_pipeline_settings_function()
			self.add_log_content_function("Settings file saved successfully")




	




	def create_pipeline_settings_function(self):
		print("Settings file created!")
		basic_file_type_list = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]

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
			"shots":["[project]_[key]_[sqversion]_[shversion]", "shots", None]
		}
		self.additionnal_settings = {
			#"checkboxValues":[False, False, True, False, False, False],
			"3dSceneExtension":[".ma",".mb"],
			"3dItemExtension":[".obj", ".fbx"],
			"texturesExtension":[".png", ".tif",".tiff",".tex", ".exr", ".jpg"],
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"],
			"renderFolderInProject":"images",
			"renderFrameSyntax":["[content].[frame]", "[content]_[frame]"],
			"textureFolderInProject": "3dPaintTextures",
			"discordBotToken":None,
			"discordChannelId":None,
			"renderEngine":"Renderman",
			"renderShaderNodeList":["lambert"]
		}
		self.user_settings = {
			"checkboxValuesMainPage":[False, False, True, False, False],
			"checkboxValuesRenamePanel":[False, False],
			"checkboxValuesTextureLinkingPanel":[True, False, True, True],
			"checkboxValuesMissingFramesPanel":[False],
			"checkboxValuesExportPanel":[False, False, True, False, False],
			"FavoriteFiles":{},
			"ExportRaimbow":True,
			"ExportWebsite":True,
		}
		
		self.texture_settings = {
			"Renderman":{
				"diffuse": [
					["diffuse","Diffuse","Diff","diff"],
					("PxrTexture","filename","resultRGB"),
					[
						("PxrHSL", "inputRGB", "resultRGB"),
						("PxrRemap", "inputRGB", "resultRGB"),
					],
					("PxrSurface", "diffuseColor"),
					[
						("PxrTexture","linearize",1)
					]
					],

				"displace": [
					["displace", "Displace", "disp", "Disp"],
					("PxrTexture","filename", "resultRGBR"),
					[
						("PxrRemap", "inputRGBR", "resultRGBR"),
						("PxrDispTransform", "dispScalar", "resultF"),
						("PxrDisplace", "dispScalar", "outColor"),
					],
					("shadingEngine", "rman__displacement"),
					[
						("PxrTexture", "linearize",0),
						("PxrDispTransform","dispRemapMode",2)
					]
				]
				}
		}
		

		self.save_settings_file()
		return self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings, self.user_settings



	def reset_default_syntax_function(self,event):
		self.default_settings = {
			"character":["[project]_[key]_[name]_[type]", "char", None],
			"prop":["[project]_[key]_[name]_[type]", "prop", None],
			"set":["[project]_[key]_[name]_[type]", "set", None,],
			"fx":["[project]_[key]_[name]_[type]","fx", None,],
			"shots":["[project]_[key]_[sqversion]_[shversion]", "shots", None,]
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
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"],
			"renderFolderInProject":"images",
			"renderFrameSyntax":["[content].[frame]", "[content]_[frame]"],
			"textureFolderInProject":"sourceimages",
			"discordBotToken":None,
			"discordChannelId":None,
			"renderEngine":"Renderman",
			"renderShaderNodeList":["lambert"]
		}
		self.default_user_settings = {
			"checkboxValuesMainPage":[False, False, True, False, False],
			"checkboxValuesRenamePanel":[False, False],
			"checkboxValuesTextureLinkingPanel":[True, False, True, True],
			"checkboxValuesMissingFramesPanel":[False],
			"checkboxValuesExportPanel":[False, False, True, False, False],
			"FavoriteFiles":{},
			"ExportRaimbow":True,
			"ExportWebsite":True,
		}
		
		self.default_texture_settings = {
			"Renderman":{
				"diffuse": [
					["diffuse","Diffuse","Diff","diff"],
					("PxrTexture","filename","resultRGB"),
					[
						("PxrHSL", "inputRGB", "resultRGB"),
						("PxrRemap", "inputRGB", "resultRGB"),
					],
					("PxrSurface", "diffuseColor"),
					[
						("PxrTexture","linearize",1)
					]
					],

				"displace": [
					["displace", "Displace", "disp", "Disp"],
					("PxrTexture","filename", "resultRGBR"),
					[
						("PxrRemap", "inputRGBR", "resultRGBR"),
						("PxrDisplace", "dispScalar", "outColor"),
					],
					("shadingEngine", "rman__displacement"),
					[
						()
					]
				]
				}
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


		if name_selection != None:
			if self.current_name != name_selection[0]:
				self.current_name = name_selection[0]
		"""
		if type_selection != None:
			if self.current_type != type_selection[0]:
				self.current_type = type_selection[0]
		"""

		
		
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
			self.search_files_function(type_selection, kind_selection, name_selection)






	def search_files_function(self, type_selection, kind_selection, name_selection):
		#get the content of all checkbox
		#to define the searching field
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

				print(default_folder_splited)
				for item in default_folder_splited:
					if item in default_folder_variable_list:
						break
					else:
						final_default_folder.append(item)
				print("Default Folder defined")
				print(final_default_folder)
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
		for folder in starting_folder:
			total_files += int(sum([len(files) for root, dirs, files in os.walk(folder)]))
		i = 0



		#self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting",min=0, max=total_files)
	
		print("Searching...")
		print("Starting folder : %s"%starting_folder)


		
		final_file_list = []
		final_name_list = []
		
		
		
		
		for folder in starting_folder:
			print("searching in [%s]"%folder)
			p = 0 
			total_files = int(sum([len(files) for root, dirs, files in os.walk(folder)]))
			
			if total_files != 0:
				self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting", min=0, max=total_files)
			
			for r, d, f in os.walk(folder):
				

				if ("PipelineManagerData" in d)==True:
					d.remove("PipelineManagerData")

				for file in f:
					p+=1
					print("[%s | %s]		checking - %s"%(p, total_files, file))
					mc.progressWindow(edit=True, progress=p, status="Processing...")
					#get files information
					file_path = os.path.dirname(file)
					file_name = os.path.splitext(os.path.basename(file))[0]
					file_extension = os.path.splitext(file)[1]
					#check if extension of the file is in the list
					if (len(extension_list)!= 0) and (file_extension in extension_list)==False:
						continue
					
					#split de filename to check the len of the syntax
					#get the syntax and the keyword of the current type
					if type_selection != None:
						for t in type_selection:
							error=False
							syntax = self.settings[t][0]
							keyword = self.settings[t][1]

							splited_filename = file_name.split("_")
							splited_syntax = syntax.split("_")

							

							if len(splited_filename) != len(splited_syntax):
								error=True
								continue

							#DISPLAY ONLY FILES WITH THE RIGHT SIZE
							#print("\nNEW FILE - %s"%file)
							#print("[key]" in splited_syntax)





							if "[type]" in splited_syntax:
								type_index = splited_syntax.index("[type]")
								"""
								if no type is selected then 
								skip the type error
								"""
								if kind_selection == None:
									pass
								#print(splited_filename[type_index], splited_filename[type_index] in kind_selection, kind_selection)
								elif (splited_filename[type_index] in kind_selection)==False:
									error=True 
									print("ERROR type %s" % file)
									continue


							if "[key]" in splited_syntax:
								key_index = splited_syntax.index("[key]")

								#print(splited_filename[key_index], keyword)
								if splited_filename[key_index] != keyword:
									print("ERROR key %s" % file)
									error=True 
									#print("keyword error")
									continue
								else:
									print(file)


							#check the whole syntax of the file
							if "[project]" in splited_syntax:
								project_index = splited_syntax.index("[project]")
								#print(splited_filename[keyword_index], project_name)
								if splited_filename[project_index] != project_name:
									print("ERROR project %s" % file)
									error=True 
									continue

							if "[version]" in splited_syntax:	
								version_index = splited_syntax.index("[version]")

								if (splited_filename[version_index]) != "publish":
									if (len(splited_filename[version_index].split("v")) == 2):
										if (splited_filename[version_index].split("v")[0] != "") or (splited_filename[version_index].split("v")[1].isdigit()==False):
											print("ERROR version %s" % file)
											error=True
		
											continue
									else:

										error=True
										continue

							if "[sqversion]" in splited_syntax:
								version_index = splited_syntax.index(["sqversion"])
								if (len(splited_filename[version_index].split("sq"))==2):
									if (splited_filename[version_index].split("sq")[0] != "") or (splited_filename[version_index].split("sq")[1].isdigit()==False):
										error=True 

										continue
							if "[shversion]" in splited_syntax:
								version_index = splited_syntax.index(["shversion"])
								if (len(splited_filename[version_index].split("sh"))==2):
									if (splited_filename[version_index].split("sh")[0] != "") or (splited_filename[version_index].split("sh")[1].isdigit()==False):
										error=True 

										continue
							#check that the file is contained in name list selection
							if (name_selection != None):
								#check the name keyword in the syntax
								if ( "[name]" in splited_syntax ) == False:
									print("ERROR name %s" % file)
									error=True
									continue
								else:
									
									
									if (splited_filename[splited_syntax.index("[name]")] in name_selection) == False:
										print("ERROR name %s" % file)
										error=True 
										continue

									


							if ("[name]" in splited_syntax) and (error == False):
								name = splited_filename[splited_syntax.index("[name]")]
								if (name in final_name_list)==False:
									final_name_list.append(name)


							if ("[artist]" in splited_syntax):
								artist_name = splited_filename[splited_syntax.index("[artist]")]
								print(artist_name)
							


					


						if error == False:
							#print("FILE CHECKED - %s" % file)
							final_file_list.append(file)

		print("\nSEARCHING DONE!!!\n")
		mc.progressWindow(endProgress=True)

		
		mc.textScrollList(self.result_list, edit=True,removeAll=True, append=final_file_list)


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
		except:
			pass
		
				





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
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		folder_name = (mc.textField(self.project_label, query=True, text=True))
		#project_name = os.path.basename(os.path.normpath(folder_name))

		if file_selection == None:
			mc.error("You have to select at least one file!")
			return 



		#try to find file in the folder
		for item in file_selection:
			for r, d, f in os.walk(folder_name):
				for file in f:
					if file == item:
						self.add_log_content_function("[%s] File found in project" % item)
						if os.path.isfile(os.path.join(r, item)):
							try:
								if command==False:
									mc.file(os.path.join(r, item), i=True)
								if command==True:
									mc.file(os.path.join(r, item), r=True)
								self.add_log_content_function("[%s] File imported successfully"%item)
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

	def export_edit_file_function(self, event):
		"""
		create the full filename from syntax settings
		"""
		final_syntax = []
		if mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)==None:
			mc.error("You have to select a type!")
			return

		for kind, content in self.settings.items():
			if kind == mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)[0]:
				syntax = content[0].split("_")

				for element in syntax:
					if element == "[project]":
						final_syntax.append(os.path.basename(os.path.normpath(mc.workspace(query=True, active=True))))
					if element == "[key]":
						final_syntax.append(content[1])
					if element == "[artist]":
						#get the content of artist textfield
						artist_name = mc.textField(self.export_artist_name_textfield, query=True, text=True)
						if (self.letter_verification_function(artist_name)) != True:
							mc.error("You have to enter a valid artist name!")
							return
						else:
							final_syntax.append(artist_name)
					if element == "[name]":
						name = mc.textField(self.export_edit_name_textfield, query=True, text=True)
						if (self.letter_verification_function(name)==False) or (self.letter_verification_function(name)==None):
							mc.error("You have to define a name for the new file!")
							return
						else:
							final_syntax.append(name)
					if element == "[type]":
						type_selection = mc.textScrollList(self.export_edit_type_textscrolllist, query=True,si=True)
						if type_selection == None:
							mc.error("You have to select a type!")
							return
						else:
							final_syntax.append(type_selection[0])
					if (element == "[version]") or (element == "[shversion]") or (element == "[sqversion]"):
						if element == "[version]":
							version = list(str(mc.intField(self.export_edit_fileversion, query=True, value=True)))
						if element == "[shversion]":
							version = list(str(mc.intField(self.export_edit_shotversion, query=True, value=True)))
						if element == "[sqversion]":
							version = list(str(mc.intField(self.export_edit_sqversion, query=True, value=True)))
						if len(version)<3:
							while len(version) < 3:
								version.insert(0,"0")
						final_syntax.append("v"+"".join(version))
					

		final_filename = "_".join(final_syntax)
		#check if we need to find the default folder
		if mc.checkBox(self.export_edit_defaultfolder_checkbox, query=True, value=True)==True:
			
			for kind, content in self.settings.items():
			
				if kind == mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)[0]:
					default_folder = content[2]
	
					if (default_folder == None) or (default_folder == "None"):
						mc.error("Impossible to use default folder You need to define on in settings!")
						return
					else:
						final_filename = os.path.join(default_folder, final_filename+".ma")
		
			

		else:
			try:
				folder = mc.fileDialog2(fm=3)[0]
			except:
				mc.error("You have to select a destination folder!")
				return
			else:
				final_filename = os.path.join(folder, final_filename+".ma")


		
		#save the current file
		#rename the current file
		#save the renamed 
		if os.path.isfile(final_filename)==False:
			try:
				mc.file(save=True)
			except:
				mc.warning("Impossible to save the current file\nNo name defined for it!")
				pass
			mc.file(rename=final_filename)
			mc.file(save=True, f=True, type="mayaAscii")

			mc.warning("EDIT FILE SUCCESFULLY SAVED\n[%s]"%final_filename)
			self.take_picture_function("test")
			self.add_log_content_function("Export edit file succeed [%s]"%final_filename)
		else:
			self.add_log_content_function("Export edit file failed, the file already exist")
			mc.error("This file already exist!")
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

		mc.displayRGBColor("background", *(0.5,0.5,0.5))
		congrats_rank = randrange(0,8)
		if os.path.isfile("Data/icons/congrats%s.gif"%congrats_rank)==True:
		
			if os.path.isdir(self.program_folder)==True:

				webbrowser.open(os.path.join(self.program_folder, "Data/icons/congrats%s.gif"%congrats_rank))




		


	def export_publish_function(self, event):
		#get current project path
		project_path = mc.workspace(query=True, active=True)
		project_name = os.path.basename(project_path)
		current_scene_path = (mc.file(query=True, sn=True))
		"""
		save the current file as it is
		check all elements of the publish step list
		save the current file as the new publish file

		save the current file in the current project folder
		search for the pulbish folder
		"""

		"""
		try:
			mc.file(save=True)
		except:
			mc.error("Impossible to save the current file!")
			return
		"""
		selection = mc.textScrollList(self.export_publish_textscrolllist, query=True, si=True)

		if type(selection)==list:
			for item in selection:

				#DELETE UNUSED NODES
				if item == self.publish_step_list[0]:
					#delete unused nodes
					mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1, "deleteUnusedNodes");')
					mc.warning("Unused nodes deleted")


				#HIDE JOINTS
				if item == self.publish_step_list[1]:
					#hide all joints
					#display override in ref mode
					select_all = mc.select(all=True)
					selection = mc.ls(sl=True)
					final_selection = []

					for item in selection:
						final_selection.append(item)

						if mc.listRelatives(item, allDescendents=True) != None:
							final_selection += mc.listRelatives(item, allDescendents=True)
					
					joint_list = []
					for item in final_selection:
						if mc.objectType(item) == "joint":
							joint_list.append(item)
					
					for joint in joint_list:
						mc.setAttr("%s.overrideEnabled"%joint,1)
						mc.setAttr("%s.overrideDisplayType"%joint,2)
					mc.select(all=True, deselect=True)

					mc.warning("All controllers hidden")


				#REMOVE ALL ANIMATIONS KEYS
				if item == self.publish_step_list[2]:
					#select all nurbs curve and remove all keys on them
					print("hello world!")

		#check the nomenclature of the current file to define the right publish nomenclature
		#get checkbox values
		if mc.checkBox(self.export_publish_samelocation_checkbox, query=True, value=True)==True:
			#get current location of the file your working on
			publish_path = os.path.dirname(mc.file(query=True, sn=True))
			if os.path.dirname(publish_path)==False:
				mc.error("Impossible to export, no location existing!")
				return
			#change the nomenclature of the current file
			extension = os.path.splitext(current_scene_path)[1]
			splited_name = os.path.basename(os.path.splitext(current_scene_path)[0]).split("_")
			version_present=False
			for i in range(0, len(splited_name)):
				if list(splited_name[i])[0] == "v":
					#print(splited_name[i].split("v"))
					
					if len(splited_name[i].split("v"))==2:
						
						if (splited_name[i].split("v")[1].isnumeric())==True:
							splited_name[i] = "publish"
							version_present=True 
							break
			if version_present==False:
				splited_name.insert(0, "Publish")
			filename = "_".join(splited_name)+extension
			mc.file(save=True)
			#save the new file at the new destination
			mc.file(rename=os.path.join(publish_path, filename))
			if extension == ".ma":
				mc.file(save=True, type="mayaAscii")
			if extension == ".mb":
				mc.file(save=True, type="mayaBinary")
			mc.warning("Publish scene saved successfully")
			print(self.user_settings["ExportRaimbow"])
			if self.user_settings["ExportRaimbow"]==True:
				self.print_color_for_publish_function()

			print(os.path.join(publish_path, filename))



		if mc.checkBox(self.export_publish_searchlocation_checkbox, query=True, value=True)==True:
			#get values from folder presets
			edit_folder_name = mc.textField(self.settings_editfolder_textfield, query=True, text=True)
			publish_folder_name = mc.textField(self.settings_publishfolder_textfield, query=True, text=True)

			if (self.letter_verification_function(edit_folder_name)==False) or (self.letter_verification_function(publish_folder_name)==False):
				mc.error("Impossible to get edit / publish folder names!")
				return
			
			if os.path.isdir(project_path)==False:
				mc.error("Impossible to export, project isn't defined!")
				return
			
			find = False 
			path = current_scene_path
			folder_to_recreate = []
			for i in range(0, len(current_scene_path.split("/"))):
			

				if os.path.basename(path) == edit_folder_name:
					if os.path.isdir(os.path.join(os.path.dirname(path), publish_folder_name))==True:
						folder_to_recreate.pop(-1)
						publish_path = os.path.join(os.path.dirname(path), publish_folder_name)
						find = True

						#recreate folders if they don't exist
						folder_to_recreate.reverse()
						for i in range(0, len(folder_to_recreate)):
							if os.path.isdir(os.path.join(publish_path,folder_to_recreate[i]))==False:
								os.mkdir(os.path.join(publish_path, folder_to_recreate[i]))
							publish_path = os.path.join(publish_path,folder_to_recreate[i])
							
						#detect the new nomenclature of the file
						extension = os.path.splitext(current_scene_path)[1]
						splited_name = os.path.basename(os.path.splitext(current_scene_path)[0]).split("_")
						version_present=False
						for i in range(0, len(splited_name)):
							if list(splited_name[i])[0] == "v":
								#print(splited_name[i].split("v"))
								
								if len(splited_name[i].split("v"))==2:
									
									if (splited_name[i].split("v")[1].isnumeric())==True:
										splited_name[i] = "publish"
										version_present=True 
										break
								
						if version_present==False:
							splited_name.insert(0, "Publish")
						filename = "_".join(splited_name)+extension
						
						#save the current file
						mc.file(save=True)
						#save the new file at the new destination
						mc.file(rename=os.path.join(publish_path, filename))
						if extension == ".ma":
							mc.file(save=True, type="mayaAscii")
						if extension == ".mb":
							mc.file(save=True, type="mayaBinary")

						mc.warning("Publish scene saved successfully")
						print(self.user_settings["ExportRaimbow"])
						if self.user_settings["ExportRaimbow"] == True:
							self.print_color_for_publish_function()

						print(os.path.join(publish_path, filename))
						self.take_picture_function("test")
						break
				folder_to_recreate.append(os.path.basename(os.path.dirname(path)))	
				if os.path.basename(path) == project_name:
					mc.error("No edit folder found in the project!")
					return

				
				path = os.path.normpath(path+os.sep+os.pardir)



			
			



						










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

				for keyword in searchbar_content:
					if (keyword in file) == False:
						valid=False 

				if valid == True:
					file_list.append(file)
			
		mc.progressWindow(endProgress=True)
                
     	
        
		mc.textScrollList(self.result_list, edit=True, removeAll=True, append=file_list)



	def delete_favorite_file_function(self, event):
		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		if favorite_selection == None:
			mc.error("Nothing to delete!")
			return
		favorite_data = self.user_settings["FavoriteFiles"]
		favorite_data.pop(favorite_selection[0])
		self.user_settings["FavoriteFiles"] = favorite_data 
		self.save_settings_file()
		self.apply_user_settings_function()




	def open_location_function(self, data, event):
		favorite_selection = mc.textScrollList(self.favorite_list, query=True, si=True)
		if favorite_selection != None:
			#get the user settings
			file_to_open = self.user_settings["FavoriteFiles"][favorite_selection[0]]
			print(file_to_open)
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
					mc.workspace(filepath, openWorkspace=True, n=True)
				except:
					try:
						mc.workspace(filepath, openWorkspace=True)
					except:
						mc.error("Impossible to set the project!")
						return 
				os.chdir(filepath)
				mc.warning("Project path set to : %s"%filepath)
			return
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
							try:
								mc.workspace(path, openWorkspace=True, n=True)
							except:
								try:
									mc.workspace(path, openWorkspace=True)
								except:
									mc.error("Impossible to set the project!")
									return
							mc.warning("Project path set to : %s"%path)
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

		print(mc.checkBox(self.searchbar_checkbox, query=True, value=True), mc.checkBox(self.folder_checkbox, query=True, value=True))

		#self.additionnal_settings["checkboxValues"] = [mc.checkBox(self.searchbar_checkbox, query=True, value=True), mc.checkBox(self.folder_checkbox, query=True, value=True), scenes, items, textures, folder]
		self.additionnal_settings["3dSceneExtension"] = scenes_extension_list
		self.additionnal_settings["3dItemExtension"] = items_extension_list
		self.additionnal_settings["texturesExtension"] = textures_extension_list
		self.user_settings["checkboxValuesMainPage"] = [mc.checkBox(self.searchbar_checkbox, query=True, value=True), mc.checkBox(self.folder_checkbox, query=True, value=True), mc.checkBox(self.scenes_checkbox, query=True, value=True), mc.checkBox(self.items_checkbox, query=True, value=True), mc.checkBox(self.textures_checkbox, query=True, value=True)]
		self.user_settings["checkboxValuesRenamePanel"] = [mc.checkBox(self.hardrename_checkbox_file, query=True, value=True), mc.checkBox(self.hardrename_checkbox_folder, query=True, value=True)]
		self.user_settings["checkboxValuesTextureLinkingPanel"] = [mc.checkBox(self.render_texture_manual_checkbox, query=True, value=True), mc.checkBox(self.render_texture_automatic_checkbox, query=True, value=True), mc.checkBox(self.render_texture_limit_project, query=True, value=True), mc.checkBox(self.render_texture_udim_checking, query=True, value=True)]
		self.user_settings["checkboxValuesMissingFramesPanel"] = [mc.checkBox(self.render_checking_checkbox, query=True, value=True)]
		self.user_settings["checkboxValuesExportPanel"] = [mc.checkBox(self.export_current_folder_checkbox, query=True, value=True), mc.checkBox(self.export_custom_folder_checkbox, query=True, value=True), mc.checkBox(self.export_assist_folder_checkbox, query=True, value=True), mc.checkBox(self.template_fromselection_checkbox, query=True, value=True), mc.checkBox(self.export_edit_name_checkbox, query=True, value=True)]

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
		mc.warning("Saved!")



		
	def define_export_nomenclature_function(self, status):
		type_selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)
		kind_selection = mc.textScrollList(self.export_kind_textscrolllist, query=True, si=True)

		if type_selection == None:
			mc.error("You have to select a type!")
			return
		nomenclature = self.settings[type_selection[0]]
		if ("[type]" in nomenclature) and (kind_selection == None):
			mc.error("You have also to select a kind!")
			return
		else:
			#get the nomenclature of the current type
			nomenclature = self.settings[type_selection[0]][0]
			keyword = self.settings[type_selection[0]][1]
			defaultfolder = self.settings[type_selection[0]][2]

			splited_nomenclature = nomenclature.split("_")
			splited_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0].split("_")
			"""
			print(type_selection[0])
			print(splited_nomenclature)
			print(splited_filename)"""

			final_filename = []

			for i in range(0, len(splited_nomenclature)):
				#print(splited_nomenclature[i])
				if splited_nomenclature[i] == "[key]":
					#print("nique tes grands morts maya!")
					#print(type_selection[0])
					final_filename.append(keyword)
					#final_filename.append(type_selection[0])

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
								if word == setting_content[1]:
									actual_keyword = setting_content[1]
									if ("[name]" in setting_content[0].split("_")) == False:
										mc.error("Impossible to get the name from the actual filename!")
										return
									else:
										actual_name = splited_filename[setting_content[0].split("_").index("[name]")]
						if( actual_keyword == None) or (actual_name == None):
							mc.error("Impossible to get the actual name of the file to create the filename!")
							return
						else:
							print(actual_name)
							final_filename.append(actual_name)
					else:
						#try to get the content of the textfield
						content = mc.textField(self.export_edit_name_textfield, query=True, text=True)
						if (self.letter_verification_function(content)==True):
							print(content)
							final_filename.append(content)
						else:
							mc.error("Impossible to get the name in textfield!")
							return

				if splited_nomenclature[i] == "[version]":
					#if mc.checkBox(self.export_edit_version_checkbox, query=True, value=True) == False:
						#try to get the version in textfield
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

				if splited_nomenclature[i] == "[type]":
					final_filename.append(kind_selection[0])
			
			print(final_filename)
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
		if mc.checkBox(self.export_assist_folder_checkbox, query=True, value=True)==True:
			final_filepath = []
			#check the value of the default folder
			default_folder_path = self.settings[type_selection[0]][2]
			if default_folder_path == None:
				mc.error("Impossible to detect a default folder in settings!")
				return
			splited_default_folder = default_folder_path.split("/")
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

			return "/".join(final_filepath)



		


				



	def export_edit_function(self, info, event):
		filename = self.define_export_nomenclature_function("edit")
		filepath = self.define_export_path_function(filename, "edit")

		extension = "mayaAscii"
		if (mc.checkBox(self.export_item_checkbox, query=True, value=True)==True):
			extension = "OBJexport"
			filename = os.path.splitext(filename)[0]+".obj"
			print("New extension for the file [OBJexport]")

		final_path = os.path.join(filepath, filename)
		print("Returned filename : [%s]"%filename)
		print("Returned filepath : [%s]"%filepath)
		
		#save the current scene with current filename




		
		

		
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
				mc.file(save=True, type=extension)

				mc.warning("File saved successfully!")
				print(final_path)
				
			except:
				mc.error("Impossible to save the file!")
				return
		else:
			#get maya selection
			selection = mc.ls(sl=True)
			if (len(selection))==0:
				mc.error("No item selected to export!")
				return
			try:
				os.makedirs(filepath, exist_ok=True)
				mc.file(final_path,force=True, shader=True, pr=True, es=True, type=extension)
				mc.warning("Selection exported successfully!")
				print(final_path)
			
			except:
				mc.error("Impossible to export selection!")
				return
		#define a random number between 0 and 100 (1/4 chances)
		
		#print("Are you lucky")
		random_number = randrange(0, 100)
		if (random_number < 50):
			if self.user_settings["ExportWebsite"]==True:
				self.open_website_for_edit_function()
		

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
		filepath = self.define_export_path_function(filename, "publish")
		final_path = os.path.join(filepath, filename)

		extension = "mayaAscii"
		if (mc.checkBox(self.export_item_checkbox, query=True, value=True)==True):
			filename = "_".join(splited_filename) + ".obj"
			extension = "OBJexport"
			print("New extension for the file [OBJexport]")

		print("Returned filename : [%s]"%filename)
		print("Returned filepath : [%s]"%filepath)
		print(final_path)

		

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
			try:
				os.makedirs(filepath, exist_ok=True)
				mc.file(final_path,force=True, shader=True, pr=True, es=True, type=extension)
				mc.warning("Selection exported successfully!")

				if self.user_settings["ExportRaimbow"]==True:
					self.print_color_for_publish_function()
				print(final_path)
				return
			except:
				mc.error("Impossible to export selection!")
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





	def create_new_item_template_function(self, event):
		#get informations to create new item architecture
		if mc.checkBox(self.template_fromselection_checkbox, query=True, value=True)==False:
			item_name = [mc.textField(self.template_textfield, query=True, text=True)]
		else:
			item_name = mc.ls(sl=True)
		template_name = mc.textScrollList(self.template_textscrolllist, query=True, si=True)
		template_type = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)

		if type(item_name) == str:
			if self.letter_verification_function(item_name) != True:
				mc.error("You have to define a name for the new item to create!")
				return
		elif type(item_name) == list:
			if len(item_name) == 0:
				mc.error("You have to select items!")
		else:
			mc.error("You have to select items!")
		if template_name == None:
			mc.error("You have to pick a template!")
			return
		template_name = template_name[0]
		if template_type == None:
			mc.error("You have to pick a type!")
			return


		#print(self.settings_dictionnary[template_type[0]])
		if (self.settings[template_type[0]][2] == None) or ("[key]" in self.settings[template_type[0]][2])==False:
			mc.error("You have to define a default folder, with a [key] inside!")
			return
		for name in item_name:
			starting_folder = self.settings[template_type[0]][2]

			while os.path.basename(starting_folder) != "[key]":
				starting_folder = os.path.dirname(starting_folder)

		
			if ("[Origin]" in starting_folder):
				starting_folder = starting_folder.replace("[Origin]",self.project_path)
				
			if ("[key]" in starting_folder):
				starting_folder = starting_folder.replace("[key]",template_type[0])
			if ("[name]" in starting_folder):
				starting_folder = starting_folder.replace("[name]", name)

			if ("[mayaProjectName]" in starting_folder):
				starting_folder = starting_folder.replace("[mayaProjectName]", self.additionnal_settings["mayaProjectName"])

			if ("[type]" in starting_folder) or ("[editPublishFolder]" in starting_folder):
				mc.error("Impossible to create new item with that default folder architecture!")
				return


			#add the name of the new folder to the starting path
			starting_folder = os.path.join(starting_folder, name)
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
			print("searching")
			return
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
				archive_data = pickle.load(read_file)
			key_list = list(archive_data.keys())
			if (archive_name in key_list)==True:
				mc.error("An archive with that name already exist!")
				return
			else:
				archive_data[archive_name] = archive_path
				with open(os.path.join(self.project_path, "PipelineManagerData/ArchiveData.dll"), "wb") as save_file:
					pickle.dump(archive_data, save_file)
		except:
			#create the archive file with the new archive
			archive_data = {
				archive_name:archive_path
			}
			os.makedirs(os.path.join(project_path, "PipelineManagerData"), exist_ok=True)
			with open(os.path.join(project_path, "PipelineManagerData/ArchiveData.dll"), "wb") as save_file:
				pickle.dump(archive_data, save_file)

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

		mc.textScrollList(self.archivemenu_textscrolllist, edit=True, removeAll=True, append=list(archive_data.keys()))
		mc.textScrollList(self.archive_archivelist_textscrolllist, edit=True, removeAll=True, append=list(archive_data.keys()))


	


	def display_archive_content_function(self):
		#get archive selection
		archive_selection = mc.textScrollList(self.archive_archivelist_textscrolllist, query=True, si=True)
		if archive_selection == None:
			mc.error("You have to select an archive!")
			return
		archive_selection = "PipoArchive_"+archive_selection[0]
		archive_keys = list(self.archive_data.keys())
		archive_values = list(self.archive_data.values())
		try:
			archive_index = archive_keys.index(archive_selection)
		except:
			mc.error("Impossible to find the archive!\nScan your pipeline!")
			return
		archive_path = archive_values[archive_index]
		if os.path.isfile(archive_path)==False:
			mc.error("This archive doesn't exist : %s"%archive_path)
			return
		else:
			#get the content of the archive:
			try:
				with zipfile.ZipFile(archive_path) as archive:
					content = archive.namelist()
				mc.textScrollList(self.archive_archivecontent_textscrolllist, edit=True, append=content)
			except:
				mc.error("Impossible to read the archive!")
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




	def add_to_favorite_scene_function(self, event):

		#get the file selection
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
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
		final_file_list = []
		for root, dirs, files in os.walk(path):
			#print(root)
			for f in files:
				#print(f in file_selection, f in final_file_list, f)
				if (f in file_selection) and (f in final_file_list)==False:
					final_file_list.append(os.path.join(root, f))
		favorite_file_data = self.user_settings["FavoriteFiles"]

		if len(final_file_list) != 0:
			for file in final_file_list:
				file = file.replace(os.sep, '/')
				favorite_file_data[os.path.basename(file)] = file


		self.user_settings["FavoriteFiles"] = favorite_file_data
		self.save_settings_file()
		self.apply_user_settings_function()




