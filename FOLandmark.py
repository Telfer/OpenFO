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

from task_landmark import LandmarkTaskPanel

class FOLandmark:
    def GetResources(self):
        return { 
                 "MenuText" : "Landmarks",
                 "ToolTip"  : "Located Landmarks on Foot"}
    
    def Activated(self):
        self.ui = FreeCADGui.FOToolBar
        self.view = FreeCADGui.activeView()
        if self.ui:
            #Start Task Panel (not visible)
            self.ui.sourceCmd = self
            self.task = LandmarkTaskPanel()
            
        self.positions = {"point on lateral side of heel": None,
                          "point on posterior of heel" : None,
                          "point on medial side of heel" : None,
                          "highest point on lateral arch" : None,
                          "highest point on medial arch" : None, 
                          "the medial side of the distal MTH1" : None,
                          "the lateral side of the distal MTH5" : None}
        self.active_position = "point on lateral side of heel"
        self.doc = FreeCAD.activeDocument()
        if self.doc.getObjectsByLabel(self.active_position)!= []:
            #If Landmarks already set, skip to task panel
            FreeCADGui.Control.showDialog(self.task)
        else:
            #Set Landmarks
            print("Identify point on lateral side of heel")
            self.clickCallback = self.view.addEventCallback("SoMouseButtonEvent",self.logPosition)

    def finish(self):
        if self.clickCallback:
            try:
                #Remove click call back
                self.view.removeEventCallback("SoMouseButtonEvent", self.clickCallback)
                self.clickCallback = None
            except:
                pass
        else:
            pass
        FreeCADGui.Selection.clearSelection()
    
    def logPosition(self, info):
        down = (info["State"] == "DOWN")
        pos = info["Position"]
        if (down):
            pnt = self.view.getPoint(pos)
            info = self.view.getObjectInfo(pos)
            self.positions[self.active_position] = info
            if info == None:
                pass
            elif list(self.positions.keys()).index(self.active_position) + 1 in range(len(list(self.positions.keys()))):
                if self.doc.getObjectsByLabel(self.active_position) != []:
                    #If landmark already set, change current landmark
                    point = self.doc.getObjectsByLabel(self.active_position)[0]
                    point.X = self.positions[self.active_position]["x"]
                    point.Y = self.positions[self.active_position]["y"]
                    point.Z = self.positions[self.active_position]["z"]
                else:
                    #If landmark not set yet, create new point
                    point = self.doc.addObject("Part::Vertex", self.active_position)
                    point.X = self.positions[self.active_position]["x"]
                    point.Y = self.positions[self.active_position]["y"]
                    point.Z = self.positions[self.active_position]["z"]
                    point.Label = self.active_position
                point.ViewObject.PointSize = 5
                point.ViewObject.PointColor = (0.3, 0.1, 0.8)
                self.active_position = list(self.positions.keys())[list(self.positions.keys()).index(self.active_position) + 1] #iterate position
                FreeCAD.Console.PrintMessage(f"Identify {self.active_position} \n")
                self.doc.recompute()
            else:
                #on last landmark
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
                point.ViewObject.PointSize = 5
                point.ViewObject.PointColor = (0.3, 0.1, 0.8)
                self.doc.recompute()
                #dump landmarks to json file (may not be neccessary)
                filepath = os.path.expanduser("~/Documents/landmarkVariables.json")
                with open(filepath, "w+") as write_file:
                    json.dump(self.positions, write_file)
                self.finish()
                FreeCADGui.Control.showDialog(self.task)

     
FreeCADGui.addCommand("Landmark", FOLandmark())