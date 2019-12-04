"""Soil properties file module."""

from Data.SoilType import SoilType

SOILTYP = [411, 412, 421, 422, 431, 432, 442, 512, 521, 522, 532, 542, 612, 621,
           622, 631, 632, 642, 721, 722, 731, 732, 821, 822, 831, 832, 921, 922]
"""Soil types supported for the current data set."""

DDAYSOILDIC = {411: 2.0, 412: 2.0, 421: 2.0, 422: 2.0, 431: 4.0, 432: 4.0, 442: 6.0,
               512: 2.0, 521: 2.0, 522: 2.0, 532: 4.0, 542: 6.0, 612: 3.0, 621: 3.0,
               622: 3.0, 631: 4.0, 632: 4.0, 642: 6.0, 721: 3.0, 722: 3.0, 731: 4.0,
               732: 4.0, 821: 4.0, 822: 4.0, 831: 6.0, 832: 6.0, 921: 4.0, 922: 4.0}
"""Drainage duration based on the soil type."""

class SoilPropFile():
    """Represents a SOILPROP file."""

    SoilTypes = [None] * 28

    def __init__(self, filename):
        print("Reading SOILPROP file at: " + filename)
        file = open(filename, "r")

        file.readline()

        for line in file.readlines():
            if len(line) > 0:
                soilType = SoilType(line.strip())
                try:
                    soilType.Index = SOILTYP.index(soilType.ISCODE)
                    # TONOTE: Applying hard-coded values as in the Fortran code.
                    soilType.DRNCOE = 0.5
                    soilType.DRNDAY = DDAYSOILDIC[soilType.ISCODE]
                    self.SoilTypes[soilType.Index] = soilType
                except ValueError:
                    pass

        file.close()
