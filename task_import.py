import FreeCAD,FreeCADGui,Part
import json
import Mesh
import os
import PySide.QtCore as QtCore

class ImportTaskPanel:
   def __init__(self):
       # this will create a Qt widget from our ui file
       self.form = FreeCADGui.PySideUic.loadUi(r"C:\Users\hanam\AppData\Roaming\FreeCAD\Mod\Hana_workbenchFO\TaskImport.ui")
       self.fileSpec = None
       QtCore.QObject.connect(self.form.browse, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.fileSelect)
       #QtCore.QObject.connect(self.form.thicknessOut, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.thickness)
       #QtCore.QObject.connect(self.form.postingOut, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.posting)
       #QtCore.QObject.connect(self.form.heelraiseOut, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.heelraise)
       #QtCore.QObject.connect(self.form.sexOut, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.shoesex)
       #QtCore.QObject.connect(self.form.sizeOut, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.shoesize)
 
   def fileSelect(self, fn):
       """Assign the selected file."""
       self.fileSpec = fn
   def thickness(self, fn):
       """Assign the selected file."""
       self.thick = fn
   def posting(self, fn):
       """Assign the selected file."""
       self.post = fn
   def heelraise(self, fn):
       """Assign the selected file."""
       self.heel = fn
   def shoesex(self, fn):
       """Assign the selected file."""
       self.sex = fn
   def shoesize(self, fn):
       """Assign the selected file."""
       self.size = fn
       
   def accept(self):
       options_dict = {"foot_file" : self.fileSpec, 
                    "FO_thickness": 2,#self.thick,
                    "posting" : 2,#self.form.postingOut.value(), 
                    "heel_raise" : 3,#self.form.heelraiseOut.value(),
                    "shoe_sex" : 2,#self.form.sizeOut.value(), 
                    "shoe_size" : 2}#self.form.sexOut.value()}
       start_button(options_dict)
       FreeCADGui.Control.closeDialog()
       print("Move on to Position")

def start_button(option_dict):
    filepath = os.path.expanduser("~/Documents/importVariables.json")
    with open(filepath, "w+") as write_file:
        json.dump(option_dict, write_file)
    doc = FreeCAD.newDocument()
    foot = Mesh.Mesh(option_dict['foot_file'])
    Mesh.show(foot)
    
    doc.recompute()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCADGui.runCommand('Std_DrawStyle',2)   


#panel = ImportTaskPanel()
#FreeCADGui.Control.showDialog(panel)