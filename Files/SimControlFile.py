"""Simulation control file module."""

import os

from Files.DataFile import DataFile
from Data.SimControl import SimControl


class SimControlFile(DataFile):
    """Represents the data in the Simulation Control file (CNTRFILE)"""

    def __init__(self, filename):
        print("Reading CNTRFILE file at: " + filename)
        super().__init__(filename)
        self.readAll()

    def getRowForLine(self, line: str):
        """Parse the line and return the corresponding row."""
        if not line: return None
        data = line.split("\t")
        return SimControl(data[0], int(data[1]), int(data[2]), int(data[3].strip()))

    @classmethod
    def isfile(cls, filename: str):
        """Returns true if the specified filename has the .txt extension."""
        return filename and filename.lower().endswith(".txt") \
            and os.path.basename(filename).startswith("WSiteInfo_")
