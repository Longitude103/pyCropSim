"""YIELDS implementation"""

# 100% REVISED

# Implements original Fortran SUBROUTINE SNOWMELT (LINES 1798~1848)
# It's called only DEPLT (2156)

# =================================================================
# INPUT DATA                                    
# =================================================================
# CROP:             The crop type
# IYEAR:            Current year of the simulation.
# YMAX:
# YTREND:           Flag indicating if adjustment is required.
# YCOEFF:
# ETYLD:
# ETMAX:
# =================================================================
# OUTPUT
# YIELD:
# YLDRATIO              required for YR output to RepRiver format.
# BVALUE                required for YR output to RepRiver format.
# =================================================================


import SIM

# Coefficients to adjust maximum yields over time for grains, tuber and forage crops
AC = (-22.963, -13.156, -18.249, 1.000, 1.000,
      -11.008, -22.963, -24.578, -17.165, -12.562, -20.334)
BC = (0.01199, 0.00708, 0.00963, 0.00000, 0.00000,
      0.00601, 0.01199, 0.01280, 0.00909, 0.00678, 0.01067)

_AC = (-2.29629993e1, -1.31560001e1, -1.82490005e1, 1.00000000, 1.00000000,
       -1.10080004e1, -2.29629993e1, -2.45779991e1, -1.71650009e1, -1.25620003e1, -2.03339996e1)

_BC = (1.19899996e-2, 7.07999989e-3, 9.63000022e-3, 0.0, 0.0,
       6.01000013e-3, 1.19899996e-2, 1.27999997e-2, 9.08999983e-3, 6.77999994e-3, 1.06699998e-2)


def YIELDS():
    """Implementation of the YIELDS subroutine."""

    # TOASK: About YADJ, the Fortran code says:
    # ===================================================
    # YADJ is the fraction of the yield for the specified
    # year versus what the yield would have been in 2001
    # ===================================================

    YMAX: float = SIM.Sim.YMAX
    ICROP: int = SIM.Sim.CROP - 1
    YCOEFF: float = SIM.Sim.YCOEFF
    # YADJ: fraction of the yield for the specified year VS what the yield would have been in 2001
    YADJ: float = 1.0 if SIM.BLOC.YTREND != 1 else max(0.0, AC[ICROP] + BC[ICROP] * SIM.IYEAR)
    if SIM.Sim.CROP.requiresYieldAdjustment():
        # This code is only required to execute when YADJ is > 0
        if SIM.Sim.IYIELD == 1:
            TR, TA = 0.0, 0.0
            for i in range(5):
                TA += SIM.TPS[i]
                TR += SIM.TDEF[i]
            SIM.YIELD = YADJ * YMAX * (1.0 - YCOEFF * TR / TA)
        else:
            SIM.YIELD = YADJ * YMAX * ((1.0 - YCOEFF) + YCOEFF * SIM.ETYLD / SIM.ETMAX)
    else:
        SIM.YIELD = YMAX

    if SIM.YIELD < 0.0:
        SIM.YIELD = 0.0

    # BVALUE and YLDRATIO required for YR output to RepRiver format.
    SIM.BVALUE = float("inf") if SIM.ETMAX == 0.0 else YADJ * YMAX * YCOEFF / SIM.ETMAX
    SIM.YLDRATIO = SIM.YIELD / (YADJ * YMAX)
