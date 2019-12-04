"""EPRECIP implementation"""

# 100% REVISED

#=================================================================
# INPUT DATA                                    REQUIRED FOR CROPS
#=================================================================
# DEPTH[LAYER]
# THETA[LAYER]
# FIELDC[LAYER]
# PWP[LAYER]
# 
# IHYGRP
# CN
# CNFALLOW
# RESIDUE
# RESTYP
# OLDCRP
# 
# GDD               Growing Degree Days                     ALL
# GDDEFC
# GDDVEG
#
# SATWC
#
# RAIN
#=================================================================
# OUTPUT
#=================================================================
# CURVNO
# RUNON
# RUNOFF
# EPRECIP
# AWATER
#=================================================================


import sys
from math import exp
from math import log
from math import sqrt

import SIM

def EFPRECIP():
    """Implements the EFPRECIP subroutine."""
    # TONOTE: Fully revised method.
    # Calculate The Runoff Fraction From The Antecedent Moisture @1642
    S: float = CalculateRunOffFraction(GetCurveNumber())
    #S /= 25.4

    # Calculate The Effective Precip.
    CalculateEffectivePrecipitation(S)

def CalculateRunOffFraction(CNUMB: float) -> float:
    """Calculate The Runoff Fraction From The Antecedent Moisture"""
    # TONOTE: Fully revised method.

    S3 = 25.4 * (1000.0 / (23.0 * CNUMB / (10.0 + 0.13 * CNUMB)) - 10.0)
    SMAX = 25.4 * (1000.0 / (4.2 * CNUMB / (10.0 - 0.058 * CNUMB)) - 10.0)

    tempDepth = 0.0
    pwp, depth = 0.0, 0.0
    TOTRDP, RUNDEP = 0.0, 12.0
    SW, SAT, FC = 0.0, 0.0, 0.0
    for i in range(SIM.Sim.LAYERS):
        pwp = SIM.PWP[i]
        depth = SIM.BLOC.DEPTH[i]
        TOTRDP += depth
        tempDepth = depth if TOTRDP < RUNDEP else RUNDEP - (TOTRDP - depth)
        SAT += (SIM.SATWC - pwp) * 25.4 * tempDepth
        SW += (SIM.THETA[i] - pwp) * 25.4 * tempDepth
        FC += (SIM.Soil.FIELDC[i] - pwp) * 25.4 * tempDepth
        if TOTRDP >= RUNDEP:
            break

    temp: float = log(FC / (1.0 - S3 / SMAX) - FC)
    W2: float = (temp - log(SAT / (1.0 - 2.54 / SMAX) - SAT)) / (SAT - FC)
    W1: float = temp + W2 * FC
    S: float = max(2.54, SMAX * (1.0 - SW / (SW + exp(W1 - W2 * SW))))
    SIM.CURVNO = 25400.0 / (S + 254.0)
    return S

def GetCurveNumber() -> float:
    """Return the Curve Number for the current crop."""
    # TONOTE: Fully revised method
    CN = SIM.BLOC.CN
    # TONOTE: In Fortran => IHYGRP = SOIL/10 - 10*(SOIL/100)
    #IHYGRP:int = int(SIM.SOIL/10.0 - 10.0*(SIM.SOIL/100.0))
    IHYGRP: int = SIM.Soil.HydrologicGroup - 1
    CNUMB: float = CN[SIM.Sim.CROP][IHYGRP]
    if SIM.Sim.CROP < 10:
        # Adjust Curve Number For Residue Cover for small grain and row crops.
        # TONOTE: I guess we are using OLDCRP instead of 
        #           CROP because is about the residue cover, right?
        INVCNFACT: float = 1.0 - max(GetCurveAdjustmentFactor(\
            SIM.RESIDUE, SIM.BLOC.RESTYP[SIM.OLDCRP - 1]), 0.0)
        
        CNFALLOW: float = SIM.BLOC.CNFALLOW[IHYGRP]
        CNFALO: float = CNFALLOW * INVCNFACT
        
        GDD = SIM.Sim.GDD
        if SIM.GDD <= GDD.VEG:
            CNUMB = CNFALO
        else:
            CNAVG: float = CNUMB * INVCNFACT
            if SIM.GDD <= GDD.EFC:
                CNUMB = CNFALO + (CNAVG-CNFALO) * (SIM.GDD-GDD.VEG) / (GDD.EFC-GDD.VEG)
            else:
                CNPEAK: float = (2.0 * CNUMB - CNFALLOW) * INVCNFACT
                CNUMB = CNAVG + (CNPEAK-CNAVG) * (SIM.GDD-GDD.EFC) / (GDD.MAT-GDD.EFC)
            
        if SIM.GDD > GDD.MAT: CNUMB = CNFALO * INVCNFACT

    return CNUMB

def GetCurveAdjustmentFactor(residue: float, residueType: int) -> float:
    """Returns the Curve Number adjusted factor
    based on the specified type and amount of residue. """
    # TONOTE: Fully revised method
    if residueType == 1:
        return (12.648 - 4.7000 / sqrt(0.001123 * residue)) / 100.0
    # Get the adjustment factor for Corn and Sorghum
    return (12.456 - 6.4098 / sqrt(0.001123 * residue)) / 100.0

def RunOffFractionToCurveNumber(runOffFraction: float) -> float:
    """Computes the Curve Number for the run-off fraction."""
    # TONOTE: Not used by now, but could be handy in the future.
    return 25400.0 / (runOffFraction + 254.0)

def CalculateEffectivePrecipitation(S: float):
    """Calculate The Effective Precipitation."""
    # TONOTE: Fully revised method.
    # Compute The Relative Runoff -- Fraction Of Precipitation
    RRUNOF: float = ComputeRelativeRunoff(S / 25.4, SIM.RAIN)

    # alculate The Effective Precipitation.
    # Increase the depth in the channel portion of conservation terraces.
    if SIM.Sim.ITERRC == 0:
        # If not a terrace channel
        SIM.EPRECIP = SIM.RAIN * (1.0 - RRUNOF)
        SIM.RUNON = 0.0
        SIM.RUNOFF = SIM.RAIN - SIM.EPRECIP
    else:
        SIM.RUNON = SIM.RAIN * RRUNOF * (SIM.Sim.TINTRV-SIM.Sim.CHANW) / SIM.Sim.CHANW
        DPOND: float = (SIM.RAIN * RRUNOF + SIM.RUNON) / 12.0
        # Depth of ponded water in the channel (in feet).
        if DPOND <= SIM.Sim.CHAND:
            SIM.RUNOFF = 0.0
            SIM.EPRECIP = SIM.RUNON + SIM.RAIN
        else:
            SIM.RUNOFF = (DPOND - SIM.Sim.CHAND) * 12.0
            SIM.EPRECIP = SIM.RAIN * (1.0-RRUNOF) + SIM.Sim.CHAND * 12.0

    if SIM.RUNOFF < 0.0 or (SIM.EPRECIP > SIM.RAIN and SIM.Sim.ITERRC == 0):
        # TOASK: Here the Fortran code exists after printing some variable values to the console
        # It seems that the simulation has found some kind of error condition,
        # however, it does not display any error message.
        # By now, I'm replicating the Fortran code behaviour.
        print(" @ 1487:", SIM.JDAY, SIM.Sim.CROP, SIM.SOIL, SIM.RAIN, S * 25.4, RRUNOF,
              SIM.EPRECIP, SIM.RAIN, SIM.RUNOFF, SIM.Sim.ITERRC, SIM.CurrentCrop.SIMFILE)
        sys.exit()

def ComputeRelativeRunoff(S: float, P: float) -> float:
    """Compute The Relative Runoff -- Fraction Of Precipitation"""
    # TONOTE: Fully revised method.
    #return 0.0 if S * 0.2 > P else (((P - 0.2*S)**2.0) / (P + 0.8*S)) / P
    S02: float = S * 0.2
    if S02 > P: return 0.0
    P02S: float = P - S02
    return ((P02S * P02S) / (P + 0.8*S)) / P
