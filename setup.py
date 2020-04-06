from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                            "freecad", "casat", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.casat',
      version=str(__version__),
      packages=['freecad',
                'freecad.casat'],
      maintainer="Chris_G",
      maintainer_email="cg@grellier.fr",
      url="https://github.com/tomate44/casat",
      description="Curve And Surface Additional Tools, a Freecad workbench",
      install_requires=['numpy'], # should be satisfied by FreeCAD's system dependencies already
      include_package_data=True)
