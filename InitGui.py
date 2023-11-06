class FOWorkbench (Workbench):
    MenuText = "FO Workbench"
    ToolTop = "Workbench to produce a FO for a given mesh foot with input parameters"
    #Icon = ##
    
    def Initialize(self):
        import FOImport, FOLandmark, FOPosition
        
        self.list = ["Import", "Landmark", "Position"]
        self.appendToolbar("Commands", self.list)
        self.appendMenu("New Menus", self.list)

    def Activated(self):
        return
                         
    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        self.appendContextMenu("My commands", self.list)
        
                         
    def GetClassName(self):
        return "Gui::PythonWorkbench"
        
Gui.addWorkbench(FOWorkbench())
