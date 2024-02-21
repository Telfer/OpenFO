v=Gui.activeDocument().activeView()

#This class logs any mouse button events. As the registered callback function fires twice for 'down' and
#'up' events we need a boolean flag to handle this.
class ViewObserver:
   def __init__(self, view):
       self.view = view
   
   def logPosition(self, info):
       down = (info["State"] == "DOWN")
       pos = info["Position"]
       if (down):
           pnt = self.view.getPoint(pos)
           info = self.view.getObjectInfo(pos)
           FreeCAD.Console.PrintMessage("Object info: " + str(info) + "\n")



o = ViewObserver(v)
c = v.addEventCallback("SoMouseButtonEvent",o.logPosition)