import sys
import os
from dataclasses import dataclass

from pathlib import Path

sys.path.append("../")
import unittest
APP_DIR = "../"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from PySide6 import QtGui

from utilsOpenEMS.ScriptLinesGenerator.PythonScriptLinesGenerator2 import PythonScriptLinesGenerator2
from utilsOpenEMS.GuiHelpers.FactoryCadInterface import FactoryCadInterface
from utilsOpenEMS.GuiHelpers.GuiHelpers import GuiHelpers
from ExportOpenEMSDialog import ExportOpenEMSDialog
from utilsOpenEMS.SaveLoad.IniValidator0v1 import IniValidator0v1
from utilsOpenEMS.SaveLoad.IniFile0v1 import IniFile0v1

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

'''
class ExportOpenEMSDialog_Test(unittest.TestCase):
    def setUp(self):
        self._instance = QApplication([])

    def tearDown(self):
        #self._instance.quit()
        self._instance.exit(0)
        del self._instance
        while not isinstance(QtGui.qApp, None):
            self._instance.exit(0)

    def test_run(self):
        ExportOpenEMSDialog()
'''

_instance = QApplication([])

class PythonScriptLinesGenerator2_Test(unittest.TestCase):
    def setUp(self):
        cadHelpers = FactoryCadInterface.createHelper(APP_DIR)
        path_to_ui = os.path.join(APP_DIR, "ui", "dialog.ui")
        self.form = cadHelpers.loadUI(path_to_ui, _instance)

        #guiHelpers = GuiHelpers(self.form, statusBar = None)
        guiHelpers = DummyGuiHelper()
        self.gen = PythonScriptLinesGenerator2(form=self.form, guiHelpers=guiHelpers)

    def tearDown(self):
        _instance.quit()
        _instance.exit(0)
        #del _instance
        super(PythonScriptLinesGenerator2_Test, self).tearDown()

    def test_create(self):
        pass

    def test_create_file_blank(self):
        for s in [
                self.gen.getCoordinateSystemScriptLines(),
                (self.gen.getMaterialDefinitionsScriptLines(items=[], outputDir=None, generateObjects=True)),
                (self.gen.getCartesianOrCylindricalScriptLinesFromStartStop(bbCoords=BBox(0,1,0,1,0,1), startPointName=None, stopPointName=None)),
                (self.gen.getInitScriptLines()),
                (self.gen.getExcitationScriptLines(False)),
                (self.gen.getExcitationScriptLines(True)),
                (self.gen.getBoundaryConditionsScriptLines()),
                (self.gen.getMinimalGridlineSpacingScriptLines())]:
            print(s)
            assert(len(s)==0 or s[-1] == '\n')
            #assert(s[0] == '\n')
        # print(self.gen.writeNf2ffButtonClicked())
        # print(self.gen.drawS11ButtonClicked())
        # print(self.gen.drawS21ButtonClicked())

        try:
            self.gen.generateOpenEMSScriptString()
        except UserWarning:
            pass

    def test_create_file(self):
        try:
            self.gen.generateOpenEMSScript(outputDir="./")
        except UserWarning:
            pass

class IniValidator_Test(unittest.TestCase):
    def setUp(self):
        self.validator = IniValidator0v1()

    def tearDown(self):
        _instance.quit()
        _instance.exit(0)
        #del _instance

    def test_create(self):
        pass

    def test_stored(self):
        self.validator.checkFile(str(Path("data") / "aaaaa.ini"))


class IniFile0v_Test(unittest.TestCase):
    def setUp(self):
        cadHelpers = FactoryCadInterface.createHelper(APP_DIR)
        path_to_ui = os.path.join(APP_DIR, "ui", "dialog.ui")
        self.form = cadHelpers.loadUI(path_to_ui, _instance)

        #guiHelpers = GuiHelpers(self.form, statusBar = None)
        guiHelpers = DummyGuiHelper()
        self.gen = PythonScriptLinesGenerator2(form=self.form, guiHelpers=guiHelpers)
        self.validator = IniValidator0v1()

        self.reader = IniFile0v1(form=self.form)

    def tearDown(self):
        _instance.quit()
        _instance.exit(0)
        #del _instance

    def test_create(self):
        pass

    def test_read_generate(self):
        '''
        Read file and export python
        '''
        fname = str(Path("data") / "aaaaa.ini")
        self.reader.read(fname)
        _, fileName = self.gen.generateOpenEMSScript(outputDir="./")

    def test_read_generate_fixed_grid(self):
        '''
        Read file and export python
        '''
        fname = str(Path("data") / "fixed-distance-grid.ini")
        self.reader.read(fname)
        _, fileName = self.gen.generateOpenEMSScript(outputDir="./")


if __name__ == "__main__":
    unittest.main()
