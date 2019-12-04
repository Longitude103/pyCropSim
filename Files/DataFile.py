"""Data File module."""

from itertools import chain
from io import TextIOWrapper
from abc import ABC, abstractmethod
from aenum import IntEnum


class OutputFormats(IntEnum):
    """The different output formats available."""
    Undefined = 0
    # COHYST
    COHYST = 1
    # Republican River (original v7 format)
    REPRIVER = 2


class DataRow(ABC):
    """Abstract base class for output rows."""

    def compare(self, other):
        """Returns a new row containing the difference between this row and the other specified."""
        diffs = 0
        ret = type(self)()
        for slot in self.getSlots():
            member = self[slot]
            if not member is None:
                if isinstance(member, str):
                    if member != other[slot]:
                        diffs += 1
                        ret[slot] = other[slot]
                else:
                    if member != other[slot]:
                        if isinstance(member, list):
                            for i in range(len(member)):
                                if member[i] != other[slot][i]:
                                    diffs += 1
                                    ret[slot][i] = member[i] - other[slot][i]
                        else:
                            diffs += 1
                            ret[slot] = member - other[slot]

        return (diffs, ret)

    def compareOutputStr(self, line: str):
        """Compares the string representation of this row with the specified line."""
        s = f"{self}"
        hasNaN = "nan" in s or "NaN" in line
        hasInf = "inf" in s or "Inf" in line
        if hasNaN or hasInf:
            print("WARNING: Arithmetic error found.")
        if s != line:
            if hasNaN or hasInf and s.lower() == line.lower():
                return True
            print("WARNING: Format Eror:")
            print(line)
            print(s)
            return False
        return True

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, item):
        setattr(self, key, item)

    def __eq__(self, other):
        if isinstance(type(other), type(self)):
            for slot in self.getSlots():
                if self[slot] != other[slot]:
                    return False
        else:
            for slot in self.getSlots():
                if self[slot] != other:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getSlots(self):
        """Returns the declared slots, including those inherited from base classes."""
        return chain.from_iterable(getattr(cls, '__slots__', []) for cls in type(self).__mro__)

    def printNonZeroValues(self):
        """Prints the values in the row having a value distinct from 0."""
        for slot in self.getSlots():
            member = self[slot]
            if isinstance(member, str):
                if member and len(member) > 0:
                    print(f"{slot:<10}:\t{member}")
            elif isinstance(member, list):
                for i in range(len(member)):
                    if member[i] != 0:
                        name = f"{slot}[{i}]"
                        print(f"{name:<10}:\t{member[i]:10.20f}")
            elif member != 0:
                if isinstance(member, DataRow):
                    member.printNonZeroValues()
                else:
                    print(f"{slot:<10}:\t{member:<10.20f}")


class DataFile(ABC):
    """Abstract base class for data files."""

    Rows = []
    """The rows contained in the file."""

    eof: int
    """The EOF position."""
    file: TextIOWrapper
    """The IOWrapper of the file."""
    filename: str
    """The filename of the data file."""

    def __init__(self, filename: str):
        self.Rows = []
        self.filename = filename
        if filename:
            self.open()
        else:
            self.file = None

    def __del__(self):
        self.close()

    @classmethod
    def isfile(cls, filename: str):
        """Returns true if the specified filename has the .txt extension."""
        return filename and filename.lower().endswith(".txt")

    def readAll(self):
        """Reads all the rows in the file."""
        while not self.ReadNext() is None:
            pass

    def ReadNext(self):
        """Reads the row in the file."""
        line = self.file.readline()
        if line:
            row = self.getRowForLine(line)
            if row:
                self.Rows.append(row)
                return row
        else:
            self.file.close()
        return None

    @abstractmethod
    def getRowForLine(self, line: str) -> DataRow:
        """Parse the line and return the corresponding row."""
        return None

    def open(self):
        """Opens the output file for reading."""
        self.file = open(self.filename, "rt")
        sof = self.file.tell()
        self.eof = self.file.seek(0, 2)
        self.file.seek(sof)

    def saveTo(self, filename):
        """Saves the data file to the specified location."""
        file = open(filename, "wt")
        for row in self.Rows:
            file.write(f"{row}\n")
        file.close()

    def close(self):
        """Closes the output file."""
        if not self.file is None:
            self.file.close()
