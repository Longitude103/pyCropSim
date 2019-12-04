"""EVAP implementation"""

# TONOTE: 100% REVISED

#===================================
# INPUT
#===================================
# 
# AIRDRY
# DEPTH
# EP

#===================================
# OUTPUT
#===================================

from math import log
from math import sqrt

import SIM

def EVAP():
    """Implements the EVAP subroutine."""

    SIM.E1, SIM.E2 = 0.0, 0.0
    if SIM.EP > 0.0:
        DEPTH = SIM.BLOC.DEPTH
        AIRDRY = SIM.Soil.AIRDRY
        ALPHA = SIM.ALPHA1  
        if ALPHA == 0.0:
            ALPHA = 0.303 * (SIM.Soil.FIELDC[0] - AIRDRY[0]) * DEPTH[0] + 0.0547

        if abs(SIM.THETA[0] - AIRDRY[0]) <= 0.0001:
            # Stage 2 Drying
            EvaporationStage2(ALPHA)
        else:
            # Adjust Potential Evaporation By The Amount Of Residue Cover
            if SIM.RESIDUE > 0.0:
                RESDEP = 1.123E-07 * SIM.RESIDUE / SIM.BLOC.SPGRAV[SIM.OLDCRP-1]
                REDF: float = min(1.0, -0.99 - 0.236 * log(RESDEP))
                if REDF < 0.0: REDF = 0.0
                SIM.EP *= REDF

            # Stage 1 Drying
            SIM.TIME = float(SIM.JDAY)
            AVAIL: float = (SIM.THETA[0] - AIRDRY[0]) * DEPTH[0]
            if AVAIL >= SIM.EP:
                SIM.E1 = SIM.EP
            else:
                # Transition from Stage 1 to Stage 2
                SIM.TIME = float(SIM.JDAY-1) + AVAIL / SIM.EP
                SIM.E1 = AVAIL
                SIM.E2 = ALPHA * sqrt(1.0 - AVAIL / SIM.EP)
                AVAIL2: float = (SIM.THETA[1] - AIRDRY[1]) * DEPTH[1]
                if SIM.E2 > AVAIL2: SIM.E2 = AVAIL2
                if (SIM.E1 + SIM.E2) > SIM.EP:
                    SIM.E2 = SIM.EP - SIM.E1
                    #SIM.TIME = float(SIM.JDAY) - (SIM.E2 / ALPHA) ** 2.0
                    SIM.TIME = float(SIM.JDAY) - ((SIM.E2 / ALPHA)*(SIM.E2 / ALPHA))

        if SIM.E1 < 0.0: SIM.E1 = 0.0
        if SIM.E2 < 0.0: SIM.E2 = 0.0

def EvaporationStage2(alpha: float):
    """Stage 2 Drying"""
    if SIM.THETA[1] > SIM.Soil.AIRDRY[1]:
        SIM.E2 = alpha * (sqrt(float(SIM.JDAY)-SIM.TIME) - sqrt(float(SIM.JDAY-1)-SIM.TIME))
        if SIM.E2 > SIM.EP: SIM.E2 = SIM.EP
        AVAIL2 = (SIM.THETA[1] - SIM.Soil.AIRDRY[1]) * SIM.BLOC.DEPTH[1]
        if SIM.E2 > AVAIL2: SIM.E2 = AVAIL2
