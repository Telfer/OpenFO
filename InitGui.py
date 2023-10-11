{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ea5ec7fc-73fb-4894-83a8-31b117fb5c8b",
   "metadata": {},
   "outputs": [],
   "source": [
    "class FOWorkbench (Workbench):\n",
    "    MenuText = \"FO Workbench\"\n",
    "    ToolTop = \"Workbench to produce a FO for a given mesh foot with input parameters\"\n",
    "    Icon \"\"\"***\"\"\"\n",
    "\n",
    "    def Initialize(self):\n",
    "        import FOBuild, FOImport, FOLandmarks, FOPosition\n",
    "        self.list = [\"Build\", \"Import\", \"Landmark\", \"Position\"]\n",
    "        self.appendToolbar(\"Commands\", self.list)\n",
    "        self.appendMenu(\"New Menus\", self.list)\n",
    "\n",
    "    def Activated(self):\n",
    "        return\n",
    "\n",
    "    def Deactivated(self):\n",
    "        return\n",
    "\n",
    "    def GetClassName(self):\n",
    "        return \"Gui::PythonWorkbench\"\n",
    "\n",
    "Gui.addWorkbench(FOWorkbench):\n",
    "    "
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
