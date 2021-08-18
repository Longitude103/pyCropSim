"""NTHET implementation"""

# 100% REVISED.

import SIM


def NTHET():
    """Calculate The Amount Of Water That Can Be Added To Each Layer"""

    DINFL: float = 0.0
    # The amount of water added to a layer.
    AMT: float = 0.0
    # The amount of water that can be added to a layer

    for i in range(SIM.Sim.LAYERS):
        if SIM.DINF == 0.0: return
        AMT = (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i]
        if AMT < 0.0: AMT = 0.0

        if AMT >= SIM.DINF:
            DINFL = SIM.DINF
            SIM.DINF = 0.0
        else:
            DINFL = AMT
            SIM.DINF -= AMT

        # Add Water To The Layer
        SIM.THETA[i] += DINFL / SIM.BLOC.DEPTH[i]

    # If Any Water Is Left Then Add An Equal Amount To Every Layer
    THETUP: float = SIM.DINF / SIM.TOTDEP
    for i in range(SIM.Sim.LAYERS):
        SIM.THETA[i] += THETUP

    SIM.DINF = 0.0
