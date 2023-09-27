# Title: ORTHOTIC DESIGN  
# Part: 1 
# Description: IMPORT
# Version: 0.2
# Last edited: 2020_03_10
# Author: Scott Telfer


# =============================================================================

## TO DO
# Add OK button to GUI
#


# =============================================================================

## Import Modules
import rhinoscriptsyntax as rs
import math
import Meier_UI_Utility
import Rhino


# =============================================================================

## Open new instance
#rs.DocumentModified(False)
#rs.Command("_-New _None")


# =============================================================================

## Turn off viewport to speed up processing
rs.EnableRedraw(False)


# =============================================================================

## SET UP LAYERS
# Add new layers
rs.AddLayer("Original scan")
rs.AddLayer("Reference plane", visible = False)
rs.AddLayer("Side", visible = False)
rs.AddLayer("FO_length", visible = False)
rs.AddLayer("FO_thickness", visible = False)
rs.AddLayer("Posting", visible = False)
rs.AddLayer("Heel_raise", visible = False)
rs.AddLayer("Shoe_sex", visible = False)
rs.AddLayer("Shoe_size", visible = False)
rs.AddLayer("Position scan", visible = False)
rs.AddLayer("Heel Medial", color = (0, 255, 225), visible = False)
rs.AddLayer("Heel Center", color = (0, 255, 225), visible = False)
rs.AddLayer("Heel Lateral", color = (0, 255, 225), visible = False)
rs.AddLayer("Arch Medial", color = (0, 255, 225), visible = False)
rs.AddLayer("Arch Lateral", color = (0, 255, 225), visible = False)
rs.AddLayer("MTPJ1", color = (0, 255, 225), visible = False)
rs.AddLayer("MTPJ5", color = (0, 255, 225), visible = False)
rs.AddLayer("FO Build", visible = False)
rs.CurrentLayer("Original scan")


# =============================================================================

## Import Scan
# Choose file
fnm = rs.OpenFileName("Choose scanned file", ".stl|", None, None, None)

# Import stl
#Load stl
commandString = ("-_import " + fnm + " _Enter")
scan = rs.Command(commandString)


# =============================================================================

## Copy to next layer
scan2 = rs.ObjectsByLayer("Original scan")
scan3 = rs.CopyObject(scan2)
#scan3 = rs.GetObject()
rs.ObjectLayer(scan3, layer = "Position scan")
rs.CurrentLayer("Position scan")
rs.LayerVisible("Original scan", False)


# =============================================================================

## Set display
persp_max = rs.IsViewMaximized("Perspective")
if persp_max:
    rs.ZoomExtents()
    print "Perspective view maximised"
else:
    rs.MaximizeRestoreView(view = "Perspective")
    rs.ZoomExtents()


# =============================================================================

## Turn display back on
rs.EnableRedraw(True)


# =============================================================================

def Main():
    # Make the UI object
    ui = CircleUI()
    # Show the dialog from the UI class
    Rhino.UI.Dialogs.ShowSemiModal(ui.form)
    # User has exited the dialog - store values as points
    rs.CurrentLayer("FO_length")
    if ui.FO_length == "3/4":
        rs.AddPoint(0, 0, 5)
    else:
        rs.AddPoint(0, 0, -5)
    rs.CurrentLayer("FO_thickness")
    rs.AddPoint(0, 0, ui.FO_thickness)
    rs.CurrentLayer("Posting")
    rs.AddPoint(0, 0, ui.posting)
    rs.CurrentLayer("Heel_raise")
    rs.AddPoint(0, 0, ui.heel_raise)
    rs.CurrentLayer("Shoe_sex")
    if ui.FO_length == "Female":
        rs.AddPoint(0, 0, 5)
    else:
        rs.AddPoint(0, 0, -5)
    rs.CurrentLayer("Shoe_size")
    rs.AddPoint(0, 0, ui.shoe_size)


#Creates the UI form, adds controls, and lays them out on the form
class CircleUI():
    def __init__(self):
        # Holds the FO length value the UI updates. The default will be 0
        self.FO_length = "3/4"
        # Holds the FO thickness value the UI updates. The default will be 0
        self.FO_thickness = 4
        # Holds the posting value the UI updates. The default will be 0
        self.posting = 0
        # Holds the heel raise value the UI updates. The default will be 0
        self.heel_raise = 0
        # Holds the shoe size sex the UI updates. The default will be Female
        self.shoe_sex = "Female"
        # Holds the shoe size value the UI updates. The default will be 0
        self.shoe_size = 8
        # Make a new form (dialog)
        self.form = Meier_UI_Utility.UIForm("Orthotic design parameters") 
        # Accumulate controls for the form using "addXYZ.." methods
        self.form.panel.addLabel("", "By Scott Telfer, Version 0.1", None, True)
        self.form.panel.addLabel("", "Contact scott.telfer@gmail.com for support", None, True)
        self.form.panel.addLabel("", "", None, None)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "Define your orthosis design using the choices below", (0, 0, 255), True)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "Orthosis length:", None, True)
        self.form.panel.addComboBox("FO length:", ["3/4", "Full"], 0, True, \
            self.FO_length_SelectedIndexChanged)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "Posting (+ve = medial; -ve = lateral):", None, True)
        self.form.panel.addNumericUpDown("", -10, 10, 0.5, 1, self.posting, 80, \
            True, self.Posting_OnValueChange)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "FO thickness:", None, True)
        self.form.panel.addNumericUpDown("", 3, 5, 0.5, 1, self.FO_thickness, 80, \
            True, self.FO_thickness_OnValueChange)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "Heel raise:", None, True)
        self.form.panel.addNumericUpDown("", 0, 5, 0.5, 1, self.heel_raise, 80, \
            True, self.heel_raise_OnValueChange)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "Subject sex:", None, True)
        self.form.panel.addComboBox("Sex:", ["Female", "Male"], 0, True, \
            self.shoe_sex_SelectedIndexChanged)
        self.form.panel.addSeparator("", 215, True)
        self.form.panel.addLabel("", "Shoe size:", None, True)
        self.form.panel.addNumericUpDown("", 3, 15, 0.5, 1, self.shoe_size, 80, \
            True, self.shoe_size_OnValueChange)
        # Layout the controls on the form
        self.form.layoutControls() 
    
    # Delgates. Store the changed values
    def FO_thickness_OnValueChange(self, sender, e):
        self.FO_thickness = sender.Value
    def Posting_OnValueChange(self, sender, e):
        self.posting = sender.Value
    def FO_length_SelectedIndexChanged(self, sender, e):
        index = sender.SelectedIndex # 0 based index of choice
        self.FO_length = sender.SelectedItem # Text of choice
    def heel_raise_OnValueChange(self, sender, e):
        self.heel_raise = sender.Value
    def shoe_sex_SelectedIndexChanged(self, sender, e):
        index = sender.SelectedIndex # 0 based index of choice
        self.shoe_sex = sender.SelectedItem # Text of choice
    def shoe_size_OnValueChange(self, sender, e):
        self.shoe_size = sender.Value

# Execute it...
if( __name__ == "__main__" ):
    Main()


# =============================================================================

# Layer housekeeping
rs.CurrentLayer("Position scan")
rs.LayerVisible("FO_length", False)
rs.LayerVisible("FO_thickness", False)
rs.LayerVisible("Posting", False)
rs.LayerVisible("Heel_raise", False)
rs.LayerVisible("Shoe_sex", False)
rs.LayerVisible("Shoe_size", False)


# =============================================================================

## Request user to trim object to size
rs.MessageBox("Trim scan to size")


###############################################################################
# =============================================================================
# END OF SCRIPT
# =============================================================================
###############################################################################