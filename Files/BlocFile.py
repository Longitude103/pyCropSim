"""Holds the data contained in the file BLOCK.DAT"""

from HelperIO import ReadFloats
from HelperIO import ReadNextFloat
from HelperIO import ReadNextInteger
from HelperIO import ReadNextSequenceAsFloats
from HelperIO import ReadNextSequenceAsInteger

from Data.Crop import CropId


class BlocFile:
    """Represents the data in the bloc file (BLOCFILE.DAT)"""

    __slots__ = ("ETRFACT", "NFDAY", "YTREND", "DEPTH", "YDENS", "RESRAT", "SPGRAV", "FRAGIL",
                 "RESTYP", "KCL", "KCU", "TBASE", "TCEIL", "SFTMP", "SMFMX", "SMFMN", "SNOCOVMX",
                 "SNOCOV1", "SNOCOV2", "TIMP", "CN", "CNFALLOW", "CC")

    def __init__(self, filename):
        print("Reading BLOC file at: " + filename)
        file = open(filename, "r")

        self.ETRFACT = ReadNextFloat(file)
        """ETR Adjusment Factor used to reduce Penman-Monteith 
        values for HPCC stations and field conditions"""
        self.NFDAY = ReadNextInteger(file)
        """Forecast Period"""
        self.YTREND = ReadNextInteger(file, 1)
        """Yield Trend Flag"""
        # Read the depth of the 10 soil layers in inches
        self.DEPTH = ReadNextSequenceAsFloats(file)
        """SOIL LAYER DEPTHS (in inches)."""
        self.YDENS = ReadNextSequenceAsFloats(file)
        """Yield density (in lb/harvest)."""
        self.RESRAT = ReadNextSequenceAsFloats(file)
        """Ratio of harvest mass to residue mass."""
        self.SPGRAV = ReadNextSequenceAsFloats(file)
        """Specific gravity (Mg/m³) for the residue."""
        self.FRAGIL = ReadNextSequenceAsInteger(file)
        """Type of Residue."""
        self.RESTYP = ReadNextSequenceAsInteger(file)
        """Type of Residue for use in curve number adjustment."""

        self.CC = {}
        """Crop Coefficients."""
        # Now comes 8 series of KCo (Crop Coefficients), see CropId Enum.
        for i in range(7):
            self.CC[CropId(i + 1)] = (ReadNextSequenceAsFloats(file), ReadFloats(file, 10))

        # Read Alfalfa Crop Coefficients
        self.CC[CropId.Alfalfa] = (ReadNextSequenceAsFloats(file), ReadFloats(file, 10),
                                   ReadFloats(file, 10))

        self.KCL = ReadNextSequenceAsFloats(file)
        """Lower limit for crop coefficients."""
        self.KCU = ReadNextSequenceAsFloats(file)
        """Upper limit for crop coefficients."""
        # Read base temperatures
        self.TBASE = ReadNextSequenceAsFloats(file)
        """GDD Base Temperature."""
        self.TCEIL = ReadNextSequenceAsFloats(file)
        """GDD Ceiling Temperature."""

        temps = ReadNextSequenceAsFloats(file)
        self.SFTMP = temps[0]
        """Snowfall temperature (in °F)"""
        self.SMFMX = temps[1]
        """Maximum melt rate for snow during year (June 21) 
        where °F refers to the air temperature  (in °F/day)."""
        self.SMFMN = temps[2]
        """Minimum melt rate for snow during year (Dec 21) 
        where °F refers to the air temperature  (in °F/day)."""
        # SMFMX and SMFMN allow the rate of snow melt to vary through the year.
        # These parameters are accounting for the impact of soil temperature on snow melt.
        self.SNOCOVMX = temps[3]
        """Minimum snow water content that corresponds to 100% snow cover, (in H₂O).
        If the snow water content is less than SNOCOVMX, 
        then a certain percentage of the ground will be bare."""
        self.SNOCOV1 = temps[4]
        """1st shape parameter for snow cover equation.
        This parameter is determined by solving the equation for 50% snow cover."""
        self.SNOCOV2 = temps[5]
        """2nd shape parameter for snow cover equation.
        This parameter is determined by solving the equation for 95% snow cover."""
        self.TIMP = temps[6]
        """Snow pack temperature lag factor (0-1).
        1 = no lag (snow pack temp=current day air temp) as the lag factor goes to zero,
        the snow pack's temperature will be less influenced by the current day's air temperature."""
        # READ CURVE NUMBERS FOR ANTECEDENT MOISTURE CONDITION
        # VALUES ARE FOR EACH CROP AND FOUR HYDROLOGIC CONDITIONS
        # TOASK: CNFALLOW could be added to CN with it's corresponding CropId(0) key
        self.CN = {}
        """Curve numbers for each crop type."""
        self.CNFALLOW = ReadNextSequenceAsFloats(file)
        """Curve number for Fallow - Bare Soil for each 4 hydrological condition."""
        for i in range(22):
            self.CN[CropId(i + 1)] = ReadNextSequenceAsFloats(file)

        file.close()
