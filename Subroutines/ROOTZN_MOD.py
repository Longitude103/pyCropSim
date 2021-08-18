"""ROOTZN implementation"""

# 100% REVISED

# Implements original Fortran SUBROUTINE ROOTZN (LINES 1723~1797)

# =================================================================
# INPUT DATA                                    REQUIRED FOR CROPS
# =================================================================
# RZMIN
# RZMAX
# RZMGMT
# GDD               Growing Degree Days                     ALL
# GDDFLO
# GDDROOT
# DEPTH[LAYER]
# PERRZD[LAYER]
# AVMFT[LAYER]
# PAWFT[LAYER]
# =================================================================
# OUTPUT
# =================================================================
# RDZ
# RDF[LAYER]
# PERRZD[LAYER]
# PAW
# AWATER
# =================================================================


import SIM


# TONOTE: Very weird that the arguments to RDIST were named like that instead of Z1,Z2


def RDIST(Z2: float, Z1: float) -> float:
    """Root distribution function."""
    # return 2.0633 * (Z2 - Z1) - 1.622 * (Z2*Z2 - Z1*Z1) + 0.5587 * (Z2**3.0 - Z1**3.0)
    # TONOTE: Changed the exponentation function with integers to try to match Fortran results.
    return 2.0633 * (Z2 - Z1) - 1.622 * (Z2 * Z2 - Z1 * Z1) + 0.5587 * (Z2 * Z2 * Z2 - Z1 * Z1 * Z1)


def ROOTZN():
    """Implements the ROOTZN subroutine."""
    # TONOTE: In the original Fortran code, there were 3 DO loops
    # This Python code does the same in a single loop.
    # 1. Loop: <- DEPTH, -> REMAIN, PERRZD, == DEPTH
    # 2. Loop: 

    GDDROOT: float = SIM.Sim.GDDROOT
    RZMIN, RZMAX = SIM.Sim.RZMIN, SIM.RZMAX
    RZD: float = (RZMAX - RZMIN) * (SIM.GDD - GDDROOT) / (SIM.Sim.GDD.FLO - GDDROOT) + RZMIN

    if RZD > RZMAX:
        RZD = RZMAX
    if RZD < RZMIN:
        RZD = RZMIN

    # TONOTE: This was giving different values from the original code since RZMIN > RZMAX
    # RZD = min(RZMAX, max(RZMIN, RZD))

    depth = 0.0
    ZU, ZL = 0.0, 0.0
    FDEPTH: float = 0.0
    REMAIN: float = RZD
    RZMGMT: float = SIM.RZMGMT
    SIM.PAW, SIM.AWATER = 0.0, 0.0
    TOPDEP: float = 0.0  # Top depth of a soil layer.
    BOTDEP: float = 0.0  # Bottom depth of a soil layer.

    for i in range(SIM.Sim.LAYERS):
        depth = SIM.BLOC.DEPTH[i]
        # Calculate The Percent Of Each Layer Filled With Roots
        REMAIN -= depth
        if REMAIN >= 0.0: SIM.PERRZD[i] = 1.0
        if -depth < REMAIN < 0.0:
            SIM.PERRZD[i] = (depth + REMAIN) / depth
        if REMAIN < 0.0: REMAIN = 0.0
        # Compute the available water in the irrigation management zone
        # that extends through the RZMGMT depth and the plant available
        # water in the whole root zone. TOPDEP and BOTDEP are the top
        # and bottom depths of a soil layer. When RZMGMT lies between the
        # top and bottom the fraction of the layer that contributes to
        # available water is the distance from the top to RZMGMT if the
        # roots are below RZMGMT, or PERRZD if the roots are above RZMGMT.
        TOPDEP = BOTDEP
        BOTDEP += depth
        if BOTDEP <= RZMGMT: SIM.AWATER += SIM.AVMFT[i] * SIM.PERRZD[i]
        # TONOTE: Removed a redundat condition
        if TOPDEP < RZMGMT < BOTDEP:
            FDEPTH = SIM.PERRZD[i] if RZD < RZMGMT else (RZMGMT - TOPDEP) / depth
            SIM.AWATER += SIM.AVMFT[i] * FDEPTH
        SIM.PAW += SIM.PAWFT[i] * SIM.PERRZD[i]

        ZU = ZL
        ZL += depth / RZD
        if ZL > 1.0:
            ZL = 1.0

        SIM.RDF[i] = RDIST(ZL, ZU)

    # Update Globals
    SIM.RZD = RZD
