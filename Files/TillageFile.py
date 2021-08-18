"""Tillage file module"""

from HelperIO import ReadNextNumberSequence
from Data.Tillage import Tillage


class TillageFile:
    """Represents the data in the tillage file (TILLFILE)"""

    Tillages = {}

    def __init__(self, filename):
        print("Reading TILLAGE file at: " + filename)
        file = open(filename, "rt+")

        data = []
        sof = file.tell()
        eof = file.seek(0, 2)
        file.seek(sof)
        file.readline()
        file.readline()

        while eof != file.tell():
            data = ReadNextNumberSequence(file, True)
            code = int(data[0])
            self.Tillages[code] = Tillage(code, float(data[1]), float(data[2]), data[3])

        print(str(len(self.Tillages)) + " tillage types read.")

        file.close()

    def GetFactor(self, code: str, residueType: int) -> float:
        """Get the residue adjusting factor based on the residue type."""
        return self.Tillages[code].TILFAC[residueType-1]
