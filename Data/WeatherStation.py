"""Weather Station module."""


class WeatherStation:
    """Represents a Weather Station."""

    __slots__ = ("LOCATE", "IMSTR", "IDSTR", "NDAYS", "LAT", "LONG", "ELEV")

    def __init__(self, locate: str, imstr: int, idstr: int, ndays: int, lat: float, long: float, elev: float):
        """Initialize the Weather station class."""
        self.LOCATE = locate
        self.IMSTR = imstr
        """Month start index."""
        self.IDSTR = idstr
        """Day start index."""
        self.NDAYS = ndays
        """Number of days for which the file contains data."""
        self.LAT = lat
        """Latitude."""
        self.LONG = long
        """Longitude"""
        self.ELEV = elev
        """Elevation."""
