import FreeCAD,FreeCADGui,Part
import json
import Mesh
import os
import PySide.QtCore as QtCore
import pathlib 

class ImportTaskPanel:
   def __init__(self):
       # this will create a Qt widget from our ui file
       cwd = str(pathlib.Path(__file__).parent.resolve())
       filepathform = cwd + "\TaskImport.ui"
       self.form = FreeCADGui.PySideUic.loadUi(filepathform)
       self.fileSpec = None
       QtCore.QObject.connect(self.form.browse, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.fileSelect)
       self.doc = FreeCAD.activeDocument()
       if self.doc == None:
            self.doc = FreeCAD.newDocument()
 
   def fileSelect(self, fn):
       """Assign the selected file."""
       self.fileSpec = fn
       
   def accept(self):
       if self.doc.getObjectsByLabel("Mesh") == [] and self.doc.getObjectsByLabel("Mesh001") == []:
           if self.fileSpec == None:
               print("Please select a mesh file")
               return
           else:
               foot = Mesh.Mesh(self.fileSpec)
               FreeCADGui.runCommand('Std_DrawStyle', 2)
               Mesh.show(foot)
       else:
           pass
       
       options_dict = {"FO_thickness": self.form.thicknessOut.value(),
                    "posting" : self.form.postingOut.value(), 
                    "heel_raise" : self.form.heelraiseOut.value(),
                    "shoe_sex" : self.form.sexOut.currentText(), 
                    "shoe_size" : self.form.sizeOut.currentText()} 
       minSize = 3
       options_dict["shoe_size"] = int((float(options_dict["shoe_size"])-minSize) *2) 
       
       if options_dict["shoe_sex"] == "Female":
            options_dict["shoe_sex"] = 1
       else:
            options_dict["shoe_sex"] = -1 
       
       for label, value in options_dict.items():
            if self.doc.getObjectsByLabel(label) != []:
                point = self.doc.getObjectsByLabel(label)[0]
                point.X = value
                point.Y = 0
                point.Z = 0
                point.ViewObject.hide()
            else:
                point = self.doc.addObject("Part::Vertex", label)
                point.X = value
                point.Y = 0
                point.Z = 0
                point.Label = label
                point.ViewObject.hide()
            
           
       self.doc.recompute()
       FreeCADGui.SendMsgToActiveView("ViewFit")   
       FreeCADGui.Control.closeDialog()
       print("Move on to Position")



