"""Irrigation module."""

from aenum import IntEnum
from HelperIO import ReadNextInteger, ReadNextFloat, ReadNextSequenceAsFloats, ReadFloats

class IrrigationTypes(IntEnum):
    """Irrigation type, IRRTYP"""
    Undefined = 0
    DryLand = 1
    HistoricalDates = 2
    Pivots = 3
    Furrow = 4
    BorderCorrugation = 5

    def isIrrigated(self):
        """Return True if the irrigation type is other than DryLand (> 1)."""
        return self > 1

class IrrigationSchedulingMethods(IntEnum):
    """Irrigation scheduling methods, IRRSCH"""
    Undefined = 0
    GroundwaterOrOtherFullDemandSystems = 1
    """Groundwater or other Full Demand Systems"""
    DistrictDemandBasedScheduling = 2
    """District/Demand Based Scheduling"""
    DistrictRotationSystemWithFixedDeliverySchedulesAndGrossDepth = 3
    """
    District/Rotation System With Fixed Delivery Schedules And Gross Depth.
    Don't allow irrigation if before the first delivery date.
    If after November 1st for Alfalfa and Grass ot if after the maturity date for other crops.
    """
    SimulationForKnownFutureWeatherForNOAAProject = 4
    """Simulation for known future weather for NOAA project"""

class IrrigationData:
    """Irrigation data from a .SIM file."""
    __slots = ("IRRTYP", "PAD", "RAINAL", "SYSCAP", "IPER", \
        "APMIN", "APMAX", "SMALLI", "GSTART", "GSTOP", "IRRSCH", "JFIRST")

    def __init__(self, file):
        self.IRRTYP = IrrigationTypes(ReadNextInteger(file))
        """The type of irrigation, defined in IrrigationTypes."""
        self.PAD = ReadNextSequenceAsFloats(file)
        """Percent Allowable Depletion."""
        self.RAINAL = ReadFloats(file, 5)
        """Rainfall allowance for each growth stage."""
        self.SYSCAP = ReadNextFloat(file, 1)
        """System capacity."""
        self.IPER = ReadNextSequenceAsFloats(file)
        """Decimal percent of operating time for each stage."""
        self.APMIN = ReadNextSequenceAsFloats(file)
        """Minimum irrigation application in each stage."""
        self.APMAX = ReadNextSequenceAsFloats(file)
        """Maximum irrigation application in each stage."""
        self.SMALLI = ReadNextSequenceAsFloats(file)
        """Smallest Allowable Irrigation by Grow Stage, in inches."""
        self.GSTART = ReadNextFloat(file)
        """DEGREE DAYS TO START OF IRRIGATION"""
        self.GSTOP = ReadNextFloat(file)
        """DEGREE DAYS OF LAST IRRIGATION"""
        self.IRRSCH = IrrigationSchedulingMethods(ReadNextInteger(file))
        """Irrigation scheduling method, the type of water supply for irrigation."""
        self.JFIRST = ReadNextInteger(file, 1)
        """FIRST DELIVERY DATE, in Julian Days"""
