import os
import FreeCAD
from freecad.casat.version import __version__

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

ICONPATH = os.path.join(os.path.dirname(__file__), "gui", "resources")
DEBUG = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Casat").GetBool('Debug', False)

def message(s):
    FreeCAD.Console.PrintMessage("Casat::" + str(s) + "\n")
def warning(s):
    FreeCAD.Console.PrintWarning("Casat::" + str(s) + "\n")
def error(s):
    FreeCAD.Console.PrintError(  "Casat::" + str(s) + "\n")
def debug(s):
    if DEBUG:
        message(s)

message("python module (v{0}) has been successfully imported".format(str(__version__)))
debug("debug mode activated")
