"""SNOWMELT implementation"""

# Implements original Fortran SUBROUTINE SNOWMELT (LINES 3900~4019)
# It's called once at DEPL if there's some snow or precipitation.
# I's called just before EFPRECIP

#==================================================================
# INPUT
#==================================================================
# JDAY
# TIMP
# TAVG
# SFTMP
# SMTMP
# SMFMN
# SMFMX
# SNOCOV1
# SNOCOV2
# SNOCOVMX
#==================================================================
# I/O
#==================================================================
# SNOTMP
# SNOH20
# RAIN
#==================================================================
# OUTPUT
#==================================================================
# SNOMLT
#==================================================================

from math import sin
from math import exp

import SIM

# TONOTE: Weird thing about SMTMP, is declared and read in SNOWMELT, but never assigned

SMTMP = 0.0
"""Snow melt base temperature (in °F)."""


def SNOWMELT(JDAY: int):
    """This subroutine predicts daily snom melt."""

    # (LINE 3976)
    # Estimate snow pack temperature
    # TONOTE: SNOTMP comes from the initial data file and previous simulation results,
    # the same as SNOH2O, SNOTMP only read and modified here,
    # SNOH2O also read at SOILTEMP
    SIM.SNOTMP = SIM.SNOTMP * (1.0 - SIM.BLOC.TIMP) + SIM.TAVG * SIM.BLOC.TIMP
    # Calculate snow fall
    if SIM.TAVG <= SIM.BLOC.SFTMP:
        SIM.SNOH2O += SIM.RAIN
        # TONOTE: SNOFALL is not actually used, only assigned in one statement, never used.
        # SIM.SNOFALL = SIM.RAIN
        SIM.RAIN = 0.0


    # Adjust melt factor for time of year
    IJDAY: int = JDAY - 1
    if SIM.SNOH2O > 0.0 and SIM.TMAX[IJDAY] > SMTMP:
        SMFMX: float = SIM.BLOC.SMFMX
        SMFMN: float = SIM.BLOC.SMFMN
        SMFAC: float = (SMFMX + SMFMN) / 2.0 + sin((JDAY - 81)/58.09) * (SMFMX - SMFMN) / 2.0
        SNOMLT: float = SMFAC * (((SIM.SNOTMP + SIM.TMAX[IJDAY]) / 2.0) - SMTMP)
        # SNOMLT: Amount of water in snow melt (in H₂O).
        # Adjust for areal extent of snow cover
        if SIM.SNOH2O < SIM.BLOC.SNOCOVMX:
            # XX is the ratio of amount of current day's snow water
            XX: float = SIM.SNOH2O / SIM.BLOC.SNOCOVMX
            SNOMLT *= XX / (XX + exp(SIM.BLOC.SNOCOV1 - SIM.BLOC.SNOCOV2 * XX))

        if SNOMLT < 0: SNOMLT = 0.0
        if SNOMLT > SIM.SNOH2O: SNOMLT = SIM.SNOH2O
        SIM.SNOH2O -= SNOMLT
        SIM.RAIN += SNOMLT
