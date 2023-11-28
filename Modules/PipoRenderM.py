import os
import maya.cmds as mc
import pymel.core as pm
import sys
import pickle
import yaml
import discord 
import asyncio
import glob
import scandir
import json

from functools import partial
from datetime import datetime


class PipelineRenderApplication:

	def import_from_shaderlibrary_function(self, event):
		#check the selection in shaderlist
		shader_selection = mc.textScrollList(self.saved_shader_textscrolllist, query=True, si=True)
		if (type(shader_selection)!= list) or (len(shader_selection) == 0):
			mc.error("You have to select a shader to import!")
			return 

		#get the path of the project
		project_path = mc.textField(self.project_label, query=True, text=True)

		for shader in shader_selection:
			#check if the shader exists in the folder
			if os.path.isfile(os.path.join(project_path, "PipelineManagerData/shaderDataBase/%s"%shader))==False:
				mc.warning("Shader skipped [%s]"%shader)
				continue
			else:
				try:
					mc.file(os.path.join(project_path, "PipelineManagerData/shaderDataBase/%s"%shader), i=True)
				except:
					mc.warning("Impossible to import the shader [%s]"%shader)
					continue





	def detect_missing_frames_function(self, event):
		#get all required informations
		#frame range
		starting_frame = mc.intField(self.render_startingframe_textfield, query=True, value=True)
		ending_frame = mc.intField(self.render_endingframe_textfield, query=True, value=True)

		if (self.default_render_nomenclature == None) or (self.root_render_folder == None):
			mc.error("You have to check the render folder before checking missing frames!\nImportant informations are missing!")
			return


		"""
		file dictionnary
			folder
				files
				files
			folder
				files
				files
		"""
		file_dictionnary = {}
		log_list = {
			"nomenclatureChecking":[],
			"missingFrames":[],
			"noSizeFile":[],
			"lightFiles":[],
			"averageRenderSize":"None"
		}

		


		for root_folder in self.root_render_folder:
			for element in os.listdir(root_folder):
				#check that it's a folder and not a file!
				if os.path.splitext(element)[1] == "":
					file_list = os.listdir(os.path.join(root_folder, element))
					
					"""
					check the syntax of each file in the folder
					"""
					for file in file_list:
						splited_file = os.path.splitext(file)[0].split(self.default_render_spliting_method)
						if len(splited_file) != len(self.default_render_nomenclature):
							mc.warning("File skipped because of wrong nomenclature [%s]"%file)

							#update error dictionnary
							nomenclature_checking = log_list["nomenclatureChecking"]
							nomenclature_checking.append(file)
							log_list["nomenclatureChecking"]=nomenclature_checking
							continue
						else:
							#check the index of the frame
							#check the index of the content
							content = splited_file[self.default_render_nomenclature.index("[content]")]
							frame = splited_file[self.default_render_nomenclature.index("[frame]")]
							
							if content not in file_dictionnary:
								file_dictionnary[content] = [[file, frame]]
							else:
								content_list = file_dictionnary[content]
								content_list.append([file, frame])
								file_dictionnary[content] = content_list

		if len(list(file_dictionnary.keys())) == 0:
			mc.error("No frame detected!")
			return


		"""
		for each frame check the syntax to get the frame
		create a loop that is frame range long --> check for missing frames
		for existing frames check the size of the file
		"""
		if (starting_frame >= ending_frame):
			mc.error("Wrong frame range in fields!")
			return



		frame_range = list(range(starting_frame, ending_frame))
		print(frame_range)


		"""
		need to compare the actual frame list (range list) with the files frames list
			import os
			file_size = os.path.getsize('d:/test_file.jpg')
			print("File Size is :", file_size)
		"""
		average_size = 0
		lower_size = 0


		

		for key, value in file_dictionnary.items():
			frame_list = []
			for file in value:
				#print(file[0])
				#list all frames
				#check the size of the file on the hardrive
				#print(file[0])
				
				for root_folder in self.root_render_folder:
					for root, dirs, files in os.walk(root_folder):
						for f in files:
							if f == file[0]:
								#checking size of the file
								file_size = os.path.getsize(os.path.join(root, f))

								if file_size == 0:
									no_size_file_list = log_list["noSizeFile"]
									no_size_file_list.append(f)
									log_list["noSizeFile"] = no_size_file_list
								else:
									if average_size == 0:
										average_size = file_size
										lower_size = (average_size * 95) / 100
										
									else:
										average_size = (average_size + file_size) / 2
										lower_size = (average_size * 80) / 100
										

									if (file_size <= lower_size):
										variable_frame_list = log_list["lightFiles"]
										variable_frame_list.append("%s : [%s]"%(f, file_size))
										log_list["lightFiles"] = variable_frame_list
									
									





				frame_list.append(int(file[1]))

			#print(frame_list)
			for frame in frame_range:
				#print(frame, frame in frame_list)
				if (frame in frame_list) == False:
					missing_frame_list = log_list["missingFrames"]
					missing_frame_list.append("%s : [%s]"%(key, frame))
					log_list["missingFrames"] = missing_frame_list
		log_list["averageRenderSize"] = average_size

		


		#create informations 
		#send to local textscrolllist

		"""
		EMOJIS
			:face_with_symbols_over_mouth:
		"""
		textscrolllist_info = []
		self.discord_message = "##########################################\n:loudspeaker:**RENDER CHECKING**:warning:\n##########################################\n"
		for key, value in log_list.items():

			self.discord_message += "\n\n__%s__\n"%key
			textscrolllist_info.append("\n")
			textscrolllist_info.append(key)

			if type(value) == list:
				for v in value:
					self.discord_message += "\t_%s_\n"%str(v)
					textscrolllist_info.append(str(v))
			else:
				textscrolllist_info.append("_%s_"%str(value))
				self.discord_message += "\t%s\n"%str(value)
		mc.textScrollList(self.render_renderlog_textscrolllist, edit=True, removeAll=True, append=textscrolllist_info)


		"""
		formatting text for discord message
		"""
		if mc.checkBox(self.render_checking_checkbox, query=True, value=True) == True:

			#try to get discord server informations in dictionnary
			self.token = self.additionnal_settings["discordBotToken"]
			self.channel_id = self.additionnal_settings["discordChannelId"]

			if (self.token == None) or (self.channel_id == None):
				mc.error("Missing informations to send messages on discord server!")
				return
			else:
				asyncio.run(self.send_discord_message_function())




	async def send_discord_message_function(self):
	    intents = discord.Intents.default()
	    intents.typing = False
	    intents.presences = False

	    client = discord.Client(intents=intents)

	    @client.event
	    async def on_ready():
	        print(f"We have logged in as {client.user}")
	        guild = client.get_guild(self.channel_id)
	        channel = discord.utils.get(guild.channels, name="général")
	        await channel.send(self.discord_message)
	        await client.close()

	    try:
	        await client.start(self.token)
	        # Ajouter une pause pour attendre que le bot soit prêt avant d'envoyer le message
	        await asyncio.sleep(5)
	    except KeyboardInterrupt:
	        print("Bot closed!")
	    except Exception as e:
	        print(f"An error occurred: {e}")








	
	





	def save_in_shaderlibrary_function(self, event):
		#get selection in current shader textscrolllist
		selection = mc.textScrollList(self.current_shader_textscrolllist, query=True, si=True)

		if (selection == None) or (len(selection)==0):
			mc.error("You have to select a shader to save!")
			return 
		else:
			
			#detect all shaders connections to select all nodes to save!
			self.all_connexions = []

			for shader in selection:
				"""
				for each shader selected
				get the shading engine to select
				"""
				shading_engine = mc.listConnections(shader, type="shadingEngine")

				if shading_engine == None:
					mc.warning("Shader skipped, Impossible to find shading engine [%s]"%shader)
				else:
					if (shading_engine in self.all_connexions)==False:
						self.all_connexions += shading_engine
			self.all_connexions += selection 

			#select element (NO EXTAND)
			#export the new file in the pipeline
			mc.select(self.all_connexions, r=True, ne=True)
			
			try:
				#create all required folders
				os.makedirs(os.path.join(mc.textField(self.project_label, query=True, text=True), "PipelineManagerData/shaderDataBase/"), exist_ok=True)
				mc.file(os.path.join(mc.textField(self.project_label, query=True, text=True), "PipelineManagerData/shaderDataBase/shader_%s.ma"%selection[0]), type="mayaAscii", es=True)
				print("Shader exported [shader_%s.ma]"%(selection[0]))
			
			except:
				mc.error("Impossible to export shader!")
				return
			#update the list in the textscrolllist
			#list files in the shader data base library
			content_list = os.listdir(os.path.join(mc.textField(self.project_label, query=True, text=True), "PipelineManagerData/shaderDataBase/"))
			file_list = []
			for content in content_list:
				
				if os.path.isfile(os.path.join(mc.textField(self.project_label, query=True, text=True), "PipelineManagerData/shaderDataBase/%s"%content))==True:
					#check the starting keyword in the filename
					filename = os.path.splitext(os.path.basename(content))[0].split("_")
					#print(filename)
					if filename[0] == "shader":
						file_list.append(content)
			mc.textScrollList(self.saved_shader_textscrolllist, edit=True, removeAll=True, append=file_list)

			






	def refresh_shaderlibrary_function(self,event):
		"""
		check shader list in current scene
		"""
		if self.additionnal_settings != None:
			if self.additionnal_settings["renderShaderNodeList"] != None:
				shader_list = []
				
				shader_node_list = self.additionnal_settings["renderShaderNodeList"]
				for shader_node in shader_node_list:
					try:
						shader_list+=mc.ls(type=shader_node)
					except:
						mc.warning("Impossible to get list of elements in scene\nfor this type [%s]"%shader_node)
						continue

				mc.textScrollList(self.current_shader_textscrolllist, edit=True, removeAll=True, append=sorted	(shader_list))

			#check saved shaders in pipelinemanagerdata folder
			try:
				saved_shader_list = os.listdir(os.path.join(mc.textField(self.project_label, query=True, text=True), "PipelineManagerData/shaderDataBase/"))
				if saved_shader_list != None:
					for element in saved_shader_list:
						if os.path.isfile(os.path.join(mc.textField(self.project_label, query=True, text=True), "PipelineManagerData/shaderDataBase/%s"%element))==False:
							saved_shader_list.remove(element)
						elif (element.startswith("shader_")==False) or (len(element.split("shader_"))!=2):
							saved_shader_list.remove(element)

				mc.textScrollList(self.saved_shader_textscrolllist, edit=True, removeAll=True, append=sorted	(saved_shader_list))
			except:
				mc.warning("Impossible to get saved shaders list!")
				return 


	def checking_frame_define_folder_function(self, event):
		"""
		try to define the starting folder
		project path + render folder in project path
		"""
		final_path = None	
		project_path = mc.workspace(query=True, active=True)
		if os.path.isdir(project_path)==True:
			final_path = project_path

			#print(self.additionnal_settings["renderFolderInProject"])
			if self.additionnal_settings["renderFolderInProject"] != None:
				#try to find that folder in the project
				found=False
				for r, d, f in os.walk(final_path):
					for directory in d:
						print(directory)
						if os.path.basename(directory) == self.additionnal_settings["renderFolderInProject"]:
							final_path = os.path.join(r, directory)
							print("FOUND!!!!")
							found=True
							break
					if found != False:
						break
		if found == False:
			mc.warning("Unable to find the render folder in the project!")
		#final path == starting folder


		folder=mc.fileDialog2(fm=3, startingDirectory=final_path)
		if folder == None:
			mc.error("You have to define a folder containing your batch render!")
			return
		print("Batch render folder defined successfully\n%s"%folder)

		"""
		check the first folder
		separate according to syntax settings and get first and last file!
		"""
		folder_list = os.listdir(folder[0])
		for element in folder_list:
			if os.path.splitext(element)[1] != "":
				folder_list.remove(element)
		if len(folder_list) == 0:
			mc.error("The folder doesn't contain anything!")
			return
		file_list = os.listdir(os.path.join(folder[0],folder_list[0]))
		for file in file_list:
			#check that it's a file
			if os.path.splitext(file)[0] == "":
				file_list.remove(file)

		#get the first file and the last file in the file list
		first_file=file_list[0]
		#get the snytax of the first file
		if len(self.additionnal_settings["renderFrameSyntax"]) == 0:
			mc.error("Impossible to get frame range!")
			return

		"""
		CHECKLIST FRAME NOMENCLATURE
			same split method (. _)
			same length
			same method
		"""
		syntax_result = False
		splited_syntax = None
		splited_filename = None
		spliting_method = None

		
		for syntax in self.additionnal_settings["renderFrameSyntax"]:
			f = os.path.splitext(file_list[0])[0]
			if "." in f:
				spliting_method = "."
			elif "_" in f:
				spliting_method = "_"
			else:
				mc.error("Impossible to split syntax!")
				return


			splited_syntax = syntax.split(spliting_method)
			splited_filename = f.split(spliting_method)

			if ("[content]" in splited_syntax) == False:
				mc.error("Impossible to get content in nomenclature!")
				return
			if ("[frame]" in splited_syntax)==False:
				mc.error("Impossible to get frame range in nomenclature!")
				return


			if len(splited_syntax) == len(splited_filename):
					print("SYNTAX FOUND!")
					syntax_result = True
					break
		
		if syntax_result ==False:
			mc.error("Renders are not matching with nomenclatures!")
			return

		#get first frame index
		frame_index = splited_syntax.index("[frame]")
		first_frame_content = splited_filename[splited_syntax.index("[content]")]
		first_frame = splited_filename[splited_syntax.index("[frame]")]


		file_list.pop(0)

		print("CHECKING CONTENT!")
		for file in file_list:
			#split the files according to the syntax method
			splited_f = os.path.splitext(file)[0].split(spliting_method)
			#print(splited_f, splited_filename)
			if len(splited_f) != len(splited_filename):
				continue
			else:
				frame_content = splited_f[splited_syntax.index("[content]")]
				if frame_content == first_frame_content:
					continue
				else:
					last_frame = splited_f[splited_syntax.index("[frame]")]
		if (last_frame.isdigit()==False) or (first_frame.isdigit()==False):
			mc.error("Frames are not well indicated in nomenclature!")
			return
		mc.intField(self.render_startingframe_textfield, edit=True, value=int(first_frame))
		mc.intField(self.render_endingframe_textfield, edit=True, value=int(last_frame))

		self.default_render_spliting_method = spliting_method
		self.root_render_folder = folder
		self.default_render_nomenclature = splited_syntax






	def create_texture_preset_function(self, event):
		project_path = mc.textField(self.project_label, query=True, text=True)
		"""
		for selection in hypershade save all the connexions and attributes of nodes
		"""
		#get the name of the preset
		preset_name = mc.textField(self.render_texture_preset_textfield, query=True, text=True)
		if self.letter_verification_function(preset_name) != True:
			mc.error("You have to enter a valid name for the preset!")
			return 

		#get node selection
		self.texture_data = {}

		try:
			with open(os.path.join(project_path, "PipelineManagerData/TexturePreset.json"), "r") as read_file:
				self.texture_data = json.load(read_file)

		except:
			mc.warning("Impossible to read texture preset file!")

		self.node_list = {}
		self.connexion_list = []
		#REMEMBER TO CHECK THAT THE NAME DOESNT ALREADY EXISTS IN THE SETTINGS
		if preset_name in self.texture_data:
			mc.error("This preset name already exist!")
			return 

		

		node_selection = mc.ls(sl=True)
		for element in node_selection:
			self.get_all_nodes_function(element)

		for element in node_selection:
			self.get_connexions(element)


		self.texture_data[preset_name] = {
			"node_list":self.node_list,
			"connexion_list":self.connexion_list
		}
	

		#open the dictionnary file
		#add the new dictionnary
		
		with open(os.path.join(project_path, "PipelineManagerData/TexturePreset.json"), "w") as save_file:
			save_file.write(json.dumps(self.texture_data, indent=4))
		print("Texture preset saved!")
		mc.textScrollList(self.render_preset_textscrolllist, edit=True, removeAll=True, append=list(self.texture_data.keys()))
		





	def get_connexions(self,x):
		input = mc.listConnections(x, source=True, destination=False, scn=True) or []
		connexions = mc.listConnections(x, c=True, p=True, scn=True) or []
		#output = mc.listConnections(x, source=False, destination=True) or []

		for i in range(0, len(connexions)):
			try:
				#get the connexions node name
				source_name = connexions[i].split(".")[0]
				destination_name = connexions[i+1].split(".")[0]
				
				if (source_name in self.node_list) and (destination_name in self.node_list):
					self.connexion_list.append((connexions[i], connexions[i+1]))

			except:
				pass
					
			
			
			
		for i in input:
			self.get_connexions(i)





	def get_all_nodes_function(self, x):
		if x not in self.node_list:
			attribute_dictionnary = {}
			for attr in mc.listAttr(x, se=True):

				try:	
					try:
						attribute_dictionnary[attr] = mc.getAttr("%s.%s"%(x, attr), type="string")
						
					except:
						attribute_dictionnary[attr] = mc.getAttr("%s.%s"%(x,attr))
				except:
					mc.warning("Impossible to save attribute [%s] for the node %s"%(attr, x))
				#print(attr)
				
			#print(mc.nodeType(x))
			#check if the name of the node is corresponding to a channel name
			#check if the type of the node is the same that the texture node for that channel
			channel = False

			render_settings = self.texture_settings[self.additionnal_settings["renderEngine"]]
			channel_data = render_settings["channelData"]

			for key, value in channel_data.items():
				#print(x, key, value["textureNode"], mc.nodeType(x))
				if (key in x) and (mc.nodeType(x)==value["textureNode"]):
					channel = key
					break
			
			#self.node_list[x] = [mc.nodeType(x), attribute_dictionnary]
			self.node_list[x] = {
				"nodeType":mc.nodeType(x),
				"nodeTextureChannel":channel,
				"nodeAttributes":attribute_dictionnary,
			}
		i = mc.listConnections(x, source=True, destination=False, scn=True) or []
		

		for input in i:
			self.get_all_nodes_function(input)



	def load_texture_data_funtion(self):
		project_path = mc.textField(self.project_label, query=True, text=True)
		try:
			with open(os.path.join(project_path, "PipelineManagerData/TexturePreset.json"), "r") as read_file:
				self.texture_data = json.load(read_file)
			print("Texture preset loaded!")

		except:
			mc.warning("Impossible to load texture preset data!")
			return 
		mc.textScrollList(self.render_preset_textscrolllist, edit=True, removeAll=True, append=list(self.texture_data.keys()))	




	def load_channel_data_function(self):
		try:
			channel_data = self.texture_settings[self.additionnal_settings["renderEngine"]]["channelData"]
		except:
			mc.error("Impossible to get Channel Data in settings!")
			return 
		channel_list = list(channel_data.keys())
		mc.textScrollList(self.texture_channel_textscrolllist, edit=True, removeAll=True, append=channel_list)


	def load_texture_in_project_function(self, event):
		#get project path
		current_project_path = mc.workspace(query=True, active=True)
		if os.path.isdir(current_project_path)==False:
			mc.warning("You have to set a project before!")
			return


		else:
			#get texture folder in project
			texture_folder_in_project = self.additionnal_settings["textureFolderInProject"]

			#go through the folders
			for root, dirs, files in scandir.walk(current_project_path):
				for d in dirs:
					if d == texture_folder_in_project:
						contenu = os.listdir(os.path.join(root, d))

						# Filtrer les dossiers parmi le contenu
						noms_de_dossiers = [element for element in contenu if os.path.isdir(os.path.join(os.path.join(root, d), element))]

						# Affichez la liste des noms de dossiers
						try:
							mc.textScrollList(self.texture_folder_textscrolllist, edit=True, removeAll=True, append=noms_de_dossiers)
						except:
							mc.error("Impossible to refresh texture folder list!")
							return




	def search_textures_function(self):
		#get selection in all list
		self.texture_list = {}
		current_project_path = mc.workspace(query=True, active=True)
		if os.path.isdir(current_project_path)==False:
			mc.error("You have to set a project before!")
			return
		texture_folder_selection = mc.textScrollList(self.texture_folder_textscrolllist, query=True, si=True)
		if texture_folder_selection == None:
			mc.error("You have to select a texture folder in project!")
			return
		#get the channel selection

		texture_extension_list = self.additionnal_settings["texturesExtension"]
		channel_selection = mc.textScrollList(self.texture_channel_textscrolllist, query=True, si=True)
		#get the whole path of the folder
		for i in range(0, len(texture_folder_selection)):
			for root, dirs, files in scandir.walk(current_project_path):
				for d in dirs:
					#print(d, texture_folder_selection[i])
					if d == texture_folder_selection[i]:
						#print("FOUND TEXTURE FOLDER!")
						texture_folder_selection[i] = os.path.join(root, d)

						#get all textures in selected folders
						file_list = os.listdir(os.path.join(root, d))
						for file in file_list:

							if os.path.isfile(os.path.join(os.path.join(root, d), file)) == True:
								#print("file found!")
								if os.path.splitext(file)[1] in texture_extension_list:

									if channel_selection != None:
										#get the list of keywords for that channel
										channel_data = self.texture_settings[self.additionnal_settings["renderEngine"]]["channelData"]
										for channel in channel_selection:
											if channel not in channel_data:
												mc.warning("Impossible to get keywords for this channel [%s]"%channel)

											else:
												found=False
												for keyword in channel_data[channel]["keywordList"]:
													if keyword in os.path.splitext(file)[0]:
														if file not in self.texture_list:
															self.texture_list[file] = [os.path.join(root, d), channel]
									"""
									else:
										if file not in self.texture_list:
											self.texture_list[file] = [os.path.join(root, d), False]
									"""


		
		mc.textScrollList(self.texture_result_textscrolllist, edit=True, removeAll=True, append=list(self.texture_list.keys()))




	def delete_texture_preset_function(self, event):
		#get selection in lists
		preset_selection = mc.textScrollList(self.render_preset_textscrolllist, query=True, si=True)
		if preset_selection == None:
			mc.error("You have to select a preset to delete!")
			return 
		#go through the preset file
		project_path = mc.textField(self.project_label, query=True, text=True)
		try:
			with open(os.path.join(project_path, "PipelineManagerData/TexturePreset.json"),"r") as read_file:
				texture_preset_data = json.load(read_file)
		except:
			mc.error("Impossible to open texture preset file!")
			return 
		try:
			texture_preset_data.pop(preset_selection[0])
		except:
			pass
		try:
			with open(os.path.join(project_path, "PipelineManagerData/TexturePreset.json"), "w") as save_file:
				save_file.write(json.dumps(texture_preset_data, indent=4))
		except:
			mc.error("Impossible to save texture preset file!")
			return 
		mc.textScrollList(self.render_preset_textscrolllist, edit=True, removeAll=True, append=list(texture_preset_data.keys()))




	def create_shader_from_texture_function(self,event):
		#check file selections and channel selected
		#both are required
		texture_selection = mc.textScrollList(self.texture_result_textscrolllist, query=True, si=True)
		channel_selection = mc.textScrollList(self.texture_channel_textscrolllist, query=True, si=True)
		preset_selection = mc.textScrollList(self.render_preset_textscrolllist, query=True, si=True)
		node_selection = mc.ls(sl=True)


		if (texture_selection == None) or (channel_selection == None):
			mc.error("You have to select textures and at least one channel!")
			return
		if preset_selection == None:
			mc.error("You have to select a preset to recreate!")
			return
		preset_selection = preset_selection[0]

		project_path = mc.textField(self.project_label, query=True, text=True)
		try:
			with open(os.path.join(project_path, "PipelineManagerData/TexturePreset.json"), "r") as read_file:
				texture_preset = json.load(read_file)
			self.node_list = texture_preset[preset_selection]["node_list"]
			self.connexion_list = texture_preset[preset_selection]["connexion_list"]
		except:
			mc.error("Impossible to read texture preset file!")
			return 

		#create an index of textures by channel
		#loop of node creation
		self.identifier_dictionnary = {}
		node_name_list = list(self.node_list.keys())
		self.replace_dictionnary = {}






		for node in node_name_list:
			print("\n%s"%node)
			#print(node)
			#print("create %s"%node)

			"""
			during the creation of the node, check if the node is linked to a channel
			if yes connect a texture of the same channel and after remove that texture from the texture to connect list
			"""
			
			error=False
			for node_selected in node_selection:
				if mc.nodeType(node_selected) == self.node_list[node]["nodeType"]:
					#replace the old node by the new one in the texture preset dictionnary
					print("REPLACE A NODE IN DICTIONNARY")
					error=True
					print()
					self.replace_dictionnary[node] = node_selected

			if error!=True:
				
				if self.node_list[node]["nodeType"] in self.texture_settings[self.additionnal_settings["renderEngine"]]["shadingNodes"]:
					new_node = mc.shadingNode(self.node_list[node]["nodeType"], asShader=True)
				else:
					new_node = mc.shadingNode(self.node_list[node]["nodeType"], asTexture=True)



				#set the attributes for that node
				attribute_dictionnary = self.node_list[node]["nodeAttributes"]
				for attr, attr_value in attribute_dictionnary.items():
					#print(attr, attr_value, node)
					try:
						try:
							mc.setAttr("%s.%s"%(new_node, attr), attr_value, type="string")
						except:
							mc.setAttr("%s.%s"%(new_node, attr), attr_value)
					except:
						mc.warning("Impossible to set attribute [%s] for the node %s"%(attr, new_node))




					
				#check that the node created got the same channel
				#check that this node is from the right type for that channel
				#print(self.node_list[node]["nodeTextureChannel"], channel_selection)
				#print(node, self.node_list[node]["nodeTextureChannel"], channel_selection)
				checked = False
				for channel in channel_selection:
					#print(str(self.node_list[node]["nodeTextureChannel"]), channel, str(self.node_list[node]["nodeTextureChannel"]) in channel)
					if (channel) in str(self.node_list[node]["nodeTextureChannel"]):
						checked=True 

				if checked==True:
					print('CHECKED')
					#go through the list of textures and connect one that is matching
					node_setting_type = self.texture_settings[self.additionnal_settings["renderEngine"]]["channelData"][self.node_list[node]["nodeTextureChannel"]]["textureNode"]
					#print("setting", node_setting_type, self.node_list[node]["nodeType"])

					if node_setting_type == self.node_list[node]["nodeType"]:
						try:
							for texture_name, texture_data in self.texture_list.items():
								#print("CHECKING %s, %s"%(texture_name, texture_data))
								if texture_name in texture_selection:

									if self.node_list[node]["nodeTextureChannel"] == texture_data[1]:
										
										attribute_for_texture = self.texture_settings[self.additionnal_settings["renderEngine"]]["textureNodes"][node_setting_type]

										#check the name of the texture and replace udims number by udims codes
										filename, extension = os.path.splitext(texture_name)

										#split the filename by dots
										splited_filename_dots = filename.split(".")
										splited_filename_underscore = filename.split("_")

										if mc.checkBox(self.render_udim_checkbox,query=True, value=True)==True:
											#try to find <UDIM>
											if len(splited_filename_dots) > 1:
												for i in range(1, len(splited_filename_dots)):

													
													if splited_filename_dots[i].isdigit() == True:
														#print("UDIM POTENTIALLY DETECTED!")
														#change the filename and replace the udim index by the undim code
														splited_filename_dots[i] = "<UDIM>"
														udim = True

														texture_name = ".".join(splited_filename_dots) + extension
														#print(texture_name)
														break
											
											if len(splited_filename_underscore) >=3 :
												u_value = splited_filename_underscore[-2]
												v_value = splited_filename_underscore[-1]

												if (u_value.split("u")[0] == "") and (u_value[1].isdigit()==True) and (v_value.split("v")[0] == "") and (v_value[1].isdigit()==True):
													splited_filename_underscore[-2] = "u<u>"
													splited_filename_underscore[-1] = "v<v>"
													#origin_filename = file_selection[y]
													texture_name = "_".join(splited_filename_underscore) + extension
													#print("UDIM POTENTIALLY DETECTED")
													#print(texture_name)
													udim = True

										

										print("\nCONNECTING TEXTURE\n%s"%texture_name)
										mc.setAttr("%s.%s"%(new_node,attribute_for_texture), os.path.join(texture_data[0], texture_name), type="string")
										self.texture_list.pop(texture_name)
						except:
							pass

			else:
				new_node = node_selected


			self.identifier_dictionnary[node] = {
				"node_name":new_node, 
				"node_type":self.node_list[node]["nodeType"],
				"node_texture":self.node_list[node]["nodeTextureChannel"],
				"node_identifier":mc.ls(new_node, uuid=True)[0],
			}
			


		for key, value in self.identifier_dictionnary.items():
			if key in self.replace_dictionnary:
				value["node_name"] = self.replace_dictionnary[key]
				self.identifier_dictionnary[key] = value

		

		for key, value in self.identifier_dictionnary.items():
			print(key, value)

		#print(self.replace_dictionnary)
	
	
		for connexion in self.connexion_list:
			origin_node, origin_attr = connexion[0].split(".")
			destination_node, destination_attr = connexion[1].split(".")

			


			#print(origin_connection, destination_connection)
			try:
				origin_connection = "%s.%s"%(self.identifier_dictionnary[origin_node]["node_name"],origin_attr)
				destination_connection = "%s.%s"%(self.identifier_dictionnary[destination_node]["node_name"], destination_attr)
				mc.connectAttr(origin_connection, destination_connection, f=True)
			except:
				print("connexion %s %s failed"%(origin_connection, destination_connection))
		
		








