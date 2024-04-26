import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector

import pivy.coin as coin
import PySide.QtCore as QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP

import draftutils.groups as groups
from draftutils.translate import translate
import draftguitools.gui_base_original as gui_base_original

from functions import *
import Tracker_Class
import Snapper_Class


class FOTranslate(gui_base_original.Modifier):
    """Gui Command for the Move tool."""

    def __init__(self):
        super(FOTranslate, self).__init__()

    def GetResources(self):
        """Set icon, menu and tooltip."""

        return {'MenuText': QT_TRANSLATE_NOOP("Translate", "Move"),
                'ToolTip': QT_TRANSLATE_NOOP("Translate", "Moves the selected objects from one base point to another point.\nIf the \"copy\" option is active, it will create displaced copies.\nCTRL to snap, SHIFT to constrain.")}

    def Activated(self, orientation):
        """Execute when the command is called."""
        self.ghosts = []
        self.lines = []
        self.view = Gui.ActiveDocument.ActiveView
        self.node = []
        self.commitList = []
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.planetrack = Tracker_Class.PlaneTracker(self.u, self.v)
        self.linesSet = False
        self.doc = App.ActiveDocument
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
        self.sep = coin.SoSeparator()
        self.autoinvert = True
        self.get_object_selection()
        
    def get_object_selection(self):
        """Get the object selection."""
        obj = self.doc.getObject('Mesh001')
        Gui.Selection.addSelection(obj)
        self.proceed()
            
            
    def proceed(self):
        """Continue with the command after a selection has been made."""
        print("Pick start point")
        self.selected_objects = Gui.Selection.getSelection()
        self.selected_objects = groups.get_group_contents(self.selected_objects,
                                      addgroups=True,
                                      spaces=True,
                                      noarchchild=True)
        if not self.ghosts:
            self.set_ghosts()
        self.selected_subelements = Gui.Selection.getSelectionEx()
        self.call = self.view.addEventCallback("SoEvent", self.action)
        

    def finish(self, cont=False):
        """Terminate the operation.

        Parameters
        ----------
        cont: bool or None, optional
            Restart (continue) the command if `True`, or if `None` and
            `ui.continueMode` is `True`.
        """
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
        

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """
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
        self.get_point()
        self.point = self.pos
        if self.linesSet: 
            self.update_lines()
        if len(self.node) > 0:
            last = self.node[len(self.node) - 1]
            self.vector = self.point.sub(last)
            for ghost in self.ghosts:
                ghost.move(self.vector)
                ghost.on()
        redraw_3d_view()

    def handle_mouse_click_event(self, arg):
        """Handle the mouse when the first button is clicked."""
        if not self.linesSet:
            self.set_lines()
            self.linesSet = True
        else:
            self.update_lines()
        if not self.ghosts:
            self.set_ghosts()
        for obj in self.selected_objects:
            obj.Visibility = False
        if not self.point:
            return
        redraw_3d_view()
        if self.node == []:
            self.node.append(self.point)
            for ghost in self.ghosts:
                ghost.on()
            print("Pick end point")
            if self.planetrack:
                self.planetrack.set(self.point)
                self.planetrack.off()
        else:
            last = self.node[0]
            self.vector = self.point.sub(last)
            self.move(False)
            self.finish(cont=None)

    def set_ghosts(self):
        """Set the ghost to display."""
        for ghost in self.ghosts:
            ghost.remove()
        self.ghosts = [Tracker_Class.ghostTracker(self.selected_objects)]
        
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
    
    def move(self, is_copy=False):
        """Perform the move of the subelements or the entire object."""
        self.move_object(is_copy)

    def move_subelements(self, is_copy):
        """Move the subelements."""
        try:
            if is_copy:
                self.commit(translate("draft", "Copy"),
                            self.build_copy_subelements_command())
            else:
                self.commit(translate("draft", "Move"),
                            self.build_move_subelements_command())
        except Exception:
            print("Some subelements could not be moved.")

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
                _cmd += toString(self.vector)
                _cmd += ']'
                arguments.append(_cmd)

        all_args = ', '.join(arguments)
        command.append('Draft.copy_moved_edges([' + all_args + '])')
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def build_move_subelements_command(self):
        """Build the string to commit to move the subelements."""
        import Part

        command = []
        V = len("Vertex")
        E = len("Edge")
        for obj in self.selected_subelements:
            for index, subelement in enumerate(obj.SubObjects):
                if isinstance(subelement, Part.Vertex):
                    _vertex_index = int(obj.SubElementNames[index][V:]) - 1
                    _cmd = 'Draft.move_vertex'
                    _cmd += '('
                    _cmd += 'FreeCAD.ActiveDocument.'
                    _cmd += obj.ObjectName + ', '
                    _cmd += str(_vertex_index) + ', '
                    _cmd += toString(self.vector)
                    _cmd += ')'
                    command.append(_cmd)
                elif isinstance(subelement, Part.Edge):
                    _edge_index = int(obj.SubElementNames[index][E:]) - 1
                    _cmd = 'Draft.move_edge'
                    _cmd += '('
                    _cmd += 'FreeCAD.ActiveDocument.'
                    _cmd += obj.ObjectName + ', '
                    _cmd += str(_edge_index) + ', '
                    _cmd += toString(self.vector)
                    _cmd += ')'
                    command.append(_cmd)
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def move_object(self, is_copy):
        """Move the object."""
        _doc = 'FreeCAD.ActiveDocument.'
        _selected = self.selected_objects

        objects = '['
        objects += ', '.join([_doc + obj.Name for obj in _selected])
        objects += ']'
        Gui.addModule("Draft")

        _cmd = 'Draft.move'
        _cmd += '('
        _cmd += objects + ', '
        _cmd += toString(self.vector) + ', '
        _cmd += 'copy=' + str(is_copy)
        _cmd += ')'
        _cmd_list = [_cmd,
                     'FreeCAD.ActiveDocument.recompute()']

        _mode = "Copy" if is_copy else "Move"
        self.commit(translate("draft", _mode),
                    _cmd_list)
        for obj in self.selected_objects:
                obj.Visibility = True
    
    def commit(self, name, func):
        """Store actions in the commit list to be run later.

        Parameters
        ----------
        name: str
            An arbitrary string that indicates the name of the operation
            to run.

        func: list of str
            Each element of the list is a string that will be run by
            `Gui.doCommand`.

            See the complete information in the `draftutils.todo.ToDo` class.
        """
        self.commitList.append((name, func))

        
_DEBUG = 0
_DEBUG_inner = 0

class ToDo:
    """A static class that delays execution of functions.

    It calls `QtCore.QTimer.singleShot(0, doTasks)`
    where `doTasks` is a static method which executes
    the commands stored in the list attributes.

    Attributes
    ----------
    itinerary: list of tuples
        Each tuple is of the form `(name, arg)`.
        The `name` is a reference (pointer) to a function,
        and `arg` is the corresponding argument that is passed
        to that function.
        It then tries executing the function with the argument,
        if available, or without it, if not available.
        ::
            name(arg)
            name()

    commitlist: list of tuples
        Each tuple is of the form `(name, command_list)`.
        The `name` is a string identifier or description of the commands
        that will be run, and `command_list` is a list of strings
        that indicate the Python instructions that will be executed,
        or a reference to a single function that will be executed.

        If `command_list` is a list, the program opens a transaction,
        then runs all commands in the list in sequence,
        and finally commits the transaction.
        ::
            command_list = ["command1", "command2", "..."]
            App.activeDocument().openTransaction(name)
            Gui.doCommand("command1")
            Gui.doCommand("command2")
            Gui.doCommand("...")
            App.activeDocument().commitTransaction()

        If `command_list` is a reference to a function
        the function is executed directly.
        ::
            command_list = function
            App.activeDocument().openTransaction(name)
            function()
            App.activeDocument().commitTransaction()

    afteritinerary: list of tuples
        Each tuple is of the form `(name, arg)`.
        This list is used just like `itinerary`.

    Lists
    -----
    The lists contain tuples. Each tuple contains a `name` which is just
    a string to identify the operation, and a `command_list` which is
    a list of strings, each string an individual Python instruction.
    """

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
        """Add the function and argument to the itinerary list.

        Schedule geometry manipulation that would crash Coin if done
        in the event callback.

        If the `itinerary` list is empty, it will call
        `QtCore.QTimer.singleShot(0, ToDo.doTasks)`
        to execute the commands in the other lists.

        Finally, it will build the tuple `(f, arg)`
        and append it to the `itinerary` list.

        Parameters
        ----------
        f: function reference
            A reference (pointer) to a Python command
            which can be executed directly.
            ::
                f()

        arg: argument reference
            A reference (pointer) to the argument to the `f` function.
            ::
                f(arg)
        """
        if _DEBUG:
            print ("Debug: delaying.\n function: {}\n".format(f))
        if ToDo.itinerary == []:
            QtCore.QTimer.singleShot(0, ToDo.doTasks)
        ToDo.itinerary.append((f, arg))

    @staticmethod
    def delayCommit(cl):
        """Execute the other lists, and add to the commit list.

        Schedule geometry manipulation that would crash Coin if done
        in the event callback.

        First it calls
        `QtCore.QTimer.singleShot(0, ToDo.doTasks)`
        to execute the commands in all lists.

        Then the `cl` list is assigned as the new commit list.

        Parameters
        ----------
        cl: list of tuples
            Each tuple is of the form `(name, command_list)`.
            The `name` is a string identifier or description of the commands
            that will be run, and `command_list` is a list of strings
            that indicate the Python instructions that will be executed.

            See the attributes of the `ToDo` class for more information.
        """
        if _DEBUG:
            print("Debug: delaying commit.\n commitlist: {}\n".format(cl))
        QtCore.QTimer.singleShot(0, ToDo.doTasks)
        ToDo.commitlist = cl

    @staticmethod
    def delayAfter(f, arg):
        """Add the function and argument to the afteritinerary list.

        Schedule geometry manipulation that would crash Coin if done
        in the event callback.

        Works the same as `delay`.

        If the `afteritinerary` list is empty, it will call
        `QtCore.QTimer.singleShot(0, ToDo.doTasks)`
        to execute the commands in the other lists.

        Finally, it will build the tuple `(f, arg)`
        and append it to the `afteritinerary` list.
        """
        if _DEBUG:
            print("Debug: delaying after.\n function: {}\n".format(f))
        if ToDo.afteritinerary == []:
            QtCore.QTimer.singleShot(0, ToDo.doTasks)
        ToDo.afteritinerary.append((f, arg))

todo = ToDo  


#Gui.addCommand('Translate', FOTranslate())

## @}
