"""Main simulation module."""

import os
from math import exp

import SIM

from Subroutines.DAYS import DAYOFYR
from Subroutines.YIELDS import YIELDS
from Subroutines.READWEAT import READWEAT
from Subroutines.DEPLT import DEPLT

from Data.Crop import Crop, CropId
from Data.Tillage import TillageFlags
from Data.Tillage import TillageOperation
from Data.SimControl import SimControl
from Data.Irrigation import IrrigationTypes

from Files.SimFile import SimFile
from Files.InputSummary import PrintInputSummary


def initSimulation(sim: SimControl):
    """Initializes the simulation parameters and returns the list of crops to simulate."""
    SIM.Control = sim
    if SIM.IZONE != sim.IZONE:
        SIM.IZONE = sim.IZONE
        SIM.Crops = SIM.Config.openCropFile(SIM.IZONE).Rows

    SIM.Site = SIM.Sites[sim.WSITE]
    return SIM.Site

def initSoilSimulation(soilKey: int, soilIndex: int):
    """Init simulation for the specified soil."""
    
    SIM.SOIL = soilKey
    SIM.Soil = SIM.SoilProps[soilIndex]
    print(f"{soilIndex}\tWEATHER SITE: {SIM.Control.WSITE}\tSOIL: {soilKey}")


def initCropSimulation(crop: Crop):
    """Initializes the simulation for the specified crop data row."""

    crop.WEAFILE = f"{SIM.Control.WSITE}{crop.YR}"
    print(f"{crop.Index}\t{crop.SIMFILE}\t{crop.WEAFILE}\t{crop.YR}")
    SIM.CurrentCrop = crop
    SIM.IYEAR = crop.YR
    
    # TONOTE: @765, II is the index from the crop list, simulated or skipped
    # TOASK: It doesn't makes more sense to check the live condition
    # against the index of simulated crops ?
    SIM.ISIM, SIM.IRIGNO = crop.Index, 0
    # Set initial condition for live crops for wheat when 
    # simulating the second sequence of a wheat-fallow rotation
    SIM.LIVECOND = SIM.ISIM > 0 and crop.YR < SIM.LASTYR and crop.SIMFILE == SIM.LASTSIMF
    SIM.LASTSIMF, SIM.LASTYR = crop.SIMFILE, crop.YR



def loadSimulationFiles():
    """Loads the .WEA and .SIM for the current simulation."""
    
    simFilename = os.path.join(SIM.Config.getZonePath(SIM.IZONE), \
       f"{SIM.CurrentCrop.SIMFILE}.SIM")
    
#    if simFilename == SIM.LASTSIMF:
#        reloadLastSimFile()
#    else:
    loadSimFile(SimFile(simFilename))

    initSoilData()

    setInitialConditions()

    READWEAT(SIM.Site.NWSITE, SIM.CurrentCrop.YR)

    # @ 1049
    #initTillageDays()

    initTillageDaysWithBranches()

    # @ 1079
    openOutputFiles()

def performSimulation():
    """Performs the simulation."""
    loadSimulationFiles()
    # @1110
    DEPLT()
    # @1114
    calculateYield()

    rewriteInitFile()

    # Do Output @1165~1215
    SIM.writeYearRow()

    if SIM.PrintOut.IPFLAG > 3:
        PrintInputSummary()

    SIM.closeFiles()


def loadSimFile(file: SimFile):
    """Loads the specified .SIM file into the global data module."""
    SIM.Sim = file
    SIM.RZMAX = file.RZMAX
    SIM.RZMGMT = file.RZMGMT

    if file.Irrigation.IRRTYP != IrrigationTypes.HistoricalDates:
        SIM.ALPHA1 = 0.0

    # Adjust the maximum and management root depths based on the soil type.
    # Depths are reduced for soils in the 300-600 series.
    if not file.CROP.isPasture():
        # soilRz is the Available Water Holding Capacity (In Quarter Of Inch/Foot)
        # encoded as the first digit of the digit code
        # TONOTE: Here soilRz is a float that takes 4.11 from the soil code
        # 
        soilRz = SIM.Soil.AvailableWaterHoldingCapacity
        rzFact = min((0.6 + 0.4*(float(soilRz) - 3.0)/4.0), 1.0)
        SIM.RZMAX *= rzFact
        SIM.RZMGMT *= rzFact

def initSoilData():
    """Initialize soil data."""

    loadInitialData()

    # @976 
    SIM.SATWC = 1.0 - SIM.Soil.BULKD / 2.65
    
    SIM.PWP = SIM.Soil.PWP[:]
    # DRNCOE & DRNDAY are found in Soil properties.
    SIM.TOTDEP, SIM.DPLBG = 0.0, 0.0
    for i in range(SIM.Sim.LAYERS):
        DEPTH: float = SIM.BLOC.DEPTH[i]
        SIM.CENTER[i] = SIM.TOTDEP + DEPTH * 0.5
        RDEPTH: float = SIM.CENTER[i] / SIM.RZMAX
        if RDEPTH > 1.0: RDEPTH = 1.0
        D = exp(-2.303 * RDEPTH ** 4.462)
        # TONOTE: Here PWP is both R/W, I guess the original programmers
        # were aware of the proper order or reading/writing.
        SIM.AVMFT[i] = (SIM.Soil.FIELDC[i] - SIM.PWP[i]) * DEPTH
        SIM.PWP[i] += (SIM.Soil.FIELDC[i] - SIM.PWP[i]) * (1.0 - D)
        # The new value of PWP is being used here por PAWFT.
        SIM.PAWFT[i] = (SIM.Soil.FIELDC[i] - SIM.PWP[i]) * DEPTH

        SIM.DPLBG += (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * DEPTH
        SIM.TOTDEP += DEPTH

    # @922

def setInitialConditions():
    """Sets the initial simulation conditions."""

    # Load initial data.
    #initFile = InitialFile(os.path.join(SIM.Config.InputPath, \
    #os.path.normpath(SIM.Config.INITFILE)))
    # TODO: By now, not loading/rewriting the Initial file, 
    # using the Default at program start and using memory copy.
    

    # TOASK: @985 Why not LIVECROP = LIVECOND ?
    if SIM.LIVECOND: SIM.LIVECROP = True
    # Set intial conditions for residue for grain and tuber crops
    # Set residue to default value for other crops
    SIM.RESIDUE = SIM.OLDRES if SIM.Sim.CROP < 10 else 100.0
    # Set starting conditions for winter wheat.
    if SIM.Sim.CROP == 7:
        SIM.JDYPLT = DAYOFYR(SIM.Sim.IMPLT, SIM.Sim.IDPLT)
        SIM.JFPLT = SIM.JDYPLT
        # If the crop is irrigated or the tillage flag is set to continuous
        # then the crop is alive at the start of the simulation
        # TONOTE: Why to change the tillage flag?
        if SIM.Sim.Irrigation.IRRTYP > 1 or SIM.Sim.ITFLAG > 2:
            SIM.LIVECROP = True
        elif not SIM.LIVECROP:
            SIM.Sim.ITFLAG = TillageFlags.Fallow
        # If the crop is alive set the greenup date to March 15 and 
        # the planting date is set to a negative number to indicate
        #  that the crop was planted before the start of this year.
        if SIM.LIVECROP:
            SIM.Sim.IMPLT = 3
            SIM.Sim.IDPLT = 15
            if SIM.Sim.Irrigation.IRRTYP == 1 and SIM.Sim.ITFLAG < 3:
                SIM.JFPLT = -999
    else:
        SIM.LIVECROP = False
        SIM.JFPLT = -999

    # DPLBG accumulation made in the previous loop in initSoilData()

    SIM.DRAIND = SIM.Soil.DRNDAY
    SIM.DCOEFF = SIM.Soil.DRNCOE

    # Compute Day Of Year For Special Days
    SIM.JDYBG = DAYOFYR(SIM.Sim.IMBG, SIM.Sim.IDBG)
    SIM.JDYEND = DAYOFYR(SIM.Sim.IMEND, SIM.Sim.IDEND)
    SIM.JDYPLT = DAYOFYR(SIM.Sim.IMPLT, SIM.Sim.IDPLT)
    print(f"Simulating from DAY {SIM.JDYBG} to {SIM.JDYEND}")

def initTillageDaysWithBranches():
    """CONVERT TILLAGE DAYS TO THE DAY OF THE YEAR RATHER THAN
    THE DAYS BEFORE PLANTING, AFTER PLANTING OR AFTER MATURITY."""
    for i in range(SIM.Sim.NTILLS):
        till: TillageOperation = SIM.Sim.TillageOperations[i]
        if SIM.Sim.CROP != 7:
            if till.ITILTM == 1:
                till.TILDAY = SIM.JDYPLT - till.TILDAY
            elif till.ITILTM == 2: till.TILDAY += SIM.JDYPLT
            elif till.ITILTM == 3: till.TILDAY += SIM.JDYMAT
        elif not SIM.LIVECROP:
            if till.ITILTM == 1:
                till.TILDAY = SIM.JDYPLT - till.TILDAY
            elif till.ITILTM == 2: till.TILDAY += SIM.JDYPLT
            elif till.ITILTM == 3: till.TILDAY += 367
        else:
            if till.ITILTM == 1:
                till.TILDAY = -999 - till.TILDAY
            elif till.ITILTM == 2: till.TILDAY = -999 + till.TILDAY
            elif till.ITILTM == 3: till.TILDAY += SIM.JDYMAT
        # TODO: Check if the values in Sim are actually changed without re-assigment
        SIM.Sim.TillageOperations[i] = till

def openOutputFiles():
    """Open output files."""
    # TODO: Continue @1079 Open Output Files
    SIM.openMonFile()
    SIM.openYearFile()
    SIM.openPrecipFile()
    SIM.openOutFile()
    SIM.openProfileFile()
    
    # Print Header for Out File
    pout = SIM.PrintOut
    if pout.IPFLAG > 1 and (pout.IPSOIL == SIM.SOIL or SIM.Config.PRINT_ALL_SOILS):
        if pout.JPRSTR <= SIM.IYEAR <= pout.JPRSTP:
            if SIM.Site.NWSITE in pout.PRSITE:
                #WRITE(7,450)WEAFILE(II),ICROP(CROP),SOIL,SIMFILE(II),ITFLAG,IHYGRP
                #FORMAT(1X,A12/5X,A8,5X,'SOIL CODE:',I4,5X,'CROP/IRR/TILL: ',
                #A8,5X,'TILL CODE: ',I3,5X,'HYDRO GROUP: ', I2/159('-'))
                crop = SIM.CurrentCrop
                IHYGRP = SIM.Soil.HydrologicGroup
                SIM.outFile.write((
                    f" {crop.WEAFILE:<12}\n     {SIM.Sim.CROP.getName(SIM.Config.LEGACY):<8}"
                    f"     SOIL CODE: {SIM.SOIL:>4}     CROP/IRR/TILL: {crop.SIMFILE:<8}     "
                    f"TILL CODE: {SIM.Sim.ITFLAG:>3}     HYDROGROUP: {IHYGRP:>2}\n{'*'*159}\n"
                    ))

def loadInitialData():
    """Writes the initial data to the simulation shared space."""
    SIM.THETA = SIM.InitialData.THETA[:]
    SIM.OLDCRP = SIM.InitialData.CROP
    SIM.OLDRES = SIM.InitialData.RESIDUE

    SIM.LIVECROP = SIM.InitialData.LIVECROP
    SIM.SNOTMP = SIM.InitialData.SNOTMP
    SIM.SNOH2O = SIM.InitialData.SNOH2O

    SIM.SOILT = SIM.InitialData.SOILT[:]

def rewriteInitFile():
    """Rewrites the INITFILE."""
    # TODO: By now using an in-memory Initial file.
    # @1148
    
    SIM.InitialData.THETA = SIM.THETA[:]
    SIM.InitialData.CROP = SIM.Sim.CROP
    SIM.InitialData.RESIDUE = SIM.RESIDUE

    SIM.InitialData.LIVECROP = SIM.LIVECROP
    SIM.InitialData.SNOTMP = SIM.SNOTMP
    SIM.InitialData.SNOH2O = SIM.SNOH2O

    SIM.InitialData.SOILT = SIM.SOILT[:]


def calculateYield():
    """Calculate Yield If There Is A Growing Crop"""
    # From @1114 to 1146

    # Calculate Yield If There Is A Growing Crop
    if SIM.Sim.ITFLAG > 0:
        YIELDS()
    else:
        SIM.YIELD = 0.0
        SIM.YLDRATIO = 0.0

    # Update the initial water content and residue for 
    # next year and reset the livecrop flag for winter wheat.
    # TONOTE: I guess that the initial water content and 
    # residue for next is already updated in YIELDS()
    if SIM.Sim.CROP == CropId.WinterWheat:
        # If the wheat crop was alive at the start of the year it was harvested
        # and is now dead for wheat-fallow rotations. Conversely if it started
        # the year as dead, it was planted in the fall and is now alive.
        SIM.LIVECROP = (not SIM.LIVECROP) if SIM.Sim.Irrigation.IRRTYP == 1 \
            and SIM.Sim.ITFLAG < 3 else True
    else:
        SIM.LIVECROP = False
