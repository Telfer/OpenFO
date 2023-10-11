{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f267be39-2fbb-4685-b176-bc58c8eb501e",
   "metadata": {},
   "outputs": [],
   "source": [
    "FreeCAD.addImportType(\"My own format (*.own)\", \"importOwn\")\n",
    "FreeCAD.addExportType(\"My own format (*.own)\", \"importOwn\")\n",
    "print(\"I am executing some stuff here when FreeCAD starts!\")"
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
