from .SettingsItem import SettingsItem
import math
import numpy as np
import logging


_log = logging.getLogger("freecad-openems")

# Grid settings class
# Fixed Count    - fixed number per axes
# Fixed Distance - gridlines have fixed distance between them
# User Defined   - user has to provide coordinates where lines should be


class GridSettingsItem(SettingsItem):
    cartesianCylindricCoordsAlternativeValues = [
        ("x+", "r+"),
        ("x-", "r-"),
        ("x", "r"),
        ("y+", "theta+"),
        ("y-", "theta-"),
        ("y", "theta"),
        ("XY plane, top layer", "r-theta, top layer"),
        ("XY plane, bottom layer", "r-theta, bottom layer"),
        ("XZ plane, front layer", "z-theta, outside layer"),
        ("XZ plane, back layer", "z-theta, inside layer"),
        (
            "YZ plane, right layer",
            "z-theta, outside layer",
        ),  # cylindrical has just 2 independent planes so this is repeating
        (
            "YZ plane, left layer",
            "z-theta, inside layer",
        ),  # cylindrical has just 2 indipendent planes so this is repeating
        ("XY plane", "r-theta plane"),
        (
            "XZ plane",
            "z-theta plane",
        ),  # cylindrical has just 2 independent planes so this is repeating
        (
            "YZ plane",
            "z-theta plane",
        ),  # cylindrical has just 2 independent planes so this is repeating
    ]

    lumpedPortCartesianExcitationDirection = ["z", "x", "y"]
    multilayeredPortCartesianLayerDirection = [
        "XY plane, top layer",
        "XY plane, bottom layer",
        "XZ plane, front layer",
        "XZ plane, back layer",
        "YZ plane, right layer",
        "YZ plane, left layer",
    ]
    multilayeredPortCartesianPropagationDirection = ["x+", "x-", "y+", "y-", "z+", "z-"]

    lumpedPortCylindricalExcitationDirection = ["z", "r", "theta"]
    multilayeredPortCylindricalLayerDirection = [
        "r-theta, top layer",
        "r-theta, bottom layer",
        "z-theta, outside layer",
        "z-theta, inside layer",
    ]
    multilayeredPortCylindricalPropagationDirection = [
        "r+",
        "r-",
        "theta+",
        "theta-",
        "z+",
        "z-",
    ]

    multilayeredSymmetricPortCartesianLayerDirection = [
        "XY plane",
        "XZ plane",
        "YZ plane",
    ]
    multilayeredSymmetricPortCylindricalLayerDirection = [
        "r-theta plane",
        "z-theta plane",
        "z-theta plane",
    ]

    def __init__(
        self,
        name="",
        type="",
        gridOffset=None,
        fixedCount=None,
        fixedDistance=None,
        userDefined=None,
        units="mm",
        unitsAngle="deg",
        xenabled=False,
        yenabled=False,
        zenabled=False,
        smoothMeshDefault=None,
        coordsType="rectangular",
    ):
        self.name = name
        self.type = type
        self.coordsType = coordsType
        self.units = units
        self.unitsAngle = unitsAngle
        self.xenabled = xenabled
        self.yenabled = yenabled
        self.zenabled = zenabled

        self.fixedCount = {"x": 0, "y": 0, "z": 0} if fixedCount is None else fixedCount
        self.fixedDistance = (
            {"x": 0, "y": 0, "z": 0} if fixedDistance is None else fixedDistance
        )
        self.smoothMesh = (
            {"xMaxRes": 0, "yMaxRes": 0, "zMaxRes": 0}
            if smoothMeshDefault is None
            else smoothMeshDefault
        )
        self.userDefined = {"data": ""} if userDefined is None else userDefined

        self.generateLinesInside = False
        self.gridOffset = (
            {"x": 0, "y": 0, "z": 0, "units": "um"}
            if gridOffset is None
            else gridOffset
        )

        self.topPriorityLines = True

    # Return xyz distances, count or user defined array based what user asked for.
    def getXYZ(self, referenceUnit=1):
        if self.type == "Fixed Count":
            return self.fixedCount
        if self.type == "Fixed Distance":

            def dict_mult(d, x):
                return {n: d[n] * x for n in d.keys()}

            return dict_mult(
                self.fixedDistance, self.getUnitsAsNumber(self.units) / referenceUnit
            )
        if self.type == "User Defined":
            return self.userDefined["data"]
        if self.type == "Smooth Mesh":
            return self.smoothMesh

    def getUnitAsScriptLine(self):
        return str(self.getUnitsAsNumber(self.units))

    def getSettingsUnitAsNumber(self):
        """
        :return: Self units as float number, ie.:
                mm -> 1.0e-3
                m  -> 1.0
        """
        return self.getUnitsAsNumber(self.units)

    def getGridOffset(self):
        return (
            self.gridOffset
            if self.generateLinesInside
            else {"x": 0, "y": 0, "z": 0, "units": "um"}
        )

    def getCartesianAsCylindricalCoords(
        self, bbCoords, xmin, xmax, ymin, ymax, zmin, zmax
    ):
        # radius must be chosen from all corners
        polarR1 = (xmin**2 + ymin**2) ** 0.5
        polarR2 = (xmax**2 + ymax**2) ** 0.5
        polarR3 = (xmin**2 + ymax**2) ** 0.5
        polarR4 = (xmax**2 + ymin**2) ** 0.5

        # theta must be chosen from all corners
        polarTheta1 = math.atan2(ymin, xmin)
        polarTheta2 = math.atan2(ymax, xmax)
        polarTheta3 = math.atan2(ymin, xmax)
        polarTheta4 = math.atan2(ymax, xmin)

        #
        #   THERE IS DIFFERENCE WHEN COORD ORIGIN xy (0,0) IS INSIDE OBJECT SO HERE IS LITTLE REASSIGN if that happen
        #       x is r (radius) in this case from 0-xmax
        #       y is theta in this case 0-360deg
        #       z stays as it is
        #
        if (
            bbCoords.XMin <= 0
            and bbCoords.YMin <= 0
            and bbCoords.XMax >= 0
            and bbCoords.YMax >= 0
        ):
            #
            #   origin inside object boundaries
            #
            xmin = 0
            xmax = max(polarR1, polarR2, polarR3, polarR4)
            ymin = -math.pi
            ymax = math.pi
        elif np.sign(bbCoords.XMin) == np.sign(bbCoords.XMax) and np.sign(
            bbCoords.YMin
        ) == np.sign(bbCoords.YMax):
            #
            #   object boundaries are in some quarter of XY plane, this is simples OK case
            #
            xmin = min(polarR1, polarR2, polarR3, polarR4)
            xmax = max(polarR1, polarR2, polarR3, polarR4)
            ymin = min(polarTheta1, polarTheta2, polarTheta3, polarTheta4)
            ymax = max(polarTheta1, polarTheta2, polarTheta3, polarTheta4)
        elif np.sign(bbCoords.XMin) == np.sign(bbCoords.XMax) and np.sign(
            bbCoords.YMin
        ) != np.sign(bbCoords.YMax):
            #
            #   object boundaries are crossing X axis
            #
            aux_xmin = xmin
            aux_xmax = xmax

            xmin = min(abs(aux_xmin), abs(aux_xmax))
            xmax = max(abs(aux_xmin), abs(aux_xmax))
            ymin = (
                polarTheta2 - 2 * math.pi if np.sign(bbCoords.XMin) < 0 else polarTheta1
            )
            ymax = polarTheta3 if np.sign(bbCoords.XMin) < 0 else polarTheta4
        elif np.sign(bbCoords.XMin) != np.sign(bbCoords.XMax) and np.sign(
            bbCoords.YMin
        ) == np.sign(bbCoords.YMax):
            #
            #   object boundaries are crossing Y axis
            #
            aux_ymin = ymin
            aux_ymax = ymax

            xmin = min(abs(aux_ymin), abs(aux_ymax))
            xmax = max(abs(aux_ymin), abs(aux_ymax))
            ymin = polarTheta4 if np.sign(bbCoords.YMin) < 0 else polarTheta3
            ymax = polarTheta2 if np.sign(bbCoords.YMin) < 0 else polarTheta1
        else:
            # just for safety to have it right
            _log.warning(
                "%WARNING there is some speecial case like objects are placed on grid and some solution for cylindrical coords for this object was chosen but PROBABLY IS WRONG! check this gridlines manualy please"
            )

            xmin = min(polarR1, polarR2, polarR3, polarR4)
            xmax = max(polarR1, polarR2, polarR3, polarR4)
            ymin = min(polarTheta1, polarTheta2, polarTheta3, polarTheta4)
            ymax = max(polarTheta1, polarTheta2, polarTheta3, polarTheta4)
            print(
                "WARNING: There is strange case of object position for grid generate, some coords for polar grid were generated. Maybe move objects to another place."
            )

        return xmin, xmax, ymin, ymax, zmin, zmax
