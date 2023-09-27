# Title: ORTHOTIC DESIGN  
# Part: 2
# Description: POSITION
# Version: 0.3
# Last edited: 2016_04_02
# Author: Scott Telfer


# =============================================================================

## TO DO
# Instead of moving to top view initially, use persp but with view facing in same direction as top
# For positions, take user through each view, stating with front, and make scan solid view for easier positioning 
# Make sphere appear to mark landmarks (different colours)
# make function for getting coordinates from points


# =============================================================================

## Import Modules
import rhinoscriptsyntax as rs
import math


# =============================================================================

# helper functions
def point_coords(pt):
    rs.UnselectAllObjects()
    rs.SelectObject(pt)
    point_coords = rs.GetPointCoordinates(preselect = True)
    return point_coords[0]

def cross(v1, v2):
    cx = [v1[1] * v2[2] - v1[2] * v2[1],
          v1[2] * v2[0] - v1[0] * v2[2],
          v1[0] * v2[1] - v1[1] * v2[0]]
    return cx

def dot(v1, v2):
    dp = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    return dp


# =============================================================================

## Identify scan
sca = rs.ObjectsByLayer("Position scan")
scan = sca[0]


# =============================================================================

## Identify points for positioning
# Make Position scan layer current
rs.CurrentLayer("Position scan")

# Get coordinates of heel
heel_pt = rs.GetPointOnMesh(scan, "Identify lowest point of heel on the plantar surface")

# Get coordinates of metatarsal head 1
MTH1_pt = rs.GetPointOnMesh(scan, "Identify MTH1 on the plantar surface")

# Get coordinates of metatarsal head 5
MTH5_pt = rs.GetPointOnMesh(scan, "Identify MTH5 on the plantar surface")

# Get coordinates of highest point on arch
arch_pt = rs.GetPointOnMesh(scan, "Identify point on arch")


# =============================================================================

# To reduce build time, we'll turn off the redraw option
rs.EnableRedraw(False)


# =============================================================================

## Make plane to align to
rs.CurrentLayer("Reference plane")
rect = rs.AddRectangle(rs.WorldXYPlane(), 200.0, 400.0)
rs.MoveObject(rect, (-100 , -200, 0))
rs.AddPlanarSrf(rect)


# =============================================================================

## Virtual landmarks
# Make Position scan layer current
rs.CurrentLayer("Position scan")

# Determine forefoot centre point
ff_mid = [(MTH1_pt[0] + MTH5_pt[0]) / 2,
(MTH1_pt[1] + MTH5_pt[1]) / 2,
(MTH1_pt[2] + MTH5_pt[2]) / 2]

# Determine foot centre point
foot_mid = [(ff_mid[0] + heel_pt[0]) / 2,
(ff_mid[1] + heel_pt[1]) / 2, 
(ff_mid[2] + heel_pt[2]) / 2]

# Add point objects
heel_pt = rs.AddPoint(heel_pt)
MTH1_pt = rs.AddPoint(MTH1_pt)
MTH5_pt = rs.AddPoint(MTH5_pt)
arch_pt = rs.AddPoint(arch_pt)
ff_mid = rs.AddPoint(ff_mid)


# =============================================================================

## Translate scan and landmarks to origin
# Translate scan to origin
foot_mid = [x * -1 for x in foot_mid]
scan = rs.MoveObject(scan, foot_mid)

# Move points
heel_pt = rs.MoveObject(heel_pt, foot_mid)
MTH1_pt = rs.MoveObject(MTH1_pt, foot_mid)
MTH5_pt = rs.MoveObject(MTH5_pt, foot_mid)
arch_pt = rs.MoveObject(arch_pt, foot_mid)
ff_mid = rs.MoveObject(ff_mid, foot_mid)


# =============================================================================

## Rotate scan to reference plane
# Get new point coords
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_mid_coords = point_coords(ff_mid)

# Find foot plane normal
a = (MTH1_pt_coords[0] - heel_pt_coords[0], 
    MTH1_pt_coords[1] - heel_pt_coords[1], 
    MTH1_pt_coords[2] - heel_pt_coords[2])
b = (MTH5_pt_coords[0] - heel_pt_coords[0], 
    MTH5_pt_coords[1] - heel_pt_coords[1], 
    MTH5_pt_coords[2] - heel_pt_coords[2]) 
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

# Rotate scan
scan = rs.RotateObject(scan, (0, 0, 0), rotation_angle = theta,
    axis = rot_axis)

# Rotate landmarks
heel_pt = rs.RotateObject(heel_pt, (0, 0, 0), 
    rotation_angle = theta, axis = rot_axis)
MTH1_pt = rs.RotateObject(MTH1_pt, (0, 0, 0), 
    rotation_angle = theta, axis = rot_axis)
MTH5_pt = rs.RotateObject(MTH5_pt, (0, 0, 0), 
    rotation_angle = theta, axis = rot_axis)
arch_pt = rs.RotateObject(arch_pt, (0, 0, 0), 
rotation_angle = theta, axis = rot_axis)
ff_mid = rs.RotateObject(ff_mid, (0, 0, 0), 
    rotation_angle = theta, axis = rot_axis)


# ==============================================================

# Get rotated point coordinates
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_mid_coords = point_coords(ff_mid)

# Is scan upside down?
if arch_pt_coords[2] < 0:
    scan = rs.RotateObject(scan, (0, 0, 0), 180, (0, 1, 0))
    heel_pt = rs.RotateObject(heel_pt, (0, 0, 0), 180, (0, 1, 0))
    MTH1_pt = rs.RotateObject(MTH1_pt, (0, 0, 0), 180, (0, 1, 0))
    MTH5_pt = rs.RotateObject(MTH5_pt, (0, 0, 0), 180, (0, 1, 0))
    arch_pt = rs.RotateObject(arch_pt, (0, 0, 0), 180, (0, 1, 0))
    ff_mid = rs.RotateObject(ff_mid, (0, 0, 0), 180, (0, 1, 0))


# ================================================================

## Rotate scan to align foot axis with y
# Get rotated point coordinates
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_mid_coords = point_coords(ff_mid)

# If anterior/posterior needs to be reversed 
if ff_mid_coords[1] < 0:
    scan = rs.RotateObject(scan, (0, 0, 0), 180, (0, 0, 1))
    heel_pt = rs.RotateObject(heel_pt, (0, 0, 0), 180, (0, 0, 1))
    MTH1_pt = rs.RotateObject(MTH1_pt, (0, 0, 0), 180, (0, 0, 1))
    MTH5_pt = rs.RotateObject(MTH5_pt, (0, 0, 0), 180, (0, 0, 1))
    arch_pt = rs.RotateObject(arch_pt, (0, 0, 0), 180, (0, 0, 1))
    ff_mid = rs.RotateObject(ff_mid, (0, 0, 0), 180, (0, 0, 1))

# Get rotated point coordinates
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_mid_coords = point_coords(ff_mid)

if ff_mid_coords[0] < 0:
    scan = rs.RotateObject(scan, (0, 0, 0), -90, (0, 0, 1))
    heel_pt = rs.RotateObject(heel_pt, (0, 0, 0), -90, (0, 0, 1))
    MTH1_pt = rs.RotateObject(MTH1_pt, (0, 0, 0), -90, (0, 0, 1))
    MTH5_pt = rs.RotateObject(MTH5_pt, (0, 0, 0), -90, (0, 0, 1))
    arch_pt = rs.RotateObject(arch_pt, (0, 0, 0), -90, (0, 0, 1))
    ff_mid = rs.RotateObject(ff_mid, (0, 0, 0), -90, (0, 0, 1))

# Get rotated point coordinates
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_mid_coords = point_coords(ff_mid)
	
# Find angle between foot axis and y axis
theta = math.degrees(math.atan(ff_mid_coords[0] / ff_mid_coords[1]))

# Rotate objects
scan = rs.RotateObject(scan, (0, 0, 0), theta, (0, 0, 1))
heel_pt = rs.RotateObject(heel_pt, (0, 0, 0), theta, (0, 0, 1))
MTH1_pt = rs.RotateObject(MTH1_pt, (0, 0, 0), theta, (0, 0, 1))
MTH5_pt = rs.RotateObject(MTH5_pt, (0, 0, 0), theta, (0, 0, 1))
arch_pt = rs.RotateObject(arch_pt, (0, 0, 0), theta, (0, 0, 1))
ff_mid = rs.RotateObject(ff_mid, (0, 0, 0), theta, (0, 0, 1))

# Get rotated point coordinates
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_mid_coords = point_coords(ff_mid)


# =============================================================================

## Reposition to align with 2nd
# Find side
rs.CurrentLayer("Side")
if MTH1_pt_coords[0] > MTH5_pt_coords[0]:
    side = 1
    rs.AddPoint(0, 0, 5)
else:
    side = 2
    rs.AddPoint(0, 0, -5)
rs.CurrentLayer("Position scan")
rs.LayerVisible("Side", False)

# Second MTH
if side == 2:
    ff_2 = ((MTH1_pt_coords[0] + (0.4 *(MTH5_pt_coords[0] - MTH1_pt_coords[0]))),
        (MTH1_pt_coords[1] - (0.4 * (MTH1_pt_coords[1] - MTH5_pt_coords[1]))), 0)
else:
    ff_2 = ((MTH5_pt_coords[0] + (0.6 *(MTH1_pt_coords[0] - MTH5_pt_coords[0]))),
        (MTH1_pt_coords[1] - (0.4 * (MTH1_pt_coords[1] - MTH5_pt_coords[1]))), 0)

# Determine new foot centre point
foot_mid2 = ((ff_2[0] + heel_pt_coords[0]) / 2,
             (ff_2[1] + heel_pt_coords[1]) / 2, 
             (ff_2[2] + heel_pt_coords[2]) / 2)
ff_2 = rs.AddPoint(ff_2)

# Translate to new origin
foot_mid2 = [x * -1 for x in foot_mid2]
scan = rs.MoveObject(scan, foot_mid2)
heel_pt = rs.MoveObject(heel_pt, foot_mid2)
MTH1_pt = rs.MoveObject(MTH1_pt, foot_mid2)
MTH5_pt = rs.MoveObject(MTH5_pt, foot_mid2)
arch_pt = rs.MoveObject(arch_pt, foot_mid2)
ff_2 = rs.MoveObject(ff_2, foot_mid2)

# Get translated point coordinates
heel_pt_coords = point_coords(heel_pt)
MTH1_pt_coords = point_coords(MTH1_pt)
MTH5_pt_coords = point_coords(MTH5_pt)
arch_pt_coords = point_coords(arch_pt)
ff_2_coords = point_coords(ff_2)

# Find angle between foot axis and y axis
theta = math.degrees(math.atan(ff_2_coords[0] / ff_2_coords[1]))

# Rotate objects
scan = rs.RotateObject(scan, (0, 0, 0), theta, (0, 0, 1))


# ==================================================================

## Return to all views and zoom extent on all
viewmax = rs.IsViewMaximized(view = "Top")
if viewmax:
    rs.MaximizeRestoreView(view = "Top")
viewmax = rs.IsViewMaximized(view = "Right")
if viewmax:
    rs.MaximizeRestoreView(view = "Right")
viewmax = rs.IsViewMaximized(view = "Front")
if viewmax:
    rs.MaximizeRestoreView(view = "Front")
viewmax = rs.IsViewMaximized(view = "Perspective")
if viewmax:
    rs.MaximizeRestoreView(view = "Perspective")
rs.ZoomExtents("Top")
rs.ZoomExtents("Right")
rs.ZoomExtents("Front")
rs.ZoomExtents("Perspective")

# Delete landmark points
rs.DeleteObjects([heel_pt, MTH1_pt, MTH5_pt, arch_pt, ff_2, ff_mid])

# Enable redraw
rs.EnableRedraw(True)


# ==================================================================

# Request user to make further position adjustments as required
rs.MessageBox("Make further position adjustments to align scan with plane")


# ==================================================================
