"""CropFile module"""

import os
from Data.Crop import Crop
from Files.DataFile import DataFile


class CropFile(DataFile):
    """Defines the contents in a crop file. CROPFILE"""

    def __init__(self, filename: str = None):
        self.Rows = []
        if filename:
            print("Reading CROPFILE file at: " + filename)
            super().__init__(filename)
            self.readAll()

    def getRowForLine(self, line: str):
        """Parse the line and return the corresponding row."""
        if not line:
            return None
        data = line.split(",")
        return Crop(data[0], int(data[1].strip()), len(self.Rows))

    @classmethod
    def isfile(cls, filename: str):
        """Returns true if the specified filename has the .txt extension."""
        return filename and filename.lower().endswith(".csv") \
            and os.path.basename(filename).startswith("Cropping")
