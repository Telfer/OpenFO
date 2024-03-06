# Title:OTHOTIC DESIGN
# Part:1
# Description: LANDMARKS
# Version 0.0
# Author: Hana Keller

#===================================

# Import Modules
import FreeCAD 
import FreeCADGui
import Part, PartGui
import math
import json
import os

class FOLandmark:
    def GetResources(self):
        return { 
                 "MenuText" : "Landmarks",
                 "ToolTip"  : "Located Landmarks on Foot"}
    
    def Activated(self):
        Main()
        return
    
       
        

#This class logs any mouse button events. As the registered callback function fires twice for 'down' and
#'up' events we need a boolean flag to handle this.
class ViewObserver:
    def __init__(self, view):
        self.view = view
        self.positions = {"point on lateral side of heel": None,
                          "point on posterior of heel" : None,
                          "point on medial side of heel" : None,
                          "highest point on lateral arch" : None,
                          "highest point on medial arch" : None, 
                          "the medial side of the distal MTH1" : None,
                          "the lateral side of the distal MTH5" : None}
        self.active_position = "point on lateral side of heel"
        self.doc = FreeCAD.activeDocument()
                        
       
   
    def logPosition(self, info):
        down = (info["State"] == "DOWN")
        pos = info["Position"]
        if (down):
            pnt = self.view.getPoint(pos)
            info = self.view.getObjectInfo(pos)
            #FreeCAD.Console.PrintMessage("Object info: " + str(info) + "\n")
            self.positions[self.active_position] = info
            if info == None:
                pass
            elif list(self.positions.keys()).index(self.active_position) + 1 in range(len(list(self.positions.keys()))):
                if self.doc.getObjectsByLabel(self.active_position) != []:
                    point = self.doc.getObjectsByLabel(self.active_position)[0]
                    point.X = self.positions[self.active_position]["x"]
                    point.Y = self.positions[self.active_position]["y"]
                    point.Z = self.positions[self.active_position]["z"]
                else:
                    point = self.doc.addObject("Part::Vertex", self.active_position)
                    point.X = self.positions[self.active_position]["x"]
                    point.Y = self.positions[self.active_position]["y"]
                    point.Z = self.positions[self.active_position]["z"]
                    point.Label = self.active_position
                
                self.active_position = list(self.positions.keys())[list(self.positions.keys()).index(self.active_position) + 1]
                FreeCAD.Console.PrintMessage(f"Identify {self.active_position} \n")
                self.doc.recompute()
            else:
                filepath = os.path.expanduser("~/Documents/landmarkVariables.json")
                with open(filepath, "w+") as write_file:
                    json.dump(self.positions, write_file)
                print("Move on the next Step: Build")
            
        

def Main():
    print("Identify point on lateral side of heel")
    currentView = FreeCADGui.activeView()
    observer = ViewObserver(currentView)
    clickCallback = currentView.addEventCallback("SoMouseButtonEvent",observer.logPosition)
    
      
     
FreeCADGui.addCommand("Landmark", FOLandmark())