#coding: utf-8
#PIPELINE MANAGER

#Copyright 2023, Robin Delaporte AKA Quazar, All rights reserved.



import threading
import os 
import maya.cmds as mc
import pymel.core as pm
import json
import pickle
import sys

from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler
from time import sleep
from functools import partial
from datetime import datetime



class PipelineObserverApplication:


	def parse_file_function(self, f):
		
		#print("Checking file %s %s"%(root, f))
		file_name = None
		
		#parse filename
		filename, extension = os.path.splitext(f)
		splited_filename = filename.split("_")
		



		for key, value in self.settings.items():

			error=False
			syntax = value[0]
			splited_syntax = syntax.split("_")
			#print(splited_syntax)

			if len(splited_filename) != len(splited_syntax):
				error=True
				continue
			#print(f)
			#print("	checking with %s"%key)

			if "[type]" in splited_syntax:
				index = splited_syntax.index("[type]")
		
				if (splited_filename[index] in self.settings_dictionnary[key])==False:
		
					#print("type error")
					error=True
					continue

			if "[key]" in splited_syntax:
				index = splited_syntax.index("[key]")
				#print(splited_filename[index], key)
				if splited_filename[index] != key:
					#print("key error")
					error=True
					continue
			

			if "[project]" in splited_syntax:
				index = splited_syntax.index("[project]")

				project_name = os.path.basename(self.project_path)
				if splited_filename[index] != project_name:
					#print("project error")
					error=True
					continue

			if "[version]" in splited_syntax:
				index = splited_syntax.index("[version]")

				if splited_filename[index] != self.additionnal_settings["editPublishFolder"][1]:
					if (len(splited_filename[index].split("v"))==2):
						if (splited_filename[index].split("v")[0] != "") or (splited_filename[index].split("v")[1].isdigit()==False):
							#print("version error")
							error=True
							continue
							

			if "[sqversion]" in splited_syntax:
					index = splited_syntax.index("[sqversion]")
					if (len(splited_filename[index].split("sq"))==2):
						if (splited_filename[index].split("sq")[0] != "") or (splited_filename[index].split("sq")[1].isdigit()==False):
							#print("sqversion error")
							error=True 
							continue
							

							
			if "[shversion]" in splited_syntax:
				index = splited_syntax.index("[shversion]")
				if (len(splited_filename[index].split("sh"))==2):
					if (splited_filename[index].split("sh")[0] != "") or (splited_filename[index].split("sh")[1].isdigit()==False):
						#print("shversion error")
						error=True 
						continue
						

						


			if ("[name]" in splited_syntax):
				name = splited_filename[splited_syntax.index("[name]")]
				#print("name detected %s"%splited_filename[splited_syntax.index("[name]")])
				file_name = name
				


			if ("[artist]" in splited_syntax):
				artist = splited_filename[splited_syntax.index("[artist]")]
				if (self.letter_verification_function(artist) == False) or (self.letter_verification_function(artist)==None):
					#print("artist error")
					error=True
					continue

			if error==False:
				return file_name
		return False
			
		

		


	




	
	def watch_folder(self, path):
		self.event_handler = MyHandler(self)
		observer = Observer()
		observer.schedule(self.event_handler, path=path, recursive=True)
		observer.start()
		print("observer launched!")

		
		while mc.window(self.main_window, exists=True)==True:
			value = mc.window(self.main_window, exists=True)
			#print(value, type(value))
			#print(mc.window(self.main_window, exists=True))
			sleep(1)
	
		print("Observer stopped")
		observer.stop()
		observer.join()


	
	def create_pipeline_index_function(self, project_path):
	
		self.pipeline_index = {}

		try:
			for root, dirs, files in os.walk(project_path):
				
				
				for f in files:
					
					value = self.parse_file_function(f)
					


					filename, extension = os.path.splitext(os.path.basename(f))
					
					if value!=False:
						#print(value, f)
					
							
						self.pipeline_index[f] = {
							"path":(r""+root).replace("\\", "/").replace(os.sep, "/"),
							"fullpath": (r""+os.path.join(root, f)).replace("\\", "/").replace(os.sep, "/"),
							"filename":filename,
							"filesize": os.path.getsize(os.path.join(root, f)),
							"filedate": (datetime.fromtimestamp(os.path.getmtime(os.path.join(root, f)))).strftime("%Y-%m-%d")
							}
			self.save_pipeline_index_function()	

			print("Done searching in %s"%project_path)
		
		except:
			mc.error("Impossible to create pipeline index!")
			return
		
		

	





	def save_pipeline_index_function(self):
		#save the pipeline index in the Pipeline folder
		json_dictionnary = {
			"mirrorSettings":self.settings,
			"mirrorSettingsDictionnary":self.settings_dictionnary,
			"pipelineIndex":self.pipeline_index,
		}
		try:
			with open(os.path.join(self.project_path, "PipelineManagerData/PipelineIndex.json"), 'w') as save_file:
				save_file.write(json.dumps(json_dictionnary, indent=4))
			print("Pipeline index saved successfully!")
			return
		except:
			mc.error("Impossible to save Pipeline index in Pipeline!")
			return

	



		
class MyHandler(FileSystemEventHandler):

	def __init__(self, pipo_application):
		self.pipo = pipo_application
		#self.pipo.say_hello()
		

	def on_modified(self, event):
		if not event.is_directory:
			#print('modified')
			
			filepath = event.src_path
			if os.path.basename(filepath) != "PipelineIndex.json":
				#print("Modified\n")
				file_data = {
					"path":(os.path.dirname(event.src_path)).replace(os.sep, "/"),
					"fullpath":(event.src_path).replace(os.sep, "/"),
					"filename":os.path.splitext(os.path.dirname(event.src_path))[0],
					"filesize":os.path.getsize(event.src_path),
					"filedate":(datetime.fromtimestamp(os.path.getmtime(event.src_path))).strftime("%Y-%m-%d")
				}
				value = self.pipo.parse_file_function(os.path.basename(event.src_path))

				#go through the whole index and delete files that doesn't exist anymore
				if value != False:
					#print("value after modifying %s [%s]"%(value, event.src_path))
					self.delete_ghost_files_function()

					self.pipo.save_pipeline_index_function()

	def on_created(self, event):
		if not event.is_directory:
			#print("created")
			filepath = event.src_path
			file_data = {
				"path":(os.path.dirname(event.src_path)).replace(os.sep, "/"),
				"fullpath":(event.src_path).replace(os.sep, "/"),
				"filename":os.path.splitext(os.path.dirname(event.src_path))[0],
				"filesize":os.path.getsize(event.src_path),
				"filedate":(datetime.fromtimestamp(os.path.getmtime(event.src_path))).strftime("%Y-%m-%d")
			}
			#print("Created\n")
			#print(filepath)
			self.pipo.pipeline_index[os.path.basename(filepath)] = file_data
			#print(self.pipo.pipeline_index)
			value = self.pipo.parse_file_function(os.path.basename(event.src_path))
			if value != False:
				#print("value after creating %s [%s]"%(value, event.src_path))
				self.delete_ghost_files_function()
				self.pipo.save_pipeline_index_function()

	def delete_ghost_files_function(self):
		#print("\nDELETE ALL GHOST FILES IN INDEX\n")
		for file, data in self.pipo.pipeline_index.items():
			full_path = os.path.join(data["path"], file)
	
			if os.path.isfile(full_path) == False:
				

				try:
					del self.pipo.pipeline_index[file]
				except:
					pass 	

	def on_moved(self, event):
		#replace the old value by the new value
		if not event.is_directory:
			#print("moved")
			old_path = event.src_path
			new_path = event.dest_path

			
			
			#find the old key in the dictionnary
			#remove it 
			#change it by the new values
			try:
				del self.pipo.pipeline_index[os.path.basename(event.src_path)]
			except:
				pass
			self.delete_ghost_files_function()
			#check if the new filename is correct
			value = self.pipo.parse_file_function(os.path.basename(event.dest_path))
			#print("value after moving %s [%s]"%(value, event.src_path))
			if value != False:

				filepath = event.dest_path
				file_data = {
					"path":(os.path.dirname(event.dest_path)).replace(os.sep, "/"),
					"fullpath":(event.dest_path).replace(os.sep, "/"),
					"filename":os.path.splitext(os.path.dirname(event.dest_path))[0],
					"filesize":os.path.getsize(event.dest_path),
					"filedate":(datetime.fromtimestamp(os.path.getmtime(event.dest_path))).strftime("%Y-%m-%d")
				}
				self.pipo.pipeline_index[os.path.basename(event.dest_path)] = file_data
				
				self.pipo.save_pipeline_index_function()
				#print("MOVED")
			

	def on_deleted(self, event):
		if not event.is_directory:
			#print("deleted")
			#print(event.src_path)
			#get the value of the file in the dictionnary
			#delete this key
			#save the new dictionnary
			if (os.path.basename(event.src_path)) in self.pipo.pipeline_index:
				#print("detected")
				try:
					del self.pipo.pipeline_index[os.path.basename(event.src_path)]
					self.delete_ghost_files_function()
					self.pipo.save_pipeline_index_function()
					
				except:
					pass 
