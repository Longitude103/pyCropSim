"""Implements the printing of the input summary."""

# LINES 1217~1398

import SIM
from Data.Crop import CropId
from Subroutines.DAYS import CALDAY

IMEFC, IDEFC = 0, 0
IMMAT, IDMAT = 0, 0

ITYPE = ('DRYLAND', 'HISTORIC.', 'C. PIVOT', 'FURROWS', 'BORDER/C')


def PrintInputSummary():
    """Prints the input summary."""
    global IMEFC, IDEFC, IMMAT, IDMAT

    if SIM.Sim.CROP == CropId.Alfalfa:
        PrintCuttingDatesAndSeasonalResultsForAlfalfaSimulations()
        # Continues to #4991: PrintDeficitsAndYields()
    else:
        IMEFC, IDEFC = CALDAY(SIM.JDYEFC)
        IMMAT, IDMAT = CALDAY(SIM.JDYMAT)

        if SIM.Sim.CROP >= 11:
            PrintCuttingDatesForHaySimulations()
            # Continues to #4991: PrintDeficitsAndYields() if IRRTYPE != 2,
            # else to 500: PrintSimulationParameters()
        elif SIM.Sim.Irrigation.IRRTYP != 2:
            # Skip printing of results for historical dates of irrigation
            PrintSeasonalResults()
            # Continues to #4991: PrintDeficitsAndYields()
        else:
            # Continue to 500: PrintSimulationParameters()
            pass

    if SIM.Sim.Irrigation.IRRTYP != 2:
        PrintDeficitsAndYields()

    PrintSimulationParameters()


def PrintSeasonalResults():
    """Prints seasonal results."""

    # 495 WRITE(7,530) IMPLT,IDPLT,IMVEG,IDVEG,IMEFC,IDEFC,IMFLO,IDFLO,IMRIPE,IDRIPE,IMMAT,IDMAT
    IMFLO, IDFLO = CALDAY(SIM.JDYFLO)
    IMRIPE, IDRIPE = CALDAY(SIM.JDYRIPE)
    IMVEG, IDVEG = CALDAY(SIM.JDYVEG)
    # if SIM.Sim.Irrigation.IRRTYP != 2:
    SIM.outFile.write((
        f"\n\n {'-' * 42}\n{' ' * 9}GROWTH SUMMARY\n {'-' * 42}\n"
        f" PLANTING DATE{' ' * 21}{SIM.Sim.IMPLT:>3}{SIM.Sim.IDPLT:>3}\n"
        f" FOUR LEAF DATE{' ' * 20}{IMVEG:>3}{IDVEG:>3}\n"
        f" DATE EFFECTIVE COVER{' ' * 14}{IMEFC:>3}{IDEFC:>3}\n"
        f" DATE OF FLOWERING{' ' * 17}{IMFLO:>3}{IDFLO:>3}\n"
        f" BEGIN YIELD DEVELOPMENT{' ' * 11}{IMRIPE:>3}{IDRIPE:>3}\n"
        f" DATE OF MATURITY{' ' * 18}{IMMAT:>3}{IDMAT:>3}\n"
    ))


def PrintCuttingDatesForHaySimulations():
    """Prints cutting dates for hay simulations"""
    # Label 496. @1249~1252
    # WRITE(7,531) IMPLT,IDPLT,IMEFC,IDEFC,IMMAT,IDMAT
    # 531     FORMAT(//,1X,42('-'),/,1X,8X,'GROWTH SUMMARY',/,1X,           &
    #      42('-'),/,1X,'PLANTING DATE',21X,2I3,                       &
    #      /,1X,'DATE EFFECTIVE COVER',14X,2I3,                        &
    #      /,1X,'DATE OF MATURITY',18X,2I3)
    SIM.outFile.write((
        f"\n\n {'-' * 42}\n{' ' * 9}GROWTH SUMMARY\n {'-' * 42}\n"
        f" PLANTING DATE{' ' * 21}{SIM.Sim.IMPLT:>3}{SIM.Sim.IDPLT:>3}\n"
        f" DATE EFFECTIVE COVER{' ' * 14}{IMEFC:>3}{IDEFC:>3}\n"
        f" DATE OF MATURITY{' ' * 18}{IMMAT:>3}{IDMAT:>3}\n"
    ))


def PrintCuttingDatesAndSeasonalResultsForAlfalfaSimulations():
    """Prints Cutting Dates And Seasonal Results For Alfalfa Simulations"""
    IMON, IDAY = CALDAY(SIM.JDYPLT)
    SIM.outFile.write(
        f"\n\n{'-' * 42}\n{' ' * 9}ALFALFA CUTTING SCHEDULE\n {'-' * 42}\n GREENUP DATE{' ' * 22}")
    SIM.outFile.write(f"{IMON:>3}{IDAY:>3}\n")
    for i in range(5):
        IMON, IDAY = CALDAY(SIM.Sim.JDYCUT[i])
        SIM.outFile.write(f" DATE OF CUTTING NO.       {i:>3}{' ' * 9}{IMON:>3}{IDAY:>3}\n")


def PrintSimulationParameters():
    """Prints the simulation parameters."""
    # Label 500 @ 1288
    # WRITE(7,560)ICROP(CROP),IYIELD,YCOEFF,SOIL,LAYERS,GDDROOT,
    # RZMIN,RZMAX,RZMGMT,(DEPTH(I),I=1,LAYERS)
    # WRITE(7,570)DPLBG,ITYPE(IRRTYP),PAD,TBREAK,RAINAL,SYSCAP,
    # APMIN,APMAX,SMALLI,EAPP,EREUSE,PRUNOF,GSTART,GSTOP,JFIRST,JDFREQ,DDEPTH
    depths = "".join(f"{SIM.BLOC.DEPTH[i]:>6.1f}" for i in range(10))
    SIM.outFile.write((
        f"\n\n {'-' * 42}\n{' ' * 9}INPUT DATA \n {'-' * 42}\n"
        f" CROP = {SIM.Sim.CROP.getName(SIM.Config.LEGACY):<8}\n"
        f"     YIELD MODEL = {SIM.YIELD:>5}     YIELD COEFF = {SIM.Sim.YCOEFF:>7.2f}\n"
        f" SOIL CODE = {SIM.SOIL:>3}\n NUMBER OF LAYERS ={SIM.Sim.LAYERS:>3}\n"
        f" GDD ROOTS START = {SIM.Sim.GDDROOT:>7.1f}\n"
        f" MINIMUM ROOTZONE = {SIM.Sim.RZMIN:>5.2f}\n"
        f" MAXIMUM ROOTZONE = {SIM.RZMAX:>5.2f}\n"
        f" MANAGEMENT ROOTZONE = {SIM.RZMGMT:>5.2f}\n"
        f" DEPTH OF EACH LAYER, inches :\n {depths}\n"))

    IRR = SIM.Sim.Irrigation
    depls = "".join(f"{IRR.PAD[i]:>6.2f}" for i in range(5))
    SIM.outFile.write((
        f" BEGINING DEPLETION = {SIM.DPLBG:>5.2f}\n"
        f" IRRIGATION TYPE = {ITYPE[SIM.Sim.Irrigation.IRRTYP - 1]}\n"
        f" ALLOWABLE DEPLETION, % BY STAGE {depls}\n"
        f" TBREAK, % OF PLANT AVAILABLE WATER = {SIM.Sim.TBREAK:>5.2f}\n"
    ))

    writeArray5F52(" RAINFALL ALLOWANCE BY GROWTH STAGE,in : ", IRR.RAINAL)
    SIM.outFile.write("\n SYSTEM CAPACITY, in/day = {IRR.SYSCAP:>5.2f}")
    writeArray5F52("\n APPLICATION MIMINUM BY GROWTH STAGE, in: ", IRR.APMIN)
    writeArray5F52("\n APPLICATION MAXIMUM BY GROWTH STAGE, in: ", IRR.APMAX)
    writeArray5F52("\n SMALLEST IRRIGATION BY GROWTH STAGE, in: ", IRR.SMALLI)
    writeArray5F52("\n APPLICATION EFFICIENCY BY GROWTH STAGE : ", SIM.Sim.EAPP)
    writeArray5F52("\n REUSE EFFICIENCY BY GROWTH STAGE : ", SIM.Sim.EREUSE)
    writeArray5F52("\n PERCENT RUNOFF BY GROWTH STAGE : ", SIM.Sim.PRUNOF)

    SIM.outFile.write((
        f"\n DEGREE DAYS TO START OF IRRIGATION, F = {IRR.GSTART:>6.0f}\n"
        f" DEGREE DAYS OF LAST IRRIGATION, F = {IRR.GSTOP:>6.0f}\n"
        f" FIRST DELIVERY DATE, julian {IRR.JFIRST:>4}\n"
        f" DELIVERY FREQUENCY, DAYS {SIM.Sim.JDFREQ:>4}\n"
        f" DELIVERY DEPTH, in {SIM.Sim.DDEPTH:>5.1f}\n"
    ))

    GDD = SIM.Sim.GDD
    if SIM.Sim.CROP < 10:
        SIM.outFile.write("  FOURLF  GDDEFC  GDDFLO  GDDRIPE  GDDMAT\n")
        SIM.outFile.write(
            f"  {GDD.VEG:>6.0f}  {GDD.EFC:>6.0f}  {GDD.FLO:>6.0f}"
            f"  {GDD.RIPE:>6.0f}  {GDD.MAT:>6.0f}\n")
    else:
        SIM.outFile.write(f"  GDDEFC  GDDMAT\n  {GDD.EFC:>6.0f}  {GDD.MAT:>6.0f}\n")

    for i in range(1, 23):
        SIM.outFile.write(f"  {CropId(i).getName(SIM.Config.LEGACY):<8}{' ' * 10}")
        SIM.outFile.write("".join([f"{SIM.BLOC.CN[i][j]:>7.0f}" for j in range(4)]))
        SIM.outFile.write("\n")

    # Compute Final Soil Water Depletion
    depths = ""
    thetas = ""
    SIM.outFile.write(f"{' ' * 10}ENDING VOLUMETRIC WATER CONTENTS \n")
    SIM.outFile.write(f"{' ' * 20}DEPTH INTERVALS: \n{' ' * 5}")
    DPLN = 0.0
    for i in range(SIM.Sim.LAYERS):
        DPLN += (SIM.Soil.FIELDC[i] - SIM.THETA[i]) * SIM.BLOC.DEPTH[i]
        depths += f"{SIM.BLOC.DEPTH[i]:>6.0f}"
        thetas += f"{SIM.THETA[i]:>6.3f}"
    SIM.outFile.write(depths)
    SIM.outFile.write(f"\n{' ' * 5}{'-' * 60}\n{' ' * 5}")
    SIM.outFile.write(thetas)
    SIM.outFile.write(f"\n\n{' ' * 20}TOTAL PROFILE DEPLETION, INCHES = {DPLN:>6.1f}\n")


def writeArray5F52(header: str, array: list):
    """Writes 5 float elements formatted as 5.2f"""
    SIM.outFile.write(header)
    for i in range(5):
        SIM.outFile.write(f"{array[i]:>5.2f}")


def PrintDeficitsAndYields():
    """Prints deficits and yields."""
    # Label 4991 @1270
    if SIM.Sim.CROP < 10:
        # Print Deficits And Yield For Grain and Tuber Crops
        # WRITE(7,540)(TDEF(I),I=1,3),TDEFS
        # WRITE(7,550) YIELD, ETMAX, ETYLD
        SIM.outFile.write(f"\n\n{' ' * 9}TRANSPIRATION DEFICITS\n {'-' * 42}\n")
        SIM.outFile.write(f"  VEGETATIVE   FLOWERING   FRUIT DEVELOP  \n {'-' * 42}\n")
        tdefs = f"{' ' * 8}".join([f"{SIM.TDEF[i]:>6.2f}" for i in range(2)])
        SIM.outFile.write(f"\n   {tdefs}\n {'-' * 42}\n{' ' * 27}TOTAL{SIM.TDEFS:>6.3f}\n")
    else:
        # Print Transpiration Deficits & Yield For Non Row Crops
        SIM.outFile.write(f"\n\n{'-' * 42}\n{' ' * 9}TRANSPIRATION DEFICITS, inch\n {'-' * 42}\n")
        for i in range(1 if SIM.Sim.CROP > 10 else 5):
            SIM.outFile.write(f" DEFICIT DURING CUTTING NO. {i:>3}    {SIM.TDEF[i]:>6.1f}\n")
        SIM.outFile.write(f" {'-' * 42}\n SEASONAL DEFICIT{' ' * 18}{SIM.TDEFS:>6.1f}\n")

    SIM.outFile.write((f"\n YIELD, %{' ' * 22}{SIM.YIELD:>6.1f}"
                       f"\n MAX. ET, inches{' ' * 15}{SIM.ETMAX:>6.1f}"
                       f"\n ACTUAL ET FOR YIELD, inches{' ' * 3}{SIM.ETYLD:>6.1f}\n"))
