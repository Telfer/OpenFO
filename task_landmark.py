import FreeCAD,FreeCADGui,Part
import json
import Mesh
import os
import PySide.QtCore as QtCore
import pathlib

class LandmarkTaskPanel:
   def __init__(self):
       # this will create a Qt widget from our ui file
       cwd = str(pathlib.Path(__file__).parent.resolve())
       filepathform = cwd + "\TaskPosition.ui"
       self.form = FreeCADGui.PySideUic.loadUi(filepathform)
       self.form = FreeCADGui.PySideUic.loadUi(r"C:\Users\hanam\AppData\Roaming\FreeCAD\Mod\Hana_workbenchFO\TaskLandmark.ui")
       self.form.setObjectName("LandmarkTaskPanel")
       self.form.setWindowTitle("Landmark")
       self.clickCallback = None
       self.view = FreeCADGui.activeView()
       self.doc = FreeCAD.activeDocument()
       
       self.positions = ["point on lateral side of heel",
                  "point on posterior of heel",
                  "point on medial side of heel",
                  "highest point n lateral arch",
                  "highest point on medial arch", 
                  "the medial side of the distal MTH1",
                  "the lateral side of the distal MTH5"]
       
       QtCore.QObject.connect(self.form.latHeel, QtCore.SIGNAL("clicked()"), self.lateralHeel)
       QtCore.QObject.connect(self.form.postHeel, QtCore.SIGNAL("clicked()"), self.posteriorHeel)
       QtCore.QObject.connect(self.form.medHeel, QtCore.SIGNAL("clicked()"), self.medialHeel)
       QtCore.QObject.connect(self.form.latArch, QtCore.SIGNAL("clicked()"), self.lateralArch)
       QtCore.QObject.connect(self.form.medArch, QtCore.SIGNAL("clicked()"), self.medialArch)
       QtCore.QObject.connect(self.form.medMTH1, QtCore.SIGNAL("clicked()"), self.medialMTH)
       QtCore.QObject.connect(self.form.latMTH5, QtCore.SIGNAL("clicked()"), self.lateralMTH)
   
   def lateralHeel(self):
       self.buttonClicked(0) 
   def posteriorHeel(self):
       self.buttonClicked(1) 
   def medialHeel(self):
       self.buttonClicked(2)        
   def lateralArch(self):
       self.buttonClicked(3) 
   def medialArch(self):
       self.buttonClicked(4) 
   def medialMTH(self):
       self.buttonClicked(5) 
   def lateralMTH(self):
       self.buttonClicked(6) 
       
   def buttonClicked(self, position):
       self.removeCall()
       self.currentPosition = position
       self.active_position = self.positions[self.currentPosition]
       FreeCAD.Console.PrintMessage(f"Identify {self.active_position} \n")
       self.clickCallback = self.view.addEventCallback("SoMouseButtonEvent",self.logPosition)
       
    
   def logPosition(self, info):
        down = (info["State"] == "DOWN")
        pos = info["Position"]
        if (down):
            pnt = self.view.getPoint(pos)
            info = self.view.getObjectInfo(pos)
            self.positionInfo = info
            if info == None:
                pass
            elif self.doc.getObjectsByLabel(self.active_position) != []:
                point = self.doc.getObjectsByLabel(self.active_position)[0]
                point.X = self.positionInfo["x"]
                point.Y = self.positionInfo["y"]
                point.Z = self.positionInfo["z"]
            else:
                point = self.doc.addObject("Part::Vertex", self.active_position)
                point.X = self.positionInfo["x"]
                point.Y = self.positionInfo["y"]
                point.Z = self.positionInfo["z"]
                point.Label = self.active_position
            # filepath = os.path.expanduser("~/Documents/landmarkVariables.json")
            # f = open(filepath, "r") 
            # self.params = json.loads(f.read())
            # print (self.params)
            # f.close()
            # self.params[self.active_position] = self.positionInfo
            # with open(filepath,"w") as write_file:
                # json.dump(self.params, write_file)
            
            self.doc.recompute()
            self.removeCall()
   
   def removeCall(self):
        if self.clickCallback:
            try:
                self.view.removeEventCallback("SoMouseButtonEvent", self.clickCallback)
                self.clickCallback = None
            except:
                pass
                
                
   def accept(self):
       print("Move on to Build")
       FreeCADGui.Control.closeDialog()
   
