# Title:OTHOTIC DESIGN
# Part:1
# Description: Postion
# Version 0.0
# Author: Hana Keller

#===================================

import FreeCAD, FreeCADGui
import Draft
import Part, PartGui
import os
import math
import numpy as np
import Mesh
import PySide.QtCore as QtCore
from draftutils.translate import translate
from PySide.QtCore import QT_TRANSLATE_NOOP
from functions import *

from task_position import PositionTaskPanel


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

shoeCord_female = [[-126, -132, -126, -134, -115, -122, -136, -142], 
                    [-24, -30, -22.5, -28.9, -22, -27, -25, -31], 
                    [-100, -100, -100, -102, -95, -100, -103, -103],
                    [29, 36, 24.9, 33.1, 26.0, 33, 31, 34],
                    [-100, -100, -100, -100, -100, -100, -100, -100],
                    [18, 20, 16.8, 20.5, 17, 24, 17, 28],
                    [-121, -128, -120, -127, -110, -115, -130, -125],
                    [-15, -17.5, -13.9, -17.8, -19, -22, -14, -15],
                    [-121, -124.5, -119, -125.4, -105, -110, -131, -138],
                    [25, 36, 17.2, 37.4, 21, 38, 13, 38],
                    [-10, -12.7, -10, -13.3, -10, -10, -16, -16],
                    [-31, -34, -27.7, -36.4, -26, -35, -28, -38],
                    [-40, -40, -40, -41, -40, -40, -40, -40],
                    [32, 41, 25.6, 43.4, 25, 44, 29, 47],
                    [25, 25, 25, 23.4, 25, 25, 30, 30],
                    [37, 44, 35, 46.6, 30, 46, 41, 50],
                    [40, 40, 40, 38.1, 40, 40, 50, 50],
                    [39, 45.5, 38.6, 47.3, 33, 47, 43.5, 51],
                    [46, 46, 46.4, 42, 46, 46, 56, 56],
                    [40, 46, 40.6, 48.4, 36, 47, 45, 51],
                    [50, 50, 50, 50, 50, 50, 60, 60],
                    [46, 51, 44.5, 49.4, 40, 45, 47, 51],
                    [80, 80, 80, 80, 80, 80, 80, 80],
                    [32, 35, 31, 34.2, 30, 35, 35, 40],
                    [135, 136.7, 134.2, 135.9, 124, 124, 140, 145],
                    [12, 13, 11.4, 12.2, 12, 11, 7, 10],
                    [145, 146, 143.9, 147.8, 134, 140, 154, 160],
                    [-13, -15.4, -12.3, -15.4, -11, -19, -9, -18],
                    [136, 137.7, 135.3, 137.7, 124, 124, 150, 150],
                    [-40, -44.5, -40, -47.6, -37, -43, -38, -46],
                    [60, 60, 60, 60, 60, 60, 80, 80],
                    [-38, -41, -36.9, -45, -35, -41, -39, -46],
                    [17, 17, 17, 17, 17, 17, 20, 20],
                    [-38.5, -42, -37.5, -46, -36, -42, -39, -46],
                    [22, 22, 22, 22, 22, 22, 22, 22],
                    [-39, -42.5, -38.6, -47, -37, -42, -39, -47],
                    [27, 27, 27, 26, 27, 27, 30, 30],
                    [-37, -40, -34.5, -43.4, -34, -41, -37, -45],
                    [9, 9, 9, 6.4, 9, 9, 10, 10]]
                    
shoeCord_male = [0]

class FOPosition:

    def GetResources(self):
        return {
                 "MenuText" : "Position",
                 "ToolTip"  : "Position the foot correctly"}
                 
    def Activated(self):
        self.ui = FreeCADGui.FOToolBar
        self.view = FreeCADGui.activeView()
        if self.ui:
            #Start position task panel, not set to visible
            self.ui.sourceCmd = self
            self.task = PositionTaskPanel()
        
        self.doc = FreeCAD.activeDocument()
        
        self.positions = {"lowest point of heel on the plantar surface": None,
                          "MTH1 on the plantar surface" : None,
                          "MTH5 on the plantar surface" : None,
                          "point on arch" : None}
        self.positionLabels = ["lowest_point_of_heel_on_the_plantar_surface",
                          "MTH1_on_the_plantar_surface",
                          "MTH5_on_the_plantar_surface",
                          "point_on_arch"]
        self.next_position = 0
        
        self.view = FreeCADGui.activeView()
        self.active_position = "lowest point of heel on the plantar surface"
        self.doc = FreeCAD.activeDocument()
        if self.doc.getObjectsByLabel("Shoe_Edge") == []:
            print("Identify lowest point of heel on the plantar surface")
            self.clickCallback = self.view.addEventCallback("SoMouseButtonEvent",self.logPosition)
        else:    
            FreeCADGui.Control.showDialog(self.task)
            


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
                    self.point = self.doc.getObjectsByLabel(self.positionLabels[0])
                    self.point.X = self.positions[self.active_position]["x"]
                    self.point.Y = self.positions[self.active_position]["y"]
                    self.point.Z = self.positions[self.active_position]["z"]
                else:
                    self.point = self.doc.addObject("Part::Vertex", self.active_position)
                    self.point.Label = self.active_position
                    self.point.X = self.positions[self.active_position]["x"]
                    self.point.Y = self.positions[self.active_position]["y"]
                    self.point.Z = self.positions[self.active_position]["z"]
                self.point.ViewObject.PointSize = 5
                self.point.ViewObject.PointColor = (0.3, 0.1, 0.8)                    
                self.doc.recompute()
                
                # Iterate over all positions in the self.positions dictionary
                self.next_position = list(self.positions.keys()).index(self.active_position) + 1
                if self.next_position <= len(self.positions.keys()) - 1:
                    self.active_position = list(self.positions.keys())[self.next_position]
                    FreeCAD.Console.PrintMessage(f"Identify {self.active_position} \n")
                else:                    
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
                    
                    self.foot_mid = [(ff_mid[0] + heel_pt_X) / 2,(ff_mid[1] + heel_pt_Y) / 2, (ff_mid[2] + heel_pt_Z) / 2]
                    self.midpoint = self.doc.addObject("Part::Vertex", "Foot Mid")
                    self.midpoint.Label = "Foot Mid"
                    self.midpoint.X = self.foot_mid[0]
                    self.midpoint.Y = self.foot_mid[1]
                    self.midpoint.Z = self.foot_mid[2]
                    self.doc.recompute()
                    self.moveMesh()
                    self.active_position = None
                    self.doc.recompute()
                    self.finish()
                    FreeCADGui.Control.showDialog(self.task)
                    FreeCADGui.ActiveDocument.ActiveView.fitAll()
            else:
                pass   
    
    # def getShoeCords (self):
        # filepath = os.path.expanduser("~/Documents/shoeOutline.txt")
        # f = open(filepath, "r")
        # shoeCord = f.read()
   
    def buildShoeShape(self, size_index):        
        # make shoe outline numbers into coordinates
        
        # heel_center = [0, heel_center_pt_y[size_index], 0]
        # heel_lateral = [heel_lateral_pt_x[size_index], heel_lateral_pt_y[size_index], 0]
        # heel_medial = [heel_medial_pt_x[size_index], heel_medial_pt_y[size_index], 0]
        # heel_center_medial = [heel_center_medial_x[size_index], heel_center_medial_y[size_index], 0]
        # heel_center_lateral = [heel_center_lateral_x[size_index], heel_center_lateral_y[size_index], 0]
        # arch_medial = [arch_medial_pt_x[size_index], arch_medial_pt_y[size_index], 0]
        # arch_lateral = [arch_lateral_pt_x[size_index], arch_lateral_pt_y[size_index], 0]
        # mtpj1_prox = [mtpj1_prox_x[size_index], mtpj1_prox_y[size_index], 0]
        # mtpj1 = [mtpj1_pt_x[size_index], mtpj1_pt_y[size_index], 0]
        # mtpj1 = [mtpj1_pt_x[size_index], mtpj1_pt_y[size_index], 0]
        # mtpj1_dist1 = [mtpj1_dist1_x[size_index], mtpj1_dist1_y[size_index], 0]
        # mtpj1_dist2 = [mtpj1_dist2_x[size_index], mtpj1_dist2_y[size_index], 0]
        # ff_med = [ff_med_x[size_index], ff_med_y[size_index], 0]
        # toe_med = [toe_med_x[size_index], toe_med_y[size_index], 0]
        # toe = [toe_pt_x[size_index], toe_pt_y[size_index], 0]
        # toe_lat = [toe_lat_x[size_index], toe_lat_y[size_index], 0]
        # ff_lat = [ff_lat_x[size_index], ff_lat_y[size_index], 0]
        # mtpj5 = [mtpj5_pt_x[size_index], mtpj5_pt_y[size_index], 0]
        # mtpj5_dist1 = [mtpj5_dist1_x[size_index], mtpj5_dist1_y[size_index], 0]
        # mtpj5_dist2 = [mtpj5_dist2_x[size_index], mtpj5_dist2_y[size_index], 0]
        # mtpj5_prox = [mtpj5_prox_x[size_index], mtpj5_prox_y[size_index], 0]
        
        
        #ShoeCords order: heel_center_pt_y ,heel_lateral_pt_x ,heel_lateral_pt_y ,heel_medial_pt_x,heel_medial_pt_y ,heel_center_medial_x,heel_center_medial_y,heel_center_lateral_x ,heel_center_lateral_y,arch_medial_pt_x,arch_medial_pt_y,arch_lateral_pt_x,
            #arch_lateral_pt_y,mtpj1_prox_x,mtpj1_prox_y,mtpj1_pt_x,mtpj1_pt_y,mtpj1_dist1_x,mtpj1_dist1_y ,mtpj1_dist2_x,mtpj1_dist2_y,ff_med_x,ff_med_y,toe_med_x,toe_med_y ,toe_pt_x,toe_pt_y,toe_lat_x,toe_lat_y,ff_lat_x,ff_lat_y,mtpj5_pt_x,
            #mtpj5_pt_y,mtpj5_dist1_x ,mtpj5_dist1_y,mtpj5_dist2_x,mtpj5_dist2_y,mtpj5_prox_x,mtpj5_prox_y
        shoe_sex = int(self.doc.getObjectsByLabel("shoe_sex")[0].X) # Female = 1, Male = -1
        if shoe_sex == 1:
            shoeCord = shoeCord_female
        else:
            shoeCord = shoeCord_male
        heel_center = [0, shoeCord[0][size_index], 0]
        heel_lateral = [shoeCord[1][size_index], shoeCord[2][size_index], 0]
        heel_medial = [shoeCord[3][size_index], shoeCord[4][size_index], 0]
        heel_center_medial = [shoeCord[5][size_index], shoeCord[6][size_index], 0]
        heel_center_lateral = [shoeCord[7][size_index], shoeCord[8][size_index], 0]
        arch_medial = [shoeCord[9][size_index], shoeCord[10][size_index], 0]
        arch_lateral = [shoeCord[11][size_index], shoeCord[12][size_index], 0]
        mtpj1_prox = [shoeCord[13][size_index], shoeCord[14][size_index], 0]
        mtpj1 = [shoeCord[15][size_index], shoeCord[16][size_index], 0]
        mtpj1_dist1 = [shoeCord[17][size_index], shoeCord[18][size_index], 0]
        mtpj1_dist2 = [shoeCord[19][size_index], shoeCord[20][size_index], 0]
        ff_med = [shoeCord[21][size_index], shoeCord[22][size_index], 0]
        toe_med = [shoeCord[23][size_index], shoeCord[24][size_index], 0]
        toe = [shoeCord[25][size_index], shoeCord[26][size_index], 0]
        toe_lat = [shoeCord[27][size_index], shoeCord[28][size_index], 0]
        ff_lat = [shoeCord[29][size_index], shoeCord[30][size_index], 0]
        mtpj5 = [shoeCord[31][size_index], shoeCord[32][size_index], 0]
        mtpj5_dist1 = [shoeCord[33][size_index], shoeCord[34][size_index], 0]
        mtpj5_dist2 = [shoeCord[35][size_index], shoeCord[36][size_index], 0]
        mtpj5_prox = [shoeCord[37][size_index], shoeCord[38][size_index], 0]
        
        points_outline = [heel_center, heel_center_medial,
                                     heel_medial, arch_medial, mtpj1_prox, mtpj1,
                                     mtpj1_dist1, mtpj1_dist2, ff_med, toe_med, toe,
                                     toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1,
                                     mtpj5, mtpj5_prox, arch_lateral, heel_lateral,
                                     heel_center_lateral, heel_center]
                                     
                                     
        ##Confirm Left or Right foot:                           
        self.heel_pt = self.doc.getObjectsByLabel("lowest point of heel on the plantar surface")[0]
        self.MTH1_pt = self.doc.getObjectsByLabel("MTH1 on the plantar surface")[0]
        
        self.arch_pt = self.doc.getObjectsByLabel("point on arch")[0]
        self.MTH5_pt = self.doc.getObjectsByLabel("MTH5 on the plantar surface")[0]

        vec1 = [self.heel_pt.X - self.MTH1_pt.X, self.heel_pt.Y - self.MTH1_pt.Y, self.heel_pt.Z - self.MTH1_pt.Z]
        vec2 = [self.MTH5_pt.X - self.MTH1_pt.X, self.MTH5_pt.Y - self.MTH1_pt.Y, self.MTH5_pt.Z - self.MTH1_pt.Z]
        
        planeVec = cross(vec1, vec2)
        k = - planeVec[0] * self.heel_pt.X - planeVec[1] * self.heel_pt.Y - planeVec[2] * self.heel_pt.Z
        
        expectedZ = -(self.arch_pt.X * planeVec[0] + self.arch_pt.Y * planeVec[1] + k)/planeVec[2]
                   
        if self.arch_pt.Z < expectedZ:
            for i in range(len(points_outline)):
                points_outline[i]=[-points_outline[i][0], points_outline[i][1], points_outline[i][2]]
            self.side = "Right"
            point = self.doc.addObject("Part::Vertex", "side")
            point.X = 1
            point.Y = 0
            point.Z = 0
            point.Label = "side"
            point.ViewObject.hide()
        else:
            self.side = "Left"
            point = self.doc.addObject("Part::Vertex", "side")
            point.X = -1
            point.Y = 0
            point.Z = 0
            point.Label = "side"
            point.ViewObject.hide()
            
            
        self.bs_Outline = Part.BSplineCurve()
        self.bs_Outline.buildFromPoles(points_outline, True)
        
        self.shoeEdge = self.doc.addObject("Part::Feature", "Shoe Edge")
        self.shoeEdge.ViewObject.LineColor = (0.4,0.0,1.00)
        self.shoeEdge.ViewObject.LineWidth = 3

        self.shoeEdge.Shape = self.bs_Outline.toShape()
        self.doc.recompute()

            
    def moveMesh(self):
        shoe_size = int(self.doc.getObjectsByLabel("shoe_size")[0].X)
        self.buildShoeShape(shoe_size)
        mesh_foot = self.doc.getObjectsByLabel("Mesh")[0]

        heel_pt_x = self.heel_pt.X - self.midpoint.X
        heel_pt_y = self.heel_pt.Y - self.midpoint.Y
        heel_pt_z = self.heel_pt.Z - self.midpoint.Z
        
        MTH1_pt_x = self.MTH1_pt.X - self.midpoint.X
        MTH1_pt_y = self.MTH1_pt.Y - self.midpoint.Y
        MTH1_pt_z = self.MTH1_pt.Z - self.midpoint.Z
        
        MTH5_pt_x = self.MTH5_pt.X - self.midpoint.X
        MTH5_pt_y = self.MTH5_pt.Y - self.midpoint.Y
        MTH5_pt_z = self.MTH5_pt.Z - self.midpoint.Z
        
        arch_pt_x = self.arch_pt.X - self.midpoint.X
        arch_pt_y = self.arch_pt.Y - self.midpoint.Y
        arch_pt_z = self.arch_pt.Z - self.midpoint.Z
        self.doc.recompute()
        
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

        # Find rotation angle between foot plane normal and z axis
        unit_scale = math.sqrt(foot_plane_norm[0]**2 + 
                               foot_plane_norm[1]**2 + 
                               foot_plane_norm[2]**2)
        foot_plane_norm = (foot_plane_norm[0] / unit_scale,
                           foot_plane_norm[1] / unit_scale, 
                           foot_plane_norm[2] / unit_scale)
        d_prod = dot(foot_plane_norm, z_axis) 
        theta = math.degrees(math.acos(d_prod))
     
        
        #New placement of the foot with translation and rotation to match shoe outline
        mesh_foot.Placement = FreeCAD.Placement(FreeCAD.Vector(self.midpoint.X,self.midpoint.Z,self.midpoint.Y), 
                                                FreeCAD.Rotation(FreeCAD.Vector(-rot_axis[0], -rot_axis[1], rot_axis[2]),theta),
                                                FreeCAD.Vector(0,0,0))
        self.mesh_final = mesh_foot.Mesh.copy()
        Mesh.show(self.mesh_final)
        self.doc.recompute()
        
    def remove_objects(self):
        #Removes points made to rotate mesh
        for obj in self.doc.Objects:
            if obj.Label not in ["Shoe_Edge", "Mesh001", "posting", "shoe_size", "shoe_sex", "FO_thickness", "heel_raise", "side"]:
                try:
                    self.doc.removeObject(obj.Label.replace(' ', '_'))
                except Exception as e:
                    print(f"Could not remove {obj.Label.replace(' ', '_')} exception {e}")
        self.doc.recompute()

    def finish(self):
        self.remove_objects()
        if self.clickCallback:
            try:
                self.view.removeEventCallback("SoMouseButtonEvent", self.clickCallback)
                self.clickCallback = None
            except Exception as e:
                 print(e)
        FreeCADGui.Selection.clearSelection()


FreeCADGui.addCommand("Position", FOPosition())