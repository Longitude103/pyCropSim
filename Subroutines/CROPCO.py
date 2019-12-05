"""Implementation module for the CROPCO subroutine."""

# Implements original Fortran SUBROUTINE CROPCO (LINES 2985~3546)
# Called only by READWEAT

# TONOTE: Fully revised module.

# =================================================================
# INPUT DATA                                    REQUIRED FOR CROPS
# =================================================================

# CROP:             The crop type
# JDAY:             Current Julian Day of the simulation.   ALL
# JDYFRZ:           Freeze Date                             ALL
# JDYEFC:           Day to effective cover.             <=7 ONLY
# JFPLT             Day of planting.                    <=7 and 10
# ICUT              Not sure. Cut index to grow stage?  10 only
# JDYCUT            Julian Day of Cutting.              10 and 11
# GDD               Growing Degree Days                     ALL
# GDDMAT            GDD TO MATURITY                         ALL
# STATIC==========================================================
# CC                Crop Coefficients.                  <=7 and 10
# KCL, KCU          Lower and Upper limits to KC            ALL
# =================================================================
# OUTPUT
# KC:
# =================================================================

import SIM
# SIM is the module which holds global data accessed an modified
# during the different simulation stages and subroutines.

from Fortran import INT

from Data.Crop import CropId

FSKC = {
    9: (0.192, 0.462, 0.808, 0.150, 1.000, 0.300),
    12: (0.036, 0.109, 0.927, 0.243, 0.750, 0.669),
    13: (0.036, 0.109, 0.927, 0.243, 0.587, 0.587),
    # TONOTE: In the Fortan code we can see changes (see @3256)
    # in the KCMID and KCEND values for CROP = 13 dated at 5-26-03
    # that were later commented out and using the original values.
    14: (0.036, 0.073, 1.000, 0.688, 0.746, 0.746),
    15: (0.000, 0.100, 1.000, 0.150, 0.150, 0.150),
    16: (0.105, 0.158, 0.842, 0.364, 1.082, 0.798),
    17: (0.105, 0.158, 0.842, 0.547, 0.873, 0.691),
    18: (0.071, 0.286, 0.857, 0.243, 1.011, 0.282),
    19: (0.036, 0.109, 1.000, 0.729, 1.011, 0.606),
    20: (0.010, 0.100, 1.000, 0.800, 0.800, 0.800),
    21: (0.010, 0.100, 1.000, 0.526, 0.526, 1.012),
    22: (0.036, 0.109, 0.927, 0.243, 0.587, 0.587)
    }
"""Coefficients for straight computing of the majority of crop types."""

# FGS stands for Full Growing Season


def CROPCO():
    """Compute Daily Crop Coefficient."""

    # Crops 1 - 7 Represent Spring Grains, Edible Beans, Soybeans,
    # Potatoes, Sugar Beets, Grain Sorghum (Milo), Winter Wheat.
    # The Crop Coefficients For These Crops Are Based On Data From Jim Wright (1982)

    # TONOTE: See the different ways to represent CROP,
    # as an integer (easier to compare with the previous code)
    # or as an Enumeration (easier to understand the new code).
    # Which do you prefer ?
    CROP = SIM.Sim.CROP
    if CROP <= 7:
        __CROPCO7()
    elif CROP == CropId.Corn:
        __CROPCO8()
    elif CROP == CropId.Alfalfa:
        __CROPCO10()
    elif CROP == CropId.IrrigatedHay:
        __CROPCO11()
    else:
        cc = FSKC[CROP]
        __CROPCO(cc[0], cc[1], cc[2], cc[3], cc[4], cc[5])

    # Check Bounds On Crop Coefficients
    ICROP: int = CROP - 1
    # TONOTE: if SIM.JDAY > SIM.JDYFRZ is True, the performed computation is useless.
    if SIM.JDAY > SIM.JDYFRZ or SIM.KC < SIM.BLOC.KCL[ICROP]:
        SIM.KC = SIM.BLOC.KCL[ICROP]
    if SIM.KC > SIM.BLOC.KCU[ICROP]:
        SIM.KC = SIM.BLOC.KCU[ICROP]


def __CROPCO(FS1: float, FS2: float, FS3: float, KCINI: float, KCMID: float, KCEND: float):
    __CROPCO_FGS(SIM.GDD / SIM.Sim.GDD.MAT, FS1, FS2, FS3, KCINI, KCMID, KCEND)


def __CROPCO_FGS(FGS: float, FS1: float, FS2: float, FS3: float,
                 KCINI: float, KCMID: float, KCEND: float):
    """Adjust Kc based on FGS"""
    assert FS1 < FS2 < FS3
    # TONOTE: In some cases, KCEND > KCMID and even > KCINI (WHY ?)
    # assert(KCINI < KCMID < KCEND)

    if FGS > 1.0 or FGS <= FS1:
        SIM.KC = KCINI
    elif FS1 < FGS < FS2:
        SIM.KC = KCINI + (KCMID-KCINI) * (FGS-FS1) / (FS2-FS1)
    elif FS2 <= FGS <= FS3:
        SIM.KC = KCMID
    elif FS3 < FGS <= 1.0:
        SIM.KC = KCMID - (KCMID-KCEND) * (FGS-FS3) / (1.0-FS3)
    # TONOTE: Maybe missing a condition in which KC takes the KCEND value ?
    # Maybe this should happen when FGS > 1.0 ?


def __CROPCO7():
    """Compute Daily Crop Coefficient for Spring Grains, Edible Beans, Soybeans,
    Potatoes, Sugar Beets, Grain Sorghum (Milo) and Winter Wheat."""

    # TONOTE: Fully revised method.
    # Adjusted code for 0-base indexing
    # TONOTE: I changed the IF comparing workflow for optimization.
    IEFC, PCT = SIM.IEFC, 0.0
    # IEFC: Index to growing stage.
    if SIM.JDAY > SIM.JDYEFC:
        IEFC = 1
        PCT = float(SIM.JDAY - SIM.JDYEFC) / 100.0
    else:
        IEFC = 0
        PCT = float(SIM.JDAY - SIM.JDYPLT) / float(SIM.JDYEFC - SIM.JDYPLT)

    CROP = SIM.Sim.CROP
    ICROP = SIM.Sim.CROP - 1
    CC = SIM.BLOC.CC
    KCL = SIM.BLOC.KCL
    # TONOTE: Conditional branching changed for readability and performace,
    # Now it requires less comparisions saving CPU instructions.
    # TONOTE: Here, the lower limit is also assigned for PCT > 1.0
    if PCT < 0.0 or PCT > 1.0:
        SIM.KC = KCL[ICROP]
    else:
        IPCT = INT(PCT / 0.1)
        mod = 10.0 * (PCT % 0.1)
        # TONOTE: When IPCT == 0 and IEFC != 0, KC is never assigned.
        # IEFC is 0 when JDAY <= JDYEFC
        # However, KC is finally clamped (for every condition) to the KCL~KCU range.
        # Bug or desired behaviour ?
        if 0 < IPCT < 10:
            if IPCT == 2 and PCT < 0.1:
                SIM.KC = CC[CROP][IEFC][0] + mod * (CC[CROP][IEFC][1]-CC[CROP][IEFC][0])
            else:
                SIM.KC = CC[CROP][IEFC][IPCT-1] + mod*(CC[CROP][IEFC][IPCT]-CC[CROP][IEFC][IPCT-1])
        elif IPCT == 10:
            SIM.KC = CC[CROP][IEFC][9]
        elif IPCT == 0:
            if IEFC == 0:
                SIM.KC = KCL[ICROP] + mod * (CC[CROP][IEFC][0]-KCL[ICROP])
            else:
                print("WARNING: KC is not being assigned.")

    if CROP == 7 and SIM.JDAY >= SIM.JFPLT > 0:
        SIM.KC = 0.25

    SIM.IEFC = IEFC

    # The original code performs a redundant range clamping here,
    # since it is perfomed anyway at the end of CROPCO for all cases.
    # if SIM.KC > SIM.BLOC.KCU[ICROP]: SIM.KC = SIM.BLOC.KCU[ICROP]
    # if SIM.KC < KCL[ICROP]: SIM.KC = KCL[ICROP]


def __CROPCO8():
    """Compute Daily Crop Coefficient for Corn.
    Kc from Bill Kranz
    Values from Watts (1982) and Stegman (1988)"""
    # TONOTE: Fully revised method.
    GDD = SIM.GDD
    GDDMAT = SIM.Sim.GDD.MAT
    SIM.KC = SIM.BLOC.KCU[SIM.Sim.CROP - 1]
    if GDD <= 0.12 * GDDMAT:
        SIM.KC = 0.15
    elif GDD < 0.42 * GDDMAT:
        SIM.KC = 0.15 + 0.85 * (GDD-0.12*GDDMAT) / (0.3*GDDMAT)
    elif GDD > 0.78 * GDDMAT:
        SIM.KC = 1.0 - 0.7 * (GDD-0.78*GDDMAT) / (0.22*GDDMAT)
    elif GDD > GDDMAT:
        SIM.KC = 0.15

    # Range adjustment.
    # TONOTE: The following instructions could be written as:
    # SIM.KC = min(SIM.BLOC.KCU[SIM.Sim.CROP-1], max(0.15, SIM.KC))
    # using V = min(MAX, max(MIN, V)) makes the code more readable
    # but slower (~2X) than IF-checking, which is your preference?
    # if SIM.KC > SIM.BLOC.KCU[SIM.Sim.CROP-1]:
    #    SIM.KC = SIM.BLOC.KCU[SIM.Sim.CROP-1]
    if SIM.KC < 0.15:
        SIM.KC = 0.15


def __CROPCO10():
    """Compute crop coefficients for alfalfa. Kc from Wright (1982)"""
    # TONOTE: Fully revised method.
    # ICUT as the 0-base index
    GetCuttingIndices()
    JDAY, JDYCUT, ICUT, IEFC = SIM.JDAY, SIM.Sim.JDYCUT, SIM.ICUT - 1, SIM.IEFC

    # Compute The Percent Time For Each Stage
    PCT = SIM.PCT
    if ICUT == 0 and JDAY >= SIM.JDYPLT:
        PCT = float(JDAY-SIM.JDYPLT)/float(JDYCUT[0]-SIM.JDYPLT)

    if SIM.Config.LEGACY:
        # TONOTE: Getting legacy and probably buggy behaviour.
        if ICUT == 1:
            if SIM.IEFC == 1:
                PCT = float(JDAY-JDYCUT[0])/float(JDYCUT[1]-JDYCUT[0])
            else:
                PCT = float(JDAY-JDYCUT[0])/float(305.0-JDYCUT[0])
        elif 2 <= ICUT <= 4:
            if SIM.IEFC == 1:
                PCT = float(JDAY-JDYCUT[ICUT-1])/float(JDYCUT[ICUT]-JDYCUT[ICUT-1])
            else:
                PCT = float(JDAY-JDYCUT[ICUT])/float(305.0-JDYCUT[ICUT])
    else:
        if 1 <= ICUT <= 4:
            PCT = float(JDAY-JDYCUT[ICUT-1])/float(JDYCUT[ICUT]-JDYCUT[ICUT-1]) \
                if IEFC == 1 else float(JDAY-JDYCUT[ICUT])/float(305.0-JDYCUT[ICUT])

    # 0-based index for CC[CROP] (0,1,2)
    CROP = SIM.Sim.CROP
    ICROP = CROP - 1
    if JDAY <= SIM.JDYPLT or JDAY >= 305:
        SIM.KC = SIM.BLOC.KCL[ICROP]
        # TONOTE: Maybe we can (or should) exit the method here

    CC = SIM.BLOC.CC
    IPCT = INT(PCT / 0.1)
    # IPCT here is a 1-based index
    # CC is a dictionary so is accessed by the 1-based index instead of the 0-based
    if IPCT == 10:
        SIM.KC = CC[CROP][IEFC][9]
    else:
        mod = 10.0 * (PCT % 0.1)
        if IPCT == 0:
            SIM.KC = SIM.BLOC.KCL[ICROP] + mod * (CC[CROP][IEFC][IPCT] - SIM.BLOC.KCL[ICROP])
        elif 0 < IPCT < 10:
            SIM.KC = CC[CROP][IEFC][IPCT-1] + mod * (CC[CROP][IEFC][IPCT] - CC[CROP][IEFC][IPCT-1])


def GetCuttingIndices():
    """Gets IEFC and ICUT for Alfalfa coefficients."""

    JDAY, JDYCUT = SIM.JDAY, SIM.Sim.JDYCUT
    
    if JDAY < JDYCUT[0]:
        SIM.IEFC, SIM.ICUT = 0, 1
    if JDYCUT[0] <= JDAY < JDYCUT[1]:
        SIM.IEFC, SIM.ICUT = 1, 2
    for i in range(1, 4):
        if JDYCUT[i] < JDAY < JDYCUT[i + 1]:
            SIM.IEFC, SIM.ICUT = 1, i + 2
    if JDAY >= JDYCUT[SIM.Sim.NCUT - 1]:
        SIM.IEFC, SIM.ICUT = 2, SIM.Sim.NCUT


def __CROPCO11():
    """Compute crop coefficients for Irrigated Hay."""

    GDDMAT = SIM.Sim.GDD.MAT
    JDYCUT = SIM.Sim.JDYCUT[0]
    if SIM.JDAY == JDYCUT:
        SIM.GDDCUT = SIM.GDD

    FGS = SIM.GDD / GDDMAT if SIM.JDAY < JDYCUT else \
        (SIM.GDD-SIM.GDDCUT) / (GDDMAT-SIM.GDDCUT)
    __CROPCO_FGS(FGS, 0.036, 0.109, 0.927, 0.243, 0.750, 0.669)
