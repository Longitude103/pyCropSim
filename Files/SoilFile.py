"""SoilFile module."""

from Data.SoilData import SoilData


class SoilFile:
    """
    Represents the data in the soil file (SOILFILE).
    Which indicates the soil types that must be simulated per site.
    """

    Data = {}

    def __init__(self, filename):
        print("Reading SOIL file at: " + filename)
        file = open(filename, "r")

        _ = file.readline().strip().split(",")
        for line in file.readlines():
            if len(line) > 0:
                data = line.strip().split(",")
                sims = []
                code = data[0]
                count = int(data[1])
                for i in range(2, len(data)):
                    sims.append(int(data[i]))
                assert len(sims) == 28
                self.Data[code] = SoilData(code, count, sims)
                # print(str(len(sims)) + " simulations in " + code)

        file.close()
