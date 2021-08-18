"""Initial file module."""

from Data.Crop import CropId

from HelperIO import ReadFloats
from HelperIO import ReadNextFloat
from HelperIO import ReadNextInteger


class InitialFile:
    """Represents the contents of the INITIAL FILE"""
    __slots__ = ("THETA", "CROP", "RESIDUE", "LIVECROP", "SNOTMP", "SNOH2O", "SOILT")

    def __init__(self, filename: str = None):
        """InitialFile constructor."""
        self.THETA = [0.185, 0.173, 0.180, 0.161, 0.184, 0.184, 0.222, 0.247, 0.310, 0.338]
        """INITAL VOLUMETRIC WATER CONTENT FOR EACH LAYER"""
        self.CROP: CropId = CropId.NativePastureGrass
        self.RESIDUE = 100.0
        """Amount of residue on soil surface, in lb/acre"""
        # See LiveCrop Enum
        self.LIVECROP = False
        """If True, starting year with growing wheat.
        If False, starting with residue/fallow from wheat/other crops"""
        self.SNOTMP = 9.6
        """Temperature of snow pack (in Farenheit degrees)"""
        self.SNOH2O = 0.0
        """Amount of water in snow (in inches H20) TODO: Is H20 a unit (?)"""
        self.SOILT = [8.7, 10.0, 12.9, 18.1, 23.8, 29.6, 35.0, 38.8, 42.0, 44.4]
        """Average temperature of soil layer (in Farenheit degrees)"""

        if filename:
            print("Reading INITFILE file at: " + filename)
            file = open(filename, "r")

            self.THETA = ReadFloats(file, 10)
            self.CROP = ReadNextInteger(file)
            self.RESIDUE = ReadNextFloat(file)

            self.LIVECROP = ReadNextInteger(file) == 1
            self.SNOTMP = ReadNextFloat(file)
            self.SNOH2O = ReadNextFloat(file)
            self.SOILT = ReadFloats(file, 10)

            file.close()

    def saveToFile(self, filename):
        """Saves the current data to a file specified by filename."""
        file = open(filename, "wt")
        theta = "".join(["{:>6.3f}".format(self.THETA[i]) for i in range(10)])
        soilt = "".join(["  {:>5.1f}".format(self.SOILT[i]) for i in range(10)])
        file.write((
            f"  {theta}\n  {int(self.CROP):>4}  {self.RESIDUE:>9.1f}  {int(self.LIVECROP):>4}\n"
            f"  {self.SNOTMP:>8.1f}    {self.SNOH2O:>6.2f}    {soilt}\n"))
        file.close()
