import FreeCAD, FreeCADGui
import math

class FOBuild:
    def Activated(self):
        FreeCAD.Console.PrintMessage("")

# =============================================================================

    # Helper functions
    def dist_2_points(p1, p2):
        d = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return d
    
    def proj_point_x(p1, p2, x_coord):
        m = (p1[1] - p2[1]) / (p1[0] - p2[0])
        c = p1[1] - (m * p1[0])
        y_coord = (m * x_coord) + c
        return y_coord
    
    def proj_point_y(p1, p2, y_coord):
        m = (p1[1] - p2[1]) / (p1[0] - p2[0])
        c = p1[1] - (m * p1[0])
        x_coord = (y_coord - c) / m
        return x_coord
    
    def point_on_line(x, y, offset):
        d = math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)
        t = offset / d
        xt = ((1 - t) * x[0]) + (t * y[0])
        yt = ((1 - t) * x[1]) + (t * y[1])
        xx = [xt, yt, 0.0]
        return xx
    
    def rot_point_coords(pt, center, angle, axis):
        point = rs.AddPoint(pt)
        point_rot = rs.RotateObject(point, center, angle, axis)
        rs.UnselectAllObjects()
        rs.SelectObject(point_rot)
        point_coords = rs.GetPointCoordinates(preselect = True)
        rs.DeleteObjects([point, point_rot])
        return point_coords[0]
    
    def get_layer_point_coords(layer):
        layer_bits = rs.ObjectsByLayer(layer)
        point = layer_bits[0]
        rs.UnselectAllObjects()
        rs.SelectObject(point)
        point_coords = rs.GetPointCoordinates(preselect = True)
        return point_coords[0]
    
    def build_FO(side, thickness, heel_medial, heel_center, heel_lateral,
                 arch_lateral, arch_medial, mtpj1, mtpj5, posting, heel_offset):
        
        ## forefoot offset
        ff_offset = -5.0
        
        ## adjust for side if required
        if side[2] < 0:
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
            heel_medial = rot_point_coords(heel_medial, heel_center, posting, 
                                           [0.0, 1.0, 0.0])
            heel_lateral = rot_point_coords(heel_lateral, heel_center, posting, 
                                            [0.0, 1.0, 0.0])
            arch_medial = rot_point_coords(arch_medial, heel_center, posting, 
                                           [0.0, 1.0, 0.0])
            arch_lateral = rot_point_coords(arch_lateral, heel_center, posting, 
                                            [0.0, 1.0, 0.0])
        
        
        # =========================================================================
        
        # forefoot width adjustment
        ff_d = dist_2_points(mtpj1, mtpj5)
        
        if (ff_d > 90):
            x = (ff_d - 85) / 2
            mtpj1 = [mtpj1[0] - x, mtpj1[1], mtpj1[2]]
            mtpj5 = [mtpj5[0] + x, mtpj5[1], mtpj5[2]]
        
        
        # =========================================================================
        
        # calculated landmarks
        ## adjusted heel landmarks
        heel_center_med_offset = ((heel_medial[0] - heel_center[0]) * heel_offset)
        heel_center_medial = [heel_center[0] + heel_center_med_offset,
                              heel_center[1] + 5, heel_center[2]]
        if posting != 0:
            heel_center_medial = rot_point_coords(heel_center_medial, heel_center, 
                                                  posting, [0.0, 1.0, 0.0])
        heel_center_lat_offset = -1 * ((heel_lateral[0] - heel_center[0]) * heel_offset)
        heel_center_lateral = [heel_center[0] - heel_center_lat_offset, 
                               heel_center[1] + 5, heel_center[2]]
        if posting != 0:
            heel_center_lateral = rot_point_coords(heel_center_lateral, heel_center, 
                                                   posting, [0.0, 1.0, 0.0])
        
        # adjusted mtpj landmarks
        mtpj1_adj = [mtpj1[0] - 2.0, mtpj1[1] - 10.0, ff_offset]
        mtpj5_adj = [mtpj5[0] + 2.0, mtpj5[1] - 10.0, ff_offset]
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
        mtpj1_prox1 = [mtpj1_prox1 - 0.4, mtpj1_adj[1] - 2, ff_offset]
        mtpj1_prox2 = proj_point_y(mtpj1_adj, [arch_medial_adj[0], arch_medial_adj[1], ff_offset], 
                                   mtpj1_adj[1] - 4)
        mtpj1_prox2 = [mtpj1_prox2, mtpj1_adj[1] - 4, ff_offset + 0.5]
        mtpj1_lateral1 = proj_point_x(ff_center, mtpj1_adj, mtpj1_adj[0] - 2)
        mtpj1_lateral1 = [mtpj1_adj[0] - 2, mtpj1_lateral1 -0.4, ff_offset]
        mtpj1_lateral2 = proj_point_x(ff_center, mtpj1_adj, mtpj1_adj[0] - 4)
        mtpj1_lateral2 = [mtpj1_adj[0] - 4, mtpj1_lateral2, ff_offset]
        mtpj5_prox1 = proj_point_y(mtpj5_adj, [arch_lateral_adj[0], arch_lateral_adj[1], ff_offset], 
                                   mtpj5_adj[1] - 2)
        mtpj5_prox1 = [mtpj5_prox1 + 0.4, mtpj5_adj[1] - 2, ff_offset]
        mtpj5_prox2 = proj_point_y(mtpj5_adj, [arch_lateral_adj[0], arch_lateral_adj[1], ff_offset], 
                                   mtpj5_adj[1] - 4)
        mtpj5_prox2 = [mtpj5_prox2, mtpj5_adj[1] - 4, ff_offset + 0.5]
        mtpj5_lateral1 = proj_point_x(ff_center, mtpj5_adj, mtpj5_adj[0] + 2)
        mtpj5_lateral1 = [mtpj5_adj[0] + 2, mtpj5_lateral1 -0.4, ff_offset]
        mtpj5_lateral2 = proj_point_x(ff_center, mtpj5_adj, mtpj5_adj[0] + 4)
        mtpj5_lateral2 = [mtpj5_adj[0] + 4, mtpj5_lateral2, ff_offset]
        arch_mid = [(arch_medial[0] + arch_lateral[0]) / 2,
                    (arch_medial[1] + arch_lateral[1]) / 2, 5.0]
        
        
        # =========================================================================
        
        # make curves
        medial_curve = rs.AddInterpCurve([heel_center, heel_center_medial,
                                          heel_medial, arch_medial_adj, 
                                          mtpj1_prox2, mtpj1_prox1, mtpj1_lateral1,
                                          mtpj1_lateral2,
                                          ff_center], degree = 3, knotstyle = 2)
        lateral_curve = rs.AddInterpCurve([heel_center, heel_center_lateral,
                                           heel_lateral, arch_lateral_adj, 
                                           mtpj5_prox2, mtpj5_prox1, mtpj5_lateral1,
                                           mtpj5_lateral2,
                                           ff_center], degree = 3, knotstyle = 2)
        center_curve = rs.AddInterpCurve([heel_center, 
                                          [(heel_medial[0] + heel_lateral[0]) / 2, 
                                          (heel_medial[1] + heel_lateral[1]) / 2, 0.0],
                                          arch_mid, ff_center])
        cross_curve_heel = rs.AddInterpCurve([heel_medial, 
                                              [(heel_medial[0] + heel_lateral[0]) / 2, 
                                               (heel_medial[1] + heel_lateral[1]) / 2, 2.0], 
                                              heel_lateral])
        cross_curve_arch = rs.AddInterpCurve([arch_medial_adj, arch_mid, 
                                              arch_lateral_adj])
        
        
        # =========================================================================
        
        # make top surface
        top_srf = rs.AddNetworkSrf([medial_curve, lateral_curve, center_curve, 
                                    cross_curve_heel, cross_curve_arch])
        
        
        # =========================================================================
        
        # make bottom surface 
        bottom_srf = rs.CopyObject(top_srf)
        bottom_srf = rs.MoveObject(bottom_srf, [0.0, 0.0, -3.0])
        
        
        # =========================================================================
        
        # make edges
        edges = rs.DuplicateSurfaceBorder(top_srf)
        ext_line = rs.AddLine([0.0, 0.0, 0.0], [0.0, 0.0, -3.0])
        edge_srf = rs.ExtrudeCurve(edges, ext_line)
        rs.DeleteObjects([edges, ext_line])
        
        
        # =========================================================================
        
        # add heel 
        ## heel outline
        heel_curve = rs.AddInterpCurve([[heel_medial[0] - 3.0, 
                                         heel_medial[1] + 10.0, 0.0],
                                        [heel_medial[0] - 3.0, 
                                         heel_medial[1] + 1.0, 0.0],
                                        [heel_medial[0] - 3.0, heel_medial[1], 0.0], 
                                        [heel_center_medial[0] - 3.0, 
                                         heel_center_medial[1] + 3.0, 0.0],
                                        [heel_center[0], heel_center[1] + 3.0, 0.0],
                                        [heel_center_lateral[0] + 3.0, 
                                         heel_center_lateral[1] + 4.0, 0.0],
                                        [heel_lateral[0] + 3.0, heel_lateral[1], 0.0],
                                        [heel_lateral[0] + 3.0, 
                                         heel_lateral[1] + 1.0, 0.0],
                                        [heel_lateral[0] + 3.0, 
                                         heel_lateral[1] + 10.0, 0.0]],
                                        knotstyle = 2)
        heel_curve2 = rs.OffsetCurve(heel_curve, [0, 0, 0], 4.0)
        heel_line = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 0.0], 
                               [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 0.0])
        heel_line2 = rs.AddLine([heel_medial[0] - 7.0, heel_medial[1] + 10.0, 0.0], 
                                [heel_lateral[0] + 7.0, heel_lateral[1] + 10.0, 0.0])
        heel_curve_c = rs.JoinCurves([heel_curve, heel_line])
        
        ## heel bottom surface
        heel_bottom_srf = rs.AddEdgeSrf([heel_curve2, heel_line2])
        heel_bottom_srf = rs.MoveObject(heel_bottom_srf, [0.0, 0.0, -4.0])
        
        ## heel bottom curve
        bot_rad = rs.AddArc(rs.WorldZXPlane(), 4.0, 90.0)
        bot_rad = rs.RotateObject(bot_rad, [0, 0, 0], 90, [0, 1, 0])
        bot_rad = rs.MoveObject(bot_rad, [heel_medial[0] - 7.0, 
                                          heel_medial[1] + 10.0, 0.0])
        heel_bottom_edge = rs.AddSweep1(heel_curve, [bot_rad])
        
        ## heel sides
        ext_line = rs.AddLine([0.0, 0.0, 0.0], [0.0, 0.0, 30.0])
        heel_edge = rs.ExtrudeCurve(heel_curve, ext_line)
        
        ## heel front1
        bot_rad2 = rs.AddArc(rs.WorldZXPlane(), 4.0, 90.0)
        bot_rad2 = rs.RotateObject(bot_rad2, [0, 0, 0], 180, [0, 1, 0])
        bot_rad2 = rs.MoveObject(bot_rad2, [heel_lateral[0] + 7.0, 
                                            heel_lateral[1] + 10.0, 0.0])
        top_edge = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 0.0],
                              [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 0.0])
        bott_edge = rs.AddLine([heel_medial[0] - 5.0, heel_medial[1] + 10.0, -2.0], 
                               [heel_lateral[0] + 5.0, heel_lateral[1] + 10.0, -2.0])
        front_edge = rs.AddEdgeSrf([bot_rad, bot_rad2, top_edge, bott_edge])
        
        ## heel front 2
        med_line = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 0.0], 
                              [heel_medial[0] - 3.0, heel_medial[1] + 10.0, 30.0])
        lat_line = rs.AddLine([heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 0.0],
                              [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 30.0])
        top_line = rs.AddLine([heel_medial[0] - 3.0, heel_medial[1] + 10.0, 30.0],
                              [heel_lateral[0] + 3.0, heel_lateral[1] + 10.0, 30.0])
        front_edge2 = rs.AddEdgeSrf([med_line, top_line, lat_line, top_edge])
        
        ## heel top surface
        heel_srf = rs.JoinSurfaces([heel_bottom_srf, heel_bottom_edge, heel_edge, 
                                    front_edge, front_edge2])
        heel_srf = rs.MoveObject(heel_srf, [0.0, 0.0, -2.0])
        rot_center_x = (heel_lateral[0] + heel_medial[0]) / 2
        rot_center_y = (heel_lateral[1] + heel_medial[1]) / 2
        heel_srf = rs.RotateObject(heel_srf, [rot_center_x, rot_center_y, -4.0], 4.0, [1.0, 0.0, 0.0])
        heel_srf = rs.MoveObject(heel_srf, [0.0, 2.0, 0.0])
        bottom_srf_w_heel = rs.BooleanIntersection(bottom_srf, heel_srf)
        
        ## tidy up objects
        rs.DeleteObjects([ext_line, heel_curve_c, heel_curve, heel_line, bot_rad, 
                          bot_rad2, med_line, lat_line, top_line, top_edge, bott_edge,
                          heel_edge, front_edge, front_edge2, heel_bottom_edge,
                          heel_bottom_srf, heel_line2, heel_curve2])
        
        
        # =========================================================================
        
        # create solid
        FO = rs.JoinSurfaces([top_srf, edge_srf, bottom_srf_w_heel], 
                             delete_input = True)
        
        
        # =========================================================================
        
        # trim forefoot of FO
        corners = [[400.0, 400.0, -20.0], [-400.0, 400.0, -20.0], 
                   [-400.0, ff_center[1] - 70.0, -20.0], 
                   [400.0, ff_center[1] - 70.0, -20.0],
                   [400.0, 200.0, ff_offset - 2.0], [-400.0, 200.0, ff_offset - 2.0], 
                   [-400.0, ff_center[1] - 70.0, ff_offset - 2.0], 
                   [400.0, ff_center[1] - 70.0, ff_offset - 2.0]]
        box = rs.AddBox(corners)
        FO = rs.BooleanDifference(FO, box)
        
        
        # =========================================================================
        
        ## Correct for side if required
        if side[2] < 0:
             FO = rs.MirrorObject(FO, [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        
        # tidy up
        rs.DeleteObjects([medial_curve, lateral_curve, center_curve, 
                          cross_curve_heel, cross_curve_arch])
        
        
        # =========================================================================
        
        ## return FO
        return FO
    
    
    # =============================================================================
    
    # Add Layers
    rs.AddLayer("Neutral")
    rs.AddLayer("Medial 5")
    rs.AddLayer("Medial 10")
    rs.AddLayer("Lateral 5")
    
    
    # =============================================================================
    
    ## Get side
    rs.CurrentLayer("Side")
    side = rs.ObjectsByLayer("Side")
    side = side[0]
    rs.UnselectAllObjects()
    rs.SelectObject(side)
    side = rs.GetPointCoordinates(preselect = True)
    side = side[0]
    
    
    # =============================================================================
    ### Neutral FO ###
    # =============================================================================
    
    # change layer
    rs.CurrentLayer("Neutral")
    
    ## Anatomical landmarks
    heel_medial = get_layer_point_coords("Heel Medial")
    heel_center = get_layer_point_coords("Heel Center")
    heel_lateral = get_layer_point_coords("Heel Lateral")
    arch_medial = get_layer_point_coords("Arch Medial")
    mtpj1 = get_layer_point_coords("MTPJ1")
    mtpj5 = get_layer_point_coords("MTPJ5")
    arch_lateral = get_layer_point_coords("Arch Lateral")
    
    # build FO
    FO_Neutral = build_FO(side, 3.0, heel_medial, heel_center, heel_lateral,
                          arch_lateral, arch_medial, mtpj1, mtpj5, 0, 0.65)