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
import scandir
import queue

from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler
from time import sleep
from functools import partial
from datetime import datetime



class PipelineObserverApplication:


	def parse_file_function(self, f):
		#print("Checking file : %s"%f)
		#print("Checking file %s %s"%(root, f))
		file_name = None
		
		#parse filename
		filename, extension = os.path.splitext(f)
		splited_filename = filename.split("_")
		



		for key, value in self.settings.items():

			error=False
			saved_key = None
			saved_type = None
			saved_name = None
			sqversion = None 
			shversion = None

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
				#print(key)
				#print(self.settings_dictionnary)
				if (splited_filename[index] in self.settings_dictionnary[key])==False:
		
					#print("type error")
					error=True
					continue
				else:
					saved_type = splited_filename[index]

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
						else:
							sqversion = splited_filename[index]
							

							
			if "[shversion]" in splited_syntax:
				index = splited_syntax.index("[shversion]")
				if (len(splited_filename[index].split("sh"))==2):
					if (splited_filename[index].split("sh")[0] != "") or (splited_filename[index].split("sh")[1].isdigit()==False):
						#print("shversion error")
						error=True 
						continue
					else:
						shversion = splited_filename[index]
						

						


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
				#return (file_name, key, saved_type)
				return {
					"file_name":file_name,
					"key":key,
					"saved_type":saved_type,
					"sqversion":sqversion,
					"shversion":shversion,
				}
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


	def process_file(self, file_queue):
		
		while True:
			file_path = file_queue.get()
			if file_path != None:
				path = os.path.dirname(file_path)
				filename, extension = os.path.splitext(os.path.basename(file_path))
				
					
				if os.path.basename(file_path) in self.pipeline_index:
					#check the path in the pipeline
					if os.path.isfile(self.pipeline_index[os.path.basename(file_path)]["fullpath"])==False:
						self.pipeline_index[os.path.basename(file_path)] = {
							"path":(r""+path).replace("\\", "/").replace(os.sep, "/"),
							"fullpath": (r""+os.path.join(path, filename)).replace("\\", "/").replace(os.sep, "/"),
							"filename":filename,
						}
				else:
					#launch parsing
					
					value = self.parse_file_function(os.path.basename(file_path))
					if value != False:
					
						self.pipeline_index[os.path.basename(file_path)] = {
							"path":(r""+path).replace("\\", "/").replace(os.sep, "/"),
							"fullpath": (r""+os.path.join(path, filename)).replace("\\", "/").replace(os.sep, "/"),
							"filename":filename,
						}
					
						

					with self.lock:
						if file_path not in self.processed_files:
							self.processed_files.add(file_path)
					
			
			file_queue.task_done()



	
	def create_pipeline_index_function(self, project_path):
		print("\nStarting creation of Pipeline index : ")
		print("Pipeline index creation in progress ...")
	
		#self.pipeline_index = {}
	
		
		#self.already_checked_file = []
		full_size = 0
		"""
		for root,_,files in scandir.walk(project_path):
			full_size += len(files)
		"""
		file_queue = queue.Queue()
		self.lock = threading.Lock()
		self.processed_files = set()
		
		
		for root, folders, files in scandir.walk(project_path):
			if os.path.basename(root) not in self.additionnal_settings["dodgeList"]:
				for file in files:
					filename, extension = os.path.splitext(file)
					if (extension in self.additionnal_settings["3dSceneExtension"]) or (extension in self.additionnal_settings["3dItemExtension"]):
						file_path = os.path.join(root, file)
						file_queue.put(file_path)
	

		size = file_queue.qsize()

		print("Number of files to check : %s\n"%size)

		
		
		num_thread = 4
		threads = []
		#self.semaphore = threading.Semaphore(num_thread)
		self.start_thread_moment = datetime.now()

		self.start_index_moment = datetime.now()

		for i in range(num_thread):
			#self.semaphore.acquire()
			print("STARTING THREAD! =====================================================\n")
			thread = threading.Thread(target=self.process_file, args=(file_queue,))
			thread.start()
			threads.append(thread)

		
		for thread in threads:
			file_queue.put(None)
		for thread in threads:
			thread.join()
		


		self.end_index_moment = datetime.now()

		print("\nDone searching in %s"%project_path)
		print("Delta : %s"%(self.end_index_moment - self.start_index_moment))
		self.save_pipeline_index_function()
			
		"""
		#FIRST VERSION OF INDEX CREATION SYSTEM
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
						}
		"""
		
		
	
		
		

	





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
			#print("Pipeline index saved successfully!")
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
		try:
			for file, data in self.pipo.pipeline_index.items():
				full_path = os.path.join(data["path"], file)
		
				if os.path.isfile(full_path) == False:
					

					try:
						del self.pipo.pipeline_index[file]
					except:
						pass 
		except:
			print("Impossible to check ghost files now!")
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

