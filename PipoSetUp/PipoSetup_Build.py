#File that build the Pipo_Installer file into a .exe file
import sys
from cx_Freeze import setup, Executable


base = None
if sys.platform == "win32":
	base = "Win32GUI"

executables = [
	Executable("Pipo_Installer.py", base=base)
	]
includes = [
	"SetupData.yaml"
	]

setup(
	name = "PipoInstaller Build",
	version = 0.1,
	description = "",
	executables=executables,
	options = {
		"build_exe": {
			"include_files": includes
		}
	}
)



