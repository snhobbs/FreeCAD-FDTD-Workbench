from utilsOpenEMS.GuiHelpers.CadInterface import CadInterface

class FactoryCadInterface:

    @staticmethod
    def createHelper(APP_DIR = ""):
        interfaceInstance = CadInterface()
        if interfaceInstance.type == "FreeCAD":
            from  utilsOpenEMS.GuiHelpers.FreeCADHelpers import FreeCADHelpers
            return FreeCADHelpers(APP_DIR)
        return CadInterface(APP_DIR)
