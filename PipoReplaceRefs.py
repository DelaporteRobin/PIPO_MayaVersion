import maya.cmds as mc
import json
import os



"""
TASKLIST:
	get refs selection

	get the path of the first reference
	check if the type lookdev is in the path
	replace the type by lookdevN
		in the path 
		in the filename

	if the file exist replace the reference by the new one
	assign the shader of the new references (for each mesh inside)
	by the shader of the same mesh in the main reference
"""


class Application:
	def __init__(self):
		#loaded
		print("PipoReplaceRefs launched")

		self.width=250
		self.height=400

		self.program_path = os.getcwd()

		self.main_interface()


	def create_default_settings(self):
		"""
		LIST OF POSSIBLE SWITCH
		lookdev, lookdevNaked, lookdevProxy
		"""
		self.switch_settings = {
			"lookdevNaked":"lookdevNaked",
			"lookdevProxy":"lookdevProxy",
			"lookdev":"loookdev",
		}
		try:
			with open(os.path.join(os.getcwd(), "PipoReplaceRefsData.json"), "w") as save_file:
				json.dump(self.switch_settings, save_file, indent=4)
		except:
			mc.warning("Impossible to create settings!")
			return
		else:
			print("Settings created successfully!")
			return


	def load_setting_file_function(self):
		#get the path of the program
		print("PATH OF THE PROGRAM")
		print(self.program_path)

		os.chdir(self.program_path)

		try:
			with open(os.path.join(os.getcwd(), "PipoReplaceRefsData.json"), "r") as read_file:
				content = json.load(read_file)
		except:
			mc.warning("Impossible to load settings!")
			self.create_default_settings()
			return
		else:
			





	def main_interface(self):

		self.main_window = mc.window(sizeable=False, width=self.width, height=self.height)


		self.main_column = mc.columnLayout(adjustableColumn=True, parent=self.main_window)
		mc.text(label="PipoReplaceRefs - By Quazar", parent=self.main_column, align="center")

		mc.button(label="Switch Refs", parent=self.main_column, command=self.switch_refs_function)

		self.main_rowcolumn = mc.rowColumnLayout(parent=self.main_column, numberOfColumns=2, columnWidth=((1, self.width/2), (2, self.width/2)))
		self.leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.main_rowcolumn)
		self.rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.main_rowcolumn)

		self.left_textscrolllist = mc.textScrollList(numberOfRows=8, parent=self.leftcolumn)
		self.right_textscrolllist = mc.textScrollList(numberOfRows=8, parent=self.rightcolumn)



		self.load_setting_file_function()



		mc.showWindow()




	def get_children_function(self, item):
		children = mc.listRelatives(item, children=True, shapes=False, fullPath=True)
		#print(children)
		if children != None:
			for child in children:
				if child not in self.first_ref_children:
					self.first_ref_children.append(child)
				self.get_children_function(child)	

		





	def switch_refs_function(self, event):
		selection = mc.ls(sl=True)

		if (selection == None) or (len(selection) == 0):
			mc.error("No item selected!")
			return


		first_ref = selection[0]
		selection.pop(0)

		#check that the first element is in reference
		if mc.referenceQuery(first_ref, inr=True)==False:
			mc.error("Your main item must be a reference!")
			return

		self.first_ref_children = []
		self.get_children_function(first_ref)

		


		for element in selection:
			#print(element)
			#check that it's a reference
			if mc.referenceQuery(element, inr=True) == True:
				#get the path of the reference
				ref_path = mc.referenceQuery(element, filename=True, un=True, wcn=True)
				ref_name = mc.referenceQuery(element, filename=True, shn=True, wcn=True)
				replace_path = ref_path.replace("lookdev", "lookdevNaked")
			
				if os.path.isfile(replace_path)==False:
					mc.warning("New ref doesn't exist in the pipeline!")
					print(replace_path)
				else:
					#replace the old reference by the new one
					#go through each mesh of the first item (get children if transform)
					
					reference_node = mc.file(ref_path, query=True, referenceNode=True)
					#replace
					mc.file(replace_path, loadReference=reference_node)

			else:
				mc.warning("Item skipped because not in reference")
				print(element)





if __name__ == "__main__":
	Application()