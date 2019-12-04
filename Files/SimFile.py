"""Simulation file module."""

import copy

from HelperIO import ReadNextFloat
from HelperIO import ReadNextInteger
from HelperIO import ReadIntegersInLine
from HelperIO import ReadNextSequenceAsFloats

from Data.GDD import GddData

from Data.Crop import CropId
from Data.Tillage import TillageFlags, TillageOperation
from Data.Irrigation import IrrigationData
from Data.Irrigation import IrrigationTypes

class SimFile:
    """Represents a simulation .SIM file."""
    __slots__ = ("CHAND", "CHANW", "CROP", "DDEPTH", "EAPP", "EREUSE", "GDD", "GDDROOT", \
        "IDBG", "IDEND", "IDPLT", "IMBG", "IMEND", "IMPLT", "ITERRC", "ITFLAG", "IYIELD", \
        "Irrigation", "JDFREQ", "JDYCUT", "JGOI", "JSTOPI", "LAYERS", "NCUT", "NTILLS", "PRUNOF", \
        "RZMAX", "RZMGMT", "RZMIN", "TBREAK", "TINTRV", "TillageOperations", "YCOEFF", "YMAX", \
        "_ITFLAG", "_RZMAX", "_RZMGMT", "_TILL")
    # TODO: Find the values in the .SIM files that are modified during the simulation:
    # IMPLT, IDPLT, TillageOperations[i].TILDAY

    def __init__(self, filename: str = None):
        self.JDFREQ = 0
        """DELIVERY FREQUENCY, DAYS."""
        self.DDEPTH = 0.0
        """DELIVERY DEPTH, in inches."""

        if filename is None: return

        print("Reading SIMFILE file at: " + filename)
        file = open(filename, "r")

        # See line 821 in Fortran code
        # Read The Setup Values From The SIM Files
        self.CROP = CropId(ReadNextInteger(file))
        """Crop Type."""
        self.LAYERS = ReadNextInteger(file, 1)
        assert self.LAYERS == 10

        # TODO: This member is modified, check the ramifications.
        self.IMPLT = ReadNextInteger(file)
        # TODO: This member is modified, check the ramifications.
        self.IDPLT = ReadNextInteger(file)
        self.IMBG = ReadNextInteger(file)
        self.IDBG = ReadNextInteger(file)
        self.IMEND = ReadNextInteger(file)
        self.IDEND = ReadNextInteger(file, 1)

        self.JDYCUT = []
        self.GDD = GddData()
        if self.CROP < CropId.Alfalfa:
            self.GDD.VEG = ReadNextFloat(file)
            self.GDD.FLO = ReadNextFloat(file)
            self.GDD.RIPE = ReadNextFloat(file)
            self.GDD.YFORM = ReadNextFloat(file)
            self.GDD.EFC = ReadNextFloat(file)
            self.GDD.MAT = ReadNextFloat(file)
        elif self.CROP < 12:
            # Read Cutting Dates For Alfalfa And Irrigated Hay
            self.NCUT = ReadNextInteger(file)
            """Number of cuttings."""
            for _ in range(5):
                self.JDYCUT.append(ReadNextInteger(file))
        else:
            # Read GDD For Effective Cover And Maturity For Other Plantings
            self.GDD.EFC = ReadNextFloat(file)
            self.GDD.MAT = ReadNextFloat(file)
        _ = file.readline()

        # Read Root Depth data, line 839
        self.RZMIN = ReadNextFloat(file)
        self.RZMAX = ReadNextFloat(file)
        self._RZMAX = self.RZMAX
        self.TBREAK = ReadNextFloat(file)
        self.GDDROOT = ReadNextFloat(file)
        self.RZMGMT = ReadNextFloat(file, 1)
        self._RZMGMT = self.RZMGMT

        self.IYIELD = ReadNextInteger(file)
        self.YMAX = ReadNextFloat(file)
        self.YCOEFF = ReadNextFloat(file, 1)

        # (842-851) Adjustment is done at the moment of loading the file into the simulation.

        # Read terrace parameters
        self.ITERRC = ReadNextInteger(file)
        self.CHAND = ReadNextFloat(file)
        self.CHANW = ReadNextFloat(file)
        self.TINTRV = ReadNextFloat(file, 1)

        # Read tillage operation
        itemp = ReadIntegersInLine(file)
        self.NTILLS = itemp[0]
        """Number of tillage operations."""
        # TODO: This member is modified, check the ramifications.
        self.ITFLAG = TillageFlags(itemp[1])
        """Tillage code."""
        self._ITFLAG = self.ITFLAG
        self.TillageOperations = []
        for _ in range(self.NTILLS):
            itemp = ReadIntegersInLine(file)
            self.TillageOperations.append(TillageOperation(itemp[0], itemp[1], itemp[2]))
        self._TILL = copy.deepcopy(self.TillageOperations)

        # Read irrigation data
        self.Irrigation = IrrigationData(file)
        # Read Frequency For Rotation System And The Depth Delivered.
        # For Alfalfa/Pasture/Hay Can Simulate An Iterruption Of Supply
        # For During The Summer When Water Is Applied To Row Crops
        if self.Irrigation.IRRSCH == 3:
            if not (self.CROP >= 10 and self.CROP <= 13):
                self.JSTOPI = ReadNextInteger(file)
                self.JGOI = ReadNextInteger(file)
            self.JDFREQ = ReadNextInteger(file)
            self.DDEPTH = ReadNextFloat(file, 1)

        self.EAPP = ReadNextSequenceAsFloats(file)
        """Application efficiency."""
        self.EREUSE = ReadNextSequenceAsFloats(file)
        """Reuse efficiency."""
        self.PRUNOF = ReadNextSequenceAsFloats(file)
        """Runoff Percentage."""

        # 912
        # For Simulating Known Irrigation Dates, read historical data.
        if self.Irrigation.IRRTYP == IrrigationTypes.HistoricalDates:
            # TODO: Check FDFILE path declaration and format.
            # TOASK: This case seems to never happen on any of the .SIM files provided
            # I would not implement this if I cannot check the input source format.
            FDFILE = file.readline().strip()
            print("FDFILE path read from .SIM: " + FDFILE)
            raise NotImplementedError

        file.close()

    def restore(self):
        """Restores the overwritten values as they were read from the file."""
        # TODO: Check restoring.
        self.RZMAX = self._RZMAX
        self.RZMGMT = self._RZMGMT
        self.ITFLAG = self._ITFLAG
        self.TillageOperations = copy.deepcopy(self._TILL)
