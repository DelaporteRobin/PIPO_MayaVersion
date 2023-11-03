import maya.cmds as mc
import json



class Application:
	def __init__(self):
		self.texture_node_list = {
			"PxrTexture":"filename",
			"PxrNormalMap": "filename",
		}
		self.channel_preset_list = {
			"DIFFUSE": {
				"keyword":["diffuse", "diff", "Diffuse", "Diff"],
				"node":"PxrTexture",
			},
			"ROUGHNESS": {
				"keyword":["Roughness", "Rough", "rough", "roughness"],
				"node":"PxrTexture",
			},
			"NORMAL": {
				"keyword":["normal", "Normal"],
				"node":"PxrNormalMap",
			},
			"DISPLACE": {
				"keyword":["height", "displace", "displacement"],
				"node":"PxrTexture",
			},
		}
		path = "C:/Users/3D4/Desktop/data.json"
		self.node_list = {}
		self.connexion_list = []
		


		selection = mc.ls(sl=True)
		#get init list of nodes
		for element in selection:
			self.get_all_nodes_function(element)



		
		for element in selection:
			self.get_connexions(element)


		data = {
			"node_list":self.node_list,
			"connexion_list":self.connexion_list
		}
		with open(path, "w") as save_file:
			save_file.write(json.dumps(data, indent=4))
		print("saved!")


		
		



	def get_all_nodes_function(self, x):
		if x not in self.node_list:
			attribute_dictionnary = {}
			for attr in mc.listAttr(x, se=True):
				#print(attr)
				try:
					attribute_dictionnary[attr] = mc.getAttr("%s.%s"%(x, attr))
				except:
					pass
			#print(mc.nodeType(x))
			#check if the name of the node is corresponding to a channel name
			#check if the type of the node is the same that the texture node for that channel
			channel = False
			for key, value in self.channel_preset_list.items():
				if (key in x) and (mc.nodeType(x)==value["node"]):
					channel = x
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



Application()
