import os
import requests
import zipfile
import colorama
import yaml
import platform
import subprocess

<<<<<<< HEAD
=======
from pyfiglet import Figlet
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e
from time import sleep
from termcolor import *

colorama.init()


<<<<<<< HEAD

=======
#pyfiglet font creation
main_font = Figlet(font="graffiti")
second_font = Figlet(font="digital")
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e

"""
Setup steps:
	Check that install data file exists
	install project from github at the right location / destination
	check if python is installed
		if python is installed try to install all python plugins
		try to locate mayapy
		install all dependencies
"""
<<<<<<< HEAD
print(__file__)
setup_file = os.path.join(os.getcwd(), "SetupData.yaml")
current_path = os.getcwd()



#display title
print(colored("Pipo Setup", "magenta"))
print(colored("Writen by Quazar", "white"))

print("Current path: %s"%os.getcwd())
print("Estimated setup file path: %s"%setup_file)
=======


#display title
print(colored(main_font.renderText("Pipo Setup"), "light_magenta"))
print(colored(second_font.renderText("Writen by Quazar"), "white"))
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e


def ciao():
	sleep(5)
	exit()




#check if the setup file exist
<<<<<<< HEAD

=======
current_path = os.getcwd()
setup_file = os.path.join(os.getcwd(), "SetupData.yaml")
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e


if os.path.isfile(setup_file)==False:
	print(colored("Impossible to install Pipo\nThe SetupData file doesn't exist!"))
	ciao()

<<<<<<< HEAD

try:
	with open(setup_file, "r") as read_file:
		setup_data = yaml.load(read_file, Loader=yaml.Loader)
=======
try:
	with open(os.path.join(os.getcwd(),"SetupData.yaml"), "r") as read_file:
		setup_data = yaml.load(read_file, Loader=yaml.Loader)

>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e
except:
	print(colored("Impossible to load data!", "red"))
	ciao()

repo_url = setup_data["GithubPath"]
output_folder = setup_data["Destination"]
plugins_list = setup_data["PluginList"]
maya_installation_path = setup_data["mayaDefaultPath"]

<<<<<<< HEAD
print(colored("Setup Informations", "red"))
print(colored("Github project : ", "yellow"), repo_url)
print(colored("Install folder : ", "yellow"), output_folder)


print(colored("\nGithub repository installation\n", "magenta"))

try:
	# Download the ZIP archive of the repository
	response = requests.get(f"{repo_url}/archive/master.zip")
except:
	print(colored("Impossible to reach github repository!", "red"))
	ciao()
=======
print(colored(second_font.renderText("Setup Informations"), "light_yellow"))
print(colored("Github project : ", "light_yellow"), repo_url)
print(colored("Install folder : ", "light_yellow"), output_folder)


print(colored("\nGithub repository installation\n", "light_magenta"))

# Download the ZIP archive of the repository
response = requests.get(f"{repo_url}/archive/master.zip")
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e

if response.status_code != 200:
    print(colored(f"Failed to download the repository. Status code: {response.status_code}", "red"))
    ciao()

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder, exist_ok=True)

# Save the ZIP archive to a temporary file
temp_zip_path = os.path.join(output_folder, "temp_project.zip")
with open(temp_zip_path, "wb") as temp_zip_file:
    temp_zip_file.write(response.content)

# Unzip the downloaded archive to the output folder
with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
    zip_ref.extractall(output_folder)

# Clean up the temporary ZIP file
os.remove(temp_zip_path)

<<<<<<< HEAD
print(colored("\nGithub repository installed succesfully\n", "green"))
=======
print(colored("\nGithub repository installed succesfully\n", "light_green"))
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e



#Check if python is installed on the computer
#Install it if python doesn't exist
installed=True
try:
	subprocess.run(["python", "--version"], capture_output=True, check=True)
	installed=True 
<<<<<<< HEAD
	print(colored("\nPython is installed on your computer!\n", "green"))
=======
	print(colored("\nPython is installed on your computer!\n", "light_green"))
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e
except subprocess.CalledProcessError:
	print(colored("\nPython isn't installed on your computer!\n", "red"))
	installed=False


if installed==True:
	for plugin in plugins_list:
		try:
			os.system("python -m pip install %s"%plugin)
		except:
			print(colored("Impossible to download the plugin [%s]"%plugin))
			continue

print("Possible mayapy path : %s"%maya_installation_path)
if os.path.isfile(os.path.join(maya_installation_path, "mayapy.exe"))==True:
	#try to install with mayapy all the python dependencies
	for plugin in plugins_list:
		try:
			os.system('"%s" -m pip install %s'%(os.path.join(maya_installation_path, "mayapy.exe"), plugin))
		except:
			print(colored("Impossible to download the plugin [%s]"%plugin))

else:
	print(colored("Impossible to install python plugins for maya!", "red"))



<<<<<<< HEAD
print(colored("Installation completed", "green"))
=======
print(colored(second_font.renderText("Installation completed!"), "light_green"))
>>>>>>> 5c4b91633b578ac62f5b4dc456b75385743bba7e
sleep(5)
exit()

