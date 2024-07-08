import maya.cmds as mc
import json



class CreateConnections:
	def __init__(self):
		self.shader_node_list = [
			"PxrSurface",
			"PxrLayerSurface",
			"PxrDisplace",
			]
		path = "C:/Users/3D4/Desktop/data.json"
		
		#load data in json files
		with open(path, "r") as read_file:
			data = json.load(read_file)
		self.node_list = data["node_list"]
		self.connexion_list = data["connexion_list"]


		node_name_list = list(self.node_list.keys())
		print(node_name_list)

		self.identifier_dictionnary = {}
		
		#create each node of the dictionnary
		#for each node
		#get the uuid of the new node created
		for node in node_name_list:
			print("create %s"%node)
			if self.node_list[node]["nodeType"] in self.shader_node_list:
				new_node = mc.shadingNode(self.node_list[node]["nodeType"], asShader=True)
			else:
				new_node = mc.shadingNode(self.node_list[node]["nodeType"], asTexture=True)
			self.identifier_dictionnary[node] = {
				"node_name":new_node, 
				"node_type":self.node_list[node]["nodeType"],
				"node_texture":self.node_list[node]["nodeTextureChannel"],
				"node_identifier":mc.ls(new_node, uuid=True)[0],
				}

		print("\n")


		for key, value in self.identifier_dictionnary.items():
			print(key, value)
		
		print("TRYING TO CREATE THE CONNEXION")
		#make the connexion
		for connexion in self.connexion_list:

			origin_node, origin_attr = connexion[0].split(".")
			destination_node, destination_attr = connexion[1].split(".")

			origin_connection = "%s.%s"%(self.identifier_dictionnary[origin_node]["node_name"],origin_attr)
			destination_connection = "%s.%s"%(self.identifier_dictionnary[destination_node]["node_name"], destination_attr)


			print(origin_connection, destination_connection)
			try:
				mc.connectAttr(origin_connection, destination_connection, f=True)
			except:
				pass


		






CreateConnections()
