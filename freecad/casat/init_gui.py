#/**********************************************************************
#*                                                                     *
#* Copyright (c) XXXX FreeCAD AUthor <freecad_author@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
GUI Initialization module
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  First Things First
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  --- Copyrights ---
#
#  Here at the top of the module, it's good practice to always add
#  the license text.  Add your name and email, if desired.
#  Date is optional and reflects the date of first publication *only*.
#
#  --- Globals ----
#
#  Per standard Python practice, imports are located at the top of the
#  file, with the exception of workbench commands - more later on that.
#
#  Also note the use of the TEMPLATEWB_VERSION constant.  This provides
#  a quick, easy way to version your workbench and makes it easy for
#  a user to know which version they're running.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.casat import ICONPATH
from freecad.casat.version import __version__


class casat_workbench(Gui.Workbench):
    """
    class which gets initiated at starup of the gui
    """

    #Constants for UI locations for toolboxes
    MENU = 1
    TOOLBAR = 2
    CONTEXT = 4

    #Workbench GUI-specific attributes
    MenuText = "casat " + str(__version__)
    ToolTip = "Curve And Surface Additional Tools, a Freecad workbench"
    Icon = os.path.join(ICONPATH, "template_resource.svg")
    toolbox = []

    def __init__(self):
        """
        Constructor
        """

        self.command_ui = {

            'MenuText': {
                'gui': self.MENU,
                'cmd': ['casat_FaceIsocurves', 'MyCommand1', 'MyCommand2', 'MyCommand3']
            },

            'Files': {
                'gui': self.TOOLBAR,
                'cmd': ['casat_FaceIsocurves', 'MyCommand2']
            },

            'Geometry': {
                'gui': self.TOOLBAR + self.CONTEXT,
                'cmd': ['casat_FaceIsocurves', 'MyCommand1', 'MyCommand3']
            },
        }

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        Import commands here
        """

        #import commands here to be added to the user interface
        from .gui.commands import my_command_1, my_command_2, my_command_3
        from .gui.commands import face_isocurves

        #iterate the command toolboxes defined in __init__() and add
        #them to the UI according to the assigned location flags
        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.TOOLBAR:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.MENU:
                self.appendMenu(_k, _v['cmd'])

        self.appendToolbar("Tools", self.toolbox)
        self.appendMenu("Tools", self.toolbox)

        #Add diagnostic code or other start-up related activities here
        App.Console.PrintMessage("\n\tSwitching to casat workbench ({0})".format(str(__version__)))

    def Activated(self):
        """
        Workbench activation occurs when switched to
        """
        pass

    def Deactivated(self):
        """
        Workbench deactivation occurs when switched away from in the UI
        """
        pass

    def ContextMenu(self, recipient):
        """
        Right-click menu options
        """

        #Populate the context menu when it's called
        for _k, _v in self.command_ui.items():
            if _v['gui'] & self.CONTEXT:
                self.appendContextMenu(_k, _v['cmd'])

Gui.addWorkbench(casat_workbench())
