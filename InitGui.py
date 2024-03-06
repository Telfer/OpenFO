class FOWorkbench (Workbench):
    MenuText = "FO Workbench"
    ToolTop = "Workbench to produce a FO for a given mesh foot with input parameters"
    #Icon = ##
    
    def Initialize(self):
        import FOGui
        import FOImport, FOPosition,FOLandmark
        
        self.list = ["Import", "Position", "Rotate", "Translate", "Landmark"]
        self.appendToolbar("Commands", self.list)
        self.appendMenu("New Menus", self.list)

    def Activated(self):
        if hasattr(FreeCADGui, "FOToolBar"):
            FreeCADGui.FOToolBar.Activated()
        return
                         
    def Deactivated(self):
        if hasattr(FreeCADGui, "FOToolBar"):
            FreeCADGui.FOToolBar.Deactivated()
        return

    def ContextMenu(self, recipient):
        self.appendContextMenu("My commands", self.list)
        
                         
    def GetClassName(self):
        return "Gui::PythonWorkbench"
        
Gui.addWorkbench(FOWorkbench())
