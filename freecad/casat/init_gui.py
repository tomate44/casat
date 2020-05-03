#/**********************************************************************
#*                                                                     *
#* Copyright (c) Christophe Grellier <cg@grellier.fr>                  *
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
Casat stands for Curve And Surface Additional Tools.
It is a Freecad workbench mainly dedicated to the manipulation and creation
of curves and surfaces, and more specifically NURBS.
"""

import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.casat import *
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
    MenuText = "Casat" # + str(__version__)
    ToolTip = "Curve And Surface Additional Tools, a Freecad workbench"
    Icon = os.path.join(ICONPATH, "casat_wb.svg")

    def __init__(self):
        """Workbench Constructor"""
        self.toolbox = ['bspline_to_console']
        self.command_ui = {
            'Casat': {
                'gui': self.MENU + self.TOOLBAR + self.CONTEXT,
                'cmd': ['casat_flatten_face', 'casat_isocurves', 'to_console']
            },
            #'Casat': {
                #'gui': self.TOOLBAR,
                #'cmd': ['casat_flatten_face', 'casat_isocurves', 'to_console']
            #},
            #'Casat': {
                #'gui': self.CONTEXT,
                #'cmd': ['casat_flatten_face', 'casat_isocurves', 'to_console', ]
            #},
            'Devel': {
                'gui': self.TOOLBAR,
                'cmd': ['to_console', 'bspline_to_console']
            },
        }

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        Import commands here
        """
        message("Activation\n\n   ***   Welcome to CASAT workbench.   ***\nC.A.S.A.T -> Curve And Surface Additional Tools\n")
        #import commands here to be added to the user interface
        from .gui.commands import my_command_1, my_command_2, my_command_3
        from .gui.commands import face_isocurves
        from .gui.commands import face_flattening
        from .gui.commands import dev_tools

        #iterate the command toolboxes defined in __init__() and add
        #them to the UI according to the assigned location flags
        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.TOOLBAR:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.MENU:
                self.appendMenu(_k, _v['cmd'])

            if (_k == 'Devel') and FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Casat").GetBool('Devel', False):
                self.appendToolbar(_k, _v['cmd'])

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
        #if recipient == "View":
            #contextlist = ["adjacent_faces","bspline_to_console"] # list of commands
            #self.appendContextMenu("Curves",contextlist)
        #elif recipient == "Tree":
            #contextlist = [] # list of commands
            #self.appendContextMenu("Curves",contextlist)
        #Populate the context menu when it's called
        for _k, _v in self.command_ui.items():
            if _v['gui'] & self.CONTEXT:
                self.appendContextMenu(_k, _v['cmd'])

Gui.addWorkbench(casat_workbench())
