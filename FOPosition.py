# Title:OTHOTIC DESIGN
# Part:1
# Description: Postion
# Version 0.0
# Author: Hana Keller

#===================================

import FreeCAD, FreeCADGui
import json

class FOPosition:

    def GetResources(self):
        return {
                 "MenuText" : "Position",
                 "ToolTip"  : "Position the foot correctly"}
                 
    def Activated(self):
        FreeCAD.Console.PrintMessage("")
        
FreeCADGui.addCommand("Position", FOPosition())