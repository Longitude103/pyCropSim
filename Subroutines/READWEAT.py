"""Implementation module for subroutine READWEAT"""

# 100% REVISED

from math import cos
from math import exp

import SIM

from Subroutines.DAYS import DAYOFYR
from Subroutines.CROPCO import CROPCO

from Files.WeaFile import WeaFile
from Data.WeatherDailyData import WeatherDailyData

def READWEAT(site: str, year: int):
    """Read and Process Weather Data"""

    wea = WeaFile(SIM.Config.getSiteFilename(site, year))
    
    SIM.Station = wea.StationData
    SIM.JDYSTR = DAYOFYR(SIM.Station.IMSTR, SIM.Station.IDSTR)

    # This counter should yield the same as SIM.Station.NDAYS
    NDAYS = 0

    # Set Defaults For First Days Of Simulation For Weather
    TMINA, TMAXA = 30.0, 55.0
    ETRA, PRECIPA = 0.10, 0.0

    temp = [0.0] * 366
    SIM.ETR = temp[:]
    SIM.TMIN = temp[:]
    SIM.TMAX = temp[:]
    SIM.GDDS = temp[:]
    SIM.SOLAR = temp[:]
    SIM.PRECIP = temp[:]
    SIM.CROPKC = temp[:]

    startIndex = SIM.JDYSTR - 1
    endIndex = startIndex + SIM.Station.NDAYS
    for i in range(startIndex, endIndex):
        data: WeatherDailyData = wea.ReadNextDayData()

        SIM.ETR[i] = ETRA if data.ETR < 0.0 or data.ETR > 0.6 else data.ETR
        SIM.TMIN[i] = TMINA if data.TMIN < -50.0 or data.TMIN > 100.0 else data.TMIN
        SIM.TMAX[i] = TMAXA if data.TMAX < -50.0 or data.TMAX > 125.0 else data.TMAX
        SIM.PRECIP[i] = PRECIPA if data.PRECIP < 0.0 or data.PRECIP > 10.0 else data.PRECIP
        
        # Adjusted for 0-based indexing.
        if i - SIM.JDYSTR >= 2:
            ETRA = (SIM.ETR[i] + SIM.ETR[i-1] + SIM.ETR[i-2]) / 3.0
            TMINA = (SIM.TMIN[i] + SIM.TMIN[i-1] + SIM.TMIN[i-2]) / 3.0
            TMAXA = (SIM.TMAX[i] + SIM.TMAX[i-1] + SIM.TMAX[i-2]) / 3.0
            PRECIPA = (SIM.PRECIP[i] + SIM.PRECIP[i-1] + SIM.PRECIP[i-2]) / 3.0

        # Reduce Reference Crop ET for Field Values and High Values from HPCC
        SIM.ETR[i] *= SIM.BLOC.ETRFACT
        NDAYS += 1

    wea.close()

    assert NDAYS == SIM.Station.NDAYS

    # JDYSTP is used only locally so removed from global SIM data.
    #SIM.JDYSTP = SIM.JDYSTR + NDAYS - 1

    CalculateGrowingDegreeDays()

    CalculateCropData()

    ComputeDailyCropCoefficients()


def CalculateGrowingDegreeDays():
    """Calculate The Growing Degree Days"""
    # TONOTE: REVISED
    SIM.JDYFRZ = 0

    ICROP = SIM.Sim.CROP - 1
    CEIL = SIM.BLOC.TCEIL[ICROP]
    BASE = SIM.BLOC.TBASE[ICROP]
    for i in range(SIM.JDYPLT-1, SIM.JDYEND):
        i1: int = i + 1
        T1 = SIM.TMAX[i]
        if T1 >= CEIL: T1 = CEIL
        if T1 < BASE: T1 = BASE
        T2 = SIM.TMIN[i]
        if T2 <= BASE: T2 = BASE
        if T2 > CEIL: T2 = CEIL
        SIM.GDD = (T1 + T2) / 2.0 - BASE
        if SIM.GDD < 0.0: SIM.GDD = 0.0
        SIM.GDDS[i] = SIM.GDDS[i-1] + SIM.GDD
        
        # Determine First Killing Freeze Date
        if i1 < 200 or SIM.TMIN[i] >= 26.0: continue
        if SIM.JDYFRZ < 1: SIM.JDYFRZ = i1

    if SIM.JDYFRZ < 1: SIM.JDYFRZ = SIM.JDYEND
    if SIM.JDYSTR > SIM.JDYBG: SIM.JDYBG = SIM.JDYSTR

def CalculateCropData():
    """Calculate Development, Maturity And Cover Dates Based On Gdd
    Skip Calculation Of Development Dates For Non Row Crops"""

    # @3637~3680
    # TONOTE: Full revised

    if SIM.Sim.CROP >= 10:
        SIM.JDYMAT = SIM.JDYFRZ
        SIM.JDYEFC = __FindGddIndexGreaterOrEqualTo(SIM.Sim.GDD.EFC)
    else:
        GDD = SIM.Sim.GDD
        SIM.JDYVEG, SIM.JDYEFC, SIM.JDYFLO, SIM.JDYRIPE, SIM.JDYMAT = \
            __FindGddIndices([GDD.VEG, GDD.EFC, GDD.FLO, GDD.RIPE, GDD.MAT])
        if SIM.JDYMAT > SIM.JDYFRZ: SIM.JDYMAT = SIM.JDYFRZ

def __FindGddIndexGreaterOrEqualTo(value: float) -> int:
    """Finds the GDD 1-based index for the specified value."""
    # TONOTE: Full revised
    # This must return the 1-based index.
    for i in range(SIM.JDYPLT-1, SIM.JDYEND):
        if SIM.GDDS[i] >= value: return i + 1
    return SIM.JDYEND + 1

def __FindGddIndicesOld():
    SIM.JDYEFC = __FindGddIndexGreaterOrEqualTo(SIM.Sim.GDD.EFC)
    SIM.JDYMAT = __FindGddIndexGreaterOrEqualTo(SIM.Sim.GDD.MAT)
    SIM.JDYFLO = __FindGddIndexGreaterOrEqualTo(SIM.Sim.GDD.FLO)
    SIM.JDYRIPE = __FindGddIndexGreaterOrEqualTo(SIM.Sim.GDD.RIPE)
    SIM.JDYVEG = __FindGddIndexGreaterOrEqualTo(SIM.Sim.GDD.VEG)

def __FindGddIndices(values: list) -> list:
    """Finds the GDD 1-based index for the specified value."""
    # This method saves many loops.
    n: int = len(values)
    remain = [*range(n)]
    ret: list = [SIM.JDYEND + 1] * n
    
    # TONOTE: Full revised
    # This must return the 1-based index.
    for i in range(SIM.JDYPLT-1, SIM.JDYEND):
        for j in remain:
            if SIM.GDDS[i] >= values[j]:
                ret[j] = i + 1
                remain.remove(j)
                if not remain: return ret
    return ret


def ComputeDailyCropCoefficients():
    """Compute daily value of crop coefficients"""
    
    # @ 3683
    # TONOTE: Fully revised
    JDYSTP: int = SIM.JDYSTR + SIM.Station.NDAYS - 1
    for i in range(SIM.JDYSTR-1, JDYSTP):
        SIM.JDAY = i + 1
        CROPCO()
        SIM.GDD = SIM.GDDS[i]
        SIM.CROPKC[i] = SIM.KC

    SIM.TANUAL = 0.0
    # USELESS see 1.3 on FortranCodeAnalysis.txt
    #TAMP, AIRMIN, AIRMAX = 0.0, 0.0, 0.0
    LAT, ELEV = SIM.Station.LAT, SIM.Station.ELEV
    for i in range(JDYSTP):
        DAY = i + 1
        TMAX = SIM.TMAX[i]
        TMIN = SIM.TMIN[i]
        SIM.TAVG = 0.5 * (TMAX + TMIN)
        RSOA = 753.6 - 6.53 * LAT + 0.0057 * ELEV
        RSOB = -7.1 + 6.4 * LAT + 0.0030 * ELEV
        RSO = RSOA + RSOB * cos(2*3.14159*(DAY-170)/365)
        DELTAT = TMAX - TMIN

        if SIM.PRECIP[i] > 0.2:
            SIM.SOLAR[i] = RSO * exp(0.0146*SIM.TAVG)/(1.0+exp(-DELTAT/36.301))**3.6795
        else:
            SIM.SOLAR[i] = RSO * exp(7.82E-4*SIM.TAVG)/(1.0+exp(-DELTAT/9.4619))**3.6142

        SIM.TANUAL += SIM.TAVG
        # NOTE: These lines are actually useless too
        #if TMAX > AIRMAX: AIRMAX = TMAX
        #if TMIN < AIRMIN: AIRMIN = TMIN

    # TONOTE: Also useless
    #TAMP = AIRMAX - AIRMIN

    SIM.TANUAL /= float(SIM.Station.NDAYS)
