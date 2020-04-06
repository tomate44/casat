import os
from freecad.casat.version import __version__

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

ICONPATH = os.path.join(os.path.dirname(__file__), "gui", "resources")

print("casat ({0}) python module has been successfully imported".format(str(__version__)))
