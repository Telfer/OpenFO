import FreeCAD, FreeCADGui
import Draft
import Part, PartGui
import os
import math
from functions import *
import numpy as np


# Gordoncurve / Bspline curve


class FOBuild:
    def GetResources(self):
        return { 
                 "MenuText" : "Build",
                 "ToolTip"  : "Build FO"}
   

    def Activated(self):
        FreeCADGui.SendMsgToActiveView("ViewFit")
        self.view = FreeCADGui.activeView()
        self.doc = FreeCAD.activeDocument()
        if self.get_params():
            self.build_FO(self.sides, self.FO_Thickness, self.medHeel, self.postHeel, self.latHeel, self.latArch, self.medArch, self.MTPJ1, self.MTPJ5, self.posting, 0.65, self.heel_raise)

    
    def get_params(self):
        try:
            self.FO_Thickness = int(self.doc.getObjectsByLabel("FO_thickness")[0].X)
            self.posting = int(self.doc.getObjectsByLabel("posting")[0].X)
            self.heel_raise = int(self.doc.getObjectsByLabel("heel_raise")[0].X)
        except:
            print("Complete Import function first")
            return False
        try: 
            self.sides = int(self.doc.getObjectsByLabel("side")[0].X)
            self.mesh_foot = self.doc.getObjectsByLabel("Mesh001")[0]
        except:
            print("Complete Position function first")
            return False
        try:
            self.latHeel = self.doc.getObjectsByLabel("point on lateral side of heel")[0]
            self.latHeel = self.returnPoint(self.latHeel)
            self.postHeel = self.doc.getObjectsByLabel("point on posterior of heel")[0]
            self.postHeel = self.returnPoint(self.postHeel)
            self.medHeel = self.doc.getObjectsByLabel("point on medial side of heel")[0]
            self.medHeel = self.returnPoint(self.medHeel)
            self.latArch = self.doc.getObjectsByLabel("highest point on lateral arch")[0]
            self.latArch = self.returnPoint(self.latArch)
            self.medArch = self.doc.getObjectsByLabel("highest point on medial arch")[0]
            self.medArch = self.returnPoint(self.medArch)
            self.MTPJ1 = self.doc.getObjectsByLabel("the medial side of the distal MTH1")[0]
            self.MTPJ1 = self.returnPoint(self.MTPJ1)
            self.MTPJ5 = self.doc.getObjectsByLabel("the lateral side of the distal MTH5")[0]
            self.MTPJ5 = self.returnPoint(self.MTPJ5)
        except:
            print("Complete Landmark function first")
            return False
        return True
    
    def returnPoint(self, obj):
        returnpoint = [float(obj.X), float(obj.Y), float(obj.Z)]
        return returnpoint
    
    def rot_point_coords(self, pt, center, angle, axis):
        point = self.doc.addObject("Part::Vertex", "pt")
        point.X = pt[0]
        point.Y = pt[1]
        point.Z = pt[2]
        point.Placement = FreeCAD.Placement(point, center, angle, axis)
        point2 = [point.X, point.Y, point.Z]
        
        self.doc.removeObject('pt')
        self.doc.recompute()
        
        return point2
        
    def makePoint(self, label, newpoint):
        if self.doc.getObjectsByLabel(label) != []:
            #If landmark already set, change current landmark
            point = self.doc.getObjectsByLabel(label)[0]
            point.X = newpoint[0]
            point.Y = newpoint[1]
            point.Z = newpoint[2]
        else:
            #If landmark not set yet, create new point
            point = self.doc.addObject("Part::Vertex", label)
            point.X = newpoint[0]
            point.Y = newpoint[1]
            point.Z = newpoint[2]
            point.Label = label
        point.ViewObject.ShapeColor = (1.00,1.00,1.00)
        point.ViewObject.LineColor = (1.00,1.00,1.00)
        point.ViewObject.LineWidth = 5
        point.ViewObject.PointSize = 5
        point.ViewObject.PointColor = (1.00, 0.1, 0.8)
    
    
    def build_FO(self, side, thickness, heel_medial, heel_center, heel_lateral,
                 arch_lateral, arch_medial, mtpj1, mtpj5, posting, heel_offset, heel_rise):
        
        ## forefoot offset
        ff_offset = -5.0
        
        ## adjust for side if required
        if side < 0:  ##May need to be >0
            heel_medial[0] = heel_medial[0] * -1 
            heel_center[0] = heel_center[0] * -1
            heel_lateral[0] = heel_lateral[0] * -1 
            arch_medial[0] = arch_medial[0] * -1 
            mtpj1[0] = mtpj1[0] * -1 
            mtpj5[0] = mtpj5[0] * -1 
            arch_lateral[0] = arch_lateral[0] * -1
        
        
        # =========================================================================
        
        ## Hindfoot posting adjustment
        if heel_medial[2] > 20:
            heel_medial[2] = 20
        if heel_lateral[2] > 20:
            heel_lateral[2] = 20
        if heel_center[2] > 20:
            heel_center[2] = 20
        if posting != 0:
            heel_medial = self.rot_point_coords(heel_medial, heel_center, posting, 
                                           [0.0, 1.0, 0.0])
            heel_lateral = self.rot_point_coords(heel_lateral, heel_center, posting, 
                                            [0.0, 1.0, 0.0])
            arch_medial = self.rot_point_coords(arch_medial, heel_center, posting, 
                                           [0.0, 1.0, 0.0])
            arch_lateral = self.rot_point_coords(arch_lateral, heel_center, posting, 
                                            [0.0, 1.0, 0.0])
        
        
        # =========================================================================
        
        # forefoot width adjustment
        ff_d = dist_2_points(mtpj1, mtpj5)
        
        if (ff_d > 90):
            x = (ff_d - 85) / 2
            mtpj1 = [mtpj1[0] + x, mtpj1[1], mtpj1[2]]
            mtpj5 = [mtpj5[0] - x, mtpj5[1], mtpj5[2]]

        # =========================================================================
        
        # calculated landmarks
        
        ## adjusted heel landmarks
        heel_center_med_offset = ((heel_medial[0] - heel_center[0]) * heel_offset)
        heel_center_medial = [heel_center[0] + heel_center_med_offset,
                              heel_center[1] + 5, heel_center[2]]
        if posting != 0:
            heel_center_medial = self.rot_point_coords(heel_center_medial, heel_center, 
                                                  posting, [0.0, 1.0, 0.0])
        heel_center_lat_offset = -1 * ((heel_lateral[0] - heel_center[0]) * heel_offset)
        heel_center_lateral = [heel_center[0] - heel_center_lat_offset, 
                               heel_center[1] + 5, heel_center[2]]
        if posting != 0:
            heel_center_lateral = self.rot_point_coords(heel_center_lateral, heel_center, 
                                                   posting, [0.0, 1.0, 0.0])
        
        # adjusted mtpj landmarks
        mtpj1_adj = [mtpj1[0] + 2.0, mtpj1[1] - 10.0, ff_offset]
        mtpj5_adj = [mtpj5[0] - 2.0, mtpj5[1] - 10.0, ff_offset]
        ff_center = [(mtpj1_adj[0] + mtpj5_adj[0]) / 2, 
                     ((mtpj1_adj[1] + mtpj5_adj[1]) / 2) + 4, ff_offset]
        
        
        # adjusted arch landmarks
        if arch_lateral[2] > 12:    
            arch_lateral[2] = 12
        arch_medial_adj = proj_point_y(heel_medial, mtpj1_adj, arch_medial[1])
        arch_medial_adj = [arch_medial_adj, arch_medial[1], arch_medial[2]]
        arch_lateral_adj = proj_point_y(heel_lateral, mtpj5_adj, arch_lateral[1])
        arch_lateral_adj = [arch_lateral_adj, arch_lateral[1], arch_lateral[2]]
        
        # adjust mtpj landmarks
        mtpj1_prox1 = proj_point_y(mtpj1_adj, [arch_medial_adj[0], arch_medial_adj[1], ff_offset],
                                   mtpj1_adj[1] - 2)
        mtpj1_prox1 = [mtpj1_prox1 + 0.4, mtpj1_adj[1] - 2, ff_offset]
        mtpj1_prox2 = proj_point_y(mtpj1_adj, [arch_medial_adj[0], arch_medial_adj[1], ff_offset], 
                                   mtpj1_adj[1] - 4)
        mtpj1_prox2 = [mtpj1_prox2, mtpj1_adj[1] - 4, ff_offset + 0.5]
        mtpj1_lateral1 = proj_point_x(ff_center, mtpj1_adj, mtpj1_adj[0] - 2)
        mtpj1_lateral1 = [mtpj1_adj[0] + 2, mtpj1_lateral1 -0.4, ff_offset]
        mtpj1_lateral2 = proj_point_x(ff_center, mtpj1_adj, mtpj1_adj[0] - 4)
        mtpj1_lateral2 = [mtpj1_adj[0] + 4, mtpj1_lateral2, ff_offset]
        mtpj5_prox1 = proj_point_y(mtpj5_adj, [arch_lateral_adj[0], arch_lateral_adj[1], ff_offset], 
                                   mtpj5_adj[1] - 2)
        mtpj5_prox1 = [mtpj5_prox1 - 0.4, mtpj5_adj[1] - 2, ff_offset]
        mtpj5_prox2 = proj_point_y(mtpj5_adj, [arch_lateral_adj[0], arch_lateral_adj[1], ff_offset], 
                                   mtpj5_adj[1] - 4)
        mtpj5_prox2 = [mtpj5_prox2, mtpj5_adj[1] - 4, ff_offset + 0.5]
        mtpj5_lateral1 = proj_point_x(ff_center, mtpj5_adj, mtpj5_adj[0] + 2)
        mtpj5_lateral1 = [mtpj5_adj[0] - 2, mtpj5_lateral1 -0.4, ff_offset]
        mtpj5_lateral2 = proj_point_x(ff_center, mtpj5_adj, mtpj5_adj[0] + 4)
        mtpj5_lateral2 = [mtpj5_adj[0] - 4, mtpj5_lateral2, ff_offset]
        arch_mid = [(arch_medial[0] + arch_lateral[0]) / 2,
                    (arch_medial[1] + arch_lateral[1]) / 2, 5.0]
              
        # # calculated landmarks
        
        # #adjusted heel landmarks
        # heel_center_med_offset = ((heel_medial[0] - heel_center[0]) * heel_offset)
        # heel_center_medial = [heel_center[0] + heel_center_med_offset,
                              # heel_center[1] + 5, heel_center[2]]
        # if posting != 0:
            # heel_center_medial = self.rot_point_coords(heel_center_medial, heel_center, 
                                                  # posting, [0.0, 1.0, 0.0])
        # heel_center_lat_offset = -1 * ((heel_lateral[0] - heel_center[0]) * heel_offset)
        # heel_center_lateral = [heel_center[0] - heel_center_lat_offset, 
                               # heel_center[1] + 5, heel_center[2]]
        # if posting != 0:
            # heel_center_lateral = self.rot_point_coords(heel_center_lateral, heel_center, 
                                                   # posting, [0.0, 1.0, 0.0])
        
        # # adjusted mtpj landmarks
        # mtpj1_adj = [mtpj1[0] - 2.0, mtpj1[1] - 10.0, ff_offset]
        # mtpj5_adj = [mtpj5[0] + 2.0, mtpj5[1] - 10.0, ff_offset]
        # ff_center = [(mtpj1_adj[0] + mtpj5_adj[0]) / 2, 
                     # ((mtpj1_adj[1] + mtpj5_adj[1]) / 2) + 4, ff_offset]
        
        # # adjusted arch landmarks
        # if arch_lateral[2] > 12:    
            # arch_lateral[2] = 12
        # arch_medial_adj = proj_point_y(heel_medial, mtpj1_adj, arch_medial[1])
        # arch_medial_adj = [arch_medial_adj, arch_medial[1], arch_medial[2]]
        # arch_lateral_adj = proj_point_y(heel_lateral, mtpj5_adj, arch_lateral[1])
        # arch_lateral_adj = [arch_lateral_adj, arch_lateral[1], arch_lateral[2]]
        
        # # adjust mtpj landmarks
        # mtpj1_prox1 = proj_point_y(mtpj1_adj, [arch_medial_adj[0], arch_medial_adj[1], ff_offset],
                                   # mtpj1_adj[1] - 2)
        # mtpj1_prox1 = [mtpj1_prox1 - 0.4, mtpj1_adj[1] - 2, ff_offset]
        # mtpj1_prox2 = proj_point_y(mtpj1_adj, [arch_medial_adj[0], arch_medial_adj[1], ff_offset], 
                                   # mtpj1_adj[1] - 4)
        # mtpj1_prox2 = [mtpj1_prox2, mtpj1_adj[1] - 4, ff_offset + 0.5]
        # mtpj1_lateral1 = proj_point_x(ff_center, mtpj1_adj, mtpj1_adj[0] - 2)
        # mtpj1_lateral1 = [mtpj1_adj[0] - 2, mtpj1_lateral1 -0.4, ff_offset]
        # mtpj1_lateral2 = proj_point_x(ff_center, mtpj1_adj, mtpj1_adj[0] - 4)
        # mtpj1_lateral2 = [mtpj1_adj[0] - 4, mtpj1_lateral2, ff_offset]
        # mtpj5_prox1 = proj_point_y(mtpj5_adj, [arch_lateral_adj[0], arch_lateral_adj[1], ff_offset], 
                                   # mtpj5_adj[1] - 2)
        # mtpj5_prox1 = [mtpj5_prox1 + 0.4, mtpj5_adj[1] - 2, ff_offset]
        # mtpj5_prox2 = proj_point_y(mtpj5_adj, [arch_lateral_adj[0], arch_lateral_adj[1], ff_offset], 
                                   # mtpj5_adj[1] - 4)
        # mtpj5_prox2 = [mtpj5_prox2, mtpj5_adj[1] - 4, ff_offset + 0.5]
        # mtpj5_lateral1 = proj_point_x(ff_center, mtpj5_adj, mtpj5_adj[0] + 2)
        # mtpj5_lateral1 = [mtpj5_adj[0] + 2, mtpj5_lateral1 -0.4, ff_offset]
        # mtpj5_lateral2 = proj_point_x(ff_center, mtpj5_adj, mtpj5_adj[0] + 4)
        # mtpj5_lateral2 = [mtpj5_adj[0] + 4, mtpj5_lateral2, ff_offset]
        # arch_mid = [(arch_medial[0] + arch_lateral[0]) / 2,
                    # (arch_medial[1] + arch_lateral[1]) / 2, 5.0]
                    
               
        # =========================================================================
        
        # make curves

        
        self.shoeEdge = self.doc.getObjectsByLabel("Shoe_Edge")[0]
        
        #points for curve creation
        self.makePoint("heel center", heel_center)
        self.makePoint("heel center medial", heel_center_medial)
        self.makePoint("heel center lateral", heel_center_lateral)
        self.makePoint("heel medial", heel_medial)
        self.makePoint("heel lateral", heel_lateral)
        self.makePoint("arch medial adjusted", arch_medial_adj)
        self.makePoint("MTPJ1 proximal 1", mtpj1_prox1)
        self.makePoint("MTPJ1 proximal 2", mtpj1_prox2)
        self.makePoint("MTPJ5 proximal 1", mtpj5_prox1)
        self.makePoint("MTPJ5 proximal 2", mtpj5_prox2)
        self.makePoint("MTPJ1 lateral 1", mtpj1_lateral1)
        self.makePoint("MTPJ1 lateral 2", mtpj1_lateral2)
        self.makePoint("MTPJ5 lateral 1", mtpj5_lateral1)
        self.makePoint("MTPJ5 lateral 2", mtpj5_lateral2)
        self.makePoint("fore foot center", ff_center)
        self.makePoint("arch medial adjusted", arch_medial_adj)
        self.makePoint("arch lateral adjusted", arch_lateral_adj)
        self.makePoint("arch middle", arch_mid)
        
        point1 = [(heel_medial[0] + heel_lateral[0]) / 2,(heel_medial[1] + heel_lateral[1]) / 2, 0.0]
        point2 = [(heel_medial[0] + heel_lateral[0]) / 2, (heel_medial[1] + heel_lateral[1]) / 2, 2.0]
        self.makePoint('mid center curve point', point1)
        self.makePoint('mid cross curve heel point', point2)
               
        ## MEDIAL CURVE                                     
        medial_curve_points_vectors = [FreeCAD.Vector(heel_center), FreeCAD.Vector(heel_center_medial),
                                          FreeCAD.Vector(heel_medial), FreeCAD.Vector(arch_medial_adj), 
                                          FreeCAD.Vector(mtpj1_prox2), FreeCAD.Vector(mtpj1_prox1), FreeCAD.Vector(mtpj1_lateral1),
                                          FreeCAD.Vector(mtpj1_lateral2),
                                          FreeCAD.Vector(ff_center)]
        #medial_curve = Draft.make_bspline(medial_curve_points_vectors, closed=False, face=False, support=None)
        #medial_curve.ViewObject.LineColor = (0.0,0.5,0.5)
        
        ## LATERAL CURVE                                 
        lateral_curve_points = [FreeCAD.Vector(heel_center), FreeCAD.Vector(heel_center_lateral),
                                           FreeCAD.Vector(heel_lateral), FreeCAD.Vector(arch_lateral_adj), 
                                           FreeCAD.Vector(mtpj5_prox2), FreeCAD.Vector(mtpj5_prox1), FreeCAD.Vector(mtpj5_lateral1),
                                           FreeCAD.Vector(mtpj5_lateral2),
                                           FreeCAD.Vector(ff_center)]
        #lateral_curve = Draft.make_bspline(lateral_curve_points, closed=False, face=False, support=None)
        #lateral_curve.ViewObject.LineColor = (0.0,0.5,0.5)         
                 
        ## CENTER CURVE                                   
        center_curve_points = [FreeCAD.Vector(heel_center), 
                                          FreeCAD.Vector([(heel_medial[0] + heel_lateral[0]) / 2, 
                                          (heel_medial[1] + heel_lateral[1]) / 2, 0.0]),
                                          FreeCAD.Vector(arch_mid), FreeCAD.Vector(ff_center)]
        center_curve = Draft.make_bspline(center_curve_points, closed=False, face=False, support=None)                                  
        center_curve.ViewObject.LineColor = (0.0,0.5,0.5)
        
        ## CROSS CURVE HEEL        
        cross_curve_heel_points = [FreeCAD.Vector(heel_medial), 
                                              FreeCAD.Vector([(heel_medial[0] + heel_lateral[0]) / 2, 
                                               (heel_medial[1] + heel_lateral[1]) / 2, 2.0]), 
                                              FreeCAD.Vector(heel_lateral)] 
         
        cross_curve_heel = Draft.make_bspline(cross_curve_heel_points, closed=False, face=False, support=None)
        cross_curve_heel.ViewObject.LineColor = (0.0,0.5,0.5)
        
        ## CROSS CURVE ARCH                                
        cross_curve_arch_points = [FreeCAD.Vector(arch_medial_adj), FreeCAD.Vector(arch_mid), 
                                              FreeCAD.Vector(arch_lateral_adj)]
        cross_curve_arch = Draft.make_bspline(cross_curve_arch_points, closed=False, face=False, support=None)
        cross_curve_arch.ViewObject.LineColor = (0.0,0.5,0.5) 
                  
        ## TOTAL OUTSIDE CURVE          
        total_curve_points = [FreeCAD.Vector(heel_center), FreeCAD.Vector(heel_center_medial),
                                          FreeCAD.Vector(heel_medial), FreeCAD.Vector(arch_medial_adj), 
                                          FreeCAD.Vector(mtpj1_prox2), FreeCAD.Vector(mtpj1_prox1), FreeCAD.Vector(mtpj1_lateral1),
                                          FreeCAD.Vector(mtpj1_lateral2),
                                          FreeCAD.Vector(ff_center), FreeCAD.Vector(mtpj5_lateral2),FreeCAD.Vector(mtpj5_lateral1),FreeCAD.Vector(mtpj5_prox1),FreeCAD.Vector(mtpj5_prox2),FreeCAD.Vector(arch_lateral_adj), FreeCAD.Vector(heel_lateral),
                                          FreeCAD.Vector(heel_center_lateral)]
        total_curve = Draft.make_bspline(total_curve_points, closed=True, face=False, support=None)
        total_curve.ViewObject.LineColor = (0.2,0.8,0.5)
        
        
        self.doc.recompute()
        
        
        # =========================================================================
        
        # make top surface
        #top_srf = rs.AddNetworkSrf([medial_curve, lateral_curve, center_curve, 
                                    #cross_curve_heel, cross_curve_arch])
        
        
        # =========================================================================
        
        # make bottom surface 
        #bottom_srf = rs.CopyObject(top_srf)
        #bottom_srf = rs.MoveObject(bottom_srf, [0.0, 0.0, -3.0]) #thickness
        
        
        # =========================================================================
        
        # make edges
        #edges = rs.DuplicateSurfaceBorder(top_srf)
        #ext_line = rs.AddLine([0.0, 0.0, 0.0], [0.0, 0.0, -3.0])
        #edge_srf = rs.ExtrudeCurve(edges, ext_line)
        #rs.DeleteObjects([edges, ext_line])
        
        
        # =========================================================================
        
        # add heel 
        ## heel outline
        # heel_curve = rs.AddInterpCurve([[heel_medial[0] - 3.0, 
                                         # heel_medial[1] + 10.0, 0.0],
                                        # [heel_medial[0] - 3.0, 
                                         # heel_medial[1] + 1.0, 0.0],
                                        # [heel_medial[0] - 3.0, heel_medial[1], 0.0], 
                                        # [heel_center_medial[0] - 3.0, 
                                         # heel_center_medial[1] + 3.0, 0.0],
                                        # [heel_center[0], heel_center[1] + 3.0, 0.0],
                                        # [heel_center_lateral[0] + 3.0, 
                                         # heel_center_lateral[1] + 4.0, 0.0],
                                        # [heel_lateral[0] + 3.0, heel_lateral[1], 0.0],
                                        # [heel_lateral[0] + 3.0, 
                                         # heel_lateral[1] + 1.0, 0.0],
                                        # [heel_lateral[0] + 3.0, 
                                         # heel_lateral[1] + 10.0, 0.0]],
                                        # knotstyle = 2)
        # heel_curve2 = rs.OffsetCurve(heel_curve, [0, 0, 0], 4.0)
        # heel_line = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 0.0], 
                               # [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 0.0])
        # heel_line2 = rs.AddLine([heel_medial[0] - 7.0, heel_medial[1] + 10.0, 0.0], 
                                # [heel_lateral[0] + 7.0, heel_lateral[1] + 10.0, 0.0])
        # heel_curve_c = rs.JoinCurves([heel_curve, heel_line])
        
        # ## heel bottom surface
        # heel_bottom_srf = rs.AddEdgeSrf([heel_curve2, heel_line2])
        # heel_bottom_srf = rs.MoveObject(heel_bottom_srf, [0.0, 0.0, -4.0])
        
        # ## heel bottom curve
        # bot_rad = rs.AddArc(rs.WorldZXPlane(), 4.0, 90.0)
        # bot_rad = rs.RotateObject(bot_rad, [0, 0, 0], 90, [0, 1, 0])
        # bot_rad = rs.MoveObject(bot_rad, [heel_medial[0] - 7.0, 
                                          # heel_medial[1] + 10.0, 0.0])
        # heel_bottom_edge = rs.AddSweep1(heel_curve, [bot_rad])
        
        # ## heel sides
        # ext_line = rs.AddLine([0.0, 0.0, 0.0], [0.0, 0.0, 30.0])
        # heel_edge = rs.ExtrudeCurve(heel_curve, ext_line)
        
        # ## heel front1
        # bot_rad2 = rs.AddArc(rs.WorldZXPlane(), 4.0, 90.0)
        # bot_rad2 = rs.RotateObject(bot_rad2, [0, 0, 0], 180, [0, 1, 0])
        # bot_rad2 = rs.MoveObject(bot_rad2, [heel_lateral[0] + 7.0, 
                                            # heel_lateral[1] + 10.0, 0.0])
        # top_edge = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 0.0],
                              # [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 0.0])
        # bott_edge = rs.AddLine([heel_medial[0] - 5.0, heel_medial[1] + 10.0, -2.0], 
                               # [heel_lateral[0] + 5.0, heel_lateral[1] + 10.0, -2.0])
        # front_edge = rs.AddEdgeSrf([bot_rad, bot_rad2, top_edge, bott_edge])
        
        # ## heel front 2
        # med_line = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 0.0], 
                              # [heel_medial[0] - 3.0, heel_medial[1] + 10.0, 30.0])
        # lat_line = rs.AddLine([heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 0.0],
                              # [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 30.0])
        # top_line = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 30.0],
                              # [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 30.0])
        # front_edge2 = rs.AddEdgeSrf([med_line, top_line, lat_line, top_edge])
        
        # ## heel top surface
        # heel_srf = rs.JoinSurfaces([heel_bottom_srf, heel_bottom_edge, heel_edge, 
                                    # front_edge, front_edge2])
        # heel_srf = rs.MoveObject(heel_srf, [0.0, 0.0, -2.0])
        # rot_center_x = (heel_lateral[0] + heel_medial[0]) / 2
        # rot_center_y = (heel_lateral[1] + heel_medial[1]) / 2
        # heel_srf = rs.RotateObject(heel_srf, [rot_center_x, rot_center_y, -4.0], 4.0, [1.0, 0.0, 0.0])
        # heel_srf = rs.MoveObject(heel_srf, [0.0, 2.0, 0.0])
        # bottom_srf_w_heel = rs.BooleanIntersection(bottom_srf, heel_srf)
        
        # ## tidy up objects
        # rs.DeleteObjects([ext_line, heel_curve_c, heel_curve, heel_line, bot_rad, 
                          # bot_rad2, med_line, lat_line, top_line, top_edge, bott_edge,
                          # heel_edge, front_edge, front_edge2, heel_bottom_edge,
                          # heel_bottom_srf, heel_line2, heel_curve2])
        
        
        # # =========================================================================
        
        # # create solid
        # FO = rs.JoinSurfaces([top_srf, edge_srf, bottom_srf_w_heel], 
                             # delete_input = True)
        
        
        # # =========================================================================
        
        # # trim forefoot of FO
        # corners = [[400.0, 400.0, -20.0], [-400.0, 400.0, -20.0], 
                   # [-400.0, ff_center[1] - 70.0, -20.0], 
                   # [400.0, ff_center[1] - 70.0, -20.0],
                   # [400.0, 200.0, ff_offset - 2.0], [-400.0, 200.0, ff_offset - 2.0], 
                   # [-400.0, ff_center[1] - 70.0, ff_offset - 2.0], 
                   # [400.0, ff_center[1] - 70.0, ff_offset - 2.0]]
        # box = rs.AddBox(corners)
        # FO = rs.BooleanDifference(FO, box)
        
        
        # # =========================================================================
        
        # ## Correct for side if required
        # if side[2] < 0:
             # FO = rs.MirrorObject(FO, [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        
        # # tidy up
        # rs.DeleteObjects([medial_curve, lateral_curve, center_curve, 
                          # cross_curve_heel, cross_curve_arch])
        
        
        # # =========================================================================
        
        # ## return FO
        # return FO

    
    ## Get side
    # rs.CurrentLayer("Side")
    # side = rs.ObjectsByLayer("Side")
    # side = side[0]
    # rs.UnselectAllObjects()
    # rs.SelectObject(side)
    # side = rs.GetPointCoordinates(preselect = True)
    # side = side[0]
    

    
    ## Anatomical landmarks
    # heel_medial = get_layer_point_coords("Heel Medial")
    # heel_center = get_layer_point_coords("Heel Center")
    # heel_lateral = get_layer_point_coords("Heel Lateral")
    # arch_medial = get_layer_point_coords("Arch Medial")
    # mtpj1 = get_layer_point_coords("MTPJ1")
    # mtpj5 = get_layer_point_coords("MTPJ5")
    # arch_lateral = get_layer_point_coords("Arch Lateral")
    
    # build FO
    #FO_Neutral = build_FO(side, 3.0, heel_medial, heel_center, heel_lateral, arch_lateral, arch_medial, mtpj1, mtpj5, 0, 0.65)
    
    
FreeCADGui.addCommand("Build", FOBuild())