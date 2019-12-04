"""Program Entry Point"""

import sys

import SIM

from Configuration import Configuration
from Subroutines import CROPSIM
from Errors.CustomError import CropSimError

SIM.Config = Configuration()

print("Starting simulation.")

# From Label 6 to 950, lines 683~1433 in the Fortran Program code.
for sim in SIM.Simulations:
    # This print emulates the original console output.
    print(sim)
    site = CROPSIM.initSimulation(sim)

    # Here starts the loop from label 15 to 900.
    #soilIndex = 0
    for soilIndex in range(len(SIM.SoilProps)):   # @ 738 DO 850 ISOIL = 1,28 / 850 CONTINUE
        if site.SOILSIM[soilIndex] == 1:
            # Go on with the simulation if specified on CROPFILE
            try:
                CROPSIM.initSoilSimulation(SIM.SoilProps[soilIndex].ISCODE, soilIndex)

                # @ 749, DO 800 II=1,NORUNS
                # Begins Sim loop for 1 to total years for this site.
                #crop: Crop = None
                II: int = 0
                print(f"NORUNS: {len(SIM.Crops)}")
                for crop in SIM.Crops:
                    assert crop.Index == II
                    II += 1
                    if crop.YR < SIM.Control.YEAR1: break

                    print(f"#{II} YEAR:{crop.YR}")

                    CROPSIM.initCropSimulation(crop)

                    CROPSIM.performSimulation()

                    # TODO: Remove this break in production, just for testing a single year run
                    if SIM.Config.SINGLE_RUN: break
                
            except CropSimError as err:
                print(err)
                sys.exit()
            
            # TODO: Remove this break in production, just for testing a single year run
            if SIM.Config.SINGLE_RUN: break
        else:
            break
        soilIndex += 1

    
    if SIM.Config.SINGLE_RUN: break

print("CropSim terminated successfully.")
