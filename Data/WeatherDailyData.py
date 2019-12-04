"""Weather daily data module."""

class WeatherDailyData:
    """Data from a Weather Station for a single day."""
    __slots__ = ("DOY", "TMAX", "TMIN", "PRECIP", "EVAP", "ETR")

    def __init__(self, doy: int, tmax: float, tmin: float,\
       precip: float, evap: float, etrhg: float):
        self.DOY = doy
        """Day Of Year, 1-based index."""
        self.TMAX = tmax
        """Maximum temperature (in °F)."""
        self.TMIN = tmin
        """Minimum temperature (in °F)."""
        self.PRECIP = precip
        """Recorded precipitation (in inches)."""
        self.EVAP = evap
        """Pan evaporation (inches/day).
        If not available for the station, a value of -99.00 is displayed."""
        self.ETR = etrhg
        """Reference crop ET as calculated using the Hargreaves method used
        during development of the Republican River Settlement Model."""

    def __str__(self):
        return "\t".join((self.DOY, str(self.TMAX),
                          str(self.TMIN), str(self.PRECIP),
                          str(self.EVAP), str(self.ETR)))
