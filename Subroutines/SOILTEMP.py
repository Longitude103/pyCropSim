"""SOILTEMP implementation"""
# Implements original Fortran SUBROUTINE SOILTEMP (LINES 3728~3897)

# TONOTE: 100% REVISED

# =================================================================
# INPUT DATA
# =================================================================
# CROP:             The crop type
# SOIL
# JDAY:             Current Julian Day of the simulation.
# JDYMAT:           Julian Day of maturity.
# JDYPLT            Julian Day of planting.
# TMIN, TMAX, TAVG, TANUAL
# SNOH2O
# KC
# YMAX
# YDENS
# RESRAT
# RESIDUE

# TOTDEP
# TOTWAT
# 
# BULKD
# SOLAR

# CENTER
# SOILT
# =================================================================
# STATIC==========================================================
# KCL, KCU          Lower and Upper limits to KC
# =================================================================
# OUTPUT
# TAVG
# SOILT
# =================================================================


from math import log
from math import exp

import SIM

TLAG: float = 0.8
"""Lag coefficient for soil temperature."""


def SOILTEMP():
    """This method estimates daily average temperature at the bottom of each soil layer."""

    ROM = SIM.BLOC
    BULKD: float = SIM.Soil.BULKD

    # DP: Maximum damping depth, in inches.
    # SWAT manual equation 2.3.6
    DP: float = 39.4 + 98.4 * (BULKD / (BULKD + 686.0 * exp(-5.63 * BULKD)))
    # WC: scaling factor for soil water impact on daily damping depth
    # SWAT manual equation 2.3.7
    WC: float = SIM.TOTWAT / ((0.356 - (0.144 * BULKD)) * SIM.TOTDEP)
    # DD: damping depth for day, in mm.
    # SWAT manual equation 2.3.8
    # DD: float = DP * exp(log(19.7 / DP) * ((1.0 - WC) / (1.0 + WC))**2.0)
    base: float = (1.0 - WC) / (1.0 + WC)
    DD: float = DP * exp(log(19.7 / DP) * (base * base))

    # Compute the amount of soil cover from above ground biomass (AGBIO) and crop residue (RESIDUE).
    AGBIO: float = 0.0
    if SIM.JDYPLT <= SIM.JDAY < SIM.JDYMAT and SIM.ETMAX > 0.0:
        ICROP = SIM.Sim.CROP - 1
        AGBIO = SIM.Sim.YMAX * ROM.YDENS[ICROP] * ROM.RESRAT[ICROP]
        AGBIO *= (SIM.KC - ROM.KCL[ICROP]) / (ROM.KCU[ICROP] - ROM.KCL[ICROP])

    # Calculate lag factor for soil cover impact on soil surface temperature.
    # SWAT manual equation 2.3.11
    CV: float = SIM.RESIDUE + AGBIO
    # BCV: lagging factor for cover
    BCV: float = 1.123 * CV / (1.123 * CV + exp(7.563 - 1.4566E-4 * CV))

    if SIM.SNOH2O >= 0.0:
        XX: float = 1.0
        if SIM.SNOH2O <= 4.724:
            XX = SIM.SNOH2O / (SIM.SNOH2O + exp(6.055 - 7.625 * SIM.SNOH2O))
        # TONOTE: Maybe this max(1.0, BCV) should be done anyway? Also when SNOH20 < 0.0
        BCV = max(XX, BCV)

    # Calculate temperature at soil surface
    ALBEDO: float = 0.8
    if SIM.SNOH2O <= 0.02:
        COV: float = exp(-5.0E-5 * 1.123 * CV)
        ALBSOIL: float = 0.30 - 0.10 * (SIM.Soil.AvailableWaterHoldingCapacity - 4.0) / 5.0
        # ALBSOIL: float = 0.30 - 0.10 * (SIM.SOIL/100.0 - 4.0) / 5.0
        ALBEDO = 0.23 * (1.0 - COV) + COV * ALBSOIL

    IJDAY: int = SIM.JDAY - 1
    # SWAT manual equation 2.3.10
    # STO: Radiation hitting soil surface on day, in MJ/m²
    STO: float = (4.1855E-02 * SIM.SOLAR[IJDAY] * (1.0 - ALBEDO) - 14.0) / 20.0
    # SWAT manual equation 2.3.9
    SIM.TAVG = (SIM.TMAX[IJDAY] + SIM.TMIN[IJDAY]) / 2.0
    # TBARE: Temperature of bare soil surface, in °C.
    TBARE: float = SIM.TAVG + 0.5 * (SIM.TMAX[IJDAY] - SIM.TMIN[IJDAY]) * STO

    # SURFTEMP: Temperature of soil surface, in °C.
    SURFTEMP: float = TBARE
    if SIM.RESIDUE > 0.01 or SIM.SNOH2O > 0.01:
        # SWAT manual equation 2.3.12
        # TCOV: temperature of soil surface corrected for cover, in °C.
        TCOV: float = BCV * SIM.SOILT[1] + (1.0 - BCV) * TBARE
        SURFTEMP = min(TBARE, TCOV)

    # calculate temperature for each layer on current day
    # ZD: ratio of depth at center of layer to damping depth
    # TLAG is the lag coefficient for soil temperature.
    for k in range(SIM.Sim.LAYERS):
        # calculate depth at center of layer (SWAT manual equation 2.3.5)
        ZD = SIM.CENTER[k] / DD
        # SWAT manual equation 2.3.4
        DF = ZD / (ZD + exp(-0.8669 - 2.0775 * ZD))
        # SWAT manual equation 2.3.3
        SIM.SOILT[k] = TLAG * SIM.SOILT[k] + (1.0 - TLAG) * (DF * (SIM.TANUAL - SURFTEMP) + SURFTEMP)
