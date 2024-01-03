# Title:OTHOTIC DESIGN
# Part:1
# Description:IMPORT
# Version 0.0
# Author: Hana Keller

#===================================

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import FreeCAD, FreeCADGui
import json
import os
import Mesh
import Part

class FOImport:

    def GetResources(self):
        return { 
                 "MenuText" : "Import",
                 "ToolTip"  : "Import foot FreeCAD File"}
    
    def Activated(self):
        Main()
        return
        
class BuildDropdown: 
    def __init__(self, root, dropdown_label, dropdown_row, dropdown_list, dropdown_units):
        self.inputValue = 0
    
        dropdown_label_text = Label(root, text = dropdown_label, bg="#6FAFE7").grid(row = dropdown_row, column = 0, padx = 0, pady = 0, sticky=W)
        
        options = [f"{option} {dropdown_units}" for option in dropdown_list]
        self.clicked = StringVar()
        self.dropdown = OptionMenu(root, self.clicked, *options)
        self.dropdown.grid(row = dropdown_row, column = 1, padx=0, pady=0, sticky=W)
  
        self.dropdown.grid()
        
    def get_value(self):
        value_str = self.clicked.get()
        return value_str.split(' ')[0]

class FileButton:
    def __init__(self, root, button_label, button_text, button_row):
        self.filepath = ""
        
        foot_file_frame = Frame(root, bg="#6FAFE7")
        foot_file_frame.grid(row = button_row, column = 1, padx = 0, pady = 0, sticky=W)
        Label(root, text = button_label, bg="#6FAFE7").grid(row = button_row, column = 0, padx = 0, pady = 0, sticky=W)
        foot_file = Button(root, text = button_text, command= lambda: self.open_file()).grid(row = button_row, column = 1, padx = 0, pady = 0, sticky=W)
    
    def open_file(self):
        file = filedialog.askopenfile(mode='r', filetypes=[('STL', '*.stl')])
        self.filepath = file.name
        
    def get_value(self):
        return self.filepath
        
def Main(): 
    root = Tk()
    root.title("FO Import")
    root.geometry("600x400")  # set starting size of window
    root.maxsize(2000, 2000)  # width x height
    root.config(bg="#6FAFE7")
    
    # Get Foot STL file
    foot_file = FileButton(root, "Location of file of foot STL: ", "Browse", 0)
   
   # Dropdowns for inputs
    FO_thickness = BuildDropdown(root, "Thickness of FO: ", 1, [0.5, 1, 3, 5], 'mm')
    posting = BuildDropdown(root, "Posting (+ve = medial; -ve = lateral): ", 2, [-10, 10, 0.5, 1], 'degrees')
    heel_raise = BuildDropdown(root, "Heel raise:  ", 3, [-10, 10, 0.5, 1], 'degrees')
    shoe_sex = BuildDropdown(root, "Sex: ", 4, ["Female", "Male"], '')
    shoe_size = BuildDropdown(root, "Shoe size: ", 5, [1,2,3,4,5,6], 'size')
   
    # Button to start the build
    run_program = Button(root, text = "START", command=lambda: start_button(root, {"foot_file" : foot_file.get_value(), 
                    "FO_thickness": FO_thickness.get_value(),
                    "posting" : posting.get_value(), 
                    "heel_raise" : heel_raise.get_value(),
                    "shoe_sex" : shoe_sex.get_value(), 
                    "shoe_size" : shoe_size.get_value()})).grid(row = 6, column = 0, padx = 0, pady = 0, sticky = W+E+N+S)
                    
    root.mainloop()
    print("Move on to next Step: Position")
    return

def start_button(root, option_dict):
    filepath = os.path.expanduser("~/Documents/importVariables.json")
    with open(filepath, "w+") as write_file:
        json.dump(option_dict, write_file)
    root.destroy()
    doc = FreeCAD.newDocument()
    foot = Mesh.Mesh(option_dict['foot_file'])
    #foot.Label("Foot Mesh")
    Mesh.show(foot)
    
    doc.recompute()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCADGui.runCommand('Std_DrawStyle',2)   



FreeCADGui.addCommand("Import", FOImport())