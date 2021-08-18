"""Implementation module for the DEPLT subroutine. Lines (1849~2744)"""

import sys
from aenum import IntEnum
import SIM
import Fortran
from Data.Crop import CropId
from Data.Tillage import TillageOperation
from Data.Summary import WeeklyData, MonthlyData

# from Subroutines.ROOTZN import ROOTZN
from Subroutines.SNOWMELT import SNOWMELT
from Subroutines.EFPRECIP import EFPRECIP
from Subroutines.NTHET_MOD import NTHET
from Subroutines.YIELDS import YIELDS
from Subroutines.IRRIGA import IRRIGA
from Subroutines.SOILTEMP import SOILTEMP
from Subroutines.DAYS import CALDAY
from Subroutines.EVAP_MOD import EVAP
from Subroutines.ROOTZN_MOD import ROOTZN

from Errors.CustomError import TransLoopConvergenceError


class ContinueTo(IntEnum):
    """Flags to signaling required program flow control."""
    Transpiration = 1
    """GOTO 200"""
    DailyEvaporation = 2
    """GOTO 248"""
    ComputeET = 3
    """GOTO 250"""
    Redistribution = 4
    """GOTO 260"""


# The following methods don't use variables of the Depletion class.


def ComputeWaterDepletion():
    """Compute Available Water Depletion."""
    SIM.AWDPLN = 0.0
    RZMGMT = SIM.RZMGMT

    depth: float = 0.0
    FDEPTH: float = 0.0
    TOPDEP: float = 0.0  # Top depth of a soil layer.
    BOTDEP: float = 0.0  # Bottom depth of a soil layer.
    for i in range(SIM.Sim.LAYERS):
        depth = SIM.BLOC.DEPTH[i]
        TOPDEP = BOTDEP
        BOTDEP += depth

        if BOTDEP <= RZMGMT:
            SIM.DEPL[i] = (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * depth * SIM.PERRZD[i]
            SIM.AWDPLN += SIM.DEPL[i]
            # TONOTE: Bad practice to compare floats this way.
            # This is only safe if both values can be represented as fractions of integers.
            if SIM.RZMGMT == BOTDEP: return
            # if abs(RZMGMT - BOTDEP) < 0.001: return

        if TOPDEP < RZMGMT < BOTDEP:
            FDEPTH = SIM.PERRZD[i] if SIM.RZD < RZMGMT else (RZMGMT - TOPDEP) / depth
            SIM.DEPL[i] = (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * depth * FDEPTH
            SIM.AWDPLN += SIM.DEPL[i]
            return


def ComputeAvailableWaterDepletion():
    """Compute Available Water Depletion to see if irrigation is needed."""
    # @2032
    ComputeWaterDepletion()

    SIM.DPLA = SIM.AWATER * SIM.Sim.Irrigation.PAD[SIM.KSTG - 1]


def ComputeFinalSoilWaterDepletions():
    """Compute Final Soil Water Depletion."""
    SIM.DPLN = 0.0
    for i in range(SIM.Sim.LAYERS):
        SIM.DPLN += (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i]

    ComputeWaterDepletion()


def ComputeAmountOfWaterStoredInSoilProfile():
    """Computes the amount of water stored in soil profile."""
    SIM.TOTWAT = 0.0
    for i in range(SIM.Sim.LAYERS):
        SIM.TOTWAT += SIM.THETA[i] * SIM.BLOC.DEPTH[i]


def DetermineGrowthStage():
    """Determine the growth stage for grain, tuber and forage crops."""
    # TONOTE: Fully revised method.
    # Implements Fortran code lines (1994~2004)
    SIM.KSTG = 1
    if SIM.Sim.CROP < 12:
        if SIM.GDD > SIM.Sim.GDD.FLO: SIM.KSTG = 2
        if SIM.GDD > SIM.Sim.GDD.RIPE: SIM.KSTG = 3
        if SIM.Sim.CROP.isForage(): SIM.KSTG = SIM.ICUT
    elif SIM.GDD > SIM.Sim.GDD.EFC:
        SIM.KSTG = 2


def AdjustResidueCover():
    """Adjust the amount of residue cover for tillage on row crops & grains after crop maturity"""

    # Label 120
    SIM.KC = SIM.CROPKC[SIM.JDAY - 1]
    if SIM.Sim.CROP < 10:
        if SIM.JDAY == SIM.JDYMAT:
            if SIM.Sim.CROP != CropId.WinterWheat or SIM.LIVECROP:
                YIELDS()
                ICROP: int = SIM.Sim.CROP - 1
                SIM.RESIDUE = SIM.YIELD * SIM.BLOC.YDENS[ICROP] * SIM.BLOC.RESRAT[ICROP]
                SIM.OLDCRP = SIM.Sim.CROP
        for i in range(SIM.Sim.NTILLS):
            tillage: TillageOperation = SIM.Sim.TillageOperations[i]
            if SIM.JDAY == tillage.TILDAY:
                SIM.RESIDUE *= SIM.Tillages.GetFactor(tillage.TILCOD, SIM.BLOC.FRAGIL[SIM.OLDCRP - 1])


def PrintHeaders():
    """Prints the report headers."""
    # (lines 1946~1970)
    if SIM.PrintOut.IPFLAG > 0 and (SIM.PrintOut.IPSOIL == SIM.SOIL or SIM.Config.PRINT_ALL_SOILS):
        if SIM.PrintOut.JPRSTR <= SIM.IYEAR <= SIM.PrintOut.JPRSTP \
                and SIM.Control.WSITE in SIM.PrintOut.PRSITE:
            SIM.outFile.write((
                f"{' ' * 8}DAILY  TOTAL  TOTAL  TOTAL  TOTAL   NET   GROSS  GROSS   NET    SNOW"
                f"{' ' * 31}TOTAL CROP TOTAL AWATER       ROOT PLANT  HOLD TOTAL\n"
                "  DATE   ETR    ETR    EVAP  TRANS    ET   IRRIG  IRRIG PRECIP PRECIP"
                "    H2O   RUNON  CURVE  RESIDUE   GDD DRAIN "
                f"COEF  DEPL  DEPL  DEPL DEPTH WATER  CAPA WATER\n     {'     IN' * 11}      NO.   "
                f"LB/AC     F     IN{' ' * 9}{'IN    ' * 1}% {'    IN' * 4}\n{'-' * 159}\n{' ' * 70}"
                f"{SIM.SNOH2O:>6.3f}{' ' * 77}{SIM.TOTWAT:>6.2f}\n"))
            # TONOTE: There's no space between RUNON and AWDPLN headers here.
            SIM.profileFile.write((
                " DATE  DFRACT EXTRA DIST  DET DRAIN DNETIR DINF RUNONAWDPLN DPLA"
                f"{' ' * 16}VOLUMETRIC WATER CONTENTS{' ' * 30}SOIL TEMPERATURE, F\n{'-' * 163}\n"))


def PrintWeeklySummary():
    """Print Weekly Summaries"""

    for i in range(52):
        SIM.precipFile.write((
            f'{SIM.Control.WSITE},{SIM.IYEAR:>5},{(i + 1):>3},{SIM.SOIL:>4},{SIM.Sim.CROP:>3},'
            f"{SIM.Sim.ITFLAG:>2},{SIM.Sim.Irrigation.IRRTYP:>2},{SIM.Sim.ITERRC:>2},"
            f"{SIM.WEEK[i].toPrecipFile()}\n"))


class DepletionData:
    """Holds the data for depletion computing."""
    __slots__ = ("DDINF", "DET", "DFRACT", "DIST", "DISTD", "DNETI", "DPLPER", "DRAIN", "DRNOFF", "E", "EOFF", "EPMAX",
                 "ES", "ET", "ETOFF", "ETROFF", "ETRS", "EVEG", "EXTRA", "IPRINT", "JDYWET", "PERDEP", "RNOFF",
                 "RUNONS", "T", "TOFF", "TP", "TRANS", "TS", "TUP", "TUSE", "TVEG", "TWAIT", "TWEIGH", "UPTAKE",
                 "WAVAIL")

    def __init__(self):
        """Initializes the values as they as required before starting the loop."""
        SIM.AWATER = 0.0
        SIM.DRAINS = 0.0
        SIM.EPRECIPS = 0.0
        SIM.ETMAX = 0.0
        SIM.ETS = 0.0  # @1958
        SIM.ETYLD = 0.0
        SIM.ICUT = 1
        SIM.IRIGNO = 0
        SIM.JNEXTI = 1.0
        SIM.KSTG = 0
        SIM.PRECIPS = 0.0
        SIM.SGRIRR = 0.0
        SIM.SNIRR = 0.0
        SIM.TDEFS = 0.0
        SIM.RZD = SIM.Sim.RZMIN
        SIM.TPS = ([0.0] * 5)[:]
        SIM.TDEF = ([0.0] * 5)[:]
        SIM.PERRZD = ([0.0] * 10)[:]
        SIM.MON.clear()
        for _ in range(12): SIM.MON.append(MonthlyData())
        SIM.WEEK.clear()
        for _ in range(53): SIM.WEEK.append(WeeklyData())

        self.JDYWET = SIM.JDYBG - 1
        SIM.TIME = float(self.JDYWET)

        self.DDINF = 0.0
        self.DET = 0.0
        """Depletion E + T"""
        self.DFRACT = 0.0
        """Drainage fraction = portion of EXTRA that drains per day."""
        self.DIST = 0.0
        """Average increase of water content for water not drained."""
        self.DISTD = 0.0
        """Depth of profile that is at field capacity."""
        self.DNETI = 0.0
        """Depletion Net irrigation"""
        self.DPLPER = 0.0
        self.DRAIN = 0.0
        """The depth of water that drains that day."""
        self.DRNOFF = 0.0

        self.E = 0.0
        self.EOFF = 0.0
        self.EPMAX = 0.0
        self.ES = 0.0
        """Seasonal evaporation."""
        self.ET = 0.0
        self.ETOFF = 0.0
        self.ETROFF = 0.0
        self.ETRS = 0.0
        """Seasonal reference crop ET."""
        self.EVEG = 0.0
        """Evaporation during vegetative stage."""
        self.EXTRA = 0.0
        """Now is the amount of water in excess of field capacity
        for the profile and equals the water that can drain."""
        self.IPRINT = 0
        self.PERDEP = [0.0] * 10
        self.RNOFF = 0.0
        self.RUNONS = 0.0
        self.T = 0.0
        self.TOFF = 0.0
        self.TP = 0.0
        self.TRANS = 0.0
        self.TS = 0.0
        """Seasonal transpiration."""
        self.TUP = 0.0
        self.TUSE = 0.0
        self.TVEG = 0.0
        """Transpiration during vegetative stage."""
        self.TWAIT = 0.0
        self.TWEIGH = 0.0
        self.UPTAKE = 0.0
        self.WAVAIL = 0.0

        ICROP: int = SIM.Sim.CROP - 1
        self.TUP = SIM.BLOC.KCL[ICROP] / (SIM.BLOC.KCU[ICROP] - SIM.BLOC.KCL[ICROP])

    def initLoop(self, IJDAY: int):
        """Initializes the required variables at the start of the Daily loop."""
        SIM.JDAY = IJDAY + 1
        SIM.TODAY = float(SIM.JDAY)

        self.E, self.T, self.ET = 0.0, 0.0, 0.0
        SIM.RUNON, SIM.RUNOFF, SIM.EPRECIP = 0.0, 0.0, 0.0

        SIM.GDD = SIM.GDDS[IJDAY]
        SIM.TAVG = 0.5 * (SIM.TMAX[IJDAY] + SIM.TMIN[IJDAY])

    # Irrigation Methods
    def DetermineIrrigation(self):
        """Determine if Irrigation is needed base on the type of irrigation."""

        # FULLY REVISED
        # @ 2090
        IRR = SIM.Sim.Irrigation
        if IRR.IRRTYP != 1:
            if IRR.IRRSCH == 3:
                self.PerformFixedIrrigation()
            else:
                # Fixed Irrigation Date And Amount For Simulating Experiments
                # FDIRRIG = 1 - fixed irrig date, 2 - gross depth, 3 - application eff
                if SIM.IRIGNO < 1: SIM.IRIGNO = 1
                if IRR.IRRTYP == 2:
                    IRNO: int = SIM.IRIGNO - 1
                    if Fortran.INT(SIM.FDIRRIG[IRNO][0]) == SIM.JDAY:
                        # if int(SIM.FDIRRIG[IRNO][0]) == SIM.JDAY:
                        SIM.GROIRR = SIM.FDIRRIG[IRNO][1]
                        SIM.NETIRR = SIM.GROIRR * SIM.FDIRRIG[IRNO][2]
                        SIM.DINF = SIM.NETIRR
                        SIM.IRIGNO += 1
                        self.AddIrrigationToSeasonalTotals()
                elif IRR.IRRTYP > 2:
                    if SIM.GDD < IRR.GSTART or SIM.GDD > IRR.GSTOP: return
                    IRRIGA()
                    self.AddIrrigationToSeasonalTotals()

    def PerformFixedIrrigation(self):
        """Determines the irrigation for the fixed rotation and fixed depth scheduling method."""

        # Scheduling Method 3 -- Fixed Rotation and Fixed Depth
        if SIM.JDAY < SIM.Sim.Irrigation.JFIRST:
            return

        if 10 <= SIM.Sim.CROP <= 12:
            if SIM.JDAY > 304 or (SIM.Sim.JGOI > SIM.JDAY > SIM.Sim.JSTOPI):
                return
        elif SIM.JDAY > SIM.JDYMAT:
            return

        if SIM.IRIGNO < 1:
            IRRIGA()
            if SIM.IRIGNO < 1: return
        else:
            if SIM.JDAY < SIM.JNEXTI: return
            IRRIGA()

        self.AddIrrigationToSeasonalTotals()

    def AddIrrigationToSeasonalTotals(self):
        """Adds irrigation to seasonal totals."""
        SIM.SGRIRR += SIM.GROIRR
        SIM.SNIRR += SIM.NETIRR
        self.JDYWET = SIM.JDAY
        NTHET()

    def StartEvaporationRoutine(self):
        """This method implements the control flow that starts with the evaporation routine."""

        if SIM.Sim.CROP.isNatural(): return ContinueTo.ComputeET
        if SIM.ETR[SIM.JDAY - 1] <= 0.0: return ContinueTo.Redistribution

        # @2191
        ICROP = SIM.Sim.CROP - 1
        SIM.EP = SIM.ETR[SIM.JDAY - 1] * min(1.0, SIM.BLOC.KCU[ICROP] + SIM.BLOC.KCL[ICROP] - SIM.KC)
        # TONOTE: Weird behaviour about setting EPMAX to EP before to check if it's <= 0.0
        # It could yield a DivisionByZero error later
        # Also EVAP checks if EP <= 0 before to compute, but it'd never get called in that case
        self.EPMAX = SIM.EP

        if SIM.EP <= 0.0: SIM.EP = 0.001
        if SIM.EP > 0.001:
            EVAP()
            SIM.THETA[0] -= SIM.E1 / SIM.BLOC.DEPTH[0]
            SIM.THETA[1] -= SIM.E2 / SIM.BLOC.DEPTH[1]
            self.E = SIM.E1 + SIM.E2
            if SIM.Sim.CROP == CropId.SummerFallow:
                # Skip transpiration calculation for summer fallow
                return ContinueTo.DailyEvaporation
        return ContinueTo.Transpiration

    def AddDailyETToSeasonalTotals(self):
        """Add Daily Evaporation And Transpirational ToSeasonal Totals.
        Cumulative Values By Growth Stage For Grain/Tuber/Forage Crops"""

        # This code was simplified from:
        # if SIM.Sim.CROP.isGrainOrTuber():
        #    if SIM.Sim.GDD.VEG <= SIM.GDD <= SIM.Sim.GDD.YFORM:
        #        SIM.ETMAX += SIM.E1 + SIM.E2 + D.TP
        #        SIM.ETYLD += SIM.E1 + SIM.E2 + D.T
        #        SIM.TPS[SIM.KSTG-1] += D.TP
        #        SIM.TDEFS = SIM.TDEFS + D.TP - D.T
        #        SIM.TDEF[SIM.KSTG-1] = SIM.TDEF[SIM.KSTG-1] + D.TP - D.T
        # elif SIM.Sim.CROP.isForage():
        #    # Cumulative Values By Cutting For Forage Crops
        #    SIM.TPS[SIM.ICUT-1] += D.TP
        #    SIM.TDEFS = SIM.TDEFS + D.TP - D.T
        #    SIM.TDEF[SIM.ICUT-1] = SIM.TDEF[SIM.ICUT-1] + D.TP - D.T
        #    SIM.ETMAX += SIM.E1 + SIM.E2 + D.TP
        #    SIM.ETYLD += SIM.E1 + SIM.E2 + D.T

        # Label 248
        if SIM.Sim.CROP.isGrainTuberOrForage():
            if SIM.Sim.CROP.isForage() or SIM.Sim.GDD.VEG <= SIM.GDD <= SIM.Sim.GDD.YFORM:
                i: int = (SIM.KSTG if SIM.Sim.CROP.isGrainOrTuber() else SIM.ICUT) - 1
                SIM.TPS[i] += self.TP
                SIM.ETYLD += SIM.E1 + SIM.E2 + self.T
                SIM.ETMAX += SIM.E1 + SIM.E2 + self.TP
                SIM.TDEFS = SIM.TDEFS + self.TP - self.T
                SIM.TDEF[i] = SIM.TDEF[i] + self.TP - self.T

    def DrainageRoutine(self):
        """Computes the drainage."""

        self.DRAIN = 0.0
        if self.EXTRA > 0.0:
            self.DFRACT = (float((SIM.JDAY - self.JDYWET) + 1) / SIM.DRAIND) ** SIM.DCOEFF
            if self.DFRACT > 1.0: self.DFRACT = 1.0
            self.DRAIN = self.EXTRA * self.DFRACT
            # TONOTE: LINES 2418~2420, Useless code
            self.DIST = (1.0 - self.DFRACT) * self.EXTRA / self.DISTD

            SIM.DPLN = 0.0
            for i in range(SIM.Sim.LAYERS):
                if SIM.THETA[i] >= SIM.Soil.FIELDC[i]: SIM.THETA[i] += self.DIST
                SIM.DPLN += (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i] * SIM.PERRZD[i]

    def RedistributionRoutine(self):
        """Redistribution Routine"""

        # Label 260
        # If layer is above field capacity compute the amount of extra water,
        # and set water content to field capacity.
        # If layer is below field capacity increase water content of layer up
        # to field capacity, and decrease amount of extra water.
        AMT, ADDL = 0.0, 0.0
        self.EXTRA, self.DISTD = 0.0, 0.0

        for i in range(SIM.Sim.LAYERS):
            FIELDC = SIM.Soil.FIELDC[i]
            if SIM.THETA[i] > FIELDC:
                self.EXTRA += (SIM.THETA[i] - FIELDC) * SIM.BLOC.DEPTH[i]
                SIM.THETA[i] = FIELDC
                self.DISTD += SIM.BLOC.DEPTH[i]
            elif self.EXTRA != 0.0:
                AMT = (FIELDC - SIM.THETA[i]) * SIM.BLOC.DEPTH[i]
                if AMT >= self.EXTRA:
                    ADDL = self.EXTRA
                    self.EXTRA = 0.0
                else:
                    ADDL = AMT
                    self.EXTRA -= AMT

                SIM.THETA[i] += ADDL / SIM.BLOC.DEPTH[i]
                if SIM.THETA[i] >= FIELDC:
                    self.DISTD += SIM.BLOC.DEPTH[i]

    def ComputeET(self):
        """ET computation for riparian woodlands, wetlands, AND water"""
        # Label 250, evaporation routine
        if SIM.Sim.CROP.isNatural():
            self.ET = SIM.KC * SIM.ETR[SIM.JDAY - 1]
            for i in range(SIM.Sim.LAYERS):
                SIM.THETA[i] = SIM.Soil.FIELDC[i]

    def CalculateEffectiveRainfallAmount(self):
        """Calculate Effective Rainfall Amount, and Redistribute Infiltration."""
        IJDAY: int = SIM.JDAY - 1
        if SIM.PRECIP[IJDAY] > 0.0 or SIM.SNOH2O > 0.0:
            SIM.RAIN = SIM.PRECIP[IJDAY]

            SNOWMELT(SIM.JDAY)

            EFPRECIP()

            if SIM.EPRECIP > SIM.RAIN and SIM.Sim.ITERRC == 0:
                # TODO: Here we have one of those exit conditions.
                print(" @ 1729: ", SIM.JDAY, SIM.IYEAR)
                sys.exit()
            if SIM.Sim.Irrigation.IRRTYP == 2: SIM.EPRECIP = SIM.PRECIP[IJDAY]
            SIM.DINF = SIM.EPRECIP
            self.JDYWET = SIM.JDAY
            NTHET()

    def ComputeTotalsForBeforeMayAndAfterSept(self):
        """Compute Totals For Before May And After Sept"""

        self.DPLPER = (SIM.AWDPLN / SIM.AWATER) * 100.0
        SIM.DRAINS += self.DRAIN
        self.ETRS += SIM.ETR[SIM.JDAY - 1]
        self.ES += self.E
        SIM.PRECIPS += SIM.PRECIP[SIM.JDAY - 1]
        SIM.EPRECIPS += SIM.EPRECIP
        self.RUNONS += SIM.RUNON
        self.TS += self.T

        if SIM.GDD <= SIM.Sim.GDD.VEG:
            self.EVEG += self.E
            self.TVEG += self.T

    def SetupPrinting(self):
        """
        Setup printing dates for printout.
        Returns True if print must be performed. Returns False to break the daily loop.
        """
        CROP = SIM.Sim.CROP
        if CROP.isForage() and SIM.JDAY in (SIM.JDYPLT, SIM.JDYEND, SIM.Sim.JDYCUT[SIM.ICUT - 1]):
            return True
        if CROP in (12, 13) and SIM.JDAY in (SIM.JDYEFC, SIM.JDYMAT):
            return True
        if CROP < 10 and SIM.JDAY in (SIM.JDYPLT, SIM.JDYEFC, SIM.JDYRIPE, SIM.JDYFLO, SIM.JDYMAT):
            return True

        if self.IPRINT == SIM.PrintOut.INPRIN: self.IPRINT = 0
        self.IPRINT += 1
        if self.IPRINT == 1: return True
        return False


def DEPLT():
    """DAILY SOIL WATER BALANCE-DEPLETION SUBROUTINE"""

    # LINE (1857)
    D = DepletionData()

    ComputeAmountOfWaterStoredInSoilProfile()

    PrintHeaders()

    # Start of Daily Loop @1971
    # DO 330 => CONTINUE, SO GOTO 330 breaks the loop
    for IJDAY in range(SIM.JDYBG - 1, SIM.JDYEND):
        D.initLoop(IJDAY)

        DetermineGrowthStage()

        # Compute Root Depth for the Day
        if SIM.RZD < SIM.RZMAX or SIM.AWATER <= 0.0: ROOTZN()

        D.CalculateEffectiveRainfallAmount()

        ComputeAvailableWaterDepletion()

        D.DetermineIrrigation()

        AdjustResidueCover()

        # Compute soil temperatures @2175
        SOILTEMP()

        flow = D.StartEvaporationRoutine()

        if flow == ContinueTo.Transpiration:
            flow = __TranspirationRoutine(D)
        if flow <= ContinueTo.DailyEvaporation:
            D.AddDailyETToSeasonalTotals()
        if flow <= ContinueTo.ComputeET:
            D.ComputeET()

        D.RedistributionRoutine()

        D.DrainageRoutine()

        # @2431
        # Update The Daily Values
        # Compute Totals For Before May And After Sept
        D.ComputeTotalsForBeforeMayAndAfterSept()
        # Compute Final Soil Water Depletions
        ComputeFinalSoilWaterDepletions()

        __ComputeSeasonalAndOffSeasonSummaries(D)
        __ComputeWeeklySummaries(D)

        firstMonthDay = __ComputeMonthlySummaries(D)

        if firstMonthDay:
            PrintSummary(D)
        elif D.SetupPrinting():
            PrintSummary(D)
        else:
            break
    # End of Daily Loop @2622

    PrintMonthlySummary(D)
    PrintWeeklySummary()


def __ComputeSeasonalAndOffSeasonSummaries(D: DepletionData):
    """Compute Seasonal and Off-season summaries"""

    naturalCrop: bool = SIM.Sim.CROP.isNatural()
    SIM.ETS = SIM.ETS + D.ET if naturalCrop else D.ES + D.TS
    if SIM.JDAY <= 121 or SIM.JDAY >= 274:
        D.TOFF += D.T
        D.EOFF += D.E
        D.ETOFF += D.ET if naturalCrop else D.E + D.T
        D.RNOFF += SIM.PRECIP[SIM.JDAY - 1]
        D.ETROFF += SIM.ETR[SIM.JDAY - 1]
        D.DRNOFF += D.DRAIN


def __ComputeWeeklySummaries(D: DepletionData):
    """Compute Weekly Summaries for Production Crops"""

    # TONOTE: Seems an unnecessary checking, CROP can't be greater than 22
    if SIM.Sim.CROP <= 22:
        IWEEK = int((SIM.JDAY - 1) / 7)
        SIM.WEEK[IWEEK].ET += D.E + D.T
        SIM.WEEK[IWEEK].ER += SIM.EPRECIP
        SIM.WEEK[IWEEK].IRN += SIM.NETIRR
        SIM.WEEK[IWEEK].IRG += SIM.GROIRR
        SIM.WEEK[IWEEK].ETR += SIM.ETR[SIM.JDAY - 1]
        SIM.WEEK[IWEEK].RA += SIM.PRECIP[SIM.JDAY - 1]


def __ComputeMonthlySummaries(D: DepletionData) -> bool:
    """
    Computes the monthly summaries.
    Returns True if the summary must be printed.
    Returns False if SetupPrinting must be called to decide.
    """

    MON, DAY = CALDAY(SIM.JDAY)
    IMON = MON - 1

    SIM.MON[IMON].E += D.E
    SIM.MON[IMON].T += D.T
    SIM.MON[IMON].ER += SIM.EPRECIP
    SIM.MON[IMON].ETR += SIM.ETR[SIM.JDAY - 1]
    SIM.MON[IMON].RA += SIM.PRECIP[SIM.JDAY - 1]
    SIM.MON[IMON].RON += SIM.RUNON
    SIM.MON[IMON].ROF += SIM.RUNOFF

    if SIM.MON[IMON].ROF < 0.0:
        # TODO: Non documented exit condition
        # What to do ?
        sys.exit()

    if SIM.Sim.CROP.isNatural():
        SIM.MON[IMON].ET += D.ET
    else:
        SIM.MON[IMON].ET = SIM.MON[IMON].E + SIM.MON[IMON].T

    SIM.MON[IMON].DRA += D.DRAIN
    SIM.MON[IMON].IRG += SIM.GROIRR
    SIM.GROIRR = 0.0
    SIM.MON[IMON].IRN += SIM.NETIRR
    D.DNETI = SIM.NETIRR
    SIM.NETIRR = 0.0
    SIM.MON[IMON].NUMIRR = SIM.IRIGNO
    SIM.MON[IMON].INF += SIM.DINF
    D.DDINF = SIM.DINF
    SIM.DINF = 0.0
    D.DET = D.E + D.T

    if DAY <= 1:
        SIM.MON[IMON].DPL = SIM.DPLN
        D.IPRINT = 1
        return True
    return False


def __TranspirationRoutine(D: DepletionData) -> ContinueTo:
    """Transpiration routine. Label 200"""
    # REVISED METHOD

    # TODO: Label 200
    D.TP = SIM.ETR[SIM.JDAY - 1] * (SIM.KC - SIM.BLOC.KCL[SIM.Sim.CROP - 1])

    if SIM.EP > 0.0:
        D.TP *= 1.0 + D.TUP * (D.EPMAX - D.E) / D.EPMAX

    if D.TP <= 0.0:
        return ContinueTo.Redistribution

    SIM.DPLN, D.TWEIGH, D.WAVAIL = 0.0, 0.0, 0.0

    for i in range(SIM.Sim.LAYERS):
        SIM.DEPL[i] = (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i] * SIM.PERRZD[i]
        if SIM.DEPL[i] < 0.0: SIM.DEPL[i] = 0.0

        SIM.DPLN += SIM.DEPL[i]

        if SIM.PERRZD[i] > 0.0:
            D.PERDEP[i] = SIM.DEPL[i] / (SIM.PAWFT[i] * SIM.PERRZD[i])
            if D.PERDEP[i] > 1.0: D.PERDEP[i] = 1.0

            if SIM.THETA[i] > SIM.PWP[i]:
                D.WAVAIL += (SIM.THETA[i] - SIM.PWP[i]) * SIM.BLOC.DEPTH[i] * SIM.PERRZD[i]
                D.TWEIGH += SIM.RDF[i] * (1.0 - D.PERDEP[i])
        else:
            D.PERDEP[i] = 0.0

    # @2241
    # Compute the Stress Factor
    AV: float = (1.0 - SIM.DPLN / SIM.PAW) * 100.0
    if AV < 0.0: AV = 0.0
    SR: float = 1.0 if AV > SIM.Sim.TBREAK else AV / SIM.Sim.TBREAK
    D.T = D.TP * SR
    if D.T > 0.0:
        # Uptake section
        PerformUptake(D)
    # DAILY EVAPORATION COMES LATER AT LABEL 248
    return ContinueTo.DailyEvaporation


def PerformUptake(D: DepletionData) -> ContinueTo:
    """Uptake section."""
    D.TRANS = D.T
    SIM.DPLN = 0.0
    D.TUSE, D.TWAIT = 0.0, 0.0

    if D.WAVAIL > D.T:
        ITRIES = 1
        while not __OnMoreThanEnoughWater(D):
            D.TWEIGH = D.TWAIT
            D.TRANS = D.T - D.TUSE
            if abs(D.TRANS) < 0.001: break
            if ITRIES > 20: raise TransLoopConvergenceError(SIM.JDAY, D.TRANS)
            D.TWAIT = 0.0
            ITRIES += 1
            SIM.DPLN = 0.0
    else:
        # Transpiration demand > Water Available
        for i in range(SIM.Sim.LAYERS):
            SIM.THETA[i] = SIM.PWP[i] * SIM.PERRZD[i] + SIM.THETA[i] * (1.0 - SIM.PERRZD[i])
            D.PERDEP[i] = 1.0

        SIM.DPLN = SIM.PAW
        D.TUSE = D.WAVAIL


def __OnMoreThanEnoughWater(D: DepletionData) -> bool:
    """Lines 2272~2292"""
    # Method revised.
    result: bool = True
    for i in range(SIM.Sim.LAYERS):
        D.UPTAKE = D.TRANS * (1.0 - D.PERDEP[i]) * SIM.RDF[i] / D.TWEIGH
        if D.UPTAKE < 0.0: D.UPTAKE = 0.0
        D.WAVAIL = (SIM.THETA[i] - SIM.PWP[i]) * SIM.BLOC.DEPTH[i] * SIM.PERRZD[i]
        if D.WAVAIL < 0.0: D.WAVAIL = 0.0
        # TONOTE: See the weird flow control done here in the Fortran code.
        # The use of a float as a true/false flag was pretty funny too
        if D.UPTAKE > D.WAVAIL:
            # Not Enough Layer Water For Needed Uptake
            D.TUSE += D.WAVAIL
            SIM.THETA[i] = SIM.PWP[i] * SIM.PERRZD[i] + SIM.THETA[i] * (1.0 - SIM.PERRZD[i])
            result = False
        else:
            D.TUSE += D.UPTAKE
            SIM.THETA[i] -= D.UPTAKE / SIM.BLOC.DEPTH[i]

        D.PERDEP[i] = (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i] / SIM.PAWFT[i]
        if D.PERDEP[i] > 1.0: D.PERDEP[i] = 1.0
        SIM.DPLN += (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i] * SIM.PERRZD[i]
        D.TWAIT += SIM.RDF[i] * (1.0 - D.PERDEP[i])
    return result


def PrintSummary(D: DepletionData):
    """Prints the depletion summary."""
    # Label 310 @ 2591
    ComputeAmountOfWaterStoredInSoilProfile()

    if SIM.PrintOut.IPFLAG > 1 and (SIM.PrintOut.IPSOIL == SIM.SOIL or SIM.Config.PRINT_ALL_SOILS):
        if SIM.Site.NWSITE in SIM.PrintOut.PRSITE:
            MON, DAY = CALDAY(SIM.JDAY)
            SIM.outFile.write((
                f"{MON:>3}{DAY:>3}{SIM.ETR[SIM.JDAY]:>7.2f}{D.ETRS:>7.2f}{D.ES:>7.2f}{D.TS:>7.2f}"
                f"{SIM.ETS:>7.2f}{SIM.SNIRR:>7.2f}{SIM.SGRIRR:>7.2f}{SIM.PRECIPS:>7.2f}"
                f"{SIM.EPRECIPS:>7.2f}{SIM.SNOH2O:>7.2f}{D.RUNONS:>7.2f}{SIM.CURVNO:>8.1f}"
                f"{SIM.RESIDUE:>8.0f} {SIM.GDD:>6.0f}{SIM.DRAINS:>6.2f}{SIM.KC:>5.2f}"
                f"{SIM.DPLN:>6.2f}{SIM.AWDPLN:>6.2f}{D.DPLPER:>6.1f}{SIM.RZD:>6.2f}{SIM.PAW:>6.2f}"
                f"{SIM.AWATER:>6.2f}{SIM.TOTWAT:>6.2f}\n"
            ))
            thetas = "".join([f" {SIM.THETA[i]:>4.3f}" for i in range(10)])
            soilts = "".join([f" {SIM.SOILT[i]:>4.1f}" for i in range(10)])
            SIM.profileFile.write((
                f"{MON:>3}{DAY:>3}  {D.DFRACT:>4.2f}  {D.EXTRA:>4.2f}  {D.DIST:>4.2f} "
                f"{D.DET:>4.2f}  {D.DRAIN:>4.2f}  {D.DNETI:>4.2f}  {D.DDINF:>4.2f}  "
                f"{SIM.RUNON:>4.2f} {SIM.AWDPLN:>4.2f} {SIM.DPLA:>4.2f}  {thetas}   {soilts}\n"))


def PrintMonthlySummary(D: DepletionData):
    """Print Monthly Summaries"""
    if SIM.PrintOut.IPFLAG > 1 and (SIM.PrintOut.IPSOIL == SIM.SOIL or SIM.Config.PRINT_ALL_SOILS):
        if SIM.PrintOut.JPRSTR <= SIM.IYEAR <= SIM.PrintOut.JPRSTP and \
                SIM.Site.NWSITE in SIM.PrintOut.PRSITE:
            SIM.outFile.write((
                f"{'-' * 139}\n\n\n{' ' * 20}MONTHLY WATER BALANCE SUMMARIES\n"
                f"{' ' * 17}ETR     E     T    ET   PRECIP, in  RUNON  IRRIGATION, in  TOTAL  INFIL"
                f"    DRAIN  BEGDPL\n{' ' * 10}month   in    in    in    in    tot   eff   in     "
                f"gross    net    #IRR    in      in      in\n{' ' * 10}{'-' * 97}\n"))
            IMBG, _ = CALDAY(SIM.JDYBG)
            IMEND, _ = CALDAY(SIM.JDYEND)
            total = MonthlyData()
            for i in range(IMBG - 1, IMEND):
                total.add(SIM.MON[i])
                SIM.outFile.write(SIM.MON[i].toMonthlyOutput(i + 1))

            SIM.outFile.write(f"{' ' * 10}{'-' * 104}\n")
            SIM.outFile.write(f"{' ' * 6}TOTALS   {total.toTotalOutput()}\n\n")

            SIM.outFile.write((
                f"     OFF SEASON{D.ETROFF:>6.1f}{D.EOFF:>6.1f}{D.TOFF:>6.1f}{D.ETOFF:>6.1f}"
                f"{D.RNOFF:>6.1f}{' ' * 43}{D.DRNOFF:>8.1f}\n"))
            SIM.outFile.write((
                f"     MAY - SEPT{total.ETR - D.ETROFF:>6.1f}{total.E - D.EOFF:>6.1f}"
                f"{total.T - D.TOFF:>6.1f}{total.ET - D.ETOFF:>6.1f}{total.RA - D.RNOFF:>6.1f}"
                f"{' ' * 43}{total.DRA - D.DRNOFF:>8.1f}\n\n{'=' * 139}\n\n\n\n"))

    if SIM.Config.OUTPUT_FORMAT == 2:
        if SIM.PrintOut.IPFLAG > 1:
            SIM.monthFile.write((
                f'"{SIM.CurrentCrop.WEAFILE}",{SIM.IYEAR:>5},{SIM.SOIL:>5},{SIM.Sim.CROP:>3},'
                f"{SIM.Sim.ITFLAG:>3},{SIM.Sim.Irrigation.IRRTYP:>3},{SIM.Sim.ITERRC:>3},"
            ))
            SIM.monthFile.write(",".join([
                (f"{SIM.MON[i].ET:>5.1f},{SIM.MON[i].ER:>5.1f},{SIM.MON[i].IRN:>5.1f},"
                 f"{SIM.MON[i].RA:>5.1f},{SIM.MON[i].ROF:>5.1f},{SIM.MON[i].RON:>5.1f}")
                for i in range(SIM.Sim.IMBG - 1, SIM.Sim.IMEND)]))
            SIM.monthFile.write("\n")
    else:
        rotateWheat = SIM.Sim.CROP == 7 and not SIM.LIVECROP and \
                      SIM.Sim.Irrigation.IRRTYP == 2 and SIM.Sim.ITFLAG != 3
        if rotateWheat:
            SIM.Sim.CROP = 15

        SIM.monthFile.write((
            f' {SIM.CurrentCrop.WEAFILE}  {SIM.IYEAR:>5}{SIM.SOIL:>5}{SIM.Sim.CROP:>3}'
            f"{SIM.Sim.ITFLAG:>3}{SIM.Sim.Irrigation.IRRTYP:>3}"
        ))

        SIM.monthFile.write("".join([
            (f"  {SIM.MON[i].ET:>7.2f}{SIM.MON[i].ER:>7.2f}{SIM.MON[i].IRN:>7.2f}"
             f"{SIM.MON[i].DRA:>7.2f}{SIM.MON[i].ROF:>7.2f}{SIM.MON[i].RA:>7.2f}")
            for i in range(SIM.Sim.IMBG - 1, SIM.Sim.IMEND)]))
        SIM.monthFile.write("\n")

        if rotateWheat:
            SIM.Sim.CROP = 7
