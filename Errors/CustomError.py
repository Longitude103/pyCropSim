"""Application defined exceptions."""

class CropSimError(Exception):
    """An application specific error."""

class ConvergenceError(CropSimError):
    """A Convergence error."""

class TransLoopConvergenceError(ConvergenceError):
    """A Convergence error ocurring in the transpiration loop."""

    JDAY = 0
    TRANS = 0.0

    def __init__(self, jday: int, trans: float):
        super().__init__()

        self.JDAY = jday
        self.TRANS = trans

    def __str__(self):
        return f"Convergence error in trans loop, Day={self.JDAY} Trans={self.TRANS:.2f}"

class WeatherStationNotFound(CropSimError):
    """Raises when a weather station in not found in the dataset."""

    Station = None

    def __init__(self, station):
        super().__init__()
        self.Station = station

    def __str__(self):
        return f"Weather station {self.Station} not found in the dataset."

class SoilNotFound(CropSimError):
    """Raises when a soil type in not found in the dataset."""

    SoilCode = 0

    def __init__(self, soilCode):
        super().__init__()
        self.SoilCode = soilCode

    def __str__(self):
        return f"Specified soil ({self.SoilCode}) not found in the dataset."
