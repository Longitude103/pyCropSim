"""GDD (Growing Degree Days) module."""


class GddData:
    """Represents the Growing Degree Days related data."""
    __slots__ = ("VEG", "FLO", "RIPE", "YFORM", "EFC", "MAT")

    def __init__(self):
        self.VEG = 0.0
        """GDD TO VEGETATIVE STAGE"""
        self.FLO = 0.0
        """GDD TO FLOWERING STAGE"""
        self.RIPE = 0.0
        """GDD TO RIPENING STAGE"""
        self.YFORM = 0.0
        """GDD TO YIELD FORMATION"""
        self.EFC = 0.0
        """GDD TO EFFECTIVE COVER"""
        self.MAT = 0.0
        """GDD TO MATURITY"""
