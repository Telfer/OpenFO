# Title:OTHOTIC DESIGN
# Part:1
# Description:IMPORT
# Version 0.0
# Author: Hana Keller

#===================================

import FreeCAD, FreeCADGui
from task_import import ImportTaskPanel

class FOImport:

    def GetResources(self):
        return { 
                 "MenuText" : "Import",
                 "ToolTip"  : "Import foot FreeCAD File"}
    
    def Activated(self):
        self.ui = FreeCADGui.FOToolBar
        self.view = FreeCADGui.activeView()
        if self.ui:
            self.ui.sourceCmd = self
            self.task = ImportTaskPanel()
            FreeCADGui.Control.showDialog(self.task)


FreeCADGui.addCommand("Import", FOImport())