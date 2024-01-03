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
import math
import numpy as np


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

class FOPosition:

    def GetResources(self):
        return {
                 "MenuText" : "Position",
                 "ToolTip"  : "Position the foot correctly"}
                 
    def Activated(self):
        self.doc = FreeCAD.activeDocument()
        self.Main()
 
        print("Move on the next Step: Landmark")
            
    def Main(self):     
        print("Identify lowest point of heel on the plantar surface")
        currentView = FreeCADGui.activeView()
        observer = ViewObserver(currentView)
        clickCallback = currentView.addEventCallback("SoMouseButtonEvent",observer.logPosition)

    
def readJson():
    filepath = os.path.expanduser("~/Documents/importVariables.json")
    f = open(filepath, "r") 
    parameters = json.loads(f.read())
    # self.FO_Thickness = self.parameters['FO_thickness']
    # self.posting = self.parameters['posting']
    # self.heel_raise = self.parameters['heel_raise']
    # self.sex = self.parameters['shoe_sex']
    # self.shoe_size = self.parameters['shoe_size'] 
    shoe_size = 1
    return shoe_size


def buildShoeShape(size):

    doc = FreeCAD.activeDocument()
    
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
                                 
                                 
    ##Confirm Left or Right foot:
    positions = ["lowest point of heel on the plantar surface",
                          "MTH1 on the plantar surface",
                          "MTH5 on the plantar surface",
                          "point on arch"]
                       
    heel_pt = doc.getObjectsByLabel(positions[0])[0]
    MTH1_pt = doc.getObjectsByLabel(positions[1])[0]
    MTH5_pt = doc.getObjectsByLabel(positions[2])[0]
    arch_pt = doc.getObjectsByLabel(positions[3])[0]
    
    vec1 = [heel_pt.X - MTH1_pt.X, heel_pt.Y - MTH1_pt.Y, heel_pt.Z - MTH1_pt.Z]
    vec2 = [MTH5_pt.X - MTH1_pt.X, MTH5_pt.Y - MTH1_pt.Y, MTH5_pt.Z - MTH1_pt.Z]
    
    planeVec = cross(vec1, vec2)
    k = - planeVec[0] * heel_pt.X - planeVec[1] * heel_pt.Y - planeVec[2] * heel_pt.Z
    print(f" x: {planeVec[0]} y: {planeVec[1]} z: {planeVec[2]} k: {k}")
    
    expectedZ = -(arch_pt.X * planeVec[0] + arch_pt.Y * planeVec[1] + k)/planeVec[2]
               
    if arch_pt.Z > expectedZ:
        print("Foot is Right")
        for i in range(len(points_outline)):
            points_outline[i]=[-points_outline[i][0], points_outline[i][1], points_outline[i][2]]
            #print(points_outline[i])
    else:
        print("Foot is Left")
    
    bs_Outline = Part.BSplineCurve()
    bs_Outline.buildFromPoles(points_outline, True)
    
    shoeEdge = doc.addObject("Part::Feature", "Shoe Edge")
    shoeEdge.Shape = bs_Outline.toShape()
    
    #self.mesh_foot = self.doc.getObjectsByLabel("Mesh")[0]      
        
def moveMesh():
    buildShoeShape(readJson())

    doc = FreeCAD.activeDocument()
    mesh_foot = doc.getObjectsByLabel("Mesh")[0]
    midpoint = doc.getObjectsByLabel("Foot Mid")[0]
    
    positions = ["lowest point of heel on the plantar surface",
                          "MTH1 on the plantar surface",
                          "MTH5 on the plantar surface",
                          "point on arch"]
                       
    heel_pt = doc.getObjectsByLabel(positions[0])[0]
    MTH1_pt = doc.getObjectsByLabel(positions[1])[0]
    MTH5_pt = doc.getObjectsByLabel(positions[2])[0]
    arch_pt = doc.getObjectsByLabel(positions[3])[0]

    heel_pt_x = heel_pt.X - midpoint.X
    heel_pt_y = heel_pt.Y - midpoint.Y
    heel_pt_z = heel_pt.Z - midpoint.Z
    
    MTH1_pt_x = MTH1_pt.X - midpoint.X
    MTH1_pt_y = MTH1_pt.Y - midpoint.Y
    MTH1_pt_z = MTH1_pt.Z - midpoint.Z
    
    MTH5_pt_x = MTH5_pt.X - midpoint.X
    MTH5_pt_y = MTH5_pt.Y - midpoint.Y
    MTH5_pt_z = MTH5_pt.Z - midpoint.Z
    
    arch_pt_x = arch_pt.X - midpoint.X
    arch_pt_y = arch_pt.Y - midpoint.Y
    arch_pt_z = arch_pt.Z - midpoint.Z
    doc.recompute()
    
    # Find foot plane normal
    a = (MTH1_pt_x - heel_pt_x, 
        MTH1_pt_y - heel_pt_y, 
        MTH1_pt_z - heel_pt_z)
    b = (MTH5_pt_x - heel_pt_x, 
        MTH5_pt_y - heel_pt_y, 
        MTH5_pt_z - heel_pt_z) 
    foot_plane_norm = cross(a, b)

    # Find rotation axis between foot plane and z axis
    z_axis = (0, 0, 1)
    rot_axis = cross(foot_plane_norm, z_axis)
    print(rot_axis)

    # Find rotation angle between foot plane normal and z axis
    unit_scale = math.sqrt(foot_plane_norm[0]**2 + 
                           foot_plane_norm[1]**2 + 
                           foot_plane_norm[2]**2)
    foot_plane_norm = (foot_plane_norm[0] / unit_scale,
                       foot_plane_norm[1] / unit_scale, 
                       foot_plane_norm[2] / unit_scale)
    d_prod = dot(foot_plane_norm, z_axis) 
    theta = math.degrees(math.acos(d_prod))
 
    ##Confirm/Fix left or right foot
    ##if arch_pt.Z < 0:
    #mesh_foot.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(FreeCAD.Vector(0,0,1),180),FreeCAD.Vector(0,0,0))
    ##newx0 = heel_center_x - heel_pt_x
    
    #New placement of the foot with translation and rotation to match shoe outline
    mesh_foot.Placement = FreeCAD.Placement(FreeCAD.Vector(midpoint.X,midpoint.Z,midpoint.Y), FreeCAD.Rotation(FreeCAD.Vector(-rot_axis[0], -rot_axis[1], rot_axis[2]),theta),FreeCAD.Vector(0,0,0))
    

def cross(v1, v2):
    cx = [v1[1] * v2[2] - v1[2] * v2[1],
          v1[2] * v2[0] - v1[0] * v2[2],
          v1[0] * v2[1] - v1[1] * v2[0]]
    return cx

def dot(v1, v2):
    dp = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    return dp



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
            elif list(self.positions.keys()).index(self.active_position) in range(len(list(self.positions.keys()))):
                if self.doc.getObjectsByLabel(self.active_position) != []:
                    point = self.doc.getObjectsByLabel(self.active_position)[0]
                    point.X = self.positions[self.active_position]["x"]
                    point.Y = self.positions[self.active_position]["y"]
                    point.Z = self.positions[self.active_position]["z"]
                else:
                    print(self.active_position)
                    point = self.doc.addObject("Part::Vertex", self.active_position)
                    point.X = self.positions[self.active_position]["x"]
                    point.Y = self.positions[self.active_position]["y"]
                    point.Z = self.positions[self.active_position]["z"]
                    point.Label = self.active_position
                
                self.doc.recompute()
                
                try:
                    self.active_position = list(self.positions.keys())[list(self.positions.keys()).index(self.active_position) + 1]
                    FreeCAD.Console.PrintMessage(f"Identify {self.active_position} \n")
                except:
                    #filepath = os.path.expanduser("~/Documents/landmarkVariables.json")
                    #with open(filepath, "w+") as write_file:
                        #json.dump(self.positions, write_file)
                    
                    # Determine forefoot centre point
                    MTH1_pt_X = self.positions["MTH1 on the plantar surface"]["x"]
                    MTH5_pt_X = self.positions["MTH5 on the plantar surface"]["x"]
                    
                    MTH1_pt_Y = self.positions["MTH1 on the plantar surface"]["y"]
                    MTH5_pt_Y = self.positions["MTH5 on the plantar surface"]["y"]
                    
                    MTH1_pt_Z = self.positions["MTH1 on the plantar surface"]["z"]
                    MTH5_pt_Z = self.positions["MTH5 on the plantar surface"]["z"]
                    
                    ff_mid = [(MTH1_pt_X + MTH5_pt_X) / 2, (MTH1_pt_Y + MTH5_pt_Y) / 2, (MTH1_pt_Z + MTH5_pt_Z) / 2]

                    # Determine foot centre point
                    heel_pt_X = self.positions["lowest point of heel on the plantar surface"]["x"]
                    heel_pt_Y = self.positions["lowest point of heel on the plantar surface"]["y"]
                    heel_pt_Z = self.positions["lowest point of heel on the plantar surface"]["z"]
                    
                    foot_mid = [(ff_mid[0] + heel_pt_X) / 2,(ff_mid[1] + heel_pt_Y) / 2, (ff_mid[2] + heel_pt_Z) / 2]
                    point_foot_mid = self.doc.addObject("Part::Vertex", "Foot Mid")
                    point_foot_mid.Label = "Foot Mid"
                    point_foot_mid.X = foot_mid[0]
                    point_foot_mid.Y = foot_mid[1]
                    point_foot_mid.Z = foot_mid[2]
                    self.doc.recompute()
                    moveMesh()
            else:
                pass
                
                
       

FreeCADGui.addCommand("Position", FOPosition())