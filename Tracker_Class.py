import math

import traceback
import sys
import re

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from FreeCAD import Units as U

import pivy.coin as coin
from functions import *
from todo import ToDo

class Tracker:
    """A generic Draft Tracker, to be used by other specific trackers."""

    def __init__(self, dotted=False, scolor=(0.0,0.0,0.0), swidth=2,
                 children=[], ontop=False, name=None):
        global Part, DraftGeomUtils
        import Part
        import DraftGeomUtils
        self.ontop = ontop
        self.color = coin.SoBaseColor()
        self.color.rgb = scolor
        drawstyle = coin.SoDrawStyle()
        if swidth:
            drawstyle.lineWidth = swidth
        if dotted:
            drawstyle.style = coin.SoDrawStyle.LINES
            drawstyle.lineWeight = 3
            drawstyle.linePattern = 0x0f0f  # 0xaa
        node = coin.SoSeparator()
        for c in [drawstyle, self.color] + children:
            node.addChild(c)
        self.switch = coin.SoSwitch()  # this is the on/off switch
        if name:
            self.switch.setName(name)
        self.switch.addChild(node)
        self.switch.whichChild = -1
        self.Visible = False
        ToDo.delay(self._insertSwitch, self.switch)

    def finalize(self):
        """Finish the command by removing the switch.
        Also called by ghostTracker.remove.
        """
        ToDo.delay(self._removeSwitch, self.switch)
        self.switch = None

    def _insertSwitch(self, switch):
        """Insert self.switch into the scene graph.

        Must not be called
        from an event handler (or other scene graph traversal).
        """
        sg = get_3d_view().getSceneGraph()
        if self.ontop:
            sg.insertChild(switch, 0)
        else:
            sg.addChild(switch)

    def _removeSwitch(self, switch):
        """Remove self.switch from the scene graph.

        As with _insertSwitch,
        must not be called during scene graph traversal).
        """
        sg = get_3d_view().getSceneGraph()
        if sg.findChild(switch) >= 0:
            sg.removeChild(switch)

    def on(self):
        """Set the visibility to True."""
        self.switch.whichChild = 0
        self.Visible = True

    def off(self):
        """Set the visibility to False."""
        self.switch.whichChild = -1
        self.Visible = False

    def lowerTracker(self):
        """Lower the tracker to the bottom of the scenegraph.

        So it doesn't obscure the other objects.
        """
        if self.switch:
            sg = get_3d_view().getSceneGraph()
            sg.removeChild(self.switch)
            sg.addChild(self.switch)

    def raiseTracker(self):
        """Raise the tracker to the top of the scenegraph.

        So it obscures the other objects.
        """
        if self.switch:
            sg = get_3d_view().getSceneGraph()
            sg.removeChild(self.switch)
            sg.insertChild(self.switch, 0)

class PlaneTracker(Tracker):
    """A working plane tracker."""

    def __init__(self, u, v):
        # getting screen distance
        p1 = get_3d_view().getPoint((100, 100))
        p2 = get_3d_view().getPoint((110, 100))
        bl = (p2.sub(p1)).Length * (8/2.0)
        pick = coin.SoPickStyle()
        pick.style.setValue(coin.SoPickStyle.UNPICKABLE)
        self.trans = coin.SoTransform()
        self.u = u
        self.v = v
        self.trans.translation.setValue([0, 0, 0])
        m1 = coin.SoMaterial()
        m1.transparency.setValue(0.8)
        m1.diffuseColor.setValue([0.4, 0.4, 0.6])
        c1 = coin.SoCoordinate3()
        c1.point.setValues([[-bl, -bl, 0],
                            [bl, -bl, 0],
                            [bl, bl, 0],
                            [-bl, bl, 0]])
        f = coin.SoIndexedFaceSet()
        f.coordIndex.setValues([0, 1, 2, 3])
        m2 = coin.SoMaterial()
        m2.transparency.setValue(0)
        m2.diffuseColor.setValue([0.2, 0.2, 0.3])
        c2 = coin.SoCoordinate3()
        c2.point.setValues([[0, bl, 0], [0, 0, 0],
                            [bl, 0, 0], [-0.05*bl, 0.95*bl, 0],
                            [0, bl, 0], [0.05*bl, 0.95*bl, 0],
                            [0.95*bl, 0.05*bl, 0], [bl, 0, 0],
                            [0.95*bl, -0.05*bl, 0]])
        l = coin.SoLineSet()
        l.numVertices.setValues([3, 3, 3])
        s = coin.SoSeparator()
        s.addChild(pick)
        s.addChild(self.trans)
        s.addChild(m1)
        s.addChild(c1)
        s.addChild(f)
        s.addChild(m2)
        s.addChild(c2)
        s.addChild(l)
        super().__init__(children=[s], name="planeTracker")
    
    def getPlacement(self, rotated=False):
        """Return the placement of the plane.

        Parameters
        ----------
        rotated : bool, optional
            It defaults to `False`. If it is `True`, it switches `axis`
            with `-v` to produce a rotated placement.

        Returns
        -------
        Base::Placement
            A placement, comprised of a `Base` (`Base::Vector3`),
            and a `Rotation` (`Base::Rotation`).
        """
        if rotated:
            m = self.getPlaneRotation(self.u, self.axis)
        else:
            m = self.getPlaneRotation(self.u, self.v)
        m.move(self.position)
        p = App.Placement(m)
        return p

    def set(self, pos=None):
        """Set the translation to the position."""
        if pos:
            Q = self.getRotation().Rotation.Q
        else:
            plm = self.getPlacement()
            Q = plm.Rotation.Q
            pos = plm.Base
        self.trans.translation.setValue([pos.x, pos.y, pos.z])
        self.trans.rotation.setValue([Q[0], Q[1], Q[2], Q[3]])
        self.on()
    
    def getRotation(self):
        """Return a placement describing the plane orientation only.

        If `FreeCAD.GuiUp` is `True`, that is, if the graphical interface
        is loaded, it will test if the active object is an `Arch` container
        and will calculate the placement accordingly.

        Returns
        -------
        Base::Placement
            A placement, comprised of a `Base` (`Base::Vector3`),
            and a `Rotation` (`Base::Rotation`).
        """
        m = self.getPlaneRotation(self.u, self.v)
        p = App.Placement(m)
        # Arch active container
        if App.GuiUp:
            if Gui.ActiveDocument:
                view = Gui.ActiveDocument.ActiveView
                if view and hasattr(view,"getActiveOject"):
                    a = view.getActiveObject("Arch")
                    if a:
                        p = a.Placement.inverse().multiply(p)
        return p
    
    def getPlaneRotation(self, uvec, vvec, _ = None):
        """Return a rotation matrix defining the (u,v,w) coordinate system.

        The rotation matrix uses the elements from each vector.
        `v` is adjusted to be perpendicular to `u`
        ::
                (u.x  v.x  w.x  0  )
            R = (u.y  v.y  w.y  0  )
                (u.z  v.z  w.z  0  )
                (0    0    0    1.0)

        Parameters
        ----------
        u : Base::Vector3
            The first vector.
        v : Base::Vector3
            Hint for the second vector.
        _ : Ignored. For backwards compatibility

        Returns
        -------
        Base::Matrix4D
            The new rotation matrix defining a new coordinate system,
            or `None` if `u` or `v` is `None` or
            if `u` and `v` are parallel.
        """
        if (not uvec) or (not vvec):
            return None
        typecheck([(uvec, Vector), (vvec, Vector)], "getPlaneRotation")
        u = Vector(uvec)
        u.normalize()
        w = uvec.cross(vvec)
        if not w.Length:
            return None
        w.normalize()
        vvec = w.cross(uvec)

        mvec = App.Matrix(uvec.x, vvec.x, w.x, 0,
                           uvec.y, vvec.y, w.y, 0,
                           uvec.z, vvec.z, w.z, 0,
                           0.0, 0.0, 0.0, 1.0)
        return mvec

class ghostTracker(Tracker):
    """A Ghost tracker, that allows to copy whole object representations.

    You can pass it an object or a list of objects, or a shape.
    """
    
    def __init__(self, sel, dotted=False, scolor=(1.0,1.0,1.0), swidth=None):
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
        self.children = [self.trans]
        rootsep = coin.SoSeparator()
        if not isinstance(sel, list):
            sel = [sel]
        for obj in sel:
            import Part
            if not isinstance(obj, Part.Vertex):
                rootsep.addChild(self.getNode(obj))
            else:
                self.coords = coin.SoCoordinate3()
                self.coords.point.setValue((obj.X, obj.Y, obj.Z))
                color = coin.SoBaseColor()
                self.marker = coin.SoMarkerSet()  # this is the marker symbol
                self.marker.markerIndex = Gui.getMarkerIndex("quad", 9)
                node = coin.SoAnnotation()
                selnode = coin.SoSeparator()
                selnode.addChild(self.coords)
                selnode.addChild(color)
                selnode.addChild(self.marker)
                node.addChild(selnode)
                rootsep.addChild(node)
        self.children.append(rootsep)
        super().__init__(dotted, scolor, swidth,
                         children=self.children, name="ghostTracker")

    def remove(self):
        """Remove the ghost when switching to and from subelement mode."""
        if self.switch:
            self.finalize()

    def move(self, delta):
        """Move the ghost to a given position.

        Relative from its start position.
        """
        self.trans.translation.setValue([delta.x, delta.y, delta.z])

    def rotate(self, axis, angle):
        """Rotate the ghost of a given angle."""
        self.trans.rotation.setValue(coin.SbVec3f(tup(axis)), angle)

    def center(self, point):
        """Set the rotation/scale center of the ghost."""
        self.trans.center.setValue(point.x, point.y, point.z)

    def scale(self, delta):
        """Scale the ghost by the given factor."""
        self.trans.scaleFactor.setValue([delta.x, delta.y, delta.z])

    def getNode(self, obj):
        """Return a coin node representing the given object."""
        import Part
        if isinstance(obj, Part.Shape):
            return self.getNodeLight(obj)
        elif obj.isDerivedFrom("Part::Feature"):
            return self.getNodeFull(obj)
        else:
            return self.getNodeFull(obj)
    
    def getPlaneRotation(self, uvec, vvec, _ = None):
        """Return a rotation matrix defining the (u,v,w) coordinate system.

        The rotation matrix uses the elements from each vector.
        `v` is adjusted to be perpendicular to `u`
        ::
                (u.x  v.x  w.x  0  )
            R = (u.y  v.y  w.y  0  )
                (u.z  v.z  w.z  0  )
                (0    0    0    1.0)

        Parameters
        ----------
        u : Base::Vector3
            The first vector.
        v : Base::Vector3
            Hint for the second vector.
        _ : Ignored. For backwards compatibility

        Returns
        -------
        Base::Matrix4D
            The new rotation matrix defining a new coordinate system,
            or `None` if `u` or `v` is `None` or
            if `u` and `v` are parallel.
        """
        if (not uvec) or (not vvec):
            return None
        typecheck([(uvec, Vector), (vvec, Vector)], "getPlaneRotation")
        u = Vector(uvec)
        u.normalize()
        w = uvec.cross(vvec)
        if not w.Length:
            return None
        w.normalize()
        vvec = w.cross(uvec)

        mvec = App.Matrix(uvec.x, vvec.x, w.x, 0,
                           uvec.y, vvec.y, w.y, 0,
                           uvec.z, vvec.z, w.z, 0,
                           0.0, 0.0, 0.0, 1.0)
        return mvec
    
    def getNodeFull(self, obj):
        """Get a coin node which is a copy of the current representation."""
        sep = coin.SoSeparator()
        try:
            sep.addChild(obj.ViewObject.RootNode.copy())
            # add Part container offset
            if hasattr(obj, "getGlobalPlacement"):
                if obj.Placement != obj.getGlobalPlacement():
                    if sep.getChild(0).getNumChildren() > 0:
                        if isinstance(sep.getChild(0).getChild(0),coin.SoTransform):
                            gpl = obj.getGlobalPlacement()
                            sep.getChild(0).getChild(0).translation.setValue(tuple(gpl.Base))
                            sep.getChild(0).getChild(0).rotation.setValue(gpl.Rotation.Q)
        except Exception:
            print("ghostTracker: Error retrieving coin node (full)")
        return sep

    def getNodeLight(self, shape):
        """Extract a lighter version directly from a shape."""
        # error-prone
        sep = coin.SoSeparator()
        try:
            inputstr = coin.SoInput()
            inputstr.setBuffer(shape.writeInventor())
            coinobj = coin.SoDB.readAll(inputstr)
            # only add wireframe or full node?
            sep.addChild(coinobj.getChildren()[1])
            # sep.addChild(coinobj)
        except Exception:
            print("ghostTracker: Error retrieving coin node (light)")
        return sep

    def getMatrix(self):
        """Get matrix of the active view."""
        r = Gui.ActiveDocument.ActiveView.getViewer().getSoRenderManager().getViewportRegion()
        v = coin.SoGetMatrixAction(r)
        m = self.trans.getMatrix(v)
        if m:
            m = m.getValue()
            return App.Matrix(m[0][0], m[0][1], m[0][2], m[0][3],
                                  m[1][0], m[1][1], m[1][2], m[1][3],
                                  m[2][0], m[2][1], m[2][2], m[2][3],
                                  m[3][0], m[3][1], m[3][2], m[3][3])
        else:
            return App.Matrix()

    def setMatrix(self, matrix):
        """Set the transformation matrix."""
        m = coin.SbMatrix(matrix.A11, matrix.A12, matrix.A13, matrix.A14,
                          matrix.A21, matrix.A22, matrix.A23, matrix.A24,
                          matrix.A31, matrix.A32, matrix.A33, matrix.A34,
                          matrix.A41, matrix.A42, matrix.A43, matrix.A44)
        self.trans.setMatrix(m)

class arcTracker(Tracker):
    """An arc tracker."""
    
    def __init__(self, normal=None):
        dotted = False
        scolor = (1.0,1.0,1.0)
        swidth = 50
        start = 0
        end = math.pi*2
        self.circle = None
        self.startangle = math.degrees(start)
        self.endangle = math.degrees(end)
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
        self.sep = coin.SoSeparator()
        self.autoinvert = True
        if normal:
            self.normal = normal
        else:
            pass
        self.recompute()
        super().__init__(dotted, scolor, swidth,
                         [self.trans, self.sep], name="arcTracker")

    def getDeviation(self):
        """Return a deviation vector that represents the base of the circle."""
        import Part
        c = Part.makeCircle(1, Vector(0, 0, 0), self.normal)
        return c.Vertexes[0].Point

    def setCenter(self, cen):
        """Set the center point."""
        self.trans.translation.setValue([cen.x, cen.y, cen.z])

    def setRadius(self, rad):
        """Set the radius."""
        self.trans.scaleFactor.setValue([rad, rad, rad])

    def getRadius(self):
        """Return the current radius."""
        return self.trans.scaleFactor.getValue()[0]

    def setStartAngle(self, ang):
        """Set the start angle."""
        self.startangle = math.degrees(ang)
        self.recompute()

    def _removeSwitch(self, switch):
        """Remove self.switch from the scene graph.

        As with _insertSwitch,
        must not be called during scene graph traversal).
        """
        sg = get_3d_view().getSceneGraph()
        if sg.findChild(switch) >= 0:
            sg.removeChild(switch)

    def getAngle(self, pt):
        """Return the angle of a given vector in radians."""
        c = self.trans.translation.getValue()
        center = Vector(c[0], c[1], c[2])
        rad = pt.sub(center)
        a = angle_rad(rad, self.getDeviation(), self.normal)
        return a

    def getAngles(self):
        """Return the start and end angles in degrees."""
        return(self.startangle, self.endangle)

    def setStartPoint(self, pt):
        """Set the start angle from a point."""
        self.setStartAngle(-self.getAngle(pt))

    def setApertureAngle(self, ang):
        """Set the end angle by giving the aperture angle."""
        ap = math.degrees(ang)
        self.endangle = self.startangle + ap
        self.recompute()
        

    def recompute(self):
        """Recompute the tracker."""
        import Part
        if self.circle:
            self.sep.removeChild(self.circle)
        self.circle = None
        if (self.endangle < self.startangle) or not self.autoinvert:
            c = Part.makeCircle(10, Vector(0, 0, 0),
                                self.normal, self.endangle, self.startangle)
        else:
            c = Part.makeCircle(10, Vector(0, 0, 0),
                                self.normal, self.startangle, self.endangle)
        buf = c.writeInventor(2, 0.01)
        if True:
            ivin = coin.SoInput()
            ivin.setBuffer(buf)
            ivob = coin.SoDB.readAll(ivin)
            buf = buf.replace("\n", "")
            pts = re.findall("point \[(.*?)\]", buf)[0]
            pts = pts.split(",")
            pc = []
            for p in pts:
                v = p.strip().split()
                pc.append([float(v[0]), float(v[1]), float(v[2])])
            coords = coin.SoCoordinate3()
            coords.point.setValues(0, len(pc), pc)
            line = coin.SoLineSet()
            line.numVertices.setValue(-1)
            self.circle = coin.SoSeparator()
            self.circle.addChild(coords)
            self.circle.addChild(line)
            self.sep.addChild(self.circle)
        else:
            ivin = coin.SoInput()
            ivin.setBuffer(buf)
            ivob = coin.SoDB.readAll(ivin)
        
                
                
class lineTracker(Tracker):
    """A Line tracker, used by the tools that need to draw temporary lines"""

    def __init__(self):
        line = coin.SoLineSet()
        dotted = False
        scolor = (0.0,0.0,0.0)
        swidth = 2
        ontop = False
        line.numVertices.setValue(2)
        self.coords = coin.SoCoordinate3()  # this is the coordinate
        self.coords.point.setValues(0, 2, [[0, 0, 0], [1, 0, 0]])
        super().__init__(dotted, scolor, swidth,
                         [self.coords, line],
                         ontop, name="lineTracker")

    def p1(self, point=None):
        """Set or get the first point of the line."""
        if point:
            if self.coords.point.getValues()[0].getValue() != tuple(point):
                self.coords.point.set1Value(0, point.x, point.y, point.z)
        else:
            return Vector(self.coords.point.getValues()[0].getValue())

    def p2(self, point=None):
        """Set or get the second point of the line."""
        if point:
            if self.coords.point.getValues()[-1].getValue() != tuple(point):
                self.coords.point.set1Value(1, point.x, point.y, point.z)
        else:
            return Vector(self.coords.point.getValues()[-1].getValue())

    def getLength(self):
        """Return the length of the line."""
        p1 = Vector(self.coords.point.getValues()[0].getValue())
        p2 = Vector(self.coords.point.getValues()[-1].getValue())
        return (p2.sub(p1)).Length
