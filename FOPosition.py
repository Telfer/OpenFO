# Title:OTHOTIC DESIGN
# Part:1
# Description: Postion
# Version 0.0
# Author: Hana Keller

#===================================

import FreeCAD, FreeCADGui
import json
import Part, PartGui
import os

class FOPosition:

    def GetResources(self):
        return {
                 "MenuText" : "Position",
                 "ToolTip"  : "Position the foot correctly"}
                 
    def Activated(self):
        self.buildShoeShape()
        Main()
        if (self.doc.getObjectsByLabel("Foot Mid") != []):
            #
            print("Move on the next Step: Landmark")
        
    def buildShoeShape(self):

        self.doc = FreeCAD.activeDocument()
        
        size = 1
        ## outline data points (M9, M9.5, W8.5, M12)
        heel_center_pt_y = [-126, -132, -126, -134, -115, -122, -136, -142]
        heel_lateral_pt_x = [-24, -30, -22.5, -28.9, -22, -27, -25, -31]
        heel_lateral_pt_y = [-100, -100, -100, -102, -95, -100, -103, -103]
        heel_medial_pt_x = [29, 36, 24.9, 33.1, 26.0, 33, 31, 34]
        heel_medial_pt_y = [-100, -100, -100, -100, -100, -100, -100, -100]
        heel_center_medial_x = [18, 20, 16.8, 20.5, 17, 24, 17, 28]
        heel_center_medial_y = [-121, -128, -120, -127, -110, -115, -130, -125]
        heel_center_lateral_x = [-15, -17.5, -13.9, -17.8, -19, -22, -14, -15]
        heel_center_lateral_y = [-121, -124.5, -119, -125.4, -105, -110, -131, -138]
        arch_medial_pt_x = [25, 36, 17.2, 37.4, 21, 38, 13, 38]
        arch_medial_pt_y = [-10, -12.7, -10, -13.3, -10, -10, -16, -16]
        mtpj1_prox_x = [32, 41, 25.6, 43.4, 25, 44, 29, 47]
        mtpj1_prox_y = [25, 25, 25, 23.4, 25, 25, 30, 30]
        mtpj1_pt_x = [37, 44, 35, 46.6, 30, 46, 41, 50]
        mtpj1_pt_y = [40, 40, 40, 38.1, 40, 40, 50, 50]
        mtpj1_dist1_x = [39, 45.5, 38.6, 47.3, 33, 47, 43.5, 51]
        mtpj1_dist1_y = [46, 46, 46.4, 42, 46, 46, 56, 56]
        mtpj1_dist2_x = [40, 46, 40.6, 48.4, 36, 47, 45, 51]
        mtpj1_dist2_y = [50, 50, 50, 50, 50, 50, 60, 60]
        toe_med_x = [32, 35, 31, 34.2, 30, 35, 35, 40]
        toe_med_y = [135, 136.7, 134.2, 135.9, 124, 124, 140, 145]
        toe_pt_x = [12, 13, 11.4, 12.2, 12, 11, 7, 10]
        toe_pt_y = [145, 146, 143.9, 147.8, 134, 140, 154, 160]
        toe_lat_x = [-13, -15.4, -12.3, -15.4, -11, -19, -9, -18]
        toe_lat_y = [136, 137.7, 135.3, 137.7, 124, 124, 150, 150]
        mtpj5_pt_x = [-38, -41, -36.9, -45, -35, -41, -39, -46]
        mtpj5_pt_y = [17, 17, 17, 17, 17, 17, 20, 20]
        mtpj5_prox_x = [-37, -40, -34.5, -43.4, -34, -41, -37, -45]
        mtpj5_prox_y = [9, 9, 9, 6.4, 9, 9, 10, 10]
        mtpj5_dist1_x = [-38.5, -42, -37.5, -46, -36, -42, -39, -46]
        mtpj5_dist1_y = [22, 22, 22, 22, 22, 22, 22, 22]
        mtpj5_dist2_x = [-39, -42.5, -38.6, -47, -37, -42, -39, -47]
        mtpj5_dist2_y = [27, 27, 27, 26, 27, 27, 30, 30]
        arch_lateral_pt_x = [-31, -34, -27.7, -36.4, -26, -35, -28, -38]
        arch_lateral_pt_y = [-40, -40, -40, -41, -40, -40, -40, -40]
        ff_med_x = [46, 51, 44.5, 49.4, 40, 45, 47, 51]
        ff_med_y = [80, 80, 80, 80, 80, 80, 80, 80]
        ff_lat_x = [-40, -44.5, -40, -47.6, -37, -43, -38, -46]
        ff_lat_y = [60, 60, 60, 60, 60, 60, 80, 80]

        # make shoe outline numbers into coordinates
        heel_center = [0, heel_center_pt_y[size], 0]
        heel_lateral = [heel_lateral_pt_x[size], heel_lateral_pt_y[size], 0]
        heel_medial = [heel_medial_pt_x[size], heel_medial_pt_y[size], 0]
        heel_center_medial = [heel_center_medial_x[size], heel_center_medial_y[size], 0]
        heel_center_lateral = [heel_center_lateral_x[size], heel_center_lateral_y[size], 0]
        arch_medial = [arch_medial_pt_x[size], arch_medial_pt_y[size], 0]
        arch_lateral = [arch_lateral_pt_x[size], arch_lateral_pt_y[size], 0]
        mtpj1_prox = [mtpj1_prox_x[size], mtpj1_prox_y[size], 0]
        mtpj1 = [mtpj1_pt_x[size], mtpj1_pt_y[size], 0]
        mtpj1_dist1 = [mtpj1_dist1_x[size], mtpj1_dist1_y[size], 0]
        mtpj1_dist2 = [mtpj1_dist2_x[size], mtpj1_dist2_y[size], 0]
        ff_med = [ff_med_x[size], ff_med_y[size], 0]
        toe_med = [toe_med_x[size], toe_med_y[size], 0]
        toe = [toe_pt_x[size], toe_pt_y[size], 0]
        toe_lat = [toe_lat_x[size], toe_lat_y[size], 0]
        ff_lat = [ff_lat_x[size], ff_lat_y[size], 0]
        mtpj5 = [mtpj5_pt_x[size], mtpj5_pt_y[size], 0]
        mtpj5_dist1 = [mtpj5_dist1_x[size], mtpj5_dist1_y[size], 0]
        mtpj5_dist2 = [mtpj5_dist2_x[size], mtpj5_dist2_y[size], 0]
        mtpj5_prox = [mtpj5_prox_x[size], mtpj5_prox_y[size], 0]
        
        points_outline = [heel_center, heel_center_medial,
                                     heel_medial, arch_medial, mtpj1_prox, mtpj1,
                                     mtpj1_dist1, mtpj1_dist2, ff_med, toe_med, toe,
                                     toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1,
                                     mtpj5, mtpj5_prox, arch_lateral, heel_lateral,
                                     heel_center_lateral, heel_center]
        self.bs_Outline = Part.BSplineCurve()
        self.bs_Outline.buildFromPoles(points_outline, True)
        
        shoeEdge = self.doc.addObject("Part::Feature", "Shoe Edge")
        shoeEdge.Shape = self.bs_Outline.toShape()
        
        self.mesh_foot = self.doc.getObjectsByLabel("Mesh")[0]
        


class ViewObserver:
    def __init__(self, view):
        self.view = view
        self.positions = {"lowest point of heel on the plantar surface": None,
                          "MTH1 on the plantar surface" : None,
                          "MTH5 on the plantar surface" : None,
                          "point on arch" : None}
        self.active_position = "lowest point of heel on the plantar surface"
        self.doc = FreeCAD.activeDocument()
        
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
                    point = self.doc.getObject(self.active_position)
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
                
                # Determine forefoot centre point
                MTH1_pt_x = self.positions["MTH1 on the plantar surface"]["x"]
                MTH5_pt_x = self.positions["MTH5 on the plantar surface"]["x"]
                
                MTH1_pt_y = self.positions["MTH1 on the plantar surface"]["y"]
                MTH5_pt_y = self.positions["MTH5 on the plantar surface"]["y"]
                
                MTH1_pt_z = self.positions["MTH1 on the plantar surface"]["z"]
                MTH5_pt_z = self.positions["MTH5 on the plantar surface"]["z"]
                
                ff_mid = [(MTH1_pt_x + MTH5_pt_x) / 2, (MTH1_pt_y + MTH5_pt_y) / 2, (MTH1_pt_z + MTH5_pt_z) / 2]

                # Determine foot centre point
                heel_pt_x = self.positions["lowest point of heel on the plantar surface"]["x"]
                heel_pt_y = self.positions["lowest point of heel on the plantar surface"]["y"]
                heel_pt_z = self.positions["lowest point of heel on the plantar surface"]["z"]
                
                foot_mid = [(ff_mid[0] + heel_pt_x) / 2,(ff_mid[1] + heel_pt_y) / 2, (ff_mid[2] + heel_pt_z) / 2]
                point_foot_mid = self.doc.addObject("Part::Vertex", "Foot Mid")
                point_foot_mid.Label = "Foot Mid"
                point_foot_mid.X = foot_mid[0]
                point_foot_mid.Y = foot_mid[1]
                point_foot_mid.Z = foot_mid[2]
                self.doc.recompute()
                
        

def Main():               
    print("Identify lowest point of heel on the plantar surface")
    currentView = FreeCADGui.activeView()
    observer = ViewObserver(currentView)
    clickCallback = currentView.addEventCallback("SoMouseButtonEvent",observer.logPosition)



FreeCADGui.addCommand("Position", FOPosition())