import sys
import os
from dataclasses import dataclass

sys.path.append("../")
import unittest
APP_DIR = "../"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from utilsOpenEMS.ScriptLinesGenerator.PythonScriptLinesGenerator2 import PythonScriptLinesGenerator2
from utilsOpenEMS.GuiHelpers.FactoryCadInterface import FactoryCadInterface
from utilsOpenEMS.GuiHelpers.GuiHelpers import GuiHelpers
from ExportOpenEMSDialog import ExportOpenEMSDialog

_instance = QApplication([])

@dataclass
class BBox:
    XMin: float
    XMax: float
    YMin: float
    YMax: float
    ZMin: float
    ZMax: float


class DummyGuiHelper:
    statusBar = None
    def displayMessage(self, *args, **kwargs):
        print(*args)

class ExportOpenEMSDialog_Test(unittest.TestCase):
    def test_run(self):
        ExportOpenEMSDialog()
        pass

class PythonScriptLinesGenerator2_Test(unittest.TestCase):
    def setUp(self):
        cadHelpers = FactoryCadInterface.createHelper(APP_DIR)
        path_to_ui = os.path.join(APP_DIR, "ui", "dialog.ui")
        self.form = cadHelpers.loadUI(path_to_ui, _instance)

        #guiHelpers = GuiHelpers(self.form, statusBar = None)
        guiHelpers = DummyGuiHelper()
        self.gen = PythonScriptLinesGenerator2(form=self.form, guiHelpers=guiHelpers)

    def tearDown(self):
        pass

    def test_create(self):
        pass

    def test_create_file_blank(self):
        print(self.gen.getCoordinateSystemScriptLines())
        print(self.gen.getMaterialDefinitionsScriptLines(items=[], outputDir=None, generateObjects=True))
        print(self.gen.getCartesianOrCylindricalScriptLinesFromStartStop(bbCoords=BBox(0,1,0,1,0,1), startPointName=None, stopPointName=None))
        print(self.gen.getInitScriptLines())
        print(self.gen.getExcitationScriptLines(False))
        print(self.gen.getExcitationScriptLines(True))
        print(self.gen.getBoundaryConditionsScriptLines())
        print(self.gen.getMinimalGridlineSpacingScriptLines())
        print(self.gen.generateOpenEMSScript(outputDir="./"))
        # print(self.gen.writeNf2ffButtonClicked())
        # print(self.gen.drawS11ButtonClicked())
        # print(self.gen.drawS21ButtonClicked())

if __name__ == "__main__":
    unittest.main()
