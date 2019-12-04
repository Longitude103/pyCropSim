"""Soil Data module."""

from Files.SoilPropFile import SOILTYP

class SoilData:
    """Represents one data row from the SOILFILE."""

    __slots__ = ("NWSITE", "NMUID", "SOILSIM")

    def __init__(self, nwsite, nmuid, soilsim: list):
        self.NWSITE = nwsite
        """The 4-digit code for the weather station."""
        self.NMUID = nmuid
        self.SOILSIM = soilsim
        """A list of integers indicating the soils to be simulated.
        If > 0, the soil at the current index must be simulated."""

    def __str__(self):
        return f"{self.NWSITE},{self.NMUID}"

    @classmethod
    def createFullSimulationForSite(cls, SITE: str):
        """Returns True if the specified file is a MON file."""
        return SoilData(SITE, 1, [1] * len(SOILTYP))
