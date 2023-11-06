# Title:OTHOTIC DESIGN
# Part:1
# Description: LANDMARKS
# Version 0.0
# Author: Hana Keller

#===================================

# Import Modules
import FreeCAD as fc
import FreeCADGui
import math
import json

class FOLandmark:
    def GetResources(self):
        return { 
                 "MenuText" : "Landmarks",
                 "ToolTip"  : "Located Landmarks on Foot"}
    
    def Activated(self):
        print("Select first position")
        #while (FreeCADGui.Selection.isSelected(): 
        #    pass
        # print("True")
        #selec = FreeCADGui.Selection.getSelection()
        return
    
    
    #filepath = os.path.expanduser("~/Documents/potato.json")
    #with open(filepath, "w+") as write_file:
        #json.dump()
     
FreeCADGui.addCommand("Landmark", FOLandmark())