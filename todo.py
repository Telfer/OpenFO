from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import FreeCADGui as Gui
import PySide.QtCore as QtCore
from FreeCAD import Vector

import pivy.coin as coin

import draftutils.groups as groups
from draftutils.messages import _msg, _err
from draftutils.translate import translate
import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original

from functions import *
import Tracker_Class

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
                #_log(traceback.format_exc())
                #_err(traceback.format_exc())
                #wrn = ("ToDo.doTasks, Unexpected error:\n"
                #       "{0}\n"
                #       "in {1}({2})".format(sys.exc_info()[0], f, arg))
                #_wrn(wrn)
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