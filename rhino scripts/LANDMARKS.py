# Title: ORTHOTIC DESIGN  
# Part: 3
# Description: LANDMARKS
# Version: 2.0
# Last edited: 2020_03_06
# Author: Scott Telfer


# =============================================================================

## TO DO 
# Add coloured spheres to mark landmarks that have been identified 
#


# =============================================================================

## Modules
import rhinoscriptsyntax as rs
import math


# =============================================================================

## Set up layers
rs.LayerVisible("Reference plane", False)


# =============================================================================

## Identify foot scan
sca = rs.ObjectsByLayer("Position scan")
scan = sca[0]
rs.UnselectAllObjects()


# =============================================================================

## Identify points to generate trim curves
# Go to and maximise side view
persp_max = rs.IsViewMaximized("Perspective")
if persp_max:
    rs.ZoomExtents()
    print "Perspective view maximised"
else:
    rs.MaximizeRestoreView(view = "Perspective")
    rs.ZoomExtents()

# Select point on lateral side of heel
heel_lateral = rs.GetPointOnMesh(scan, "Identify point on lateral side of heel")

# Select point on center posterior of heel
heel_center = rs.GetPointOnMesh(scan, "Identify point on posterior of heel")

# Select point on medial side of heel
heel_medial = rs.GetPointOnMesh(scan, "Identify point on medial side of heel")

# Select point on medial side of heel
arch_lateral = rs.GetPointOnMesh(scan, "Identify highest point on lateral arch")

# Select point on arch
arch_medial = rs.GetPointOnMesh(scan, "Identify highest point on medial arch")

# Select point on medial side of distal metatarsal head 1
mtpj1 = rs.GetPointOnMesh(scan, "Identify the medial side of the distal MTH1")

# Select point on lateral side of distal metatarsal head 5
mtpj5 = rs.GetPointOnMesh(scan, "Identify the lateral side of the distal MTH5")


# =============================================================================

## Add points to assigned layers
rs.CurrentLayer("Heel Medial")
objs = rs.ObjectsByLayer("Heel Medial")
rs.DeleteObjects(objs)
rs.AddPoint(heel_medial)
rs.CurrentLayer("Heel Lateral")
objs = rs.ObjectsByLayer("Heel Lateral")
rs.DeleteObjects(objs)
rs.AddPoint(heel_lateral)
rs.CurrentLayer("Heel Center")
objs = rs.ObjectsByLayer("Heel Center")
rs.DeleteObjects(objs)
rs.AddPoint(heel_center)
rs.CurrentLayer("Arch Medial")
objs = rs.ObjectsByLayer("Arch Medial")
rs.DeleteObjects(objs)
rs.AddPoint(arch_medial)
rs.CurrentLayer("Arch Lateral")
objs = rs.ObjectsByLayer("Arch Lateral")
rs.DeleteObjects(objs)
rs.AddPoint(arch_lateral)
rs.CurrentLayer("MTPJ1")
objs = rs.ObjectsByLayer("MTPJ1")
rs.DeleteObjects(objs)
rs.AddPoint(mtpj1)
rs.CurrentLayer("MTPJ5")
objs = rs.ObjectsByLayer("MTPJ5")
rs.DeleteObjects(objs)
rs.AddPoint(mtpj5)


# ================================================================== 

## Final adjustments to view medial and lateral trimlines
# Make perspective view
rs.MaximizeRestoreView("Perspective")
rs.ZoomExtents()
rs.ViewDisplayMode("Perspective", "Shaded")


# ==================================================================