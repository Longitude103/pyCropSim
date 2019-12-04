"""
This is the module to store simulation read and write variables.
ReadOnly variables are structured into their corresponding File or Data classes.
"""

import os

from Data.Crop import Crop
from Data.Crop import CropId
from Data.SoilData import SoilData
from Data.SoilType import SoilType
from Data.SimControl import SimControl
from Data.Irrigation import IrrigationTypes
from Data.WeatherStation import WeatherStation
from Data.Summary import WeeklyData, MonthlyData

from Files.SimFile import SimFile
from Files.BlocFile import BlocFile
from Files.TillageFile import TillageFile
from Files.PrintOutFile import PrintOutFile
from Files.InitialFile import InitialFile
from Files.DataFile import OutputFormats

# Constants
__CROP_COUNT: int = 22
__LAYER_COUNT: int = 10
__SOILSIM_COUNT: int = 28

# Static Data

Config = None
"""Program configuration"""
InitialData: InitialFile = None
"""Initial Data read from the INITIAL.DAT file."""

Sites = {}
"""A dictionary with the site simulation data."""
SoilProps = None
"""A list with the soil types loaded from the SOILPROP file."""

Crops = []

Sim: SimFile = None
Soil: SoilType = None
"""The current simulated soil type."""
Site: SoilData = None
"""The current site in simulation."""
BLOC: BlocFile = None
Tillages: TillageFile = None
Station: WeatherStation = None
Control: SimControl = None
PrintOut: PrintOutFile = None
CurrentCrop: Crop = None

Simulations = []

#Variable Data

IZONE: int = 0
"""The current zone for the simulation."""
LIVECOND: bool = False

ISIM: int = 0
"""Simulation 0-based index"""

# From INITIAL data file
OLDCRP: int = 0
OLDRES: float = 0.0

LIVECROP: bool = False
"""
If LIVECROP = 0, starting with residue/fallow from wheat/other crops
If LIVECROP = 1, starting year with growing wheat
"""



# =====================================================
# PER-LAYER DATA
PERRZD = [0.0]
"""Percent Of Each Layer Filled With Roots."""
RDF = [0.0] * __LAYER_COUNT
"""Root distribution."""
PAWFT = [0.0] * __LAYER_COUNT
"""Plant Available Water for each layer."""
PWP = [0.0] * __LAYER_COUNT
"""Permanent wilting point value for the 10 soil layers."""

CENTER = [0.0] * __LAYER_COUNT
"""The depth at the middle point of the layer.
TONOTE: CENTER: This is actually read-only, calculated on SimFile loading."""

AVMFT = [0.0] * __LAYER_COUNT
"""Available Volumetric Moisture in each layer."""
THETA = [0.0]
"""INITAL VOLUMETRIC WATER CONTENT FOR EACH LAYER.
TONOTE: From INITIAL data file"""
SOILT = [0.0]
"""Average temperature of soil layer (in °F)."""
DEPL = [0.0] * __LAYER_COUNT
"""
Used by ComputeWaterDepletion() and __TranspirationRoutine() on DEPLT.
"""
# PER-LAYER DATA
# =====================================================
# SOIL related.


# SOIL related.
# =====================================================

RESIDUE: float = 0.0
"""Amount of residue on soil surface (in lb/acre)."""

SOIL = 411 # A initial value to perform testing of .SIM files, which relies on this
"""The current soil code for the simulation."""

TOTDEP = 0.0
"""Total depth of soil profile, depth to bottom of soil layer (in inches)."""

# =====================================================

EP, E1, E2 = 0.0, 0.0, 0.0
"""Related to evaporation stages."""

# =====================================================
# Dates
TIME: float = 0.0
TODAY: float = 0.0
JNEXTI: float = 0.0


JDAY: int = 0
"""Current Julian Day of the simulation."""
IYEAR: int = 0
"""Current year of the simulation."""

JDYSTR: int = 0
"""First day of weather data."""
JDYBG: int = 0
"""First day of simulation."""
JDYEND: int = 0
"""Last day of simulation."""
JDYPLT: int = 0
"""Day of planting of wheat in the fall."""
JDYMAT: int = 0
"""Day of maturity."""
JDYFRZ: int = 0
"""Freeze Date"""
JDYEFC: int = 0
"""Day to effective cover."""
JDYFLO: int = 0
"""Day of start of flowering stage."""
JDYRIPE: int = 0
"""Ripe Day."""
JDYVEG: int = 0
"""Day of start of vegetative stage."""

JFPLT: int = 0
"""Day the wheat is planted in the fall."""
# Date related
# =====================================================

# =====================================================
# DAILY DATA
TMAX = []
"""Maximum temperature (in °F)."""
TMIN = []
"""Minimum temperature (in °F)."""
PRECIP = [0.0]
"""Recorded precipitation (in inches)."""

SOLAR = [0.0]

ETR = [0.0]
CROPKC = [0.0]
"""Daily value of Crop Coefficient."""


# DAILY DATA
# =====================================================

# =====================================================
# SEASONAL DATA

KSTG: int = 0
"""Growth stage index."""
ICUT: int = 0


SNIRR = 0.0
"""Seasonal net irrigation."""
SGRIRR = 0.0
"""Seasonal gross irrigation."""
TDEFS = 0.0
"""Seasonal transpiration deficit."""

TPS = []
"""Seasonal potential transpiration."""
TDEF = []
"""Transpirational deficit during each stage."""


# SEASONAL DATA
# =====================================================

PAW = 0.0
"""Current Plant Available Water."""
AWATER = 0.0

GDD = 0.0
"""Current GDD in the simulation."""

#Initialized on READWEAT
GDDS: list
"""Accumulated GDD"""


# Yield used in lines:
# 1119: PROGRAM: Assigned to 0.0 if ITFLAG > 0
# 1170: PROGRAM: Written to REP RIVER output file.
# 1203: PROGRAM: Written to unit 13
# 1274, 1285: PROGRAM: Written to unit 7
# 2157: DEPLT: Read after calling YIELDS
YIELD = 0.0
ETYLD = 0.0
ETMAX = 0.0
BVALUE = 0.0
YLDRATIO = 0.0

# From EFPRECIP
EPRECIP = 0.0
PRECIPS = 0.0
EPRECIPS = 0.0

RUNON = 0.0
"""Depth of water that runs onto terrace channel, (in inches)"""
RUNOFF = 0.0
"""Depth of water that runs off, (in inches)"""


# Soil related


DINF = 0.0
"""The depth of water that infiltrated."""


# =====================================================
# Snow parameters
SNOTMP = 0.0
"""Temperature of snow pack (in °F)."""
SNOH2O = 0.0
"""Amount of water in snow (in inches H20)"""

# TONOTE: SNOFALL not is actually used, only assigned in one statement, never used.
#SNOFALL = 0.0
#"""Amount of water in snow on current day (in H₂O)."""
# =====================================================

TANUAL = 0.0
"""Average annual air temperature, (in °C)."""
TAVG = 0.0
"""Average temperature of the day (in °F)."""
RAIN = 0.0
"""Daily rain (in inches)"""


ALPHA1 = 0.0 #in lines 137, 914, 934, 1477, 1478 (Move it to the SimFile (?))

CURVNO = 0.0
"""Curve Number from EFPRECIP"""

# Adjusted values, always use these instead of those in the SimFile.
RZMAX: float
RZMGMT: float

KC = 0.0
"""Crop Coefficient."""

# Irrigation related
IRIGNO = 0
"""Number os irrigations."""
NETIRR = 0.0
"""Net irrigation."""
GROIRR = 0.0
"""Gross irrigation."""

DPLA = 0.0
DPLN = 0.0
AWDPLN = 0.0
"""Allowable depletion."""


MON = [MonthlyData()]
"""Monthly data array."""
WEEK = [WeeklyData()]
"""Weekly data array."""

TOTWAT = 0.0
"""Amount of water stored in soil profile, (in inches H₂O)."""
DRAIND = 0.0
"""Drainage time for current soil."""
DCOEFF = 0.0
"""Drainage coefficient for current soil."""
DRAINS = 0.0
"""Total drainage."""

RZD = 0.0
ETS = 0.0


FDIRRIG = []
"""2-dimensional array for storing historical data."""

SATWC = 0.0
"""Saturated soil water content."""

LASTSIMF, LASTYR = "", 0
DPLBG: float = 0.0
IEFC: int = 0
PCT: float = 0.0
GDDCUT: float = 0.0

# I/O section

outFile = None
yearFile = None
monthFile = None
precipFile = None
profileFile = None

def openMonFile():
    """Returns the path to the monthly summary output file."""
    global monthFile

    monthFilename: str = None
    if Config.OUTPUT_FORMAT == OutputFormats.REPRIVER:
        dirPath = os.path.join(Config.OUTDIR)
        if not os.path.isdir(dirPath): os.makedirs(dirPath, exist_ok=True)
        monthFilename = os.path.join(dirPath, \
            f"{Control.WSITE}{CurrentCrop.YR}{Soil.ISCODE}_MON.TXT")
    # Defaulting to COHYST
    #if Config.OutputFormat == OutputFormats.COHYST:
    dirPath = os.path.join(Config.OUTDIR, "Mon")
    if not os.path.isdir(dirPath): os.makedirs(dirPath, exist_ok=True)
    monthFilename = os.path.join(dirPath, f"{Control.WSITE}_MON.TXT")
    monthFile = open(monthFilename, "at")
    return monthFilename

def openYearFile():
    """Returns the path to the monthly summary output file."""
    global yearFile

    dirPath = os.path.join(Config.OUTDIR, "YR")
    if not os.path.isdir(dirPath): os.makedirs(dirPath, exist_ok=True)
    yearFilename: str = os.path.join(dirPath, f"{Control.WSITE}_YR.TXT")
    yearFile = open(yearFilename, "wt")
    return yearFilename

def openPrecipFile():
    """Returns the path to the precipitation output file."""
    global precipFile

    dirPath: str = os.path.join(Config.OUTDIR, "Precip")
    if not os.path.isdir(dirPath): os.makedirs(dirPath, exist_ok=True)
    precipFilename = os.path.join(dirPath, f"{Control.WSITE}_PRECIP.CSV")
    precipFile = open(precipFilename, "at")
    return precipFilename

def openOutFile():
    """Opens the OUT file for appending."""
    global outFile

    filename = os.path.join(Config.OUTDIR, f"{Control.WSITE}_OUT.TXT")
    outFile = open(filename, "at")

def openProfileFile():
    """Opens the PROFILE file for appending."""
    global profileFile

    filename = os.path.join(Config.OUTDIR, "PROFILE.TXT")
    profileFile = open(filename, "at")

def closeFiles():
    """Closes the output files."""
    global monthFile, yearFile, precipFile, outFile, profileFile

    if yearFile:
        yearFile.close()
        yearFile = None
    if monthFile:
        monthFile.close()
        monthFile = None
    if precipFile:
        precipFile.close()
        precipFile = None
    if outFile:
        outFile.close()
        outFile = None
    if profileFile:
        profileFile.close()
        profileFile = None

def writeInitialFile(filename, newLine="\n"):
    """Writes the data in the structure to the file specified."""
    file = open(filename, "wt")

    file.write("  ")
    for _, theta in enumerate(THETA):
        file.write(f"{theta}:4.3f")
    file.write(newLine)

    file.write(f"  {int(Sim.CROP):4}  {RESIDUE:7.1f}  {int(LIVECROP):4}{newLine}")
    file.write(f"  {SNOTMP:8.1f}    {SNOH2O:6.2f}    ")
    for _, soilt in enumerate(SOILT):
        file.write(f"{soilt}:5.1f")
    file.write(newLine)

    file.close()

def writeYearRow():
    """Writes the current year row to output YR file."""
    cropName = Sim.CROP.getName(Config.LEGACY)
    
    IRR = Sim.Irrigation
    line: str = None
    TOTROF: float = 0.0
    JFIRST = IRR.JFIRST
    if Config.OUTPUT_FORMAT == OutputFormats.REPRIVER:
        IMPLT = Sim.IMPLT
        IDPLT = Sim.IDPLT
        # FORMAT(A4,',',A8,8(',',I5),',',F9.2,3(',',F7.2),',',F6.3,
        # 2(',',F7.2),',',I5,3(',',F6.2),',',F8.2,',',A10)
        line = (f"{Site.NWSITE:>4},{CurrentCrop.SIMFILE:>8},{SOIL:>5},{IYEAR:>5},"
                f"{IMPLT:>5},{IDPLT:>5},{JFIRST:>5},{JDYEFC:>5},{JDYMAT:>5},{JDYFRZ:>5},"
                f"{YIELD:>9.2f},{ETS:>7.2f},{ETYLD:>7.2f},{BVALUE:>7.2f},{YLDRATIO:>6.3f},"
                f"{SGRIRR:>7.2f},{SNIRR:>7.2f},{IRIGNO:>5},{PRECIPS:>6.2f},{EPRECIPS:>6.2f}"
                f",{DRAINS:>6.2f},{DPLBG:>8.2f},  {cropName:<8}\n")
    else:
        # Perform wheat/fallow rotation (?)
        if LIVECROP and Sim.CROP == CropId.WinterWheat and Sim.ITFLAG != 3 and \
            Sim.Irrigation.IRRTYP == IrrigationTypes.DryLand:
            Sim.CROP = CropId.SummerFallow
        ITFLAG = Sim.ITFLAG
        IRRTYP = IRR.IRRTYP
        # compute annual runoff
        for i in range(Sim.IMBG - 1, Sim.IMEND):
            TOTROF += MON[i].ROF
        # FORMAT(1X,A4,2X,A8,1X,8I5,F8.1,2X,3F7.2,I5,2X,4F6.2,2X,A10, 3I3, F7.2)
        line = (f" {Site.NWSITE:>4}  {CurrentCrop.SIMFILE:>8} {SOIL:>5}{IYEAR:>5}"
                f"{JDYPLT:>5}{JFIRST:>5}{JFIRST:>5}{JDYEFC:>5}{JDYMAT:>5}{JDYFRZ:>5}"
                f"{YIELD:>8.1f}  {ETS:>7.2f}{SGRIRR:>7.2f}{SNIRR:>7.2f}{IRIGNO:>5}  "
                f"{PRECIPS:>6.2f}{EPRECIPS:>6.2f}{DRAINS:>6.2f}{DPLBG:>6.2f}    "
                f"{cropName:<8}{Sim.CROP:>3}{ITFLAG:>3}{IRRTYP:>3}{TOTROF:>7.2f}\n")
        print(line)

        if LIVECROP and Sim.CROP == CropId.SummerFallow and Sim.ITFLAG != 3 and \
            Sim.Irrigation.IRRTYP == IrrigationTypes.DryLand:
            Sim.CROP = CropId.WinterWheat

    yearFile.write(line)
