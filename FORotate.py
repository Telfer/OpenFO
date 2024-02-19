import math
from PySide.QtCore import QT_TRANSLATE_NOOP

import traceback
import sys
import PySide.QtCore as QtCore
import re

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
#from FreeCAD import Units as U

import pivy.coin as coin

import draftutils.groups as groups
from draftutils.translate import translate
#import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original

import Tracker_Class
from functions import *
import Snapper_Class

class FORotate(gui_base_original.Modifier):
    """Gui Command for the Rotate tool."""

    def GetResources(self):
        """Set icon, menu and tooltip."""
        _tip = ()

        return {
                'MenuText': QT_TRANSLATE_NOOP("Rotate", "Rotate"),
                'ToolTip': QT_TRANSLATE_NOOP("Rotate", "Rotates the selected objects. Choose the center of rotation, then the initial angle, and then the final angle.\nIf the \"copy\" option is active, it will create rotated copies.\nCTRL to snap, SHIFT to constrain. Hold ALT and click to create a copy with each click.")}

    def Activated(self, dotted=False, scolor=(0.0,0.0,0.0), swidth=None,
                 start=0, end=math.pi*2, normal=None, u=Vector(1, 0, 0), v=Vector(0, 1, 0), w=Vector(0, 0, 1),
                 pos=Vector(0, 0, 0)):
        """Execute when the command is called."""
        print("Select Foot Mesh")
        self.ghosts = []
        self.lines = []
        self.view = Gui.ActiveDocument.ActiveView
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.planetrack = Tracker_Class.PlaneTracker(self.u, self.v)
        self.axis = w
        self.commitList = []
        self.position = pos
        self.arctrack = None
        self.stored = None
        self.setup()
        self.circle = None
        self.doc = App.ActiveDocument
        self.startangle = math.degrees(start)
        self.endangle = math.degrees(end)
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
        self.sep = coin.SoSeparator()
        self.autoinvert = True
        self.get_object_selection()


    def get_object_selection(self):
        """Get the object selection."""
        #if Gui.Selection.getSelection():
        #    return self.proceed()
        self.call = self.view.addEventCallback("SoEvent", self.select_object)
        
    def select_object(self, arg):
        """Handle the selection of objects depending on buttons pressed."""
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif not arg["CtrlDown"] and Gui.Selection.hasSelection():
            self.proceed()
        
    def proceed(self):
        """Continue with the command after a selection has been made."""
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)
        self.selected_objects = Gui.Selection.getSelection()
        self.selected_objects = groups.get_group_contents(self.selected_objects,
                                      addgroups=True,
                                      spaces=True,
                                      noarchchild=True)
        self.selected_subelements = Gui.Selection.getSelectionEx()
        self.step = 0
        self.center = None
        self.arctrack = Tracker_Class.arcTracker(self.axis)
        self.call = self.view.addEventCallback("SoEvent", self.action)
        print("Pick rotation center")

    def action(self, arg):
        """Handle the 3D scene events."""
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.handle_mouse_move_event(arg)
        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):
            self.handle_mouse_click_event(arg)

    def handle_mouse_move_event(self, arg):
        """Handle the mouse when moving."""
        for ghost in self.ghosts:
            ghost.off()
        p = self.view.getCursorPos()
        self.point = self.view.getPoint(p)
        self.info = self.view.getObjectInfo(p)
        self.ctrlPoint = App.Vector(self.point)
        if self.center and dist(self.point, self.center):
            viewdelta = project(self.point.sub(self.center),
                                              self.axis)
            if not isNull(viewdelta):
                self.point = self.point.add(viewdelta.negative())
        self.extendedCopy = False
        if self.step == 3:
            self.finish()
        if self.step == 0:
            pass
        elif self.step == 1:
            currentrad = dist(self.point, self.center)
            if currentrad != 0:
                angle = angle_rad(self.u,
                              self.point.sub(self.center),
                              self.axis)
            else:
                angle = 0
            self.firstangle = angle
        elif self.step == 2:
            self.update_lines()
            currentrad = dist(self.point, self.center)
            if currentrad != 0:
                angle = angle_rad(self.u,
                        self.point.sub(self.center),
                        self.axis)
            else:
                angle = 0
            if angle < self.firstangle:
                sweep = (2 * math.pi - self.firstangle) + angle
            else:
                sweep = angle - self.firstangle
            self.arctrack.on()
            self.arctrack.setApertureAngle(sweep)
            for ghost in self.ghosts:
                ghost.rotate(self.axis, sweep)
                ghost.on()
        redraw_3d_view()

    def handle_mouse_click_event(self, arg):
        """Handle the mouse when the first button is clicked."""
        if not self.point:
            return
        if self.step == 0:
            self.set_center()
        elif self.step == 1:
            self.set_start_point()
        else:
            self.set_rotation_angle(arg)

    def set_center(self):
        """Set the center of the rotation."""
        if not self.ghosts:
            self.set_ghosts()
        self.center = self.point
        self.set_lines()
        self.node = [self.point]
        self.arctrack.setCenter(self.center)
        for ghost in self.ghosts:
            ghost.center(self.center)
        self.step = 1
        print("Pick base angle")
        if self.planetrack:
            self.planetrack.set(self.point)

    def set_start_point(self):
        """Set the starting point of the rotation."""
        self.rad = dist(self.point, self.center)
        self.arctrack.on()
        self.arctrack.setStartPoint(self.point)
        #self.set_lines()
        for ghost in self.ghosts:
            ghost.on()
        self.step = 2
        print("Pick rotation angle")

    def set_rotation_angle(self, arg):
        """Set the rotation angle."""

        angle = self.point.sub(self.center).getAngle(self.u)
        _v = project(self.point.sub(self.center), self.v)
        if _v.getAngle(self.v) > 1:
            angle = -angle
        if angle < self.firstangle:
            self.angle = (2 * math.pi - self.firstangle) + angle
        else:
            self.angle = angle - self.firstangle
        self.rotate(self.extendedCopy)
        self.finish()

    def set_ghosts(self):
        """Set the ghost to display."""
        for ghost in self.ghosts:
            ghost.remove()
        self.ghosts = [Tracker_Class.ghostTracker(self.selected_objects)]
        if self.center:
            for ghost in self.ghosts:
                ghost.center(self.center)

    def finish(self):
        """Terminate the operation."""
        if self.arctrack:
            self.arctrack.finalize()
        for ghost in self.ghosts:
            ghost.finalize()
        if self.call:
            try:
                self.view.removeEventCallback("SoEvent", self.call)
            except RuntimeError:
                pass
            self.call = None
        if self.commitList:
            last_cmd = self.commitList[-1][1][-1]
            if last_cmd.find("recompute") >= 0:
                self.commitList[-1] = (self.commitList[-1][0], self.commitList[-1][1][:-1])
                ToDo.delayCommit(self.commitList)
                ToDo.delayAfter(Gui.doCommand, last_cmd)
            else:
                ToDo.delayCommit(self.commitList)
        self.commitList = []
        self.lines.off()
        self.planetrack.off()
        if self.doc:
            self.doc.recompute()
        Gui.Selection.clearSelection()
    
    def get_point(self):
        self.p = self.view.getCursorPos()
        self.pos = self.view.getPoint(self.p)
        
    def set_lines(self):
        """Set the line to displayc."""
        self.get_point()
        for line in self.lines:
            self.lines.remove()
        self.lines = Tracker_Class.lineTracker()
        self.lines.p1(self.pos)
        self.lines.p2(self.pos)
        self.lines.on()
    
    def update_lines(self):
        self.get_point()
        self.lines.p2(self.pos)
    
    def rotate(self, is_copy=False):
        """Perform the rotation of the subelements or the entire object."""
        self.rotate_object(is_copy)
                
    def rotate_subelements(self, is_copy):
        """Rotate the subelements."""
        try:
            if is_copy:
                self.commit(translate("draft", "Copy"),
                            self.build_copy_subelements_command())
            else:
                self.commit(translate("draft", "Rotate"),
                            self.build_rotate_subelements_command())
        except Exception:
            print("Some subelements could not be moved.")
    
    def commit(self, name, func):
        """Store actions in the commit list to be run later. """
        self.commitList.append((name, func))
    
    def build_copy_subelements_command(self):
        """Build the string to commit to copy the subelements."""
        import Part
        command = []
        arguments = []
        E = len("Edge")
        for obj in self.selected_subelements:
            for index, subelement in enumerate(obj.SubObjects):
                if not isinstance(subelement, Part.Edge):
                    continue
                _edge_index = int(obj.SubElementNames[index][E:]) - 1
                _cmd = '['
                _cmd += 'FreeCAD.ActiveDocument.'
                _cmd += obj.ObjectName + ', '
                _cmd += str(_edge_index) + ', '
                _cmd += str(math.degrees(self.angle)) + ', '
                _cmd += toString(self.center) + ', '
                _cmd += toString(self.axis)
                _cmd += ']'
                arguments.append(_cmd)

        all_args = ', '.join(arguments)
        command.append('Draft.copy_rotated_edges([' + all_args + '])')
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def build_rotate_subelements_command(self):
        """Build the string to commit to rotate the subelements."""
        import Part
        command = []
        V = len("Vertex")
        E = len("Edge")
        for obj in self.selected_subelements:
            for index, subelement in enumerate(obj.SubObjects):
                if isinstance(subelement, Part.Vertex):
                    _vertex_index = int(obj.SubElementNames[index][V:]) - 1
                    _cmd = 'Draft.rotate_vertex'
                    _cmd += '('
                    _cmd += 'FreeCAD.ActiveDocument.'
                    _cmd += obj.ObjectName + ', '
                    _cmd += str(_vertex_index) + ', '
                    _cmd += str(math.degrees(self.angle)) + ', '
                    _cmd += toString(self.center) + ', '
                    _cmd += toString(self.axis)
                    _cmd += ')'
                    command.append(_cmd)
                elif isinstance(subelement, Part.Edge):
                    _edge_index = int(obj.SubElementNames[index][E:]) - 1
                    _cmd = 'Draft.rotate_edge'
                    _cmd += '('
                    _cmd += 'FreeCAD.ActiveDocument.'
                    _cmd += obj.ObjectName + ', '
                    _cmd += str(_edge_index) + ', '
                    _cmd += str(math.degrees(self.angle)) + ', '
                    _cmd += toString(self.center) + ', '
                    _cmd += toString(self.axis)
                    _cmd += ')'
                    command.append(_cmd)
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def rotate_object(self, is_copy):
        """Move the object."""

        _doc = 'FreeCAD.ActiveDocument.'
        _selected = self.selected_objects

        objects = '['
        objects += ','.join([_doc + obj.Name for obj in _selected])
        objects += ']'

        _cmd = 'Draft.rotate'
        _cmd += '('
        _cmd += objects + ', '
        _cmd += str(math.degrees(self.angle)) + ', '
        _cmd += toString(self.center) + ', '
        _cmd += 'axis=' + toString(self.axis) + ', '
        _cmd += 'copy=' + str(is_copy)
        _cmd += ')'
        _cmd_list = [_cmd,
                     'FreeCAD.ActiveDocument.recompute()']

        _mode = "Copy" if is_copy else "Rotate"
        Gui.addModule("Draft")
        self.commit(translate("draft", _mode),
                    _cmd_list)

    def setup(self, direction=None, point=None, upvec=None, force=False):
        """Set up the working plane if it exists but is undefined."""
        self.weak = True
        if self.weak or force:
            if direction and point:
                self.alignToPointAndAxis(point, direction, 0, upvec)
            elif True:
                try:
                    from pivy import coin
                    view = Gui.ActiveDocument.ActiveView
                    camera = view.getCameraNode()
                    rot = camera.getField("orientation").getValue()
                    coin_up = coin.SbVec3f(0, 1, 0)
                    upvec = Vector(rot.multVec(coin_up).getValue())
                    vdir = view.getViewDirection()
                    # don't change the plane if the axis and v vector
                    # are already correct:
                    tol = Part.Precision.angular()
                    if abs(math.pi - vdir.getAngle(self.axis)) > tol \
                            or abs(math.pi - upvec.getAngle(self.v)) > tol:
                        self.alignToPointAndAxis(Vector(0, 0, 0),
                                                 vdir.negative(), 0, upvec)
                except Exception:
                    pass
            if force:
                self.weak = False
            else: 
                self.weak = True
            self.normal = self.axis
    
    def getRotation(self):
        """Return a placement describing the plane orientation only."""
        m = getPlaneRotation(self.u, self.v)
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
        

    
    def alignToPointAndAxis(self, point, axis, offset=0, upvec=None):
        """Align the working plane to a point and an axis (vector)."""
        self.doc = App.ActiveDocument
        self.axis = axis
        self.axis.normalize()
        if axis.getAngle(Vector(1, 0, 0)) < 0.00001:
            self.axis = Vector(1, 0, 0)
            self.u = Vector(0, 1, 0)
            self.v = Vector(0, 0, 1)
        elif axis.getAngle(Vector(-1, 0, 0)) < 0.00001:
            self.axis = Vector(-1, 0, 0)
            self.u = Vector(0, -1, 0)
            self.v = Vector(0, 0, 1)
        elif upvec:
            self.u = upvec.cross(self.axis)
            self.u.normalize()
            self.v = self.axis.cross(self.u)
            self.v.normalize()
        else:
            self.v = axis.cross(Vector(1, 0, 0))
            self.v.normalize()
            self.u = rotateSpec(self.v, -math.pi/2, self.axis)
            self.u.normalize()
        offsetVector = Vector(axis)
        offsetVector.multiply(offset)
        self.position = point.add(offsetVector)
        self.weak = False
        # Console.PrintMessage("(position = " + str(self.position) + ")\n")
        # Console.PrintMessage(self.__repr__() + "\n")


_DEBUG = 0
_DEBUG_inner = 0

class ToDo:
    """A static class that delays execution of functions."""

    itinerary = []
    commitlist = []
    afteritinerary = []

    @staticmethod
    def doTasks():
        """Execute the commands stored in the lists.

        The lists are `itinerary`, `commitlist` and `afteritinerary`.
        """
        if _DEBUG:
            print("Debug: doing delayed tasks.\n itinerary: {0}\n commitlist: {1}\n afteritinerary: {2}\n".format(todo.itinerary, todo.commitlist, todo.afteritinerary))
        try:
            for f, arg in ToDo.itinerary:
                try:
                    if _DEBUG_inner:
                        print("Debug: executing.\n function: {}\n".format(f))
                    if arg or (arg is False):
                        f(arg)
                    else:
                        f()
                except Exception:
                    pass
        except ReferenceError:
            pass
        ToDo.itinerary = []

        if ToDo.commitlist:
            for name, func in ToDo.commitlist:
                if _DEBUG_inner:
                    print("Debug: committing.\n name: {}\n".format(name))
                try:
                    name = str(name)
                    App.activeDocument().openTransaction(name)
                    if isinstance(func, list):
                        for string in func:
                            Gui.doCommand(string)
                    else:
                        func()
                    App.activeDocument().commitTransaction()
                except Exception:
                    pass
            # Restack Draft screen widgets after creation
            #if hasattr(Gui, "Snapper"):
                #Gui.Snapper.restack()
        ToDo.commitlist = []

        for f, arg in ToDo.afteritinerary:
            try:
                if _DEBUG_inner:
                    print("Debug: executing after.\n function: {}\n".format(f))
                if arg:
                    f(arg)
                else:
                    f()
            except Exception:
                pass
        ToDo.afteritinerary = []

    @staticmethod
    def delay(f, arg):
        """Add the function and argument to the itinerary list."""
        if _DEBUG:
            print ("Debug: delaying.\n function: {}\n".format(f))
        if ToDo.itinerary == []:
            QtCore.QTimer.singleShot(0, ToDo.doTasks)
        ToDo.itinerary.append((f, arg))

    @staticmethod
    def delayCommit(cl):
        """Execute the other lists, and add to the commit list."""
        if _DEBUG:
            print("Debug: delaying commit.\n commitlist: {}\n".format(cl))
        QtCore.QTimer.singleShot(0, ToDo.doTasks)
        ToDo.commitlist = cl

    @staticmethod
    def delayAfter(f, arg):
        """Add the function and argument to the afteritinerary list."""
        if _DEBUG:
            print("Debug: delaying after.\n function: {}\n".format(f))
        if ToDo.afteritinerary == []:
            QtCore.QTimer.singleShot(0, ToDo.doTasks)
        ToDo.afteritinerary.append((f, arg))

todo = ToDo

Gui.addCommand('Rotate', FORotate())

## @}
