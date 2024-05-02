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
       QtCore.QObject.connect(self.form.browse, QtCore.SIGNAL("fileNameSelected(const QString&)"), self.fileSelect)
 
   def fileSelect(self, fn):
       """Assign the selected file."""
       self.fileSpec = fn
   # def thickness(self, fn):
       # """Assign the selected file."""
       # self.thick = fn
   # def posting(self, fn):
       # """Assign the selected file."""
       # self.post = fn
   # def heelraise(self, fn):
       # """Assign the selected file."""
       # self.heel = fn
   # def shoesex(self, fn):
       # """Assign the selected file."""
       # self.sex = fn
   # def shoesize(self, fn):
       # """Assign the selected file."""
       # self.size = fn
       
   def accept(self):
       options_dict = {"foot_file" : self.fileSpec, 
                    "FO_thickness": self.form.thicknessOut.value(),
                    "posting" : self.form.postingOut.value(), 
                    "heel_raise" : self.form.heelraiseOut.value(),
                    "shoe_sex" : self.form.sexOut.currentText(), 
                    "shoe_size" : self.form.sizeOut.currentText(),
                    "side" : "Left"}
       self.start_button(options_dict)
       FreeCADGui.Control.closeDialog()
       print("Move on to Position")
    
    # def updateJson (self):
       # for keys in options_dict:
            # if options_dict[keys] == None
    
   def start_button(self, option_dict):
       filepath = os.path.expanduser("~/Documents/importVariables.json")
       with open(filepath, "w+") as write_file:
           #self.parameters = json.loads(write_file.read())
           #self.updateJson()
           json.dump(option_dict, write_file)
       doc = FreeCAD.newDocument()
       foot = Mesh.Mesh(option_dict['foot_file'])
       FreeCADGui.runCommand('Std_DrawStyle', 2)
       Mesh.show(foot)
        
       doc.recompute()
       FreeCADGui.SendMsgToActiveView("ViewFit")   


