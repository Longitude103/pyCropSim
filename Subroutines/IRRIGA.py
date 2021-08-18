"""IRRIGA implementation module."""

# Implements original Fortran SUBROUTINE IRRIGA (LINES 2745~2984)

# Fully revised module.

# ================================================================
# INPUT
# ================================================================
# KSTG, ICUT
# IRR
# NFDAY
# DPLA
# DPLN
# AWDPLN
# TODAY
# JNEXTI
# GDD
# EAPP
# EREUSE
# PRUNOF
# DDEPTH
# ETR
# CROPKC
# PRECIP
#
# ================================================================
# OUTPUT
# ================================================================
# NETIRR
# GROIRR
# DINF
# IRIGNO
# 
# SIM.Sim.Irrigation.JFIRST
# ================================================================

import SIM

from Data.Irrigation import IrrigationData, IrrigationTypes


def IRRIGA():
    """Irrigation scheduling routine."""

    # Don't Allow Irrigation If Before The First Delivery Date
    # Of If After November 1 For Alfalfa And Grass Or If After The
    # Maturity Date For Other Crops.
    #
    # For Stress Irrigation of Alfalfa And Grass There Is Also a Period
    # Between JSTOPI And JGOI When Irrigation Is Not Allowed

    SIM.NETIRR, SIM.GROIRR = 0.0, 0.0

    ISTAGE: int = SIM.ICUT if SIM.KSTG == 0 else SIM.KSTG

    # Adjusting ISTAGE to a 0-based index
    ISTAGE -= 1

    IRR = SIM.Sim.Irrigation
    RAINSTOR: float = IRR.RAINAL[ISTAGE] * SIM.DPLA

    if IRR.IRRSCH < 3:
        ComputeForAllowableDepletion(IRR, ISTAGE, RAINSTOR)
    elif IRR.IRRSCH == 3:
        ComputeForRotationSystems(IRR, ISTAGE, RAINSTOR)
    elif IRR.IRRSCH in (4, 5):
        ComputeForKnownFutureRainfall(IRR, ISTAGE, RAINSTOR, IRR.IRRSCH == 5)


def ComputeForAllowableDepletion(IRR: IrrigationData, ISTAGE: int, RAINSTOR: float):
    """Computes the irrigation for the allowable depletion scheduling method."""
    # -------------------------------------------------------------------------
    #   Irrigation Scheduled By Allowable Depletion
    #   Only Allow Irrigation If The Gross Irrigation Required Is Larger Than
    #   The Smallest Allowable Irrigation.  This Is The Smallest Depth That
    #   That Will Be Allowed Even Though Leaching May Occur If The Actual
    #   Irrigation With The Existing System Exceeds This Amount.
    #   The Smallest Allowable Irrigation Is The Minimum Amount That Would Be
    #   Practical With The Irrigation System Regardless Of Crop Needs.
    # -------------------------------------------------------------------------
    if SIM.AWDPLN < SIM.DPLA or SIM.TODAY + 1.0 < SIM.JNEXTI or \
            SIM.GDD < IRR.GSTART or SIM.GDD >= IRR.GSTOP:
        return

    SIM.NETIRR = SIM.DPLN - RAINSTOR
    SIM.GROIRR = SIM.NETIRR / SIM.Sim.EAPP[ISTAGE]

    if __adjustIfLessThan(IRR, ISTAGE):
        # For Surface Irrigation Systems Runoff And Reuse Losses Are Considered
        __considerIrrigationLoss(IRR, ISTAGE)


def ComputeForRotationSystems(IRR: IrrigationData, ISTAGE: int, RAINSTOR: float):
    """Computes the irrigation for a rotation system."""
    # Fixed Delivery Schedule For Rotation Systems
    # Check If Water Is Needed.  Irrigate If The Depletion Minus The
    # Rainfall Allowance Exceeds The Smallest Allowable Irrigation.
    SOILMD: float = SIM.AWDPLN - RAINSTOR
    if SOILMD <= SIM.Sim.EAPP[ISTAGE] * IRR.SMALLI[ISTAGE]:
        SIM.NETIRR, SIM.GROIRR, SIM.DINF = 0.0, 0.0, 0.0
    else:
        SIM.GROIRR = SIM.Sim.DDEPTH
        SIM.NETIRR = SIM.Sim.DDEPTH * SIM.Sim.EAPP[ISTAGE]
        SIM.DINF = SIM.NETIRR if IRR.IRRTYP <= 3 else \
            SIM.GROIRR * (1.0 - (1.0 - SIM.Sim.EREUSE[ISTAGE]) * SIM.Sim.PRUNOF[ISTAGE])

        __addIrigNo()


def ComputeForKnownFutureRainfall(IRR: IrrigationData, ISTAGE: int, RAINSTOR: float, considerET: bool):
    """Scheduling with known future rainfall"""
    NFDAY: int = SIM.BLOC.NFDAY
    if SIM.JDAY < SIM.JNEXTI or SIM.GDD < IRR.GSTART or SIM.GDD >= IRR.GSTOP:
        return
    # Compute rain and crop ET for the forecast period
    # FORCRAIN: Rain during future forecast period.
    # SIM.NETIRR = 0.0 # Redundant rest of NETIRR
    FORCET, FORCRAIN = 0.0, 0.0
    if considerET:
        for i in range(SIM.JDAY, SIM.JDAY + NFDAY):
            FORCRAIN += SIM.PRECIP[i]
            FORCET += SIM.ETR[i] * SIM.CROPKC[i]
        # Can delay irrigation if the forecast rain will meet needs
        if SIM.AWDPLN >= SIM.DPLA and FORCRAIN <= 1.0:
            SIM.NETIRR = max(0.0, SIM.DPLN - RAINSTOR)
    else:
        for i in range(SIM.JDAY, SIM.JDAY + NFDAY):
            FORCRAIN += SIM.PRECIP[i]
        # Can delay irrigation if the forecast rain will meet needs
        if SIM.AWDPLN - FORCRAIN >= SIM.DPLA:
            SIM.NETIRR = max(0.0, SIM.DPLN - RAINSTOR)

    SIM.GROIRR = SIM.NETIRR / SIM.Sim.EAPP[ISTAGE]

    __adjustIfLessThan(IRR, ISTAGE)

    # For Surface Irrigation Systems Runoff And Reuse Losses Are Considered
    __considerIrrigationLoss(IRR, ISTAGE)


def __adjustIfLessThan(IRR: IrrigationData, ISTAGE: int) -> bool:
    """Returns False when GROIRR was < SMALLI, so irrigation loss 
    should not be considered for Allowable Depletion schedule."""

    if SIM.GROIRR < IRR.SMALLI[ISTAGE]:
        SIM.NETIRR, SIM.GROIRR, SIM.DINF = 0.0, 0.0, 0.0
        return False

    if SIM.GROIRR < IRR.APMIN[ISTAGE]: SIM.GROIRR = IRR.APMIN[ISTAGE]
    if SIM.GROIRR > IRR.APMAX[ISTAGE]: SIM.GROIRR = IRR.APMAX[ISTAGE]
    SIM.NETIRR = SIM.GROIRR * SIM.Sim.EAPP[ISTAGE]
    return True


def __considerIrrigationLoss(IRR: IrrigationData, ISTAGE: int):
    # For Surface Irrigation Systems Runoff And Reuse Losses Are Considered

    SIM.DINF = SIM.NETIRR if IRR.IRRTYP != IrrigationTypes.Furrow else \
        SIM.GROIRR * (1.0 - (1.0 - SIM.Sim.EREUSE[ISTAGE]) * SIM.Sim.PRUNOF[ISTAGE])

    CYCLET: float = SIM.GROIRR / (IRR.SYSCAP * IRR.IPER[ISTAGE])
    SIM.JNEXTI = max(SIM.TODAY, SIM.JNEXTI) + CYCLET

    __addIrigNo()


def __addIrigNo():
    """Advances the IRIGNO global variable."""
    SIM.IRIGNO += 1
    if SIM.IRIGNO == 1:
        SIM.Sim.Irrigation.JFIRST = SIM.JDAY
