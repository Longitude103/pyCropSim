"""Module defining crop related objects."""

from aenum import IntEnum
from Files.DataFile import DataRow

TuberCropTypes = (4, 5)
"""The index for tuber crop types."""

GrainCropTypes = (1, 2, 3, 6, 7, 8, 9)
"""The index for grain crop types."""

NaturalCropTypes = (16, 18, 19, 20, 21)
"""The index for natural crop types."""

OutputNames = ('SM.GRAIN', 'ED BEANS', 'SOYBEANS', 'POTATOES',
               'S. BEETS', 'SORGHUM', 'W. WHEAT', 'CORN', 'SUNFLOWR', 'ALFALFA',
               'IRR HAY', 'IRR PAST', 'N. RANGE', 'TURF', 'FALLOW', 'R. WOODS',
               'NR. WOOD', 'CATTAILS', 'REED/RUSH', 'SHAL H2O', 'DEEP H2O', 'FARMSTED')
"""Crop names for the output files."""

LegacyNames = ('SM.GRAIN', 'ED BEANS', 'SOYBEANS', 'POTATOES',
               'S. BEETS', 'SORGHUM', 'W. WHEAT', 'CORN', 'SUNFLOWR', 'ALFALFA',
               'IRR HAY', 'IRR PAST', 'N. RANGE', 'TURF', 'FALLOW', 'R. WOODS',
               'NR. WOOD', 'CATTAILS', 'REED/RUS', 'SHAL H2O', 'DEEP H2O', 'FARMSTED')
"""The crop names the Fortan app were actually using for the output files."""

Codes = ("SGRA", "BEAN", "SOYB", "POTA",
         "BEET", "SORG", "WHEA", "CORN", "SUNF", "ALFA",
         "IRRI", "", "NATV")

Suffixes = ("DRCT", "IRCT", "PAST")
"""Suffixes found for .WEA files."""

class CropId(IntEnum):
    """Enumeration of the crop types."""
    Undefined = -1
    FallowBarSoil = 0
    SpringGrains = 1
    EdibleBeans = 2
    Soybeans = 3
    Potatoes = 4
    SugarBeets = 5
    GrainSorghum = 6
    WinterWheat = 7
    Corn = 8
    Sunflower = 9

    Alfalfa = 10
    IrrigatedHay = 11

    IrrigatedPasture = 12
    NativePastureGrass = 13

    UrbanTurf = 14
    SummerFallow = 15
    RiparianWoodlands = 16
    NonRiparianWoodlands = 17
    Cattails = 18
    ReedRush = 19
    ShallowWater = 20
    DeepWater = 21
    Farmstead = 22

    def isGrain(self) -> bool:
        """Returns True if the crop type is a grain crop."""
        return self.value in GrainCropTypes

    def isGrainOrTuber(self) -> bool:
        """Returns True is the crop is grain or tuber (< 10)"""
        return self < 10

    def isGrainTuberOrForage(self) -> bool:
        """Returns True is the crop is grain or tuber (< 10)"""
        return self < 12

    def isForage(self) -> bool:
        """Returns True if the crop type is forage. Alfalfa or Irrigated Hay. (10, 11)"""
        return 9 < self < 12

    def isPasture(self) -> bool:
        """Returns True if the crop type is Pasture, False otherwise."""
        return 11 < self < 14

    def isNatural(self) -> bool:
        """Returns True if the crop type is natural."""
        return self.value in NaturalCropTypes

    def requiresYieldAdjustment(self) -> bool:
        """Returns True if the crop type requires yield adjustment. (< 12)"""
        return self < 12

    def getName(self, legacy: bool = False) -> str:
        """Returns the crop names for compliant reports."""
        return LegacyNames[self - 1] if legacy else OutputNames[self - 1]

class Crop(DataRow):
    """Simulation info for a crop type."""
    __slots__ = ("SIMFILE", "YR", "Index", "WEAFILE")

    def __init__(self, sim_file: str, year: int, index: int):
        self.YR = year
        """The year."""
        self.Index = index
        """The 0-based index of this crop simulation in the CROPFILE."""
        # TONOTE: This index equals to II and ISIM during the simulation,
        # but they are 0-based index here.
        self.SIMFILE = sim_file
        """The name of the .SIM file."""
        self.WEAFILE = ""
        """Stores the name of the weather data file."""

    def __str__(self):
        return f"{self.SIMFILE},{self.YR}"

    def __eq__(self, other):
        if not isinstance(other, Crop): return False
        return self.SIMFILE == other.SIMFILE and self.YR == other.YEAR
