"""Module definition for the SimControl class."""

from Files.DataFile import DataRow

class SimControl(DataRow):
    """Defines the parameters of a simulation."""
    __slots__ = ("WSITE", "IZONE", "CLIMZONE", "YEAR1")

    def __init__(self, wsite: str, izone: int, climzone: int, year: int):
        self.WSITE = wsite
        """The name of the weather site."""
        self.IZONE = izone
        """The climatic zone 1-based indes."""
        self.CLIMZONE = climzone
        """Not sure, never used."""
        self.YEAR1 = year
        """The year to start the simulation. (?)"""

    def __str__(self):
        return f"{self.WSITE}\t{self.IZONE}\t{self.CLIMZONE}\t{self.YEAR1}"

    def __eq__(self, other): 
        if not isinstance(other, SimControl): return False
        return self.WSITE == other.WSITE and self.YEAR1 == other.YEAR1

    def __hash__(self):
        # necessary for instances to behave sanely in dicts and sets.
        return hash((self.WSITE, self.YEAR1))
