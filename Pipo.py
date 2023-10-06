#coding: utf-8
#PIPELINE MANAGER

#Copyright 2023, Robin Delaporte AKA Quazar, All rights reserved.



#archive documentation : https://realpython.com/python-zipfile/
import threading
import maya.cmds as mc
import pymel.core as pm
import os  
import ctypes
import sys
import json
import pickle

from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler

from time import sleep
from functools import partial
from datetime import datetime






def onMayaDroppedPythonFile(*args):
	#create the path for all the functions
	path = '/'.join(__file__.replace("", "/").split("/")[:-1])
	sys.path.append(path)
"""
if (os.getcwd() in sys.path)==False:
	sys.path.append(os.getcwd())
"""




from Pipo.Modules.PipoM import PipelineApplication 
from Pipo.Modules.PipoRenderM import PipelineRenderApplication
from Pipo.Modules.PipoObserverM import PipelineObserverApplication
#from Pipo.Modules.PipoObserverM import MyHandler








class PipelineGuiApplication(PipelineApplication, PipelineRenderApplication, PipelineObserverApplication):
 	
 	
	def create_script_button_function(self):
		#try to detect all the scripts presents in the script folder of Pipo Pipeline Manager folder
		#check if Pipo's shelf exists
		if not mc.shelfLayout("PipoShelf",exists=True):
			mc.warning("Impossible to import external scripts!")
			return 
		if os.path.isdir(os.path.join(self.project_path, "PipelineManagerData/scripts"))==True:
			#print all scripts that are present in the folder
			elements = os.listdir(os.path.join(self.project_path, "PipelineManagerData/scripts"))
			for element in elements:
				if os.path.splitext(element)[1] != ".py":
					elements.remove(element)
			print("\nScripts detected in Pipeline Folder")
			
			"""
			for each script try to create a button and launch an exec function

			"""
			
			for script in elements:
				print("Creating button for script [%s]"%script)
				script_name = os.path.splitext(script)[0]

				button_name_list = []
				try:
					for name in mc.shelfLayout("PipoShelf", query=True, childArray=True):
					   button_name_list.append(mc.shelfButton(name, query=True, label=True))
				except:
					pass
				


				if (script_name in button_name_list)==False:
					if os.path.isfile(os.path.join(self.project_path, "PipelineManagerData/scripts/icons/%s.png"%script_name))==True:
						image = (os.path.join(self.project_path, "PipelineManagerData/scripts/icons/%s.png"%script_name))

						with open(os.path.join(self.project_path, "PipelineManagerData/scripts/%s.py"%script_name), "r") as read_file:
							script_content = read_file.read()

						button = mc.shelfButton(
							label=script_name,
							annotation=script_name,
							image=image,
							style="iconAndTextCentered",
							parent=self.pipo_shelf,
							command=script_content,
							)
						print("Image detected [%s.png]"%script_name)
					else:
						mc.warning("Impossible to create a button for that script!\nNo icon detected!")
				else:
					print("A button already exists for the script [%s]"%script_name)





	def __init__(self):

		self.bright_color = [0.570, 0.166, 0.0855]
		self.dark_color = [0.250, 0.158, 0.140]

		print("Pipo Launching...")
		self.current_name = None
		self.current_type = None



		#define the program folder
		self.program_folder = None
		for path in sys.path:
			if os.path.isdir(os.path.join(path, "Pipo"))==True:
				os.chdir(os.path.join(path, "Pipo"))
				self.program_folder = os.path.join(path, "Pipo")
				mc.warning("Program folder defined")
		if self.program_folder == None:
			mc.warning("The program folder wasn't defined!")
			return







		#create interface shelf on maya
		if not mc.shelfLayout("PipoShelf",exists=True):
			#create button to execute the program
			#read the content of Pipo's code
			print(os.getcwd())
			if os.path.isfile("Data/icons/PipoIcon.png")==False:
				mc.warning("Impossible to load icon for Pipo button!")

			elif (os.path.isfile("Pipo.py")==False):
				mc.warning("Impossible to create Pipo button!")
			else:
				self.pipo_shelf = mc.shelfLayout("PipoShelf",p="ShelfLayout")
				with open("Pipo.py", "r") as read_script:
					pipo_script = read_script.read()

				#pipo_script = mc.runTimeCommand( annotation='Print the word "Hello"', command='print "Hello\\n"', MyHelloCommand )
				button = mc.shelfButton(
				    label="PipoMain",
				    image=os.path.join(os.getcwd(),"Data/icons/PipoIcon.png"),
				    style="iconOnly",
				    width=32,
				    parent=self.pipo_shelf,
				    command=pipo_script
				  	)
				#sys.exit()
				
			
		else:
			self.pipo_shelf = mc.shelfLayout("PipoShelf", query=True, fullPathName=True)

		

			
		
		

		#check if the module list file exist
		#self.project_path = mc.workspace(query=True, rd=True)
		self.project_path = None
		self.window_width = 450
		self.window_height=450

		letter = 'abcdefghijklmnopqrstuvwxyz'
		figure = '0123456789'

		self.list_letter = list(letter)
		self.list_capital = list(letter.upper())
		self.list_figure = list(figure)

		self.texture_folder_list = {}
		self.texture_list = {}
		
		self.folder_path = os.getcwd()

		self.item_type_list = [
			".ma",
			".mb",
			".obj",
			".tex",
			".exr",
			".tif",
			".png",
			".vdb"]

		self.log_list_content = []

		self.texture_to_connect_list = []
		#load settings stored in files
		#if the file doesn't exist
		#create a new file with default settings
		#check the current project of maya
		if os.path.isdir("Data/icons/")==False:
			mc.warning("Impossible to find icons folder!")
			self.icons_folder=False 
		else:
			print("Icons folder found!")
			self.icons_folder=True





		if os.path.isfile("Data/PipelineData.dll")==True:
			try:
				with open("Data/PipelineData.dll", "rb") as read_file:
					self.project_path = pickle.load(read_file)
				if type(self.project_path)==list:
					self.project_path = self.project_path[0]
				if os.path.isdir(self.project_path)==False:
					mc.warning("The saved project folder doesn't exist with the same path on that computer!")
					self.project_path = "None"
				else:
					mc.warning("Project Path loaded!")
			except:
				mc.error("Impossible to read the pipeline data file!")
				self.project_path = "None"
		else:
			self.project_path = "None"
			mc.warning("No informations loaded!")




				



		self.create_script_button_function()

		#launch the function that check
		#if the shader settings file exists
		#if it doesn't create it

		#self.shader_init_function()

		self.settings = {}
		self.settings_dictionnary = {}
		self.additionnal_settings = {}
		self.texture_settings = {}


		self.settings, self.settings_dictionnary, self.additionnal_settings, self.texture_settings, self.user_settings = self.load_settings_function()
	
		
		
	  


		self.archive_data = {}
		if os.path.isdir(self.project_path)==True:
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/ArchiveData.dll"), "rb") as read_file:
					self.archive_data = pickle.load(read_file)

			except:
				mc.warning("Impossible to load archive data!")

			#check if the index folder exists
			"""
			if index doesn't exist
				create the index
			if the index exist
				check the settings mirror
					if settings mirror != settings
						recreate the index with parsing
			"""
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineIndex.json"), "r") as read_file:
					content = json.load(read_file)

				self.settings_mirror = content["mirrorSettings"]
				self.settings_dictionnary_mirror = content["mirrorSettingsDictionnary"]
				self.pipeline_index = content["pipelineIndex"]

				#if (self.settings != self.settings_mirror) or (self.settings_dictionnary_mirror != self.settings_dictionnary):
				self.create_pipeline_index_thread = threading.Thread(target=partial(self.create_pipeline_index_function, self.project_path))
				self.create_pipeline_index_thread.start()
				
				#else:
				#	print("Index loaded, no difference in mirrors!")
			
			except:
				mc.warning("Impossible to load Pipeline index!")

				#launch pipeline index
				self.create_pipeline_index_thread = threading.Thread(target=partial(self.create_pipeline_index_function, self.project_path))
				self.create_pipeline_index_thread.start()



		
			#CREATE LISTENER
			self.watchdog_thread = threading.Thread(target=self.watch_folder, args=(self.project_path,))
			self.watchdog_thread.start()

		#IMPORTANTS VARIABLES
		self.receive_notification = True
		self.message_thread_status = True
		self.window_name = None

		self.pack_function_list = {}


		self.file_type = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]
		self.variable_list = ["[key]", "[project]", "[type]", "[state]", "[version]", "[sqversion]", "[shversion]"]
		self.default_folder_list = []
		self.new_step_list = []
		self.new_type_list = []
		self.name_list_value = []
		self.type_list_value = []
		self.file_list_value = []
		self.result_list_value = []
		self.previous_log_team = []
		self.launch_message_thread = False

		self.default_render_spliting_method = None
		self.default_render_nomenclature = None
		self.root_render_folder = None

		self.build_pipeline_interface_function()








	
	def resize_command_function(self):
		#get the window width
		width = mc.window(self.main_window, query=True, width=True)
		height= mc.window(self.main_window, query=True, height=True)

		
		
			
	
		







	def build_pipeline_interface_function(self):
		self.main_window = mc.window(sizeable=False, title="Pipo - Written by Quazar", width=self.window_width, height=self.window_height)

		#self.scrollbar = mc.scrollLayout(width=self.window_width + 40, parent=self.main_window, resizeCommand=self.resize_command_function)
		self.main_column = mc.columnLayout(adjustableColumn=True, parent=self.main_window)
		self.add_log_content_function("Interface built")
		#self.main_window = mc.window(title="PipelineManager", sizeable=True, height=self.window_height, width=self.window_width)
		self.pack_function_list["Pipeline"] = ["PipelineManagerTool"]


		#self.main_column = mc.columnLayout(adjustableColumn=True)
		

		self.form_pipeline = mc.formLayout(parent=self.main_column)
		self.tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5, parent=self.form_pipeline)
		mc.formLayout(self.form_pipeline, edit=True, attachForm=((self.tabs,"top",0), (self.tabs, "bottom",0),(self.tabs,"left",0),(self.tabs,"right",0)))

		"""
		ASSETS
		character, props, sets, fx
		mod, rig, groom, cloth, lookdev, alembic
		
		SHOTS
		sequence, shots
		layout, camera, matte painting, anim, render

		POSTPROD
		sequence, shots
		renders, compositing
		"""
		#main scroll layout of the asset page
		self.prod_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		#self.asset_main_scroll = mc.scrollLayout(horizontalScrollBarThickness=1, width=self.window_width+16, parent=self.prod_column, resizeCommand=self.resize_command_function, height=self.window_height)
		


		#DEFINE PROJECT FOLDER
		mc.separator(style="none", height=15, parent=self.prod_column)

		
		self.project_columns = mc.rowColumnLayout(numberOfColumns=4, parent=self.prod_column, columnWidth=((1, self.window_width/2)))
		self.project_label = mc.textField(editable=False, backgroundColor=[0.2, 0.2, 0.2], parent=self.project_columns, text=self.project_path)

		if self.icons_folder == False:
			mc.button(label="Set Project Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "project"))
			mc.button(label="Set Other Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "folder"))
		else:
			mc.iconTextButton(style="iconOnly", width=60, parent=self.project_columns, image1="Data/icons/project_icon.png", command=partial(self.define_project_path_ui_function, "event", "project"))
			mc.iconTextButton(style="iconOnly", width=60, parent=self.project_columns, image1="Data/icons/folder_icon.png", command=partial(self.define_project_path_ui_function, "event", "folder"))
		self.loading_status = mc.text(label="")
		mc.separator(style="singleDash", height=25, parent=self.prod_column)


		#self.assets_search_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Search for assets", parent=self.prod_column, collapsable=True, collapse=False, width=self.window_width)


		self.assets_main_rowcolumn = mc.rowColumnLayout(parent=self.prod_column, numberOfColumns=2, columnWidth=((1, self.window_width/3)))
		self.assets_main_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.assets_main_rowcolumn)
		self.assets_main_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.assets_main_rowcolumn)





		mc.rowColumnLayout(self.assets_main_rowcolumn, edit=True, adjustableColumn=2)
		if self.project_path !="None":
			for key, value in self.settings.items():
				self.type_list_value.append(key)

		self.note_column = mc.columnLayout(adjustableColumn=True, parent=self.assets_main_rightcolumn)
		self.favorite_frame = mc.frameLayout(backgroundColor=self.bright_color, parent=self.note_column, label="Favorite scenes", collapsable=True, collapse=True)
		self.favorite_list = mc.textScrollList(numberOfRows=8, parent=self.favorite_frame, doubleClickCommand=partial(self.open_location_function, "open", "event"))
		mc.button(label="Delete Favorite", parent=self.favorite_frame, command=self.delete_favorite_file_function)
		mc.separator(style="singleDash", height=15, parent=self.favorite_frame)
		
		
		self.note_textfield = mc.scrollField(parent=self.note_column, height=40, wordWrap=True, font="plainLabelFont", enterCommand=self.save_note_function)
		self.assets_prod_column = mc.rowColumnLayout(numberOfColumns=4, parent=self.assets_main_rightcolumn, columnWidth=((1, self.window_width/6), (2, self.window_width/6), (3, self.window_width/6)))
		self.type_list=mc.textScrollList(allowMultiSelection=True, numberOfRows=13,parent=self.assets_prod_column, selectCommand=self.display_new_list_function, append=self.type_list_value)
		self.name_list=mc.textScrollList(allowMultiSelection=True, numberOfRows=13, parent=self.assets_prod_column, selectCommand=self.display_new_list_function)
		self.kind_list=mc.textScrollList(allowMultiSelection=True, numberOfRows=13, parent=self.assets_prod_column, selectCommand=self.display_new_list_function, append=self.file_type)
		self.result_list=mc.textScrollList(allowMultiSelection=True, numberOfRows=10, parent=self.assets_main_rightcolumn, doubleClickCommand=partial(self.open_file_function, "event"), selectCommand=self.search_for_thumbnail_function)

			
		mc.rowColumnLayout(self.assets_prod_column, edit=True, adjustableColumn=4)

	
		#SEARCHBAR
		self.searchbar_limit_frame = mc.frameLayout(backgroundColor=self.bright_color, parent=self.assets_main_leftcolumn, label="Research settings", collapsable=True, collapse=True)
		self.index_checkbox = mc.checkBox(label="Use Index file", value=True, parent=self.searchbar_limit_frame)
		self.searchbar_checkbox = mc.checkBox(label="Limit research to project", value=False, parent=self.searchbar_limit_frame, changeCommand=partial(self.save_additionnal_settings_function, "none"), onCommand=partial(self.save_additionnal_settings_function, "project"))
		self.folder_checkbox = mc.checkBox(label="Limit research to default\nfolder", value=False, parent=self.searchbar_limit_frame, changeCommand=partial(self.save_additionnal_settings_function, "none"), onCommand=partial(self.save_additionnal_settings_function, "folder"))
		self.scenes_checkbox = mc.checkBox(label="Search for 3D Scenes", value=True, parent=self.searchbar_limit_frame, changeCommand=partial(self.save_additionnal_settings_function, None))
		self.items_checkbox = mc.checkBox(label="Search for 3D Items", value=False, parent=self.searchbar_limit_frame, changeCommand=partial(self.save_additionnal_settings_function, None))
		self.textures_checkbox = mc.checkBox(label="Search for Textures", value=False, parent=self.searchbar_limit_frame, changeCommand=partial(self.save_additionnal_settings_function, None))
		mc.separator(style="singleDash", parent=self.searchbar_limit_frame)
		mc.text(label="Searchbar", parent=self.assets_main_leftcolumn)
		self.main_assets_searchbar = mc.textField(parent=self.assets_main_leftcolumn, changeCommand=self.searchbar_function, enterCommand=self.searchbar_function)
		mc.text(label="3D Scene extension", parent=self.searchbar_limit_frame)
		self.assets_scene_extension_textfield = mc.textField(parent=self.searchbar_limit_frame, enterCommand=partial(self.save_additionnal_settings_function, None))
		mc.text(label="3D Exported Items extension", parent=self.searchbar_limit_frame)
		self.assets_items_extension_textfield = mc.textField(parent=self.searchbar_limit_frame, enterCommand=partial(self.save_additionnal_settings_function, None))
		mc.text(label="Textures extension", parent=self.searchbar_limit_frame)
		self.assets_textures_extension_textfield = mc.textField(parent=self.searchbar_limit_frame, enterCommand=partial(self.save_additionnal_settings_function, None))

		"""
		if self.additionnal_settings != None:
			mc.checkBox(self.searchbar_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][0])
			mc.checkBox(self.folder_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][1])
		"""
		
		#IMAGE BOX
		mc.separator(style="none", height=10)
		self.image_box = mc.image(parent=self.assets_main_leftcolumn, visible=True, backgroundColor=self.dark_color, height=self.window_width/5, width=self.window_width/5)
		mc.button(label="Save Thumbnail", parent=self.assets_main_leftcolumn, command=self.take_picture_function)
		mc.separator(style="none", height=10, parent=self.assets_main_leftcolumn)
		mc.button(label="Save Scene", parent=self.assets_main_leftcolumn, command=self.save_current_scene_function)
		mc.button(label="Set Project", parent=self.assets_main_leftcolumn, command=self.set_project_function)
		mc.button(label="Open scene folder", parent=self.assets_main_leftcolumn, command=partial(self.open_location_function, "folder"))
		mc.button(label="Add scenes to favorites", parent=self.assets_main_leftcolumn, command=self.add_to_favorite_scene_function)

		mc.separator(style="singleDash", height=25, parent=self.assets_main_leftcolumn)

		mc.button(label="Add Script to Shelf", parent=self.assets_main_leftcolumn, command=self.add_script_to_shelf_function)
		

		#RENAME
		self.assets_rename_frame = mc.frameLayout(backgroundColor=self.bright_color,label = "Rename files", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.text(label="Content to rename", parent=self.assets_rename_frame)
		self.rename_oldcontent_textfield = mc.textField(parent=self.assets_rename_frame)
		mc.text(label="New content", parent=self.assets_rename_frame)
		self.rename_newcontent_textfield = mc.textField(parent=self.assets_rename_frame)

		mc.text(label="Prefix", parent=self.assets_rename_frame)
		self.rename_prefix_textfield = mc.textField(parent=self.assets_rename_frame)
		mc.text(label="Suffix", parent=self.assets_rename_frame)
		self.rename_suffix_textfield = mc.textField(parent=self.assets_rename_frame)

		mc.button(label="Rename", parent=self.assets_rename_frame, command=partial(self.rename_filename_function, "RENAME"))

		self.hardrename_checkbox_file = mc.checkBox(label="Include files", parent=self.assets_rename_frame, changeCommand=partial(self.save_additionnal_settings_function, "none"))
		self.hardrename_checkbox_folder = mc.checkBox(label="Include folders", parent=self.assets_rename_frame, changeCommand=partial(self.save_additionnal_settings_function, "none"))
		mc.button(label="Hard Rename in Pipeline", enable=False, command=partial(self.rename_filename_function, "HARDRENAME"))


		

		#IMPORT
		self.assets_import_frame = mc.frameLayout(backgroundColor=self.bright_color, label = "Import files", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.button(label="Import in scene", parent=self.assets_import_frame, command=partial(self.import_in_scene_function, False))
		mc.button(label="Import as reference", parent=self.assets_import_frame, command=partial(self.import_in_scene_function, True))


		self.assets_archive_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Archive files", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.text(label="Archive name", parent=self.assets_archive_frame)
		self.archivemenu_textfield = mc.textField(parent=self.assets_archive_frame)

		self.archivemenu_textscrolllist = mc.textScrollList(numberOfRows=8, parent=self.assets_archive_frame)
		mc.text(label="Archive saved at", align="left",parent=self.assets_archive_frame)
		self.archivemenu_projectcheckbox = mc.checkBox(label="project root", value=False, parent=self.assets_archive_frame, changeCommand=partial(self.update_archive_checkbox_function, "project"))
		self.archivemenu_pipelinecheckbox = mc.checkBox(label="pipeline root",value=True, parent=self.assets_archive_frame, changeCommand=partial(self.update_archive_checkbox_function, "pipeline"))
		mc.button(label="Create archive from files", parent=self.assets_archive_frame, command=self.create_archive_from_files_function)
		mc.button(label="Add files to archive", parent=self.assets_archive_frame, command=self.add_files_to_archive_function)

		




		if (self.project_path != None) and (self.additionnal_settings!= None):
			"""
			mc.checkBox(self.searchbar_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][0])
			mc.checkBox(self.scenes_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][1])
			mc.checkBox(self.items_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][2])
			mc.checkBox(self.textures_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][3])
			mc.checkBox(self.folder_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][4])"""
			mc.textField(self.assets_scene_extension_textfield, edit=True, text=";".join(self.additionnal_settings["3dSceneExtension"]))
			mc.textField(self.assets_items_extension_textfield, edit=True, text=";".join(self.additionnal_settings["3dItemExtension"]))
			mc.textField(self.assets_textures_extension_textfield, edit=True, text=";".join(self.additionnal_settings["texturesExtension"]))
			"""
				except:
					mc.warning("Impossible to launch GUI Presets on Mai page!")
			"""









		"""
		INSTEAD OF DELETING FILES
		OR IF SOME FILES ARE TOO HEAVY TO BE TRANSPORTED
		"""

		#ARCHIVE
		"""
		create archive in the pipeline (empty)
		create archive from a (parallel process) folder
		create archive of the (parallel process) pipeline

		move files inside of the archive
		move files out of the archive
		read the content of the archive
		"""
		self.archive_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		self.archive_rowcolumn = mc.rowColumnLayout(numberOfColumns=3, columnWidth=((1, self.window_width/3), (2, self.window_width*(1/3)), (3, self.window_width*(1/3))))

		self.archive_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.archive_rowcolumn)
		self.archive_centercolumn = mc.columnLayout(adjustableColumn=True, parent=self.archive_rowcolumn)
		self.archive_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.archive_rowcolumn)
		
		mc.separator(style="none", height=20, parent=self.archive_leftcolumn)
		mc.button(label="Scan pipeline\nto find archives", parent=self.archive_leftcolumn)
		mc.button(label="Import files in project", parent=self.archive_leftcolumn)
		mc.button(label="Generate download link\nfrom archive", parent=self.archive_leftcolumn)
		mc.button(label="Delete archive", parent=self.archive_leftcolumn)

		mc.text(label="Archive list", parent=self.archive_centercolumn)
		self.archive_archivelist_textscrolllist = mc.textScrollList(numberOfRows=15, parent=self.archive_centercolumn, selectCommand=self.display_archive_content_function)

		mc.text(label="Archive content", parent=self.archive_rightcolumn)
		self.archive_archivecontent_textscrolllist = mc.textScrollList(numberOfRows=15, parent=self.archive_rightcolumn)






		archive_key = list(self.archive_data.keys())
		for i in range(0, len(archive_key)):
			archive_key[i] = archive_key[i].replace("PipoArchive_", "")
		mc.textScrollList(self.archivemenu_textscrolllist, edit=True, append=archive_key)
		mc.textScrollList(self.archive_archivelist_textscrolllist, edit=True, append=archive_key)


		











		"""
		RENDERS PANEL
		MISSING FRAMES CHECKING
			logs box
			check for missing frames button
			[send notification on discord checkbox]
		"""
		self.render_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)

		self.render_texture_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Texture linking", parent=self.render_column, collapsable=True, collapse=True)
		self.render_texture_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, int(self.window_width/3)),(2, self.window_width*2/3)))
		self.render_texture_column_options = mc.columnLayout(adjustableColumn=True, parent=self.render_texture_rowcolumn)
		self.render_texture_right_column = mc.columnLayout(adjustableColumn=True, parent=self.render_texture_rowcolumn)
		self.render_texture_right_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, parent=self.render_texture_right_column, columnWidth=((1, self.window_width/3), (2, self.window_width/3)))
		self.render_texture_column_names = mc.columnLayout(adjustableColumn=True, parent=self.render_texture_right_rowcolumn)
		self.render_texture_column_channel = mc.columnLayout(adjustableColumn=True, parent=self.render_texture_right_rowcolumn)
		#self.render_texture_column_result = mc.columnLayout(adjustableColumn=True, parent=self.render_texture_rowcolumn)
		self.render_texture_result_column = mc.columnLayout(adjustableColumn=True, parent=self.render_texture_right_column)

		mc.text(label="Textures names found", parent=self.render_texture_column_names)
		mc.text(label="Textures channel list", parent=self.render_texture_column_channel)
		#mc.text(label="Textures files found",parent=self.render_texture_column_result)
		self.render_texture_list_names = mc.textScrollList(numberOfRows=15, parent=self.render_texture_column_names, selectCommand=self.search_for_texture_function)
		self.render_texture_list_channel = mc.textScrollList(numberOfRows=15, parent=self.render_texture_column_channel, allowMultiSelection=True, selectCommand=self.search_for_texture_function)
		self.render_texture_list_result = mc.textScrollList(numberOfRows=8, parent=self.render_texture_result_column)

		mc.separator(style="none", parent=self.render_texture_column_options, height=10)
		self.render_texture_manual_checkbox = mc.checkBox(label="Manual connection", value=False, parent=self.render_texture_column_options, changeCommand=partial(self.render_texture_change_checkbox_function, "manual"))
		self.render_texture_automatic_checkbox = mc.checkBox(label="Automatic connection", value=True, parent=self.render_texture_column_options, changeCommand=partial(self.render_texture_change_checkbox_function, "automatic"))
		mc.separator(style="singleDash", parent=self.render_texture_column_options, height=20)
		self.render_texture_limit_project = mc.checkBox(label="Limit research\nto project", changeCommand=partial(self.save_additionnal_settings_function, "none"), value=False, parent=self.render_texture_column_options)
		self.render_texture_udim_checking = mc.checkBox(label="Check for udims", value=True, changeCommand=partial(self.save_additionnal_settings_function, "none"), parent=self.render_texture_column_options)

		mc.button(label="REFRESH", parent=self.render_texture_column_options, command=self.refresh_texture_name_function)
		mc.button(label="Connect\nto selected", command=self.connect_texture_to_selected_shader_function, parent=self.render_texture_column_options)

		#print(self.texture_settings)
		#add elements in textscrolllist
		if self.additionnal_settings != None:
			if (self.additionnal_settings["renderEngine"] in list(self.texture_settings.keys()))==True:
				render_settings = self.texture_settings[self.additionnal_settings["renderEngine"]]
				channel_list = list(self.texture_settings[self.additionnal_settings["renderEngine"]].keys())
				mc.textScrollList(self.render_texture_list_channel, edit=True, removeAll=True, append=channel_list)

			#print(self.additionnal_settings["textureFolderInProject"])
			if (self.additionnal_settings["textureFolderInProject"] != None):
				self.refresh_texture_name_function(None)
				self.search_for_texture_function()

				





		self.render_missingframes_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Checking for missing frames", parent=self.render_column, collapsable=True, collapse=True)

		self.render_missingframes_rowcolumn=mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/3), (2, int(self.window_width - self.window_width/3))), parent=self.render_missingframes_frame)
		self.render_missingframes_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.render_missingframes_rowcolumn)
		self.render_missingframes_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.render_missingframes_rowcolumn)

		mc.button(label="Define render folder", parent=self.render_missingframes_leftcolumn, command=self.checking_frame_define_folder_function)
		mc.separator(style="none", height=10, parent=self.render_missingframes_leftcolumn)
		
		mc.text(label="Starting frame", parent=self.render_missingframes_leftcolumn)
		self.render_startingframe_textfield = mc.intField(parent=self.render_missingframes_leftcolumn)
		mc.text(label="Ending frame", parent=self.render_missingframes_leftcolumn)
		self.render_endingframe_textfield = mc.intField(parent=self.render_missingframes_leftcolumn)

		mc.separator(style="none", height=10)
		self.render_checking_checkbox = mc.checkBox(label="Send message on discord", changeCommand=partial(self.save_additionnal_settings_function, "none"), parent=self.render_missingframes_leftcolumn, value=True)
		mc.button(label="CHECK MISSING FRAMES", command=self.detect_missing_frames_function, parent=self.render_missingframes_leftcolumn)

		self.render_renderlog_textscrolllist = mc.textScrollList(numberOfRows=15, parent=self.render_missingframes_rightcolumn)




		self.render_shaderlibrary_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Shader library", parent=self.render_column, collapsable=True, collapse=True)
		"""
		list of saved shaders
		list of current shaders
		"""
		self.render_shaderlibrary_rowcolumn = mc.rowColumnLayout(parent=self.render_shaderlibrary_frame,numberOfColumns=3, columnWidth=((1, self.window_width/3), (2, self.window_width/3), (3, self.window_width/3)))
		self.render_shaderlibrary_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.render_shaderlibrary_rowcolumn)
		self.render_shaderlibrary_centercolumn = mc.columnLayout(adjustableColumn=True, parent=self.render_shaderlibrary_rowcolumn)
		self.render_shaderlibrary_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.render_shaderlibrary_rowcolumn)

		mc.text(label="Shaders in current scene", parent=self.render_shaderlibrary_centercolumn)
		mc.text(label="Saved shaders", parent=self.render_shaderlibrary_rightcolumn)
		self.current_shader_textscrolllist = mc.textScrollList(allowMultiSelection=True, parent=self.render_shaderlibrary_centercolumn, numberOfRows=15)
		self.saved_shader_textscrolllist = mc.textScrollList(parent=self.render_shaderlibrary_rightcolumn, allowMultiSelection=True, numberOfRows=15)

		mc.separator(style="none", height=15, parent=self.render_shaderlibrary_leftcolumn)
		mc.button(label="REFRESH", parent=self.render_shaderlibrary_leftcolumn, command=self.refresh_shaderlibrary_function)
		mc.button(label="Save shader", parent=self.render_shaderlibrary_leftcolumn, command=self.save_in_shaderlibrary_function)
		mc.button(label="Import shader", parent=self.render_shaderlibrary_leftcolumn, command=self.import_from_shaderlibrary_function)


		self.refresh_shaderlibrary_function("event")




		



	








		self.export_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		#self.export_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.export_column, height=self.window_height, resizeCommand=self.resize_command_function)
		self.export_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width*(1/3)), (2, self.window_width*(2/3))), parent=self.export_column)

		self.export_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.export_rowcolumn)
		self.export_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.export_rowcolumn)

		mc.separator(style="none", height=20, parent=self.export_leftcolumn)
		self.export_current_folder_checkbox = mc.checkBox(label="Export in current folder",value=False, parent=self.export_leftcolumn, changeCommand=partial(self.change_export_checkbox_value_function, "current"))
		self.export_custom_folder_checkbox = mc.checkBox(label="Export in custom folder", value=False, parent=self.export_leftcolumn, changeCommand=partial(self.change_export_checkbox_value_function, "custom"))
		self.export_assist_folder_checkbox = mc.checkBox(label="Default folder\nlocation assist", value=True, parent=self.export_leftcolumn, changeCommand=partial(self.change_export_checkbox_value_function, "assist"))
		self.export_projectassist_folder_checkbox = mc.checkBox(label="Current project\ndefault folder", value=False, parent=self.export_leftcolumn, changeCommand=partial(self.change_export_checkbox_value_function, "projectassist"))
		mc.separator(style="none", height=10, parent=self.export_leftcolumn)

		mc.text(label="Current artist name", parent=self.export_leftcolumn, align="left")
		self.export_artist_name_textfield = mc.textField(parent=self.export_leftcolumn)

		mc.separator(style="none", height=20, parent=self.export_leftcolumn)

		
		self.export_item_checkbox = mc.checkBox(label="Export as item", changeCommand=partial(self.save_additionnal_settings_function, "none"), parent=self.export_leftcolumn)
		mc.separator(style="none", height=5, parent=self.export_leftcolumn)

		#CREATE NEW TEMPLATE
		#SAVE NEW TEMPLATE
		mc.separator(style="none", height=10, parent=self.export_leftcolumn)
		self.template_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Edit Template", parent=self.export_leftcolumn, collapsable=True, collapse=True)
		mc.text(parent=self.template_frame, label="New template name")
		self.template_textfield = mc.textField(parent=self.template_frame)
		mc.button(label="Save new template", parent=self.template_frame, command=self.create_template_function)
		mc.button(label="Delete template", parent=self.template_frame, command=self.delete_template_function)
		mc.separator(style="none", height=10, parent=self.template_frame)
		
		self.template_fromselection_checkbox = mc.checkBox(label="Create from outliner selection", parent=self.template_frame, value=False)
		mc.separator(style="singleDash", height=5, parent=self.template_frame)

		

		mc.separator(style="none", height=15, parent=self.export_leftcolumn)
		self.template_textscrolllist = mc.textScrollList(numberOfRows=5, parent=self.export_leftcolumn)
		self.export_edit_name_checkbox = mc.checkBox(label="Keep same name", changeCommand=partial(self.save_additionnal_settings_function, "none"), value=True, parent=self.export_leftcolumn)
		mc.separator(style="singleDash", height=2, parent=self.export_leftcolumn)
		mc.text(label="Item Name", align="left", parent=self.export_leftcolumn)
		self.export_edit_name_textfield = mc.textField(parent=self.export_leftcolumn)

		mc.separator(style="none", height=15, parent=self.export_leftcolumn)
		mc.button(label="Create New Item architecture", parent=self.export_leftcolumn, command=partial(self.create_new_item_template_function, False))
		#mc.button(label="Create New Item  architeture\nand Export", parent=self.export_leftcolumn, command=partial(self.create_new_item_template_function, True))

		self.reload_template_function()


		self.export_edit_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Export edit files", parent=self.export_leftcolumn, collapsable=True, collapse=True)	
		
		mc.text(label="File Version", align="left", parent=self.export_edit_frame)
		#self.export_edit_version_checkbox = mc.checkBox(label="Automatic version check", value=False, parent=self.export_edit_frame)
		self.export_edit_version_intfield = mc.intField(parent=self.export_edit_frame)

		mc.text(label="Sequence number", align="left", parent=self.export_edit_frame)
		self.export_edit_sequence_intfield = mc.intField(parent=self.export_edit_frame)

		mc.text(label="Shot number", align="left", parent=self.export_edit_frame)
		self.export_edit_shot_intfield = mc.intField(parent=self.export_edit_frame)
		
		
		mc.button(label="Save Edit", parent=self.export_edit_frame, command=partial(self.export_edit_function, "standard"),backgroundColor=self.dark_color)
		mc.button(label="Export selected", parent=self.export_edit_frame, command=partial(self.export_edit_function, "selection"))

		self.export_publish_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Export publish files", parent=self.export_leftcolumn, collapsable=True, collapse=True)
		mc.button(label="Save Publish", parent=self.export_publish_frame, command=partial(self.export_publish_function, "standard"),backgroundColor=self.dark_color)
		#self.export_publish_keepname_checkbox = mc.checkBox(label="Keep item name", parent=self.export_leftcolumn)
		mc.button(label="Publish selected", parent=self.export_publish_frame,command=partial(self.export_publish_function, "selection"))



		#textscrolllist of export window
		self.export_right_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width*(2/6)), (2, self.window_width*(2/6))), parent=self.export_rightcolumn)
		
		
		self.export_type_textscrolllist = mc.textScrollList(numberOfRows=25, parent=self.export_right_rowcolumn, allowMultiSelection=False, selectCommand=self.update_export_kind_information)
		self.export_kind_textscrolllist = mc.textScrollList(numberOfRows=25, parent=self.export_right_rowcolumn, allowMultiSelection=False)
		if self.settings != None:
			mc.textScrollList(self.export_type_textscrolllist, edit=True, removeAll=True, append=list(self.settings.keys()))


		








		"""
		self.log_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs, height=self.window_height)
		self.log_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.log_column, height=self.window_height, resizeCommand=self.resize_command_function)

		self.log_program_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Program Log", labelAlign="top", width=self.window_width, collapsable=True, collapse=True,parent=self.log_scroll)
		self.log_list = mc.textScrollList(parent=self.log_program_frame, allowMultiSelection=False, enable=True, height=self.window_height/2, append=self.log_list_content)

		self.log_team_frame = mc.frameLayout(backgroundColor=self.bright_color, label="Team logs", width=self.window_width, collapsable=True, collapse=True, parent=self.log_scroll)
		self.lost_team_list = mc.textScrollList(parent=self.log_team_frame, allowMultiSelection=False, enable=True, height=self.window_height/2)
		"""




		mc.tabLayout(self.tabs, edit=True, tabLabel=((self.prod_column, "PROD ASSETS"), (self.export_column, "EXPORT"), (self.render_column, "RENDER"), (self.archive_column, "ARCHIVE")))
		#self.dock_control = mc.dockControl(label="Pipo - Written by Quazar", enablePopupOption=True, floating=True, area="left", content=self.main_window, allowedArea=["right", "left"])


		self.apply_user_settings_function()


		mc.showWindow()







	
	
	def apply_user_settings_function(self):
		if (self.program_folder != None) and (self.program_folder != "None"):
			try:
				mc.checkBox(self.searchbar_checkbox, edit=True, value=self.user_settings["checkboxValuesMainPage"][0])
				mc.checkBox(self.folder_checkbox, edit=True, value=self.user_settings["checkboxValuesMainPage"][1])
				mc.checkBox(self.scenes_checkbox, edit=True, value=self.user_settings["checkboxValuesMainPage"][2])
				mc.checkBox(self.items_checkbox, edit=True, value=self.user_settings["checkboxValuesMainPage"][3])
				mc.checkBox(self.textures_checkbox, edit=True, value=self.user_settings["checkboxValuesMainPage"][4])

				mc.checkBox(self.hardrename_checkbox_file, edit=True, value=self.user_settings["checkboxValuesRenamePanel"][0])
				mc.checkBox(self.hardrename_checkbox_folder, edit=True, value=self.user_settings["checkboxValuesRenamePanel"][1])

				mc.checkBox(self.render_texture_manual_checkbox, edit=True, value=self.user_settings["checkboxValuesTextureLinkingPanel"][0])
				mc.checkBox(self.render_texture_automatic_checkbox, edit=True, value=self.user_settings["checkboxValuesTextureLinkingPanel"][1])
				mc.checkBox(self.render_texture_limit_project, edit=True, value=self.user_settings["checkboxValuesTextureLinkingPanel"][2])
				mc.checkBox(self.render_texture_udim_checking, edit=True, value=self.user_settings["checkboxValuesTextureLinkingPanel"][3])

				mc.checkBox(self.render_checking_checkbox, edit=True, value=self.user_settings["checkboxValuesMissingFramesPanel"][0])

				mc.checkBox(self.export_current_folder_checkbox, edit=True, value=self.user_settings["checkboxValuesExportPanel"][0])
				mc.checkBox(self.export_custom_folder_checkbox, edit=True, value=self.user_settings["checkboxValuesExportPanel"][1])
				mc.checkBox(self.export_assist_folder_checkbox, edit=True, value=self.user_settings["checkboxValuesExportPanel"][2])
				mc.checkBox(self.template_fromselection_checkbox, edit=True, value=self.user_settings["checkboxValuesExportPanel"][4])
				mc.checkBox(self.export_edit_name_checkbox, edit=True, value=self.user_settings["checkboxValuesExportPanel"][5])
				mc.checkBox(self.export_projectassist_folder_checkbox, edit=True, value=self.user_settings["checkboxValuesExportPanel"][3])


				favorite_files = self.user_settings["FavoriteFiles"]
				favorite_file_list = list(favorite_files.keys())
				mc.textScrollList(self.favorite_list, edit=True, removeAll=True, append=favorite_file_list)

			
			except:
				mc.warning("Impossible to apply user settings on GUI!")
				return
			


	def update_archive_checkbox_function(self, command, event):
		if command == "project":
			if mc.checkBox(self.archivemenu_projectcheckbox, query=True, value=True)==True:
				mc.checkBox(self.archivemenu_pipelinecheckbox, edit=True, value=False)
			else:
				mc.checkBox(self.archivemenu_pipelinecheckbox, edit=True, value=True)
		if command == "pipeline":
			if mc.checkBox(self.archivemenu_pipelinecheckbox, query=True, value=True)==True:
				mc.checkBox(self.archivemenu_projectcheckbox, edit=True, value=False)
			else:
				mc.checkBox(self.archivemenu_projectcheckbox, edit=True, value=True)
		self.save_additionnal_settings_function("none", "none")


	def render_texture_change_checkbox_function(self, command, event):
		if command == "manual":
			if mc.checkBox(self.render_texture_manual_checkbox, query=True, value=True)==True:
				mc.checkBox(self.render_texture_automatic_checkbox, edit=True, value=False)
				mc.textScrollList(self.render_texture_list_channel, edit=True, allowMultiSelection=False)
		if command == "automatic":
			if mc.checkBox(self.render_texture_automatic_checkbox, query=True, value=True)==True:
				mc.checkBox(self.render_texture_manual_checkbox, edit=True, value=False)
				mc.textScrollList(self.render_texture_list_channel, edit=True, allowMultiSelection=True)

		self.save_additionnal_settings_function("none", "none")


	def change_export_checkbox_value_function(self, command, event):
		if command == "custom":
			if mc.checkBox(self.export_custom_folder_checkbox, query=True, value=True)==True:
				mc.checkBox(self.export_current_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_assist_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_projectassist_folder_checkbox, edit=True, value=False)
		elif command == "current":
			if mc.checkBox(self.export_current_folder_checkbox, query=True, value=True)==True:
				mc.checkBox(self.export_custom_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_assist_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_projectassist_folder_checkbox, edit=True, value=False)
		elif command == "assist":
			if mc.checkBox(self.export_assist_folder_checkbox, query=True, value=True)==True:
				mc.checkBox(self.export_custom_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_current_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_projectassist_folder_checkbox, edit=True, value=False)
		elif command == "projectassist":
			if mc.checkBox(self.export_projectassist_folder_checkbox, query=True, value=True)==True:
				mc.checkBox(self.export_custom_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_assist_folder_checkbox, edit=True, value=False)
				mc.checkBox(self.export_current_folder_checkbox, edit=True, value=False)
		self.save_additionnal_settings_function("none", "none")
		
			


	def update_export_kind_information(self):
		selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)[0]

		#get list of kind in settings
		mc.textScrollList(self.export_kind_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[selection])


	def display_settings_informations_function(self):
		#get the textscrolllist selection
		selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		if selection != None:
			for key, value in self.settings_dictionnary.items():
				if key == selection[0]:
					try:
						mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=value)
					except:
						mc.warning("Impossible to display list!")
						pass

			for key, value in self.settings.items():
				#print(key, selection[0])
				if key == selection[0]:
					mc.textField(self.setting_syntax_textfield, edit=True, text=self.settings[key][0])
					mc.textField(self.setting_keyword_textfield, edit=True, text=self.settings[key][1])


					if (value[2] != None):
						mc.button(self.setting_default_folder_button, edit=True, label=value[2])
					else:
						mc.button(self.setting_default_folder_button, edit=True, label="Default Folder")
					"""
					if self.settings[key][2] != None:
						mc.button(self.setting_folder_button, edit=True, label=self.settings[key][2])
					else:
						mc.button(self.setting_folder_button, edit=True, label="None")
					"""



	def export_publish_samelocation_function(self, event):
		search_folder = mc.checkBox(self.export_publish_searchlocation_checkbox, query=True, value=True)
		if search_folder == True:
			mc.checkBox(self.export_publish_searchlocation_checkbox, edit=True, value=False)
	def export_publish_searchlocation_function(self, event):
		same_folder = mc.checkBox(self.export_publish_samelocation_checkbox, query=True, value=True)
		if same_folder == True:
			mc.checkBox(self.export_publish_samelocation_checkbox, edit=True, value=False)

		

	


	def enable_publish_file_name_function(self, event):
		if mc.checkBox(self.export_publish_checkbox, query=True, value=True)==True:
			mc.textField(self.export_publish_textfield, edit=True, enable=False)
		else:
			mc.textField(self.export_publish_textfield, edit=True, enable=True)





	def refresh_export_type_list_function(self):
		#take the content
		type_list = []
		try:
			for kind, content in self.settings_dictionnary.items():
				type_list.append(kind)
		except:
			pass
		mc.textScrollList(self.export_edit_kind_textscrolllist, edit=True, removeAll=True, append=type_list)






	def export_edit_display_version_field_function(self):
		#query the value of the current item selected in the option menu
		try:
			selection = mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)[0]
		except:
			return
		#check in dictionnary settings if the current selection contain [version], [shotversion] or [seqversion]
		for kind, content in self.settings.items():
			syntax = content[0].split("_")

			if kind == selection:
				if ("[version]" in syntax)==False:
					mc.intField(self.export_edit_fileversion, edit=True, enable=False)
				else:
					mc.intField(self.export_edit_fileversion, edit=True, enable=True)

				if ("[shversion]" in syntax)==False:
					mc.intField(self.export_edit_shotversion, edit=True, enable=False)
				else:
					mc.intField(self.export_edit_shotversion, edit=True, enable=True)

				if ("[sqversion]" in syntax)==False:
					mc.intField(self.export_edit_sqversion, edit=True, enable=False)
				else:
					mc.intField(self.export_edit_sqversion, edit=True, enable=True)

				#print(type_list)
				type_list = self.settings_dictionnary[kind]
				mc.textScrollList(self.export_edit_type_textscrolllist, edit=True, removeAll=True, append=type_list)

				return

				"""
				for element in type_list:
					mc.menuItem(self.export_edit_type_menu, label=element)"""


	

		

	def export_name_checkbox_function(self, event):
		checkbox_value = mc.checkBox(self.export_name_checkbox, query=True, value=True)
		
		if checkbox_value == True:
			mc.textField(self.export_name_textfield, edit=True, enable=False)
		else:
			mc.textField(self.export_name_textfield, edit=True, enable=True)

	

		

PipelineGuiApplication()