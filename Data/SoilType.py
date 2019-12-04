"""SoilType module."""

from aenum import IntEnum

class DepthToGroundwaterFlag(IntEnum):
    """Depth to groundwater flags."""
    LessThanSixFeet = 1
    GreaterThanSixFeet = 2


class SoilType:
    """Represents a type of soil."""

    #TONOTE: DRCOE & DRNDAY are not read from the file,
    # but overriden by constants in the code instead DRCOE=DCOFSOIL,DRNDAY=DDAYSOIL
    # Probably values on the file yields more accurate simulation results.

    # 2, 4, 9, 15, 21, 30, 42, 54, 66, 78
    __slots__ = ("ISCODE", "BULKD", "ORGM", "FIELDC", "PWP", "AIRDRY", "DRNCOE", "DRNDAY",\
        "AvailableWaterHoldingCapacity", "HydrologicGroup", "DepthToGroundwaterIndicator", "Index")

    def __init__(self, line):

        values = list(filter(None, line.split()))
        self.PWP = []
        """Permanent wilting point value for the 10 soil layers."""
        self.AIRDRY = []
        """Air dry volumetric water content for top three layers. (2,4,9)"""
        self.FIELDC = []
        """Field capacity (FC) for 10 soil layers. (2,4,9,15,21,30,42,54,66,78)"""
        code = values[0]
        self.ISCODE = int(code)
        """3 Digit Code That Represents
        1. The Available Water Holding Capacity (In Quarter Of Inch/Foot),
        2. Hydrologic Group (1=a,...4=d), And
        3. Depth To Groundwater Indicator (1<6ft, 2>6ft)"""
        self.BULKD = float(values[1])
        """Average bulk density of soil profile (int Mg/m³)."""
        self.ORGM = float(values[2])
        """The organic matter value for the soil type."""
        for i in range(3, 13):
            self.FIELDC.append(float(values[i]))
        for i in range(13, 23):
            self.PWP.append(float(values[i]))
        for i in range(23, 26):
            self.AIRDRY.append(float(values[i]))
        self.DRNCOE = float(values[26])
        """Drainage coefficient."""
        self.DRNDAY = float(values[27])
        """Drainage duration."""
        self.AvailableWaterHoldingCapacity = int(code[0])
        """Available Water Holding Capacity (In Quarter Of Inch/Foot)"""
        self.HydrologicGroup = int(code[1])
        """The hydrologic group for this soil."""
        self.DepthToGroundwaterIndicator = DepthToGroundwaterFlag(int(code[2]))
        """Depth to groundwater indicator."""
