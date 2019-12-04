"""Tillage Data module."""

from aenum import IntEnum

class ResidueType(IntEnum):
    """The type of residue, fragile (2) or not (1),
   this is used as and index to the tillage factors."""
    NonFragile = 1
    Fragile = 2

class TillageFlags(IntEnum):
    """Tillage flags."""
    Fallow = 0
    Convent = 1
    Conserv = 2
    Continuous = 3

class TillageTiming(IntEnum):
    """Tillage timing."""
    Undefined = 0
    PreplantOperation = 1
    DuringGrowingSeason = 2
    AfterHarvest = 3

class TillageOperation:
    """Tillage operation."""

    __slots__ = ("ITILTM", "TILDAY", "TILCOD")

    def __init__(self, timing: int, day: int, code: int):
        self.ITILTM = TillageTiming(timing)
        """Tillage timing."""
        self.TILDAY = day
        """Days before planting, after planting or maturity depending on the tillage timing."""
        self.TILCOD = code
        """Tillage code."""

class Tillage:
    """Tillage is the agricultural preparation of soil by mechanical
    agitation of various types, such as digging, stirring, and overturning."""

    __slots__ = ("ITC", "TILFAC", "TILTYP")

    def __init__(self, index: int, non_fragile_residue_factor: float, \
       fragile_residue_factor: float, description: str):
        self.ITC = index
        """Index of the tillage method in the tillage file."""
        self.TILFAC = (non_fragile_residue_factor / 100.0, fragile_residue_factor / 100.0)
        """Residue factors, in to decimal percentage."""
        self.TILTYP = description
        """Description of the tillage method."""

    def __str__(self):
        return "\t".join((self.ITC, str(self.TILFAC[0]), str(self.TILFAC[1]), self.TILTYP))
