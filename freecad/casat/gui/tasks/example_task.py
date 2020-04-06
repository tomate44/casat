# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
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
Example task template
"""

import FreeCAD as App
import FreeCADGui as Gui

import Draft

from .. import resources
from .base_task import BaseTask

class ExampleTask(BaseTask):
    """
    Example task template
    """

    def __init__(self):
        """
        Constructor
        """

        #initialize the inherited base class
        super().__init__(resources.__path__[0] + '/example_task_panel.ui')

        #Initialize state that will be global to the task here
        self.view = Gui.ActiveDocument.ActiveView

        #list of tuples, associating the control name with the
        #signal and task callback
        self.widgets = [
            ('draw_circle_button', 'clicked', self.draw_circle_callback),
            ('draw_rectangle_button', 'clicked', self.draw_rectangle_callback),
            ('delete_object_button', 'clicked', self.delete_object_callback)
        ]

    def setup(self):
        """
        Override of base class method.  Optional
        """

        print('setting up task...')
        super().setup()

    def draw_circle_callback(self):
        """
        Callback to draw a circle
        """

        print('draw circle callback')

        Draft.makeCircle(10.0)
        App.activeDocument().recompute()
        Gui.SendMsgToActiveView('ViewFit')

    def draw_rectangle_callback(self):
        """
        Callback to draw a rectangle
        """

        print('draw rectangle callback')

        Draft.makeRectangle(20.0, 5.0)
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView('ViewFit')

    def delete_object_callback(self):
        """
        Callback to delete the selected object
        """

        _sel = Gui.Selection.getSelection()

        if not _sel:
            return

        _name = _sel[0].Name

        print('delete selected object', _name)

        App.ActiveDocument.removeObject(_name)
        App.ActiveDocument.recompute()

    def accept(self):
        """
        Overrides base implementation (optional)
        """

        print("task results accepted")
        super().accept()

    def reject(self):
        """
        Overrides base implementation (optional)
        """

        print('task results rejected')
        super().reject()
